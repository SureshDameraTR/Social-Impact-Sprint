"""Comprehensive integration tests for /v1/onboarding/complete endpoint.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
NOTE: This test mutates the user's preferences/district/lang_pref.
      farmer2 (+919900000003) is used as the primary subject to avoid
      interfering with tests that depend on farmer (+919900000002) state.
Run: pytest tests/comprehensive/test_onboarding_comprehensive.py -v
"""

import time

import pytest


VALID_ONBOARDING_PAYLOAD = {
    "preferred_language": "kn",
    "district": "Mandya",
    "village_code": "KA-MYS-001",
    "primary_species": ["cattle", "buffalo"],
    "herd_size": 5,
    "has_milk_center_access": True,
    "shg_member": False,
}


# ---------------------------------------------------------------------------
# Test 1: POST /v1/onboarding/complete — happy path returns expected shape
# ---------------------------------------------------------------------------

def test_onboarding_complete_happy_path(api, farmer2_auth):
    """POST /v1/onboarding/complete with valid payload returns completion response."""
    start = time.time()
    resp = api.post(
        "/v1/onboarding/complete",
        json=VALID_ONBOARDING_PAYLOAD,
        headers=farmer2_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] POST /v1/onboarding/complete: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()

    assert "user_id" in body, f"Missing 'user_id': {body}"
    assert "onboarding_complete" in body, f"Missing 'onboarding_complete': {body}"
    assert "preferences" in body, f"Missing 'preferences': {body}"
    assert "message" in body, f"Missing 'message': {body}"
    assert "next_steps" in body, f"Missing 'next_steps': {body}"

    assert body["onboarding_complete"] is True
    assert isinstance(body["next_steps"], list)
    assert len(body["next_steps"]) > 0, "next_steps should not be empty"


# ---------------------------------------------------------------------------
# Test 2: POST /v1/onboarding/complete — preferences are persisted correctly
# ---------------------------------------------------------------------------

def test_onboarding_preferences_persisted(api, farmer2_auth):
    """Preferences returned in response match those submitted."""
    payload = {
        "preferred_language": "hi",
        "district": "Bengaluru Urban",
        "village_code": "KA-BLR-042",
        "primary_species": ["goat"],
        "herd_size": 12,
        "has_milk_center_access": False,
        "shg_member": True,
    }
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    prefs = resp.json()["preferences"]

    assert prefs["preferred_language"] == payload["preferred_language"]
    assert prefs["district"] == payload["district"]
    assert prefs["village_code"] == payload["village_code"]
    assert prefs["primary_species"] == payload["primary_species"]
    assert prefs["herd_size"] == payload["herd_size"]
    assert prefs["has_milk_center_access"] == payload["has_milk_center_access"]
    assert prefs["shg_member"] == payload["shg_member"]
    assert prefs["onboarding_complete"] is True


# ---------------------------------------------------------------------------
# Test 3: POST /v1/onboarding/complete — 401 without auth
# ---------------------------------------------------------------------------

