from pathlib import Path

import pytest
from PIL import Image

from storygenai.story_builder import build_story_plan
from storygenai.video_renderer import render_story_video


def test_render_story_video_creates_mp4(tmp_path):
    plan = build_story_plan("A tiny idea about learning", "Educational", 15)
    output = render_story_video(plan, tmp_path / "story.mp4", fps=1, width=240, height=426)

    assert output.exists()
    assert output.stat().st_size > 1000
    assert output.read_bytes()[4:8] == b"ftyp"


@pytest.mark.parametrize(
    "plan",
    [
        {"duration_seconds": 15, "scenes": []},
        {"duration_seconds": 0, "scenes": [{"title": "Scene"}]},
    ],
)
def test_render_story_video_rejects_invalid_plan(tmp_path, plan):
    with pytest.raises(ValueError):
        render_story_video(plan, tmp_path / "invalid.mp4", fps=1, width=240, height=426)



def test_render_malayalam_story_video(tmp_path):
    plan = build_story_plan("എഐ പഠിക്കാം", "Educational", 15, language="Malayalam")
    output = render_story_video(plan, tmp_path / "malayalam-story.mp4", fps=1, width=240, height=426)

    assert output.exists()
    assert output.stat().st_size > 1000
    assert output.read_bytes()[4:8] == b"ftyp"


def test_render_story_video_with_avatar_photo_creates_mp4(tmp_path):
    plan = build_story_plan("A short story about a teacher", "Motivational", 15)
    avatar = Image.new("RGB", (320, 640), (210, 180, 160))
    output = render_story_video(
        plan,
        tmp_path / "avatar-story.mp4",
        fps=1,
        width=240,
        height=426,
        avatar_image=avatar,
    )

    assert output.exists()
    assert output.stat().st_size > 1000
    assert output.read_bytes()[4:8] == b"ftyp"

