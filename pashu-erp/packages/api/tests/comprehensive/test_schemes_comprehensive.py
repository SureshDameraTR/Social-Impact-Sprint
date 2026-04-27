"""Comprehensive integration tests for /v1/schemes endpoints.

Tests:
  - GET list — pagination, envelope, ministry filter
  - GET by id
  - POST create (admin only)
  - Auth enforcement
  - Error cases: missing fields, fake UUIDs, wrong role for POST

Run: pytest tests/comprehensive/test_schemes_comprehensive.py -v
"""

import time
import uuid

import pytest

FAKE_UUID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_code() -> str:
    """Generate a unique scheme_code to avoid DB conflicts on repeated runs."""
    return f"TEST-{uuid.uuid4().hex[:8].upper()}"


def _create_scheme(api, admin_auth, name="Test Scheme") -> dict:
    """Create a minimal government scheme as admin."""
    resp = api.post(
        "/v1/schemes",
        json={
            "scheme_code": _unique_code(),
            "name": name,
            "ministry": "Ministry of Agriculture",
            "description": "Test scheme for integration testing",
            "eligibility_criteria": "All farmers owning livestock",
            "required_documents": ["Aadhaar", "Land Records"],
            "max_subsidy_amount": "50000.00",
            "subsidy_percentage": "50.00",
            "is_active": True,
            "valid_from": "2024-01-01",
        },
        headers=admin_auth,
    )
    return resp


# ---------------------------------------------------------------------------
# Test 1: GET /v1/schemes requires auth
# ---------------------------------------------------------------------------


def test_list_schemes_requires_auth(api):
    """GET /v1/schemes without auth returns 401."""
    start = time.time()
    resp = api.get("/v1/schemes")
    duration = time.time() - start
    print(f"\n[timing] GET /v1/schemes no auth: {duration:.3f}s")

    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 2: GET /v1/schemes returns data/total envelope
# ---------------------------------------------------------------------------


