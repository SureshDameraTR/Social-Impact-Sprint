import enum
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, Numeric, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PolicyStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    claimed = "claimed"


class ClaimStatus(str, enum.Enum):
    filed = "filed"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    animal_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("animals.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    policy_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    premium_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    coverage_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(PolicyStatus, name="policy_status"), nullable=False, default="active"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    animal = relationship("Animal", foreign_keys=[animal_id], lazy="selectin")
    claims = relationship("InsuranceClaim", back_populates="policy", foreign_keys="InsuranceClaim.policy_id", lazy="selectin")


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    policy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("insurance_policies.id"), nullable=False
    )
    claim_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(ClaimStatus, name="claim_status"), nullable=False, default="filed"
    )
    filed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    policy = relationship("InsurancePolicy", back_populates="claims", foreign_keys=[policy_id], lazy="selectin")
