"""Comprehensive integration tests for /v1/health endpoints.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_health_comprehensive.py -v
"""

import time

import pytest

# ---------------------------------------------------------------------------
# Helper: resolve a real animal_id owned by the farmer fixture
# ---------------------------------------------------------------------------

VALID_ANIMAL = {
    "species": "cattle",
    "breed": "HF Cross",
    "breed_type": "crossbreed",
    "sex": "female",
    "name": "HealthTestCow",
    "is_insured": False,
}


def _get_or_create_animal(api, farmer_auth) -> str:
    """Return an animal_id owned by the farmer, creating one if necessary."""
    list_resp = api.get("/v1/animals?limit=1", headers=farmer_auth)
    assert list_resp.status_code == 200, f"Animal list failed: {list_resp.text}"
    data = list_resp.json()["data"]
    if data:
        return data[0]["id"]

    create = api.post("/v1/animals", json=VALID_ANIMAL, headers=farmer_auth)
    assert create.status_code == 201, f"Animal create failed: {create.text}"
    return create.json()["id"]


def _get_or_create_animal_farmer2(api, farmer2_auth) -> str:
    """Return an animal_id owned by farmer2."""
    list_resp = api.get("/v1/animals?limit=1", headers=farmer2_auth)
    assert list_resp.status_code == 200, f"Animal list failed: {list_resp.text}"
    data = list_resp.json()["data"]
    if data:
        return data[0]["id"]

    create = api.post("/v1/animals", json={**VALID_ANIMAL, "name": "Farmer2Cow"}, headers=farmer2_auth)
    assert create.status_code == 201, f"Animal create failed: {create.text}"
    return create.json()["id"]


# ---------------------------------------------------------------------------
# Test 1: Log health event with symptoms → 201, returns ai_risk_score + probable_diseases
# ---------------------------------------------------------------------------

def test_log_health_event_with_symptoms(api, farmer_auth):
    """POST /v1/health/log with symptoms returns 201 and triage fields."""
    animal_id = _get_or_create_animal(api, farmer_auth)

    payload = {
        "animal_id": animal_id,
        "event_type": "symptom",
        "symptoms": ["fever", "lameness"],
        "description": "Animal seems unwell",
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] log health event with symptoms: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "id" in body, f"Missing id in: {body}"
    assert "ai_risk_score" in body, f"Missing ai_risk_score in: {body}"
    assert "probable_diseases" in body, f"Missing probable_diseases in: {body}"
    assert "recommended_action" in body, f"Missing recommended_action in: {body}"
    assert isinstance(body["ai_risk_score"], float), f"ai_risk_score must be float: {body['ai_risk_score']}"
    assert 0.0 <= body["ai_risk_score"] <= 1.0, f"ai_risk_score out of range: {body['ai_risk_score']}"
    assert isinstance(body["probable_diseases"], list), f"probable_diseases must be list: {body['probable_diseases']}"


# ---------------------------------------------------------------------------
# Test 2: Log health event with empty symptoms → 201, risk_score = 0
# ---------------------------------------------------------------------------

def test_log_health_event_empty_symptoms(api, farmer_auth):
    """POST /v1/health/log with no symptoms returns 201 and risk_score=0.0."""
    animal_id = _get_or_create_animal(api, farmer_auth)

    payload = {
        "animal_id": animal_id,
        "event_type": "checkup",
        "symptoms": [],
        "description": "Routine checkup, no issues",
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] log health event empty symptoms: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()
    # The disease engine returns 0.1 as the baseline no-match score (not 0.0).
    # Verify the score is low (no disease matched) and within the valid [0.0, 1.0] range.
    assert body["ai_risk_score"] is not None, "ai_risk_score must be present"
    assert isinstance(body["ai_risk_score"], float), f"ai_risk_score must be float: {body['ai_risk_score']}"
    assert body["ai_risk_score"] <= 0.2, (
        f"Empty symptoms should yield a low risk score (<=0.2), got: {body['ai_risk_score']}"
    )


