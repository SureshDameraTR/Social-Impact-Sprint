"""Pydantic schemas for IoT device and telemetry endpoints."""

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Device schemas
# ---------------------------------------------------------------------------

class IoTDeviceRead(BaseModel):
    device_id: str
    animal_id: str | None = None
    type: str
    status: str
    battery_pct: int | None = None
    firmware: str | None = None
    lat: float | None = None
    lng: float | None = None
    last_seen: str | None = None
    firmware_version: str | None = None
    assigned_animal_id: str | None = None


class IoTDeviceListResponse(BaseModel):
    data: list[IoTDeviceRead]
    total: int


# ---------------------------------------------------------------------------
# Device type aggregation
# ---------------------------------------------------------------------------

class DeviceTypeCount(BaseModel):
    name: str
    total: int
    online: int
    offline: int


# ---------------------------------------------------------------------------
# Telemetry schemas
# ---------------------------------------------------------------------------

class TelemetryMetric(BaseModel):
    type: str
    value: float | dict[str, float]
    unit: str


class TelemetryReading(BaseModel):
    device_id: str
    animal_id: str | None = None
    timestamp: str
    metrics: list[TelemetryMetric]
    battery_pct: int | None = None
    rssi: int | None = None


class TelemetryListResponse(BaseModel):
    data: list[TelemetryReading]
    total: int
