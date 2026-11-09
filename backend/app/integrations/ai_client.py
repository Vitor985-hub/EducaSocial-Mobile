from typing import Protocol

from app.core.exceptions import AIServiceUnavailableError
from app.schemas.ai import AIQueryRequest, AIQueryResponse


class AIServiceClient(Protocol):
    def ask(self, request: AIQueryRequest) -> AIQueryResponse: ...


class DisabledAIClient:
    def ask(self, request: AIQueryRequest) -> AIQueryResponse:
        raise AIServiceUnavailableError("O assistente de IA ainda não está disponível.")
