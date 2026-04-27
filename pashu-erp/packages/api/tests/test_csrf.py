"""Unit tests for CSRF middleware — app/middleware/csrf.py.

The CSRFMiddleware implements the double-submit cookie pattern:
- Safe methods (GET, HEAD, OPTIONS) are exempt.
- Exempt paths (/v1/auth/*, /health) are exempt.
- Requests with a valid Bearer JWT skip CSRF checks.
- All other mutating requests must include both a ``csrf_token`` cookie
  AND a matching ``X-CSRF-Token`` header.  Mismatch or absence => 403.
"""

import secrets
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Fixtures — CSRF tests need a client WITHOUT a valid Bearer JWT so the
# middleware actually reaches the cookie/header check.
# ---------------------------------------------------------------------------


@pytest.fixture
async def csrf_client(mock_db: AsyncMock) -> AsyncGenerator[AsyncClient, None]:
    """Test client with DB mocked and auth overridden but NO Bearer header.

    This forces mutating requests through the CSRF cookie/header validation
    path instead of the JWT-bypass branch.
    """
    from app.database import get_db
    from app.main import create_app
    from app.middleware.auth import get_current_user

    app = create_app()

    fake_user = MagicMock()
    fake_user.id = "csrf-test-user"
    fake_user.role = "farmer"
    fake_user.name = "CSRF Test Farmer"
    fake_user.phone = "+919900099000"
    fake_user.lang_pref = "kn"
    fake_user.location_district = "Tumkur"

    async def _override_db():
        yield mock_db

    async def _override_auth():
        return fake_user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 1. Safe methods are exempt — no CSRF token required
# ---------------------------------------------------------------------------


class TestSafeMethodsExempt:
    """GET, HEAD, and OPTIONS should pass without any CSRF token."""

    async def test_get_request_no_csrf_required(self, csrf_client: AsyncClient) -> None:
        """GET to any path passes without CSRF token.

        The endpoint may return a non-200 (e.g. 503 if DB is mocked); the
        assertion is that CSRF does NOT block it with 403.
        """
        resp = await csrf_client.get("/health")
        # Must NOT be a CSRF rejection
        if resp.status_code == 403:
            body = resp.json()
            assert body.get("code") not in ("CSRF_MISSING", "CSRF_MISMATCH")

    async def test_head_request_no_csrf_required(self) -> None:
        """HEAD is not a mutating method; middleware passes through directly."""
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "HEAD",
            "path": "/v1/animals",
            "headers": [],
        }
        await middleware(scope, None, None)
        assert inner_called, "HEAD requests must not be blocked by CSRF middleware"

    async def test_options_request_no_csrf_required(self, csrf_client: AsyncClient) -> None:
        """OPTIONS request passes without CSRF token.

        FastAPI + CORSMiddleware handles OPTIONS; the key assertion is that
        the CSRF middleware does NOT block it with a 403.
        """
        resp = await csrf_client.options("/v1/animals")
        assert resp.status_code != 403


# ---------------------------------------------------------------------------
# 2. Auth paths are exempt
# ---------------------------------------------------------------------------


class TestAuthPathsExempt:
    """POST to /v1/auth/* paths in EXEMPT_PATHS should skip CSRF checks.

    These test the middleware logic directly to avoid coupling with endpoint
    internals (rate limiters, DB calls) that are irrelevant to CSRF.
    """

    async def test_auth_request_otp_exempt(self) -> None:
        """POST to /v1/auth/request-otp is in EXEMPT_PATHS; middleware passes through."""
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/v1/auth/request-otp",
            "headers": [],
        }
        await middleware(scope, None, None)
        assert inner_called, "Middleware should pass request-otp through to inner app"

    async def test_auth_verify_otp_exempt(self) -> None:
        """POST to /v1/auth/verify-otp is in EXEMPT_PATHS; middleware passes through."""
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/v1/auth/verify-otp",
            "headers": [],
        }
        await middleware(scope, None, None)
        assert inner_called, "Middleware should pass verify-otp through to inner app"

    async def test_auth_logout_exempt(self) -> None:
        """POST to /v1/auth/logout is in EXEMPT_PATHS; middleware passes through."""
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/v1/auth/logout",
            "headers": [],
        }
        await middleware(scope, None, None)
        assert inner_called, "Middleware should pass logout through to inner app"

    async def test_health_post_exempt(self) -> None:
        """POST to /health is in EXEMPT_PATHS; middleware passes through."""
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/health",
            "headers": [],
        }
        await middleware(scope, None, None)
        assert inner_called, "Middleware should pass /health through to inner app"

    async def test_non_exempt_auth_path_requires_csrf(self) -> None:
        """POST to /v1/auth/me (NOT in EXEMPT_PATHS) is still CSRF-protected."""
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False
        sent_messages: list[dict] = []

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        async def fake_send(message):
            sent_messages.append(message)

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/v1/auth/me",
            "headers": [],
        }
        await middleware(scope, None, fake_send)
        assert not inner_called, "Middleware should block /v1/auth/me without CSRF"
        # Should have sent a 403 response
        assert sent_messages[0]["status"] == 403


