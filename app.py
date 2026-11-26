import json
import re
import tempfile
from pathlib import Path

import streamlit as st

from storygenai.config import get_settings
from storygenai.file_utils import ensure_project_dirs
from storygenai.story_builder import build_story_plan
from storygenai.captions import generate_srt
from storygenai.audio_mux import mux_audio
from storygenai.tts import generate_narration
from storygenai.video_renderer import render_story_video

settings = get_settings()
ensure_project_dirs(settings)

st.set_page_config(page_title="StoryGenAI", page_icon="🎬", layout="centered")
st.title("🎬 StoryGenAI")
st.subheader("Turn your ideas into short-form stories")
st.write(
    "Create a structured English or Malayalam story outline and export it as a vertical video. "
    "This prototype uses local templates and open-source rendering tools."
)

st.info(
    "The video uses text scene cards. You can upload your own narration recording "
    "to add voice audio. Offline text-to-speech is available with selectable voice and speed; Malayalam script templates are available; face animation is not connected yet."
)

with st.form("story_form"):
    prompt = st.text_area("Your story idea", placeholder="A short story about...")
    style = st.selectbox("Story style", ["Educational", "Motivational", "Funny", "Cinematic"])
    script_language = st.selectbox("Script language", ["English", "Malayalam"])
    duration = st.slider("Target duration (seconds)", min_value=15, max_value=90, value=30, step=5)
    submitted = st.form_submit_button("Prepare story")

if submitted:
    try:
        st.session_state["story_plan"] = build_story_plan(prompt, style, duration, language=script_language)
        st.session_state.pop("story_video_bytes", None)
        st.session_state.pop("generated_narration_bytes", None)
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
    st.download_button(
        "Download subtitles (SRT)",
        data=generate_srt(plan),
        file_name="story_captions.srt",
        mime="application/x-subrip",
    )

    narration_file = st.file_uploader("Optional recorded narration", type=["wav", "mp3", "m4a", "aac", "ogg", "flac"])
    voice_options = {
        "English — US": "en-us",
        "English — India (Indian English)": "en-in",
        "Malayalam (മലയാളം)": "ml",
        "English — UK": "en-gb",
        "English — Scottish": "en-sc",
        "English — UK (RP)": "en-gb-x-rp",
        "English — US (female variant)": "en-us+f3",
    }
    voice_labels = list(voice_options)
    default_voice_index = voice_labels.index("Malayalam (മലയാളം)") if plan.get("language") == "Malayalam" else 0
    selected_voice_label = st.selectbox("Generated voice", voice_labels, index=default_voice_index)
    selected_voice = voice_options[selected_voice_label]
    if selected_voice == "ml":
        st.info("Malayalam voice selected. The current story builder creates English scripts and this voice does not translate them. For Malayalam speech, use a Malayalam narration recording for now; editable Malayalam scripts/translation are a future feature.")
    speech_speed = st.slider("Speech speed (words per minute)", min_value=100, max_value=220, value=155, step=5)
    if st.button("Generate narration audio (offline)"):
        temporary_tts = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", dir=settings.outputs_dir, delete=False) as temp_tts:
                temporary_tts = Path(temp_tts.name)
            with st.spinner("Generating narration with the offline voice engine..."):
                generate_narration(plan, temporary_tts, voice=selected_voice, speed=speech_speed)
                st.session_state["generated_narration_bytes"] = temporary_tts.read_bytes()
            st.success("Narration WAV generated. It will be added to your MP4.")
        except Exception as error:
            st.error(f"Could not generate narration: {error}")
        finally:
            if temporary_tts is not None:
                temporary_tts.unlink(missing_ok=True)

    generated_audio = st.session_state.get("generated_narration_bytes")
    if generated_audio:
        st.audio(generated_audio, format="audio/wav")
        st.download_button("Download generated narration (WAV)", data=generated_audio, file_name="story_narration.wav", mime="audio/wav")
    if narration_file or generated_audio:
        st.caption("Recorded narration takes priority if both a recording and generated narration are available. Audio is padded or trimmed to the video duration.")

    if st.button("Render vertical MP4"):
        temporary_video = None
        temporary_audio = None
        temporary_final = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", dir=settings.outputs_dir, delete=False) as temp_video:
                temporary_video = Path(temp_video.name)
            with st.spinner("Rendering your vertical video..."):
                render_story_video(plan, temporary_video)
                final_path = temporary_video
                if narration_file is not None or generated_audio is not None:
                    if narration_file is not None:
                        audio_suffix = Path(narration_file.name).suffix.lower() or ".wav"
                        audio_bytes = narration_file.getbuffer()
                    else:
                        audio_suffix = ".wav"
                        audio_bytes = generated_audio
                    with tempfile.NamedTemporaryFile(suffix=audio_suffix, dir=settings.outputs_dir, delete=False) as temp_audio:
                        temporary_audio = Path(temp_audio.name)
                        temp_audio.write(audio_bytes)
                    with tempfile.NamedTemporaryFile(suffix=".mp4", dir=settings.outputs_dir, delete=False) as temp_output:
                        temporary_final = Path(temp_output.name)
                    mux_audio(temporary_video, temporary_audio, temporary_final, plan["duration_seconds"])
                    final_path = temporary_final
                st.session_state["story_video_bytes"] = final_path.read_bytes()
                safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", plan["title"]).strip("_")[:50] or "story"
                st.session_state["story_video_name"] = f"{safe_title}.mp4"
        except Exception as error:
            st.error(f"Could not render the video: {error}")
        finally:
            for temporary_path in (temporary_video, temporary_audio, temporary_final):
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
