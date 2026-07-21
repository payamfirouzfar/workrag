from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    # ─── LLM / Embeddings provider ──────────────────────────
    # "ollama" (default): free, runs locally, no API key or per-token cost.
    # "openai": paid, requires OPENAI_API_KEY. Switch by setting
    # LLM_PROVIDER=openai in .env -- nothing else in the code needs to change.
    llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.1"
    ollama_embedding_model: str = "nomic-embed-text"
    # nomic-embed-text produces 768-dim vectors; text-embedding-3-small
    # produces 1536-dim. The Job.embedding column size follows this setting,
    # so it must match whichever provider/model is actually configured.
    embedding_dim: int = 768

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
