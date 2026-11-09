from collections.abc import Iterable

from app.core.text import normalize_text
from app.models.program import CoverageScope, Program
from app.repositories.program import ProgramFilters


class InMemoryProgramRepository:
    def __init__(self, programs: Iterable[Program]) -> None:
        self._programs = {program.id: program for program in programs}

    def list_programs(
        self, filters: ProgramFilters, offset: int, limit: int
    ) -> tuple[list[Program], int]:
        matching = sorted(
            (program for program in self._programs.values() if _matches(program, filters)),
            key=lambda program: program.id,
        )
        return matching[offset : offset + limit], len(matching)

    def get_by_id(self, program_id: int) -> Program | None:
        return self._programs.get(program_id)


def _matches(program: Program, filters: ProgramFilters) -> bool:
    if filters.category is not None and program.category != filters.category:
        return False
    if not _matches_location(program, filters.state, filters.municipality):
        return False
    if filters.query and not _matches_query(program, filters.query):
        return False
    return True


def _matches_location(program: Program, state: str | None, municipality: str | None) -> bool:
    if state is None or program.scope is CoverageScope.NACIONAL:
        return True
    if program.state != state:
        return False
    if program.scope is CoverageScope.ESTADUAL or municipality is None:
        return True
    return normalize_text(program.municipality or "") == normalize_text(municipality)


def _matches_query(program: Program, query: str) -> bool:
    haystack = normalize_text(f"{program.name} {program.summary} {program.description}")
    return all(token in haystack for token in normalize_text(query).split())
