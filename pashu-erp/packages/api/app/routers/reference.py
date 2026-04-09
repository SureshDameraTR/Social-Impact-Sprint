"""Reference data endpoints -- market rates, insurance premiums, medicine catalog."""

import time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models.reference import InsurancePremium, MarketRate, MedicineCatalog
from app.models.user import User

router = APIRouter(prefix="/v1/reference", tags=["Reference Data"])

# ---------------------------------------------------------------------------
# Simple in-memory cache: key -> (data, timestamp)
# ---------------------------------------------------------------------------
_cache: dict[str, tuple[list, float]] = {}
_CACHE_TTL = 60  # seconds


def _get_cached(key: str) -> list | None:
    entry = _cache.get(key)
    if entry and time.monotonic() - entry[1] < _CACHE_TTL:
        return entry[0]
    _cache.pop(key, None)
    return None


def _set_cached(key: str, data: list) -> None:
    _cache[key] = (data, time.monotonic())


def _invalidate_prefix(prefix: str) -> None:
    """Remove all cache entries whose key starts with prefix."""
    stale = [k for k in _cache if k.startswith(prefix)]
    for k in stale:
        del _cache[k]


# ---------------------------------------------------------------------------
# Market rates
# ---------------------------------------------------------------------------


@router.get("/market-rates")
async def list_market_rates(
    district: str | None = Query(None, description="Filter by district"),
    product: str | None = Query(None, description="Filter by product key"),
    db: AsyncSession = Depends(get_db),
):
    """List market rates with optional filters."""
    cache_key = f"market_rates:{district}:{product}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return {"data": cached}

    stmt = select(MarketRate)
    if district:
        stmt = stmt.where(MarketRate.district == district)
    if product:
        stmt = stmt.where(MarketRate.product == product)
    stmt = stmt.order_by(MarketRate.product)

    result = await db.execute(stmt)
    data = [row.__dict__ for row in result.scalars().all()]
    for d in data:
        d.pop("_sa_instance_state", None)

    _set_cached(cache_key, data)
    return {"data": data}


@router.put("/market-rates/{rate_id}")
async def update_market_rate(
    rate_id: UUID,
    body: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin-only: update a market rate record."""
    result = await db.execute(
        select(MarketRate).where(MarketRate.id == rate_id)
    )
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(status_code=404, detail="Market rate not found")

    allowed = {"product", "unit", "min_price", "max_price", "avg_price", "district", "label", "source"}
    for field, value in body.items():
        if field in allowed:
            setattr(rate, field, value)

    await db.commit()
    await db.refresh(rate)
    _invalidate_prefix("market_rates:")

    data = rate.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


# ---------------------------------------------------------------------------
# Insurance premiums
# ---------------------------------------------------------------------------


@router.get("/insurance-premiums")
async def list_insurance_premiums(
    species: str | None = Query(None, description="Filter by species"),
    breed_type: str | None = Query(None, description="Filter by breed type"),
    db: AsyncSession = Depends(get_db),
):
    """List insurance premium rates with optional filters."""
    cache_key = f"insurance_premiums:{species}:{breed_type}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return {"data": cached}

    stmt = select(InsurancePremium)
    if species:
        stmt = stmt.where(InsurancePremium.species == species)
    if breed_type:
        stmt = stmt.where(InsurancePremium.breed_type == breed_type)
    stmt = stmt.order_by(InsurancePremium.species, InsurancePremium.breed_type)

    result = await db.execute(stmt)
    data = [row.__dict__ for row in result.scalars().all()]
    for d in data:
        d.pop("_sa_instance_state", None)

    _set_cached(cache_key, data)
    return {"data": data}


@router.put("/insurance-premiums/{premium_id}")
async def update_insurance_premium(
    premium_id: UUID,
    body: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin-only: update an insurance premium record."""
    result = await db.execute(
        select(InsurancePremium).where(InsurancePremium.id == premium_id)
    )
    premium = result.scalar_one_or_none()
    if premium is None:
        raise HTTPException(status_code=404, detail="Insurance premium not found")

    allowed = {"species", "breed_type", "premium_pct", "animal_value_inr", "scheme_name"}
    for field, value in body.items():
        if field in allowed:
            setattr(premium, field, value)

    await db.commit()
    await db.refresh(premium)
    _invalidate_prefix("insurance_premiums:")

    data = premium.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data


# ---------------------------------------------------------------------------
# Medicine catalog
# ---------------------------------------------------------------------------


@router.get("/medicines")
async def list_medicines(
    species: str | None = Query(None, description="Filter by applicable species"),
    category: str | None = Query(None, description="Filter by category"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
):
    """List medicine catalog entries with optional filters."""
    cache_key = f"medicines:{species}:{category}:{is_active}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return {"data": cached}

    stmt = select(MedicineCatalog)
    if species:
        stmt = stmt.where(MedicineCatalog.species_applicable.any(species))
    if category:
        stmt = stmt.where(MedicineCatalog.category == category)
    if is_active is not None:
        stmt = stmt.where(MedicineCatalog.is_active == is_active)
    stmt = stmt.order_by(MedicineCatalog.name)

    result = await db.execute(stmt)
    data = [row.__dict__ for row in result.scalars().all()]
    for d in data:
        d.pop("_sa_instance_state", None)

    _set_cached(cache_key, data)
    return {"data": data}
