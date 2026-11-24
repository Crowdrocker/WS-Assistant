from __future__ import annotations

import signal
from pathlib import Path
from types import SimpleNamespace

import pytest

from ws_assistant.config import load_config, validate_config
from ws_assistant.voice.whisper import VoiceError, record_and_transcribe


def test_reports_missing_recorder(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("ws_assistant.voice.whisper.shutil.which", lambda _: None)
    with pytest.raises(VoiceError, match="Recorder 'pw-record' was not found"):
        record_and_transcribe(
            recorder_command="pw-record",
            whisper_command="whisper-cli",
            model_path=str(tmp_path / "model.bin"),
        )


def test_records_then_transcribes_to_local_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    model = tmp_path / "model.bin"
    model.write_bytes(b"model")
    commands: list[list[str]] = []

    class FakeStdin:
        @staticmethod
        def isatty() -> bool:
            return True

    class FakeRecorder:
        returncode: int | None = None

        def __init__(self, command: list[str], **_kwargs: object) -> None:
            commands.append(command)
            Path(command[-1]).write_bytes(b"RIFF" + b"\0" * 50)

        def send_signal(self, received_signal: int) -> None:
            assert received_signal == signal.SIGINT
            self.returncode = -signal.SIGINT

        def communicate(self, timeout: int) -> tuple[str, str]:
            return "", ""

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        commands.append(command)
        prefix = Path(command[command.index("-of") + 1])
        prefix.with_suffix(".txt").write_text("switch to gaming", encoding="utf-8")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr("ws_assistant.voice.whisper.shutil.which", lambda name: f"/bin/{name}")
    monkeypatch.setattr("ws_assistant.voice.whisper.sys.stdin", FakeStdin())
    monkeypatch.setattr("ws_assistant.voice.whisper.subprocess.Popen", FakeRecorder)
    monkeypatch.setattr("ws_assistant.voice.whisper.subprocess.run", fake_run)

    transcript = record_and_transcribe(
        recorder_command="pw-record",
        whisper_command="whisper-cli",
        model_path=str(model),
        input_fn=lambda: "",
    )

    assert transcript == "switch to gaming"
    assert commands[0][1:5] == ["--rate", "16000", "--channels", "1"]
    assert commands[1][1:3] == ["-m", str(model)]


def test_voice_settings_must_be_complete_when_enabled() -> None:
    config = load_config()
    config["voice"]["enabled"] = True
    assert "voice.model_path is required when voice.enabled is true." in validate_config(config)


def test_default_voice_is_disabled(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.yaml")
    assert config["voice"]["enabled"] is False
    assert validate_config(config) == []
