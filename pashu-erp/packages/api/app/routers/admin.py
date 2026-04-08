"""Admin dashboard endpoints (admin-only)."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.animal import Animal
from app.models.health import HealthEvent
from app.models.marketplace import SellRecord
from app.models.milk import YieldLog
from app.models.user import User

router = APIRouter(prefix="/v1/admin", tags=["Admin"])


@router.get("/stats")
async def dashboard_stats(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard stats: farmer count, animal count, today's milk, active alerts, marketplace revenue, active sellers."""
    # Farmer count
    farmer_count_result = await db.execute(
        select(func.count()).select_from(User).where(User.role == "farmer")
    )
    farmer_count = farmer_count_result.scalar() or 0

    # Animal count
    animal_count_result = await db.execute(
        select(func.count()).select_from(Animal)
    )
    animal_count = animal_count_result.scalar() or 0

    # Today's milk
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    milk_result = await db.execute(
        select(func.coalesce(func.sum(YieldLog.quantity_liters), 0.0))
        .where(YieldLog.recorded_at >= today_start)
    )
    todays_milk = float(milk_result.scalar() or 0)

    # Active health alerts (events in last 7 days with risk > 0.5)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    alert_result = await db.execute(
        select(func.count())
        .select_from(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > 0.5,
        )
    )
    active_alerts = alert_result.scalar() or 0

    # Marketplace revenue (all time)
    revenue_result = await db.execute(
        select(func.coalesce(func.sum(SellRecord.total_amount), 0))
    )
    marketplace_revenue = float(revenue_result.scalar() or 0)

    # Active sellers (users with at least one sell record in last 30 days)
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    sellers_result = await db.execute(
        select(func.count(func.distinct(SellRecord.user_id)))
        .where(SellRecord.sold_at >= month_ago)
    )
    active_sellers = sellers_result.scalar() or 0

    return {
        "farmer_count": farmer_count,
        "animal_count": animal_count,
        "todays_milk_liters": round(todays_milk, 2),
        "active_alerts": active_alerts,
        "marketplace_revenue": round(marketplace_revenue, 2),
        "active_sellers": active_sellers,
    }


@router.get("/charts/milk")
async def milk_chart_data(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """30-day milk collection chart data."""
    now = datetime.now(timezone.utc)
    days = []

    for i in range(30):
        day = now - timedelta(days=29 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        result = await db.execute(
            select(func.coalesce(func.sum(YieldLog.quantity_liters), 0.0))
            .where(YieldLog.recorded_at >= day_start, YieldLog.recorded_at < day_end)
        )
        total = float(result.scalar() or 0)
        days.append({
            "date": day_start.date().isoformat(),
            "liters": round(total, 2),
        })

    return {"period": "30_days", "data": days}


@router.get("/gis/alerts")
async def gis_alert_markers(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """GIS data for disease alert map markers.

    Returns recent high-risk health events with location info for map plotting.
    """
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    result = await db.execute(
        select(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > 0.5,
        )
        .order_by(HealthEvent.ai_risk_score.desc())
        .limit(100)
    )
    events = result.scalars().all()

    markers = []
    for event in events:
        # Get animal to find owner's location
        animal_result = await db.execute(
            select(Animal).where(Animal.id == event.animal_id)
        )
        animal = animal_result.scalar_one_or_none()
        if animal is None:
            continue

        owner_result = await db.execute(
            select(User).where(User.id == animal.user_id)
        )
        owner = owner_result.scalar_one_or_none()

        markers.append({
            "event_id": str(event.id),
            "animal_id": str(event.animal_id),
            "species": animal.species if animal else None,
            "risk_score": event.ai_risk_score,
            "probable_diseases": event.probable_diseases,
            "district": owner.location_district if owner else None,
            "village_code": owner.village_code if owner else None,
            "event_date": event.event_date.isoformat(),
        })

    return {"alert_count": len(markers), "markers": markers}
