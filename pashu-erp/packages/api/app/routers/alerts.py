"""Community disease alert endpoints."""

import math
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.alerts import CommunityAlert
from app.models.user import User
from app.schemas.alerts import CommunityAlertCreate, CommunityAlertRead

router = APIRouter(prefix="/v1/alerts", tags=["Community Alerts"])


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.post("/report", response_model=CommunityAlertRead, status_code=status.HTTP_201_CREATED)
async def report_disease_alert(
    body: CommunityAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Report a disease outbreak in the community."""
    alert = CommunityAlert(
        reported_by=str(current_user.id),
        disease_name=body.disease_name,
        lat=body.lat,
        lon=body.lon,
        radius_km=body.radius_km,
        severity=body.severity.value,
        verified=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.get("/nearby", response_model=list[CommunityAlertRead])
async def get_nearby_alerts(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(10.0, gt=0, le=100, description="Search radius in km"),
    db: AsyncSession = Depends(get_db),
):
    """Get disease alerts near a location."""
    now = datetime.now(timezone.utc)

    # Fetch all non-expired alerts, then filter by distance
    result = await db.execute(
        select(CommunityAlert).where(
            CommunityAlert.expires_at > now,
        )
    )
    all_alerts = result.scalars().all()

    nearby = []
    for alert in all_alerts:
        distance = _haversine_km(lat, lon, alert.lat, alert.lon)
        if distance <= radius:
            nearby.append(alert)

    # Sort by created_at descending
    nearby.sort(key=lambda a: a.created_at, reverse=True)
    return nearby


@router.patch("/{alert_id}/verify", response_model=CommunityAlertRead)
async def verify_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin: verify a community disease alert."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can verify alerts")

    result = await db.execute(
        select(CommunityAlert).where(CommunityAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.verified = True
    await db.commit()
    await db.refresh(alert)
    return alert
