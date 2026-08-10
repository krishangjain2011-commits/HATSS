"""Versioned API router composition."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    copilot,
    file_security,
    health,
    network,
    security,
    system,
    face,
    sensors,
    intrusions,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(system.router)
api_router.include_router(security.router)
api_router.include_router(file_security.router)
api_router.include_router(network.router)
api_router.include_router(copilot.router)
api_router.include_router(face.router)
api_router.include_router(sensors.router)
api_router.include_router(intrusions.router)
