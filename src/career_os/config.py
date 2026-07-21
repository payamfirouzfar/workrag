from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"

    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/email/oauth/callback"

    browser_headless: bool = True
    browser_user_data_dir: str = "./data/browser_profile"

    respect_robots_txt: bool = True
    default_source_policy: str = "API_ALLOWED"
    max_requests_per_minute: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
