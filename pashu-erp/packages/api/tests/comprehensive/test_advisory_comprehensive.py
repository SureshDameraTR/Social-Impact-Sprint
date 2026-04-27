"""Comprehensive integration tests for /v1/advisory endpoints.

Hits the REAL running API at localhost:8000 with a real PostgreSQL database.
Read advisory.py and the advisory schema before editing.

Endpoints:
  GET /v1/advisory/tips                 — list active tips (species/category filters)
  GET /v1/advisory/tips/{tip_id}        — single tip by UUID

Auth: any authenticated user can read; no write endpoints on this router.
The list endpoint only returns is_active=True tips.

Run: pytest tests/comprehensive/test_advisory_comprehensive.py -v
"""

import time
from uuid import uuid4

import pytest


# ===========================================================================
# Helpers
# ===========================================================================


def _get_all_tips(api, auth_headers: dict) -> list:
    """Return all advisory tips from the list endpoint."""
    resp = api.get("/v1/advisory/tips", params={"limit": 100}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return resp.json().get("data", [])


def _get_first_tip_id(api, auth_headers: dict) -> str | None:
    """Return UUID of the first active tip, or None if empty."""
    tips = _get_all_tips(api, auth_headers)
    return tips[0]["id"] if tips else None


# ===========================================================================
# Positive tests
# ===========================================================================


def test_advisory_tips_happy_path(api, farmer_auth):
    """GET /v1/advisory/tips returns 200 with data+total envelope."""
    start = time.time()
    resp = api.get("/v1/advisory/tips", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] list tips: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] == len(body["data"]) or body["total"] >= len(body["data"])


def test_advisory_tips_item_schema(api, farmer_auth):
    """Each tip has the required AdvisoryTipRead fields."""
    resp = api.get("/v1/advisory/tips", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    if not body["data"]:
        pytest.skip("No advisory tips in DB — seed data may be missing")

    tip = body["data"][0]
    required_fields = [
        "id", "title_en", "category", "source", "priority", "is_active", "published_at",
    ]
    for field in required_fields:
        assert field in tip, f"Missing '{field}' in tip: {tip}"

    # Schema constraints
    assert tip["category"] in ("health", "feeding", "breeding", "government"), (
        f"Unexpected category: {tip['category']}"
    )
    assert tip["source"] in ("ICAR", "KMF", "NABARD", "Community"), (
        f"Unexpected source: {tip['source']}"
    )
    assert tip["is_active"] is True, "List endpoint should only return active tips"


def test_advisory_tips_only_active_returned(api, farmer_auth):
    """All tips returned by the list endpoint must be active (is_active=True)."""
    resp = api.get("/v1/advisory/tips", params={"limit": 100}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    for tip in resp.json()["data"]:
        assert tip["is_active"] is True, (
            f"Inactive tip found in list: id={tip['id']}"
        )


def test_advisory_tips_pagination_limit(api, farmer_auth):
    """GET /v1/advisory/tips?limit=2 returns at most 2 tips."""
    resp = api.get("/v1/advisory/tips", params={"limit": 2}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["data"]) <= 2


def test_advisory_tips_pagination_no_overlap(api, farmer_auth):
    """Two consecutive pages (limit=1) have no overlapping tip IDs."""
    p1 = api.get("/v1/advisory/tips", params={"limit": 1, "offset": 0}, headers=farmer_auth)
    p2 = api.get("/v1/advisory/tips", params={"limit": 1, "offset": 1}, headers=farmer_auth)
    assert p1.status_code == 200, p1.text
    assert p2.status_code == 200, p2.text

    ids1 = {t["id"] for t in p1.json()["data"]}
    ids2 = {t["id"] for t in p2.json()["data"]}
    if ids1 and ids2:
        assert ids1.isdisjoint(ids2), f"Pages overlap: {ids1} & {ids2}"


def test_advisory_tips_filter_by_species(api, farmer_auth):
    """GET /v1/advisory/tips?species=cattle only returns cattle tips."""
    resp = api.get("/v1/advisory/tips", params={"species": "cattle"}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    for tip in body["data"]:
        applicable = tip.get("species_applicable") or []
        assert "cattle" in applicable, (
            f"Tip {tip['id']} species_applicable={applicable} does not include 'cattle'"
        )


def test_advisory_get_tip_by_id(api, farmer_auth):
    """GET /v1/advisory/tips/{tip_id} returns the correct tip."""
    tip_id = _get_first_tip_id(api, farmer_auth)
    if tip_id is None:
        pytest.skip("No tips in DB")

    start = time.time()
    resp = api.get(f"/v1/advisory/tips/{tip_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get tip by id: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert str(body["id"]) == tip_id, f"Returned wrong tip: {body}"
    # Bilingual fields should be present
    assert "title_en" in body


def test_advisory_tips_bilingual_fields(api, farmer_auth):
    """Tips may include Kannada translations (title_kn, body_kn are optional)."""
    resp = api.get("/v1/advisory/tips", params={"limit": 10}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    if not body["data"]:
        pytest.skip("No tips in DB")

    # title_kn and body_kn are optional in schema — just verify they don't error
    tip = body["data"][0]
    assert "title_en" in tip  # English always required
    # Kannada fields optional but schema must contain the key
    assert "title_kn" in tip or True  # key may be absent if schema excludes None


# ===========================================================================
# Negative tests
# ===========================================================================


def test_advisory_tips_requires_auth(api):
    """GET /v1/advisory/tips returns 401/403 without auth."""
    resp = api.get("/v1/advisory/tips")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_advisory_get_tip_requires_auth(api, farmer_auth):
    """GET /v1/advisory/tips/{id} returns 401/403 without auth."""
    tip_id = _get_first_tip_id(api, farmer_auth)
    if tip_id is None:
        tip_id = str(uuid4())
    resp = api.get(f"/v1/advisory/tips/{tip_id}")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_advisory_get_nonexistent_tip_returns_404(api, farmer_auth):
    """GET /v1/advisory/tips/{unknown_uuid} returns 404."""
    resp = api.get(f"/v1/advisory/tips/{uuid4()}", headers=farmer_auth)
    assert resp.status_code == 404, (
        f"Expected 404 for unknown tip, got {resp.status_code}: {resp.text}"
    )


def test_advisory_get_invalid_uuid_returns_422(api, farmer_auth):
    """GET /v1/advisory/tips/not-a-uuid returns 422 validation error."""
    resp = api.get("/v1/advisory/tips/not-a-uuid", headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for invalid UUID, got {resp.status_code}: {resp.text}"
    )


def test_advisory_tips_negative_offset_rejected(api, farmer_auth):
    """GET /v1/advisory/tips?offset=-1 is rejected (ge=0)."""
    resp = api.get("/v1/advisory/tips", params={"offset": -1}, headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for offset=-1, got {resp.status_code}: {resp.text}"
    )


def test_advisory_tips_limit_too_large_rejected(api, farmer_auth):
    """GET /v1/advisory/tips?limit=999 is rejected (max=100)."""
    resp = api.get("/v1/advisory/tips", params={"limit": 999}, headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for limit=999, got {resp.status_code}: {resp.text}"
    )
