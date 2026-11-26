from storygenai.captions import caption_segments, generate_srt
from storygenai.story_builder import build_story_plan


def test_caption_segments_include_hook_scenes_and_call_to_action():
    plan = build_story_plan("Learn a useful skill", "Educational", 30)
    segments = caption_segments(plan)

    assert segments[0]["title"] == "HOOK"
    assert segments[-1]["title"] == "CALL TO ACTION"
    assert len(segments) == len(plan["scenes"]) + 2
    assert sum(segment["duration"] for segment in segments) == 30


def test_srt_has_ordered_cues_and_valid_timestamp_format():
    plan = build_story_plan("Learn a useful skill", "Educational", 15)
    srt = generate_srt(plan)

    assert "00:00:00,000 --> " in srt
    assert "HOOK" not in srt  # Subtitle text is the spoken hook, not its card label.
    assert srt.startswith("1\n")
    assert f"{len(plan['scenes']) + 2}\n" in srt
