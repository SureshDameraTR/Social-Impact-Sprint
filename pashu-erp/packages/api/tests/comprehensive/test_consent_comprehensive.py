"""Comprehensive integration tests for /v1/consent endpoints (DPDP Act 2023).

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Consent operations are scoped to the authenticated user — farmer2 is used
as the primary subject to keep state isolated from other test files.

ConsentPurpose values (from app/models/consent.py):
  livestock_management | health_records | financial_transactions |
  government_schemes   | analytics

Run: pytest tests/comprehensive/test_consent_comprehensive.py -v
"""

import time

import pytest

# Use a purpose unlikely to be pre-seeded for farmer2 so grant/withdraw cycles work cleanly
TEST_PURPOSE = "analytics"
TEST_CONSENT_TEXT = (
    "I hereby grant PashuRaksha permission to process my livestock data "
    "for analytics and platform improvement under DPDP Act 2023."
)


# ---------------------------------------------------------------------------
# Helper: ensure a clean granted consent exists for farmer2 on TEST_PURPOSE
# ---------------------------------------------------------------------------

def _ensure_granted_consent(api, auth_headers: dict) -> dict:
    """Grant TEST_PURPOSE consent and return the response body."""
    resp = api.post(
        "/v1/consent/grant",
        json={"purpose": TEST_PURPOSE, "consent_text": TEST_CONSENT_TEXT},
        headers=auth_headers,
    )
    assert resp.status_code == 201, f"Grant failed: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# Test 1: POST /v1/consent/grant — happy path returns 201 with consent record
# ---------------------------------------------------------------------------

