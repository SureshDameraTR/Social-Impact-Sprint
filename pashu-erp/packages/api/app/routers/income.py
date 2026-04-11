"""Income dashboard endpoints."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import cast, Date, extract, func, select
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

    # Transaction income/expense via SQL aggregation
    txn_result = await db.execute(
        select(
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .where(Transaction.user_id == user_id, Transaction.created_at >= since)
        .group_by(Transaction.type)
    )
    txn_totals = {row.type: Decimal(str(row.total)) for row in txn_result.all()}
    txn_income = txn_totals.get("income", Decimal("0"))
    txn_expense = txn_totals.get("expense", Decimal("0"))

    # Sell record total via SQL aggregation
    sell_result = await db.execute(
        select(func.coalesce(func.sum(SellRecord.total_amount), 0))
        .where(SellRecord.user_id == user_id, SellRecord.sold_at >= since)
    )
    sell_income = Decimal(str(sell_result.scalar() or 0))

    total_income = txn_income + sell_income

    return {
        "user_id": str(user_id),
        "period": period,
        "total_income": float(total_income.quantize(Decimal("0.01"))),
        "transaction_income": float(txn_income.quantize(Decimal("0.01"))),
        "marketplace_income": float(sell_income.quantize(Decimal("0.01"))),
        "total_expense": float(txn_expense.quantize(Decimal("0.01"))),
        "net": float((total_income - txn_expense).quantize(Decimal("0.01"))),
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

    # Transaction income by category via SQL GROUP BY
    txn_result = await db.execute(
        select(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.created_at >= since,
        )
        .group_by(Transaction.category)
    )
    by_category: dict[str, float] = {}
    for row in txn_result.all():
        by_category[row.category] = float(Decimal(str(row.total)).quantize(Decimal("0.01")))

    # Sell record income by product type via SQL GROUP BY
    sell_result = await db.execute(
        select(
            SellRecord.product_type,
            func.sum(SellRecord.total_amount).label("total"),
        )
        .where(
            SellRecord.user_id == user_id,
            SellRecord.sold_at >= since,
        )
        .group_by(SellRecord.product_type)
    )
    for row in sell_result.all():
        by_category[f"marketplace_{row.product_type}"] = float(Decimal(str(row.total)).quantize(Decimal("0.01")))

    return {
        "user_id": str(user_id),
        "period": period,
        "breakdown": by_category,
    }


@router.get("/history/{user_id}")
async def income_history(
    user_id: UUID,
    period: str = Query("month", description="week, month, or year"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transaction list for the given period with pagination."""
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
            "amount": float(Decimal(str(t.amount))),
            "category": t.category,
            "description": t.description,
            "date": t.created_at.isoformat(),
        })
    for s in sells:
        history.append({
            "type": "sale",
            "sub_type": "income",
            "amount": float(Decimal(str(s.total_amount))),
            "category": s.product_type,
            "description": f"{s.quantity} {s.unit} @ {float(Decimal(str(s.price_per_unit)))}/{s.unit}",
            "date": s.sold_at.isoformat(),
        })

    # Sort combined list by date descending
    history.sort(key=lambda x: x["date"], reverse=True)

    # Apply pagination to the combined list
    total = len(history)
    history = history[offset:offset + limit]

    return {
        "data": history,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# ---------------------------------------------------------------------------
# Convenience endpoints (current-user context for mobile)
# ---------------------------------------------------------------------------

@router.get("/summary")
async def my_income_summary(
    period: str = Query("month", description="week, month, or year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Weekly/monthly totals for the authenticated user."""
    since = datetime.now(timezone.utc) - _period_delta(period)

    txn_result = await db.execute(
        select(
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .where(Transaction.user_id == current_user.id, Transaction.created_at >= since)
        .group_by(Transaction.type)
    )
    txn_totals = {row.type: Decimal(str(row.total)) for row in txn_result.all()}
    txn_income = txn_totals.get("income", Decimal("0"))
    txn_expense = txn_totals.get("expense", Decimal("0"))

    sell_result = await db.execute(
        select(func.coalesce(func.sum(SellRecord.total_amount), 0))
        .where(SellRecord.user_id == current_user.id, SellRecord.sold_at >= since)
    )
    sell_income = Decimal(str(sell_result.scalar() or 0))

    total_income = txn_income + sell_income

    return {
        "user_id": str(current_user.id),
        "period": period,
        "total_income": float(total_income.quantize(Decimal("0.01"))),
        "transaction_income": float(txn_income.quantize(Decimal("0.01"))),
        "marketplace_income": float(sell_income.quantize(Decimal("0.01"))),
        "total_expense": float(txn_expense.quantize(Decimal("0.01"))),
        "net": float((total_income - txn_expense).quantize(Decimal("0.01"))),
    }


@router.get("/transactions")
async def my_income_transactions(
    period: str = Query("month", description="week, month, or year"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transaction list for the authenticated user."""
    since = datetime.now(timezone.utc) - _period_delta(period)

    base = select(Transaction).where(
        Transaction.user_id == current_user.id, Transaction.created_at >= since
    )
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(Transaction.created_at.desc()).offset(offset).limit(limit)
    )
    data = result.scalars().all()

    return {"data": data, "total": total, "limit": limit, "offset": offset}


# ---------------------------------------------------------------------------
# Admin-oriented aggregation endpoints
# ---------------------------------------------------------------------------

@router.get("/by-category")
async def income_by_category(
    period: str = Query("month", description="week, month, or year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Income grouped by category across all users (admin view) or current user."""
    since = datetime.now(timezone.utc) - _period_delta(period)

    # Transaction income by category
    txn_query = (
        select(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
        )
        .where(Transaction.type == "income", Transaction.created_at >= since)
    )
    if current_user.role != "admin":
        txn_query = txn_query.where(Transaction.user_id == current_user.id)
    txn_query = txn_query.group_by(Transaction.category)

    txn_result = await db.execute(txn_query)
    by_category: dict[str, float] = {}
    for row in txn_result.all():
        by_category[row.category] = float(Decimal(str(row.total)).quantize(Decimal("0.01")))

    # Sell record income by product type
    sell_query = (
        select(
            SellRecord.product_type,
            func.sum(SellRecord.total_amount).label("total"),
        )
        .where(SellRecord.sold_at >= since)
    )
    if current_user.role != "admin":
        sell_query = sell_query.where(SellRecord.user_id == current_user.id)
    sell_query = sell_query.group_by(SellRecord.product_type)

    sell_result = await db.execute(sell_query)
    for row in sell_result.all():
        key = f"marketplace_{row.product_type}"
        by_category[key] = float(Decimal(str(row.total)).quantize(Decimal("0.01")))

    return {"period": period, "breakdown": by_category}


@router.get("/monthly")
async def income_monthly_trend(
    months: int = Query(12, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Monthly income trend for charting."""
    since = datetime.now(timezone.utc) - timedelta(days=months * 31)

    # Transactions grouped by month
    txn_query = (
        select(
            extract("year", Transaction.created_at).label("yr"),
            extract("month", Transaction.created_at).label("mo"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .where(Transaction.created_at >= since)
    )
    if current_user.role != "admin":
        txn_query = txn_query.where(Transaction.user_id == current_user.id)
    txn_query = txn_query.group_by("yr", "mo", Transaction.type)

    txn_result = await db.execute(txn_query)

    month_data: dict[str, dict[str, Decimal]] = {}
    for row in txn_result.all():
        key = f"{int(row.yr)}-{int(row.mo):02d}"
        if key not in month_data:
            month_data[key] = {"income": Decimal("0"), "expense": Decimal("0"), "marketplace": Decimal("0")}
        month_data[key][row.type] = Decimal(str(row.total))

    # Sell records grouped by month
    sell_query = (
        select(
            extract("year", SellRecord.sold_at).label("yr"),
            extract("month", SellRecord.sold_at).label("mo"),
            func.sum(SellRecord.total_amount).label("total"),
        )
        .where(SellRecord.sold_at >= since)
    )
    if current_user.role != "admin":
        sell_query = sell_query.where(SellRecord.user_id == current_user.id)
    sell_query = sell_query.group_by("yr", "mo")

    sell_result = await db.execute(sell_query)
    for row in sell_result.all():
        key = f"{int(row.yr)}-{int(row.mo):02d}"
        if key not in month_data:
            month_data[key] = {"income": Decimal("0"), "expense": Decimal("0"), "marketplace": Decimal("0")}
        month_data[key]["marketplace"] = Decimal(str(row.total))

    # Sort by month key
    trend = []
    for key in sorted(month_data.keys()):
        d = month_data[key]
        total_inc = d["income"] + d["marketplace"]
        trend.append({
            "month": key,
            "income": float(total_inc.quantize(Decimal("0.01"))),
            "expense": float(d["expense"].quantize(Decimal("0.01"))),
            "net": float((total_inc - d["expense"]).quantize(Decimal("0.01"))),
        })

    return {"months": months, "data": trend}
