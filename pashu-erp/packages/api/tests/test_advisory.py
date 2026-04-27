"""Unit tests for Advisory endpoints — /v1/advisory."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient


def _mock_tip() -> MagicMock:
    tip = MagicMock()
    tip.id = uuid.uuid4()
    tip.title_en = "Summer Heat Management"
    tip.title_kn = None
    tip.body_en = "Ensure adequate water supply during summer"
    tip.body_kn = None
    tip.category = "health"
    tip.species_applicable = ["cattle", "goat"]
    tip.source = "ICAR"
    tip.priority = 5
    tip.is_active = True
    tip.published_at = datetime.now(timezone.utc)
    return tip


# ---------------------------------------------------------------------------
# GET /v1/advisory/tips
# ---------------------------------------------------------------------------


class TestListTips:
    async def test_list_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/advisory/tips")
        assert resp.status_code == 200

    async def test_list_with_species_filter(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET with species filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/advisory/tips?species=cattle")
        assert resp.status_code == 200

    async def test_list_with_category_filter(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET with category filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/advisory/tips?category=management")
        assert resp.status_code == 200

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/advisory/tips")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/advisory/tips/{id}
# ---------------------------------------------------------------------------


class TestGetTip:
    async def test_get_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 for existing tip."""
        tip = _mock_tip()
        result = MagicMock()
        result.scalar_one_or_none.return_value = tip
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/advisory/tips/{tip.id}")
        assert resp.status_code == 200

    async def test_get_not_found(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET with nonexistent ID returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/advisory/tips/{uuid.uuid4()}")
        assert resp.status_code == 404