def test_onboarding_unauthenticated_401(api):
    """POST /v1/onboarding/complete without auth returns 401."""
    resp = api.post("/v1/onboarding/complete", json=VALID_ONBOARDING_PAYLOAD)
    assert resp.status_code in (401, 403), (
        f"Expected 401/403 without auth, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 4: POST /v1/onboarding/complete — 422 for missing required 'district'
# ---------------------------------------------------------------------------

def test_onboarding_missing_district_422(api, farmer2_auth):
    """POST /v1/onboarding/complete without 'district' (required) returns 422."""
    payload = {k: v for k, v in VALID_ONBOARDING_PAYLOAD.items() if k != "district"}
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for missing district, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 5: POST /v1/onboarding/complete — 422 for district too long (>100 chars)
# ---------------------------------------------------------------------------

def test_onboarding_district_too_long_422(api, farmer2_auth):
    """POST /v1/onboarding/complete with district > 100 chars returns 422."""
    payload = {**VALID_ONBOARDING_PAYLOAD, "district": "A" * 101}
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for district > 100 chars, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 6: POST /v1/onboarding/complete — 422 for negative herd_size
# ---------------------------------------------------------------------------

def test_onboarding_negative_herd_size_422(api, farmer2_auth):
    """POST /v1/onboarding/complete with herd_size < 0 returns 422."""
    payload = {**VALID_ONBOARDING_PAYLOAD, "herd_size": -1}
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for negative herd_size, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: POST /v1/onboarding/complete — village_code is optional (null OK)
# ---------------------------------------------------------------------------

def test_onboarding_village_code_optional(api, farmer2_auth):
    """POST /v1/onboarding/complete without village_code succeeds."""
    payload = {k: v for k, v in VALID_ONBOARDING_PAYLOAD.items() if k != "village_code"}
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 200, (
        f"Expected 200 without village_code, got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert body["onboarding_complete"] is True


# ---------------------------------------------------------------------------
# Test 8: POST /v1/onboarding/complete — empty primary_species is accepted
# ---------------------------------------------------------------------------

def test_onboarding_empty_species_list_accepted(api, farmer2_auth):
    """POST /v1/onboarding/complete with empty primary_species list is valid."""
    payload = {**VALID_ONBOARDING_PAYLOAD, "primary_species": []}
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 200, (
        f"Expected 200 for empty primary_species, got {resp.status_code}: {resp.text}"
    )
    prefs = resp.json()["preferences"]
    assert prefs["primary_species"] == []


# ---------------------------------------------------------------------------
# Test 9: POST /v1/onboarding/complete — Kannada district name (Unicode)
# ---------------------------------------------------------------------------

def test_onboarding_kannada_district_name(api, farmer2_auth):
    """POST /v1/onboarding/complete with Kannada Unicode district name is accepted."""
    payload = {**VALID_ONBOARDING_PAYLOAD, "district": "ಮಂಡ್ಯ"}  # Kannada: Mandya
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 200, (
        f"Expected 200 for Kannada district name, got {resp.status_code}: {resp.text}"
    )
    assert resp.json()["preferences"]["district"] == "ಮಂಡ್ಯ"


# ---------------------------------------------------------------------------
# Test 10: POST /v1/onboarding/complete — idempotent (can be called multiple times)
# ---------------------------------------------------------------------------

def test_onboarding_idempotent_second_call(api, farmer2_auth):
    """POST /v1/onboarding/complete can be called twice and overwrites preferences."""
    payload_v1 = {**VALID_ONBOARDING_PAYLOAD, "district": "Mysuru", "herd_size": 3}
    resp1 = api.post("/v1/onboarding/complete", json=payload_v1, headers=farmer2_auth)
    assert resp1.status_code == 200, f"First call failed: {resp1.text}"

    payload_v2 = {**VALID_ONBOARDING_PAYLOAD, "district": "Hassan", "herd_size": 7}
    resp2 = api.post("/v1/onboarding/complete", json=payload_v2, headers=farmer2_auth)
    assert resp2.status_code == 200, f"Second call failed: {resp2.text}"

    prefs = resp2.json()["preferences"]
    assert prefs["district"] == "Hassan", f"Second call did not overwrite district: {prefs}"
    assert prefs["herd_size"] == 7, f"Second call did not overwrite herd_size: {prefs}"


# ---------------------------------------------------------------------------
# Test 11: POST /v1/onboarding/complete — user_id in response matches token user
# ---------------------------------------------------------------------------

def test_onboarding_user_id_matches_profile(api, farmer2_auth):
    """user_id in onboarding response matches the authenticated user's profile ID."""
    # Get profile first
    profile_resp = api.get("/v1/users/profile", headers=farmer2_auth)
    assert profile_resp.status_code == 200, f"Profile fetch failed: {profile_resp.text}"
    profile_id = profile_resp.json()["id"]

    resp = api.post(
        "/v1/onboarding/complete",
        json=VALID_ONBOARDING_PAYLOAD,
        headers=farmer2_auth,
    )
    assert resp.status_code == 200, f"Onboarding failed: {resp.text}"
    assert resp.json()["user_id"] == str(profile_id), (
        f"user_id mismatch: {resp.json()['user_id']} != {profile_id}"
    )


# ---------------------------------------------------------------------------
# Test 12: POST /v1/onboarding/complete — 422 for village_code too long
# ---------------------------------------------------------------------------

def test_onboarding_village_code_too_long_422(api, farmer2_auth):
    """POST /v1/onboarding/complete with village_code > 20 chars returns 422."""
    payload = {**VALID_ONBOARDING_PAYLOAD, "village_code": "X" * 21}
    resp = api.post("/v1/onboarding/complete", json=payload, headers=farmer2_auth)
    assert resp.status_code == 422, (
        f"Expected 422 for village_code > 20 chars, got {resp.status_code}: {resp.text}"
    )
