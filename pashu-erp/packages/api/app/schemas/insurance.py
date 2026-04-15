import re
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(v: str | None) -> str | None:
    if v is None:
        return v
    return _HTML_TAG_RE.sub("", v).strip()


class PolicyStatus(str, Enum):
    active = "active"
    expired = "expired"
    claimed = "claimed"


class ClaimStatus(str, Enum):
    filed = "filed"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"


class InsurancePolicyRead(BaseModel):
    id: UUID
    animal_id: UUID
    provider: str
    policy_number: str
    premium_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    coverage_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    valid_from: datetime
    valid_to: datetime
    status: PolicyStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class InsuranceClaimCreate(BaseModel):
    policy_id: UUID
    claim_type: str = Field(..., max_length=100)
    description: str | None = None
    photo_urls: list[str] = Field(default_factory=list)

    @field_validator("claim_type", "description", mode="before")
    @classmethod
    def strip_html_tags(cls, v: str | None) -> str | None:
        return _strip_html(v)


class InsuranceClaimRead(BaseModel):
    id: UUID
    policy_id: UUID
    claim_type: str
    description: str | None = None
    photo_urls: list[str] | None = None
    status: ClaimStatus
    filed_at: datetime

    model_config = {"from_attributes": True}


class PremiumEstimate(BaseModel):
    animal_id: UUID
    species: str
    breed: str
    estimated_premium: Decimal = Field(..., max_digits=10, decimal_places=2)
    coverage_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    provider: str
    notes: str
