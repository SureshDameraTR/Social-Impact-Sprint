"""Shared fixtures for PashuRaksha API tests.

Tests run against a live local API (environment=development).
The console OTP provider logs OTPs to stdout — tests extract them
by calling request-otp then verify-otp with the known dev OTP.
"""

import os

import httpx
import pytest

BASE_URL = "http://localhost:8000"

FARMER_PHONE = "+919900000002"
ADMIN_PHONE = "+919900000001"


def _get_token(phone: str) -> str:
    """Request OTP then verify to get a JWT.

    In dev mode, the OTP is logged to console. For automated tests,
    set TEST_OTP env var with the OTP value after requesting it.
    """
    r = httpx.post(f"{BASE_URL}/v1/auth/request-otp", json={"phone": phone})
    assert r.status_code == 200, f"OTP request failed: {r.text}"

    test_otp = os.environ.get("TEST_OTP", "")
    if not test_otp:
        pytest.skip("TEST_OTP env var required for auth tests")

    r = httpx.post(
        f"{BASE_URL}/v1/auth/verify-otp",
        json={"phone": phone, "otp": test_otp, "client_type": "mobile"},
    )
    assert r.status_code == 200, f"Auth failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def farmer_token() -> str:
    return _get_token(FARMER_PHONE)


@pytest.fixture(scope="session")
def admin_token() -> str:
    return _get_token(ADMIN_PHONE)


@pytest.fixture(scope="session")
def farmer_user_id(farmer_token: str) -> str:
    r = httpx.get(
        f"{BASE_URL}/v1/auth/me",
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert r.status_code == 200
    return r.json()["user_id"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
