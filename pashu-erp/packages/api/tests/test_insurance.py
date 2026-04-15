"""Unit tests for Insurance endpoints — /v1/insurance."""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_animal(user_id: str = FARMER_USER_ID) -> MagicMock:
    animal = MagicMock()
    animal.id = uuid.uuid4()
    animal.user_id = user_id
    animal.species = "cattle"
    animal.breed = "Gir"
    animal.breed_type = "indigenous"
    return animal


def _mock_policy() -> MagicMock:
    policy = MagicMock()
    policy.id = uuid.uuid4()
    policy.animal_id = uuid.uuid4()
    policy.provider = "National Insurance"
    policy.policy_number = "POL-001"
    policy.premium_amount = 1400.0
    policy.coverage_amount = 40000.0
    policy.valid_from = date(2024, 1, 1)
    policy.valid_to = date(2025, 1, 1)
    policy.status = "active"
    policy.created_at = datetime.now(timezone.utc)
    return policy


def _mock_premium_row() -> MagicMock:
    row = MagicMock()
    row.species = "cattle"
    row.breed_type = "indigenous"
    row.animal_value_inr = 40000
    row.premium_pct = 3.5
    return row


# ---------------------------------------------------------------------------
# GET /v1/insurance/policies/{user_id}
# ---------------------------------------------------------------------------


class TestGetUserPolicies:
    async def test_policies_own_user(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET own policies returns 200."""
        animal_result = MagicMock()
        animal_result.all.return_value = [(uuid.uuid4(),)]

        policy_result = MagicMock()
        policy_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(
            side_effect=[animal_result, policy_result]
        )

        resp = await client.get(f"/v1/insurance/policies/{FARMER_USER_ID}")
        assert resp.status_code == 200

    async def test_policies_other_user_forbidden(
        self, client: AsyncClient
    ) -> None:
        """GET another user's policies returns 403."""
        resp = await client.get(f"/v1/insurance/policies/{uuid.uuid4()}")
        assert resp.status_code == 403

    async def test_policies_no_auth(self, client_no_auth: AsyncClient) -> None:
        """GET without auth returns 401/403."""
        resp = await client_no_auth.get(
            f"/v1/insurance/policies/{uuid.uuid4()}"
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# POST /v1/insurance/claims
# ---------------------------------------------------------------------------


class TestFileClaim:
    async def test_file_claim_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        policy = _mock_policy()
        animal = _mock_animal()
        animal.id = policy.animal_id

        policy_result = MagicMock()
        policy_result.scalar_one_or_none.return_value = policy
        animal_result = MagicMock()
        animal_result.scalar_one_or_none.return_value = animal

        mock_db.execute = AsyncMock(
            side_effect=[policy_result, animal_result]
        )

        resp = await client.post(
            "/v1/insurance/claims",
            json={
                "policy_id": str(policy.id),
                "claim_type": "death",
                "description": "Animal died of disease",
            },
        )
        assert resp.status_code == 201

    async def test_file_claim_policy_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent policy returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/insurance/claims",
            json={
                "policy_id": str(uuid.uuid4()),
                "claim_type": "death",
                "description": "Test",
            },
        )
        assert resp.status_code == 404

    async def test_file_claim_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post(
            "/v1/insurance/claims",
            json={"claim_type": "death"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /v1/insurance/premium-estimate/{animal_id}
# ---------------------------------------------------------------------------


class TestPremiumEstimate:
    async def test_estimate_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with premium estimate."""
        animal = _mock_animal()
        animal_result = MagicMock()
        animal_result.scalar_one_or_none.return_value = animal

        premium_row = _mock_premium_row()
        premium_result = MagicMock()
        premium_result.scalar_one_or_none.return_value = premium_row

        mock_db.execute = AsyncMock(
            side_effect=[animal_result, premium_result]
        )

        resp = await client.get(f"/v1/insurance/premium-estimate/{animal.id}")
        assert resp.status_code == 200
        body = resp.json()
        assert "estimated_premium" in body
        assert "coverage_amount" in body

    async def test_estimate_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(
            f"/v1/insurance/premium-estimate/{uuid.uuid4()}"
        )
        assert resp.status_code == 404
