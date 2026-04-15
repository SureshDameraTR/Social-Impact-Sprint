"""Weather mock service.

Generates realistic weather data for Karnataka districts using seasonal
patterns and deterministic seeding for consistency.
"""

import base64
import hashlib
import io
import json
import math
import struct
import uuid
import wave
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/weather", tags=["Weather"])

# Load district metadata
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
with open(_DATA_DIR / "karnataka_districts.json") as f:
    DISTRICTS: dict[str, dict] = json.load(f)

# Weather conditions ordered by severity
CONDITIONS = [
    "Clear Sky",
    "Partly Cloudy",
    "Cloudy",
    "Light Rain",
    "Moderate Rain",
    "Heavy Rain",
    "Thunderstorm",
]


def _deterministic_seed(district: str, d: date) -> float:
    """Return a deterministic pseudo-random float in [0, 1) from district+date."""
    raw = f"{district.lower().strip()}:{d.isoformat()}"
    h = hashlib.sha256(raw.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _deterministic_random(seed_float: float, salt: int) -> float:
    """Derive additional pseudo-random values from a seed using a salt."""
    combined = seed_float * 1000000 + salt
    h = hashlib.md5(str(combined).encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _get_season(month: int) -> str:
    """Return the meteorological season for Karnataka."""
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "summer"
    elif month in (6, 7, 8, 9):
        return "monsoon"
    else:
        return "post_monsoon"


def _elevation_factor(elevation: float) -> float:
    """Temperature drops ~0.65C per 100m above sea level. Normalize around 600m."""
    return (elevation - 600) * 0.0065


def _compute_thi(temp: float, humidity: float) -> float:
    """Temperature-Humidity Index (heat stress index).

    THI = 0.8 * T + (RH/100) * (T - 14.4) + 46.4
    """
    return round(0.8 * temp + (humidity / 100.0) * (temp - 14.4) + 46.4, 1)


def _generate_forecast(district: str, target_date: date) -> dict:
    """Generate a single day forecast for a district."""
    district_key = district.lower().strip()
    meta = DISTRICTS.get(district_key)
    if meta is None:
        # Unknown district: use defaults
        elevation = 600.0
    else:
        elevation = meta["elevation"]

    seed = _deterministic_seed(district_key, target_date)
    month = target_date.month
    season = _get_season(month)
    elev_adj = _elevation_factor(elevation)

    # Base temperature ranges by season (Celsius, at ~600m elevation)
    season_params = {
        "winter": {"t_min_base": 12.0, "t_max_base": 28.0, "rh_base": 45.0, "rain_base": 0.0},
        "summer": {"t_min_base": 22.0, "t_max_base": 38.0, "rh_base": 30.0, "rain_base": 0.0},
        "monsoon": {"t_min_base": 20.0, "t_max_base": 30.0, "rh_base": 80.0, "rain_base": 15.0},
        "post_monsoon": {"t_min_base": 18.0, "t_max_base": 31.0, "rh_base": 60.0, "rain_base": 3.0},
    }
    params = season_params[season]

    # Add sinusoidal variation within the season using day-of-year
    doy = target_date.timetuple().tm_yday
    seasonal_wave = math.sin(2 * math.pi * doy / 365.0)

    r1 = _deterministic_random(seed, 1)
    r2 = _deterministic_random(seed, 2)
    r3 = _deterministic_random(seed, 3)
    r4 = _deterministic_random(seed, 4)
    r5 = _deterministic_random(seed, 5)

    # Temperature with elevation adjustment and daily variation
    temp_min = round(params["t_min_base"] - elev_adj + (r1 - 0.5) * 4 + seasonal_wave * 2, 1)
    temp_max = round(params["t_max_base"] - elev_adj + (r2 - 0.5) * 6 + seasonal_wave * 3, 1)
    # Ensure min < max with at least 5C spread
    if temp_max - temp_min < 5:
        temp_max = temp_min + 5 + r2 * 3

    temp_max = round(temp_max, 1)

    # Humidity
    humidity = round(params["rh_base"] + (r3 - 0.5) * 20, 1)
    humidity = max(15.0, min(98.0, humidity))

    # Rainfall
    if season == "monsoon":
        # Monsoon: 0-40mm with higher probability of rain
        if r4 > 0.2:
            rainfall = round(r4 * 40.0, 1)
        else:
            rainfall = 0.0
    elif season == "summer":
        # Summer: mostly dry, occasional pre-monsoon showers
        if r4 > 0.85:
            rainfall = round((r4 - 0.85) * 50.0, 1)
        else:
            rainfall = 0.0
    elif season == "post_monsoon":
        # Post-monsoon: retreating monsoon, some rain
        if r4 > 0.5:
            rainfall = round(r4 * 20.0, 1)
        else:
            rainfall = 0.0
    else:
        # Winter: very rare rain
        if r4 > 0.92:
            rainfall = round((r4 - 0.92) * 15.0, 1)
        else:
            rainfall = 0.0

    # Wind speed (km/h)
    wind_base = {"winter": 8, "summer": 12, "monsoon": 15, "post_monsoon": 10}
    wind_speed = round(wind_base[season] + (r5 - 0.5) * 10, 1)
    wind_speed = max(2.0, wind_speed)

    # Condition based on rainfall and humidity
    if rainfall > 25:
        condition = "Thunderstorm" if r5 > 0.5 else "Heavy Rain"
    elif rainfall > 10:
        condition = "Heavy Rain" if r5 > 0.7 else "Moderate Rain"
    elif rainfall > 2:
        condition = "Moderate Rain" if r5 > 0.6 else "Light Rain"
    elif rainfall > 0:
        condition = "Light Rain"
    elif humidity > 70:
        condition = "Cloudy" if r3 > 0.5 else "Partly Cloudy"
    elif humidity > 50:
        condition = "Partly Cloudy" if r3 > 0.4 else "Clear Sky"
    else:
        condition = "Clear Sky"

    # Heat stress index using the average of min and max
    avg_temp = (temp_min + temp_max) / 2.0
    heat_stress_index = _compute_thi(avg_temp, humidity)

    return {
        "date": target_date.isoformat(),
        "district": district_key,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "humidity": humidity,
        "rainfall_mm": rainfall,
        "wind_speed": wind_speed,
        "condition": condition,
        "heat_stress_index": heat_stress_index,
    }


@router.get("/forecast")
async def get_forecast(
    district: str = Query(..., description="Karnataka district name"),
    days: int = Query(5, ge=1, le=15, description="Number of forecast days"),
):
    """Return weather forecasts for a Karnataka district."""
    today = date.today()
    forecasts = [_generate_forecast(district, today + timedelta(days=i)) for i in range(days)]
    return forecasts


@router.get("/alerts")
async def get_alerts(
    district: str = Query(..., description="Karnataka district name"),
):
    """Return active weather alerts based on current season."""
    today = date.today()
    season = _get_season(today.month)
    district_key = district.lower().strip()
    now = datetime.now(timezone.utc)
    alerts = []

    if season == "summer":
        # Heat wave alerts for summer months
        seed = _deterministic_seed(district_key, today)
        if seed > 0.4:
            severity = "extreme" if seed > 0.8 else "severe" if seed > 0.6 else "moderate"
            alerts.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"heat-{district_key}-{today}")),
                "district": district_key,
                "alert_type": "heat_wave",
                "severity": severity,
                "description": (
                    f"Heat wave warning for {district_key}. Maximum temperatures expected "
                    f"to exceed 40\u00b0C. Ensure livestock have access to shade and water."
                ),
                "valid_from": now.isoformat(),
                "valid_to": (now + timedelta(hours=48)).isoformat(),
                "source": "IMD",
                "created_at": now.isoformat(),
            })

    elif season == "monsoon":
        # Flood risk and heavy rain alerts
        seed = _deterministic_seed(district_key, today)
        if seed > 0.3:
            severity = "extreme" if seed > 0.85 else "severe" if seed > 0.6 else "moderate"
            alerts.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"flood-{district_key}-{today}")),
                "district": district_key,
                "alert_type": "flood_risk",
                "severity": severity,
                "description": (
                    f"Heavy rainfall warning for {district_key}. Risk of flooding "
                    f"in low-lying areas. Move livestock to higher ground."
                ),
                "valid_from": now.isoformat(),
                "valid_to": (now + timedelta(hours=72)).isoformat(),
                "source": "IMD",
                "created_at": now.isoformat(),
            })
        if seed > 0.5:
            alerts.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"rain-{district_key}-{today}")),
                "district": district_key,
                "alert_type": "heavy_rainfall",
                "severity": "moderate",
                "description": (
                    f"Heavy to very heavy rainfall expected in {district_key}. "
                    f"Livestock shelters should be reinforced."
                ),
                "valid_from": now.isoformat(),
                "valid_to": (now + timedelta(hours=24)).isoformat(),
                "source": "IMD",
                "created_at": now.isoformat(),
            })

    elif season == "winter":
        # Cold wave alerts
        seed = _deterministic_seed(district_key, today)
        if seed > 0.6:
            severity = "severe" if seed > 0.8 else "moderate"
            alerts.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cold-{district_key}-{today}")),
                "district": district_key,
                "alert_type": "cold_wave",
                "severity": severity,
                "description": (
                    f"Cold wave conditions in {district_key}. Minimum temperatures "
                    f"may drop below 10\u00b0C. Provide warm bedding for livestock."
                ),
                "valid_from": now.isoformat(),
                "valid_to": (now + timedelta(hours=36)).isoformat(),
                "source": "IMD",
                "created_at": now.isoformat(),
            })

    else:
        # Post-monsoon: occasional cyclone or heavy rain warnings
        seed = _deterministic_seed(district_key, today)
        if seed > 0.7:
            alerts.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cyclone-{district_key}-{today}")),
                "district": district_key,
                "alert_type": "cyclone_warning",
                "severity": "moderate",
                "description": (
                    f"Cyclonic activity may affect {district_key}. "
                    f"Secure livestock shelters and stock emergency fodder."
                ),
                "valid_from": now.isoformat(),
                "valid_to": (now + timedelta(hours=48)).isoformat(),
                "source": "IMD",
                "created_at": now.isoformat(),
            })

    return alerts


class TTSRequest(BaseModel):
    district: str
    language_code: str = "kn-IN"


def _generate_silent_wav(duration_ms: int = 200, sample_rate: int = 8000) -> bytes:
    """Generate a tiny valid WAV file containing silence."""
    num_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # Write silence (zero samples)
        wf.writeframes(struct.pack(f"<{num_samples}h", *([0] * num_samples)))
    return buf.getvalue()


@router.post("/tts")
async def weather_tts(req: TTSRequest):
    """Return a mock TTS audio response for weather information.

    Generates a tiny valid WAV file (silence) encoded as base64 to mimic
    a real TTS service like Sarvam AI.
    """
    wav_bytes = _generate_silent_wav()
    audio_b64 = base64.b64encode(wav_bytes).decode("ascii")
    request_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tts-{req.district}-{req.language_code}"))
    return {
        "audio": audio_b64,
        "request_id": request_id,
    }
