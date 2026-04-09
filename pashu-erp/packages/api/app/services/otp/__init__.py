from app.config import settings
from app.services.otp.base import OTPProvider


def get_otp_provider() -> OTPProvider:
    if settings.environment == "development":
        from app.services.otp.console import ConsoleOTPProvider
        return ConsoleOTPProvider()
    else:
        from app.services.otp.sarvam import SarvamOTPProvider
        if not settings.sarvam_api_key:
            raise RuntimeError("SARVAM_API_KEY is required in non-development environments")
        return SarvamOTPProvider(settings.sarvam_api_key)
