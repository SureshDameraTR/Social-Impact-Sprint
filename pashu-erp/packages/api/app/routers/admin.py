"""Admin dashboard endpoints (admin-only)."""

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db

# Admin dashboard configuration (previously in constants.py)
RISK_SCORE_THRESHOLD: float = 0.5
ALERT_WINDOW_DAYS: int = 7
ACTIVE_SELLER_WINDOW_DAYS: int = 30
from app.middleware.auth import require_admin
from app.models.animal import Animal
from app.models.finance import Transaction
from app.models.health import HealthEvent
from app.models.marketplace import SellRecord
from app.models.milk import YieldLog
from app.models.shg import SHGGroup
from app.models.user import User

router = APIRouter(prefix="/v1/admin", tags=["Admin"])


@router.get("/stats")
async def dashboard_stats(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard stats: counts, milk, alerts, revenue, sellers."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = datetime.now(timezone.utc) - timedelta(days=ALERT_WINDOW_DAYS)
    month_ago = datetime.now(timezone.utc) - timedelta(days=ACTIVE_SELLER_WINDOW_DAYS)
    women_farmer_subq = select(User.id).where(
        User.role == "farmer", User.gender == "female", User.deleted_at.is_(None)
    )

    # Fire all 10 queries in parallel using asyncio.gather
    (
        farmer_count_result,
        animal_count_result,
        milk_result,
        alert_result,
        revenue_result,
        sellers_result,
        women_farmers_result,
        women_tx_result,
        women_sell_result,
        women_animals_result,
        shg_count_result,
    ) = await asyncio.gather(
        db.execute(
            select(func.count()).select_from(User)
            .where(User.role == "farmer", User.deleted_at.is_(None))
        ),
        db.execute(
            select(func.count()).select_from(Animal).where(Animal.deleted_at.is_(None))
        ),
        db.execute(
            select(func.coalesce(func.sum(YieldLog.quantity_liters), 0.0))
            .where(YieldLog.recorded_at >= today_start, YieldLog.deleted_at.is_(None))
        ),
        db.execute(
            select(func.count()).select_from(HealthEvent).where(
                HealthEvent.event_date >= week_ago,
                HealthEvent.ai_risk_score > RISK_SCORE_THRESHOLD,
                HealthEvent.deleted_at.is_(None),
            )
        ),
        db.execute(
            select(func.coalesce(func.sum(SellRecord.total_amount), 0))
            .where(SellRecord.deleted_at.is_(None))
        ),
        db.execute(
            select(func.count(func.distinct(SellRecord.user_id)))
            .where(SellRecord.sold_at >= month_ago, SellRecord.deleted_at.is_(None))
        ),
        db.execute(
            select(func.count()).select_from(User).where(
                User.role == "farmer", User.gender == "female", User.deleted_at.is_(None)
            )
        ),
        db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(Transaction.user_id.in_(women_farmer_subq), Transaction.deleted_at.is_(None))
        ),
        db.execute(
            select(func.coalesce(func.sum(SellRecord.total_amount), 0))
            .where(SellRecord.user_id.in_(women_farmer_subq), SellRecord.deleted_at.is_(None))
        ),
        db.execute(
            select(func.count()).select_from(Animal).where(
                Animal.user_id.in_(women_farmer_subq), Animal.deleted_at.is_(None),
            )
        ),
        db.execute(
            select(func.count()).select_from(SHGGroup).where(SHGGroup.deleted_at.is_(None))
        ),
    )

    farmer_count = farmer_count_result.scalar() or 0
    animal_count = animal_count_result.scalar() or 0
    todays_milk = float(milk_result.scalar() or 0)
    active_alerts = alert_result.scalar() or 0
    marketplace_revenue = float(revenue_result.scalar() or 0)
    active_sellers = sellers_result.scalar() or 0
    women_farmers = women_farmers_result.scalar() or 0
    women_tx_revenue = float(women_tx_result.scalar() or 0)
    women_sell_revenue = float(women_sell_result.scalar() or 0)
    women_revenue = women_tx_revenue + women_sell_revenue
    women_animals = women_animals_result.scalar() or 0
    women_shg_count = shg_count_result.scalar() or 0

    return {
        "farmer_count": farmer_count,
        "animal_count": animal_count,
        "todays_milk_liters": round(todays_milk, 2),
        "active_alerts": active_alerts,
        "marketplace_revenue": round(marketplace_revenue, 2),
        "active_sellers": active_sellers,
        "women_farmers": women_farmers,
        "women_revenue": round(women_revenue, 2),
        "women_animals": women_animals,
        "women_shg_count": women_shg_count,
    }


@router.get("/charts/milk")
async def milk_chart_data(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """30-day milk collection chart data."""
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Single GROUP BY query instead of 30 individual queries
    result = await db.execute(
        select(
            cast(YieldLog.recorded_at, Date).label("day"),
            func.coalesce(func.sum(YieldLog.quantity_liters), 0.0).label("total"),
        )
        .where(YieldLog.recorded_at >= start_date, YieldLog.deleted_at.is_(None))
        .group_by(cast(YieldLog.recorded_at, Date))
    )
    rows = {row.day: float(row.total) for row in result.all()}

    # Fill missing days in Python
    days = []
    for i in range(30):
        day = (now - timedelta(days=29 - i)).date()
        days.append({
            "date": day.isoformat(),
            "liters": round(rows.get(day, 0.0), 2),
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
    week_ago = datetime.now(timezone.utc) - timedelta(days=ALERT_WINDOW_DAYS)

    # Eager-load Animal (and Animal.owner) in a single query to avoid N+1
    result = await db.execute(
        select(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > RISK_SCORE_THRESHOLD,
            HealthEvent.deleted_at.is_(None),
        )
        .options(
            selectinload(HealthEvent.animal).selectinload(Animal.owner),
        )
        .order_by(HealthEvent.ai_risk_score.desc())
        .limit(100)
    )
    events = result.scalars().all()

    markers = []
    for event in events:
        animal = event.animal
        if animal is None:
            continue
        owner = animal.owner

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
