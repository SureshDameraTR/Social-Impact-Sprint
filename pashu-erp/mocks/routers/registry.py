"""Bharat Pashudhan (INAPH) registry mock router."""

import calendar
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from random import Random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/registry", tags=["Registry"])

# ---------------------------------------------------------------------------
# Load breed data at import time
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).parent.parent / "data"
with open(_DATA_DIR / "breeds.json") as _f:
    BREEDS: dict[str, list[dict]] = json.load(_f)

# Flattened list of (species, breed_dict) for weighted selection
_ALL_BREEDS: list[tuple[str, dict]] = []
for _species, _breed_list in BREEDS.items():
    for _b in _breed_list:
        _ALL_BREEDS.append((_species, _b))

# ---------------------------------------------------------------------------
# Realistic Karnataka reference data
# ---------------------------------------------------------------------------
OWNER_SURNAMES = ["Patil", "Hegde", "Gowda", "Kumar", "Naik"]
OWNER_FIRST_NAMES = ["Ramesh", "Suresh", "Mahesh", "Ganesh", "Rajesh",
                     "Lakshmi", "Savitri", "Anita", "Bhagya", "Renuka"]
VILLAGES = ["Navalgund", "Hubli", "Gadag", "Ranebennur", "Haveri",
            "Dharwad", "Belgaum", "Karwar", "Sirsi", "Honnavar"]
BLOCKS = ["Navalgund", "Hubli", "Gadag", "Ranebennur", "Haveri"]
DISTRICTS = ["Dharwad", "Gadag", "Haveri", "Belgaum", "Uttara Kannada"]
VACCINATION_TYPES = ["FMD", "Brucellosis", "PPR", "HS", "BQ"]
VACCINATOR_NAMES = ["Dr. Patil", "Dr. Hegde", "Dr. Gowda", "Dr. Kulkarni", "Dr. Joshi"]
INSURANCE_SCHEMES = ["LISS", "DCCB", "RKBY"]

# GPS bounding box for northern Karnataka
GPS_LAT_RANGE = (14.8, 15.8)
GPS_LNG_RANGE = (74.5, 76.0)

# Pashu Aadhaar format: starts with "IN", 12 chars total
_PASHU_AADHAAR_RE = re.compile(r"^IN[A-Z0-9]{10}$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_from_id(pashu_id: str) -> int:
    """Deterministic integer seed from an ID string."""
    return int(hashlib.sha256(pashu_id.encode()).hexdigest(), 16) % (2**32)


def _generate_animal(pashu_id: str) -> dict:
    """Build a deterministic animal record from the pashu_aadhaar_id."""
    rng = Random(_seed_from_id(pashu_id))

    # Pick species + breed
    species, breed = rng.choice(_ALL_BREEDS)

    # Owner
    first = rng.choice(OWNER_FIRST_NAMES)
    last = rng.choice(OWNER_SURNAMES)
    village = rng.choice(VILLAGES)
    block = rng.choice(BLOCKS)
    district = rng.choice(DISTRICTS)
    mobile_suffix = rng.randint(7000000000, 9999999999)
    aadhaar_last4 = f"{rng.randint(1000, 9999)}"

    # Date of birth: 1-8 years ago from a fixed reference (2026-04-09)
    ref_date = date(2026, 4, 9)
    age_days = rng.randint(365, 365 * 8)
    dob = ref_date - timedelta(days=age_days)

    # Sex
    sex = rng.choice(["male", "female", "female", "female"])  # 75% female

    # GPS
    lat = round(rng.uniform(*GPS_LAT_RANGE), 4)
    lng = round(rng.uniform(*GPS_LNG_RANGE), 4)

    # Dam / sire tags (deterministic from seed)
    dam_num = rng.randint(100000, 999999)
    sire_num = rng.randint(100000, 999999)
    prefix = pashu_id[:6]
    dam_tag = f"{prefix}{dam_num:06d}"
    sire_tag = f"{prefix}{sire_num:06d}"

    # Vaccinations (1-3 records)
    vacc_count = rng.randint(1, 3)
    vaccinations = []
    for _ in range(vacc_count):
        vtype = rng.choice(VACCINATION_TYPES)
        vacc_year = rng.choice([2024, 2025, 2026])
        vacc_month = rng.randint(1, 12)
        vacc_day = rng.randint(1, 28)
        batch_num = rng.randint(1000, 9999)
        vaccinations.append({
            "type": vtype,
            "date": f"{vacc_year}-{vacc_month:02d}-{vacc_day:02d}",
            "batch": f"{vtype}-{vacc_year}-KA-{batch_num}",
            "vaccinator": rng.choice(VACCINATOR_NAMES),
        })

    # Insurance
    scheme = rng.choice(INSURANCE_SCHEMES)
    policy_num = rng.randint(10000, 99999)
    valid_year = rng.choice([2026, 2027])
    valid_month = rng.randint(1, 12)
    last_day = calendar.monthrange(valid_year, valid_month)[1]

    return {
        "pashu_aadhaar_id": pashu_id,
        "species": species,
        "breed": breed["name"],
        "breed_code": breed["code"],
        "sex": sex,
        "date_of_birth": dob.isoformat(),
        "owner": {
            "name": f"{first} {last}",
            "aadhaar_last4": aadhaar_last4,
            "mobile": f"+91{mobile_suffix}",
            "village": village,
            "block": block,
            "district": district,
            "state": "Karnataka",
        },
        "dam_tag": dam_tag,
        "sire_tag": sire_tag,
        "gps": {"lat": lat, "lng": lng},
        "vaccinations": vaccinations,
        "insurance": {
            "policy_number": f"{scheme}-KA-{valid_year}-{policy_num}",
            "scheme": scheme,
            "valid_until": f"{valid_year}-{valid_month:02d}-{last_day:02d}",
        },
        "source": "Bharat Pashudhan National Database",
        "lookup_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class SyncRequest(BaseModel):
    animal_id: str


class SyncResponse(BaseModel):
    status: str
    animal_id: str
    last_sync: str
    registry_version: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/animals/{pashu_aadhaar_id}")
async def get_animal(pashu_aadhaar_id: str):
    """Look up an animal by Pashu Aadhaar ID from the Bharat Pashudhan registry."""
    if not _PASHU_AADHAAR_RE.match(pashu_aadhaar_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Pashu Aadhaar format: must be 12 characters starting with 'IN'. Got: {pashu_aadhaar_id}",
        )
    return _generate_animal(pashu_aadhaar_id)


@router.post("/sync", response_model=SyncResponse)
async def sync_animal(body: SyncRequest):
    """Sync an animal record with the Bharat Pashudhan national database."""
    return SyncResponse(
        status="synced",
        animal_id=body.animal_id,
        last_sync=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        registry_version="2.1",
    )
