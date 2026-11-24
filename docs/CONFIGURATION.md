# Configuration

Copy the example file:

```bash
cp config/assistant.example.yaml config/assistant.yaml
```

`config/assistant.yaml` is ignored by Git so local settings do not get committed.

The configuration validates the assistant name, local runtime mode, Ollama URL/model/timeout, and OBS port. `ai.base_url` defaults to the local Ollama endpoint and `ai.model` must match a model installed in Ollama to use `ai-check` or `interpret`.

Never put API keys, OBS passwords, or other credentials in a committed config file.

## Voice input

Voice input is opt-in. Install `pw-record` (PipeWire) and `whisper-cli` (Whisper.cpp), download a Whisper.cpp model, and set these values in `config/assistant.yaml`:

```yaml
voice:
  enabled: true
  speech_to_text: "whisper.cpp"
  recorder_command: "pw-record"
  whisper_command: "whisper-cli"
  model_path: "/path/to/ggml-base.en.bin"
```

Run `ws-assistant voice` from an interactive terminal. It records from the default PipeWire input until you press Enter, transcribes locally, then asks Ollama to interpret the transcript. The resulting intent is only printed; no system action is executed.

In Niri, bind a key to launch it in a terminal (replace `foot` with your terminal and use the absolute path to the executable if it is only installed in a virtual environment):

```kdl
binds {
    Mod+Shift+V { spawn "foot" "-e" "ws-assistant" "voice"; }
}
```

For the first local AI setup, install/run Ollama using the method supported by your Void Linux system, then fetch the configured model:

```bash
ollama pull llama3.2
ws-assistant ai-check
ws-assistant interpret "Switch OBS to the gaming scene"
```

`interpret` currently produces a structured proposal only. It does not execute the suggested action.
