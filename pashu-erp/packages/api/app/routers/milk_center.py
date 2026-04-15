"""Milk collection center management endpoints."""

import hashlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.milk import MilkCollectionCenter, MilkCollectionRecord
from app.models.user import User
from app.schemas.milk_center import (
    DailyReportResponse,
    FarmerSearchResult,
    FarmerSettlementsResponse,
    MilkReceiveRequest,
    MilkReceiveResponse,
    MyCenterResponse,
    QuickEnrollRequest,
    QuickEnrollResponse,
)
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


@router.get("/my-center", response_model=MyCenterResponse)
async def get_my_center(
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Return the collection centre assigned to the current user."""
    result = await db.execute(
        select(MilkCollectionCenter).where(
            MilkCollectionCenter.manager_user_id == current_user.id,
            MilkCollectionCenter.is_active.is_(True),
            MilkCollectionCenter.deleted_at.is_(None),
        )
    )
    center = result.scalar_one_or_none()
    if center is None:
        raise HTTPException(status_code=404, detail="No centre assigned")
    return {"id": str(center.id), "name": center.name, "code": center.code, "district": center.district}


@router.post("/receive", status_code=status.HTTP_201_CREATED, response_model=MilkReceiveResponse)
async def receive_milk(
    body: MilkReceiveRequest,
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Record milk receipt with quality parameters and auto-calculated rate."""
    # Verify center exists
    center_result = await db.execute(
        select(MilkCollectionCenter).where(MilkCollectionCenter.id == body.center_id, MilkCollectionCenter.deleted_at.is_(None))
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


@router.get("/{center_id}/daily-report", response_model=DailyReportResponse)
async def get_daily_report(
    center_id: UUID,
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Get daily milk collection report for a center."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # SQL aggregation by shift — avoids loading all records into Python
    shift_result = await db.execute(
        select(
            MilkCollectionRecord.shift,
            func.count().label("count"),
            func.sum(MilkCollectionRecord.quantity_liters).label("total_liters"),
            func.avg(MilkCollectionRecord.fat_pct).label("avg_fat"),
            func.avg(MilkCollectionRecord.snf_pct).label("avg_snf"),
            func.coalesce(func.sum(MilkCollectionRecord.total_amount), 0).label("total_paid"),
            func.count(func.distinct(MilkCollectionRecord.farmer_user_id)).label("farmer_count"),
        )
        .where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= today_start,
            MilkCollectionRecord.collected_at < today_end,
            MilkCollectionRecord.deleted_at.is_(None),
        )
        .group_by(MilkCollectionRecord.shift)
    )
    rows = shift_result.all()

    # Build per-shift and overall totals from aggregated rows
    overall_liters = Decimal("0")
    overall_amount = Decimal("0")
    overall_count = 0
    overall_fat_sum = Decimal("0")
    overall_snf_sum = Decimal("0")
    morning_data = {"liters": 0.0, "farmers": 0}
    evening_data = {"liters": 0.0, "farmers": 0}

    for r in rows:
        liters = Decimal(str(r.total_liters or 0))
        paid = Decimal(str(r.total_paid or 0))
        cnt = r.count or 0
        overall_liters += liters
        overall_amount += paid
        overall_count += cnt
        overall_fat_sum += Decimal(str(r.avg_fat or 0)) * cnt
        overall_snf_sum += Decimal(str(r.avg_snf or 0)) * cnt

        shift_info = {
            "liters": float(liters.quantize(Decimal("0.01"))),
            "farmers": r.farmer_count or 0,
        }
        if r.shift == "morning":
            morning_data = shift_info
        else:
            evening_data = shift_info

    avg_fat = (
        (overall_fat_sum / overall_count).quantize(Decimal("0.01"))
        if overall_count else Decimal("0")
    )
    avg_snf = (
        (overall_snf_sum / overall_count).quantize(Decimal("0.01"))
        if overall_count else Decimal("0")
    )

    # Total distinct farmers across shifts
    farmer_count_result = await db.execute(
        select(func.count(func.distinct(MilkCollectionRecord.farmer_user_id)))
        .where(
            MilkCollectionRecord.center_id == center_id,
            MilkCollectionRecord.collected_at >= today_start,
            MilkCollectionRecord.collected_at < today_end,
            MilkCollectionRecord.deleted_at.is_(None),
        )
    )
    total_farmers = farmer_count_result.scalar() or 0

    return {
        "center_id": str(center_id),
        "date": today_start.date().isoformat(),
        "summary": {
            "total_liters": float(overall_liters.quantize(Decimal("0.01"))),
            "total_amount_inr": float(overall_amount.quantize(Decimal("0.01"))),
            "farmer_count": total_farmers,
            "record_count": overall_count,
            "avg_fat_pct": float(avg_fat),
            "avg_snf_pct": float(avg_snf),
        },
        "morning": morning_data,
        "evening": evening_data,
    }


@router.get("/{center_id}/farmer-settlements", response_model=FarmerSettlementsResponse)
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
            MilkCollectionRecord.deleted_at.is_(None),
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


@router.get("/farmers/search", response_model=list[FarmerSearchResult])
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
        .where(User.role == "farmer", User.deleted_at.is_(None), or_(*filters))
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


@router.post("/farmers/enroll", status_code=status.HTTP_201_CREATED, response_model=QuickEnrollResponse)
async def quick_enroll_farmer(
    body: QuickEnrollRequest,
    current_user: User = Depends(require_milk_center_staff),
    db: AsyncSession = Depends(get_db),
):
    """Quick-enroll a new farmer at the collection centre."""
    aadhaar_hash = hashlib.sha256(body.aadhaar.encode()).hexdigest()

    dup_result = await db.execute(
        select(User).where(User.deleted_at.is_(None), or_(User.phone == body.phone, User.aadhaar_hash == aadhaar_hash))
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
