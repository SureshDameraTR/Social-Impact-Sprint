# Phase 2: Production Hardening Design — PashuRaksha ERP

**Date:** 2026-04-09
**Status:** Approved
**Scope:** Mock backend services, reference data migration, error handling, external service integration

---

## Decisions

| Decision | Choice |
|----------|--------|
| External service strategy | Separate FastAPI mock service, configurable URLs, swap to real backends later |
| Reference data migration | Single Alembic batch — market_rates, insurance_premiums, medicine_catalog |
| Error handling (mobile) | Global Snackbar hook using react-native-paper |
| Empty button handlers | Wire to mock backends (weather TTS, insurance photo upload) |
| Admin code quality | Fix `any` types + pagination bugs alongside other changes |

---

## Section 1: Mock Backend Services

A separate FastAPI application in `pashu-erp/mocks/` that implements four route groups on port 8001.

### Architecture

```
mocks/
├── main.py              # FastAPI app, mounts all routers
├── requirements.txt     # fastapi, uvicorn, python-multipart
├── Dockerfile
├── routers/
│   ├── weather.py       # /api/weather/*
│   ├── registry.py      # /api/registry/*
│   ├── iot.py           # /api/iot/*
│   └── storage.py       # /api/storage/*
├── data/
│   ├── karnataka_districts.json   # lat/lon + elevation for weather
│   ├── breeds.json                # ICAR breed codes
│   └── sample_devices.json        # IoT device fleet
└── uploads/             # local file storage for insurance photos
```

PashuRaksha API connects via environment variables:
```
WEATHER_API_URL=http://localhost:8001/api/weather
BHARAT_PASHUDHAN_API_URL=http://localhost:8001/api/registry
IOT_GATEWAY_URL=http://localhost:8001/api/iot
STORAGE_API_URL=http://localhost:8001/api/storage
```

Production swap: change URLs to real endpoints, no code changes.

### Weather Service (based on Open-Meteo API contract)

Open-Meteo is free with no API key. Our mock mirrors its response format.

**Endpoints:**
- `GET /api/weather/forecast?district={name}&days={n}` — Returns daily forecast
- `GET /api/weather/alerts?district={name}` — Returns active weather alerts
- `GET /api/weather/tts` — Returns audio bytes (Kannada weather summary)

**Response format (forecast):**
```json
{
  "district": "Dharwad",
  "forecasts": [
    {
      "date": "2026-04-09",
      "district": "Dharwad",
      "temp_min": 22.0,
      "temp_max": 35.7,
      "humidity": 65.0,
      "rainfall_mm": 0.0,
      "wind_speed": 10.9,
      "condition": "Partly Cloudy",
      "heat_stress_index": 78.2
    }
  ]
}
```

Karnataka district coordinates for weather lookup:
- Dharwad: 15.46°N, 75.01°E
- Belgaum: 15.85°N, 74.50°E
- Mysore: 12.30°N, 76.66°E
- Tumkur: 13.34°N, 77.10°E
- Shimoga: 13.93°N, 75.57°E
- Hassan: 13.01°N, 76.10°E

Seasonal patterns: monsoon (June-Sep) = high rainfall, winter (Dec-Feb) = low temps, summer (Mar-May) = high temps.

**TTS endpoint** mirrors Sarvam AI contract:
- Input: `POST /api/weather/tts` with `{district, language_code: "kn"}`
- Output: `{audio: "<base64-wav>", request_id: "..."}`
- Mock returns a small pre-recorded audio placeholder

### Bharat Pashudhan Registry (INAPH)

No public API exists. Our mock implements the API contract PashuRaksha expects for future government integration.

**Pashu Aadhaar format:** 12 digits — `IN` + 2-digit state code + 2-digit district code + 8-digit sequence
- Example: `IN29180001234` (Karnataka[29] + Dharwad[18] + sequence)

**Endpoints:**
- `GET /api/registry/animals/{pashu_aadhaar_id}` — Lookup by tag
- `POST /api/registry/sync` — Sync local record with registry

