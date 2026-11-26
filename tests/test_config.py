from pathlib import Path

from storygenai.config import get_settings
from storygenai.file_utils import ensure_project_dirs, safe_child_path


def test_settings_use_environment_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STORYGENAI_DATA_DIR", str(tmp_path / "storydata"))
    settings = get_settings()
    assert settings.data_dir == tmp_path / "storydata"
    assert settings.uploads_dir == settings.data_dir / "uploads"


def test_ensure_project_dirs_creates_directories(tmp_path, monkeypatch):
    monkeypatch.setenv("STORYGENAI_DATA_DIR", str(tmp_path / "storydata"))
    settings = get_settings()
    ensure_project_dirs(settings)
    assert settings.data_dir.is_dir()
    assert settings.uploads_dir.is_dir()
    assert settings.outputs_dir.is_dir()


def test_safe_child_path_rejects_traversal(tmp_path):
    try:
        safe_child_path(tmp_path, "../outside.txt")
    except ValueError:
        pass
    else:
        raise AssertionError("Path traversal should be rejected")
