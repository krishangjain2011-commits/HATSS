"""ESP32 sensor data schemas."""

from datetime import datetime
from pydantic import BaseModel


class SensorReading(BaseModel):
    """Individual sensor reading."""
    fire: bool
    pir: bool
    gas: bool
    water_level: float = 0.0  # 0-100%
    timestamp: datetime | None = None


class SensorStatus(BaseModel):
    """Current sensor status."""
    fire: bool
    pir: bool
    gas: bool
    water_level: float = 0.0  # 0-100%
    water_level_alert: bool = False  # True if water level is high
    last_update: str
    status: str = "connected"
