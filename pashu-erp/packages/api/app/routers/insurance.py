"""Livestock insurance policy and claims endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.insurance import InsuranceClaim, InsurancePolicy
from app.models.reference import InsurancePremium
from app.models.user import User
from app.schemas.insurance import (
    InsuranceClaimCreate,
    InsuranceClaimRead,
    InsurancePolicyListResponse,
    PremiumEstimate,
)

router = APIRouter(prefix="/v1/insurance", tags=["Insurance"])


@router.get("/policies", response_model=InsurancePolicyListResponse)
async def get_my_policies(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get insurance policies for the authenticated user's animals."""
    user_id = current_user.id

    animal_result = await db.execute(
        select(Animal.id).where(Animal.user_id == user_id, Animal.deleted_at.is_(None))
    )
    animal_ids = [row[0] for row in animal_result.all()]

    if not animal_ids:
        return {"data": [], "total": 0}

    count_result = await db.execute(
        select(func.count())
        .select_from(InsurancePolicy)
        .where(InsurancePolicy.animal_id.in_(animal_ids), InsurancePolicy.deleted_at.is_(None))
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(InsurancePolicy)
        .where(InsurancePolicy.animal_id.in_(animal_ids), InsurancePolicy.deleted_at.is_(None))
        .order_by(InsurancePolicy.valid_to.desc())
        .offset(offset)
        .limit(limit)
    )
    return {"data": result.scalars().all(), "total": total}


@router.get("/policies/{user_id}", response_model=InsurancePolicyListResponse)
async def get_user_policies(
    user_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all insurance policies for a user's animals (admin or self)."""
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Get user's animal IDs
    animal_result = await db.execute(
        select(Animal.id).where(Animal.user_id == user_id, Animal.deleted_at.is_(None))
    )
    animal_ids = [row[0] for row in animal_result.all()]

    if not animal_ids:
        return {"data": [], "total": 0}

    count_result = await db.execute(
        select(func.count())
        .select_from(InsurancePolicy)
        .where(InsurancePolicy.animal_id.in_(animal_ids), InsurancePolicy.deleted_at.is_(None))
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(InsurancePolicy)
        .where(InsurancePolicy.animal_id.in_(animal_ids), InsurancePolicy.deleted_at.is_(None))
        .order_by(InsurancePolicy.valid_to.desc())
        .offset(offset)
        .limit(limit)
    )
    return {"data": result.scalars().all(), "total": total}


@router.post("/claims", response_model=InsuranceClaimRead, status_code=status.HTTP_201_CREATED)
async def file_claim(
    body: InsuranceClaimCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """File an insurance claim against a policy."""
    # Verify policy exists
    policy_result = await db.execute(
        select(InsurancePolicy).where(
            InsurancePolicy.id == body.policy_id, InsurancePolicy.deleted_at.is_(None)
        )
    )
    policy = policy_result.scalar_one_or_none()
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Verify the animal belongs to the user
    animal_result = await db.execute(
        select(Animal).where(Animal.id == policy.animal_id, Animal.deleted_at.is_(None))
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Estimate insurance premium for an animal based on species, breed type, and age."""
    result = await db.execute(
        select(Animal).where(Animal.id == animal_id, Animal.deleted_at.is_(None))
    )
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")

    if str(animal.user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to estimate for this animal")

    species = animal.species.lower() if animal.species else "cattle"
    breed_type = animal.breed_type.lower() if animal.breed_type else "indigenous"

    # Look up insurance premium data from reference table
    premium_result = await db.execute(
        select(InsurancePremium).where(
            InsurancePremium.species == species,
            InsurancePremium.breed_type == breed_type,
        )
    )
    premium_row = premium_result.scalar_one_or_none()

    if premium_row is None:
        # Fallback: try species with cattle defaults
        fallback_result = await db.execute(
            select(InsurancePremium).where(
                InsurancePremium.species == "cattle",
                InsurancePremium.breed_type == "indigenous",
            )
        )
        premium_row = fallback_result.scalar_one_or_none()

    animal_value = int(premium_row.animal_value_inr) if premium_row else 40000
    premium_pct = float(premium_row.premium_pct) if premium_row else 3.5

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
