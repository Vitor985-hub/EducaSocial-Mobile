from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.api.dependencies import ProgramServiceDep
from app.models.program import ProgramCategory
from app.schemas.common import Page
from app.schemas.error import ErrorResponse
from app.schemas.program import ProgramDetail, ProgramSummary

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("", response_model=Page[ProgramSummary])
def list_programs(
    service: ProgramServiceDep,
    q: Annotated[
        str | None,
        Query(min_length=2, max_length=100, description="Busca por texto no nome e na descrição."),
    ] = None,
    category: Annotated[ProgramCategory | None, Query(description="Categoria do programa.")] = None,
    state: Annotated[
        str | None,
        Query(min_length=2, max_length=2, description="Sigla da UF, por exemplo SP."),
    ] = None,
    municipality: Annotated[
        str | None,
        Query(min_length=2, max_length=100, description="Município. Exige o parâmetro state."),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Page[ProgramSummary]:
    result = service.list_programs(
        query=q,
        category=category,
        state=state,
        municipality=municipality,
        page=page,
        page_size=page_size,
    )
    return Page[ProgramSummary](
        items=[ProgramSummary.model_validate(program) for program in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get(
    "/{program_id}",
    response_model=ProgramDetail,
    responses={404: {"model": ErrorResponse}},
)
def get_program(
    program_id: Annotated[int, Path(ge=1)],
    service: ProgramServiceDep,
) -> ProgramDetail:
    return ProgramDetail.model_validate(service.get_program(program_id))
