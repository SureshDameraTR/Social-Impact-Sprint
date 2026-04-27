"""Milk recording endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.milk import MilkCollectionRecord, YieldLog
from app.models.user import User
from app.schemas.milk import YieldLogCreate, YieldLogListResponse, YieldLogRead

router = APIRouter(prefix="/v1/milk", tags=["Milk"])


# ---------------------------------------------------------------------------
# Convenience endpoints for mobile app (current user context)
# ---------------------------------------------------------------------------


@router.get("", response_model=YieldLogListResponse)
async def list_milk_records(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List milk yield records (admin: all, farmer: own only)."""
    base = select(YieldLog).where(YieldLog.deleted_at.is_(None))
    if current_user.role != "admin":
        base = base.where(YieldLog.user_id == current_user.id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(YieldLog.recorded_at.desc()).offset(offset).limit(limit)
    )
    data = [YieldLogRead.model_validate(r, from_attributes=True) for r in result.scalars().all()]
    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/today")
async def get_today_total(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's total milk yield for the authenticated user."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(
            func.coalesce(func.sum(YieldLog.quantity_liters), 0).label("total"),
            func.count().label("entries"),
        ).where(
            YieldLog.user_id == current_user.id,
            YieldLog.recorded_at >= today_start,
            YieldLog.deleted_at.is_(None),
        )
    )
    row = result.one()
    return {
        "user_id": str(current_user.id),
        "date": today_start.date().isoformat(),
        "total_liters": round(float(row.total), 2),
        "entries": row.entries,
    }


@router.get("/history", response_model=YieldLogListResponse)
async def get_my_milk_history(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get milk yield history for the authenticated user."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    base = select(YieldLog).where(
        YieldLog.user_id == current_user.id,
        YieldLog.recorded_at >= since,
        YieldLog.deleted_at.is_(None),
    )

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(YieldLog.recorded_at.desc()).offset(offset).limit(limit)
    )
    data = [YieldLogRead.model_validate(r, from_attributes=True) for r in result.scalars().all()]
    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/daily-summary")
async def get_daily_summary(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Daily aggregated milk data for charting (admin dashboard)."""
    from sqlalchemy import Date, cast

    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

    base_filter = (YieldLog.recorded_at >= start_date) & (YieldLog.deleted_at.is_(None))
    if current_user.role != "admin":
        base_filter = (
            (YieldLog.recorded_at >= start_date)
            & (YieldLog.user_id == current_user.id)
            & (YieldLog.deleted_at.is_(None))
        )

    result = await db.execute(
        select(
            cast(YieldLog.recorded_at, Date).label("day"),
            func.coalesce(func.sum(YieldLog.quantity_liters), 0.0).label("total"),
            func.count(func.distinct(YieldLog.user_id)).label("farmers"),
        )
        .where(base_filter)
        .group_by(cast(YieldLog.recorded_at, Date))
    )
    rows = {row.day: {"liters": float(row.total), "farmers": row.farmers} for row in result.all()}

    data = []
    for i in range(days):
        day = (now - timedelta(days=days - 1 - i)).date()
        entry = rows.get(day, {"liters": 0.0, "farmers": 0})
        data.append(
            {
                "date": day.isoformat(),
                "liters": round(entry["liters"], 2),
                "farmers": entry["farmers"],
            }
        )

    return {"period_days": days, "data": data}


@router.post("/yield", response_model=YieldLogRead, status_code=status.HTTP_201_CREATED)
async def record_yield(
    body: YieldLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a milk yield entry for an animal."""
    # Verify animal ownership
    result = await db.execute(
        select(Animal).where(Animal.id == body.animal_id, Animal.deleted_at.is_(None))
    )
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    log = YieldLog(
        animal_id=str(body.animal_id),
        user_id=str(current_user.id),
        quantity_liters=body.quantity_liters,
        session=body.session.value,
        notes=body.notes,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/farmer/{user_id}/history", response_model=YieldLogListResponse)
async def get_milk_history(
    user_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get milk yield history with pagination."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    base = select(YieldLog).where(
        YieldLog.user_id == user_id, YieldLog.recorded_at >= since, YieldLog.deleted_at.is_(None)
    )

    # Count
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    # Data
    result = await db.execute(
        base.order_by(YieldLog.recorded_at.desc()).offset(offset).limit(limit)
    )
    data = [YieldLogRead.model_validate(r, from_attributes=True) for r in result.scalars().all()]

    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/center/{center_id}/daily")
async def get_daily_collection(
    center_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily milk collection summary for a milk center."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Aggregate in SQL instead of fetching all records
    agg_result = await db.execute(
        select(
            func.coalesce(func.sum(MilkCollectionRecord.quantity_liters), 0).label("total_liters"),
            func.coalesce(func.sum(MilkCollectionRecord.total_amount), 0).label("total_amount"),
            func.count(func.distinct(MilkCollectionRecord.farmer_user_id)).label("farmer_count"),
            func.count().label("record_count"),
        ).where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= today_start,
            MilkCollectionRecord.collected_at < today_end,
            MilkCollectionRecord.deleted_at.is_(None),
        )
    )
    row = agg_result.one()

    return {
        "center_id": str(center_id),
        "date": today_start.date().isoformat(),
        "total_liters": round(float(row.total_liters), 2),
        "total_amount": round(float(row.total_amount), 2),
        "farmer_count": row.farmer_count,
        "record_count": row.record_count,
    }
