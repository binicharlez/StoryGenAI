"""Create a simple, deterministic story outline without external services."""

from __future__ import annotations

import re


_STYLE_HOOKS = {
    "Educational": "Here is one surprising thing to understand about",
    "Motivational": "If you have ever struggled with this, remember:",
    "Funny": "Imagine this happening to you:",
    "Cinematic": "Picture this moment:",
}


def build_story_plan(idea: str, style: str, duration_seconds: int) -> dict:
    """Build a short narration and scene plan from a user idea.

    This is a local template-based prototype, not an AI model or video generator.
    """
    cleaned_idea = re.sub(r"\s+", " ", idea).strip()
    if not cleaned_idea:
        raise ValueError("Please provide a story idea.")
    if style not in _STYLE_HOOKS:
        raise ValueError(f"Unsupported story style: {style}")
    if not isinstance(duration_seconds, int) or not 15 <= duration_seconds <= 90:
        raise ValueError("Duration must be an integer between 15 and 90 seconds.")

    hook = f"{_STYLE_HOOKS[style]} {cleaned_idea.rstrip('.!?')}."
    scene_count = max(3, min(5, round(duration_seconds / 15)))
    beat_templates = [
        ("Set the scene", "Introduce the idea and why it matters."),
        ("Show the challenge", "Describe a relatable problem or question."),
        ("Reveal the key point", "Share the central insight or turning point."),
        ("Make it practical", "Give one simple action the viewer can try."),
        ("Close with impact", "End with a memorable takeaway."),
    ]
    selected_beats = beat_templates[:scene_count]
    scene_duration = duration_seconds / scene_count

    scenes = []
    for index, (title, direction) in enumerate(selected_beats, start=1):
        scenes.append(
            {
                "scene": index,
                "title": title,
                "duration_seconds": round(scene_duration),
                "narration": f"{direction} Topic: {cleaned_idea}",
                "visual_prompt": (
                    f"Vertical 9:16 video, {style.lower()} style; "
                    f"visualize: {direction.lower()} Topic: {cleaned_idea}"
                ),
            }
        )

    narration = " ".join([hook] + [scene["narration"] for scene in scenes])
    return {
        "title": cleaned_idea[:80],
        "style": style,
        "duration_seconds": duration_seconds,
        "hook": hook,
        "narration": narration,
        "scenes": scenes,
        "call_to_action": "Follow for more short stories and practical ideas.",
    }
