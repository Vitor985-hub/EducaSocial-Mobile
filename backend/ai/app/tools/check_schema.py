import sys

from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.container import build_engine
from app.core.config import get_settings
from app.core.exceptions import AIServiceError

EXPECTED_COLUMNS: dict[str, set[str]] = {
    "region": {"id", "name", "level", "state", "parent_id"},
    "opportunity": {
        "id",
        "title",
        "description",
        "eligibility",
        "required_documents",
        "application_steps",
        "region_id",
        "status",
        "last_reviewed",
    },
    "source": {"id", "opportunity_id", "name", "url"},
    "document": {"id", "opportunity_id", "source_id", "chunk_index", "content", "embedding_model"},
    "document_embedding": {"id", "document_id", "embedding_model", "dimensions", "embedding"},
}


def find_schema_problems(engine: Engine) -> list[str]:
    inspector = inspect(engine)
    problems: list[str] = []
    for table, expected in EXPECTED_COLUMNS.items():
        if not inspector.has_table(table):
            problems.append(f"Tabela ausente: {table}")
            continue
        present = {column["name"] for column in inspector.get_columns(table)}
        missing = sorted(expected - present)
        if missing:
            problems.append(f"Colunas ausentes em {table}: {', '.join(missing)}")
    return problems


def describe_contents(engine: Engine) -> list[str]:
    inspector = inspect(engine)
    lines: list[str] = []
    with engine.connect() as connection:
        for table in EXPECTED_COLUMNS:
            if not inspector.has_table(table):
                continue
            total = connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            lines.append(f"{table}: {total} linhas")
        if inspector.has_table("document_embedding"):
            rows = connection.execute(
                text(
                    "SELECT embedding_model, dimensions, COUNT(*) "
                    "FROM document_embedding GROUP BY embedding_model, dimensions"
                )
            ).all()
            for model, dimensions, total in rows:
                lines.append(f"  embeddings {model} ({dimensions} dimensões): {total}")
    return lines


def main() -> int:
    try:
        engine = build_engine(get_settings())
        problems = find_schema_problems(engine)
        for line in describe_contents(engine):
            print(line)
    except AIServiceError as exc:
        print(f"Erro: {exc.message}", file=sys.stderr)
        return 1
    except SQLAlchemyError as exc:
        print(f"Não foi possível consultar o banco: {type(exc).__name__}", file=sys.stderr)
        return 1
    if problems:
        print("\nProblemas encontrados:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("\nSchema compatível com o módulo de IA.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
