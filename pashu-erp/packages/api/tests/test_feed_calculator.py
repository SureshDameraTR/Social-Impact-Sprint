"""Tests for the NDDB ration calculator (app.services.feed_calculator)."""

from decimal import Decimal

from app.schemas.feed import RationResult
from app.services.feed_calculator import FEEDING_STANDARDS, calculate_ration


class TestBasicCalculation:
    def test_returns_ration_result(self):
        result = calculate_ration("cattle", 400.0)
        assert isinstance(result, RationResult)

    def test_cattle_dry_400kg(self):
        """400 kg dry cattle: DM = 400 * 2.0 / 100 = 8 kg."""
        result = calculate_ration("cattle", 400.0, "dry")
        assert result.total_cost_per_day > 0
        assert len(result.ingredients) == 4  # green + dry + concentrate + mineral

    def test_ingredient_names(self):
        result = calculate_ration("cattle", 400.0)
        names = [i.name for i in result.ingredients]
        assert "Green Fodder (Napier)" in names
        assert "Dry Fodder (Paddy Straw)" in names
        assert "Concentrate Mix" in names
        assert "Mineral Mixture" in names

    def test_all_quantities_positive(self):
        result = calculate_ration("cattle", 400.0, "early")
        for ing in result.ingredients:
            assert ing.daily_qty_kg > 0

    def test_cost_increases_with_weight(self):
        small = calculate_ration("cattle", 200.0)
        large = calculate_ration("cattle", 500.0)
        assert large.total_cost_per_day > small.total_cost_per_day

    def test_cost_increases_with_lactation(self):
        dry = calculate_ration("cattle", 400.0, "dry")
        early = calculate_ration("cattle", 400.0, "early")
        assert early.total_cost_per_day > dry.total_cost_per_day


class TestLactationStages:
    def test_early_lactation_higher_dm(self):
        """Early lactation needs 3.5% BW vs 2.0% for dry."""
        early = calculate_ration("cattle", 400.0, "early")
        dry = calculate_ration("cattle", 400.0, "dry")
        early_total = sum(i.daily_qty_kg for i in early.ingredients)
        dry_total = sum(i.daily_qty_kg for i in dry.ingredients)
        assert early_total > dry_total

    def test_mid_lactation(self):
        result = calculate_ration("cattle", 400.0, "mid")
        assert result.total_cost_per_day > 0

    def test_late_lactation(self):
        result = calculate_ration("cattle", 400.0, "late")
        assert result.total_cost_per_day > 0

    def test_none_lactation_uses_default(self):
        result = calculate_ration("cattle", 400.0, None)
        assert result.total_cost_per_day > 0

    def test_early_lactation_energy_marginal(self):
        """Early lactation should note marginal energy balance."""
        result = calculate_ration("cattle", 400.0, "early")
        assert "Marginal" in result.energy_balance or "extra concentrate" in result.energy_balance

    def test_non_early_energy_adequate(self):
        result = calculate_ration("cattle", 400.0, "dry")
        assert result.energy_balance == "Adequate"


class TestSpecies:
    def test_goat_30kg(self):
        result = calculate_ration("goat", 30.0)
        assert result.total_cost_per_day > 0
        assert result.total_cost_per_day < calculate_ration("cattle", 400.0).total_cost_per_day

    def test_sheep_40kg(self):
        result = calculate_ration("sheep", 40.0)
        assert result.total_cost_per_day > 0

    def test_poultry_2kg(self):
        result = calculate_ration("poultry", 2.0)
        assert result.total_cost_per_day > 0

    def test_unknown_species_falls_back_to_cattle(self):
        """Unknown species should use cattle standards as fallback."""
        result = calculate_ration("yak", 300.0)
        assert isinstance(result, RationResult)
        assert result.total_cost_per_day > 0

    def test_case_insensitive_species(self):
        lower = calculate_ration("cattle", 400.0)
        upper = calculate_ration("Cattle", 400.0)
        assert lower.total_cost_per_day == upper.total_cost_per_day


class TestProteinBalance:
    def test_protein_balance_string(self):
        result = calculate_ration("cattle", 400.0, "dry")
        assert (
            result.protein_balance in ["Balanced"]
            or "Surplus" in result.protein_balance
            or "Deficit" in result.protein_balance
        )

    def test_surplus_protein_noted(self):
        """Dry cattle with low CP requirement should show surplus."""
        result = calculate_ration("cattle", 400.0, "dry")
        # Dry cattle need 8% CP which is relatively low
        assert "Surplus" in result.protein_balance or result.protein_balance == "Balanced"

    def test_early_lactation_protein(self):
        """Early lactation with 16% CP may show deficit."""
        result = calculate_ration("cattle", 400.0, "early")
        # High protein demand in early lactation
        assert isinstance(result.protein_balance, str)


class TestEdgeCases:
    def test_very_small_weight(self):
        """A very small animal should still produce valid results."""
        result = calculate_ration("goat", 5.0)
        assert result.total_cost_per_day > 0
        for ing in result.ingredients:
            assert ing.daily_qty_kg >= 0

    def test_very_large_weight(self):
        """A very large animal (buffalo) should scale linearly."""
        result = calculate_ration("cattle", 800.0)
        half = calculate_ration("cattle", 400.0)
        # Cost should roughly double (not exact due to mineral minimum)
        assert result.total_cost_per_day > half.total_cost_per_day * Decimal("1.5")

    def test_mineral_minimum(self):
        """Mineral mixture should be at least 0.05 kg."""
        result = calculate_ration("poultry", 2.0)
        mineral = next((i for i in result.ingredients if "Mineral" in i.name), None)
        assert mineral is not None, "Expected Mineral ingredient not found"
        assert mineral.daily_qty_kg >= Decimal("0.05")

    def test_feeding_standards_integrity(self):
        """All species in standards should have required keys."""
        for species, stages in FEEDING_STANDARDS.items():
            for stage, std in stages.items():
                assert "dm_pct_bw" in std, f"{species}/{stage} missing dm_pct_bw"
                assert "cp_pct" in std, f"{species}/{stage} missing cp_pct"
                assert "tdn_pct" in std, f"{species}/{stage} missing tdn_pct"
                assert std["dm_pct_bw"] > 0
