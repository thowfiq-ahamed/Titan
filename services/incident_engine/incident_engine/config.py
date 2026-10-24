"""
TITAN Incident Engine - Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    APP_NAME: str = "titan-incident-engine"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8002

    # Webhook Authentication
    ALERTMANAGER_WEBHOOK_SECRET: str = Field(default="dev-alertmanager-webhook-secret")

    # Platform API connection
    PLATFORM_API_URL: str = Field(default="http://localhost:8000")
    PLATFORM_API_KEY: str = Field(default="titan-platform-master-key-2026")

    # Operational Mode: 'remediation' or 'diagnosis_only'
    DIAGNOSIS_MODE: str = Field(default="remediation")


settings = Settings()
