"""Private FastAPI endpoint for SadTalker running on a GPU host.

Run only behind HTTPS. Set SADTALKER_SERVICE_TOKEN and install SadTalker/checkpoints
on the same machine. Uploaded media is stored in a temporary directory and removed
after the MP4 response has been sent.
"""
from __future__ import annotations

import hmac
import os
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

# This service must run the local model; never call itself recursively.
os.environ.pop("SADTALKER_API_URL", None)

from storygenai.talking_avatar import generate_talking_avatar, sadtalker_status

app = FastAPI(title="StoryGenAI Private Avatar Inference", docs_url=None, redoc_url=None)
bearer = HTTPBearer(auto_error=False)
inference_lock = threading.Lock()
MAX_IMAGE = 20 * 1024 * 1024
MAX_AUDIO = 50 * 1024 * 1024
MAX_POSE = 120 * 1024 * 1024


def require_token(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> None:
    expected = os.environ.get("SADTALKER_SERVICE_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Avatar service token is not configured.")
    supplied = credentials.credentials if credentials else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid service token.")


async def save_upload(upload: UploadFile, destination: Path, max_bytes: int, accepted: set[str]) -> None:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in accepted:
        raise HTTPException(status_code=415, detail=f"Unsupported file extension: {suffix or 'none'}")
    written = 0
    try:
        with destination.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                written += len(chunk)
                if written > max_bytes:
                    raise HTTPException(status_code=413, detail="Uploaded file exceeds the size limit.")
                output.write(chunk)
    finally:
        await upload.close()
    if written == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")


@app.get("/health")
def health():
    ready, reason = sadtalker_status()
    if not ready:
        raise HTTPException(status_code=503, detail=reason)
    return {"status": "ready", "engine": "SadTalker"}


@app.post("/v1/animate", dependencies=[Depends(require_token)])
async def animate(
    source_image: Annotated[UploadFile, File()],
    driven_audio: Annotated[UploadFile, File()],
    pose_style: Annotated[int, Form()] = 0,
    preprocess: Annotated[str, Form()] = "full",
    size: Annotated[int, Form()] = 256,
    pose_reference_video: Annotated[UploadFile | None, File()] = None,
):
    if not 0 <= pose_style <= 45 or preprocess not in {"crop", "extcrop", "resize", "full", "extfull"} or size not in {256, 512}:
        raise HTTPException(status_code=422, detail="Invalid animation settings.")
    temp_root = Path(tempfile.mkdtemp(prefix="storygenai-avatar-"))
    source_path = temp_root / "source.png"
    audio_path = temp_root / "narration.wav"
    result_dir = temp_root / "result"
    try:
        await save_upload(source_image, source_path, MAX_IMAGE, {".png", ".jpg", ".jpeg"})
        await save_upload(driven_audio, audio_path, MAX_AUDIO, {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac"})
        pose_path = None
        if pose_reference_video is not None:
            pose_path = temp_root / "pose.mp4"
            await save_upload(pose_reference_video, pose_path, MAX_POSE, {".mp4"})
        if not inference_lock.acquire(blocking=False):
            raise HTTPException(status_code=429, detail="The GPU is busy rendering another video. Please retry in a few minutes.")
        try:
            output_path = await run_in_threadpool(
                generate_talking_avatar,
                source_path,
                audio_path,
                result_dir,
                pose_style,
                preprocess,
                size,
                pose_path,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Avatar inference failed: {str(exc)[:1800]}") from exc
        finally:
            inference_lock.release()
        if not output_path.is_file() or output_path.stat().st_size < 1024:
            raise HTTPException(status_code=500, detail="Inference did not produce a valid MP4.")
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="storygenai_talking_avatar.mp4",
            background=BackgroundTask(shutil.rmtree, temp_root, ignore_errors=True),
        )
    except Exception:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise
