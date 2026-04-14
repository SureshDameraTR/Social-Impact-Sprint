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
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:8081,http://localhost:8082"
    pool_size: int = 10
    max_overflow: int = 20
    pool_recycle: int = 3600
    rate_limit_per_minute: int = 10
    sql_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
