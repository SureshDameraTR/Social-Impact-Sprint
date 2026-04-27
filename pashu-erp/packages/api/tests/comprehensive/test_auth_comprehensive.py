"""Comprehensive integration tests for /v1/auth endpoints.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_auth_comprehensive.py -v

NOTE on rate limiting: the /v1/auth/request-otp endpoint is rate-limited to
5 requests per minute per IP. The session conftest already uses 3 slots to
obtain admin/farmer/farmer2 tokens. Tests that make additional OTP requests
skip gracefully when the endpoint is rate-limited.

Recommended: run this file in isolation after a clean server restart, or wait
60 seconds between the conftest setup and test execution:

    pytest tests/comprehensive/test_auth_comprehensive.py -v
"""

import re
import subprocess
import time

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PHONE_FARMER = "+919900000002"
PHONE_FARMER2 = "+919900000003"
PHONE_ADMIN = "+919900000001"
# farmer3 — not used by session conftest, reserved for refresh token test
PHONE_FARMER3 = "+919900000004"


def extract_otp() -> str | None:
    """Read the most recent OTP from docker API container logs."""
    time.sleep(0.3)
    result = subprocess.run(
        ["docker", "logs", "pashu-erp-api-1", "--tail", "15"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    matches = re.findall(r"Code:\s*(\d{6})", result.stdout + result.stderr)
    return matches[-1] if matches else None


def _request_otp_or_skip(api, phone: str) -> None:
    """POST request-otp; skip the test gracefully if the rate limit is hit."""
    resp = api.post("/v1/auth/request-otp", json={"phone": phone})
    if resp.status_code == 429:
        pytest.skip(
            "OTP endpoint rate-limited (5/min per IP). "
            "Run this test file in isolation or wait 60s after conftest setup."
        )
    assert resp.status_code == 200, f"OTP request failed ({resp.status_code}): {resp.text}"


# ---------------------------------------------------------------------------
# Test 1: request-otp with valid phone → 200
# ---------------------------------------------------------------------------

def test_request_otp_valid_phone(api):
    """POST /v1/auth/request-otp with a valid +91 phone returns 200 or skips on rate limit."""
    start = time.time()
    resp = api.post("/v1/auth/request-otp", json={"phone": PHONE_FARMER})
    duration = time.time() - start
    print(f"\n[timing] request-otp valid: {duration:.3f}s")

    if resp.status_code == 429:
        pytest.skip("OTP rate-limited; run in isolation to validate this path")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "message" in body
    assert (
        "OTP" in body["message"]
        or "otp" in body["message"].lower()
        or "sent" in body["message"].lower()
    )


# ---------------------------------------------------------------------------
# Test 2: request-otp with invalid phone (no +91 prefix) → 422
# ---------------------------------------------------------------------------

def test_request_otp_invalid_phone_no_prefix(api):
    """POST /v1/auth/request-otp without +91 prefix returns 422 validation error."""
    start = time.time()
    resp = api.post("/v1/auth/request-otp", json={"phone": "9900000002"})
    duration = time.time() - start
    print(f"\n[timing] request-otp invalid prefix: {duration:.3f}s")

    # Validation runs before rate limiting — always 422 regardless of rate limit state.
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 3: request-otp with short phone number → 422
# ---------------------------------------------------------------------------

def test_request_otp_short_phone(api):
    """POST /v1/auth/request-otp with a short number returns 422 validation error."""
    start = time.time()
    resp = api.post("/v1/auth/request-otp", json={"phone": "+9199"})
    duration = time.time() - start
    print(f"\n[timing] request-otp short: {duration:.3f}s")

    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 4: verify-otp with correct OTP (extracted from docker logs) → 200
# ---------------------------------------------------------------------------

def test_verify_otp_correct(api):
    """Full OTP flow: request → extract from logs → verify → get tokens."""
    _request_otp_or_skip(api, PHONE_FARMER)
    otp = extract_otp()
    assert otp is not None, "Could not extract OTP from docker logs"

    start = time.time()
    verify_resp = api.post(
        "/v1/auth/verify-otp",
        json={"phone": PHONE_FARMER, "otp": otp, "client_type": "mobile"},
    )
    duration = time.time() - start
    print(f"\n[timing] verify-otp correct full flow: {duration:.3f}s")

    assert verify_resp.status_code == 200, (
        f"Expected 200, got {verify_resp.status_code}: {verify_resp.text}"
    )
    body = verify_resp.json()
    assert "access_token" in body, f"Missing access_token in: {body}"
    assert "refresh_token" in body, f"Missing refresh_token in: {body}"
    assert body["access_token"], "access_token must be non-empty"
    assert body["refresh_token"], "refresh_token must be non-empty"


# ---------------------------------------------------------------------------
# Test 5: verify-otp with wrong OTP → 401
# ---------------------------------------------------------------------------

def test_verify_otp_wrong_otp(api):
    """POST /v1/auth/verify-otp with incorrect OTP returns 401."""
    _request_otp_or_skip(api, PHONE_FARMER2)

    start = time.time()
    resp = api.post(
        "/v1/auth/verify-otp",
        json={"phone": PHONE_FARMER2, "otp": "000000", "client_type": "mobile"},
    )
    duration = time.time() - start
    print(f"\n[timing] verify-otp wrong otp: {duration:.3f}s")

    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "detail" in body


# ---------------------------------------------------------------------------
# Test 6: verify-otp for a phone that never requested OTP → 401
# ---------------------------------------------------------------------------

def test_verify_otp_no_prior_request(api):
    """POST /v1/auth/verify-otp for a phone with no OTP record returns 401.

    The verify endpoint itself is rate-limited to 5/minute. If the rate limit
    is already exhausted from other tests, the endpoint returns 429 instead of
    401. We accept both to guard against environment interference.
    """
    # Use a phone that has no OTP pending (never seeded)
    fresh_phone = "+919800000099"
    start = time.time()
    resp = api.post(
        "/v1/auth/verify-otp",
        json={"phone": fresh_phone, "otp": "123456", "client_type": "mobile"},
    )
    duration = time.time() - start
    print(f"\n[timing] verify-otp no prior request: {duration:.3f}s")

    # 401: no OTP record (expected). 429: rate-limited (environment condition).
    assert resp.status_code in (401, 429), (
        f"Expected 401 (no OTP record) or 429 (rate limited), got {resp.status_code}: {resp.text}"
    )
    if resp.status_code == 429:
        pytest.skip("Verify endpoint rate-limited; run in isolation to confirm 401 path")


# ---------------------------------------------------------------------------
# Test 7: verify-otp with mobile client_type → tokens returned in body
# ---------------------------------------------------------------------------

def test_verify_otp_mobile_client_type(api):
    """Mobile client_type returns access_token and refresh_token in JSON body."""
    _request_otp_or_skip(api, PHONE_ADMIN)
    otp = extract_otp()
    assert otp is not None, "Could not extract OTP from docker logs"

    start = time.time()
    resp = api.post(
        "/v1/auth/verify-otp",
        json={"phone": PHONE_ADMIN, "otp": otp, "client_type": "mobile"},
    )
    duration = time.time() - start
    print(f"\n[timing] verify-otp mobile client: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    # Mobile client must receive tokens in the body
    assert "access_token" in body, f"Missing access_token in body: {body}"
    assert "refresh_token" in body, f"Missing refresh_token in body: {body}"
    assert "user_id" in body, f"Missing user_id in body: {body}"
    assert "role" in body, f"Missing role in body: {body}"
    assert body.get("token_type") == "bearer", (
        f"Expected token_type='bearer', got: {body.get('token_type')}"
    )


# ---------------------------------------------------------------------------
# Test 8: GET /me with valid token → 200, returns user_id + role
# ---------------------------------------------------------------------------

def test_get_me_valid_token(api, farmer_auth):
    """GET /v1/auth/me with a valid bearer token returns user_id and role."""
    start = time.time()
    resp = api.get("/v1/auth/me", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] GET /me valid token: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "user_id" in body, f"Missing user_id in: {body}"
    assert "role" in body, f"Missing role in: {body}"
    assert body["user_id"], "user_id must be non-empty"
    assert body["role"] in ("admin", "farmer", "vet", "milk_center"), (
        f"Unexpected role: {body['role']}"
    )


# ---------------------------------------------------------------------------
# Test 9: GET /me with no token → 401
# ---------------------------------------------------------------------------

def test_get_me_no_token(api):
    """GET /v1/auth/me without Authorization header returns 401."""
    start = time.time()
    resp = api.get("/v1/auth/me")
    duration = time.time() - start
    print(f"\n[timing] GET /me no token: {duration:.3f}s")

    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 10: GET /me with garbage token → 401
# ---------------------------------------------------------------------------

def test_get_me_garbage_token(api):
    """GET /v1/auth/me with a malformed token returns 401."""
    start = time.time()
    resp = api.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer this.is.not.a.valid.jwt.token"},
    )
    duration = time.time() - start
    print(f"\n[timing] GET /me garbage token: {duration:.3f}s")

    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 11: refresh with valid refresh_token → 200, new token pair issued
# ---------------------------------------------------------------------------

def test_refresh_with_valid_token(api):
    """POST /v1/auth/refresh with a valid refresh_token returns a new token pair.

    Uses farmer3 (+919900000004) which is outside the session conftest fixtures
    to avoid cross-contaminating the shared tokens.  Skips gracefully when the
    OTP rate limit is exhausted — run this test file in isolation for full coverage.
    """
    phone = PHONE_FARMER3

    req_resp = api.post("/v1/auth/request-otp", json={"phone": phone})
    if req_resp.status_code == 429:
        pytest.skip("OTP endpoint rate-limited (5/min per IP); run in isolation")
    assert req_resp.status_code == 200, f"OTP request failed: {req_resp.text}"

    otp = extract_otp()
    assert otp is not None, "Could not extract OTP from docker logs"

    verify_resp = api.post(
        "/v1/auth/verify-otp",
        json={"phone": phone, "otp": otp, "client_type": "mobile"},
    )
    assert verify_resp.status_code == 200, f"OTP verify failed: {verify_resp.text}"
    refresh_token = verify_resp.json()["refresh_token"]

    start = time.time()
    resp = api.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    duration = time.time() - start
    print(f"\n[timing] refresh valid token: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "access_token" in body, f"Missing access_token in: {body}"
    assert "refresh_token" in body, f"Missing refresh_token in: {body}"
    # Token rotation: the new refresh token must differ from the original
    assert body["refresh_token"] != refresh_token, "Refresh token should be rotated"


# ---------------------------------------------------------------------------
# Test 12: logout → 200
# ---------------------------------------------------------------------------

def test_logout(api, farmer_token):
    """POST /v1/auth/logout with the session farmer token returns 200.

    Reuses the session-scoped farmer_token (no new OTP request required).
    WARNING: after this call the token is revoked — run auth tests last
    or in an isolated session to avoid breaking other farmer_auth-dependent tests.
    """
    start = time.time()
    resp = api.post(
        "/v1/auth/logout",
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    duration = time.time() - start
    print(f"\n[timing] logout: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "message" in body
    assert "logout" in body["message"].lower() or "logged" in body["message"].lower()
