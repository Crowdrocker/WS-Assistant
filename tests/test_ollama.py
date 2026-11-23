from __future__ import annotations

import json
from io import BytesIO
from urllib.request import Request

import pytest

from ws_assistant.ai.intent import parse_intent
from ws_assistant.ai.ollama import OllamaClient, OllamaError


class FakeResponse(BytesIO):
    def __init__(self, value: dict) -> None:
        super().__init__(json.dumps(value).encode("utf-8"))


def test_interpret_requests_structured_non_streaming_output(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    content = json.dumps(
        {
            "kind": "action_request",
            "action": "switch_obs_scene",
            "arguments": {"scene": "Gaming"},
            "response": "Switching to Gaming.",
        }
    )

    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse({"message": {"content": content}})

    monkeypatch.setattr("ws_assistant.ai.ollama.urlopen", fake_urlopen)
    result = OllamaClient("http://127.0.0.1:11434/", "llama3.2").interpret("Switch to gaming")

    request = captured["request"]
    assert isinstance(request, Request)
    body = json.loads(request.data)
    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    assert body["stream"] is False
    assert body["format"]["required"] == ["kind", "action", "arguments", "response"]
    assert result.to_dict()["arguments"] == {"scene": "Gaming"}
    assert captured["timeout"] == 120


def test_check_model_accepts_default_latest_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ws_assistant.ai.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse({"models": [{"name": "llama3.2:latest"}]}),
    )
    assert OllamaClient("http://localhost:11434", "llama3.2").check_model()


@pytest.mark.parametrize(
    "content",
    [
        '{"kind":"action_request","action":"rm -rf","arguments":{},"response":"Done"}',
        '{"kind":"answer","action":"switch_obs_scene","arguments":{},"response":"Done"}',
        '{"kind":"answer","action":null,"arguments":[],"response":"Done"}',
        '{"kind":[],"action":null,"arguments":{},"response":"Done"}',
        '{"kind":"unknown","action":null,"arguments":{},"response":"Done"}',
    ],
)
def test_rejects_invalid_intents(content: str) -> None:
    with pytest.raises(ValueError):
        parse_intent(content)


def test_reports_invalid_ollama_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ws_assistant.ai.ollama.urlopen",
        lambda *_args, **_kwargs: FakeResponse({"message": {"content": "not json"}}),
    )
    with pytest.raises(ValueError, match="not valid JSON"):
        OllamaClient("http://localhost:11434", "llama3.2").interpret("hello")


@pytest.mark.parametrize(
    "base_url",
    [
        "file:///tmp/ollama",
        "http://user:password@localhost:11434",
        "http://localhost:11434?token=secret",
    ],
)
def test_rejects_unsafe_base_urls(base_url: str) -> None:
    with pytest.raises(ValueError):
        OllamaClient(base_url, "llama3.2")


def test_reports_connection_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import URLError

    def fail(*_args: object, **_kwargs: object) -> None:
        raise URLError("refused")

    monkeypatch.setattr("ws_assistant.ai.ollama.urlopen", fail)
    with pytest.raises(OllamaError, match="Could not connect to Ollama"):
        OllamaClient("http://localhost:11434", "llama3.2").check_model()
