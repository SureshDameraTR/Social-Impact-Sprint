from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import OTPRequest, OTPVerify, TokenResponse

router = APIRouter(prefix="/v1/auth", tags=["auth"])

MOCK_OTP = "123456"


@router.post("/request-otp")
async def request_otp(body: OTPRequest):
    return {"message": "OTP sent successfully", "phone": body.phone}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    if body.otp != MOCK_OTP:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")

    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()

    if not user:
        user = User(phone=body.phone, name=f"Farmer {body.phone[-4:]}", role="farmer", lang_pref="kn")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "phone": user.phone,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
    }
    access_token = jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        role=user.role,
        name=user.name,
    )
