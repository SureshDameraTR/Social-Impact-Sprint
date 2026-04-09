"""Shared error types for external service clients."""


class ServiceNotConfiguredError(RuntimeError):
    """Raised when a required service URL env var is not set."""

    def __init__(self, env_var: str):
        super().__init__(f"{env_var} is not configured")
        self.env_var = env_var


class ServiceUnavailableError(RuntimeError):
    """Raised when an external service cannot be reached."""

    def __init__(self, service: str, detail: str = ""):
        super().__init__(f"{service} is unavailable: {detail}")
        self.service = service
