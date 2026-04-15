import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(v: str | None) -> str | None:
    if v is None:
        return v
    return _HTML_TAG_RE.sub("", v).strip()


class SHGGrading(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    ungraded = "ungraded"


class SHGGroupCreate(BaseModel):
    name: str = Field(..., max_length=200)
    registration_number: str | None = Field(None, max_length=50)
    district: str | None = Field(None, max_length=100)
    village_code: str | None = Field(None, max_length=20)
    member_count: int = Field(default=0, ge=0)
    women_only: bool = True
    formation_date: date | None = None
    total_savings: Decimal = Field(default=Decimal("0"), max_digits=10, decimal_places=2)
    grading: SHGGrading = SHGGrading.ungraded
    panchsutra_compliance: dict | None = None

    @field_validator("name", "district", mode="before")
    @classmethod
    def strip_html_tags(cls, v: str | None) -> str | None:
        return _strip_html(v)


class SHGGroupRead(BaseModel):
    id: UUID
    name: str
    registration_number: str | None = None
    district: str | None = None
    village_code: str | None = None
    admin_user_id: UUID
    member_count: int
    women_only: bool
    formation_date: date | None = None
    total_savings: Decimal = Field(..., max_digits=10, decimal_places=2)
    grading: SHGGrading
    panchsutra_compliance: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PanchsutraScore(BaseModel):
    regular_meetings: bool
    regular_savings: bool
    regular_internal_lending: bool
    regular_bookkeeping: bool
    active_bank_linkage: bool
    score: int = Field(..., ge=0, le=5)
    grade: str
