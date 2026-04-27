"""Reference data endpoints -- market rates, insurance premiums, medicine catalog."""

from uuid import UUID

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models.breed import Breed, SpeciesRef
from app.models.domain_knowledge import DiseaseRule, FeedStandard, VaccinationScheduleEntry
from app.models.location import District, State, SubDistrict, Village
from app.models.reference import InsurancePremium, MarketRate, MedicineCatalog
from app.models.user import User
from app.schemas.reference import (
    BreedListResponse,
    DiseaseRuleListResponse,
    DistrictListResponse,
    FeedStandardListResponse,
    InsurancePremiumListResponse,
    InsurancePremiumRead,
    InsurancePremiumUpdate,
    LocationHierarchyResponse,
    MarketRateListResponse,
    MarketRateRead,
    MarketRateUpdate,
    MedicineCatalogListResponse,
    SpeciesListResponse,
    SubDistrictListResponse,
    VaccinationScheduleListResponse,
    VillageListResponse,
)

router = APIRouter(prefix="/v1/reference", tags=["Reference Data"])


# ---------------------------------------------------------------------------
# Bounded TTL cache (maxsize prevents unbounded growth)
# ---------------------------------------------------------------------------
_cache: TTLCache = TTLCache(maxsize=100, ttl=60)


def _get_cached(key: str) -> list | None:
    return _cache.get(key)


def _set_cached(key: str, data: list) -> None:
    _cache[key] = data


def _invalidate_prefix(prefix: str) -> None:
    """Remove all cache entries whose key starts with prefix."""
    stale = [k for k in list(_cache.keys()) if k.startswith(prefix)]
    for k in stale:
        _cache.pop(k, None)


# ---------------------------------------------------------------------------
# Market rates
# ---------------------------------------------------------------------------


