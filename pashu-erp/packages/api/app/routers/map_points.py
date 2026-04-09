"""Map data endpoints for GIS visualization."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db

# Admin dashboard configuration (previously in constants.py)
RISK_SCORE_THRESHOLD: float = 0.5
ALERT_WINDOW_DAYS: int = 7
from app.middleware.auth import get_current_user
from app.models.alerts import CommunityAlert
from app.models.animal import Animal
from app.models.health import HealthEvent
from app.models.milk import MilkCollectionCenter
from app.models.user import User

router = APIRouter(prefix="/v1/map", tags=["Map"])


@router.get("/points")
async def get_map_points(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Combined map data: health alerts, milk centers, community alerts, farmer locations."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=ALERT_WINDOW_DAYS)
    points = []

    # 1. High-risk health events (via animal owner location)
    health_result = await db.execute(
        select(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > RISK_SCORE_THRESHOLD,
        )
        .options(
            selectinload(HealthEvent.animal).selectinload(Animal.owner),
        )
        .limit(100)
    )
    for event in health_result.scalars().all():
        animal = event.animal
        if animal is None:
            continue
        owner = animal.owner
        if owner and owner.village_code:
            points.append({
                "type": "health_alert",
                "id": str(event.id),
                "label": f"Risk: {event.ai_risk_score:.0%}",
                "district": owner.location_district,
                "village_code": owner.village_code,
                "risk_score": event.ai_risk_score,
                "species": animal.species,
                "date": event.event_date.isoformat(),
            })

    # 2. Milk collection centers
    center_result = await db.execute(
        select(MilkCollectionCenter).where(MilkCollectionCenter.is_active == True)  # noqa: E712
    )
    for center in center_result.scalars().all():
        points.append({
            "type": "milk_center",
            "id": str(center.id),
            "label": center.name,
            "district": center.district,
            "village_code": center.village_code,
        })

    # 3. Active community alerts (with lat/lon)
    alert_result = await db.execute(
        select(CommunityAlert).where(CommunityAlert.expires_at > func.now())
    )
    for alert in alert_result.scalars().all():
        points.append({
            "type": "community_alert",
            "id": str(alert.id),
            "label": alert.disease_name,
            "lat": alert.lat,
            "lon": alert.lon,
            "radius_km": alert.radius_km,
            "severity": alert.severity,
            "verified": alert.verified,
        })

    # 4. Farmers with village codes (aggregated count per village)
    farmer_result = await db.execute(
        select(
            User.village_code,
            User.location_district,
            func.count().label("farmer_count"),
        )
        .where(User.role == "farmer", User.village_code.isnot(None))
        .group_by(User.village_code, User.location_district)
    )
    for row in farmer_result.all():
        points.append({
            "type": "farmer_cluster",
            "village_code": row.village_code,
            "district": row.location_district,
            "farmer_count": row.farmer_count,
        })

    return {"total": len(points), "points": points}
