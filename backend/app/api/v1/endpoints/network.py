"""Read-only local network telemetry endpoint."""

import asyncio

from fastapi import APIRouter

from app.schemas.network import NetworkOverview
from app.services.windows_network import get_network_overview

router = APIRouter(prefix="/network", tags=["network"])


@router.get(
    "/overview", response_model=NetworkOverview, summary="Read live Windows network telemetry"
)
async def read_network_overview() -> NetworkOverview:
    """Return live Windows network facts without scanning or changing the network."""

    return await asyncio.to_thread(get_network_overview)
