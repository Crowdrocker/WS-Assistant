# WS Assistant

A local-first, modular desktop assistant for Linux. This first milestone provides a safe foundation; voice recognition, Ollama, OBS, and desktop integrations will be added as independent modules.

## Current status

**v0.1.0 — Foundation scaffold**

- Python package and command-line entry point
- YAML configuration with a sample config
- Safe command registry (no arbitrary shell execution)
- Basic status and configuration validation commands
- Arch Linux and Fedora setup helpers
- Unit tests

Not implemented yet: microphone capture, wake-word detection, Whisper, Ollama, TTS, OBS WebSocket, or compositor-specific automation.

## Quick start

```bash
git clone https://github.com/Crowdrocker/WS-Assistant.git
cd WS-Assistant
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp config/assistant.example.yaml config/assistant.yaml
ws-assistant status
ws-assistant config-check
```

The application reads `config/assistant.yaml` when present. Otherwise it uses built-in defaults. Do not commit personal tokens, passwords, or private device details.

## Safety

WS Assistant must never pass an AI-generated string directly to a shell. Future integrations will use named, allow-listed actions with validated arguments. Destructive or privacy-sensitive actions should require explicit confirmation.

## Development

```bash
python -m pytest
```

See `docs/` for architecture, configuration, and roadmap details.

## License

Review the repository's existing `LICENSE` file before redistributing this scaffold.
