"""
Configuration management for the application.

Loads environment variables and provides typed settings.

@spec: specs/002-todo-backend-api/spec.md (FR-001, FR-007)
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str

    # Better Auth Configuration — URL of the Better Auth server (for JWKS)
    BETTER_AUTH_URL: str = "http://localhost:3000"
    BETTER_AUTH_SECRET: str  # Shared secret with frontend (must match)

    # Application Configuration
    APP_ENV: str = "development"
    DEBUG: bool = False  # Set to True only in development via .env
    LOG_LEVEL: str = "INFO"

    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Pool Configuration
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Security
    ENABLE_SECURITY_HEADERS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV.lower() == "development"


# Global settings instance
settings = Settings()
