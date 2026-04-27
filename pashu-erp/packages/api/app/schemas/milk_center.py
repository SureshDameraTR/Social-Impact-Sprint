"""Pydantic schemas for milk collection center endpoints."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class MilkReceiveRequest(BaseModel):
    center_id: UUID
    farmer_user_id: UUID
    quantity_liters: Decimal = Field(..., gt=0, le=100, max_digits=6, decimal_places=2)
    fat_pct: Decimal = Field(
        ..., ge=Decimal("1.0"), le=Decimal("12.0"), max_digits=4, decimal_places=2
    )
    snf_pct: Decimal = Field(
        ..., ge=Decimal("6.0"), le=Decimal("12.0"), max_digits=4, decimal_places=2
    )
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
    quantity_liters: Decimal = Field(..., max_digits=6, decimal_places=2)
    fat_pct: Decimal = Field(..., max_digits=4, decimal_places=2)
    snf_pct: Decimal = Field(..., max_digits=4, decimal_places=2)
    rate_per_liter: Decimal = Field(..., max_digits=8, decimal_places=2)
    total_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    shift: str
    collected_at: str | None = None


class ShiftSummary(BaseModel):
    liters: Decimal = Field(..., max_digits=10, decimal_places=2)
    farmers: int


class DailyReportSummary(BaseModel):
    total_liters: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_amount_inr: Decimal = Field(..., max_digits=12, decimal_places=2)
    farmer_count: int
    record_count: int
    avg_fat_pct: Decimal = Field(..., max_digits=4, decimal_places=2)
    avg_snf_pct: Decimal = Field(..., max_digits=4, decimal_places=2)


class DailyReportResponse(BaseModel):
    center_id: str
    date: str
    summary: DailyReportSummary
    morning: ShiftSummary
    evening: ShiftSummary


class FarmerSettlementItem(BaseModel):
    farmer_user_id: str
    total_liters: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_amount_inr: Decimal = Field(..., max_digits=12, decimal_places=2)
    deliveries: int
    avg_fat_pct: Decimal = Field(..., max_digits=4, decimal_places=2)
    avg_snf_pct: Decimal = Field(..., max_digits=4, decimal_places=2)


class FarmerSettlementsResponse(BaseModel):
    center_id: str
    period_days: int
    settlements: list[FarmerSettlementItem]
    total_farmers: int
    total_payout_inr: Decimal = Field(..., max_digits=12, decimal_places=2)


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
