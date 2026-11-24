from __future__ import annotations

import argparse
import json
import logging
import platform
import sys
from pathlib import Path

from ws_assistant import __version__
from ws_assistant.ai.ollama import OllamaClient, OllamaError
from ws_assistant.config import load_config, validate_config
from ws_assistant.voice.whisper import VoiceError, record_and_transcribe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ws-assistant", description="Local-first desktop assistant.")
    parser.add_argument("--config", type=Path, help="Path to assistant YAML config.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("status", help="Show basic runtime information.")
    subparsers.add_parser("config-check", help="Validate the configuration.")
    subparsers.add_parser("actions", help="List registered safe actions.")
    subparsers.add_parser("ai-check", help="Check Ollama connectivity and configured model.")
    interpret = subparsers.add_parser("interpret", help="Turn text into a structured intent proposal.")
    interpret.add_argument("text", help="Text to interpret as a desktop assistant request.")
    subparsers.add_parser("voice", help="Record a voice request and print its intent proposal.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        config = load_config(args.config)
    except (OSError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    level = str(config["assistant"].get("log_level", "INFO")).upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO))

    if args.command in (None, "status"):
        print(f"{config['assistant']['name']} v{__version__}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print("Mode: local")
        print("Ollama AI: `ws-assistant ai-check` and `ws-assistant interpret`")
        print(
            "Voice input: enabled"
            if config["voice"].get("enabled")
            else "Voice input: disabled (configure voice.enabled to enable)"
        )
        print("Desktop/OBS integrations: not enabled")
        return 0
    if args.command == "config-check":
        errors = validate_config(config)
        if errors:
            print("\n".join(f"ERROR: {error}" for error in errors))
            return 1
        print("Configuration looks good.")
        return 0
    if args.command == "actions":
        print("No desktop actions are registered yet.")
        print("Future actions will be explicitly allow-listed.")
        return 0
    if args.command in {"ai-check", "interpret", "voice"}:
        try:
            text = args.text if args.command == "interpret" else None
            if args.command == "voice":
                voice = config["voice"]
                if not voice.get("enabled"):
                    print(
                        "Voice input is disabled. Set voice.enabled: true in config/assistant.yaml.",
                        file=sys.stderr,
                    )
                    return 1
                text = record_and_transcribe(
                    recorder_command=str(voice["recorder_command"]),
                    whisper_command=str(voice["whisper_command"]),
                    model_path=str(voice["model_path"]),
                )
                print(f"Heard: {text}")
            ai = config["ai"]
            client = OllamaClient(
                base_url=str(ai["base_url"]),
                model=str(ai["model"]),
                timeout_seconds=float(ai.get("timeout_seconds", 120)),
            )
            if args.command == "ai-check":
                if client.check_model():
                    print(f"Connected to Ollama; model '{client.model}' is installed.")
                    return 0
                print(
                    f"Connected to Ollama, but model '{client.model}' is not installed.",
                    file=sys.stderr,
                )
                return 1
            if text is None:
                raise ValueError("No text was available to interpret.")
            intent = client.interpret(text)
        except (OllamaError, VoiceError, ValueError) as exc:
            print(f"Assistant error: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(intent.to_dict(), indent=2, ensure_ascii=False))
        print("Proposal only; no desktop action was executed.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
