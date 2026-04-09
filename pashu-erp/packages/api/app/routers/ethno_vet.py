"""Ethno-veterinary traditional remedy endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ethno_vet import TraditionalRemedy
from app.schemas.ethno_vet import TraditionalRemedyRead

router = APIRouter(prefix="/v1/ethno-vet", tags=["Ethno-Veterinary"])


@router.get("/remedies", response_model=list[TraditionalRemedyRead])
async def list_remedies(
    species: str | None = Query(None, description="Filter by species"),
    condition: str | None = Query(None, description="Filter by condition treated"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List traditional remedies with optional filters."""
    query = select(TraditionalRemedy).order_by(TraditionalRemedy.name_en)

    if species:
        # Filter where species appears in dosage_by_species JSONB keys
        query = query.where(
            TraditionalRemedy.dosage_by_species.has_key(species.lower())
        )

    if condition:
        # Filter where condition appears in conditions_treated JSONB array
        query = query.where(
            TraditionalRemedy.conditions_treated.contains([condition.lower()])
        )

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/remedies/{remedy_id}", response_model=TraditionalRemedyRead)
async def get_remedy(remedy_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a traditional remedy."""
    result = await db.execute(
        select(TraditionalRemedy).where(TraditionalRemedy.id == remedy_id)
    )
    remedy = result.scalar_one_or_none()
    if remedy is None:
        raise HTTPException(status_code=404, detail="Remedy not found")
    return remedy


@router.get("/search", response_model=list[TraditionalRemedyRead])
async def search_remedies(
    q: str = Query(..., min_length=2, description="Search keyword"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search remedies by keyword across name, ingredient, and conditions."""
    pattern = f"%{q.lower()}%"
    result = await db.execute(
        select(TraditionalRemedy).where(
            or_(
                TraditionalRemedy.name_en.ilike(pattern),
                TraditionalRemedy.name_kn.ilike(pattern),
                TraditionalRemedy.plant_ingredient.ilike(pattern),
                TraditionalRemedy.preparation_method.ilike(pattern),
            )
        ).offset(skip).limit(limit)
    )
    return result.scalars().all()
