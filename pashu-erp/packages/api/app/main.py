import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    from circuitbreaker import CircuitBreakerError
except ImportError:
    CircuitBreakerError = None
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIASGIMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, get_db
from app.logging_config import setup_logging
from app.middleware.csrf import CSRFMiddleware
from app.middleware.rate_limit import get_client_ip, limiter
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import (
    admin,
    advisory,
    alerts,
    animals,
    auth,
    bharat_pashudhan,
    consent,
    ethno_vet,
    feed,
    files,
    finance,
    health,
    income,
    insurance,
    iot,
    map_points,
    marketplace,
    medicine,
    medicine_log,
    milk,
    milk_center,
    onboarding,
    reference,
    schemes,
    shg,
    storage,
    users,
    vaccination,
    vet,
    weather,
)
from app.services.errors import ServiceNotConfiguredError, ServiceUnavailableError
from app.services.http_client import close_http_client

logger = logging.getLogger(__name__)


class ContentSizeLimitMiddleware:
    """Reject request bodies larger than a given limit (pure ASGI middleware).

    Returns 413 Payload Too Large if Content-Length exceeds the threshold.
    Also enforces the limit on streaming bodies without Content-Length.
    """

    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check Content-Length header if present
        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                if int(content_length) > self.MAX_BODY_SIZE:
                    response = JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large", "code": "PAYLOAD_TOO_LARGE"},
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass

        # Wrap receive to track streaming body size
        body_size = 0

        async def size_limited_receive():
            nonlocal body_size
            message = await receive()
            if message.get("type") == "http.request":
                body_size += len(message.get("body", b""))
                if body_size > self.MAX_BODY_SIZE:
                    raise HTTPException(status_code=413, detail="Request body too large")
            return message

        await self.app(scope, size_limited_receive, send)