def test_consent_grant_happy_path(api, farmer2_auth):
    """POST /v1/consent/grant returns 201 with id, user_id, purpose, status=granted."""
    start = time.time()
    resp = api.post(
        "/v1/consent/grant",
        json={"purpose": TEST_PURPOSE, "consent_text": TEST_CONSENT_TEXT},
        headers=farmer2_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/consent/grant: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "id" in body, f"Missing 'id': {body}"
    assert "user_id" in body, f"Missing 'user_id': {body}"
    assert "purpose" in body, f"Missing 'purpose': {body}"
    assert "status" in body, f"Missing 'status': {body}"
    assert "consent_text" in body, f"Missing 'consent_text': {body}"
    assert "created_at" in body, f"Missing 'created_at': {body}"

    assert body["purpose"] == TEST_PURPOSE
    assert body["status"] == "granted"
    assert body["consent_text"] == TEST_CONSENT_TEXT


# ---------------------------------------------------------------------------
# Test 2: POST /v1/consent/grant — 401 without auth
# ---------------------------------------------------------------------------

def test_consent_grant_unauthenticated_401(api):
    """POST /v1/consent/grant without auth returns 401."""
    resp = api.post(
        "/v1/consent/grant",
        json={"purpose": TEST_PURPOSE, "consent_text": TEST_CONSENT_TEXT},
    )
    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 3: POST /v1/consent/grant — 422 for invalid purpose value
# ---------------------------------------------------------------------------

def test_consent_grant_invalid_purpose_422(api, farmer2_auth):
    """POST /v1/consent/grant with an unknown purpose returns 422."""
    resp = api.post(
        "/v1/consent/grant",
        json={"purpose": "surveillance", "consent_text": TEST_CONSENT_TEXT},
        headers=farmer2_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for invalid purpose, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: POST /v1/consent/grant — 422 for consent_text too short (< 10 chars)
# ---------------------------------------------------------------------------

def test_consent_grant_short_text_422(api, farmer2_auth):
    """POST /v1/consent/grant with consent_text < 10 chars returns 422."""
    resp = api.post(
        "/v1/consent/grant",
        json={"purpose": TEST_PURPOSE, "consent_text": "too short"},
        headers=farmer2_auth,
    )
    assert resp.status_code == 422, (
        f"Expected 422 for short consent_text, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 5: GET /v1/consent/my — lists consents for authenticated user
# ---------------------------------------------------------------------------

def test_consent_list_my_happy_path(api, farmer2_auth):
    """GET /v1/consent/my returns data+total envelope for the current user."""
    # Grant one first so list is non-empty
    _ensure_granted_consent(api, farmer2_auth)

    start = time.time()
    resp = api.get("/v1/consent/my", headers=farmer2_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /v1/consent/my: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data': {body}"
    assert "total" in body, f"Missing 'total': {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 1, f"Expected at least 1 consent after grant: {body}"


# ---------------------------------------------------------------------------
# Test 6: GET /v1/consent/my — 401 without auth
# ---------------------------------------------------------------------------

def test_consent_list_my_unauthenticated_401(api):
    """GET /v1/consent/my without auth returns 401."""
    resp = api.get("/v1/consent/my")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: GET /v1/consent/my — each consent item has required fields
# ---------------------------------------------------------------------------

def test_consent_list_item_schema(api, farmer2_auth):
    """Each consent record in GET /v1/consent/my has required schema fields."""
    _ensure_granted_consent(api, farmer2_auth)
    resp = api.get("/v1/consent/my", headers=farmer2_auth)
    assert resp.status_code == 200
    body = resp.json()

    for consent in body["data"]:
        assert "id" in consent, f"Consent missing 'id': {consent}"
        assert "purpose" in consent, f"Consent missing 'purpose': {consent}"
        assert "status" in consent, f"Consent missing 'status': {consent}"
        assert "consent_text" in consent, f"Consent missing 'consent_text': {consent}"
        assert "created_at" in consent, f"Consent missing 'created_at': {consent}"
        assert consent["status"] in ("granted", "withdrawn"), (
            f"Unknown status '{consent['status']}'"
        )


# ---------------------------------------------------------------------------
# Test 8: GET /v1/consent/my — scoped per user (farmer1 sees only own records)
# ---------------------------------------------------------------------------

def test_consent_list_user_isolation(api, farmer_auth, farmer2_auth):
    """Each user's GET /v1/consent/my only returns their own consent records."""
    # Grant for farmer2
    consent = _ensure_granted_consent(api, farmer2_auth)
    farmer2_consent_id = consent["id"]

    # farmer1 should NOT see farmer2's consent
    resp = api.get("/v1/consent/my", headers=farmer_auth)
    assert resp.status_code == 200
    farmer1_ids = {c["id"] for c in resp.json()["data"]}
    assert farmer2_consent_id not in farmer1_ids, (
        f"farmer1 can see farmer2's consent {farmer2_consent_id}"
    )


# ---------------------------------------------------------------------------
# Test 9: POST /v1/consent/withdraw — withdraws a granted consent
# ---------------------------------------------------------------------------

def test_consent_withdraw_happy_path(api, farmer2_auth):
    """POST /v1/consent/withdraw changes status from granted to withdrawn."""
    # Ensure a granted consent exists for TEST_PURPOSE
    _ensure_granted_consent(api, farmer2_auth)

    start = time.time()
    resp = api.post(
        "/v1/consent/withdraw",
        json={"purpose": TEST_PURPOSE},
        headers=farmer2_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/consent/withdraw: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["status"] == "withdrawn", f"Expected status=withdrawn: {body}"
    assert body["purpose"] == TEST_PURPOSE, f"Purpose mismatch: {body}"


# ---------------------------------------------------------------------------
# Test 10: POST /v1/consent/withdraw — 404 when no granted consent exists
# ---------------------------------------------------------------------------

def test_consent_withdraw_no_consent_404(api, farmer2_auth):
    """POST /v1/consent/withdraw for a purpose with no granted consent returns 404."""
    # Use a purpose that is unlikely to have an active granted consent after prior withdrawal
    # First, withdraw any existing government_schemes consent
    api.post(
        "/v1/consent/withdraw",
        json={"purpose": "government_schemes"},
        headers=farmer2_auth,
    )
    # Now try to withdraw again — no granted consent should remain
    resp = api.post(
        "/v1/consent/withdraw",
        json={"purpose": "government_schemes"},
        headers=farmer2_auth,
    )
    # Might be 404 if none was granted, or 200 if one existed — both acceptable
    # If 200 returned, withdraw again until we get 404
    attempts = 0
    while resp.status_code == 200 and attempts < 5:
        resp = api.post(
            "/v1/consent/withdraw",
            json={"purpose": "government_schemes"},
            headers=farmer2_auth,
        )
        attempts += 1

    assert resp.status_code == 404, (
        f"Expected 404 after exhausting granted consents, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 11: DELETE /v1/consent/erasure-request — accepted with 202
# ---------------------------------------------------------------------------

def test_consent_erasure_request_accepted(api, farmer2_auth):
    """DELETE /v1/consent/erasure-request returns 202 with detail message."""
    # Grant a consent first so there is something to erase
    _ensure_granted_consent(api, farmer2_auth)

    start = time.time()
    resp = api.delete("/v1/consent/erasure-request", headers=farmer2_auth)
    duration = time.time() - start
    print(f"\n[timing] DELETE /v1/consent/erasure-request: {duration:.3f}s")

    assert resp.status_code == 202, f"Expected 202, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "detail" in body, f"Missing 'detail': {body}"
    assert "erasure" in body["detail"].lower() or "request" in body["detail"].lower(), (
        f"Detail doesn't mention erasure: {body['detail']}"
    )
    assert "user_id" in body, f"Missing 'user_id': {body}"


# ---------------------------------------------------------------------------
# Test 12: DELETE /v1/consent/erasure-request — 401 without auth
# ---------------------------------------------------------------------------

def test_consent_erasure_unauthenticated_401(api):
    """DELETE /v1/consent/erasure-request without auth returns 401."""
    resp = api.delete("/v1/consent/erasure-request")
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )
