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

The story builder is deterministic and template-based. Story text and captions do not require a paid API. Animated MP4 export requires SadTalker and its checkpoints, either locally or through the authenticated remote GPU service described below. The app does not silently substitute a still-photo video for the requested talking avatar. You can upload your own narration recording and the app will pad or trim it to the planned video duration. When SadTalker is installed locally, the talking-avatar mode animates the face and lip-syncs to the audio. The app can generate basic offline narration using espeak-ng, select from several English voice variants including Indian English and Malayalam, adjust speech speed, or accept a recorded voice track. English is the default script language. Malayalam mode provides Malayalam hooks, scene titles, scene narration guidance, and a Malayalam call-to-action; enter your topic in Malayalam for Malayalam narration text. The Malayalam voice does not translate English input. Voice cloning is not connected. An optional SadTalker adapter is included for audio-driven facial animation and lip-sync, but the SadTalker code and model checkpoints must be installed separately on a local/GPU machine. It is not bundled into the Streamlit Community Cloud deployment.


## Talking-avatar mode (SadTalker)

StoryGenAI includes an optional adapter for [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker). Given a presenter photo and narration WAV, it runs SadTalker to animate facial movement and lip-sync, then adds the narration track to the MP4. It supports full-image preprocessing and a pose-style setting. The adapter does not pass SadTalker's `--still` flag, allowing audio-driven head motion. An optional short MP4 pose-reference video of you sitting upright and gesturing can guide the generated pose through SadTalker’s reference-pose option. This is a pose-transfer aid, not a guarantee of perfectly natural hand gestures.

### Important: Streamlit Community Cloud

The default Community Cloud runtime does not include SadTalker or its checkpoints. The app cannot create a talking-avatar video there until the model is installed in a suitable runtime. Installing the adapter package alone is not enough. For local use, install SadTalker and its checkpoints separately, then set `SADTALKER_DIR` and, if using a separate environment, `SADTALKER_PYTHON`. SadTalker's official macOS instructions were tested on Apple Silicon; Intel macOS may require dependency adjustments.

### Install for local/GPU use

1. Clone and install SadTalker following its official installation instructions, and download its required checkpoints into that checkout's checkpoints folder.
2. Install StoryGenAI requirements in your Python environment and install system packages espeak-ng and fonts-noto-core.
3. Set the path to the SadTalker checkout before starting Streamlit:

   export SADTALKER_DIR="/path/to/SadTalker"
   # Optional: use the Python executable from SadTalker's dedicated environment
   export SADTALKER_PYTHON="/path/to/sadtalker-env/bin/python"
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


## Hosted talking-avatar inference (GPU service)

The Streamlit website is the **front end**. SadTalker must run on a separate machine with a supported GPU and its model checkpoints. This repository now includes an authenticated FastAPI inference service; the Streamlit app can call it instead of trying to load SadTalker inside the web app.

### 1. Prepare a GPU machine

On a GPU host you control, clone this repository and install SadTalker and its checkpoints using the [official SadTalker installation guide](https://github.com/OpenTalker/SadTalker/blob/main/docs/install.md). The service and SadTalker must run in the same environment or be configured with `SADTALKER_DIR` and `SADTALKER_PYTHON`.

Install the service dependencies from this repository:

```bash
python -m pip install -r avatar-service-requirements.txt
```

Configure the local SadTalker paths and a long random service token (do not use the example value):

```bash
export SADTALKER_DIR="/path/to/SadTalker"
export SADTALKER_PYTHON="/path/to/sadtalker-env/bin/python"
export SADTALKER_SERVICE_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
uvicorn avatar_service:app --host 0.0.0.0 --port 8000
```

Put the service behind HTTPS (for example, a reverse proxy or your GPU host's HTTPS ingress). Do not expose port 8000 directly to the public internet without HTTPS and access controls. The service requires a bearer token, limits upload sizes, permits one GPU inference at a time, and deletes uploaded media after the MP4 response is sent. Keep the token private.

### 2. Connect the Streamlit website

In Streamlit Community Cloud, open your app's **Settings → Secrets** and add:

```toml
SADTALKER_API_URL = "https://your-https-gpu-host"
SADTALKER_API_TOKEN = "the-same-long-random-token"
```

Restart/reboot the Streamlit app. The status should report that authenticated remote inference is configured. Upload a photo and narration, then render. The app downloads the generated MP4 from the GPU service and adds the final audio track.

### Important

- This service code is committed, but it is **not deployed or GPU-tested by GitHub Actions**. You still need to install SadTalker/checkpoints and start it on a GPU host, then add the URL and token to Streamlit Secrets.
- GPU hosting may cost money; a free, continuously available GPU endpoint is not guaranteed. Do not enter payment details or deploy paid resources without checking the provider's price and shutdown policy.
- SadTalker creates audio-driven facial/head animation. A single photo does not guarantee realistic full-body movement or natural hand gestures. A pose-reference video can guide the pose but is not a guarantee.
- Test first with a short narration and a photo you have permission to animate. Never commit personal photos, narration, or generated videos to this public repository.
