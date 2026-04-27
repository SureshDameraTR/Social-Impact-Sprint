from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class WeatherAlertSeverity(str, Enum):
    low = "low"
    moderate = "moderate"
    severe = "severe"
    extreme = "extreme"


class WeatherAlertCreate(BaseModel):
    district: str = Field(..., max_length=100)
    alert_type: str = Field(..., max_length=50)
    severity: WeatherAlertSeverity
    description: str | None = None
    valid_from: datetime
    valid_to: datetime
    source: str = "IMD"


class WeatherAlertRead(BaseModel):
    id: UUID
    district: str
    alert_type: str
    severity: WeatherAlertSeverity
    description: str | None = None
    valid_from: datetime
    valid_to: datetime
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WeatherForecast(BaseModel):
    date: date
    district: str
    temp_min: float
    temp_max: float
    humidity: float
    rainfall_mm: float
    wind_speed: float
    condition: str
    heat_stress_index: float
