"""Extended system monitoring with ESP32 sensor integration.

Combines existing system telemetry with IoT sensor data from ESP32 devices
(fire, PIR motion, gas sensors).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.services.system_monitor import get_system_overview


class SensorStatus:
    """Manages ESP32 sensor readings."""

    def __init__(self) -> None:
        """Initialize sensor status tracking."""
        self.fire: bool = False
        self.pir: bool = False
        self.gas: bool = False
        self.last_update: datetime | None = None

    def update(self, fire: bool, pir: bool, gas: bool) -> None:
        """Update sensor readings.

        Args:
            fire: Fire sensor status.
            pir: PIR motion sensor status.
            gas: Gas sensor status.
        """
        self.fire = bool(fire)
        self.pir = bool(pir)
        self.gas = bool(gas)
        self.last_update = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with sensor status and last update time.
        """
        return {
            "fire": self.fire,
            "pir": self.pir,
            "gas": self.gas,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }

    def has_alert(self) -> bool:
        """Check if any sensor is alerting.

        Returns:
            True if any sensor is triggered, False otherwise.
        """
        return self.fire or self.pir or self.gas


# Global sensor instance
_sensor_status = SensorStatus()


def update_sensor_data(fire: bool, pir: bool, gas: bool) -> dict[str, Any]:
    """Update ESP32 sensor readings.

    Args:
        fire: Fire sensor status.
        pir: PIR motion sensor status.
        gas: Gas sensor status.

    Returns:
        Updated sensor status dictionary.
    """
    _sensor_status.update(fire, pir, gas)
    return _sensor_status.to_dict()


def get_sensor_status() -> dict[str, Any]:
    """Get current sensor status.

    Returns:
        Dictionary with sensor readings and last update time.
    """
    return _sensor_status.to_dict()


def get_system_with_sensors() -> dict[str, Any]:
    """Get combined system overview and sensor status.

    Returns:
        Dictionary containing both system telemetry and sensor data.
    """
    system_overview = get_system_overview()
    return {
        "system": system_overview.model_dump(),
        "sensors": _sensor_status.to_dict(),
        "observed_at": datetime.now(UTC).isoformat(),
    }
