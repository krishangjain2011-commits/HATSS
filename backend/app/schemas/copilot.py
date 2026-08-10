"""Models for an explicit, local-model evidence briefing request."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CopilotStatus(BaseModel):
    """Availability of the configured local AI provider."""

    enabled: bool
    provider: Literal["ollama"] = "ollama"
    model: str
    detail: str


class CopilotBriefRequest(BaseModel):
    """Explicit consent is required before local security evidence is shared with a model."""

    question: str = Field(min_length=3, max_length=1000)
    confirm_local_evidence: Literal[True]


class CopilotBriefResponse(BaseModel):
    """A model-generated briefing with the evidence source boundaries retained."""

    provider: Literal["ollama"] = "ollama"
    model: str
    generated_at: datetime
    evidence_sources: list[str]
    answer: str
