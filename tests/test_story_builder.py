import pytest

from storygenai.story_builder import build_story_plan


def test_build_story_plan_returns_requested_style_and_duration():
    plan = build_story_plan("Learn about AI agents", "Educational", 30)
    assert plan["style"] == "Educational"
    assert plan["duration_seconds"] == 30
    assert plan["title"] == "Learn about AI agents"
    assert len(plan["scenes"]) == 3
    assert "AI agents" in plan["hook"]


def test_story_idea_whitespace_is_normalized():
    plan = build_story_plan("  A short  story\n about space  ", "Cinematic", 15)
    assert plan["title"] == "A short story about space"


@pytest.mark.parametrize("idea,style,duration", [
    ("   ", "Educational", 30),
    ("A valid idea", "Unknown", 30),
    ("A valid idea", "Educational", 10),
    ("A valid idea", "Educational", 100),
    ("A valid idea", "Educational", 30.5),
])
def test_invalid_story_inputs_raise_value_error(idea, style, duration):
    with pytest.raises(ValueError):
        build_story_plan(idea, style, duration)
