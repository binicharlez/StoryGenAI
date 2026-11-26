"""Generate prompt-grounded short stories locally without paid APIs."""

from __future__ import annotations

import re


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
    location = location_match.group(1).strip() if location_match else "a quiet village"
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
            "അന്ന് {character} മനസ്സിലാക്കി: കൗതുകവും ധൈര്യവും ചേർന്നാൽ ചെറിയൊരു കണ്ടെത്തലും വലിയൊരു സാഹസമായി മാറും."
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
