"""Pydantic schemas for DPDP consent endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.consent import ConsentPurpose, ConsentStatus


class ConsentGrantRequest(BaseModel):
    purpose: ConsentPurpose
    consent_text: str = Field(..., min_length=10, max_length=5000)


class ConsentWithdrawRequest(BaseModel):
    purpose: ConsentPurpose


class ConsentResponse(BaseModel):
    id: UUID
    user_id: UUID
    purpose: ConsentPurpose
    status: ConsentStatus
    consent_text: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConsentListResponse(BaseModel):
    data: list[ConsentResponse]
    total: int
