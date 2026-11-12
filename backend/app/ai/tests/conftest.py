from datetime import date

import pytest
from sqlalchemy import Engine, create_engine, insert
from sqlalchemy.pool import StaticPool

from app.repositories import mysql
from app.repositories.mysql import SqlChunkRepository


@pytest.fixture
def engine() -> Engine:
    test_engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    mysql.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture
def repository(engine: Engine) -> SqlChunkRepository:
    return SqlChunkRepository(engine)


@pytest.fixture
def seeded_engine(engine: Engine) -> Engine:
    with engine.begin() as connection:
        connection.execute(
            insert(mysql.region),
            [
                {"id": 1, "name": "Brasil", "level": "national", "state": None, "parent_id": None},
                {"id": 2, "name": "São Paulo", "level": "state", "state": "SP", "parent_id": 1},
                {"id": 3, "name": "Santo André", "level": "city", "state": None, "parent_id": 2},
            ],
        )
        base = {
            "required_documents": ["RG", "CPF"],
            "application_steps": ["Procurar o atendimento", "Entregar os documentos"],
            "status": "current",
            "last_reviewed": date(2026, 11, 1),
        }
        connection.execute(
            insert(mysql.opportunity),
            [
                {
                    "id": 1,
                    "title": "Programa nacional",
                    "description": "Descrição nacional.",
                    "eligibility": "Elegibilidade nacional.",
                    "region_id": 1,
                    **base,
                },
                {
                    "id": 2,
                    "title": "Programa estadual",
                    "description": "Descrição estadual.",
                    "eligibility": "Elegibilidade estadual.",
                    "region_id": 2,
                    **base,
                },
                {
                    "id": 3,
                    "title": "Programa municipal",
                    "description": "Descrição municipal.",
                    "eligibility": "Elegibilidade municipal.",
                    "region_id": 3,
                    **base,
                },
            ],
        )
        connection.execute(
            insert(mysql.source),
            [
                {
                    "id": 1,
                    "opportunity_id": 1,
                    "name": "Fonte nacional",
                    "url": "https://a.invalid",
                },
                {
                    "id": 2,
                    "opportunity_id": 3,
                    "name": "Fonte municipal",
                    "url": "https://c.invalid",
                },
            ],
        )
    return engine
