"""Read-only evidence models backed by native Windows security sources."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DataSourceState(BaseModel):
    """Whether an operating-system security source was accessible."""

    status: Literal["available", "unavailable"]
    detail: str
    observed_at: datetime


class DefenderThreat(BaseModel):
    """A record reported by Microsoft Defender, without HATSS interpretation."""

    threat_id: int | None = None
    name: str
    severity: str | None = None
    category: str | None = None
    resources: list[str] = Field(default_factory=list)
    action_success: bool | None = None
    detected_at: str | None = None
    status_changed_at: str | None = None


class DefenderOverview(BaseModel):
    """Microsoft Defender's reported state and detections."""

    source: Literal["microsoft_defender"] = "microsoft_defender"
    state: DataSourceState
    antivirus_enabled: bool | None = None
    real_time_protection_enabled: bool | None = None
    behavior_monitor_enabled: bool | None = None
    signature_last_updated: str | None = None
    engine_version: str | None = None
    detections: list[DefenderThreat] = Field(default_factory=list)


class SysmonEvent(BaseModel):
    """One unmodified Sysmon event summary from the local Windows event log."""

    record_id: int
    event_id: int
    event_type: str = "Unknown Sysmon event"
    occurred_at: str
    provider: str
    message: str


class SysmonOverview(BaseModel):
    """Recent Sysmon evidence. Sysmon itself, not HATSS, collects these events."""

    source: Literal["sysmon"] = "sysmon"
    state: DataSourceState
    events: list[SysmonEvent] = Field(default_factory=list)