**Animal record fields (matching INAPH data model):**
```json
{
  "pashu_aadhaar_id": "IN29180001234",
  "species": "cattle",
  "breed": "Gir",
  "breed_code": "GIR001",
  "sex": "female",
  "date_of_birth": "2022-03-15",
  "owner": {
    "name": "Ravi Kumar",
    "aadhaar_last4": "5678",
    "mobile": "+919876543210",
    "village": "Navalgund",
    "block": "Navalgund",
    "district": "Dharwad",
    "state": "Karnataka"
  },
  "dam_tag": "IN29180000987",
  "sire_tag": "IN29180000456",
  "gps": {"lat": 15.17, "lng": 75.36},
  "vaccinations": [
    {"type": "FMD", "date": "2025-11-01", "batch": "FMD-2025-KA-4521", "vaccinator": "Dr. Patil"},
    {"type": "Brucellosis", "date": "2025-06-15", "batch": "BRU-2025-KA-1102", "vaccinator": "Dr. Hegde"}
  ],
  "insurance": {
    "policy_number": "LISS-KA-2025-78901",
    "scheme": "LISS",
    "valid_until": "2026-09-30"
  },
  "source": "Bharat Pashudhan National Database",
  "lookup_timestamp": "2026-04-09T10:30:00Z"
}
```

Species supported: cattle, buffalo, goat, sheep, pig, horse, camel, donkey, mithun, yak.
Vaccination types: FMD, Brucellosis, PPR, HS (Haemorrhagic Septicaemia), BQ (Black Quarter).

### IoT Gateway

**Endpoints:**
- `GET /api/iot/devices` — List devices with filters (`?status=active&type=smart_collar`)
- `GET /api/iot/devices/{device_id}` — Device detail with last_seen, battery_level
- `GET /api/iot/devices/{device_id}/latest` — Latest telemetry per metric
- `GET /api/iot/telemetry?device_id=X&metric=temperature&from=&to=` — Historical query

**Telemetry payload:**
```json
{
  "device_id": "SC-GIR-0042",
  "animal_id": "IN29180001234",
  "timestamp": "2026-04-09T05:30:00+05:30",
  "metrics": [
    {"type": "body_temperature", "value": 38.6, "unit": "°C"},
    {"type": "activity_index", "value": 142, "unit": "steps/hr"},
    {"type": "rumination", "value": 48, "unit": "min/hr"},
    {"type": "gps", "value": {"lat": 15.17, "lng": 75.36}, "unit": "coords"}
  ],
  "battery_pct": 82,
  "rssi": -67
}
```

**Device types:** smart_collar (temp + activity + GPS), ear_tag_sensor (temp only), bolus_sensor (core body temp), milk_meter (flow rate), pedometer (activity).

**Livestock reference values (Indian breeds):**

| Metric | Gir/Sahiwal Normal | Alert Threshold |
|--------|-------------------|-----------------|
| Body temperature | 38.0–39.0°C | >39.5°C (fever), <37.5°C (hypothermia) |
| Rumination | 40–60 min/hr | <25 min/hr (illness/stress) |
| Activity | 80–200 steps/hr | >350 (estrus), <30 (lethargy) |

Mock generates realistic time-series with occasional anomalies (fever spikes, estrus patterns).

### Storage Service

**Endpoints:**
- `POST /api/storage/files` — Multipart upload (file + metadata)
- `GET /api/storage/files/{file_id}` — Download file bytes
- `GET /api/storage/files?entity_type=animal&entity_id={id}` — List files for entity

**Upload request:** `multipart/form-data` with fields: `file` (binary), `category` (insurance_photo, claim_evidence, ear_tag_photo), `entity_type` (animal, policy, claim), `entity_id` (UUID).

**Upload response:**
```json
{
  "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "url": "/api/storage/files/f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "buffalo_front_view.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 245760,
  "category": "insurance_photo",
  "entity_type": "animal",
  "entity_id": "a1b2c3d4-...",
  "created_at": "2026-04-09T10:30:00Z"
}
```

Mock stores files on local disk under `./uploads/{file_id}`. Validates content_type (image/jpeg, image/png only). Same API contract works when swapping to S3/MinIO later.

---

## Section 2: PashuRaksha API — HTTP Client Integration

Replace `_NOT_CONFIGURED` stubs with real `httpx` async calls to configurable URLs.

