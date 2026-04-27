"""Unit tests for Auth endpoints — /v1/auth.

Covers OTP request, OTP verification, JWT issuance, CSRF tokens,
refresh tokens, logout, and protected-route access control.
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import bcrypt
import jwt as pyjwt
import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import _JWT_ALGORITHM, _JWT_SECRET, _make_user

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_PHONE = "+919876543210"
VALID_OTP = "123456"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hash_otp(otp: str) -> str:
    """Hash an OTP the same way the router does."""
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()


def _make_otp_record(
    phone: str = VALID_PHONE,
    otp: str = VALID_OTP,
    attempts: int = 0,
    request_count: int = 1,
    expired: bool = False,
    max_attempts_exceeded: bool = False,
) -> MagicMock:
    """Create a mock OTPRequest ORM object."""
    record = MagicMock()
    record.phone = phone
    record.otp_hash = _hash_otp(otp)
    record.attempts = 3 if max_attempts_exceeded else attempts
    record.request_count = request_count
    record.created_at = datetime.now(timezone.utc) - timedelta(minutes=2)

    if expired:
        record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    else:
        record.expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    return record


def _mock_scalar_result(value):
    """Wrap a value in the Result -> scalar_one_or_none() chain."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _verify_otp_db_side_effects(user, *, otp_record=None, user_exists=True):
    """Build the standard side_effect list for a verify-otp call.

    verify-otp performs these DB calls in order:
      1. SELECT OTPRequest by phone
      2. DELETE OTPRequest (on success)
      3. SELECT User by phone
      4. (if new user) flush after commit + refresh
      5. flush for _create_refresh_token  (db.add + db.flush)
    """
    if otp_record is None:
        otp_record = _make_otp_record()

    effects = [
        _mock_scalar_result(otp_record),      # 1. SELECT OTP
        MagicMock(),                           # 2. DELETE OTP
        _mock_scalar_result(user if user_exists else None),  # 3. SELECT User
    ]
    return effects


