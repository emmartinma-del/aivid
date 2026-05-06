"""
Official App Store and Google Play video specifications.
All resolutions listed as (width, height).
"""
from dataclasses import dataclass


@dataclass
class VideoSpec:
    width: int
    height: int
    orientation: str       # portrait | landscape
    fps: int
    max_duration_sec: int
    codec: str
    audio_codec: str
    max_bitrate_kbps: int
    store: str             # ios | android
    label: str             # human-readable label


IOS_SPECS: list[VideoSpec] = [
    VideoSpec(1080, 1920, "portrait", 30, 30, "h264", "aac", 10000, "ios", "iPhone 6.7\" Portrait"),
    VideoSpec(1290, 2796, "portrait", 30, 30, "h264", "aac", 10000, "ios", "iPhone 6.7\" Pro Portrait"),
    VideoSpec(1242, 2688, "portrait", 30, 30, "h264", "aac", 10000, "ios", "iPhone 6.5\" Portrait"),
    VideoSpec(1920, 1080, "landscape", 30, 30, "h264", "aac", 10000, "ios", "iPhone Landscape"),
    VideoSpec(2048, 2732, "portrait", 30, 30, "h264", "aac", 10000, "ios", "iPad 12.9\" Portrait"),
    VideoSpec(2732, 2048, "landscape", 30, 30, "h264", "aac", 10000, "ios", "iPad 12.9\" Landscape"),
]

ANDROID_SPECS: list[VideoSpec] = [
    VideoSpec(1080, 1920, "portrait", 30, 120, "h264", "aac", 8000, "android", "Android Portrait"),
    VideoSpec(1080, 2340, "portrait", 30, 120, "h264", "aac", 8000, "android", "Android Tall Portrait"),
    VideoSpec(1920, 1080, "landscape", 30, 120, "h264", "aac", 8000, "android", "Android Landscape"),
]

ALL_SPECS = IOS_SPECS + ANDROID_SPECS


def get_specs_for_store(target_store: str) -> list[VideoSpec]:
    """Return specs for ios, android, or both."""
    if target_store == "ios":
        return IOS_SPECS
    if target_store == "android":
        return ANDROID_SPECS
    return ALL_SPECS


def get_primary_spec(target_store: str) -> VideoSpec:
    """Return the main portrait spec used for MVP single-output generation."""
    specs = get_specs_for_store(target_store)
    portrait = [s for s in specs if s.orientation == "portrait"]
    return portrait[0]


# Allowed MIME types for uploaded assets
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}
ALLOWED_ASSET_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
