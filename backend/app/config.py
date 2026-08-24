"""Application configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "TheSummarist API"
    environment: str = "development"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://summarist:summarist@localhost:5433/thesummarist"
    )
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    storage_backend: str = "local"
    storage_local_dir: Path = Path("./storage")
    s3_bucket: str = ""
    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""

    llm_base_url: str = "https://integrate.api.nvidia.com/v1"
    llm_api_key: str = ""
    llm_model: str = "deepseek-ai/deepseek-v4-flash-0731"

    ocr_engine_label: str = "Advanced Vision V4"
    tesseract_cmd: str = "tesseract"

    tts_provider: str = "stub"

    public_base_url: str = "http://localhost:8000"
    max_upload_bytes: int = 50 * 1024 * 1024

    # Maximum characters of extracted text fed into the LLM per call.
    llm_max_input_chars: int = 60_000
    # Characters per map chunk when splitting long documents.
    llm_chunk_chars: int = 12_000
    # Hard cap on total map calls per summary (cost bound for any doc length).
    llm_max_map_calls: int = 48
    # Max concurrent map calls.
    llm_map_concurrency: int = 4
    # Max output tokens per LLM call.
    llm_max_output_tokens: int = 4_096


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
