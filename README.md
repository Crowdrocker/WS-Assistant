# WS Assistant

A local-first, modular desktop assistant for Linux. Ollama can turn typed requests into structured intent proposals. Voice recognition, OBS, and desktop integrations remain separate follow-up modules.

## Current status

**Local AI milestone**

- Python package and command-line entry point
- YAML configuration with a sample config
- Safe command registry (no arbitrary shell execution)
- Ollama connectivity/model check and structured intent interpretation
- Basic status and configuration validation commands
- Arch Linux and Fedora setup helpers
- Unit tests

Not implemented yet: microphone capture, wake-word detection, Whisper, TTS, OBS WebSocket, or compositor-specific automation.

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
ws-assistant ai-check
ws-assistant interpret "Switch OBS to the gaming scene"
```

The application reads `config/assistant.yaml` when present. Otherwise it uses built-in defaults. Do not commit personal tokens, passwords, or private device details.

On Void Linux, run Ollama as a local service or user process and pull the configured model (`ollama pull llama3.2`). The assistant connects to `http://127.0.0.1:11434` by default. `interpret` accepts text for now; it prints a structured proposal and does not execute desktop commands.

## Safety

WS Assistant must never pass an AI-generated string directly to a shell. Current Ollama output is an untrusted, validated proposal only; no desktop action is executed. Future integrations will use named, allow-listed actions with validated arguments. Destructive or privacy-sensitive actions should require explicit confirmation.

## Development

```bash
python -m pytest
```

See `docs/` for architecture, configuration, and roadmap details.

## License

Review the repository's existing `LICENSE` file before redistributing this scaffold.
