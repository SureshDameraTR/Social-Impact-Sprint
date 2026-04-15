"""Unit tests for IoT endpoints — /v1/iot."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# GET /v1/iot/devices
# ---------------------------------------------------------------------------


class TestListDevices:
    async def test_list_success(self, client: AsyncClient) -> None:
        """GET returns 200 with device list."""
        with patch(
            "app.routers.iot.iot_service.list_devices",
            new_callable=AsyncMock,
            return_value={"data": [], "total": 0},
        ):
            resp = await client.get("/v1/iot/devices")
            assert resp.status_code == 200

    async def test_list_with_status_filter(self, client: AsyncClient) -> None:
        """GET with status filter returns 200."""
        with patch(
            "app.routers.iot.iot_service.list_devices",
            new_callable=AsyncMock,
            return_value={"data": [], "total": 0},
        ):
            resp = await client.get("/v1/iot/devices?status=active")
            assert resp.status_code == 200

    async def test_list_gateway_error(self, client: AsyncClient) -> None:
        """GET when gateway is down returns 502."""
        with patch(
            "app.routers.iot.iot_service.list_devices",
            new_callable=AsyncMock,
            side_effect=httpx.RequestError("Connection refused"),
        ):
            resp = await client.get("/v1/iot/devices")
            assert resp.status_code == 502

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/iot/devices")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/iot/device-types
# ---------------------------------------------------------------------------


class TestListDeviceTypes:
    async def test_device_types_success(self, client: AsyncClient) -> None:
        """GET returns 200 with aggregated device types."""
        mock_devices = {
            "data": [
                {"device_id": "D1", "type": "temperature", "status": "active"},
                {"device_id": "D2", "type": "temperature", "status": "inactive"},
                {"device_id": "D3", "type": "gps", "status": "active"},
            ],
            "total": 3,
        }
        with patch(
            "app.routers.iot.iot_service.list_devices",
            new_callable=AsyncMock,
            return_value=mock_devices,
        ):
            resp = await client.get("/v1/iot/device-types")
            assert resp.status_code == 200
            body = resp.json()
            assert isinstance(body, list)

    async def test_device_types_gateway_down(self, client: AsyncClient) -> None:
        """GET when gateway is down returns empty list."""
        with patch(
            "app.routers.iot.iot_service.list_devices",
            new_callable=AsyncMock,
            side_effect=httpx.RequestError("timeout"),
        ):
            resp = await client.get("/v1/iot/device-types")
            assert resp.status_code == 200
            assert resp.json() == []


# ---------------------------------------------------------------------------
# GET /v1/iot/readings
# ---------------------------------------------------------------------------


class TestListReadings:
    async def test_readings_with_device_id(self, client: AsyncClient) -> None:
        """GET with device_id returns 200."""
        with patch(
            "app.routers.iot.iot_service.get_telemetry",
            new_callable=AsyncMock,
            return_value={"data": [], "total": 0},
        ):
            resp = await client.get("/v1/iot/readings?device_id=D1")
            assert resp.status_code == 200

    async def test_readings_all_devices(self, client: AsyncClient) -> None:
        """GET without device_id fetches all."""
        with patch(
            "app.routers.iot.iot_service.list_devices",
            new_callable=AsyncMock,
            return_value={"data": [], "total": 0},
        ):
            resp = await client.get("/v1/iot/readings")
            assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /v1/iot/devices/{device_id}
# ---------------------------------------------------------------------------


class TestGetDevice:
    async def test_get_success(self, client: AsyncClient) -> None:
        """GET returns 200."""
        with patch(
            "app.routers.iot.iot_service.get_device",
            new_callable=AsyncMock,
            return_value={"device_id": "D1", "type": "temperature", "status": "active"},
        ):
            resp = await client.get("/v1/iot/devices/D1")
            assert resp.status_code == 200

    async def test_get_gateway_error(self, client: AsyncClient) -> None:
        """GET when gateway is down returns 502."""
        with patch(
            "app.routers.iot.iot_service.get_device",
            new_callable=AsyncMock,
            side_effect=httpx.RequestError("timeout"),
        ):
            resp = await client.get("/v1/iot/devices/D1")
            assert resp.status_code == 502


# ---------------------------------------------------------------------------
# GET /v1/iot/devices/{device_id}/latest
# ---------------------------------------------------------------------------


class TestGetLatestTelemetry:
    async def test_latest_success(self, client: AsyncClient) -> None:
        """GET returns 200."""
        with patch(
            "app.routers.iot.iot_service.get_latest_telemetry",
            new_callable=AsyncMock,
            return_value={"temperature": 38.5, "timestamp": "2026-04-15T10:00:00Z"},
        ):
            resp = await client.get("/v1/iot/devices/D1/latest")
            assert resp.status_code == 200
