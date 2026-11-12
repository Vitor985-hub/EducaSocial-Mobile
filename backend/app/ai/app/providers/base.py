from collections.abc import Sequence
from typing import Protocol


class EmbeddingProvider(Protocol):
    model_name: str

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class LLMProvider(Protocol):
    def generate(self, system: str, prompt: str) -> str: ...
