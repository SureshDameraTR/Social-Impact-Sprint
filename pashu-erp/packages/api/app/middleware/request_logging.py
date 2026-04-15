import logging
import time
import uuid

from app.logging_config import request_id_var

logger = logging.getLogger("pashuraksha.http")


class RequestLoggingMiddleware:
    """Log HTTP requests with timing and request ID (pure ASGI middleware)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request ID from headers or generate one
        request_id = None
        for key, value in scope.get("headers", []):
            if key.lower() == b"x-request-id":
                request_id = value.decode("latin-1")
                break
        if not request_id:
            request_id = str(uuid.uuid4())[:8]

        request_id_var.set(request_id)

        method = scope.get("method", "")
        path = scope.get("path", "")
        start = time.perf_counter()
        status_code = 0

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                # Inject X-Request-ID header into the response
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("latin-1")))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # Skip health checks from logs
        if path != "/health":
            logger.info(
                "%s %s → %s (%.1fms)",
                method,
                path,
                status_code,
                duration_ms,
                extra={
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
