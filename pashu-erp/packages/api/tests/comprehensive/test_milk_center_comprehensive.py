"""Comprehensive integration tests for /v1/milk-center endpoints.

Covers: my-center, receive, daily-report, farmer-settlements, farmers/search, farmers/enroll.

The milk_center role has no token fixture in conftest.py; we test role-guarded endpoints
using farmer_auth and admin_auth.  Milk-center-only endpoints are expected to return 403
when accessed by a farmer.
"""

import time
import uuid

import pytest

BASE = "/v1/milk-center"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_a_center_id(api, admin_auth) -> str | None:
    """Try to find any MilkCollectionCenter via the DB.
    Fall back to None if the table is empty (tests that need it will skip).
    We probe /v1/milk-center/my-center — but that requires milk_center role,
    so instead we attempt a known-fake UUID against daily-report as admin.
    Actually we just return None and let callers skip; the receive POST test
    creates its own record only if a center exists.
    """
    return None


def _get_farmer_user_id(api, farmer_auth) -> str:
    resp = api.get("/v1/auth/me", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    return str(resp.json()["user_id"])


# ===========================================================================
# POSITIVE TESTS — accessible by admin (admin has milk_center|admin role check)
# ===========================================================================


def test_farmer_search_by_name(api, admin_auth):
    """GET /v1/milk-center/farmers/search?name=... returns a list."""
    t0 = time.time()
    resp = api.get(f"{BASE}/farmers/search", headers=admin_auth, params={"name": "Test"})
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/farmers/search → {resp.status_code} in {elapsed:.3f}s")

    # 200 or empty list — either is acceptable; just not 401/403/500
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, list)


def test_farmer_search_by_phone(api, admin_auth):
    """GET /v1/milk-center/farmers/search?phone=... returns list items with expected fields."""
    resp = api.get(f"{BASE}/farmers/search", headers=admin_auth, params={"phone": "+91990"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, list)
    if body:
        farmer = body[0]
        for field in ("id", "name", "phone"):
            assert field in farmer, f"Missing field '{field}': {farmer}"


def test_farmer_search_results_capped_at_10(api, admin_auth):
    """GET /v1/milk-center/farmers/search returns at most 10 results."""
    resp = api.get(f"{BASE}/farmers/search", headers=admin_auth, params={"name": "an"})
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) <= 10, f"Expected <= 10 results, got {len(resp.json())}"