### weather_service.py
- Make async calls to `WEATHER_API_URL`
- Karnataka district → lat/lon lookup table
- Map response to existing `WeatherForecast` schema
- New `get_tts(district, language)` function for voice summaries
- 10-second timeout, `raise_for_status()`

### bharat_pashudhan.py
- Make async calls to `BHARAT_PASHUDHAN_API_URL`
- `lookup_animal()` returns `None` on 404
- `sync_animal()` posts local record, returns sync status
- 10-second timeout

### New: iot_service.py
- Make async calls to `IOT_GATEWAY_URL`
- `list_devices()`, `get_device(id)`, `get_latest(device_id)`, `get_telemetry(device_id, from, to)`
- Replaces empty `{"data": [], "total": 0}` responses in iot.py router

### New: storage_service.py
- Make async calls to `STORAGE_API_URL`
- `upload_file(file, category, entity_type, entity_id)` — multipart POST
- `get_file(file_id)` — returns bytes
- `list_files(entity_type, entity_id)` — returns metadata list

### Startup validation
All 4 URLs enforced in `_validate_settings()` for non-development mode. Development mode logs warnings for missing URLs.

---

## Section 3: Reference Data Migration

Single Alembic migration creates all reference tables and seeds initial data from `constants.py`.

### New tables

**market_rates:**
- id (UUID), product (varchar), unit (varchar), min_price (decimal), max_price (decimal), avg_price (decimal)
- district (varchar), label (varchar), effective_date (date), source (varchar)
- created_at, updated_at timestamps

**insurance_premiums:**
- id (UUID), species (varchar), breed_type (varchar), premium_pct (decimal), animal_value_inr (integer)
- scheme_name (varchar), effective_date (date)
- created_at, updated_at timestamps

**medicine_catalog:**
- id (UUID), name (varchar), category (varchar), dosage_info (text), species_applicable (varchar[])
- withdrawal_period_days (integer), is_active (boolean, default true)
- created_at, updated_at timestamps

### Seed data
- 13 market rates from `KARNATAKA_MARKET_RATES`
- 12 insurance premiums from `INSURANCE_PREMIUM_RATES` × `INSURANCE_ANIMAL_VALUES`
- Medicine catalog from existing medicine model data

### New API endpoints
- `GET /v1/reference/market-rates?district=&product=`
- `GET /v1/reference/insurance-premiums?species=&breed_type=`
- `GET /v1/reference/medicines?species=&category=`
- Admin CRUD for updating rates without code deploys

### Cache
Simple in-memory cache (60-second TTL) for reference data queries. `constants.py` deleted after migration.

---

## Section 4: Error Handling + Empty Handlers

### Global Snackbar (mobile)

New `useSnackbar` hook + context provider:
```typescript
const { showError, showSuccess, showInfo } = useSnackbar();

// In catch blocks:
catch (e) {
  console.error(e);
  showError("Failed to save medicine log");
}
```

Uses `react-native-paper` `Snackbar` (already in deps). Red for errors, green for success. Auto-dismiss 4 seconds.

### Fix silent catches
- `medicine-log.tsx` — show error via snackbar
- `sell.tsx` — show error via snackbar
- `milk.tsx` — show error via snackbar

### Wire empty handlers
- **Weather voice summary** — New `GET /v1/weather/tts/{district}` endpoint proxies to mock TTS, mobile plays via `expo-av`
- **Insurance photo button** — `expo-image-picker` capture/gallery → `POST /v1/files` → links to insurance record

### Admin type fixes
- Replace `any` types with proper interfaces as pages are touched
- Pagination `total` uses server-side filtered count

---

## Section 5: Docker Compose + Environment

### docker-compose.yml additions
```yaml
mock-backends:
  build: ./mocks
  ports:
    - "8001:8001"
  volumes:
    - ./mocks/uploads:/app/uploads
```

### API environment variables
```
WEATHER_API_URL=http://mock-backends:8001/api/weather
BHARAT_PASHUDHAN_API_URL=http://mock-backends:8001/api/registry
IOT_GATEWAY_URL=http://mock-backends:8001/api/iot
STORAGE_API_URL=http://mock-backends:8001/api/storage
```

### Startup validation
Non-development: all 4 URLs required (fail fast).
Development: missing URLs produce clear warning log.

### .env.example
Updated with all new variables documented.
