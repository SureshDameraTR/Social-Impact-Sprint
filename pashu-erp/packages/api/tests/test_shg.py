"""Unit tests for SHG (Self Help Group) endpoints — /v1/shg."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_shg(admin_user_id: str = FARMER_USER_ID) -> MagicMock:
    group = MagicMock()
    group.id = uuid.uuid4()
    group.name = "Lakshmi Mahila SHG"
    group.registration_number = "SHG-2024-001"
    group.district = "Tumkur"
    group.village_code = "629001"
    group.admin_user_id = admin_user_id
    group.member_count = 12
    group.women_only = True
    group.formation_date = date(2023, 6, 15)
    group.total_savings = 25000.0
    group.grading = "A"
    group.panchsutra_compliance = {
        "regular_meetings": True,
        "regular_savings": True,
        "regular_internal_lending": True,
        "regular_repayment": True,
        "uptodate_bookkeeping": False,
    }
    group.created_at = datetime.now(timezone.utc)
    return group


def _valid_shg_payload() -> dict:
    return {
        "name": "Lakshmi Mahila SHG",
        "district": "Tumkur",
        "member_count": 12,
        "women_only": True,
        "total_savings": 25000.0,
    }


# ---------------------------------------------------------------------------
# POST /v1/shg — Create
# ---------------------------------------------------------------------------


class TestCreateSHG:
    async def test_create_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        resp = await client.post("/v1/shg", json=_valid_shg_payload())
        assert resp.status_code == 201

    async def test_create_missing_name(self, client: AsyncClient) -> None:
        """POST without 'name' returns 422."""
        resp = await client.post("/v1/shg", json={"district": "Tumkur"})
        assert resp.status_code == 422

    async def test_create_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post("/v1/shg", json=_valid_shg_payload())
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/shg — List
# ---------------------------------------------------------------------------


class TestListSHG:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/shg")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /v1/shg/{id}
# ---------------------------------------------------------------------------


class TestGetSHG:
    async def test_get_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 for existing group."""
        group = _mock_shg()
        result = MagicMock()
        result.scalar_one_or_none.return_value = group
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/shg/{group.id}")
        assert resp.status_code == 200

    async def test_get_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent ID returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/shg/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /v1/shg/{id}
# ---------------------------------------------------------------------------


class TestUpdateSHG:
    async def test_update_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH returns 200."""
        group = _mock_shg()
        result = MagicMock()
        result.scalar_one_or_none.return_value = group
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.patch(
            f"/v1/shg/{group.id}",
            json={"name": "Updated Name"},
        )
        assert resp.status_code == 200

    async def test_update_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH on nonexistent group returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.patch(
            f"/v1/shg/{uuid.uuid4()}",
            json={"name": "Updated"},
        )
        assert resp.status_code == 404

    async def test_update_forbidden(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH by non-admin returns 403."""
        group = _mock_shg(admin_user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = group
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.patch(
            f"/v1/shg/{group.id}",
            json={"name": "Hack"},
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /v1/shg/{id}/compliance — Panchsutra
# ---------------------------------------------------------------------------


class TestPanchsutraCompliance:
    async def test_compliance_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with compliance score."""
        group = _mock_shg()
        result = MagicMock()
        result.scalar_one_or_none.return_value = group
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/shg/{group.id}/compliance")
        assert resp.status_code == 200
        body = resp.json()
        assert "score" in body
        assert "total" in body
        assert "percentage" in body
        assert "principles" in body

    async def test_compliance_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent SHG returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/shg/{uuid.uuid4()}/compliance")
        assert resp.status_code == 404
