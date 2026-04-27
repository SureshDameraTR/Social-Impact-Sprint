"""Per-service circuit breakers for external API calls.

Each external service gets its own CircuitBreaker instance so that one
degraded dependency does not mask failures in another.

Configuration:
    failure_threshold=5   Open the circuit after 5 consecutive failures.
    recovery_timeout=60   Attempt a probe call after 60 seconds.

When a breaker is open, calls raise ``CircuitBreakerError`` from the
``circuitbreaker`` package.  The global exception handler in ``main.py``
converts that into an HTTP 503.
"""

try:
    from circuitbreaker import CircuitBreaker
except ImportError:

    class CircuitBreaker:  # type: ignore[no-redef]
        def __init__(self, **kwargs):
            self.name = kwargs.get("name", "unknown")

        def __call__(self, func):
            return func


_FAILURE_THRESHOLD = 5
_RECOVERY_TIMEOUT = 60  # seconds


def _make_breaker(name: str) -> CircuitBreaker:
    return CircuitBreaker(
        failure_threshold=_FAILURE_THRESHOLD,
        recovery_timeout=_RECOVERY_TIMEOUT,
        name=name,
    )


weather_breaker = _make_breaker("weather")
registry_breaker = _make_breaker("bharat_pashudhan")
iot_breaker = _make_breaker("iot_gateway")
storage_breaker = _make_breaker("storage")
sarvam_breaker = _make_breaker("sarvam")
