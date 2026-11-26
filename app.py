from pathlib import Path

import streamlit as st

from storygenai.config import get_settings
from storygenai.file_utils import ensure_project_dirs

settings = get_settings()
ensure_project_dirs(settings)

st.set_page_config(page_title="StoryGenAI", page_icon="🎬", layout="centered")
st.title("🎬 StoryGenAI")
st.subheader("Turn your ideas into short-form stories")
st.write(
    "StoryGenAI is an early-stage project for creating engaging vertical video "
    "stories. This Phase 1 build provides the project foundation and interface."
)

st.info("Video generation is not connected yet. No external API or model is called in this phase.")

with st.form("story_form"):
    prompt = st.text_area("Your story idea", placeholder="A short story about...")
    style = st.selectbox("Story style", ["Educational", "Motivational", "Funny", "Cinematic"])
    duration = st.slider("Target duration (seconds)", min_value=15, max_value=90, value=30, step=5)
    submitted = st.form_submit_button("Prepare story")

if submitted:
    if not prompt.strip():
        st.warning("Please enter a story idea first.")
    else:
        st.success("Your idea is ready for the next development phase.")
        st.write({"idea": prompt.strip(), "style": style, "duration_seconds": duration})
