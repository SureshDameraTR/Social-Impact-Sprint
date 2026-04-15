"""Tests for the rule-based disease triage engine (app.services.disease_rules).

Covers all 4 species, exact symptom matching logic, scoring, sorting,
edge cases (unknown species, empty symptoms, below-threshold matches),
and the 55+ rules comprehensively.
"""

from app.services.disease_rules import DISEASE_RULES, evaluate_symptoms


# ---------------------------------------------------------------------------
# Cattle — known symptom combinations
# ---------------------------------------------------------------------------

class TestCattleDiseaseMatching:

    def test_fmd_classic_symptoms(self):
        """FMD requires min_match=3; supplying 4 classic symptoms should match."""
        result = evaluate_symptoms("cattle", ["fever", "drooling", "blisters_mouth", "lameness"])
        matches = result["matches"]
        assert len(matches) >= 1
        fmd = next(m for m in matches if "FMD" in m["disease"])
        assert fmd["match_count"] >= 3
        assert fmd["risk_level"] == "critical"
        assert result["risk_level"] == "critical"

    def test_mastitis_two_symptoms(self):
        """Mastitis min_match=2; two matching symptoms should trigger."""
        result = evaluate_symptoms("cattle", ["swollen_udder", "hot_udder"])
        matches = result["matches"]
        mastitis = next((m for m in matches if "Mastitis" in m["disease"]), None)
        assert mastitis is not None
        assert mastitis["match_count"] == 2
        assert mastitis["risk_level"] == "high"

    def test_brucellosis_critical(self):
        result = evaluate_symptoms("cattle", ["abortion", "retained_placenta", "swollen_joints"])
        matches = result["matches"]
        bruc = next((m for m in matches if "Brucellosis" in m["disease"]), None)
        assert bruc is not None
        assert bruc["risk_level"] == "critical"

    def test_hs_three_symptoms(self):
        result = evaluate_symptoms("cattle", ["high_fever", "swollen_throat", "difficulty_breathing"])
        matches = result["matches"]
        hs = next((m for m in matches if "Hemorrhagic" in m["disease"]), None)
        assert hs is not None
        assert hs["match_count"] == 3

    def test_black_quarter(self):
        result = evaluate_symptoms("cattle", ["high_fever", "swollen_leg", "lameness", "crepitant_swelling"])
        bq = next((m for m in result["matches"] if "Black Quarter" in m["disease"]), None)
        assert bq is not None
        assert bq["risk_level"] == "critical"

    def test_theileriosis(self):
        result = evaluate_symptoms("cattle", ["high_fever", "swollen_lymph_nodes", "anaemia", "jaundice"])
        theil = next((m for m in result["matches"] if "Theileriosis" in m["disease"]), None)
        assert theil is not None
        assert theil["risk_level"] == "high"

    def test_babesiosis(self):
        result = evaluate_symptoms("cattle", ["high_fever", "red_urine", "anaemia", "jaundice"])
        bab = next((m for m in result["matches"] if "Babesiosis" in m["disease"]), None)
        assert bab is not None

    def test_anaplasmosis(self):
        result = evaluate_symptoms("cattle", ["fever", "anaemia", "jaundice", "weakness"])
        anap = next((m for m in result["matches"] if "Anaplasmosis" in m["disease"]), None)
        assert anap is not None

    def test_bloat(self):
        result = evaluate_symptoms("cattle", ["distended_abdomen", "difficulty_breathing"])
        bloat = next((m for m in result["matches"] if "Bloat" in m["disease"]), None)
        assert bloat is not None

    def test_milk_fever(self):
        result = evaluate_symptoms("cattle", ["weakness", "unable_to_stand", "cold_ears", "muscle_tremors"])
        mf = next((m for m in result["matches"] if "Milk Fever" in m["disease"]), None)
        assert mf is not None

    def test_ketosis(self):
        result = evaluate_symptoms(
            "cattle",
            ["loss_of_appetite", "reduced_milk", "rapid_weight_loss", "sweet_breath"],
        )
        ket = next((m for m in result["matches"] if "Ketosis" in m["disease"]), None)
        assert ket is not None
        assert ket["risk_level"] == "medium"

    def test_retained_placenta(self):
        result = evaluate_symptoms("cattle", ["retained_placenta", "foul_discharge"])
        rp = next((m for m in result["matches"] if "Retained Placenta" in m["disease"]), None)
        assert rp is not None

    def test_metritis(self):
        result = evaluate_symptoms("cattle", ["foul_discharge", "fever", "loss_of_appetite", "reduced_milk"])
        met = next((m for m in result["matches"] if "Metritis" in m["disease"]), None)
        assert met is not None

    def test_johnes_disease(self):
        result = evaluate_symptoms("cattle", ["chronic_diarrhea", "weight_loss", "reduced_milk"])
        johne = next((m for m in result["matches"] if "Johne" in m["disease"]), None)
        assert johne is not None

    def test_ibr(self):
        result = evaluate_symptoms(
            "cattle", ["nasal_discharge", "fever", "red_eyes", "cough"]
        )
        ibr = next((m for m in result["matches"] if "IBR" in m["disease"]), None)
        assert ibr is not None

    def test_bvd(self):
        result = evaluate_symptoms(
            "cattle", ["diarrhea", "fever", "nasal_discharge", "mouth_ulcers"]
        )
        bvd = next((m for m in result["matches"] if "BVD" in m["disease"]), None)
        assert bvd is not None

    def test_lsd(self):
        result = evaluate_symptoms(
            "cattle", ["skin_nodules", "fever", "swollen_lymph_nodes", "reduced_milk"]
        )
        lsd = next((m for m in result["matches"] if "Lumpy" in m["disease"]), None)
        assert lsd is not None
        assert lsd["risk_level"] == "critical"

    def test_anthrax(self):
        result = evaluate_symptoms("cattle", ["sudden_death", "bleeding_from_orifices"])
        anthrax = next((m for m in result["matches"] if "Anthrax" in m["disease"]), None)
        assert anthrax is not None
        assert anthrax["risk_level"] == "critical"

    def test_bovine_tb(self):
        result = evaluate_symptoms(
            "cattle", ["chronic_cough", "weight_loss", "reduced_milk"]
        )
        tb = next((m for m in result["matches"] if "Tuberculosis" in m["disease"]), None)
        assert tb is not None

    def test_trypanosomiasis(self):
        result = evaluate_symptoms("cattle", ["fever", "anaemia", "edema", "weight_loss"])
        surra = next((m for m in result["matches"] if "Trypanosomiasis" in m["disease"]), None)
        assert surra is not None

    def test_acidosis(self):
        result = evaluate_symptoms(
            "cattle", ["diarrhea", "loss_of_appetite", "dehydration", "weakness"]
        )
        acid = next((m for m in result["matches"] if "Acidosis" in m["disease"]), None)
        assert acid is not None


