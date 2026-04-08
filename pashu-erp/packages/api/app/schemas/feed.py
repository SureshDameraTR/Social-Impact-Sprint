from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class FeedCategory(str, Enum):
    roughage = "roughage"
    concentrate = "concentrate"
    supplement = "supplement"
    mineral = "mineral"


class LactationStage(str, Enum):
    dry = "dry"
    early = "early"
    mid = "mid"
    late = "late"


class FeedIngredientRead(BaseModel):
    id: UUID
    name_en: str
    name_kn: str | None = None
    category: FeedCategory
    protein_pct: float
    energy_kcal: float
    cost_per_kg: float
    availability_season: str | None = None
    locally_available: bool

    model_config = {"from_attributes": True}


class RationIngredient(BaseModel):
    name: str
    daily_qty_kg: float


class RationRequest(BaseModel):
    species: str
    breed: str | None = None
    weight_kg: float = Field(..., gt=0)
    lactation_stage: LactationStage | None = None
    available_ingredients: list[UUID] = Field(default_factory=list)


class RationResult(BaseModel):
    ingredients: list[RationIngredient]
    total_cost_per_day: float
    protein_balance: str
    energy_balance: str
