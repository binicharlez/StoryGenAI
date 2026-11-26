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


def test_generate_short_story_returns_complete_story_for_idea():
    from storygenai.story_builder import generate_short_story

    story = generate_short_story("a big village", "Cinematic")
    assert "a big village" in story
    assert len(story.split()) > 40
    assert "\n\n" in story


def test_generate_short_story_rejects_empty_idea():
    from storygenai.story_builder import generate_short_story

    with pytest.raises(ValueError, match="story idea"):
        generate_short_story("   ")

def test_generated_story_uses_prompt_character_discovery_and_setting():
    from storygenai.story_builder import generate_short_story

    story = generate_short_story(
        "A little girl named Anu discovers a magical garden in Kerala.",
        "Cinematic",
    )

    assert "Anu" in story
    assert "magical garden" in story
    assert "Kerala" in story
    assert "Buddhist temple" not in story
    assert "KGF Vissers" not in story
