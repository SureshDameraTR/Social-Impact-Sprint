"""Shared test data factories for PashuRaksha API tests.

Centralizes mock object creation that was previously duplicated across
test_animals.py, test_health.py, test_milk.py, test_medicine.py,
test_insurance.py, and test_vaccination.py.

Usage:
    from tests.factories import mock_animal, valid_animal_payload
"""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

from tests.conftest import FARMER_USER_ID


def mock_animal(user_id: str = FARMER_USER_ID, **overrides) -> MagicMock:
    """Create a mock Animal ORM object with sensible defaults.

    All attributes used across the test suite are included. Pass keyword
    arguments to override any default value.
    """
    animal = MagicMock()
    defaults = {
        "id": uuid.uuid4(),
        "user_id": user_id,
        "name": "Gauri",
        "species": "cattle",
        "breed": "Gir",
        "breed_type": "indigenous",
        "pashu_aadhaar_id": "IN0000000001",
        "tag_id": "TAG001",
        "date_of_birth": date(2020, 1, 15),
        "sex": "female",
        "lactation_number": 2,
        "body_condition_score": 3.5,
        "is_insured": False,
        "metadata_": {},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    for attr, value in defaults.items():
        setattr(animal, attr, value)
    return animal


def valid_animal_payload(**overrides) -> dict:
    """Return a valid JSON payload for POST /v1/animals."""
    defaults = {
        "name": "Gauri",
        "species": "cattle",
        "breed": "Gir",
        "breed_type": "indigenous",
        "sex": "female",
    }
    defaults.update(overrides)
    return defaults


def mock_health_event(**overrides) -> MagicMock:
    """Create a mock HealthEvent ORM object."""
    event = MagicMock()
    defaults = {
        "id": uuid.uuid4(),
        "animal_id": uuid.uuid4(),
        "event_type": "symptom",
        "description": "Fever and reduced appetite",
        "symptoms": ["fever", "loss_of_appetite"],
        "ai_risk_score": 0.7,
        "recommended_action": "Consult vet",
        "probable_diseases": ["FMD"],
        "recorded_by": FARMER_USER_ID,
        "event_date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    for attr, value in defaults.items():
        setattr(event, attr, value)
    return event


def mock_yield_log(**overrides) -> MagicMock:
    """Create a mock YieldLog ORM object."""
    log = MagicMock()
    defaults = {
        "id": uuid.uuid4(),
        "animal_id": uuid.uuid4(),
        "user_id": FARMER_USER_ID,
        "quantity_liters": 5.5,
        "session": "morning",
        "notes": "Good yield",
        "recorded_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    for attr, value in defaults.items():
        setattr(log, attr, value)
    return log
