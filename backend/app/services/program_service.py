from dataclasses import dataclass

from app.core.exceptions import ProgramNotFoundError
from app.models.program import Program, ProgramCategory
from app.repositories.program import ProgramFilters, ProgramRepository
from app.services.location import validate_location


@dataclass(frozen=True, slots=True)
class ProgramPage:
    items: list[Program]
    total: int
    page: int
    page_size: int


class ProgramService:
    def __init__(self, repository: ProgramRepository) -> None:
        self._repository = repository

    def list_programs(
        self,
        *,
        query: str | None = None,
        category: ProgramCategory | None = None,
        state: str | None = None,
        municipality: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ProgramPage:
        normalized_state, normalized_municipality = validate_location(state, municipality)
        filters = ProgramFilters(
            query=query.strip() if query else None,
            category=category,
            state=normalized_state,
            municipality=normalized_municipality,
        )
        items, total = self._repository.list_programs(
            filters, offset=(page - 1) * page_size, limit=page_size
        )
        return ProgramPage(items=items, total=total, page=page, page_size=page_size)

    def get_program(self, program_id: int) -> Program:
        program = self._repository.get_by_id(program_id)
        if program is None:
            raise ProgramNotFoundError(program_id)
        return program
