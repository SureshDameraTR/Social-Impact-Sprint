import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, get_db
from app.middleware.csrf import CSRFMiddleware

logger = logging.getLogger(__name__)

from app.routers import (
    auth,
    animals,
    health,
    milk,
    finance,
    shg,
    schemes,
    marketplace,
    income,
    admin,
    weather,
    feed,
    ethno_vet,
    bharat_pashudhan,
    vaccination,
    insurance,
    alerts,
    medicine,
    medicine_log,
    milk_center,
    advisory,
    onboarding,
    iot,
    map_points,
    users,
)


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
    if settings.environment != "development" and not settings.cors_origins:
        raise RuntimeError("CORS_ORIGINS is required in non-development environments")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_settings()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="PashuRaksha ERP",
        description="Livestock management ERP for rural Indian farmers",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    )

    app.add_middleware(CSRFMiddleware)

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

    return app


app = create_app()
