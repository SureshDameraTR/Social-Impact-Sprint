"""User onboarding endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.onboarding import OnboardingCompleteRequest, OnboardingCompleteResponse

router = APIRouter(prefix="/v1/onboarding", tags=["Onboarding"])


@router.post("/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    body: OnboardingCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark onboarding as complete and save user preferences."""
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

    # Re-load the user within the current session to avoid detached-instance errors
    # (current_user may be served from the auth cache, bound to a different session)
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Persist preferences on the user record
    user.preferences = preferences
    user.location_district = body.district
    user.lang_pref = body.preferred_language
    if body.village_code is not None:
        user.village_code = body.village_code

    await db.commit()
    await db.refresh(user)

    return {
        "user_id": str(user.id),
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
