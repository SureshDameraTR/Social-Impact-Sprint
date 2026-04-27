"""DPDP Act 2023 consent management endpoints."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.consent import Consent, ConsentStatus
from app.models.user import User
from app.schemas.consent import (
    ConsentGrantRequest,
    ConsentListResponse,
    ConsentResponse,
    ConsentWithdrawRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/consent", tags=["DPDP Consent"])


@router.post("/grant", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def grant_consent(
    body: ConsentGrantRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record explicit consent for a data processing purpose (DPDP Act s.6)."""
    consent = Consent(
        user_id=current_user.id,
        purpose=body.purpose,
        status=ConsentStatus.granted,
        consent_text=body.consent_text,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:512],
    )
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    return consent


@router.post("/withdraw", response_model=ConsentResponse)
async def withdraw_consent(
    body: ConsentWithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Withdraw consent for a data processing purpose (DPDP Act s.6(6))."""
    # Find the most recent granted consent for this purpose
    stmt = (
        select(Consent)
        .where(
            Consent.user_id == current_user.id,
            Consent.purpose == body.purpose,
            Consent.status == ConsentStatus.granted,
            Consent.deleted_at.is_(None),
        )
        .order_by(Consent.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    consent = result.scalar_one_or_none()

    if consent is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"No active consent found for purpose '{body.purpose.value}'",
        )

    consent.status = ConsentStatus.withdrawn
    await db.commit()
    await db.refresh(consent)
    return consent


@router.get("/my", response_model=ConsentListResponse)
async def list_my_consents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all consent records for the current user."""
    count_stmt = (
        select(func.count())
        .select_from(Consent)
        .where(Consent.user_id == current_user.id, Consent.deleted_at.is_(None))
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    stmt = (
        select(Consent)
        .where(Consent.user_id == current_user.id, Consent.deleted_at.is_(None))
        .order_by(Consent.created_at.desc())
    )
    result = await db.execute(stmt)
    return {"data": result.scalars().all(), "total": total}


@router.delete("/erasure-request", status_code=status.HTTP_202_ACCEPTED)
async def request_erasure(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Request right to erasure (DPDP Act s.12). Soft-marks all user consents for admin review."""
    now = datetime.now(timezone.utc)
    stmt = (
        update(Consent)
        .where(Consent.user_id == current_user.id, Consent.deleted_at.is_(None))
        .values(deleted_at=now)
    )
    await db.execute(stmt)
    await db.commit()

    logger.info("Erasure request filed for user %s", current_user.id)
    return {
        "detail": "Erasure request accepted. Your data will be reviewed and removed.",
        "user_id": current_user.id,
    }
