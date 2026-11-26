"""Environment-based application settings."""
from dataclasses import dataclass
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_name: str
    data_dir: Path
    uploads_dir: Path
    outputs_dir: Path


def get_settings() -> Settings:
    """Read settings from environment variables with safe local defaults."""
    data_dir = Path(os.getenv("STORYGENAI_DATA_DIR", PROJECT_ROOT / "data")).expanduser()
    return Settings(
        app_name=os.getenv("STORYGENAI_APP_NAME", "StoryGenAI"),
        data_dir=data_dir,
        uploads_dir=data_dir / "uploads",
        outputs_dir=data_dir / "outputs",
    )
