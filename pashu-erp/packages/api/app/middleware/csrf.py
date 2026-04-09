"""Double-submit cookie CSRF protection middleware."""

import hmac

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

EXEMPT_PATHS = {
    "/v1/auth/request-otp",
    "/v1/auth/verify-otp",
    "/v1/auth/logout",
    "/health",
}

MUTATING_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
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
