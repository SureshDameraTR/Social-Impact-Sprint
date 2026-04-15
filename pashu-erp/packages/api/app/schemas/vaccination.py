"""Pydantic schemas for vaccination-specific endpoints.

Note: VaccinationCreate and VaccinationRead live in schemas/health.py
and are reused here. This file covers additional shapes unique to the
vaccination router (coverage, schedules, species breakdown).
"""

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Species breakdown
# ---------------------------------------------------------------------------

class SpeciesBreakdownItem(BaseModel):
    species: str
    vaccination_count: int
    animal_count: int


class SpeciesBreakdownResponse(BaseModel):
    breakdown: list[SpeciesBreakdownItem]


# ---------------------------------------------------------------------------
# Village coverage
# ---------------------------------------------------------------------------

class VillageCoverageItem(BaseModel):
    village_code: str | None = None
    total_animals: int
    coverage_pct: float | dict[str, float]
    vaccine_counts: dict[str, int] | None = None


class VillageCoverageResponse(BaseModel):
    data: list[VillageCoverageItem]
    total: int


# ---------------------------------------------------------------------------
# Vaccination schedule
# ---------------------------------------------------------------------------

class ScheduleEntry(BaseModel):
    vaccine: str
    age_months: int | None = None
    frequency: str | None = None
    notes: str | None = None
    species: str | None = None


class ScheduleListResponse(BaseModel):
    data: list[ScheduleEntry]
    total: int


class SpeciesScheduleResponse(BaseModel):
    species: str
    schedule: list[dict[str, object]]
    message: str | None = None


# ---------------------------------------------------------------------------
# Due vaccinations
# ---------------------------------------------------------------------------

class DueVaccinationItem(BaseModel):
    vaccine: str | None = None
    due_date: str | None = None
    animal_id: str | None = None
    animal_name: str | None = None
    species: str | None = None
    age_months: int | None = None


class DueVaccinationsResponse(BaseModel):
    user_id: str
    due_vaccinations: list[DueVaccinationItem]
    total_animals: int


# ---------------------------------------------------------------------------
# Village coverage (single village)
# ---------------------------------------------------------------------------

class SingleVillageCoverage(BaseModel):
    village_code: str
    total_animals: int
    vaccine_counts: dict[str, int]
    coverage_pct: dict[str, float]
