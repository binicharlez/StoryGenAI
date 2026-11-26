import subprocess

import pytest

import imageio_ffmpeg

from storygenai.audio_mux import mux_audio
from storygenai.story_builder import build_story_plan
from storygenai.video_renderer import render_story_video


def test_mux_audio_adds_audio_stream_to_mp4(tmp_path):
    plan = build_story_plan("A short audio test", "Educational", 15)
    video = render_story_video(plan, tmp_path / "silent.mp4", fps=1, width=240, height=426)
    audio = tmp_path / "narration.wav"
    create_audio = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y", "-loglevel", "error",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
        "-t", "1", "-c:a", "pcm_s16le", str(audio),
    ]
    subprocess.run(create_audio, check=True, capture_output=True)
    output = mux_audio(video, audio, tmp_path / "with_audio.mp4", 15)

    assert output.exists()
    assert output.stat().st_size > video.stat().st_size
    verify_audio = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-v", "error", "-i", str(output),
        "-map", "0:a:0", "-f", "null", "-",
    ]
    subprocess.run(verify_audio, check=True, capture_output=True)


def test_mux_audio_rejects_unsupported_extension(tmp_path):
    video = tmp_path / "video.mp4"
    audio = tmp_path / "voice.xyz"
    video.write_bytes(b'video')
    audio.write_bytes(b'audio')
    with pytest.raises(ValueError, match='Unsupported audio format'):
        mux_audio(video, audio, tmp_path / "out.mp4", 10)


def test_mux_audio_requires_positive_duration(tmp_path):
    video = tmp_path / "video.mp4"
    audio = tmp_path / "voice.wav"
    video.write_bytes(b'video')
    audio.write_bytes(b'audio')
    with pytest.raises(ValueError, match='positive integer'):
        mux_audio(video, audio, tmp_path / "out.mp4", 0)
