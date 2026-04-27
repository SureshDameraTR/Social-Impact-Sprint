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
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    twilio_allowed_phones: str = ""  # comma-separated whitelist, empty = allow all
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

    # Open-Meteo (free, no key)
    open_meteo_base_url: str = "https://api.open-meteo.com"
    weather_cache_ttl_seconds: int = 10800

    # data.gov.in
    data_gov_in_api_key: str = ""
    data_gov_in_base_url: str = "https://api.data.gov.in"

    # S3 / MinIO
    s3_endpoint_url: str = ""
    s3_bucket_name: str = "pashuraksha"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "ap-south-1"
    s3_presigned_url_expiry: int = 3600

    # Refresh jobs
    refresh_log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
