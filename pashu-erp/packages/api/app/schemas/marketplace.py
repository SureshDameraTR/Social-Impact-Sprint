from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


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
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    price_per_unit: float = Field(..., gt=0)
    buyer_name: str | None = Field(None, max_length=200)
    buyer_phone: str | None = Field(None, max_length=15)
    notes: str | None = Field(None, max_length=500)


class SellRecordRead(BaseModel):
    id: UUID
    user_id: UUID
    product_type: ProductType
    quantity: float
    unit: str
    price_per_unit: float
    total_amount: float
    buyer_name: str | None = None
    buyer_phone: str | None = None
    sold_at: datetime
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MarketplaceSummary(BaseModel):
    total_sales: float
    total_revenue: float
    sales_count: int
    by_product: dict[str, float]


class ProductPriceRate(BaseModel):
    product_type: str
    unit: str
    min_price: float
    max_price: float
    avg_price: float
    district: str
