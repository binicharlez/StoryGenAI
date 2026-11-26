"""Optional SadTalker adapter for audio-driven talking-avatar video.

The app does not download multi-gigabyte model checkpoints automatically.
Configure SADTALKER_DIR to a local SadTalker checkout with its checkpoints.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_sadtalker_dir(project_root: str | Path | None = None) -> Path:
    """Return the configured SadTalker checkout path."""
    configured = os.environ.get("SADTALKER_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    root = Path(project_root).resolve() if project_root else Path(__file__).resolve().parents[1]
    return root / "SadTalker"


def sadtalker_status(project_root: str | Path | None = None) -> tuple[bool, str]:
    """Report whether the external SadTalker code and checkpoints are present."""
    model_dir = get_sadtalker_dir(project_root)
    inference = model_dir / "inference.py"
    checkpoint_dir = Path(os.environ.get("SADTALKER_CHECKPOINT_DIR", model_dir / "checkpoints")).expanduser()
    if not inference.is_file():
        return False, f"SadTalker inference.py was not found at {inference}"
    if not checkpoint_dir.is_dir() or not any(checkpoint_dir.iterdir()):
        return False, f"SadTalker checkpoints were not found in {checkpoint_dir}"
    return True, f"SadTalker is configured at {model_dir}"


def generate_talking_avatar(
    source_image: str | Path,
    driven_audio: str | Path,
    result_dir: str | Path,
    pose_style: int = 0,
    preprocess: str = "full",
    size: int = 256,
    pose_reference_video: str | Path | None = None,
) -> Path:
    """Run SadTalker and return its generated MP4 path."""
    ready, message = sadtalker_status()
    if not ready:
        raise RuntimeError(
            message
            + ". Install SadTalker and its model checkpoints, then set SADTALKER_DIR. "
            "See https://github.com/OpenTalker/SadTalker"
        )

    image_path = Path(source_image).expanduser().resolve()
    audio_path = Path(driven_audio).expanduser().resolve()
    output_dir = Path(result_dir).expanduser().resolve()
    if not image_path.is_file():
        raise FileNotFoundError(f"Presenter photo not found: {image_path}")
    if not audio_path.is_file():
        raise FileNotFoundError(f"Narration audio not found: {audio_path}")
    pose_video_path = Path(pose_reference_video).expanduser().resolve() if pose_reference_video else None
    if pose_video_path is not None and not pose_video_path.is_file():
        raise FileNotFoundError(f"Pose reference video not found: {pose_video_path}")
    if not 0 <= pose_style <= 45:
        raise ValueError("Pose style must be between 0 and 45.")
    if preprocess not in {"crop", "extcrop", "resize", "full", "extfull"}:
        raise ValueError("Unsupported SadTalker preprocessing mode.")
    if size not in {256, 512}:
        raise ValueError("SadTalker size must be 256 or 512.")

    model_dir = get_sadtalker_dir()
    checkpoint_dir = Path(os.environ.get("SADTALKER_CHECKPOINT_DIR", model_dir / "checkpoints")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(model_dir / "inference.py"),
        "--source_image", str(image_path),
        "--driven_audio", str(audio_path),
        "--result_dir", str(output_dir),
        "--checkpoint_dir", str(checkpoint_dir),
        "--preprocess", preprocess,
        "--size", str(size),
        "--pose_style", str(pose_style),
        "--verbose",
    ]
    if pose_video_path is not None:
        command.extend(["--ref_pose", str(pose_video_path)])
    if os.environ.get("SADTALKER_FORCE_CPU", "").strip().lower() in {"1", "true", "yes"}:
        command.append("--cpu")

    result = subprocess.run(
        command,
        cwd=str(model_dir),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "No diagnostic output was returned.")[-2500:]
        raise RuntimeError(f"SadTalker failed (exit {result.returncode}):\n{detail}")

    videos = [path for path in output_dir.rglob("*.mp4") if path.is_file() and path.stat().st_size > 0]
    if not videos:
        detail = (result.stdout or result.stderr or "SadTalker produced no MP4 file.")[-1500:]
        raise RuntimeError(f"SadTalker completed but no video was found:\n{detail}")
    return max(videos, key=lambda path: path.stat().st_mtime)