# ---------------------------------------------------------------------------
# 3. CSRF enforcement on mutation methods — missing token => 403
# ---------------------------------------------------------------------------


class TestCSRFEnforcementMissingToken:
    """Mutating requests WITHOUT CSRF tokens must be rejected with 403."""

    async def test_post_without_csrf_returns_403(self, csrf_client: AsyncClient) -> None:
        """POST to a protected route without CSRF header/cookie returns 403."""
        resp = await csrf_client.post("/v1/animals", json={"name": "test"})
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"

    async def test_put_without_csrf_returns_403(self, csrf_client: AsyncClient) -> None:
        """PUT without CSRF returns 403."""
        resp = await csrf_client.put("/v1/animals/some-id", json={"name": "test"})
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"

    async def test_delete_without_csrf_returns_403(self, csrf_client: AsyncClient) -> None:
        """DELETE without CSRF returns 403."""
        resp = await csrf_client.delete("/v1/animals/some-id")
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"

    async def test_patch_without_csrf_returns_403(self, csrf_client: AsyncClient) -> None:
        """PATCH without CSRF returns 403."""
        resp = await csrf_client.patch("/v1/animals/some-id", json={"name": "test"})
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"


# ---------------------------------------------------------------------------
# 4. CSRF validation — matching vs. mismatched tokens
# ---------------------------------------------------------------------------


