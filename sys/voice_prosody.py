"""SSOT Voice Prosody Director for local acoustic sculpting on KhanhTTS-OmniVoice.

Because `kjanh/KhanhTTS-OmniVoice` performs zero-shot voice cloning without ElevenLabs v3
inline emotion tags (`[whisper]`, `[excited]`), cinema vocal variation is sculpted by
combining:
- `omni_speed`: model-native synthesis pacing
- `atempo`: local WSOLA time-stretch factor
- `eq_chain`: FFmpeg acoustic EQ + band-limiting filter chain
- `micro_gain_db`: per-scene level trim relative to `-14.0 LUFS` baseline
- `gap_after_sec` + explicit `[pause:Xms]` / `[pause:Xs]` silence splicing.
"""
from __future__ import annotations

import re
from typing import Any

BASELINE_LUFS: float = -14.0
DEFAULT_DELIVERY_MODE: str = "narrative_cinema"

# Pause marker regex matching script_cadence_checker.PAUSE_RE: [pause:550ms], [pause:0.5s], [pause:500]
PAUSE_RE = re.compile(r"\[pause:\s*([0-9]+(?:\.[0-9]+)?|\.[0-9]+)\s*(ms|s)?\s*\]", re.IGNORECASE)


def _profile(
    mode: str,
    *,
    omni_speed: float,
    atempo: float,
    gap_after_sec: float,
    micro_gain_db: float,
    eq_chain: str,
    description: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "omni_speed": omni_speed,
        "atempo": atempo,
        "effective_rate": round(omni_speed * atempo, 3),
        "gap_after_sec": gap_after_sec,
        "micro_gain_db": micro_gain_db,
        "eq_chain": eq_chain,
        "description": description,
    }


VOICE_DELIVERY_PROFILES: dict[str, dict[str, Any]] = {
    "tense_whisper": _profile(
        "tense_whisper",
        omni_speed=0.98,
        atempo=1.10,
        gap_after_sec=0.28,
        micro_gain_db=-1.8,
        eq_chain=(
            "highpass=f=75,equalizer=f=155:t=q:w=1.1:g=2.4,"
            "equalizer=f=3500:t=q:w=1.2:g=-1.5,lowpass=f=11500"
        ),
        description="Intimate low-register tension with softened upper presence and wide beat pauses.",
    ),
    "narrative_cinema": _profile(
        "narrative_cinema",
        omni_speed=1.08,
        atempo=1.14,
        gap_after_sec=0.14,
        micro_gain_db=0.0,
        eq_chain=(
            "highpass=f=80,equalizer=f=180:t=q:w=1.1:g=1.2,"
            "equalizer=f=3200:t=q:w=1.0:g=2.2,equalizer=f=6500:t=q:w=1.2:g=1.5,lowpass=f=15000"
        ),
        description="Crisp documentary cinema storytelling baseline at 0.0 dB relative trim.",
    ),
    "tactical_breakdown": _profile(
        "tactical_breakdown",
        omni_speed=1.06,
        atempo=1.16,
        gap_after_sec=0.22,
        micro_gain_db=0.3,
        eq_chain=(
            "highpass=f=85,equalizer=f=180:t=q:w=1.1:g=1.0,"
            "equalizer=f=3200:t=q:w=1.0:g=2.8,equalizer=f=6000:t=q:w=1.2:g=1.8,lowpass=f=15000"
        ),
        description="Articulate tactical mechanism explanation with sharp consonant clarity.",
    ),
    "urgent_escalation": _profile(
        "urgent_escalation",
        omni_speed=1.16,
        atempo=1.19,
        gap_after_sec=0.05,
        micro_gain_db=0.8,
        eq_chain=(
            "highpass=f=95,equalizer=f=190:t=q:w=1.0:g=0.8,"
            "equalizer=f=3000:t=q:w=1.0:g=2.4,equalizer=f=6500:t=q:w=1.2:g=1.5,lowpass=f=15000"
        ),
        description="Rapid high-urgency escalation with tight inter-scene transitions.",
    ),
    "climax_heroic": _profile(
        "climax_heroic",
        omni_speed=1.12,
        atempo=1.18,
        gap_after_sec=0.10,
        micro_gain_db=1.5,
        eq_chain=(
            "highpass=f=80,equalizer=f=175:t=q:w=1.1:g=2.6,"
            "equalizer=f=3400:t=q:w=1.0:g=3.0,equalizer=f=7000:t=q:w=1.2:g=2.0,lowpass=f=15500"
        ),
        description="Full-bodied climax delivery with chest warmth, presence boost, and air.",
    ),
    "reflective_lesson": _profile(
        "reflective_lesson",
        omni_speed=0.99,
        atempo=1.13,
        gap_after_sec=0.32,
        micro_gain_db=-0.4,
        eq_chain=(
            "highpass=f=75,equalizer=f=165:t=q:w=1.1:g=2.0,"
            "equalizer=f=2800:t=q:w=1.0:g=1.5,lowpass=f=13500"
        ),
        description="Measured, lingering reflective takeaway cadence.",
    ),
}


DYNAMIC_MICRO_GAIN_DB: dict[str, float] = {
    "tense_whisper": -2.6,
    "narrative_cinema": 0.0,
    "tactical_breakdown": 0.3,
    "urgent_escalation": 1.4,
    "climax_heroic": 2.2,
    "reflective_lesson": -0.4,
}


def resolve_delivery_profile(mode: str | None) -> dict[str, Any]:
    """Return a copy of the prosody delivery profile with widened cinema dynamic contrast."""
    key = (mode or "").strip()
    if key not in VOICE_DELIVERY_PROFILES:
        key = DEFAULT_DELIVERY_MODE
    prof = dict(VOICE_DELIVERY_PROFILES[key])
    if key in DYNAMIC_MICRO_GAIN_DB:
        prof["micro_gain_db"] = DYNAMIC_MICRO_GAIN_DB[key]
    return prof


def split_text_with_pauses(text: str) -> list[dict[str, Any]]:
    """Parse `[pause:Xms]` / `[pause:Xs]` tags into ordered speech and pause items.

    Uses the same numeric/unit rule as `script_cadence_checker.PAUSE_RE` (`unit == 'ms'`
    or bare numbers `> 10` become `val / 1000.0` seconds). Whitespace-only speech spans
    are skipped, and adjacent pauses with no intervening speech are merged cleanly.
    """
    if not text or not str(text).strip():
        return []

    src = str(text)
    items: list[dict[str, Any]] = []
    cursor = 0

    for match in PAUSE_RE.finditer(src):
        speech = src[cursor:match.start()].strip()
        if speech:
            items.append({"type": "speech", "text": speech})

        val = float(match.group(1))
        unit = (match.group(2) or "").lower()
        sec = val / 1000.0 if (unit == "ms" or (not unit and val > 10)) else val
        sec = round(sec, 6)
        if sec > 0:
            if items and items[-1]["type"] == "pause":
                items[-1]["seconds"] = round(items[-1]["seconds"] + sec, 6)
            else:
                items.append({"type": "pause", "seconds": sec})
        cursor = match.end()

    tail_speech = src[cursor:].strip()
    if tail_speech:
        items.append({"type": "speech", "text": tail_speech})

    return items


__all__ = [
    "BASELINE_LUFS",
    "DEFAULT_DELIVERY_MODE",
    "DYNAMIC_MICRO_GAIN_DB",
    "PAUSE_RE",
    "VOICE_DELIVERY_PROFILES",
    "resolve_delivery_profile",
    "split_text_with_pauses",
]
