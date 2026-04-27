import importlib
import sys
import types
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

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


# Avoid triggering app.schemas.__init__ (which re-exports all sibling schemas
# and hits a pre-existing Pydantic Decimal constraint bug in milk.py).
# Seed the package in sys.modules as a bare namespace so importlib only loads
# the reference submodule.
if "app.schemas" not in sys.modules:
    _pkg = types.ModuleType("app.schemas")
    _pkg.__path__ = [__import__("app").__path__[0] + "/schemas"]
    _pkg.__package__ = "app.schemas"
    sys.modules["app.schemas"] = _pkg

_ref = importlib.import_module("app.schemas.reference")
StateRead = _ref.StateRead
DistrictRead = _ref.DistrictRead
SubDistrictRead = _ref.SubDistrictRead
VillageRead = _ref.VillageRead
SpeciesRead = _ref.SpeciesRead
BreedRead = _ref.BreedRead
DiseaseRuleRead = _ref.DiseaseRuleRead
VaccinationScheduleRead = _ref.VaccinationScheduleRead
FeedStandardRead = _ref.FeedStandardRead
LocationHierarchyResponse = _ref.LocationHierarchyResponse


class TestReferenceSchemas:
    def test_state_read_from_attributes(self):
        schema = StateRead.model_validate(
            {"lgd_code": 29, "name": "Karnataka", "name_local": "ಕರ್ನಾಟಕ"},
        )
        assert schema.lgd_code == 29

    def test_location_hierarchy_response(self):
        resp = LocationHierarchyResponse.model_validate(
            {"data": [{"lgd_code": 29, "name": "Karnataka", "name_local": None}], "total": 1},
        )
        assert resp.total == 1
        assert len(resp.data) == 1

    def test_breed_read(self):
        schema = BreedRead.model_validate({
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "Hallikar", "name_local": "ಹಳ್ಳಿಕಾರ್",
            "species_code": "cattle", "origin": "Karnataka",
            "nbagr_code": "INDIA_CATTLE_0600",
            "is_indigenous": True,
        })
        assert schema.name == "Hallikar"


@pytest.fixture
async def ref_client(mock_db):
    """Minimal test client that mounts only the reference router.

    This avoids importing the full app (which triggers the milk.py Decimal
    constraint bug in Pydantic) while still exercising the public endpoints.
    ``mock_db`` comes from conftest.
    """
    from app.database import get_db
    from app.routers.reference import router

    app = FastAPI()
    app.include_router(router)

    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


class TestReferenceLocationEndpoints:
    async def test_list_states(self, ref_client: AsyncClient, mock_db):
        """Reference endpoints are public — no auth required."""
        state = MagicMock(spec=State)
        state.lgd_code = 29
        state.name = "Karnataka"
        state.name_local = "ಕರ್ನಾಟಕ"

        count_result = MagicMock()
        count_result.scalar.return_value = 1
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [state]
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await ref_client.get("/v1/reference/states")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["data"][0]["name"] == "Karnataka"

    async def test_list_districts_by_state(self, ref_client: AsyncClient, mock_db):
        district = MagicMock(spec=District)
        district.lgd_code = 2922
        district.name = "Mysuru"
        district.name_local = None
        district.state_lgd_code = 29
        district.latitude = 12.30
        district.longitude = 76.66
        district.elevation_m = None

        count_result = MagicMock()
        count_result.scalar.return_value = 1
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [district]
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        resp = await ref_client.get("/v1/reference/districts?state_lgd_code=29")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"][0]["name"] == "Mysuru"
