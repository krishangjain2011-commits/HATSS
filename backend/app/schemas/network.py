"""Response models for live, read-only Windows network telemetry."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NetworkSourceState(BaseModel):
    """Whether native Windows network data could be read."""

    status: Literal["available", "unavailable"]
    detail: str
    observed_at: datetime


class NetworkNeighbor(BaseModel):
    """A neighbor entry reported by the Windows networking stack."""

    ip_address: str
    link_layer_address: str | None = None
    state: str | None = None
    interface_alias: str | None = None
    address_family: str | None = None


class TcpConnection(BaseModel):
    """A current TCP connection reported by Windows, with its owner when accessible."""

    local_address: str
    local_port: int = Field(ge=0, le=65535)
    remote_address: str
    remote_port: int = Field(ge=0, le=65535)
    state: str
    owning_process_id: int = Field(ge=0)
    owning_process_name: str | None = None


class NetworkOverview(BaseModel):
    """A factual local network snapshot; HATSS does not classify entries as threats."""

    source: Literal["windows_networking"] = "windows_networking"
    state: NetworkSourceState
    neighbors: list[NetworkNeighbor] = Field(default_factory=list)
    tcp_connections: list[TcpConnection] = Field(default_factory=list)
