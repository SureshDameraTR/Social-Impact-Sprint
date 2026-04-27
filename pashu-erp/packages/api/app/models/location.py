"""Location hierarchy models — State, District, SubDistrict, Village.

Uses India's LGD (Local Government Directory) codes as natural integer primary keys.
These are government-assigned identifiers, not auto-generated UUIDs.
"""

from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class State(TimestampMixin, Base):
    __tablename__ = "states"

    lgd_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name_local: Mapped[str | None] = mapped_column(String(100), nullable=True)


class District(TimestampMixin, Base):
    __tablename__ = "districts"

    lgd_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_lgd_code: Mapped[int] = mapped_column(
        Integer, ForeignKey("states.lgd_code"), nullable=False, index=True
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)


class SubDistrict(TimestampMixin, Base):
    __tablename__ = "sub_districts"

    lgd_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district_lgd_code: Mapped[int] = mapped_column(
        Integer, ForeignKey("districts.lgd_code"), nullable=False, index=True
    )


class Village(TimestampMixin, Base):
    __tablename__ = "villages"

    lgd_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_local: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sub_district_lgd_code: Mapped[int] = mapped_column(
        Integer, ForeignKey("sub_districts.lgd_code"), nullable=False, index=True
    )
    pincode: Mapped[str | None] = mapped_column(String(6), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_villages_sub_district_name", "sub_district_lgd_code", "name"),
    )
