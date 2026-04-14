# Mock Backends — Agent Instructions

FastAPI / Python 3.10 / Port 8001

## Purpose

Simulates external services that PashuRaksha integrates with. Each mock returns realistic data without requiring actual API keys or external connectivity.

## Critical Rules

1. **Response format must match real APIs** — frontends and API service clients depend on exact shapes
2. **Configurable via env vars** — API package uses `WEATHER_API_URL`, `REGISTRY_API_URL`, etc.
3. **Zero-code swap** — to switch from mock to real, just change the URL env var
4. **No auth on mocks** — mocks accept all requests (auth is the API's job)

## File Structure

- `main.py` — FastAPI app, mounts all routers
- `routers/weather.py` — IMD weather forecast (Karnataka districts)
- `routers/registry.py` — Bharat Pashudhan national animal registry
- `routers/iot.py` — IoT device telemetry (temperature, humidity, GPS)
- `routers/storage.py` — File upload/download (local filesystem)
- `data/karnataka_districts.json` — 30 district weather profiles
- `data/breeds.json` — Animal breed reference data
- `data/sample_devices.json` — IoT device fixtures

## Running

```bash
# Via Docker (recommended)
docker compose up mock-backends

# Standalone
cd pashu-erp/mocks
pip install -r requirements.txt
uvicorn main:app --port 8001
```
