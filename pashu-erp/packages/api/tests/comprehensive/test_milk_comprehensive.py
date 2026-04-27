"""Comprehensive integration tests for /v1/milk endpoints.

Covers: list, today, history, daily-summary, yield POST, farmer history, center daily.
Reads the REAL API at localhost:8000 — requires docker compose to be running.
"""

import time
import uuid

import pytest

BASE = "/v1/milk"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_farmer_animal_id(api, farmer_auth) -> str | None:
    """Return the first animal owned by the farmer, or None."""
    resp = api.get("/v1/animals", headers=farmer_auth)
    if resp.status_code == 200:
        data = resp.json().get("data", [])
        if data:
            return str(data[0]["id"])
    return None


def _get_farmer_user_id(api, farmer_auth) -> str:
    """Return the authenticated farmer's user_id."""
    resp = api.get("/v1/auth/me", headers=farmer_auth)
    assert resp.status_code == 200, f"Failed to get user: {resp.text}"
    return str(resp.json()["user_id"])


# ===========================================================================
# POSITIVE TESTS
# ===========================================================================


def test_list_milk_records_returns_envelope(api, farmer_auth):
    """GET /v1/milk returns {data, total, limit, offset}."""
    t0 = time.time()
    resp = api.get(BASE, headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE} → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body, f"Missing 'data' key: {body}"
    assert "total" in body, f"Missing 'total' key: {body}"
    assert "limit" in body, f"Missing 'limit' key: {body}"
    assert "offset" in body, f"Missing 'offset' key: {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 0


def test_list_milk_records_item_schema(api, farmer_auth):
    """Each record in list response has required fields."""
    resp = api.get(BASE, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]

    if data:
        record = data[0]
        for field in ("id", "animal_id", "user_id", "quantity_liters", "session", "recorded_at"):
            assert field in record, f"Missing field '{field}': {record}"
        assert record["session"] in ("morning", "evening"), f"Bad session: {record['session']}"


def test_admin_list_milk_sees_all(api, admin_auth, farmer_auth):
    """Admin gets all records; farmer gets only own."""
    admin_resp = api.get(BASE, headers=admin_auth)
    farmer_resp = api.get(BASE, headers=farmer_auth)

    assert admin_resp.status_code == 200, admin_resp.text
    assert farmer_resp.status_code == 200, farmer_resp.text

    admin_total = admin_resp.json()["total"]
    farmer_total = farmer_resp.json()["total"]
    # Admin total must be >= farmer total (farmer's subset)
    assert admin_total >= farmer_total, (
        f"Admin total {admin_total} < farmer total {farmer_total}"
    )


