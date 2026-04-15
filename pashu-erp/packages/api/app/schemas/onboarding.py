"""Pydantic schemas for user onboarding endpoints."""

from pydantic import BaseModel, Field


class OnboardingCompleteRequest(BaseModel):
    preferred_language: str = Field(default="kn", description="ISO 639-1 language code")
    district: str = Field(..., max_length=100)
    village_code: str | None = Field(None, max_length=20)
    primary_species: list[str] = Field(default_factory=list, description="Primary livestock species")
    herd_size: int = Field(default=0, ge=0)
    has_milk_center_access: bool = False
    shg_member: bool = False


class OnboardingPreferences(BaseModel):
    preferred_language: str
    district: str
    village_code: str | None = None
    primary_species: list[str]
    herd_size: int
    has_milk_center_access: bool
    shg_member: bool
    onboarding_complete: bool


class OnboardingCompleteResponse(BaseModel):
    user_id: str
    onboarding_complete: bool
    preferences: OnboardingPreferences
    message: str
    next_steps: list[str]
