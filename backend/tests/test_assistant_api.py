from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_ai_client
from app.schemas.ai import AIQueryRequest, AIQueryResponse, AISource

URL = "/api/v1/assistant/query"


class RecordingAIClient:
    def __init__(self) -> None:
        self.requests: list[AIQueryRequest] = []

    def ask(self, request: AIQueryRequest) -> AIQueryResponse:
        self.requests.append(request)
        return AIQueryResponse(
            answer="Resposta fictícia de teste.",
            sources=[AISource(title="Fonte fictícia", program_id=1)],
        )


def test_assistant_is_unavailable_until_ai_module_is_connected(client: TestClient) -> None:
    response = client.post(URL, json={"question": "Como pedir um benefício?"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_unavailable"


def test_assistant_delegates_to_ai_client_and_returns_contract(
    app: FastAPI, client: TestClient
) -> None:
    recorder = RecordingAIClient()
    app.dependency_overrides[get_ai_client] = lambda: recorder

    response = client.post(URL, json={"question": "  Como pedir um benefício?  ", "state": "sp"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Resposta fictícia de teste.",
        "sources": [{"title": "Fonte fictícia", "program_id": 1, "url": None}],
    }
    assert recorder.requests[0].question == "Como pedir um benefício?"
    assert recorder.requests[0].state == "SP"


def test_assistant_rejects_short_question(client: TestClient) -> None:
    response = client.post(URL, json={"question": "a"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_assistant_rejects_municipality_without_state(client: TestClient) -> None:
    response = client.post(
        URL, json={"question": "Quais programas existem?", "municipality": "Santos"}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_filter"
