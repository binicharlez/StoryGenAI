"""Generate offline narration audio using the espeak-ng system voice engine."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from storygenai.captions import caption_segments


def generate_narration(plan: dict, output_path: str | Path, voice: str = "en-us", speed: int = 155) -> Path:
    """Synthesize the story hook, scenes, and CTA into a WAV file offline."""
    executable = shutil.which("espeak-ng")
    if executable is None:
        raise RuntimeError("Offline TTS engine espeak-ng is not installed. Install it in your environment first.")
    if not isinstance(speed, int) or not 80 <= speed <= 300:
        raise ValueError("Speech speed must be an integer between 80 and 300 words per minute.")
    if not isinstance(voice, str) or not voice.strip() or any(char.isspace() for char in voice):
        raise ValueError("Voice must be a non-empty espeak-ng voice identifier.")
    segments = caption_segments(plan)
    narration = " ".join(segment["text"] for segment in segments).strip()
    if not narration:
        raise ValueError("Story plan has no narration text.")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "-v", voice, "-s", str(speed), "-w", str(destination), narration]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"Offline TTS failed: {result.stderr[-1000:]}")
    if not destination.is_file() or destination.stat().st_size < 44:
        raise RuntimeError("Offline TTS did not create a valid WAV file.")
    return destination
