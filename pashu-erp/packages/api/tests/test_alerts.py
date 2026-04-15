"""Unit tests for Community Alert endpoints — /v1/alerts."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_alert() -> MagicMock:
    alert = MagicMock()
    alert.id = uuid.uuid4()
    alert.reported_by = FARMER_USER_ID
    alert.disease_name = "FMD Outbreak"
    alert.lat = 13.34
    alert.lon = 77.1
    alert.radius_km = 5.0
    alert.severity = "critical"
    alert.verified = False
    alert.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
    alert.created_at = datetime.now(timezone.utc)
    return alert


# ---------------------------------------------------------------------------
# POST /v1/alerts/report
# ---------------------------------------------------------------------------


class TestReportAlert:
    async def test_report_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        resp = await client.post(
            "/v1/alerts/report",
            json={
                "disease_name": "FMD Outbreak",
                "lat": 13.34,
                "lon": 77.1,
                "radius_km": 5.0,
                "severity": "critical",
            },
        )
        assert resp.status_code == 201

    async def test_report_invalid_severity(self, client: AsyncClient) -> None:
        """POST with invalid severity enum returns 422."""
        resp = await client.post(
            "/v1/alerts/report",
            json={
                "disease_name": "FMD Outbreak",
                "lat": 13.34,
                "lon": 77.1,
                "radius_km": 5.0,
                "severity": "high",
            },
        )
        assert resp.status_code == 422

    async def test_report_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post(
            "/v1/alerts/report",
            json={"disease_name": "FMD"},
        )
        assert resp.status_code == 422

    async def test_report_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/alerts/report",
            json={
                "disease_name": "FMD",
                "lat": 13.34,
                "lon": 77.1,
                "radius_km": 5.0,
                "severity": "critical",
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/alerts/nearby
# ---------------------------------------------------------------------------


class TestNearbyAlerts:
    async def test_nearby_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with valid coords returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/alerts/nearby?lat=13.34&lon=77.1")
        assert resp.status_code == 200

    async def test_nearby_missing_coords(self, client: AsyncClient) -> None:
        """GET without lat/lon returns 422."""
        resp = await client.get("/v1/alerts/nearby")
        assert resp.status_code == 422

    async def test_nearby_invalid_lat(self, client: AsyncClient) -> None:
        """GET with lat out of range returns 422."""
        resp = await client.get("/v1/alerts/nearby?lat=100&lon=77.1")
        assert resp.status_code == 422

    async def test_nearby_with_radius(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with custom radius returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/alerts/nearby?lat=13.34&lon=77.1&radius=25")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# PATCH /v1/alerts/{id}/verify
# ---------------------------------------------------------------------------


class TestVerifyAlert:
    async def test_verify_as_vet(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH as vet returns 200."""
        alert = _mock_alert()
        result = MagicMock()
        result.scalar_one_or_none.return_value = alert
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_vet.patch(f"/v1/alerts/{alert.id}/verify")
        assert resp.status_code == 200

    async def test_verify_as_admin(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH as admin returns 200."""
        alert = _mock_alert()
        result = MagicMock()
        result.scalar_one_or_none.return_value = alert
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_admin.patch(f"/v1/alerts/{alert.id}/verify")
        assert resp.status_code == 200

    async def test_verify_as_farmer_forbidden(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH as farmer returns 403."""
        alert = _mock_alert()
        resp = await client.patch(f"/v1/alerts/{alert.id}/verify")
        assert resp.status_code == 403

    async def test_verify_not_found(
        self, client_as_admin: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """PATCH on nonexistent alert returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client_as_admin.patch(f"/v1/alerts/{uuid.uuid4()}/verify")
        assert resp.status_code == 404
