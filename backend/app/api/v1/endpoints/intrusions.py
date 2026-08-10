"""Intrusion detection and event endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException
from app.services.intrusion_detector import (
    get_intrusion_images,
    get_intrusion_count,
    get_intrusion_image_path
)

router = APIRouter(prefix="/intrusions", tags=["intrusions"])


@router.get("/list", response_model=list[str], summary="Get recent intrusion images")
async def list_intrusions(limit: int = 6) -> list[str]:
    """Get list of recent intrusion alert images."""
    return await asyncio.to_thread(get_intrusion_images, limit=limit)


@router.get("/count", response_model=dict, summary="Get intrusion count")
async def count_intrusions() -> dict:
    """Get total intrusion event count."""
    count = await asyncio.to_thread(get_intrusion_count)
    return {"count": count}


@router.get("/metrics", response_model=dict, summary="Get intrusion metrics")
async def get_intrusion_metrics() -> dict:
    """Get intrusion detection metrics."""
    count = await asyncio.to_thread(get_intrusion_count)
    recent = await asyncio.to_thread(get_intrusion_images, limit=6)
    
    return {
        "total_events": count,
        "recent_events": len(recent),
        "latest_images": recent,
        "status": "active" if count > 0 else "clear"
    }
