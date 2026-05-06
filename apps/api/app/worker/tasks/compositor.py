"""
FFmpeg-based video compositor.
Builds the final video from: screenshots + voiceover + background music.
"""
import os
import subprocess
import ffmpeg
from PIL import Image, ImageDraw, ImageFont
from app.worker.utils.store_specs import VideoSpec
from app.worker.utils.ffmpeg_helpers import get_duration

THEME_COLORS = {
    "modern":    {"bg": "#0F172A", "accent": "#6366F1", "text": "#F8FAFC"},
    "gaming":    {"bg": "#030712", "accent": "#22D3EE", "text": "#F0FDF4"},
    "corporate": {"bg": "#1E3A5F", "accent": "#3B82F6", "text": "#FFFFFF"},
    "fun":       {"bg": "#4C1D95", "accent": "#F59E0B", "text": "#FEF3C7"},
}


def compose_video(
    workdir: str,
    screenshot_paths: list[str],
    icon_path: str | None,
    voiceover_path: str,
    music_path: str,
    script: dict,
    spec: VideoSpec,
    style_theme: str,
    app_name: str,
    output_path: str,
) -> str:
    """
    Compose the final video. Returns output_path.
    Pipeline:
      1. Title card (3s)
      2. Screenshots with text overlay (3s each, Ken Burns)
      3. CTA card (3s)
      4. Audio mix
      5. Final encode
    """
    colors = THEME_COLORS.get(style_theme, THEME_COLORS["modern"])
    w, h = spec.width, spec.height
    fps = spec.fps
    segments: list[str] = []

    # 1. Title card
    title_path = os.path.join(workdir, "segment_title.mp4")
    _make_title_card(title_path, w, h, fps, 3, app_name, colors, icon_path)
    segments.append(title_path)

    # 2. Screenshots (up to 6)
    scenes = script.get("scene_descriptions", [])
    for idx, ss_path in enumerate(screenshot_paths[:6]):
        seg_path = os.path.join(workdir, f"segment_ss_{idx}.mp4")
        duration = scenes[idx]["duration"] if idx < len(scenes) else 3
        overlay_text = scenes[idx].get("text_overlay", "") if idx < len(scenes) else ""
        _make_screenshot_segment(ss_path, seg_path, w, h, fps, float(duration), overlay_text, colors, zoom_in=(idx % 2 == 0))
        segments.append(seg_path)

    # 3. CTA card
    cta_path = os.path.join(workdir, "segment_cta.mp4")
    cta_text = script.get("call_to_action", "Download Now")
    _make_cta_card(cta_path, w, h, fps, 3, cta_text, colors, icon_path)
    segments.append(cta_path)

    # 4. Concat all segments
    concat_video_path = os.path.join(workdir, "video_no_audio.mp4")
    _concat_segments(segments, concat_video_path)

    # 5. Mux with mixed audio
    voice_duration = get_duration(voiceover_path)
    total_duration = get_duration(concat_video_path)
    mixed_audio_path = os.path.join(workdir, "audio_mix.aac")
    _mix_audio(voiceover_path, music_path, mixed_audio_path, total_duration)

    # 6. Final encode
    _final_encode(concat_video_path, mixed_audio_path, output_path, spec, total_duration)
    return output_path


def _make_title_card(path: str, w: int, h: int, fps: int, duration: int, app_name: str, colors: dict, icon_path: str | None) -> None:
    img_path = path.replace(".mp4", ".png")
    img = Image.new("RGB", (w, h), color=colors["bg"])
    draw = ImageDraw.Draw(img)

    if icon_path and os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((200, 200))
        img.paste(icon, (w // 2 - 100, h // 2 - 160), icon)

    # Title text centered
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 64)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), app_name, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((w - text_w) // 2, h // 2 + 80), app_name, fill=colors["text"], font=font)
    img.save(img_path)

    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", img_path, "-t", str(duration), "-r", str(fps),
         "-vcodec", "libx264", "-pix_fmt", "yuv420p", path],
        check=True, capture_output=True,
    )
    os.remove(img_path)


def _make_screenshot_segment(
    ss_path: str, out_path: str, w: int, h: int, fps: int, duration: float,
    overlay_text: str, colors: dict, zoom_in: bool
) -> None:
    # Resize screenshot to fit, then Ken Burns + text overlay
    scale_expr = f"if(gt(a,{w}/{h}),{h}*a,-1)"
    crop_expr = f"if(gt(a,{w}/{h}),-1,{w}/a)"

    scale_factor = 1.05
    sw, sh = int(w * scale_factor), int(h * scale_factor)

    if zoom_in:
        x_expr = f"(iw-{w})/2*(t/{duration})"
        y_expr = f"(ih-{h})/2*(t/{duration})"
    else:
        x_expr = f"(iw-{w})/2*(1-t/{duration})"
        y_expr = f"(ih-{h})/2*(1-t/{duration})"

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", ss_path,
        "-t", str(duration), "-r", str(fps),
        "-vf", (
            f"scale={sw}:{sh}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}:{x_expr}:{y_expr}"
            + (f",drawtext=text='{overlay_text}':fontsize=40:fontcolor={colors['text']}:x=(w-tw)/2:y=h-th-60:box=1:boxcolor={colors['accent']}@0.6:boxborderw=10" if overlay_text else "")
        ),
        "-vcodec", "libx264", "-pix_fmt", "yuv420p", out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def _make_cta_card(path: str, w: int, h: int, fps: int, duration: int, cta_text: str, colors: dict, icon_path: str | None) -> None:
    img_path = path.replace(".mp4", ".png")
    img = Image.new("RGB", (w, h), color=colors["bg"])
    draw = ImageDraw.Draw(img)

    if icon_path and os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((160, 160))
        img.paste(icon, (w // 2 - 80, h // 2 - 200), icon)

    try:
        font_cta = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 52)
    except OSError:
        font_cta = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, h // 2 + 50), cta_text, fill=colors["accent"], font=font_cta)
    img.save(img_path)

    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", img_path, "-t", str(duration), "-r", str(fps),
         "-vf", f"fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5}:d=0.5",
         "-vcodec", "libx264", "-pix_fmt", "yuv420p", path],
        check=True, capture_output=True,
    )
    os.remove(img_path)


def _concat_segments(segments: list[str], output_path: str) -> None:
    list_file = output_path.replace(".mp4", "_list.txt")
    with open(list_file, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-c", "copy", output_path],
        check=True, capture_output=True,
    )
    os.remove(list_file)


def _mix_audio(voice_path: str, music_path: str, output_path: str, duration: float) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", voice_path,
            "-i", music_path,
            "-filter_complex", f"[0:a][1:a]amix=inputs=2:duration=first:weights='2 0.4'[aout]",
            "-map", "[aout]",
            "-t", str(duration),
            "-acodec", "aac", "-ab", "192k",
            output_path,
        ],
        check=True, capture_output=True,
    )


def _final_encode(video_path: str, audio_path: str, output_path: str, spec: VideoSpec, duration: float) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v:0", "-map", "1:a:0",
            "-t", str(min(duration, spec.max_duration_sec)),
            "-vcodec", "libx264", "-profile:v", "high", "-level", "4.0",
            "-pix_fmt", "yuv420p", "-r", str(spec.fps),
            "-acodec", "aac", "-ab", "192k",
            "-movflags", "+faststart",
            output_path,
        ],
        check=True, capture_output=True,
    )
