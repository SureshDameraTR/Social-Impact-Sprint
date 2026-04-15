import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class MilkSession(str, enum.Enum):
    morning = "morning"
    evening = "evening"


class YieldLog(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "yield_logs"
    __table_args__ = (
        UniqueConstraint(
            "animal_id", "session", "recorded_at",
            name="uq_yield_animal_session_date",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    animal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    quantity_liters: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    session: Mapped[str] = mapped_column(Enum(MilkSession, name="milk_session"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships — lazy="noload" to prevent automatic eager loading
    animal = relationship(
        "Animal", back_populates="yield_logs",
        foreign_keys=[animal_id], lazy="noload",
    )
    user = relationship(
        "User", back_populates="yield_logs",
        foreign_keys=[user_id], lazy="noload",
    )


class MilkCollectionCenter(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "milk_collection_centers"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    manager_user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manager = relationship("User", foreign_keys=[manager_user_id], lazy="noload")
    collection_records = relationship(
        "MilkCollectionRecord", back_populates="center",
        foreign_keys="MilkCollectionRecord.center_id", lazy="noload",
    )


class MilkCollectionRecord(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "milk_collection_records"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    center_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("milk_collection_centers.id"), nullable=False
    )
    farmer_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    quantity_liters: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fat_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    snf_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    rate_per_liter: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    shift: Mapped[str] = mapped_column(
        Enum(MilkSession, name="milk_session", create_type=False),
        nullable=False,
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    # Relationships — lazy="noload" to prevent automatic eager loading
    center = relationship(
        "MilkCollectionCenter", back_populates="collection_records",
        foreign_keys=[center_id], lazy="noload",
    )
    farmer = relationship("User", foreign_keys=[farmer_user_id], lazy="noload")
