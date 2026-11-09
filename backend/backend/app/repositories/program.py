from dataclasses import dataclass
from typing import Protocol

from app.models.program import Program, ProgramCategory


@dataclass(frozen=True, slots=True)
class ProgramFilters:
    query: str | None = None
    category: ProgramCategory | None = None
    state: str | None = None
    municipality: str | None = None


class ProgramRepository(Protocol):
    def list_programs(
        self, filters: ProgramFilters, offset: int, limit: int
    ) -> tuple[list[Program], int]: ...

    def get_by_id(self, program_id: int) -> Program | None: ...
