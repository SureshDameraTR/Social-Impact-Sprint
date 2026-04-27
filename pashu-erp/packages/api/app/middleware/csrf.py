"""Double-submit cookie CSRF protection middleware (pure ASGI).

Tokens are HMAC-signed and bound to the user's JWT session so that a
token minted for one user cannot be replayed by another.

Token format:  ``base64url(timestamp_bytes) . base64url(hmac_digest)``

The HMAC is computed as:
    HMAC-SHA256(jwt_secret, user_id + ":" + str(issued_at_epoch))

Validation checks:
    1. Token is present in both cookie and header (double-submit).
    2. Cookie value == header value.
    3. Timestamp is not older than ``csrf_token_max_age_seconds``.
    4. HMAC signature matches when recomputed from the JWT claims.
"""

import base64
import hashlib
import hmac as _hmac
import json
import struct
import time

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings

EXEMPT_PATHS = {
    "/v1/auth/request-otp",
    "/v1/auth/verify-otp",
    "/v1/auth/refresh",
    "/v1/auth/logout",
    "/health",
}

MUTATING_METHODS = {b"POST", b"PUT", b"DELETE", b"PATCH"}


# ---------------------------------------------------------------------------
# Token helpers (importable by routers)
# ---------------------------------------------------------------------------


def generate_csrf_token(user_id: str, issued_at: int) -> str:
    """Create an HMAC-signed CSRF token bound to *user_id* and *issued_at*.

    Parameters
    ----------
    user_id:
        The ``sub`` claim from the user's JWT (UUID as string).
    issued_at:
        Unix epoch seconds (typically ``int(time.time())`` at login).

    Returns
    -------
    str
        ``<base64url_timestamp>.<base64url_hmac>``
    """
    ts_bytes = struct.pack(">I", issued_at)
    ts_b64 = base64.urlsafe_b64encode(ts_bytes).rstrip(b"=").decode()

    msg = f"{user_id}:{issued_at}".encode()
    sig = _hmac.new(settings.jwt_secret.encode(), msg, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()

    return f"{ts_b64}.{sig_b64}"


def _pad_b64(s: str) -> str:
    """Re-add base64 padding stripped during generation."""
    return s + "=" * (-len(s) % 4)


def validate_csrf_token(token: str, user_id: str) -> bool:
    """Return True if *token* is a valid, non-expired CSRF token for *user_id*.

    Checks performed:
    1. Token format is ``timestamp_b64.signature_b64``.
    2. Timestamp decodes to a 4-byte big-endian unsigned int.
    3. Timestamp is not older than ``settings.csrf_token_max_age_seconds``.
    4. Recomputed HMAC matches the signature in the token.
    """
    parts = token.split(".")
    if len(parts) != 2:
        return False

    try:
        ts_bytes = base64.urlsafe_b64decode(_pad_b64(parts[0]))
        if len(ts_bytes) != 4:
            return False
        (issued_at,) = struct.unpack(">I", ts_bytes)
    except Exception:
        return False

    # Check expiry
    now = int(time.time())
    if now - issued_at > settings.csrf_token_max_age_seconds:
        return False
    # Reject tokens from the future (clock-skew tolerance: 60 s)
    if issued_at > now + 60:
        return False

    # Recompute HMAC and compare
    msg = f"{user_id}:{issued_at}".encode()
    expected_sig = _hmac.new(
        settings.jwt_secret.encode(), msg, hashlib.sha256
    ).digest()

    try:
        actual_sig = base64.urlsafe_b64decode(_pad_b64(parts[1]))
    except Exception:
        return False

    return _hmac.compare_digest(expected_sig, actual_sig)


# ---------------------------------------------------------------------------
# Internal ASGI helpers
# ---------------------------------------------------------------------------


def _is_valid_bearer(token: str) -> bool:
    """Return True only if *token* is a non-expired JWT signed with our secret."""
    try:
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return True
    except InvalidTokenError:
        return False


def _decode_jwt_claims(token: str) -> dict | None:
    """Decode a JWT and return the payload dict, or None on failure."""
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except InvalidTokenError:
        return None


def _get_header(headers: list, name: bytes) -> str | None:
    """Extract a header value from the raw ASGI header list."""
    for key, value in headers:
        if key.lower() == name:
            return value.decode("latin-1")
    return None


def _get_cookie(headers: list, cookie_name: str) -> str | None:
    """Extract a named cookie from the raw ASGI Cookie header."""
    for key, value in headers:
        if key.lower() == b"cookie":
            for part in value.decode("latin-1").split(";"):
                part = part.strip()
                if part.startswith(f"{cookie_name}="):
                    return part[len(cookie_name) + 1 :]
    return None


async def _send_json_response(send, status_code: int, body: dict):
    """Send a complete JSON error response via raw ASGI."""
    payload = json.dumps(body).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(payload)).encode()),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": payload,
        }
    )


# ---------------------------------------------------------------------------
# ASGI Middleware
# ---------------------------------------------------------------------------


class CSRFMiddleware:
    """Double-submit cookie CSRF protection (pure ASGI middleware).

    For requests that arrive with a session cookie (no Bearer header), the
    middleware validates that the CSRF token is HMAC-signed for the same
    user who owns the session JWT.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        if method.encode() not in MUTATING_METHODS:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return

        headers = scope.get("headers", [])

        # Skip CSRF for valid Bearer JWT tokens (mobile / API clients)
        auth_header = _get_header(headers, b"authorization") or ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token and _is_valid_bearer(token):
                await self.app(scope, receive, send)
                return

        # --- Double-submit check ---
        cookie_token = _get_cookie(headers, "csrf_token")
        header_token = _get_header(headers, b"x-csrf-token")

        if not cookie_token or not header_token:
            await _send_json_response(
                send,
                403,
                {"detail": "CSRF token missing", "code": "CSRF_MISSING"},
            )
            return

        if not _hmac.compare_digest(cookie_token, header_token):
            await _send_json_response(
                send,
                403,
                {"detail": "CSRF token mismatch", "code": "CSRF_MISMATCH"},
            )
            return

        # --- HMAC signature + expiry check ---
        # Extract user_id from the session JWT cookie to verify the CSRF
        # token is bound to this specific session.
        session_jwt = _get_cookie(headers, "token")
        if not session_jwt:
            await _send_json_response(
                send,
                403,
                {"detail": "Session cookie missing", "code": "CSRF_NO_SESSION"},
            )
            return

        claims = _decode_jwt_claims(session_jwt)
        if claims is None:
            await _send_json_response(
                send,
                403,
                {"detail": "Invalid session", "code": "CSRF_INVALID_SESSION"},
            )
            return

        user_id = claims.get("sub", "")
        if not validate_csrf_token(cookie_token, user_id):
            await _send_json_response(
                send,
                403,
                {
                    "detail": "CSRF token invalid or expired",
                    "code": "CSRF_SIGNATURE_INVALID",
                },
            )
            return

        await self.app(scope, receive, send)
