# Phase 2: Production Hardening — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace all mock/stub endpoints with real HTTP client calls to configurable mock backends, migrate hardcoded data to database, fix silent error handling, and wire empty button handlers.

**Architecture:** Separate FastAPI mock service (port 8001) implements weather, registry, IoT, and storage APIs. PashuRaksha API makes real httpx calls to configurable URLs. Single Alembic migration for reference data. Global snackbar for mobile error handling.

**Tech Stack:** FastAPI, httpx, Alembic, SQLAlchemy, react-native-paper Snackbar, expo-image-picker, expo-av

---

## Task 1: Mock Service — Scaffold + Weather Router

**Files:**
- Create: `mocks/main.py`
- Create: `mocks/requirements.txt`
- Create: `mocks/Dockerfile`
- Create: `mocks/routers/__init__.py`
- Create: `mocks/routers/weather.py`
- Create: `mocks/data/karnataka_districts.json`

**Step 1: Create mock service scaffold**

`mocks/requirements.txt`:
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.9
```

`mocks/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import weather, registry, iot, storage

app = FastAPI(title="PashuRaksha Mock Backends", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(registry.router)
app.include_router(iot.router)
app.include_router(storage.router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-backends"}
```

`mocks/Dockerfile`:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Step 2: Create Karnataka districts data**

`mocks/data/karnataka_districts.json`:
```json
{
  "dharwad": {"lat": 15.46, "lon": 75.01, "elevation": 727},
  "belgaum": {"lat": 15.85, "lon": 74.50, "elevation": 784},
  "mysore": {"lat": 12.30, "lon": 76.66, "elevation": 770},
  "tumkur": {"lat": 13.34, "lon": 77.10, "elevation": 822},
  "shimoga": {"lat": 13.93, "lon": 75.57, "elevation": 569},
  "hassan": {"lat": 13.01, "lon": 76.10, "elevation": 978},
  "mandya": {"lat": 12.52, "lon": 76.90, "elevation": 694},
  "davanagere": {"lat": 14.47, "lon": 75.92, "elevation": 597},
  "haveri": {"lat": 14.79, "lon": 75.40, "elevation": 558},
  "raichur": {"lat": 16.21, "lon": 77.37, "elevation": 407},
  "bagalkot": {"lat": 16.18, "lon": 75.70, "elevation": 533},
  "bidar": {"lat": 17.91, "lon": 77.52, "elevation": 670}
}
```

**Step 3: Create weather router**

`mocks/routers/weather.py` — Three endpoints:
- `GET /api/weather/forecast` — Generates realistic forecasts using district coordinates and seasonal patterns (monsoon June-Sep high rainfall, summer Mar-May high temps, winter Dec-Feb low temps). Uses deterministic seed from district+date for consistency.
- `GET /api/weather/alerts` — Returns weather alerts based on seasonal hazards (heat wave in summer, flood risk in monsoon).
- `POST /api/weather/tts` — Returns a small base64-encoded WAV audio placeholder. Accepts `{district, language_code}`.

Response matches `WeatherForecast` schema: `{date, district, temp_min, temp_max, humidity, rainfall_mm, wind_speed, condition, heat_stress_index}`.

Heat stress index formula: `THI = 0.8 * T + (RH/100) * (T - 14.4) + 46.4`

**Step 4: Verify mock starts**

```bash
cd mocks && pip install -r requirements.txt && uvicorn main:app --port 8001
# Test: curl http://localhost:8001/api/weather/forecast?district=dharwad&days=3
```

**Step 5: Commit**
```bash
git add mocks/
git commit -m "feat: scaffold mock backend service with weather router"
```

---

## Task 2: Mock Service — Bharat Pashudhan Registry Router

**Files:**
- Create: `mocks/routers/registry.py`
- Create: `mocks/data/breeds.json`

**Step 1: Create breeds reference data**

`mocks/data/breeds.json` — ICAR breed codes for cattle, buffalo, goat, sheep:
```json
{
  "cattle": [
    {"code": "GIR001", "name": "Gir", "origin": "Gujarat"},
    {"code": "SAH001", "name": "Sahiwal", "origin": "Punjab"},
    {"code": "RED001", "name": "Red Sindhi", "origin": "Sindh"},
    {"code": "THR001", "name": "Tharparkar", "origin": "Rajasthan"},
    {"code": "KAN001", "name": "Kangayam", "origin": "Tamil Nadu"},
    {"code": "HF001", "name": "Holstein Friesian", "origin": "Imported"},
    {"code": "JER001", "name": "Jersey", "origin": "Imported"}
  ],
  "buffalo": [
    {"code": "MUR001", "name": "Murrah", "origin": "Haryana"},
    {"code": "JAF001", "name": "Jaffarabadi", "origin": "Gujarat"},
    {"code": "SUR001", "name": "Surti", "origin": "Gujarat"}
  ],
  "goat": [
    {"code": "JAM001", "name": "Jamunapari", "origin": "UP"},
    {"code": "BEE001", "name": "Beetal", "origin": "Punjab"},
    {"code": "OSM001", "name": "Osmanabadi", "origin": "Maharashtra"},
    {"code": "BLK001", "name": "Black Bengal", "origin": "West Bengal"}
  ],
  "sheep": [
    {"code": "BAN001", "name": "Bannur", "origin": "Karnataka"},
    {"code": "DEC001", "name": "Deccani", "origin": "Maharashtra"},
    {"code": "NEL001", "name": "Nellore", "origin": "Andhra Pradesh"}
  ]
}
```

**Step 2: Create registry router**

`mocks/routers/registry.py` — Two endpoints:
- `GET /api/registry/animals/{pashu_aadhaar_id}` — Validates 12-digit format (must start with `IN`). Generates deterministic animal record from the ID (seeded by ID hash): species, breed, owner details, vaccination history, insurance. Returns 404 for IDs not matching format.
- `POST /api/registry/sync` — Accepts `{animal_id, local_data}`, returns `{status: "synced", last_sync: "..."}`.

**Step 3: Verify**
```bash
curl http://localhost:8001/api/registry/animals/IN29180001234
# Should return full animal record JSON
curl http://localhost:8001/api/registry/animals/INVALID
# Should return 404
```

**Step 4: Commit**
```bash
git add mocks/routers/registry.py mocks/data/breeds.json
git commit -m "feat: add Bharat Pashudhan registry mock with INAPH data model"
```

---

## Task 3: Mock Service — IoT Gateway Router

**Files:**
- Create: `mocks/routers/iot.py`
- Create: `mocks/data/sample_devices.json`

**Step 1: Create sample device fleet**

`mocks/data/sample_devices.json` — 8-10 devices across different types (smart_collar, ear_tag_sensor, bolus_sensor, milk_meter, pedometer) assigned to animals with Pashu Aadhaar IDs.

**Step 2: Create IoT router**

`mocks/routers/iot.py` — Four endpoints:
- `GET /api/iot/devices` — List devices with optional filters (`?status=active&type=smart_collar`). Returns device metadata: id, type, firmware_version, assigned_animal_id, last_seen, battery_pct, status.
- `GET /api/iot/devices/{device_id}` — Single device detail.
- `GET /api/iot/devices/{device_id}/latest` — Latest telemetry reading per metric type. Generates realistic values: body_temperature (38.0-39.0°C ± noise), activity (80-200 steps/hr), rumination (40-60 min/hr), GPS (near Karnataka coords).
- `GET /api/iot/telemetry` — Historical telemetry with `device_id`, `metric`, `from`, `to` params. Generates time-series at 15-minute intervals. Occasionally injects anomalies (fever spike, estrus activity pattern).

Reference thresholds in response headers or separate endpoint:
- Temperature fever: >39.5°C
- Low rumination: <25 min/hr
- Estrus indicator: activity >350 steps/hr sustained >4hrs

**Step 3: Verify**
```bash
curl http://localhost:8001/api/iot/devices
curl "http://localhost:8001/api/iot/devices/SC-GIR-0042/latest"
curl "http://localhost:8001/api/iot/telemetry?device_id=SC-GIR-0042&metric=body_temperature&from=2026-04-08T00:00:00Z&to=2026-04-09T00:00:00Z"
```

**Step 4: Commit**
```bash
git add mocks/routers/iot.py mocks/data/sample_devices.json
git commit -m "feat: add IoT gateway mock with realistic livestock telemetry"
```

---

## Task 4: Mock Service — Storage Router

**Files:**
- Create: `mocks/routers/storage.py`

**Step 1: Create storage router**

`mocks/routers/storage.py` — Three endpoints:
- `POST /api/storage/files` — Accepts multipart upload. Fields: `file` (binary, required), `category` (insurance_photo/claim_evidence/ear_tag_photo), `entity_type` (animal/policy/claim), `entity_id` (UUID). Validates content_type (image/jpeg, image/png only). Saves to `./uploads/{uuid}`. Returns metadata JSON with file_id, url, filename, content_type, size_bytes, category, entity_type, entity_id, created_at.
- `GET /api/storage/files/{file_id}` — Returns file bytes with correct Content-Type header. 404 if not found.
- `GET /api/storage/files` — List files filtered by `entity_type` and `entity_id`. Returns array of metadata.

In-memory metadata store (dict). Files persisted to disk.

**Step 2: Create uploads directory**
```bash
mkdir -p mocks/uploads && echo "*\n!.gitkeep" > mocks/uploads/.gitignore
```

**Step 3: Verify**
```bash
curl -X POST http://localhost:8001/api/storage/files \
  -F "file=@test.jpg" -F "category=insurance_photo" \
  -F "entity_type=animal" -F "entity_id=test-uuid"
# Should return metadata JSON with file_id
```

**Step 4: Commit**
```bash
git add mocks/routers/storage.py mocks/uploads/.gitignore
git commit -m "feat: add file storage mock for insurance photo uploads"
```

---

## Task 5: API — Weather Service HTTP Client

**Files:**
- Modify: `packages/api/app/services/weather_service.py`
- Modify: `packages/api/app/routers/weather.py`
- Modify: `packages/api/app/config.py`

**Step 1: Add env vars to config**

In `config.py`, add to Settings:
```python
weather_api_url: str = ""
bharat_pashudhan_api_url: str = ""
iot_gateway_url: str = ""
storage_api_url: str = ""
```

**Step 2: Rewrite weather_service.py**

Replace `_NOT_CONFIGURED` stubs with async httpx calls:
```python
import httpx
from app.config import settings

KARNATAKA_DISTRICTS = {
    "dharwad": {"lat": 15.46, "lon": 75.01},
    # ... (same as mock data)
}

async def get_forecast(district: str, days: int = 5) -> list[WeatherForecast]:
    if not settings.weather_api_url:
        raise ServiceNotConfiguredError("WEATHER_API_URL")
    coords = KARNATAKA_DISTRICTS.get(district.lower())
    if not coords:
        raise ValueError(f"Unknown district: {district}")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.weather_api_url}/forecast",
            params={"district": district, "days": days},
        )
        resp.raise_for_status()
    data = resp.json()
    return [WeatherForecast(**f) for f in data["forecasts"]]

