"""Shared fixtures for comprehensive API integration tests.

These tests hit the REAL running API at localhost:8000 with a REAL database.
The API must be running via docker compose before executing these tests.

Auth flow:
  1. Reset OTP rate limits in the database
  2. POST /v1/auth/request-otp  → triggers OTP generation
  3. Read OTP from docker logs  → console provider prints to stderr
  4. POST /v1/auth/verify-otp   → returns access_token
"""

import re
import subprocess
import time

import httpx
import pytest

API_BASE = "http://localhost:8000"

# Test accounts from seed data
ACCOUNTS = {
    "admin": "+919900000001",
    "farmer": "+919900000002",
    "farmer2": "+919900000003",
    "farmer3": "+919900000004",
    "vet": "+919900000005",
}


def _reset_otp_rate_limits():
    """Reset OTP request counts in DB so rate limits don't block tests."""
    subprocess.run(
        [
            "docker", "exec", "pashu-erp-db-1",
            "psql", "-U", "pashu", "-d", "pashuraksha", "-c",
            "UPDATE otp_requests SET request_count = 0, attempts = 0;",
        ],
        capture_output=True,
        timeout=10,
    )
    # Also reset the in-memory slowapi rate limiter by restarting nothing —
    # slowapi tracks by IP in memory. We space out requests instead.


def _extract_otp_from_logs(phone: str) -> str:
    """Read the most recent OTP for a specific phone from docker logs."""
    result = subprocess.run(
        ["docker", "logs", "pashu-erp-api-1", "--tail", "30"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    combined = result.stdout + result.stderr
    # Find OTP blocks for this specific phone
    pattern = rf"DEV OTP for {re.escape(phone)}.*?Code:\s*(\d{{6}})"
    matches = re.findall(pattern, combined, re.DOTALL)
    if not matches:
        # Fallback: just get the last OTP code
        matches = re.findall(r"Code:\s*(\d{6})", combined)
    if not matches:
        raise RuntimeError(
            f"Could not find OTP in docker logs for {phone}. "
            f"Last 300 chars:\n{combined[-300:]}"
        )
    return matches[-1]


def _get_token(phone: str, client_type: str = "mobile", max_retries: int = 5) -> dict:
    """Complete the OTP auth flow with retry for rate limits."""
    with httpx.Client(base_url=API_BASE, timeout=30) as client:
        for attempt in range(max_retries):
            # Step 1: Request OTP
            resp = client.post("/v1/auth/request-otp", json={"phone": phone})
            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    # Wait for slowapi per-minute limit to reset (61s > 1 min window)
                    time.sleep(61)
                    continue
                raise RuntimeError(
                    f"OTP rate limit exhausted after {max_retries} retries for {phone}"
                )
            assert resp.status_code == 200, f"OTP request failed ({resp.status_code}): {resp.text}"

            # Small delay to ensure logs are flushed
            time.sleep(0.5)

            # Step 2: Extract OTP from docker logs
            otp = _extract_otp_from_logs(phone)

            # Step 3: Verify OTP
            resp = client.post(
                "/v1/auth/verify-otp",
                json={"phone": phone, "otp": otp, "client_type": client_type},
            )
            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(15)
                    continue
                raise RuntimeError(f"Verify rate limit exhausted for {phone}")
            assert resp.status_code == 200, f"OTP verify failed ({resp.status_code}): {resp.text}"
            return resp.json()

    raise RuntimeError(f"Failed to get token for {phone}")


# Cache tokens at module level so they survive across all test files
_token_cache: dict[str, str] = {}
_auth_cache: dict[str, dict] = {}


def _ensure_tokens():
    """Initialize all tokens once, with rate limit reset and spacing."""
    if _token_cache:
        return

    # Reset DB-level OTP rate limits before getting tokens
    _reset_otp_rate_limits()

    # Get tokens one at a time with spacing to avoid slowapi per-minute limit
    for role, phone in [
        ("admin", ACCOUNTS["admin"]),
        ("farmer", ACCOUNTS["farmer"]),
        ("farmer2", ACCOUNTS["farmer2"]),
        ("vet", ACCOUNTS["vet"]),
    ]:
        data = _get_token(phone)
        _token_cache[role] = data["access_token"]
        _auth_cache[role] = {"Authorization": f"Bearer {data['access_token']}"}
        time.sleep(1)  # Space requests to stay within 5/min limit


@pytest.fixture(scope="session")
def admin_token() -> str:
    _ensure_tokens()
    return _token_cache["admin"]


@pytest.fixture(scope="session")
def farmer_token() -> str:
    _ensure_tokens()
    return _token_cache["farmer"]


@pytest.fixture(scope="session")
def farmer2_token() -> str:
    _ensure_tokens()
    return _token_cache["farmer2"]


@pytest.fixture(scope="session")
def vet_token() -> str:
    _ensure_tokens()
    return _token_cache["vet"]


@pytest.fixture(scope="session")
def admin_auth(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def farmer_auth(farmer_token) -> dict:
    return {"Authorization": f"Bearer {farmer_token}"}


@pytest.fixture(scope="session")
def farmer2_auth(farmer2_token) -> dict:
    return {"Authorization": f"Bearer {farmer2_token}"}


@pytest.fixture(scope="session")
def vet_auth(vet_token) -> dict:
    return {"Authorization": f"Bearer {vet_token}"}


@pytest.fixture(scope="session")
def api() -> httpx.Client:
    """Reusable httpx client pointed at the API."""
    with httpx.Client(base_url=API_BASE, timeout=30) as client:
        yield client


# ---------------------------------------------------------------------------
# Utility: check API is reachable, skip all tests if not
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Skip all comprehensive tests if API is not reachable."""
    try:
        resp = httpx.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code != 200:
            pytest.skip("API not healthy", allow_module_level=True)
    except httpx.ConnectError:
        pytest.skip("API not reachable at localhost:8000", allow_module_level=True)
