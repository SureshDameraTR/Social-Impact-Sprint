"""Feed ingredient and ration calculation endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.feed import FeedIngredient
from app.models.user import User
from app.schemas.feed import FeedIngredientListResponse, RationRequest, RationResult
from app.services.feed_calculator import calculate_ration

router = APIRouter(prefix="/v1/feed", tags=["Feed & Nutrition"])


@router.get("/ingredients", response_model=FeedIngredientListResponse)
async def list_ingredients(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all feed ingredients."""
    count_result = await db.execute(
        select(func.count()).select_from(FeedIngredient).where(FeedIngredient.deleted_at.is_(None))
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(FeedIngredient)
        .where(FeedIngredient.deleted_at.is_(None))
        .order_by(FeedIngredient.category, FeedIngredient.name_en)
        .offset(offset)
        .limit(limit)
    )
    return {"data": result.scalars().all(), "total": total}


@router.post("/calculate-ration", response_model=RationResult)
async def calculate_balanced_ration(
    body: RationRequest, current_user: User = Depends(get_current_user)
):
    """Calculate a balanced daily ration based on NDDB feeding standards."""
    return calculate_ration(
        species=body.species,
        weight_kg=body.weight_kg,
        lactation_stage=body.lactation_stage.value if body.lactation_stage else None,
        available_ingredients=[str(i) for i in body.available_ingredients],
    )
