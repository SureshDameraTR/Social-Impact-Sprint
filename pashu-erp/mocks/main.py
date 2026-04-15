"""PashuRaksha Mock External Services.

Mimics real external services (weather, registry, IoT, storage) so the main
PashuRaksha API can make real HTTP calls during development and testing.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import weather, registry, iot, storage

app = FastAPI(
    title="PashuRaksha Mock Services",
    description="Mock external services for PashuRaksha ERP development",
    version="0.1.0",
)

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:8081"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(registry.router)
app.include_router(iot.router)
app.include_router(storage.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "pashuraksha-mock-services"}
