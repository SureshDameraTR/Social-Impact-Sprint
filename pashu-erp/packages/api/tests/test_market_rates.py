"""Tests for market rates service (app.services.market_rates)."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.services.market_rates import get_all_market_rates


class TestGetAllMarketRates:
    async def test_returns_rates_keyed_by_product(self):
        """Rates dict should be keyed by product name."""
        row1 = MagicMock()
        row1.product = "Cow Milk"
        row1.unit = "per_liter"
        row1.min_price = Decimal("28.00")
        row1.max_price = Decimal("35.00")
        row1.avg_price = Decimal("31.50")
        row1.district = "Tumkur"
        row1.label = "Cow Milk (per liter)"

        row2 = MagicMock()
        row2.product = "Buffalo Milk"
        row2.unit = "per_liter"
        row2.min_price = Decimal("40.00")
        row2.max_price = Decimal("52.00")
        row2.avg_price = Decimal("46.00")
        row2.district = "Tumkur"
        row2.label = "Buffalo Milk (per liter)"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [row1, row2]

        db = AsyncMock()
        db.execute.return_value = mock_result

        rates = await get_all_market_rates(db)

        assert "Cow Milk" in rates
        assert "Buffalo Milk" in rates
        assert rates["Cow Milk"]["avg"] == 31.50
        assert rates["Buffalo Milk"]["unit"] == "per_liter"
        assert rates["Cow Milk"]["district"] == "Tumkur"

    async def test_empty_table_returns_empty_dict(self):
        """No rows in DB should return empty dict."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        db = AsyncMock()
        db.execute.return_value = mock_result

        rates = await get_all_market_rates(db)
        assert rates == {}

    async def test_prices_are_floats(self):
        """Decimal prices should be converted to float in output."""
        row = MagicMock()
        row.product = "Ghee"
        row.unit = "per_kg"
        row.min_price = Decimal("450.00")
        row.max_price = Decimal("550.00")
        row.avg_price = Decimal("500.00")
        row.district = "Dharwad"
        row.label = "Ghee (per kg)"

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [row]

        db = AsyncMock()
        db.execute.return_value = mock_result

        rates = await get_all_market_rates(db)
        assert isinstance(rates["Ghee"]["min"], float)
        assert isinstance(rates["Ghee"]["max"], float)
        assert isinstance(rates["Ghee"]["avg"], float)
