import re
import zlib
from collections.abc import Sequence
from datetime import date
from typing import Any

from app.core.text import normalize_text
from app.repositories.chunks import StoredChunk


class HashEmbedder:
    def __init__(self, dimensions: int = 256, model_name: str = "fake-embedder") -> None:
        self.model_name = model_name
        self._dimensions = dimensions
        self.document_calls = 0
        self.query_calls = 0

    def vector(self, text: str) -> list[float]:
        values = [0.0] * self._dimensions
        for token in re.findall(r"\w+", normalize_text(text)):
            values[zlib.crc32(token.encode()) % self._dimensions] += 1.0
        return values

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        self.document_calls += 1
        return [self.vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        self.query_calls += 1
        return self.vector(text)


class ScriptedLLM:
    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.calls: list[tuple[str, str]] = []

    def generate(self, system: str, prompt: str) -> str:
        self.calls.append((system, prompt))
        return self.answer


class StaticRepository:
    def __init__(self, chunks: Sequence[StoredChunk]) -> None:
        self._chunks = list(chunks)
        self.loads = 0

    def load_chunks(self, embedding_model: str) -> list[StoredChunk]:
        self.loads += 1
        return list(self._chunks)


def make_chunk(embedder: HashEmbedder | None = None, **overrides: Any) -> StoredChunk:
    embedder = embedder or HashEmbedder()
    values: dict[str, Any] = {
        "document_id": 1,
        "opportunity_id": 1,
        "chunk_index": 0,
        "content": "conteúdo de teste",
        "opportunity_title": "Programa de teste",
        "status": "current",
        "last_reviewed": date(2026, 11, 1),
        "region_level": "national",
        "region_state": None,
        "region_name": "Brasil",
        "source_name": "Fonte de teste",
        "source_url": "https://exemplo.invalid/fonte",
    }
    values.update(overrides)
    values.setdefault("embedding", embedder.vector(values["content"]))
    return StoredChunk(**values)
