import json
import re
import tempfile
from pathlib import Path

import streamlit as st

from storygenai.config import get_settings
from storygenai.file_utils import ensure_project_dirs
from storygenai.story_builder import build_story_plan, generate_short_story
from storygenai.captions import generate_srt
from storygenai.audio_mux import mux_audio
from storygenai.tts import generate_narration
from storygenai.video_renderer import render_story_video

settings = get_settings()
ensure_project_dirs(settings)

st.set_page_config(page_title="Story Generator", page_icon="📖", layout="centered")
st.title("📖 StoryGenAI: Bring Your Imagination to Life!")
st.subheader("Create captivating short stories in seconds! ✍️✨")
st.write(
    "Welcome to Story Generator, your storytelling assistant!\n\n"
    "Describe an idea, character, or setting and turn it into a short story. "
    "You can then edit the scenes, create narration, and export a vertical video."
)
st.caption("Stories are generated locally from your prompt—no paid API is required.")

with st.form("story_form"):
    prompt = st.text_area("Describe a character and a setting:", placeholder="e.g., a curious child in a big village")
    style = st.selectbox("Story style", ["Educational", "Motivational", "Funny", "Cinematic"])
    script_language = st.selectbox("Script language", ["English", "Malayalam"])
    duration = st.slider("Target duration (seconds)", min_value=15, max_value=90, value=30, step=5)
    submitted = st.form_submit_button("✨ Generate Story")

if submitted:
    try:
        for editor_key in list(st.session_state):
            if editor_key.startswith("editor_"):
                del st.session_state[editor_key]
        st.session_state["story_plan"] = build_story_plan(prompt, style, duration, language=script_language)
        st.session_state["generated_story_text"] = generate_short_story(prompt, style, language=script_language)
        st.session_state.pop("story_video_bytes", None)
        st.session_state.pop("generated_narration_bytes", None)
    except ValueError as error:
        st.warning(str(error))
        st.session_state.pop("story_plan", None)
        st.session_state.pop("generated_story_text", None)

plan = st.session_state.get("story_plan")
if plan:
    st.success("Your story is ready!")
    st.markdown("### 📚 Generated story")
    story_text = st.session_state.get("generated_story_text", plan["narration"])
    st.write(story_text)
    st.download_button(
        "Download story (TXT)",
        data=story_text,
        file_name="generated_story.txt",
        mime="text/plain",
    )
    st.markdown("### Scene editor")
    st.caption("Edit the story before rendering. Scene durations determine the video timeline.")
    with st.form("scene_editor_form"):
        edited_hook = st.text_area("Hook", value=plan.get("hook", ""), key="editor_hook")
        edited_scenes = []
        for scene in plan.get("scenes", []):
            st.markdown(f'**Scene {scene["scene"]}**')
            edited_title = st.text_input(
                "Scene title",
                value=scene.get("title", ""),
                key=f'editor_title_{scene["scene"]}',
            )
            edited_narration = st.text_area(
                "Scene narration",
                value=scene.get("narration", ""),
                key=f'editor_narration_{scene["scene"]}',
            )
            edited_duration = st.number_input(
                "Scene duration (seconds)",
                min_value=1,
                max_value=90,
                value=max(1, int(scene.get("duration_seconds", 1))),
                step=1,
                key=f'editor_duration_{scene["scene"]}',
            )
            edited_scenes.append(
                {
                    **scene,
                    "title": edited_title.strip() or f'Scene {scene["scene"]}',
                    "narration": edited_narration.strip(),
                    "duration_seconds": int(edited_duration),
                }
            )
        edited_cta = st.text_area(
            "Call to action",
            value=plan.get("call_to_action", ""),
            key="editor_cta",
        )
        save_edits = st.form_submit_button("Apply scene edits")
    if save_edits:
        plan["hook"] = edited_hook.strip()
        plan["scenes"] = edited_scenes
        plan["call_to_action"] = edited_cta.strip()
        plan["duration_seconds"] = sum(scene["duration_seconds"] for scene in edited_scenes)
        plan["narration"] = " ".join(
            [plan["hook"]]
            + [scene["narration"] for scene in edited_scenes]
            + [plan["call_to_action"]]
        ).strip()
        st.session_state["story_plan"] = plan
        st.session_state.pop("story_video_bytes", None)
        st.session_state.pop("generated_narration_bytes", None)
        st.success("Edits applied. Generate narration and render again to use the updated story.")
        st.rerun()
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
        st.info("Malayalam voice selected. This voice reads Malayalam text but does not translate English narration. Choose Malayalam script mode and enter your topic in Malayalam for a Malayalam narration draft.")
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
        st.caption("Recorded narration takes priority. If no audio is uploaded or generated, narration is created automatically when you render the MP4. Audio is padded or trimmed to the video duration.")

    if st.button("Render vertical MP4"):
        temporary_video = None
        temporary_audio = None
        temporary_final = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", dir=settings.outputs_dir, delete=False) as temp_video:
                temporary_video = Path(temp_video.name)
            with st.spinner("Rendering video and adding narration..."):
                render_story_video(plan, temporary_video)
                if narration_file is not None:
                    audio_suffix = Path(narration_file.name).suffix.lower() or ".wav"
                    audio_bytes = narration_file.getbuffer()
                else:
                    audio_suffix = ".wav"
                    audio_bytes = generated_audio
                    if audio_bytes is None:
                        # Automatically create narration when the user has not generated or uploaded audio.
                        with tempfile.NamedTemporaryFile(suffix=".wav", dir=settings.outputs_dir, delete=False) as auto_tts:
                            temporary_audio = Path(auto_tts.name)
                        generate_narration(plan, temporary_audio, voice=selected_voice, speed=speech_speed)
                        audio_bytes = temporary_audio.read_bytes()
                        st.session_state["generated_narration_bytes"] = audio_bytes
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

st.markdown("---")
st.markdown("<div style=\"text-align:center; color:gray; font-weight:600;\">⭐ Made by Bini Mol N. C. ⭐</div>", unsafe_allow_html=True)
