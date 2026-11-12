import json
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    Engine,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    bindparam,
    func,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import JSON

from app.core.exceptions import StoreError
from app.repositories.chunks import (
    NewDocument,
    OpportunityRecord,
    PendingDocument,
    StoredChunk,
)

WRITE_BATCH_SIZE = 100

metadata = MetaData()

_id = BigInteger().with_variant(Integer(), "sqlite")

region = Table(
    "region",
    metadata,
    Column("id", _id, primary_key=True),
    Column("name", String(255)),
    Column("level", String(20)),
    Column("state", String(2)),
    Column("parent_id", _id),
)

opportunity = Table(
    "opportunity",
    metadata,
    Column("id", _id, primary_key=True),
    Column("title", String(500)),
    Column("description", Text),
    Column("eligibility", Text),
    Column("required_documents", JSON),
    Column("application_steps", JSON),
    Column("region_id", _id),
    Column("status", String(20)),
    Column("last_reviewed", Date),
)

source = Table(
    "source",
    metadata,
    Column("id", _id, primary_key=True),
    Column("opportunity_id", _id),
    Column("name", String(255)),
    Column("url", String(2048)),
)

document = Table(
    "document",
    metadata,
    Column("id", _id, primary_key=True),
    Column("opportunity_id", _id),
    Column("source_id", _id),
    Column("chunk_index", Integer),
    Column("content", Text),
    Column("embedding_model", String(255)),
    Column("embedding", JSON(none_as_null=True)),
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        value = json.loads(value)
    return list(value)


class SqlChunkRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def load_chunks(self, embedding_model: str) -> list[StoredChunk]:
        parent = region.alias("parent")
        statement = (
            select(
                document.c.id.label("document_id"),
                document.c.opportunity_id,
                document.c.chunk_index,
                document.c.content,
                opportunity.c.title,
                opportunity.c.status,
                opportunity.c.last_reviewed,
                region.c.level,
                func.coalesce(region.c.state, parent.c.state).label("state"),
                region.c.name.label("region_name"),
                source.c.name.label("source_name"),
                source.c.url.label("source_url"),
                document.c.embedding,
            )
            .select_from(document)
            .join(opportunity, opportunity.c.id == document.c.opportunity_id)
            .join(region, region.c.id == opportunity.c.region_id)
            .outerjoin(parent, parent.c.id == region.c.parent_id)
            .outerjoin(source, source.c.id == document.c.source_id)
            .where(
                document.c.embedding.is_not(None),
                document.c.embedding_model == embedding_model,
            )
            .order_by(document.c.id)
        )
        fallback_statement = select(source.c.opportunity_id, source.c.name, source.c.url).order_by(
            source.c.id
        )
        try:
            with self._engine.connect() as connection:
                rows = connection.execute(statement).mappings().all()
                fallback_rows = connection.execute(fallback_statement).all()
            fallback: dict[int, tuple[str, str]] = {}
            for opportunity_id, name, url in fallback_rows:
                fallback.setdefault(int(opportunity_id), (name, url))
            chunks = [self._to_chunk(row, fallback) for row in rows]
        except (SQLAlchemyError, ValueError, TypeError) as exc:
            raise StoreError("Falha ao carregar os chunks do banco.") from exc
        return [chunk for chunk in chunks if chunk.embedding]

    @staticmethod
    def _to_chunk(row: Mapping[str, Any], fallback: Mapping[int, tuple[str, str]]) -> StoredChunk:
        source_name, source_url = row["source_name"], row["source_url"]
        if source_name is None:
            source_name, source_url = fallback.get(int(row["opportunity_id"]), (None, None))
        return StoredChunk(
            document_id=int(row["document_id"]),
            opportunity_id=int(row["opportunity_id"]),
            chunk_index=int(row["chunk_index"]),
            content=row["content"],
            opportunity_title=row["title"],
            status=row["status"],
            last_reviewed=row["last_reviewed"],
            region_level=row["level"],
            region_state=row["state"],
            region_name=row["region_name"],
            source_name=source_name,
            source_url=source_url,
            embedding=[float(value) for value in _as_list(row["embedding"])],
        )

    def pending_documents(self, embedding_model: str) -> list[PendingDocument]:
        statement = (
            select(document.c.id, document.c.content)
            .where(
                or_(
                    document.c.embedding.is_(None),
                    document.c.embedding_model.is_(None),
                    document.c.embedding_model != embedding_model,
                )
            )
            .order_by(document.c.id)
        )
        try:
            with self._engine.connect() as connection:
                rows = connection.execute(statement).all()
        except SQLAlchemyError as exc:
            raise StoreError("Falha ao consultar documentos pendentes.") from exc
        return [PendingDocument(document_id=int(row[0]), content=row[1]) for row in rows]

    def save_embeddings(self, embedding_model: str, embeddings: Mapping[int, list[float]]) -> int:
        rows = [
            {"target_id": document_id, "vector": vector}
            for document_id, vector in embeddings.items()
        ]
        statement = (
            update(document)
            .where(document.c.id == bindparam("target_id"))
            .values(
                embedding=bindparam("vector", type_=JSON(none_as_null=True)),
                embedding_model=embedding_model,
            )
        )
        try:
            with self._engine.begin() as connection:
                for start in range(0, len(rows), WRITE_BATCH_SIZE):
                    connection.execute(statement, rows[start : start + WRITE_BATCH_SIZE])
        except SQLAlchemyError as exc:
            raise StoreError("Falha ao gravar os embeddings.") from exc
        return len(rows)

    def opportunities_without_documents(self) -> list[OpportunityRecord]:
        first_source = (
            select(source.c.opportunity_id, func.min(source.c.id).label("source_id"))
            .group_by(source.c.opportunity_id)
            .subquery()
        )
        statement = (
            select(
                opportunity.c.id,
                opportunity.c.title,
                opportunity.c.description,
                opportunity.c.eligibility,
                opportunity.c.required_documents,
                opportunity.c.application_steps,
                first_source.c.source_id,
            )
            .outerjoin(first_source, first_source.c.opportunity_id == opportunity.c.id)
            .outerjoin(document, document.c.opportunity_id == opportunity.c.id)
            .where(document.c.id.is_(None))
            .order_by(opportunity.c.id)
        )
        try:
            with self._engine.connect() as connection:
                rows = connection.execute(statement).all()
            return [
                OpportunityRecord(
                    id=int(row[0]),
                    title=row[1],
                    description=row[2] or "",
                    eligibility=row[3] or "",
                    required_documents=[str(item) for item in _as_list(row[4])],
                    application_steps=[str(item) for item in _as_list(row[5])],
                    source_id=int(row[6]) if row[6] is not None else None,
                )
                for row in rows
            ]
        except (SQLAlchemyError, ValueError, TypeError) as exc:
            raise StoreError("Falha ao consultar oportunidades sem documentos.") from exc

    def insert_documents(self, documents: Sequence[NewDocument]) -> int:
        rows = [
            {
                "opportunity_id": item.opportunity_id,
                "source_id": item.source_id,
                "chunk_index": item.chunk_index,
                "content": item.content,
            }
            for item in documents
        ]
        if not rows:
            return 0
        try:
            with self._engine.begin() as connection:
                for start in range(0, len(rows), WRITE_BATCH_SIZE):
                    connection.execute(insert(document), rows[start : start + WRITE_BATCH_SIZE])
        except SQLAlchemyError as exc:
            raise StoreError("Falha ao gravar os documentos.") from exc
        return len(rows)