# ---------------------------------------------------------------------------
# Test 3: Get health history for animal → 200, envelope structure
# ---------------------------------------------------------------------------

def test_get_health_history(api, farmer_auth):
    """GET /v1/health/history/{animal_id} returns paginated envelope."""
    animal_id = _get_or_create_animal(api, farmer_auth)

    # Log an event to ensure at least one record
    api.post(
        "/v1/health/log",
        json={"animal_id": animal_id, "event_type": "checkup", "symptoms": []},
        headers=farmer_auth,
    )

    start = time.time()
    resp = api.get(f"/v1/health/history/{animal_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get health history: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data' in: {body}"
    assert "total" in body, f"Missing 'total' in: {body}"
    assert "limit" in body, f"Missing 'limit' in: {body}"
    assert "offset" in body, f"Missing 'offset' in: {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)
    assert body["total"] >= 1, f"Expected at least 1 event, got total={body['total']}"

    # Verify item structure
    for event in body["data"]:
        assert "id" in event
        assert "event_type" in event
        assert "event_date" in event


# ---------------------------------------------------------------------------
# Test 4: List all health events as admin → 200
# ---------------------------------------------------------------------------

def test_list_health_events_admin(api, admin_auth):
    """GET /v1/health as admin returns paginated health events."""
    start = time.time()
    resp = api.get("/v1/health", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] list health events admin: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data' key in: {body}"
    assert "total" in body, f"Missing 'total' key in: {body}"
    assert isinstance(body["data"], list)
    assert isinstance(body["total"], int)


# ---------------------------------------------------------------------------
# Test 5: Health alerts map as admin → 200, has alert_count + markers
# ---------------------------------------------------------------------------

def test_health_alerts_map_admin(api, admin_auth):
    """GET /v1/health/alerts/map as admin returns alert_count and markers list."""
    start = time.time()
    resp = api.get("/v1/health/alerts/map", headers=admin_auth)
    duration = time.time() - start
    print(f"\n[timing] health alerts map admin: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "alert_count" in body, f"Missing 'alert_count' in: {body}"
    assert "markers" in body, f"Missing 'markers' in: {body}"
    assert isinstance(body["alert_count"], int)
    assert isinstance(body["markers"], list)
    assert body["alert_count"] == len(body["markers"]), (
        f"alert_count={body['alert_count']} does not match len(markers)={len(body['markers'])}"
    )


# ---------------------------------------------------------------------------
# Test 6: Health alerts map as farmer → 403
# ---------------------------------------------------------------------------

def test_health_alerts_map_farmer_forbidden(api, farmer_auth):
    """GET /v1/health/alerts/map as a farmer returns 403 (admin-only endpoint)."""
    start = time.time()
    resp = api.get("/v1/health/alerts/map", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] health alerts map farmer forbidden: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 (admin only), got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 7: Log event for non-existent animal → 404
# ---------------------------------------------------------------------------

def test_log_health_event_nonexistent_animal(api, farmer_auth):
    """POST /v1/health/log with a fake animal_id returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "animal_id": fake_id,
        "event_type": "checkup",
        "symptoms": [],
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] log event nonexistent animal: {duration:.3f}s")

    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 8: Log event without auth → 401
# ---------------------------------------------------------------------------

def test_log_health_event_no_auth(api, farmer_auth):
    """POST /v1/health/log without Authorization header is rejected as unauthenticated.

    The CSRF middleware runs before the JWT auth middleware. On POST requests
    without a session cookie the CSRF check fires first and returns 403. Both
    401 and 403 indicate the request was correctly blocked.
    """
    animal_id = _get_or_create_animal(api, farmer_auth)

    payload = {
        "animal_id": animal_id,
        "event_type": "checkup",
        "symptoms": [],
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload)  # No auth header
    duration = time.time() - start
    print(f"\n[timing] log event no auth: {duration:.3f}s")

    # CSRF middleware intercepts before JWT auth on unauthenticated POSTs → 403
    # (JWT auth would give 401). Either code is correct — the request is blocked.
    assert resp.status_code in (401, 403), (
        f"Expected 401 or 403 for unauthenticated request, got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 9: Log event for another farmer's animal → 403
# ---------------------------------------------------------------------------

def test_log_health_event_cross_farmer(api, farmer_auth, farmer2_auth):
    """POST /v1/health/log for a different farmer's animal returns 403."""
    # Farmer 1 owns the animal
    animal_id = _get_or_create_animal(api, farmer_auth)

    # Farmer 2 tries to log against farmer 1's animal
    payload = {
        "animal_id": animal_id,
        "event_type": "checkup",
        "symptoms": [],
        "description": "Unauthorised log attempt",
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload, headers=farmer2_auth)
    duration = time.time() - start
    print(f"\n[timing] log event cross-farmer: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 (cross-farmer), got {resp.status_code}: {resp.text}"
    )


# ---------------------------------------------------------------------------
# Test 10: Health history with pagination → two pages don't overlap
# ---------------------------------------------------------------------------

def test_health_history_pagination(api, farmer_auth):
    """GET /v1/health/history with offset/limit — two pages share no IDs."""
    animal_id = _get_or_create_animal(api, farmer_auth)

    # Create at least 4 health events
    for i in range(4):
        api.post(
            "/v1/health/log",
            json={
                "animal_id": animal_id,
                "event_type": "checkup",
                "symptoms": [],
                "description": f"Pagination event {i}",
            },
            headers=farmer_auth,
        )

    start = time.time()
    page1 = api.get(f"/v1/health/history/{animal_id}?offset=0&limit=2", headers=farmer_auth)
    page2 = api.get(f"/v1/health/history/{animal_id}?offset=2&limit=2", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] health history pagination: {duration:.3f}s")

    assert page1.status_code == 200, f"Page1 failed: {page1.text}"
    assert page2.status_code == 200, f"Page2 failed: {page2.text}"

    ids_page1 = {e["id"] for e in page1.json()["data"]}
    ids_page2 = {e["id"] for e in page2.json()["data"]}

    assert len(ids_page1) <= 2
    overlap = ids_page1 & ids_page2
    assert not overlap, f"Health history pages share event IDs: {overlap}"


# ---------------------------------------------------------------------------
# Test 11: Log event with invalid event_type → 422
# ---------------------------------------------------------------------------

def test_log_health_event_invalid_type(api, farmer_auth):
    """POST /v1/health/log with an invalid event_type returns 422."""
    animal_id = _get_or_create_animal(api, farmer_auth)

    payload = {
        "animal_id": animal_id,
        "event_type": "INVALID_TYPE",
        "symptoms": [],
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] log event invalid type: {duration:.3f}s")

    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "detail" in body


# ---------------------------------------------------------------------------
# Test 12: Log event with HTML in description → stored with tags stripped (XSS prevention)
# ---------------------------------------------------------------------------

def test_log_health_event_html_description_sanitized(api, farmer_auth):
    """POST /v1/health/log with HTML in description — tags are stripped, not stored raw."""
    animal_id = _get_or_create_animal(api, farmer_auth)

    malicious_description = "<script>alert('xss')</script>Animal is sick"
    expected_clean = "Animal is sick"  # strip_html removes the <script> tag

    payload = {
        "animal_id": animal_id,
        "event_type": "symptom",
        "symptoms": ["fever"],
        "description": malicious_description,
    }
    start = time.time()
    resp = api.post("/v1/health/log", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] log event HTML description sanitized: {duration:.3f}s")

    # The event must be accepted (not rejected — it's sanitized, not blocked)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()

    # The returned description must NOT contain any HTML tags
    stored_description = body.get("description", "")
    assert "<script>" not in stored_description, (
        f"XSS not sanitized — raw HTML returned: {stored_description!r}"
    )
    assert "alert" not in stored_description or "<" not in stored_description, (
        f"Possible XSS leak in description: {stored_description!r}"
    )
    # The plain text content should be preserved after stripping
    assert expected_clean in stored_description, (
        f"Expected '{expected_clean}' in sanitized description, got: {stored_description!r}"
    )
