"""Unit tests for Admin dashboard endpoints — /v1/admin."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# GET /v1/admin/stats — Dashboard stats
# ---------------------------------------------------------------------------


class TestDashboardStats:
    async def test_stats_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET as admin returns 200 with all stat fields."""
        # Stats endpoint makes many sequential DB calls
        scalar_result = MagicMock()
        scalar_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=scalar_result)

        resp = await client_as_admin.get("/v1/admin/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert "farmer_count" in body
        assert "animal_count" in body
        assert "todays_milk_liters" in body
        assert "active_alerts" in body
        assert "marketplace_revenue" in body
        assert "active_sellers" in body
        assert "women_farmers" in body
        assert "women_revenue" in body

    async def test_stats_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/admin/stats")
        assert resp.status_code in (401, 403)

    async def test_stats_as_farmer_forbidden(
        self, client: AsyncClient
    ) -> None:
        """GET as farmer returns 403 (admin only)."""
        resp = await client.get("/v1/admin/stats")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /v1/admin/charts/milk
# ---------------------------------------------------------------------------


class TestMilkChart:
    async def test_milk_chart_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET as admin returns 200 with chart data."""
        result = MagicMock()
        result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_admin.get("/v1/admin/charts/milk")
        assert resp.status_code == 200
        body = resp.json()
        assert "period" in body
        assert "data" in body
        assert len(body["data"]) == 30  # 30 days of data

    async def test_milk_chart_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/admin/charts/milk")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/admin/gis/alerts
# ---------------------------------------------------------------------------


class TestGISAlerts:
    async def test_gis_alerts_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET as admin returns 200 with GIS markers."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_admin.get("/v1/admin/gis/alerts")
        assert resp.status_code == 200
        body = resp.json()
        assert "alert_count" in body
        assert "markers" in body
