import json
import re
import tempfile
from pathlib import Path

import streamlit as st

from storygenai.config import get_settings
from storygenai.file_utils import ensure_project_dirs
from storygenai.story_builder import build_story_plan
from storygenai.video_renderer import render_story_video

settings = get_settings()
ensure_project_dirs(settings)

st.set_page_config(page_title="StoryGenAI", page_icon="🎬", layout="centered")
st.title("🎬 StoryGenAI")
st.subheader("Turn your ideas into short-form stories")
st.write(
    "Create a structured story outline and export it as a vertical video. "
    "This prototype uses local templates and open-source rendering tools."
)

st.info(
    "The MP4 is a silent scene-card video with text. Voice generation, face animation, "
    "and AI-generated footage are not connected yet."
)

with st.form("story_form"):
    prompt = st.text_area("Your story idea", placeholder="A short story about...")
    style = st.selectbox("Story style", ["Educational", "Motivational", "Funny", "Cinematic"])
    duration = st.slider("Target duration (seconds)", min_value=15, max_value=90, value=30, step=5)
    submitted = st.form_submit_button("Prepare story")

if submitted:
    try:
        st.session_state["story_plan"] = build_story_plan(prompt, style, duration)
        st.session_state.pop("story_video_bytes", None)
    except ValueError as error:
        st.warning(str(error))
        st.session_state.pop("story_plan", None)

plan = st.session_state.get("story_plan")
if plan:
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

    if st.button("Render vertical MP4"):
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".mp4", dir=settings.outputs_dir, delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
            with st.spinner("Rendering your silent vertical video..."):
                render_story_video(plan, temporary_path)
                st.session_state["story_video_bytes"] = temporary_path.read_bytes()
                safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", plan["title"]).strip("_")[:50] or "story"
                st.session_state["story_video_name"] = f"{safe_title}.mp4"
        except Exception as error:
            st.error(f"Could not render the video: {error}")
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    video_bytes = st.session_state.get("story_video_bytes")
    if video_bytes:
        st.success("Your MP4 is ready.")
        st.download_button(
            "Download vertical video (MP4)",
            data=video_bytes,
            file_name=st.session_state.get("story_video_name", "storygenai.mp4"),
            mime="video/mp4",
        )
