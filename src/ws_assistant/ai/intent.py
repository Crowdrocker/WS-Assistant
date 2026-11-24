from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any

_ACTION_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_INTENT_KINDS = {"answer", "action_request", "clarification"}


@dataclass(frozen=True)
class Intent:
    kind: str
    action: str | None
    arguments: dict[str, Any]
    response: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_intent(content: str) -> Intent:
    """Parse and validate structured model output without executing any of it."""
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Ollama intent was not valid JSON.") from exc
    if not isinstance(value, dict) or set(value) != {"kind", "action", "arguments", "response"}:
        raise ValueError("Ollama intent must contain kind, action, arguments, and response.")
    kind = value["kind"]
    action = value["action"]
    arguments = value["arguments"]
    response = value["response"]
    if not isinstance(kind, str) or kind not in _INTENT_KINDS:
        raise ValueError(f"Unsupported intent kind: {kind!r}.")
    if action is not None and (not isinstance(action, str) or not _ACTION_NAME.fullmatch(action)):
        raise ValueError("Intent action must be a lowercase identifier or null.")
    if not isinstance(arguments, dict):
        raise ValueError("Intent arguments must be a JSON object.")
    if not isinstance(response, str) or not response.strip():
        raise ValueError("Intent response must not be empty.")
    if kind == "action_request" and action is None:
        raise ValueError("An action_request must include an action identifier.")
    if kind != "action_request" and action is not None:
        raise ValueError("Only action_request intents may include an action identifier.")
    return Intent(kind=kind, action=action, arguments=arguments, response=response.strip())