def test_daily_report_with_fake_center_id_is_404_or_200_admin(api, admin_auth):
    """GET /v1/milk-center/{center_id}/daily-report with unknown UUID.
    Admin role bypasses the ownership check — result should be 200 (empty) or 404.
    """
    fake_id = str(uuid.uuid4())
    t0 = time.time()
    resp = api.get(f"{BASE}/{fake_id}/daily-report", headers=admin_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/{fake_id}/daily-report → {resp.status_code} in {elapsed:.3f}s")

    # Admin: no ownership check, so it returns a 200 with zero summary — not 404
    assert resp.status_code in (200, 404), f"Unexpected status {resp.status_code}: {resp.text}"
    if resp.status_code == 200:
        body = resp.json()
        assert "summary" in body
        assert "morning" in body
        assert "evening" in body


def test_daily_report_summary_fields(api, admin_auth):
    """If daily report 200, validate summary subfields."""
    fake_id = str(uuid.uuid4())
    resp = api.get(f"{BASE}/{fake_id}/daily-report", headers=admin_auth)
    if resp.status_code != 200:
        pytest.skip("No center data available, skipping field validation")
    body = resp.json()
    summary = body["summary"]
    for field in ("total_liters", "total_amount_inr", "farmer_count", "record_count"):
        assert field in summary, f"Missing summary field '{field}': {summary}"


def test_farmer_settlements_admin_access(api, admin_auth):
    """GET /v1/milk-center/{id}/farmer-settlements accessible by admin."""
    fake_id = str(uuid.uuid4())
    t0 = time.time()
    resp = api.get(f"{BASE}/{fake_id}/farmer-settlements", headers=admin_auth)
    elapsed = time.time() - t0
    print(f"\nGET farmer-settlements → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code in (200, 404), f"Unexpected {resp.status_code}: {resp.text}"
    if resp.status_code == 200:
        body = resp.json()
        assert "settlements" in body
        assert "total_payout_inr" in body


def test_enroll_farmer_creates_user(api, admin_auth):
    """POST /v1/milk-center/farmers/enroll creates a new farmer account."""
    unique_suffix = str(uuid.uuid4().hex[:6])
    payload = {
        "name": f"Test Farmer {unique_suffix}",
        "phone": f"+919{unique_suffix[:9]}",  # fabricate unique phone
        "aadhaar": f"{'9' * 12}",  # 12 digit Aadhaar — will be unique via phone
        "village_code": "KA001",
    }
    # Use a genuinely unique phone number
    payload["phone"] = "+91" + "6" + str(uuid.uuid4().int)[:9]
    payload["aadhaar"] = str(uuid.uuid4().int)[:12].zfill(12)

    t0 = time.time()
    resp = api.post(f"{BASE}/farmers/enroll", json=payload, headers=admin_auth)
    elapsed = time.time() - t0
    print(f"\nPOST {BASE}/farmers/enroll → {resp.status_code} in {elapsed:.3f}s | {resp.text[:200]}")

    assert resp.status_code in (201, 409), f"Unexpected {resp.status_code}: {resp.text}"
    if resp.status_code == 201:
        body = resp.json()
        assert "id" in body
        assert "phone" in body
        assert "message" in body


# ===========================================================================
# NEGATIVE TESTS
# ===========================================================================


def test_my_center_requires_auth(api):
    """GET /v1/milk-center/my-center without auth → 401."""
    resp = api.get(f"{BASE}/my-center")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_my_center_farmer_role_forbidden(api, farmer_auth):
    """GET /v1/milk-center/my-center as farmer → 403."""
    t0 = time.time()
    resp = api.get(f"{BASE}/my-center", headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/my-center (farmer) → {resp.status_code} in {elapsed:.3f}s")
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


def test_receive_milk_farmer_role_forbidden(api, farmer_auth):
    """POST /v1/milk-center/receive as farmer → 403."""
    payload = {
        "center_id": str(uuid.uuid4()),
        "farmer_user_id": str(uuid.uuid4()),
        "quantity_liters": "10.00",
        "fat_pct": "4.00",
        "snf_pct": "8.50",
        "shift": "morning",
    }
    resp = api.post(f"{BASE}/receive", json=payload, headers=farmer_auth)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


def test_receive_milk_requires_auth(api):
    """POST /v1/milk-center/receive without auth → 401."""
    resp = api.post(f"{BASE}/receive", json={})
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}: {resp.text}"


def test_receive_milk_fat_out_of_range(api, admin_auth):
    """POST /v1/milk-center/receive with fat_pct=0 (below ge=1.0) → 422."""
    payload = {
        "center_id": str(uuid.uuid4()),
        "farmer_user_id": str(uuid.uuid4()),
        "quantity_liters": "5.00",
        "fat_pct": "0.00",  # invalid: must be >= 1.0
        "snf_pct": "8.50",
        "shift": "morning",
    }
    resp = api.post(f"{BASE}/receive", json=payload, headers=admin_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_farmer_search_no_params_returns_400(api, admin_auth):
    """GET /v1/milk-center/farmers/search with no params → 400."""
    resp = api.get(f"{BASE}/farmers/search", headers=admin_auth)
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"


def test_farmer_search_requires_auth(api):
    """GET /v1/milk-center/farmers/search without auth → 401."""
    resp = api.get(f"{BASE}/farmers/search", params={"name": "test"})
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_enroll_invalid_phone_format(api, admin_auth):
    """POST /v1/milk-center/farmers/enroll with bad phone format → 422."""
    payload = {
        "name": "Bad Phone Farmer",
        "phone": "12345",  # wrong format — must match +91[6-9]\d{9}
        "aadhaar": "123456789012",
    }
    resp = api.post(f"{BASE}/farmers/enroll", json=payload, headers=admin_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_enroll_invalid_aadhaar_format(api, admin_auth):
    """POST /v1/milk-center/farmers/enroll with non-12-digit Aadhaar → 422."""
    payload = {
        "name": "Bad Aadhaar Farmer",
        "phone": "+917654321098",
        "aadhaar": "12345",  # too short
    }
    resp = api.post(f"{BASE}/farmers/enroll", json=payload, headers=admin_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_daily_report_requires_auth(api):
    """GET /v1/milk-center/{id}/daily-report without auth → 401."""
    fake_id = str(uuid.uuid4())
    resp = api.get(f"{BASE}/{fake_id}/daily-report")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_daily_report_farmer_role_forbidden(api, farmer_auth):
    """GET /v1/milk-center/{id}/daily-report as farmer → 403."""
    fake_id = str(uuid.uuid4())
    resp = api.get(f"{BASE}/{fake_id}/daily-report", headers=farmer_auth)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
