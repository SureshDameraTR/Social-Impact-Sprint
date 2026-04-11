import re
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(v: str | None) -> str | None:
    """Remove HTML tags from a string value."""
    if v is None:
        return v
    return _HTML_TAG_RE.sub("", v).strip()


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

    @field_validator("name", "breed", mode="before")
    @classmethod
    def strip_html_tags(cls, v: str | None) -> str | None:
        return _strip_html(v)

    @field_validator("date_of_birth", mode="after")
    @classmethod
    def birth_not_in_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v


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

    @field_validator("name", "breed", mode="before")
    @classmethod
    def strip_html_tags(cls, v: str | None) -> str | None:
        return _strip_html(v)

    @field_validator("date_of_birth", mode="after")
    @classmethod
    def birth_not_in_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v


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
