"""IoT device and sensor reading endpoints.

Proxies requests to the IoT gateway backend when configured.
Falls back to 503 via global exception handler when the gateway URL is not set.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, Query, HTTPException

from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import iot_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/iot", tags=["IoT"])


@router.get("/devices")
async def list_devices(
    status: str = Query(None, description="Filter by device status"),
    device_type: str = Query(None, description="Filter by device type"),
    current_user: User = Depends(get_current_user),
):
    """List IoT devices for the current user."""
    try:
        return await iot_service.list_devices(status=status, device_type=device_type)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="IoT gateway error")
    except httpx.RequestError:
        logger.exception("IoT gateway request failed")
        raise HTTPException(status_code=502, detail="IoT gateway unavailable")


@router.get("/device-types")
async def list_device_types(
    current_user: User = Depends(get_current_user),
):
    """List supported IoT device types."""
    return {
        "device_types": [
            {"type": "temperature_sensor", "label": "Temperature Sensor", "count": 0},
            {"type": "humidity_sensor", "label": "Humidity Sensor", "count": 0},
            {"type": "pedometer", "label": "Pedometer (Activity Tracker)", "count": 0},
            {"type": "milk_meter", "label": "Milk Flow Meter", "count": 0},
            {"type": "gps_collar", "label": "GPS Collar", "count": 0},
        ]
    }


@router.get("/readings")
async def list_readings(
    device_id: str | None = Query(None, description="Filter by device ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get IoT sensor readings."""
    try:
        return await iot_service.get_telemetry(device_id=device_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="IoT gateway error")
    except httpx.RequestError:
        logger.exception("IoT gateway request failed")
        raise HTTPException(status_code=502, detail="IoT gateway unavailable")


@router.get("/devices/{device_id}")
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a single IoT device by ID."""
    try:
        return await iot_service.get_device(device_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="IoT gateway error")
    except httpx.RequestError:
        logger.exception("IoT gateway request failed")
        raise HTTPException(status_code=502, detail="IoT gateway unavailable")


@router.get("/devices/{device_id}/latest")
async def get_latest_telemetry(
    device_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get the latest telemetry reading for a device."""
    try:
        return await iot_service.get_latest_telemetry(device_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="IoT gateway error")
    except httpx.RequestError:
        logger.exception("IoT gateway request failed")
        raise HTTPException(status_code=502, detail="IoT gateway unavailable")
