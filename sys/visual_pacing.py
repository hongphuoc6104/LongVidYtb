"""Measured full-frame storyboard acceptance, independent of rendering providers."""
from __future__ import annotations

import math
from typing import Any

OPENING_WINDOW_SECONDS = 12.5
FIRST_WINDOW_SECONDS = 5.0
BODY_MIN_HOLD_SECONDS = 0.83
BODY_MAX_HOLD_SECONDS = 3.80
MAX_AVERAGE_HOLD_SECONDS = 3.0


def check_see_say_beat_density(
    scenes: list[dict[str, Any]],
    format_profile: str | None = None,
) -> list[str]:
    """Validate a measured renderer timeline; image starts use half-open windows.

    Count unique full-frame beat starts across scene boundaries. This is an
    acceptance gate for the full-frame production profile, not old job migration.
    """
    total_beats = sum(len(sc.get('images', [])) for sc in scenes)
    total_duration = scenes[-1]['end'] - scenes[0]['start'] if scenes and 'end' in scenes[-1] and 'start' in scenes[0] else 0.0
    is_long_explainer = (
        format_profile == 'long_16x9'
        or total_duration > 120.0
        or (total_beats > 0 and total_duration / total_beats > 2.8)
    )

    max_average = 6.0 if is_long_explainer else MAX_AVERAGE_HOLD_SECONDS
    body_max = 8.5 if is_long_explainer else BODY_MAX_HOLD_SECONDS
    body_min = BODY_MIN_HOLD_SECONDS
    min_first_five = 2 if is_long_explainer else 3
    min_opening = 3 if is_long_explainer else 6

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
        if (end - start) / len(beats) > max_average:
            errors.append(f"LOW_VISUAL_BEAT_DENSITY: {scene['id']} averages more than {max_average}s per beat")
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
            if absolute >= 15 and not body_min <= hold <= body_max:
                errors.append(f"VISUAL_HOLD_INVALID: {scene['id']}/{beat['id']} holds {hold:.3f}s")
    first_five = sum(at < FIRST_WINDOW_SECONDS for at in starts)
    opening = sum(at < OPENING_WINDOW_SECONDS for at in starts)
    if not min_first_five <= first_five <= 5:
        errors.append(f"OPENING_VISUAL_DENSITY: expected {min_first_five}–5 starts in [0,5), got {first_five}")
    if not min_opening <= opening <= 10:
        errors.append(f"OPENING_VISUAL_DENSITY: expected {min_opening}–10 starts in [0,12.5), got {opening}")
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
        if target == beat['at']:
            return
        beat.setdefault('original_at', beat['at'])
        beat['at'] = round(target, 4)

    if start == 0.0 and count >= 3 and beats[2]['at'] >= 5.0:
        target = min(4.8, beats[1]['at'] + (5.0 - beats[1]['at']) * .75)
        if target > beats[1]['at'] + .5:
            move(2, target)
    if (
        start == 0.0
        and count > 10
        and beats[10]['at'] < OPENING_WINDOW_SECONDS
        and duration > OPENING_WINDOW_SECONDS + .1
        and (count == 11 or OPENING_WINDOW_SECONDS + .05 <= beats[11]['at'] - .5)
    ):
        move(10, round(OPENING_WINDOW_SECONDS + .05, 4))
    if end <= 15:
        return
    avg_hold = duration / count
    minimum, maximum = .85, max(3.75, avg_hold * 1.35)
    for _ in range(15):
        for index in range(count - 1, 0, -1):
            following = beats[index + 1]['at'] if index + 1 < count else duration
            hold = following - beats[index]['at']
            target = following - minimum if hold < minimum else following - maximum if hold > maximum else None
            if target is not None and target >= beats[index - 1]['at'] + minimum:
                move(index, target)
        for index in range(1, count):
            previous = beats[index - 1]['at']
            hold = beats[index]['at'] - previous
            target = previous + maximum if hold > maximum else previous + minimum if hold < minimum else None
            following = beats[index + 1]['at'] if index + 1 < count else duration
            if target is not None and target <= following - minimum:
                move(index, target)
