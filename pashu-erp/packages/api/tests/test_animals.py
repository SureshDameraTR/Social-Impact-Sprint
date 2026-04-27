"""Unit tests for Animal CRUD endpoints — /v1/animals."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_animal(user_id: str = FARMER_USER_ID) -> MagicMock:
    animal = MagicMock()
    animal.id = uuid.uuid4()
    animal.user_id = user_id
    animal.name = "Gauri"
    animal.species = "cattle"
    animal.breed = "Gir"
    animal.breed_type = "indigenous"
    animal.pashu_aadhaar_id = "123456789012"
    animal.tag_id = "TAG001"
    animal.date_of_birth = date(2020, 1, 15)
    animal.sex = "female"
    animal.lactation_number = 2
    animal.body_condition_score = 3.5
    animal.is_insured = False
    animal.metadata_ = {}
    animal.created_at = datetime.now(timezone.utc)
    animal.updated_at = datetime.now(timezone.utc)
    return animal


def _valid_animal_payload() -> dict:
    return {
        "name": "Gauri",
        "species": "cattle",
        "breed": "Gir",
        "breed_type": "indigenous",
        "sex": "female",
    }


# ---------------------------------------------------------------------------
# POST /v1/animals — Create
# ---------------------------------------------------------------------------


class TestCreateAnimal:
    async def test_create_animal_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST with valid data returns 201."""
        resp = await client.post("/v1/animals", json=_valid_animal_payload())
        assert resp.status_code == 201

    async def test_create_animal_missing_species(self, client: AsyncClient) -> None:
        """POST without required 'species' field returns 422."""
        payload = {"breed": "Gir", "breed_type": "indigenous", "sex": "male"}
        resp = await client.post("/v1/animals", json=payload)
        assert resp.status_code == 422

    async def test_create_animal_invalid_species(self, client: AsyncClient) -> None:
        """POST with invalid species enum returns 422."""
        payload = _valid_animal_payload()
        payload["species"] = "elephant"
        resp = await client.post("/v1/animals", json=payload)
        assert resp.status_code == 422

    async def test_create_animal_invalid_breed_type(self, client: AsyncClient) -> None:
        """POST with invalid breed_type enum returns 422."""
        payload = _valid_animal_payload()
        payload["breed_type"] = "alien"
        resp = await client.post("/v1/animals", json=payload)
        assert resp.status_code == 422

    async def test_create_animal_invalid_sex(self, client: AsyncClient) -> None:
        """POST with invalid sex enum returns 422."""
        payload = _valid_animal_payload()
        payload["sex"] = "unknown"
        resp = await client.post("/v1/animals", json=payload)
        assert resp.status_code == 422

    async def test_create_animal_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post("/v1/animals", json=_valid_animal_payload())
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/animals — List
# ---------------------------------------------------------------------------


class TestListAnimals:
    async def test_list_animals_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with paginated data."""
        # Mock count query
        count_result = MagicMock()
        count_result.scalar.return_value = 1

        # Mock data query
        animal = _mock_animal()
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [animal]

        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/animals")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body

    async def test_list_animals_with_species_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with species filter returns 200."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await client.get("/v1/animals?species=cattle")
        assert resp.status_code == 200

    async def test_list_animals_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/animals")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/animals/{id} — Get single
# ---------------------------------------------------------------------------


class TestGetAnimal:
    async def test_get_animal_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET with valid ID returns 200."""
        animal = _mock_animal()
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/animals/{animal.id}")
        assert resp.status_code == 200

    async def test_get_animal_not_found(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET with nonexistent ID returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/animals/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_get_animal_forbidden(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET on another user's animal returns 403."""
        animal = _mock_animal(user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/animals/{animal.id}")
        assert resp.status_code == 403

    async def test_vet_same_district_allowed(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Vet accessing animal owned by farmer in same district returns 200."""
        owner_id = str(uuid.uuid4())
        animal = _mock_animal(user_id=owner_id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        # Mock db.get to return owner with same village_code prefix
        owner = MagicMock()
        owner.village_code = "629002"  # same prefix "62" as vet's "629001"
        mock_db.get = AsyncMock(return_value=owner)

        resp = await client_as_vet.get(f"/v1/animals/{animal.id}")
        assert resp.status_code == 200

    async def test_vet_different_district_forbidden(
        self, client_as_vet: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """Vet accessing animal owned by farmer in different district returns 403."""
        owner_id = str(uuid.uuid4())
        animal = _mock_animal(user_id=owner_id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        # Mock db.get to return owner with different village_code prefix
        owner = MagicMock()
        owner.village_code = "990001"  # different prefix "99" vs vet's "62"
        mock_db.get = AsyncMock(return_value=owner)

        resp = await client_as_vet.get(f"/v1/animals/{animal.id}")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# PATCH /v1/animals/{id} — Update
# ---------------------------------------------------------------------------


class TestUpdateAnimal:
    async def test_update_animal_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """PATCH with valid data returns 200."""
        animal = _mock_animal()
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.patch(
            f"/v1/animals/{animal.id}",
            json={"name": "Gauri Updated"},
        )
        assert resp.status_code == 200

    async def test_update_animal_not_found(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """PATCH on nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.patch(
            f"/v1/animals/{uuid.uuid4()}",
            json={"name": "Test"},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /v1/animals/{id}
# ---------------------------------------------------------------------------


class TestDeleteAnimal:
    async def test_delete_animal_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """DELETE returns 204."""
        animal = _mock_animal()
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.delete(f"/v1/animals/{animal.id}")
        assert resp.status_code == 204

    async def test_delete_animal_not_found(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """DELETE on nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.delete(f"/v1/animals/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_delete_animal_forbidden(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """DELETE on another user's animal returns 403."""
        animal = _mock_animal(user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.delete(f"/v1/animals/{animal.id}")
        assert resp.status_code == 403
