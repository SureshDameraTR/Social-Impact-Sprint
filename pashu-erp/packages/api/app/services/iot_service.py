"""IoT gateway service client.

Proxies requests to the configured IoT gateway backend.
"""

from typing import Optional

import httpx

from app.config import settings
from app.services.errors import ServiceNotConfiguredError


def _base_url() -> str:
    url = settings.iot_gateway_url
    if not url:
        raise ServiceNotConfiguredError("IOT_GATEWAY_URL")
    return url.rstrip("/")


async def list_devices(
    status: Optional[str] = None,
    device_type: Optional[str] = None,
) -> dict:
    """List IoT devices with optional filters."""
    base = _base_url()
    params: dict = {}
    if status is not None:
        params["status"] = status
    if device_type is not None:
        params["device_type"] = device_type

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{base}/devices", params=params)
        resp.raise_for_status()
        return resp.json()


async def get_device(device_id: str) -> dict:
    """Get a single IoT device by ID."""
    base = _base_url()

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{base}/devices/{device_id}")
        resp.raise_for_status()
        return resp.json()


async def get_latest_telemetry(device_id: str) -> dict:
    """Get the latest telemetry reading for a device."""
    base = _base_url()

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{base}/devices/{device_id}/latest")
        resp.raise_for_status()
        return resp.json()


async def get_telemetry(
    device_id: Optional[str] = None,
    metric: Optional[str] = None,
    from_ts: Optional[str] = None,
    to_ts: Optional[str] = None,
) -> dict:
    """Query telemetry data with optional filters."""
    base = _base_url()
    params: dict = {}
    if device_id is not None:
        params["device_id"] = device_id
    if metric is not None:
        params["metric"] = metric
    if from_ts is not None:
        params["from"] = from_ts
    if to_ts is not None:
        params["to"] = to_ts

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{base}/telemetry", params=params)
        resp.raise_for_status()
        return resp.json()
