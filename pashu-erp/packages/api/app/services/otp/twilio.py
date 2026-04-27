import logging
from base64 import b64encode

import httpx

from app.services.otp.base import OTPProvider

logger = logging.getLogger("pashuraksha.otp")


class TwilioOTPProvider(OTPProvider):
    """Send OTP via Twilio SMS API (uses httpx, no SDK needed)."""

    def __init__(
        self, account_sid: str, auth_token: str, from_number: str, allowed_phones: set[str] | None = None,
    ) -> None:
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self._allowed_phones = allowed_phones
        self._url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    async def send_otp(self, phone: str, otp: str) -> None:
        if self._allowed_phones and phone not in self._allowed_phones:
            logger.warning("Phone %s not in whitelist — OTP blocked to protect credits", phone)
            raise RuntimeError(
                "SMS not available for this number. Contact admin to whitelist your phone."
            )

        message = f"Your PashuRaksha verification code is {otp}. Valid for 5 minutes. Do not share."
        credentials = b64encode(f"{self._account_sid}:{self._auth_token}".encode()).decode()

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                self._url,
                headers={"Authorization": f"Basic {credentials}"},
                data={
                    "To": phone,
                    "From": self._from_number,
                    "Body": message,
                },
            )
            if resp.status_code >= 400:
                error_msg = resp.json().get("message", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
                logger.error("Twilio SMS failed (%s): %s", resp.status_code, error_msg)
                raise RuntimeError(f"Twilio SMS failed ({resp.status_code}): {error_msg}")

        logger.info("OTP sent to %s via Twilio (SID: %s)", phone[-4:].rjust(len(phone), '*'), resp.json().get("sid", "unknown"))
