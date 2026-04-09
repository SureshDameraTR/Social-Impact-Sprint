import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, enum.Enum):
    farmer = "farmer"
    admin = "admin"
    vet = "vet"
    milk_center = "milk_center"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    role: Mapped[str] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    lang_pref: Mapped[str] = mapped_column(String(5), default="kn", server_default="kn")
    location_district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_state: Mapped[str] = mapped_column(String(50), default="Karnataka", server_default="Karnataka")
    village_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    animals = relationship("Animal", back_populates="owner", foreign_keys="Animal.user_id", lazy="selectin")
    yield_logs = relationship("YieldLog", back_populates="user", foreign_keys="YieldLog.user_id", lazy="noload")
    transactions = relationship("Transaction", back_populates="user", foreign_keys="Transaction.user_id", lazy="noload")
    sell_records = relationship("SellRecord", back_populates="user", foreign_keys="SellRecord.user_id", lazy="noload")
