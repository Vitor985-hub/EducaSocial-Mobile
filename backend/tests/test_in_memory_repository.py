from app.core.text import normalize_text
from app.models.program import CoverageScope, ProgramCategory
from app.repositories.in_memory_program import InMemoryProgramRepository
from app.repositories.program import ProgramFilters
from tests.factories import make_program


def build_repository() -> InMemoryProgramRepository:
    return InMemoryProgramRepository(
        [
            make_program(id=2, name="Estadual", scope=CoverageScope.ESTADUAL, state="MG"),
            make_program(id=1, name="Nacional"),
            make_program(
                id=3,
                name="Municipal",
                scope=CoverageScope.MUNICIPAL,
                state="MG",
                municipality="Belo Horizonte",
                category=ProgramCategory.MORADIA,
            ),
        ]
    )


def test_results_are_ordered_by_id() -> None:
    items, total = build_repository().list_programs(ProgramFilters(), offset=0, limit=10)

    assert [program.id for program in items] == [1, 2, 3]
    assert total == 3


def test_total_ignores_offset_and_limit() -> None:
    items, total = build_repository().list_programs(ProgramFilters(), offset=1, limit=1)

    assert [program.id for program in items] == [2]
    assert total == 3


def test_national_programs_match_any_location() -> None:
    filters = ProgramFilters(state="AM", municipality="Manaus")

    items, _ = build_repository().list_programs(filters, offset=0, limit=10)

    assert [program.id for program in items] == [1]


def test_municipal_program_requires_same_state_and_municipality() -> None:
    repository = build_repository()

    matching, _ = repository.list_programs(
        ProgramFilters(state="MG", municipality="belo horizonte"), offset=0, limit=10
    )
    other_state, _ = repository.list_programs(
        ProgramFilters(state="SP", municipality="Belo Horizonte"), offset=0, limit=10
    )

    assert [program.id for program in matching] == [1, 2, 3]
    assert [program.id for program in other_state] == [1]


def test_category_filter() -> None:
    items, _ = build_repository().list_programs(
        ProgramFilters(category=ProgramCategory.MORADIA), offset=0, limit=10
    )

    assert [program.id for program in items] == [3]


def test_get_by_id() -> None:
    repository = build_repository()

    assert repository.get_by_id(2).name == "Estadual"
    assert repository.get_by_id(42) is None


def test_normalize_text_removes_accents_and_case() -> None:
    assert normalize_text("  São Paulo ") == "sao paulo"
