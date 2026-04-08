from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GovtSchemeCreate(BaseModel):
    scheme_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    ministry: str | None = Field(None, max_length=200)
    description: str | None = None
    eligibility_criteria: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    max_subsidy_amount: float | None = None
    subsidy_percentage: float | None = None
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
    max_subsidy_amount: float | None = None
    subsidy_percentage: float | None = None
    is_active: bool
    valid_from: date
    valid_to: date | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
