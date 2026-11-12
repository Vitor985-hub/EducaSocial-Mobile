import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np

from app.core.exceptions import ConfigurationError
from app.core.text import normalize_text
from app.repositories.chunks import ChunkRepository, StoredChunk


@dataclass(frozen=True, slots=True)
class Hit:
    chunk: StoredChunk
    score: float


def location_matches(chunk: StoredChunk, state: str | None, municipality: str | None) -> bool:
    if state is None or chunk.region_level == "national":
        return True
    if chunk.region_state != state:
        return False
    if chunk.region_level == "state" or municipality is None:
        return True
    return normalize_text(chunk.region_name) == normalize_text(municipality)


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class VectorIndex:
    def __init__(self, chunks: Sequence[StoredChunk]) -> None:
        self._chunks = list(chunks)
        self._matrix: np.ndarray | None = None
        if self._chunks:
            try:
                raw = np.asarray([chunk.embedding for chunk in self._chunks], dtype=np.float32)
            except ValueError as exc:
                raise ConfigurationError(
                    "Embeddings armazenados têm dimensões diferentes."
                ) from exc
            self._matrix = _normalize_rows(raw)

    def __len__(self) -> int:
        return len(self._chunks)

    def search(
        self,
        query: Sequence[float],
        state: str | None,
        municipality: str | None,
        top_k: int,
        min_score: float,
    ) -> list[Hit]:
        if self._matrix is None:
            return []
        vector = np.asarray(query, dtype=np.float32)
        if vector.shape[0] != self._matrix.shape[1]:
            raise ConfigurationError(
                "A dimensão do embedding da pergunta difere da dos chunks armazenados."
            )
        norm = float(np.linalg.norm(vector))
        if norm == 0:
            return []
        scores = self._matrix @ (vector / norm)
        allowed = np.fromiter(
            (location_matches(chunk, state, municipality) for chunk in self._chunks),
            dtype=bool,
            count=len(self._chunks),
        )
        scores = np.where(allowed, scores, -1.0)
        order = np.argsort(-scores)[:top_k]
        return [
            Hit(chunk=self._chunks[index], score=float(scores[index]))
            for index in order
            if scores[index] >= min_score
        ]


class ChunkIndexProvider:
    def __init__(
        self,
        repository: ChunkRepository,
        embedding_model: str,
        ttl_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._repository = repository
        self._embedding_model = embedding_model
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._index: VectorIndex | None = None
        self._loaded_at = 0.0

    def get(self) -> VectorIndex:
        with self._lock:
            now = self._clock()
            expired = now - self._loaded_at >= self._ttl_seconds
            if self._index is None or expired:
                chunks = self._repository.load_chunks(self._embedding_model)
                self._index = VectorIndex(chunks)
                self._loaded_at = now
            return self._index
