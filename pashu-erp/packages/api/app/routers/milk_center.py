"""Milk collection center management endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.milk import MilkCollectionCenter, MilkCollectionRecord
from app.models.user import User
from app.services.milk_pricing import calculate_rate

router = APIRouter(prefix="/v1/milk-center", tags=["Milk Center"])


class MilkReceiveRequest(BaseModel):
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: float = Field(..., gt=0)
    fat_pct: float = Field(..., ge=1.0, le=12.0)
    snf_pct: float = Field(..., ge=6.0, le=12.0)
    shift: str = Field(..., pattern="^(morning|evening)$")


@router.post("/receive", status_code=status.HTTP_201_CREATED)
async def receive_milk(
    body: MilkReceiveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record milk receipt with quality parameters and auto-calculated rate."""
    # Verify center exists
    center_result = await db.execute(
        select(MilkCollectionCenter).where(MilkCollectionCenter.id == body.center_id)
    )
    center = center_result.scalar_one_or_none()
    if center is None:
        raise HTTPException(status_code=404, detail="Milk center not found")

    # Calculate rate based on FAT/SNF
    rate = calculate_rate(body.fat_pct, body.snf_pct)
    total_amount = round(rate * body.quantity_liters, 2)

    record = MilkCollectionRecord(
        center_id=str(body.center_id),
        farmer_user_id=str(body.farmer_user_id),
        quantity_liters=body.quantity_liters,
        fat_pct=body.fat_pct,
        snf_pct=body.snf_pct,
        rate_per_liter=rate,
        total_amount=total_amount,
        shift=body.shift,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": str(record.id),
        "center_id": str(body.center_id),
        "farmer_user_id": str(body.farmer_user_id),
        "quantity_liters": body.quantity_liters,
        "fat_pct": body.fat_pct,
        "snf_pct": body.snf_pct,
        "rate_per_liter": rate,
        "total_amount": total_amount,
        "shift": body.shift,
        "collected_at": record.collected_at.isoformat() if record.collected_at else None,
    }


@router.get("/{center_id}/daily-report")
async def get_daily_report(
    center_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily milk collection report for a center."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    result = await db.execute(
        select(MilkCollectionRecord)
        .where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= today_start,
            MilkCollectionRecord.collected_at < today_end,
        )
        .order_by(MilkCollectionRecord.collected_at)
    )
    records = result.scalars().all()

    morning = [r for r in records if r.shift == "morning"]
    evening = [r for r in records if r.shift == "evening"]

    total_liters = sum(r.quantity_liters for r in records)
    total_amount = sum(float(r.total_amount or 0) for r in records)
    farmer_ids = {str(r.farmer_user_id) for r in records}
    avg_fat = sum(r.fat_pct or 0 for r in records) / len(records) if records else 0
    avg_snf = sum(r.snf_pct or 0 for r in records) / len(records) if records else 0

    return {
        "center_id": str(center_id),
        "date": today_start.date().isoformat(),
        "summary": {
            "total_liters": round(total_liters, 2),
            "total_amount_inr": round(total_amount, 2),
            "farmer_count": len(farmer_ids),
            "record_count": len(records),
            "avg_fat_pct": round(avg_fat, 2),
            "avg_snf_pct": round(avg_snf, 2),
        },
        "morning": {
            "liters": round(sum(r.quantity_liters for r in morning), 2),
            "farmers": len({str(r.farmer_user_id) for r in morning}),
        },
        "evening": {
            "liters": round(sum(r.quantity_liters for r in evening), 2),
            "farmers": len({str(r.farmer_user_id) for r in evening}),
        },
    }


@router.get("/{center_id}/farmer-settlements")
async def get_farmer_settlements(
    center_id: UUID,
    days: int = 15,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get payment settlement summary per farmer for a billing period."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(MilkCollectionRecord)
        .where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= since,
        )
        .order_by(MilkCollectionRecord.farmer_user_id)
    )
    records = result.scalars().all()

    # Aggregate by farmer
    settlements: dict[str, dict] = {}
    for r in records:
        fid = str(r.farmer_user_id)
        if fid not in settlements:
            settlements[fid] = {
                "farmer_user_id": fid,
                "total_liters": 0,
                "total_amount": 0,
                "deliveries": 0,
                "avg_fat": 0,
                "avg_snf": 0,
                "fat_sum": 0,
                "snf_sum": 0,
            }
        s = settlements[fid]
        s["total_liters"] += r.quantity_liters
        s["total_amount"] += float(r.total_amount or 0)
        s["deliveries"] += 1
        s["fat_sum"] += r.fat_pct or 0
        s["snf_sum"] += r.snf_pct or 0

    result_list = []
    for s in settlements.values():
        count = s["deliveries"]
        result_list.append({
            "farmer_user_id": s["farmer_user_id"],
            "total_liters": round(s["total_liters"], 2),
            "total_amount_inr": round(s["total_amount"], 2),
            "deliveries": count,
            "avg_fat_pct": round(s["fat_sum"] / count, 2) if count else 0,
            "avg_snf_pct": round(s["snf_sum"] / count, 2) if count else 0,
        })

    result_list.sort(key=lambda x: x["total_amount_inr"], reverse=True)

    return {
        "center_id": str(center_id),
        "period_days": days,
        "settlements": result_list,
        "total_farmers": len(result_list),
        "total_payout_inr": round(sum(s["total_amount_inr"] for s in result_list), 2),
    }
