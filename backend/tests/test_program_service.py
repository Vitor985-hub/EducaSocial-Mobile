import pytest

from app.core.exceptions import InvalidFilterError, ProgramNotFoundError
from app.models.program import CoverageScope, ProgramCategory
from app.repositories.in_memory_program import InMemoryProgramRepository
from app.services.program_service import ProgramService
from tests.factories import make_program


@pytest.fixture
def service() -> ProgramService:
    programs = [
        make_program(id=1, name="Nacional A"),
        make_program(id=2, name="Estadual SP", scope=CoverageScope.ESTADUAL, state="SP"),
        make_program(id=3, name="Estadual RJ", scope=CoverageScope.ESTADUAL, state="RJ"),
        make_program(
            id=4,
            name="Municipal Santos",
            scope=CoverageScope.MUNICIPAL,
            state="SP",
            municipality="Santos",
            category=ProgramCategory.SAUDE,
        ),
    ]
    return ProgramService(InMemoryProgramRepository(programs))


def test_list_without_filters_returns_everything(service: ProgramService) -> None:
    result = service.list_programs()

    assert result.total == 4
    assert [program.id for program in result.items] == [1, 2, 3, 4]


def test_list_applies_pagination_offset(service: ProgramService) -> None:
    result = service.list_programs(page=2, page_size=3)

    assert result.total == 4
    assert result.page == 2
    assert [program.id for program in result.items] == [4]


def test_state_is_normalized_to_upper_case(service: ProgramService) -> None:
    result = service.list_programs(state="  sp ")

    assert [program.id for program in result.items] == [1, 2, 4]


def test_municipality_filter_excludes_other_municipalities(service: ProgramService) -> None:
    result = service.list_programs(state="SP", municipality="Campinas")

    assert [program.id for program in result.items] == [1, 2]


def test_municipality_without_state_raises(service: ProgramService) -> None:
    with pytest.raises(InvalidFilterError):
        service.list_programs(municipality="Santos")


def test_unknown_state_raises(service: ProgramService) -> None:
    with pytest.raises(InvalidFilterError):
        service.list_programs(state="ZZ")


def test_get_program_returns_existing(service: ProgramService) -> None:
    assert service.get_program(3).name == "Estadual RJ"


def test_get_program_raises_when_missing(service: ProgramService) -> None:
    with pytest.raises(ProgramNotFoundError):
        service.get_program(99)
