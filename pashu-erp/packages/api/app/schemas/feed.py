from decimal import Decimal
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
    protein_pct: Decimal = Field(..., max_digits=5, decimal_places=2)
    energy_kcal: float
    cost_per_kg: Decimal = Field(..., max_digits=10, decimal_places=2)
    availability_season: str | None = None
    locally_available: bool

    model_config = {"from_attributes": True}


class RationIngredient(BaseModel):
    name: str
    daily_qty_kg: Decimal = Field(..., max_digits=10, decimal_places=2)


class RationRequest(BaseModel):
    species: str
    breed: str | None = None
    weight_kg: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    lactation_stage: LactationStage | None = None
    available_ingredients: list[UUID] = Field(default_factory=list)


class RationResult(BaseModel):
    ingredients: list[RationIngredient]
    total_cost_per_day: Decimal = Field(..., max_digits=10, decimal_places=2)
    protein_balance: str
    energy_balance: str
