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
from app.schemas.milk import MilkHistoryResponse, YieldLogCreate, YieldLogRead

router = APIRouter(prefix="/v1/milk", tags=["Milk"])


@router.post("/yield", response_model=YieldLogRead, status_code=status.HTTP_201_CREATED)
async def record_yield(
    body: YieldLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a milk yield entry for an animal."""
    # Verify animal ownership
    result = await db.execute(select(Animal).where(Animal.id == body.animal_id))
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


@router.get("/farmer/{user_id}/history", response_model=MilkHistoryResponse)
async def get_milk_history(
    user_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get milk yield history with aggregated chart data."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(YieldLog)
        .where(YieldLog.user_id == user_id, YieldLog.recorded_at >= since)
        .order_by(YieldLog.recorded_at.desc())
    )
    logs = result.scalars().all()

    total_liters = sum(l.quantity_liters for l in logs)
    average_daily = total_liters / days if days > 0 else 0.0

    return MilkHistoryResponse(
        logs=logs,
        total_liters=round(total_liters, 2),
        average_daily=round(average_daily, 2),
        period_days=days,
    )


@router.get("/center/{center_id}/daily")
async def get_daily_collection(
    center_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily milk collection summary for a milk center."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    result = await db.execute(
        select(MilkCollectionRecord)
        .where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= today_start,
            MilkCollectionRecord.collected_at < today_end,
        )
        .order_by(MilkCollectionRecord.collected_at.desc())
    )
    records = result.scalars().all()

    total_liters = sum(r.quantity_liters for r in records)
    total_amount = sum(float(r.total_amount or 0) for r in records)
    farmer_count = len({str(r.farmer_user_id) for r in records})

    return {
        "center_id": str(center_id),
        "date": today_start.date().isoformat(),
        "total_liters": round(total_liters, 2),
        "total_amount": round(total_amount, 2),
        "farmer_count": farmer_count,
        "record_count": len(records),
    }
