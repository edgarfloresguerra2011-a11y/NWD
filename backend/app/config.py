from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Nexus Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./nexuscold.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    WARMUP_POOL_SIZE: int = 100
    MAX_EMAILS_PER_ACCOUNT_PER_DAY: int = 100

    STRIPE_API_KEY: Optional[str] = None
    WHITELABEL_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
