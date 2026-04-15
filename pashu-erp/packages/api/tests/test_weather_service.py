"""Tests for weather service client (app.services.weather_service)."""

from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest

from app.services.errors import ServiceNotConfiguredError
from app.services.weather_service import get_forecast, get_alerts, get_tts


# ---------------------------------------------------------------------------
# get_forecast
# ---------------------------------------------------------------------------

class TestGetForecast:

    async def test_happy_path(self):
        """Returns list of WeatherForecast objects on success."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {
                "date": "2026-04-15",
                "district": "tumkur",
                "temp_min": 22.0,
                "temp_max": 35.0,
                "humidity": 60.0,
                "rainfall_mm": 0.0,
                "wind_speed": 12.0,
                "condition": "Clear",
                "heat_stress_index": 75.0,
            }
        ]
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.weather_service.settings") as mock_settings, \
             patch("app.services.weather_service.httpx.AsyncClient", return_value=mock_client):
            mock_settings.weather_api_url = "http://mock:8001/weather"
            forecasts = await get_forecast("tumkur", days=1)

        assert len(forecasts) == 1
        assert forecasts[0].district == "tumkur"
        assert forecasts[0].temp_max == 35.0

    async def test_not_configured_raises(self):
        """Raises ServiceNotConfiguredError when URL is empty."""
        with patch("app.services.weather_service.settings") as mock_settings:
            mock_settings.weather_api_url = ""
            with pytest.raises(ServiceNotConfiguredError):
                await get_forecast("tumkur")

    async def test_http_error_propagates(self):
        """HTTP errors from the upstream API propagate as HTTPStatusError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 502
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "bad gateway", request=MagicMock(), response=mock_resp
        )

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.weather_service.settings") as mock_settings, \
             patch("app.services.weather_service.httpx.AsyncClient", return_value=mock_client):
            mock_settings.weather_api_url = "http://mock:8001/weather"
            with pytest.raises(httpx.HTTPStatusError):
                await get_forecast("tumkur")


# ---------------------------------------------------------------------------
# get_alerts
# ---------------------------------------------------------------------------

class TestGetAlerts:

    async def test_returns_list(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"type": "heat_wave", "severity": "extreme"}]
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.weather_service.settings") as mock_settings, \
             patch("app.services.weather_service.httpx.AsyncClient", return_value=mock_client):
            mock_settings.weather_api_url = "http://mock:8001/weather"
            alerts = await get_alerts("tumkur")

        assert len(alerts) == 1
        assert alerts[0]["type"] == "heat_wave"


# ---------------------------------------------------------------------------
# get_tts
# ---------------------------------------------------------------------------

class TestGetTts:

    async def test_returns_dict(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"text": "Clear sky", "audio_url": None}
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.weather_service.settings") as mock_settings, \
             patch("app.services.weather_service.httpx.AsyncClient", return_value=mock_client):
            mock_settings.weather_api_url = "http://mock:8001/weather"
            result = await get_tts("tumkur", language_code="kn")

        assert result["text"] == "Clear sky"
