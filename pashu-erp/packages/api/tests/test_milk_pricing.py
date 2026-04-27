"""Tests for KMF FAT/SNF slab-based milk pricing (app.services.milk_pricing)."""

from decimal import Decimal

from app.services.milk_pricing import FAT_SLABS, _get_slab_rate, calculate_rate


class TestGetSlabRate:
    def test_value_in_middle_slab(self):
        """FAT 4.2 falls in the 4.0-4.5 slab -> rate 8.50."""
        rate = _get_slab_rate(Decimal("4.2"), FAT_SLABS)
        assert rate == Decimal("8.50")

    def test_value_at_slab_boundary(self):
        """FAT exactly 3.5 starts the 3.5-4.0 slab -> rate 8.00."""
        rate = _get_slab_rate(Decimal("3.5"), FAT_SLABS)
        assert rate == Decimal("8.00")

    def test_value_above_all_slabs(self):
        """FAT 12.0 (above max) uses the highest slab rate."""
        rate = _get_slab_rate(Decimal("12.0"), FAT_SLABS)
        assert rate == FAT_SLABS[-1]["rate_per_unit"]

    def test_value_below_all_slabs(self):
        """FAT 1.0 (below min) uses the lowest slab rate."""
        rate = _get_slab_rate(Decimal("1.0"), FAT_SLABS)
        assert rate == FAT_SLABS[0]["rate_per_unit"]


class TestCalculateRate:
    def test_standard_cow_milk(self):
        """Typical cow milk: FAT 4.0, SNF 8.5."""
        rate = calculate_rate(4.0, 8.5)
        assert isinstance(rate, Decimal)
        assert rate > Decimal("0")

    def test_known_calculation(self):
        """FAT 4.0 (slab 8.50), SNF 8.5 (slab 6.00).
        rate = (4.0 * 8.50) + (8.5 * 6.00) = 34.0 + 51.0 = 85.00
        """
        rate = calculate_rate(4.0, 8.5)
        assert rate == Decimal("85.00")

    def test_high_fat_buffalo_milk(self):
        """Buffalo milk: FAT 7.0, SNF 9.0."""
        rate = calculate_rate(7.0, 9.0)
        # FAT 7.0 -> 7.0-10.0 slab = 11.00; SNF 9.0 -> 9.0-10.0 slab = 7.00
        # (7.0 * 11.00) + (9.0 * 7.00) = 77 + 63 = 140.00
        assert rate == Decimal("140.00")

    def test_low_fat_low_snf(self):
        """Low quality: FAT 3.0, SNF 8.0 (both at lowest slab)."""
        rate = calculate_rate(3.0, 8.0)
        # FAT 3.0 -> 3.0-3.5 slab = 7.50; SNF 8.0 -> 8.0-8.3 slab = 5.00
        # (3.0 * 7.50) + (8.0 * 5.00) = 22.5 + 40.0 = 62.50
        assert rate == Decimal("62.50")

    def test_result_has_two_decimal_places(self):
        """Rate should always be rounded to 2 decimal places."""
        rate = calculate_rate(3.2, 8.1)
        assert rate == rate.quantize(Decimal("0.01"))
