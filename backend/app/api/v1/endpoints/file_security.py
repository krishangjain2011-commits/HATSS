"""Explicit, non-destructive file-security endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.file_security import (
    DefenderScanAction,
    DefenderScanCapability,
    DefenderScanRequest,
)
from app.services.file_security import (
    UnsafeScanDirectoryError,
    get_defender_scan_capability,
    start_defender_custom_scan,
)

router = APIRouter(prefix="/file-security", tags=["file security"])


@router.get(
    "/defender",
    response_model=DefenderScanCapability,
    summary="Read Microsoft Defender custom-scan capability",
)
async def read_defender_scan_capability() -> DefenderScanCapability:
    """Return source state only; this endpoint never starts a scan."""

    return await asyncio.to_thread(get_defender_scan_capability)


@router.post(
    "/defender/scans",
    response_model=DefenderScanAction,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start one user-requested Defender custom scan",
)
async def request_defender_custom_scan(
    payload: DefenderScanRequest, response: Response
) -> DefenderScanAction:
    """Start a scan for one existing, specific user directory and nothing else."""

    try:
        scan_action = await asyncio.to_thread(start_defender_custom_scan, payload.directory)
    except UnsafeScanDirectoryError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    if scan_action.state != "started":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return scan_action
