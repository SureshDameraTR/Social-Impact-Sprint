"""Comprehensive integration tests for /v1/medicine-log endpoints.

The medicine-log router is a mobile-compatibility alias for withdrawal data.
It has one primary endpoint:
  - GET /v1/medicine-log/withdrawals

We derive 10 tests by varying auth roles, query contexts, and edge cases.

Run: pytest tests/comprehensive/test_medicine_log_comprehensive.py -v
"""

import time

import pytest


# ---------------------------------------------------------------------------
# Test 1: GET /v1/medicine-log/withdrawals requires auth
# ---------------------------------------------------------------------------


def test_withdrawals_requires_auth(api):
    """GET /v1/medicine-log/withdrawals without auth returns 401."""
    start = time.time()
    resp = api.get("/v1/medicine-log/withdrawals")
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicine-log/withdrawals no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: GET /v1/medicine-log/withdrawals returns data/total envelope
# ---------------------------------------------------------------------------


def test_withdrawals_envelope_structure(api, farmer_auth):
    """GET /v1/medicine-log/withdrawals returns proper data/total envelope."""
    start = time.time()
    resp = api.get("/v1/medicine-log/withdrawals", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicine-log/withdrawals farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 0


# ---------------------------------------------------------------------------
# Test 3: total matches length of data array
# ---------------------------------------------------------------------------


def test_withdrawals_total_matches_data_length(api, farmer_auth):
    """total in withdrawal response equals len(data)."""
    resp = api.get("/v1/medicine-log/withdrawals", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    assert body["total"] == len(body["data"]), (
        f"total={body['total']} does not match len(data)={len(body['data'])}"
    )


# ---------------------------------------------------------------------------
# Test 4: Each withdrawal item has the expected fields
# ---------------------------------------------------------------------------


def test_withdrawals_item_schema(api, farmer_auth):
    """If withdrawal items exist, they have all required fields."""
    resp = api.get("/v1/medicine-log/withdrawals", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    for item in body["data"]:
        assert "animal_id" in item, f"Missing 'animal_id': {item}"
        assert "medicine" in item, f"Missing 'medicine': {item}"
        assert "administered_at" in item, f"Missing 'administered_at': {item}"
        assert "milk_safe" in item, f"Missing 'milk_safe': {item}"
        assert "meat_safe" in item, f"Missing 'meat_safe': {item}"
        assert isinstance(item["milk_safe"], bool)
        assert isinstance(item["meat_safe"], bool)


# ---------------------------------------------------------------------------
# Test 5: All returned items are active withdrawals (milk or meat active)
# ---------------------------------------------------------------------------


def test_withdrawals_only_active_items(api, farmer_auth):
    """Each item in the response has at least one active withdrawal."""
    resp = api.get("/v1/medicine-log/withdrawals", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    for item in body["data"]:
        # Active means at least one withdrawal date is set
        milk_active = item.get("milk_withdrawal_until") is not None
        meat_active = item.get("meat_withdrawal_until") is not None
        assert milk_active or meat_active, (
            f"Item has no active withdrawal: {item}"
        )


# ---------------------------------------------------------------------------
# Test 6: farmer2 gets their own withdrawals (data isolation)
# ---------------------------------------------------------------------------


def test_withdrawals_farmer_data_isolation(api, farmer_auth, farmer2_auth):
    """Two different farmers get independent withdrawal lists."""
    resp1 = api.get("/v1/medicine-log/withdrawals", headers=farmer_auth)
    resp2 = api.get("/v1/medicine-log/withdrawals", headers=farmer2_auth)

    assert resp1.status_code == 200, f"farmer1 failed: {resp1.text}"
    assert resp2.status_code == 200, f"farmer2 failed: {resp2.text}"

    # The animal_ids should not overlap between farmers
    ids1 = {item["animal_id"] for item in resp1.json()["data"]}
    ids2 = {item["animal_id"] for item in resp2.json()["data"]}
    # If both are non-empty, they must be disjoint (no shared animals)
    if ids1 and ids2:
        assert ids1.isdisjoint(ids2), (
            f"Farmers share animal withdrawal data: {ids1 & ids2}"
        )


# ---------------------------------------------------------------------------
# Test 7: Admin user can also call the endpoint
# ---------------------------------------------------------------------------


def test_withdrawals_accessible_by_admin(api, admin_auth):
    """GET /v1/medicine-log/withdrawals works for admin role."""
    start = time.time()
    resp = api.get("/v1/medicine-log/withdrawals", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicine-log/withdrawals admin: {duration:.3f}s")

    assert resp.status_code == 200, (
        f"Expected 200 for admin, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert "data" in body and "total" in body


# ---------------------------------------------------------------------------
# Test 8: Vet user can call the endpoint
# ---------------------------------------------------------------------------


def test_withdrawals_accessible_by_vet(api, vet_auth):
    """GET /v1/medicine-log/withdrawals works for vet role."""
    start = time.time()
    resp = api.get("/v1/medicine-log/withdrawals", headers=vet_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicine-log/withdrawals vet: {duration:.3f}s")

    assert resp.status_code == 200, (
        f"Expected 200 for vet, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert "data" in body and "total" in body


# ---------------------------------------------------------------------------
# Test 9: Response time is under 2 seconds
# ---------------------------------------------------------------------------


def test_withdrawals_response_time(api, farmer_auth):
    """GET /v1/medicine-log/withdrawals responds in under 2 seconds."""
    start = time.time()
    resp = api.get("/v1/medicine-log/withdrawals", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicine-log/withdrawals timing: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    assert duration < 2.0, f"Response too slow: {duration:.3f}s (threshold: 2.0s)"


# ---------------------------------------------------------------------------
# Test 10: Bearer token with garbage value returns 401
# ---------------------------------------------------------------------------


def test_withdrawals_garbage_token_rejected(api):
    """GET /v1/medicine-log/withdrawals with malformed Bearer token → 401."""
    start = time.time()
    resp = api.get(
        "/v1/medicine-log/withdrawals",
        headers={"Authorization": "Bearer not.a.real.jwt"},
    )
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicine-log/withdrawals garbage token: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )
