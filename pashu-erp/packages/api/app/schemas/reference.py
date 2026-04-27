"""Pydantic schemas for reference data endpoints.

Covers: locations, breeds, domain knowledge (disease rules, vaccination
schedules, feed standards), market rates, insurance premiums, medicine catalog.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Location hierarchy
# ---------------------------------------------------------------------------


class StateRead(BaseModel):
    lgd_code: int
    name: str
    name_local: str | None = None
    model_config = ConfigDict(from_attributes=True)


class DistrictRead(BaseModel):
    lgd_code: int
    name: str
    name_local: str | None = None
    state_lgd_code: int
    latitude: float | None = None
    longitude: float | None = None
    elevation_m: float | None = None
    model_config = ConfigDict(from_attributes=True)


class SubDistrictRead(BaseModel):
    lgd_code: int
    name: str
    name_local: str | None = None
    district_lgd_code: int
    model_config = ConfigDict(from_attributes=True)


class VillageRead(BaseModel):
    lgd_code: int
    name: str
    name_local: str | None = None
    sub_district_lgd_code: int
    pincode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    model_config = ConfigDict(from_attributes=True)


class LocationHierarchyResponse(BaseModel):
    data: list[StateRead]
    total: int


class DistrictListResponse(BaseModel):
    data: list[DistrictRead]
    total: int


class SubDistrictListResponse(BaseModel):
    data: list[SubDistrictRead]
    total: int


class VillageListResponse(BaseModel):
    data: list[VillageRead]
    total: int


# ---------------------------------------------------------------------------
# Species & breeds
# ---------------------------------------------------------------------------


class SpeciesRead(BaseModel):
    code: str
    name_en: str
    name_kn: str | None = None
    name_hi: str | None = None
    emoji: str | None = None
    model_config = ConfigDict(from_attributes=True)


class SpeciesListResponse(BaseModel):
    data: list[SpeciesRead]
    total: int


class BreedRead(BaseModel):
    id: UUID
    name: str
    name_local: str | None = None
    species_code: str
    origin: str | None = None
    nbagr_code: str | None = None
    is_indigenous: bool
    model_config = ConfigDict(from_attributes=True)


class BreedListResponse(BaseModel):
    data: list[BreedRead]
    total: int


# ---------------------------------------------------------------------------
# Domain knowledge — disease rules, vaccination schedules, feed standards
# ---------------------------------------------------------------------------


class DiseaseRuleRead(BaseModel):
    id: UUID
    species_code: str
    disease_name: str
    symptoms: list[str]
    min_match: int
    risk_level: str
    action: str
    source: str | None = None
    model_config = ConfigDict(from_attributes=True)


class DiseaseRuleListResponse(BaseModel):
    data: list[DiseaseRuleRead]
    total: int


class VaccinationScheduleRead(BaseModel):
    id: UUID
    species_code: str
    vaccine_name: str
    first_dose_months: int | None = None
    first_dose_days: int | None = None
    repeat_interval_months: int | None = None
    is_mandatory: bool
    notes: str | None = None
    source: str | None = None
    model_config = ConfigDict(from_attributes=True)


class VaccinationScheduleListResponse(BaseModel):
    data: list[VaccinationScheduleRead]
    total: int


class FeedStandardRead(BaseModel):
    id: UUID
    species_code: str
    lactation_stage: str | None = None
    dm_intake_pct_body_weight: float
    crude_protein_pct: float
    tdn_pct: float
    source: str | None = None
    model_config = ConfigDict(from_attributes=True)


class FeedStandardListResponse(BaseModel):
    data: list[FeedStandardRead]
    total: int


class MarketPriceRead(BaseModel):
    id: UUID
    product: str
    district: str
    min_price: float | None = None
    max_price: float | None = None
    modal_price: float
    unit: str
    source: str | None = None
    model_config = ConfigDict(from_attributes=True)


class MarketPriceListResponse(BaseModel):
    data: list[MarketPriceRead]
    total: int

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
    total: int


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
    total: int


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
    total: int
