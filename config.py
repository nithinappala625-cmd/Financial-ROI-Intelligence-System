"""
Configuration module — single source of truth for all environment variables.
Uses Pydantic BaseSettings for type-checked env var loading.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT / Auth ────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_MINUTES: int = 10080  # 7 days

    # ── Application ───────────────────────────────────────────────────────
    ENVIRONMENT: str = "dev"
    APP_TITLE: str = "AI Financial Management & ROI Intelligence Platform"
    APP_VERSION: str = "1.0.0"

    # ── Optional (for future use by other developers) ─────────────────────
    REDIS_URL: str | None = None
    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    AI_ENGINE_BASE_URL: str | None = None
    SENDGRID_API_KEY: str | None = None


settings = Settings()
