from __future__ import annotations

import argparse
import logging
import platform
import sys
from pathlib import Path

from ws_assistant import __version__
from ws_assistant.config import load_config, validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ws-assistant", description="Local-first desktop assistant.")
    parser.add_argument("--config", type=Path, help="Path to assistant YAML config.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("status", help="Show basic runtime information.")
    subparsers.add_parser("config-check", help="Validate the configuration.")
    subparsers.add_parser("actions", help="List registered safe actions.")
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
        print("Voice/AI/OBS integrations: not enabled in this foundation build")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
