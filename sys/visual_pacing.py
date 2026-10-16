"""Measured full-frame storyboard acceptance, independent of rendering providers."""
from __future__ import annotations

import math
from typing import Any

OPENING_WINDOW_SECONDS = 12.5
FIRST_WINDOW_SECONDS = 5.0
BODY_MIN_HOLD_SECONDS = 0.83
BODY_MAX_HOLD_SECONDS = 3.80
MAX_AVERAGE_HOLD_SECONDS = 2.8


def check_see_say_beat_density(scenes: list[dict[str, Any]]) -> list[str]:
    """Validate a measured renderer timeline; image starts use half-open windows.

    Count unique full-frame beat starts across scene boundaries. This is an
    acceptance gate for the full-frame production profile, not old job migration.
    """
    errors: list[str] = []
    starts: list[float] = []
    previous_end = 0.0
    for scene in scenes:
        start, end = float(scene['start']), float(scene['end'])
        if not all(math.isfinite(value) for value in (start, end)) or abs(start - previous_end) > 2 / 48000 or end <= start:
            errors.append(f"VISUAL_TIMELINE_INVALID: {scene['id']}")
            continue
        previous_end = end
        beats = scene.get('images', [])
        if not beats:
            errors.append(f"LOW_VISUAL_BEAT_DENSITY: {scene['id']} has no image beats")
            continue
        if (end - start) / len(beats) > MAX_AVERAGE_HOLD_SECONDS:
            errors.append(f"LOW_VISUAL_BEAT_DENSITY: {scene['id']} averages more than 2.8s per beat")
        last_at = -1.0
        for index, beat in enumerate(beats):
            at = float(beat['at'])
            if not math.isfinite(at) or not last_at < at < end - start or (index == 0 and at != 0):
                errors.append(f"VISUAL_BEAT_INVALID: {scene['id']}/{beat['id']}")
                continue
            last_at = at
            absolute = start + at
            starts.append(absolute)
            following = float(beats[index + 1]['at']) if index + 1 < len(beats) else end - start
            hold = following - at
            if absolute >= 15 and not BODY_MIN_HOLD_SECONDS <= hold <= BODY_MAX_HOLD_SECONDS:
                errors.append(f"VISUAL_HOLD_INVALID: {scene['id']}/{beat['id']} holds {hold:.3f}s")
    first_five = sum(at < FIRST_WINDOW_SECONDS for at in starts)
    opening = sum(at < OPENING_WINDOW_SECONDS for at in starts)
    if first_five != 4:
        errors.append(f"OPENING_VISUAL_DENSITY: expected 4 starts in [0,5), got {first_five}")
    if not 8 <= opening <= 9:
        errors.append(f"OPENING_VISUAL_DENSITY: expected 8–9 starts in [0,12.5), got {opening}")
    return errors
