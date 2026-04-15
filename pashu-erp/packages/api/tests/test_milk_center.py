"""Unit tests for Milk Center endpoints — /v1/milk-center."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import MILK_CENTER_USER_ID


def _mock_center() -> MagicMock:
    center = MagicMock()
    center.id = uuid.uuid4()
    center.name = "Tumkur Milk Center"
    center.code = "TMK-001"
    center.district = "Tumkur"
    center.village_code = "629001"
    center.manager_user_id = MILK_CENTER_USER_ID
    center.is_active = True
    return center


# ---------------------------------------------------------------------------
# GET /v1/milk-center/my-center
# ---------------------------------------------------------------------------


class TestMyCenter:
    async def test_my_center_success(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with center info."""
        center = _mock_center()
        result = MagicMock()
        result.scalar_one_or_none.return_value = center
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.get("/v1/milk-center/my-center")
        assert resp.status_code == 200
        body = resp.json()
        assert "name" in body
        assert "code" in body

    async def test_my_center_not_found(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with no assigned center returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.get("/v1/milk-center/my-center")
        assert resp.status_code == 404

    async def test_my_center_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/milk-center/my-center")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /v1/milk-center/receive
# ---------------------------------------------------------------------------


class TestReceiveMilk:
    async def test_receive_success(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        center = _mock_center()
        result = MagicMock()
        result.scalar_one_or_none.return_value = center
        mock_db.execute = AsyncMock(return_value=result)

        with patch(
            "app.routers.milk_center.calculate_rate",
            return_value=Decimal("35.50"),
        ):
            resp = await client_as_milk_center.post(
                "/v1/milk-center/receive",
                json={
                    "center_id": str(center.id),
                    "farmer_user_id": str(uuid.uuid4()),
                    "quantity_liters": 10.5,
                    "fat_pct": 4.5,
                    "snf_pct": 8.5,
                    "shift": "morning",
                },
            )
            assert resp.status_code == 201
            body = resp.json()
            assert "rate_per_liter" in body
            assert "total_amount" in body

    async def test_receive_center_not_found(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent center returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.post(
            "/v1/milk-center/receive",
            json={
                "center_id": str(uuid.uuid4()),
                "farmer_user_id": str(uuid.uuid4()),
                "quantity_liters": 10.5,
                "fat_pct": 4.5,
                "snf_pct": 8.5,
                "shift": "morning",
            },
        )
        assert resp.status_code == 404

    async def test_receive_invalid_shift(
        self, client_as_milk_center: AsyncClient
    ) -> None:
        """POST with invalid shift returns 422."""
        resp = await client_as_milk_center.post(
            "/v1/milk-center/receive",
            json={
                "center_id": str(uuid.uuid4()),
                "farmer_user_id": str(uuid.uuid4()),
                "quantity_liters": 10.5,
                "fat_pct": 4.5,
                "snf_pct": 8.5,
                "shift": "afternoon",
            },
        )
        assert resp.status_code == 422

    async def test_receive_missing_fields(
        self, client_as_milk_center: AsyncClient
    ) -> None:
        """POST without required fields returns 422."""
        resp = await client_as_milk_center.post(
            "/v1/milk-center/receive",
            json={"quantity_liters": 10.5},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /v1/milk-center/{center_id}/daily-report
# ---------------------------------------------------------------------------


class TestDailyReport:
    async def test_daily_report_success(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with daily report."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.get(
            f"/v1/milk-center/{uuid.uuid4()}/daily-report"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "summary" in body
        assert "morning" in body
        assert "evening" in body


# ---------------------------------------------------------------------------
# GET /v1/milk-center/{center_id}/farmer-settlements
# ---------------------------------------------------------------------------


class TestFarmerSettlements:
    async def test_settlements_success(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with settlement data."""
        result = MagicMock()
        result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.get(
            f"/v1/milk-center/{uuid.uuid4()}/farmer-settlements"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "settlements" in body
        assert "total_payout_inr" in body


# ---------------------------------------------------------------------------
# GET /v1/milk-center/farmers/search
# ---------------------------------------------------------------------------


class TestSearchFarmers:
    async def test_search_by_phone(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with phone param returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.get(
            "/v1/milk-center/farmers/search?phone=99000"
        )
        assert resp.status_code == 200

    async def test_search_no_params(
        self, client_as_milk_center: AsyncClient
    ) -> None:
        """GET without search params returns 400."""
        resp = await client_as_milk_center.get(
            "/v1/milk-center/farmers/search"
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /v1/milk-center/farmers/enroll
# ---------------------------------------------------------------------------


class TestQuickEnrollFarmer:
    async def test_enroll_success(
        self, client_as_milk_center: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_milk_center.post(
            "/v1/milk-center/farmers/enroll",
            json={
                "name": "Rajesh Kumar",
                "phone": "+919876543210",
                "aadhaar": "123456789012",
            },
        )
        assert resp.status_code == 201

    async def test_enroll_invalid_phone(
        self, client_as_milk_center: AsyncClient
    ) -> None:
        """POST with invalid phone pattern returns 422."""
        resp = await client_as_milk_center.post(
            "/v1/milk-center/farmers/enroll",
            json={
                "name": "Test",
                "phone": "1234567890",
                "aadhaar": "123456789012",
            },
        )
        assert resp.status_code == 422

    async def test_enroll_invalid_aadhaar(
        self, client_as_milk_center: AsyncClient
    ) -> None:
        """POST with invalid Aadhaar returns 422."""
        resp = await client_as_milk_center.post(
            "/v1/milk-center/farmers/enroll",
            json={
                "name": "Test",
                "phone": "+919876543210",
                "aadhaar": "1234",
            },
        )
        assert resp.status_code == 422
