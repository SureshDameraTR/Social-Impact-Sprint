import enum
from datetime import date, datetime

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_kn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    withdrawal_milk_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    withdrawal_meat_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    species_applicable: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    administrations = relationship(
        "MedicineAdministration", back_populates="medicine", foreign_keys="MedicineAdministration.medicine_id"
    )


class MedicineAdministration(Base):
    __tablename__ = "medicine_administrations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    animal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False
    )
    medicine_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medicines.id"), nullable=False
    )
    administered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    withdrawal_milk_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    withdrawal_meat_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    animal = relationship("Animal", foreign_keys=[animal_id])
    medicine = relationship("Medicine", back_populates="administrations", foreign_keys=[medicine_id])
