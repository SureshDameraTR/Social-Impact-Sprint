"""Comprehensive integration tests for /v1/reference endpoints.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_reference_comprehensive.py -v
"""

import time

import pytest


# ---------------------------------------------------------------------------
# Test 1: GET /v1/reference/market-rates — farmer can read, envelope shape
# ---------------------------------------------------------------------------

def test_market_rates_list_farmer_happy_path(api, farmer_auth):
    """GET /v1/reference/market-rates as farmer returns data+total envelope."""
    start = time.time()
    resp = api.get("/v1/reference/market-rates", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/reference/market-rates: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)


# ---------------------------------------------------------------------------
# Test 2: GET /v1/reference/market-rates — item schema validation
# ---------------------------------------------------------------------------

def test_market_rates_item_schema(api, farmer_auth):
    """Each market rate item has id, product, and numeric price fields."""
    resp = api.get("/v1/reference/market-rates", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    for rate in body["data"]:
        assert "id" in rate, f"Rate missing 'id': {rate}"
        assert "product" in rate, f"Rate missing 'product': {rate}"
        # Prices should be non-negative if present
        for price_field in ("min_price", "max_price", "avg_price"):
            if rate.get(price_field) is not None:
                assert float(rate[price_field]) >= 0, (
                    f"{price_field} should be >= 0: {rate[price_field]}"
                )


# ---------------------------------------------------------------------------
# Test 3: GET /v1/reference/market-rates — 401 without auth
# ---------------------------------------------------------------------------

def test_market_rates_unauthenticated_401(api):
    """GET /v1/reference/market-rates without auth returns 401."""
    resp = api.get("/v1/reference/market-rates")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: GET /v1/reference/market-rates — district filter narrows results
# ---------------------------------------------------------------------------

def test_market_rates_district_filter(api, farmer_auth):
    """GET /v1/reference/market-rates?district=X returns only matching district rows."""
    all_resp = api.get("/v1/reference/market-rates", headers=farmer_auth)
    assert all_resp.status_code == 200
    all_data = all_resp.json()["data"]
    if not all_data:
        pytest.skip("No market rates in seed data")

    # Find a district present in the data
    districts = [r["district"] for r in all_data if r.get("district")]
    if not districts:
        pytest.skip("No market rate rows have a district set")

    target_district = districts[0]
    filtered_resp = api.get(
        f"/v1/reference/market-rates?district={target_district}", headers=farmer_auth
    )
    assert filtered_resp.status_code == 200
    for rate in filtered_resp.json()["data"]:
        assert rate["district"] == target_district, (
            f"Filter returned row with wrong district: {rate}"
        )


# ---------------------------------------------------------------------------
# Test 5: PUT /v1/reference/market-rates/{id} — admin can update
# ---------------------------------------------------------------------------

def test_market_rates_update_admin(api, admin_auth, farmer_auth):
    """PUT /v1/reference/market-rates/{id} as admin updates the record."""
    rates_resp = api.get("/v1/reference/market-rates", headers=admin_auth)
    assert rates_resp.status_code == 200
    rates = rates_resp.json()["data"]
    if not rates:
        pytest.skip("No market rates in seed data")

    rate_id = rates[0]["id"]
    original_label = rates[0].get("label", "original-label")

    new_label = "test-label-updated"
    resp = api.put(
        f"/v1/reference/market-rates/{rate_id}",
        json={"label": new_label},
        headers=admin_auth,
    )
    assert resp.status_code == 200, f"PUT market-rate failed: {resp.text}"
    body = resp.json()
    assert body["label"] == new_label, f"Label not updated: {body}"
    assert str(body["id"]) == str(rate_id)

    # Restore original label
    api.put(
        f"/v1/reference/market-rates/{rate_id}",
        json={"label": original_label},
        headers=admin_auth,
    )


# ---------------------------------------------------------------------------
# Test 6: PUT /v1/reference/market-rates/{id} — farmer returns 403
# ---------------------------------------------------------------------------

def test_market_rates_update_farmer_403(api, admin_auth, farmer_auth):
    """PUT /v1/reference/market-rates/{id} as farmer returns 403 (admin-only)."""
    rates_resp = api.get("/v1/reference/market-rates", headers=admin_auth)
    assert rates_resp.status_code == 200
    rates = rates_resp.json()["data"]
    if not rates:
        pytest.skip("No market rates in seed data")

    rate_id = rates[0]["id"]
    resp = api.put(
        f"/v1/reference/market-rates/{rate_id}",
        json={"label": "should-fail"},
        headers=farmer_auth,
    )
    assert resp.status_code == 403, (
        f"Expected 403 for farmer on market-rate PUT, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: PUT /v1/reference/market-rates/{id} — 404 for unknown ID
# ---------------------------------------------------------------------------

def test_market_rates_update_404(api, admin_auth):
    """PUT /v1/reference/market-rates/{fake_id} returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = api.put(
        f"/v1/reference/market-rates/{fake_id}",
        json={"label": "ghost"},
        headers=admin_auth,
    )
    assert resp.status_code == 404, (
        f"Expected 404 for unknown market rate, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 8: GET /v1/reference/insurance-premiums — any auth can read
# ---------------------------------------------------------------------------

def test_insurance_premiums_list_farmer(api, farmer_auth):
    """GET /v1/reference/insurance-premiums as farmer returns data+total envelope."""
    start = time.time()
    resp = api.get("/v1/reference/insurance-premiums", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/reference/insurance-premiums: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body and "total" in body
    for premium in body["data"]:
        assert "id" in premium, f"Premium missing 'id': {premium}"
        assert "species" in premium, f"Premium missing 'species': {premium}"


# ---------------------------------------------------------------------------
# Test 9: PUT /v1/reference/insurance-premiums/{id} — farmer returns 403
# ---------------------------------------------------------------------------

def test_insurance_premiums_update_farmer_403(api, admin_auth, farmer_auth):
    """PUT /v1/reference/insurance-premiums/{id} as farmer returns 403."""
    premiums_resp = api.get("/v1/reference/insurance-premiums", headers=admin_auth)
    assert premiums_resp.status_code == 200
    premiums = premiums_resp.json()["data"]
    if not premiums:
        pytest.skip("No insurance premiums in seed data")

    prem_id = premiums[0]["id"]
    resp = api.put(
        f"/v1/reference/insurance-premiums/{prem_id}",
        json={"scheme_name": "should-fail"},
        headers=farmer_auth,
    )
    assert resp.status_code == 403, (
        f"Expected 403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 10: PUT /v1/reference/insurance-premiums/{id} — admin can update
# ---------------------------------------------------------------------------

def test_insurance_premiums_update_admin(api, admin_auth):
    """PUT /v1/reference/insurance-premiums/{id} as admin updates the record."""
    premiums_resp = api.get("/v1/reference/insurance-premiums", headers=admin_auth)
    assert premiums_resp.status_code == 200
    premiums = premiums_resp.json()["data"]
    if not premiums:
        pytest.skip("No insurance premiums in seed data")

    prem_id = premiums[0]["id"]
    original_scheme = premiums[0].get("scheme_name", "original")

    new_scheme = "Test-Scheme-Updated"
    resp = api.put(
        f"/v1/reference/insurance-premiums/{prem_id}",
        json={"scheme_name": new_scheme},
        headers=admin_auth,
    )
    assert resp.status_code == 200, f"PUT insurance-premium failed: {resp.text}"
    body = resp.json()
    assert body["scheme_name"] == new_scheme, f"Scheme name not updated: {body}"

    # Restore
    api.put(
        f"/v1/reference/insurance-premiums/{prem_id}",
        json={"scheme_name": original_scheme},
        headers=admin_auth,
    )


# ---------------------------------------------------------------------------
# Test 11: GET /v1/reference/medicines — any auth can read
# ---------------------------------------------------------------------------

def test_medicines_list_farmer(api, farmer_auth):
    """GET /v1/reference/medicines as farmer returns data+total envelope."""
    start = time.time()
    resp = api.get("/v1/reference/medicines", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/reference/medicines: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body and "total" in body
    assert isinstance(body["data"], list)

    for med in body["data"]:
        assert "id" in med, f"Medicine missing 'id': {med}"
        assert "name" in med, f"Medicine missing 'name': {med}"


# ---------------------------------------------------------------------------
# Test 12: GET /v1/reference/medicines — is_active filter works
# ---------------------------------------------------------------------------

def test_medicines_is_active_filter(api, farmer_auth):
    """GET /v1/reference/medicines?is_active=true returns only active medicines."""
    resp = api.get("/v1/reference/medicines?is_active=true", headers=farmer_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    for med in resp.json()["data"]:
        assert med.get("is_active") is True, (
            f"is_active filter returned inactive medicine: {med}"
        )
