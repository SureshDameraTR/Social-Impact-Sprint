import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import engine, get_db
from app.logging_config import setup_logging
from app.middleware.csrf import CSRFMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.services.errors import ServiceNotConfiguredError, ServiceUnavailableError
from app.services.http_client import close_http_client

logger = logging.getLogger(__name__)

from app.routers import (
    admin,
    advisory,
    alerts,
    animals,
    auth,
    bharat_pashudhan,
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
    users,
    vaccination,
    vet,
    weather,
)


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
                headers.extend([
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy",
                     b"camera=(), microphone=(), geolocation=(self), payment=()"),
                    (b"cross-origin-opener-policy", b"same-origin"),
                ])
                if settings.environment != "development":
                    headers.append(
                        (b"strict-transport-security",
                         b"max-age=31536000; includeSubDomains")
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
    yield
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

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CSRFMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

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
                    checks[name] = (
                        "connected" if resp.status_code == 200 else "error"
                    )
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

    return app


app = create_app()
