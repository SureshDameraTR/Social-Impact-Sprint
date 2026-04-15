from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    environment: str = "development"
    sarvam_api_key: str = ""
    weather_api_url: str = ""
    bharat_pashudhan_api_url: str = ""
    iot_gateway_url: str = ""
    storage_api_url: str = ""
    cors_origins: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    rate_limit_per_minute: int = 10
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
