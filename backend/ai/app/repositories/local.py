import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from app.core.exceptions import ConfigurationError, StoreError
from app.repositories.chunks import (
    NewDocument,
    OpportunityRecord,
    PendingDocument,
    StoredChunk,
)


class LocalChunkRepository:
    def __init__(
        self,
        path: Path | None = None,
        documents: Sequence[Mapping[str, Any]] | None = None,
    ) -> None:
        self._path = path
        self._documents: list[dict[str, Any]] = [dict(item) for item in documents or []]
        self._embeddings: dict[str, dict[str, list[float]]] = {}
        if documents is None and path is not None and path.exists():
            self._read(path)

    def _read(self, path: Path) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self._documents = [dict(item) for item in payload.get("documents", [])]
            self._embeddings = {
                model: {str(key): list(vector) for key, vector in vectors.items()}
                for model, vectors in payload.get("embeddings", {}).items()
            }
        except (OSError, ValueError, AttributeError, TypeError) as exc:
            raise StoreError(f"Arquivo local inválido: {path}.") from exc

    def _persist(self) -> None:
        if self._path is None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        payload = {"documents": self._documents, "embeddings": self._embeddings}
        temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self._path)

    def load_chunks(self, embedding_model: str) -> list[StoredChunk]:
        vectors = self._embeddings.get(embedding_model, {})
        chunks = []
        for item in self._documents:
            vector = vectors.get(str(item["document_id"]))
            if vector is None:
                continue
            reviewed = item.get("last_reviewed")
            chunks.append(
                StoredChunk(
                    document_id=int(item["document_id"]),
                    opportunity_id=int(item["opportunity_id"]),
                    chunk_index=int(item.get("chunk_index", 0)),
                    content=item["content"],
                    opportunity_title=item["opportunity_title"],
                    status=item.get("status"),
                    last_reviewed=date.fromisoformat(reviewed) if reviewed else None,
                    region_level=item["region_level"],
                    region_state=item.get("region_state"),
                    region_name=item["region_name"],
                    source_name=item.get("source_name"),
                    source_url=item.get("source_url"),
                    embedding=vector,
                )
            )
        return chunks

    def pending_documents(self, embedding_model: str) -> list[PendingDocument]:
        vectors = self._embeddings.get(embedding_model, {})
        return [
            PendingDocument(document_id=int(item["document_id"]), content=item["content"])
            for item in self._documents
            if str(item["document_id"]) not in vectors
        ]

    def save_embeddings(self, embedding_model: str, embeddings: Mapping[int, list[float]]) -> int:
        stored = self._embeddings.setdefault(embedding_model, {})
        for document_id, vector in embeddings.items():
            stored[str(document_id)] = list(vector)
        self._persist()
        return len(embeddings)

    def opportunities_without_documents(self) -> list[OpportunityRecord]:
        raise ConfigurationError("build-documents exige CHUNK_STORE=mysql.")

    def insert_documents(self, documents: Sequence[NewDocument]) -> int:
        raise ConfigurationError("build-documents exige CHUNK_STORE=mysql.")
