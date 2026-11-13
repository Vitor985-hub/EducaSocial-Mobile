from collections.abc import Sequence
from typing import Any

import httpx

from app.ai.core.exceptions import ProviderError
from app.ai.providers.http import batches, post_json

PROVIDER = "Gemini"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DOCUMENT_TASK = "RETRIEVAL_DOCUMENT"
QUERY_TASK = "RETRIEVAL_QUERY"


class GeminiEmbeddingProvider:
    def __init__(
        self,
        client: httpx.Client,
        api_model: str,
        dimensions: int,
        batch_size: int = 50,
    ) -> None:
        self._client = client
        self._api_model = api_model
        self._dimensions = dimensions
        self._batch_size = batch_size
        self.model_name = f"{api_model}:{dimensions}"

    def _request(self, text: str, task_type: str) -> dict[str, Any]:
        return {
            "model": f"models/{self._api_model}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
            "outputDimensionality": self._dimensions,
        }

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for batch in batches(list(texts), self._batch_size):
            data = post_json(
                self._client,
                f"/models/{self._api_model}:batchEmbedContents",
                {"requests": [self._request(text, DOCUMENT_TASK) for text in batch]},
                PROVIDER,
            )
            embeddings = data.get("embeddings")
            if not isinstance(embeddings, list) or len(embeddings) != len(batch):
                raise ProviderError("Gemini retornou embeddings em formato inesperado.")
            try:
                vectors.extend(item["values"] for item in embeddings)
            except (KeyError, TypeError) as exc:
                raise ProviderError("Gemini retornou embeddings em formato inesperado.") from exc
        return vectors

    def embed_query(self, text: str) -> list[float]:
        data = post_json(
            self._client,
            f"/models/{self._api_model}:embedContent",
            self._request(text, QUERY_TASK),
            PROVIDER,
        )
        embedding = data.get("embedding")
        values = embedding.get("values") if isinstance(embedding, dict) else None
        if not isinstance(values, list):
            raise ProviderError("Gemini retornou o embedding em formato inesperado.")
        return values


class GeminiLLMProvider:
    def __init__(self, client: httpx.Client, model: str, temperature: float = 0.1) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature

    def generate(self, system: str, prompt: str) -> str:
        data = post_json(
            self._client,
            f"/models/{self._model}:generateContent",
            {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": self._temperature},
            },
            PROVIDER,
        )
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts)
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ProviderError("Gemini não retornou texto (resposta vazia ou bloqueada).") from exc
        if not text.strip():
            raise ProviderError("Gemini não retornou texto (resposta vazia ou bloqueada).")
        return text
