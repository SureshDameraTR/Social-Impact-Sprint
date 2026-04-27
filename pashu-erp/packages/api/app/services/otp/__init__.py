from app.config import settings
from app.services.otp.base import OTPProvider


def get_otp_provider() -> OTPProvider:
    if settings.environment == "development":
        from app.services.otp.console import ConsoleOTPProvider

        return ConsoleOTPProvider()

    # Twilio takes priority when configured
    if settings.twilio_account_sid and settings.twilio_auth_token:
        from app.services.otp.twilio import TwilioOTPProvider

        allowed = None
        if settings.twilio_allowed_phones:
            allowed = {p.strip() for p in settings.twilio_allowed_phones.split(",") if p.strip()}

        return TwilioOTPProvider(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
            settings.twilio_from_number,
            allowed_phones=allowed,
        )

    if settings.sarvam_api_key:
        from app.services.otp.sarvam import SarvamOTPProvider

        return SarvamOTPProvider(settings.sarvam_api_key, settings.sarvam_base_url)

    raise RuntimeError(
        "No SMS provider configured. Set TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN, "
        "or SARVAM_API_KEY, or use ENVIRONMENT=development for console OTP."
    )
