from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://pashu:pashu_dev_2026@localhost:5432/pashuraksha"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    environment: str = "development"
    sarvam_api_key: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
