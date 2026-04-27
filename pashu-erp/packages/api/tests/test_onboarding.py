"""Unit tests for Onboarding endpoints — /v1/onboarding."""

from unittest.mock import AsyncMock

from httpx import AsyncClient


def _valid_onboarding_payload() -> dict:
    return {
        "preferred_language": "kn",
        "district": "Tumkur",
        "village_code": "629001",
        "primary_species": ["cattle", "goat"],
        "herd_size": 5,
        "has_milk_center_access": True,
        "shg_member": True,
    }


# ---------------------------------------------------------------------------
# POST /v1/onboarding/complete
# ---------------------------------------------------------------------------


class TestCompleteOnboarding:
    async def test_complete_success(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST with valid data returns 200."""
        resp = await client.post(
            "/v1/onboarding/complete",
            json=_valid_onboarding_payload(),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["onboarding_complete"] is True
        assert "preferences" in body
        assert "next_steps" in body
        assert len(body["next_steps"]) > 0

    async def test_complete_missing_district(self, client: AsyncClient) -> None:
        """POST without required 'district' returns 422."""
        payload = _valid_onboarding_payload()
        del payload["district"]
        resp = await client.post("/v1/onboarding/complete", json=payload)
        assert resp.status_code == 422

    async def test_complete_minimal_data(self, client: AsyncClient, mock_db: AsyncMock) -> None:
        """POST with only required fields returns 200."""
        resp = await client.post(
            "/v1/onboarding/complete",
            json={"district": "Tumkur"},
        )
        assert resp.status_code == 200

    async def test_complete_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/onboarding/complete",
            json=_valid_onboarding_payload(),
        )
        assert resp.status_code in (401, 403)
