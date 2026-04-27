"""Comprehensive integration tests for /v1/feed endpoints.

Hits the REAL running API at localhost:8000 with a real PostgreSQL database.
Read feed.py and the feed schema before editing.

Endpoints:
  GET  /v1/feed/ingredients            — list all feed ingredients
  POST /v1/feed/calculate-ration       — calculate balanced daily ration

Run: pytest tests/comprehensive/test_feed_comprehensive.py -v
"""

import time
from decimal import Decimal

import pytest


# ===========================================================================
# Positive tests
# ===========================================================================


def test_feed_ingredients_happy_path(api, farmer_auth):
    """GET /v1/feed/ingredients returns 200 with data+total envelope."""
    start = time.time()
    resp = api.get("/v1/feed/ingredients", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] list ingredients: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)


def test_feed_ingredients_item_schema(api, farmer_auth):
    """Each ingredient has the required FeedIngredientRead fields."""
    resp = api.get("/v1/feed/ingredients", headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    if not body["data"]:
        pytest.skip("No feed ingredients in DB — seed data may be missing")

    ingredient = body["data"][0]
    required_fields = [
        "id", "name_en", "category", "protein_pct",
        "energy_kcal", "cost_per_kg", "locally_available",
    ]
    for field in required_fields:
        assert field in ingredient, f"Missing '{field}' in ingredient: {ingredient}"

    assert ingredient["category"] in ("roughage", "concentrate", "supplement", "mineral"), (
        f"Unexpected category: {ingredient['category']}"
    )
    assert isinstance(ingredient["locally_available"], bool)


def test_feed_ingredients_pagination_limit(api, farmer_auth):
    """GET /v1/feed/ingredients?limit=2 returns at most 2 items."""
    resp = api.get("/v1/feed/ingredients", params={"limit": 2}, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["data"]) <= 2, f"Expected at most 2 items, got {len(body['data'])}"


def test_feed_ingredients_pagination_offset(api, farmer_auth):
    """Second page (offset=1, limit=1) differs from first page (offset=0, limit=1)."""
    page1 = api.get(
        "/v1/feed/ingredients", params={"limit": 1, "offset": 0}, headers=farmer_auth
    )
    page2 = api.get(
        "/v1/feed/ingredients", params={"limit": 1, "offset": 1}, headers=farmer_auth
    )
    assert page1.status_code == 200, page1.text
    assert page2.status_code == 200, page2.text

    data1 = page1.json()["data"]
    data2 = page2.json()["data"]

    if data1 and data2:
        ids1 = {item["id"] for item in data1}
        ids2 = {item["id"] for item in data2}
        assert ids1.isdisjoint(ids2), f"Pages overlap: {ids1} and {ids2}"


def test_feed_calculate_ration_cattle(api, farmer_auth):
    """POST /v1/feed/calculate-ration for cattle returns RationResult schema."""
    payload = {
        "species": "cattle",
        "weight_kg": "400.00",
        "lactation_stage": "mid",
    }
    start = time.time()
    resp = api.post("/v1/feed/calculate-ration", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] calculate ration cattle: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "ingredients" in body, f"Missing 'ingredients': {body}"
    assert "total_cost_per_day" in body, f"Missing 'total_cost_per_day': {body}"
    assert "protein_balance" in body, f"Missing 'protein_balance': {body}"
    assert "energy_balance" in body, f"Missing 'energy_balance': {body}"
    assert isinstance(body["ingredients"], list)


def test_feed_calculate_ration_buffalo(api, farmer_auth):
    """POST /v1/feed/calculate-ration for buffalo returns valid result."""
    payload = {
        "species": "buffalo",
        "weight_kg": "500.00",
        "lactation_stage": "early",
    }
    resp = api.post("/v1/feed/calculate-ration", json=payload, headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "ingredients" in body
    assert float(body["total_cost_per_day"]) >= 0


def test_feed_calculate_ration_goat(api, farmer_auth):
    """POST /v1/feed/calculate-ration for goat (lighter weight) returns valid result."""
    payload = {
        "species": "goat",
        "weight_kg": "35.00",
    }
    resp = api.post("/v1/feed/calculate-ration", json=payload, headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "ingredients" in body


def test_feed_calculate_ration_dry_cow(api, farmer_auth):
    """POST /v1/feed/calculate-ration with lactation_stage=dry works."""
    payload = {
        "species": "cattle",
        "weight_kg": "350.00",
        "lactation_stage": "dry",
    }
    resp = api.post("/v1/feed/calculate-ration", json=payload, headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


# ===========================================================================
# Negative tests
# ===========================================================================


def test_feed_ingredients_requires_auth(api):
    """GET /v1/feed/ingredients returns 401/403 without auth."""
    resp = api.get("/v1/feed/ingredients")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_feed_calculate_ration_requires_auth(api):
    """POST /v1/feed/calculate-ration returns 401/403 without auth."""
    resp = api.post("/v1/feed/calculate-ration", json={"species": "cattle", "weight_kg": "400"})
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


def test_feed_calculate_ration_missing_species(api, farmer_auth):
    """POST /v1/feed/calculate-ration without 'species' returns 422."""
    resp = api.post(
        "/v1/feed/calculate-ration",
        json={"weight_kg": "400.00"},
        headers=farmer_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for missing species, got {resp.status_code}: {resp.text}"
    )


def test_feed_calculate_ration_zero_weight(api, farmer_auth):
    """POST /v1/feed/calculate-ration with weight_kg=0 is rejected (gt=0)."""
    resp = api.post(
        "/v1/feed/calculate-ration",
        json={"species": "cattle", "weight_kg": "0"},
        headers=farmer_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for weight_kg=0, got {resp.status_code}: {resp.text}"
    )


def test_feed_calculate_ration_invalid_lactation_stage(api, farmer_auth):
    """POST /v1/feed/calculate-ration with unknown lactation_stage returns 422."""
    resp = api.post(
        "/v1/feed/calculate-ration",
        json={"species": "cattle", "weight_kg": "400", "lactation_stage": "super_late"},
        headers=farmer_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for invalid lactation_stage, got {resp.status_code}: {resp.text}"
    )


def test_feed_ingredients_negative_offset_rejected(api, farmer_auth):
    """GET /v1/feed/ingredients?offset=-1 is rejected (min=0)."""
    resp = api.get("/v1/feed/ingredients", params={"offset": -1}, headers=farmer_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for offset=-1, got {resp.status_code}: {resp.text}"
    )
