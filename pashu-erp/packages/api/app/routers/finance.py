"""Finance / transaction endpoints."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.finance import Transaction, TransactionType
from app.models.user import User

router = APIRouter(prefix="/v1/finance", tags=["Finance"])


# ---------------------------------------------------------------------------
# Pydantic schemas (inline — light enough to keep here)
# ---------------------------------------------------------------------------
from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    type: str = Field(..., description="income or expense")
    amount: float = Field(..., gt=0)
    category: str = Field(..., max_length=50)
    description: str | None = Field(None, max_length=500)
    reference_id: UUID | None = None


class TransactionRead(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    amount: float
    category: str
    description: str | None = None
    reference_id: UUID | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/transaction", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def record_transaction(
    body: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a financial transaction."""
    txn = Transaction(
        user_id=current_user.id,
        type=body.type,
        amount=Decimal(str(body.amount)),
        category=body.category,
        description=body.description,
        reference_id=str(body.reference_id) if body.reference_id else None,
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    return txn


@router.get("/summary")
async def financial_summary(
    period: str = Query("month", description="week, month, or year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get financial summary for the current user."""
    now = datetime.now(timezone.utc)
    if period == "week":
        since = now - timedelta(weeks=1)
    elif period == "year":
        since = now - timedelta(days=365)
    else:
        since = now - timedelta(days=30)

    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id, Transaction.created_at >= since)
    )
    txns = result.scalars().all()

    total_income = sum(float(t.amount) for t in txns if t.type == "income")
    total_expense = sum(float(t.amount) for t in txns if t.type == "expense")

    # Category breakdown
    income_by_category: dict[str, float] = {}
    expense_by_category: dict[str, float] = {}
    for t in txns:
        bucket = income_by_category if t.type == "income" else expense_by_category
        bucket[t.category] = bucket.get(t.category, 0) + float(t.amount)

    return {
        "period": period,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net": round(total_income - total_expense, 2),
        "transaction_count": len(txns),
        "income_by_category": income_by_category,
        "expense_by_category": expense_by_category,
    }
