"""Small filesystem helpers for local StoryGenAI data."""
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def ensure_project_dirs(settings) -> None:
    """Create the data, upload, and output directories if missing."""
    for directory in (settings.data_dir, settings.uploads_dir, settings.outputs_dir):
        Path(directory).mkdir(parents=True, exist_ok=True)


def safe_child_path(base_dir: PathLike, filename: str) -> Path:
    """Return a path inside base_dir, rejecting path traversal attempts."""
    base = Path(base_dir).expanduser().resolve()
    candidate = (base / filename).resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError("Filename must stay within the selected directory")
    if candidate == base:
        raise ValueError("A filename is required")
    return candidate


def save_bytes(base_dir: PathLike, filename: str, content: bytes) -> Path:
    """Save bytes to a safe child path and return the resulting path."""
    destination = safe_child_path(base_dir, filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return destination
