"""Comprehensive integration tests for /v1/shg endpoints.

Tests:
  - POST create SHG group
  - GET list (scoped to admin_user_id)
  - GET by id (ownership enforcement)
  - PATCH update (group admin only)
  - GET compliance score (Panchsutra)
  - Auth enforcement
  - Error cases: missing fields, fake UUIDs, cross-owner access

Run: pytest tests/comprehensive/test_shg_comprehensive.py -v
"""

import time

import pytest

FAKE_UUID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_shg(api, auth, name="Test SHG Group") -> dict:
    """Create a minimal SHG group and return the response body."""
    resp = api.post(
        "/v1/shg",
        json={
            "name": name,
            "district": "Tumkur",
            "village_code": "KA-TU-001",
            "member_count": 12,
            "women_only": True,
            "formation_date": "2023-01-15",
            "total_savings": "5000.00",
            "grading": "B",
            "panchsutra_compliance": {
                "regular_meetings": True,
                "regular_savings": True,
                "regular_internal_lending": False,
                "regular_repayment": True,
                "uptodate_bookkeeping": False,
            },
        },
        headers=auth,
    )
    return resp


# ---------------------------------------------------------------------------
# Test 1: POST /v1/shg requires auth
# ---------------------------------------------------------------------------


def test_create_shg_requires_auth(api):
    """POST /v1/shg without auth returns 401."""
    start = time.time()
    resp = api.post("/v1/shg", json={"name": "Test SHG"})
    duration = time.time() - start
    print(f"\n[timing] POST /v1/shg no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: POST /v1/shg missing required name → 422
# ---------------------------------------------------------------------------


def test_create_shg_missing_name(api, farmer_auth):
    """POST /v1/shg without name field returns 422."""
    start = time.time()
    resp = api.post("/v1/shg", json={}, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] POST /v1/shg missing name: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 3: POST /v1/shg happy path — creates group and returns schema
# ---------------------------------------------------------------------------


def test_create_shg_happy_path(api, farmer_auth):
    """POST /v1/shg creates a group and returns SHGGroupRead schema."""
    start = time.time()
    resp = _create_shg(api, farmer_auth, name="Namma Mahila SHG")
    duration = time.time() - start
    print(f"\n[timing] POST /v1/shg success: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "id" in body, f"Missing 'id': {body}"
    assert "name" in body, f"Missing 'name': {body}"
    assert "admin_user_id" in body, f"Missing 'admin_user_id': {body}"
    assert "member_count" in body, f"Missing 'member_count': {body}"
    assert "women_only" in body, f"Missing 'women_only': {body}"
    assert "grading" in body, f"Missing 'grading': {body}"
    assert body["name"] == "Namma Mahila SHG"
    assert body["member_count"] == 12
    assert body["women_only"] is True


# ---------------------------------------------------------------------------
# Test 4: GET /v1/shg returns data/total envelope scoped to current user
# ---------------------------------------------------------------------------


def test_list_shg_envelope_structure(api, farmer_auth):
    """GET /v1/shg returns data/total envelope with user-scoped groups."""
    start = time.time()
    resp = api.get("/v1/shg", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/shg farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    # total is the full DB count; data is the paginated slice (may be less than total)
    assert body["total"] >= len(body["data"])


# ---------------------------------------------------------------------------
# Test 5: GET /v1/shg pagination — limit works
# ---------------------------------------------------------------------------


def test_list_shg_pagination_limit(api, farmer_auth):
    """GET /v1/shg respects the limit query parameter."""
    resp = api.get("/v1/shg?limit=1", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    assert len(body["data"]) <= 1, (
        f"Expected at most 1 item, got {len(body['data'])}"
    )


# ---------------------------------------------------------------------------
# Test 6: GET /v1/shg/{shg_id} happy path — returns SHGGroupRead
# ---------------------------------------------------------------------------


def test_get_shg_by_id(api, farmer_auth):
    """GET /v1/shg/{id} returns the correct SHG group."""
    create_resp = _create_shg(api, farmer_auth, name="Akka Sahayog SHG")
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    shg_id = create_resp.json()["id"]

    start = time.time()
    resp = api.get(f"/v1/shg/{shg_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/shg/{shg_id}: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["id"] == shg_id, f"ID mismatch: {body['id']} != {shg_id}"
    assert body["name"] == "Akka Sahayog SHG"


# ---------------------------------------------------------------------------
# Test 7: GET /v1/shg/{fake_uuid} → 404
# ---------------------------------------------------------------------------


def test_get_shg_nonexistent_returns_404(api, farmer_auth):
    """GET /v1/shg/<fake_uuid> returns 404."""
    start = time.time()
    resp = api.get(f"/v1/shg/{FAKE_UUID}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/shg fake uuid: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: GET /v1/shg/{id} cross-owner → 403
# ---------------------------------------------------------------------------


def test_get_shg_cross_owner_forbidden(api, farmer_auth, farmer2_auth):
    """GET /v1/shg/{id} for another user's group returns 403."""
    # farmer creates a group
    create_resp = _create_shg(api, farmer_auth, name="Farmer1 SHG Private")
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    shg_id = create_resp.json()["id"]

    # farmer2 tries to access it
    start = time.time()
    resp = api.get(f"/v1/shg/{shg_id}", headers=farmer2_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/shg cross-owner: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for cross-owner access, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: PATCH /v1/shg/{id} — update fields
# ---------------------------------------------------------------------------


def test_update_shg(api, farmer_auth):
    """PATCH /v1/shg/{id} updates specified fields."""
    create_resp = _create_shg(api, farmer_auth, name="Update Test SHG")
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    shg_id = create_resp.json()["id"]

    start = time.time()
    resp = api.patch(
        f"/v1/shg/{shg_id}",
        json={"member_count": 20, "grading": "A"},
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] PATCH /v1/shg update: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["member_count"] == 20, f"member_count not updated: {body}"
    assert body["grading"] == "A", f"grading not updated: {body}"


# ---------------------------------------------------------------------------
# Test 10: PATCH /v1/shg/{id} cross-owner → 403
# ---------------------------------------------------------------------------


def test_update_shg_cross_owner_forbidden(api, farmer_auth, farmer2_auth):
    """PATCH /v1/shg/{id} by non-owner returns 403."""
    create_resp = _create_shg(api, farmer_auth, name="Patch Cross Owner Test")
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    shg_id = create_resp.json()["id"]

    start = time.time()
    resp = api.patch(
        f"/v1/shg/{shg_id}",
        json={"member_count": 999},
        headers=farmer2_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] PATCH /v1/shg cross-owner: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/shg/{id}/compliance returns Panchsutra score
# ---------------------------------------------------------------------------


def test_panchsutra_compliance_score(api, farmer_auth):
    """GET /v1/shg/{id}/compliance returns score with 5 principles."""
    create_resp = _create_shg(api, farmer_auth, name="Compliance Test SHG")
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    shg_id = create_resp.json()["id"]

    start = time.time()
    resp = api.get(f"/v1/shg/{shg_id}/compliance", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/shg compliance: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "shg_id" in body, f"Missing 'shg_id': {body}"
    assert "principles" in body, f"Missing 'principles': {body}"
    assert "score" in body, f"Missing 'score': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert "percentage" in body, f"Missing 'percentage': {body}"
    assert "grading" in body, f"Missing 'grading': {body}"
    assert body["total"] == 5, f"Expected 5 principles, got {body['total']}"
    assert 0 <= body["score"] <= 5, f"Score out of range: {body['score']}"
    assert 0.0 <= body["percentage"] <= 100.0, f"Percentage out of range: {body['percentage']}"


# ---------------------------------------------------------------------------
# Test 12: Kannada SHG name is accepted
# ---------------------------------------------------------------------------


def test_create_shg_kannada_name(api, farmer_auth):
    """POST /v1/shg with Kannada name returns 201."""
    start = time.time()
    resp = api.post(
        "/v1/shg",
        json={
            "name": "ನಮ್ಮ ಮಹಿಳಾ ಸ್ವ-ಸಹಾಯ ಗುಂಪು",  # Kannada: Our Women's Self Help Group
            "district": "Mysuru",
            "member_count": 10,
            "women_only": True,
        },
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/shg Kannada name: {duration:.3f}s")

    assert resp.status_code == 201, (
        f"Expected 201 for Kannada SHG name, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert "ನಮ್ಮ" in body["name"], f"Kannada name not preserved: {body['name']}"
