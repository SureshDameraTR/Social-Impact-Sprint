from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class MilkSession(str, Enum):
    morning = "morning"
    evening = "evening"


class YieldLogCreate(BaseModel):
    animal_id: UUID
    quantity_liters: Decimal = Field(..., gt=0, le=100, max_digits=10, decimal_places=2)
    session: MilkSession
    notes: str | None = Field(None, max_length=500)


class YieldLogRead(BaseModel):
    id: UUID
    animal_id: UUID
    user_id: UUID
    quantity_liters: Decimal = Field(..., max_digits=10, decimal_places=2)
    session: MilkSession
    notes: str | None = None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class MilkHistoryResponse(BaseModel):
    logs: list[YieldLogRead]
    total_liters: Decimal = Field(..., max_digits=10, decimal_places=2)
    average_daily: Decimal = Field(..., max_digits=10, decimal_places=2)
    period_days: int


class CollectionRecordCreate(BaseModel):
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: Decimal = Field(..., gt=0, le=100, max_digits=10, decimal_places=2)
    fat_pct: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    snf_pct: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    shift: MilkSession


class CollectionRecordRead(BaseModel):
    id: UUID
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: Decimal = Field(..., max_digits=10, decimal_places=2)
    fat_pct: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    snf_pct: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    rate_per_liter: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    total_amount: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    shift: MilkSession
    collected_at: datetime

    model_config = {"from_attributes": True}
