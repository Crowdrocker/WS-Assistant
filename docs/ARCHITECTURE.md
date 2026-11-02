# Architecture

WS Assistant is a local-first Python application with optional integrations.

```text
Voice input (future) -> Speech-to-text -> Intent router
AI provider (optional) ---------------> Intent router
Intent router -> Allow-listed actions -> Desktop / OBS / audio adapters
Response -> Text-to-speech (future)
```

## Design rules

1. Keep the core usable without Ollama, a microphone, or OBS.
2. Keep platform-specific behavior behind integration modules.
3. Never execute AI-generated shell commands.
4. Validate action names and arguments against explicit schemas.
5. Require confirmation for sensitive actions.
6. Keep credentials out of committed config files.

Planned packages: `voice/`, `ai/`, `commands/`, `desktop/`, and `integrations/`.
