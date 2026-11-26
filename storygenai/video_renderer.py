"""Render a story plan as a simple, silent vertical MP4 video."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import imageio_ffmpeg

from storygenai.captions import caption_segments
from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH = 1080
HEIGHT = 1920
FPS = 24


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Load a Unicode font with complex-script shaping support when available."""
    import glob

    names = (
        ["NotoSansMalayalam-Bold.ttf", "NotoSansMalayalamUI-Bold.ttf", "NotoSans-Bold.ttf"]
        if bold
        else ["NotoSansMalayalam-Regular.ttf", "NotoSansMalayalamUI-Regular.ttf", "NotoSans-Regular.ttf"]
    )
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansMalayalamUI-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansMalayalamUI-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Malayalam Sangam MN.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        candidates.extend(glob.glob(f"/usr/share/fonts/**/*{name}", recursive=True))
    candidates.extend(glob.glob("/usr/share/fonts/**/*Malayalam*.ttf", recursive=True))
    candidates.extend(glob.glob("/usr/share/fonts/**/*Malayalam*.otf", recursive=True))

    # Prefer RAQM, which shapes Malayalam conjuncts and vowel signs correctly.
    layout_engine = getattr(ImageFont, "Layout", None)
    raqm = getattr(layout_engine, "RAQM", None) if layout_engine else None
    for candidate in dict.fromkeys(candidates):
        try:
            if raqm is not None:
                return ImageFont.truetype(candidate, size=size, layout_engine=raqm)
            return ImageFont.truetype(candidate, size=size)
        except (OSError, ValueError):
            continue
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _make_frame(scene: dict[str, Any], scene_number: int, scene_count: int, style: str, width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (int(14 + 18 * ratio), int(24 + 12 * ratio), int(48 + 30 * ratio))
        draw.line((0, y, width, y), fill=color)
    margin = int(width * 0.09)
    accent = (112, 190, 255)
    draw.rounded_rectangle(
        (margin, int(height * 0.12), width - margin, int(height * 0.125)),
        radius=max(2, width // 135),
        fill=accent,
    )

    label_font = _font(max(18, int(width * 0.035)), bold=True)
    title_font = _font(max(30, int(width * 0.075)), bold=True)
    body_font = _font(max(20, int(width * 0.043)))
    footer_font = _font(max(16, int(width * 0.03)))

    draw.text((margin, int(height * 0.16)), f"{style.upper()}  •  {scene.get('label', 'SCENE')} {scene_number}/{scene_count}", font=label_font, fill=accent)
    title_lines = _wrap_text(draw, str(scene.get("title", f"Scene {scene_number}")), title_font, width - 2 * margin)
    y = int(height * 0.28)
    for line in title_lines[:3]:
        draw.text((margin, y), line, font=title_font, fill=(255, 255, 255))
        y += int(title_font.size * 1.25)

    body_lines = _wrap_text(draw, str(scene.get("narration", "")).strip(), body_font, width - 2 * margin)
    y += int(height * 0.04)
    line_height = int(body_font.size * 1.55)
    max_lines = max(3, int(height * 0.28 / line_height))
    for line in body_lines[:max_lines]:
        draw.text((margin, y), line, font=body_font, fill=(220, 228, 240))
        y += line_height

    draw.text((margin, int(height * 0.88)), "STORYGENAI  •  CREATE YOUR NEXT STORY", font=footer_font, fill=(155, 170, 194))
    return image



def _make_avatar_frame(
    avatar_image: Image.Image,
    scene: dict[str, Any],
    width: int,
    height: int,
) -> Image.Image:
    """Create a portrait photo-based scene frame; does not animate facial features."""
    source = avatar_image.convert("RGB")
    frame = ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.42))
    draw = ImageDraw.Draw(frame, "RGBA")
    caption_font = _font(max(24, int(width * 0.043)), bold=True)
    text = str(scene.get("narration", "")).strip()
    lines = _wrap_text(draw, text, caption_font, int(width * 0.82))
    line_height = int(caption_font.size * 1.35)
    max_lines = max(2, min(5, int(height * 0.15 / line_height)))
    lines = lines[:max_lines]
    panel_height = line_height * len(lines) + int(height * 0.035)
    top = height - panel_height
    draw.rectangle((0, top, width, height), fill=(5, 10, 20, 185))
    y = top + int(height * 0.018)
    for line in lines:
        draw.text((int(width * 0.08), y), line, font=caption_font, fill=(255, 255, 255, 255))
        y += line_height
    return frame

def render_story_video(
    plan: dict[str, Any],
    output_path: str | Path,
    fps: int = FPS,
    width: int = WIDTH,
    height: int = HEIGHT,
    avatar_image: Image.Image | None = None,
) -> Path:
    """Render a silent 9:16 MP4 from a story plan using bundled FFmpeg."""
    scenes = plan.get("scenes")
    duration = plan.get("duration_seconds")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("The story plan must contain at least one scene.")
    if not isinstance(duration, int) or duration <= 0:
        raise ValueError("The story plan must contain a positive integer duration.")
    if fps < 1 or width < 2 or height < 2:
        raise ValueError("FPS and video dimensions must be positive.")
    if width % 2 or height % 2:
        raise ValueError("Video width and height must be even for MP4 encoding.")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    total_frames = duration * fps
    segments = caption_segments(plan)
    scene_count = len(segments)
    frame_bytes = [
        (
            _make_avatar_frame(
                avatar_image,
                {"title": segment["title"], "narration": segment["text"], "label": segment["title"].upper()},
                width,
                height,
            )
            if avatar_image is not None
            else _make_frame(
                {"title": segment["title"], "narration": segment["text"], "label": segment["title"].upper()},
                index + 1,
                scene_count,
                str(plan.get("style", "Story")),
                width,
                height,
            )
        ).tobytes()
        for index, segment in enumerate(segments)
    ]
    boundaries = []
    elapsed = 0.0
    for segment in segments:
        elapsed += segment["duration"]
        boundaries.append(min(total_frames, round(elapsed * fps)))
    boundaries[-1] = total_frames
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgb24",
        "-r", str(fps), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(destination),
    ]

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert process.stdin is not None
    try:
        segment_index = 0
        for frame_index in range(total_frames):
            while segment_index < scene_count - 1 and frame_index >= boundaries[segment_index]:
                segment_index += 1
            process.stdin.write(frame_bytes[segment_index])
        process.stdin.close()
        error_output = process.stderr.read() if process.stderr is not None else b""
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(f"FFmpeg could not render the video: {error_output.decode(errors='replace')[-1000:]}")
    except Exception:
        if process.poll() is None:
            process.kill()
            process.wait()
        destination.unlink(missing_ok=True)
        raise

    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError("Video rendering did not produce an MP4 file.")
    return destination
