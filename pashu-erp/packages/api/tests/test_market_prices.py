# tests/test_market_prices.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.refresh.market_prices import AgmarknetSyncService
from app.services.refresh.base import RefreshResult


class TestAgmarknetSync:
    @pytest.mark.asyncio
    async def test_sync_prices_creates_records(self):
        mock_data_gov = MagicMock()
        mock_data_gov.fetch_all_records = AsyncMock(return_value=[
            {
                "state": "Karnataka",
                "district": "Mysore",
                "market": "Mysore",
                "commodity": "Milk",
                "variety": "Cow Milk",
                "arrival_date": "27/04/2026",
                "min_price": "30",
                "max_price": "40",
                "modal_price": "35",
            },
        ])

        mock_db = AsyncMock()

        service = AgmarknetSyncService(data_gov_client=mock_data_gov)
        result = await service.sync_prices(mock_db, state="Karnataka")

        assert isinstance(result, RefreshResult)
        assert result.records_fetched == 1
        assert result.source == "data.gov.in/Agmarknet"
        assert result.records_inserted == 1
