import logging
from collections.abc import Iterator, Sequence
from typing import Any

import httpx

from app.core.exceptions import ProviderError

logger = logging.getLogger(__name__)


def make_client(
    base_url: str,
    timeout: float,
    headers: dict[str, str] | None = None,
    transport: httpx.BaseTransport | None = None,
) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        timeout=timeout,
        headers=headers,
        transport=transport,
    )


def post_json(
    client: httpx.Client, path: str, payload: dict[str, Any], provider: str
) -> dict[str, Any]:
    try:
        response = client.post(path, json=payload)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.warning("%s respondeu HTTP %s em %s", provider, status, path)
        raise ProviderError(f"{provider} retornou erro HTTP {status}.") from exc
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("%s indisponível: %s", provider, type(exc).__name__)
        raise ProviderError(f"{provider} indisponível ou com resposta inválida.") from exc
    if not isinstance(data, dict):
        raise ProviderError(f"{provider} retornou uma resposta em formato inesperado.")
    return data


def batches(items: Sequence[Any], size: int) -> Iterator[Sequence[Any]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]
