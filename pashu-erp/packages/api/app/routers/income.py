"""Income dashboard endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.finance import Transaction
from app.models.marketplace import SellRecord
from app.models.user import User

router = APIRouter(prefix="/v1/income", tags=["Income"])


def _period_delta(period: str) -> timedelta:
    if period == "week":
        return timedelta(weeks=1)
    elif period == "year":
        return timedelta(days=365)
    return timedelta(days=30)


@router.get("/summary/{user_id}")
async def income_summary(
    user_id: UUID,
    period: str = Query("month", description="week, month, or year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Weekly/monthly totals from transactions + sell records."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    since = datetime.now(timezone.utc) - _period_delta(period)

    # Transactions
    txn_result = await db.execute(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.created_at >= since,
        )
    )
    txns = txn_result.scalars().all()

    txn_income = sum(float(t.amount) for t in txns if t.type == "income")
    txn_expense = sum(float(t.amount) for t in txns if t.type == "expense")

    # Sell records
    sell_result = await db.execute(
        select(SellRecord).where(
            SellRecord.user_id == user_id,
            SellRecord.sold_at >= since,
        )
    )
    sells = sell_result.scalars().all()
    sell_income = sum(float(s.total_amount) for s in sells)

    total_income = txn_income + sell_income

    return {
        "user_id": str(user_id),
        "period": period,
        "total_income": round(total_income, 2),
        "transaction_income": round(txn_income, 2),
        "marketplace_income": round(sell_income, 2),
        "total_expense": round(txn_expense, 2),
        "net": round(total_income - txn_expense, 2),
    }


@router.get("/breakdown/{user_id}")
async def income_breakdown(
    user_id: UUID,
    period: str = Query("month", description="week, month, or year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Income broken down by product category."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    since = datetime.now(timezone.utc) - _period_delta(period)

    # Transaction income by category
    txn_result = await db.execute(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.created_at >= since,
        )
    )
    txns = txn_result.scalars().all()
    by_category: dict[str, float] = {}
    for t in txns:
        by_category[t.category] = by_category.get(t.category, 0) + float(t.amount)

    # Sell record income by product type
    sell_result = await db.execute(
        select(SellRecord).where(
            SellRecord.user_id == user_id,
            SellRecord.sold_at >= since,
        )
    )
    sells = sell_result.scalars().all()
    for s in sells:
        key = f"marketplace_{s.product_type}"
        by_category[key] = by_category.get(key, 0) + float(s.total_amount)

    return {
        "user_id": str(user_id),
        "period": period,
        "breakdown": by_category,
    }


@router.get("/history/{user_id}")
async def income_history(
    user_id: UUID,
    period: str = Query("month", description="week, month, or year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transaction list for the given period."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    since = datetime.now(timezone.utc) - _period_delta(period)

    txn_result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user_id, Transaction.created_at >= since)
        .order_by(Transaction.created_at.desc())
    )
    txns = txn_result.scalars().all()

    sell_result = await db.execute(
        select(SellRecord)
        .where(SellRecord.user_id == user_id, SellRecord.sold_at >= since)
        .order_by(SellRecord.sold_at.desc())
    )
    sells = sell_result.scalars().all()

    history = []
    for t in txns:
        history.append({
            "type": "transaction",
            "sub_type": t.type,
            "amount": float(t.amount),
            "category": t.category,
            "description": t.description,
            "date": t.created_at.isoformat(),
        })
    for s in sells:
        history.append({
            "type": "sale",
            "sub_type": "income",
            "amount": float(s.total_amount),
            "category": s.product_type,
            "description": f"{s.quantity} {s.unit} @ {float(s.price_per_unit)}/{s.unit}",
            "date": s.sold_at.isoformat(),
        })

    # Sort combined list by date descending
    history.sort(key=lambda x: x["date"], reverse=True)

    return {
        "user_id": str(user_id),
        "period": period,
        "entries": history,
    }
