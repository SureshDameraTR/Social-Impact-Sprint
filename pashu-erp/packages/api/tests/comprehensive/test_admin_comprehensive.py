"""Comprehensive integration tests for /v1/admin endpoints.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_admin_comprehensive.py -v
"""

import time

import pytest

# ---------------------------------------------------------------------------
# Test 1: GET /v1/admin/stats — happy path as admin
# ---------------------------------------------------------------------------

def test_admin_stats_happy_path(api, admin_auth):
    """GET /v1/admin/stats returns all expected stat fields."""
    start = time.time()
    resp = api.get("/v1/admin/stats", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/admin/stats: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    expected_keys = [
        "farmer_count",
        "animal_count",
        "todays_milk_liters",
        "active_alerts",
        "marketplace_revenue",
        "active_sellers",
        "women_farmers",
        "women_revenue",
        "women_animals",
        "women_shg_count",
    ]
    for key in expected_keys:
        assert key in body, f"Missing key '{key}' in stats response: {body}"

    # All numeric values — none should be negative
    for key in expected_keys:
        assert isinstance(body[key], (int, float)), (
            f"Key '{key}' should be numeric, got {type(body[key])}: {body[key]}"
        )
        assert body[key] >= 0, f"Key '{key}' has unexpected negative value: {body[key]}"


# ---------------------------------------------------------------------------
# Test 2: GET /v1/admin/stats — 401 without auth
# ---------------------------------------------------------------------------

def test_admin_stats_unauthenticated_returns_401(api):
    """GET /v1/admin/stats without auth header returns 401."""
    resp = api.get("/v1/admin/stats")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 3: GET /v1/admin/stats — 403 for farmer role
# ---------------------------------------------------------------------------

def test_admin_stats_farmer_returns_403(api, farmer_auth):
    """GET /v1/admin/stats with farmer token returns 403 (admin-only)."""
    resp = api.get("/v1/admin/stats", headers=farmer_auth)
    assert resp.status_code == 403, (
        f"Expected 403 for farmer on admin endpoint, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: GET /v1/admin/charts/milk — 30-day structure
# ---------------------------------------------------------------------------

def test_admin_charts_milk_structure(api, admin_auth):
    """GET /v1/admin/charts/milk returns 30-day period with correct shape."""
    start = time.time()
    resp = api.get("/v1/admin/charts/milk", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/admin/charts/milk: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "period" in body, f"Missing 'period' key: {body}"
    assert "data" in body, f"Missing 'data' key: {body}"
    assert body["period"] == "30_days", f"Expected period=30_days, got {body['period']}"

    data = body["data"]
    assert isinstance(data, list), f"Expected 'data' to be a list, got {type(data)}"
    assert len(data) == 30, f"Expected exactly 30 days, got {len(data)}: {data}"

    # Verify each entry has 'date' and 'liters'
    for entry in data:
        assert "date" in entry, f"Entry missing 'date': {entry}"
        assert "liters" in entry, f"Entry missing 'liters': {entry}"
        assert isinstance(entry["liters"], (int, float)), (
            f"liters should be numeric: {entry}"
        )
        assert entry["liters"] >= 0, f"Negative liters value: {entry}"


# ---------------------------------------------------------------------------
# Test 5: GET /v1/admin/charts/milk — 401 without auth
# ---------------------------------------------------------------------------

def test_admin_charts_milk_unauthenticated(api):
    """GET /v1/admin/charts/milk without auth returns 401."""
    resp = api.get("/v1/admin/charts/milk")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 6: GET /v1/admin/gis/alerts — response structure
# ---------------------------------------------------------------------------

def test_admin_gis_alerts_structure(api, admin_auth):
    """GET /v1/admin/gis/alerts returns alert_count and markers list."""
    start = time.time()
    resp = api.get("/v1/admin/gis/alerts", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/admin/gis/alerts: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "alert_count" in body, f"Missing 'alert_count': {body}"
    assert "markers" in body, f"Missing 'markers': {body}"
    assert isinstance(body["markers"], list), (
        f"'markers' should be a list: {type(body['markers'])}"
    )
    assert isinstance(body["alert_count"], int), (
        f"'alert_count' should be int: {type(body['alert_count'])}"
    )
    assert body["alert_count"] == len(body["markers"]), (
        f"alert_count {body['alert_count']} != len(markers) {len(body['markers'])}"
    )

    # If there are markers, verify required fields
    for marker in body["markers"]:
        assert "event_id" in marker, f"Marker missing 'event_id': {marker}"
        assert "animal_id" in marker, f"Marker missing 'animal_id': {marker}"
        assert "risk_score" in marker, f"Marker missing 'risk_score': {marker}"
        assert "event_date" in marker, f"Marker missing 'event_date': {marker}"


# ---------------------------------------------------------------------------
# Test 7: GET /v1/admin/gis/alerts — 403 for vet role
# ---------------------------------------------------------------------------

def test_admin_gis_alerts_vet_forbidden(api, vet_auth):
    """GET /v1/admin/gis/alerts with vet token returns 403 (admin-only)."""
    resp = api.get("/v1/admin/gis/alerts", headers=vet_auth)
    assert resp.status_code == 403, (
        f"Expected 403 for vet on admin endpoint, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: PATCH /v1/admin/users/{id}/role — 404 for unknown user
# ---------------------------------------------------------------------------

def test_admin_update_role_unknown_user_404(api, admin_auth):
    """PATCH /v1/admin/users/{id}/role with non-existent UUID returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = api.patch(
        f"/v1/admin/users/{fake_id}/role",
        json={"role": "farmer"},
        headers=admin_auth,
    )
    assert resp.status_code == 404, (
        f"Expected 404 for unknown user, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: PATCH /v1/admin/users/{id}/role — 422 for invalid role
# ---------------------------------------------------------------------------

def test_admin_update_role_invalid_role_422(api, admin_auth, farmer_auth):
    """PATCH /v1/admin/users/{id}/role with invalid role string returns 422."""
    # First get an actual farmer user ID via the list endpoint
    list_resp = api.get("/v1/farmers?limit=1", headers=admin_auth)
    assert list_resp.status_code == 200, f"Could not list farmers: {list_resp.text}"
    farmers = list_resp.json().get("data", [])
    if not farmers:
        pytest.skip("No farmers found in seed data")

    farmer_id = farmers[0]["id"]
    resp = api.patch(
        f"/v1/admin/users/{farmer_id}/role",
        json={"role": "supervillain"},
        headers=admin_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for invalid role, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 10: PATCH /v1/admin/users/{id}/role — success + revert (idempotent)
# ---------------------------------------------------------------------------

def test_admin_update_role_and_revert(api, admin_auth):
    """PATCH /v1/admin/users/{id}/role changes role and returns previous_role; revert after."""
    list_resp = api.get("/v1/farmers?limit=1", headers=admin_auth)
    assert list_resp.status_code == 200, f"Could not list farmers: {list_resp.text}"
    farmers = list_resp.json().get("data", [])
    if not farmers:
        pytest.skip("No farmers found in seed data")

    farmer_id = farmers[0]["id"]

    # Change farmer → vet
    resp = api.patch(
        f"/v1/admin/users/{farmer_id}/role",
        json={"role": "vet"},
        headers=admin_auth,
    )
    assert resp.status_code == 200, f"Role change failed: {resp.text}"
    body = resp.json()
    assert body["role"] == "vet", f"Expected role=vet: {body}"
    assert body["previous_role"] == "farmer", f"Expected previous_role=farmer: {body}"
    assert "id" in body and "name" in body

    # Revert back to farmer
    revert_resp = api.patch(
        f"/v1/admin/users/{farmer_id}/role",
        json={"role": "farmer"},
        headers=admin_auth,
    )
    assert revert_resp.status_code == 200, f"Role revert failed: {revert_resp.text}"
    revert_body = revert_resp.json()
    assert revert_body["role"] == "farmer", f"Role not reverted: {revert_body}"


# ---------------------------------------------------------------------------
# Test 11: PATCH /v1/admin/users/{id}/role — 403 for farmer token
# ---------------------------------------------------------------------------

def test_admin_update_role_farmer_token_403(api, admin_auth, farmer_auth):
    """PATCH /v1/admin/users/{id}/role with farmer token returns 403."""
    list_resp = api.get("/v1/farmers?limit=1", headers=admin_auth)
    assert list_resp.status_code == 200, f"Could not list farmers: {list_resp.text}"
    farmers = list_resp.json().get("data", [])
    if not farmers:
        pytest.skip("No farmers found in seed data")

    farmer_id = farmers[0]["id"]
    resp = api.patch(
        f"/v1/admin/users/{farmer_id}/role",
        json={"role": "vet"},
        headers=farmer_auth,
    )
    assert resp.status_code == 403, (
        f"Expected 403 for farmer patching role, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 12: PATCH /v1/admin/users/{id}/role — 422 for malformed UUID
# ---------------------------------------------------------------------------

def test_admin_update_role_malformed_uuid_422(api, admin_auth):
    """PATCH /v1/admin/users/not-a-uuid/role returns 422 validation error."""
    resp = api.patch(
        "/v1/admin/users/not-a-uuid/role",
        json={"role": "farmer"},
        headers=admin_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for malformed UUID, got {resp.status_code}: {resp.text}"
    )
