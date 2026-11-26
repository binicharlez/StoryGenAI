# StoryGenAI

StoryGenAI is an early-stage Streamlit project for turning text ideas into creative vertical-video stories.

## Current prototype

- Story idea input with Educational, Motivational, Funny, and Cinematic styles
- English or Malayalam script templates (Malayalam input topic is retained as entered)
- Offline template-based narration draft and scene outline
- Visual prompts for each scene
- In-app scene editor for the hook, scene titles, narration, durations, and call-to-action before export
- JSON export of the story plan
- Vertical MP4 export (9:16, H.264) with narration and captions; still-photo mode or optional audio-driven SadTalker face animation
- SRT subtitle export aligned to the story timeline
- Optional user-recorded narration upload (WAV, MP3, M4A, AAC, OGG, FLAC) muxed into the MP4
- Offline text-to-speech narration using the free espeak-ng engine, with selectable English voice variants including Indian English and Malayalam, and speech speed
- Configuration and safe file-management utilities
- Automated tests through GitHub Actions

The story builder is deterministic and template-based. MP4 rendering uses Pillow and the bundled FFmpeg binary from imageio-ffmpeg. No paid API or AI model is required. The default video uses story cards or a selected presenter photo. You can upload your own narration recording and the app will pad or trim it to the planned video duration. When SadTalker is installed locally, the talking-avatar mode animates the face and lip-syncs to the audio. The app can generate basic offline narration using espeak-ng, select from several English voice variants including Indian English and Malayalam, adjust speech speed, or accept a recorded voice track. English is the default script language. Malayalam mode provides Malayalam hooks, scene titles, scene narration guidance, and a Malayalam call-to-action; enter your topic in Malayalam for Malayalam narration text. The Malayalam voice does not translate English input. Voice cloning is not connected. An optional SadTalker adapter is included for audio-driven facial animation and lip-sync, but the SadTalker code and model checkpoints must be installed separately on a local/GPU machine. It is not bundled into the Streamlit Community Cloud deployment.


## Talking-avatar mode (SadTalker)

StoryGenAI includes an optional adapter for [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker). Given a presenter photo and narration WAV, it runs SadTalker to animate facial movement and lip-sync, then adds the narration track to the MP4. It supports full-image preprocessing and a pose-style setting. The adapter does not pass SadTalker's `--still` flag, allowing audio-driven head motion. An optional short MP4 pose-reference video of you sitting upright and gesturing can guide the generated pose through SadTalker’s reference-pose option. This is a pose-transfer aid, not a guarantee of perfectly natural hand gestures.

### Install for local/GPU use

1. Clone and install SadTalker following its official installation instructions, and download its required checkpoints into that checkout's checkpoints folder.
2. Install StoryGenAI requirements in your Python environment and install system packages espeak-ng and fonts-noto-core.
3. Set the path to the SadTalker checkout before starting Streamlit:

   export SADTALKER_DIR="/path/to/SadTalker"
   streamlit run app.py

   Optionally set SADTALKER_CHECKPOINT_DIR if your checkpoints are stored elsewhere. Set SADTALKER_FORCE_CPU=1 to force CPU inference.

4. In StoryGenAI, select **Talking avatar (SadTalker)**, upload a presenter photo, optionally upload a short MP4 of yourself sitting upright and gesturing as a pose reference, generate or upload narration, and render.

SadTalker is a large model and is not downloaded automatically. The app checks whether its inference script and checkpoints are present and reports a setup message if they are missing. Streamlit Community Cloud's standard resource limits are generally unsuitable for large CPU-based avatar inference; use a local runtime or a GPU environment. Test a short clip first.

Official references:
- [SadTalker repository and CLI](https://github.com/OpenTalker/SadTalker)
- [Streamlit Community Cloud resource limits](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)

### Presenter photo privacy

Upload photos through the app's file uploader for session processing. Do not commit personal reference photos to a public repository. The app does not need a photo archive committed to GitHub.

## Deploy as a live website (Streamlit Community Cloud)\n\n1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.\n2. Choose **Create app** and select `binicharlez/StoryGenAI`.\n3. Select branch `main` and main file path `app.py`.\n4. Click **Deploy**. The `requirements.txt` and `packages.txt` files install the app dependencies.\n5. Streamlit will provide the live website URL after deployment completes.\n\nThe repository is prepared for deployment, but pushing code to GitHub does not automatically create a Streamlit-hosted URL unless the app is connected and deployed there.\n\n## Run in GitHub Codespaces

1. Open this repository on GitHub.
2. Select **Code → Codespaces → Create codespace on main**.
3. Wait for the environment to finish setting up.
4. In the Codespaces terminal, run:

   ```bash
   streamlit run app.py
   ```

5. Open the forwarded port **8501** when prompted.
6. Enter a story idea, prepare the outline, select **Generate narration audio (offline)** or optionally upload your own recording, edit the hook/scenes/CTA in the Scene editor and apply changes, then select **Render vertical MP4** and download the result.

The Codespaces configuration installs Python dependencies, espeak-ng, and Noto fonts for Malayalam text automatically.

## Run locally (optional)

Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
sudo apt-get update && sudo apt-get install -y espeak-ng fonts-noto-core
python -m pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
pytest -q
```

GitHub Actions runs tests on pushes to `main` and pull requests targeting `main`.

## Configuration

Optional environment variables:
- `STORYGENAI_APP_NAME`
- `STORYGENAI_DATA_DIR`

Keep real credentials in GitHub Actions secrets or a trusted secrets manager. Never commit credentials or private user media to the repository.
