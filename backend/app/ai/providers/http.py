import logging
import time
from collections.abc import Iterator, Sequence
from typing import Any

import httpx

from app.ai.core.exceptions import ProviderError

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = frozenset({502, 503, 504})
RETRY_DELAYS = (2.0,)


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
    attempt = 0
    while True:
        try:
            response = client.post(path, json=payload)
            response.raise_for_status()
            data = response.json()
            break
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.warning("%s respondeu HTTP %s em %s", provider, status, path)
            if status in RETRYABLE_STATUS and attempt < len(RETRY_DELAYS):
                time.sleep(RETRY_DELAYS[attempt])
                attempt += 1
                continue
            raise ProviderError(f"{provider} retornou erro HTTP {status}.") from exc
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            logger.warning("%s indisponível: %s", provider, type(exc).__name__)
            if attempt < len(RETRY_DELAYS):
                time.sleep(RETRY_DELAYS[attempt])
                attempt += 1
                continue
            raise ProviderError(f"{provider} indisponível ou com resposta inválida.") from exc
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("%s indisponível: %s", provider, type(exc).__name__)
            raise ProviderError(f"{provider} indisponível ou com resposta inválida.") from exc
    if not isinstance(data, dict):
        raise ProviderError(f"{provider} retornou uma resposta em formato inesperado.")
    return data


def batches(items: Sequence[Any], size: int) -> Iterator[Sequence[Any]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]