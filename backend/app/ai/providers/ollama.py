from collections.abc import Sequence

import httpx

from app.ai.core.exceptions import ProviderError
from app.ai.providers.http import batches, post_json

PROVIDER = "Ollama"


class OllamaEmbeddingProvider:
    def __init__(self, client: httpx.Client, model: str, batch_size: int = 32) -> None:
        self._client = client
        self._batch_size = batch_size
        self.model_name = model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for batch in batches(list(texts), self._batch_size):
            data = post_json(
                self._client,
                "/api/embed",
                {"model": self.model_name, "input": list(batch)},
                PROVIDER,
            )
            embeddings = data.get("embeddings")
            if not isinstance(embeddings, list) or len(embeddings) != len(batch):
                raise ProviderError("Ollama retornou embeddings em formato inesperado.")
            vectors.extend(embeddings)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class OllamaLLMProvider:
    def __init__(self, client: httpx.Client, model: str, temperature: float = 0.1) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature

    def generate(self, system: str, prompt: str) -> str:
        data = post_json(
            self._client,
            "/api/chat",
            {
                "model": self._model,
                "stream": False,
                "options": {"temperature": self._temperature},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            },
            PROVIDER,
        )
        message = data.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise ProviderError("Ollama não retornou texto na resposta.")
        return content
