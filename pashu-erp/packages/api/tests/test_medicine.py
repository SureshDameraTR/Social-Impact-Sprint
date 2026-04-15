"""Unit tests for Medicine endpoints — /v1/medicines."""

import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from tests.conftest import FARMER_USER_ID


def _mock_medicine() -> MagicMock:
    med = MagicMock()
    med.id = uuid.uuid4()
    med.name_en = "Oxytetracycline"
    med.name_kn = None
    med.category = "antibiotic"
    med.withdrawal_milk_days = 7
    med.withdrawal_meat_days = 28
    return med


def _mock_animal(user_id: str = FARMER_USER_ID) -> MagicMock:
    animal = MagicMock()
    animal.id = uuid.uuid4()
    animal.user_id = user_id
    animal.species = "cattle"
    return animal


def _mock_administration() -> MagicMock:
    admin = MagicMock()
    admin.id = uuid.uuid4()
    admin.animal_id = uuid.uuid4()
    admin.medicine_id = uuid.uuid4()
    admin.administered_at = datetime.now(timezone.utc)
    admin.withdrawal_milk_until = date.today() + timedelta(days=7)
    admin.withdrawal_meat_until = date.today() + timedelta(days=28)
    admin.medicine = _mock_medicine()
    return admin


# ---------------------------------------------------------------------------
# GET /v1/medicines — List
# ---------------------------------------------------------------------------


class TestListMedicines:
    async def test_list_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get("/v1/medicines")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /v1/medicines/administer
# ---------------------------------------------------------------------------


class TestAdministerMedicine:
    async def test_administer_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with valid data returns 201."""
        animal = _mock_animal()
        medicine = _mock_medicine()

        animal_result = MagicMock()
        animal_result.scalar_one_or_none.return_value = animal
        med_result = MagicMock()
        med_result.scalar_one_or_none.return_value = medicine

        mock_db.execute = AsyncMock(
            side_effect=[animal_result, med_result]
        )

        resp = await client.post(
            "/v1/medicines/administer",
            json={
                "animal_id": str(animal.id),
                "medicine_id": str(medicine.id),
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "withdrawal_milk_until" in body
        assert "withdrawal_meat_until" in body

    async def test_administer_animal_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent animal returns 404."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/medicines/administer",
            json={
                "animal_id": str(uuid.uuid4()),
                "medicine_id": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 404

    async def test_administer_medicine_not_found(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST with nonexistent medicine returns 404."""
        animal = _mock_animal()
        animal_result = MagicMock()
        animal_result.scalar_one_or_none.return_value = animal
        med_result = MagicMock()
        med_result.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(
            side_effect=[animal_result, med_result]
        )

        resp = await client.post(
            "/v1/medicines/administer",
            json={
                "animal_id": str(animal.id),
                "medicine_id": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 404

    async def test_administer_forbidden(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """POST on another user's animal returns 403."""
        animal = _mock_animal(user_id=str(uuid.uuid4()))
        result = MagicMock()
        result.scalar_one_or_none.return_value = animal
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.post(
            "/v1/medicines/administer",
            json={
                "animal_id": str(animal.id),
                "medicine_id": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 403

    async def test_administer_missing_fields(self, client: AsyncClient) -> None:
        """POST without required fields returns 422."""
        resp = await client.post(
            "/v1/medicines/administer",
            json={"animal_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 422

    async def test_administer_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/medicines/administer",
            json={
                "animal_id": str(uuid.uuid4()),
                "medicine_id": str(uuid.uuid4()),
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/medicines/withdrawal-status/{animal_id}
# ---------------------------------------------------------------------------


class TestWithdrawalStatus:
    async def test_status_success(
        self, client: AsyncClient, mock_db: AsyncMock
    ) -> None:
        """GET returns 200 with withdrawal data."""
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        resp = await client.get(
            f"/v1/medicines/withdrawal-status/{uuid.uuid4()}"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "milk_safe" in body
        assert "meat_safe" in body
        assert "active_withdrawals" in body
