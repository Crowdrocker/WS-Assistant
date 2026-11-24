# Architecture

WS Assistant is a local-first Python application with optional integrations.

```text
Voice input (future) -> Speech-to-text --+
Typed text ------------------------------+-> Ollama intent interpreter
                                          -> Validated proposal (current)
                                          -> Allow-listed actions -> Desktop / OBS / audio adapters (future)
Response -> Text-to-speech (future)
```

## Design rules

1. Keep the core usable without Ollama, a microphone, or OBS.
2. Keep platform-specific behavior behind integration modules.
3. Treat AI output as untrusted and never execute AI-generated shell commands.
4. Validate structured intent output before passing it to any future action router.
5. Require confirmation for sensitive actions.
6. Keep credentials out of committed config files.

The current `ai/` module uses Ollama's local `/api/chat` endpoint and structured JSON output. It does not execute actions. Planned packages: `voice/`, `commands/`, `desktop/`, and `integrations/`.
