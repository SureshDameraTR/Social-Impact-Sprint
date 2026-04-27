from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import strip_html as _strip_html


class ProductType(str, Enum):
    milk = "milk"
    eggs = "eggs"
    goat_products = "goat_products"
    sheep_products = "sheep_products"
    manure = "manure"
    wool = "wool"
    other = "other"


class SellRecordCreate(BaseModel):
    product_type: ProductType
    quantity: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    unit: str = Field(..., max_length=20)
    price_per_unit: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    buyer_name: str | None = Field(None, max_length=200)
    buyer_phone: str | None = Field(None, max_length=15)
    notes: str | None = Field(None, max_length=500)

    @field_validator("buyer_name", "notes", mode="before")
    @classmethod
    def strip_html_tags(cls, v: str | None) -> str | None:
        return _strip_html(v)


class SellRecordRead(BaseModel):
    id: UUID
    user_id: UUID
    product_type: ProductType
    quantity: Decimal = Field(..., max_digits=10, decimal_places=2)
    unit: str
    price_per_unit: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    buyer_name: str | None = None
    buyer_phone: str | None = None
    sold_at: datetime
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SellRecordListResponse(BaseModel):
    data: list[SellRecordRead]
    total: int
    limit: int
    offset: int


class MarketplaceSummary(BaseModel):
    total_sales: Decimal = Field(..., max_digits=10, decimal_places=2)
    total_revenue: Decimal = Field(..., max_digits=10, decimal_places=2)
    sales_count: int
    by_product: dict[str, Decimal]


class ProductPriceRate(BaseModel):
    product_type: str
    unit: str
    min_price: Decimal = Field(..., max_digits=10, decimal_places=2)
    max_price: Decimal = Field(..., max_digits=10, decimal_places=2)
    avg_price: Decimal = Field(..., max_digits=10, decimal_places=2)
    district: str