class SecurityHeadersMiddleware:
    """Add security headers to all responses (pure ASGI middleware)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"referrer-policy", b"strict-origin-when-cross-origin"),
                        (
                            b"permissions-policy",
                            b"camera=(), microphone=(), geolocation=(self), payment=()",
                        ),
                        (b"cross-origin-opener-policy", b"same-origin"),
                        (b"cross-origin-embedder-policy", b"require-corp"),
                        (
                            b"content-security-policy",
                            b"default-src 'self'; script-src 'self'; "
                            b"style-src 'self' 'unsafe-inline'; "
                            b"img-src 'self' data: blob:; font-src 'self'; "
                            b"frame-ancestors 'none'; base-uri 'self'; "
                            b"form-action 'self'",
                        ),
                    ]
                )
                if settings.environment != "development":
                    headers.append(
                        (b"strict-transport-security", b"max-age=31536000; includeSubDomains")
                    )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_headers)


def _validate_settings():
    """Fail fast if required settings are missing or insecure."""
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is required")
    if len(settings.jwt_secret) < 64:
        raise RuntimeError(
            "JWT_SECRET must be at least 64 hex characters (256 bits). "
            "Generate with: openssl rand -hex 32"
        )
    if settings.environment != "development" and not settings.aadhaar_hash_secret:
        raise RuntimeError("AADHAAR_HASH_SECRET must be set in production")
    if settings.environment != "development" and not settings.sarvam_api_key:
        raise RuntimeError("SARVAM_API_KEY is required in non-development environments")
    if not settings.cors_origins:
        if settings.environment == "development":
            settings.cors_origins = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8081"
            logger.info("CORS_ORIGINS not set — using development defaults")
        else:
            raise RuntimeError("CORS_ORIGINS is required in non-development environments")

    service_urls = [
        ("WEATHER_API_URL", settings.weather_api_url),
        ("BHARAT_PASHUDHAN_API_URL", settings.bharat_pashudhan_api_url),
        ("IOT_GATEWAY_URL", settings.iot_gateway_url),
        ("STORAGE_API_URL", settings.storage_api_url),
    ]
    if settings.environment == "development":
        for name, val in service_urls:
            if not val:
                logger.warning("%s not set — related endpoints will return 503", name)
    else:
        for name, val in service_urls:
            if not val:
                raise RuntimeError(f"{name} is required in non-development environments")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_settings()
    app.state.start_time = datetime.now(timezone.utc)

    # Initialize Open-Meteo weather service on app state
    from app.services.http_client import get_http_client
    from app.services.open_meteo import OpenMeteoService

    http_client = await get_http_client()
    app.state.open_meteo = OpenMeteoService(
        http_client=http_client,
        base_url=settings.open_meteo_base_url,
        cache_ttl=settings.weather_cache_ttl_seconds,
    )

    # Initialize S3 storage service (only if credentials are configured)
    if settings.s3_access_key:
        from aiobotocore.session import AioSession

        from app.services.storage_service import S3StorageService

        s3_session = AioSession()
        s3_ctx = s3_session.create_client(
            "s3",
            endpoint_url=settings.s3_endpoint_url or None,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )
        app.state.s3_client_ctx = s3_ctx
        app.state.s3_raw = await s3_ctx.__aenter__()
        app.state.s3_storage = S3StorageService(
            s3_client=app.state.s3_raw,
            bucket=settings.s3_bucket_name,
            presigned_expiry=settings.s3_presigned_url_expiry,
        )

    yield
    if hasattr(app.state, "s3_client_ctx"):
        await app.state.s3_client_ctx.__aexit__(None, None, None)
    await close_http_client()
    await engine.dispose()


def create_app() -> FastAPI:
    setup_logging(settings.environment)

    docs_url = "/docs" if settings.environment == "development" else None
    redoc_url = "/redoc" if settings.environment == "development" else None

    app = FastAPI(
        title="PashuRaksha ERP",
        description="Livestock management ERP for rural Indian farmers",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )

    # Set development CORS defaults before reading (lifespan runs later)
    if settings.environment == "development" and not settings.cors_origins:
        settings.cors_origins = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8081"
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

    app.state.limiter = limiter
    app.add_middleware(SlowAPIASGIMiddleware)
    app.add_middleware(ContentSizeLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    # CORS must be outermost (added last) so it can set headers on all
    # responses, including errors from inner middleware (CSRF 403, etc.)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    )

    app.include_router(auth.router)
    app.include_router(animals.router)
    app.include_router(health.router)
    app.include_router(milk.router)
    app.include_router(finance.router)
    app.include_router(shg.router)
    app.include_router(schemes.router)
    app.include_router(marketplace.router)
    app.include_router(income.router)
    app.include_router(admin.router)
    app.include_router(weather.router)
    app.include_router(feed.router)
    app.include_router(ethno_vet.router)
    app.include_router(bharat_pashudhan.router)
    app.include_router(vaccination.router)
    app.include_router(insurance.router)
    app.include_router(alerts.router)
    app.include_router(medicine.router)
    app.include_router(medicine_log.router)
    app.include_router(milk_center.router)
    app.include_router(advisory.router)
    app.include_router(onboarding.router)
    app.include_router(iot.router)
    app.include_router(map_points.router)
    app.include_router(users.router)
    app.include_router(reference.router)
    app.include_router(files.router)
    app.include_router(vet.router)
    app.include_router(consent.router)
    app.include_router(storage.router)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        logger.warning(
            "Rate limit exceeded",
            extra={"client_ip": get_client_ip(request), "path": request.url.path},
        )
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "code": "RATE_LIMITED",
            },
        )

    @app.exception_handler(ServiceNotConfiguredError)
    async def not_configured_handler(request, exc):
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc), "code": "SERVICE_NOT_CONFIGURED"},
        )

    @app.exception_handler(ServiceUnavailableError)
    async def unavailable_handler(request, exc):
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc), "code": "SERVICE_UNAVAILABLE"},
        )

    if CircuitBreakerError is not None:
        @app.exception_handler(CircuitBreakerError)
        async def circuit_breaker_handler(request: Request, exc: CircuitBreakerError):
            breaker = exc._breaker if hasattr(exc, "_breaker") else None
            name = breaker.name if breaker else "unknown"
            logger.warning(
                "Circuit breaker open — request rejected",
                extra={"service": name, "path": request.url.path},
            )
            return JSONResponse(
                status_code=503,
                content={
                    "detail": f"Service '{name}' is temporarily unavailable. Please retry later.",
                    "code": "CIRCUIT_OPEN",
                },
            )

    @app.get("/health")
    async def healthcheck():
        try:
            async for session in get_db():
                await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
        except Exception:
            logger.exception("Health check failed")
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "database": "disconnected"},
            )

    @app.get("/ready")
    async def readiness():
        """Readiness probe -- checks all dependencies."""
        checks = {"database": "unknown", "weather": "unknown", "iot": "unknown"}

        # Check DB
        try:
            async for session in get_db():
                await session.execute(text("SELECT 1"))
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "disconnected"

        # Check external services (just connectivity, not full requests)
        from app.services.http_client import get_http_client

        for name, url in [
            ("weather", settings.weather_api_url),
            ("iot", settings.iot_gateway_url),
        ]:
            if url:
                try:
                    parsed = urlparse(url)
                    health_url = f"{parsed.scheme}://{parsed.netloc}/health"
                    client = await get_http_client()
                    resp = await client.get(health_url, timeout=3.0)
                    checks[name] = "connected" if resp.status_code == 200 else "error"
                except Exception:
                    checks[name] = "unreachable"
            else:
                checks[name] = "not_configured"

        all_ok = checks["database"] == "connected"
        status_code = 200 if all_ok else 503
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if all_ok else "not_ready",
                "checks": checks,
            },
        )

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Basic metrics for monitoring."""
        now = datetime.now(timezone.utc)
        start = getattr(app.state, "start_time", None)
        uptime = (now - start).total_seconds() if start else 0
        return {
            "uptime_seconds": round(uptime, 1),
            "status": "running",
        }

    return app


app = create_app()
