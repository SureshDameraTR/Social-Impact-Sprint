"""Unit tests for Bharat Pashudhan registry endpoints — /v1/registry."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# GET /v1/registry/lookup/{pashu_aadhaar_id}
# ---------------------------------------------------------------------------


class TestLookupAnimal:
    async def test_lookup_success(self, client: AsyncClient) -> None:
        """GET with valid ID returns 200."""
        mock_result = {
            "pashu_aadhaar_id": "123456789012",
            "species": "cattle",
            "breed": "Gir",
            "owner_name": "Lakshmi",
        }
        with patch(
            "app.routers.bharat_pashudhan.lookup_animal",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.get("/v1/registry/lookup/123456789012")
            assert resp.status_code == 200
            body = resp.json()
            assert body["species"] == "cattle"

    async def test_lookup_not_found(self, client: AsyncClient) -> None:
        """GET with nonexistent ID returns 404."""
        with patch(
            "app.routers.bharat_pashudhan.lookup_animal",
            new_callable=AsyncMock,
            return_value=None,
        ):
            resp = await client.get("/v1/registry/lookup/000000000000")
            assert resp.status_code == 404

    async def test_lookup_registry_error(self, client: AsyncClient) -> None:
        """GET when registry is down returns HTTP error."""
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.text = "Service unavailable"
        exc = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_resp
        )
        with patch(
            "app.routers.bharat_pashudhan.lookup_animal",
            new_callable=AsyncMock,
            side_effect=exc,
        ):
            resp = await client.get("/v1/registry/lookup/123456789012")
            assert resp.status_code == 503


# ---------------------------------------------------------------------------
# POST /v1/registry/sync/{animal_id}
# ---------------------------------------------------------------------------


class TestSyncAnimal:
    async def test_sync_success(self, client: AsyncClient) -> None:
        """POST returns 200 with sync result."""
        animal_id = uuid.uuid4()
        with patch(
            "app.routers.bharat_pashudhan.sync_animal",
            new_callable=AsyncMock,
            return_value={"synced": True, "animal_id": str(animal_id)},
        ):
            resp = await client.post(f"/v1/registry/sync/{animal_id}")
            assert resp.status_code == 200

    async def test_sync_registry_error(self, client: AsyncClient) -> None:
        """POST when registry is down returns HTTP error."""
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.text = "unavailable"
        exc = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_resp
        )
        with patch(
            "app.routers.bharat_pashudhan.sync_animal",
            new_callable=AsyncMock,
            side_effect=exc,
        ):
            resp = await client.post(f"/v1/registry/sync/{uuid.uuid4()}")
            assert resp.status_code == 503
