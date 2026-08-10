"""ESP32 sensor data schemas."""

from datetime import datetime
from pydantic import BaseModel


class SensorReading(BaseModel):
    """Individual sensor reading."""
    fire: bool
    pir: bool
    gas: bool
    timestamp: datetime | None = None


class SensorStatus(BaseModel):
    """Current sensor status."""
    fire: bool
    pir: bool
    gas: bool
    last_update: str
    status: str = "connected"
