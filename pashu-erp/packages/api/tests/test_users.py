"""Unit tests for User endpoints — /v1/farmers, /v1/users."""

from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# GET /v1/farmers — List (admin only)
# ---------------------------------------------------------------------------


class TestListFarmers:
    async def test_list_as_admin(self, client_as_admin: AsyncClient, mock_db: AsyncMock) -> None:
        """GET as admin returns 200 with paginated data."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        user_result = MagicMock()
        user_result.scalars.return_value.all.return_value = []
        animal_count_result = MagicMock()
        animal_count_result.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[count_result, user_result, animal_count_result])

        resp = await client_as_admin.get("/v1/farmers")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_list_as_farmer_forbidden(self, client: AsyncClient) -> None:
        """GET as farmer returns 403."""
        resp = await client.get("/v1/farmers")
        assert resp.status_code == 403

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/farmers")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/users/profile
# ---------------------------------------------------------------------------


class TestGetProfile:
    async def test_profile_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with user profile."""
        count_result = MagicMock()
        count_result.scalar.return_value = 3
        mock_db.execute = AsyncMock(return_value=count_result)

        resp = await client.get("/v1/users/profile")
        assert resp.status_code == 200
        body = resp.json()
        assert "id" in body
        assert "role" in body
        assert "animal_count" in body

    async def test_profile_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/users/profile")
        assert resp.status_code in (401, 403)
