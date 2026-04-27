"""Advisory tips and guidance endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.advisory import AdvisoryTip
from app.models.user import User
from app.schemas.advisory import AdvisoryTipListResponse, AdvisoryTipRead

router = APIRouter(prefix="/v1/advisory", tags=["Advisory"])


@router.get("/tips", response_model=AdvisoryTipListResponse)
async def list_tips(
    species: str | None = Query(None, description="Filter by species"),
    category: str | None = Query(None, description="Filter by category"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List advisory tips with optional species and category filters."""
    base_filters = [
        AdvisoryTip.is_active == True,  # noqa: E712
        AdvisoryTip.deleted_at.is_(None),
    ]
    count_query = select(func.count()).select_from(AdvisoryTip).where(*base_filters)
    query = (
        select(AdvisoryTip)
        .where(*base_filters)
        .order_by(AdvisoryTip.priority.desc(), AdvisoryTip.published_at.desc())
    )

    if species:
        species_filter = AdvisoryTip.species_applicable.contains([species.lower()])
        count_query = count_query.where(species_filter)
        query = query.where(species_filter)

    if category:
        cat_filter = AdvisoryTip.category == category.lower()
        count_query = count_query.where(cat_filter)
        query = query.where(cat_filter)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    result = await db.execute(query.offset(offset).limit(limit))
    return {"data": result.scalars().all(), "total": total}


@router.get("/tips/{tip_id}", response_model=AdvisoryTipRead)
async def get_tip(
    tip_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get a specific advisory tip by ID."""
    result = await db.execute(
        select(AdvisoryTip).where(AdvisoryTip.id == tip_id, AdvisoryTip.deleted_at.is_(None))
    )
    tip = result.scalar_one_or_none()
    if tip is None:
        raise HTTPException(status_code=404, detail="Advisory tip not found")
    return tip
