"""Veterinary consultation endpoints."""

from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db

# Dashboard configuration
RISK_SCORE_THRESHOLD: float = 0.5
ALERT_WINDOW_DAYS: int = 7

from app.middleware.auth import get_current_user, require_vet_or_admin
from app.models.alerts import CommunityAlert
from app.models.animal import Animal
from app.models.health import HealthEvent
from app.models.user import User
from app.models.vet import VetConsultation, ConsultationStatus, ConsultationPriority

router = APIRouter(prefix="/v1/vet", tags=["vet"])


# ---------------------------------------------------------------------------
# Request bodies (Pydantic)
# ---------------------------------------------------------------------------

class DiagnoseBody(BaseModel):
    diagnosis: str
    prescription: Optional[str] = None
    follow_up_date: Optional[date] = None


class VideoLinkBody(BaseModel):
    video_call_url: str


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _district_for_user(user: User) -> str | None:
    """Return the district to scope queries, or None for admins (no scoping)."""
    if user.role == "admin":
        return None
    return user.location_district


def _serialize_case(c: "VetConsultation") -> dict:
    """Convert a VetConsultation ORM object to a JSON-safe dict."""
    animal = None
    if c.animal:
        owner = None
        if c.animal.owner:
            o = c.animal.owner
            owner = {"id": str(o.id), "name": o.name, "phone": o.phone, "village_code": o.village_code, "location_district": o.location_district}
        animal = {"id": str(c.animal.id), "species": c.animal.species, "name": c.animal.name, "breed": c.animal.breed, "owner": owner}
    return {
        "id": str(c.id),
        "animal_id": str(c.animal_id),
        "farmer_id": str(c.farmer_id),
        "vet_id": str(c.vet_id) if c.vet_id else None,
        "status": c.status,
        "priority": c.priority,
        "channel": c.channel,
        "farmer_notes": c.farmer_notes,
        "photo_urls": c.photo_urls,
        "diagnosis": c.diagnosis,
        "prescription": c.prescription,
        "follow_up_date": str(c.follow_up_date) if c.follow_up_date else None,
        "video_call_url": c.video_call_url,
        "district": c.district,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        "animal": animal,
        "farmer": {"id": str(c.farmer_id), "name": c.animal.owner.name if c.animal and c.animal.owner else None},
    }


# ---------------------------------------------------------------------------
# Case list & detail
# ---------------------------------------------------------------------------

