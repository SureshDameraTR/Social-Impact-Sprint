"""Comprehensive integration tests for /v1/insurance endpoints.

Hits the REAL running API at localhost:8000 with a real PostgreSQL database.
Read insurance.py and the insurance schema before editing.

Endpoints:
  GET  /v1/insurance/policies/{user_id}          — user's animal policies
  POST /v1/insurance/claims                       — file a claim
  GET  /v1/insurance/premium-estimate/{animal_id} — estimate premium

Auth rules:
  - policies: owner can see their own; admin can see any; others get 403
  - claims: only the animal's owner can file
  - premium-estimate: only owner or admin

Run: pytest tests/comprehensive/test_insurance_comprehensive.py -v
"""

import time
from uuid import uuid4

import pytest


# ---------------------------------------------------------------------------
# Helper: get the current user's ID from the auth token
# ---------------------------------------------------------------------------


def _get_my_user_id(api, auth_headers: dict) -> str:
    """Retrieve the authenticated user's UUID via GET /v1/users/profile."""
    resp = api.get("/v1/users/profile", headers=auth_headers)
    assert resp.status_code == 200, f"Could not fetch /v1/users/profile: {resp.text}"
    return str(resp.json()["id"])


def _get_my_animals(api, auth_headers: dict) -> list:
    """Retrieve the authenticated user's animals."""
    resp = api.get("/v1/animals", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return resp.json().get("data", [])


# ===========================================================================
# Positive tests
# ===========================================================================


def test_insurance_policies_own_user_returns_envelope(api, farmer_auth):
    """GET /v1/insurance/policies/{user_id} returns data+total envelope for own user."""
    user_id = _get_my_user_id(api, farmer_auth)

    start = time.time()
    resp = api.get(f"/v1/insurance/policies/{user_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] policies own user: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] == len(body["data"])


def test_insurance_policies_schema_when_data_exists(api, farmer_auth):
    """If policies exist for the farmer, each item has required InsurancePolicyRead fields."""
    user_id = _get_my_user_id(api, farmer_auth)
    resp = api.get(f"/v1/insurance/policies/{user_id}", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    if body["data"]:
        policy = body["data"][0]
        for field in ["id", "animal_id", "provider", "policy_number", "premium_amount",
                      "coverage_amount", "valid_from", "valid_to", "status"]:
            assert field in policy, f"Missing '{field}' in policy: {policy}"
        assert policy["status"] in ("active", "expired", "claimed")


def test_insurance_policies_admin_can_access_any_user(api, admin_auth, farmer_auth):
    """Admin can call policies endpoint for another user's ID."""
    farmer_id = _get_my_user_id(api, farmer_auth)
    resp = api.get(f"/v1/insurance/policies/{farmer_id}", headers=admin_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body


def test_insurance_policies_pagination(api, farmer_auth):
    """Pagination params offset and limit are respected."""
    user_id = _get_my_user_id(api, farmer_auth)

    resp_full = api.get(
        f"/v1/insurance/policies/{user_id}", params={"limit": 50}, headers=farmer_auth
    )
    resp_limited = api.get(
        f"/v1/insurance/policies/{user_id}", params={"limit": 1}, headers=farmer_auth
    )
    assert resp_full.status_code == 200, resp_full.text
    assert resp_limited.status_code == 200, resp_limited.text

    full_total = resp_full.json()["total"]
    limited_data = resp_limited.json()["data"]
    assert len(limited_data) <= 1, f"Expected at most 1 result, got {len(limited_data)}"


def test_insurance_premium_estimate_for_own_animal(api, farmer_auth):
    """GET /v1/insurance/premium-estimate/{animal_id} returns PremiumEstimate schema."""
    animals = _get_my_animals(api, farmer_auth)
    if not animals:
        pytest.skip("No animals found for farmer — seed data may be missing")

    animal_id = animals[0]["id"]
    start = time.time()
    resp = api.get(f"/v1/insurance/premium-estimate/{animal_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] premium estimate: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    for field in ["animal_id", "species", "breed", "estimated_premium",
                  "coverage_amount", "provider", "notes"]:
        assert field in body, f"Missing '{field}' in premium estimate: {body}"

    assert float(body["estimated_premium"]) > 0, "Expected positive premium estimate"
    assert float(body["coverage_amount"]) > 0, "Expected positive coverage amount"


def test_insurance_premium_estimate_note_contains_subsidy_info(api, farmer_auth):
    """Premium estimate notes mention government subsidy."""
    animals = _get_my_animals(api, farmer_auth)
    if not animals:
        pytest.skip("No animals found for farmer")

    animal_id = animals[0]["id"]
    resp = api.get(f"/v1/insurance/premium-estimate/{animal_id}", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # The router always includes subsidy info in notes
    notes = body.get("notes", "")
    assert "subsidy" in notes.lower() or "%" in notes, (
        f"Expected subsidy mention in notes: {notes}"
    )


# ===========================================================================
# Negative tests
# ===========================================================================


def test_insurance_policies_requires_auth(api, farmer_auth):
    """GET /v1/insurance/policies/{user_id} returns 401/403 without auth."""
    user_id = _get_my_user_id(api, farmer_auth)
    resp = api.get(f"/v1/insurance/policies/{user_id}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_insurance_policies_farmer_cannot_see_other_user(api, farmer_auth, farmer2_auth):
    """Farmer cannot retrieve policies for a different user."""
    other_user_id = _get_my_user_id(api, farmer2_auth)
    resp = api.get(f"/v1/insurance/policies/{other_user_id}", headers=farmer_auth)
    assert resp.status_code == 403, (
        f"Expected 403 when farmer accesses other user policies, got {resp.status_code}: {resp.text}"
    )


def test_insurance_policies_invalid_uuid(api, farmer_auth):
    """GET /v1/insurance/policies/not-a-uuid returns 422."""
    resp = api.get("/v1/insurance/policies/not-a-uuid", headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for invalid UUID, got {resp.status_code}: {resp.text}"
    )


def test_insurance_claims_unknown_policy_returns_404(api, farmer_auth):
    """POST /v1/insurance/claims with nonexistent policy_id returns 404."""
    resp = api.post(
        "/v1/insurance/claims",
        json={
            "policy_id": str(uuid4()),
            "claim_type": "death",
            "description": "Animal died due to disease",
        },
        headers=farmer_auth,
    )
    assert resp.status_code == 404, (
        f"Expected 404 for unknown policy, got {resp.status_code}: {resp.text}"
    )


def test_insurance_premium_estimate_unknown_animal(api, farmer_auth):
    """GET /v1/insurance/premium-estimate/{unknown_id} returns 404."""
    resp = api.get(
        f"/v1/insurance/premium-estimate/{uuid4()}",
        headers=farmer_auth,
    )
    assert resp.status_code == 404, (
        f"Expected 404 for unknown animal, got {resp.status_code}: {resp.text}"
    )


def test_insurance_premium_estimate_other_farmer_animal(api, farmer_auth, farmer2_auth):
    """Farmer cannot get premium estimate for another farmer's animal."""
    # Get an animal from farmer2
    farmer2_animals = _get_my_animals(api, farmer2_auth)
    if not farmer2_animals:
        pytest.skip("No animals found for farmer2 — seed data may be missing")

    animal_id = farmer2_animals[0]["id"]
    resp = api.get(
        f"/v1/insurance/premium-estimate/{animal_id}", headers=farmer_auth
    )
    assert resp.status_code == 403, (
        f"Expected 403 when farmer accesses other farmer's animal, got {resp.status_code}: {resp.text}"
    )
