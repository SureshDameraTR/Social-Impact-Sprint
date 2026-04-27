from abc import ABC, abstractmethod


class OTPProvider(ABC):
    @abstractmethod
    async def send_otp(self, phone: str, otp: str) -> None:
        """Deliver an OTP to the given phone number.

        Raises:
            RuntimeError: If delivery fails.
        """

    async def verify_otp(self, phone: str, otp: str, expected: str) -> bool:
        """Verify an OTP code against the expected value.

        The default implementation performs a constant-time string comparison.
        Subclasses may override to add provider-specific verification (e.g.
        calling an external API).

        Returns:
            True if the OTP matches, False otherwise.
        """
        import hmac

        return hmac.compare_digest(otp, expected)
