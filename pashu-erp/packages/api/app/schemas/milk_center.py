"""Pydantic schemas for milk collection center endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class MilkReceiveRequest(BaseModel):
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: float = Field(..., gt=0, le=100)
    fat_pct: float = Field(..., ge=1.0, le=12.0)
    snf_pct: float = Field(..., ge=6.0, le=12.0)
    shift: str = Field(..., pattern="^(morning|evening)$")


class QuickEnrollRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    aadhaar: str = Field(..., pattern=r"^\d{12}$")
    village_code: str | None = Field(None, max_length=20)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class MyCenterResponse(BaseModel):
    id: str
    name: str
    code: str
    district: str | None = None


class MilkReceiveResponse(BaseModel):
    id: str
    center_id: str
    farmer_user_id: str
    quantity_liters: float
    fat_pct: float
    snf_pct: float
    rate_per_liter: float
    total_amount: float
    shift: str
    collected_at: str | None = None


class ShiftSummary(BaseModel):
    liters: float
    farmers: int


class DailyReportSummary(BaseModel):
    total_liters: float
    total_amount_inr: float
    farmer_count: int
    record_count: int
    avg_fat_pct: float
    avg_snf_pct: float


class DailyReportResponse(BaseModel):
    center_id: str
    date: str
    summary: DailyReportSummary
    morning: ShiftSummary
    evening: ShiftSummary


class FarmerSettlementItem(BaseModel):
    farmer_user_id: str
    total_liters: float
    total_amount_inr: float
    deliveries: int
    avg_fat_pct: float
    avg_snf_pct: float


class FarmerSettlementsResponse(BaseModel):
    center_id: str
    period_days: int
    settlements: list[FarmerSettlementItem]
    total_farmers: int
    total_payout_inr: float


class FarmerSearchResult(BaseModel):
    id: str
    name: str | None = None
    phone: str | None = None
    aadhaar_last4: str | None = None
    village_code: str | None = None
    district: str | None = None


class QuickEnrollResponse(BaseModel):
    id: str
    name: str
    phone: str
    aadhaar_last4: str | None = None
    message: str
