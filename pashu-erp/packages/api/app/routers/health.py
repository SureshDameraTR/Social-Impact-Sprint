"""Health events and vaccination endpoints."""

from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.health import HealthEvent, Vaccination
from app.models.user import User
from app.schemas.health import (
    HealthEventCreate,
    HealthEventRead,
    VaccinationCreate,
    VaccinationRead,
)
from app.services.disease_rules import evaluate_symptoms

router = APIRouter(prefix="/v1", tags=["Health"])


# ---------------------------------------------------------------------------
# Health Events
# ---------------------------------------------------------------------------

@router.post("/health/log", response_model=HealthEventRead, status_code=status.HTTP_201_CREATED)
async def log_health_event(
    body: HealthEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a health event for an animal and run the disease triage engine."""
    # Verify animal exists and belongs to user
    result = await db.execute(select(Animal).where(Animal.id == body.animal_id))
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    # Run disease triage
    triage = evaluate_symptoms(animal.species, body.symptoms)

    event = HealthEvent(
        animal_id=str(body.animal_id),
        event_type=body.event_type.value,
        description=body.description,
        symptoms=body.symptoms,
        ai_risk_score=triage["risk_score"],
        recommended_action=triage["recommended_action"],
        probable_diseases=[m["disease"] for m in triage["matches"]],
        recorded_by=str(current_user.id),
        event_date=body.event_date or datetime.now(timezone.utc),
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/health/history/{animal_id}", response_model=list[HealthEventRead])
async def get_health_history(
    animal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get health event history for an animal."""
    # Verify ownership
    animal_result = await db.execute(select(Animal).where(Animal.id == animal_id))
    animal = animal_result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    result = await db.execute(
        select(HealthEvent)
        .where(HealthEvent.animal_id == animal_id)
        .order_by(HealthEvent.event_date.desc())
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Vaccinations
# ---------------------------------------------------------------------------

@router.post("/vaccinations", response_model=VaccinationRead, status_code=status.HTTP_201_CREATED)
async def record_vaccination(
    body: VaccinationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a vaccination for an animal."""
    # Verify animal exists and belongs to user
    result = await db.execute(select(Animal).where(Animal.id == body.animal_id))
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    vaccination = Vaccination(
        animal_id=str(body.animal_id),
        vaccine_name=body.vaccine_name,
        administered_on=body.administered_on,
        next_due=body.next_due,
        batch_number=body.batch_number,
        recorded_by=str(current_user.id),
    )
    db.add(vaccination)
    await db.commit()
    await db.refresh(vaccination)
    return vaccination


@router.get("/vaccinations/{animal_id}", response_model=list[VaccinationRead])
async def get_vaccinations(
    animal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get vaccination records for an animal."""
    animal_result = await db.execute(select(Animal).where(Animal.id == animal_id))
    animal = animal_result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    result = await db.execute(
        select(Vaccination)
        .where(Vaccination.animal_id == animal_id)
        .order_by(Vaccination.administered_on.desc())
    )
    return result.scalars().all()


@router.get("/vaccinations/due", response_model=list[VaccinationRead])
async def get_due_vaccinations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming vaccinations for all of the current user's animals."""
    today = date.today()
    # Get all animal IDs for the current user
    animal_result = await db.execute(
        select(Animal.id).where(Animal.user_id == current_user.id)
    )
    animal_ids = [row[0] for row in animal_result.all()]

    if not animal_ids:
        return []

    result = await db.execute(
        select(Vaccination)
        .where(
            Vaccination.animal_id.in_(animal_ids),
            Vaccination.next_due != None,  # noqa: E711
            Vaccination.next_due >= today,
        )
        .order_by(Vaccination.next_due.asc())
    )
    return result.scalars().all()
