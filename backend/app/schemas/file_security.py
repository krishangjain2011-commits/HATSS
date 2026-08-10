"""Contracts for explicit, Microsoft Defender-backed file scans."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.security import DataSourceState


class DefenderScanRequest(BaseModel):
    """A directory selected by the user for one custom Defender scan."""

    directory: str = Field(
        min_length=1,
        max_length=1024,
        description="Absolute path to an existing directory selected by the user.",
    )

    @field_validator("directory")
    @classmethod
    def directory_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("directory must not be blank")
        return value


class DefenderScanCapability(BaseModel):
    """Whether the local Defender installation can run a custom scan."""

    source: Literal["microsoft_defender"] = "microsoft_defender"
    state: DataSourceState
    antivirus_enabled: bool | None = None
    custom_scan_available: bool = False


class DefenderScanAction(BaseModel):
    """Result of requesting a single Defender custom scan."""

    source: Literal["microsoft_defender"] = "microsoft_defender"
    action: Literal["custom_scan"] = "custom_scan"
    state: Literal["started", "unavailable", "failed"]
    directory: str
    detail: str
    requested_at: datetime
