"""Double-submit cookie CSRF protection middleware (pure ASGI)."""

import hmac
import json

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings

EXEMPT_PATHS = {
    "/v1/auth/request-otp",
    "/v1/auth/verify-otp",
    "/v1/auth/logout",
    "/health",
}

MUTATING_METHODS = {b"POST", b"PUT", b"DELETE", b"PATCH"}


def _is_valid_bearer(token: str) -> bool:
    """Return True only if *token* is a non-expired JWT signed with our secret."""
    try:
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return True
    except InvalidTokenError:
        return False


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
                    return part[len(cookie_name) + 1:]
    return None


async def _send_json_response(send, status_code: int, body: dict):
    """Send a complete JSON error response via raw ASGI."""
    payload = json.dumps(body).encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": status_code,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(payload)).encode()),
        ],
    })
    await send({
        "type": "http.response.body",
        "body": payload,
    })


class CSRFMiddleware:
    """Double-submit cookie CSRF protection (pure ASGI middleware)."""

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

        # Skip CSRF for valid Bearer JWT tokens
        auth_header = _get_header(headers, b"authorization") or ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token and _is_valid_bearer(token):
                await self.app(scope, receive, send)
                return

        cookie_token = _get_cookie(headers, "csrf_token")
        header_token = _get_header(headers, b"x-csrf-token")

        if not cookie_token or not header_token:
            await _send_json_response(
                send, 403,
                {"detail": "CSRF token missing", "code": "CSRF_MISSING"},
            )
            return

        if not hmac.compare_digest(cookie_token, header_token):
            await _send_json_response(
                send, 403,
                {"detail": "CSRF token mismatch", "code": "CSRF_MISMATCH"},
            )
            return

        await self.app(scope, receive, send)