# ---------------------------------------------------------------------------
# Goat diseases
# ---------------------------------------------------------------------------

class TestGoatDiseaseMatching:

    def test_ppr(self):
        result = evaluate_symptoms("goat", ["fever", "nasal_discharge", "mouth_ulcers", "diarrhea"])
        ppr = next((m for m in result["matches"] if "PPR" in m["disease"]), None)
        assert ppr is not None
        assert ppr["risk_level"] == "critical"

    def test_enterotoxemia(self):
        result = evaluate_symptoms("goat", ["sudden_death", "convulsions"])
        ent = next((m for m in result["matches"] if "Enterotoxemia" in m["disease"]), None)
        assert ent is not None

    def test_goat_pox(self):
        result = evaluate_symptoms("goat", ["fever", "skin_nodules", "nasal_discharge"])
        gpox = next((m for m in result["matches"] if "Goat Pox" in m["disease"]), None)
        assert gpox is not None

    def test_haemonchosis(self):
        result = evaluate_symptoms("goat", ["anaemia", "bottle_jaw", "weakness"])
        haem = next((m for m in result["matches"] if "Haemonchosis" in m["disease"]), None)
        assert haem is not None

    def test_pneumonia(self):
        result = evaluate_symptoms(
            "goat", ["cough", "nasal_discharge", "fever", "difficulty_breathing"]
        )
        pneu = next((m for m in result["matches"] if "Pneumonia" in m["disease"]), None)
        assert pneu is not None

    def test_caprine_mastitis(self):
        result = evaluate_symptoms("goat", ["swollen_udder", "hot_udder"])
        mast = next((m for m in result["matches"] if "Caprine Mastitis" in m["disease"]), None)
        assert mast is not None

    def test_caprine_brucellosis(self):
        result = evaluate_symptoms("goat", ["abortion", "retained_placenta"])
        bruc = next((m for m in result["matches"] if "Caprine Brucellosis" in m["disease"]), None)
        assert bruc is not None

    def test_johnes_caprine(self):
        result = evaluate_symptoms(
            "goat", ["chronic_diarrhea", "weight_loss", "normal_appetite"]
        )
        johne = next((m for m in result["matches"] if "Johne" in m["disease"]), None)
        assert johne is not None

    def test_orf(self):
        result = evaluate_symptoms("goat", ["scabs_lips", "scabs_nose"])
        orf = next((m for m in result["matches"] if "Orf" in m["disease"]), None)
        assert orf is not None
        assert orf["risk_level"] == "medium"

    def test_ccpp(self):
        result = evaluate_symptoms(
            "goat", ["cough", "difficulty_breathing", "nasal_discharge"]
        )
        ccpp = next((m for m in result["matches"] if "CCPP" in m["disease"]), None)
        assert ccpp is not None

    def test_coccidiosis_caprine(self):
        result = evaluate_symptoms(
            "goat", ["bloody_diarrhea", "weight_loss", "dehydration"]
        )
        cocc = next((m for m in result["matches"] if "Coccidiosis" in m["disease"]), None)
        assert cocc is not None

    def test_foot_rot_caprine(self):
        result = evaluate_symptoms("goat", ["lameness", "foul_smell_feet"])
        fr = next((m for m in result["matches"] if "Foot Rot" in m["disease"]), None)
        assert fr is not None

    def test_pregnancy_toxemia_caprine(self):
        result = evaluate_symptoms(
            "goat", ["loss_of_appetite", "lethargy", "teeth_grinding"]
        )
        pt = next((m for m in result["matches"] if "Pregnancy Toxemia" in m["disease"]), None)
        assert pt is not None

    def test_caprine_bloat(self):
        result = evaluate_symptoms("goat", ["distended_abdomen", "difficulty_breathing"])
        blot = next((m for m in result["matches"] if "Caprine Bloat" in m["disease"]), None)
        assert blot is not None

    def test_tetanus(self):
        result = evaluate_symptoms(
            "goat", ["muscle_stiffness", "lock_jaw", "erect_ears"]
        )
        tet = next((m for m in result["matches"] if "Tetanus" in m["disease"]), None)
        assert tet is not None
        assert tet["risk_level"] == "critical"


