"""Karnataka Milk Federation FAT/SNF slab-based rate calculator."""

from decimal import ROUND_HALF_UP, Decimal

# KMF pricing slabs (approximate rates as of 2025-26)
# Rate = Base rate + FAT premium + SNF premium
# Base rate varies by district and season

FAT_SLABS = [
    {"min": Decimal("3.0"), "max": Decimal("3.5"), "rate_per_unit": Decimal("7.50")},
    {"min": Decimal("3.5"), "max": Decimal("4.0"), "rate_per_unit": Decimal("8.00")},
    {"min": Decimal("4.0"), "max": Decimal("4.5"), "rate_per_unit": Decimal("8.50")},
    {"min": Decimal("4.5"), "max": Decimal("5.0"), "rate_per_unit": Decimal("9.00")},
    {"min": Decimal("5.0"), "max": Decimal("5.5"), "rate_per_unit": Decimal("9.50")},
    {"min": Decimal("5.5"), "max": Decimal("6.0"), "rate_per_unit": Decimal("10.00")},
    {"min": Decimal("6.0"), "max": Decimal("7.0"), "rate_per_unit": Decimal("10.50")},
    {"min": Decimal("7.0"), "max": Decimal("10.0"), "rate_per_unit": Decimal("11.00")},
]

SNF_SLABS = [
    {"min": Decimal("8.0"), "max": Decimal("8.3"), "rate_per_unit": Decimal("5.00")},
    {"min": Decimal("8.3"), "max": Decimal("8.5"), "rate_per_unit": Decimal("5.50")},
    {"min": Decimal("8.5"), "max": Decimal("8.8"), "rate_per_unit": Decimal("6.00")},
    {"min": Decimal("8.8"), "max": Decimal("9.0"), "rate_per_unit": Decimal("6.50")},
    {"min": Decimal("9.0"), "max": Decimal("10.0"), "rate_per_unit": Decimal("7.00")},
]

TWO_PLACES = Decimal("0.01")


def _get_slab_rate(value: Decimal, slabs: list[dict]) -> Decimal:
    """Find the applicable slab rate for a given value."""
    for slab in slabs:
        if slab["min"] <= value < slab["max"]:
            return slab["rate_per_unit"]
    # If above all slabs, use the highest
    if value >= slabs[-1]["max"]:
        return slabs[-1]["rate_per_unit"]
    # If below all slabs, use the lowest
    return slabs[0]["rate_per_unit"]


def calculate_rate(fat_pct: float, snf_pct: float) -> Decimal:
    """Calculate milk rate per liter based on FAT and SNF percentages.

    Uses KMF slab-based pricing:
        Total rate = (FAT_rate * FAT%) + (SNF_rate * SNF%) / 2

    Args:
        fat_pct: Fat percentage (typically 3.0 - 7.0 for cow, 6.0 - 10.0 for buffalo)
        snf_pct: Solids-Not-Fat percentage (typically 8.0 - 9.5)

    Returns:
        Rate per liter in INR as Decimal
    """
    fat_d = Decimal(str(fat_pct))
    snf_d = Decimal(str(snf_pct))

    fat_rate = _get_slab_rate(fat_d, FAT_SLABS)
    snf_rate = _get_slab_rate(snf_d, SNF_SLABS)

    rate_per_liter = (fat_d * fat_rate + snf_d * snf_rate) / Decimal("2")

    return rate_per_liter.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
