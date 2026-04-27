"""Unit tests for DPDP Consent endpoints — /v1/consent."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient


def _mock_consent(
    purpose: str = "livestock_management",
    status: str = "granted",
) -> MagicMock:
    consent = MagicMock()
    consent.id = uuid.uuid4()
    consent.user_id = uuid.uuid4()
    consent.purpose = purpose
    consent.status = status
    consent.consent_text = "I consent to processing of my livestock data."
    consent.ip_address = "127.0.0.1"
    consent.user_agent = "test-agent"
    consent.created_at = datetime.now(timezone.utc)
    consent.updated_at = datetime.now(timezone.utc)
    consent.deleted_at = None
    return consent


# ---------------------------------------------------------------------------
# POST /v1/consent/grant
# ---------------------------------------------------------------------------


class TestGrantConsent:
    async def test_grant_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST /grant returns 201."""
        resp = await client.post(
            "/v1/consent/grant",
            json={
                "purpose": "livestock_management",
                "consent_text": "I consent to processing of my livestock management data.",
            },
        )
        assert resp.status_code == 201

    async def test_grant_invalid_purpose(self, client: AsyncClient) -> None:
        """POST /grant with invalid purpose returns 422."""
        resp = await client.post(
            "/v1/consent/grant",
            json={
                "purpose": "invalid_purpose",
                "consent_text": "I consent to some processing.",
            },
        )
        assert resp.status_code == 422

    async def test_grant_missing_text(self, client: AsyncClient) -> None:
        """POST /grant without consent_text returns 422."""
        resp = await client.post(
            "/v1/consent/grant",
            json={"purpose": "health_records"},
        )
        assert resp.status_code == 422

    async def test_grant_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST /grant without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/consent/grant",
            json={
                "purpose": "livestock_management",
                "consent_text": "I consent to processing of my livestock management data.",
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /v1/consent/withdraw
# ---------------------------------------------------------------------------


class TestWithdrawConsent:
    async def test_withdraw_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST /withdraw returns 200 when active consent exists."""
        consent = _mock_consent()
        result = MagicMock()
        result.scalar_one_or_none.return_value = consent
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/consent/withdraw",
            json={"purpose": "livestock_management"},
        )
        assert resp.status_code == 200

    async def test_withdraw_not_found(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST /withdraw returns 404 when no active consent exists."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/consent/withdraw",
            json={"purpose": "analytics"},
        )
        assert resp.status_code == 404

    async def test_withdraw_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST /withdraw without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/consent/withdraw",
            json={"purpose": "livestock_management"},
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/consent/my
# ---------------------------------------------------------------------------


class TestListMyConsents:
    async def test_list_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET /my returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/consent/my")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET /my without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/consent/my")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# DELETE /v1/consent/erasure-request
# ---------------------------------------------------------------------------


class TestErasureRequest:
    async def test_erasure_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """DELETE /erasure-request returns 202."""
        result = MagicMock()
        result.rowcount = 0
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.delete("/v1/consent/erasure-request")
        assert resp.status_code == 202
        assert "erasure" in resp.json()["detail"].lower()

    async def test_erasure_no_auth(self, client_no_auth: AsyncClient) -> None:
        """DELETE /erasure-request without auth returns 401/403."""
        resp = await client_no_auth.delete("/v1/consent/erasure-request")
        assert resp.status_code in (401, 403)
