"""Unit tests for Vaccination endpoints — /v1/vaccinations."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_animal(user_id: str = FARMER_USER_ID) -> MagicMock:
    animal = MagicMock()
    animal.id = uuid.uuid4()
    animal.user_id = user_id
    animal.species = "cattle"
    animal.name = "Gauri"
    animal.tag_id = "TAG001"
    animal.date_of_birth = date(2020, 1, 15)
    return animal


def _mock_vaccination() -> MagicMock:
    vax = MagicMock()
    vax.id = uuid.uuid4()
    vax.animal_id = uuid.uuid4()
    vax.vaccine_name = "FMD"
    vax.administered_on = date(2024, 3, 15)
    vax.next_due = date(2024, 9, 15)
    vax.batch_number = "BATCH-001"
    vax.recorded_by = FARMER_USER_ID
    vax.created_at = datetime.now(timezone.utc)
    return vax


# ---------------------------------------------------------------------------
# POST /v1/vaccinations — Record
# ---------------------------------------------------------------------------


class TestRecordVaccination:
    async def test_record_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        animal = _mock_animal()
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/vaccinations",
            json={
                "animal_id": str(animal.id),
                "vaccine_name": "FMD",
                "administered_on": "2024-03-15",
            },
        )
        assert resp.status_code == 201

    async def test_record_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/vaccinations",
            json={
                "animal_id": str(uuid.uuid4()),
                "vaccine_name": "FMD",
                "administered_on": "2024-03-15",
            },
        )
        assert resp.status_code == 404

    async def test_record_forbidden(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST on another user's animal returns 403."""
        animal = _mock_animal(user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/vaccinations",
            json={
                "animal_id": str(animal.id),
                "vaccine_name": "FMD",
                "administered_on": "2024-03-15",
            },
        )
        assert resp.status_code == 403

    async def test_record_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post(
            "/v1/vaccinations",
            json={"vaccine_name": "FMD"},
        )
        assert resp.status_code == 422

    async def test_record_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/vaccinations",
            json={
                "animal_id": str(uuid.uuid4()),
                "vaccine_name": "FMD",
                "administered_on": "2024-03-15",
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/vaccinations/due
# ---------------------------------------------------------------------------


class TestDueVaccinations:
    async def test_due_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        animal_result = MagicMock()
        animal_result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=animal_result)

        resp = await client.get("/v1/vaccinations/due")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /v1/vaccinations/schedule
# ---------------------------------------------------------------------------


class TestVaccinationSchedule:
    async def test_schedule_all(self, client: AsyncClient) -> None:
        """GET returns 200 with schedules for all species."""
        resp = await client.get("/v1/vaccinations/schedule")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_schedule_species(self, client: AsyncClient) -> None:
        """GET for specific species returns 200."""
        resp = await client.get("/v1/vaccinations/schedule/cattle")
        assert resp.status_code == 200
        body = resp.json()
        assert body["species"] == "Cattle"


# ---------------------------------------------------------------------------
# GET /v1/vaccinations/{animal_id}
# ---------------------------------------------------------------------------


class TestGetVaccinations:
    async def test_get_for_animal_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 for owned animal."""
        animal = _mock_animal()
        animal_result = MagicMock()
        animal_result.scalar_one_or_none.return_value = animal

        vax_result = MagicMock()
        vax_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(
            side_effect=[animal_result, vax_result]
        )

        resp = await client.get(f"/v1/vaccinations/{animal.id}")
        assert resp.status_code == 200

    async def test_get_for_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/vaccinations/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /v1/vaccinations/species-breakdown
# ---------------------------------------------------------------------------


class TestSpeciesBreakdown:
    async def test_breakdown_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with breakdown data."""
        result = MagicMock()
        result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/vaccinations/species-breakdown")
        assert resp.status_code == 200
        body = resp.json()
        assert "breakdown" in body


# ---------------------------------------------------------------------------
# GET /v1/vaccinations/village-coverage
# ---------------------------------------------------------------------------


class TestVillageCoverage:
    async def test_coverage_with_village(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with village_code returns 200."""
        total_result = MagicMock()
        total_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=total_result)

        resp = await client.get(
            "/v1/vaccinations/village-coverage?village_code=629001"
        )
        assert resp.status_code == 200

    async def test_coverage_all_villages(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET without village_code returns 200."""
        result = MagicMock()
        result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/vaccinations/village-coverage")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body
