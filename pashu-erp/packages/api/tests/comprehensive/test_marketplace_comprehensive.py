"""Comprehensive integration tests for /v1/marketplace endpoints.

Endpoints:
  GET  /v1/marketplace                  — list sell records (admin: all, farmer: own)
  POST /v1/marketplace/sell             — record a product sale
  GET  /v1/marketplace/history/{user_id} — sell history with pagination
  GET  /v1/marketplace/rates            — current Karnataka APMC market rates
  GET  /v1/marketplace/summary/{user_id} — marketplace stats summary

SellRecordCreate schema:
  product_type: milk|eggs|goat_products|sheep_products|manure|wool|other
  quantity: Decimal gt=0
  unit: str max_length=20
  price_per_unit: Decimal gt=0
  buyer_name: str | None
  buyer_phone: str | None
  notes: str | None

SellRecordRead schema:
  id, user_id, product_type, quantity, unit, price_per_unit, total_amount,
  buyer_name, buyer_phone, sold_at, notes, created_at
"""

import time
import uuid

import pytest

BASE = "/v1/marketplace"

VALID_PRODUCT_TYPES = ["milk", "eggs", "goat_products", "sheep_products", "manure", "wool", "other"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_user_id(api, auth_headers) -> str:
    resp = api.get("/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return str(resp.json()["user_id"])


def _create_sale(api, auth_headers, **overrides) -> dict:
    """Helper to POST a sale and return the response body."""
    payload = {
        "product_type": "milk",
        "quantity": "10.00",
        "unit": "litre",
        "price_per_unit": "35.00",
        "buyer_name": "Integration Test Buyer",
        "notes": "Test sale",
    }
    payload.update(overrides)
    resp = api.post(f"{BASE}/sell", json=payload, headers=auth_headers)
    return resp


# ===========================================================================
# POSITIVE TESTS
# ===========================================================================


def test_list_sell_records_returns_envelope(api, farmer_auth):
    """GET /v1/marketplace returns {data, total, limit, offset}."""
    t0 = time.time()
    resp = api.get(BASE, headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE} → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert "limit" in body, f"Missing 'limit': {body}"
    assert "offset" in body, f"Missing 'offset': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 0


def test_list_sell_records_item_schema(api, farmer_auth):
    """Each sell record has expected fields."""
    # Ensure at least one record exists
    _create_sale(api, farmer_auth)

    resp = api.get(BASE, headers=farmer_auth)
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]

    if data:
        record = data[0]
        for field in (
            "id", "user_id", "product_type", "quantity", "unit",
            "price_per_unit", "total_amount", "sold_at", "created_at",
        ):
            assert field in record, f"Missing field '{field}': {record}"
        assert record["product_type"] in VALID_PRODUCT_TYPES


def test_post_sell_milk_created(api, farmer_auth):
    """POST /v1/marketplace/sell with milk data → 201 with correct fields."""
    t0 = time.time()
    resp = _create_sale(api, farmer_auth, product_type="milk", quantity="15.50", price_per_unit="38.00")
    elapsed = time.time() - t0
    print(f"\nPOST {BASE}/sell → {resp.status_code} in {elapsed:.3f}s | {resp.text[:200]}")

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "id" in body
    assert "user_id" in body
    assert body["product_type"] == "milk"
    assert float(body["quantity"]) == pytest.approx(15.50)
    assert float(body["price_per_unit"]) == pytest.approx(38.00)
    # total_amount = 15.50 * 38.00 = 589.00
    assert float(body["total_amount"]) == pytest.approx(589.00, abs=0.01)
    assert "sold_at" in body


def test_post_sell_eggs_product_type(api, farmer_auth):
    """POST /v1/marketplace/sell with eggs product type → 201."""
    resp = _create_sale(api, farmer_auth, product_type="eggs", quantity="100.00",
                        unit="dozen", price_per_unit="60.00")
    assert resp.status_code == 201, resp.text
    assert resp.json()["product_type"] == "eggs"


def test_post_sell_without_optional_fields(api, farmer_auth):
    """POST /v1/marketplace/sell without buyer_name/phone/notes → 201."""
    payload = {
        "product_type": "wool",
        "quantity": "5.00",
        "unit": "kg",
        "price_per_unit": "120.00",
    }
    resp = api.post(f"{BASE}/sell", json=payload, headers=farmer_auth)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["buyer_name"] is None
    assert body["buyer_phone"] is None


def test_sell_history_self_access(api, farmer_auth):
    """GET /v1/marketplace/history/{own_user_id} → 200 with envelope."""
    user_id = _get_user_id(api, farmer_auth)
    t0 = time.time()
    resp = api.get(f"{BASE}/history/{user_id}", headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/history/{user_id} → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "data" in body
    assert "total" in body
    assert isinstance(body["data"], list)


def test_sell_history_pagination_no_overlap(api, farmer_auth):
    """Two pages of sell history must not overlap in IDs."""
    user_id = _get_user_id(api, farmer_auth)

    # Ensure at least 2 records
    _create_sale(api, farmer_auth)
    _create_sale(api, farmer_auth)

    page1 = api.get(f"{BASE}/history/{user_id}", headers=farmer_auth,
                    params={"limit": 2, "offset": 0})
    page2 = api.get(f"{BASE}/history/{user_id}", headers=farmer_auth,
                    params={"limit": 2, "offset": 2})

    assert page1.status_code == 200, page1.text
    assert page2.status_code == 200, page2.text

    ids1 = {r["id"] for r in page1.json()["data"]}
    ids2 = {r["id"] for r in page2.json()["data"]}
    overlap = ids1 & ids2
    assert not overlap, f"Overlapping IDs across pages: {overlap}"


def test_get_market_rates_schema(api, farmer_auth):
    """GET /v1/marketplace/rates returns source, updated_at, rates."""
    t0 = time.time()
    resp = api.get(f"{BASE}/rates", headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/rates → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "source" in body, f"Missing 'source': {body}"
    assert "updated_at" in body, f"Missing 'updated_at': {body}"
    assert "rates" in body, f"Missing 'rates': {body}"


def test_get_marketplace_summary_self(api, farmer_auth):
    """GET /v1/marketplace/summary/{own_user_id} returns summary stats."""
    user_id = _get_user_id(api, farmer_auth)
    t0 = time.time()
    resp = api.get(f"{BASE}/summary/{user_id}", headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/summary/{user_id} → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    for field in ("user_id", "total_revenue", "total_quantity", "total_sales", "by_product"):
        assert field in body, f"Missing field '{field}': {body}"
    assert body["user_id"] == user_id
    assert isinstance(body["total_sales"], int)
    assert isinstance(body["by_product"], dict)


def test_admin_list_sees_all_records(api, admin_auth, farmer_auth):
    """Admin list total >= farmer list total."""
    admin_resp = api.get(BASE, headers=admin_auth)
    farmer_resp = api.get(BASE, headers=farmer_auth)

    assert admin_resp.status_code == 200, admin_resp.text
    assert farmer_resp.status_code == 200, farmer_resp.text

    assert admin_resp.json()["total"] >= farmer_resp.json()["total"]


def test_post_sell_total_amount_computed_correctly(api, farmer_auth):
    """total_amount == quantity * price_per_unit."""
    qty = 8.00
    price = 45.50
    expected_total = round(qty * price, 2)  # 364.00

    resp = _create_sale(api, farmer_auth,
                        quantity=str(qty), price_per_unit=str(price), product_type="other")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert float(body["total_amount"]) == pytest.approx(expected_total, abs=0.01), (
        f"total_amount mismatch: {body['total_amount']} != {expected_total}"
    )


# ===========================================================================
# NEGATIVE TESTS
# ===========================================================================


def test_list_requires_auth(api):
    """GET /v1/marketplace without auth → 401."""
    resp = api.get(BASE)
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_sell_requires_auth(api):
    """POST /v1/marketplace/sell without auth → 401/403 (CSRF fires before JWT)."""
    payload = {"product_type": "milk", "quantity": "5.00", "unit": "litre", "price_per_unit": "35.00"}
    resp = api.post(f"{BASE}/sell", json=payload)
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}: {resp.text}"


def test_rates_requires_auth(api):
    """GET /v1/marketplace/rates without auth → 401."""
    resp = api.get(f"{BASE}/rates")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_sell_missing_product_type(api, farmer_auth):
    """POST /v1/marketplace/sell without product_type → 422."""
    payload = {"quantity": "5.00", "unit": "litre", "price_per_unit": "35.00"}
    resp = api.post(f"{BASE}/sell", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_sell_invalid_product_type(api, farmer_auth):
    """POST /v1/marketplace/sell with unknown product_type → 422."""
    payload = {
        "product_type": "vegetables",  # not a valid ProductType
        "quantity": "5.00",
        "unit": "kg",
        "price_per_unit": "20.00",
    }
    resp = api.post(f"{BASE}/sell", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_sell_zero_quantity_rejected(api, farmer_auth):
    """POST /v1/marketplace/sell with quantity=0 → 422 (gt=0)."""
    payload = {"product_type": "milk", "quantity": "0.00", "unit": "litre", "price_per_unit": "35.00"}
    resp = api.post(f"{BASE}/sell", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_sell_zero_price_rejected(api, farmer_auth):
    """POST /v1/marketplace/sell with price_per_unit=0 → 422 (gt=0)."""
    payload = {"product_type": "eggs", "quantity": "10.00", "unit": "dozen", "price_per_unit": "0.00"}
    resp = api.post(f"{BASE}/sell", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_history_other_user_forbidden(api, farmer_auth, farmer2_auth):
    """GET /v1/marketplace/history/{other_user_id} as farmer → 403."""
    other_id = _get_user_id(api, farmer2_auth)
    resp = api.get(f"{BASE}/history/{other_id}", headers=farmer_auth)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


def test_summary_other_user_forbidden(api, farmer_auth, farmer2_auth):
    """GET /v1/marketplace/summary/{other_user_id} as farmer → 403."""
    other_id = _get_user_id(api, farmer2_auth)
    resp = api.get(f"{BASE}/summary/{other_id}", headers=farmer_auth)
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


def test_history_invalid_uuid_path(api, farmer_auth):
    """GET /v1/marketplace/history/not-a-uuid → 422."""
    resp = api.get(f"{BASE}/history/not-a-uuid", headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_sell_unit_too_long(api, farmer_auth):
    """POST /v1/marketplace/sell with unit > 20 chars → 422."""
    payload = {
        "product_type": "milk",
        "quantity": "5.00",
        "unit": "x" * 21,  # max_length=20
        "price_per_unit": "35.00",
    }
    resp = api.post(f"{BASE}/sell", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
