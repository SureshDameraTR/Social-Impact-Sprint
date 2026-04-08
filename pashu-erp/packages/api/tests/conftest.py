"""Shared fixtures for PashuRaksha API tests."""

import pytest
import httpx

BASE_URL = "http://localhost:8000"

FARMER_PHONE = "+919900000002"  # Seeded farmer: Lakshmi
ADMIN_PHONE = "+919900000001"   # Seeded admin: Deepak
MOCK_OTP = "123456"


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def farmer_token() -> str:
    """Authenticate as the seeded farmer and return a JWT."""
    r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
        "phone": FARMER_PHONE, "otp": MOCK_OTP,
    })
    assert r.status_code == 200, f"Farmer auth failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def admin_token() -> str:
    """Authenticate as the seeded admin and return a JWT."""
    r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
        "phone": ADMIN_PHONE, "otp": MOCK_OTP,
    })
    assert r.status_code == 200, f"Admin auth failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def farmer_user_id() -> str:
    """Return the seeded farmer's user_id."""
    r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
        "phone": FARMER_PHONE, "otp": MOCK_OTP,
    })
    assert r.status_code == 200
    return r.json()["user_id"]


def auth_header(token: str) -> dict:
    """Build an Authorization header from a token."""
    return {"Authorization": f"Bearer {token}"}
