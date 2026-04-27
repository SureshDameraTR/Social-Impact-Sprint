"""Comprehensive integration tests for /v1/alerts endpoints.

Tests:
  - POST /report — create disease alert
  - GET /nearby — geo-based query
  - PATCH /{alert_id}/verify — admin/vet only
  - Auth enforcement across roles
  - Error cases: missing fields, invalid coords, fake UUIDs

Run: pytest tests/comprehensive/test_alerts_comprehensive.py -v
"""

import time

import pytest

FAKE_UUID = "00000000-0000-0000-0000-000000000000"

# Tumkur, Karnataka coordinates (test location)
TEST_LAT = 13.3409
TEST_LON = 77.1010


# ---------------------------------------------------------------------------
# Test 1: POST /v1/alerts/report requires auth
# ---------------------------------------------------------------------------


def test_report_requires_auth(api):
    """POST /v1/alerts/report without auth returns 401."""
    start = time.time()
    resp = api.post(
        "/v1/alerts/report",
        json={
            "disease_name": "FMD",
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "severity": "moderate",
        },
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/alerts/report no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: POST /v1/alerts/report with valid data → 201 + schema
# ---------------------------------------------------------------------------


def test_report_happy_path(api, farmer_auth):
    """POST /v1/alerts/report creates an alert and returns CommunityAlertRead schema."""
    start = time.time()
    resp = api.post(
        "/v1/alerts/report",
        json={
            "disease_name": "Foot and Mouth Disease",
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "radius_km": 5.0,
            "severity": "moderate",
        },
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/alerts/report success: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "id" in body, f"Missing 'id': {body}"
    assert "disease_name" in body, f"Missing 'disease_name': {body}"
    assert "severity" in body, f"Missing 'severity': {body}"
    assert "verified" in body, f"Missing 'verified': {body}"
    assert body["verified"] is False, "New alerts should not be pre-verified"
    assert body["disease_name"] == "Foot and Mouth Disease"
    assert body["severity"] == "moderate"


# ---------------------------------------------------------------------------
# Test 3: POST /v1/alerts/report missing required fields → 422
# ---------------------------------------------------------------------------


def test_report_missing_fields(api, farmer_auth):
    """POST /v1/alerts/report with empty body returns 422."""
    start = time.time()
    resp = api.post("/v1/alerts/report", json={}, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] POST /v1/alerts/report missing fields: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: POST /v1/alerts/report with invalid severity → 422
# ---------------------------------------------------------------------------


def test_report_invalid_severity(api, farmer_auth):
    """POST /v1/alerts/report with invalid severity value returns 422."""
    start = time.time()
    resp = api.post(
        "/v1/alerts/report",
        json={
            "disease_name": "Test",
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "severity": "catastrophic",  # not a valid enum value
        },
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/alerts/report invalid severity: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 5: GET /v1/alerts/nearby requires auth
# ---------------------------------------------------------------------------


def test_nearby_requires_auth(api):
    """GET /v1/alerts/nearby without auth returns 401."""
    start = time.time()
    resp = api.get(f"/v1/alerts/nearby?lat={TEST_LAT}&lon={TEST_LON}")
    duration = time.time() - start
    print(f"\n[timing] GET /v1/alerts/nearby no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 6: GET /v1/alerts/nearby returns data/total envelope
# ---------------------------------------------------------------------------


def test_nearby_envelope_structure(api, farmer_auth):
    """GET /v1/alerts/nearby returns data/total envelope."""
    start = time.time()
    resp = api.get(
        f"/v1/alerts/nearby?lat={TEST_LAT}&lon={TEST_LON}&radius=50",
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] GET /v1/alerts/nearby farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)


# ---------------------------------------------------------------------------
# Test 7: GET /v1/alerts/nearby missing lat/lon → 422
# ---------------------------------------------------------------------------


def test_nearby_missing_coordinates(api, farmer_auth):
    """GET /v1/alerts/nearby without lat/lon query params returns 422."""
    start = time.time()
    resp = api.get("/v1/alerts/nearby", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/alerts/nearby no coords: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: GET /v1/alerts/nearby out-of-range radius → 422
# ---------------------------------------------------------------------------


def test_nearby_radius_exceeds_max(api, farmer_auth):
    """GET /v1/alerts/nearby with radius > 100 km → 422."""
    start = time.time()
    resp = api.get(
        f"/v1/alerts/nearby?lat={TEST_LAT}&lon={TEST_LON}&radius=999",
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] GET /v1/alerts/nearby bad radius: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: PATCH /{alert_id}/verify — farmer gets 403
# ---------------------------------------------------------------------------


def test_verify_alert_farmer_forbidden(api, farmer_auth):
    """PATCH /v1/alerts/{id}/verify returns 403 for farmer role."""
    # Create an alert first so we have a real ID to try
    create_resp = api.post(
        "/v1/alerts/report",
        json={
            "disease_name": "Brucellosis",
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "severity": "severe",
        },
        headers=farmer_auth,
    )
    assert create_resp.status_code == 201, f"Alert creation failed: {create_resp.text}"
    alert_id = create_resp.json()["id"]

    start = time.time()
    resp = api.patch(f"/v1/alerts/{alert_id}/verify", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] PATCH /v1/alerts/verify farmer: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for farmer verifying alert, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 10: PATCH /{alert_id}/verify — vet can verify
# ---------------------------------------------------------------------------


def test_verify_alert_vet_can_verify(api, farmer_auth, vet_auth):
    """PATCH /v1/alerts/{id}/verify succeeds for vet role."""
    # Create alert as farmer
    create_resp = api.post(
        "/v1/alerts/report",
        json={
            "disease_name": "Lumpy Skin Disease",
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "severity": "critical",
        },
        headers=farmer_auth,
    )
    assert create_resp.status_code == 201, f"Alert creation failed: {create_resp.text}"
    alert_id = create_resp.json()["id"]

    start = time.time()
    resp = api.patch(f"/v1/alerts/{alert_id}/verify", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] PATCH /v1/alerts/verify vet: {duration:.3f}s")

    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert body.get("verified") is True, f"Expected verified=True: {body}"


# ---------------------------------------------------------------------------
# Test 11: PATCH /{fake_uuid}/verify → 404
# ---------------------------------------------------------------------------


def test_verify_alert_nonexistent_returns_404(api, vet_auth):
    """PATCH /v1/alerts/<fake_uuid>/verify returns 404."""
    start = time.time()
    resp = api.patch(f"/v1/alerts/{FAKE_UUID}/verify", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] PATCH /v1/alerts/verify fake uuid: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 12: POST /v1/alerts/report Kannada disease name is accepted
# ---------------------------------------------------------------------------


def test_report_kannada_disease_name(api, farmer_auth):
    """POST /v1/alerts/report with Kannada disease name returns 201."""
    start = time.time()
    resp = api.post(
        "/v1/alerts/report",
        json={
            "disease_name": "ಕಾಲು ಮತ್ತು ಬಾಯಿ ರೋಗ",  # Kannada: Foot and Mouth Disease
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "severity": "low",
        },
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/alerts/report Kannada name: {duration:.3f}s")

    assert resp.status_code == 201, (
        f"Expected 201 for Kannada disease name, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert body["disease_name"] == "ಕಾಲು ಮತ್ತು ಬಾಯಿ ರೋಗ"
