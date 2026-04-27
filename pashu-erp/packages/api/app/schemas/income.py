from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class IncomeSummary(BaseModel):
    total_income: Decimal
    period: str  # "week" / "month" / "year"
    start_date: date
    end_date: date
    by_product: dict[str, Decimal]
    transaction_count: int


class IncomeBreakdown(BaseModel):
    product_type: str
    amount: Decimal
    percentage: float
    transaction_count: int
