from pathlib import Path

import pytest

from storygenai.story_builder import build_story_plan
from storygenai.tts import generate_narration


def test_generate_narration_creates_wav(tmp_path):
    plan = build_story_plan("A short explanation about learning", "Educational", 15)
    output = generate_narration(plan, tmp_path / "narration.wav")

    assert output.exists()
    assert output.read_bytes()[:4] == b"RIFF"
    assert output.read_bytes()[8:12] == b"WAVE"
    assert output.stat().st_size > 1000


def test_generate_narration_validates_speed(tmp_path):
    plan = build_story_plan("Test narration", "Educational", 15)
    with pytest.raises(ValueError, match="speed"):
        generate_narration(plan, tmp_path / "bad.wav", speed=500)
