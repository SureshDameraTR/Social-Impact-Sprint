from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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
    milk_center,
    advisory,
    onboarding,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="PashuRaksha ERP",
        description="Livestock management ERP for rural Indian farmers",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
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

    # --- Future-scope modules ---
    app.include_router(weather.router)
    app.include_router(feed.router)
    app.include_router(ethno_vet.router)
    app.include_router(bharat_pashudhan.router)
    app.include_router(vaccination.router)
    app.include_router(insurance.router)
    app.include_router(alerts.router)
    app.include_router(medicine.router)
    app.include_router(milk_center.router)
    app.include_router(advisory.router)
    app.include_router(onboarding.router)

    @app.get("/health")
    async def healthcheck():
        return {"status": "healthy", "service": "pashuraksha-api"}

    return app


app = create_app()
