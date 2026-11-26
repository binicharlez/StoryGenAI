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
    cleaned_idea = re.sub(r"\s+", " ", idea).strip()
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
                    f"visualize: {direction.lower()} Topic: {cleaned_idea}"
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


def generate_short_story(idea: str, style: str = "Cinematic", language: str = "English") -> str:
    """Generate a complete short story locally from a simple story template."""
    cleaned_idea = re.sub(r"\s+", " ", idea).strip()
    if not cleaned_idea:
        raise ValueError("Please provide a story idea.")
    if style not in {"Educational", "Motivational", "Funny", "Cinematic"}:
        raise ValueError(f"Unsupported story style: {style}")
    if language not in {"English", "Malayalam"}:
        raise ValueError(f"Unsupported story language: {language}")

    if language == "Malayalam":
        return (
            f"{cleaned_idea} എന്ന ആശയത്തെ ചുറ്റിപ്പറ്റിയാണ് ഈ കഥ. "
            "ഒരു ദിവസം മീരയ്ക്ക് ഒരു അസാധാരണമായ കാര്യം കണ്ടെത്താനായി. "
            "ആദ്യം അവൾക്ക് എന്തുചെയ്യണമെന്ന് മനസ്സിലായില്ല, പക്ഷേ ധൈര്യത്തോടെ മുന്നോട്ട് പോയി. "
            "സുഹൃത്തുക്കളുടെ സഹായത്തോടെ അവൾ പ്രശ്നത്തിന് ഒരു നല്ല പരിഹാരം കണ്ടെത്തി. "
            "അന്ന് മീര പഠിച്ചത്, ചെറിയൊരു ആശയത്തിനുപോലും വലിയ മാറ്റം സൃഷ്ടിക്കാനാകുമെന്നാണ്."
        )

    openings = {
        "Educational": f"One bright morning, a curious child named Mira discovered something fascinating about {cleaned_idea}.",
        "Motivational": f"In a world shaped by {cleaned_idea}, Mira had one dream that everyone said was impossible.",
        "Funny": f"Mira's day started normally, until {cleaned_idea} turned everything upside down.",
        "Cinematic": f"The wind fell silent as Mira came face to face with {cleaned_idea}.",
    }
    middle = (
        "At first, the problem seemed too big to solve. Mira paused, looked carefully, "
        "and noticed a small clue that everyone else had missed. Instead of giving up, "
        "she asked for help and tried a new approach."
    )
    endings = {
        "Educational": "By sunset, Mira understood that curiosity and careful observation can turn a confusing problem into a valuable lesson.",
        "Motivational": "Step by step, Mira moved forward. The journey taught her that courage is not having no fear—it is taking the next step despite it.",
        "Funny": "Her plan worked perfectly—except for one tiny detail that made the whole village laugh. Mira laughed loudest of all.",
        "Cinematic": "As the final light crossed the horizon, Mira knew the moment had changed her forever. A new adventure was already waiting.",
    }
    return f"{openings[style]}\n\n{middle}\\n\\n{endings[style]}"
