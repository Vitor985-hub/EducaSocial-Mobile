from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

from app.core.exceptions import ConfigurationError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    environment: Literal["development", "staging", "production"] = "development"
    ai_service_api_key: SecretStr | None = None

    db_host: str | None = None
    db_port: int = 3306
    db_name: str | None = None
    db_user: str | None = None
    db_password: SecretStr | None = None

    chunk_store: Literal["mysql", "local"] = "mysql"
    local_store_path: Path = Path("data/local_store.json")

    llm_provider: Literal["ollama", "gemini"] = "ollama"
    embedding_provider: Literal["ollama", "gemini"] = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "qwen2.5:7b"
    ollama_embedding_model: str = "bge-m3"

    gemini_api_key: SecretStr | None = None
    gemini_llm_model: str | None = None
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_embedding_dimensions: int = Field(default=768, ge=64, le=3072)

    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    retrieval_min_score: float = Field(default=0.45, ge=0.0, le=1.0)
    index_ttl_seconds: int = Field(default=300, ge=0)
    provider_timeout_seconds: float = Field(default=60.0, gt=0)
    chunk_max_chars: int = Field(default=1200, ge=200)
    chunk_overlap_chars: int = Field(default=150, ge=0)

    @model_validator(mode="after")
    def validate_consistency(self) -> "Settings":
        if self.environment == "production" and self.ai_service_api_key is None:
            raise ValueError("AI_SERVICE_API_KEY é obrigatória em produção.")
        if self.chunk_overlap_chars >= self.chunk_max_chars:
            raise ValueError("CHUNK_OVERLAP_CHARS deve ser menor que CHUNK_MAX_CHARS.")
        return self

    @property
    def database_url(self) -> URL:
        required = {
            "DB_HOST": self.db_host,
            "DB_NAME": self.db_name,
            "DB_USER": self.db_user,
            "DB_PASSWORD": self.db_password,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ConfigurationError(f"Variáveis de banco ausentes: {', '.join(missing)}.")
        return URL.create(
            "mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
