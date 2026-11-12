from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredChunk:
    document_id: int
    opportunity_id: int
    chunk_index: int
    content: str
    opportunity_title: str
    status: str | None
    last_reviewed: date | None
    region_level: str
    region_state: str | None
    region_name: str
    source_name: str | None
    source_url: str | None
    embedding: list[float]


@dataclass(frozen=True, slots=True)
class PendingDocument:
    document_id: int
    content: str


@dataclass(frozen=True, slots=True)
class OpportunityRecord:
    id: int
    title: str
    description: str
    eligibility: str
    required_documents: list[str]
    application_steps: list[str]
    source_id: int | None


@dataclass(frozen=True, slots=True)
class NewDocument:
    opportunity_id: int
    source_id: int | None
    chunk_index: int
    content: str


class ChunkRepository(Protocol):
    def load_chunks(self, embedding_model: str) -> list[StoredChunk]: ...

    def pending_documents(self, embedding_model: str) -> list[PendingDocument]: ...

    def save_embeddings(
        self, embedding_model: str, embeddings: Mapping[int, list[float]]
    ) -> int: ...

    def opportunities_without_documents(self) -> list[OpportunityRecord]: ...

    def insert_documents(self, documents: Sequence[NewDocument]) -> int: ...
