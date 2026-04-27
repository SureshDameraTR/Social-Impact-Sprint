import httpx

from app.services.circuit_breakers import sarvam_breaker
from app.services.otp.base import OTPProvider


class SarvamOTPProvider(OTPProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.sarvam.ai") -> None:
        self._api_key = api_key
        self._base_url = base_url

    @sarvam_breaker
    async def send_otp(self, phone: str, otp: str) -> None:
        message = f"Your PashuRaksha verification code is {otp}. Valid for 5 minutes. Do not share."
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self._base_url}/v1/sms/send",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={"phone": phone, "message": message},
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"Sarvam SMS failed ({resp.status_code}): {resp.text}")
