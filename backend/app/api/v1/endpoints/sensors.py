"""ESP32 sensor endpoints."""

import asyncio
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.sensors import SensorStatus, SensorReading
from app.services.esp32_sensors import update_sensors, get_sensor_status, get_alert_status
from app.services.intrusion_detector import get_intrusion_count
from datetime import datetime

router = APIRouter(prefix="/sensors", tags=["sensors"])

ESP32_IP = "192.168.4.1"
ESP32_URL = f"http://{ESP32_IP}/api/sensors"


class SensorDataInput(BaseModel):
    """Input for sensor data from ESP32."""
    fire: bool
    pir: bool
    gas: bool
    water_level: float = 0.0  # 0-100%


async def fetch_from_esp32() -> dict:
    """Fetch sensor data directly from ESP32."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(ESP32_URL)
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"ESP32 fetch error: {e}")
    return None


@router.get("/esp32/live", response_model=dict, summary="Get live sensor data from ESP32")
async def get_esp32_live() -> dict:
    """
    Fetch live sensor data directly from ESP32.
    
    Returns:
    {
        "ir": false,
        "flame": false,
        "gas": false,
        "water": 45.5,
        "mq2_rating": 3,
        "buzzer": false,
        "muted": false,
        "raw_water": 2500
    }
    """
    data = await fetch_from_esp32()
    if data:
        return {
            "fire": data.get("flame", False),
            "pir": data.get("ir", False),
            "gas": data.get("gas", False),
            "water_level": data.get("water", 0),
            "mq2_rating": data.get("mq2_rating", 0),
            "raw_water": data.get("raw_water", 0),
            "last_update": datetime.now().isoformat(),
            "source": "esp32"
        }
    raise HTTPException(status_code=503, detail="ESP32 not responding")


@router.post("/data", response_model=dict, summary="Receive sensor data from ESP32")
async def receive_sensor_data(data: SensorDataInput) -> dict:
    """
    Receive and store sensor data from ESP32.
    
    Expected POST body:
    {
        "fire": false,
        "pir": true,
        "gas": false,
        "water_level": 45.5
    }
    """
    try:
        sensor_state = await asyncio.to_thread(update_sensors, data.fire, data.pir, data.gas, data.water_level)
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
        water_level=status.get("water_level", 0.0),
        water_level_alert=status.get("water_level_alert", False),
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
        "water_level": status.get("water_level", 0.0),
        "water_level_alert": status.get("water_level_alert", False),
        "last_update": status["last_update"],
        "total_intrusions": intrusion_count,
        "critical_alerts": int(status["fire"]) + int(status["gas"]) + int(status.get("water_level_alert", False))
    }
