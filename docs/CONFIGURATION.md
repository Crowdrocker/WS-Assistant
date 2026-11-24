# Configuration

Copy the example file:

```bash
cp config/assistant.example.yaml config/assistant.yaml
```

`config/assistant.yaml` is ignored by Git so local settings do not get committed.

The configuration validates the assistant name, local runtime mode, Ollama URL/model/timeout, and OBS port. `ai.base_url` defaults to the local Ollama endpoint and `ai.model` must match a model installed in Ollama to use `ai-check` or `interpret`.

Never put API keys, OBS passwords, or other credentials in a committed config file.

For the first local AI setup, install/run Ollama using the method supported by your Void Linux system, then fetch the configured model:

```bash
ollama pull llama3.2
ws-assistant ai-check
ws-assistant interpret "Switch OBS to the gaming scene"
```

`interpret` currently produces a structured proposal only. It does not execute the suggested action.
