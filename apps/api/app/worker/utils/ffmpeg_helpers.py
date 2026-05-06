"""
FFmpeg helper utilities. All heavy lifting is expressed as ffmpeg-python filter chains.
Switching to GPU encoding (NVENC) requires only changing vcodec_args below.
"""
import os
import subprocess
import json
import ffmpeg
from app.worker.utils.store_specs import VideoSpec


def probe(path: str) -> dict:
    """Return FFprobe JSON for a file."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", path],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def get_duration(path: str) -> float:
    data = probe(path)
    return float(data["format"]["duration"])


def get_resolution(path: str) -> tuple[int, int]:
    data = probe(path)
    for stream in data["streams"]:
        if stream.get("codec_type") == "video":
            return stream["width"], stream["height"]
    raise ValueError(f"No video stream found in {path}")


def vcodec_args(spec: VideoSpec) -> dict:
    """Encoder parameters – swap 'libx264' → 'h264_nvenc' for GPU workers."""
    return {
        "vcodec": "libx264",
        "profile:v": "high",
        "level": "4.0",
        "pix_fmt": "yuv420p",
        "r": spec.fps,
        "video_bitrate": f"{spec.max_bitrate_kbps}k",
        "acodec": "aac",
        "audio_bitrate": "192k",
        "movflags": "+faststart",
    }


def resize_image(src: str, dst: str, width: int, height: int) -> None:
    """Resize + crop an image to exact dimensions using FFmpeg."""
    (
        ffmpeg
        .input(src)
        .filter("scale", w=f"if(gt(a,{width}/{height}),{height}*a,-1)", h=f"if(gt(a,{width}/{height}),-1,{width}/a)")
        .filter("crop", width, height)
        .output(dst, vframes=1)
        .overwrite_output()
        .run(quiet=True)
    )


def add_ken_burns(src: str, dst: str, duration: float, width: int, height: int, zoom_in: bool = True) -> None:
    """Apply a gentle Ken Burns zoom to a still image."""
    scale_factor = 1.05
    sw, sh = int(width * scale_factor), int(height * scale_factor)
    if zoom_in:
        x_expr = f"(iw-{width})/2*(t/{duration})"
        y_expr = f"(ih-{height})/2*(t/{duration})"
    else:
        x_expr = f"(iw-{width})/2*(1-t/{duration})"
        y_expr = f"(ih-{height})/2*(1-t/{duration})"

    (
        ffmpeg
        .input(src, loop=1, t=duration)
        .filter("scale", sw, sh)
        .filter("crop", width, height, x_expr, y_expr)
        .output(dst, r=30, vcodec="libx264", pix_fmt="yuv420p", preset="fast")
        .overwrite_output()
        .run(quiet=True)
    )


def mix_audio(voice_path: str, music_path: str, output_path: str, duration: float) -> None:
    """Mix voiceover (primary) with background music (ducked)."""
    voice = ffmpeg.input(voice_path)
    music = ffmpeg.input(music_path)
    (
        ffmpeg
        .filter([voice.audio, music.audio], "amix", inputs=2, duration="first", weights="2 0.4")
        .filter("atrim", end=duration)
        .output(output_path, acodec="aac", audio_bitrate="192k")
        .overwrite_output()
        .run(quiet=True)
    )


def encode_final(video_path: str, audio_path: str, output_path: str, spec: VideoSpec) -> None:
    """Mux video + audio and encode to final H.264 MP4."""
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)
    (
        ffmpeg
        .output(video, audio, output_path, **vcodec_args(spec))
        .overwrite_output()
        .run(quiet=True)
    )


def validate_output(path: str, spec: VideoSpec) -> list[str]:
    """Validate the output file against store specs. Returns list of errors."""
    errors = []
    try:
        data = probe(path)
        video_stream = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in data["streams"] if s.get("codec_type") == "audio"), None)
        duration = float(data["format"]["duration"])

        if not video_stream:
            errors.append("No video stream found")
            return errors

        if video_stream.get("codec_name") not in ("h264", "avc"):
            errors.append(f"Wrong codec: {video_stream.get('codec_name')}, expected h264")
        if video_stream.get("width") != spec.width:
            errors.append(f"Wrong width: {video_stream.get('width')}, expected {spec.width}")
        if video_stream.get("height") != spec.height:
            errors.append(f"Wrong height: {video_stream.get('height')}, expected {spec.height}")
        if duration > spec.max_duration_sec:
            errors.append(f"Duration {duration:.1f}s exceeds max {spec.max_duration_sec}s")
        if not audio_stream:
            errors.append("No audio stream found")
        file_size_mb = os.path.getsize(path) / (1024 * 1024)
        if file_size_mb > 500:
            errors.append(f"File size {file_size_mb:.0f}MB exceeds 500MB limit")

    except Exception as e:
        errors.append(f"Probe failed: {e}")
    return errors
