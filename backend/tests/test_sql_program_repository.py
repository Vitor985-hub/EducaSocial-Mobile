import json

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from app.core.exceptions import ProgramStoreError
from app.models.program import CoverageScope, ProgramCategory
from app.repositories.program import ProgramFilters
from app.repositories.sql_program import SqlProgramRepository

SCHEMA = [
    "CREATE TABLE region (id INTEGER PRIMARY KEY, name TEXT, level TEXT, state TEXT,"
    " parent_id INTEGER)",
    "CREATE TABLE category (id INTEGER PRIMARY KEY, name TEXT)",
    "CREATE TABLE opportunity (id INTEGER PRIMARY KEY, title TEXT, description TEXT,"
    " eligibility TEXT, required_documents TEXT, application_steps TEXT, region_id INTEGER,"
    " category_id INTEGER, last_reviewed DATE, status TEXT)",
    "CREATE TABLE source (id INTEGER PRIMARY KEY, opportunity_id INTEGER, name TEXT, url TEXT)",
]


@pytest.fixture
def engine() -> Engine:
    eng = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    with eng.begin() as conn:
        for statement in SCHEMA:
            conn.execute(text(statement))
        conn.execute(
            text(
                "INSERT INTO region VALUES (1,'Brasil','national',NULL,NULL),"
                "(2,'São Paulo','state','SP',1),(3,'São Paulo','city',NULL,2)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO category VALUES "
                "(1,'Renda'),(2,'Assistência Social'),(3,'Desconhecida')"
            )
        )
        rows = [
            (
                1,
                "Bolsa Família",
                "Programa federal de renda. Segunda frase.",
                "Renda baixa.\nCadastro",
                1,
                1,
            ),
            (2, "CRAS", "Centro de atendimento.", "Qualquer pessoa.", 3, 2),
            (3, "Fora do mapa", "x", "y", 1, 3),
        ]
        for pid, title, desc, elig, region_id, category_id in rows:
            conn.execute(
                text(
                    "INSERT INTO opportunity VALUES "
                    "(:i,:t,:d,:e,:docs,:steps,:r,:c,:lr,'unconfirmed')"
                ),
                {
                    "i": pid,
                    "t": title,
                    "d": desc,
                    "e": elig,
                    "docs": json.dumps(["RG", "CPF"]),
                    "steps": json.dumps(["Procure o CRAS", "Leve os documentos"]),
                    "r": region_id,
                    "c": category_id,
                    "lr": "2026-11-13",
                },
            )
        conn.execute(
            text(
                "INSERT INTO source VALUES (1,1,'MDS','https://mds.invalid'),(2,2,'SMADS','https://smads.invalid')"
            )
        )
    return eng


def test_maps_national_program(engine: Engine) -> None:
    program = SqlProgramRepository(engine).get_by_id(1)

    assert program is not None
    assert program.name == "Bolsa Família"
    assert program.summary == "Programa federal de renda."
    assert program.category is ProgramCategory.RENDA
    assert program.scope is CoverageScope.NACIONAL
    assert (program.state, program.municipality) == (None, None)
    assert program.eligibility == ("Renda baixa.", "Cadastro")
    assert program.managing_body == "MDS"
    assert program.official_url == "https://mds.invalid"
    assert program.how_to_apply.startswith("1. Procure o CRAS\n2. Leve os documentos")
    assert "Documentos: RG; CPF." in program.how_to_apply


def test_maps_city_program_with_state_from_parent(engine: Engine) -> None:
    program = SqlProgramRepository(engine).get_by_id(2)

    assert program is not None
    assert program.category is ProgramCategory.ASSISTENCIA_SOCIAL
    assert program.scope is CoverageScope.MUNICIPAL
    assert (program.state, program.municipality) == ("SP", "São Paulo")


def test_skips_rows_with_unmapped_category(engine: Engine) -> None:
    repository = SqlProgramRepository(engine)

    items, total = repository.list_programs(ProgramFilters(), 0, 20)

    assert [item.id for item in items] == [1, 2]
    assert total == 2
    assert repository.get_by_id(3) is None


def test_applies_location_and_query_filters(engine: Engine) -> None:
    repository = SqlProgramRepository(engine)

    outside, _ = repository.list_programs(ProgramFilters(state="RJ"), 0, 20)
    queried, _ = repository.list_programs(ProgramFilters(query="cras"), 0, 20)

    assert [item.id for item in outside] == [1]
    assert [item.id for item in queried] == [2]


def test_database_failure_becomes_store_error() -> None:
    broken = create_engine("sqlite://")

    with pytest.raises(ProgramStoreError):
        SqlProgramRepository(broken).get_by_id(1)
