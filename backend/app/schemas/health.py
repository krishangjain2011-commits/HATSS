"""Schemas for non-domain operational health endpoints."""

from typing import Literal

from pydantic import BaseModel


class LivenessResponse(BaseModel):
    """Response returned when the API process is accepting requests."""

    status: Literal["ok"]
    service: str
    version: str


class ReadinessResponse(BaseModel):
    """Response returned when the API can reach its required database."""

    status: Literal["ok"]
    database: Literal["available"]
