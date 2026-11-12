import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_rag_service
from app.core.config import Settings, get_settings
from app.core.exceptions import ProviderError
from app.main import create_app
from app.services.rag_service import RagService
from app.services.retrieval import ChunkIndexProvider
from tests.fakes import HashEmbedder, ScriptedLLM, StaticRepository, make_chunk

URL = "/v1/query"
EMBEDDER = HashEmbedder()


def build_service(llm=None) -> RagService:
    chunk = make_chunk(
        EMBEDDER,
        opportunity_id=5,
        content="auxílio aluguel moradia atendimento",
        source_name="Prefeitura",
        source_url="https://prefeitura.invalid/aluguel",
    )
    index = ChunkIndexProvider(StaticRepository([chunk]), EMBEDDER.model_name, 300)
    return RagService(EMBEDDER, llm or ScriptedLLM("Resposta [1]."), index, 3, 0.2)


@pytest.fixture
def app() -> FastAPI:
    application = create_app()
    application.dependency_overrides[get_rag_service] = build_service
    application.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_query_returns_contract_shape(client: TestClient) -> None:
    response = client.post(URL, json={"question": "auxílio aluguel moradia", "state": "sp"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Resposta [1].",
        "sources": [
            {"title": "Prefeitura", "program_id": 5, "url": "https://prefeitura.invalid/aluguel"}
        ],
    }


def test_query_rejects_short_question(client: TestClient) -> None:
    assert client.post(URL, json={"question": "a"}).status_code == 422


def test_query_rejects_municipality_without_state(client: TestClient) -> None:
    response = client.post(URL, json={"question": "auxílio aluguel", "municipality": "Santos"})

    assert response.status_code == 422


def test_api_key_is_enforced_when_configured(app: FastAPI, client: TestClient) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, ai_service_api_key="segredo"
    )
    body = {"question": "auxílio aluguel moradia"}

    missing = client.post(URL, json=body)
    wrong = client.post(URL, json=body, headers={"X-API-Key": "errada"})
    valid = client.post(URL, json=body, headers={"X-API-Key": "segredo"})

    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "unauthorized"
    assert wrong.status_code == 401
    assert valid.status_code == 200


def test_health_does_not_require_api_key(app: FastAPI, client: TestClient) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, ai_service_api_key="segredo"
    )

    assert client.get("/health").status_code == 200


def test_provider_failure_becomes_503(app: FastAPI, client: TestClient) -> None:
    class FailingEmbedder(HashEmbedder):
        def embed_query(self, text: str) -> list[float]:
            raise ProviderError("Ollama indisponível ou com resposta inválida.")

    service = build_service()
    service._embedder = FailingEmbedder()
    app.dependency_overrides[get_rag_service] = lambda: service

    response = client.post(URL, json={"question": "auxílio aluguel moradia"})

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "provider_unavailable",
            "message": "Ollama indisponível ou com resposta inválida.",
        }
    }
