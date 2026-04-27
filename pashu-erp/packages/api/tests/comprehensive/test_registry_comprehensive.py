"""Comprehensive integration tests for /v1/registry (Bharat Pashudhan) endpoints.

Hits the REAL running API at localhost:8000, which proxies to the mock registry
backend at localhost:8001. Read bharat_pashudhan.py and the bharat_pashudhan schema.

Pashu Aadhaar format: starts with "IN", 12 chars total (e.g., "INKA00000001").
The mock validates this format; invalid formats return HTTP 400 from the registry,
which the API router re-raises as an HTTPException.

Run: pytest tests/comprehensive/test_registry_comprehensive.py -v
"""

import time
from uuid import uuid4

import pytest


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Valid Pashu Aadhaar IDs — "IN" + 10 uppercase alphanumeric chars
VALID_PASHU_ID_1 = "INKA00000001"
VALID_PASHU_ID_2 = "INKB12345678"
VALID_PASHU_ID_3 = "IN2900001234"


# ===========================================================================
# Positive tests
# ===========================================================================


def test_registry_lookup_happy_path(api, farmer_auth):
    """GET /v1/registry/lookup/{id} returns 200 with RegistryAnimalLookup schema."""
    start = time.time()
    resp = api.get(f"/v1/registry/lookup/{VALID_PASHU_ID_1}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] registry lookup: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    # RegistryAnimalLookup required fields
    assert "pashu_aadhaar_id" in body, f"Missing 'pashu_aadhaar_id': {body}"
    assert "species" in body, f"Missing 'species': {body}"
    assert "breed" in body, f"Missing 'breed': {body}"
    assert "sex" in body, f"Missing 'sex': {body}"
    assert body["pashu_aadhaar_id"] == VALID_PASHU_ID_1


def test_registry_lookup_owner_nested(api, farmer_auth):
    """Lookup response contains a nested owner object with expected fields."""
    resp = api.get(f"/v1/registry/lookup/{VALID_PASHU_ID_1}", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    owner = body.get("owner")
    assert owner is not None, f"Expected 'owner' in response: {body}"
    assert "name" in owner, f"Missing 'name' in owner: {owner}"
    # Owner should have location fields
    assert "district" in owner, f"Missing 'district' in owner: {owner}"
    assert "state" in owner, f"Missing 'state' in owner: {owner}"


def test_registry_lookup_vaccinations_list(api, farmer_auth):
    """Lookup response contains a vaccinations list."""
    resp = api.get(f"/v1/registry/lookup/{VALID_PASHU_ID_2}", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert "vaccinations" in body, f"Missing 'vaccinations': {body}"
    assert isinstance(body["vaccinations"], list)
    if body["vaccinations"]:
        vacc = body["vaccinations"][0]
        assert "type" in vacc, f"Missing 'type' in vaccination: {vacc}"
        assert "date" in vacc, f"Missing 'date' in vaccination: {vacc}"


def test_registry_lookup_deterministic(api, farmer_auth):
    """Same Pashu Aadhaar ID returns the same data on two consecutive calls."""
    resp1 = api.get(f"/v1/registry/lookup/{VALID_PASHU_ID_3}", headers=farmer_auth)
    resp2 = api.get(f"/v1/registry/lookup/{VALID_PASHU_ID_3}", headers=farmer_auth)
    assert resp1.status_code == 200, resp1.text
    assert resp2.status_code == 200, resp2.text

    body1 = resp1.json()
    body2 = resp2.json()
    # Core fields must be identical (deterministic seed)
    assert body1["species"] == body2["species"], "species changed between calls"
    assert body1["breed"] == body2["breed"], "breed changed between calls"
    assert body1["sex"] == body2["sex"], "sex changed between calls"


def test_registry_sync_happy_path(api, farmer_auth):
    """POST /v1/registry/sync/{animal_id} returns 200 with RegistrySyncResponse."""
    animal_id = str(uuid4())
    start = time.time()
    resp = api.post(f"/v1/registry/sync/{animal_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] registry sync: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "status" in body, f"Missing 'status': {body}"
    assert "animal_id" in body, f"Missing 'animal_id': {body}"
    assert "last_sync" in body, f"Missing 'last_sync': {body}"
    assert body["status"] == "synced", f"Expected status='synced', got: {body['status']}"
    assert body["animal_id"] == animal_id


def test_registry_sync_returns_version(api, farmer_auth):
    """POST /v1/registry/sync/{animal_id} response includes registry_version."""
    animal_id = str(uuid4())
    resp = api.post(f"/v1/registry/sync/{animal_id}", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # registry_version is optional in schema but mock always returns it
    assert "registry_version" in body, f"Missing 'registry_version': {body}"


# ===========================================================================
# Negative tests
# ===========================================================================


def test_registry_lookup_requires_auth(api):
    """GET /v1/registry/lookup/{id} returns 401/403 without auth."""
    resp = api.get(f"/v1/registry/lookup/{VALID_PASHU_ID_1}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_registry_sync_requires_auth(api):
    """POST /v1/registry/sync/{animal_id} returns 401/403 without auth."""
    resp = api.post(f"/v1/registry/sync/{uuid4()}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_registry_lookup_invalid_format_too_short(api, farmer_auth):
    """GET /v1/registry/lookup/IN123 (too short) gets an error from the registry."""
    resp = api.get("/v1/registry/lookup/IN123", headers=farmer_auth)
    # Mock validates format and returns 400, which becomes HTTPException
    # 404 is also acceptable when mock service returns not-found for invalid format
    assert resp.status_code in (400, 404, 422, 502), (
        f"Expected error for short ID, got {resp.status_code}: {resp.text}"
    )


def test_registry_lookup_invalid_format_no_in_prefix(api, farmer_auth):
    """GET /v1/registry/lookup/ABCD00000001 (missing IN prefix) gets rejected."""
    resp = api.get("/v1/registry/lookup/ABCD00000001", headers=farmer_auth)
    # 404 is acceptable when mock service returns not-found for invalid format
    assert resp.status_code in (400, 404, 422, 502), (
        f"Expected error for missing IN prefix, got {resp.status_code}: {resp.text}"
    )


def test_registry_sync_invalid_uuid(api, farmer_auth):
    """POST /v1/registry/sync/not-a-uuid returns 422 validation error."""
    resp = api.post("/v1/registry/sync/not-a-uuid", headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for non-UUID animal_id, got {resp.status_code}: {resp.text}"
    )
