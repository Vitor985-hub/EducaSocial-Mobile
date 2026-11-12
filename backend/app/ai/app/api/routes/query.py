from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service, require_api_key
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag_service import RagService

router = APIRouter(prefix="/v1", tags=["query"], dependencies=[Depends(require_api_key)])


@router.post("/query", response_model=QueryResponse)
def query(
    payload: QueryRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> QueryResponse:
    return service.ask(payload)
