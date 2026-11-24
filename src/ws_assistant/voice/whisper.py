from __future__ import annotations

import shutil
import signal
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path


class VoiceError(RuntimeError):
    """Raised when audio capture or local transcription fails."""


def record_and_transcribe(
    *,
    recorder_command: str,
    whisper_command: str,
    model_path: str,
    input_fn: Callable[[], str] | None = None,
) -> str:
    """Record from the default PipeWire source until Enter, then transcribe locally."""
    recorder = shutil.which(recorder_command)
    if recorder is None:
        raise VoiceError(f"Recorder '{recorder_command}' was not found on PATH.")
    whisper = shutil.which(whisper_command)
    if whisper is None:
        raise VoiceError(f"Whisper executable '{whisper_command}' was not found on PATH.")
    model = Path(model_path).expanduser()
    if not model.is_file():
        raise VoiceError(f"Whisper model file does not exist: {model}")
    if not sys.stdin.isatty():
        raise VoiceError("Voice recording requires an interactive terminal.")

    with tempfile.TemporaryDirectory(prefix="ws-assistant-voice-") as directory:
        recording = Path(directory) / "recording.wav"
        transcript_prefix = Path(directory) / "transcript"
        try:
            process = subprocess.Popen(
                [recorder, "--rate", "16000", "--channels", "1", str(recording)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError as exc:
            raise VoiceError(f"Could not start PipeWire recorder: {exc}") from exc

        print("Recording from the default microphone. Press Enter to stop.")
        try:
            (input_fn or input)()
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            try:
                process.send_signal(signal.SIGINT)
            except ProcessLookupError:
                pass
            try:
                _, recorder_error = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                _, recorder_error = process.communicate()

        if process.returncode not in (0, -signal.SIGINT, 128 + signal.SIGINT):
            detail = (recorder_error or "").strip()
            message = f"PipeWire recording failed with exit code {process.returncode}."
            if detail:
                message = f"{message} {detail}"
            raise VoiceError(message)
        if not recording.is_file() or recording.stat().st_size <= 44:
            raise VoiceError("No audio was recorded. Check your default microphone in PipeWire.")

        try:
            result = subprocess.run(
                [
                    whisper,
                    "-m",
                    str(model),
                    "-f",
                    str(recording),
                    "-nt",
                    "-np",
                    "-otxt",
                    "-of",
                    str(transcript_prefix),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired as exc:
            raise VoiceError("Whisper transcription timed out after 300 seconds.") from exc
        except OSError as exc:
            raise VoiceError(f"Could not start Whisper: {exc}") from exc
        if result.returncode != 0:
            detail = result.stderr.strip()
            message = f"Whisper failed with exit code {result.returncode}."
            if detail:
                message = f"{message} {detail}"
            raise VoiceError(message)

        transcript_file = transcript_prefix.with_suffix(".txt")
        try:
            transcript = transcript_file.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise VoiceError("Whisper completed without producing a transcript.") from exc
        if not transcript:
            raise VoiceError("No speech was recognized.")
        return transcript
