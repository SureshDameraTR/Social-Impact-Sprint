"""Weather forecast and alert endpoints."""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.weather_service import (
    get_alerts,
    get_forecast,
    get_tts,
)

router = APIRouter(prefix="/v1/weather", tags=["Weather"])

# Condition → emoji mapping for mobile UI
_CONDITION_EMOJI = {
    "sunny": "\u2600\uFE0F",
    "clear": "\u2600\uFE0F",
    "clear sky": "\u2600\uFE0F",
    "partly cloudy": "\u26C5",
    "cloudy": "\u2601\uFE0F",
    "overcast": "\u2601\uFE0F",
    "light rain": "\U0001F326\uFE0F",
    "moderate rain": "\U0001F327\uFE0F",
    "rain": "\U0001F327\uFE0F",
    "heavy rain": "\U0001F327\uFE0F",
    "thunderstorm": "\u26C8\uFE0F",
    "hot": "\U0001F321\uFE0F",
}

_DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@router.get("")
async def get_weather_summary(
    current_user: User = Depends(get_current_user),
):
    """Get combined current + forecast weather for the user's district.

    Returns the shape expected by the mobile app:
    {current: {temp, humidity, rainfall, wind, condition, emoji, location},
     forecast: [{day, temp, emoji, rain}, ...]}
    """
    district = getattr(current_user, "location_district", None) or "dharwad"
    try:
        forecasts = await get_forecast(district, 5)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        ) from exc

    if not forecasts:
        raise HTTPException(status_code=404, detail="No forecast data available")

    # First day's forecast becomes "current" conditions
    today = forecasts[0]
    condition_lower = today.condition.lower()
    emoji = _CONDITION_EMOJI.get(condition_lower, "\U0001F324\uFE0F")

    current = {
        "temp": round((today.temp_min + today.temp_max) / 2, 1),
        "humidity": round(today.humidity),
        "rainfall": round(today.rainfall_mm, 1),
        "wind": round(today.wind_speed, 1),
        "condition": today.condition,
        "emoji": emoji,
        "location": district.title(),
    }

    forecast = []
    for f in forecasts[1:]:
        day_name = _DAY_NAMES[f.date.weekday()]
        f_emoji = _CONDITION_EMOJI.get(f.condition.lower(), "\U0001F324\uFE0F")
        forecast.append({
            "day": day_name,
            "temp": round((f.temp_min + f.temp_max) / 2, 1),
            "emoji": f_emoji,
            "rain": round(f.rainfall_mm, 1),
        })

    return {"current": current, "forecast": forecast}


@router.get("/forecast/{district}")
async def get_weather_forecast(
    district: str,
    days: int = Query(5, ge=1, le=14, description="Number of forecast days"),
    current_user: User = Depends(get_current_user),
):
    """Get weather forecast for a district."""
    try:
        forecasts = await get_forecast(district, days)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        ) from exc
    return {
        "district": district.title(),
        "days": days,
        "forecasts": [f.model_dump() for f in forecasts],
        "source": "IMD",
    }


@router.get("/alerts/{district}")
async def get_weather_alerts(district: str, current_user: User = Depends(get_current_user)):
    """Get active weather alerts for a district."""
    try:
        alerts = await get_alerts(district)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        ) from exc
    return {
        "district": district.title(),
        "active_alerts": alerts,
        "count": len(alerts),
    }


@router.get("/tts/{district}")
async def get_weather_tts(
    district: str, lang: str = Query("kn"), current_user: User = Depends(get_current_user)
):
    """Get text-to-speech weather summary for a district."""
    try:
        result = await get_tts(district, lang)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        ) from exc
    return result
