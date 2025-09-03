from __future__ import annotations

from typing import Any

from src.pipeline.healthchecks import check_ollama


class DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception("bad status")

    def json(self) -> Any:
        return self._payload


def test_check_ollama_present(monkeypatch):
    def fake_get(url, timeout=5):
        assert url.endswith("/tags")
        return DummyResponse({"models": [{"name": "gemma:2b"}]})

    import requests

    monkeypatch.setattr(requests, "get", fake_get)
    ok, msg = check_ollama("http://localhost:11434/api", "gemma:2b")
    assert ok is True
    assert "Model available" in msg


def test_check_ollama_missing(monkeypatch):
    def fake_get(url, timeout=5):
        return DummyResponse({"models": []})

    import requests

    monkeypatch.setattr(requests, "get", fake_get)
    ok, msg = check_ollama("http://localhost:11434/api", "gemma:2b")
    assert ok is False
    assert "model not found" in msg

