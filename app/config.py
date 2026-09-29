"""Configuration loaded from the environment (12-factor style)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. ``AGENT_API_KEY`` deliberately has no default."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    port: int = 8000
    agent_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    log_level: str = "INFO"
