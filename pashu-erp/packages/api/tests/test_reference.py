"""Unit tests for Reference Data endpoints — /v1/reference."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


class _FakeRate:
    """Plain object that supports ``__dict__.copy()`` like a real ORM model."""

    def __init__(self) -> None:
        self.id = uuid.uuid4()
        self.product = "milk"
        self.unit = "liter"
        self.min_price = 30.0
        self.max_price = 40.0
        self.avg_price = 35.0
        self.district = "Tumkur"
        self.label = "Fresh cow milk"
        self.source = "Karnataka APMC"
        self.created_at = None
        self.updated_at = None
        self._sa_instance_state = object()  # placeholder


def _mock_rate() -> _FakeRate:
    return _FakeRate()


# ---------------------------------------------------------------------------
# GET /v1/reference/market-rates
# ---------------------------------------------------------------------------


class TestListMarketRates:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with data."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        # Clear cache to avoid stale data
        from app.routers.reference import _cache
        _cache.clear()

        resp = await client.get("/v1/reference/market-rates")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body

    async def test_list_with_district_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with district filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        from app.routers.reference import _cache
        _cache.clear()

        resp = await client.get("/v1/reference/market-rates?district=Tumkur")
        assert resp.status_code == 200

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/reference/market-rates")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# PUT /v1/reference/market-rates/{id} — Admin only
# ---------------------------------------------------------------------------


class TestUpdateMarketRate:
    async def test_update_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PUT as admin returns 200."""
        rate = _mock_rate()
        result = MagicMock()
        result.scalar_one_or_none.return_value = rate
        mock_db.execute = AsyncMock(return_value=result)

        from app.routers.reference import _cache
        _cache.clear()

        resp = await client_as_admin.put(
            f"/v1/reference/market-rates/{rate.id}",
            json={"avg_price": 37.5},
        )
        assert resp.status_code == 200

    async def test_update_not_found(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PUT with nonexistent rate returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_admin.put(
            f"/v1/reference/market-rates/{uuid.uuid4()}",
            json={"avg_price": 37.5},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /v1/reference/insurance-premiums
# ---------------------------------------------------------------------------


class TestListInsurancePremiums:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        from app.routers.reference import _cache
        _cache.clear()

        resp = await client.get("/v1/reference/insurance-premiums")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body


# ---------------------------------------------------------------------------
# GET /v1/reference/medicines
# ---------------------------------------------------------------------------


class TestListMedicineCatalog:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        from app.routers.reference import _cache
        _cache.clear()

        resp = await client.get("/v1/reference/medicines")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body

    async def test_list_with_species_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with species filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        from app.routers.reference import _cache
        _cache.clear()

        resp = await client.get("/v1/reference/medicines?species=cattle")
        assert resp.status_code == 200
