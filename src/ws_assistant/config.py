from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "assistant": {"name": "WS Assistant", "log_level": "INFO"},
    "runtime": {"mode": "local"},
    "ai": {"provider": "ollama", "base_url": "http://127.0.0.1:11434", "model": "llama3.2"},
    "voice": {"enabled": False, "speech_to_text": "whisper.cpp", "text_to_speech": "system"},
    "desktop": {"compositor": "auto", "confirm_sensitive_actions": True},
    "integrations": {"obs": {"enabled": False, "host": "127.0.0.1", "port": 4455}},
}


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load YAML config, falling back to safe built-in defaults."""
    config_path = path or Path("config/assistant.yaml")
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError("Configuration root must be a YAML mapping.")
    merged = DEFAULT_CONFIG.copy()
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
    port = config.get("integrations", {}).get("obs", {}).get("port", 4455)
    if not isinstance(port, int) or not 1 <= port <= 65535:
        errors.append("integrations.obs.port must be an integer from 1 to 65535.")
    return errors
