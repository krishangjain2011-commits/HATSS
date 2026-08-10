"""Operational liveness and readiness endpoints."""

import asyncio
import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.db.session import get_engine
from app.schemas.health import LivenessResponse, ReadinessResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["operations"])


@router.get("/health/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    """Return success when the HTTP application can process requests."""
    settings = get_settings()
    return LivenessResponse(
        status="ok",
        service="hatss-api",
        version=settings.app_version,
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    """Return success only when PostgreSQL accepts a simple connection."""
    try:
        await asyncio.to_thread(_check_database)
    except (RuntimeError, SQLAlchemyError) as error:
        logger.warning("Database readiness check failed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "database_unavailable",
                "message": "The database is not ready.",
            },
        ) from error

    return ReadinessResponse(status="ok", database="available")


def _check_database() -> None:
    """Blocking database check (runs in thread pool)."""
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
