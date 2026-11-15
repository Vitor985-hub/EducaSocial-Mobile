import httpx
import pytest

from app.ai.core.exceptions import ProviderError
from app.ai.providers import http as http_module


def test_transient_gateway_errors_are_retried_then_succeed(monkeypatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(http_module.time, "sleep", sleeps.append)
    responses = iter([503, 200])
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        status = next(responses)
        return httpx.Response(status, json={"ok": True})

    client = http_module.make_client("http://x", 5, transport=httpx.MockTransport(handler))

    assert http_module.post_json(client, "/p", {}, "Teste") == {"ok": True}
    assert calls["count"] == 2
    assert sleeps == [2.0]


def test_persistent_503_gives_up_after_one_retry(monkeypatch) -> None:
    monkeypatch.setattr(http_module.time, "sleep", lambda seconds: None)
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(503, json={})

    client = http_module.make_client("http://x", 5, transport=httpx.MockTransport(handler))

    with pytest.raises(ProviderError, match="503"):
        http_module.post_json(client, "/p", {}, "Teste")
    assert calls["count"] == 2


@pytest.mark.parametrize("status", [404, 429])
def test_rate_limit_and_client_errors_are_not_retried(monkeypatch, status: int) -> None:
    monkeypatch.setattr(http_module.time, "sleep", lambda seconds: None)
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(status, json={})

    client = http_module.make_client("http://x", 5, transport=httpx.MockTransport(handler))

    with pytest.raises(ProviderError, match=str(status)):
        http_module.post_json(client, "/p", {}, "Teste")
    assert calls["count"] == 1