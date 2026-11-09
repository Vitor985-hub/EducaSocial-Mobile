from app.integrations.ai_client import AIServiceClient
from app.schemas.ai import AIQueryRequest, AIQueryResponse
from app.services.location import validate_location


class AssistantService:
    def __init__(self, client: AIServiceClient) -> None:
        self._client = client

    def ask(self, request: AIQueryRequest) -> AIQueryResponse:
        state, municipality = validate_location(request.state, request.municipality)
        normalized = request.model_copy(update={"state": state, "municipality": municipality})
        return self._client.ask(normalized)
