"""Comprehensive integration tests for /v1/finance endpoints.

Covers: POST /transaction, GET /summary (week/month/year), auth checks, validation.

TransactionCreate schema:
  type: "income" | "expense"
  amount: Decimal gt=0
  category: str max_length=50
  reference_id: UUID | None
  description: str | None

TransactionRead schema:
  id, user_id, type, amount, category, reference_id, description, status, created_at
"""

import time
import uuid

import pytest

BASE = "/v1/finance"


# ===========================================================================
# POSITIVE TESTS
# ===========================================================================


def test_post_income_transaction_created(api, farmer_auth):
    """POST /v1/finance/transaction with valid income data → 201."""
    payload = {
        "type": "income",
        "amount": "1500.00",
        "category": "milk_sale",
        "description": "Integration test income entry",
    }
    t0 = time.time()
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    elapsed = time.time() - t0
    print(f"\nPOST {BASE}/transaction → {resp.status_code} in {elapsed:.3f}s | {resp.text[:200]}")

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "id" in body, f"Missing id: {body}"
    assert "user_id" in body
    assert body["type"] == "income"
    assert float(body["amount"]) == pytest.approx(1500.00)
    assert body["category"] == "milk_sale"
    assert "status" in body
    assert "created_at" in body


def test_post_expense_transaction_created(api, farmer_auth):
    """POST /v1/finance/transaction with valid expense data → 201."""
    payload = {
        "type": "expense",
        "amount": "250.50",
        "category": "feed",
        "description": "Feed purchase",
    }
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["type"] == "expense"
    assert float(body["amount"]) == pytest.approx(250.50)


def test_post_transaction_with_reference_id(api, farmer_auth):
    """POST /v1/finance/transaction with optional reference_id → 201."""
    ref_id = str(uuid.uuid4())
    payload = {
        "type": "income",
        "amount": "800.00",
        "category": "cattle_sale",
        "reference_id": ref_id,
        "description": "Sale with reference",
    }
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["reference_id"] == ref_id


def test_financial_summary_month(api, farmer_auth):
    """GET /v1/finance/summary?period=month returns correct structure."""
    t0 = time.time()
    resp = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "month"})
    elapsed = time.time() - t0
    print(f"\nGET {BASE}/summary?period=month → {resp.status_code} in {elapsed:.3f}s")

    assert resp.status_code == 200, resp.text
    body = resp.json()
    for field in ("period", "total_income", "total_expense", "net", "transaction_count"):
        assert field in body, f"Missing field '{field}': {body}"
    assert body["period"] == "month"
    assert isinstance(body["total_income"], (int, float))
    assert isinstance(body["total_expense"], (int, float))
    assert isinstance(body["transaction_count"], int)


def test_financial_summary_week_period(api, farmer_auth):
    """GET /v1/finance/summary?period=week returns period=week in response."""
    resp = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "week"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["period"] == "week"


def test_financial_summary_year_period(api, farmer_auth):
    """GET /v1/finance/summary?period=year returns period=year in response."""
    resp = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "year"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["period"] == "year"


def test_financial_summary_net_is_income_minus_expense(api, farmer_auth):
    """Summary: net == total_income - total_expense."""
    resp = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "month"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    expected_net = round(body["total_income"] - body["total_expense"], 2)
    assert body["net"] == pytest.approx(expected_net, abs=0.01), (
        f"net mismatch: {body['net']} != {expected_net}"
    )


def test_financial_summary_categories_are_dicts(api, farmer_auth):
    """Summary income_by_category and expense_by_category are dicts."""
    resp = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "month"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body.get("income_by_category", {}), dict)
    assert isinstance(body.get("expense_by_category", {}), dict)


def test_transaction_reflects_in_summary(api, farmer_auth):
    """After posting a transaction, summary transaction_count increases."""
    before = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "month"}).json()
    before_count = before["transaction_count"]

    payload = {
        "type": "income",
        "amount": "100.00",
        "category": "other",
        "description": "count-check test",
    }
    create_resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert create_resp.status_code == 201, create_resp.text

    after = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "month"}).json()
    assert after["transaction_count"] == before_count + 1, (
        f"Count did not increase: before={before_count}, after={after['transaction_count']}"
    )


# ===========================================================================
# NEGATIVE TESTS
# ===========================================================================


def test_transaction_requires_auth(api):
    """POST /v1/finance/transaction without auth → 401/403 (CSRF fires before JWT)."""
    payload = {"type": "income", "amount": "100.00", "category": "test"}
    resp = api.post(f"{BASE}/transaction", json=payload)
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}: {resp.text}"


def test_summary_requires_auth(api):
    """GET /v1/finance/summary without auth → 401."""
    resp = api.get(f"{BASE}/summary")
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


def test_transaction_missing_type(api, farmer_auth):
    """POST /v1/finance/transaction without type → 422."""
    payload = {"amount": "100.00", "category": "test"}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_transaction_missing_amount(api, farmer_auth):
    """POST /v1/finance/transaction without amount → 422."""
    payload = {"type": "income", "category": "test"}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_transaction_zero_amount_rejected(api, farmer_auth):
    """POST /v1/finance/transaction with amount=0 → 422 (gt=0)."""
    payload = {"type": "income", "amount": "0.00", "category": "test"}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_transaction_negative_amount_rejected(api, farmer_auth):
    """POST /v1/finance/transaction with negative amount → 422."""
    payload = {"type": "expense", "amount": "-50.00", "category": "test"}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_transaction_invalid_type_rejected(api, farmer_auth):
    """POST /v1/finance/transaction with type='transfer' → 422."""
    payload = {"type": "transfer", "amount": "100.00", "category": "test"}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_transaction_category_too_long(api, farmer_auth):
    """POST /v1/finance/transaction with category > 50 chars → 422."""
    payload = {"type": "income", "amount": "100.00", "category": "x" * 51}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_summary_missing_category_field(api, farmer_auth):
    """POST /v1/finance/transaction with missing category → 422."""
    payload = {"type": "income", "amount": "100.00"}
    resp = api.post(f"{BASE}/transaction", json=payload, headers=farmer_auth)
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


def test_summary_unknown_period_falls_back_to_month(api, farmer_auth):
    """GET /v1/finance/summary with unknown period returns month-like response."""
    resp = api.get(f"{BASE}/summary", headers=farmer_auth, params={"period": "quarterly"})
    # Router defaults unknown → month (30-day) but returns whatever period value was passed
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    # summary always returns some period string
    assert "period" in body
