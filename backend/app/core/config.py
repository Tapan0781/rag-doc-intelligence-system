from __future__ import annotations

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "rag-doc-intelligence-system"
    environment: str = "dev"
    log_level: str = "INFO"

    # Pinecone
    pinecone_api_key: str | None = None
    pinecone_index_name: str | None = None
    pinecone_host: str | None = None

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # LLM (OpenAI)
    openai_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_max_output_tokens: int = 512

    # API Auth + Rate Limit
    api_key: str | None = None
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    # Retrieval
    max_query_results: int = 5


class Chunk(BaseModel):
    id: str
    text: str
    metadata: dict[str, str]


settings = AppSettings()
