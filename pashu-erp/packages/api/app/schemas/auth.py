from enum import Enum

from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$", examples=["+919876543210"])


class OTPVerify(BaseModel):
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6, examples=["123456"])
    remember_me: bool = False
    client_type: str = Field(default="web", pattern=r"^(web|mobile)$")


class AuthUserResponse(BaseModel):
    """Response body for verify-otp and /me endpoints."""
    user_id: str
    role: str
    name: str | None = None


class TokenResponse(AuthUserResponse):
    """Extended response for mobile clients that receive token in body."""
    access_token: str
    token_type: str = "bearer"


class AuthErrorCode(str, Enum):
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_INVALID = "OTP_INVALID"
    OTP_MAX_ATTEMPTS = "OTP_MAX_ATTEMPTS"
    RATE_LIMITED = "RATE_LIMITED"
    ROLE_NOT_AUTHORIZED = "ROLE_NOT_AUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"


class AuthErrorResponse(BaseModel):
    detail: str
    code: AuthErrorCode
