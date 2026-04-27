"""Unit tests for Feed & Nutrition endpoints — /v1/feed."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient


def _mock_ingredient() -> MagicMock:
    ing = MagicMock()
    ing.id = uuid.uuid4()
    ing.name_en = "Wheat bran"
    ing.name_kn = None
    ing.category = "concentrate"
    ing.dm_pct = 88.0
    ing.cp_pct = 15.0
    ing.tdn_pct = 65.0
    ing.cost_per_kg = 12.0
    return ing


# ---------------------------------------------------------------------------
# GET /v1/feed/ingredients
# ---------------------------------------------------------------------------


class TestListIngredients:
    async def test_list_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """GET returns 200 with ingredient list."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/feed/ingredients")
        assert resp.status_code == 200

    async def test_list_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get("/v1/feed/ingredients")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /v1/feed/calculate-ration
# ---------------------------------------------------------------------------


class TestCalculateRation:
    async def test_calculate_success(self, client: AsyncClient) -> None:
        """POST with valid data returns 200."""
        from app.schemas.feed import RationIngredient, RationResult

        mock_result = RationResult(
            ingredients=[
                RationIngredient(name="Green Fodder (Napier)", daily_qty_kg=15.0),
                RationIngredient(name="Concentrate Mix", daily_qty_kg=3.9),
            ],
            total_cost_per_day=131.80,
            protein_balance="Balanced",
            energy_balance="Adequate",
        )
        with patch(
            "app.routers.feed.calculate_ration",
            return_value=mock_result,
        ):
            resp = await client.post(
                "/v1/feed/calculate-ration",
                json={
                    "species": "cattle",
                    "weight_kg": 400,
                    "available_ingredients": [],
                },
            )
            assert resp.status_code == 200

    async def test_calculate_missing_species(self, client: AsyncClient) -> None:
        """POST without required 'species' returns 422."""
        resp = await client.post(
            "/v1/feed/calculate-ration",
            json={"weight_kg": 400},
        )
        assert resp.status_code == 422

    async def test_calculate_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/feed/calculate-ration",
            json={"species": "cattle", "weight_kg": 400},
        )
        assert resp.status_code in (401, 403)
