from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    lab_public_url: str = "http://localhost:8080"
    database_url: str = "sqlite:////data/content-lab.db"
    openai_api_key: str | None = None
    vibe_api_token: str | None = None
    vibe_webhook_secret: str | None = None
    vibe_api_base_url: str = "https://lk.vibemarketolog.ru/api/agent"
    max_request_budget_rub: float = 30.0
    estimate_ttl_seconds: int = 900
    chroma_path: str = "/data/chroma"
    docs_url: str = "https://lk.vibemarketolog.ru/docs/agent-api"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[2] / ".env",
        extra="ignore",
    )


settings = Settings()
