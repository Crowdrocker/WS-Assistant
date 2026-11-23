from __future__ import annotations

import json
import math
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from ws_assistant.ai.intent import Intent, parse_intent

INTENT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["answer", "action_request", "clarification"]},
        "action": {"type": ["string", "null"]},
        "arguments": {"type": "object"},
        "response": {"type": "string"},
    },
    "required": ["kind", "action", "arguments", "response"],
    "additionalProperties": False,
}

INTENT_SYSTEM_PROMPT = """\
Interpret the user's request for a local desktop voice assistant.
Return only the requested JSON object. Never provide shell commands, code to execute,
or instructions to run a command. An action_request is only a proposal, not permission
to perform it. Use answer for general questions, action_request for a concrete desktop
action, and clarification when the request is ambiguous or missing required details.
Keep action as a short lowercase identifier (letters, digits, underscores), arguments
as a JSON object, and response as a concise sentence suitable for text-to-speech.
"""


class OllamaError(RuntimeError):
    """Raised when Ollama cannot satisfy a local AI request."""


@dataclass(frozen=True)
class OllamaClient:
    base_url: str
    model: str
    timeout_seconds: float = 120

    def __post_init__(self) -> None:
        parsed = urlsplit(self.base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Ollama base_url must be an HTTP(S) URL without credentials or query.")
        if not self.model.strip():
            raise ValueError("Ollama model must not be empty.")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("Ollama timeout_seconds must be greater than zero.")

    @property
    def _api_base(self) -> str:
        return self.base_url.rstrip("/")

    def check_model(self) -> bool:
        """Return whether the configured model is present in Ollama."""
        response = self._request("GET", "/api/tags")
        models = response.get("models")
        if not isinstance(models, list):
            raise OllamaError("Ollama returned an invalid model list.")
        installed = {
            entry["name"]
            for entry in models
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }
        return self.model in installed or f"{self.model}:latest" in installed

    def interpret(self, text: str) -> Intent:
        """Convert user text to a validated, non-executable intent proposal."""
        if not text.strip():
            raise ValueError("Request text must not be empty.")
        response = self._request(
            "POST",
            "/api/chat",
            {
                "model": self.model,
                "stream": False,
                "format": INTENT_SCHEMA,
                "messages": [
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
            },
        )
        message = response.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise OllamaError("Ollama returned an invalid chat response.")
        return parse_intent(message["content"])

    def _request(self, method: str, path: str, payload: dict[str, object] | None = None) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self._api_base}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read()
        except HTTPError as exc:
            raise OllamaError(f"Ollama returned HTTP {exc.code}.") from exc
        except URLError as exc:
            raise OllamaError(f"Could not connect to Ollama: {exc.reason}") from exc
        except OSError as exc:
            raise OllamaError(f"Could not connect to Ollama: {exc}") from exc
        try:
            decoded = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OllamaError("Ollama returned invalid JSON.") from exc
        if not isinstance(decoded, dict):
            raise OllamaError("Ollama returned an invalid response.")
        if isinstance(decoded.get("error"), str):
            raise OllamaError(f"Ollama error: {decoded['error']}")
        return decoded
