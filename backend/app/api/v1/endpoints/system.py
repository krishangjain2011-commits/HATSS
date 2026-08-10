"""Read-only host telemetry endpoints."""

import asyncio

from fastapi import APIRouter

from app.schemas.system import SystemOverview
from app.services.system_monitor import get_system_overview

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/overview", response_model=SystemOverview, summary="Read live host telemetry")
async def read_system_overview() -> SystemOverview:
    """Return a live host snapshot without making changes to the host."""

    return await asyncio.to_thread(get_system_overview)
