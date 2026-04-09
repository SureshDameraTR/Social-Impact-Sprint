"""Feed ingredient and ration calculation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.feed import FeedIngredient
from app.schemas.feed import FeedIngredientRead, RationRequest, RationResult
from app.services.feed_calculator import calculate_ration

router = APIRouter(prefix="/v1/feed", tags=["Feed & Nutrition"])


@router.get("/ingredients", response_model=list[FeedIngredientRead])
async def list_ingredients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all feed ingredients."""
    result = await db.execute(
        select(FeedIngredient)
        .order_by(FeedIngredient.category, FeedIngredient.name_en)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/calculate-ration", response_model=RationResult)
async def calculate_balanced_ration(body: RationRequest):
    """Calculate a balanced daily ration based on NDDB feeding standards."""
    return calculate_ration(
        species=body.species,
        weight_kg=body.weight_kg,
        lactation_stage=body.lactation_stage.value if body.lactation_stage else None,
        available_ingredients=[str(i) for i in body.available_ingredients],
    )
