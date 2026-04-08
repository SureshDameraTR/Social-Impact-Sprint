"""Mock client for Bharat Pashudhan (national animal registry) API."""

from datetime import date, datetime, timezone
from uuid import UUID

# Mock national registry data
MOCK_REGISTRY = {
    "IN14KA000001": {
        "pashu_aadhaar_id": "IN14KA000001",
        "species": "cattle",
        "breed": "Hallikar",
        "sex": "female",
        "date_of_birth": "2020-03-15",
        "district": "Mysore",
        "state": "Karnataka",
        "owner_name": "Ramesh Kumar",
        "owner_aadhaar_last4": "4521",
        "vaccination_status": "up_to_date",
        "insurance_status": "active",
        "last_health_check": "2026-02-10",
        "registry_status": "verified",
        "registered_on": "2020-04-01",
    },
    "IN14KA000002": {
        "pashu_aadhaar_id": "IN14KA000002",
        "species": "cattle",
        "breed": "HF Crossbreed",
        "sex": "female",
        "date_of_birth": "2021-08-20",
        "district": "Mandya",
        "state": "Karnataka",
        "owner_name": "Lakshmi Devi",
        "owner_aadhaar_last4": "7832",
        "vaccination_status": "overdue",
        "insurance_status": "expired",
        "last_health_check": "2025-11-05",
        "registry_status": "verified",
        "registered_on": "2021-09-15",
    },
    "IN14KA000003": {
        "pashu_aadhaar_id": "IN14KA000003",
        "species": "goat",
        "breed": "Osmanabadi",
        "sex": "female",
        "date_of_birth": "2023-01-10",
        "district": "Mysore",
        "state": "Karnataka",
        "owner_name": "Venkatesh Gowda",
        "owner_aadhaar_last4": "9156",
        "vaccination_status": "up_to_date",
        "insurance_status": "none",
        "last_health_check": "2026-03-20",
        "registry_status": "verified",
        "registered_on": "2023-02-05",
    },
}


def lookup_animal(pashu_aadhaar_id: str) -> dict | None:
    """Look up an animal in the national Bharat Pashudhan registry (mock)."""
    record = MOCK_REGISTRY.get(pashu_aadhaar_id.upper())
    if record is None:
        return None
    return {
        **record,
        "lookup_timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "Bharat Pashudhan National Database",
        "api_version": "v1.0-mock",
    }


def sync_animal(animal_id: UUID) -> dict:
    """Mock sync of local animal record with national registry."""
    return {
        "animal_id": str(animal_id),
        "sync_status": "success",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "fields_updated": ["vaccination_status", "insurance_status", "last_health_check"],
        "next_sync_due": (date.today().replace(month=date.today().month % 12 + 1)).isoformat(),
        "message": "Animal record synchronized with Bharat Pashudhan registry.",
    }
