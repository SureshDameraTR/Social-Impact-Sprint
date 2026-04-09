"""Vaccination CRUD, scheduling, and coverage endpoints.

All vaccination routes live here (consolidated from health.py).
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.health import Vaccination
from app.models.user import User
from app.schemas.health import VaccinationCreate, VaccinationRead
from app.services.vaccination_scheduler import get_due_vaccinations, get_vaccination_schedule

router = APIRouter(prefix="/v1/vaccinations", tags=["Vaccinations"])


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.post("", response_model=VaccinationRead, status_code=status.HTTP_201_CREATED)
async def record_vaccination(
    body: VaccinationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a vaccination for an animal."""
    result = await db.execute(select(Animal).where(Animal.id == body.animal_id))
    animal = result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    vaccination = Vaccination(
        animal_id=str(body.animal_id),
        vaccine_name=body.vaccine_name,
        administered_on=body.administered_on,
        next_due=body.next_due,
        batch_number=body.batch_number,
        recorded_by=str(current_user.id),
    )
    db.add(vaccination)
    await db.commit()
    await db.refresh(vaccination)
    return vaccination


# IMPORTANT: All static paths must come BEFORE /{animal_id} to avoid being captured as a UUID
@router.get("/due", response_model=list[VaccinationRead])
async def get_due_vaccinations_for_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming vaccinations for all of the current user's animals."""
    today = date.today()
    animal_result = await db.execute(
        select(Animal.id).where(Animal.user_id == current_user.id)
    )
    animal_ids = [row[0] for row in animal_result.all()]

    if not animal_ids:
        return []

    result = await db.execute(
        select(Vaccination)
        .where(
            Vaccination.animal_id.in_(animal_ids),
            Vaccination.next_due != None,  # noqa: E711
            Vaccination.next_due >= today,
        )
        .order_by(Vaccination.next_due.asc())
    )
    return result.scalars().all()


@router.get("/species-breakdown")
async def get_species_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Vaccination counts broken down by species (admin dashboard)."""
    result = await db.execute(
        select(
            Animal.species,
            func.count(func.distinct(Vaccination.id)).label("vaccination_count"),
            func.count(func.distinct(Animal.id)).label("animal_count"),
        )
        .join(Vaccination, Vaccination.animal_id == Animal.id)
        .group_by(Animal.species)
    )
    breakdown = []
    for row in result.all():
        breakdown.append({
            "species": row.species,
            "vaccination_count": row.vaccination_count,
            "animal_count": row.animal_count,
        })
    return {"breakdown": breakdown}


@router.get("/village-coverage")
async def get_village_coverage_admin(
    village_code: str | None = Query(None, description="Village code to check coverage for (omit for all villages)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get vaccination coverage for a village or all villages (admin dashboard)."""
    if village_code:
        total_result = await db.execute(
            select(func.count())
            .select_from(Animal)
            .join(User, Animal.user_id == User.id)
            .where(User.village_code == village_code)
        )
        total_animals = total_result.scalar() or 0
        if total_animals == 0:
            return {"data": [{"village_code": village_code, "total_animals": 0, "coverage_pct": {}, "vaccine_counts": {}}], "total": 1}
        vaccine_counts_result = await db.execute(
            select(
                Vaccination.vaccine_name,
                func.count(func.distinct(Vaccination.animal_id)).label("count"),
            )
            .join(Animal, Vaccination.animal_id == Animal.id)
            .join(User, Animal.user_id == User.id)
            .where(User.village_code == village_code)
            .group_by(Vaccination.vaccine_name)
        )
        vaccine_rows = vaccine_counts_result.all()
        vaccine_counts = {}
        coverage_pct = {}
        for row in vaccine_rows:
            vaccine_counts[row.vaccine_name] = row.count
            coverage_pct[row.vaccine_name] = round((row.count / total_animals) * 100, 1)
        return {"data": [{"village_code": village_code, "total_animals": total_animals, "vaccine_counts": vaccine_counts, "coverage_pct": coverage_pct}], "total": 1}

    # No village_code: aggregate across all villages
    village_result = await db.execute(
        select(
            User.village_code,
            func.count(func.distinct(Animal.id)).label("total_animals"),
            func.count(func.distinct(Vaccination.id)).label("vaccinated_count"),
        )
        .select_from(User)
        .join(Animal, Animal.user_id == User.id)
        .outerjoin(Vaccination, Vaccination.animal_id == Animal.id)
        .where(User.village_code.isnot(None))
        .group_by(User.village_code)
    )
    data = []
    for row in village_result.all():
        pct = round((row.vaccinated_count / row.total_animals) * 100, 1) if row.total_animals > 0 else 0
        data.append({
            "village_code": row.village_code,
            "total_animals": row.total_animals,
            "coverage_pct": pct,
        })
    return {"data": data, "total": len(data)}


