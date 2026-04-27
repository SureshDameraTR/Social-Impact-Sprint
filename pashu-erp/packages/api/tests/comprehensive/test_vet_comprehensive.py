"""Comprehensive integration tests for /v1/vet endpoints.

Tests the veterinary consultation workflow:
  - Case list & detail
  - Claim → Diagnose → Close lifecycle
  - Dashboard stats & alerts
  - my-cases for farmers
  - Auth/role enforcement

Run: pytest tests/comprehensive/test_vet_comprehensive.py -v
"""

import time

import pytest

FAKE_UUID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# Test 1: GET /v1/vet/cases requires vet or admin role
# ---------------------------------------------------------------------------


def test_cases_list_requires_vet_or_admin_role(api, farmer_auth):
    """GET /v1/vet/cases returns 403 for a farmer (not vet/admin)."""
    start = time.time()
    resp = api.get("/v1/vet/cases", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/cases farmer: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for farmer on vet endpoint, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: GET /v1/vet/cases no auth returns 401
# ---------------------------------------------------------------------------


def test_cases_list_requires_auth(api):
    """GET /v1/vet/cases without auth returns 401."""
    start = time.time()
    resp = api.get("/v1/vet/cases")
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/cases no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 3: GET /v1/vet/cases vet auth → response envelope
# ---------------------------------------------------------------------------


def test_cases_list_envelope_structure(api, vet_auth):
    """GET /v1/vet/cases with valid vet token returns proper envelope."""
    start = time.time()
    resp = api.get("/v1/vet/cases", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/cases vet: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data' key: {body}"
    assert "total" in body, f"Missing 'total' key: {body}"
    assert "offset" in body, f"Missing 'offset' key: {body}"
    assert "limit" in body, f"Missing 'limit' key: {body}"
    assert isinstance(body["data"], list), "data must be a list"
    assert isinstance(body["total"], int), "total must be an int"
    assert body["total"] >= 0


# ---------------------------------------------------------------------------
# Test 4: GET /v1/vet/cases item schema when data exists
# ---------------------------------------------------------------------------


def test_cases_list_item_schema(api, vet_auth):
    """When vet cases exist, each item has required fields."""
    resp = api.get("/v1/vet/cases", headers=vet_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    if body["data"]:
        case = body["data"][0]
        assert "id" in case, f"Missing 'id' in case: {case}"
        assert "animal_id" in case, f"Missing 'animal_id' in case: {case}"
        assert "farmer_id" in case, f"Missing 'farmer_id' in case: {case}"
        assert "status" in case, f"Missing 'status' in case: {case}"
        assert "priority" in case, f"Missing 'priority' in case: {case}"
        assert "channel" in case, f"Missing 'channel' in case: {case}"
        assert case["status"] in (
            "pending", "in_review", "diagnosed", "closed"
        ), f"Unexpected status: {case['status']}"
        assert case["priority"] in (
            "routine", "urgent", "emergency"
        ), f"Unexpected priority: {case['priority']}"


# ---------------------------------------------------------------------------
# Test 5: GET /v1/vet/cases pagination — no overlap between pages
# ---------------------------------------------------------------------------


def test_cases_list_pagination_no_overlap(api, vet_auth):
    """Paginated case results have no overlapping IDs across pages."""
    resp1 = api.get("/v1/vet/cases?offset=0&limit=5", headers=vet_auth)
    resp2 = api.get("/v1/vet/cases?offset=5&limit=5", headers=vet_auth)

    assert resp1.status_code == 200, f"Page 1 failed: {resp1.text}"
    assert resp2.status_code == 200, f"Page 2 failed: {resp2.text}"

    ids1 = {c["id"] for c in resp1.json()["data"]}
    ids2 = {c["id"] for c in resp2.json()["data"]}
    assert ids1.isdisjoint(ids2), f"Overlapping IDs between pages: {ids1 & ids2}"


# ---------------------------------------------------------------------------
# Test 6: GET /v1/vet/cases filter by status
# ---------------------------------------------------------------------------


def test_cases_list_status_filter(api, vet_auth):
    """GET /v1/vet/cases?status=pending returns only pending cases."""
    resp = api.get("/v1/vet/cases?status=pending", headers=vet_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    for case in body["data"]:
        assert case["status"] == "pending", (
            f"Expected only 'pending' cases, found status={case['status']}"
        )


# ---------------------------------------------------------------------------
# Test 7: GET /v1/vet/cases/{case_id} bad UUID returns 422
# ---------------------------------------------------------------------------


def test_get_case_bad_uuid_returns_422(api, vet_auth):
    """GET /v1/vet/cases/not-a-uuid returns 422 validation error."""
    start = time.time()
    resp = api.get("/v1/vet/cases/not-a-uuid", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/cases bad uuid: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: GET /v1/vet/cases/{fake_uuid} returns 404
# ---------------------------------------------------------------------------


def test_get_case_nonexistent_returns_404(api, vet_auth):
    """GET /v1/vet/cases/<fake_uuid> returns 404."""
    start = time.time()
    resp = api.get(f"/v1/vet/cases/{FAKE_UUID}", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/cases fake uuid: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: PATCH /v1/vet/cases/{fake_uuid}/claim returns 404
# ---------------------------------------------------------------------------


def test_claim_nonexistent_case_returns_404(api, vet_auth):
    """PATCH /v1/vet/cases/<fake_uuid>/claim returns 404."""
    start = time.time()
    resp = api.patch(f"/v1/vet/cases/{FAKE_UUID}/claim", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] PATCH /v1/vet/cases claim fake: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 10: GET /v1/vet/dashboard/stats returns correct shape
# ---------------------------------------------------------------------------


def test_dashboard_stats_schema(api, vet_auth):
    """GET /v1/vet/dashboard/stats returns numeric stats fields."""
    start = time.time()
    resp = api.get("/v1/vet/dashboard/stats", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/dashboard/stats: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "pending_cases" in body, f"Missing pending_cases: {body}"
    assert "diagnosed_today" in body, f"Missing diagnosed_today: {body}"
    assert "district_animals" in body, f"Missing district_animals: {body}"
    assert "active_alerts" in body, f"Missing active_alerts: {body}"

    assert isinstance(body["pending_cases"], int), "pending_cases must be int"
    assert isinstance(body["diagnosed_today"], int), "diagnosed_today must be int"
    assert isinstance(body["district_animals"], int), "district_animals must be int"
    assert isinstance(body["active_alerts"], int), "active_alerts must be int"
    assert body["pending_cases"] >= 0
    assert body["district_animals"] >= 0


# ---------------------------------------------------------------------------
# Test 11: GET /v1/vet/dashboard/alerts returns correct shape
# ---------------------------------------------------------------------------


def test_dashboard_alerts_schema(api, vet_auth):
    """GET /v1/vet/dashboard/alerts returns community_alerts and health_events."""
    start = time.time()
    resp = api.get("/v1/vet/dashboard/alerts", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/dashboard/alerts: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "community_alerts" in body, f"Missing community_alerts: {body}"
    assert "health_events" in body, f"Missing health_events: {body}"
    assert isinstance(body["community_alerts"], list)
    assert isinstance(body["health_events"], list)


# ---------------------------------------------------------------------------
# Test 12: GET /v1/vet/my-cases works for any authenticated user
# ---------------------------------------------------------------------------


def test_my_cases_for_farmer(api, farmer_auth):
    """GET /v1/vet/my-cases returns the farmer's own consultation cases."""
    start = time.time()
    resp = api.get("/v1/vet/my-cases", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vet/my-cases farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] == len(body["data"])
