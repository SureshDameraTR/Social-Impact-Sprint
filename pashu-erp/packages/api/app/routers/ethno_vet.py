"""Ethno-veterinary traditional remedy endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.ethno_vet import TraditionalRemedy
from app.models.user import User
from app.schemas.ethno_vet import TraditionalRemedyRead

router = APIRouter(prefix="/v1/ethno-vet", tags=["Ethno-Veterinary"])


@router.get("/remedies")
async def list_remedies(
    species: str | None = Query(None, description="Filter by species"),
    condition: str | None = Query(None, description="Filter by condition treated"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List traditional remedies with optional filters."""
    count_query = (
        select(func.count())
        .select_from(TraditionalRemedy)
        .where(TraditionalRemedy.deleted_at.is_(None))
    )
    query = (
        select(TraditionalRemedy)
        .where(TraditionalRemedy.deleted_at.is_(None))
        .order_by(TraditionalRemedy.name_en)
    )

    if species:
        # Filter where species appears in dosage_by_species JSONB keys
        species_filter = TraditionalRemedy.dosage_by_species.has_key(species.lower())
        count_query = count_query.where(species_filter)
        query = query.where(species_filter)

    if condition:
        # Filter where condition appears in conditions_treated JSONB array
        condition_filter = TraditionalRemedy.conditions_treated.contains([condition.lower()])
        count_query = count_query.where(condition_filter)
        query = query.where(condition_filter)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    result = await db.execute(query.offset(skip).limit(limit))
    return {"data": result.scalars().all(), "total": total}


@router.get("/remedies/{remedy_id}", response_model=TraditionalRemedyRead)
async def get_remedy(remedy_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get detailed information about a traditional remedy."""
    result = await db.execute(
        select(TraditionalRemedy).where(TraditionalRemedy.id == remedy_id, TraditionalRemedy.deleted_at.is_(None))
    )
    remedy = result.scalar_one_or_none()
    if remedy is None:
        raise HTTPException(status_code=404, detail="Remedy not found")
    return remedy


@router.get("/search")
async def search_remedies(
    q: str = Query(..., min_length=2, description="Search keyword"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search remedies by keyword across name, ingredient, and conditions."""
    escaped = q.replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{escaped.lower()}%"
    search_filter = [
        TraditionalRemedy.deleted_at.is_(None),
        or_(
            TraditionalRemedy.name_en.ilike(pattern),
            TraditionalRemedy.name_kn.ilike(pattern),
            TraditionalRemedy.plant_ingredient.ilike(pattern),
            TraditionalRemedy.preparation_method.ilike(pattern),
        ),
    ]

    count_result = await db.execute(
        select(func.count()).select_from(TraditionalRemedy).where(*search_filter)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(TraditionalRemedy).where(*search_filter).offset(skip).limit(limit)
    )
    return {"data": result.scalars().all(), "total": total}
