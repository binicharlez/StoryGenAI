"""Attach a user-provided narration track to a rendered MP4."""

from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg

SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac"}


def mux_audio(video_path: str | Path, audio_path: str | Path, output_path: str | Path, duration_seconds: int) -> Path:
    """Mux narration into the video, padding short audio and trimming long audio."""
    video = Path(video_path)
    audio = Path(audio_path)
    output = Path(output_path)

    if not video.is_file():
        raise FileNotFoundError(f"Video file not found: {video}")
    if not audio.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio}")
    if audio.suffix.lower() not in SUPPORTED_AUDIO_SUFFIXES:
        raise ValueError("Unsupported audio format. Use WAV, MP3, M4A, AAC, OGG, or FLAC.")
    if not isinstance(duration_seconds, int) or duration_seconds <= 0:
        raise ValueError("Duration must be a positive integer.")

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y", "-loglevel", "error",
        "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", "apad", "-t", str(duration_seconds),
        "-movflags", "+faststart", str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        output.unlink(missing_ok=True)
        raise RuntimeError(f"Could not attach narration audio: {result.stderr[-1200:]}")
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Audio muxing did not produce an MP4 file.")
    return output
