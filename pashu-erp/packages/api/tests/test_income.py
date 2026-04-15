"""Unit tests for Income endpoints — /v1/income."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


# ---------------------------------------------------------------------------
# GET /v1/income/summary/{user_id}
# ---------------------------------------------------------------------------


class TestIncomeSummary:
    async def test_summary_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with income summary."""
        txn_result = MagicMock()
        txn_result.all.return_value = []
        sell_result = MagicMock()
        sell_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(side_effect=[txn_result, sell_result])

        resp = await client.get(f"/v1/income/summary/{FARMER_USER_ID}")
        assert resp.status_code == 200
        body = resp.json()
        assert "total_income" in body
        assert "total_expense" in body
        assert "net" in body

    async def test_summary_other_user_forbidden(
        self, client: AsyncClient
    ) -> None:
        """GET another user's summary returns 403."""
        resp = await client.get(f"/v1/income/summary/{uuid.uuid4()}")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /v1/income/summary — Current user convenience
# ---------------------------------------------------------------------------


class TestMyIncomeSummary:
    async def test_my_summary_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 for current user."""
        txn_result = MagicMock()
        txn_result.all.return_value = []
        sell_result = MagicMock()
        sell_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(side_effect=[txn_result, sell_result])

        resp = await client.get("/v1/income/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert "total_income" in body

    async def test_my_summary_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/income/summary")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/income/breakdown/{user_id}
# ---------------------------------------------------------------------------


class TestIncomeBreakdown:
    async def test_breakdown_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with breakdown data."""
        txn_result = MagicMock()
        txn_result.all.return_value = []
        sell_result = MagicMock()
        sell_result.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[txn_result, sell_result])

        resp = await client.get(f"/v1/income/breakdown/{FARMER_USER_ID}")
        assert resp.status_code == 200
        body = resp.json()
        assert "breakdown" in body

    async def test_breakdown_other_user_forbidden(
        self, client: AsyncClient
    ) -> None:
        """GET another user's breakdown returns 403."""
        resp = await client.get(f"/v1/income/breakdown/{uuid.uuid4()}")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /v1/income/transactions — Current user
# ---------------------------------------------------------------------------


class TestMyTransactions:
    async def test_transactions_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with paginated data."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/income/transactions")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body


# ---------------------------------------------------------------------------
# GET /v1/income/by-category
# ---------------------------------------------------------------------------


class TestIncomeByCategory:
    async def test_by_category_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        txn_result = MagicMock()
        txn_result.all.return_value = []
        sell_result = MagicMock()
        sell_result.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[txn_result, sell_result])

        resp = await client.get("/v1/income/by-category")
        assert resp.status_code == 200
        body = resp.json()
        assert "breakdown" in body


# ---------------------------------------------------------------------------
# GET /v1/income/monthly
# ---------------------------------------------------------------------------


class TestMonthlyTrend:
    async def test_monthly_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        txn_result = MagicMock()
        txn_result.all.return_value = []
        sell_result = MagicMock()
        sell_result.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[txn_result, sell_result])

        resp = await client.get("/v1/income/monthly")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
