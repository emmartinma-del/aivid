"""
Voiceover generation: ElevenLabs preferred, OpenAI TTS as fallback.
"""
import os
import httpx
from openai import OpenAI
from app.config import settings

STYLE_VOICES = {
    "gaming":    {"elevenlabs": "IKne3meq5aSn9XLyUdCD", "openai": "onyx"},     # energetic male
    "modern":    {"elevenlabs": "21m00Tcm4TlvDq8ikWAM", "openai": "nova"},     # clear female
    "corporate": {"elevenlabs": "pNInz6obpgDQGcFmaJgB", "openai": "alloy"},   # professional neutral
    "fun":       {"elevenlabs": "EXAVITQu4vr4xnSDxMaL", "openai": "shimmer"}, # bright female
}


def generate_voiceover(narration_text: str, style_theme: str, output_path: str) -> str:
    """Generate voiceover audio and save to output_path. Returns the path."""
    voices = STYLE_VOICES.get(style_theme, STYLE_VOICES["modern"])

    if settings.elevenlabs_api_key:
        return _elevenlabs(narration_text, voices["elevenlabs"], output_path)
    return _openai_tts(narration_text, voices["openai"], output_path)


def _elevenlabs(text: str, voice_id: str, output_path: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": settings.elevenlabs_api_key, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    with httpx.Client(timeout=60) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()

    mp3_path = output_path.replace(".wav", ".mp3")
    with open(mp3_path, "wb") as f:
        f.write(resp.content)

    _convert_to_wav(mp3_path, output_path)
    os.remove(mp3_path)
    return output_path


def _openai_tts(text: str, voice: str, output_path: str) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    mp3_path = output_path.replace(".wav", ".mp3")
    response = client.audio.speech.create(model="tts-1-hd", voice=voice, input=text)
    response.stream_to_file(mp3_path)
    _convert_to_wav(mp3_path, output_path)
    os.remove(mp3_path)
    return output_path


def _convert_to_wav(mp3_path: str, wav_path: str) -> None:
    import subprocess
    subprocess.run(
        ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "2", wav_path],
        check=True, capture_output=True,
    )
