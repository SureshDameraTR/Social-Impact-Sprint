"""IMD weather service for Karnataka districts.

Requires WEATHER_API_URL setting to be configured.
Raises ServiceNotConfiguredError when the URL is empty.
"""

import httpx

from app.config import settings
from app.schemas.weather import WeatherForecast
from app.services.errors import ServiceNotConfiguredError

KARNATAKA_DISTRICTS = {
    "dharwad": {"lat": 15.46, "lon": 75.01},
    "belgaum": {"lat": 15.85, "lon": 74.50},
    "mysore": {"lat": 12.30, "lon": 76.66},
    "tumkur": {"lat": 13.34, "lon": 77.10},
    "shimoga": {"lat": 13.93, "lon": 75.57},
    "hassan": {"lat": 13.01, "lon": 76.10},
    "mandya": {"lat": 12.52, "lon": 76.90},
    "davanagere": {"lat": 14.47, "lon": 75.92},
    "haveri": {"lat": 14.79, "lon": 75.40},
    "raichur": {"lat": 16.21, "lon": 77.37},
    "bagalkot": {"lat": 16.18, "lon": 75.70},
    "bidar": {"lat": 17.91, "lon": 77.52},
}

_TIMEOUT = 10.0


def _require_weather_url() -> str:
    url = settings.weather_api_url
    if not url:
        raise ServiceNotConfiguredError("WEATHER_API_URL")
    return url


def _calculate_heat_stress_index(temp_max: float, humidity: float) -> float:
    """Simplified heat stress index (Temperature-Humidity Index).

    THI = 0.8 * T + (RH/100) * (T - 14.4) + 46.4
    Normal < 72, Mild stress 72-78, Moderate 78-88, Severe > 88
    """
    thi = 0.8 * temp_max + (humidity / 100) * (temp_max - 14.4) + 46.4
    return round(thi, 1)


async def get_forecast(district: str, days: int = 5) -> list[WeatherForecast]:
    """Return weather forecast for a Karnataka district."""
    base_url = _require_weather_url()
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            f"{base_url}/forecast",
            params={"district": district, "days": days},
        )
        resp.raise_for_status()
        return [WeatherForecast(**item) for item in resp.json()]


async def get_alerts(district: str) -> list[dict]:
    """Return active weather alerts for a district."""
    base_url = _require_weather_url()
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            f"{base_url}/alerts",
            params={"district": district},
        )
        resp.raise_for_status()
        return resp.json()


async def get_tts(district: str, language_code: str = "kn") -> dict:
    """Request text-to-speech weather summary for a district."""
    base_url = _require_weather_url()
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{base_url}/tts",
            json={"district": district, "language_code": language_code},
        )
        resp.raise_for_status()
        return resp.json()
