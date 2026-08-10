"""Read-only host telemetry collection using the Python standard library.

This service exposes operational facts only. It does not classify processes,
assign threat scores, inspect file contents, scan the network, or take action.
"""

from __future__ import annotations

import csv
import os
import platform
import shutil
import socket
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.schemas.system import (
    CpuSummary,
    DiskSummary,
    HostSummary,
    MemorySummary,
    ProcessSummary,
    SystemOverview,
)


def _system_volume() -> str:
    """Return a valid system-volume path on Windows, macOS, and Linux."""

    return Path.home().anchor or Path.cwd().anchor or "/"


def _windows_edition_label(product_name: str, build_number: int) -> str:
    """Correct Windows' legacy 10.0 API label using its actual build number."""

    family = "Windows 11" if build_number >= 22000 else "Windows 10"
    if product_name.startswith("Windows 10"):
        return product_name.replace("Windows 10", family, 1)
    return product_name or family


def _operating_system() -> str:
    """Return the host OS name without Windows 11 being mislabeled as Windows 10."""

    if os.name != "nt":
        return f"{platform.system()} {platform.release()}"

    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        ) as key:
            product_name = str(winreg.QueryValueEx(key, "ProductName")[0])
            build_number = int(str(winreg.QueryValueEx(key, "CurrentBuildNumber")[0]))
        return f"{_windows_edition_label(product_name, build_number)} (build {build_number})"
    except (FileNotFoundError, OSError, ValueError):
        return f"Windows {platform.release()}"


def _windows_memory() -> tuple[int, int, int, float]:
    """Read Windows memory counters through GlobalMemoryStatusEx."""

    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    used = status.total_physical - status.available_physical
    return status.total_physical, status.available_physical, used, float(status.memory_load)


def _memory() -> tuple[int, int, int, float]:
    """Read host memory counters without adding an external agent dependency."""

    if os.name == "nt":
        return _windows_memory()

    values: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        key, raw_value = line.split(":", maxsplit=1)
        values[key] = int(raw_value.strip().split()[0]) * 1024
    total = values["MemTotal"]
    available = values.get("MemAvailable", values.get("MemFree", 0))
    used = total - available
    return total, available, used, (used / total * 100) if total else 0.0


def _cpu_usage_percent() -> float:
    """Estimate current CPU load with the best native facility available."""

    if os.name != "nt":
        try:
            return min(os.getloadavg()[0] / (os.cpu_count() or 1) * 100, 100.0)
        except OSError:
            return 0.0

    import ctypes

    class FileTime(ctypes.Structure):
        _fields_ = [("low", ctypes.c_ulong), ("high", ctypes.c_ulong)]

    def read_times() -> tuple[int, int, int]:
        idle, kernel, user = FileTime(), FileTime(), FileTime()
        if not ctypes.windll.kernel32.GetSystemTimes(
            ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
        ):
            raise OSError("GetSystemTimes failed")

        def as_int(value: FileTime) -> int:
            return (value.high << 32) | value.low

        return as_int(idle), as_int(kernel), as_int(user)

    before = read_times()
    time.sleep(0.1)
    after = read_times()
    idle_delta = after[0] - before[0]
    total_delta = (after[1] - before[1]) + (after[2] - before[2])
    return max(0.0, min(100.0, (1 - idle_delta / total_delta) * 100)) if total_delta else 0.0


def _windows_processes(total_memory: int) -> tuple[int, list[ProcessSummary], str]:
    """Read process names, PIDs, and working sets through the built-in tasklist."""

    tasklist_path = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "tasklist.exe"
    result = (
        subprocess.run(  # noqa: S603 - fixed Windows system executable and fixed arguments only
            [str(tasklist_path), "/FO", "CSV", "/NH"],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            text=True,
        )
    )
    if result.returncode != 0:
        return 0, [], "limited"
    processes: list[ProcessSummary] = []
    for row in csv.reader(result.stdout.splitlines()):
        if len(row) < 5 or not row[1].isdigit():
            continue
        memory_digits = "".join(character for character in row[4] if character.isdigit())
        memory_bytes = int(memory_digits) * 1024 if memory_digits else 0
        processes.append(
            ProcessSummary(
                pid=int(row[1]),
                name=row[0] or "Unknown process",
                memory_percent=(memory_bytes / total_memory * 100) if total_memory else 0.0,
                status="running",
            )
        )
    processes.sort(key=lambda item: item.memory_percent, reverse=True)
    return len(processes), processes[:8], "available"


def _unix_processes(total_memory: int) -> tuple[int, list[ProcessSummary], str]:
    """Read accessible Linux process information from /proc without mutation."""

    processes: list[ProcessSummary] = []
    for process_dir in Path("/proc").iterdir():
        if not process_dir.name.isdigit():
            continue
        try:
            status = (process_dir / "status").read_text(encoding="utf-8")
            fields = dict(line.split(":", 1) for line in status.splitlines() if ":" in line)
            name = fields.get("Name", "Unknown process").strip()
            rss = int(fields.get("VmRSS", "0 kB").split()[0]) * 1024
            processes.append(
                ProcessSummary(
                    pid=int(process_dir.name),
                    name=name,
                    memory_percent=(rss / total_memory * 100) if total_memory else 0.0,
                    status="running",
                )
            )
        except (OSError, ValueError):
            continue
    processes.sort(key=lambda item: item.memory_percent, reverse=True)
    return len(processes), processes[:8], "available"


def _processes(total_memory: int) -> tuple[int, list[ProcessSummary], str]:
    return _windows_processes(total_memory) if os.name == "nt" else _unix_processes(total_memory)


def _booted_at() -> datetime:
    """Return an estimated system boot time using native OS facilities."""

    if os.name == "nt":
        import ctypes

        uptime_ms = ctypes.windll.kernel32.GetTickCount64()
        return datetime.now(UTC) - timedelta(milliseconds=uptime_ms)
    for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines():
        if line.startswith("btime "):
            return datetime.fromtimestamp(int(line.split()[1]), tz=UTC)
    return datetime.now(UTC)


def get_system_overview() -> SystemOverview:
    """Produce a live, non-destructive snapshot of the host running FastAPI."""

    observed_at = datetime.now(UTC)
    total_memory, available_memory, used_memory, memory_percent = _memory()
    disk = shutil.disk_usage(_system_volume())
    booted_at = _booted_at()
    running_processes, top_processes, process_collection_status = _processes(total_memory)

    return SystemOverview(
        observed_at=observed_at,
        host=HostSummary(
            hostname=socket.gethostname(),
            operating_system=_operating_system(),
            booted_at=booted_at,
            uptime_seconds=max(int((observed_at - booted_at).total_seconds()), 0),
        ),
        cpu=CpuSummary(
            usage_percent=_cpu_usage_percent(),
            physical_cores=os.cpu_count() or 1,
            logical_cores=os.cpu_count() or 1,
        ),
        memory=MemorySummary(
            total_bytes=total_memory,
            available_bytes=available_memory,
            used_bytes=used_memory,
            usage_percent=memory_percent,
        ),
        disk=DiskSummary(
            total_bytes=disk.total,
            used_bytes=disk.used,
            free_bytes=disk.free,
            usage_percent=(disk.used / disk.total * 100) if disk.total else 0.0,
        ),
        running_processes=running_processes,
        top_processes=top_processes,
        process_collection_status=process_collection_status,
    )
