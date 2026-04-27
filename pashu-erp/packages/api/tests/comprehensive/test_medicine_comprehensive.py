"""Comprehensive integration tests for /v1/medicines endpoints.

Tests:
  - GET catalog (list) — pagination, envelope
  - POST /administer — animal ownership, medicine existence, withdrawal calculation
  - GET /withdrawal-status/{animal_id} — ownership check
  - Auth enforcement
  - Error cases: missing fields, fake UUIDs, wrong owner

Run: pytest tests/comprehensive/test_medicine_comprehensive.py -v
"""

import time

import pytest

FAKE_UUID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_farmer_animal_id(api, auth) -> str | None:
    """Return the first animal ID owned by the authed farmer."""
    resp = api.get("/v1/animals", headers=auth)
    if resp.status_code != 200:
        return None
    data = resp.json().get("data", [])
    return data[0]["id"] if data else None


def _get_medicine_id(api, auth) -> str | None:
    """Return the first medicine ID from the catalog."""
    resp = api.get("/v1/medicines", headers=auth)
    if resp.status_code != 200:
        return None
    data = resp.json().get("data", [])
    return str(data[0]["id"]) if data else None


# ---------------------------------------------------------------------------
# Test 1: GET /v1/medicines requires auth
# ---------------------------------------------------------------------------


def test_medicines_list_requires_auth(api):
    """GET /v1/medicines without auth returns 401."""
    start = time.time()
    resp = api.get("/v1/medicines")
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicines no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: GET /v1/medicines returns envelope with data/total
# ---------------------------------------------------------------------------


