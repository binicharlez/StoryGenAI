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



def test_malayalam_story_plan_uses_malayalam_template_and_voice_language():
    plan = build_story_plan("എഐ പഠിക്കാം", "Educational", 15, language="Malayalam")

    assert plan["language"] == "Malayalam"
    assert "ഇതിനെക്കുറിച്ച്" in plan["hook"]
    assert "എഐ പഠിക്കാം" in plan["narration"]
    assert plan["scenes"][0]["title"] == "സാഹചര്യം പരിചയപ്പെടുത്തുക"
    assert "ഫോളോ ചെയ്യൂ" in plan["call_to_action"]


def test_unsupported_story_language_is_rejected():
    with pytest.raises(ValueError, match="language"):
        build_story_plan("A topic", "Educational", 15, language="Tamil")
