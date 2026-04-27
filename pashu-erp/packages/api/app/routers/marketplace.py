"""Marketplace / product sales endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.marketplace import SellRecord
from app.models.user import User
from app.schemas.marketplace import SellRecordCreate, SellRecordListResponse, SellRecordRead
from app.services.market_rates import get_all_market_rates

router = APIRouter(prefix="/v1/marketplace", tags=["Marketplace"])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("", response_model=SellRecordListResponse)
async def list_sell_records(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List sell records (admin: all, farmer: own only)."""
    base = select(SellRecord).where(SellRecord.deleted_at.is_(None))
    if current_user.role != "admin":
        base = base.where(SellRecord.user_id == current_user.id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(base.order_by(SellRecord.sold_at.desc()).offset(offset).limit(limit))
    data = result.scalars().all()
    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.post("/sell", response_model=SellRecordRead, status_code=status.HTTP_201_CREATED)
async def record_sale(
    body: SellRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a product sale."""
    total_amount = Decimal(str(body.quantity)) * Decimal(str(body.price_per_unit))
    total_amount = total_amount.quantize(Decimal("0.01"))

    record = SellRecord(
        user_id=current_user.id,
        product_type=body.product_type.value,
        quantity=Decimal(str(body.quantity)),
        unit=body.unit,
        price_per_unit=Decimal(str(body.price_per_unit)),
        total_amount=total_amount,
        buyer_name=body.buyer_name,
        buyer_phone=body.buyer_phone,
        sold_at=datetime.now(timezone.utc),
        notes=body.notes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/history/{user_id}", response_model=SellRecordListResponse)
async def get_sell_history(
    user_id: UUID,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get sell history for a user with pagination."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    base = select(SellRecord).where(SellRecord.user_id == user_id, SellRecord.deleted_at.is_(None))

    # Count
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    # Data
    result = await db.execute(base.order_by(SellRecord.sold_at.desc()).offset(offset).limit(limit))
    data = result.scalars().all()

    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/rates")
async def get_market_rates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current Karnataka APMC market rates from database."""
    rates = await get_all_market_rates(db)
    return {
        "source": "Karnataka APMC",
        "updated_at": datetime.now(timezone.utc).date().isoformat(),
        "rates": rates,
    }


@router.get("/summary/{user_id}")
async def get_marketplace_summary(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get marketplace summary stats for a user."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Aggregate totals in SQL
    totals_result = await db.execute(
        select(
            func.coalesce(func.sum(SellRecord.total_amount), 0).label("total_revenue"),
            func.coalesce(func.sum(SellRecord.quantity), 0).label("total_quantity"),
            func.count().label("total_sales"),
        ).where(SellRecord.user_id == user_id, SellRecord.deleted_at.is_(None))
    )
    totals = totals_result.one()

    # Breakdown by product type via GROUP BY
    breakdown_result = await db.execute(
        select(
            SellRecord.product_type,
            func.sum(SellRecord.quantity).label("quantity"),
            func.sum(SellRecord.total_amount).label("revenue"),
            func.count().label("count"),
        )
        .where(SellRecord.user_id == user_id, SellRecord.deleted_at.is_(None))
        .group_by(SellRecord.product_type)
    )
    by_product: dict[str, dict] = {}
    for row in breakdown_result.all():
        by_product[row.product_type] = {
            "quantity": round(float(row.quantity), 2),
            "revenue": round(float(row.revenue), 2),
            "count": row.count,
        }

    return {
        "user_id": str(user_id),
        "total_revenue": round(float(totals.total_revenue), 2),
        "total_quantity": round(float(totals.total_quantity), 2),
        "total_sales": totals.total_sales,
        "by_product": by_product,
    }