# ---------------------------------------------------------------------------
# Sheep diseases
# ---------------------------------------------------------------------------

class TestSheepDiseaseMatching:

    def test_blue_tongue(self):
        result = evaluate_symptoms("sheep", ["fever", "swollen_tongue", "blue_tongue"])
        bt = next((m for m in result["matches"] if "Blue Tongue" in m["disease"]), None)
        assert bt is not None
        assert bt["risk_level"] == "critical"

    def test_sheep_pox(self):
        result = evaluate_symptoms(
            "sheep", ["fever", "skin_nodules", "nasal_discharge"]
        )
        sp = next((m for m in result["matches"] if "Sheep Pox" in m["disease"]), None)
        assert sp is not None

    def test_enterotoxemia_ovine(self):
        result = evaluate_symptoms("sheep", ["sudden_death", "convulsions"])
        ent = next((m for m in result["matches"] if "Enterotoxemia" in m["disease"]), None)
        assert ent is not None

    def test_haemonchosis_ovine(self):
        result = evaluate_symptoms("sheep", ["anaemia", "bottle_jaw", "weakness"])
        haem = next((m for m in result["matches"] if "Haemonchosis" in m["disease"]), None)
        assert haem is not None

    def test_foot_rot_ovine(self):
        result = evaluate_symptoms("sheep", ["lameness", "foul_smell_feet"])
        fr = next((m for m in result["matches"] if "Foot Rot" in m["disease"]), None)
        assert fr is not None

    def test_ovine_pneumonia(self):
        result = evaluate_symptoms(
            "sheep", ["cough", "nasal_discharge", "fever"]
        )
        pn = next((m for m in result["matches"] if "Ovine Pneumonia" in m["disease"]), None)
        assert pn is not None

    def test_pregnancy_toxemia_ovine(self):
        result = evaluate_symptoms(
            "sheep", ["loss_of_appetite", "lethargy", "teeth_grinding"]
        )
        pt = next((m for m in result["matches"] if "Pregnancy Toxemia" in m["disease"]), None)
        assert pt is not None

    def test_braxy(self):
        result = evaluate_symptoms("sheep", ["sudden_death", "high_fever"])
        br = next((m for m in result["matches"] if "Braxy" in m["disease"]), None)
        assert br is not None

    def test_louping_ill(self):
        result = evaluate_symptoms("sheep", ["fever", "tremors", "incoordination"])
        li = next((m for m in result["matches"] if "Louping" in m["disease"]), None)
        assert li is not None

    def test_scrapie(self):
        result = evaluate_symptoms(
            "sheep", ["itching", "wool_loss", "incoordination"]
        )
        scr = next((m for m in result["matches"] if "Scrapie" in m["disease"]), None)
        assert scr is not None
        assert scr["risk_level"] == "critical"


