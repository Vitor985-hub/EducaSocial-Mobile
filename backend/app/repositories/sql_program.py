import json
import re
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import ProgramStoreError
from app.core.text import normalize_text
from app.models.program import CoverageScope, Program, ProgramCategory
from app.repositories.in_memory_program import matches
from app.repositories.program import ProgramFilters

SUMMARY_LIMIT = 200

PROGRAMS_SQL = text(
    """
    SELECT o.id, o.title, o.description, o.eligibility, o.required_documents,
           o.application_steps, c.name AS category, r.level, r.name AS region_name,
           r.state AS region_state, p.state AS parent_state
    FROM opportunity o
    JOIN region r ON r.id = o.region_id
    LEFT JOIN region p ON p.id = r.parent_id
    JOIN category c ON c.id = o.category_id
    ORDER BY o.id
    """
)

SOURCES_SQL = text("SELECT opportunity_id, name, url FROM source ORDER BY id")

LEVEL_TO_SCOPE = {
    "national": CoverageScope.NACIONAL,
    "state": CoverageScope.ESTADUAL,
    "city": CoverageScope.MUNICIPAL,
}


class SqlProgramRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def list_programs(
        self, filters: ProgramFilters, offset: int, limit: int
    ) -> tuple[list[Program], int]:
        matching = [program for program in self._load() if matches(program, filters)]
        return matching[offset : offset + limit], len(matching)

    def get_by_id(self, program_id: int) -> Program | None:
        return next((program for program in self._load() if program.id == program_id), None)

    def _load(self) -> list[Program]:
        try:
            with self._engine.connect() as connection:
                rows = connection.execute(PROGRAMS_SQL).mappings().all()
                sources = connection.execute(SOURCES_SQL).mappings().all()
        except SQLAlchemyError as exc:
            raise ProgramStoreError("Não foi possível ler os programas do banco.") from exc
        by_opportunity: dict[int, list[Any]] = {}
        for source in sources:
            by_opportunity.setdefault(source["opportunity_id"], []).append(source)
        programs = []
        for row in rows:
            program = _to_program(row, by_opportunity.get(row["id"], []))
            if program is not None:
                programs.append(program)
        return programs


def _to_program(row: Any, sources: Sequence[Any]) -> Program | None:
    scope = LEVEL_TO_SCOPE.get(row["level"])
    category = _to_category(row["category"])
    if scope is None or category is None:
        return None
    description = (row["description"] or "").strip()
    state = None
    municipality = None
    if scope is CoverageScope.ESTADUAL:
        state = row["region_state"]
    elif scope is CoverageScope.MUNICIPAL:
        state = row["parent_state"] or row["region_state"]
        municipality = row["region_name"]
    return Program(
        id=row["id"],
        name=row["title"],
        summary=_summarize(description),
        description=description,
        category=category,
        scope=scope,
        state=state,
        municipality=municipality,
        managing_body=sources[0]["name"] if sources else "Órgão responsável não informado",
        eligibility=_split_lines(row["eligibility"]),
        how_to_apply=_how_to_apply(row["application_steps"], row["required_documents"]),
        official_url=sources[0]["url"] if sources else None,
    )


def _to_category(name: str | None) -> ProgramCategory | None:
    key = re.sub(r"\s+", "_", normalize_text(name or ""))
    try:
        return ProgramCategory(key)
    except ValueError:
        return None


def _summarize(description: str) -> str:
    first = re.split(r"(?<=[.!?])\s", description, maxsplit=1)[0]
    if len(first) <= SUMMARY_LIMIT:
        return first
    return first[: SUMMARY_LIMIT - 1].rstrip() + "…"


def _split_lines(value: str | None) -> tuple[str, ...]:
    return tuple(line.strip() for line in (value or "").splitlines() if line.strip())


def _how_to_apply(steps: Any, documents: Any) -> str:
    parts = []
    if steps:
        parts.append(
            "\n".join(f"{number}. {step}" for number, step in enumerate(_as_list(steps), 1))
        )
    if documents:
        parts.append("Documentos: " + "; ".join(_as_list(documents)) + ".")
    return "\n\n".join(parts)


def _as_list(value: Any) -> list[str]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return [value]
    return [str(item) for item in value]
