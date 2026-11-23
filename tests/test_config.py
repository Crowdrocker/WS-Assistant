from pathlib import Path

import pytest

from ws_assistant.config import load_config, validate_config


def test_defaults_load_when_file_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.yaml")
    assert config["assistant"]["name"] == "WS Assistant"
    assert validate_config(config) == []


def test_rejects_unknown_section(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("unknown: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown configuration section"):
        load_config(path)


def test_rejects_invalid_obs_port() -> None:
    config = load_config()
    config["integrations"]["obs"]["port"] = 70000
    assert "integrations.obs.port must be an integer from 1 to 65535." in validate_config(config)


def test_rejects_invalid_ollama_settings() -> None:
    config = load_config()
    config["ai"]["base_url"] = "file:///tmp/ollama"
    config["ai"]["model"] = " "
    config["ai"]["timeout_seconds"] = 0
    errors = validate_config(config)
    assert "ai.base_url must be an HTTP(S) URL without credentials or query." in errors
    assert "ai.model must not be empty." in errors
    assert "ai.timeout_seconds must be a positive number." in errors


def test_rejects_malformed_ollama_url_and_non_finite_timeout() -> None:
    config = load_config()
    config["ai"]["base_url"] = "http://[invalid"
    config["ai"]["timeout_seconds"] = float("nan")
    errors = validate_config(config)
    assert "ai.base_url must be an HTTP(S) URL without credentials or query." in errors
    assert "ai.timeout_seconds must be a positive number." in errors