def test_list_schemes_envelope_structure(api, farmer_auth):
    """GET /v1/schemes returns proper data/total envelope."""
    start = time.time()
    resp = api.get("/v1/schemes", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/schemes farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 0


# ---------------------------------------------------------------------------
# Test 3: GET /v1/schemes item schema
# ---------------------------------------------------------------------------


def test_list_schemes_item_schema(api, farmer_auth):
    """Each scheme item has required fields."""
    resp = api.get("/v1/schemes", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    if body["data"]:
        scheme = body["data"][0]
        assert "id" in scheme, f"Missing 'id': {scheme}"
        assert "scheme_code" in scheme, f"Missing 'scheme_code': {scheme}"
        assert "name" in scheme, f"Missing 'name': {scheme}"
        assert "is_active" in scheme, f"Missing 'is_active': {scheme}"
        assert "valid_from" in scheme, f"Missing 'valid_from': {scheme}"
        assert "created_at" in scheme, f"Missing 'created_at': {scheme}"
        assert isinstance(scheme["is_active"], bool)


# ---------------------------------------------------------------------------
# Test 4: GET /v1/schemes pagination — no overlap
# ---------------------------------------------------------------------------


def test_list_schemes_pagination_no_overlap(api, farmer_auth):
    """Paginated scheme results have no overlapping IDs across pages."""
    resp1 = api.get("/v1/schemes?offset=0&limit=5", headers=farmer_auth)
    resp2 = api.get("/v1/schemes?offset=5&limit=5", headers=farmer_auth)

    assert resp1.status_code == 200, f"Page 1 failed: {resp1.text}"
    assert resp2.status_code == 200, f"Page 2 failed: {resp2.text}"

    ids1 = {str(s["id"]) for s in resp1.json()["data"]}
    ids2 = {str(s["id"]) for s in resp2.json()["data"]}
    assert ids1.isdisjoint(ids2), f"Overlapping IDs: {ids1 & ids2}"


# ---------------------------------------------------------------------------
# Test 5: GET /v1/schemes?ministry=... filter works
# ---------------------------------------------------------------------------


def test_list_schemes_ministry_filter(api, farmer_auth, admin_auth):
    """GET /v1/schemes?ministry=Agriculture returns only matching schemes."""
    # Ensure at least one scheme with this ministry exists
    _create_scheme(api, admin_auth, name="Ministry Filter Test Scheme")

    resp = api.get("/v1/schemes?ministry=Agriculture", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    body = resp.json()

    # All returned schemes must contain "Agriculture" in their ministry field
    for scheme in body["data"]:
        ministry = scheme.get("ministry", "") or ""
        assert "Agriculture" in ministry or "agriculture" in ministry.lower(), (
            f"Ministry filter mismatch: scheme ministry='{ministry}'"
        )


# ---------------------------------------------------------------------------
# Test 6: POST /v1/schemes — farmer gets 403
# ---------------------------------------------------------------------------


def test_create_scheme_farmer_forbidden(api, farmer_auth):
    """POST /v1/schemes returns 403 for farmer role."""
    start = time.time()
    resp = api.post(
        "/v1/schemes",
        json={
            "scheme_code": _unique_code(),
            "name": "Farmer Attempt Scheme",
            "is_active": True,
            "valid_from": "2024-01-01",
        },
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/schemes farmer: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 for farmer creating scheme, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: POST /v1/schemes — admin can create
# ---------------------------------------------------------------------------


def test_create_scheme_admin_success(api, admin_auth):
    """POST /v1/schemes creates a scheme and returns GovtSchemeRead schema."""
    start = time.time()
    resp = _create_scheme(api, admin_auth, name="PM Livestock Insurance Scheme")
    duration = time.time() - start
    print(f"\n[timing] POST /v1/schemes admin: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "id" in body, f"Missing 'id': {body}"
    assert "scheme_code" in body, f"Missing 'scheme_code': {body}"
    assert "name" in body, f"Missing 'name': {body}"
    assert "is_active" in body, f"Missing 'is_active': {body}"
    assert "created_at" in body, f"Missing 'created_at': {body}"
    assert body["name"] == "PM Livestock Insurance Scheme"
    assert body["is_active"] is True


# ---------------------------------------------------------------------------
# Test 8: POST /v1/schemes missing required fields → 422
# ---------------------------------------------------------------------------


def test_create_scheme_missing_fields(api, admin_auth):
    """POST /v1/schemes with empty body returns 422."""
    start = time.time()
    resp = api.post("/v1/schemes", json={}, headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] POST /v1/schemes missing fields: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: GET /v1/schemes/{scheme_id} returns scheme detail
# ---------------------------------------------------------------------------


def test_get_scheme_by_id(api, farmer_auth, admin_auth):
    """GET /v1/schemes/{id} returns the correct scheme."""
    create_resp = _create_scheme(api, admin_auth, name="Get By ID Test Scheme")
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    scheme_id = create_resp.json()["id"]

    start = time.time()
    resp = api.get(f"/v1/schemes/{scheme_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/schemes/{scheme_id}: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert str(body["id"]) == scheme_id, f"ID mismatch: {body['id']} != {scheme_id}"
    assert body["name"] == "Get By ID Test Scheme"


# ---------------------------------------------------------------------------
# Test 10: GET /v1/schemes/{fake_uuid} returns 404
# ---------------------------------------------------------------------------


def test_get_scheme_nonexistent_returns_404(api, farmer_auth):
    """GET /v1/schemes/<fake_uuid> returns 404."""
    start = time.time()
    resp = api.get(f"/v1/schemes/{FAKE_UUID}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/schemes fake uuid: {duration:.3f}s")

    assert resp.status_code == 404, (
        f"Expected 404, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/schemes/{bad_uuid} → 422
# ---------------------------------------------------------------------------


def test_get_scheme_invalid_uuid_format(api, farmer_auth):
    """GET /v1/schemes/not-a-uuid returns 422 validation error."""
    start = time.time()
    resp = api.get("/v1/schemes/not-a-uuid", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/schemes bad uuid format: {duration:.3f}s")

    assert resp.status_code == 422, (
        f"Expected 422, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 12: Create → Read — fields persist correctly
# ---------------------------------------------------------------------------


def test_create_then_read_scheme_consistency(api, admin_auth, farmer_auth):
    """Creating a scheme and reading it back returns consistent field values."""
    code = _unique_code()
    create_resp = api.post(
        "/v1/schemes",
        json={
            "scheme_code": code,
            "name": "Mukhyamantri Pashu Bima Yojana",
            "ministry": "Ministry of Animal Husbandry",
            "description": "Livestock insurance for BPL farmers",
            "eligibility_criteria": "BPL card holders",
            "required_documents": ["BPL Card", "Aadhaar"],
            "max_subsidy_amount": "25000.00",
            "subsidy_percentage": "75.00",
            "is_active": True,
            "valid_from": "2024-04-01",
            "valid_to": "2025-03-31",
        },
        headers=admin_auth,
    )
    assert create_resp.status_code == 201, f"Create failed: {create_resp.text}"
    scheme_id = create_resp.json()["id"]

    read_resp = api.get(f"/v1/schemes/{scheme_id}", headers=farmer_auth)
    assert read_resp.status_code == 200, f"Read failed: {read_resp.text}"
    body = read_resp.json()

    assert body["scheme_code"] == code
    assert body["name"] == "Mukhyamantri Pashu Bima Yojana"
    assert body["ministry"] == "Ministry of Animal Husbandry"
    assert body["is_active"] is True
    # Subsidy percentage stored as decimal
    assert body["subsidy_percentage"] is not None
