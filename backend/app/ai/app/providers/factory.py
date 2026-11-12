from pydantic import SecretStr

from app.core.config import Settings
from app.core.exceptions import ConfigurationError
from app.providers.base import EmbeddingProvider, LLMProvider
from app.providers.gemini import BASE_URL, GeminiEmbeddingProvider, GeminiLLMProvider
from app.providers.http import make_client
from app.providers.ollama import OllamaEmbeddingProvider, OllamaLLMProvider


def _gemini_client(settings: Settings):
    key: SecretStr | None = settings.gemini_api_key
    if key is None:
        raise ConfigurationError("GEMINI_API_KEY não configurada.")
    return make_client(
        BASE_URL,
        settings.provider_timeout_seconds,
        headers={"x-goog-api-key": key.get_secret_value()},
    )


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "ollama":
        client = make_client(settings.ollama_base_url, settings.provider_timeout_seconds)
        return OllamaEmbeddingProvider(client, settings.ollama_embedding_model)
    return GeminiEmbeddingProvider(
        _gemini_client(settings),
        settings.gemini_embedding_model,
        settings.gemini_embedding_dimensions,
    )


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "ollama":
        client = make_client(settings.ollama_base_url, settings.provider_timeout_seconds)
        return OllamaLLMProvider(client, settings.ollama_llm_model)
    if not settings.gemini_llm_model:
        raise ConfigurationError("GEMINI_LLM_MODEL não configurado.")
    return GeminiLLMProvider(_gemini_client(settings), settings.gemini_llm_model)