async def get_alerts(district: str) -> list[dict]:
    if not settings.weather_api_url:
        raise ServiceNotConfiguredError("WEATHER_API_URL")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.weather_api_url}/alerts",
            params={"district": district},
        )
        resp.raise_for_status()
    return resp.json().get("alerts", [])

async def get_tts(district: str, language_code: str = "kn") -> dict:
    if not settings.weather_api_url:
        raise ServiceNotConfiguredError("WEATHER_API_URL")
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{settings.weather_api_url}/tts",
            json={"district": district, "language_code": language_code},
        )
        resp.raise_for_status()
    return resp.json()
```

**Step 3: Update weather router**

Make endpoints async, add TTS endpoint:
```python
@router.get("/tts/{district}")
async def get_weather_tts(district: str, lang: str = "kn"):
    result = await get_tts(district, lang)
    return result
```

**Step 4: Verify**
```bash
# Start mock on 8001, API on 8000 with WEATHER_API_URL=http://localhost:8001/api/weather
curl http://localhost:8000/v1/weather/forecast/dharwad
```

**Step 5: Commit**
```bash
git add packages/api/app/services/weather_service.py packages/api/app/routers/weather.py packages/api/app/config.py
git commit -m "feat: replace weather stubs with httpx calls to configurable URL"
```

---

## Task 6: API — Bharat Pashudhan HTTP Client

**Files:**
- Modify: `packages/api/app/services/bharat_pashudhan.py`

**Step 1: Rewrite bharat_pashudhan.py**

Replace stubs with async httpx calls:
```python
async def lookup_animal(pashu_aadhaar_id: str) -> dict | None:
    if not settings.bharat_pashudhan_api_url:
        raise ServiceNotConfiguredError("BHARAT_PASHUDHAN_API_URL")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{settings.bharat_pashudhan_api_url}/animals/{pashu_aadhaar_id}"
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
    record = resp.json()
    record["lookup_timestamp"] = datetime.now(timezone.utc).isoformat()
    record["source"] = "Bharat Pashudhan National Database"
    return record

