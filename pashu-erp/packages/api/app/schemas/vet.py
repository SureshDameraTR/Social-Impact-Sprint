"""Pydantic schemas for veterinary consultation endpoints."""

from datetime import date
from enum import Enum

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Enums (mirror model enums for schema-level validation)
# ---------------------------------------------------------------------------

class ConsultationStatus(str, Enum):
    pending = "pending"
    in_review = "in_review"
    diagnosed = "diagnosed"
    closed = "closed"


class ConsultationPriority(str, Enum):
    routine = "routine"
    urgent = "urgent"
    emergency = "emergency"


class ConsultationChannel(str, Enum):
    photo = "photo"
    walk_in = "walk_in"
    referral = "referral"


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class DiagnoseBody(BaseModel):
    diagnosis: str
    prescription: str | None = None
    follow_up_date: date | None = None


class VideoLinkBody(BaseModel):
    video_call_url: str


# ---------------------------------------------------------------------------
# Nested read schemas
# ---------------------------------------------------------------------------

class OwnerBrief(BaseModel):
    id: str
    name: str | None = None
    phone: str | None = None
    village_code: str | None = None
    location_district: str | None = None


class AnimalBrief(BaseModel):
    id: str
    species: str | None = None
    name: str | None = None
    breed: str | None = None
    owner: OwnerBrief | None = None


class FarmerBrief(BaseModel):
    id: str
    name: str | None = None


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class VetCaseRead(BaseModel):
    id: str
    animal_id: str
    farmer_id: str
    vet_id: str | None = None
    status: str
    priority: str
    channel: str
    farmer_notes: str | None = None
    photo_urls: list[str] | None = None
    diagnosis: str | None = None
    prescription: str | None = None
    follow_up_date: str | None = None
    video_call_url: str | None = None
    district: str
    created_at: str | None = None
    updated_at: str | None = None
    animal: AnimalBrief | None = None
    farmer: FarmerBrief | None = None


class VetCaseListResponse(BaseModel):
    data: list[VetCaseRead]
    skip: int
    limit: int


class VetMyCasesResponse(BaseModel):
    data: list[VetCaseRead]


# ---------------------------------------------------------------------------
# Dashboard schemas
# ---------------------------------------------------------------------------

class VetDashboardStats(BaseModel):
    pending_cases: int
    diagnosed_today: int
    district_animals: int
    active_alerts: int


class VetDashboardAlertsResponse(BaseModel):
    community_alerts: list[dict[str, object]]
    health_events: list[dict[str, object]]
