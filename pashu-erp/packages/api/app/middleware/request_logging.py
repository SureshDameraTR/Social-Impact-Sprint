import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import request_id_var

logger = logging.getLogger("pashuraksha.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request_id_var.set(request_id)

        start = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start) * 1000, 1)

        # Skip health checks from logs
        if request.url.path != "/health":
            logger.info(
                "%s %s → %s (%.1fms)",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )

        response.headers["X-Request-ID"] = request_id
        return response
