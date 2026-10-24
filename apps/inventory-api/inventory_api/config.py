"""
TITAN Inventory API - Configuration Management
Centralized, validated settings using Pydantic Settings.
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

    APP_NAME: str = "titan-inventory-api"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="development, staging, or production")
    LOG_LEVEL: str = Field(default="INFO", description="DEBUG, INFO, WARNING, ERROR, CRITICAL")
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://titan_user:titan_secure_pass@localhost:5432/titan_inventory",
        description="SQLAlchemy compatible database connection string"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_PRE_PING: bool = True

    # Reliability Lab - Controlled Fault Injection Security Controls
    ENABLE_FAULT_INJECTION: bool = Field(
        default=False,
        description="Enables test-only failure simulation endpoints. MUST be false in production."
    )
    FAULT_INJECTION_AUTH_TOKEN: str = Field(
        default="",
        description="Bearer token or header required to trigger simulated faults. Must be explicitly injected."
    )

    # CORS
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
