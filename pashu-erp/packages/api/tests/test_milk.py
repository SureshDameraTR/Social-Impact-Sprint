"""Unit tests for Milk recording endpoints — /v1/milk."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_yield_log() -> MagicMock:
    log = MagicMock()
    log.id = uuid.uuid4()
    log.animal_id = uuid.uuid4()
    log.user_id = FARMER_USER_ID
    log.quantity_liters = 5.5
    log.session = "morning"
    log.notes = "Good yield"
    log.recorded_at = datetime.now(timezone.utc)
    return log


def _mock_animal(user_id: str = FARMER_USER_ID) -> MagicMock:
    animal = MagicMock()
    animal.id = uuid.uuid4()
    animal.user_id = user_id
    animal.species = "cattle"
    return animal


# ---------------------------------------------------------------------------
# GET /v1/milk — List records
# ---------------------------------------------------------------------------


class TestListMilkRecords:
    async def test_list_milk_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with paginated structure."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/milk")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_list_milk_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/milk")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/milk/today
# ---------------------------------------------------------------------------


class TestGetTodayTotal:
    async def test_today_total_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with today's milk data."""
        row = MagicMock()
        row.total = 12.5
        row.entries = 3
        result = MagicMock()
        result.one.return_value = row
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/milk/today")
        assert resp.status_code == 200
        body = resp.json()
        assert "total_liters" in body
        assert "entries" in body


# ---------------------------------------------------------------------------
# GET /v1/milk/history
# ---------------------------------------------------------------------------


class TestMilkHistory:
    async def test_history_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with history data."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/milk/history")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body


# ---------------------------------------------------------------------------
# GET /v1/milk/daily-summary
# ---------------------------------------------------------------------------


class TestDailySummary:
    async def test_daily_summary_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with daily chart data."""
        result = MagicMock()
        result.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/milk/daily-summary")
        assert resp.status_code == 200
        body = resp.json()
        assert "period_days" in body
        assert "data" in body


# ---------------------------------------------------------------------------
# POST /v1/milk/yield — Record yield
# ---------------------------------------------------------------------------


class TestRecordYield:
    async def test_record_yield_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST with valid data returns 201."""
        animal = _mock_animal()
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/milk/yield",
            json={
                "animal_id": str(animal.id),
                "quantity_liters": 5.5,
                "session": "morning",
            },
        )
        assert resp.status_code == 201

    async def test_record_yield_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/milk/yield",
            json={
                "animal_id": str(uuid.uuid4()),
                "quantity_liters": 5.5,
                "session": "morning",
            },
        )
        assert resp.status_code == 404

    async def test_record_yield_forbidden(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST on another user's animal returns 403."""
        animal = _mock_animal(user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/milk/yield",
            json={
                "animal_id": str(animal.id),
                "quantity_liters": 5.5,
                "session": "morning",
            },
        )
        assert resp.status_code == 403

    async def test_record_yield_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post("/v1/milk/yield", json={"quantity_liters": 5.5})
        assert resp.status_code == 422

    async def test_record_yield_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/milk/yield",
            json={
                "animal_id": str(uuid.uuid4()),
                "quantity_liters": 5.5,
                "session": "morning",
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/milk/center/{center_id}/daily
# ---------------------------------------------------------------------------


class TestDailyCollection:
    async def test_daily_collection_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with daily collection summary."""
        center_id = uuid.uuid4()
        row = MagicMock()
        row.total_liters = 100.5
        row.total_amount = 3500.0
        row.farmer_count = 10
        row.record_count = 20
        result = MagicMock()
        result.one.return_value = row
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/milk/center/{center_id}/daily")
        assert resp.status_code == 200
        body = resp.json()
        assert "total_liters" in body
        assert "farmer_count" in body