@router.get("/market-rates", response_model=MarketRateListResponse)
async def list_market_rates(
    district: str | None = Query(None, description="Filter by district"),
    product: str | None = Query(None, description="Filter by product key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List market rates with optional filters."""
    cache_key = f"market_rates:{district}:{product}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return {"data": cached, "total": len(cached)}

    stmt = select(MarketRate).where(MarketRate.deleted_at.is_(None))
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
    return {"data": data, "total": len(data)}


@router.put("/market-rates/{rate_id}", response_model=MarketRateRead)
async def update_market_rate(
    rate_id: UUID,
    body: MarketRateUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin-only: update a market rate record."""
    result = await db.execute(select(MarketRate).where(MarketRate.id == rate_id))
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(status_code=404, detail="Market rate not found")

    for field, value in body.model_dump(exclude_unset=True).items():
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


@router.get("/insurance-premiums", response_model=InsurancePremiumListResponse)
async def list_insurance_premiums(
    species: str | None = Query(None, description="Filter by species"),
    breed_type: str | None = Query(None, description="Filter by breed type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List insurance premium rates with optional filters."""
    cache_key = f"insurance_premiums:{species}:{breed_type}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return {"data": cached, "total": len(cached)}

    stmt = select(InsurancePremium).where(InsurancePremium.deleted_at.is_(None))
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
    return {"data": data, "total": len(data)}


@router.put("/insurance-premiums/{premium_id}", response_model=InsurancePremiumRead)
async def update_insurance_premium(
    premium_id: UUID,
    body: InsurancePremiumUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin-only: update an insurance premium record."""
    result = await db.execute(select(InsurancePremium).where(InsurancePremium.id == premium_id))
    premium = result.scalar_one_or_none()
    if premium is None:
        raise HTTPException(status_code=404, detail="Insurance premium not found")

    for field, value in body.model_dump(exclude_unset=True).items():
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


@router.get("/medicines", response_model=MedicineCatalogListResponse)
async def list_medicines(
    species: str | None = Query(None, description="Filter by applicable species"),
    category: str | None = Query(None, description="Filter by category"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List medicine catalog entries with optional filters."""
    cache_key = f"medicines:{species}:{category}:{is_active}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return {"data": cached, "total": len(cached)}

    stmt = select(MedicineCatalog).where(MedicineCatalog.deleted_at.is_(None))
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
    return {"data": data, "total": len(data)}


# ---------------------------------------------------------------------------
# Location hierarchy (public — no auth required)
# ---------------------------------------------------------------------------


@router.get("/states", response_model=LocationHierarchyResponse)
async def list_states(db: AsyncSession = Depends(get_db)):
    count = (await db.execute(select(func.count()).select_from(State))).scalar() or 0
    rows = (await db.execute(select(State).order_by(State.name))).scalars().all()
    return {"data": rows, "total": count}


@router.get("/districts", response_model=DistrictListResponse)
async def list_districts(
    state_lgd_code: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    base = select(District)
    if state_lgd_code is not None:
        base = base.where(District.state_lgd_code == state_lgd_code)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (await db.execute(base.order_by(District.name))).scalars().all()
    return {"data": rows, "total": count}


@router.get("/sub-districts", response_model=SubDistrictListResponse)
async def list_sub_districts(
    district_lgd_code: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    base = select(SubDistrict).where(SubDistrict.district_lgd_code == district_lgd_code)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (await db.execute(base.order_by(SubDistrict.name))).scalars().all()
    return {"data": rows, "total": count}


@router.get("/villages", response_model=VillageListResponse)
async def list_villages(
    sub_district_lgd_code: int = Query(...),
    q: str | None = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    base = select(Village).where(Village.sub_district_lgd_code == sub_district_lgd_code)
    if q:
        base = base.where(Village.name.ilike(f"%{q}%"))
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    stmt = base.order_by(Village.name).offset(offset).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    return {"data": rows, "total": count}


# ---------------------------------------------------------------------------
# Species & breeds (public)
# ---------------------------------------------------------------------------


@router.get("/species", response_model=SpeciesListResponse)
async def list_species(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(SpeciesRef).where(SpeciesRef.is_active.is_(True)).order_by(SpeciesRef.name_en)
    )).scalars().all()
    return {"data": rows, "total": len(rows)}


@router.get("/breeds", response_model=BreedListResponse)
async def list_breeds(
    species_code: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    base = select(Breed).where(Breed.is_active.is_(True))
    if species_code:
        base = base.where(Breed.species_code == species_code)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (await db.execute(base.order_by(Breed.name))).scalars().all()
    return {"data": rows, "total": count}


# ---------------------------------------------------------------------------
# Domain knowledge (public)
# ---------------------------------------------------------------------------


@router.get("/disease-rules", response_model=DiseaseRuleListResponse)
async def list_disease_rules(
    species_code: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    base = select(DiseaseRule).where(DiseaseRule.is_active.is_(True))
    if species_code:
        base = base.where(DiseaseRule.species_code == species_code)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (await db.execute(base.order_by(DiseaseRule.disease_name))).scalars().all()
    return {"data": rows, "total": count}


@router.get("/vaccination-schedule", response_model=VaccinationScheduleListResponse)
async def list_vaccination_schedule(
    species_code: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    base = select(VaccinationScheduleEntry).where(VaccinationScheduleEntry.is_active.is_(True))
    if species_code:
        base = base.where(VaccinationScheduleEntry.species_code == species_code)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (await db.execute(base.order_by(VaccinationScheduleEntry.vaccine_name))).scalars().all()
    return {"data": rows, "total": count}


@router.get("/feed-standards", response_model=FeedStandardListResponse)
async def list_feed_standards(
    species_code: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    base = select(FeedStandard).where(FeedStandard.is_active.is_(True))
    if species_code:
        base = base.where(FeedStandard.species_code == species_code)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    rows = (await db.execute(base.order_by(FeedStandard.species_code))).scalars().all()
    return {"data": rows, "total": count}
