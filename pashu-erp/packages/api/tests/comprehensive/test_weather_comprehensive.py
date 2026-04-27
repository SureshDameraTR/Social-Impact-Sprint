"""Comprehensive integration tests for /v1/weather endpoints.

Hits the REAL running API at localhost:8000 which proxies to the mock weather
backend at localhost:8001. Read weather.py and weather_service.py before editing.

Run: pytest tests/comprehensive/test_weather_comprehensive.py -v
"""

import time

import pytest


# ---------------------------------------------------------------------------
# Constants — Karnataka district names as the service accepts them
# ---------------------------------------------------------------------------

DISTRICT_BENGALURU = "bengaluru urban"
DISTRICT_MYSURU = "mysuru"
DISTRICT_DHARWAD = "dharwad"


# ===========================================================================
# Positive tests
# ===========================================================================


def test_weather_forecast_happy_path(api, farmer_auth):
    """GET /v1/weather/forecast/{district} returns 200 with correct envelope."""
    start = time.time()
    resp = api.get(f"/v1/weather/forecast/{DISTRICT_BENGALURU}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] forecast happy path: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    # Top-level envelope fields
    assert "district" in body, f"Missing 'district': {body}"
    assert "days" in body, f"Missing 'days': {body}"
    assert "forecasts" in body, f"Missing 'forecasts': {body}"
    assert "source" in body, f"Missing 'source': {body}"

    assert isinstance(body["forecasts"], list)
    assert len(body["forecasts"]) == 5  # default days=5
    assert body["days"] == 5
    assert body["source"] == "IMD"


def test_weather_forecast_returns_expected_fields(api, farmer_auth):
    """Each forecast item contains all required meteorological fields."""
    resp = api.get(f"/v1/weather/forecast/{DISTRICT_MYSURU}", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert len(body["forecasts"]) > 0
    item = body["forecasts"][0]

    required_fields = [
        "date", "district", "temp_min", "temp_max",
        "humidity", "rainfall_mm", "wind_speed", "condition", "heat_stress_index",
    ]
    for field in required_fields:
        assert field in item, f"Missing field '{field}' in forecast: {item}"

    # Numeric sanity checks
    assert isinstance(item["temp_min"], (int, float))
    assert isinstance(item["temp_max"], (int, float))
    assert item["temp_max"] >= item["temp_min"]
    assert 0.0 <= item["humidity"] <= 100.0
    assert item["rainfall_mm"] >= 0.0
    assert item["wind_speed"] >= 0.0


def test_weather_forecast_custom_days(api, farmer_auth):
    """GET /v1/weather/forecast/{district}?days=3 returns exactly 3 forecast items."""
    resp = api.get(
        f"/v1/weather/forecast/{DISTRICT_DHARWAD}",
        params={"days": 3},
        headers=farmer_auth,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["days"] == 3
    assert len(body["forecasts"]) == 3


def test_weather_alerts_happy_path(api, farmer_auth):
    """GET /v1/weather/alerts/{district} returns 200 with envelope."""
    start = time.time()
    resp = api.get(f"/v1/weather/alerts/{DISTRICT_BENGALURU}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] alerts happy path: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "district" in body, f"Missing 'district': {body}"
    assert "active_alerts" in body, f"Missing 'active_alerts': {body}"
    assert "count" in body, f"Missing 'count': {body}"
    assert isinstance(body["active_alerts"], list)
    assert body["count"] == len(body["active_alerts"])


def test_weather_alerts_count_consistent(api, farmer_auth):
    """Alerts 'count' field always equals len(active_alerts)."""
    for district in [DISTRICT_BENGALURU, DISTRICT_MYSURU, DISTRICT_DHARWAD]:
        resp = api.get(f"/v1/weather/alerts/{district}", headers=farmer_auth)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["count"] == len(body["active_alerts"]), (
            f"count mismatch for {district}: count={body['count']} "
            f"but len(active_alerts)={len(body['active_alerts'])}"
        )


def test_weather_tts_happy_path(api, farmer_auth):
    """GET /v1/weather/tts/{district} returns 200 with audio response."""
    start = time.time()
    resp = api.get(f"/v1/weather/tts/{DISTRICT_BENGALURU}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] tts happy path: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    # Mock TTS returns audio + metadata
    assert "audio" in body, f"Missing 'audio' in TTS response: {body}"
    assert isinstance(body["audio"], str)
    assert len(body["audio"]) > 0, "TTS audio field is empty"


def test_weather_tts_kannada_language(api, farmer_auth):
    """GET /v1/weather/tts/{district}?lang=kn returns Kannada TTS."""
    resp = api.get(
        f"/v1/weather/tts/{DISTRICT_MYSURU}",
        params={"lang": "kn"},
        headers=farmer_auth,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "audio" in body


# ===========================================================================
# Negative tests
# ===========================================================================


def test_weather_forecast_requires_auth(api):
    """GET /v1/weather/forecast/{district} returns 401 with no token."""
    resp = api.get(f"/v1/weather/forecast/{DISTRICT_BENGALURU}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_weather_alerts_requires_auth(api):
    """GET /v1/weather/alerts/{district} returns 401 with no token."""
    resp = api.get(f"/v1/weather/alerts/{DISTRICT_BENGALURU}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_weather_tts_requires_auth(api):
    """GET /v1/weather/tts/{district} returns 401 with no token."""
    resp = api.get(f"/v1/weather/tts/{DISTRICT_BENGALURU}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_weather_forecast_days_too_large(api, farmer_auth):
    """GET /v1/weather/forecast/{district}?days=99 is rejected (max=14)."""
    resp = api.get(
        f"/v1/weather/forecast/{DISTRICT_BENGALURU}",
        params={"days": 99},
        headers=farmer_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for days=99, got {resp.status_code}: {resp.text}"
    )


def test_weather_forecast_days_zero(api, farmer_auth):
    """GET /v1/weather/forecast/{district}?days=0 is rejected (min=1)."""
    resp = api.get(
        f"/v1/weather/forecast/{DISTRICT_BENGALURU}",
        params={"days": 0},
        headers=farmer_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for days=0, got {resp.status_code}: {resp.text}"
    )


def test_weather_response_time_under_two_seconds(api, farmer_auth):
    """Forecast response must arrive within 2 seconds (mock backend is local)."""
    start = time.time()
    resp = api.get(f"/v1/weather/forecast/{DISTRICT_BENGALURU}", headers=farmer_auth)
    duration = time.time() - start
    assert resp.status_code == 200, resp.text
    assert duration < 2.0, f"Forecast took {duration:.2f}s — expected < 2s"
