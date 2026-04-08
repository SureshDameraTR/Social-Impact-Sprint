"""Mock IMD weather service for Karnataka districts."""

import random
from datetime import date, datetime, timedelta, timezone

from app.schemas.weather import WeatherAlertRead, WeatherForecast

# Karnataka April weather profiles by district
DISTRICT_PROFILES = {
    "mysore": {
        "temp_min_range": (22, 26),
        "temp_max_range": (33, 38),
        "humidity_range": (35, 65),
        "rainfall_chance": 0.2,
        "rainfall_range": (0, 15),
        "wind_range": (8, 18),
        "conditions": ["Partly Cloudy", "Hot & Humid", "Clear", "Pre-monsoon Showers", "Hazy"],
    },
    "mandya": {
        "temp_min_range": (21, 25),
        "temp_max_range": (34, 38),
        "humidity_range": (30, 60),
        "rainfall_chance": 0.15,
        "rainfall_range": (0, 12),
        "wind_range": (6, 15),
        "conditions": ["Clear", "Hot & Dry", "Partly Cloudy", "Hazy", "Pre-monsoon Showers"],
    },
}

# Default profile for unknown districts
DEFAULT_PROFILE = {
    "temp_min_range": (23, 27),
    "temp_max_range": (32, 37),
    "humidity_range": (40, 65),
    "rainfall_chance": 0.2,
    "rainfall_range": (0, 10),
    "wind_range": (8, 16),
    "conditions": ["Partly Cloudy", "Clear", "Hot & Humid"],
}

MOCK_ALERTS = {
    "mysore": [
        {
            "id": "a1b2c3d4-0001-4000-a000-000000000001",
            "district": "Mysore",
            "alert_type": "heat_stress",
            "severity": "moderate",
            "description": "Temperature expected to reach 37-38°C. Ensure livestock have shade and adequate water. Avoid transport during peak hours (11 AM - 3 PM).",
            "valid_from": datetime.now(timezone.utc).isoformat(),
            "valid_to": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "source": "IMD",
        },
    ],
    "mandya": [
        {
            "id": "a1b2c3d4-0002-4000-a000-000000000001",
            "district": "Mandya",
            "alert_type": "heavy_rain",
            "severity": "low",
            "description": "Isolated pre-monsoon showers expected. Ensure livestock shelters have drainage. Store dry fodder indoors.",
            "valid_from": datetime.now(timezone.utc).isoformat(),
            "valid_to": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "source": "IMD",
        },
    ],
}


def _calculate_heat_stress_index(temp_max: float, humidity: float) -> float:
    """Simplified heat stress index (Temperature-Humidity Index).

    THI = 0.8 * T + (RH/100) * (T - 14.4) + 46.4
    Normal < 72, Mild stress 72-78, Moderate 78-88, Severe > 88
    """
    thi = 0.8 * temp_max + (humidity / 100) * (temp_max - 14.4) + 46.4
    return round(thi, 1)


def get_forecast(district: str, days: int = 5) -> list[WeatherForecast]:
    """Return mock 5-day forecast for a Karnataka district."""
    district_key = district.lower().strip()
    profile = DISTRICT_PROFILES.get(district_key, DEFAULT_PROFILE)

    random.seed(hash(district_key + str(date.today())))
    forecasts = []

    for i in range(days):
        forecast_date = date.today() + timedelta(days=i)
        temp_min = round(random.uniform(*profile["temp_min_range"]), 1)
        temp_max = round(random.uniform(*profile["temp_max_range"]), 1)
        humidity = round(random.uniform(*profile["humidity_range"]), 1)
        has_rain = random.random() < profile["rainfall_chance"]
        rainfall = round(random.uniform(*profile["rainfall_range"]), 1) if has_rain else 0.0
        wind_speed = round(random.uniform(*profile["wind_range"]), 1)
        condition = random.choice(profile["conditions"])
        hsi = _calculate_heat_stress_index(temp_max, humidity)

        forecasts.append(
            WeatherForecast(
                date=forecast_date,
                district=district.title(),
                temp_min=temp_min,
                temp_max=temp_max,
                humidity=humidity,
                rainfall_mm=rainfall,
                wind_speed=wind_speed,
                condition=condition,
                heat_stress_index=hsi,
            )
        )

    return forecasts


def get_alerts(district: str) -> list[dict]:
    """Return active weather alerts for a district."""
    district_key = district.lower().strip()
    return MOCK_ALERTS.get(district_key, [])
