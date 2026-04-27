"""Tests for IoT gateway service client (app.services.iot_service)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.errors import ServiceNotConfiguredError
from app.services.iot_service import (
    get_device,
    get_latest_telemetry,
    get_telemetry,
    list_devices,
)


def _mock_client(response_json, method="get"):
    """Helper to build a mock client with a canned response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = response_json
    mock_resp.raise_for_status = MagicMock()

    mc = AsyncMock()
    getattr(mc, method).return_value = mock_resp
    return mc


def _patch_client(mc):
    """Patch get_http_client to return the mock client."""
    return patch(
        "app.services.iot_service.get_http_client",
        new_callable=AsyncMock,
        return_value=mc,
    )


# ---------------------------------------------------------------------------
# list_devices
# ---------------------------------------------------------------------------


class TestListDevices:
    async def test_returns_device_list(self):
        payload = {
            "data": [{"device_id": "D1", "type": "temperature"}],
            "total": 1,
        }
        mc = _mock_client(payload)

        with (
            patch("app.services.iot_service.settings") as s,
            _patch_client(mc),
        ):
            s.iot_gateway_url = "http://mock:8001/iot"
            result = await list_devices()

        assert result["total"] == 1
        assert result["data"][0]["device_id"] == "D1"

    async def test_filters_passed_as_params(self):
        mc = _mock_client({"data": [], "total": 0})

        with (
            patch("app.services.iot_service.settings") as s,
            _patch_client(mc),
        ):
            s.iot_gateway_url = "http://mock:8001/iot"
            await list_devices(status="active", device_type="gps")

        call_kwargs = mc.get.call_args
        assert call_kwargs.kwargs["params"]["status"] == "active"
        assert call_kwargs.kwargs["params"]["type"] == "gps"

    async def test_not_configured_raises(self):
        with patch("app.services.iot_service.settings") as s:
            s.iot_gateway_url = ""
            with pytest.raises(ServiceNotConfiguredError):
                await list_devices()


# ---------------------------------------------------------------------------
# get_telemetry
# ---------------------------------------------------------------------------


class TestGetTelemetry:
    async def test_returns_telemetry_data(self):
        payload = {
            "data": [{"metric": "temperature", "value": 38.5}],
            "total": 1,
        }
        mc = _mock_client(payload)

        with (
            patch("app.services.iot_service.settings") as s,
            _patch_client(mc),
        ):
            s.iot_gateway_url = "http://mock:8001/iot"
            result = await get_telemetry(device_id="D1", metric="temperature")

        assert result["total"] == 1

    async def test_http_error_propagates(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "unavailable", request=MagicMock(), response=mock_resp
        )

        mc = AsyncMock()
        mc.get.return_value = mock_resp

        with (
            patch("app.services.iot_service.settings") as s,
            _patch_client(mc),
        ):
            s.iot_gateway_url = "http://mock:8001/iot"
            with pytest.raises(httpx.HTTPStatusError):
                await get_telemetry(device_id="D1")


# ---------------------------------------------------------------------------
# get_device + get_latest_telemetry
# ---------------------------------------------------------------------------


class TestGetDevice:
    async def test_get_device_success(self):
        payload = {"device_id": "D1", "type": "gps", "status": "active"}
        mc = _mock_client(payload)

        with (
            patch("app.services.iot_service.settings") as s,
            _patch_client(mc),
        ):
            s.iot_gateway_url = "http://mock:8001/iot"
            result = await get_device("D1")

        assert result["device_id"] == "D1"

    async def test_get_latest_telemetry_success(self):
        payload = {"temperature": 38.5, "timestamp": "2026-04-15T10:00:00Z"}
        mc = _mock_client(payload)

        with (
            patch("app.services.iot_service.settings") as s,
            _patch_client(mc),
        ):
            s.iot_gateway_url = "http://mock:8001/iot"
            result = await get_latest_telemetry("D1")

        assert result["temperature"] == 38.5
