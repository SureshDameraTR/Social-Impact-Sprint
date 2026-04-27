"""Comprehensive integration tests for /v1/farmers and /v1/users/profile endpoints.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_users_comprehensive.py -v
"""

import time

import pytest


# ---------------------------------------------------------------------------
# Test 1: GET /v1/farmers — admin can list farmers
# ---------------------------------------------------------------------------

def test_list_farmers_admin_happy_path(api, admin_auth):
    """GET /v1/farmers as admin returns paginated farmer list with envelope."""
    start = time.time()
    resp = api.get("/v1/farmers", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/farmers: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data' key: {body}"
    assert "total" in body, f"Missing 'total' key: {body}"
    assert "limit" in body, f"Missing 'limit' key: {body}"
    assert "offset" in body, f"Missing 'offset' key: {body}"
    assert isinstance(body["data"], list), f"'data' should be a list: {type(body['data'])}"
    assert isinstance(body["total"], int), f"'total' should be int: {type(body['total'])}"


# ---------------------------------------------------------------------------
# Test 2: GET /v1/farmers — farmer token returns 403
# ---------------------------------------------------------------------------

def test_list_farmers_farmer_token_403(api, farmer_auth):
    """GET /v1/farmers with farmer token returns 403 (admin-only)."""
    resp = api.get("/v1/farmers", headers=farmer_auth)
    assert resp.status_code == 403, (
        f"Expected 403 for farmer token on /v1/farmers, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 3: GET /v1/farmers — 401 without auth
# ---------------------------------------------------------------------------

def test_list_farmers_unauthenticated_401(api):
    """GET /v1/farmers without auth header returns 401."""
    resp = api.get("/v1/farmers")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: GET /v1/farmers — each farmer item has expected fields
# ---------------------------------------------------------------------------

def test_list_farmers_item_schema(api, admin_auth):
    """Each farmer item in the list has id, name, phone, animals_count fields."""
    resp = api.get("/v1/farmers?limit=5", headers=admin_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    for farmer in body["data"]:
        assert "id" in farmer, f"Farmer missing 'id': {farmer}"
        assert "name" in farmer, f"Farmer missing 'name': {farmer}"
        assert "phone" in farmer, f"Farmer missing 'phone': {farmer}"
        assert "animals_count" in farmer, f"Farmer missing 'animals_count': {farmer}"
        assert isinstance(farmer["animals_count"], int), (
            f"animals_count should be int: {farmer['animals_count']}"
        )
        assert farmer["animals_count"] >= 0, (
            f"animals_count should be >= 0: {farmer['animals_count']}"
        )


# ---------------------------------------------------------------------------
# Test 5: GET /v1/farmers — pagination limit/offset
# ---------------------------------------------------------------------------

def test_list_farmers_pagination(api, admin_auth):
    """GET /v1/farmers with limit=2&offset=0 returns at most 2 items; offset shifts results."""
    resp1 = api.get("/v1/farmers?limit=2&offset=0", headers=admin_auth)
    assert resp1.status_code == 200, f"Page 1 failed: {resp1.text}"
    body1 = resp1.json()
    assert len(body1["data"]) <= 2, f"Limit=2 returned {len(body1['data'])} items"
    assert body1["limit"] == 2
    assert body1["offset"] == 0

    resp2 = api.get("/v1/farmers?limit=2&offset=2", headers=admin_auth)
    assert resp2.status_code == 200, f"Page 2 failed: {resp2.text}"
    body2 = resp2.json()
    assert body2["offset"] == 2

    # No overlap between pages
    ids1 = {f["id"] for f in body1["data"]}
    ids2 = {f["id"] for f in body2["data"]}
    assert ids1.isdisjoint(ids2), f"Pages overlap: {ids1 & ids2}"


# ---------------------------------------------------------------------------
# Test 6: GET /v1/farmers — negative offset returns 422
# ---------------------------------------------------------------------------

def test_list_farmers_negative_offset_422(api, admin_auth):
    """GET /v1/farmers?offset=-1 returns 422 validation error."""
    resp = api.get("/v1/farmers?offset=-1", headers=admin_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for negative offset, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: GET /v1/farmers — limit over max returns 422
# ---------------------------------------------------------------------------

def test_list_farmers_limit_over_max_422(api, admin_auth):
    """GET /v1/farmers?limit=201 (over max 200) returns 422 validation error."""
    resp = api.get("/v1/farmers?limit=201", headers=admin_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for limit > 200, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: GET /v1/users/profile — farmer can read own profile
# ---------------------------------------------------------------------------

def test_get_profile_farmer_happy_path(api, farmer_auth):
    """GET /v1/users/profile as farmer returns own user profile."""
    start = time.time()
    resp = api.get("/v1/users/profile", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/users/profile (farmer): {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    expected_keys = ["id", "name", "phone", "role", "animal_count"]
    for key in expected_keys:
        assert key in body, f"Profile missing '{key}': {body}"

    assert body["role"] == "farmer", f"Expected role=farmer: {body['role']}"
    assert isinstance(body["animal_count"], int), (
        f"animal_count should be int: {body['animal_count']}"
    )
    assert body["animal_count"] >= 0


# ---------------------------------------------------------------------------
# Test 9: GET /v1/users/profile — admin can read own profile
# ---------------------------------------------------------------------------

def test_get_profile_admin_happy_path(api, admin_auth):
    """GET /v1/users/profile as admin returns admin profile with role=admin."""
    resp = api.get("/v1/users/profile", headers=admin_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["role"] == "admin", f"Expected role=admin: {body['role']}"
    assert "id" in body and "phone" in body


# ---------------------------------------------------------------------------
# Test 10: GET /v1/users/profile — 401 without auth
# ---------------------------------------------------------------------------

def test_get_profile_unauthenticated_401(api):
    """GET /v1/users/profile without auth header returns 401."""
    resp = api.get("/v1/users/profile")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/users/profile — two farmers see different profiles
# ---------------------------------------------------------------------------

def test_get_profile_isolated_per_user(api, farmer_auth, farmer2_auth):
    """Two different farmer tokens return different profile IDs (isolation)."""
    resp1 = api.get("/v1/users/profile", headers=farmer_auth)
    resp2 = api.get("/v1/users/profile", headers=farmer2_auth)

    assert resp1.status_code == 200, f"Farmer1 profile failed: {resp1.text}"
    assert resp2.status_code == 200, f"Farmer2 profile failed: {resp2.text}"

    id1 = resp1.json()["id"]
    id2 = resp2.json()["id"]
    assert id1 != id2, f"Two different tokens returned same user ID: {id1}"


# ---------------------------------------------------------------------------
# Test 12: GET /v1/users/profile — vet sees role=vet
# ---------------------------------------------------------------------------

def test_get_profile_vet_role(api, vet_auth):
    """GET /v1/users/profile as vet returns role=vet."""
    resp = api.get("/v1/users/profile", headers=vet_auth)
    assert resp.status_code == 200, f"Expected 200 for vet, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["role"] == "vet", f"Expected role=vet: {body['role']}"
