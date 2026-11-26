import json

import streamlit as st

from storygenai.config import get_settings
from storygenai.file_utils import ensure_project_dirs
from storygenai.story_builder import build_story_plan

settings = get_settings()
ensure_project_dirs(settings)

st.set_page_config(page_title="StoryGenAI", page_icon="🎬", layout="centered")
st.title("🎬 StoryGenAI")
st.subheader("Turn your ideas into short-form stories")
st.write(
    "Create a structured story outline for a vertical video. "
    "This prototype works locally with templates and does not call a paid API."
)

st.info(
    "This version creates a narration draft and scene plan. "
    "Video rendering, voice generation, and AI model integration are not connected yet."
)

with st.form("story_form"):
    prompt = st.text_area("Your story idea", placeholder="A short story about...")
    style = st.selectbox("Story style", ["Educational", "Motivational", "Funny", "Cinematic"])
    duration = st.slider("Target duration (seconds)", min_value=15, max_value=90, value=30, step=5)
    submitted = st.form_submit_button("Prepare story")

if submitted:
    try:
        plan = build_story_plan(prompt, style, duration)
    except ValueError as error:
        st.warning(str(error))
    else:
        st.success("Your story outline is ready!")
        st.subheader(plan["title"])
        st.caption(f'{plan["style"]} · {plan["duration_seconds"]} seconds')
        st.markdown("### Hook")
        st.write(plan["hook"])
        st.markdown("### Narration draft")
        st.write(plan["narration"])
        st.markdown("### Scene plan")
        for scene in plan["scenes"]:
            with st.expander(f'Scene {scene["scene"]}: {scene["title"]}'):
                st.write(f'Duration: {scene["duration_seconds"]} seconds')
                st.write("**Narration direction**")
                st.write(scene["narration"])
                st.write("**Visual prompt**")
                st.write(scene["visual_prompt"])
        st.markdown("### Call to action")
        st.write(plan["call_to_action"])
        st.download_button(
            "Download story plan (JSON)",
            data=json.dumps(plan, indent=2, ensure_ascii=False),
            file_name="story_plan.json",
            mime="application/json",
        )