async def sync_animal(animal_id: UUID) -> dict:
    if not settings.bharat_pashudhan_api_url:
        raise ServiceNotConfiguredError("BHARAT_PASHUDHAN_API_URL")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{settings.bharat_pashudhan_api_url}/sync",
            json={"animal_id": str(animal_id)},
        )
        resp.raise_for_status()
    return resp.json()
```

**Step 2: Update router to async**

`bharat_pashudhan.py` router — make endpoint functions async, await service calls.

**Step 3: Commit**
```bash
git add packages/api/app/services/bharat_pashudhan.py packages/api/app/routers/bharat_pashudhan.py
git commit -m "feat: replace Bharat Pashudhan stubs with httpx calls"
```

---

## Task 7: API — IoT Service + Storage Service

**Files:**
- Create: `packages/api/app/services/iot_service.py`
- Create: `packages/api/app/services/storage_service.py`
- Modify: `packages/api/app/routers/iot.py`
- Create: `packages/api/app/routers/files.py`
- Modify: `packages/api/app/main.py`

**Step 1: Create iot_service.py**

httpx client calling `IOT_GATEWAY_URL`:
- `list_devices(status, device_type)` → `GET /devices`
- `get_device(device_id)` → `GET /devices/{id}`
- `get_latest(device_id)` → `GET /devices/{id}/latest`
- `get_telemetry(device_id, metric, from_dt, to_dt)` → `GET /telemetry`

**Step 2: Rewrite iot.py router**

Replace empty responses with actual service calls. Keep auth dependency.

**Step 3: Create storage_service.py**

httpx client calling `STORAGE_API_URL`:
- `upload_file(file_bytes, filename, content_type, category, entity_type, entity_id)` → `POST /files`
- `get_file(file_id)` → `GET /files/{id}`
- `list_files(entity_type, entity_id)` → `GET /files`

**Step 4: Create files router**

`packages/api/app/routers/files.py`:
- `POST /v1/files` — accepts UploadFile, proxies to storage service
- `GET /v1/files/{file_id}` — proxies download
- `GET /v1/files` — list by entity

Register in `main.py`.

**Step 5: Commit**
```bash
git add packages/api/app/services/iot_service.py packages/api/app/services/storage_service.py \
  packages/api/app/routers/iot.py packages/api/app/routers/files.py packages/api/app/main.py
