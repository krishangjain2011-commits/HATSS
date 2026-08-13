"""Face recognition data schemas."""

from datetime import datetime
from pydantic import BaseModel


class FaceDetection(BaseModel):
    """Detected face in video stream."""
    label: str
    confidence: float
    timestamp: datetime


class KnownFace(BaseModel):
    """Registered known face."""
    name: str
    embedding_id: str
    registered_at: datetime


class IntrusionEvent(BaseModel):
    """Intrusion alert event."""
    timestamp: datetime
    image_path: str
    confidence: float
    detector_status: str


class FaceStatus(BaseModel):
    """Current face recognition status."""
    label: str  # "KNOWN: Name", "INTRUDER", "NO FACE"
    confidence: float
    last_updated: datetime
    known_faces: list[str] = []  # List of registered known face names
