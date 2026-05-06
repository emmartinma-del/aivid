"""
Background music from Pixabay Music API (royalty-free, no attribution required for paid plans).
"""
import os
import subprocess
import httpx
from app.config import settings

STYLE_GENRES = {
    "gaming":    "electronic",
    "modern":    "ambient",
    "corporate": "corporate",
    "fun":       "upbeat",
}


def fetch_music(style_theme: str, target_duration: float, output_path: str) -> str:
    """Download background track and trim to target_duration. Returns path."""
    genre = STYLE_GENRES.get(style_theme, "ambient")
    track_url = _search_pixabay(genre)

    raw_path = output_path.replace(".mp3", "_raw.mp3")
    _download(track_url, raw_path)
    _trim_and_fade(raw_path, output_path, target_duration)
    os.remove(raw_path)
    return output_path


def _search_pixabay(genre: str) -> str:
    if not settings.pixabay_api_key:
        return _fallback_silence_url()

    url = "https://pixabay.com/api/music/"
    params = {"key": settings.pixabay_api_key, "genre": genre, "per_page": 5}
    with httpx.Client(timeout=15) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])

    if not hits:
        return _fallback_silence_url()
    return hits[0]["audio"]["original"]


def _fallback_silence_url() -> str:
    return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"


def _download(url: str, path: str) -> None:
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)


def _trim_and_fade(input_path: str, output_path: str, duration: float) -> None:
    fade_duration = min(2.0, duration * 0.1)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-t", str(duration),
            "-af", f"afade=t=out:st={duration - fade_duration}:d={fade_duration}",
            "-ar", "44100", "-ac", "2",
            output_path,
        ],
        check=True, capture_output=True,
    )
