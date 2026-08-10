"""ESP32 sensor endpoints."""

import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.sensors import SensorStatus, SensorReading
from app.services.esp32_sensors import update_sensors, get_sensor_status, get_alert_status
from app.services.intrusion_detector import get_intrusion_count
from datetime import datetime

router = APIRouter(prefix="/sensors", tags=["sensors"])


class SensorDataInput(BaseModel):
    """Input for sensor data from ESP32."""
    fire: bool
    pir: bool
    gas: bool


@router.post("/data", response_model=dict, summary="Receive sensor data from ESP32")
async def receive_sensor_data(data: SensorDataInput) -> dict:
    """
    Receive and store sensor data from ESP32.
    
    Expected POST body:
    {
        "fire": false,
        "pir": true,
        "gas": false
    }
    """
    try:
        sensor_state = await asyncio.to_thread(update_sensors, data.fire, data.pir, data.gas)
        alert_status = await asyncio.to_thread(get_alert_status)
        
        return {
            "message": "✅ Sensor data received successfully",
            "sensor_state": sensor_state,
            "alert_status": alert_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=SensorStatus, summary="Get current sensor status")
async def get_sensors() -> SensorStatus:
    """Get current sensor status."""
    status = await asyncio.to_thread(get_sensor_status)
    return SensorStatus(
        fire=status["fire"],
        pir=status["pir"],
        gas=status["gas"],
        last_update=status["last_update"],
        status=status["status"]
    )


@router.get("/alerts", response_model=dict, summary="Get current alert status")
async def get_alerts() -> dict:
    """Get current alert status based on sensors."""
    return await asyncio.to_thread(get_alert_status)


@router.get("/metrics", response_model=dict, summary="Get sensor metrics")
async def get_metrics() -> dict:
    """Get sensor metrics including intrusion count."""
    status = await asyncio.to_thread(get_sensor_status)
    intrusion_count = await asyncio.to_thread(get_intrusion_count)
    return {
        "fire_active": status["fire"],
        "pir_active": status["pir"],
        "gas_active": status["gas"],
        "last_update": status["last_update"],
        "total_intrusions": intrusion_count,
        "critical_alerts": int(status["fire"]) + int(status["gas"])
    }
