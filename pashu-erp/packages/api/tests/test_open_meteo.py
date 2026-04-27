"""Tests for Open-Meteo weather service."""

from unittest.mock import AsyncMock, MagicMock

from app.services.open_meteo import OpenMeteoService


class TestOpenMeteoService:
    async def test_get_forecast_returns_daily_data(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "daily": {
                "time": ["2026-04-27", "2026-04-28"],
                "temperature_2m_max": [32.5, 33.1],
                "temperature_2m_min": [22.1, 23.0],
                "precipitation_sum": [0.0, 2.5],
                "windspeed_10m_max": [12.3, 15.6],
            }
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        service = OpenMeteoService(http_client=mock_client)
        result = await service.get_forecast(latitude=12.30, longitude=76.66, days=2)

        assert len(result["daily"]["time"]) == 2
        assert result["daily"]["temperature_2m_max"][0] == 32.5
        mock_client.get.assert_called_once()

    async def test_get_forecast_for_district(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": ["2026-04-27"]}}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        service = OpenMeteoService(http_client=mock_client)
        await service.get_forecast(latitude=12.30, longitude=76.66, days=1)

        call_args = mock_client.get.call_args
        assert "api.open-meteo.com" in str(call_args)

    async def test_forecast_uses_cache(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"daily": {"time": ["2026-04-27"]}}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        service = OpenMeteoService(http_client=mock_client, cache_ttl=300)
        await service.get_forecast(latitude=12.30, longitude=76.66, days=1)
        await service.get_forecast(latitude=12.30, longitude=76.66, days=1)

        assert mock_client.get.call_count == 1
