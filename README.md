# StoryGenAI

StoryGenAI is an early-stage Streamlit project intended to help turn text ideas into creative vertical videos for stories and reels.

## Phase 1: Project foundation

This first phase includes:
- A simple Streamlit landing page and story-idea form
- Environment-based configuration
- Local data, upload, and output directory helpers
- Basic path-traversal protection for file writes
- Dependency and environment example files
- Initial tests

**Video generation, face/voice animation, model downloads, and external API integrations are not implemented in Phase 1.** No paid API or large model is required to run this scaffold.

## Setup

Use Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
streamlit run app.py
```

## Test

```bash
pytest
```

## Configuration

Optional settings are read from environment variables:
- `STORYGENAI_APP_NAME`
- `STORYGENAI_DATA_DIR`

Keep real credentials in your local `.env` file or a secrets manager. Never commit secrets to GitHub.