git commit -m "feat: add IoT and storage service clients with file upload router"
```

---

## Task 8: API — Startup Validation + Error Handling

**Files:**
- Modify: `packages/api/app/main.py`
- Create: `packages/api/app/services/errors.py`

**Step 1: Create service error types**

`packages/api/app/services/errors.py`:
```python
class ServiceNotConfiguredError(RuntimeError):
    def __init__(self, env_var: str):
        super().__init__(f"{env_var} is not configured")
        self.env_var = env_var

class ServiceUnavailableError(RuntimeError):
    def __init__(self, service: str, detail: str = ""):
        super().__init__(f"{service} is unavailable: {detail}")
        self.service = service
```

**Step 2: Add global exception handler in main.py**

```python
from app.services.errors import ServiceNotConfiguredError, ServiceUnavailableError

@app.exception_handler(ServiceNotConfiguredError)
async def not_configured_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc), "code": "SERVICE_NOT_CONFIGURED"})

@app.exception_handler(ServiceUnavailableError)
async def unavailable_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc), "code": "SERVICE_UNAVAILABLE"})
```

**Step 3: Update startup validation**

In `_validate_settings()`, add warnings for missing service URLs in development:
```python
import logging
logger = logging.getLogger(__name__)

if settings.environment == "development":
    for name, val in [
        ("WEATHER_API_URL", settings.weather_api_url),
        ("BHARAT_PASHUDHAN_API_URL", settings.bharat_pashudhan_api_url),
        ("IOT_GATEWAY_URL", settings.iot_gateway_url),
        ("STORAGE_API_URL", settings.storage_api_url),
    ]:
        if not val:
            logger.warning("%s not set — %s endpoints will return 503", name, name.split("_API_URL")[0].lower())
