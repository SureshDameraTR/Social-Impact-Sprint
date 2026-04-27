"""Finance / transaction endpoints."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.finance import Transaction
from app.models.user import User
from app.schemas.finance import TransactionCreate, TransactionRead

router = APIRouter(prefix="/v1/finance", tags=["Finance"])


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
        amount=body.amount,
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

    # SQL aggregation — avoid loading all rows into Python
    result = await db.execute(
        select(
            Transaction.type,
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count().label("cnt"),
        )
        .where(
            Transaction.user_id == current_user.id,
            Transaction.created_at >= since,
            Transaction.deleted_at.is_(None),
        )
        .group_by(Transaction.type, Transaction.category)
    )
    rows = result.all()

    total_income = Decimal("0")
    total_expense = Decimal("0")
    income_by_category: dict[str, float] = {}
    expense_by_category: dict[str, float] = {}
    transaction_count = 0

    for r in rows:
        amt = Decimal(str(r.total))
        transaction_count += r.cnt
        if r.type == "income":
            total_income += amt
            income_by_category[r.category] = float(amt.quantize(Decimal("0.01")))
        else:
            total_expense += amt
            expense_by_category[r.category] = float(amt.quantize(Decimal("0.01")))

    return {
        "period": period,
        "total_income": float(total_income.quantize(Decimal("0.01"))),
        "total_expense": float(total_expense.quantize(Decimal("0.01"))),
        "net": float((total_income - total_expense).quantize(Decimal("0.01"))),
        "transaction_count": transaction_count,
        "income_by_category": income_by_category,
        "expense_by_category": expense_by_category,
    }
