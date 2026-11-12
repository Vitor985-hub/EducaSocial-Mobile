import json

import httpx
import pytest

from app.core.config import Settings
from app.core.exceptions import ConfigurationError, ProviderError
from app.providers.factory import build_embedding_provider, build_llm_provider
from app.providers.gemini import (
    BASE_URL,
    GeminiEmbeddingProvider,
    GeminiLLMProvider,
)
from app.providers.http import make_client
from app.providers.ollama import OllamaEmbeddingProvider, OllamaLLMProvider


def client_with(handler, base_url="http://ollama.invalid", headers=None) -> httpx.Client:
    return make_client(base_url, 5, headers=headers, transport=httpx.MockTransport(handler))


def test_ollama_embeddings_send_batches_and_parse_vectors() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        requests.append((request.url.path, body))
        return httpx.Response(200, json={"embeddings": [[1.0, 0.0] for _ in body["input"]]})

    provider = OllamaEmbeddingProvider(client_with(handler), "bge-m3", batch_size=2)

    vectors = provider.embed_documents(["a", "b", "c"])

    assert vectors == [[1.0, 0.0]] * 3
    assert [path for path, _ in requests] == ["/api/embed", "/api/embed"]
    assert requests[0][1] == {"model": "bge-m3", "input": ["a", "b"]}
    assert provider.model_name == "bge-m3"


def test_ollama_embed_query_returns_single_vector() -> None:
    provider = OllamaEmbeddingProvider(
        client_with(lambda request: httpx.Response(200, json={"embeddings": [[0.5, 0.5]]})),
        "bge-m3",
    )

    assert provider.embed_query("oi") == [0.5, 0.5]


def test_ollama_rejects_wrong_number_of_embeddings() -> None:
    provider = OllamaEmbeddingProvider(
        client_with(lambda request: httpx.Response(200, json={"embeddings": []})), "bge-m3"
    )

    with pytest.raises(ProviderError):
        provider.embed_documents(["a"])


def test_ollama_chat_request_and_response() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"message": {"role": "assistant", "content": "olá"}})

    provider = OllamaLLMProvider(client_with(handler), "qwen2.5:7b")

    assert provider.generate("sistema", "pergunta") == "olá"
    assert captured["path"] == "/api/chat"
    assert captured["body"]["model"] == "qwen2.5:7b"
    assert captured["body"]["stream"] is False
    assert captured["body"]["messages"] == [
        {"role": "system", "content": "sistema"},
        {"role": "user", "content": "pergunta"},
    ]


def test_ollama_http_error_becomes_provider_error() -> None:
    provider = OllamaLLMProvider(
        client_with(lambda request: httpx.Response(500, json={"error": "boom"})), "m"
    )

    with pytest.raises(ProviderError, match="HTTP 500"):
        provider.generate("s", "p")


def test_ollama_connection_failure_becomes_provider_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("recusada")

    provider = OllamaLLMProvider(client_with(handler), "m")

    with pytest.raises(ProviderError):
        provider.generate("s", "p")


def test_ollama_empty_content_is_an_error() -> None:
    provider = OllamaLLMProvider(
        client_with(lambda request: httpx.Response(200, json={"message": {"content": "  "}})), "m"
    )

    with pytest.raises(ProviderError):
        provider.generate("s", "p")


def test_gemini_batch_embeddings_use_document_task_and_dimensions() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["key"] = request.headers.get("x-goog-api-key")
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"embeddings": [{"values": [0.1, 0.2]}, {"values": [0.3, 0.4]}]}
        )

    client = client_with(handler, BASE_URL, {"x-goog-api-key": "chave-teste"})
    provider = GeminiEmbeddingProvider(client, "gemini-embedding-001", 768)

    vectors = provider.embed_documents(["a", "b"])

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert captured["path"].endswith("/models/gemini-embedding-001:batchEmbedContents")
    assert captured["key"] == "chave-teste"
    first = captured["body"]["requests"][0]
    assert first["taskType"] == "RETRIEVAL_DOCUMENT"
    assert first["outputDimensionality"] == 768
    assert first["model"] == "models/gemini-embedding-001"
    assert provider.model_name == "gemini-embedding-001:768"


def test_gemini_query_embedding_uses_query_task() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"embedding": {"values": [0.7, 0.3]}})

    provider = GeminiEmbeddingProvider(client_with(handler, BASE_URL), "gemini-embedding-001", 768)

    assert provider.embed_query("oi") == [0.7, 0.3]
    assert captured["path"].endswith(":embedContent")
    assert captured["body"]["taskType"] == "RETRIEVAL_QUERY"


def test_gemini_generate_request_and_response() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "uma "}, {"text": "resposta"}]}}]},
        )

    provider = GeminiLLMProvider(client_with(handler, BASE_URL), "modelo-x")

    assert provider.generate("sistema", "pergunta") == "uma resposta"
    assert captured["path"].endswith("/models/modelo-x:generateContent")
    assert captured["body"]["systemInstruction"]["parts"][0]["text"] == "sistema"
    assert captured["body"]["contents"][0]["parts"][0]["text"] == "pergunta"


def test_gemini_blocked_response_is_an_error() -> None:
    provider = GeminiLLMProvider(
        client_with(lambda request: httpx.Response(200, json={"candidates": []}), BASE_URL), "m"
    )

    with pytest.raises(ProviderError):
        provider.generate("s", "p")


def test_gemini_error_does_not_leak_api_key() -> None:
    client = client_with(
        lambda request: httpx.Response(403, json={}), BASE_URL, {"x-goog-api-key": "chave-secreta"}
    )

    with pytest.raises(ProviderError) as error:
        GeminiLLMProvider(client, "m").generate("s", "p")

    assert "chave-secreta" not in str(error.value)


def test_factory_builds_providers_from_settings() -> None:
    ollama = Settings(_env_file=None)
    gemini = Settings(
        _env_file=None,
        llm_provider="gemini",
        embedding_provider="gemini",
        gemini_api_key="k",
        gemini_llm_model="modelo-x",
    )

    assert isinstance(build_embedding_provider(ollama), OllamaEmbeddingProvider)
    assert isinstance(build_llm_provider(ollama), OllamaLLMProvider)
    assert isinstance(build_embedding_provider(gemini), GeminiEmbeddingProvider)
    assert isinstance(build_llm_provider(gemini), GeminiLLMProvider)


def test_factory_requires_gemini_configuration() -> None:
    without_key = Settings(_env_file=None, embedding_provider="gemini")
    without_model = Settings(_env_file=None, llm_provider="gemini", gemini_api_key="k")

    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        build_embedding_provider(without_key)
    with pytest.raises(ConfigurationError, match="GEMINI_LLM_MODEL"):
        build_llm_provider(without_model)
