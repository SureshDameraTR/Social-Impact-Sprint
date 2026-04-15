"""Pydantic schemas for medicine log / withdrawal endpoints."""

from pydantic import BaseModel


class WithdrawalItem(BaseModel):
    animal_id: str
    animal_name: str | None = None
    species: str | None = None
    medicine: str
    administered_at: str
    milk_withdrawal_until: str | None = None
    meat_withdrawal_until: str | None = None
    milk_safe: bool
    meat_safe: bool


class WithdrawalListResponse(BaseModel):
    data: list[WithdrawalItem]
    total: int
