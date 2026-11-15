import logging
from typing import Protocol

from app.ai.core.exceptions import AIServiceError
from app.ai.schemas.query import QueryRequest
from app.ai.services.rag_service import RagService
from app.core.exceptions import AIServiceUnavailableError
from app.schemas.ai import AIQueryRequest, AIQueryResponse

logger = logging.getLogger(__name__)

UNAVAILABLE_MESSAGE = "O assistente de IA está temporariamente indisponível."


class AIServiceClient(Protocol):
    def ask(self, request: AIQueryRequest) -> AIQueryResponse: ...


class DisabledAIClient:
    def ask(self, request: AIQueryRequest) -> AIQueryResponse:
        raise AIServiceUnavailableError("O assistente de IA ainda não está disponível.")


class InProcessAIClient:
    def __init__(self, rag_service: RagService) -> None:
        self._rag_service = rag_service

    def ask(self, request: AIQueryRequest) -> AIQueryResponse:
        try:
            result = self._rag_service.ask(QueryRequest(**request.model_dump()))
        except AIServiceError as exc:
            logger.error("Falha no módulo de IA (%s): %s", exc.code, exc.message)
            raise AIServiceUnavailableError(UNAVAILABLE_MESSAGE) from exc
        return AIQueryResponse.model_validate(result.model_dump())
