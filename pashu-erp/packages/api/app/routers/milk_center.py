"""Milk collection center management endpoints."""

import hashlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.milk import MilkCollectionCenter, MilkCollectionRecord
from app.models.user import User
from app.services.milk_pricing import calculate_rate

router = APIRouter(prefix="/v1/milk-center", tags=["Milk Center"])


async def require_milk_center_staff(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in {"milk_center", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Milk center staff access required",
        )
    return current_user


class MilkReceiveRequest(BaseModel):
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: float = Field(..., gt=0, le=100)
    fat_pct: float = Field(..., ge=1.0, le=12.0)
    snf_pct: float = Field(..., ge=6.0, le=12.0)
    shift: str = Field(..., pattern="^(morning|evening)$")


@router.get("/my-center")
async def get_my_center(
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Return the collection centre assigned to the current user."""
    result = await db.execute(
        select(MilkCollectionCenter).where(
            MilkCollectionCenter.manager_user_id == current_user.id,
            MilkCollectionCenter.is_active.is_(True),
        )
    )
    center = result.scalar_one_or_none()
    if center is None:
        raise HTTPException(status_code=404, detail="No centre assigned")
    return {"id": str(center.id), "name": center.name, "code": center.code, "district": center.district}


@router.post("/receive", status_code=status.HTTP_201_CREATED)
async def receive_milk(
    body: MilkReceiveRequest,
    current_user: User = Depends(require_milk_center_staff),
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

    # Calculate rate based on FAT/SNF (Decimal arithmetic)
    rate = calculate_rate(body.fat_pct, body.snf_pct)
    qty = Decimal(str(body.quantity_liters))
    total_amount = (rate * qty).quantize(Decimal("0.01"))

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
        "quantity_liters": float(qty),
        "fat_pct": body.fat_pct,
        "snf_pct": body.snf_pct,
        "rate_per_liter": float(rate),
        "total_amount": float(total_amount),
        "shift": body.shift,
        "collected_at": record.collected_at.isoformat() if record.collected_at else None,
    }


@router.get("/{center_id}/daily-report")
async def get_daily_report(
    center_id: UUID,
    current_user: User = Depends(require_milk_center_staff),
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

    total_liters = sum((Decimal(str(r.quantity_liters)) for r in records), Decimal("0"))
    total_amount = sum((Decimal(str(r.total_amount or 0)) for r in records), Decimal("0"))
    farmer_ids = {str(r.farmer_user_id) for r in records}
    avg_fat = sum((Decimal(str(r.fat_pct or 0)) for r in records), Decimal("0")) / len(records) if records else Decimal("0")
    avg_snf = sum((Decimal(str(r.snf_pct or 0)) for r in records), Decimal("0")) / len(records) if records else Decimal("0")

    return {
        "center_id": str(center_id),
        "date": today_start.date().isoformat(),
        "summary": {
            "total_liters": float(total_liters.quantize(Decimal("0.01"))),
            "total_amount_inr": float(total_amount.quantize(Decimal("0.01"))),
            "farmer_count": len(farmer_ids),
            "record_count": len(records),
            "avg_fat_pct": float(avg_fat.quantize(Decimal("0.01"))),
            "avg_snf_pct": float(avg_snf.quantize(Decimal("0.01"))),
        },
        "morning": {
            "liters": float(sum((Decimal(str(r.quantity_liters)) for r in morning), Decimal("0")).quantize(Decimal("0.01"))),
            "farmers": len({str(r.farmer_user_id) for r in morning}),
        },
        "evening": {
            "liters": float(sum((Decimal(str(r.quantity_liters)) for r in evening), Decimal("0")).quantize(Decimal("0.01"))),
            "farmers": len({str(r.farmer_user_id) for r in evening}),
        },
    }


@router.get("/{center_id}/farmer-settlements")
async def get_farmer_settlements(
    center_id: UUID,
    days: int = Query(15, ge=1, le=90),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get payment settlement summary per farmer for a billing period."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Aggregate by farmer in SQL via GROUP BY
    agg_result = await db.execute(
        select(
            MilkCollectionRecord.farmer_user_id,
            func.sum(MilkCollectionRecord.quantity_liters).label("total_liters"),
            func.coalesce(func.sum(MilkCollectionRecord.total_amount), 0).label("total_amount"),
            func.count().label("deliveries"),
            func.avg(MilkCollectionRecord.fat_pct).label("avg_fat"),
            func.avg(MilkCollectionRecord.snf_pct).label("avg_snf"),
        )
        .where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= since,
        )
        .group_by(MilkCollectionRecord.farmer_user_id)
        .order_by(func.sum(MilkCollectionRecord.total_amount).desc())
        .offset(skip)
        .limit(limit)
    )
    rows = agg_result.all()

    result_list = []
    total_payout = Decimal("0")
    for row in rows:
        amt = Decimal(str(row.total_amount)).quantize(Decimal("0.01"))
        total_payout += amt
        result_list.append({
            "farmer_user_id": str(row.farmer_user_id),
            "total_liters": float(Decimal(str(row.total_liters)).quantize(Decimal("0.01"))),
            "total_amount_inr": float(amt),
            "deliveries": row.deliveries,
            "avg_fat_pct": float(Decimal(str(row.avg_fat or 0)).quantize(Decimal("0.01"))),
            "avg_snf_pct": float(Decimal(str(row.avg_snf or 0)).quantize(Decimal("0.01"))),
        })

    return {
        "center_id": str(center_id),
        "period_days": days,
        "settlements": result_list,
        "total_farmers": len(result_list),
        "total_payout_inr": float(total_payout.quantize(Decimal("0.01"))),
    }


@router.get("/farmers/search")
async def search_farmers(
    phone: str | None = Query(None, min_length=3, max_length=15),
    aadhaar_last4: str | None = Query(None, min_length=4, max_length=4),
    name: str | None = Query(None, min_length=2, max_length=100),
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Search farmers by phone, last 4 Aadhaar digits, or name."""
    if not any([phone, aadhaar_last4, name]):
        raise HTTPException(status_code=400, detail="At least one search parameter required")

    filters = []
    if phone:
        escaped = phone.replace("%", "").replace("_", "")
        filters.append(User.phone.ilike(f"%{escaped}%"))
    if aadhaar_last4:
        filters.append(User.aadhaar_last4 == aadhaar_last4)
    if name:
        escaped_name = name.replace("%", "").replace("_", "")
        filters.append(User.name.ilike(f"%{escaped_name}%"))

    result = await db.execute(
        select(User)
        .where(User.role == "farmer", or_(*filters))
        .limit(10)
    )
    farmers = result.scalars().all()

    return [
        {
            "id": str(f.id),
            "name": f.name,
            "phone": f.phone,
            "aadhaar_last4": f.aadhaar_last4,
            "village_code": f.village_code,
            "district": f.location_district,
        }
        for f in farmers
    ]


class QuickEnrollRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    aadhaar: str = Field(..., pattern=r"^\d{12}$")
    village_code: str | None = Field(None, max_length=20)


@router.post("/farmers/enroll", status_code=status.HTTP_201_CREATED)
async def quick_enroll_farmer(
    body: QuickEnrollRequest,
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Quick-enroll a new farmer at the collection centre."""
    aadhaar_hash = hashlib.sha256(body.aadhaar.encode()).hexdigest()

    dup_result = await db.execute(
        select(User).where(or_(User.phone == body.phone, User.aadhaar_hash == aadhaar_hash))
    )
    dup = dup_result.scalar_one_or_none()
    if dup:
        if dup.phone == body.phone:
            raise HTTPException(status_code=409, detail="Phone number already registered")
        raise HTTPException(status_code=409, detail="Aadhaar already registered")

    farmer = User(
        name=body.name,
        phone=body.phone,
        role="farmer",
        aadhaar_hash=aadhaar_hash,
        aadhaar_last4=body.aadhaar[-4:],
        village_code=body.village_code,
        lang_pref="kn",
    )
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)

    return {
        "id": str(farmer.id),
        "name": farmer.name,
        "phone": farmer.phone,
        "aadhaar_last4": farmer.aadhaar_last4,
        "message": "Farmer enrolled successfully",
    }
