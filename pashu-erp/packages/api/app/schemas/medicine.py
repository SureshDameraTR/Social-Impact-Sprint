from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class MedicineRead(BaseModel):
    id: UUID
    name_en: str
    name_kn: str | None = None
    type: str
    withdrawal_milk_days: int
    withdrawal_meat_days: int
    species_applicable: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MedicineAdministerRequest(BaseModel):
    animal_id: UUID
    medicine_id: UUID
    administered_at: datetime | None = None


class WithdrawalStatus(BaseModel):
    animal_id: UUID
    active_withdrawals: list[dict]
    milk_safe: bool
    meat_safe: bool
    earliest_milk_safe_date: date | None = None
    earliest_meat_safe_date: date | None = None
