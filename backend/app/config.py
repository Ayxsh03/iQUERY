"""
iQuery — Centralized configuration via pydantic-settings.
All values are read from environment variables / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────
    llm_provider: str = "groq"          # "groq" | "ollama"
    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    # ── Embedding ────────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"

    # ── Vector Store ─────────────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "intraquery_docs"

    # ── Chunking ─────────────────────────────────────────────────────
    chunk_size: int = 512
    chunk_overlap: int = 64

    # ── Retrieval ────────────────────────────────────────────────────
    top_k_results: int = 5

    # ── App ──────────────────────────────────────────────────────────
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of app settings."""
    return Settings()