def test_get_today_total_schema(api, farmer_auth):
    """GET /v1/milk/today returns correct fields."""
    t0 = time.time()
    resp = api.get(f"{BASE}/today", headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/today → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "user_id" in body, f"Missing user_id: {body}"
    assert "date" in body, f"Missing date: {body}"
    assert "total_liters" in body, f"Missing total_liters: {body}"
    assert "entries" in body, f"Missing entries: {body}"
    assert isinstance(body["total_liters"], (int, float))
    assert body["total_liters"] >= 0
    assert isinstance(body["entries"], int)


def test_get_history_returns_envelope(api, farmer_auth):
    """GET /v1/milk/history returns paginated envelope."""
    t0 = time.time()
    resp = api.get(f"{BASE}/history", headers=farmer_auth, params={"days": 7})
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/history → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body
    assert "total" in body
    assert isinstance(body["data"], list)
    assert body["total"] >= 0


def test_get_daily_summary_schema(api, farmer_auth):
    """GET /v1/milk/daily-summary returns period_days + data list."""
    t0 = time.time()
    resp = api.get(f"{BASE}/daily-summary", headers=farmer_auth, params={"days": 7})
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/daily-summary → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "period_days" in body, f"Missing period_days: {body}"
    assert "data" in body, f"Missing data: {body}"
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 7  # one entry per day

    if body["data"]:
        entry = body["data"][0]
        assert "date" in entry
        assert "liters" in entry
        assert "farmers" in entry


def test_post_yield_creates_record(api, farmer_auth):
    """POST /v1/milk/yield creates a yield record (requires animal)."""
    animal_id = _get_farmer_animal_id(api, farmer_auth)
    if animal_id is None:
        pytest.skip("No animal available for farmer — seed data missing")

    payload = {
        "animal_id": animal_id,
        "quantity_liters": "5.50",
        "session": "morning",
        "notes": "Integration test entry",
    }
    t0 = time.time()
    resp = api.post(f"{BASE}/yield", json=payload, headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nPOST {BASE}/yield → {resp.status_code} in {elapsed:.3f}s | body: {resp.text[:200]}")

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "id" in body
    assert body["animal_id"] == animal_id
    assert float(body["quantity_liters"]) == pytest.approx(5.50)
    assert body["session"] == "morning"


def test_pagination_no_overlap(api, admin_auth):
    """Two pages of milk records must not overlap."""
    page1 = api.get(BASE, headers=admin_auth, params={"limit": 5, "offset": 0})
    page2 = api.get(BASE, headers=admin_auth, params={"limit": 5, "offset": 5})

    assert page1.status_code == 200, page1.text
    assert page2.status_code == 200, page2.text

    ids1 = {r["id"] for r in page1.json()["data"]}
    ids2 = {r["id"] for r in page2.json()["data"]}
    overlap = ids1 & ids2
    assert not overlap, f"Overlapping IDs across pages: {overlap}"


def test_farmer_history_endpoint_self_access(api, farmer_auth):
    """GET /v1/milk/farmer/{user_id}/history works for own user_id."""
    user_id = _get_farmer_user_id(api, farmer_auth)
    t0 = time.time()
    resp = api.get(f"{BASE}/farmer/{user_id}/history", headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/farmer/{user_id}/history → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body
    assert "total" in body


# ===========================================================================
# NEGATIVE TESTS
# ===========================================================================


def test_list_milk_requires_auth(api):
    """GET /v1/milk without auth → 401."""
    resp = api.get(BASE)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_today_requires_auth(api):
    """GET /v1/milk/today without auth → 401."""
    resp = api.get(f"{BASE}/today")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_history_requires_auth(api):
    """GET /v1/milk/history without auth → 401."""
    resp = api.get(f"{BASE}/history")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_post_yield_missing_required_fields(api, farmer_auth):
    """POST /v1/milk/yield with no body → 422."""
    resp = api.post(f"{BASE}/yield", json={}, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_post_yield_non_existent_animal(api, farmer_auth):
    """POST /v1/milk/yield with fake animal_id → 404."""
    payload = {
        "animal_id": str(uuid.uuid4()),
        "quantity_liters": "3.00",
        "session": "evening",
    }
    resp = api.post(f"{BASE}/yield", json=payload, headers=farmer_auth)
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"


def test_post_yield_negative_quantity(api, farmer_auth):
    """POST /v1/milk/yield with quantity <= 0 → 422."""
    animal_id = _get_farmer_animal_id(api, farmer_auth)
    if animal_id is None:
        pytest.skip("No animal available")

    payload = {
        "animal_id": animal_id,
        "quantity_liters": "-1.00",
        "session": "morning",
    }
    resp = api.post(f"{BASE}/yield", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_post_yield_invalid_session(api, farmer_auth):
    """POST /v1/milk/yield with invalid session value → 422."""
    animal_id = _get_farmer_animal_id(api, farmer_auth)
    if animal_id is None:
        pytest.skip("No animal available")

    payload = {
        "animal_id": animal_id,
        "quantity_liters": "3.00",
        "session": "afternoon",  # not a valid MilkSession value
    }
    resp = api.post(f"{BASE}/yield", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_farmer_history_other_user_forbidden(api, farmer_auth, farmer2_auth):
    """GET /v1/milk/farmer/{other_user_id}/history → 403 for a different farmer."""
    other_id = _get_farmer_user_id(api, farmer2_auth)
    resp = api.get(f"{BASE}/farmer/{other_id}/history", headers=farmer_auth)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


def test_daily_summary_days_boundary(api, farmer_auth):
    """GET /v1/milk/daily-summary?days=0 → 422 (ge=1)."""
    resp = api.get(f"{BASE}/daily-summary", headers=farmer_auth, params={"days": 0})
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_history_days_over_limit(api, farmer_auth):
    """GET /v1/milk/history?days=366 → 422 (le=365)."""
    resp = api.get(f"{BASE}/history", headers=farmer_auth, params={"days": 366})
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
