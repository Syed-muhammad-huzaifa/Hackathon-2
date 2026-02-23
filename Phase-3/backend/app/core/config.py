"""
Application settings loaded from environment variables.
@spec: specs/001-chatbot-backend/spec.md
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (Neon PostgreSQL - Phase 3 separate database)
    DATABASE_URL: str

    # Better Auth (Phase 3 frontend auth server - separate from Phase 2)
    BETTER_AUTH_URL: str = "http://localhost:3000"

    # Grok API (OpenAI-compatible)
    GROK_API_KEY: str = ""
    GROK_BASE_URL: str = "https://api.x.ai/v1"
    GROK_MODEL: str = "grok-3-mini"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MCP_CLIENT_TIMEOUT_SECONDS: float = 30.0

    # CORS
    ALLOWED_ORIGINS: str = "*"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def allowed_origins_list(self) -> list[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