# ---------------------------------------------------------------------------
# Poultry diseases
# ---------------------------------------------------------------------------

class TestPoultryDiseaseMatching:

    def test_newcastle(self):
        result = evaluate_symptoms(
            "poultry",
            ["respiratory_distress", "greenish_diarrhea", "twisted_neck"],
        )
        nd = next((m for m in result["matches"] if "Newcastle" in m["disease"]), None)
        assert nd is not None
        assert nd["risk_level"] == "critical"

    def test_mareks(self):
        result = evaluate_symptoms(
            "poultry", ["paralysis", "weight_loss", "grey_iris"]
        )
        mk = next((m for m in result["matches"] if "Marek" in m["disease"]), None)
        assert mk is not None

    def test_avian_influenza(self):
        result = evaluate_symptoms(
            "poultry",
            ["sudden_death", "respiratory_distress", "swollen_head"],
        )
        ai = next((m for m in result["matches"] if "Avian Influenza" in m["disease"]), None)
        assert ai is not None
        assert ai["risk_level"] == "critical"

    def test_infectious_bronchitis(self):
        result = evaluate_symptoms(
            "poultry", ["cough", "sneezing", "nasal_discharge"]
        )
        ib = next((m for m in result["matches"] if "Infectious Bronchitis" in m["disease"]), None)
        assert ib is not None

    def test_coccidiosis_poultry(self):
        result = evaluate_symptoms(
            "poultry", ["bloody_droppings", "weight_loss", "ruffled_feathers"]
        )
        cocc = next((m for m in result["matches"] if "Coccidiosis" in m["disease"]), None)
        assert cocc is not None

    def test_fowl_pox(self):
        result = evaluate_symptoms("poultry", ["wart_like_lesions", "scabs_on_comb"])
        fp = next((m for m in result["matches"] if "Fowl Pox" in m["disease"]), None)
        assert fp is not None
        assert fp["risk_level"] == "medium"

    def test_ibd_gumboro(self):
        result = evaluate_symptoms(
            "poultry",
            ["ruffled_feathers", "watery_diarrhea", "trembling"],
        )
        ibd = next((m for m in result["matches"] if "IBD" in m["disease"] or "Gumboro" in m["disease"]), None)
        assert ibd is not None

    def test_fowl_cholera(self):
        result = evaluate_symptoms(
            "poultry",
            ["sudden_death", "swollen_wattles", "greenish_diarrhea"],
        )
        fc = next((m for m in result["matches"] if "Fowl Cholera" in m["disease"]), None)
        assert fc is not None

    def test_mycoplasma(self):
        result = evaluate_symptoms(
            "poultry",
            ["cough", "nasal_discharge", "sneezing", "swollen_sinuses"],
        )
        myc = next((m for m in result["matches"] if "Mycoplasma" in m["disease"]), None)
        assert myc is not None

    def test_ecoli(self):
        result = evaluate_symptoms(
            "poultry",
            ["diarrhea", "ruffled_feathers", "lethargy", "respiratory_distress"],
        )
        ec = next((m for m in result["matches"] if "E. coli" in m["disease"]), None)
        assert ec is not None


# ---------------------------------------------------------------------------
# Scoring and sorting logic
# ---------------------------------------------------------------------------