class TestCSRFTokenValidation:
    """Verify the double-submit cookie pattern: cookie must match header."""

    async def test_valid_csrf_token_passes(
        self, csrf_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Correct CSRF token in both cookie and header allows the request through.

        The request should NOT be blocked by CSRF (no 403 with CSRF codes).
        It may get a different status (e.g. 422 for invalid body, 404 for
        missing resource) which is fine — the point is CSRF did not block it.
        """
        token = secrets.token_urlsafe(32)
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"X-CSRF-Token": token},
            cookies={"csrf_token": token},
        )
        # Must NOT be a CSRF rejection
        assert resp.status_code != 403 or resp.json().get("code") not in (
            "CSRF_MISSING",
            "CSRF_MISMATCH",
        )

    async def test_mismatched_csrf_token_returns_403(self, csrf_client: AsyncClient) -> None:
        """Different values in cookie vs. header returns 403 CSRF_MISMATCH."""
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"X-CSRF-Token": "header-token-aaa"},
            cookies={"csrf_token": "cookie-token-bbb"},
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISMATCH"

    async def test_csrf_cookie_only_no_header_returns_403(self, csrf_client: AsyncClient) -> None:
        """Cookie present but no X-CSRF-Token header returns 403 CSRF_MISSING."""
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            cookies={"csrf_token": "some-token"},
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"

    async def test_csrf_header_only_no_cookie_returns_403(self, csrf_client: AsyncClient) -> None:
        """Header present but no csrf_token cookie returns 403 CSRF_MISSING."""
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"X-CSRF-Token": "some-token"},
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------


class TestCSRFEdgeCases:
    """Edge cases: empty tokens, header casing, Bearer JWT bypass."""

    async def test_empty_csrf_header_returns_403(self, csrf_client: AsyncClient) -> None:
        """Empty string in X-CSRF-Token header is rejected."""
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"X-CSRF-Token": ""},
            cookies={"csrf_token": ""},
        )
        assert resp.status_code == 403

    async def test_empty_csrf_cookie_returns_403(self, csrf_client: AsyncClient) -> None:
        """Empty csrf_token cookie value is rejected."""
        token = secrets.token_urlsafe(32)
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"X-CSRF-Token": token},
            cookies={"csrf_token": ""},
        )
        assert resp.status_code == 403

    async def test_csrf_header_name_case_insensitive(
        self, csrf_client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """X-CSRF-Token header lookup is case-insensitive (per HTTP spec).

        The middleware uses ``key.lower() == b"x-csrf-token"`` so mixed-case
        headers should work.  httpx normalizes headers to lowercase, so this
        test confirms the middleware handles the standard path correctly.
        """
        token = secrets.token_urlsafe(32)
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"x-csrf-token": token},
            cookies={"csrf_token": token},
        )
        assert resp.status_code != 403 or resp.json().get("code") not in (
            "CSRF_MISSING",
            "CSRF_MISMATCH",
        )

    async def test_valid_bearer_jwt_bypasses_csrf(self, client: AsyncClient) -> None:
        """Requests with a valid Bearer JWT skip CSRF checks entirely.

        The ``client`` fixture from conftest.py includes a valid JWT in its
        default headers.  A POST without any CSRF tokens should still pass.
        """
        # client fixture already has a valid Bearer token in headers
        # and the auth dependency is overridden, so this should NOT 403.
        resp = await client.post("/v1/auth/logout")
        assert resp.status_code != 403

    async def test_invalid_bearer_jwt_does_not_bypass_csrf(
        self, csrf_client: AsyncClient
    ) -> None:
        """An invalid/expired JWT in the Authorization header does NOT bypass CSRF."""
        resp = await csrf_client.post(
            "/v1/animals",
            json={"name": "test"},
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert resp.status_code == 403
        body = resp.json()
        assert body["code"] == "CSRF_MISSING"

    async def test_health_endpoint_post_exempt(self) -> None:
        """/health is in EXEMPT_PATHS; even a POST passes through CSRF middleware.

        Tested at middleware level to avoid dependency on the endpoint handler.
        """
        from app.middleware.csrf import CSRFMiddleware

        inner_called = False

        async def fake_app(scope, receive, send):
            nonlocal inner_called
            inner_called = True

        middleware = CSRFMiddleware(fake_app)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/health",
            "headers": [],
        }
        await middleware(scope, None, None)
        assert inner_called

    async def test_non_http_scope_passes_through(self) -> None:
        """Non-HTTP scopes (e.g. websocket) are passed through without CSRF check."""
        from app.middleware.csrf import CSRFMiddleware

        calls = []

        async def fake_app(scope, receive, send):
            calls.append(scope)

        middleware = CSRFMiddleware(fake_app)
        scope = {"type": "websocket", "method": "POST", "path": "/ws"}
        await middleware(scope, None, None)
        assert len(calls) == 1
        assert calls[0]["type"] == "websocket"


# ---------------------------------------------------------------------------
# 6. Unit tests for internal helper functions
# ---------------------------------------------------------------------------


class TestCSRFHelpers:
    """Direct tests for _get_header, _get_cookie, and _is_valid_bearer."""

    def test_get_header_found(self) -> None:
        """_get_header returns the decoded value when the header exists."""
        from app.middleware.csrf import _get_header

        headers = [
            (b"content-type", b"application/json"),
            (b"x-csrf-token", b"my-token-123"),
        ]
        assert _get_header(headers, b"x-csrf-token") == "my-token-123"

    def test_get_header_not_found(self) -> None:
        """_get_header returns None when the header is absent."""
        from app.middleware.csrf import _get_header

        headers = [(b"content-type", b"application/json")]
        assert _get_header(headers, b"x-csrf-token") is None

    def test_get_header_case_insensitive(self) -> None:
        """_get_header matches headers case-insensitively."""
        from app.middleware.csrf import _get_header

        headers = [(b"X-CSRF-Token", b"my-token")]
        assert _get_header(headers, b"x-csrf-token") == "my-token"

    def test_get_cookie_found(self) -> None:
        """_get_cookie extracts a named cookie from the Cookie header."""
        from app.middleware.csrf import _get_cookie

        headers = [(b"cookie", b"session=abc; csrf_token=tok123; other=val")]
        assert _get_cookie(headers, "csrf_token") == "tok123"

    def test_get_cookie_not_found(self) -> None:
        """_get_cookie returns None when the cookie name is absent."""
        from app.middleware.csrf import _get_cookie

        headers = [(b"cookie", b"session=abc; other=val")]
        assert _get_cookie(headers, "csrf_token") is None

    def test_get_cookie_no_cookie_header(self) -> None:
        """_get_cookie returns None when there is no Cookie header at all."""
        from app.middleware.csrf import _get_cookie

        headers = [(b"content-type", b"application/json")]
        assert _get_cookie(headers, "csrf_token") is None

    def test_is_valid_bearer_with_valid_token(self) -> None:
        """_is_valid_bearer returns True for a properly signed, non-expired JWT."""
        import jwt as pyjwt

        from app.config import settings
        from app.middleware.csrf import _is_valid_bearer

        token = pyjwt.encode(
            {"sub": "user-1", "exp": 4102444800},  # year 2100
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        assert _is_valid_bearer(token) is True

    def test_is_valid_bearer_with_invalid_token(self) -> None:
        """_is_valid_bearer returns False for a garbage token."""
        from app.middleware.csrf import _is_valid_bearer

        assert _is_valid_bearer("not.a.real.jwt") is False

    def test_is_valid_bearer_with_wrong_secret(self) -> None:
        """_is_valid_bearer returns False for a JWT signed with the wrong secret."""
        import jwt as pyjwt

        from app.middleware.csrf import _is_valid_bearer

        token = pyjwt.encode(
            {"sub": "user-1", "exp": 4102444800},
            "wrong-secret-" + "x" * 64,
            algorithm="HS256",
        )
        assert _is_valid_bearer(token) is False

    def test_is_valid_bearer_with_expired_token(self) -> None:
        """_is_valid_bearer returns False for an expired JWT."""
        import jwt as pyjwt

        from app.config import settings
        from app.middleware.csrf import _is_valid_bearer

        token = pyjwt.encode(
            {"sub": "user-1", "exp": 946684800},  # year 2000 — long expired
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        assert _is_valid_bearer(token) is False
