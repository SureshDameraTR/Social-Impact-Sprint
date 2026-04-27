"""Unit tests for Map endpoints — /v1/map."""

from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# GET /v1/map/points
# ---------------------------------------------------------------------------


class TestGetMapPoints:
    async def test_map_points_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with combined map data."""
        # Mock health events
        health_result = MagicMock()
        health_result.scalars.return_value.all.return_value = []
        # Mock milk centers
        center_result = MagicMock()
        center_result.scalars.return_value.all.return_value = []
        # Mock community alerts
        alert_result = MagicMock()
        alert_result.scalars.return_value.all.return_value = []
        # Mock farmer clusters
        farmer_result = MagicMock()
        farmer_result.all.return_value = []

        mock_db.execute = AsyncMock(
            side_effect=[health_result, center_result, alert_result, farmer_result]
        )

        resp = await client.get("/v1/map/points")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body
        assert "data" in body
        assert isinstance(body["data"], list)

    async def test_map_points_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/map/points")
        assert resp.status_code in (401, 403)
