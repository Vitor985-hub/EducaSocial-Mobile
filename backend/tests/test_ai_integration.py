import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.ai.core.exceptions import ConfigurationError, ProviderError, StoreError
from app.ai.schemas.query import QueryRequest, QueryResponse, Source
from app.api import dependencies
from app.api.dependencies import get_ai_client
from app.core.config import get_settings
from app.core.exceptions import AIServiceUnavailableError
from app.integrations.ai_client import DisabledAIClient, InProcessAIClient
from app.schemas.ai import AIQueryRequest

URL = "/api/v1/assistant/query"


class FakeRagService:
    def __init__(self, error: Exception | None = None) -> None:
        self.requests: list[QueryRequest] = []
        self._error = error

    def ask(self, request: QueryRequest) -> QueryResponse:
        self.requests.append(request)
        if self._error:
            raise self._error
        return QueryResponse(
            answer="Procure o CRAS [1].",
            sources=[Source(title="Prefeitura", program_id=7, url="https://exemplo.invalid/a")],
        )


@pytest.fixture
def fresh_dependencies(monkeypatch: pytest.MonkeyPatch):
    def reset() -> None:
        get_settings.cache_clear()
        get_ai_client.cache_clear()

    reset()
    yield monkeypatch
    reset()


def test_client_maps_request_and_response() -> None:
    rag = FakeRagService()
    client = InProcessAIClient(rag)

    result = client.ask(AIQueryRequest(question="Como pedir?", state="SP", municipality="Santos"))

    assert rag.requests[0].question == "Como pedir?"
    assert (rag.requests[0].state, rag.requests[0].municipality) == ("SP", "Santos")
    assert result.answer == "Procure o CRAS [1]."
    assert result.sources[0].program_id == 7
    assert result.sources[0].url == "https://exemplo.invalid/a"


@pytest.mark.parametrize("error", [ProviderError("x"), StoreError("y"), ConfigurationError("z")])
def test_ai_failures_become_ai_unavailable_without_leaking_details(error: Exception) -> None:
    client = InProcessAIClient(FakeRagService(error))

    with pytest.raises(AIServiceUnavailableError) as raised:
        client.ask(AIQueryRequest(question="Como pedir?"))

    assert raised.value.status_code == 503
    assert raised.value.code == "ai_unavailable"
    assert str(error) not in raised.value.message


def test_route_returns_contract_through_the_in_process_client(
    app: FastAPI, client: TestClient
) -> None:
    app.dependency_overrides[get_ai_client] = lambda: InProcessAIClient(FakeRagService())

    response = client.post(URL, json={"question": "Como pedir ajuda?", "state": "sp"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Procure o CRAS [1].",
        "sources": [{"title": "Prefeitura", "program_id": 7, "url": "https://exemplo.invalid/a"}],
    }


def test_route_translates_ai_failure_to_503(app: FastAPI, client: TestClient) -> None:
    app.dependency_overrides[get_ai_client] = lambda: InProcessAIClient(
        FakeRagService(ProviderError("Gemini retornou erro HTTP 503."))
    )

    response = client.post(URL, json={"question": "Como pedir ajuda?"})

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "ai_unavailable",
            "message": "O assistente de IA está temporariamente indisponível.",
        }
    }


def test_ai_stays_disabled_by_default(fresh_dependencies: pytest.MonkeyPatch) -> None:
    fresh_dependencies.delenv("AI_ENABLED", raising=False)

    assert isinstance(dependencies.get_ai_client(), DisabledAIClient)


def test_ai_is_wired_with_the_shared_engine_when_enabled(
    fresh_dependencies: pytest.MonkeyPatch,
) -> None:
    from app import database
    from app.ai import container

    received: dict[str, object] = {}

    def fake_build(settings: object, engine: object = None) -> FakeRagService:
        received["engine"] = engine
        return FakeRagService()

    fresh_dependencies.setenv("AI_ENABLED", "true")
    fresh_dependencies.setattr(container, "build_rag_service", fake_build)

    client = dependencies.get_ai_client()

    assert isinstance(client, InProcessAIClient)
    assert received["engine"] is database.engine


def test_misconfigured_ai_falls_back_to_disabled_client(
    fresh_dependencies: pytest.MonkeyPatch,
) -> None:
    from app.ai import container

    def failing_build(settings: object, engine: object = None) -> FakeRagService:
        raise ConfigurationError("GEMINI_API_KEY ausente.")

    fresh_dependencies.setenv("AI_ENABLED", "true")
    fresh_dependencies.setattr(container, "build_rag_service", failing_build)

    assert isinstance(dependencies.get_ai_client(), DisabledAIClient)
