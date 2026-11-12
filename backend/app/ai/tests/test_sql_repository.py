from datetime import date

from sqlalchemy import Engine, func, insert, select

from app.repositories import mysql
from app.repositories.chunks import NewDocument
from app.repositories.mysql import SqlChunkRepository

MODEL = "modelo-a"


def seed_documents(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            insert(mysql.document),
            [
                {
                    "id": 1,
                    "opportunity_id": 1,
                    "source_id": 1,
                    "chunk_index": 0,
                    "content": "d1",
                    "embedding": [1.0, 0.0],
                    "embedding_model": MODEL,
                },
                {
                    "id": 2,
                    "opportunity_id": 3,
                    "source_id": None,
                    "chunk_index": 0,
                    "content": "d2",
                    "embedding": [0.0, 1.0],
                    "embedding_model": MODEL,
                },
                {
                    "id": 3,
                    "opportunity_id": 2,
                    "source_id": None,
                    "chunk_index": 0,
                    "content": "d3",
                    "embedding": [1.0, 1.0],
                    "embedding_model": "outro-modelo",
                },
                {
                    "id": 4,
                    "opportunity_id": 2,
                    "source_id": None,
                    "chunk_index": 1,
                    "content": "d4",
                    "embedding": None,
                    "embedding_model": None,
                },
            ],
        )


def count_documents(engine: Engine) -> int:
    with engine.connect() as connection:
        return connection.execute(select(func.count()).select_from(mysql.document)).scalar_one()


def test_load_chunks_joins_region_source_and_filters_by_model(seeded_engine: Engine) -> None:
    seed_documents(seeded_engine)

    chunks = SqlChunkRepository(seeded_engine).load_chunks(MODEL)

    assert [chunk.document_id for chunk in chunks] == [1, 2]
    national, city = chunks
    assert national.region_level == "national"
    assert national.source_name == "Fonte nacional"
    assert national.status == "current"
    assert national.last_reviewed == date(2026, 11, 1)
    assert national.embedding == [1.0, 0.0]
    assert city.region_level == "city"
    assert city.region_name == "Santo André"
    assert city.opportunity_title == "Programa municipal"


def test_city_state_falls_back_to_parent_region(seeded_engine: Engine) -> None:
    seed_documents(seeded_engine)

    city = SqlChunkRepository(seeded_engine).load_chunks(MODEL)[1]

    assert city.region_state == "SP"


def test_missing_document_source_falls_back_to_first_opportunity_source(
    seeded_engine: Engine,
) -> None:
    seed_documents(seeded_engine)

    city = SqlChunkRepository(seeded_engine).load_chunks(MODEL)[1]

    assert (city.source_name, city.source_url) == ("Fonte municipal", "https://c.invalid")


def test_load_chunks_ignores_empty_embeddings(seeded_engine: Engine) -> None:
    seed_documents(seeded_engine)
    with seeded_engine.begin() as connection:
        connection.execute(
            insert(mysql.document),
            [
                {
                    "id": 5,
                    "opportunity_id": 1,
                    "source_id": None,
                    "chunk_index": 1,
                    "content": "d5",
                    "embedding": [],
                    "embedding_model": MODEL,
                }
            ],
        )

    chunks = SqlChunkRepository(seeded_engine).load_chunks(MODEL)

    assert [chunk.document_id for chunk in chunks] == [1, 2]


def test_pending_documents_include_missing_and_other_model_embeddings(
    seeded_engine: Engine,
) -> None:
    seed_documents(seeded_engine)

    pending = SqlChunkRepository(seeded_engine).pending_documents(MODEL)

    assert [(item.document_id, item.content) for item in pending] == [(3, "d3"), (4, "d4")]


def test_save_embeddings_updates_documents_in_place(seeded_engine: Engine) -> None:
    seed_documents(seeded_engine)
    repository = SqlChunkRepository(seeded_engine)

    saved = repository.save_embeddings(MODEL, {3: [0.5, 0.5], 4: [0.1, 0.9]})
    assert saved == 2
    assert count_documents(seeded_engine) == 4
    assert repository.pending_documents(MODEL) == []

    repository.save_embeddings(MODEL, {3: [0.9, 0.1], 1: [0.2, 0.8]})
    assert count_documents(seeded_engine) == 4
    by_id = {chunk.document_id: chunk.embedding for chunk in repository.load_chunks(MODEL)}
    assert by_id[3] == [0.9, 0.1]
    assert by_id[1] == [0.2, 0.8]
    assert by_id[4] == [0.1, 0.9]


def test_save_embeddings_records_the_model_on_the_document(seeded_engine: Engine) -> None:
    seed_documents(seeded_engine)

    SqlChunkRepository(seeded_engine).save_embeddings(MODEL, {3: [0.1, 0.2, 0.3]})

    with seeded_engine.connect() as connection:
        stored_model = connection.execute(
            select(mysql.document.c.embedding_model).where(mysql.document.c.id == 3)
        ).scalar_one()
    assert stored_model == MODEL


def test_opportunities_without_documents_include_first_source(seeded_engine: Engine) -> None:
    seed_documents(seeded_engine)
    with seeded_engine.begin() as connection:
        connection.execute(mysql.document.delete().where(mysql.document.c.opportunity_id == 3))

    records = SqlChunkRepository(seeded_engine).opportunities_without_documents()

    assert [record.id for record in records] == [3]
    assert records[0].source_id == 2
    assert records[0].required_documents == ["RG", "CPF"]
    assert records[0].application_steps == ["Procurar o atendimento", "Entregar os documentos"]


def test_insert_documents_persists_rows_without_embedding(seeded_engine: Engine) -> None:
    repository = SqlChunkRepository(seeded_engine)

    inserted = repository.insert_documents(
        [
            NewDocument(opportunity_id=1, source_id=1, chunk_index=0, content="novo"),
            NewDocument(opportunity_id=1, source_id=1, chunk_index=1, content="novo 2"),
        ]
    )

    assert inserted == 2
    assert [item.content for item in repository.pending_documents(MODEL)] == ["novo", "novo 2"]
    assert repository.load_chunks(MODEL) == []
    assert repository.insert_documents([]) == 0
