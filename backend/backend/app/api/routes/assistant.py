from fastapi import APIRouter

from app.api.dependencies import AssistantServiceDep
from app.schemas.ai import AIQueryRequest, AIQueryResponse
from app.schemas.error import ErrorResponse

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post(
    "/query",
    response_model=AIQueryResponse,
    responses={503: {"model": ErrorResponse}},
)
def query_assistant(payload: AIQueryRequest, service: AssistantServiceDep) -> AIQueryResponse:
    return service.ask(payload)
