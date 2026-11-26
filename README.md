# StoryGenAI

StoryGenAI is an early-stage Streamlit project for turning text ideas into creative vertical-video stories.

## Current prototype

- Story idea input with Educational, Motivational, Funny, and Cinematic styles
- Offline template-based narration draft and scene outline
- Visual prompts for each scene
- JSON export of the story plan
- **Silent vertical MP4 export** with text-based scene cards (9:16, H.264)
- Configuration and safe file-management utilities
- Automated tests through GitHub Actions

The story builder is deterministic and template-based. MP4 rendering uses Pillow and the bundled FFmpeg binary from imageio-ffmpeg. No paid API or AI model is required. The current video contains text scene cards only; generated footage, narration audio, voice cloning, and face animation are not connected yet.

## Run in GitHub Codespaces

1. Open this repository on GitHub.
2. Select **Code → Codespaces → Create codespace on main**.
3. Wait for the environment to finish setting up.
4. In the Codespaces terminal, run:

   ```bash
   streamlit run app.py
   ```

5. Open the forwarded port **8501** when prompted.
6. Enter a story idea, prepare the outline, then select **Render vertical MP4** and download the result.

The Codespaces configuration installs the Python dependencies automatically.

## Run locally (optional)

Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
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
