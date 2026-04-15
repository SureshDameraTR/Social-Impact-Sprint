"""Unit tests for Vet consultation endpoints — /v1/vet."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import VET_USER_ID, FARMER_USER_ID


def _mock_consultation(
    vet_id: str | None = None,
    status: str = "pending",
    district: str = "Tumkur",
) -> MagicMock:
    case = MagicMock()
    case.id = uuid.uuid4()
    case.animal_id = str(uuid.uuid4())
    case.farmer_id = str(FARMER_USER_ID)
    case.vet_id = vet_id
    case.status = status
    case.priority = "urgent"
    case.channel = "photo"
    case.farmer_notes = "Animal is sick"
    case.photo_urls = []
    case.diagnosis = None
    case.prescription = None
    case.follow_up_date = None
    case.video_call_url = None
    case.district = district
    case.created_at = datetime.now(timezone.utc)
    case.updated_at = datetime.now(timezone.utc)

    # Mock the animal relationship
    animal = MagicMock()
    animal.id = case.animal_id
    animal.species = "cattle"
    animal.name = "Gauri"
    animal.breed = "Gir"
    owner = MagicMock()
    owner.id = FARMER_USER_ID
    owner.name = "Lakshmi"
    owner.phone = "+919900000002"
    owner.village_code = "629001"
    owner.location_district = "Tumkur"
    animal.owner = owner
    case.animal = animal

    return case


# ---------------------------------------------------------------------------
# GET /v1/vet/cases
# ---------------------------------------------------------------------------


class TestListCases:
    async def test_list_as_vet(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET as vet returns 200 with case data."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.get("/v1/vet/cases")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body

    async def test_list_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET as admin returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_admin.get("/v1/vet/cases")
        assert resp.status_code == 200

    async def test_list_with_filters(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with status and priority filters returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.get(
            "/v1/vet/cases?status=pending&priority=urgent"
        )
        assert resp.status_code == 200

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/vet/cases")
        assert resp.status_code in (401, 403)

    async def test_list_as_farmer_forbidden(self, client: AsyncClient) -> None:
        """GET as farmer returns 403 (vet/admin only)."""
        resp = await client.get("/v1/vet/cases")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /v1/vet/cases/{id}
# ---------------------------------------------------------------------------


class TestGetCase:
    async def test_get_success(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        case = _mock_consultation(vet_id=VET_USER_ID, status="in_review")
        result = MagicMock()
        result.scalar_one_or_none.return_value = case
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.get(f"/v1/vet/cases/{case.id}")
        assert resp.status_code == 200

    async def test_get_not_found(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent ID returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.get(f"/v1/vet/cases/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /v1/vet/cases/{id}/claim
# ---------------------------------------------------------------------------


class TestClaimCase:
    async def test_claim_success(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH on unclaimed case returns 200."""
        case = _mock_consultation()
        result = MagicMock()
        result.scalar_one_or_none.return_value = case
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.patch(f"/v1/vet/cases/{case.id}/claim")
        assert resp.status_code == 200

    async def test_claim_already_claimed(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH on already-claimed case returns 409."""
        case = _mock_consultation(vet_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = case
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.patch(f"/v1/vet/cases/{case.id}/claim")
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# PATCH /v1/vet/cases/{id}/diagnose
# ---------------------------------------------------------------------------


class TestDiagnoseCase:
    async def test_diagnose_success(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH with diagnosis returns 200."""
        case = _mock_consultation(vet_id=VET_USER_ID, status="in_review")
        result = MagicMock()
        result.scalar_one_or_none.return_value = case
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.patch(
            f"/v1/vet/cases/{case.id}/diagnose",
            json={
                "diagnosis": "FMD infection",
                "prescription": "Antibiotics for 5 days",
            },
        )
        assert resp.status_code == 200

    async def test_diagnose_unclaimed_case(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH on unclaimed case returns 400."""
        case = _mock_consultation()  # vet_id is None
        result = MagicMock()
        result.scalar_one_or_none.return_value = case
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.patch(
            f"/v1/vet/cases/{case.id}/diagnose",
            json={"diagnosis": "FMD"},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /v1/vet/cases/{id}/close
# ---------------------------------------------------------------------------


class TestCloseCase:
    async def test_close_success(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH returns 200."""
        case = _mock_consultation(vet_id=VET_USER_ID, status="diagnosed")
        result = MagicMock()
        result.scalar_one_or_none.return_value = case
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.patch(f"/v1/vet/cases/{case.id}/close")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /v1/vet/dashboard/stats
# ---------------------------------------------------------------------------


class TestVetDashboardStats:
    async def test_stats_as_vet(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with dashboard stats."""
        scalar_result = MagicMock()
        scalar_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=scalar_result)

        resp = await client_as_vet.get("/v1/vet/dashboard/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert "pending_cases" in body
        assert "diagnosed_today" in body
        assert "district_animals" in body
        assert "active_alerts" in body


# ---------------------------------------------------------------------------
# GET /v1/vet/my-cases — Farmer-facing
# ---------------------------------------------------------------------------


class TestMyCases:
    async def test_my_cases_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with farmer's own cases."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/vet/my-cases")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body

    async def test_my_cases_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/vet/my-cases")
        assert resp.status_code in (401, 403)
