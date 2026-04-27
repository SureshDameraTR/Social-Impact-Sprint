from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import strip_html as _strip_html


class HealthEventType(str, Enum):
    symptom = "symptom"
    checkup = "checkup"
    treatment = "treatment"
    emergency = "emergency"


class HealthEventCreate(BaseModel):
    animal_id: UUID
    event_type: HealthEventType
    description: str | None = None
    symptoms: list[str] = Field(default_factory=list)
    photo_urls: list[str] | None = None
    event_date: datetime | None = None

    @field_validator("description", mode="before")
    @classmethod
    def strip_html_tags(cls, v: str | None) -> str | None:
        return _strip_html(v)


class HealthEventRead(BaseModel):
    id: UUID
    animal_id: UUID
    event_type: HealthEventType
    description: str | None = None
    symptoms: list[str] | None = None
    ai_risk_score: float | None = None
    recommended_action: str | None = None
    probable_diseases: list[str] | None = None
    recorded_by: UUID | None = None
    event_date: datetime

    model_config = {"from_attributes": True}


class VaccinationCreate(BaseModel):
    animal_id: UUID
    vaccine_name: str = Field(..., max_length=200)
    administered_on: datetime
    next_due: datetime | None = None
    batch_number: str | None = Field(None, max_length=100)


class VaccinationRead(BaseModel):
    id: UUID
    animal_id: UUID
    vaccine_name: str
    administered_on: datetime
    next_due: datetime | None = None
    batch_number: str | None = None
    recorded_by: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthEventListResponse(BaseModel):
    data: list[HealthEventRead]
    total: int
    limit: int
    offset: int


class TriageResult(BaseModel):
    risk_level: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    probable_diseases: list[str]
    recommended_action: str
    source_reference: str
