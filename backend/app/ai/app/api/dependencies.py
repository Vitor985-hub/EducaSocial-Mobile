import secrets
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header

from app.container import build_rag_service
from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.services.rag_service import RagService


@lru_cache
def get_rag_service() -> RagService:
    return build_rag_service(get_settings())


def require_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    expected = settings.ai_service_api_key
    if expected is None:
        return
    provided = (x_api_key or "").encode()
    if not secrets.compare_digest(provided, expected.get_secret_value().encode()):
        raise AuthenticationError("Chave de API ausente ou inválida.")
