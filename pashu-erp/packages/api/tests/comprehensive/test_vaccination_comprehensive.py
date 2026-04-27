"""Comprehensive integration tests for /v1/vaccinations endpoints.

Tests:
  - POST record vaccination (farmer must own animal)
  - GET /due — upcoming vaccinations for current user's animals
  - GET /schedule — all species schedules
  - GET /schedule/{species} — species-specific schedule
  - GET /species-breakdown — admin only
  - GET /village-coverage — admin only
  - GET /{animal_id} — animal vaccinations (owner check)
  - PATCH /{vaccination_id} — mark as administered (owner check)
  - Auth/role enforcement

Run: pytest tests/comprehensive/test_vaccination_comprehensive.py -v
"""

import time

import pytest

FAKE_UUID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# Helper: get the first animal owned by the farmer
# ---------------------------------------------------------------------------


def _get_farmer_animal_id(api, farmer_auth) -> str | None:
    """Return the first animal ID owned by the farmer, or None."""
    resp = api.get("/v1/animals", headers=farmer_auth)
    if resp.status_code != 200:
        return None
    data = resp.json().get("data", [])
    return data[0]["id"] if data else None


# ---------------------------------------------------------------------------
# Test 1: GET /v1/vaccinations/due requires auth
# ---------------------------------------------------------------------------


def test_due_vaccinations_requires_auth(api):
    """GET /v1/vaccinations/due without auth returns 401."""
    start = time.time()
    resp = api.get("/v1/vaccinations/due")
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vaccinations/due no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: GET /v1/vaccinations/due with valid auth
# ---------------------------------------------------------------------------


def test_due_vaccinations_envelope_structure(api, farmer_auth):
    """GET /v1/vaccinations/due returns data/total envelope."""
    start = time.time()
    resp = api.get("/v1/vaccinations/due", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vaccinations/due farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 0


# ---------------------------------------------------------------------------
# Test 3: GET /v1/vaccinations/schedule returns all schedules
# ---------------------------------------------------------------------------


def test_schedule_all_species(api, farmer_auth):
    """GET /v1/vaccinations/schedule returns a schedule list for all species."""
    start = time.time()
    resp = api.get("/v1/vaccinations/schedule", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vaccinations/schedule all: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    # At least one species must have schedule entries
    assert body["total"] > 0, "Expected at least one schedule entry"


# ---------------------------------------------------------------------------
# Test 4: GET /v1/vaccinations/schedule/{species} for cattle
# ---------------------------------------------------------------------------


def test_schedule_cattle_species(api, farmer_auth):
    """GET /v1/vaccinations/schedule/cattle returns cattle-specific schedule."""
    start = time.time()
    resp = api.get("/v1/vaccinations/schedule/cattle", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vaccinations/schedule cattle: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "species" in body, f"Missing 'species': {body}"
    assert "schedule" in body, f"Missing 'schedule': {body}"
    assert isinstance(body["schedule"], list)


# ---------------------------------------------------------------------------
# Test 5: GET /v1/vaccinations/schedule/{species} unknown species returns empty schedule
# ---------------------------------------------------------------------------


def test_schedule_unknown_species_returns_empty(api, farmer_auth):
    """GET /v1/vaccinations/schedule/unicorn returns empty schedule (no 404)."""
    resp = api.get("/v1/vaccinations/schedule/unicorn", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "schedule" in body
    # unknown species → empty schedule with message
    assert body["schedule"] == [] or "message" in body


# ---------------------------------------------------------------------------
# Test 6: GET /v1/vaccinations/species-breakdown requires admin
# ---------------------------------------------------------------------------


def test_species_breakdown_requires_admin(api, farmer_auth):
    """GET /v1/vaccinations/species-breakdown returns 403 for non-admin."""
    start = time.time()
    resp = api.get("/v1/vaccinations/species-breakdown", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET species-breakdown farmer: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for farmer on admin endpoint, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: GET /v1/vaccinations/species-breakdown with admin auth
# ---------------------------------------------------------------------------


def test_species_breakdown_admin_access(api, admin_auth):
    """GET /v1/vaccinations/species-breakdown works for admin."""
    start = time.time()
    resp = api.get("/v1/vaccinations/species-breakdown", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET species-breakdown admin: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "breakdown" in body, f"Missing 'breakdown': {body}"
    assert isinstance(body["breakdown"], list)


# ---------------------------------------------------------------------------
# Test 8: GET /v1/vaccinations/village-coverage requires admin
# ---------------------------------------------------------------------------


def test_village_coverage_requires_admin(api, farmer_auth):
    """GET /v1/vaccinations/village-coverage returns 403 for non-admin."""
    start = time.time()
    resp = api.get("/v1/vaccinations/village-coverage", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET village-coverage farmer: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for farmer, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: GET /v1/vaccinations/village-coverage with admin auth
# ---------------------------------------------------------------------------


def test_village_coverage_admin_envelope(api, admin_auth):
    """GET /v1/vaccinations/village-coverage (admin) returns data/total envelope."""
    start = time.time()
    resp = api.get("/v1/vaccinations/village-coverage", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] GET village-coverage admin: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)


# ---------------------------------------------------------------------------
# Test 10: GET /v1/vaccinations/{animal_id} with fake UUID → 404
# ---------------------------------------------------------------------------


def test_get_vaccinations_nonexistent_animal(api, farmer_auth):
    """GET /v1/vaccinations/<fake_uuid> returns 404."""
    start = time.time()
    resp = api.get(f"/v1/vaccinations/{FAKE_UUID}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vaccinations fake uuid: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/vaccinations/{animal_id} cross-owner returns 403
# ---------------------------------------------------------------------------


def test_get_vaccinations_wrong_owner(api, farmer_auth, farmer2_auth):
    """GET /v1/vaccinations/{animal_id} for another farmer's animal → 403."""
    # Get farmer2's animal
    resp = api.get("/v1/animals", headers=farmer2_auth)
    if resp.status_code != 200 or not resp.json().get("data"):
        pytest.skip("No animals found for farmer2")
    animal_id = resp.json()["data"][0]["id"]

    start = time.time()
    resp = api.get(f"/v1/vaccinations/{animal_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/vaccinations cross-owner: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for cross-owner access, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 12: POST /v1/vaccinations missing required fields → 422
# ---------------------------------------------------------------------------


def test_create_vaccination_missing_fields(api, farmer_auth):
    """POST /v1/vaccinations with missing fields returns 422."""
    start = time.time()
    resp = api.post("/v1/vaccinations", json={}, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] POST /v1/vaccinations missing fields: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )
