"""Unit tests for Government Schemes endpoints — /v1/schemes."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


def _mock_scheme() -> MagicMock:
    scheme = MagicMock()
    scheme.id = uuid.uuid4()
    scheme.scheme_code = "LISS-2024"
    scheme.name = "Livestock Insurance Scheme"
    scheme.ministry = "DAHD"
    scheme.description = "Insurance subsidy for livestock"
    scheme.eligibility_criteria = "BPL farmers"
    scheme.required_documents = ["Aadhaar", "BPL Card"]
    scheme.max_subsidy_amount = 50000.0
    scheme.subsidy_percentage = 50.0
    scheme.is_active = True
    scheme.valid_from = date(2024, 1, 1)
    scheme.valid_to = date(2025, 12, 31)
    scheme.created_at = datetime.now(timezone.utc)
    return scheme


# ---------------------------------------------------------------------------
# GET /v1/schemes — List
# ---------------------------------------------------------------------------


class TestListSchemes:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/schemes")
        assert resp.status_code == 200

    async def test_list_with_ministry_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with ministry filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/schemes?ministry=DAHD")
        assert resp.status_code == 200

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/schemes")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/schemes/{id}
# ---------------------------------------------------------------------------


class TestGetScheme:
    async def test_get_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 for existing scheme."""
        scheme = _mock_scheme()
        result = MagicMock()
        result.scalar_one_or_none.return_value = scheme
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/schemes/{scheme.id}")
        assert resp.status_code == 200

    async def test_get_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent ID returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/schemes/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /v1/schemes — Create (admin only)
# ---------------------------------------------------------------------------


class TestCreateScheme:
    async def test_create_success_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST as admin returns 201."""
        resp = await client_as_admin.post(
            "/v1/schemes",
            json={
                "scheme_code": "LISS-2024",
                "name": "Livestock Insurance Scheme",
                "valid_from": "2024-01-01",
            },
        )
        assert resp.status_code == 201

    async def test_create_missing_fields(
        self, client_as_admin: AsyncClient
    ) -> None:
        """POST without required fields returns 422."""
        resp = await client_as_admin.post(
            "/v1/schemes", json={"name": "Test"}
        )
        assert resp.status_code == 422

    async def test_create_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/schemes",
            json={
                "scheme_code": "TEST",
                "name": "Test",
                "valid_from": "2024-01-01",
            },
        )
        assert resp.status_code in (401, 403)
