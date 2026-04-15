from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionStatus(str, Enum):
    completed = "completed"
    pending = "pending"
    cancelled = "cancelled"


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    category: str = Field(..., max_length=50)
    reference_id: UUID | None = None
    description: str | None = Field(None, max_length=500)


class TransactionRead(BaseModel):
    id: UUID
    user_id: UUID
    type: TransactionType
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    category: str
    reference_id: UUID | None = None
    description: str | None = None
    status: TransactionStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class FinanceSummary(BaseModel):
    total_income: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_expense: Decimal = Field(..., max_digits=10, decimal_places=2)
    net: Decimal = Field(..., max_digits=10, decimal_places=2)
    period: str
    by_category: dict[str, Decimal]
