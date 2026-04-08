"""Advisory tips and guidance endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.advisory import AdvisoryTip
from app.schemas.advisory import AdvisoryTipRead

router = APIRouter(prefix="/v1/advisory", tags=["Advisory"])


@router.get("/tips", response_model=list[AdvisoryTipRead])
async def list_tips(
    species: str | None = Query(None, description="Filter by species"),
    category: str | None = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
):
    """List advisory tips with optional species and category filters."""
    query = select(AdvisoryTip).where(
        AdvisoryTip.is_active == True  # noqa: E712
    ).order_by(AdvisoryTip.priority.desc(), AdvisoryTip.published_at.desc())

    if species:
        query = query.where(
            AdvisoryTip.species_applicable.contains([species.lower()])
        )

    if category:
        query = query.where(AdvisoryTip.category == category.lower())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/tips/{tip_id}", response_model=AdvisoryTipRead)
async def get_tip(tip_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific advisory tip by ID."""
    result = await db.execute(
        select(AdvisoryTip).where(AdvisoryTip.id == tip_id)
    )
    tip = result.scalar_one_or_none()
    if tip is None:
        raise HTTPException(status_code=404, detail="Advisory tip not found")
    return tip
