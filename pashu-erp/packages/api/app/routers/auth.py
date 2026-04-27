import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.csrf import generate_csrf_token
from app.middleware.rate_limit import limiter
from app.models.auth import RefreshToken
from app.models.otp import OTPRequest as OTPRequestModel
from app.models.user import User
from app.schemas.auth import (
    AuthErrorCode,
    AuthUserResponse,
    OTPRequest,
    OTPVerify,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services.otp import get_otp_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["auth"])

_otp_provider = None

STAFF_ROLES = {"admin", "vet", "milk_center"}

ACCESS_TOKEN_EXPIRY = timedelta(minutes=settings.jwt_expire_minutes)
REFRESH_TOKEN_EXPIRY = timedelta(days=settings.jwt_refresh_expiry_days)

MAX_OTP_REQUESTS_PER_HOUR = settings.max_otp_requests_per_hour
MAX_OTP_ATTEMPTS = settings.max_otp_attempts
OTP_EXPIRY_MINUTES = settings.otp_expiry_minutes


def _get_provider():
    global _otp_provider
    if _otp_provider is None:
        _otp_provider = get_otp_provider()
    return _otp_provider


def _auth_error(status_code: int, code: AuthErrorCode, detail: str):
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"X-Error-Code": code.value},
    )


def _generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def _hash_refresh_token(raw_token: str) -> str:
    """Hash a raw refresh token using SHA-256 for storage."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _create_access_token(user_id: str, role: str) -> str:
    """Create a short-lived JWT access token."""
    token_data = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRY,
    }
    return jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def _create_refresh_token(user_id: str, db: AsyncSession) -> str:
    """Create a refresh token, store its hash in DB, and return the raw token."""
    raw_token = secrets.token_urlsafe(48)
    token_hash = _hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRY

    refresh_record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_record)
    await db.flush()
    return raw_token


def _set_auth_cookies(response: Response, token: str, csrf_token: str, max_age: int):
    secure = settings.environment != "development"
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


def _clear_auth_cookies(response: Response):
    response.delete_cookie("token", path="/")
    response.delete_cookie("csrf_token", path="/")


@router.post("/request-otp")
@limiter.limit("5/minute")
async def request_otp(request: Request, body: OTPRequest, db: AsyncSession = Depends(get_db)):
    # CRIT-2 fix: check rate limit BEFORE any mutation.
    # Since `phone` has a unique constraint (only one row per phone), we track
    # request_count on the record itself to survive the upsert cycle.
    result = await db.execute(select(OTPRequestModel).where(OTPRequestModel.phone == body.phone))
    existing = result.scalar_one_or_none()

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    if existing and existing.created_at > one_hour_ago:
        if existing.request_count >= MAX_OTP_REQUESTS_PER_HOUR:
            raise _auth_error(
                status.HTTP_429_TOO_MANY_REQUESTS,
                AuthErrorCode.RATE_LIMITED,
                "Too many OTP requests. Try again later.",
            )

    otp = _generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()
    now = datetime.now(timezone.utc)

    # HIGH-5 fix: upsert instead of DELETE+INSERT to avoid race condition
    # with the unique constraint on phone.
    if existing:
        # If the last request was within the hour, increment; otherwise reset.
        new_count = (existing.request_count + 1) if existing.created_at > one_hour_ago else 1
        await db.execute(
            update(OTPRequestModel)
            .where(OTPRequestModel.phone == body.phone)
            .values(
                otp_hash=otp_hash,
                attempts=0,
                expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
                created_at=now,
                request_count=new_count,
            )
        )
    else:
        otp_record = OTPRequestModel(
            phone=body.phone,
            otp_hash=otp_hash,
            expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
            request_count=1,
        )
        db.add(otp_record)

    await db.commit()

    provider = _get_provider()
    await provider.send_otp(body.phone, otp)

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
@limiter.limit("5/minute")
async def verify_otp(request: Request, body: OTPVerify, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OTPRequestModel).where(OTPRequestModel.phone == body.phone))
    otp_record = result.scalar_one_or_none()

    # MED-3 fix: use a single generic message for all OTP verification failures
    # to prevent attackers from enumerating which phones have active OTPs.
    _otp_fail_msg = "Invalid or expired OTP"

    if not otp_record:
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            _otp_fail_msg,
        )

    if datetime.now(timezone.utc) > otp_record.expires_at:
        await db.execute(delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone))
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            _otp_fail_msg,
        )

    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        await db.execute(delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone))
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            _otp_fail_msg,
        )

    if not bcrypt.checkpw(body.otp.encode(), otp_record.otp_hash.encode()):
        otp_record.attempts += 1
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            _otp_fail_msg,
        )

    await db.execute(delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone))

    user_result = await db.execute(
        select(User).where(User.phone == body.phone, User.deleted_at.is_(None))
    )
    user = user_result.scalar_one_or_none()

    if not user:
        user = User(
            phone=body.phone,
            name=f"Farmer {body.phone[-4:]}",
            role="farmer",
            lang_pref="kn",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if body.client_type == "web" and user.role not in STAFF_ROLES:
        raise _auth_error(
            status.HTTP_403_FORBIDDEN,
            AuthErrorCode.ROLE_NOT_AUTHORIZED,
            "This portal is for staff. Please use the PashuRaksha mobile app.",
        )

    # Issue both access and refresh tokens.
    access_token = _create_access_token(str(user.id), user.role)
    refresh_token_raw = await _create_refresh_token(str(user.id), db)
    await db.commit()

    csrf_token = generate_csrf_token(str(user.id), int(time.time()))
    max_age_seconds = int(ACCESS_TOKEN_EXPIRY.total_seconds())

    if body.client_type == "mobile":
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_raw,
            user_id=str(user.id),
            role=user.role,
            name=user.name,
            location_district=user.location_district,
        )

    response = JSONResponse(
        content=AuthUserResponse(
            user_id=str(user.id),
            role=user.role,
            name=user.name,
            location_district=user.location_district,
        ).model_dump()
    )
    _set_auth_cookies(response, access_token, csrf_token, max_age_seconds)
    return response


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_token(
    request: Request, body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """Exchange a valid refresh token for a new access + refresh token pair.

    This endpoint does NOT require Depends(get_current_user) -- it validates
    the caller via the refresh token itself (token rotation pattern).
    """
    incoming_hash = _hash_refresh_token(body.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == incoming_hash)
    )
    stored = result.scalar_one_or_none()

    if not stored:
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.TOKEN_INVALID,
            "Invalid refresh token",
        )

    if stored.revoked_at is not None:
        # Possible token reuse attack -- revoke ALL tokens for this user.
        logger.warning(
            "Revoked refresh token reuse detected",
            extra={"user_id": str(stored.user_id)},
        )
        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == stored.user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.TOKEN_INVALID,
            "Refresh token has been revoked",
        )

    if datetime.now(timezone.utc) > stored.expires_at:
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.TOKEN_EXPIRED,
            "Refresh token expired",
        )

    # Look up the user to include role in the new access token.
    user_result = await db.execute(
        select(User).where(User.id == stored.user_id, User.deleted_at.is_(None))
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.TOKEN_INVALID,
            "User not found",
        )

    # Revoke the old refresh token (rotation).
    stored.revoked_at = datetime.now(timezone.utc)

    # Issue new pair.
    new_access_token = _create_access_token(str(user.id), user.role)
    new_refresh_token_raw = await _create_refresh_token(str(user.id), db)
    await db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token_raw,
        "token_type": "bearer",
    }


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return AuthUserResponse(
        user_id=str(current_user.id),
        role=current_user.role,
        name=current_user.name,
        location_district=current_user.location_district,
    )


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke all active refresh tokens for the current user and clear cookies."""
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == str(current_user.id),
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await db.commit()

    response = JSONResponse(content={"message": "Logged out"})
    _clear_auth_cookies(response)
    return response
