import logging

from app.services.otp.base import OTPProvider

logger = logging.getLogger("pashuraksha.otp")


class ConsoleOTPProvider(OTPProvider):
    async def send_otp(self, phone: str, otp: str) -> None:
        logger.info(
            "\n"
            "╔══════════════════════════════════╗\n"
            "║  DEV OTP for %-15s   ║\n"
            "║  Code: %s                     ║\n"
            "╚══════════════════════════════════╝",
            phone,
            otp,
        )
