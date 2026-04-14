"""Health events endpoints.

Note: Vaccination CRUD routes live in routers/vaccination.py to avoid
duplication.  This module only handles health-event logging and history.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db

# Admin dashboard configuration (previously in constants.py)
RISK_SCORE_THRESHOLD: float = 0.5
ALERT_WINDOW_DAYS: int = 7
from app.middleware.auth import get_current_user, require_admin
from app.models.animal import Animal
from app.models.health import HealthEvent
from app.models.user import User
from app.models.vet import VetConsultation
from app.schemas.health import (
    HealthEventCreate,
    HealthEventRead,
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

    # Auto-create VetConsultation when symptoms are present
    if body.symptoms:
        risk_score = triage["risk_score"]
        if risk_score > 0.8:
            priority = "emergency"
        elif risk_score > 0.5:
            priority = "urgent"
        else:
            priority = "routine"

        channel = "photo" if body.photo_urls else "referral"

        # Resolve district from animal owner
        farmer = await db.get(User, animal.user_id)
        district = (
            (farmer.location_district if farmer else None)
            or current_user.location_district
            or "unknown"
        )

        consultation = VetConsultation(
            animal_id=str(animal.id),
            farmer_id=str(current_user.id),
            status="pending",
            priority=priority,
            channel=channel,
            farmer_notes=body.description,
            photo_urls=body.photo_urls,
            district=district,
        )
        db.add(consultation)
        await db.commit()

    return event


@router.get("/health/history/{animal_id}")
async def get_health_history(
    animal_id: UUID,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get health event history for an animal with pagination."""
    # Verify ownership
    animal_result = await db.execute(select(Animal).where(Animal.id == animal_id))
    animal = animal_result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    # Count
    count_result = await db.execute(
        select(func.count()).select_from(HealthEvent).where(HealthEvent.animal_id == animal_id)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(HealthEvent)
        .where(HealthEvent.animal_id == animal_id)
        .order_by(HealthEvent.event_date.desc())
        .offset(offset)
        .limit(limit)
    )
    data = result.scalars().all()

    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/health")
async def list_health_events(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List recent health events (admin: all, farmer: own animals only)."""
    week_ago = datetime.now(timezone.utc) - timedelta(days=ALERT_WINDOW_DAYS)
    base = select(HealthEvent).where(HealthEvent.event_date >= week_ago)
    if current_user.role == "admin":
        pass  # no filter — admin sees all
    elif current_user.role == "vet":
        # Vet sees all health events in their district
        base = base.join(Animal, HealthEvent.animal_id == Animal.id).join(
            User, Animal.user_id == User.id
        ).where(User.location_district == current_user.location_district)
    else:
        # Farmer: own animals only
        animal_ids_q = select(Animal.id).where(Animal.user_id == current_user.id)
        base = base.where(HealthEvent.animal_id.in_(animal_ids_q))

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(HealthEvent.event_date.desc()).offset(offset).limit(limit)
    )
    data = result.scalars().all()
    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/health/alerts/map")
async def get_health_alerts_map(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Health events with coordinates for GIS map display."""
    week_ago = datetime.now(timezone.utc) - timedelta(days=ALERT_WINDOW_DAYS)

    result = await db.execute(
        select(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > RISK_SCORE_THRESHOLD,
        )
        .options(
            selectinload(HealthEvent.animal).selectinload(Animal.owner),
        )
        .order_by(HealthEvent.ai_risk_score.desc())
        .limit(200)
    )
    events = result.scalars().all()

    markers = []
    for event in events:
        animal = event.animal
        if animal is None:
            continue
        owner = animal.owner
        markers.append({
            "event_id": str(event.id),
            "animal_id": str(event.animal_id),
            "species": animal.species if animal else None,
            "risk_score": event.ai_risk_score,
            "probable_diseases": event.probable_diseases,
            "district": owner.location_district if owner else None,
            "village_code": owner.village_code if owner else None,
            "event_date": event.event_date.isoformat(),
        })

    return {"alert_count": len(markers), "markers": markers}
