"""Integration tests for animal CRUD operations against real PostgreSQL."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration

FARMER_PHONE = "+919876599901"


@pytest.fixture
def _patch_otp(monkeypatch: pytest.MonkeyPatch):
    """Patch the OTP generator to always return '123456'."""
    import app.routers.auth as auth_module

    monkeypatch.setattr(auth_module, "_generate_otp", lambda: "123456")


async def _create_farmer_token(client: AsyncClient, phone: str = FARMER_PHONE) -> str:
    """Helper: create a farmer via OTP flow and return an access token."""
    await client.post("/v1/auth/request-otp", json={"phone": phone})
    resp = await client.post(
        "/v1/auth/verify-otp",
        json={"phone": phone, "otp": "123456", "client_type": "mobile"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


SAMPLE_ANIMAL = {
    "species": "cattle",
    "breed": "Hallikar",
    "breed_type": "indigenous",
    "sex": "female",
    "name": "Lakshmi",
    "is_insured": False,
}


@pytest.mark.usefixtures("_patch_otp")
class TestAnimalCRUD:
    """Full animal lifecycle: create -> list -> get -> update -> delete."""

    async def test_create_animal(self, integration_client: AsyncClient):
        token = await _create_farmer_token(integration_client, "+919876599902")
        resp = await integration_client.post(
            "/v1/animals", json=SAMPLE_ANIMAL, headers=_auth(token)
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["species"] == "cattle"
        assert body["breed"] == "Hallikar"
        assert body["name"] == "Lakshmi"
        assert body["id"]
        assert body["pashu_aadhaar_id"]

    async def test_list_animals_pagination(self, integration_client: AsyncClient):
        token = await _create_farmer_token(integration_client, "+919876599903")

        # Create two animals
        for name in ("Ganga", "Yamuna"):
            animal = {**SAMPLE_ANIMAL, "name": name}
            resp = await integration_client.post(
                "/v1/animals", json=animal, headers=_auth(token)
            )
            assert resp.status_code == 201

        # List with pagination
        resp = await integration_client.get(
            "/v1/animals?limit=10&offset=0", headers=_auth(token)
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert "total" in body
        assert body["total"] >= 2
        assert len(body["data"]) >= 2

    async def test_get_single_animal(self, integration_client: AsyncClient):
        token = await _create_farmer_token(integration_client, "+919876599904")

        create_resp = await integration_client.post(
            "/v1/animals", json=SAMPLE_ANIMAL, headers=_auth(token)
        )
        animal_id = create_resp.json()["id"]

        resp = await integration_client.get(
            f"/v1/animals/{animal_id}", headers=_auth(token)
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == animal_id

    async def test_update_animal(self, integration_client: AsyncClient):
        token = await _create_farmer_token(integration_client, "+919876599905")

        create_resp = await integration_client.post(
            "/v1/animals", json=SAMPLE_ANIMAL, headers=_auth(token)
        )
        animal_id = create_resp.json()["id"]

        resp = await integration_client.patch(
            f"/v1/animals/{animal_id}",
            json={"name": "Nandi", "is_insured": True},
            headers=_auth(token),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Nandi"
        assert body["is_insured"] is True

    async def test_soft_delete_animal(self, integration_client: AsyncClient):
        token = await _create_farmer_token(integration_client, "+919876599906")

        create_resp = await integration_client.post(
            "/v1/animals", json=SAMPLE_ANIMAL, headers=_auth(token)
        )
        animal_id = create_resp.json()["id"]

        # Delete (soft)
        del_resp = await integration_client.delete(
            f"/v1/animals/{animal_id}", headers=_auth(token)
        )
        assert del_resp.status_code == 204

        # GET should return 404
        get_resp = await integration_client.get(
            f"/v1/animals/{animal_id}", headers=_auth(token)
        )
        assert get_resp.status_code == 404

    async def test_deleted_animal_excluded_from_list(
        self, integration_client: AsyncClient
    ):
        token = await _create_farmer_token(integration_client, "+919876599907")

        # Create an animal
        create_resp = await integration_client.post(
            "/v1/animals", json=SAMPLE_ANIMAL, headers=_auth(token)
        )
        animal_id = create_resp.json()["id"]

        # Delete it
        await integration_client.delete(
            f"/v1/animals/{animal_id}", headers=_auth(token)
        )

        # List should not include the deleted animal
        list_resp = await integration_client.get(
            "/v1/animals", headers=_auth(token)
        )
        assert list_resp.status_code == 200
        ids = [a["id"] for a in list_resp.json()["data"]]
        assert animal_id not in ids

    async def test_species_filter(self, integration_client: AsyncClient):
        token = await _create_farmer_token(integration_client, "+919876599908")

        # Create cattle and goat
        await integration_client.post(
            "/v1/animals", json=SAMPLE_ANIMAL, headers=_auth(token)
        )
        goat = {**SAMPLE_ANIMAL, "name": "Meena", "species": "goat", "breed": "Osmanabadi"}
        await integration_client.post(
            "/v1/animals", json=goat, headers=_auth(token)
        )

        # Filter by goat
        resp = await integration_client.get(
            "/v1/animals?species=goat", headers=_auth(token)
        )
        assert resp.status_code == 200
        for animal in resp.json()["data"]:
            assert animal["species"] == "goat"
