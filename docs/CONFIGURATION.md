# Configuration

Copy the example file:

```bash
cp config/assistant.example.yaml config/assistant.yaml
```

`config/assistant.yaml` is ignored by Git so local settings do not get committed.

The v0.1 foundation validates the assistant name, local runtime mode, and OBS port. Most integration settings are placeholders for later milestones.

Never put API keys, OBS passwords, or other credentials in a committed config file.
