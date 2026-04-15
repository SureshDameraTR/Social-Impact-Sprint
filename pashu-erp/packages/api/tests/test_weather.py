"""Unit tests for Weather endpoints — /v1/weather."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# GET /v1/weather/forecast/{district}
# ---------------------------------------------------------------------------


class TestWeatherForecast:
    async def test_forecast_success(self, client: AsyncClient) -> None:
        """GET returns 200 with forecast data."""
        mock_forecast = MagicMock()
        mock_forecast.model_dump.return_value = {
            "date": "2026-04-15",
            "max_temp": 35,
            "min_temp": 22,
            "condition": "Clear",
        }

        with patch(
            "app.routers.weather.get_forecast",
            new_callable=AsyncMock,
            return_value=[mock_forecast],
        ):
            resp = await client.get("/v1/weather/forecast/tumkur")
            assert resp.status_code == 200
            body = resp.json()
            assert body["district"] == "Tumkur"
            assert "forecasts" in body
            assert "source" in body

    async def test_forecast_with_days_param(self, client: AsyncClient) -> None:
        """GET with days parameter returns 200."""
        with patch(
            "app.routers.weather.get_forecast",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get("/v1/weather/forecast/tumkur?days=3")
            assert resp.status_code == 200
            assert resp.json()["days"] == 3

    async def test_forecast_external_error(self, client: AsyncClient) -> None:
        """GET when external API errors returns HTTP error."""
        mock_resp = MagicMock()
        mock_resp.status_code = 502
        mock_resp.text = "Gateway error"
        exc = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_resp
        )

        with patch(
            "app.routers.weather.get_forecast",
            new_callable=AsyncMock,
            side_effect=exc,
        ):
            resp = await client.get("/v1/weather/forecast/tumkur")
            assert resp.status_code == 502


# ---------------------------------------------------------------------------
# GET /v1/weather/alerts/{district}
# ---------------------------------------------------------------------------


class TestWeatherAlerts:
    async def test_alerts_success(self, client: AsyncClient) -> None:
        """GET returns 200 with alert data."""
        with patch(
            "app.routers.weather.get_alerts",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get("/v1/weather/alerts/tumkur")
            assert resp.status_code == 200
            body = resp.json()
            assert "active_alerts" in body
            assert "count" in body


# ---------------------------------------------------------------------------
# GET /v1/weather/tts/{district}
# ---------------------------------------------------------------------------


class TestWeatherTTS:
    async def test_tts_success(self, client: AsyncClient) -> None:
        """GET returns 200 with TTS data."""
        with patch(
            "app.routers.weather.get_tts",
            new_callable=AsyncMock,
            return_value={"text": "Today is sunny", "audio_url": None},
        ):
            resp = await client.get("/v1/weather/tts/tumkur")
            assert resp.status_code == 200

    async def test_tts_with_lang_param(self, client: AsyncClient) -> None:
        """GET with lang parameter returns 200."""
        with patch(
            "app.routers.weather.get_tts",
            new_callable=AsyncMock,
            return_value={"text": "Today is sunny", "audio_url": None},
        ):
            resp = await client.get("/v1/weather/tts/tumkur?lang=en")
            assert resp.status_code == 200
