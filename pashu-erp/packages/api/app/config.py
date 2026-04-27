from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    jwt_refresh_expiry_days: int = 7
    aadhaar_hash_secret: str = ""
    environment: str = "development"
    sarvam_api_key: str = ""
    sarvam_base_url: str = "https://api.sarvam.ai"
    weather_api_url: str = ""
    bharat_pashudhan_api_url: str = ""
    iot_gateway_url: str = ""
    storage_api_url: str = ""
    cors_origins: str = ""
    pool_size: int = 50
    max_overflow: int = 50
    pool_recycle: int = 3600
    database_ssl: bool = False
    rate_limit_per_minute: int = 120
    sql_echo: bool = False

    # --- Business constants (moved from routers) ---
    # Vet dashboard
    risk_score_threshold: float = 0.5
    alert_window_days: int = 7

    # Animal ID generation
    max_id_retries: int = 3

    # OTP rate limits
    max_otp_requests_per_hour: int = 5
    max_otp_attempts: int = 3
    otp_expiry_minutes: int = 5

    # CSRF token max age (seconds) — defaults to 24 hours
    csrf_token_max_age_seconds: int = 86400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
