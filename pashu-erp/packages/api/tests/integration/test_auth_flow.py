"""Integration tests for the full OTP authentication flow against real PostgreSQL."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp import OTPRequest

pytestmark = pytest.mark.integration

PHONE = "+919876543210"


async def _request_otp(client: AsyncClient, phone: str = PHONE) -> dict:
    """Request an OTP and return the response JSON."""
    resp = await client.post("/v1/auth/request-otp", json={"phone": phone})
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _get_otp_from_db(db: AsyncSession, phone: str = PHONE) -> str:
    """Retrieve the OTP hash from the database (for verification via bcrypt)."""
    result = await db.execute(select(OTPRequest).where(OTPRequest.phone == phone))
    otp_record = result.scalar_one_or_none()
    assert otp_record is not None, f"No OTP record found for {phone}"
    return otp_record.otp_hash


async def _verify_otp_bruteforce(
    client: AsyncClient, db: AsyncSession, phone: str = PHONE
) -> dict:
    """Request OTP, then brute-force verify it by trying all 6-digit codes.

    In integration tests we cannot read the plaintext OTP (it is bcrypt-hashed).
    Instead we use the console provider which logs the OTP to stdout. But since
    we are testing against a real DB, the simplest approach is to override the
    OTP generation to use a known value. We do this by requesting and then
    checking via bcrypt.

    Actually, the simplest reliable approach: request OTP, read the hash from DB,
    and use bcrypt.checkpw to find the code. But that is 900k checks.

    Better: patch the OTP generator to return a known value for integration tests.
    We monkeypatch at the router level.
    """
    # Not used directly — see the fixture approach below
    pass


@pytest.fixture
def _patch_otp(monkeypatch: pytest.MonkeyPatch):
    """Patch the OTP generator to always return '123456' for predictable tests."""
    import app.routers.auth as auth_module

    monkeypatch.setattr(auth_module, "_generate_otp", lambda: "123456")


@pytest.mark.usefixtures("_patch_otp")
class TestAuthFlow:
    """Full auth flow: request OTP -> verify -> get token -> access protected endpoint."""

    async def test_request_otp(self, integration_client: AsyncClient):
        data = await _request_otp(integration_client)
        assert data["message"] == "OTP sent successfully"

    async def test_verify_otp_creates_user(
        self, integration_client: AsyncClient, db_session: AsyncSession
    ):
        """Requesting + verifying OTP should auto-create a farmer user."""
        phone = "+919876500001"
        await _request_otp(integration_client, phone)

        resp = await integration_client.post(
            "/v1/auth/verify-otp",
            json={"phone": phone, "otp": "123456", "client_type": "mobile"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["role"] == "farmer"
        assert body["user_id"]

    async def test_invalid_otp_rejected(self, integration_client: AsyncClient):
        phone = "+919876500002"
        await _request_otp(integration_client, phone)

        resp = await integration_client.post(
            "/v1/auth/verify-otp",
            json={"phone": phone, "otp": "000000", "client_type": "mobile"},
        )
        assert resp.status_code == 401

    async def test_access_protected_endpoint_with_token(
        self, integration_client: AsyncClient
    ):
        """Full flow: OTP -> token -> GET /v1/auth/me."""
        phone = "+919876500003"
        await _request_otp(integration_client, phone)

        verify_resp = await integration_client.post(
            "/v1/auth/verify-otp",
            json={"phone": phone, "otp": "123456", "client_type": "mobile"},
        )
        assert verify_resp.status_code == 200
        token = verify_resp.json()["access_token"]

        me_resp = await integration_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["role"] == "farmer"

    async def test_refresh_token_rotation(self, integration_client: AsyncClient):
        """Verify refresh token can be exchanged for a new token pair."""
        phone = "+919876500004"
        await _request_otp(integration_client, phone)

        verify_resp = await integration_client.post(
            "/v1/auth/verify-otp",
            json={"phone": phone, "otp": "123456", "client_type": "mobile"},
        )
        assert verify_resp.status_code == 200
        tokens = verify_resp.json()
        refresh_token = tokens["refresh_token"]

        # Exchange refresh token
        refresh_resp = await integration_client.post(
            "/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["refresh_token"] != refresh_token  # rotated

        # Old refresh token should now be rejected
        reuse_resp = await integration_client.post(
            "/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert reuse_resp.status_code == 401

    async def test_unauthenticated_access_rejected(self, integration_client: AsyncClient):
        """Requests without a token should get 401."""
        resp = await integration_client.get("/v1/auth/me")
        assert resp.status_code == 401
