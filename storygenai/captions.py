"""Create subtitle segments and SRT captions from a StoryGenAI plan."""

from __future__ import annotations

from typing import Any


def caption_segments(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Return hook, scene, and call-to-action segments spanning the plan duration."""
    scenes = plan.get("scenes")
    duration = plan.get("duration_seconds")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("The story plan must contain at least one scene.")
    if not isinstance(duration, int) or duration < 5:
        raise ValueError("The story plan must contain a duration of at least 5 seconds.")

    hook = str(plan.get("hook", "")).strip()
    cta = str(plan.get("call_to_action", "")).strip()
    fixed_intro = min(2.0, duration * 0.1) if hook else 0.0
    fixed_outro = min(2.0, duration * 0.1) if cta else 0.0
    scene_budget = duration - fixed_intro - fixed_outro
    scene_weights = [max(1.0, float(scene.get("duration_seconds", 1))) for scene in scenes]
    weight_total = sum(scene_weights)

    segments: list[dict[str, Any]] = []
    if hook:
        segments.append({"title": "HOOK", "text": hook, "duration": fixed_intro})
    for scene, weight in zip(scenes, scene_weights):
        text = str(scene.get("narration", "")).strip()
        if not text:
            text = str(scene.get("title", ""))
        segments.append(
            {
                "title": str(scene.get("title", "Scene")),
                "text": text,
                "duration": scene_budget * weight / weight_total,
            }
        )
    if cta:
        segments.append({"title": "CALL TO ACTION", "text": cta, "duration": fixed_outro})

    # Correct floating-point rounding on the final segment so the timeline ends exactly.
    total = sum(segment["duration"] for segment in segments)
    if segments:
        segments[-1]["duration"] += duration - total
    return segments


def _timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds_part, millis_part = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds_part:02},{millis_part:03}"


def generate_srt(plan: dict[str, Any]) -> str:
    """Generate a UTF-8 SRT caption track aligned to the planned video duration."""
    lines: list[str] = []
    start = 0.0
    for index, segment in enumerate(caption_segments(plan), start=1):
        end = start + segment["duration"]
        lines.extend(
            [
                str(index),
                f"{_timestamp(start)} --> {_timestamp(end)}",
                segment["text"],
                "",
            ]
        )
        start = end
    return "\n".join(lines).rstrip() + "\n"
