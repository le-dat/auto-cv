from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── LLM ──────────────────────────────────────────────
    llm_provider: str = Field(default="openai", description="openai | groq | claude")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="llama3-70b-8192")
    anthropic_api_key: str = Field(default="")
    claude_model: str = Field(default="claude-3-5-haiku-20241022")

    # ── Infrastructure ────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/cvoptimizer",
    )
    redis_url: str = Field(default="redis://localhost:6379")

    # ── Input ─────────────────────────────────────────────
    max_file_size_mb: int = Field(default=10)
    allowed_input_types: list[str] = Field(
        default_factory=lambda: ["pdf", "docx", "txt", "text", "md"],
    )

    # ── Context providers ──────────────────────────────────
    context_providers: list[str] = Field(
        default_factory=lambda: ["markdown", "faiss"],
        description="Comma-separated list: markdown | faiss | db | http",
    )
    context_top_k: int = Field(default=5)
    knowledge_dir: str = Field(default="app/knowledge")
    knowledge_max_docs: int = Field(default=10)
    db_context_enabled: bool = Field(default=False)
    http_context_url: str = Field(default="")

    # ── Limits ────────────────────────────────────────────
    max_concurrent_jobs: int = Field(default=5)
    job_timeout_seconds: int = Field(default=120)

    # ── Debug ─────────────────────────────────────────────
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Convenience accessor used throughout the codebase
settings = get_settings()
