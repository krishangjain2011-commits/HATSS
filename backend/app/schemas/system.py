"""Response models for read-only host telemetry."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HostSummary(BaseModel):
    """Identity and operating-system details of the monitored host."""

    hostname: str
    operating_system: str
    booted_at: datetime
    uptime_seconds: int = Field(ge=0)


class CpuSummary(BaseModel):
    usage_percent: float = Field(ge=0, le=100)
    physical_cores: int = Field(ge=1)
    logical_cores: int = Field(ge=1)


class MemorySummary(BaseModel):
    total_bytes: int = Field(ge=0)
    available_bytes: int = Field(ge=0)
    used_bytes: int = Field(ge=0)
    usage_percent: float = Field(ge=0, le=100)


class DiskSummary(BaseModel):
    total_bytes: int = Field(ge=0)
    used_bytes: int = Field(ge=0)
    free_bytes: int = Field(ge=0)
    usage_percent: float = Field(ge=0, le=100)


class ProcessSummary(BaseModel):
    """A non-invasive summary of an accessible running process."""

    pid: int = Field(ge=0)
    name: str
    memory_percent: float = Field(ge=0)
    status: str


class SystemOverview(BaseModel):
    """A live, read-only snapshot. No risk score or threat verdict is implied."""

    data_mode: Literal["live"] = "live"
    source: Literal["native"] = "native"
    observed_at: datetime
    host: HostSummary
    cpu: CpuSummary
    memory: MemorySummary
    disk: DiskSummary
    running_processes: int = Field(ge=0)
    top_processes: list[ProcessSummary]
    process_collection_status: Literal["available", "limited"]
