"""Unit tests for Marketplace endpoints — /v1/marketplace."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_sell_record() -> MagicMock:
    rec = MagicMock()
    rec.id = uuid.uuid4()
    rec.user_id = FARMER_USER_ID
    rec.product_type = "milk"
    rec.quantity = 10.0
    rec.unit = "liters"
    rec.price_per_unit = 35.0
    rec.total_amount = 350.0
    rec.buyer_name = "Dairy Corp"
    rec.buyer_phone = "+919900000055"
    rec.sold_at = datetime.now(timezone.utc)
    rec.notes = None
    return rec


# ---------------------------------------------------------------------------
# GET /v1/marketplace — List
# ---------------------------------------------------------------------------


class TestListSellRecords:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with paginated data."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/marketplace")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/marketplace")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /v1/marketplace/sell
# ---------------------------------------------------------------------------


class TestRecordSale:
    async def test_sell_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        resp = await client.post(
            "/v1/marketplace/sell",
            json={
                "product_type": "milk",
                "quantity": 10.0,
                "unit": "liters",
                "price_per_unit": 35.0,
            },
        )
        assert resp.status_code == 201

    async def test_sell_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post(
            "/v1/marketplace/sell",
            json={"product_type": "milk"},
        )
        assert resp.status_code == 422

    async def test_sell_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/marketplace/sell",
            json={
                "product_type": "milk",
                "quantity": 10.0,
                "unit": "liters",
                "price_per_unit": 35.0,
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/marketplace/history/{user_id}
# ---------------------------------------------------------------------------


class TestSellHistory:
    async def test_history_own_user(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET own history returns 200."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get(f"/v1/marketplace/history/{FARMER_USER_ID}")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_history_other_user_forbidden(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET another user's history returns 403."""
        resp = await client.get(f"/v1/marketplace/history/{uuid.uuid4()}")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /v1/marketplace/rates
# ---------------------------------------------------------------------------


class TestMarketRates:
    async def test_rates_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with market rates."""
        with patch(
            "app.routers.marketplace.get_all_market_rates",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.get("/v1/marketplace/rates")
            assert resp.status_code == 200
            body = resp.json()
            assert "rates" in body
            assert "source" in body


# ---------------------------------------------------------------------------
# GET /v1/marketplace/summary/{user_id}
# ---------------------------------------------------------------------------


class TestMarketplaceSummary:
    async def test_summary_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET own summary returns 200."""
        totals_row = MagicMock()
        totals_row.total_revenue = 5000.0
        totals_row.total_quantity = 100.0
        totals_row.total_sales = 5
        totals_result = MagicMock()
        totals_result.one.return_value = totals_row

        breakdown_result = MagicMock()
        breakdown_result.all.return_value = []

        mock_db.execute = AsyncMock(
            side_effect=[totals_result, breakdown_result]
        )

        resp = await client.get(
            f"/v1/marketplace/summary/{FARMER_USER_ID}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "total_revenue" in body
        assert "total_sales" in body
