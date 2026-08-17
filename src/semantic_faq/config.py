from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"

    api_token: str = Field(min_length=16)

    database_url: str = "postgresql+asyncpg://faq:faq@localhost:5432/faq"

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    openai_timeout_seconds: float = 20.0

    faq_collection: str = "default"
    local_match_threshold: float = Field(default=0.78, ge=0.0, le=1.0)
    ambiguity_margin: float = Field(default=0.03, ge=0.0, le=1.0)
    max_question_length: int = Field(default=1000, ge=1, le=10_000)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]