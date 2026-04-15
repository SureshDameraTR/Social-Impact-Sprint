"""Pydantic schemas for reference data endpoints (market rates, insurance, medicine catalog)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Market rates
# ---------------------------------------------------------------------------

class MarketRateUpdate(BaseModel):
    product: str | None = Field(None, max_length=100)
    unit: str | None = Field(None, max_length=20)
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    avg_price: Decimal | None = Field(None, ge=0)
    district: str | None = Field(None, max_length=100)
    label: str | None = Field(None, max_length=200)
    source: str | None = Field(None, max_length=200)


class MarketRateRead(BaseModel):
    id: UUID
    product: str
    unit: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    avg_price: Decimal | None = None
    district: str | None = None
    label: str | None = None
    source: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MarketRateListResponse(BaseModel):
    data: list[MarketRateRead]


# ---------------------------------------------------------------------------
# Insurance premiums
# ---------------------------------------------------------------------------

class InsurancePremiumUpdate(BaseModel):
    species: str | None = Field(None, max_length=50)
    breed_type: str | None = Field(None, max_length=50)
    premium_pct: Decimal | None = Field(None, ge=0, le=100)
    animal_value_inr: int | None = Field(None, ge=0)
    scheme_name: str | None = Field(None, max_length=200)


class InsurancePremiumRead(BaseModel):
    id: UUID
    species: str
    breed_type: str | None = None
    premium_pct: Decimal | None = None
    animal_value_inr: int | None = None
    scheme_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class InsurancePremiumListResponse(BaseModel):
    data: list[InsurancePremiumRead]


# ---------------------------------------------------------------------------
# Medicine catalog
# ---------------------------------------------------------------------------

class MedicineCatalogRead(BaseModel):
    id: UUID
    name: str
    category: str | None = None
    species_applicable: list[str] | None = None
    dosage_info: str | None = None
    withdrawal_milk_days: int | None = None
    withdrawal_meat_days: int | None = None
    is_active: bool = True
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MedicineCatalogListResponse(BaseModel):
    data: list[MedicineCatalogRead]
