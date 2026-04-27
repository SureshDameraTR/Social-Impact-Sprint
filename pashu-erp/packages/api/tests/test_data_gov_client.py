# tests/test_data_gov_client.py
from unittest.mock import AsyncMock, MagicMock

from app.services.data_gov_client import DataGovClient


class TestDataGovClient:
    async def test_fetch_resource_returns_records(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "records": [{"field1": "value1"}],
            "total": 1,
            "count": 1,
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        client = DataGovClient(http_client=mock_client, api_key="test-key")
        result = await client.fetch_resource("abc123", limit=10)

        assert result["total"] == 1
        assert len(result["records"]) == 1
        call_kwargs = mock_client.get.call_args
        params = call_kwargs.kwargs.get("params", {})
        assert params.get("api-key") == "test-key"

    async def test_fetch_all_pages(self):
        page1 = MagicMock()
        page1.status_code = 200
        page1.json.return_value = {"records": [{"id": 1}, {"id": 2}], "total": 3, "count": 2}
        page1.raise_for_status = MagicMock()

        page2 = MagicMock()
        page2.status_code = 200
        page2.json.return_value = {"records": [{"id": 3}], "total": 3, "count": 1}
        page2.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[page1, page2])

        client = DataGovClient(http_client=mock_client, api_key="test-key")
        records = await client.fetch_all_records("abc123", page_size=2)

        assert len(records) == 3
        assert mock_client.get.call_count == 2
