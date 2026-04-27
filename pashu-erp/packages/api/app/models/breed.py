from sqlalchemy import Boolean, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SpeciesRef(TimestampMixin, Base):
    __tablename__ = "species_ref"

    code: Mapped[str] = mapped_column(String(30), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_kn: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name_hi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)


class Breed(TimestampMixin, Base):
    __tablename__ = "breeds"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(100), nullable=True)
    species_code: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("species_ref.code"),
        nullable=False,
        index=True,
    )
    origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nbagr_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_indigenous: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
