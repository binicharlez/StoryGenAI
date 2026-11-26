"""SadTalker adapter with local and authenticated remote GPU inference support."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import requests


def get_sadtalker_dir(project_root: str | Path | None = None) -> Path:
    configured = os.environ.get("SADTALKER_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    root = Path(project_root).resolve() if project_root else Path(__file__).resolve().parents[1]
    return root / "SadTalker"


def sadtalker_status(project_root: str | Path | None = None) -> tuple[bool, str]:
    """Report whether remote inference or a complete local SadTalker is configured."""
    remote_url = os.environ.get("SADTALKER_API_URL", "").strip()
    remote_token = os.environ.get("SADTALKER_API_TOKEN", "").strip()
    if remote_url:
        if not remote_token:
            return False, "SADTALKER_API_URL is set, but SADTALKER_API_TOKEN is missing."
        return True, "Authenticated remote SadTalker inference is configured."
    model_dir = get_sadtalker_dir(project_root)
    inference = model_dir / "inference.py"
    checkpoint_dir = Path(os.environ.get("SADTALKER_CHECKPOINT_DIR", model_dir / "checkpoints")).expanduser()
    if not inference.is_file():
        return False, f"SadTalker inference.py was not found at {inference}"
    if not checkpoint_dir.is_dir() or not any(checkpoint_dir.iterdir()):
        return False, f"SadTalker checkpoints were not found in {checkpoint_dir}"
    return True, f"SadTalker is configured at {model_dir}"


def _generate_remote(
    image_path: Path,
    audio_path: Path,
    output_dir: Path,
    pose_style: int,
    preprocess: str,
    size: int,
    pose_video_path: Path | None,
) -> Path:
    base_url = os.environ["SADTALKER_API_URL"].strip().rstrip("/")
    token = os.environ["SADTALKER_API_TOKEN"].strip()
    endpoint = base_url if base_url.endswith("/v1/animate") else base_url + "/v1/animate"
    headers = {"Authorization": f"Bearer {token}"}
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "talking_avatar.mp4"
    files = {
        "source_image": (image_path.name, image_path.open("rb"), "image/png"),
        "driven_audio": (audio_path.name, audio_path.open("rb"), "audio/wav"),
    }
    if pose_video_path is not None:
        files["pose_reference_video"] = (pose_video_path.name, pose_video_path.open("rb"), "video/mp4")
    try:
        with requests.post(
            endpoint,
            headers=headers,
            files=files,
            data={"pose_style": str(pose_style), "preprocess": preprocess, "size": str(size)},
            timeout=(30, 900),
            stream=True,
        ) as response:
            if response.status_code != 200:
                detail = response.text[:1500] if response.headers.get("content-type", "").startswith("text/") else "Remote inference failed."
                raise RuntimeError(f"Remote SadTalker returned HTTP {response.status_code}: {detail}")
            content_type = response.headers.get("content-type", "").lower()
            if "video/mp4" not in content_type and "application/octet-stream" not in content_type:
                raise RuntimeError(f"Remote inference returned unexpected content type: {content_type}")
            written = 0
            max_bytes = 300 * 1024 * 1024
            with destination.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > max_bytes:
                        raise RuntimeError("Remote video exceeded the 300 MB safety limit.")
                    output.write(chunk)
        if destination.stat().st_size < 1024:
            destination.unlink(missing_ok=True)
            raise RuntimeError("Remote service returned an empty or invalid MP4.")
        return destination
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        for _, file_tuple in files.items():
            file_tuple[1].close()


def generate_talking_avatar(
    source_image: str | Path,
    driven_audio: str | Path,
    result_dir: str | Path,
    pose_style: int = 0,
    preprocess: str = "full",
    size: int = 256,
    pose_reference_video: str | Path | None = None,
) -> Path:
    """Run remote GPU inference when configured, otherwise use local SadTalker."""
    ready, message = sadtalker_status()
    if not ready:
        raise RuntimeError(message + ". Configure remote inference or install SadTalker locally.")

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

    if os.environ.get("SADTALKER_API_URL", "").strip():
        return _generate_remote(image_path, audio_path, output_dir, pose_style, preprocess, size, pose_video_path)

    model_dir = get_sadtalker_dir()
    checkpoint_dir = Path(os.environ.get("SADTALKER_CHECKPOINT_DIR", model_dir / "checkpoints")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    sadtalker_python = os.environ.get("SADTALKER_PYTHON", "").strip() or sys.executable
    command = [
        sadtalker_python, str(model_dir / "inference.py"),
        "--source_image", str(image_path), "--driven_audio", str(audio_path),
        "--result_dir", str(output_dir), "--checkpoint_dir", str(checkpoint_dir),
        "--preprocess", preprocess, "--size", str(size), "--pose_style", str(pose_style), "--verbose",
    ]
    if pose_video_path is not None:
        command.extend(["--ref_pose", str(pose_video_path)])
    if os.environ.get("SADTALKER_FORCE_CPU", "").strip().lower() in {"1", "true", "yes"}:
        command.append("--cpu")

    result = subprocess.run(command, cwd=str(model_dir), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "No diagnostic output was returned.")[-2500:]
        raise RuntimeError(f"SadTalker failed (exit {result.returncode}):\n{detail}")
    videos = [path for path in output_dir.rglob("*.mp4") if path.is_file() and path.stat().st_size > 0]
    if not videos:
        detail = (result.stdout or result.stderr or "SadTalker produced no MP4 file.")[-1500:]
        raise RuntimeError(f"SadTalker completed but no video was found:\n{detail}")
    return max(videos, key=lambda path: path.stat().st_mtime)
