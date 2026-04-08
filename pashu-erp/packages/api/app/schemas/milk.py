from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class MilkSession(str, Enum):
    morning = "morning"
    evening = "evening"


class YieldLogCreate(BaseModel):
    animal_id: UUID
    quantity_liters: float = Field(..., gt=0)
    session: MilkSession
    notes: str | None = Field(None, max_length=500)


class YieldLogRead(BaseModel):
    id: UUID
    animal_id: UUID
    user_id: UUID
    quantity_liters: float
    session: MilkSession
    notes: str | None = None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class MilkHistoryResponse(BaseModel):
    logs: list[YieldLogRead]
    total_liters: float
    average_daily: float
    period_days: int


class CollectionRecordCreate(BaseModel):
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: float = Field(..., gt=0)
    fat_pct: float | None = None
    snf_pct: float | None = None
    shift: MilkSession


class CollectionRecordRead(BaseModel):
    id: UUID
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: float
    fat_pct: float | None = None
    snf_pct: float | None = None
    rate_per_liter: float | None = None
    total_amount: float | None = None
    shift: MilkSession
    collected_at: datetime

    model_config = {"from_attributes": True}
