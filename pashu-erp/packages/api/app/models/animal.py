import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base, SoftDeleteMixin


class Species(str, enum.Enum):
    cattle = "cattle"
    goat = "goat"
    sheep = "sheep"
    poultry = "poultry"


class BreedType(str, enum.Enum):
    indigenous = "indigenous"
    crossbreed = "crossbreed"
    exotic = "exotic"


class AnimalSex(str, enum.Enum):
    male = "male"
    female = "female"


class Animal(AuditMixin, SoftDeleteMixin, Base):
    __tablename__ = "animals"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    pashu_aadhaar_id: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    species: Mapped[str] = mapped_column(Enum(Species, name="species"), nullable=False)
    breed: Mapped[str] = mapped_column(String(100), nullable=False)
    breed_type: Mapped[str] = mapped_column(Enum(BreedType, name="breed_type"), nullable=False)
    tag_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str] = mapped_column(Enum(AnimalSex, name="animal_sex"), nullable=False)
    lactation_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body_condition_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    is_insured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships — lazy="noload" to prevent automatic eager loading;
    # use selectinload() explicitly in queries that need related data.
    owner = relationship(
        "User", back_populates="animals", foreign_keys=[user_id], lazy="noload",
    )
    health_events = relationship(
        "HealthEvent", back_populates="animal",
        foreign_keys="HealthEvent.animal_id", lazy="noload",
    )
    vaccinations = relationship(
        "Vaccination", back_populates="animal",
        foreign_keys="Vaccination.animal_id", lazy="noload",
    )
    yield_logs = relationship(
        "YieldLog", back_populates="animal",
        foreign_keys="YieldLog.animal_id", lazy="noload",
    )
