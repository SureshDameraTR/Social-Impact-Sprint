"""Weather forecast and alert endpoints."""

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.services.weather_service import (
    get_alerts,
    get_forecast,
    get_tts,
)

router = APIRouter(prefix="/v1/weather", tags=["Weather"])


@router.get("/forecast/{district}")
async def get_weather_forecast(
    district: str,
    days: int = Query(5, ge=1, le=14, description="Number of forecast days"),
):
    """Get weather forecast for a district."""
    try:
        forecasts = await get_forecast(district, days)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        )
    return {
        "district": district.title(),
        "days": days,
        "forecasts": [f.model_dump() for f in forecasts],
        "source": "IMD",
    }


@router.get("/alerts/{district}")
async def get_weather_alerts(district: str):
    """Get active weather alerts for a district."""
    try:
        alerts = await get_alerts(district)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        )
    return {
        "district": district.title(),
        "active_alerts": alerts,
        "count": len(alerts),
    }


@router.get("/tts/{district}")
async def get_weather_tts(district: str, lang: str = Query("kn")):
    """Get text-to-speech weather summary for a district."""
    try:
        result = await get_tts(district, lang)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Weather API error: {exc.response.text}",
        )
    return result
