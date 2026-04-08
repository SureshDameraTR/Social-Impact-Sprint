"""Weather forecast and alert endpoints."""

from fastapi import APIRouter, Query

from app.services.weather_service import get_alerts, get_forecast

router = APIRouter(prefix="/v1/weather", tags=["Weather"])


@router.get("/forecast/{district}")
async def get_weather_forecast(
    district: str,
    days: int = Query(5, ge=1, le=14, description="Number of forecast days"),
):
    """Get weather forecast for a Karnataka district (mock IMD data)."""
    forecasts = get_forecast(district, days)
    return {
        "district": district.title(),
        "days": days,
        "forecasts": [f.model_dump() for f in forecasts],
        "source": "IMD (mock)",
    }


@router.get("/alerts/{district}")
async def get_weather_alerts(district: str):
    """Get active weather alerts for a district."""
    alerts = get_alerts(district)
    return {
        "district": district.title(),
        "active_alerts": alerts,
        "count": len(alerts),
    }