@router.get("/schedule")
async def get_all_schedules():
    """Get ICAR vaccination schedules for all species."""
    all_schedules = []
    for species in ["cattle", "goat", "sheep", "poultry"]:
        schedule = get_vaccination_schedule(species)
        if schedule:
            for entry in schedule:
                all_schedules.append({**entry, "species": species.title()})
    return {"data": all_schedules, "total": len(all_schedules)}


@router.get("/{animal_id}", response_model=list[VaccinationRead])
async def get_vaccinations(
    animal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get vaccination records for an animal."""
    animal_result = await db.execute(select(Animal).where(Animal.id == animal_id))
    animal = animal_result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    result = await db.execute(
        select(Vaccination)
        .where(Vaccination.animal_id == animal_id)
        .order_by(Vaccination.administered_on.desc())
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Scheduling & Coverage
# ---------------------------------------------------------------------------

@router.get("/schedule/{species}")
async def get_species_schedule(species: str):
    """Get ICAR vaccination schedule for a species."""
    schedule = get_vaccination_schedule(species)
    if not schedule:
        return {"species": species, "schedule": [], "message": f"No schedule found for '{species}'"}
    return {"species": species.title(), "schedule": schedule}


@router.get("/due/{user_id}")
async def get_upcoming_vaccinations(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming vaccinations for all animals owned by a user."""
    # Get all animals for this user in one query
    result = await db.execute(
        select(Animal).where(Animal.user_id == user_id)
    )
    animals = result.scalars().all()

    if not animals:
        return {"user_id": str(user_id), "due_vaccinations": [], "total_animals": 0}

    # Fetch all vaccinations for all animal IDs in a single query
    animal_ids = [animal.id for animal in animals]
    vax_result = await db.execute(
        select(Vaccination)
        .where(Vaccination.animal_id.in_(animal_ids))
        .order_by(Vaccination.administered_on.desc())
    )
    all_vaccinations = vax_result.scalars().all()

    # Build per-animal last-vaccination maps
    animal_vax_map: dict[str, dict[str, date]] = {}
    for v in all_vaccinations:
        aid = str(v.animal_id)
        if aid not in animal_vax_map:
            animal_vax_map[aid] = {}
        if v.vaccine_name not in animal_vax_map[aid]:
            animal_vax_map[aid][v.vaccine_name] = v.administered_on

    all_due = []
    for animal in animals:
        last_vax_map = animal_vax_map.get(str(animal.id), {})
        due = get_due_vaccinations(
            species=animal.species,
            date_of_birth=animal.date_of_birth,
            last_vaccinations=last_vax_map,
        )
        for d in due:
            d["animal_id"] = str(animal.id)
            d["animal_name"] = animal.name or animal.tag_id or str(animal.id)[:8]
            d["species"] = animal.species
        all_due.extend(due)

    # Sort by due_date
    all_due.sort(key=lambda x: x.get("due_date", "9999-99-99"))

    return {
        "user_id": str(user_id),
        "due_vaccinations": all_due,
        "total_animals": len(animals),
    }


@router.get("/coverage/{village_code}")
async def get_village_coverage(
    village_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get vaccination coverage statistics for a village.

    Queries the database for real animal counts and vaccination records,
    then calculates actual coverage percentages.
    """
    # Count total animals in the village (via owner's village_code)
    total_result = await db.execute(
        select(func.count())
        .select_from(Animal)
        .join(User, Animal.user_id == User.id)
        .where(User.village_code == village_code)
    )
    total_animals = total_result.scalar() or 0

    if total_animals == 0:
        return {
            "village_code": village_code,
            "total_animals": 0,
            "coverage_pct": {},
            "vaccine_counts": {},
        }

    # Count distinct animals vaccinated per vaccine name
    vaccine_counts_result = await db.execute(
        select(
            Vaccination.vaccine_name,
            func.count(func.distinct(Vaccination.animal_id)).label("count"),
        )
        .join(Animal, Vaccination.animal_id == Animal.id)
        .join(User, Animal.user_id == User.id)
        .where(User.village_code == village_code)
        .group_by(Vaccination.vaccine_name)
    )
    vaccine_rows = vaccine_counts_result.all()

    vaccine_counts = {}
    coverage_pct = {}
    for row in vaccine_rows:
        vaccine_counts[row.vaccine_name] = row.count
        coverage_pct[row.vaccine_name] = round((row.count / total_animals) * 100, 1)

    return {
        "village_code": village_code,
        "total_animals": total_animals,
        "vaccine_counts": vaccine_counts,
        "coverage_pct": coverage_pct,
    }


@router.patch("/{vaccination_id}")
async def update_vaccination(
    vaccination_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a vaccination as administered (update administered_on to today)."""
    result = await db.execute(
        select(Vaccination).where(Vaccination.id == vaccination_id)
    )
    vaccination = result.scalar_one_or_none()
    if vaccination is None:
        raise HTTPException(status_code=404, detail="Vaccination not found")

    # Verify animal ownership
    animal_result = await db.execute(
        select(Animal).where(Animal.id == vaccination.animal_id)
    )
    animal = animal_result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    vaccination.administered_on = date.today()
    await db.commit()
    await db.refresh(vaccination)
    return vaccination
