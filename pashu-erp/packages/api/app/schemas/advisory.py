from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class AdvisoryCategory(str, Enum):
    health = "health"
    feeding = "feeding"
    breeding = "breeding"
    government = "government"


class AdvisorySource(str, Enum):
    ICAR = "ICAR"
    KMF = "KMF"
    NABARD = "NABARD"
    Community = "Community"


class AdvisoryTipRead(BaseModel):
    id: UUID
    title_en: str
    title_kn: str | None = None
    body_en: str | None = None
    body_kn: str | None = None
    category: AdvisoryCategory
    species_applicable: list[str] | None = None
    source: AdvisorySource
    priority: int
    is_active: bool
    published_at: datetime

    model_config = {"from_attributes": True}


class AdvisoryTipListResponse(BaseModel):
    data: list[AdvisoryTipRead]
    total: int
