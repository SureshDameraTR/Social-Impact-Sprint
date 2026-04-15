"""SHG (Self Help Group) CRUD + Panchsutra compliance endpoints."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.shg import SHGGroup
from app.models.user import User

router = APIRouter(prefix="/v1/shg", tags=["SHG Groups"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SHGCreate(BaseModel):
    name: str = Field(..., max_length=200)
    registration_number: str | None = Field(None, max_length=50)
    district: str | None = Field(None, max_length=100)
    village_code: str | None = Field(None, max_length=20)
    member_count: int = 0
    women_only: bool = True
    formation_date: date | None = None
    total_savings: Decimal = Field(default=Decimal("0"), max_digits=10, decimal_places=2)
    grading: str = "ungraded"
    panchsutra_compliance: dict | None = None


class SHGUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    registration_number: str | None = Field(None, max_length=50)
    district: str | None = None
    village_code: str | None = None
    member_count: int | None = None
    women_only: bool | None = None
    total_savings: Decimal | None = Field(None, max_digits=10, decimal_places=2)
    grading: str | None = None
    panchsutra_compliance: dict | None = None


class SHGRead(BaseModel):
    id: UUID
    name: str
    registration_number: str | None = None
    district: str | None = None
    village_code: str | None = None
    admin_user_id: UUID
    member_count: int
    women_only: bool
    formation_date: date | None = None
    total_savings: Decimal = Field(..., max_digits=10, decimal_places=2)
    grading: str
    panchsutra_compliance: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("", response_model=SHGRead, status_code=status.HTTP_201_CREATED)
async def create_shg(
    body: SHGCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new SHG group."""
    group = SHGGroup(
        name=body.name,
        registration_number=body.registration_number,
        district=body.district,
        village_code=body.village_code,
        admin_user_id=current_user.id,
        member_count=body.member_count,
        women_only=body.women_only,
        formation_date=body.formation_date,
        total_savings=body.total_savings,
        grading=body.grading,
        panchsutra_compliance=body.panchsutra_compliance,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.get("")
async def list_shg(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List SHG groups the current user administers."""
    base_filter = [SHGGroup.admin_user_id == current_user.id, SHGGroup.deleted_at.is_(None)]

    count_result = await db.execute(
        select(func.count()).select_from(SHGGroup).where(*base_filter)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(SHGGroup)
        .where(*base_filter)
        .order_by(SHGGroup.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return {"data": result.scalars().all(), "total": total}


@router.get("/{shg_id}", response_model=SHGRead)
async def get_shg(
    shg_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get an SHG group by ID."""
    result = await db.execute(select(SHGGroup).where(SHGGroup.id == shg_id, SHGGroup.deleted_at.is_(None)))
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="SHG group not found")
    return group


@router.patch("/{shg_id}", response_model=SHGRead)
async def update_shg(
    shg_id: UUID,
    body: SHGUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an SHG group."""
    result = await db.execute(select(SHGGroup).where(SHGGroup.id == shg_id, SHGGroup.deleted_at.is_(None)))
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="SHG group not found")
    if str(group.admin_user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not the group admin")

    update_data = body.model_dump(exclude_unset=True)
    # total_savings is already Decimal from Pydantic schema — no conversion needed
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
    return group


@router.get("/{shg_id}/compliance")
async def get_panchsutra_compliance(
    shg_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate and return Panchsutra compliance score for an SHG group.

    Panchsutra (5 principles):
    1. Regular meetings (weekly)
    2. Regular savings
    3. Regular internal lending
    4. Regular repayment
    5. Up-to-date bookkeeping
    """
    result = await db.execute(select(SHGGroup).where(SHGGroup.id == shg_id, SHGGroup.deleted_at.is_(None)))
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="SHG group not found")

    compliance = group.panchsutra_compliance or {}

    # Score each principle (0 or 1)
    principles = {
        "regular_meetings": compliance.get("regular_meetings", False),
        "regular_savings": compliance.get("regular_savings", False),
        "regular_internal_lending": compliance.get("regular_internal_lending", False),
        "regular_repayment": compliance.get("regular_repayment", False),
        "uptodate_bookkeeping": compliance.get("uptodate_bookkeeping", False),
    }

    score = sum(1 for v in principles.values() if v)
    total = len(principles)

    return {
        "shg_id": str(shg_id),
        "name": group.name,
        "principles": principles,
        "score": score,
        "total": total,
        "percentage": round((score / total) * 100, 1),
        "grading": "A" if score >= 4 else ("B" if score >= 3 else ("C" if score >= 2 else "ungraded")),
    }
