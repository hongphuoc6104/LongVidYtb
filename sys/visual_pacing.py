"""Measured full-frame storyboard acceptance, independent of rendering providers."""

from __future__ import annotations

import math
from typing import Any

OPENING_WINDOW_SECONDS = 12.5
FIRST_WINDOW_SECONDS = 5.0
BODY_MIN_HOLD_SECONDS = 0.83
BODY_MAX_HOLD_SECONDS = 3.80
MAX_AVERAGE_HOLD_SECONDS = 3.0


def check_see_say_beat_density(scenes: list[dict[str, Any]]) -> list[str]:
    """Validate a measured renderer timeline; image starts use half-open windows.

    Count unique full-frame beat starts across scene boundaries. This is an
    acceptance gate for the full-frame production profile, not old job migration.
    """
    errors: list[str] = []
    starts: list[float] = []
    previous_end = 0.0
    for scene in scenes:
        start, end = float(scene["start"]), float(scene["end"])
        if (
            not all(math.isfinite(value) for value in (start, end))
            or abs(start - previous_end) > 2 / 48000
            or end <= start
        ):
            errors.append(f"VISUAL_TIMELINE_INVALID: {scene['id']}")
            continue
        previous_end = end
        beats = scene.get("images", [])
        if not beats:
            errors.append(f"LOW_VISUAL_BEAT_DENSITY: {scene['id']} has no image beats")
            continue
        if (end - start) / len(beats) > MAX_AVERAGE_HOLD_SECONDS:
            errors.append(
                f"LOW_VISUAL_BEAT_DENSITY: {scene['id']} averages more than {MAX_AVERAGE_HOLD_SECONDS}s per beat"
            )
        last_at = -1.0
        for index, beat in enumerate(beats):
            at = float(beat["at"])
            if not math.isfinite(at) or not last_at < at < end - start or (index == 0 and at != 0):
                errors.append(f"VISUAL_BEAT_INVALID: {scene['id']}/{beat['id']}")
                continue
            last_at = at
            absolute = start + at
            starts.append(absolute)
            following = float(beats[index + 1]["at"]) if index + 1 < len(beats) else end - start
            hold = following - at
            if absolute >= 15 and not BODY_MIN_HOLD_SECONDS <= hold <= BODY_MAX_HOLD_SECONDS:
                errors.append(f"VISUAL_HOLD_INVALID: {scene['id']}/{beat['id']} holds {hold:.3f}s")
    first_five = sum(at < FIRST_WINDOW_SECONDS for at in starts)
    opening = sum(at < OPENING_WINDOW_SECONDS for at in starts)
    if not 3 <= first_five <= 5:
        errors.append(f"OPENING_VISUAL_DENSITY: expected 3–5 starts in [0,5), got {first_five}")
    if not 6 <= opening <= 10:
        errors.append(f"OPENING_VISUAL_DENSITY: expected 6–10 starts in [0,12.5), got {opening}")
    return errors


def smooth_interpolated_beats(beats: list[dict[str, Any]], start: float, end: float) -> None:
    """Improve estimated holds without moving measured acoustic anchors.

    Measured conflicts remain visible to the pacing validator. Original estimates
    are retained whenever a fallback beat is adjusted.
    """
    duration, count = end - start, len(beats)
    if count < 2:
        return

    def move(index: int, target: float) -> None:
        beat = beats[index]
        if beat.get("timing_method") != "narration_anchor_interpolated":
            return
        if target == beat["at"]:
            return
        beat.setdefault("original_at", beat["at"])
        beat["at"] = round(target, 4)

    if start == 0.0 and count >= 3 and beats[2]["at"] >= 5.0:
        target = min(4.8, beats[1]["at"] + (5.0 - beats[1]["at"]) * 0.75)
        if target > beats[1]["at"] + 0.5:
            move(2, target)
    if end <= 15:
        return
    minimum, maximum = 0.85, 3.75
    for _ in range(10):
        for index in range(count - 1, 0, -1):
            following = beats[index + 1]["at"] if index + 1 < count else duration
            hold = following - beats[index]["at"]
            target = following - minimum if hold < minimum else following - maximum if hold > maximum else None
            if target is not None and target >= beats[index - 1]["at"] + minimum:
                move(index, target)
        for index in range(1, count):
            previous = beats[index - 1]["at"]
            hold = beats[index]["at"] - previous
            target = previous + maximum if hold > maximum else previous + minimum if hold < minimum else None
            following = beats[index + 1]["at"] if index + 1 < count else duration
            if target is not None and target <= following - minimum:
                move(index, target)
