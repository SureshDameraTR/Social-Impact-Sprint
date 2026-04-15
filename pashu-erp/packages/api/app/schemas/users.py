"""Pydantic schemas for user profile and farmer listing endpoints."""

from pydantic import BaseModel


class FarmerListItem(BaseModel):
    id: str
    name: str | None = None
    phone: str | None = None
    district: str | None = None
    state: str | None = None
    village_code: str | None = None
    animals_count: int = 0
    registered_date: str | None = None


class FarmerListResponse(BaseModel):
    data: list[FarmerListItem]
    total: int
    limit: int
    offset: int


class UserProfile(BaseModel):
    id: str
    name: str | None = None
    phone: str | None = None
    role: str | None = None
    lang_pref: str | None = None
    location_district: str | None = None
    location_state: str | None = None
    village_code: str | None = None
    preferences: dict[str, object] | None = None
    animal_count: int = 0
    created_at: str | None = None
