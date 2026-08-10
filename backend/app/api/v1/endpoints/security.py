"""Read-only endpoints backed by established Windows security sources."""

import asyncio

from fastapi import APIRouter

from app.schemas.security import DefenderOverview, SysmonOverview
from app.services.windows_security import get_defender_overview, get_sysmon_overview

router = APIRouter(prefix="/security", tags=["security"])


@router.get(
    "/defender", response_model=DefenderOverview, summary="Read Microsoft Defender evidence"
)
async def read_defender_overview() -> DefenderOverview:
    return await asyncio.to_thread(get_defender_overview)


@router.get("/sysmon", response_model=SysmonOverview, summary="Read recent Sysmon evidence")
async def read_sysmon_overview() -> SysmonOverview:
    return await asyncio.to_thread(get_sysmon_overview)
