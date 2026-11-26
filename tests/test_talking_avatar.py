from pathlib import Path

import pytest

from storygenai import talking_avatar


def test_sadtalker_status_reports_missing_checkout(monkeypatch, tmp_path):
    monkeypatch.setenv("SADTALKER_DIR", str(tmp_path / "missing"))
    ready, message = talking_avatar.sadtalker_status()
    assert not ready
    assert "inference.py" in message


def test_generate_talking_avatar_invokes_configured_sadtalker(monkeypatch, tmp_path):
    model_dir = tmp_path / "SadTalker"
    (model_dir / "checkpoints").mkdir(parents=True)
    (model_dir / "checkpoints" / "test.ckpt").write_text("stub", encoding="utf-8")
    (model_dir / "inference.py").write_text("# test stub", encoding="utf-8")
    monkeypatch.setenv("SADTALKER_DIR", str(model_dir))
    monkeypatch.delenv("SADTALKER_CHECKPOINT_DIR", raising=False)
    monkeypatch.delenv("SADTALKER_FORCE_CPU", raising=False)

    image_path = tmp_path / "presenter.png"
    audio_path = tmp_path / "voice.wav"
    image_path.write_bytes(b"image")
    audio_path.write_bytes(b"audio")
    pose_path = tmp_path / "pose.mp4"
    pose_path.write_bytes(b"video")
    result_dir = tmp_path / "result"

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        output_dir = Path(command[command.index("--result_dir") + 1])
        generated = output_dir / "fake-avatar.mp4"
        generated.write_bytes(b"fake mp4")
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        return Result()

    monkeypatch.setattr(talking_avatar.subprocess, "run", fake_run)
    output = talking_avatar.generate_talking_avatar(
        image_path,
        audio_path,
        result_dir,
        pose_style=7,
        preprocess="full",
        size=256,
        pose_reference_video=pose_path,
    )

    assert output.name == "fake-avatar.mp4"
    assert "--source_image" in captured["command"]
    assert "--driven_audio" in captured["command"]
    assert "--still" in captured["command"]
    assert "--ref_pose" in captured["command"]
