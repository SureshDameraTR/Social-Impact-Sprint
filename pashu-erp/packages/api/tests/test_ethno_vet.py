"""Unit tests for Ethno-Veterinary endpoints — /v1/ethno-vet."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


def _mock_remedy() -> MagicMock:
    remedy = MagicMock()
    remedy.id = uuid.uuid4()
    remedy.name_en = "Turmeric Paste"
    remedy.name_kn = None
    remedy.plant_ingredient = "Turmeric"
    remedy.preparation_method = "Mix with mustard oil"
    remedy.administration = "Topical"
    remedy.conditions_treated = ["wound", "inflammation"]
    remedy.dosage_by_species = {"cattle": "50g", "goat": "20g"}
    remedy.scientific_evidence = "Anti-inflammatory properties documented"
    remedy.caution = "Avoid on open wounds"
    remedy.evidence_rating = "traditional"
    remedy.safety_warnings = "Avoid on open wounds"
    remedy.source_reference = "ICAR Traditional Medicine Handbook"
    remedy.created_at = datetime.now(timezone.utc)
    return remedy


# ---------------------------------------------------------------------------
# GET /v1/ethno-vet/remedies
# ---------------------------------------------------------------------------


class TestListRemedies:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/ethno-vet/remedies")
        assert resp.status_code == 200

    async def test_list_with_species_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with species filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/ethno-vet/remedies?species=cattle")
        assert resp.status_code == 200

    async def test_list_with_condition_filter(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with condition filter returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/ethno-vet/remedies?condition=wound")
        assert resp.status_code == 200

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/ethno-vet/remedies")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/ethno-vet/remedies/{id}
# ---------------------------------------------------------------------------


class TestGetRemedy:
    async def test_get_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 for existing remedy."""
        remedy = _mock_remedy()
        result = MagicMock()
        result.scalar_one_or_none.return_value = remedy
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/ethno-vet/remedies/{remedy.id}")
        assert resp.status_code == 200

    async def test_get_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent ID returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(f"/v1/ethno-vet/remedies/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /v1/ethno-vet/search
# ---------------------------------------------------------------------------


class TestSearchRemedies:
    async def test_search_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with valid query returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/ethno-vet/search?q=turmeric")
        assert resp.status_code == 200

    async def test_search_too_short_query(self, client: AsyncClient) -> None:
        """GET with query shorter than 2 chars returns 422."""
        resp = await client.get("/v1/ethno-vet/search?q=a")
        assert resp.status_code == 422

    async def test_search_missing_query(self, client: AsyncClient) -> None:
        """GET without q param returns 422."""
        resp = await client.get("/v1/ethno-vet/search")
        assert resp.status_code == 422
