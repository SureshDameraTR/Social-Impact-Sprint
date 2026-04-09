from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class Species(str, Enum):
    cattle = "cattle"
    goat = "goat"
    sheep = "sheep"
    poultry = "poultry"


class BreedType(str, Enum):
    indigenous = "indigenous"
    crossbreed = "crossbreed"
    exotic = "exotic"


class AnimalSex(str, Enum):
    male = "male"
    female = "female"


class AnimalCreate(BaseModel):
    name: str | None = None
    species: Species
    breed: str = Field(..., max_length=100)
    breed_type: BreedType
    pashu_aadhaar_id: str | None = Field(None, max_length=12)
    tag_id: str | None = Field(None, max_length=50)
    date_of_birth: date | None = None
    sex: AnimalSex
    lactation_number: int | None = None
    body_condition_score: float | None = None
    is_insured: bool = False
    metadata: dict | None = None


class AnimalUpdate(BaseModel):
    name: str | None = None
    species: Species | None = None
    breed: str | None = Field(None, max_length=100)
    breed_type: BreedType | None = None
    pashu_aadhaar_id: str | None = Field(None, max_length=12)
    tag_id: str | None = Field(None, max_length=50)
    date_of_birth: date | None = None
    sex: AnimalSex | None = None
    lactation_number: int | None = None
    body_condition_score: float | None = None
    is_insured: bool | None = None
    metadata: dict | None = None


class AnimalRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str | None = None
    species: Species
    breed: str
    breed_type: BreedType
    pashu_aadhaar_id: str
    tag_id: str | None = None
    date_of_birth: date | None = None
    sex: AnimalSex
    lactation_number: int | None = None
    body_condition_score: float | None = None
    is_insured: bool
    metadata_: dict | None = Field(None, alias="metadata_", serialization_alias="metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
