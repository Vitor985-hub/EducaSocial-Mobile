import pytest
from pydantic import ValidationError

from app.ai.core.config import Settings
from app.ai.core.exceptions import ConfigurationError


def make_settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_defaults_use_ollama_for_llm_and_embeddings() -> None:
    settings = make_settings()

    assert settings.llm_provider == "ollama"
    assert settings.embedding_provider == "ollama"
    assert settings.ollama_embedding_model == "bge-m3"


def test_llm_and_embedding_providers_are_independent() -> None:
    settings = make_settings(llm_provider="gemini", embedding_provider="ollama")

    assert settings.llm_provider == "gemini"
    assert settings.embedding_provider == "ollama"


def test_database_url_escapes_special_characters_in_password() -> None:
    settings = make_settings(
        db_host="db.exemplo.invalid", db_name="educa", db_user="app", db_password="p@ss:w/rd"
    )

    url = settings.database_url

    assert url.password == "p@ss:w/rd"
    assert url.host == "db.exemplo.invalid"
    assert "p@ss:w/rd" not in url.render_as_string(hide_password=True)


def test_database_url_reports_missing_variables_without_values() -> None:
    settings = make_settings(db_host="db.exemplo.invalid")

    with pytest.raises(ConfigurationError) as error:
        _ = settings.database_url

    assert "DB_NAME" in error.value.message
    assert "DB_USER" in error.value.message
    assert "DB_HOST" not in error.value.message


def test_production_requires_api_key() -> None:
    with pytest.raises(ValidationError):
        make_settings(environment="production")

    assert make_settings(environment="production", ai_service_api_key="segredo")


def test_overlap_must_be_smaller_than_chunk_size() -> None:
    with pytest.raises(ValidationError):
        make_settings(chunk_max_chars=300, chunk_overlap_chars=300)


def test_secrets_are_not_exposed_in_repr() -> None:
    settings = make_settings(ai_service_api_key="segredo", gemini_api_key="outro", db_password="x")

    text = repr(settings)

    assert "segredo" not in text
    assert "outro" not in text
