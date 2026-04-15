"""Pydantic schemas for Bharat Pashudhan national registry endpoints."""

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Nested structures from the registry
# ---------------------------------------------------------------------------

class RegistryOwner(BaseModel):
    name: str
    aadhaar_last4: str | None = None
    mobile: str | None = None
    village: str | None = None
    block: str | None = None
    district: str | None = None
    state: str | None = None


class RegistryGPS(BaseModel):
    lat: float
    lng: float


class RegistryVaccination(BaseModel):
    type: str
    date: str
    batch: str | None = None
    vaccinator: str | None = None


class RegistryInsurance(BaseModel):
    policy_number: str | None = None
    scheme: str | None = None
    valid_until: str | None = None


# ---------------------------------------------------------------------------
# Lookup response
# ---------------------------------------------------------------------------

class RegistryAnimalLookup(BaseModel):
    pashu_aadhaar_id: str
    species: str
    breed: str
    breed_code: str | None = None
    sex: str
    date_of_birth: str | None = None
    owner: RegistryOwner | None = None
    dam_tag: str | None = None
    sire_tag: str | None = None
    gps: RegistryGPS | None = None
    vaccinations: list[RegistryVaccination] = []
    insurance: RegistryInsurance | None = None
    source: str | None = None
    lookup_timestamp: str | None = None


# ---------------------------------------------------------------------------
# Sync response
# ---------------------------------------------------------------------------

class RegistrySyncResponse(BaseModel):
    status: str
    animal_id: str
    last_sync: str
    registry_version: str | None = None
