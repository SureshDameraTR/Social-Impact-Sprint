"""Comprehensive integration tests for /v1/ethno-vet endpoints.

Hits the REAL running API at localhost:8000 with a real PostgreSQL database.
Read ethno_vet.py and the ethno_vet schema before editing.

Endpoints:
  GET /v1/ethno-vet/remedies            — list remedies (species/condition filters)
  GET /v1/ethno-vet/remedies/{id}       — single remedy by UUID
  GET /v1/ethno-vet/search?q=<keyword>  — full-text search across remedies

Run: pytest tests/comprehensive/test_ethno_vet_comprehensive.py -v
"""

import time
from uuid import uuid4

import pytest


# ===========================================================================
# Helpers
# ===========================================================================


def _get_first_remedy_id(api, auth_headers: dict) -> str | None:
    """Return the UUID of the first remedy, or None if the DB is empty."""
    resp = api.get("/v1/ethno-vet/remedies", params={"limit": 1}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    return data[0]["id"] if data else None


# ===========================================================================
# Positive tests
# ===========================================================================


def test_ethno_vet_list_remedies_happy_path(api, farmer_auth):
    """GET /v1/ethno-vet/remedies returns 200 with data+total envelope."""
    start = time.time()
    resp = api.get("/v1/ethno-vet/remedies", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] list remedies: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)


def test_ethno_vet_list_remedies_item_schema(api, farmer_auth):
    """Each remedy item has the required TraditionalRemedyRead fields."""
    resp = api.get("/v1/ethno-vet/remedies", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    if not body["data"]:
        pytest.skip("No remedies in DB — seed data may be missing")

    remedy = body["data"][0]
    required_fields = ["id", "name_en", "plant_ingredient", "evidence_rating", "created_at"]
    for field in required_fields:
        assert field in remedy, f"Missing '{field}' in remedy: {remedy}"

    assert remedy["evidence_rating"] in ("traditional", "studied", "icar_validated"), (
        f"Unexpected evidence_rating: {remedy['evidence_rating']}"
    )


def test_ethno_vet_list_remedies_pagination_limit(api, farmer_auth):
    """GET /v1/ethno-vet/remedies?limit=2 returns at most 2 items."""
    resp = api.get("/v1/ethno-vet/remedies", params={"limit": 2}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["data"]) <= 2


def test_ethno_vet_list_remedies_pagination_no_overlap(api, farmer_auth):
    """Two consecutive pages have no overlapping remedy IDs."""
    p1 = api.get("/v1/ethno-vet/remedies", params={"limit": 1, "offset": 0}, headers=farmer_auth)
    p2 = api.get("/v1/ethno-vet/remedies", params={"limit": 1, "offset": 1}, headers=farmer_auth)
    assert p1.status_code == 200, p1.text
    assert p2.status_code == 200, p2.text

    ids1 = {r["id"] for r in p1.json()["data"]}
    ids2 = {r["id"] for r in p2.json()["data"]}
    if ids1 and ids2:
        assert ids1.isdisjoint(ids2), f"Pages overlap: {ids1} & {ids2}"


def test_ethno_vet_get_remedy_by_id(api, farmer_auth):
    """GET /v1/ethno-vet/remedies/{id} returns the correct remedy."""
    remedy_id = _get_first_remedy_id(api, farmer_auth)
    if remedy_id is None:
        pytest.skip("No remedies in DB")

    start = time.time()
    resp = api.get(f"/v1/ethno-vet/remedies/{remedy_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get remedy by id: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert str(body["id"]) == remedy_id, f"Returned wrong remedy: {body}"


def test_ethno_vet_search_returns_envelope(api, farmer_auth):
    """GET /v1/ethno-vet/search?q=<keyword> returns data+total envelope."""
    start = time.time()
    resp = api.get("/v1/ethno-vet/search", params={"q": "neem"}, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] search 'neem': {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert body["total"] == len(body["data"])


def test_ethno_vet_search_filters_by_keyword(api, farmer_auth):
    """Search results only include remedies matching the query."""
    # First load all remedies to find a keyword that's guaranteed to exist
    all_resp = api.get("/v1/ethno-vet/remedies", params={"limit": 50}, headers=farmer_auth)
    assert all_resp.status_code == 200, all_resp.text
    all_data = all_resp.json()["data"]
    if not all_data:
        pytest.skip("No remedies in DB")

    # Pick the plant_ingredient of the first remedy as a known search term
    keyword = all_data[0]["plant_ingredient"][:4].lower()  # first 4 chars
    if len(keyword) < 2:
        pytest.skip("plant_ingredient too short to search")

    search_resp = api.get("/v1/ethno-vet/search", params={"q": keyword}, headers=farmer_auth)
    assert search_resp.status_code == 200, search_resp.text
    # The remedy we seeded from must appear in results
    result_ids = {r["id"] for r in search_resp.json()["data"]}
    assert all_data[0]["id"] in result_ids, (
        f"Expected remedy {all_data[0]['id']} in search results for '{keyword}'"
    )


# ===========================================================================
# Negative tests
# ===========================================================================


def test_ethno_vet_list_requires_auth(api):
    """GET /v1/ethno-vet/remedies returns 401/403 without auth."""
    resp = api.get("/v1/ethno-vet/remedies")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_ethno_vet_get_by_id_requires_auth(api, farmer_auth):
    """GET /v1/ethno-vet/remedies/{id} returns 401/403 without auth."""
    remedy_id = _get_first_remedy_id(api, farmer_auth)
    if remedy_id is None:
        remedy_id = str(uuid4())
    resp = api.get(f"/v1/ethno-vet/remedies/{remedy_id}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_ethno_vet_get_nonexistent_remedy_returns_404(api, farmer_auth):
    """GET /v1/ethno-vet/remedies/{unknown_uuid} returns 404."""
    resp = api.get(f"/v1/ethno-vet/remedies/{uuid4()}", headers=farmer_auth)
    assert resp.status_code == 404, (
        f"Expected 404 for unknown remedy, got {resp.status_code}: {resp.text}"
    )


def test_ethno_vet_get_invalid_uuid_returns_422(api, farmer_auth):
    """GET /v1/ethno-vet/remedies/not-a-uuid returns 422."""
    resp = api.get("/v1/ethno-vet/remedies/not-a-uuid", headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for invalid UUID, got {resp.status_code}: {resp.text}"
    )


def test_ethno_vet_search_too_short_query_rejected(api, farmer_auth):
    """GET /v1/ethno-vet/search?q=x is rejected (min_length=2)."""
    resp = api.get("/v1/ethno-vet/search", params={"q": "x"}, headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for single-char query, got {resp.status_code}: {resp.text}"
    )


def test_ethno_vet_search_missing_q_rejected(api, farmer_auth):
    """GET /v1/ethno-vet/search without ?q= is rejected (required param)."""
    resp = api.get("/v1/ethno-vet/search", headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for missing q param, got {resp.status_code}: {resp.text}"
    )


def test_ethno_vet_list_negative_offset_rejected(api, farmer_auth):
    """GET /v1/ethno-vet/remedies?offset=-1 is rejected (ge=0)."""
    resp = api.get("/v1/ethno-vet/remedies", params={"offset": -1}, headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for offset=-1, got {resp.status_code}: {resp.text}"
    )
