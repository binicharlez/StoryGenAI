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

def _extract_prompt_details(idea: str) -> tuple[str, str, str]:
    """Extract a named character, discovery, and location from common prompt phrasing."""
    cleaned = re.sub(r"\s+", " ", idea).strip().rstrip(".!?")
    name_match = re.search(r"\b(?:named|called)\s+([A-Z][a-zA-Z'-]*)", cleaned)
    character = name_match.group(1) if name_match else "Mira"

    discover_match = re.search(
        r"\b(?:discover|discovers|discovered|find|finds|found|uncover|uncovers|uncovered)\s+(?:a|an|the)?\s*(.+?)(?=\s+\b(?:in|at|near|inside|within|during|while)\b|$)",
        cleaned,
        flags=re.IGNORECASE,
    )
    discovery = discover_match.group(1).strip(" ,") if discover_match else "a surprising secret"

    location_match = re.search(
        r"\b(?:in|at|near|inside|within)\s+([A-Z][A-Za-z' -]*?)(?=[,.!?]|$)",
        cleaned,
    )
    # If the prompt is a short place/idea phrase (e.g. "a big village"), preserve it verbatim.
    location = location_match.group(1).strip() if location_match else cleaned
    if location.lower().startswith(("a ", "an ", "the ")):
        location = location[2:] if location.lower().startswith("a ") else location[3:]
    return character, discovery, location


def generate_short_story(idea: str, style: str = "Cinematic", language: str = "English") -> str:
    """Create a short, locally generated story that reuses details from the user's prompt."""
    cleaned_idea = re.sub(r"\s+", " ", idea).strip()
    if not cleaned_idea:
        raise ValueError("Please provide a story idea.")
    if style not in {"Educational", "Motivational", "Funny", "Cinematic"}:
        raise ValueError("Please choose a supported story style.")
    if language not in {"English", "Malayalam"}:
        raise ValueError("Please choose English or Malayalam.")

    character, discovery, location = _extract_prompt_details(cleaned_idea)

    if language == "Malayalam":
        return (
            f"{location}യിലെ ഒരു മനോഹരമായ പ്രഭാതത്തിൽ {character} എന്ന കുട്ടി {discovery} കണ്ടെത്തി. "
            "ആദ്യമത് ഒരു സാധാരണ സ്ഥലമാണെന്ന് തോന്നിയെങ്കിലും, അകത്തേക്ക് കടന്നപ്പോൾ അത്ഭുതകരമായ കാഴ്ചകൾ അവളെ കാത്തിരുന്നു. "
            "അവിടെ ഒരു ചെറിയ പ്രശ്നം ഉണ്ടെന്ന് അവൾ ശ്രദ്ധിച്ചു. ധൈര്യത്തോടെയും സുഹൃത്തുക്കളുടെ സഹായത്തോടെയും "
            "അവൾ അതിന് പരിഹാരം കണ്ടെത്തി. "
            f"അന്ന് {character} മനസ്സിലാക്കി: കൗതുകവും ധൈര്യവും ചേർന്നാൽ ചെറിയൊരു കണ്ടെത്തലും വലിയൊരു സാഹസമായി മാറും."
        )

    opening_by_style = {
        "Educational": f"One bright morning in {location}, {character} made a fascinating discovery: {discovery}.",
        "Motivational": f"In {location}, {character} had always believed that extraordinary things could happen. Then one day, {character} discovered {discovery}.",
        "Funny": f"It was an ordinary day in {location}—until {character} discovered {discovery} and accidentally became the village's most talked-about adventurer.",
        "Cinematic": f"The morning mist drifted over {location}. Then {character} discovered {discovery}, and the quiet world changed in an instant.",
    }
    middle_by_style = {
        "Educational": f"At first, {character} did not understand what made the discovery special. By looking closely and asking thoughtful questions, {character} noticed a hidden clue. Each small observation revealed something new.",
        "Motivational": f"The path was not easy. A sudden obstacle made {character} wonder whether to turn back. But {character} took one brave step, asked a trusted friend for help, and kept going.",
        "Funny": f"Unfortunately, the discovery came with a very unexpected problem. {character} tried three clever solutions, each more ridiculous than the last, until a tiny overlooked detail finally solved everything.",
        "Cinematic": f"A strange sound echoed nearby. {character} followed a trail of tiny clues, facing uncertainty at every turn. Just when hope seemed to fade, a hidden passage revealed the answer.",
    }
    ending_by_style = {
        "Educational": f"By evening, {character} had learned that curiosity, patience, and careful observation can turn a mystery into understanding.",
        "Motivational": f"When the adventure ended, {character} was no longer afraid to try. The discovery had proved that courage grows whenever we take the next step.",
        "Funny": f"The whole village celebrated. {character} accepted the applause proudly—until the discovery made one last funny surprise and everyone burst into laughter.",
        "Cinematic": f"As the sun set over {location}, {character} looked back at the discovery. It had opened the door to a world of possibilities—and the next adventure was already calling.",
    }
    return "\n\n".join(
        [opening_by_style[style], middle_by_style[style], ending_by_style[style]]
    )