else:
    # Non-dev: all required
    for name, val in [...]:
        if not val:
            raise RuntimeError(f"{name} is required in non-development environments")
```

**Step 4: Commit**
```bash
git add packages/api/app/services/errors.py packages/api/app/main.py
git commit -m "feat: add service error types and startup validation for external URLs"
```

---

## Task 9: API — Reference Data Migration

**Files:**
- Create: `packages/api/alembic/versions/c8d9e0f1a2b3_add_reference_data_tables.py`
- Create: `packages/api/app/models/reference.py`
- Create: `packages/api/app/routers/reference.py`
- Modify: `packages/api/app/main.py`

**Step 1: Create reference data models**

`packages/api/app/models/reference.py`:
```python
class MarketRate(Base):
    __tablename__ = "market_rates"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    product = mapped_column(String(50), nullable=False)
    unit = mapped_column(String(20), nullable=False)
    min_price = mapped_column(Numeric(10, 2), nullable=False)
    max_price = mapped_column(Numeric(10, 2), nullable=False)
    avg_price = mapped_column(Numeric(10, 2), nullable=False)
    district = mapped_column(String(50), nullable=False)
    label = mapped_column(String(100), nullable=False)
    effective_date = mapped_column(Date, server_default=text("CURRENT_DATE"))
    source = mapped_column(String(50), default="Karnataka APMC")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class InsurancePremium(Base):
    __tablename__ = "insurance_premiums"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    species = mapped_column(String(30), nullable=False)
    breed_type = mapped_column(String(30), nullable=False)
    premium_pct = mapped_column(Numeric(5, 2), nullable=False)
    animal_value_inr = mapped_column(Integer, nullable=False)
    scheme_name = mapped_column(String(50), default="LISS")
    effective_date = mapped_column(Date, server_default=text("CURRENT_DATE"))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MedicineCatalog(Base):
    __tablename__ = "medicine_catalog"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = mapped_column(String(100), nullable=False)
    category = mapped_column(String(50), nullable=False)
    dosage_info = mapped_column(Text)
    species_applicable = mapped_column(ARRAY(String))
    withdrawal_period_days = mapped_column(Integer, default=0)
    is_active = mapped_column(Boolean, default=True, server_default="true")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Step 2: Create migration with seed data**

Migration seeds from `constants.py` values: 13 market rates, 12 insurance premiums (4 species × 3 breed types).

**Step 3: Create reference router**

`packages/api/app/routers/reference.py`:
- `GET /v1/reference/market-rates` — query with optional `district`, `product` filters
- `GET /v1/reference/insurance-premiums` — query with optional `species`, `breed_type` filters
- `GET /v1/reference/medicines` — query with optional `species`, `category` filters
- Admin-only: `PUT /v1/reference/market-rates/{id}`, `PUT /v1/reference/insurance-premiums/{id}`

Add 60-second TTL cache using a simple dict + timestamp.

**Step 4: Register router in main.py**

**Step 5: Commit**
```bash
git add packages/api/app/models/reference.py packages/api/app/routers/reference.py \
  packages/api/alembic/versions/c8d9e0f1a2b3_add_reference_data_tables.py packages/api/app/main.py
git commit -m "feat: add reference data tables with seed migration and API endpoints"
```

---

## Task 10: API — Remove constants.py, Update Consumers

**Files:**
- Delete: `packages/api/app/constants.py`
- Modify: any routers/services that import from `constants.py`

**Step 1: Find all imports of constants.py**

```bash
grep -r "from app.constants" packages/api/app/ --include="*.py"
grep -r "import constants" packages/api/app/ --include="*.py"
```

**Step 2: Update each consumer**

Replace `from app.constants import KARNATAKA_MARKET_RATES` with DB query via reference router or direct SQLAlchemy query. Use the 60-second cache.

