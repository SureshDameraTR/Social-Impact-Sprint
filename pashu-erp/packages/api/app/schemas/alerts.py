from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class CommunityAlertSeverity(str, Enum):
    low = "low"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"


class CommunityAlertCreate(BaseModel):
    disease_name: str = Field(..., max_length=200)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=5.0, gt=0)
    severity: CommunityAlertSeverity


class CommunityAlertRead(BaseModel):
    id: UUID
    reported_by: UUID
    disease_name: str
    lat: float
    lon: float
    radius_km: float
    severity: CommunityAlertSeverity
    verified: bool
    created_at: datetime
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}