@router.get("/cases")
async def list_cases(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """List vet consultation cases in the vet's district."""
    base = select(VetConsultation)

    # District scoping for non-admin users
    district = _district_for_user(current_user)
    if district is not None:
        base = base.where(VetConsultation.district == district)

    if status_filter is not None:
        base = base.where(VetConsultation.status == status_filter)
    if priority is not None:
        base = base.where(VetConsultation.priority == priority)

    # Priority ordering: emergency first, then descending created_at
    priority_order = case(
        (VetConsultation.priority == ConsultationPriority.emergency.value, 0),
        (VetConsultation.priority == ConsultationPriority.urgent.value, 1),
        (VetConsultation.priority == ConsultationPriority.routine.value, 2),
        else_=3,
    )

    result = await db.execute(
        base.options(
            selectinload(VetConsultation.animal).selectinload(Animal.owner),
        )
        .order_by(priority_order, VetConsultation.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    cases = result.scalars().all()

    return {"data": [_serialize_case(c) for c in cases], "skip": skip, "limit": limit}


@router.get("/cases/{case_id}")
async def get_case(
    case_id: UUID,
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get full case detail with animal health events and vaccinations."""
    result = await db.execute(
        select(VetConsultation)
        .where(VetConsultation.id == case_id)
        .options(
            selectinload(VetConsultation.animal)
            .selectinload(Animal.owner),
            selectinload(VetConsultation.animal)
            .selectinload(Animal.health_events),
            selectinload(VetConsultation.animal)
            .selectinload(Animal.vaccinations),
        )
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # District check for vets
    district = _district_for_user(current_user)
    if district is not None and case.district != district:
        raise HTTPException(status_code=403, detail="Case not in your district")

    return _serialize_case(case)


# ---------------------------------------------------------------------------
# Case actions
# ---------------------------------------------------------------------------

@router.patch("/cases/{case_id}/claim")
async def claim_case(
    case_id: UUID,
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Claim an unassigned case."""
    result = await db.execute(
        select(VetConsultation).where(VetConsultation.id == case_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # District check for vets
    district = _district_for_user(current_user)
    if district is not None and case.district != district:
        raise HTTPException(status_code=403, detail="Case not in your district")

    if case.vet_id is not None:
        raise HTTPException(status_code=409, detail="Case already claimed")

    case.vet_id = str(current_user.id)
    case.status = ConsultationStatus.in_review.value
    await db.commit()
    await db.refresh(case)
    return _serialize_case(case)


@router.patch("/cases/{case_id}/diagnose")
async def diagnose_case(
    case_id: UUID,
    body: DiagnoseBody,
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Add diagnosis to a claimed case."""
    result = await db.execute(
        select(VetConsultation).where(VetConsultation.id == case_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # Must be claimed first; vet must own the case (admin can override)
    if case.vet_id is None:
        raise HTTPException(status_code=400, detail="Case must be claimed first")
    if current_user.role != "admin" and str(case.vet_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your case")

    case.diagnosis = body.diagnosis
    case.prescription = body.prescription
    case.follow_up_date = body.follow_up_date
    case.status = ConsultationStatus.diagnosed.value
    await db.commit()
    await db.refresh(case)
    return _serialize_case(case)


@router.patch("/cases/{case_id}/video-link")
async def set_video_link(
    case_id: UUID,
    body: VideoLinkBody,
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Set the video call URL for a claimed case."""
    result = await db.execute(
        select(VetConsultation).where(VetConsultation.id == case_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.vet_id is None:
        raise HTTPException(status_code=400, detail="Case must be claimed first")
    if current_user.role != "admin" and str(case.vet_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your case")

    case.video_call_url = body.video_call_url
    await db.commit()
    await db.refresh(case)
    return _serialize_case(case)


@router.patch("/cases/{case_id}/close")
async def close_case(
    case_id: UUID,
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Close a case."""
    result = await db.execute(
        select(VetConsultation).where(VetConsultation.id == case_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    # District check for vets
    district = _district_for_user(current_user)
    if district is not None and case.district != district:
        raise HTTPException(status_code=403, detail="Case not in your district")

    case.status = ConsultationStatus.closed.value
    await db.commit()
    await db.refresh(case)
    return _serialize_case(case)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard/stats")
async def vet_dashboard_stats(
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Vet dashboard statistics: pending cases, diagnosed today, district animals, active alerts."""
    district = _district_for_user(current_user)

    # Pending cases in district
    pending_q = (
        select(func.count())
        .select_from(VetConsultation)
        .where(VetConsultation.status == ConsultationStatus.pending.value)
    )
    if district is not None:
        pending_q = pending_q.where(VetConsultation.district == district)
    pending_result = await db.execute(pending_q)
    pending_cases = pending_result.scalar() or 0

    # Diagnosed today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    diagnosed_q = (
        select(func.count())
        .select_from(VetConsultation)
        .where(
            VetConsultation.status == ConsultationStatus.diagnosed.value,
            VetConsultation.updated_at >= today_start,
        )
    )
    if district is not None:
        diagnosed_q = diagnosed_q.where(VetConsultation.district == district)
    diagnosed_result = await db.execute(diagnosed_q)
    diagnosed_today = diagnosed_result.scalar() or 0

    # District animals — join Animal -> User to scope by district
    animals_q = select(func.count()).select_from(Animal)
    if district is not None:
        animals_q = animals_q.join(User, Animal.user_id == User.id).where(
            User.location_district == district
        )
    animals_result = await db.execute(animals_q)
    district_animals = animals_result.scalar() or 0

    # Active alerts — community alerts in district within the last week
    week_ago = datetime.now(timezone.utc) - timedelta(days=ALERT_WINDOW_DAYS)
    alerts_q = (
        select(func.count())
        .select_from(CommunityAlert)
        .where(CommunityAlert.created_at >= week_ago)
    )
    if district is not None:
        # Join through reporter to get district
        alerts_q = alerts_q.join(User, CommunityAlert.reported_by == User.id).where(
            User.location_district == district
        )
    alerts_result = await db.execute(alerts_q)
    active_alerts = alerts_result.scalar() or 0

    return {
        "pending_cases": pending_cases,
        "diagnosed_today": diagnosed_today,
        "district_animals": district_animals,
        "active_alerts": active_alerts,
    }


@router.get("/dashboard/alerts")
async def vet_dashboard_alerts(
    current_user: User = Depends(require_vet_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """District health alerts: community alerts + high-risk health events."""
    district = _district_for_user(current_user)
    week_ago = datetime.now(timezone.utc) - timedelta(days=ALERT_WINDOW_DAYS)

    # Community alerts in district
    alerts_q = (
        select(CommunityAlert)
        .where(
            CommunityAlert.created_at >= week_ago,
            CommunityAlert.expires_at > func.now(),
        )
    )
    if district is not None:
        alerts_q = alerts_q.join(User, CommunityAlert.reported_by == User.id).where(
            User.location_district == district
        )
    alerts_q = alerts_q.order_by(CommunityAlert.created_at.desc()).limit(50)
    alerts_result = await db.execute(alerts_q)
    community_alerts = alerts_result.scalars().all()

    # High-risk health events in district
    events_q = (
        select(HealthEvent)
        .where(
            HealthEvent.event_date >= week_ago,
            HealthEvent.ai_risk_score > RISK_SCORE_THRESHOLD,
        )
        .options(
            selectinload(HealthEvent.animal).selectinload(Animal.owner),
        )
    )
    if district is not None:
        events_q = events_q.join(Animal, HealthEvent.animal_id == Animal.id).join(
            User, Animal.user_id == User.id
        ).where(User.location_district == district)
    events_q = events_q.order_by(HealthEvent.ai_risk_score.desc()).limit(50)
    events_result = await db.execute(events_q)
    health_events = events_result.scalars().all()

    return {
        "community_alerts": community_alerts,
        "health_events": health_events,
    }


# ---------------------------------------------------------------------------
# Farmer-facing
# ---------------------------------------------------------------------------

@router.get("/my-cases")
async def my_cases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Farmer's own consultation cases."""
    result = await db.execute(
        select(VetConsultation)
        .where(VetConsultation.farmer_id == str(current_user.id))
        .order_by(VetConsultation.created_at.desc())
    )
    cases = result.scalars().all()

    return {"data": cases}
