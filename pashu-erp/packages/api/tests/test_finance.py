"""Unit tests for Finance endpoints — /v1/finance."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_transaction() -> MagicMock:
    txn = MagicMock()
    txn.id = uuid.uuid4()
    txn.user_id = FARMER_USER_ID
    txn.type = "income"
    txn.amount = 1500.00
    txn.category = "milk_sale"
    txn.description = "Daily milk"
    txn.reference_id = None
    txn.status = "completed"
    txn.created_at = datetime.now(timezone.utc)
    return txn


# ---------------------------------------------------------------------------
# POST /v1/finance/transaction
# ---------------------------------------------------------------------------


class TestRecordTransaction:
    async def test_create_transaction_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        resp = await client.post(
            "/v1/finance/transaction",
            json={
                "type": "income",
                "amount": 1500.00,
                "category": "milk_sale",
                "description": "Daily milk sale",
            },
        )
        assert resp.status_code == 201

    async def test_create_transaction_missing_type(self, client: AsyncClient) -> None:
        """POST without 'type' returns 422."""
        resp = await client.post(
            "/v1/finance/transaction",
            json={"amount": 1500.00, "category": "milk_sale"},
        )
        assert resp.status_code == 422

    async def test_create_transaction_zero_amount(self, client: AsyncClient) -> None:
        """POST with zero amount returns 422 (amount must be > 0)."""
        resp = await client.post(
            "/v1/finance/transaction",
            json={"type": "income", "amount": 0, "category": "test"},
        )
        assert resp.status_code == 422

    async def test_create_transaction_negative_amount(
        self, client: AsyncClient
    ) -> None:
        """POST with negative amount returns 422."""
        resp = await client.post(
            "/v1/finance/transaction",
            json={"type": "income", "amount": -100, "category": "test"},
        )
        assert resp.status_code == 422

    async def test_create_transaction_no_auth(
        self, client_no_auth: AsyncClient
    ) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/finance/transaction",
            json={"type": "income", "amount": 100, "category": "test"},
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/finance/summary
# ---------------------------------------------------------------------------


class TestFinancialSummary:
    async def test_summary_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with summary data."""
        txn = _mock_transaction()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [txn]
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/finance/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert "period" in body
        assert "total_income" in body
        assert "total_expense" in body
        assert "net" in body

    async def test_summary_with_period_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with period=week returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/finance/summary?period=week")
        assert resp.status_code == 200
        assert resp.json()["period"] == "week"

    async def test_summary_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/finance/summary")
        assert resp.status_code in (401, 403)
