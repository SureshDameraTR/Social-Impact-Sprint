"""PashuRaksha Mock External Services.

Mimics real external services (weather, registry, IoT, storage) so the main
PashuRaksha API can make real HTTP calls during development and testing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import weather, registry, iot, storage

app = FastAPI(
    title="PashuRaksha Mock Services",
    description="Mock external services for PashuRaksha ERP development",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(registry.router)
app.include_router(iot.router)
app.include_router(storage.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "pashuraksha-mock-services"}
