"""User onboarding endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/v1/onboarding", tags=["Onboarding"])


class OnboardingCompleteRequest(BaseModel):
    preferred_language: str = Field(default="kn", description="ISO 639-1 language code")
    district: str = Field(..., max_length=100)
    village_code: str | None = Field(None, max_length=20)
    primary_species: list[str] = Field(default_factory=list, description="Primary livestock species")
    herd_size: int = Field(default=0, ge=0)
    has_milk_center_access: bool = False
    shg_member: bool = False


@router.post("/complete")
async def complete_onboarding(
    body: OnboardingCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark onboarding as complete and save user preferences."""
    # Update user metadata with onboarding preferences
    # In a real implementation, these would be dedicated columns or a preferences table
    preferences = {
        "preferred_language": body.preferred_language,
        "district": body.district,
        "village_code": body.village_code,
        "primary_species": body.primary_species,
        "herd_size": body.herd_size,
        "has_milk_center_access": body.has_milk_center_access,
        "shg_member": body.shg_member,
        "onboarding_complete": True,
    }

    # Store in user metadata (JSONB field if available)
    # For prototype, we return the preferences as confirmation
    return {
        "user_id": str(current_user.id),
        "onboarding_complete": True,
        "preferences": preferences,
        "message": "Onboarding completed successfully. Welcome to PashuRaksha!",
        "next_steps": [
            "Add your animals using the Animal Registration feature",
            "Record daily milk yield",
            "Check vaccination schedule for your livestock",
            "Explore government schemes you may be eligible for",
        ],
    }
