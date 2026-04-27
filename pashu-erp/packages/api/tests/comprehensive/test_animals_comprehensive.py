"""Comprehensive integration tests for /v1/animals endpoints.

Hits the REAL running API at localhost:8000 with a REAL PostgreSQL database.
Run: pytest tests/comprehensive/test_animals_comprehensive.py -v
"""

import time
import uuid

import pytest

# ---------------------------------------------------------------------------
# Minimal valid AnimalCreate payload for reuse across tests
# ---------------------------------------------------------------------------

VALID_ANIMAL = {
    "species": "cattle",
    "breed": "HF Cross",
    "breed_type": "crossbreed",
    "sex": "female",
    "name": "Test Lakshmi",
    "is_insured": False,
}


# ---------------------------------------------------------------------------
# Test 1: Create animal with valid data → 201, returns id + pashu_aadhaar_id
# ---------------------------------------------------------------------------

def test_create_animal_valid(api, farmer_auth):
    """POST /v1/animals with valid payload returns 201 and expected fields."""
    start = time.time()
    resp = api.post("/v1/animals", json=VALID_ANIMAL, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] create animal valid: {duration:.3f}s")

    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "id" in body, f"Missing id in: {body}"
    assert "pashu_aadhaar_id" in body, f"Missing pashu_aadhaar_id in: {body}"
    assert body["species"] == "cattle"
    assert body["breed"] == "HF Cross"
    assert body["sex"] == "female"
    assert body["breed_type"] == "crossbreed"
    # Clean up — soft delete the created animal
    api.delete(f"/v1/animals/{body['id']}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 2: List animals as farmer → 200, data is array, total >= 1
# ---------------------------------------------------------------------------

def test_list_animals_farmer(api, farmer_auth):
    """GET /v1/animals as farmer returns envelope with data array and total."""
    # Ensure at least one animal exists
    create = api.post("/v1/animals", json=VALID_ANIMAL, headers=farmer_auth)
    assert create.status_code == 201, f"Setup create failed: {create.text}"
    created_id = create.json()["id"]

    start = time.time()
    resp = api.get("/v1/animals", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] list animals farmer: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "data" in body, f"Missing 'data' key in: {body}"
    assert "total" in body, f"Missing 'total' key in: {body}"
    assert "limit" in body, f"Missing 'limit' key in: {body}"
    assert "offset" in body, f"Missing 'offset' key in: {body}"
    assert isinstance(body["data"], list), f"'data' must be a list, got: {type(body['data'])}"
    assert isinstance(body["total"], int), f"'total' must be int, got: {type(body['total'])}"
    assert body["total"] >= 1, f"Expected at least 1 animal, got total={body['total']}"

    # Verify each item has required fields
    for animal in body["data"]:
        assert "id" in animal
        assert "species" in animal
        assert "breed" in animal

    # Cleanup
    api.delete(f"/v1/animals/{created_id}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 3: List animals with species filter → 200, all items match species
# ---------------------------------------------------------------------------

def test_list_animals_species_filter(api, farmer_auth):
    """GET /v1/animals?species=cattle returns only cattle entries."""
    # Ensure a cattle animal exists
    create = api.post("/v1/animals", json=VALID_ANIMAL, headers=farmer_auth)
    assert create.status_code == 201, f"Setup create failed: {create.text}"
    created_id = create.json()["id"]

    start = time.time()
    resp = api.get("/v1/animals?species=cattle", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] list animals species filter: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert isinstance(body["data"], list)
    for animal in body["data"]:
        assert animal["species"] == "cattle", (
            f"Filter broken: expected cattle, got {animal['species']}"
        )

    # Cleanup
    api.delete(f"/v1/animals/{created_id}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 4: Pagination — offset=0,limit=2 vs offset=2,limit=2 have no overlap
# ---------------------------------------------------------------------------

def test_list_animals_pagination_no_overlap(api, farmer_auth):
    """Two pages of results must share no animal IDs."""
    # Create enough animals to fill two pages
    created_ids = []
    for i in range(4):
        payload = {**VALID_ANIMAL, "name": f"PaginationTest {i}"}
        r = api.post("/v1/animals", json=payload, headers=farmer_auth)
        assert r.status_code == 201, f"Setup create {i} failed: {r.text}"
        created_ids.append(r.json()["id"])

    start = time.time()
    page1 = api.get("/v1/animals?offset=0&limit=2", headers=farmer_auth)
    page2 = api.get("/v1/animals?offset=2&limit=2", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] pagination two pages: {duration:.3f}s")

    assert page1.status_code == 200, f"Page1 failed: {page1.text}"
    assert page2.status_code == 200, f"Page2 failed: {page2.text}"

    ids_page1 = {a["id"] for a in page1.json()["data"]}
    ids_page2 = {a["id"] for a in page2.json()["data"]}

    assert len(ids_page1) <= 2, f"Page1 returned {len(ids_page1)} items, expected <= 2"
    assert len(ids_page2) <= 2, f"Page2 returned {len(ids_page2)} items, expected <= 2"
    overlap = ids_page1 & ids_page2
    assert not overlap, f"Pages share IDs (overlap): {overlap}"

    # Cleanup
    for animal_id in created_ids:
        api.delete(f"/v1/animals/{animal_id}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 5: Get single animal by ID → 200, fields match creation
# ---------------------------------------------------------------------------

def test_get_single_animal(api, farmer_auth):
    """GET /v1/animals/{id} returns the exact animal with all fields."""
    create = api.post(
        "/v1/animals",
        json={**VALID_ANIMAL, "name": "SingleGetTest"},
        headers=farmer_auth,
    )
    assert create.status_code == 201, f"Create failed: {create.text}"
    animal_id = create.json()["id"]

    start = time.time()
    resp = api.get(f"/v1/animals/{animal_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get single animal: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["id"] == animal_id
    assert body["species"] == "cattle"
    assert body["name"] == "SingleGetTest"
    assert body["sex"] == "female"
    assert body["breed_type"] == "crossbreed"

    # Cleanup
    api.delete(f"/v1/animals/{animal_id}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 6: Update animal name → 200, name changed in response and re-fetch
# ---------------------------------------------------------------------------

def test_update_animal_name(api, farmer_auth):
    """PATCH /v1/animals/{id} with a new name returns 200 and persists the change."""
    create = api.post(
        "/v1/animals",
        json={**VALID_ANIMAL, "name": "BeforeUpdate"},
        headers=farmer_auth,
    )
    assert create.status_code == 201, f"Create failed: {create.text}"
    animal_id = create.json()["id"]

    start = time.time()
    resp = api.patch(
        f"/v1/animals/{animal_id}",
        json={"name": "AfterUpdate"},
        headers=farmer_auth,
    )
    duration = time.time() - start
    print(f"\n[timing] update animal name: {duration:.3f}s")

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["name"] == "AfterUpdate", f"Name not updated: {body['name']}"

    # Confirm persistence with re-fetch
    refetch = api.get(f"/v1/animals/{animal_id}", headers=farmer_auth)
    assert refetch.status_code == 200
    assert refetch.json()["name"] == "AfterUpdate"

    # Cleanup
    api.delete(f"/v1/animals/{animal_id}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 7: Create animal missing required field (no species) → 422
# ---------------------------------------------------------------------------

def test_create_animal_missing_species(api, farmer_auth):
    """POST /v1/animals without 'species' field returns 422 validation error."""
    payload = {
        "breed": "HF Cross",
        "breed_type": "crossbreed",
        "sex": "female",
    }
    start = time.time()
    resp = api.post("/v1/animals", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] create animal missing species: {duration:.3f}s")

    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "detail" in body


# ---------------------------------------------------------------------------
# Test 8: Create animal with future date_of_birth → 422
# ---------------------------------------------------------------------------

def test_create_animal_future_dob(api, farmer_auth):
    """POST /v1/animals with a future date_of_birth returns 422 validation error."""
    payload = {
        **VALID_ANIMAL,
        "date_of_birth": "2099-01-01",
    }
    start = time.time()
    resp = api.post("/v1/animals", json=payload, headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] create animal future dob: {duration:.3f}s")

    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert "detail" in body


# ---------------------------------------------------------------------------
# Test 9: Get animal with non-existent UUID → 404
# ---------------------------------------------------------------------------

def test_get_animal_not_found(api, farmer_auth):
    """GET /v1/animals/<fake-uuid> returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    start = time.time()
    resp = api.get(f"/v1/animals/{fake_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] get animal not found: {duration:.3f}s")

    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Test 10: Get animal without auth → 401
# ---------------------------------------------------------------------------

def test_get_animal_without_auth(api, farmer_auth):
    """GET /v1/animals without Authorization header returns 401."""
    # Create an animal to have a real ID to attempt accessing
    create = api.post("/v1/animals", json=VALID_ANIMAL, headers=farmer_auth)
    assert create.status_code == 201, f"Create failed: {create.text}"
    animal_id = create.json()["id"]

    start = time.time()
    resp = api.get(f"/v1/animals/{animal_id}")  # No auth header
    duration = time.time() - start
    print(f"\n[timing] get animal no auth: {duration:.3f}s")

    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}: {resp.text}"

    # Cleanup
    api.delete(f"/v1/animals/{animal_id}", headers=farmer_auth)


# ---------------------------------------------------------------------------
# Test 11: Delete animal → 204, then GET returns 404
# ---------------------------------------------------------------------------

def test_delete_animal_then_404(api, farmer_auth):
    """DELETE /v1/animals/{id} returns 204 and subsequent GET returns 404."""
    create = api.post(
        "/v1/animals",
        json={**VALID_ANIMAL, "name": "ToBeDeleted"},
        headers=farmer_auth,
    )
    assert create.status_code == 201, f"Create failed: {create.text}"
    animal_id = create.json()["id"]

    start = time.time()
    del_resp = api.delete(f"/v1/animals/{animal_id}", headers=farmer_auth)
    duration = time.time() - start
    print(f"\n[timing] delete animal: {duration:.3f}s")

    assert del_resp.status_code == 204, f"Expected 204, got {del_resp.status_code}: {del_resp.text}"

    # Verify the animal is now soft-deleted (hidden from GET)
    get_resp = api.get(f"/v1/animals/{animal_id}", headers=farmer_auth)
    assert get_resp.status_code == 404, (
        f"Expected 404 after delete, got {get_resp.status_code}: {get_resp.text}"
    )

    # Also verify not in list
    list_resp = api.get("/v1/animals", headers=farmer_auth)
    assert list_resp.status_code == 200
    ids_in_list = {a["id"] for a in list_resp.json()["data"]}
    assert animal_id not in ids_in_list, f"Soft-deleted animal still appears in list"


# ---------------------------------------------------------------------------
# Test 12: Farmer2 cannot GET farmer1's animal → 403
# ---------------------------------------------------------------------------

def test_farmer2_cannot_access_farmer1_animal(api, farmer_auth, farmer2_auth):
    """Farmer B cannot view Farmer A's animal — returns 403."""
    # Farmer 1 creates an animal
    create = api.post(
        "/v1/animals",
        json={**VALID_ANIMAL, "name": "Farmer1Exclusive"},
        headers=farmer_auth,
    )
    assert create.status_code == 201, f"Create failed: {create.text}"
    animal_id = create.json()["id"]

    # Farmer 2 attempts to GET farmer 1's animal
    start = time.time()
    resp = api.get(f"/v1/animals/{animal_id}", headers=farmer2_auth)
    duration = time.time() - start
    print(f"\n[timing] farmer2 access farmer1 animal: {duration:.3f}s")

    assert resp.status_code == 403, (
        f"Expected 403 (cross-farmer access), got {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert "detail" in body

    # Cleanup (farmer 1 deletes their own animal)
    api.delete(f"/v1/animals/{animal_id}", headers=farmer_auth)
