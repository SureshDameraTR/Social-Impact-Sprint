from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class GovtSchemeCreate(BaseModel):
    scheme_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    ministry: str | None = Field(None, max_length=200)
    description: str | None = None
    eligibility_criteria: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    max_subsidy_amount: Decimal | None = Field(None, max_digits=12, decimal_places=2)
    subsidy_percentage: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    is_active: bool = True
    valid_from: date
    valid_to: date | None = None


class GovtSchemeRead(BaseModel):
    id: UUID
    scheme_code: str
    name: str
    ministry: str | None = None
    description: str | None = None
    eligibility_criteria: str | None = None
    required_documents: list[str] | None = None
    max_subsidy_amount: Decimal | None = Field(None, max_digits=12, decimal_places=2)
    subsidy_percentage: Decimal | None = Field(None, max_digits=5, decimal_places=2)
    is_active: bool
    valid_from: date
    valid_to: date | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GovtSchemeListResponse(BaseModel):
    data: list[GovtSchemeRead]
    total: int
