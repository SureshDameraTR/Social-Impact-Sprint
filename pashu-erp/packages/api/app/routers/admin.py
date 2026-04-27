"""Admin dashboard endpoints (admin-only)."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import invalidate_user_cache, require_admin
from app.models.animal import Animal
from app.models.finance import Transaction
from app.models.health import HealthEvent
from app.models.marketplace import SellRecord
from app.models.milk import YieldLog
from app.models.shg import SHGGroup
from app.models.user import User
from app.schemas.users import UserRoleUpdate

# Admin dashboard configuration
RISK_SCORE_THRESHOLD: float = 0.5
ALERT_WINDOW_DAYS: int = 7
ACTIVE_SELLER_WINDOW_DAYS: int = 30

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

    # Run queries sequentially — AsyncSession does not support concurrent
    # db.execute() calls via asyncio.gather (causes IllegalStateChangeError).
    farmer_count_result = await db.execute(
        select(func.count())
        .select_from(User)
        .where(User.role == "farmer", User.deleted_at.is_(None))
    )
    animal_count_result = await db.execute(
        select(func.count()).select_from(Animal).where(Animal.deleted_at.is_(None))
    )
    milk_result = await db.execute(
        select(func.coalesce(func.sum(YieldLog.quantity_liters), 0.0)).where(
            YieldLog.recorded_at >= today_start, YieldLog.deleted_at.is_(None)
        )
    )
    alert_result = await db.execute(
        select(func.count())
        .select_from(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > RISK_SCORE_THRESHOLD,
            HealthEvent.deleted_at.is_(None),
        )
    )
    revenue_result = await db.execute(
        select(func.coalesce(func.sum(SellRecord.total_amount), 0)).where(
            SellRecord.deleted_at.is_(None)
        )
    )
    sellers_result = await db.execute(
        select(func.count(func.distinct(SellRecord.user_id))).where(
            SellRecord.sold_at >= month_ago, SellRecord.deleted_at.is_(None)
        )
    )
    women_farmers_result = await db.execute(
        select(func.count())
        .select_from(User)
        .where(User.role == "farmer", User.gender == "female", User.deleted_at.is_(None))
    )
    women_tx_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id.in_(women_farmer_subq), Transaction.deleted_at.is_(None)
        )
    )
    women_sell_result = await db.execute(
        select(func.coalesce(func.sum(SellRecord.total_amount), 0)).where(
            SellRecord.user_id.in_(women_farmer_subq), SellRecord.deleted_at.is_(None)
        )
    )
    women_animals_result = await db.execute(
        select(func.count())
        .select_from(Animal)
        .where(
            Animal.user_id.in_(women_farmer_subq),
            Animal.deleted_at.is_(None),
        )
    )
    shg_count_result = await db.execute(
        select(func.count()).select_from(SHGGroup).where(SHGGroup.deleted_at.is_(None))
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
        days.append(
            {
                "date": day.isoformat(),
                "liters": round(rows.get(day, 0.0), 2),
            }
        )

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

        markers.append(
            {
                "event_id": str(event.id),
                "animal_id": str(event.animal_id),
                "species": animal.species if animal else None,
                "risk_score": event.ai_risk_score,
                "probable_diseases": event.probable_diseases,
                "district": owner.location_district if owner else None,
                "village_code": owner.village_code if owner else None,
                "event_date": event.event_date.isoformat(),
            }
        )

    return {"alert_count": len(markers), "markers": markers}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    body: UserRoleUpdate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Change a user's role (admin-only). Invalidates the auth cache for the user."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    old_role = user.role
    user.role = body.role.value
    await db.commit()
    await db.refresh(user)

    invalidate_user_cache(str(user_id))

    return {
        "id": str(user.id),
        "name": user.name,
        "role": user.role,
        "previous_role": old_role,
    }
