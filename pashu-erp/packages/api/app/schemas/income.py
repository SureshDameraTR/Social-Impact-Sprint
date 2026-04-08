from datetime import date

from pydantic import BaseModel


class IncomeSummary(BaseModel):
    total_income: float
    period: str  # "week" / "month" / "year"
    start_date: date
    end_date: date
    by_product: dict[str, float]
    transaction_count: int


class IncomeBreakdown(BaseModel):
    product_type: str
    amount: float
    percentage: float
    transaction_count: int
