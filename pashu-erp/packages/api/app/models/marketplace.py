import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin, TimestampMixin


class ProductType(str, enum.Enum):
    milk = "milk"
    eggs = "eggs"
    goat_products = "goat_products"
    sheep_products = "sheep_products"
    manure = "manure"
    wool = "wool"
    other = "other"


class SellRecord(TimestampMixin, AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "sell_records"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sell_records_quantity_positive"),
        CheckConstraint("price_per_unit > 0", name="ck_sell_records_price_positive"),
        CheckConstraint("total_amount >= 0", name="ck_sell_records_total_non_negative"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    product_type: Mapped[str] = mapped_column(
        Enum(ProductType, name="product_type"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    buyer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    buyer_phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user = relationship(
        "User",
        back_populates="sell_records",
        foreign_keys=[user_id],
        lazy="noload",
    )
