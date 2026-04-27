# tests/test_milk_prices.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.refresh.base import RefreshResult
from app.services.refresh.milk_prices import MilkPriceScraper


class TestMilkPriceScraper:
    @pytest.mark.asyncio
    async def test_parse_nddb_html(self):
        html = """
        <table class="views-table">
            <thead><tr><th>State</th><th>Procurement Price (Rs/litre)</th></tr></thead>
            <tbody>
                <tr><td>Karnataka</td><td>27.50</td></tr>
                <tr><td>Gujarat</td><td>30.00</td></tr>
            </tbody>
        </table>
        """
        scraper = MilkPriceScraper(http_client=AsyncMock())
        prices = scraper._parse_price_table(html)

        assert len(prices) == 2
        assert prices[0]["state"] == "Karnataka"
        assert prices[0]["price_per_litre"] == 27.50

    @pytest.mark.asyncio
    async def test_scrape_returns_refresh_result(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = (
            "<html><body>"
            "<table class='views-table'>"
            "<thead><tr><th>State</th><th>Price</th></tr></thead>"
            "<tbody><tr><td>Karnataka</td><td>27.50</td></tr></tbody>"
            "</table></body></html>"
        )
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        mock_db = AsyncMock()

        scraper = MilkPriceScraper(http_client=mock_client)
        result = await scraper.sync_prices(mock_db)

        assert isinstance(result, RefreshResult)
        assert result.source == "NDDB/KMF"
