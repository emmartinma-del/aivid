from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://aivid:aivid_dev@localhost:5432/aivid"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # S3 / MinIO
    s3_endpoint_url: str | None = None  # None = real AWS
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_region: str = "eu-central-1"
    s3_uploads_bucket: str = "aivid-uploads"
    s3_outputs_bucket: str = "aivid-outputs"
    s3_public_url: str = ""
    cloudfront_domain: str = ""

    # AI
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    pixabay_api_key: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_free: str = ""
    stripe_price_starter: str = ""
    stripe_price_pro: str = ""
    stripe_price_agency: str = ""

    # Email
    resend_api_key: str = ""
    email_from: str = "noreply@aivid.ch"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Sentry
    sentry_dsn: str = ""

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
