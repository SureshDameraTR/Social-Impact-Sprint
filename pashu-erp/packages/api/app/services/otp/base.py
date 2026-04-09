from abc import ABC, abstractmethod


class OTPProvider(ABC):
    @abstractmethod
    async def send_otp(self, phone: str, otp: str) -> None:
        """Deliver an OTP to the given phone number.

        Raises:
            RuntimeError: If delivery fails.
        """
