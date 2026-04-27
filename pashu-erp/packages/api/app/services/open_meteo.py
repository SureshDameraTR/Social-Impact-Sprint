"""Open-Meteo weather service for livestock heat-stress and forecast data.

Free API, no key required. Docs: https://open-meteo.com/en/docs
Replaces the mock weather backend for production use.
"""

import logging

from cachetools import TTLCache
from httpx import AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

DAILY_VARS = (
    "temperature_2m_max,temperature_2m_min,"
    "precipitation_sum,windspeed_10m_max,"
    "relative_humidity_2m_max,relative_humidity_2m_min,"
    "soil_temperature_0_to_7cm_mean,soil_moisture_0_to_7cm_mean,"
    "et0_fao_evapotranspiration"
)


class OpenMeteoService:
    """Async client for the Open-Meteo forecast API with TTL caching."""

    def __init__(
        self,
        http_client: AsyncClient | None = None,
        base_url: str = "https://api.open-meteo.com",
        cache_ttl: int = 10800,
    ):
        self._client = http_client
        self._base_url = base_url
        self._cache: TTLCache = TTLCache(maxsize=200, ttl=cache_ttl)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> dict:
        """Fetch daily forecast from Open-Meteo.

        Results are cached by (lat, lon, days) rounded to 2 decimal places.
        """
        cache_key = f"forecast:{latitude:.2f}:{longitude:.2f}:{days}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        url = f"{self._base_url}/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": DAILY_VARS,
            "timezone": "Asia/Kolkata",
            "forecast_days": days,
        }

        resp = await self._client.get(url, params=params, timeout=15.0)
        resp.raise_for_status()
        data = resp.json()

        self._cache[cache_key] = data
        return data

    async def get_forecast_for_district(
        self,
        district_name: str,
        days: int = 7,
        db_session=None,
    ) -> dict | None:
        """Look up district coordinates in DB, then fetch forecast.

        Returns None if db_session is not provided or district not found.
        """
        if db_session is None:
            return None

        from sqlalchemy import select

        from app.models.location import District

        result = await db_session.execute(
            select(District).where(District.name.ilike(district_name))
        )
        district = result.scalars().first()
        if not district or not district.latitude:
            return None

        return await self.get_forecast(district.latitude, district.longitude, days)