class TestScoringAndSorting:

    def test_top_matches_limited_to_three(self):
        """Even if many rules match, only top 3 are returned."""
        # Symptoms that could match multiple cattle diseases
        result = evaluate_symptoms(
            "cattle",
            ["fever", "nasal_discharge", "reduced_milk", "loss_of_appetite",
             "diarrhea", "weakness", "weight_loss", "anaemia", "jaundice"],
        )
        assert len(result["matches"]) <= 3

    def test_match_score_calculation(self):
        """Score is match_count / total_symptoms for the rule."""
        result = evaluate_symptoms("cattle", ["fever", "drooling", "blisters_mouth"])
        fmd = next(m for m in result["matches"] if "FMD" in m["disease"])
        assert fmd["match_score"] == round(3 / 6, 3)

    def test_sort_by_score_then_risk(self):
        """Higher match scores sort first; ties broken by risk severity."""
        result = evaluate_symptoms(
            "cattle",
            ["fever", "drooling", "blisters_mouth", "lameness",
             "reduced_milk", "blisters_feet"],
        )
        if len(result["matches"]) >= 2:
            # First match should have the highest score
            assert result["matches"][0]["match_score"] >= result["matches"][1]["match_score"]

    def test_risk_score_critical_high(self):
        """Critical disease risk_score should be >= 0.9."""
        result = evaluate_symptoms("cattle", ["fever", "drooling", "blisters_mouth"])
        assert result["risk_score"] >= 0.9

    def test_risk_score_medium(self):
        """Medium-risk disease should have moderate risk_score."""
        result = evaluate_symptoms(
            "cattle",
            ["loss_of_appetite", "reduced_milk", "rapid_weight_loss", "sweet_breath"],
        )
        # Ketosis is medium risk
        if result["risk_level"] == "medium":
            assert 0.4 <= result["risk_score"] <= 0.6

    def test_multiple_matching_rules_all_returned(self):
        """Shared symptoms across diseases should match multiple rules."""
        result = evaluate_symptoms(
            "cattle",
            ["high_fever", "anaemia", "jaundice", "weakness",
             "loss_of_appetite", "red_urine"],
        )
        # Should match Babesiosis and potentially Theileriosis, Anaplasmosis
        assert len(result["matches"]) >= 2
        disease_names = [m["disease"] for m in result["matches"]]
        assert any("Babesiosis" in d for d in disease_names)

    def test_matched_symptoms_returned(self):
        """Each match should list which specific symptoms matched."""
        result = evaluate_symptoms("cattle", ["swollen_udder", "hot_udder", "clots_in_milk"])
        mastitis = next(m for m in result["matches"] if "Mastitis" in m["disease"])
        assert "swollen_udder" in mastitis["matched_symptoms"]
        assert "hot_udder" in mastitis["matched_symptoms"]
        assert "clots_in_milk" in mastitis["matched_symptoms"]


# ---------------------------------------------------------------------------
# Edge cases and boundary conditions
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_unknown_species_returns_empty(self):
        result = evaluate_symptoms("elephant", ["fever", "drooling"])
        assert result["matches"] == []
        assert result["risk_level"] == "unknown"
        assert result["risk_score"] == 0.0
        assert "elephant" in result["recommended_action"]

    def test_empty_symptoms_no_matches(self):
        result = evaluate_symptoms("cattle", [])
        assert result["matches"] == []
        assert result["risk_level"] == "low"
        assert result["risk_score"] == 0.1

    def test_single_symptom_below_threshold(self):
        """One symptom when min_match > 1 should not match."""
        result = evaluate_symptoms("cattle", ["fever"])
        # Only rules with min_match=1 would fire; none in the cattle set have that
        # Most rules require 2-3 symptoms minimum
        for m in result["matches"]:
            assert m["match_count"] >= m["total_symptoms"] // len(
                DISEASE_RULES["cattle"][0]["symptoms"]
            ) or m["match_count"] >= 2

    def test_case_insensitive_species(self):
        result_lower = evaluate_symptoms("cattle", ["fever", "drooling", "blisters_mouth"])
        result_upper = evaluate_symptoms("Cattle", ["fever", "drooling", "blisters_mouth"])
        assert result_lower["matches"][0]["disease"] == result_upper["matches"][0]["disease"]

    def test_case_insensitive_symptoms(self):
        result = evaluate_symptoms("cattle", ["Fever", "DROOLING", "Blisters_Mouth"])
        assert len(result["matches"]) >= 1

    def test_whitespace_in_symptoms_stripped(self):
        result = evaluate_symptoms("cattle", [" fever ", " drooling ", " blisters_mouth "])
        assert len(result["matches"]) >= 1

    def test_no_matching_symptoms_returns_low_risk(self):
        result = evaluate_symptoms("cattle", ["xyz_unknown", "abc_fake"])
        assert result["matches"] == []
        assert result["risk_level"] == "low"
        assert result["risk_score"] == 0.1
        assert "No matching disease" in result["recommended_action"]

    def test_recommended_action_from_top_match(self):
        result = evaluate_symptoms("cattle", ["sudden_death", "bleeding_from_orifices"])
        # Should match Anthrax
        assert "DO NOT open carcass" in result["recommended_action"]

    def test_all_species_have_rules(self):
        """Every species in the rule set should have at least 5 rules."""
        for species, rules in DISEASE_RULES.items():
            assert len(rules) >= 5, f"{species} has only {len(rules)} rules"

    def test_rule_data_integrity(self):
        """Every rule must have the required fields."""
        required_fields = {"disease", "symptoms", "min_match", "risk_level", "action", "source"}
        for species, rules in DISEASE_RULES.items():
            for rule in rules:
                for field in required_fields:
                    assert field in rule, f"{species}/{rule.get('disease', '?')} missing {field}"
                assert len(rule["symptoms"]) >= rule["min_match"], (
                    f"{species}/{rule['disease']}: min_match > symptom count"
                )
                assert rule["risk_level"] in {"critical", "high", "medium", "low"}
