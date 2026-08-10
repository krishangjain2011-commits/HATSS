"""ESP32 sensor data management."""

from datetime import datetime
import time

# Global sensor state
sensor_state = {
    "fire": False,
    "pir": False,
    "gas": False,
    "last_update": "Not received yet",
    "status": "disconnected"
}


def update_sensors(fire: bool, pir: bool, gas: bool) -> dict:
    """Update sensor readings from ESP32."""
    global sensor_state
    
    sensor_state["fire"] = bool(fire)
    sensor_state["pir"] = bool(pir)
    sensor_state["gas"] = bool(gas)
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
    
    return {
        "has_alerts": len(alerts) > 0,
        "alerts": alerts,
        "severity": "critical" if any([sensor_state["fire"], sensor_state["gas"]]) else 
                   "warning" if sensor_state["pir"] else "safe"
    }
