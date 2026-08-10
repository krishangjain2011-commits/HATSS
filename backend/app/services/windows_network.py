"""Read-only local network telemetry from built-in Windows PowerShell cmdlets.

The service reports the operating system's neighbor and TCP connection snapshots.
It does not scan other devices, modify firewall settings, or classify network activity.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.schemas.network import NetworkNeighbor, NetworkOverview, NetworkSourceState, TcpConnection


def _powershell_json(script: str) -> Any | None:
    """Run a fixed, non-mutating PowerShell query and parse its JSON output."""

    if os.name != "nt":
        return None

    executable = (
        Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / "System32"
        / "WindowsPowerShell"
        / "v1.0"
        / "powershell.exe"
    )
    try:
        result = subprocess.run(  # noqa: S603 - fixed OS executable; internal fixed query only
            [str(executable), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def _as_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return [value] if isinstance(value, dict) else []


def _unavailable(detail: str, observed_at: datetime) -> NetworkOverview:
    return NetworkOverview(
        state=NetworkSourceState(status="unavailable", detail=detail, observed_at=observed_at)
    )


def get_network_overview() -> NetworkOverview:
    """Read current Windows neighbor and TCP connection tables without changing them."""

    observed_at = datetime.now(UTC)
    if os.name != "nt":
        return _unavailable("Network integration is available on Windows only.", observed_at)

    neighbors_data = _powershell_json(
        " ".join(
            [
                "Get-NetNeighbor -ErrorAction Stop |",
                "ForEach-Object { [PSCustomObject]@{ IPAddress=$_.IPAddress;",
                "LinkLayerAddress=$_.LinkLayerAddress; State=[string]$_.State;",
                "InterfaceAlias=$_.InterfaceAlias; AddressFamily=[string]$_.AddressFamily } } |",
                "ConvertTo-Json -Compress",
            ]
        )
    )
    connections_data = _powershell_json(
        " ".join(
            [
                "Get-NetTCPConnection -ErrorAction Stop |",
                "ForEach-Object { $owner = Get-Process -Id $_.OwningProcess "
                "-ErrorAction SilentlyContinue;",
                "[PSCustomObject]@{ LocalAddress=$_.LocalAddress; LocalPort=$_.LocalPort;",
                "RemoteAddress=$_.RemoteAddress; RemotePort=$_.RemotePort; State=[string]$_.State;",
                "OwningProcess=$_.OwningProcess; OwningProcessName=if ($null -ne $owner) {",
                "$owner.ProcessName } else { $null } } } | ConvertTo-Json -Compress",
            ]
        )
    )
    if neighbors_data is None or connections_data is None:
        return _unavailable(
            "Windows network tables could not be read. Check that the backend has access to "
            "Get-NetNeighbor and Get-NetTCPConnection.",
            observed_at,
        )

    neighbors = [
        NetworkNeighbor(
            ip_address=str(item["IPAddress"]),
            link_layer_address=item.get("LinkLayerAddress"),
            state=item.get("State"),
            interface_alias=item.get("InterfaceAlias"),
            address_family=item.get("AddressFamily"),
        )
        for item in _as_records(neighbors_data)
        if item.get("IPAddress")
    ]
    tcp_connections = [
        TcpConnection(
            local_address=str(item["LocalAddress"]),
            local_port=int(item["LocalPort"]),
            remote_address=str(item["RemoteAddress"]),
            remote_port=int(item["RemotePort"]),
            state=str(item["State"]),
            owning_process_id=int(item["OwningProcess"]),
            owning_process_name=item.get("OwningProcessName"),
        )
        for item in _as_records(connections_data)
        if all(
            item.get(key) is not None
            for key in (
                "LocalAddress",
                "LocalPort",
                "RemoteAddress",
                "RemotePort",
                "State",
                "OwningProcess",
            )
        )
    ]
    return NetworkOverview(
        state=NetworkSourceState(
            status="available",
            detail="Live neighbor and TCP connection data reported by Windows.",
            observed_at=observed_at,
        ),
        neighbors=neighbors,
        tcp_connections=tcp_connections,
    )
