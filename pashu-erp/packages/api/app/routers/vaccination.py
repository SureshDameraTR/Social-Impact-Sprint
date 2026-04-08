"""Enhanced vaccination scheduling and coverage endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.animal import Animal
from app.models.health import Vaccination
from app.services.vaccination_scheduler import get_due_vaccinations, get_vaccination_schedule

router = APIRouter(prefix="/v1/vaccinations", tags=["Vaccinations"])


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
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming vaccinations for all animals owned by a user."""
    # Get all animals for this user
    result = await db.execute(
        select(Animal).where(Animal.user_id == user_id)
    )
    animals = result.scalars().all()

    if not animals:
        return {"user_id": str(user_id), "due_vaccinations": [], "total_animals": 0}

    all_due = []
    for animal in animals:
        # Get last vaccination dates for this animal
        vax_result = await db.execute(
            select(Vaccination)
            .where(Vaccination.animal_id == animal.id)
            .order_by(Vaccination.administered_on.desc())
        )
        vaccinations = vax_result.scalars().all()
        last_vax_map = {}
        for v in vaccinations:
            if v.vaccine_name not in last_vax_map:
                last_vax_map[v.vaccine_name] = v.administered_on

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
    db: AsyncSession = Depends(get_db),
):
    """Get vaccination coverage statistics for a village (mock aggregation)."""
    # Count animals in the village via user village_code if available
    # For prototype, return mock coverage stats
    return {
        "village_code": village_code,
        "total_animals": 156,
        "vaccinated_fmd": 142,
        "vaccinated_hs_bq": 128,
        "vaccinated_brucellosis": 89,
        "vaccinated_lsd": 134,
        "coverage_pct": {
            "FMD": 91.0,
            "HS+BQ": 82.1,
            "Brucellosis": 57.1,
            "LSD": 85.9,
        },
        "last_camp_date": "2026-03-15",
        "next_camp_date": "2026-04-20",
        "source": "District Veterinary Office (mock)",
    }
