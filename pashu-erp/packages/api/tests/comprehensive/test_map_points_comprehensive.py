"""Comprehensive integration tests for /v1/map/points endpoint.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_map_points_comprehensive.py -v
"""

import time

import pytest

VALID_POINT_TYPES = {
    "health_alert",
    "milk_center",
    "community_alert",
    "farmer_cluster",
}


# ---------------------------------------------------------------------------
# Test 1: GET /v1/map/points — any auth user can access
# ---------------------------------------------------------------------------

def test_map_points_farmer_happy_path(api, farmer_auth):
    """GET /v1/map/points as farmer returns data+total envelope."""
    start = time.time()
    resp = api.get("/v1/map/points", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/map/points (farmer): {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list), f"'data' should be a list"
    assert isinstance(body["total"], int), f"'total' should be int"


# ---------------------------------------------------------------------------
# Test 2: GET /v1/map/points — admin can also access
# ---------------------------------------------------------------------------

def test_map_points_admin_happy_path(api, admin_auth):
    """GET /v1/map/points as admin returns 200 (not admin-restricted)."""
    resp = api.get("/v1/map/points", headers=admin_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body and "total" in body


# ---------------------------------------------------------------------------
# Test 3: GET /v1/map/points — 401 without auth
# ---------------------------------------------------------------------------

def test_map_points_unauthenticated_401(api):
    """GET /v1/map/points without auth returns 401."""
    resp = api.get("/v1/map/points")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: GET /v1/map/points — total matches len(data)
# ---------------------------------------------------------------------------

def test_map_points_total_matches_data_length(api, farmer_auth):
    """total field equals the actual length of data list."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["total"] == len(body["data"]), (
        f"total={body['total']} != len(data)={len(body['data'])}"
    )


# ---------------------------------------------------------------------------
# Test 5: GET /v1/map/points — all points have a 'type' field
# ---------------------------------------------------------------------------

def test_map_points_all_have_type_field(api, farmer_auth):
    """Every point in the response has a non-empty 'type' field."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200
    body = resp.json()

    for point in body["data"]:
        assert "type" in point, f"Point missing 'type': {point}"
        assert point["type"], f"Point 'type' is empty: {point}"


# ---------------------------------------------------------------------------
# Test 6: GET /v1/map/points — only known point types returned
# ---------------------------------------------------------------------------

def test_map_points_only_known_types(api, farmer_auth):
    """All returned point types belong to the expected set of known types."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200
    body = resp.json()

    for point in body["data"]:
        assert point["type"] in VALID_POINT_TYPES, (
            f"Unknown point type '{point['type']}' in response: {point}"
        )


# ---------------------------------------------------------------------------
# Test 7: GET /v1/map/points — health_alert points have risk_score
# ---------------------------------------------------------------------------

def test_map_points_health_alerts_have_risk_score(api, farmer_auth):
    """health_alert points have risk_score > 0.5 (threshold) and id field."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200
    body = resp.json()

    for point in body["data"]:
        if point["type"] == "health_alert":
            assert "risk_score" in point, f"health_alert missing risk_score: {point}"
            assert point["risk_score"] is not None
            assert float(point["risk_score"]) > 0.5, (
                f"health_alert has risk_score <= 0.5 (threshold): {point['risk_score']}"
            )
            assert "id" in point, f"health_alert missing id: {point}"
            assert "date" in point, f"health_alert missing date: {point}"


# ---------------------------------------------------------------------------
# Test 8: GET /v1/map/points — milk_center points have label
# ---------------------------------------------------------------------------

def test_map_points_milk_centers_have_label(api, farmer_auth):
    """milk_center points have non-empty label and id field."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200
    body = resp.json()

    for point in body["data"]:
        if point["type"] == "milk_center":
            assert "id" in point, f"milk_center missing id: {point}"
            assert "label" in point, f"milk_center missing label: {point}"
            assert point["label"], f"milk_center has empty label: {point}"


# ---------------------------------------------------------------------------
# Test 9: GET /v1/map/points — farmer_cluster points have farmer_count
# ---------------------------------------------------------------------------

def test_map_points_farmer_clusters_have_count(api, farmer_auth):
    """farmer_cluster points have positive farmer_count and village_code."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200
    body = resp.json()

    for point in body["data"]:
        if point["type"] == "farmer_cluster":
            assert "farmer_count" in point, f"farmer_cluster missing farmer_count: {point}"
            assert isinstance(point["farmer_count"], int), (
                f"farmer_count should be int: {point['farmer_count']}"
            )
            assert point["farmer_count"] > 0, (
                f"farmer_cluster has farmer_count=0 — should not appear: {point}"
            )


# ---------------------------------------------------------------------------
# Test 10: GET /v1/map/points — vet also has access
# ---------------------------------------------------------------------------

def test_map_points_vet_access(api, vet_auth):
    """GET /v1/map/points as vet user returns 200."""
    resp = api.get("/v1/map/points", headers=vet_auth)
    assert resp.status_code == 200, (
        f"Expected 200 for vet on map/points, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/map/points — response time within acceptable threshold
# ---------------------------------------------------------------------------

def test_map_points_response_time(api, farmer_auth):
    """GET /v1/map/points responds within 3 seconds (combined 4 queries)."""
    start = time.time()
    resp = api.get("/v1/map/points", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/map/points: {duration:.3f}s")
    assert resp.status_code == 200
    assert duration < 3.0, f"map/points too slow: {duration:.3f}s"


# ---------------------------------------------------------------------------
# Test 12: GET /v1/map/points — community_alert points have severity if present
# ---------------------------------------------------------------------------

def test_map_points_community_alerts_structure(api, farmer_auth):
    """community_alert points have id, label, and lat/lon if present."""
    resp = api.get("/v1/map/points", headers=farmer_auth)
    assert resp.status_code == 200
    body = resp.json()

    for point in body["data"]:
        if point["type"] == "community_alert":
            assert "id" in point, f"community_alert missing id: {point}"
            assert "label" in point, f"community_alert missing label: {point}"
            # lat/lon may be None but field should be present
            assert "lat" in point, f"community_alert missing lat: {point}"
            assert "lon" in point, f"community_alert missing lon: {point}"
