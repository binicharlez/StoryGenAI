"""Create a simple, deterministic story outline without external services."""

from __future__ import annotations

import re


_STYLE_HOOKS = {
    "English": {
        "Educational": "Here is one surprising thing to understand about",
        "Motivational": "If you have ever struggled with this, remember:",
        "Funny": "Imagine this happening to you:",
        "Cinematic": "Picture this moment:",
    },
    "Malayalam": {
        "Educational": "ഇതിനെക്കുറിച്ച് അറിയേണ്ട ഒരു കൗതുകകരമായ കാര്യം:",
        "Motivational": "ഇതിൽ നിങ്ങൾ ഒരിക്കലെങ്കിലും ബുദ്ധിമുട്ടിയിട്ടുണ്ടെങ്കിൽ ഓർക്കുക:",
        "Funny": "ഇങ്ങനെ സംഭവിക്കുന്നത് ഒന്ന് സങ്കൽപ്പിച്ചുനോക്കൂ:",
        "Cinematic": "ഈ നിമിഷം മനസ്സിൽ കാണൂ:",
    },
}

_BEATS = {
    "English": [
        ("Set the scene", "Introduce the idea and why it matters."),
        ("Show the challenge", "Describe a relatable problem or question."),
        ("Reveal the key point", "Share the central insight or turning point."),
        ("Make it practical", "Give one simple action the viewer can try."),
        ("Close with impact", "End with a memorable takeaway."),
    ],
    "Malayalam": [
        ("സാഹചര്യം പരിചയപ്പെടുത്തുക", "ഈ ആശയം പരിചയപ്പെടുത്തുകയും അതിന്റെ പ്രാധാന്യം വ്യക്തമാക്കുകയും ചെയ്യുക."),
        ("പ്രശ്നം അവതരിപ്പിക്കുക", "പ്രേക്ഷകർക്ക് ബന്ധിപ്പിക്കാനാകുന്ന ഒരു പ്രശ്നമോ ചോദ്യമോ അവതരിപ്പിക്കുക."),
        ("പ്രധാന ആശയം വെളിപ്പെടുത്തുക", "പ്രധാനപ്പെട്ട അറിവോ വഴിത്തിരിവോ പങ്കുവെക്കുക."),
        ("പ്രായോഗികമായി അവതരിപ്പിക്കുക", "പ്രേക്ഷകർക്ക് പരീക്ഷിക്കാവുന്ന ഒരു ലളിതമായ നടപടി നിർദേശിക്കുക."),
        ("പ്രഭാവത്തോടെ അവസാനിപ്പിക്കുക", "ഓർമ്മയിൽ നിൽക്കുന്ന ഒരു സന്ദേശത്തോടെ അവസാനിപ്പിക്കുക."),
    ],
}

_CTA = {
    "English": "Follow for more short stories and practical ideas.",
    "Malayalam": "കൂടുതൽ ചെറുകഥകൾക്കും പ്രായോഗിക ആശയങ്ങൾക്കുമായി ഫോളോ ചെയ്യൂ.",
}


def build_story_plan(idea: str, style: str, duration_seconds: int, language: str = "English") -> dict:
    """Build a local template-based narration and scene plan."""
    cleaned_idea = re.sub(r"\\s+", " ", idea).strip()
    if not cleaned_idea:
        raise ValueError("Please provide a story idea.")
    if language not in _STYLE_HOOKS:
        raise ValueError(f"Unsupported story language: {language}")
    if style not in _STYLE_HOOKS[language]:
        raise ValueError(f"Unsupported story style: {style}")
    if not isinstance(duration_seconds, int) or not 15 <= duration_seconds <= 90:
        raise ValueError("Duration must be an integer between 15 and 90 seconds.")

    hook = f"{_STYLE_HOOKS[language][style]} {cleaned_idea.rstrip('.!?')}."
    scene_count = max(3, min(5, round(duration_seconds / 15)))
    selected_beats = _BEATS[language][:scene_count]
    scene_duration = duration_seconds / scene_count

    scenes = []
    for index, (title, direction) in enumerate(selected_beats, start=1):
        scenes.append(
            {
                "scene": index,
                "title": title,
                "duration_seconds": round(scene_duration),
                "narration": f"{direction} വിഷയം: {cleaned_idea}" if language == "Malayalam" else f"{direction} Topic: {cleaned_idea}",
                "visual_prompt": (
                    f"Vertical 9:16 video, {style.lower()} style; "
                    f"visualize: {direction.lower()} Topic: {cleaned_idea"
                ),
            }
        )

    narration = " ".join([hook] + [scene["narration"] for scene in scenes])
    return {
        "title": cleaned_idea[:80],
        "style": style,
        "language": language,
        "duration_seconds": duration_seconds,
        "hook": hook,
        "narration": narration,
        "scenes": scenes,
        "call_to_action": _CTA[language],
    }
