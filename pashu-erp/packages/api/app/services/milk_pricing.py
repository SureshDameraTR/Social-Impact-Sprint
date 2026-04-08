"""Karnataka Milk Federation FAT/SNF slab-based rate calculator."""

# KMF pricing slabs (approximate rates as of 2025-26)
# Rate = Base rate + FAT premium + SNF premium
# Base rate varies by district and season

FAT_SLABS = [
    {"min": 3.0, "max": 3.5, "rate_per_unit": 7.50},
    {"min": 3.5, "max": 4.0, "rate_per_unit": 8.00},
    {"min": 4.0, "max": 4.5, "rate_per_unit": 8.50},
    {"min": 4.5, "max": 5.0, "rate_per_unit": 9.00},
    {"min": 5.0, "max": 5.5, "rate_per_unit": 9.50},
    {"min": 5.5, "max": 6.0, "rate_per_unit": 10.00},
    {"min": 6.0, "max": 7.0, "rate_per_unit": 10.50},
    {"min": 7.0, "max": 10.0, "rate_per_unit": 11.00},
]

SNF_SLABS = [
    {"min": 8.0, "max": 8.3, "rate_per_unit": 5.00},
    {"min": 8.3, "max": 8.5, "rate_per_unit": 5.50},
    {"min": 8.5, "max": 8.8, "rate_per_unit": 6.00},
    {"min": 8.8, "max": 9.0, "rate_per_unit": 6.50},
    {"min": 9.0, "max": 10.0, "rate_per_unit": 7.00},
]

BASE_RATE = 20.0  # Base rate per liter (Karnataka average)


def _get_slab_rate(value: float, slabs: list[dict]) -> float:
    """Find the applicable slab rate for a given value."""
    for slab in slabs:
        if slab["min"] <= value < slab["max"]:
            return slab["rate_per_unit"]
    # If above all slabs, use the highest
    if value >= slabs[-1]["max"]:
        return slabs[-1]["rate_per_unit"]
    # If below all slabs, use the lowest
    return slabs[0]["rate_per_unit"]


def calculate_rate(fat_pct: float, snf_pct: float) -> float:
    """Calculate milk rate per liter based on FAT and SNF percentages.

    Uses KMF slab-based pricing:
        Rate = Base + (FAT_rate * FAT%) + (SNF_rate * SNF%)

    Args:
        fat_pct: Fat percentage (typically 3.0 - 7.0 for cow, 6.0 - 10.0 for buffalo)
        snf_pct: Solids-Not-Fat percentage (typically 8.0 - 9.5)

    Returns:
        Rate per liter in INR
    """
    fat_rate = _get_slab_rate(fat_pct, FAT_SLABS)
    snf_rate = _get_slab_rate(snf_pct, SNF_SLABS)

    rate = BASE_RATE + (fat_rate * fat_pct / 100) + (snf_rate * snf_pct / 100)

    # Simplified: use a more intuitive formula
    # Total rate = FAT component + SNF component
    rate_per_liter = (fat_pct * fat_rate + snf_pct * snf_rate) / 2

    return round(rate_per_liter, 2)
