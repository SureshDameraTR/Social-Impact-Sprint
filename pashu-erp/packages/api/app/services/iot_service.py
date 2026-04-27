"""IoT gateway service client.

Proxies requests to the configured IoT gateway backend.
"""

from app.config import settings
from app.services.circuit_breakers import iot_breaker
from app.services.errors import ServiceNotConfiguredError
from app.services.http_client import get_http_client, retry_on_network


def _base_url() -> str:
    url = settings.iot_gateway_url
    if not url:
        raise ServiceNotConfiguredError("IOT_GATEWAY_URL")
    return url.rstrip("/")


@iot_breaker
@retry_on_network
async def list_devices(
    status: str | None = None,
    device_type: str | None = None,
) -> dict:
    """List IoT devices with optional filters."""
    base = _base_url()
    params: dict = {}
    if status is not None:
        params["status"] = status
    if device_type is not None:
        params["type"] = device_type

    client = await get_http_client()
    resp = await client.get(f"{base}/devices", params=params)
    resp.raise_for_status()
    return resp.json()


@iot_breaker
@retry_on_network
async def get_device(device_id: str) -> dict:
    """Get a single IoT device by ID."""
    base = _base_url()

    client = await get_http_client()
    resp = await client.get(f"{base}/devices/{device_id}")
    resp.raise_for_status()
    return resp.json()


@iot_breaker
@retry_on_network
async def get_latest_telemetry(device_id: str) -> dict:
    """Get the latest telemetry reading for a device."""
    base = _base_url()

    client = await get_http_client()
    resp = await client.get(f"{base}/devices/{device_id}/latest")
    resp.raise_for_status()
    return resp.json()


@iot_breaker
@retry_on_network
async def get_telemetry(
    device_id: str | None = None,
    metric: str | None = None,
    from_ts: str | None = None,
    to_ts: str | None = None,
) -> dict:
    """Query telemetry data with optional filters."""
    base = _base_url()
    params: dict = {}
    if device_id is not None:
        params["device_id"] = device_id
    if metric is not None:
        params["metric"] = metric
    if from_ts is not None:
        params["from_ts"] = from_ts
    if to_ts is not None:
        params["to_ts"] = to_ts

    client = await get_http_client()
    resp = await client.get(f"{base}/telemetry", params=params)
    resp.raise_for_status()
    return resp.json()
