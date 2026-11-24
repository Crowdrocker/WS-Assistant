from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "assistant": {"name": "WS Assistant", "log_level": "INFO"},
    "runtime": {"mode": "local"},
    "ai": {"provider": "ollama", "base_url": "http://127.0.0.1:11434", "model": "llama3.2"},
    "voice": {
        "enabled": False,
        "speech_to_text": "whisper.cpp",
        "text_to_speech": "system",
        "recorder_command": "pw-record",
        "whisper_command": "whisper-cli",
        "model_path": "",
    },
    "desktop": {"compositor": "auto", "confirm_sensitive_actions": True},
    "integrations": {"obs": {"enabled": False, "host": "127.0.0.1", "port": 4455}},
}


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load YAML config, falling back to safe built-in defaults."""
    config_path = path or Path("config/assistant.yaml")
    if not config_path.exists():
        return deepcopy(DEFAULT_CONFIG)
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError("Configuration root must be a YAML mapping.")
    merged = deepcopy(DEFAULT_CONFIG)
    for section, values in loaded.items():
        if section not in DEFAULT_CONFIG:
            raise ValueError(f"Unknown configuration section: {section}")
        if not isinstance(values, dict):
            raise ValueError(f"Configuration section '{section}' must be a mapping.")
        merged[section] = {**DEFAULT_CONFIG[section], **values}
    return merged


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not str(config.get("assistant", {}).get("name", "")).strip():
        errors.append("assistant.name must not be empty.")
    if config.get("runtime", {}).get("mode") != "local":
        errors.append("Only runtime.mode: local is supported in v0.1.")
    ai = config.get("ai", {})
    base_url = ai.get("base_url", "")
    try:
        parsed_url = urlsplit(str(base_url))
        valid_base_url = (
            parsed_url.scheme in {"http", "https"}
            and bool(parsed_url.hostname)
            and not parsed_url.username
            and not parsed_url.password
            and not parsed_url.query
            and not parsed_url.fragment
        )
    except ValueError:
        valid_base_url = False
    if not valid_base_url:
        errors.append("ai.base_url must be an HTTP(S) URL without credentials or query.")
    if not str(ai.get("model", "")).strip():
        errors.append("ai.model must not be empty.")
    timeout = ai.get("timeout_seconds", 120)
    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        errors.append("ai.timeout_seconds must be a positive number.")
    voice = config.get("voice", {})
    if not isinstance(voice.get("enabled"), bool):
        errors.append("voice.enabled must be true or false.")
    if voice.get("enabled"):
        if voice.get("speech_to_text") != "whisper.cpp":
            errors.append("voice.speech_to_text must be 'whisper.cpp'.")
        if not str(voice.get("model_path", "")).strip():
            errors.append("voice.model_path is required when voice.enabled is true.")
        for key in ("recorder_command", "whisper_command"):
            if not str(voice.get(key, "")).strip():
                errors.append(f"voice.{key} must not be empty.")
    port = config.get("integrations", {}).get("obs", {}).get("port", 4455)
    if not isinstance(port, int) or not 1 <= port <= 65535:
        errors.append("integrations.obs.port must be an integer from 1 to 65535.")
    return errors
