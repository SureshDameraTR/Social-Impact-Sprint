"""Unit tests for Medicine Log endpoints — /v1/medicine-log."""

from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# GET /v1/medicine-log/withdrawals
# ---------------------------------------------------------------------------


class TestActiveWithdrawals:
    async def test_withdrawals_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with withdrawal data."""
        # Mock animal query
        animal_result = MagicMock()
        animal_result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=animal_result)

        resp = await client.get("/v1/medicine-log/withdrawals")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_withdrawals_no_animals(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET with no animals returns empty data."""
        animal_result = MagicMock()
        animal_result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=animal_result)

        resp = await client.get("/v1/medicine-log/withdrawals")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []
        assert body["total"] == 0

    async def test_withdrawals_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/medicine-log/withdrawals")
        assert resp.status_code in (401, 403)
