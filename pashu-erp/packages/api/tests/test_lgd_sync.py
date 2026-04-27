# tests/test_lgd_sync.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.refresh.base import RefreshResult
from app.services.refresh.lgd_sync import LGDSyncService


class TestLGDSyncService:
    @pytest.mark.asyncio
    async def test_sync_states_inserts_new_records(self):
        mock_data_gov = MagicMock()
        mock_data_gov.fetch_all_records = AsyncMock(return_value=[
            {"state_name_english_": "Karnataka", "state_code": "29"},
            {"state_name_english_": "Tamil Nadu", "state_code": "33"},
        ])

        mock_db = AsyncMock()
        empty_scalars = MagicMock(all=MagicMock(return_value=[]))
        mock_db.execute = AsyncMock(
            return_value=MagicMock(scalars=MagicMock(return_value=empty_scalars))
        )

        service = LGDSyncService(data_gov_client=mock_data_gov)
        result = await service.sync_states(mock_db)

        assert isinstance(result, RefreshResult)
        assert result.source == "data.gov.in/LGD"
        assert result.records_fetched == 2

    @pytest.mark.asyncio
    async def test_sync_is_idempotent(self):
        """Running sync twice with same data produces no duplicates."""
        mock_data_gov = MagicMock()
        mock_data_gov.fetch_all_records = AsyncMock(return_value=[
            {"state_name_english_": "Karnataka", "state_code": "29"},
        ])

        existing = MagicMock()
        existing.lgd_code = 29
        existing.name = "Karnataka"
        mock_db = AsyncMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [existing]
        execute_result = MagicMock()
        execute_result.scalars.return_value = scalars_mock
        mock_db.execute = AsyncMock(return_value=execute_result)

        service = LGDSyncService(data_gov_client=mock_data_gov)
        result = await service.sync_states(mock_db)

        assert result.records_inserted == 0
        assert result.records_unchanged == 1
