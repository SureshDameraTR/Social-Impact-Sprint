"""Double-submit cookie CSRF protection middleware."""

import hmac

import jwt
from jwt.exceptions import InvalidTokenError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings

EXEMPT_PATHS = {
    "/v1/auth/request-otp",
    "/v1/auth/verify-otp",
    "/v1/auth/logout",
    "/health",
}

MUTATING_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


def _is_valid_bearer(token: str) -> bool:
    """Return True only if *token* is a non-expired JWT signed with our secret."""
    try:
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return True
    except InvalidTokenError:
        return False


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Only skip CSRF for Bearer tokens that contain a valid JWT.
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # strip "Bearer " prefix
            if token and _is_valid_bearer(token):
                return await call_next(request)

        cookie_token = request.cookies.get("csrf_token")
        header_token = request.headers.get("x-csrf-token")

        if not cookie_token or not header_token:
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing", "code": "CSRF_MISSING"},
            )

        if not hmac.compare_digest(cookie_token, header_token):
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token mismatch", "code": "CSRF_MISMATCH"},
            )

        return await call_next(request)
