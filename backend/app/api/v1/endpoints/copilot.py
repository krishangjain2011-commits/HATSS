"""Explicit local-model evidence briefing endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException, status

from app.schemas.copilot import CopilotBriefRequest, CopilotBriefResponse, CopilotStatus
from app.services.copilot import CopilotUnavailableError, create_brief, get_copilot_status

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.get("/status", response_model=CopilotStatus, summary="Read local copilot availability")
async def read_copilot_status() -> CopilotStatus:
    return await asyncio.to_thread(get_copilot_status)


@router.post(
    "/brief", response_model=CopilotBriefResponse, summary="Request a local evidence briefing"
)
async def create_evidence_brief(request: CopilotBriefRequest) -> CopilotBriefResponse:
    try:
        return await asyncio.to_thread(create_brief, request.question)
    except CopilotUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error
