"""Unit tests for Health endpoints — /v1/health."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_health_event() -> MagicMock:
    event = MagicMock()
    event.id = uuid.uuid4()
    event.animal_id = uuid.uuid4()
    event.event_type = "symptom"
    event.description = "Fever and reduced appetite"
    event.symptoms = ["fever", "loss_of_appetite"]
    event.ai_risk_score = 0.7
    event.recommended_action = "Consult vet"
    event.probable_diseases = ["FMD"]
    event.recorded_by = FARMER_USER_ID
    event.event_date = datetime.now(timezone.utc)
    event.created_at = datetime.now(timezone.utc)
    return event


def _mock_animal(user_id: str = FARMER_USER_ID) -> MagicMock:
    animal = MagicMock()
    animal.id = uuid.uuid4()
    animal.user_id = user_id
    animal.species = "cattle"
    animal.name = "Gauri"
    return animal


# ---------------------------------------------------------------------------
# POST /v1/health/log
# ---------------------------------------------------------------------------


class TestLogHealthEvent:
    async def test_log_health_event_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid symptoms returns 201."""
        animal = _mock_animal()
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)
        mock_db.get = AsyncMock(return_value=None)

        resp = await client.post(
            "/v1/health/log",
            json={
                "animal_id": str(animal.id),
                "event_type": "symptom",
                "description": "Fever",
                "symptoms": ["fever"],
            },
        )
        assert resp.status_code == 201

    async def test_log_health_event_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/health/log",
            json={
                "animal_id": str(uuid.uuid4()),
                "event_type": "symptom",
                "description": "Fever",
                "symptoms": ["fever"],
            },
        )
        assert resp.status_code == 404

    async def test_log_health_event_forbidden(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST on another user's animal returns 403."""
        animal = _mock_animal(user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/health/log",
            json={
                "animal_id": str(animal.id),
                "event_type": "symptom",
                "description": "Fever",
                "symptoms": ["fever"],
            },
        )
        assert resp.status_code == 403

    async def test_log_health_event_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post("/v1/health/log", json={"description": "Fever"})
        assert resp.status_code == 422

    async def test_log_health_event_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/health/log",
            json={
                "animal_id": str(uuid.uuid4()),
                "event_type": "symptom",
                "description": "Fever",
                "symptoms": [],
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/health/history/{animal_id}
# ---------------------------------------------------------------------------


class TestGetHealthHistory:
    async def test_get_history_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with paginated data."""
        animal = _mock_animal()
        animal_result = MagicMock()
        animal_result.scalar_one_or_none.return_value = animal

        count_result = MagicMock()
        count_result.scalar.return_value = 1

        event = _mock_health_event()
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [event]

        mock_db.execute = AsyncMock(
            side_effect=[animal_result, count_result, data_result]
        )

        resp = await client.get(f"/v1/health/history/{animal.id}")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_get_history_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/health/history/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /v1/health — List health events
# ---------------------------------------------------------------------------


class TestListHealthEvents:
    async def test_list_events_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with paginated data."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_list_events_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/health")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/health/alerts/map — Admin only
# ---------------------------------------------------------------------------


class TestHealthAlertsMap:
    async def test_alerts_map_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET as admin returns 200."""
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=data_result)

        resp = await client_as_admin.get("/v1/health/alerts/map")
        assert resp.status_code == 200
        body = resp.json()
        assert "alert_count" in body
        assert "markers" in body

    async def test_alerts_map_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/health/alerts/map")
        assert resp.status_code in (401, 403)