def test_medicines_list_envelope(api, farmer_auth):
    """GET /v1/medicines returns data/total envelope."""
    start = time.time()
    resp = api.get("/v1/medicines", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/medicines farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 0


# ---------------------------------------------------------------------------
# Test 3: GET /v1/medicines item schema
# ---------------------------------------------------------------------------


def test_medicines_list_item_schema(api, farmer_auth):
    """Each medicine in the catalog has required fields."""
    resp = api.get("/v1/medicines", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    if body["data"]:
        med = body["data"][0]
        assert "id" in med, f"Missing 'id': {med}"
        assert "name_en" in med, f"Missing 'name_en': {med}"
        assert "type" in med, f"Missing 'type': {med}"
        assert "withdrawal_milk_days" in med, f"Missing 'withdrawal_milk_days': {med}"
        assert "withdrawal_meat_days" in med, f"Missing 'withdrawal_meat_days': {med}"
        assert isinstance(med["withdrawal_milk_days"], int)
        assert isinstance(med["withdrawal_meat_days"], int)
        assert med["withdrawal_milk_days"] >= 0
        assert med["withdrawal_meat_days"] >= 0


# ---------------------------------------------------------------------------
# Test 4: GET /v1/medicines pagination — no overlap
# ---------------------------------------------------------------------------


def test_medicines_list_pagination_no_overlap(api, farmer_auth):
    """Paginated medicine list has no overlapping IDs across pages."""
    resp1 = api.get("/v1/medicines?offset=0&limit=5", headers=farmer_auth)
    resp2 = api.get("/v1/medicines?offset=5&limit=5", headers=farmer_auth)

    assert resp1.status_code == 200, f"Page 1 failed: {resp1.text}"
    assert resp2.status_code == 200, f"Page 2 failed: {resp2.text}"

    ids1 = {str(m["id"]) for m in resp1.json()["data"]}
    ids2 = {str(m["id"]) for m in resp2.json()["data"]}
    assert ids1.isdisjoint(ids2), f"Overlapping IDs: {ids1 & ids2}"


# ---------------------------------------------------------------------------
# Test 5: POST /v1/medicines/administer requires auth
# ---------------------------------------------------------------------------


def test_administer_requires_auth(api):
    """POST /v1/medicines/administer without auth returns 401."""
    start = time.time()
    resp = api.post(
        "/v1/medicines/administer",
        json={"animal_id": FAKE_UUID, "medicine_id": FAKE_UUID},
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/medicines/administer no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 6: POST /v1/medicines/administer missing required fields → 422
# ---------------------------------------------------------------------------


def test_administer_missing_fields(api, farmer_auth):
    """POST /v1/medicines/administer with empty body returns 422."""
    start = time.time()
    resp = api.post("/v1/medicines/administer", json={}, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] POST /v1/medicines/administer missing fields: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: POST /v1/medicines/administer fake animal_id → 404
# ---------------------------------------------------------------------------


def test_administer_fake_animal_returns_404(api, farmer_auth):
    """POST /v1/medicines/administer with nonexistent animal → 404."""
    med_id = _get_medicine_id(api, farmer_auth)
    if med_id is None:
        pytest.skip("No medicines in catalog")

    start = time.time()
    resp = api.post(
        "/v1/medicines/administer",
        json={"animal_id": FAKE_UUID, "medicine_id": med_id},
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/medicines/administer fake animal: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: POST /v1/medicines/administer happy path — creates record
# ---------------------------------------------------------------------------


def test_administer_happy_path(api, farmer_auth):
    """POST /v1/medicines/administer with valid data creates a record."""
    animal_id = _get_farmer_animal_id(api, farmer_auth)
    med_id = _get_medicine_id(api, farmer_auth)
    if not animal_id or not med_id:
        pytest.skip("Requires at least one animal and one medicine")

    start = time.time()
    resp = api.post(
        "/v1/medicines/administer",
        json={"animal_id": animal_id, "medicine_id": med_id},
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/medicines/administer success: {duration:.3f}s")

    assert resp.status_code == 201, (
        f"Expected 201, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert "id" in body, f"Missing 'id': {body}"
    assert "animal_id" in body, f"Missing 'animal_id': {body}"
    assert "medicine" in body, f"Missing 'medicine': {body}"
    assert "administered_at" in body, f"Missing 'administered_at': {body}"


# ---------------------------------------------------------------------------
# Test 9: GET /v1/medicines/withdrawal-status/{animal_id} requires auth
# ---------------------------------------------------------------------------


def test_withdrawal_status_requires_auth(api):
    """GET /v1/medicines/withdrawal-status/<uuid> without auth → 401."""
    start = time.time()
    resp = api.get(f"/v1/medicines/withdrawal-status/{FAKE_UUID}")
    duration = time.time() - start
    print(f"\n[timing] GET withdrawal-status no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 10: GET /v1/medicines/withdrawal-status/{fake_uuid} → 404
# ---------------------------------------------------------------------------


def test_withdrawal_status_fake_animal(api, farmer_auth):
    """GET /v1/medicines/withdrawal-status/<fake_uuid> returns 404."""
    start = time.time()
    resp = api.get(
        f"/v1/medicines/withdrawal-status/{FAKE_UUID}", headers=farmer_auth
    )
    duration = time.time() - start
    print(f"\n[timing] GET withdrawal-status fake uuid: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/medicines/withdrawal-status — schema validation
# ---------------------------------------------------------------------------


def test_withdrawal_status_schema(api, farmer_auth):
    """GET withdrawal-status for own animal returns proper schema."""
    animal_id = _get_farmer_animal_id(api, farmer_auth)
    if not animal_id:
        pytest.skip("No animals found for farmer")

    start = time.time()
    resp = api.get(
        f"/v1/medicines/withdrawal-status/{animal_id}", headers=farmer_auth
    )
    duration = time.time() - start
    print(f"\n[timing] GET withdrawal-status own animal: {duration:.3f}s")

    assert resp.status_code == 200, (
        f"Expected 200, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()

    assert "animal_id" in body, f"Missing 'animal_id': {body}"
    assert "active_withdrawals" in body, f"Missing 'active_withdrawals': {body}"
    assert "milk_safe" in body, f"Missing 'milk_safe': {body}"
    assert "meat_safe" in body, f"Missing 'meat_safe': {body}"
    assert isinstance(body["active_withdrawals"], list)
    assert isinstance(body["milk_safe"], bool)
    assert isinstance(body["meat_safe"], bool)


# ---------------------------------------------------------------------------
# Test 12: GET /v1/medicines/withdrawal-status cross-owner → 403
# ---------------------------------------------------------------------------


def test_withdrawal_status_cross_owner(api, farmer_auth, farmer2_auth):
    """GET withdrawal-status for another farmer's animal → 403."""
    resp = api.get("/v1/animals", headers=farmer2_auth)
    if resp.status_code != 200 or not resp.json().get("data"):
        pytest.skip("No animals found for farmer2")
    animal_id = resp.json()["data"][0]["id"]

    start = time.time()
    resp = api.get(
        f"/v1/medicines/withdrawal-status/{animal_id}", headers=farmer_auth
    )
    duration = time.time() - start
    print(f"\n[timing] GET withdrawal-status cross-owner: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403, got {resp.status_code}: {resp.text}"
    )
