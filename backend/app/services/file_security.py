"""Safe, explicit Microsoft Defender custom-scan integration.

This module never deletes, quarantines, or modifies files. It starts a
Defender custom scan only after the API receives a user-selected directory.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.file_security import DefenderScanAction, DefenderScanCapability
from app.schemas.security import DataSourceState
from app.services.windows_security import _powershell_json, _run_powershell


class UnsafeScanDirectoryError(ValueError):
    """Raised when a requested directory is too broad or unsafe to scan."""


def _unavailable_state(detail: str) -> DataSourceState:
    return DataSourceState(status="unavailable", detail=detail, observed_at=datetime.now(UTC))


def _is_within(path: Path, root: Path) -> bool:
    """Return whether ``path`` is ``root`` or one of its descendants."""

    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _protected_scan_roots() -> list[Path]:
    """Return OS-owned directories that should never be broad-scanned here."""

    roots: list[Path] = []
    for variable in ("SystemRoot", "WINDIR", "ProgramFiles", "ProgramFiles(x86)", "ProgramData"):
        value = os.environ.get(variable)
        if value:
            try:
                roots.append(Path(value).resolve(strict=True))
            except OSError:
                # An environment variable can reference an unavailable drive.
                continue
    return roots


def validate_scan_directory(directory: str, *, protected_roots: list[Path] | None = None) -> Path:
    """Resolve and constrain a user-selected directory before giving it to Defender."""

    candidate = Path(directory).expanduser()
    if not candidate.is_absolute():
        raise UnsafeScanDirectoryError("Choose an absolute directory path.")

    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise UnsafeScanDirectoryError(
            "The selected directory does not exist or cannot be resolved."
        ) from error

    if not resolved.is_dir():
        raise UnsafeScanDirectoryError("The selected path must be an existing directory.")

    if resolved == Path(resolved.anchor):
        raise UnsafeScanDirectoryError(
            "Scanning a drive root is not allowed. Choose a specific directory."
        )

    try:
        home_directory = Path.home().resolve(strict=True)
    except OSError:
        home_directory = Path.home()
    if resolved == home_directory:
        raise UnsafeScanDirectoryError(
            "Scanning the entire user profile is not allowed. Choose a specific subdirectory."
        )

    for protected_root in (
        protected_roots if protected_roots is not None else _protected_scan_roots()
    ):
        if _is_within(resolved, protected_root):
            raise UnsafeScanDirectoryError(
                "Scanning Windows and program directories is not allowed. "
                "Choose a user data directory."
            )

    return resolved


def get_defender_scan_capability() -> DefenderScanCapability:
    """Report whether the local Defender custom-scan command is available."""

    if os.name != "nt":
        return DefenderScanCapability(
            state=_unavailable_state(
                "Microsoft Defender custom scans are available on Windows only."
            )
        )

    data = _powershell_json(
        """
        $ErrorActionPreference = 'Stop'
        $status = Get-MpComputerStatus
        $scanCommand = Get-Command Start-MpScan -ErrorAction SilentlyContinue
        [PSCustomObject]@{
            AntivirusEnabled = $status.AntivirusEnabled
            CustomScanAvailable = $null -ne $scanCommand
        } | ConvertTo-Json -Compress
        """
    )
    if not isinstance(data, dict) or not data.get("CustomScanAvailable"):
        return DefenderScanCapability(
            state=_unavailable_state(
                "Microsoft Defender custom scans could not be started. "
                "Defender or Start-MpScan is unavailable."
            )
        )

    return DefenderScanCapability(
        state=DataSourceState(
            status="available",
            detail="Microsoft Defender custom scans are available after an explicit user request.",
            observed_at=datetime.now(UTC),
        ),
        antivirus_enabled=data.get("AntivirusEnabled"),
        custom_scan_available=True,
    )


def start_defender_custom_scan(directory: str) -> DefenderScanAction:
    """Ask Defender to start a custom scan of one validated user directory."""

    requested_at = datetime.now(UTC)
    resolved_directory = validate_scan_directory(directory)
    capability = get_defender_scan_capability()
    if capability.state.status != "available" or not capability.custom_scan_available:
        return DefenderScanAction(
            state="unavailable",
            directory=str(resolved_directory),
            detail=capability.state.detail,
            requested_at=requested_at,
        )

    result = _run_powershell(
        """
        $ErrorActionPreference = 'Stop'
        Start-MpScan -ScanType CustomScan -ScanPath $env:HATSS_DEFENDER_SCAN_DIRECTORY
        """,
        timeout=15,
        environment={"HATSS_DEFENDER_SCAN_DIRECTORY": str(resolved_directory)},
    )
    if result is not None and result.returncode == 0:
        return DefenderScanAction(
            state="started",
            directory=str(resolved_directory),
            detail="Microsoft Defender accepted the requested custom scan.",
            requested_at=requested_at,
        )

    return DefenderScanAction(
        state="failed",
        directory=str(resolved_directory),
        detail=(
            "Microsoft Defender did not accept the custom scan request. "
            "Check Defender and try again."
        ),
        requested_at=requested_at,
    )
