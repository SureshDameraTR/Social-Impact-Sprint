import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jose import jwt
import bcrypt
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.otp import OTPRequest as OTPRequestModel
from app.models.user import User
from app.schemas.auth import (
    AuthErrorCode,
    AuthUserResponse,
    OTPRequest,
    OTPVerify,
    TokenResponse,
)
from app.services.otp import get_otp_provider

router = APIRouter(prefix="/v1/auth", tags=["auth"])

_otp_provider = None

STAFF_ROLES = {"admin", "vet", "milk_center"}

DEFAULT_EXPIRY = timedelta(hours=8)
REMEMBER_EXPIRY = timedelta(days=7)

MAX_OTP_REQUESTS_PER_HOUR = 5
MAX_OTP_ATTEMPTS = 3
OTP_EXPIRY_MINUTES = 5


def _get_provider():
    global _otp_provider
    if _otp_provider is None:
        _otp_provider = get_otp_provider()
    return _otp_provider


def _auth_error(status_code: int, code: AuthErrorCode, detail: str):
    return HTTPException(
        status_code=status_code,
        detail={"detail": detail, "code": code.value},
    )


def _generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


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
async def request_otp(body: OTPRequest, db: AsyncSession = Depends(get_db)):
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    result = await db.execute(
        select(OTPRequestModel).where(
            OTPRequestModel.phone == body.phone,
            OTPRequestModel.created_at > one_hour_ago,
        )
    )
    recent = result.scalars().all()
    if len(recent) >= MAX_OTP_REQUESTS_PER_HOUR:
        raise _auth_error(
            status.HTTP_429_TOO_MANY_REQUESTS,
            AuthErrorCode.RATE_LIMITED,
            "Too many OTP requests. Try again later.",
        )

    await db.execute(
        delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
    )

    otp = _generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()
    otp_record = OTPRequestModel(
        phone=body.phone,
        otp_hash=otp_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.add(otp_record)
    await db.commit()

    provider = _get_provider()
    await provider.send_otp(body.phone, otp)

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
async def verify_otp(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            "No OTP request found. Please request a new OTP.",
        )

    if datetime.now(timezone.utc) > otp_record.expires_at:
        await db.execute(
            delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
        )
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_EXPIRED,
            "OTP has expired. Please request a new one.",
        )

    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        await db.execute(
            delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
        )
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_MAX_ATTEMPTS,
            "Too many failed attempts. Please request a new OTP.",
        )

    if not bcrypt.checkpw(body.otp.encode(), otp_record.otp_hash.encode()):
        otp_record.attempts += 1
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            "Invalid OTP. Please try again.",
        )

    await db.execute(
        delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
    )

    user_result = await db.execute(select(User).where(User.phone == body.phone))
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

    expiry = REMEMBER_EXPIRY if body.remember_me else DEFAULT_EXPIRY
    max_age_seconds = int(expiry.total_seconds())
    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "phone": user.phone,
        "exp": datetime.now(timezone.utc) + expiry,
    }
    access_token = jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    csrf_token = secrets.token_urlsafe(32)

    if body.client_type == "mobile":
        return TokenResponse(
            access_token=access_token,
            user_id=str(user.id),
            role=user.role,
            name=user.name,
        )

    response = JSONResponse(
        content=AuthUserResponse(
            user_id=str(user.id),
            role=user.role,
            name=user.name,
        ).model_dump()
    )
    _set_auth_cookies(response, access_token, csrf_token, max_age_seconds)
    return response


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return AuthUserResponse(
        user_id=str(current_user.id),
        role=current_user.role,
        name=current_user.name,
    )


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    _clear_auth_cookies(response)
    return response
