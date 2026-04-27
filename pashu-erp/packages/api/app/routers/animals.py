"""Animal CRUD endpoints."""

import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.user import User
from app.schemas.animals import AnimalCreate, AnimalListResponse, AnimalRead, AnimalUpdate

router = APIRouter(prefix="/v1/animals", tags=["Animals"])


@router.post("", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
async def create_animal(
    body: AnimalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register a new animal for the authenticated farmer."""
    for attempt in range(settings.max_id_retries):
        # Auto-generate pashu_aadhaar_id if not provided
        pashu_id = body.pashu_aadhaar_id
        if not pashu_id:
            pashu_id = f"{secrets.randbelow(900000000000) + 100000000000}"

        animal = Animal(
            user_id=current_user.id,
            pashu_aadhaar_id=pashu_id,
            species=body.species.value,
            breed=body.breed,
            breed_type=body.breed_type.value,
            tag_id=body.tag_id,
            name=body.name,
            date_of_birth=body.date_of_birth,
            sex=body.sex.value,
            lactation_number=body.lactation_number,
            body_condition_score=body.body_condition_score,
            is_insured=body.is_insured,
            metadata_=body.metadata,
        )
        try:
            db.add(animal)
            await db.commit()
            await db.refresh(animal)
            return animal
        except IntegrityError:
            await db.rollback()
            # If the caller supplied a specific ID, don't retry with a random one
            if body.pashu_aadhaar_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="pashu_aadhaar_id already exists",
                ) from None
            # Auto-generated ID collided — retry with a new random value
            if attempt == settings.max_id_retries - 1:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Could not generate a unique Pashu Aadhaar ID; please retry",
                ) from None


@router.get("", response_model=AnimalListResponse)
async def list_animals(
    species: str | None = Query(
        None, description="Filter by species (cattle, goat, sheep, poultry)"
    ),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all animals owned by the authenticated user with pagination."""
    base = select(Animal).where(Animal.deleted_at.is_(None))
    if current_user.role == "admin":
        pass  # no filter — admin sees all
    elif current_user.role == "vet":
        # Vet sees all animals in their district
        base = base.join(User, Animal.user_id == User.id).where(
            User.location_district == current_user.location_district
        )
    else:
        # Farmer: own animals only
        base = base.where(Animal.user_id == current_user.id)
    if species:
        base = base.where(Animal.species == species)

    # Count
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    # Data
    stmt = base.order_by(Animal.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    data = result.scalars().all()

    return {"data": data, "total": total, "limit": limit, "offset": offset}


async def _can_access_animal(user: User, animal: Animal, db: AsyncSession) -> bool:
    """Check if a user can view/manage an animal.

    Admins can access any animal; vets can access animals whose owner is in
    the same district; farmers can only access their own.
    """
    if user.role == "admin":
        return True
    if user.role == "vet":
        owner = await db.get(User, animal.user_id)
        if owner and owner.village_code and user.village_code:
            return owner.village_code[:2] == user.village_code[:2]
        return True  # fallback if village_code not set
    return str(animal.user_id) == str(user.id)


def _can_modify_animal(user: User, animal: Animal) -> bool:
    """Check if a user can modify an animal. Only owner or admin."""
    if user.role == "admin":
        return True
    return str(animal.user_id) == str(user.id)


@router.get("/{animal_id}", response_model=AnimalRead)
async def get_animal(
    animal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single animal by ID (admin/vet can view any, farmer: own only)."""
    result = await db.execute(
        select(Animal).where(Animal.id == animal_id, Animal.deleted_at.is_(None))
    )
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if not await _can_access_animal(current_user, animal, db):
        raise HTTPException(status_code=403, detail="Not your animal")
    return animal


@router.patch("/{animal_id}", response_model=AnimalRead)
async def update_animal(
    animal_id: UUID,
    body: AnimalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an animal's details."""
    result = await db.execute(
        select(Animal).where(Animal.id == animal_id, Animal.deleted_at.is_(None))
    )
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if not _can_modify_animal(current_user, animal):
        raise HTTPException(status_code=403, detail="Not your animal")

    update_data = body.model_dump(exclude_unset=True)
    # Map schema field 'metadata' to model column 'metadata_'
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    for field, value in update_data.items():
        # Convert enums to their string values
        if hasattr(value, "value"):
            value = value.value
        setattr(animal, field, value)

    await db.commit()
    await db.refresh(animal)
    return animal


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    animal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an animal record."""
    result = await db.execute(
        select(Animal).where(Animal.id == animal_id, Animal.deleted_at.is_(None))
    )
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if not _can_modify_animal(current_user, animal):
        raise HTTPException(status_code=403, detail="Not your animal")

    from app.models.health import HealthEvent, Vaccination
    from app.models.milk import YieldLog

    now = datetime.now(timezone.utc)
    animal.deleted_at = now

    # Cascade soft-delete to related records
    await db.execute(
        update(HealthEvent)
        .where(HealthEvent.animal_id == animal_id, HealthEvent.deleted_at.is_(None))
        .values(deleted_at=now)
    )
    await db.execute(
        update(YieldLog)
        .where(YieldLog.animal_id == animal_id, YieldLog.deleted_at.is_(None))
        .values(deleted_at=now)
    )
    await db.execute(
        update(Vaccination)
        .where(Vaccination.animal_id == animal_id, Vaccination.deleted_at.is_(None))
        .values(deleted_at=now)
    )

    await db.commit()
