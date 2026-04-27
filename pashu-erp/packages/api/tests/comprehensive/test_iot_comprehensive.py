"""Comprehensive integration tests for /v1/iot endpoints.

Hits the REAL running API at localhost:8000, which proxies to the mock IoT
gateway at localhost:8001. Read iot.py and the IoT schema before editing.

Known device IDs from sample_devices.json:
  SC-GIR-0042 (smart_collar, active)
  ET-BAN-0021 (ear_tag_sensor, inactive)
  MM-HF-0001  (milk_meter, active)

Run: pytest tests/comprehensive/test_iot_comprehensive.py -v
"""

import time

import pytest


# ---------------------------------------------------------------------------
# Constants — from sample_devices.json
# ---------------------------------------------------------------------------

KNOWN_ACTIVE_DEVICE = "SC-GIR-0042"
KNOWN_INACTIVE_DEVICE = "ET-BAN-0021"
KNOWN_MILK_METER = "MM-HF-0001"


# ===========================================================================
# Positive tests
# ===========================================================================


def test_iot_list_devices_happy_path(api, farmer_auth):
    """GET /v1/iot/devices returns 200 with data+total envelope."""
    start = time.time()
    resp = api.get("/v1/iot/devices", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] list devices: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] > 0, "Expected at least one device from mock"


def test_iot_list_devices_item_schema(api, farmer_auth):
    """Each device in the list has required IoTDeviceRead fields."""
    resp = api.get("/v1/iot/devices", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    devices = resp.json()["data"]
    assert len(devices) > 0

    device = devices[0]
    assert "device_id" in device, f"Missing 'device_id': {device}"
    assert "type" in device, f"Missing 'type': {device}"
    assert "status" in device, f"Missing 'status': {device}"
    assert device["status"] in ("active", "inactive"), f"Unexpected status: {device['status']}"


def test_iot_list_devices_filter_by_status(api, farmer_auth):
    """GET /v1/iot/devices?status=active returns only active devices."""
    resp = api.get("/v1/iot/devices", params={"status": "active"}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    for device in body["data"]:
        assert device["status"] == "active", (
            f"Expected only active devices, got: {device['status']}"
        )


def test_iot_list_devices_filter_by_type(api, farmer_auth):
    """GET /v1/iot/devices?device_type=smart_collar returns only smart collars."""
    resp = api.get(
        "/v1/iot/devices", params={"device_type": "smart_collar"}, headers=farmer_auth
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    for device in body["data"]:
        assert device["type"] == "smart_collar", (
            f"Expected only smart_collar, got: {device['type']}"
        )


def test_iot_device_types_aggregation(api, farmer_auth):
    """GET /v1/iot/device-types returns aggregated type counts."""
    start = time.time()
    resp = api.get("/v1/iot/device-types", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] device-types: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert isinstance(body, list), f"Expected list, got {type(body)}"
    assert len(body) > 0, "Expected at least one device type"

    # Each entry has name, total, online, offline
    entry = body[0]
    assert "name" in entry, f"Missing 'name': {entry}"
    assert "total" in entry, f"Missing 'total': {entry}"
    assert "online" in entry, f"Missing 'online': {entry}"
    assert "offline" in entry, f"Missing 'offline': {entry}"
    assert entry["total"] == entry["online"] + entry["offline"], (
        f"total != online+offline for {entry}"
    )


def test_iot_get_device_by_id(api, farmer_auth):
    """GET /v1/iot/devices/{device_id} returns single device with all fields."""
    start = time.time()
    resp = api.get(f"/v1/iot/devices/{KNOWN_ACTIVE_DEVICE}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get device by id: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert body["device_id"] == KNOWN_ACTIVE_DEVICE, f"Wrong device_id: {body}"
    assert "type" in body
    assert "status" in body
    # Mock enriches with last_seen when fetched individually
    assert "last_seen" in body, f"Missing 'last_seen' on detail endpoint: {body}"


def test_iot_get_device_latest_telemetry(api, farmer_auth):
    """GET /v1/iot/devices/{device_id}/latest returns TelemetryReading schema."""
    start = time.time()
    resp = api.get(f"/v1/iot/devices/{KNOWN_ACTIVE_DEVICE}/latest", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get latest telemetry: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "device_id" in body, f"Missing 'device_id': {body}"
    assert "timestamp" in body, f"Missing 'timestamp': {body}"
    assert "metrics" in body, f"Missing 'metrics': {body}"
    assert isinstance(body["metrics"], list)
    assert len(body["metrics"]) > 0, "Expected at least one metric"

    # Validate a metric item
    metric = body["metrics"][0]
    assert "type" in metric, f"Missing 'type' in metric: {metric}"
    assert "value" in metric, f"Missing 'value' in metric: {metric}"
    assert "unit" in metric, f"Missing 'unit' in metric: {metric}"


# ===========================================================================
# Negative tests
# ===========================================================================


def test_iot_devices_requires_auth(api):
    """GET /v1/iot/devices returns 401/403 without auth."""
    resp = api.get("/v1/iot/devices")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_iot_device_types_requires_auth(api):
    """GET /v1/iot/device-types returns 401/403 without auth."""
    resp = api.get("/v1/iot/device-types")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_iot_get_unknown_device_returns_error(api, farmer_auth):
    """GET /v1/iot/devices/NONEXISTENT returns 404 or gateway error."""
    resp = api.get("/v1/iot/devices/DEVICE-DOES-NOT-EXIST-XYZ", headers=farmer_auth)
    # Mock returns 404 which the router propagates as HTTPException
    assert resp.status_code in (404, 502), (
        f"Expected 404 or 502 for unknown device, got {resp.status_code}: {resp.text}"
    )


def test_iot_readings_limit_validation(api, farmer_auth):
    """GET /v1/iot/readings?limit=999 is rejected (max=200)."""
    resp = api.get(
        "/v1/iot/readings", params={"limit": 999}, headers=farmer_auth
    )
    assert resp.status_code == 422, (
        f"Expected 422 for limit=999, got {resp.status_code}: {resp.text}"
    )


def test_iot_readings_negative_offset_rejected(api, farmer_auth):
    """GET /v1/iot/readings?offset=-1 is rejected (min=0)."""
    resp = api.get(
        "/v1/iot/readings", params={"offset": -1}, headers=farmer_auth
    )
    assert resp.status_code == 422, (
        f"Expected 422 for offset=-1, got {resp.status_code}: {resp.text}"
    )


def test_iot_readings_with_valid_device_filter(api, farmer_auth):
    """GET /v1/iot/readings?device_id=<known> returns telemetry list envelope."""
    resp = api.get(
        "/v1/iot/readings",
        params={"device_id": KNOWN_ACTIVE_DEVICE},
        headers=farmer_auth,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
