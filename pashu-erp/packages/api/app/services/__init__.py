"""Business logic services.

Import services individually rather than from this package to keep
startup fast — most modules have side-effects (HTTP clients, etc.).
"""

__all__ = [
    "bharat_pashudhan",
    "disease_rules",
    "errors",
    "feed_calculator",
    "http_client",
    "iot_service",
    "market_rates",
    "milk_pricing",
    "storage_service",
    "vaccination_scheduler",
    "weather_service",
]
