import logging
import sys

from app.services.otp.base import OTPProvider

logger = logging.getLogger("pashuraksha.otp")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setLevel(logging.DEBUG)
    logger.addHandler(_handler)


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
