"""IoT device and sensor reading endpoints.

Proxies requests to the IoT gateway backend when configured.
Falls back to 503 via global exception handler when the gateway URL is not set.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.iot import (
    DeviceTypeCount,
    IoTDeviceRead,
    TelemetryListResponse,
    TelemetryReading,
)
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


@router.get("/device-types", response_model=list[DeviceTypeCount])
async def list_device_types(
    current_user: User = Depends(get_current_user),
):
    """List IoT device types aggregated from the gateway."""
    try:
        devices_resp = await iot_service.list_devices()
        devices = devices_resp.get("data", [])
    except (httpx.HTTPStatusError, httpx.RequestError, Exception):
        logger.warning("IoT gateway unavailable for device-types aggregation")
        devices = []

    # Aggregate by device type
    type_map: dict[str, dict] = {}
    for d in devices:
        dt = d.get("type", "unknown")
        if dt not in type_map:
            type_map[dt] = {"name": dt, "total": 0, "online": 0, "offline": 0}
        type_map[dt]["total"] += 1
        if d.get("status") == "active":
            type_map[dt]["online"] += 1
        else:
            type_map[dt]["offline"] += 1

    return list(type_map.values())


@router.get("/readings", response_model=TelemetryListResponse)
async def list_readings(
    device_id: str | None = Query(None, description="Filter by device ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get IoT sensor readings from the gateway.

    When no device_id is given, fetches the latest reading for each device.
    """
    try:
        if device_id:
            return await iot_service.get_telemetry(device_id=device_id)

        # No device_id — aggregate latest from all devices
        devices_resp = await iot_service.list_devices()
        all_devices = devices_resp.get("data", [])
        readings = []
        for dev in all_devices[:limit]:
            try:
                latest = await iot_service.get_latest_telemetry(dev["device_id"])
                readings.append(latest)
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                logger.warning("Telemetry fetch failed for %s: %s", dev["device_id"], exc)
                continue
        return {"data": readings, "total": len(readings)}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="IoT gateway error")
    except httpx.RequestError:
        logger.exception("IoT gateway request failed")
        raise HTTPException(status_code=502, detail="IoT gateway unavailable")


@router.get("/devices/{device_id}", response_model=IoTDeviceRead)
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


@router.get("/devices/{device_id}/latest", response_model=TelemetryReading)
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
