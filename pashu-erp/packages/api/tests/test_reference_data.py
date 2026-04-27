from app.models.breed import Breed, SpeciesRef
from app.models.domain_knowledge import DiseaseRule, FeedStandard, VaccinationScheduleEntry
from app.models.location import District, State, SubDistrict, Village


class TestLocationModels:
    def test_state_has_required_fields(self):
        state = State(
            name="Karnataka",
            lgd_code=29,
            name_local="ಕರ್ನಾಟಕ",
        )
        assert state.name == "Karnataka"
        assert state.lgd_code == 29

    def test_district_has_required_fields(self):
        district = District(
            name="Mysuru",
            lgd_code=2922,
            state_lgd_code=29,
            latitude=12.30,
            longitude=76.66,
        )
        assert district.name == "Mysuru"
        assert district.state_lgd_code == 29

    def test_sub_district_has_required_fields(self):
        sd = SubDistrict(
            name="Mysuru Taluk",
            lgd_code=292201,
            district_lgd_code=2922,
        )
        assert sd.name == "Mysuru Taluk"

    def test_village_has_required_fields(self):
        v = Village(
            name="Navalgund",
            lgd_code=29220101,
            sub_district_lgd_code=292201,
        )
        assert v.name == "Navalgund"



class TestBreedModels:
    def test_species_ref_has_required_fields(self):
        sp = SpeciesRef(
            code="cattle",
            name_en="Cattle",
            name_kn="ಹಸು",
            emoji="\U0001f404",
        )
        assert sp.code == "cattle"
        assert sp.emoji == "\U0001f404"

    def test_breed_has_required_fields(self):
        breed = Breed(
            name="Hallikar",
            species_code="cattle",
            origin="Karnataka",
            nbagr_code="INDIA_CATTLE_0600",
        )
        assert breed.species_code == "cattle"
        assert breed.nbagr_code == "INDIA_CATTLE_0600"


class TestDomainKnowledgeModels:
    def test_disease_rule_has_required_fields(self):
        rule = DiseaseRule(
            species_code="cattle",
            disease_name="Foot and Mouth Disease (FMD)",
            symptoms=["fever", "mouth_blisters", "drooling"],
            min_match=3,
            risk_level="critical",
            action="Isolate immediately. Contact veterinarian.",
            source="ICAR-IVRI FMD Guidelines 2023",
        )
        assert rule.risk_level == "critical"
        assert len(rule.symptoms) == 3

    def test_vaccination_schedule_entry(self):
        entry = VaccinationScheduleEntry(
            species_code="cattle",
            vaccine_name="FMD",
            first_dose_months=4,
            repeat_interval_months=6,
            is_mandatory=True,
        )
        assert entry.is_mandatory is True

    def test_feed_standard(self):
        std = FeedStandard(
            species_code="cattle",
            lactation_stage="early",
            dm_intake_pct_body_weight=3.5,
            crude_protein_pct=18.0,
            tdn_pct=70.0,
            source="NDDB Feeding Standards 2023",
        )
        assert std.dm_intake_pct_body_weight == 3.5
