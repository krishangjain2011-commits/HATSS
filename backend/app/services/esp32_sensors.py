"""ESP32 sensor data management."""

from datetime import datetime
import time

# Global sensor state
sensor_state = {
    "fire": False,
    "pir": False,
    "gas": False,
    "water_level": 0.0,  # 0-100%
    "water_level_alert": False,
    "last_update": "Not received yet",
    "status": "disconnected"
}

# Water level threshold (%) - alert if above this
WATER_LEVEL_THRESHOLD = 75.0


def update_sensors(fire: bool, pir: bool, gas: bool, water_level: float = 0.0) -> dict:
    """Update sensor readings from ESP32."""
    global sensor_state
    
    # Clamp water level to 0-100%
    water_level = max(0.0, min(100.0, float(water_level)))
    
    sensor_state["fire"] = bool(fire)
    sensor_state["pir"] = bool(pir)
    sensor_state["gas"] = bool(gas)
    sensor_state["water_level"] = water_level
    sensor_state["water_level_alert"] = water_level > WATER_LEVEL_THRESHOLD
    sensor_state["last_update"] = datetime.now().strftime("%H:%M:%S")
    sensor_state["status"] = "connected"
    
    return sensor_state


def get_sensor_status() -> dict:
    """Get current sensor status."""
    return sensor_state.copy()


def get_alert_status() -> dict:
    """Get alert status based on sensor readings."""
    alerts = []
    
    if sensor_state["fire"]:
        alerts.append("🔥 FIRE DETECTED")
    if sensor_state["pir"]:
        alerts.append("👁️ MOTION DETECTED")
    if sensor_state["gas"]:
        alerts.append("🛢️ GAS LEAK DETECTED")
    if sensor_state["water_level_alert"]:
        alerts.append(f"💧 HIGH WATER LEVEL ({sensor_state['water_level']:.1f}%)")
    
    return {
        "has_alerts": len(alerts) > 0,
        "alerts": alerts,
        "severity": "critical" if any([sensor_state["fire"], sensor_state["gas"], sensor_state["water_level_alert"]]) else 
                   "warning" if sensor_state["pir"] else "safe",
        "water_level": sensor_state["water_level"],
        "water_level_alert": sensor_state["water_level_alert"]
    }
