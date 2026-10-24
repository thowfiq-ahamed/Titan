"""
TITAN Platform API - Configuration
"""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    APP_NAME: str = "titan-platform-api"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = Field(
        default="sqlite:///./titan_platform.db",
        description="Database URL for platform metadata"
    )

    # API Security
    API_KEY: str = Field(default="titan-platform-master-key-2026")
    JWT_SECRET_KEY: str = Field(default="dev-jwt-secret-key-32ch-min-entropy")
    JWT_ALGORITHM: str = "HS256"

    # Workload Service Integration
    INVENTORY_API_URL: str = Field(default="http://localhost:8001")
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
