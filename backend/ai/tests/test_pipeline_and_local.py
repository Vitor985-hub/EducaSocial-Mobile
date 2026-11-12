from pathlib import Path

import pytest
from sqlalchemy import Engine

from app.core.exceptions import ConfigurationError, ProviderError
from app.repositories.local import LocalChunkRepository
from app.repositories.mysql import SqlChunkRepository
from app.tools.check_schema import find_schema_problems
from ingestion.pipeline import build_documents, embed_pending
from tests.fakes import HashEmbedder


def test_build_documents_simulates_by_default(seeded_engine: Engine) -> None:
    repository = SqlChunkRepository(seeded_engine)

    report = build_documents(repository, 1200, 150, apply=False)

    assert report.opportunities == 3
    assert report.documents == 12
    assert report.applied is False
    assert repository.pending_documents("m") == []


def test_build_documents_apply_is_idempotent(seeded_engine: Engine) -> None:
    repository = SqlChunkRepository(seeded_engine)

    first = build_documents(repository, 1200, 150, apply=True)
    second = build_documents(repository, 1200, 150, apply=True)

    assert first.documents == 12
    assert len(repository.pending_documents("m")) == 12
    assert second.opportunities == 0
    assert second.documents == 0
    assert len(repository.pending_documents("m")) == 12


def test_embed_dry_run_does_not_call_provider_or_write(seeded_engine: Engine) -> None:
    repository = SqlChunkRepository(seeded_engine)
    build_documents(repository, 1200, 150, apply=True)
    embedder = HashEmbedder()

    report = embed_pending(repository, embedder, apply=False)

    assert report.pending == 12
    assert report.embedded == 0
    assert embedder.document_calls == 0
    assert len(repository.load_chunks(embedder.model_name)) == 0


def test_embed_apply_batches_and_is_idempotent(
    seeded_engine: Engine, capsys: pytest.CaptureFixture[str]
) -> None:
    repository = SqlChunkRepository(seeded_engine)
    build_documents(repository, 1200, 150, apply=True)
    embedder = HashEmbedder()

    first = embed_pending(repository, embedder, apply=True, batch_size=5)
    second = embed_pending(repository, embedder, apply=True, batch_size=5)

    assert first.embedded == 12
    assert embedder.document_calls == 3
    assert second.pending == 0
    chunks = repository.load_chunks(embedder.model_name)
    assert len(chunks) == 12
    assert {chunk.region_level for chunk in chunks} == {"national", "state", "city"}
    assert "12/12" in capsys.readouterr().out


def test_embed_rejects_inconsistent_vectors(seeded_engine: Engine) -> None:
    repository = SqlChunkRepository(seeded_engine)
    build_documents(repository, 1200, 150, apply=True)

    class BrokenEmbedder(HashEmbedder):
        def embed_documents(self, texts):
            return [[1.0]] * (len(texts) - 1)

    with pytest.raises(ProviderError):
        embed_pending(repository, BrokenEmbedder(), apply=True)


def test_local_repository_roundtrip_and_persistence(tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    documents = [
        {
            "document_id": 1,
            "opportunity_id": 1,
            "content": "texto",
            "opportunity_title": "Programa",
            "region_level": "state",
            "region_state": "SP",
            "region_name": "São Paulo",
            "last_reviewed": "2026-11-01",
        }
    ]
    repository = LocalChunkRepository(documents=documents, path=path)
    embedder = HashEmbedder()

    assert [item.document_id for item in repository.pending_documents(embedder.model_name)] == [1]
    embed_pending(repository, embedder, apply=True)

    reloaded = LocalChunkRepository(path)
    chunks = reloaded.load_chunks(embedder.model_name)
    assert len(chunks) == 1
    assert chunks[0].region_state == "SP"
    assert chunks[0].last_reviewed.isoformat() == "2026-11-01"
    assert reloaded.pending_documents(embedder.model_name) == []
    assert reloaded.load_chunks("outro-modelo") == []


def test_local_repository_does_not_support_document_building() -> None:
    with pytest.raises(ConfigurationError):
        LocalChunkRepository().opportunities_without_documents()


def test_example_store_file_is_loadable() -> None:
    repository = LocalChunkRepository(Path("data/local_store.example.json"))

    assert len(repository.pending_documents("qualquer")) == 3


def test_schema_check_passes_on_expected_schema(engine: Engine) -> None:
    assert find_schema_problems(engine) == []


def test_schema_check_reports_missing_table_and_columns(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE document_embedding")
        connection.exec_driver_sql("DROP TABLE source")
        connection.exec_driver_sql("CREATE TABLE source (id INTEGER PRIMARY KEY, name TEXT)")

    problems = find_schema_problems(engine)

    assert "Tabela ausente: document_embedding" in problems
    assert "Colunas ausentes em source: opportunity_id, url" in problems