# ---------------------------------------------------------------------------
# Auth client fixture — no auth override, DB mocked, rate limiter reset
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset slowapi in-memory rate limiter state between tests.

    The limiter is a module-level singleton; without this, the 5/minute
    limit on /v1/auth/* endpoints is shared across all tests in the session.
    """
    from app.middleware.rate_limit import limiter

    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
async def auth_client(mock_db: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """Test client for auth endpoints.

    Does NOT override get_current_user -- OTP endpoints are pre-auth.
    Overrides only the DB session.
    """
    from app.database import get_db
    from app.main import create_app

    app = create_app()

    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ===========================================================================
# 1. OTP REQUEST -- POST /v1/auth/request-otp
# ===========================================================================


class TestRequestOTP:
    """Tests for POST /v1/auth/request-otp."""

    @patch("app.routers.auth._get_provider")
    async def test_request_otp_valid_phone(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Valid +91 phone number returns 200 and success message."""
        provider = AsyncMock()
        mock_provider_fn.return_value = provider

        mock_db.execute = AsyncMock(return_value=_mock_scalar_result(None))

        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": VALID_PHONE},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "OTP sent successfully"

        provider.send_otp.assert_awaited_once()
        call_args = provider.send_otp.call_args
        assert call_args[0][0] == VALID_PHONE
        sent_otp = call_args[0][1]
        assert len(sent_otp) == 6
        assert sent_otp.isdigit()

    async def test_request_otp_invalid_phone_short(
        self, auth_client: AsyncClient
    ) -> None:
        """Phone number with fewer than 10 digits returns 422."""
        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": "+91987"},
        )
        assert resp.status_code == 422

    async def test_request_otp_invalid_phone_long(
        self, auth_client: AsyncClient
    ) -> None:
        """Phone number with more than 10 digits returns 422."""
        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": "+9198765432100"},
        )
        assert resp.status_code == 422

    async def test_request_otp_missing_phone(
        self, auth_client: AsyncClient
    ) -> None:
        """Request without phone field returns 422."""
        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={},
        )
        assert resp.status_code == 422

    async def test_request_otp_invalid_phone_no_country_code(
        self, auth_client: AsyncClient
    ) -> None:
        """Phone number without +91 prefix returns 422."""
        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": "9876543210"},
        )
        assert resp.status_code == 422

    async def test_request_otp_invalid_phone_wrong_start_digit(
        self, auth_client: AsyncClient
    ) -> None:
        """Indian mobile numbers start with 6-9; digit < 6 returns 422."""
        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": "+911234567890"},
        )
        assert resp.status_code == 422

    @patch("app.routers.auth._get_provider")
    async def test_request_otp_existing_record_updates(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """When an OTP record exists, it is updated (upsert) not duplicated."""
        provider = AsyncMock()
        mock_provider_fn.return_value = provider

        existing = _make_otp_record(request_count=1)
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(existing)
        )

        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": VALID_PHONE},
        )
        assert resp.status_code == 200
        # SELECT + UPDATE = at least 2 execute calls
        assert mock_db.execute.await_count >= 2
        mock_db.commit.assert_awaited()

    @patch("app.routers.auth._get_provider")
    async def test_request_otp_rate_limited_by_request_count(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """request_count >= MAX_OTP_REQUESTS_PER_HOUR returns 429."""
        provider = AsyncMock()
        mock_provider_fn.return_value = provider

        existing = _make_otp_record(request_count=10)
        existing.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(existing)
        )

        resp = await auth_client.post(
            "/v1/auth/request-otp",
            json={"phone": VALID_PHONE},
        )
        assert resp.status_code == 429
        provider.send_otp.assert_not_awaited()


# ===========================================================================
# 2. OTP VERIFICATION -- POST /v1/auth/verify-otp
# ===========================================================================


class TestVerifyOTP:
    """Tests for POST /v1/auth/verify-otp."""

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_valid_mobile(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Correct OTP with mobile client returns access_token + refresh_token."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["role"] == "farmer"
        assert body["user_id"] == str(user.id)

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_valid_web_staff(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Correct OTP with web client + staff role returns cookies."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="admin", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "web",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "user_id" in body
        assert body["role"] == "admin"
        # Web response: token goes in httpOnly cookie, not body
        assert "access_token" not in body

        assert "token" in resp.cookies
        assert "csrf_token" in resp.cookies

    async def test_verify_otp_invalid_code(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Wrong OTP returns 401."""
        otp_record = _make_otp_record(otp=VALID_OTP)
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(otp_record)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": "999999",
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 401
        assert "Invalid or expired OTP" in resp.json()["detail"]

    async def test_verify_otp_expired(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Expired OTP returns 401 and is cleaned up."""
        otp_record = _make_otp_record(expired=True)
        mock_db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_result(otp_record),
                MagicMock(),  # DELETE expired OTP
            ]
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 401

    async def test_verify_otp_max_attempts_exceeded(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """OTP with >= MAX_OTP_ATTEMPTS returns 401 and is deleted."""
        otp_record = _make_otp_record(max_attempts_exceeded=True)
        mock_db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_result(otp_record),
                MagicMock(),  # DELETE exhausted OTP
            ]
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 401

    async def test_verify_otp_no_otp_record(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Phone with no pending OTP returns 401."""
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(None)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 401

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_creates_new_user(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """First-time phone creates a new user with 'farmer' role."""
        mock_provider_fn.return_value = AsyncMock()

        added_objects: list = []
        original_add = mock_db.add

        def capture_add(obj):
            added_objects.append(obj)
            return original_add(obj)

        mock_db.add = MagicMock(side_effect=capture_add)

        async def _refresh(obj):
            if not hasattr(obj, "id") or obj.id is None:
                obj.id = str(uuid.uuid4())
            if not hasattr(obj, "created_at") or obj.created_at is None:
                obj.created_at = datetime.now(timezone.utc)
            if not hasattr(obj, "updated_at") or obj.updated_at is None:
                obj.updated_at = datetime.now(timezone.utc)
            if not hasattr(obj, "location_district"):
                obj.location_district = None

        mock_db.refresh = AsyncMock(side_effect=_refresh)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(None, user_exists=False)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200

        # Find the User object among added objects (skip RefreshToken)
        user_adds = [
            o for o in added_objects
            if hasattr(o, "phone") and o.phone == VALID_PHONE
        ]
        assert len(user_adds) >= 1
        new_user = user_adds[0]
        assert new_user.role == "farmer"
        assert new_user.lang_pref == "kn"
        assert VALID_PHONE[-4:] in new_user.name

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_web_farmer_rejected(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Web client + farmer (non-staff) role returns 403."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "web",
            },
        )
        assert resp.status_code == 403
        detail = resp.json()["detail"].lower()
        assert "staff" in detail or "mobile app" in detail

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_web_vet_allowed(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Web client + vet (staff) role returns 200."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="vet", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "web",
            },
        )
        assert resp.status_code == 200

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_web_milk_center_allowed(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Web client + milk_center (staff) role returns 200."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="milk_center", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "web",
            },
        )
        assert resp.status_code == 200

    async def test_verify_otp_invalid_otp_format(
        self, auth_client: AsyncClient
    ) -> None:
        """OTP that is not exactly 6 digits returns 422."""
        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": "123",
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 422

    async def test_verify_otp_invalid_client_type(
        self, auth_client: AsyncClient
    ) -> None:
        """Invalid client_type returns 422."""
        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "desktop",
            },
        )
        assert resp.status_code == 422


# ===========================================================================
# 3. JWT TOKEN -- Decode and verify claims
# ===========================================================================


class TestJWTToken:
    """Tests for JWT token structure and claims."""

    @patch("app.routers.auth._get_provider")
    async def test_token_contains_user_id_and_role(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """JWT contains sub (user_id), role, and exp claims."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        payload = pyjwt.decode(
            token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM]
        )
        assert payload["sub"] == str(user.id)
        assert payload["role"] == "farmer"
        assert "exp" in payload

    @patch("app.routers.auth._get_provider")
    async def test_token_expiry_matches_settings(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Access token expires at jwt_expire_minutes from settings (30 min)."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        payload = pyjwt.decode(
            token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM]
        )

        from app.config import settings

        expected_minutes = settings.jwt_expire_minutes
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = exp - now

        # Allow 1 minute tolerance for test execution time
        assert delta > timedelta(minutes=expected_minutes - 1)
        assert delta < timedelta(minutes=expected_minutes + 1)

    @patch("app.routers.auth._get_provider")
    async def test_token_accepted_by_protected_endpoint(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """A token from verify-otp is accepted by GET /v1/auth/me."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        # Reset mock for /me DB lookup
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(user)
        )

        me_resp = await auth_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        me_body = me_resp.json()
        assert me_body["user_id"] == str(user.id)
        assert me_body["role"] == "farmer"

    @patch("app.routers.auth._get_provider")
    async def test_verify_otp_issues_refresh_token(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """verify-otp response includes a refresh_token for mobile clients."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "refresh_token" in body
        assert len(body["refresh_token"]) > 0
        assert body["token_type"] == "bearer"  # noqa: S105


# ===========================================================================
# 4. CSRF TOKEN -- Cookie-based CSRF for web clients
# ===========================================================================


class TestCSRFToken:
    """Tests for CSRF token issuance in web flow."""

    @patch("app.routers.auth._get_provider")
    async def test_web_verify_sets_csrf_cookie(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Web verify-otp sets both token and csrf_token cookies."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="admin", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "web",
            },
        )
        assert resp.status_code == 200
        assert "token" in resp.cookies
        assert "csrf_token" in resp.cookies
        assert len(resp.cookies["csrf_token"]) > 0

    @patch("app.routers.auth._get_provider")
    async def test_csrf_token_is_hmac_signed(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """CSRF token has the expected dot-separated HMAC format."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="admin", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "web",
            },
        )
        assert resp.status_code == 200
        csrf = resp.cookies["csrf_token"]
        # HMAC format: <base64url_timestamp>.<base64url_hmac>
        parts = csrf.split(".")
        assert len(parts) == 2
        assert all(len(p) > 0 for p in parts)

    @patch("app.routers.auth._get_provider")
    async def test_mobile_verify_no_csrf_cookie(
        self,
        mock_provider_fn: MagicMock,
        auth_client: AsyncClient,
        mock_db: AsyncMock,
    ) -> None:
        """Mobile verify-otp does NOT set cookies."""
        mock_provider_fn.return_value = AsyncMock()

        user = _make_user(role="farmer", phone=VALID_PHONE)
        mock_db.execute = AsyncMock(
            side_effect=_verify_otp_db_side_effects(user)
        )

        resp = await auth_client.post(
            "/v1/auth/verify-otp",
            json={
                "phone": VALID_PHONE,
                "otp": VALID_OTP,
                "client_type": "mobile",
            },
        )
        assert resp.status_code == 200
        assert "token" not in resp.cookies
        assert "csrf_token" not in resp.cookies


# ===========================================================================
# 5. PROTECTED ROUTES -- Auth enforcement
# ===========================================================================


class TestProtectedRoutes:
    """Tests for auth enforcement on protected endpoints."""

    async def test_no_token_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET /v1/auth/me without Authorization header returns 401."""
        resp = await auth_client.get("/v1/auth/me")
        assert resp.status_code == 401

    async def test_invalid_token_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET /v1/auth/me with malformed JWT returns 401."""
        resp = await auth_client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer not.a.valid.jwt.token"},
        )
        assert resp.status_code == 401

    async def test_expired_token_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET /v1/auth/me with expired JWT returns 401."""
        expired_payload = {
            "sub": str(uuid.uuid4()),
            "role": "farmer",
            "exp": datetime(2020, 1, 1, tzinfo=timezone.utc),
        }
        expired_token = pyjwt.encode(
            expired_payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM
        )

        resp = await auth_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401

    async def test_token_wrong_secret_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """JWT signed with wrong secret is rejected."""
        payload = {
            "sub": str(uuid.uuid4()),
            "role": "farmer",
            "exp": datetime(2099, 1, 1, tzinfo=timezone.utc),
        }
        wrong_secret = "wrong_secret_key" + "x" * 50
        bad_token = pyjwt.encode(
            payload, wrong_secret, algorithm=_JWT_ALGORITHM
        )

        resp = await auth_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert resp.status_code == 401

    async def test_token_missing_sub_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """JWT without 'sub' claim returns 401."""
        payload = {
            "role": "farmer",
            "exp": datetime(2099, 1, 1, tzinfo=timezone.utc),
        }
        token = pyjwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)

        resp = await auth_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    async def test_token_for_nonexistent_user_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Valid JWT for a user_id not in DB returns 401."""
        fake_id = str(uuid.uuid4())
        payload = {
            "sub": fake_id,
            "role": "farmer",
            "exp": datetime(2099, 1, 1, tzinfo=timezone.utc),
        }
        token = pyjwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(None)
        )

        resp = await auth_client.get(
            "/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401


# ===========================================================================
# 6. LOGOUT -- POST /v1/auth/logout
# ===========================================================================


class TestLogout:
    """Tests for POST /v1/auth/logout (requires auth)."""

    async def test_logout_returns_200(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Authenticated POST /v1/auth/logout returns 200."""
        resp = await client.post("/v1/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out"

    async def test_logout_clears_cookies(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Logout response instructs the client to delete auth cookies."""
        resp = await client.post("/v1/auth/logout")
        assert resp.status_code == 200

        set_cookie_headers = [
            v
            for k, v in resp.headers.multi_items()
            if k.lower() == "set-cookie"
        ]
        cookie_names = [h.split("=")[0] for h in set_cookie_headers]
        assert "token" in cookie_names
        assert "csrf_token" in cookie_names

    async def test_logout_no_auth_returns_401(
        self, client_no_auth: AsyncClient
    ) -> None:
        """POST /v1/auth/logout without auth returns 401/403."""
        resp = await client_no_auth.post("/v1/auth/logout")
        assert resp.status_code in (401, 403)


# ===========================================================================
# 7. GET /v1/auth/me -- Authenticated user info
# ===========================================================================


class TestGetMe:
    """Tests for GET /v1/auth/me."""

    async def test_me_returns_user_info(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with valid token returns user profile."""
        resp = await client.get("/v1/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert "user_id" in body
        assert "role" in body
        assert "name" in body

    async def test_me_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401."""
        resp = await client_no_auth.get("/v1/auth/me")
        assert resp.status_code in (401, 403)


# ===========================================================================
# 8. REFRESH TOKEN -- POST /v1/auth/refresh
# ===========================================================================


class TestRefreshToken:
    """Tests for POST /v1/auth/refresh."""

    async def test_refresh_missing_token_returns_422(
        self, auth_client: AsyncClient
    ) -> None:
        """Missing refresh_token in body returns 422."""
        resp = await auth_client.post(
            "/v1/auth/refresh",
            json={},
        )
        assert resp.status_code == 422

    async def test_refresh_invalid_token_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Refresh token not found in DB returns 401."""
        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(None)
        )

        resp = await auth_client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "nonexistent_token_value"},
        )
        assert resp.status_code == 401

    async def test_refresh_revoked_token_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Previously revoked refresh token returns 401."""
        stored = MagicMock()
        stored.user_id = str(uuid.uuid4())
        stored.revoked_at = datetime.now(timezone.utc)
        stored.expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        mock_db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_result(stored),  # SELECT refresh token
                MagicMock(),  # UPDATE revoke all tokens for user
            ]
        )

        resp = await auth_client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "some_raw_token"},
        )
        assert resp.status_code == 401
        assert "revoked" in resp.json()["detail"].lower()

    async def test_refresh_expired_token_returns_401(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Expired refresh token returns 401."""
        stored = MagicMock()
        stored.user_id = str(uuid.uuid4())
        stored.revoked_at = None
        stored.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        mock_db.execute = AsyncMock(
            return_value=_mock_scalar_result(stored)
        )

        resp = await auth_client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "some_raw_token"},
        )
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()

    async def test_refresh_valid_returns_new_token_pair(
        self, auth_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Valid refresh token returns new access_token + refresh_token."""
        user_id = str(uuid.uuid4())
        stored = MagicMock()
        stored.user_id = user_id
        stored.revoked_at = None
        stored.expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        user = _make_user(role="farmer", user_id=user_id, phone=VALID_PHONE)

        mock_db.execute = AsyncMock(
            side_effect=[
                _mock_scalar_result(stored),  # SELECT refresh token
                _mock_scalar_result(user),    # SELECT user
            ]
        )

        resp = await auth_client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "valid_raw_token"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"  # noqa: S105

        # Verify the new access token contains correct claims
        payload = pyjwt.decode(
            body["access_token"], _JWT_SECRET, algorithms=[_JWT_ALGORITHM]
        )
        assert payload["sub"] == user_id
        assert payload["role"] == "farmer"
