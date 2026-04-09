"""Rule-based ration calculator using NDDB feeding standards."""

from app.schemas.feed import RationIngredient, RationResult

# NDDB feeding standards: daily DM intake as % of body weight, crude protein %, energy (TDN %)
FEEDING_STANDARDS = {
    "cattle": {
        "dry": {"dm_pct_bw": 2.0, "cp_pct": 8.0, "tdn_pct": 50.0},
        "early": {"dm_pct_bw": 3.5, "cp_pct": 16.0, "tdn_pct": 70.0},
        "mid": {"dm_pct_bw": 3.0, "cp_pct": 14.0, "tdn_pct": 65.0},
        "late": {"dm_pct_bw": 2.5, "cp_pct": 12.0, "tdn_pct": 60.0},
        None: {"dm_pct_bw": 2.5, "cp_pct": 10.0, "tdn_pct": 55.0},
    },
    "goat": {
        "dry": {"dm_pct_bw": 3.0, "cp_pct": 8.0, "tdn_pct": 50.0},
        "early": {"dm_pct_bw": 5.0, "cp_pct": 14.0, "tdn_pct": 65.0},
        "mid": {"dm_pct_bw": 4.5, "cp_pct": 12.0, "tdn_pct": 60.0},
        "late": {"dm_pct_bw": 4.0, "cp_pct": 10.0, "tdn_pct": 55.0},
        None: {"dm_pct_bw": 3.5, "cp_pct": 9.0, "tdn_pct": 52.0},
    },
    "sheep": {
        "dry": {"dm_pct_bw": 2.5, "cp_pct": 8.0, "tdn_pct": 50.0},
        "early": {"dm_pct_bw": 4.5, "cp_pct": 14.0, "tdn_pct": 65.0},
        "mid": {"dm_pct_bw": 4.0, "cp_pct": 12.0, "tdn_pct": 60.0},
        "late": {"dm_pct_bw": 3.5, "cp_pct": 10.0, "tdn_pct": 55.0},
        None: {"dm_pct_bw": 3.0, "cp_pct": 9.0, "tdn_pct": 52.0},
    },
    "poultry": {
        None: {"dm_pct_bw": 5.0, "cp_pct": 18.0, "tdn_pct": 70.0},
    },
}

# Default feed ingredient database for ration formulation
DEFAULT_INGREDIENTS = [
    {"name": "Green Fodder (Napier)", "category": "roughage", "protein_pct": 8.0, "energy_kcal": 450, "cost_per_kg": 3.0, "dm_pct": 20},
    {"name": "Dry Fodder (Paddy Straw)", "category": "roughage", "protein_pct": 3.5, "energy_kcal": 380, "cost_per_kg": 2.0, "dm_pct": 90},
    {"name": "Concentrate Mix", "category": "concentrate", "protein_pct": 20.0, "energy_kcal": 2800, "cost_per_kg": 22.0, "dm_pct": 90},
    {"name": "Groundnut Cake", "category": "concentrate", "protein_pct": 45.0, "energy_kcal": 2600, "cost_per_kg": 35.0, "dm_pct": 92},
    {"name": "Rice Bran", "category": "concentrate", "protein_pct": 13.0, "energy_kcal": 2400, "cost_per_kg": 15.0, "dm_pct": 90},
    {"name": "Mineral Mixture", "category": "mineral", "protein_pct": 0.0, "energy_kcal": 0, "cost_per_kg": 60.0, "dm_pct": 95},
]


def calculate_ration(
    species: str,
    weight_kg: float,
    lactation_stage: str | None = None,
    available_ingredients: list | None = None,
) -> RationResult:
    """Calculate a balanced daily ration using simple rule-based optimization.

    Uses NDDB standards to determine requirements, then allocates
    60% roughage + 40% concentrate (by DM) as a baseline.
    """
    species_key = species.lower().strip()
    standards = FEEDING_STANDARDS.get(species_key, FEEDING_STANDARDS["cattle"])
    stage_standards = standards.get(lactation_stage, standards.get(None, standards.get("dry")))

    # Total daily dry matter requirement
    total_dm_kg = weight_kg * stage_standards["dm_pct_bw"] / 100

    # Split: 60% roughage, 35% concentrate, 5% mineral
    roughage_dm = total_dm_kg * 0.60
    concentrate_dm = total_dm_kg * 0.35
    mineral_dm = total_dm_kg * 0.05

    # Calculate ration using reference ingredients
    ingredients = []
    total_cost = 0.0

    # Green fodder (convert DM to fresh weight)
    green_fresh_kg = round(roughage_dm * 0.6 / 0.20, 1)  # 60% of roughage as green, 20% DM
    ingredients.append(RationIngredient(name="Green Fodder (Napier)", daily_qty_kg=green_fresh_kg))
    total_cost += green_fresh_kg * 3.0

    # Dry fodder
    dry_kg = round(roughage_dm * 0.4 / 0.90, 1)  # 40% of roughage as dry, 90% DM
    ingredients.append(RationIngredient(name="Dry Fodder (Paddy Straw)", daily_qty_kg=dry_kg))
    total_cost += dry_kg * 2.0

    # Concentrate mix
    conc_kg = round(concentrate_dm / 0.90, 1)
    ingredients.append(RationIngredient(name="Concentrate Mix", daily_qty_kg=conc_kg))
    total_cost += conc_kg * 22.0

    # Mineral mixture
    min_kg = round(max(0.05, mineral_dm / 0.95), 2)
    ingredients.append(RationIngredient(name="Mineral Mixture", daily_qty_kg=min_kg))
    total_cost += min_kg * 60.0

    # Estimate protein and energy balance
    total_protein = (green_fresh_kg * 0.20 * 8.0 + dry_kg * 0.90 * 3.5 + conc_kg * 0.90 * 20.0) / 100
    required_protein = total_dm_kg * stage_standards["cp_pct"] / 100
    protein_diff = total_protein - required_protein

    if protein_diff > 0.05:
        protein_balance = f"Surplus (+{protein_diff:.1f} kg CP)"
    elif protein_diff < -0.05:
        protein_balance = f"Deficit ({protein_diff:.1f} kg CP) — add oilcake supplement"
    else:
        protein_balance = "Balanced"

    energy_balance = "Adequate" if lactation_stage != "early" else "Marginal — consider extra concentrate"

    return RationResult(
        ingredients=ingredients,
        total_cost_per_day=round(total_cost, 2),
        protein_balance=protein_balance,
        energy_balance=energy_balance,
    )
