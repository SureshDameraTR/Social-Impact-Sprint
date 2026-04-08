"""Livestock insurance policy and claims endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.insurance import InsuranceClaim, InsurancePolicy
from app.models.user import User
from app.schemas.insurance import (
    InsuranceClaimCreate,
    InsuranceClaimRead,
    InsurancePolicyRead,
    PremiumEstimate,
)

router = APIRouter(prefix="/v1/insurance", tags=["Insurance"])

# Premium estimation rates (% of animal value)
PREMIUM_RATES = {
    "cattle": {"indigenous": 3.0, "crossbreed": 3.5, "exotic": 4.0},
    "goat": {"indigenous": 3.5, "crossbreed": 4.0, "exotic": 4.5},
    "sheep": {"indigenous": 3.0, "crossbreed": 3.5, "exotic": 4.0},
    "poultry": {"indigenous": 5.0, "crossbreed": 5.0, "exotic": 5.0},
}

# Approximate animal values for premium estimation
ANIMAL_VALUES = {
    "cattle": {"indigenous": 40000, "crossbreed": 60000, "exotic": 80000},
    "goat": {"indigenous": 8000, "crossbreed": 12000, "exotic": 15000},
    "sheep": {"indigenous": 7000, "crossbreed": 10000, "exotic": 12000},
    "poultry": {"indigenous": 300, "crossbreed": 500, "exotic": 800},
}


@router.get("/policies/{user_id}", response_model=list[InsurancePolicyRead])
async def get_user_policies(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all insurance policies for a user's animals."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Get user's animal IDs
    animal_result = await db.execute(
        select(Animal.id).where(Animal.user_id == user_id)
    )
    animal_ids = [row[0] for row in animal_result.all()]

    if not animal_ids:
        return []

    result = await db.execute(
        select(InsurancePolicy)
        .where(InsurancePolicy.animal_id.in_(animal_ids))
        .order_by(InsurancePolicy.valid_to.desc())
    )
    return result.scalars().all()


@router.post("/claims", response_model=InsuranceClaimRead, status_code=status.HTTP_201_CREATED)
async def file_claim(
    body: InsuranceClaimCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """File an insurance claim against a policy."""
    # Verify policy exists
    policy_result = await db.execute(
        select(InsurancePolicy).where(InsurancePolicy.id == body.policy_id)
    )
    policy = policy_result.scalar_one_or_none()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Verify the animal belongs to the user
    animal_result = await db.execute(
        select(Animal).where(Animal.id == policy.animal_id)
    )
    animal = animal_result.scalar_one_or_none()
    if animal is None or str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to file claim on this policy")

    claim = InsuranceClaim(
        policy_id=str(body.policy_id),
        claim_type=body.claim_type,
        description=body.description,
        photo_urls=body.photo_urls,
        status="filed",
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    return claim


@router.get("/premium-estimate/{animal_id}", response_model=PremiumEstimate)
async def estimate_premium(
    animal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Estimate insurance premium for an animal based on species, breed type, and age."""
    result = await db.execute(select(Animal).where(Animal.id == animal_id))
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    species = animal.species.lower() if animal.species else "cattle"
    breed_type = animal.breed_type.lower() if animal.breed_type else "indigenous"

    animal_value = ANIMAL_VALUES.get(species, ANIMAL_VALUES["cattle"]).get(breed_type, 40000)
    premium_pct = PREMIUM_RATES.get(species, PREMIUM_RATES["cattle"]).get(breed_type, 3.5)

    premium = animal_value * premium_pct / 100
    # Government subsidizes 50% of premium for BPL farmers
    notes = (
        f"Premium is {premium_pct}% of estimated animal value (INR {animal_value}). "
        f"Government subsidy of up to 50% available under LISS/RGBKMY for eligible farmers."
    )

    return PremiumEstimate(
        animal_id=animal_id,
        species=species,
        breed=animal.breed or "Unknown",
        estimated_premium=round(premium, 2),
        coverage_amount=float(animal_value),
        provider="National Insurance / United India Insurance",
        notes=notes,
    )
