from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_ai_client, get_program_repository
from app.core.config import Settings, get_settings
from app.main import create_app
from app.repositories.fake_programs import FAKE_PROGRAMS
from app.repositories.in_memory_program import InMemoryProgramRepository


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.delenv("AI_ENABLED", raising=False)
    get_settings.cache_clear()
    get_ai_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_ai_client.cache_clear()


@pytest.fixture
def app() -> FastAPI:
    application = create_app()
    application.dependency_overrides[get_program_repository] = lambda: InMemoryProgramRepository(
        FAKE_PROGRAMS
    )
    return application


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client