Replace `INSURANCE_PREMIUM_RATES` / `INSURANCE_ANIMAL_VALUES` imports with DB query.

**Step 3: Delete constants.py**

**Step 4: Verify no broken imports**
```bash
cd packages/api && python -c "from app.main import app; print('OK')"
```

**Step 5: Commit**
```bash
git add -u packages/api/
git commit -m "refactor: remove constants.py, all reference data served from database"
```

---

## Task 11: Mobile — Global Snackbar Hook

**Files:**
- Create: `packages/mobile/src/hooks/useSnackbar.tsx`
- Modify: `packages/mobile/app/_layout.tsx`

**Step 1: Create snackbar context + hook**

```typescript
import React, { createContext, useCallback, useContext, useState } from 'react';
import { Snackbar } from 'react-native-paper';

type SnackType = 'error' | 'success' | 'info';

interface SnackbarContextValue {
  showError: (message: string) => void;
  showSuccess: (message: string) => void;
  showInfo: (message: string) => void;
}

const SnackbarContext = createContext<SnackbarContextValue>({
  showError: () => {},
  showSuccess: () => {},
  showInfo: () => {},
});

export function SnackbarProvider({ children }: { children: React.ReactNode }) {
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState('');
  const [type, setType] = useState<SnackType>('info');

  const show = useCallback((msg: string, t: SnackType) => {
    setMessage(msg);
    setType(t);
    setVisible(true);
  }, []);

  const bgColor = type === 'error' ? '#d32f2f' : type === 'success' ? '#2e7d32' : '#1976d2';

  return (
    <SnackbarContext.Provider
      value={{
        showError: (m) => show(m, 'error'),
        showSuccess: (m) => show(m, 'success'),
        showInfo: (m) => show(m, 'info'),
      }}
    >
      {children}
      <Snackbar
        visible={visible}
        onDismiss={() => setVisible(false)}
        duration={4000}
        style={{ backgroundColor: bgColor }}
        action={{ label: 'OK', onPress: () => setVisible(false) }}
      >
        {message}
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export const useSnackbar = () => useContext(SnackbarContext);
```

**Step 2: Wrap app layout with SnackbarProvider**

In `_layout.tsx`, wrap the root with `<SnackbarProvider>`.

**Step 3: Commit**
```bash
git add packages/mobile/src/hooks/useSnackbar.tsx packages/mobile/app/_layout.tsx
git commit -m "feat: add global snackbar hook for mobile error/success feedback"
```

---

## Task 12: Mobile — Fix Silent Catches

**Files:**
- Modify: `packages/mobile/app/(tabs)/medicine-log.tsx`
- Modify: `packages/mobile/app/(tabs)/sell.tsx`
- Modify: `packages/mobile/app/(tabs)/milk.tsx`

**Step 1: Fix medicine-log.tsx**

Find empty/silent catch blocks, add:
```typescript
const { showError } = useSnackbar();
// In catch:
catch (e) {
  console.error('Medicine log save failed:', e);
  showError('Failed to save medicine log. Please try again.');
}
```

**Step 2: Fix sell.tsx**

Same pattern:
```typescript
catch (e) {
  console.error('Listing creation failed:', e);
  showError('Failed to create listing. Please try again.');
}
```

**Step 3: Fix milk.tsx**

Same pattern:
```typescript
catch (e) {
  console.error('Milk entry failed:', e);
  showError('Failed to record milk entry. Please try again.');
}
```

**Step 4: Commit**
```bash
git add packages/mobile/app/\(tabs\)/medicine-log.tsx packages/mobile/app/\(tabs\)/sell.tsx packages/mobile/app/\(tabs\)/milk.tsx
git commit -m "fix: replace silent catches with snackbar error feedback"
```

---

## Task 13: Mobile — Weather Voice Summary Handler

**Files:**
- Modify: weather screen (find the screen with the empty voice button)
- Modify: `packages/mobile/src/services/voice.ts` (if TTS call needed)

**Step 1: Find the empty handler**
```bash
grep -r "voice\|tts\|speak\|audio" packages/mobile/app/ --include="*.tsx" -l
```

**Step 2: Wire the handler**

