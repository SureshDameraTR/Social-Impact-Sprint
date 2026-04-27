"""IMD weather service for Karnataka districts.

Requires WEATHER_API_URL setting to be configured.
Raises ServiceNotConfiguredError when the URL is empty.
"""

from app.config import settings
from app.schemas.weather import WeatherForecast
from app.services.circuit_breakers import weather_breaker
from app.services.errors import ServiceNotConfiguredError
from app.services.http_client import get_http_client, retry_on_network

KARNATAKA_DISTRICTS = {
    "bagalkote": {"lat": 16.18, "lon": 75.70},
    "ballari": {"lat": 15.14, "lon": 76.92},
    "belagavi": {"lat": 15.85, "lon": 74.50},
    "bengaluru rural": {"lat": 13.22, "lon": 77.56},
    "bengaluru urban": {"lat": 12.97, "lon": 77.59},
    "bidar": {"lat": 17.91, "lon": 77.52},
    "chamarajanagara": {"lat": 11.93, "lon": 76.94},
    "chikballapura": {"lat": 13.44, "lon": 77.73},
    "chikkamagaluru": {"lat": 13.32, "lon": 75.78},
    "chitradurga": {"lat": 14.23, "lon": 76.40},
    "dakshina kannada": {"lat": 12.87, "lon": 74.88},
    "davanagere": {"lat": 14.47, "lon": 75.92},
    "dharwad": {"lat": 15.46, "lon": 75.01},
    "gadag": {"lat": 15.43, "lon": 75.63},
    "hassan": {"lat": 13.01, "lon": 76.10},
    "haveri": {"lat": 14.79, "lon": 75.40},
    "kalaburagi": {"lat": 17.33, "lon": 76.83},
    "kodagu": {"lat": 12.42, "lon": 75.74},
    "kolar": {"lat": 13.14, "lon": 78.13},
    "koppal": {"lat": 15.35, "lon": 76.15},
    "mandya": {"lat": 12.52, "lon": 76.90},
    "mysuru": {"lat": 12.30, "lon": 76.66},
    "raichur": {"lat": 16.21, "lon": 77.37},
    "ramanagara": {"lat": 12.72, "lon": 77.28},
    "shivamogga": {"lat": 13.93, "lon": 75.57},
    "tumakuru": {"lat": 13.34, "lon": 77.10},
    "udupi": {"lat": 13.34, "lon": 74.75},
    "uttara kannada": {"lat": 14.80, "lon": 74.13},
    "vijayapura": {"lat": 16.83, "lon": 75.71},
    "vijayanagara": {"lat": 15.27, "lon": 76.39},
    "yadgir": {"lat": 16.77, "lon": 77.14},
}


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


@weather_breaker
@retry_on_network
async def get_forecast(district: str, days: int = 5) -> list[WeatherForecast]:
    """Return weather forecast for a Karnataka district."""
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
