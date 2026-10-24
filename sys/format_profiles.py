"""Single Source of Truth for Short (9:16 Portrait) and Long (16:9 Landscape) video formats.

Strictly separates visual framing, resolution, Flow RPC aspect ratios, caption layout,
caption clearance, text style, and watermark coordinates between the two pipelines.
Contains zero fixed duration constraints — video duration is determined strictly by
authored scene scripts and measured WAV narration.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

PROFILES: Dict[str, Dict[str, Any]] = {
    "short_9x16": {
        "id": "short_9x16",
        "audio_lufs": -11.0,
        "audio_peak_db": -1.0,
        "narration_pauses": {
            "short_sentence": 0.16, "sentence": 0.22, "minor": 0.12,
            "opening_short_sentence": 0.12, "opening_sentence": 0.16,
            "scene": 0.30, "tail": 0.15,
            "recommended_pivot": 0.45,
        },
        "aspect_ratio": "9:16",
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "flow_rpc_aspect": 2,
        "framing_mode": "vertical_portrait_safe_zone",
        "caption_layout": {
            "max_line_chars": 28,
            "max_cue_chars": 54,
            "bottom": 400,
            "width": 820,
            "left_offset": 56,
            "font_size": 48,
        },
        "caption_clearance_when_subtitled": {"edge": "bottom", "fraction": 0.18},
        "caption_clearance_when_unsubtitled": None,
        "text_style": {
            "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
            "color": "#172033",
            "outline": "nền sáng tương phản",
            "size": "dễ đọc trên điện thoại (khung dọc 9:16)",
            "placement": "cách mép ít nhất 10%; tránh mặt và vùng phụ đề dưới cùng 18%",
        },
        "watermark": {
            "size_ratio_w": 100 / 1080,
            "right_ratio_w": 32 / 1080,
            "top_ratio_h": 120 / 1920,
        },
    },
    "long_16x9": {
        "id": "long_16x9",
        "audio_lufs": -14.0,
        "audio_peak_db": -1.5,
        "narration_pauses": {
            "short_sentence": 0.20, "sentence": 0.28, "minor": 0.16,
            "opening_short_sentence": 0.16, "opening_sentence": 0.20,
            "scene": 0.40, "tail": 0.25,
            "recommended_pivot": 0.60,
        },
        "aspect_ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "flow_rpc_aspect": 3,
        "framing_mode": "horizontal_widescreen_cinema",
        "caption_layout": {
            "max_line_chars": 42,
            "max_cue_chars": 84,
            "bottom": 85,
            "width": 1400,
            "font_size": 38,
        },
        "caption_clearance_when_subtitled": None,
        "caption_clearance_when_unsubtitled": None,
        "text_style": {
            "font": "sans-serif rõ nét, cùng kiểu và độ đậm xuyên suốt",
            "color": "#172033",
            "outline": "nền sáng tương phản",
            "size": "dễ đọc trên màn hình ngang (khung 16:9)",
            "placement": "cách mép ít nhất 10%; bố cục ngang thoáng, không ép lề dọc điện thoại",
        },
        "watermark": {
            "size_ratio_w": 108 / 1920,
            "right_ratio_w": 23 / 1920,
            "bottom_ratio_h": 38 / 1080,
        },
    },
}

ASPECT_TO_PROFILE: Dict[str, str] = {
    "9:16": "short_9x16",
    "16:9": "long_16x9",
}

PROFILE_TO_ASPECT: Dict[str, str] = {
    "short_9x16": "9:16",
    "long_16x9": "16:9",
    "dual": "dual",
}


def get_profile(profile_or_aspect: str) -> Dict[str, Any]:
    """Return a copy of the format profile for a profile ID ('short_9x16', 'long_16x9') or aspect ratio ('9:16', '16:9')."""
    if profile_or_aspect in PROFILES:
        return dict(PROFILES[profile_or_aspect])
    if profile_or_aspect in ASPECT_TO_PROFILE:
        return dict(PROFILES[ASPECT_TO_PROFILE[profile_or_aspect]])
    raise ValueError(f"FORMAT_PROFILE_UNSUPPORTED: unknown profile or aspect ratio {profile_or_aspect!r}")


def resolve_format_profile(brief: Dict[str, Any]) -> str:
    """Resolve and validate the format profile for a brief dictionary."""
    validate_format_separation(brief)
    explicit = brief.get("format_profile")
    if explicit:
        return str(explicit)
    ratio = brief.get("aspect_ratio")
    if ratio == "dual":
        return "dual"
    if ratio in ASPECT_TO_PROFILE:
        return ASPECT_TO_PROFILE[ratio]
    raise ValueError(f"FORMAT_PROFILE_REQUIRED: explicit aspect_ratio or format_profile required, got {ratio!r}")


def validate_format_separation(brief: Dict[str, Any]) -> None:
    """Ensure format_profile, aspect_ratio, and outputs do not cross-contaminate 9:16 and 16:9."""
    if not isinstance(brief, dict):
        raise ValueError("FORMAT_SEPARATION: brief must be a dictionary")
    ratio = brief.get("aspect_ratio")
    if ratio not in ("9:16", "16:9", "dual"):
        raise ValueError(f"FORMAT_SEPARATION: explicit aspect_ratio ('9:16', '16:9', or 'dual') required, got {ratio!r}")

    profile = brief.get("format_profile")
    if profile is not None:
        if profile not in PROFILE_TO_ASPECT:
            raise ValueError(f"FORMAT_SEPARATION: unsupported format_profile {profile!r}")
        expected_ratio = PROFILE_TO_ASPECT[profile]
        if ratio != expected_ratio:
            raise ValueError(
                f"FORMAT_SEPARATION_MISMATCH: format_profile={profile!r} requires aspect_ratio={expected_ratio!r}, got {ratio!r}"
            )

    plans = brief.get("outputs")
    if plans is not None:
        if not isinstance(plans, list) or not plans:
            raise ValueError("FORMAT_SEPARATION: outputs must be a non-empty list when provided")
        expected_aspects = ["9:16", "16:9"] if ratio == "dual" else [ratio]
        actual_aspects = [p.get("aspect_ratio") for p in plans if isinstance(p, dict)]
        if actual_aspects != expected_aspects:
            raise ValueError(
                f"FORMAT_SEPARATION_MISMATCH: outputs aspect_ratios {actual_aspects} do not match {expected_aspects}"
            )


def caption_limits_for_aspect(aspect_ratio: str = "16:9") -> Tuple[int, int]:
    """Return (max_line_chars, max_cue_chars) for the given aspect ratio."""
    prof = get_profile(aspect_ratio)
    layout = prof["caption_layout"]
    return int(layout["max_line_chars"]), int(layout["max_cue_chars"])


def clearance_for_output(aspect_ratio: str = "16:9", subtitles: bool = True) -> Optional[Dict[str, Any]]:
    """Return caption_clearance dict when subtitled, or None when unsubtitled."""
    prof = get_profile(aspect_ratio)
    if subtitles:
        clearance = prof["caption_clearance_when_subtitled"]
        return dict(clearance) if clearance else None
    clearance = prof["caption_clearance_when_unsubtitled"]
    return dict(clearance) if clearance else None


def default_text_style(aspect_ratio: str = "16:9") -> Dict[str, str]:
    """Return the format-appropriate planning.text_style for '16:9' or given aspect."""
    if aspect_ratio in ("16:9", "long_16x9", "dual"):
        return dict(PROFILES["long_16x9"]["text_style"])
    prof = get_profile(aspect_ratio)
    return dict(prof["text_style"])


def audio_mastering_for_format(profile_or_aspect: str = "16:9") -> Dict[str, float]:
    """Return format-specific audio mastering settings (audio_lufs and audio_peak_db)."""
    prof = get_profile(profile_or_aspect)
    is_long = "16x9" in str(prof.get("id", "")) or prof.get("aspect_ratio") == "16:9"
    default_lufs = -14.0 if is_long else -11.0
    default_peak = -1.5 if is_long else -1.0
    return {
        "audio_lufs": float(prof.get("audio_lufs", default_lufs)),
        "audio_peak_db": float(prof.get("audio_peak_db", default_peak)),
    }

