"""Government schemes endpoints."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models.schemes import GovtScheme
from app.models.user import User

router = APIRouter(prefix="/v1/schemes", tags=["Government Schemes"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SchemeCreate(BaseModel):
    scheme_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=300)
    ministry: str | None = Field(None, max_length=200)
    description: str | None = None
    eligibility_criteria: str | None = None
    required_documents: list | dict | None = None
    max_subsidy_amount: float | None = None
    subsidy_percentage: float | None = None
    is_active: bool = True
    valid_from: date
    valid_to: date | None = None


class SchemeRead(BaseModel):
    id: UUID
    scheme_code: str
    name: str
    ministry: str | None = None
    description: str | None = None
    eligibility_criteria: str | None = None
    required_documents: list | dict | None = None
    max_subsidy_amount: float | None = None
    subsidy_percentage: float | None = None
    is_active: bool
    valid_from: date
    valid_to: date | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("", response_model=list[SchemeRead])
async def list_schemes(
    ministry: str | None = Query(None, description="Filter by ministry name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all government schemes."""
    stmt = select(GovtScheme)
    if ministry:
        stmt = stmt.where(GovtScheme.ministry.ilike(f"%{ministry}%"))
    stmt = stmt.order_by(GovtScheme.name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{scheme_id}", response_model=SchemeRead)
async def get_scheme(
    scheme_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scheme details by ID."""
    result = await db.execute(select(GovtScheme).where(GovtScheme.id == scheme_id))
    scheme = result.scalar_one_or_none()
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme


@router.post("", response_model=SchemeRead, status_code=status.HTTP_201_CREATED)
async def create_scheme(
    body: SchemeCreate,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a government scheme (admin only)."""
    scheme = GovtScheme(
        scheme_code=body.scheme_code,
        name=body.name,
        ministry=body.ministry,
        description=body.description,
        eligibility_criteria=body.eligibility_criteria,
        required_documents=body.required_documents,
        max_subsidy_amount=Decimal(str(body.max_subsidy_amount)) if body.max_subsidy_amount else None,
        subsidy_percentage=body.subsidy_percentage,
        is_active=body.is_active,
        valid_from=body.valid_from,
        valid_to=body.valid_to,
    )
    db.add(scheme)
    await db.commit()
    await db.refresh(scheme)
    return scheme
