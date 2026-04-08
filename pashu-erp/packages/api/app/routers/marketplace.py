"""Marketplace / product sales endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.marketplace import SellRecord
from app.models.user import User
from app.services.market_rates import KARNATAKA_RATES

router = APIRouter(prefix="/v1/marketplace", tags=["Marketplace"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SellCreate(BaseModel):
    product_type: str = Field(..., description="milk, eggs, goat_products, etc.")
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    price_per_unit: float = Field(..., gt=0)
    buyer_name: str | None = Field(None, max_length=200)
    buyer_phone: str | None = Field(None, max_length=15)
    sold_at: datetime
    notes: str | None = Field(None, max_length=500)


class SellRead(BaseModel):
    id: UUID
    user_id: UUID
    product_type: str
    quantity: float
    unit: str
    price_per_unit: float
    total_amount: float
    buyer_name: str | None = None
    buyer_phone: str | None = None
    sold_at: datetime
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/sell", response_model=SellRead, status_code=status.HTTP_201_CREATED)
async def record_sale(
    body: SellCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a product sale."""
    total_amount = round(body.quantity * body.price_per_unit, 2)

    record = SellRecord(
        user_id=current_user.id,
        product_type=body.product_type,
        quantity=body.quantity,
        unit=body.unit,
        price_per_unit=Decimal(str(body.price_per_unit)),
        total_amount=Decimal(str(total_amount)),
        buyer_name=body.buyer_name,
        buyer_phone=body.buyer_phone,
        sold_at=body.sold_at,
        notes=body.notes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/history/{user_id}", response_model=list[SellRead])
async def get_sell_history(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get sell history for a user."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(SellRecord)
        .where(SellRecord.user_id == user_id)
        .order_by(SellRecord.sold_at.desc())
    )
    return result.scalars().all()


@router.get("/rates")
async def get_market_rates(
    current_user: User = Depends(get_current_user),
):
    """Get current Karnataka APMC market rates."""
    return {
        "source": "Karnataka APMC (Hardcoded Reference Rates)",
        "updated_at": datetime.now(timezone.utc).date().isoformat(),
        "rates": KARNATAKA_RATES,
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

    result = await db.execute(
        select(SellRecord).where(SellRecord.user_id == user_id)
    )
    records = result.scalars().all()

    total_revenue = sum(float(r.total_amount) for r in records)
    total_quantity = sum(r.quantity for r in records)

    # Breakdown by product type
    by_product: dict[str, dict] = {}
    for r in records:
        key = r.product_type
        if key not in by_product:
            by_product[key] = {"quantity": 0.0, "revenue": 0.0, "count": 0}
        by_product[key]["quantity"] += r.quantity
        by_product[key]["revenue"] += float(r.total_amount)
        by_product[key]["count"] += 1

    return {
        "user_id": str(user_id),
        "total_revenue": round(total_revenue, 2),
        "total_quantity": round(total_quantity, 2),
        "total_sales": len(records),
        "by_product": by_product,
    }