Call `GET /v1/weather/tts/{district}` → receives `{audio: "<base64>"}` → decode base64 → play via `expo-av` Audio.Sound:
```typescript
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

const playWeatherSummary = async (district: string) => {
  try {
    const resp = await fetch(`${API_URL}/weather/tts/${district}`);
    const data = await resp.json();
    const uri = FileSystem.cacheDirectory + 'weather_tts.wav';
    await FileSystem.writeAsStringAsync(uri, data.audio, { encoding: FileSystem.EncodingType.Base64 });
    const { sound } = await Audio.Sound.createAsync({ uri });
    await sound.playAsync();
  } catch (e) {
    console.error('Weather TTS failed:', e);
    showError('Could not play weather summary');
  }
};
```

**Step 3: Commit**
```bash
git add packages/mobile/
git commit -m "feat: wire weather voice summary to TTS endpoint"
```

---

## Task 14: Mobile — Insurance Photo Upload Handler

**Files:**
- Modify: insurance screen (find the screen with the empty photo button)

**Step 1: Find the empty handler**
```bash
grep -r "photo\|camera\|image.*pick\|upload" packages/mobile/app/ --include="*.tsx" -l
```

**Step 2: Wire the handler**

```typescript
import * as ImagePicker from 'expo-image-picker';

const takeInsurancePhoto = async (animalId: string) => {
  try {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      showError('Camera permission required');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });
    if (result.canceled) return;

    const formData = new FormData();
    const asset = result.assets[0];
    formData.append('file', { uri: asset.uri, type: 'image/jpeg', name: 'insurance_photo.jpg' } as any);
    formData.append('category', 'insurance_photo');
    formData.append('entity_type', 'animal');
    formData.append('entity_id', animalId);

    const resp = await fetch(`${API_URL}/files`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) throw new Error('Upload failed');
    showSuccess('Photo uploaded successfully');
  } catch (e) {
    console.error('Photo upload failed:', e);
    showError('Failed to upload photo. Please try again.');
  }
};
```

**Step 3: Commit**
```bash
git add packages/mobile/
git commit -m "feat: wire insurance photo button to camera + file upload"
```

---

## Task 15: Docker Compose + .env Updates

**Files:**
- Modify: `pashu-erp/docker-compose.yml`
- Modify: `pashu-erp/packages/api/.env.example`
- Modify: `pashu-erp/packages/api/.env` (local only, not committed)

**Step 1: Add mock-backends service to docker-compose.yml**

```yaml
mock-backends:
  build: ./mocks
  ports:
    - "8001:8001"
  volumes:
    - ./mocks/uploads:/app/uploads
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 10s
    timeout: 5s
    retries: 3
```

Add env vars to api service:
```yaml
api:
  environment:
    WEATHER_API_URL: http://mock-backends:8001/api/weather
    BHARAT_PASHUDHAN_API_URL: http://mock-backends:8001/api/registry
    IOT_GATEWAY_URL: http://mock-backends:8001/api/iot
    STORAGE_API_URL: http://mock-backends:8001/api/storage
  depends_on:
    mock-backends:
      condition: service_healthy
```

**Step 2: Update .env.example**

Add all new env vars with comments.

**Step 3: Commit**
```bash
git add pashu-erp/docker-compose.yml pashu-erp/packages/api/.env.example
git commit -m "feat: add mock-backends to docker-compose with health checks"
```

---

## Task Dependencies

```
Tasks 1-4: Mock service (parallel — no dependencies between routers)
Tasks 5-7: API HTTP clients (parallel — each independent service, but depends on Task 1-4 for testing)
Task 8: Error handling (depends on Tasks 5-7 for error types)
Task 9: Reference data migration (independent)
Task 10: Remove constants (depends on Task 9)
Task 11: Snackbar hook (independent)
Task 12: Fix silent catches (depends on Task 11)
Tasks 13-14: Wire handlers (depends on Tasks 5, 7, 11)
Task 15: Docker compose (depends on Tasks 1-4)
```

**Parallel batch 1:** Tasks 1, 2, 3, 4 (mock routers) + Task 9 (reference data) + Task 11 (snackbar)
**Parallel batch 2:** Tasks 5, 6, 7 (API clients) + Task 10 (remove constants) + Task 12 (fix catches)
**Parallel batch 3:** Tasks 8, 13, 14, 15 (error handling, wire handlers, docker)
