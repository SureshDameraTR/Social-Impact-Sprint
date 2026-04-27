"""Pydantic schemas for map/GIS data endpoints."""

from pydantic import BaseModel


class HealthAlertPoint(BaseModel):
    type: str  # "health_alert"
    id: str
    label: str
    district: str | None = None
    village_code: str | None = None
    risk_score: float | None = None
    species: str | None = None
    date: str | None = None


class MilkCenterPoint(BaseModel):
    type: str  # "milk_center"
    id: str
    label: str
    district: str | None = None
    village_code: str | None = None


class CommunityAlertPoint(BaseModel):
    type: str  # "community_alert"
    id: str
    label: str
    lat: float | None = None
    lon: float | None = None
    radius_km: float | None = None
    severity: str | None = None
    verified: bool | None = None


class FarmerClusterPoint(BaseModel):
    type: str  # "farmer_cluster"
    village_code: str | None = None
    district: str | None = None
    farmer_count: int


# Union-style: all point types share a superset of fields
class MapPoint(BaseModel):
    type: str
    id: str | None = None
    label: str | None = None
    district: str | None = None
    village_code: str | None = None
    risk_score: float | None = None
    species: str | None = None
    date: str | None = None
    lat: float | None = None
    lon: float | None = None
    radius_km: float | None = None
    severity: str | None = None
    verified: bool | None = None
    farmer_count: int | None = None


class MapPointsResponse(BaseModel):
    data: list[MapPoint]
    total: int
