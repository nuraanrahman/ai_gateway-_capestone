from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "AI Gateway"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Auth
    jwt_secret: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 60

    # CORS — stored as comma-separated string, exposed as list via property
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def coerce_cors(cls, v):
        if isinstance(v, list):
            return ",".join(v)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 1000

    # Cost guards
    daily_token_budget: int = 50000
    max_tokens_per_request: int = 4000

    # Provider API keys
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Admin
    admin_token: str = "change-me"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
