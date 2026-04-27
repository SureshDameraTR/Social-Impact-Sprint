# tests/test_disease_sync.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.refresh.disease_sync import DiseaseSyncService
from app.services.refresh.base import RefreshResult


class TestDiseaseSyncService:
    @pytest.mark.asyncio
    async def test_seed_from_existing_rules(self):
        """Bootstrap: load existing hardcoded rules into DB."""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MagicMock(
            scalar=MagicMock(return_value=0)
        ))

        service = DiseaseSyncService()
        result = await service.seed_from_hardcoded(mock_db)

        assert isinstance(result, RefreshResult)
        assert result.records_fetched > 50  # 55+ existing rules
        assert result.source == "hardcoded/disease_rules.py"
