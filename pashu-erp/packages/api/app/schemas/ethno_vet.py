from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class EvidenceRating(str, Enum):
    traditional = "traditional"
    studied = "studied"
    icar_validated = "icar_validated"


class TraditionalRemedyRead(BaseModel):
    id: UUID
    name_en: str
    name_kn: str | None = None
    plant_ingredient: str
    preparation_method: str | None = None
    dosage_by_species: dict | None = None
    conditions_treated: list[str] | None = None
    evidence_rating: EvidenceRating
    safety_warnings: str | None = None
    source_reference: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
