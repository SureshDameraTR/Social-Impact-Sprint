"""DPDP Act 2023 — Data processing consent records."""

import enum

from sqlalchemy import Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class ConsentPurpose(str, enum.Enum):
    livestock_management = "livestock_management"
    health_records = "health_records"
    financial_transactions = "financial_transactions"
    government_schemes = "government_schemes"
    analytics = "analytics"


class ConsentStatus(str, enum.Enum):
    granted = "granted"
    withdrawn = "withdrawn"


class Consent(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    purpose: Mapped[ConsentPurpose] = mapped_column(
        Enum(ConsentPurpose),
        nullable=False,
    )
    status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus),
        nullable=False,
        default=ConsentStatus.granted,
    )
    consent_text: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
