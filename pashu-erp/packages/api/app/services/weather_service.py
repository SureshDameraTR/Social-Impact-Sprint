"""IMD weather service for Karnataka districts.

Tries Open-Meteo (free, no key) first, falls back to the mock weather backend
when Open-Meteo is unavailable or not configured.

Requires WEATHER_API_URL setting for the mock fallback path.
Raises ServiceNotConfiguredError when both sources are unavailable.
"""

import logging

from app.config import settings
from app.schemas.weather import WeatherForecast
from app.services.circuit_breakers import weather_breaker
from app.services.errors import ServiceNotConfiguredError
from app.services.http_client import get_http_client, retry_on_network

logger = logging.getLogger(__name__)


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


def _get_app_state():
    """Access the running FastAPI app's state for the Open-Meteo service."""
    from app.main import app

    return app.state


def _derive_condition(precipitation_mm: float, humidity: float, wind_kmh: float) -> str:
    """Derive a human-readable weather condition from Open-Meteo variables."""
    if precipitation_mm > 25:
        return "Thunderstorm" if wind_kmh > 20 else "Heavy Rain"
    if precipitation_mm > 10:
        return "Heavy Rain" if wind_kmh > 15 else "Moderate Rain"
    if precipitation_mm > 2:
        return "Moderate Rain" if wind_kmh > 10 else "Light Rain"
    if precipitation_mm > 0:
        return "Light Rain"
    if humidity > 70:
        return "Cloudy"
    if humidity > 50:
        return "Partly Cloudy"
    return "Clear Sky"


def _transform_open_meteo_response(data: dict, district: str) -> list[WeatherForecast]:
    """Transform Open-Meteo response to a list of WeatherForecast objects."""
    daily = data.get("daily", {})
    forecasts = []
    for i, date_str in enumerate(daily.get("time", [])):
        temp_max = daily.get("temperature_2m_max", [None])[i]
        temp_min = daily.get("temperature_2m_min", [None])[i]
        precipitation = daily.get("precipitation_sum", [0.0])[i] or 0.0
        wind_speed = daily.get("windspeed_10m_max", [0.0])[i] or 0.0
        humidity_max = daily.get("relative_humidity_2m_max", [50.0])[i] or 50.0
        humidity_min = daily.get("relative_humidity_2m_min", [30.0])[i] or 30.0

        # Use average humidity for the day
        humidity = round((humidity_max + humidity_min) / 2.0, 1)

        # Derive condition from precipitation, humidity, and wind
        condition = _derive_condition(precipitation, humidity, wind_speed)

        # Compute heat stress index using the existing THI formula
        avg_temp = ((temp_max or 25.0) + (temp_min or 15.0)) / 2.0
        heat_stress = _calculate_heat_stress_index(avg_temp, humidity)

        forecasts.append(WeatherForecast(
            date=date_str,
            district=district,
            temp_min=temp_min or 0.0,
            temp_max=temp_max or 0.0,
            humidity=humidity,
            rainfall_mm=precipitation,
            wind_speed=wind_speed,
            condition=condition,
            heat_stress_index=heat_stress,
        ))
    return forecasts


@weather_breaker
@retry_on_network
async def get_forecast(district: str, days: int = 5) -> list[WeatherForecast]:
    """Return weather forecast -- tries Open-Meteo first, falls back to mock."""
    open_meteo = getattr(_get_app_state(), "open_meteo", None)

    if open_meteo:
        try:
            from app.database import async_session

            async with async_session() as db_session:
                result = await open_meteo.get_forecast_for_district(
                    district, days, db_session
                )
                if result:
                    return _transform_open_meteo_response(result, district)
        except Exception:
            logger.warning(
                "Open-Meteo failed for %s, falling back to mock", district
            )

    # Fallback: mock weather backend
    base_url = _require_weather_url()
    client = await get_http_client()
    resp = await client.get(
        f"{base_url}/forecast",
        params={"district": district, "days": days},
    )
    resp.raise_for_status()
    return [WeatherForecast(**item) for item in resp.json()]


@weather_breaker
@retry_on_network
async def get_alerts(district: str) -> list[dict]:
    """Return active weather alerts for a district."""
    base_url = _require_weather_url()
    client = await get_http_client()
    resp = await client.get(
        f"{base_url}/alerts",
        params={"district": district},
    )
    resp.raise_for_status()
    return resp.json()


@weather_breaker
@retry_on_network
async def get_tts(district: str, language_code: str = "kn") -> dict:
    """Request text-to-speech weather summary for a district."""
    base_url = _require_weather_url()
    client = await get_http_client()
    resp = await client.post(
        f"{base_url}/tts",
        json={"district": district, "language_code": language_code},
    )
    resp.raise_for_status()
    return resp.json()
