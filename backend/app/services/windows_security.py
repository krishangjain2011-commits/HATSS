"""Read-only adapters for Microsoft Defender and Sysmon on Windows.

HATSS presents output from established Windows security sources verbatim enough
for review. It does not decide whether an event is malicious or manufacture a
severity score.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.schemas.security import (
    DataSourceState,
    DefenderOverview,
    DefenderThreat,
    SysmonEvent,
    SysmonOverview,
)


def _unavailable_state(detail: str) -> DataSourceState:
    return DataSourceState(status="unavailable", detail=detail, observed_at=datetime.now(UTC))


def _powershell_json(script: str) -> Any | None:
    """Run a fixed, read-only PowerShell query and parse its JSON output."""

    result = _run_powershell(script)
    if result is None:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def _run_powershell(
    script: str, *, timeout: int = 10, environment: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str] | None:
    """Run a fixed PowerShell command through the built-in Windows executable."""

    if os.name != "nt":
        return None

    executable = (
        Path(os.environ.get("SystemRoot", r"C:\Windows"))
        / "System32"
        / "WindowsPowerShell"
        / "v1.0"
        / "powershell.exe"
    )
    process_environment = os.environ.copy()
    if environment:
        process_environment.update(environment)
    try:
        return (
            subprocess.run(  # noqa: S603 - fixed OS executable; command is internal, not user input
                [str(executable), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                check=False,
                encoding="utf-8",
                env=process_environment,
                errors="replace",
                text=True,
                timeout=timeout,
            )
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def _as_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return [value] if isinstance(value, dict) else []


def _resource_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(resource) for resource in value]
    return [str(value)] if value else []


_SYSMON_EVENT_TYPES = {
    1: "Process Create",
    2: "File creation time changed",
    3: "Network connection detected",
    4: "Sysmon service state changed",
    5: "Process terminated",
    6: "Driver loaded",
    7: "Image loaded",
    8: "CreateRemoteThread detected",
    9: "Raw disk read",
    10: "Process access",
    11: "File created",
    12: "Registry object created or deleted",
    13: "Registry value changed",
    14: "Registry key or value renamed",
    15: "File stream hash created",
    16: "Sysmon configuration changed",
    17: "Named pipe created",
    18: "Named pipe connected",
    19: "WMI filter activity",
    20: "WMI consumer activity",
    21: "WMI filter-to-consumer binding",
    22: "DNS query",
    23: "File deleted",
    24: "Clipboard changed",
    25: "Process tampering",
    26: "File deletion detected",
    27: "Executable blocked",
}


def describe_sysmon_event(event_id: int) -> str:
    """Return Sysmon's event category without assigning a threat verdict."""

    return _SYSMON_EVENT_TYPES.get(event_id, "Unknown Sysmon event")


def get_defender_overview() -> DefenderOverview:
    """Read Defender's current state and its own recorded detections."""

    observed_at = datetime.now(UTC)
    if os.name != "nt":
        return DefenderOverview(
            state=_unavailable_state("Microsoft Defender integration is available on Windows only.")
        )

    status = _powershell_json(
        """
        $status = Get-MpComputerStatus
        [PSCustomObject]@{
            AntivirusEnabled = $status.AntivirusEnabled
            RealTimeProtectionEnabled = $status.RealTimeProtectionEnabled
            BehaviorMonitorEnabled = $status.BehaviorMonitorEnabled
            AntivirusSignatureLastUpdated = if ($null -ne $status.AntivirusSignatureLastUpdated) {
                $status.AntivirusSignatureLastUpdated.ToUniversalTime().ToString('o')
            } else { $null }
            AMEngineVersion = $status.AMEngineVersion
        } | ConvertTo-Json -Compress
        """
    )
    if not isinstance(status, dict):
        return DefenderOverview(
            state=DataSourceState(
                status="unavailable",
                detail=(
                    "Microsoft Defender status could not be read. It may be disabled or managed "
                    "by another antivirus product."
                ),
                observed_at=observed_at,
            )
        )

    threat_data = _powershell_json(
        """
        $threatsById = @{}
        Get-MpThreat | ForEach-Object { $threatsById[[string]$_.ThreatID] = $_ }
        Get-MpThreatDetection | ForEach-Object {
            $threat = $threatsById[[string]$_.ThreatID]
            [PSCustomObject]@{
                ThreatID = $_.ThreatID
                ThreatName = $threat.ThreatName
                Severity = $threat.Severity
                Category = $threat.Category
                Resources = @($_.Resources)
                ActionSuccess = $_.ActionSuccess
                InitialDetectionTime = if ($null -ne $_.InitialDetectionTime) {
                    $_.InitialDetectionTime.ToUniversalTime().ToString('o')
                } else { $null }
                LastThreatStatusChangeTime = if ($null -ne $_.LastThreatStatusChangeTime) {
                    $_.LastThreatStatusChangeTime.ToUniversalTime().ToString('o')
                } else { $null }
            }
        } | ConvertTo-Json -Compress -Depth 3
        """
    )
    detections = [
        DefenderThreat(
            threat_id=item.get("ThreatID"),
            name=item.get("ThreatName") or "Unnamed Defender detection",
            severity=item.get("Severity"),
            category=item.get("Category"),
            resources=_resource_list(item.get("Resources")),
            action_success=item.get("ActionSuccess"),
            detected_at=item.get("InitialDetectionTime"),
            status_changed_at=item.get("LastThreatStatusChangeTime"),
        )
        for item in _as_list(threat_data)
    ]
    return DefenderOverview(
        state=DataSourceState(
            status="available",
            detail="Reported directly by Microsoft Defender.",
            observed_at=observed_at,
        ),
        antivirus_enabled=status.get("AntivirusEnabled"),
        real_time_protection_enabled=status.get("RealTimeProtectionEnabled"),
        behavior_monitor_enabled=status.get("BehaviorMonitorEnabled"),
        signature_last_updated=status.get("AntivirusSignatureLastUpdated"),
        engine_version=status.get("AMEngineVersion"),
        detections=detections,
    )


def get_sysmon_overview() -> SysmonOverview:
    """Read recent Sysmon event summaries without changing its event log."""

    observed_at = datetime.now(UTC)
    if os.name != "nt":
        return SysmonOverview(
            state=_unavailable_state("Sysmon integration is available on Windows only.")
        )

    data = _powershell_json(
        " ".join(
            [
                "Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 20",
                "-ErrorAction Stop |",
                "ForEach-Object { [PSCustomObject]@{ RecordId=$_.RecordId; EventId=$_.Id;",
                "OccurredAt=$_.TimeCreated; Provider=$_.ProviderName; Message=$_.Message } } |",
                "ConvertTo-Json -Compress -Depth 3",
            ]
        )
    )
    if data is None:
        return SysmonOverview(
            state=DataSourceState(
                status="unavailable",
                detail=(
                    "Sysmon operational events are unavailable. Install Sysmon or check access "
                    "to its event log."
                ),
                observed_at=observed_at,
            )
        )

    events = [
        SysmonEvent(
            record_id=int(item["RecordId"]),
            event_id=int(item["EventId"]),
            event_type=describe_sysmon_event(int(item["EventId"])),
            occurred_at=str(item["OccurredAt"]),
            provider=str(item["Provider"]),
            message=str(item["Message"]),
        )
        for item in _as_list(data)
        if item.get("RecordId") is not None and item.get("EventId") is not None
    ]
    return SysmonOverview(
        state=DataSourceState(
            status="available",
            detail="Recent events read directly from the Sysmon operational log.",
            observed_at=observed_at,
        ),
        events=events,
    )
