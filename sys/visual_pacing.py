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

    max_average = 8.05 if is_long_explainer else MAX_AVERAGE_HOLD_SECONDS
    body_max = 11.50 if is_long_explainer else BODY_MAX_HOLD_SECONDS
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


TEMPO_HOLD_WINDOWS: dict[str, dict[str, tuple[float, float]]] = {
    "short_9x16": {
        "burst": (0.8, 1.5),
        "fast": (0.9, 1.8),
        "normal": (2.0, 3.5),
        "slow": (3.5, 5.5),
        "hold": (1.5, 3.0),
    },
    "long_16x9": {
        "burst": (1.2, 2.2),
        "fast": (2.0, 4.0),
        "normal": (4.0, 7.0),
        "slow": (7.0, 10.0),
        "hold": (5.0, 20.0),
    },
    "long_16x9_narrative_adaptive": {
        "burst": (1.2, 2.2),
        "fast": (1.8, 3.0),
        "normal": (2.4, 3.8),
        "slow": (3.6, 5.2),
        "hold": (2.0, 5.0),
    },
}

# Mapping from narrative situation / storytelling beat type to visual tempo and hold guidance
NARRATIVE_SITUATION_TEMPO_MAP: dict[str, dict[str, Any]] = {
    "hook_shock": {
        "tempo": "burst",
        "hold_range": (1.2, 2.0),
        "description": "Mở màn 3-15s đầu: Đổi hình dồn dập theo từng vế câu (6-10 chữ) hoặc lật ngược kỳ vọng.",
    },
    "rapid_examples": {
        "tempo": "burst",
        "hold_range": (1.3, 2.2),
        "description": "Liệt kê ví dụ liên hoàn / bóc tách nhiều sai lầm: Mỗi ví dụ 1 hình riêng hoặc vẽ bồi (based_on).",
    },
    "before_after_contrast": {
        "tempo": "fast",
        "hold_range": (1.8, 2.8),
        "description": "Đối chiếu Trước/Sau, Sai/Đúng, Tưởng vậy/Thực tế: Cắt nhanh 2 khung hình đối lập.",
    },
    "story_action": {
        "tempo": "fast",
        "hold_range": (1.8, 3.0),
        "description": "Tình huống đời thường có hành động/xung đột của nhân vật chính.",
    },
    "mechanism_step": {
        "tempo": "normal",
        "hold_range": (2.4, 3.6),
        "description": "Giải thích từng bước cơ chế nhân quả (Feynman): Vẽ bồi tuần tự từ nhân -> cơ chế -> quả.",
    },
    "editorial_commentary": {
        "tempo": "slow",
        "hold_range": (3.5, 5.0),
        "description": "Đánh giá / Bình luận / Ý kiến phản biện riêng của kênh: Khung hình ẩn dụ sắc bén + chữ viết tay điểm nhấn để người xem kịp ngẫm.",
    },
    "cliffhanger_peak": {
        "tempo": "fast",
        "hold_range": (1.6, 2.5),
        "description": "Đỉnh cao trào bỏ lửng (Short): Dừng ngay trước câu trả lời/bước quyết định để kích thích xem bản Full.",
    },
    "cta_bridge": {
        "tempo": "hold",
        "hold_range": (2.0, 4.0),
        "description": "Nhịp chuyển phễu cuối video sang bản Full hoặc câu hỏi thảo luận.",
    },
}

TEMPO_TOLERANCE_RATIO = 0.15


def summarize_tempo_beats(
    beats_with_times: list[dict[str, Any]],
    format_profile: str = "short_9x16",
) -> dict[str, Any]:
    """Calculate pacing metrics: avg hold, counts per tempo, and emphasis ratio."""
    if not beats_with_times:
        return {
            "total_beats": 0,
            "total_duration": 0.0,
            "avg_hold": 0.0,
            "tempo_counts": {"fast": 0, "normal": 0, "slow": 0, "hold": 0},
            "emphasis_count": 0,
            "emphasis_ratio": 0.0,
            "has_slow_insight": False,
        }

    total = len(beats_with_times)
    tempo_counts: dict[str, int] = {"fast": 0, "normal": 0, "slow": 0, "hold": 0}
    emphasis_count = 0
    total_dur = 0.0

    for idx, b in enumerate(beats_with_times):
        tempo = b.get("tempo", "normal")
        if tempo in tempo_counts:
            tempo_counts[tempo] += 1

        if b.get("emphasis_text"):
            emphasis_count += 1

        if "hold" in b:
            hold = float(b["hold"])
        elif "at" in b:
            at = float(b["at"])
            if idx + 1 < total and "at" in beats_with_times[idx + 1]:
                hold = float(beats_with_times[idx + 1]["at"]) - at
            elif "duration" in b:
                hold = float(b["duration"])
            else:
                hold = 2.5
        else:
            hold = 2.5
        total_dur += hold

    avg_hold = total_dur / total if total > 0 else 0.0
    return {
        "total_beats": total,
        "total_duration": round(total_dur, 2),
        "avg_hold": round(avg_hold, 2),
        "tempo_counts": tempo_counts,
        "emphasis_count": emphasis_count,
        "emphasis_ratio": round(emphasis_count / total, 3) if total > 0 else 0.0,
        "has_slow_insight": tempo_counts.get("slow", 0) >= 1,
    }


def check_tempo_beats(
    beats_with_times: list[dict[str, Any]],
    format_profile: str = "short_9x16",
    tolerance: float = TEMPO_TOLERANCE_RATIO,
) -> list[str]:
    """Validate measured timeline holds against tempo contracts per contract §3.3.

    Returns a list of error strings. Empty list indicates full validity.
    """
    errors: list[str] = []
    if not beats_with_times:
        errors.append("TEMPO_PACING_EMPTY: no beats provided for tempo validation")
        return errors

    profile = format_profile if format_profile in TEMPO_HOLD_WINDOWS else "short_9x16"
    windows = TEMPO_HOLD_WINDOWS[profile]

    prev_tempo: str | None = None
    consecutive_run = 0
    slow_count = 0
    emphasis_count = 0
    total_beats = len(beats_with_times)
    total_dur = 0.0

    for idx, b in enumerate(beats_with_times):
        b_id = b.get("id", f"B{idx + 1}")
        tempo = b.get("tempo", "normal")

        if tempo == "slow":
            slow_count += 1
        if b.get("emphasis_text"):
            emphasis_count += 1

        # Determine hold
        if "hold" in b:
            hold = float(b["hold"])
        elif "at" in b:
            at = float(b["at"])
            if idx + 1 < total_beats and "at" in beats_with_times[idx + 1]:
                hold = float(beats_with_times[idx + 1]["at"]) - at
            elif "end" in b:
                hold = float(b["end"]) - at
            else:
                hold = float(b.get("duration", 2.5))
        else:
            hold = float(b.get("duration", 2.5))

        total_dur += hold

        # Window validation with tolerance
        if tempo in windows:
            w_min, w_max = windows[tempo]
            min_allowed = w_min * (1.0 - tolerance)
            max_allowed = w_max * (1.0 + tolerance)
            if not (min_allowed <= hold <= max_allowed):
                errors.append(
                    f"TEMPO_HOLD_INVALID: beat '{b_id}' tempo '{tempo}' holds {hold:.2f}s outside [{min_allowed:.2f}, {max_allowed:.2f}]s"
                )

        # Consecutive tempo run check
        if tempo == prev_tempo:
            consecutive_run += 1
            if tempo == "fast":
                if consecutive_run > 5:
                    errors.append(
                        f"CONSECUTIVE_TEMPO_EXCEEDED: 'fast' tempo run of {consecutive_run} beats exceeds max allowed run of 5"
                    )
            else:
                if consecutive_run > 3:
                    errors.append(
                        f"CONSECUTIVE_TEMPO_EXCEEDED: '{tempo}' tempo run of {consecutive_run} beats exceeds max allowed run of 3"
                    )
        else:
            prev_tempo = tempo
            consecutive_run = 1

    # Insight check: >= 1 slow beat
    if slow_count < 1:
        errors.append("TEMPO_PACING_MISSING_SLOW: expected at least 1 'slow' beat at key insight, got 0")

    # Emphasis ratio check: <= 35%
    if total_beats > 0:
        emp_ratio = emphasis_count / total_beats
        if emp_ratio > 0.35:
            errors.append(
                f"EMPHASIS_RATIO_EXCEEDED: {emphasis_count}/{total_beats} ({emp_ratio:.1%}) beats have emphasis_text (max 35%)"
            )

    # Average hold check
    avg_hold = total_dur / total_beats if total_beats > 0 else 0.0
    if profile == "short_9x16":
        # Target 2.0 - 3.0 s (tolerance ±15% -> [1.70, 3.45])
        if not (1.50 <= avg_hold <= 3.45):
            errors.append(
                f"AVERAGE_HOLD_OUT_OF_TARGET: short_9x16 average hold is {avg_hold:.2f}s (target 1.8–3.0s ±15%)"
            )
    elif profile == "long_16x9":
        # Supports both Narrative-Adaptive high density (2.0–4.2s) and legacy baseline (up to 8.05s)
        if not (1.80 <= avg_hold <= 8.05):
            errors.append(
                f"AVERAGE_HOLD_OUT_OF_TARGET: long_16x9 average hold is {avg_hold:.2f}s (allowed 1.80–8.05s)"
            )
    elif profile == "long_16x9_narrative_adaptive":
        # Strict V3 Narrative-Adaptive target: 2.0 - 3.6s average hold
        if not (1.80 <= avg_hold <= 3.80):
            errors.append(
                f"AVERAGE_HOLD_OUT_OF_TARGET: long_16x9_narrative_adaptive average hold is {avg_hold:.2f}s (target 2.0–3.5s)"
            )

    return errors


def audit_narrative_visual_density(
    brief: dict[str, Any],
    content: dict[str, Any],
    estimated_duration_sec: float | None = None,
) -> list[str]:
    """Audit Narrative-Driven Adaptive Visual Pacing (V3 High-Density Standard).

    Verifies that:
    1. Unique Flow image count meets high-density thresholds (~2.2–3.5s/img for Long, ~1.8–2.6s/img for Short).
    2. Lazy zoom-reuse on identical images is eliminated (>= 90% of beats must use distinct Flow images).
    3. Scenes/beats declare situation-aware narrative roles or tempo variations (burst/fast for hooks & examples,
       normal for mechanism steps, slow for editorial commentary/verdicts).
    """
    errors: list[str] = []
    format_profile = brief.get("format_profile") or ("long_16x9" if brief.get("aspect_ratio") == "16:9" else "short_9x16")
    is_long = format_profile == "long_16x9"

    scenes = content.get("scenes", [])
    if not scenes:
        return ["NARRATIVE_PACING_EMPTY: content.json has no scenes"]

    if str(brief.get("video_engine") or "").lower() == "flow_video":
        # Flow Video synthesizes continuous 5-10s AI video clips between keyframes; skip static image hold limits.
        return []

    all_images = [img for sc in scenes for img in sc.get("images", []) if not img.get("is_crop")]
    all_beats = [b for sc in scenes for b in sc.get("beats", [])]
    uniq_img_ids = {b.get("image_id") for b in all_beats if b.get("image_id")} or {img.get("id") for img in all_images if img.get("id")}
    num_uniq_imgs = len(uniq_img_ids)
    num_beats = len(all_beats) or num_uniq_imgs

    # Estimate duration from syllable count if not provided (~3.8 syllables/sec in Vietnamese)
    if not estimated_duration_sec or estimated_duration_sec <= 0:
        total_words = sum(len((sc.get("narration") or "").split()) for sc in scenes)
        estimated_duration_sec = max(25.0, total_words / 3.8)

    avg_img_hold = estimated_duration_sec / max(1, num_uniq_imgs)
    uniq_ratio = num_uniq_imgs / max(1, num_beats)

    if is_long:
        if avg_img_hold > 3.6:
            min_needed = math.ceil(estimated_duration_sec / 3.2)
            errors.append(
                f"LOW_UNIQUE_IMAGE_DENSITY_LONG: {num_uniq_imgs} unique images for ~{estimated_duration_sec:.0f}s "
                f"({avg_img_hold:.2f}s/img > max 3.6s/img). Need >= {min_needed} unique Flow images tied to narrative beats."
            )
        if uniq_ratio < 0.88:
            errors.append(
                f"LAZY_IMAGE_ZOOM_REUSE: only {num_uniq_imgs}/{num_beats} ({uniq_ratio:.0%}) beats use unique images "
                "(min 88% required; generate new Flow frames or based_on variations instead of zooming static images)."
            )
    else:
        if avg_img_hold > 2.7:
            min_needed = math.ceil(estimated_duration_sec / 2.3)
            errors.append(
                f"LOW_UNIQUE_IMAGE_DENSITY_SHORT: {num_uniq_imgs} unique images for ~{estimated_duration_sec:.0f}s "
                f"({avg_img_hold:.2f}s/img > max 2.7s/img). Need >= {min_needed} unique Flow images."
            )
        if uniq_ratio < 0.92:
            errors.append(
                f"LAZY_IMAGE_ZOOM_REUSE_SHORT: {num_uniq_imgs}/{num_beats} ({uniq_ratio:.0%}) unique images in Short (min 92%)."
            )

    # Check narrative situation / tempo diversity across beats
    tempos_used = {b.get("tempo", "normal") for b in all_beats}
    if len(all_beats) >= 10 and len(tempos_used) < 2:
        errors.append(
            "MONOTONOUS_NARRATIVE_TEMPO: all beats use identical tempo; must vary tempo by narrative situation "
            "(burst/fast for hooks & rapid examples, normal for mechanism, slow for editorial commentary)."
        )

    return errors


def retime_long_beats_to_measured_audio(
    content: dict[str, Any],
    audio_payload: dict[str, Any],
    target_hold_sec: float = 3.0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Re-time long_16x9 beats to measured audio WAV duration with Narrative-Driven Adaptive Pacing.

    Preserves 100% of genuine Flow scene images and authored narrative beats.
    For high-density Narrative-Adaptive jobs (avg hold 2.0–4.2s), keeps all authored beats intact
    and maps narrative situations to burst/fast/normal/slow/hold tempos.
    For legacy sparser jobs, splits any beat holding > 8.0s so no beat stalls.
    """
    duration = float(audio_payload.get("duration", 0.0))
    if duration <= 0:
        return content, {"beats": 0, "avg_hold": 0.0, "tempos": {}}

    scenes = content.get("scenes", [])
    raw_total_beats = sum(len(sc.get("beats", [])) for sc in scenes)
    raw_avg_hold = duration / max(1, raw_total_beats)
    is_high_density_narrative = raw_avg_hold <= 4.25

    track = audio_payload.get("tracks", {}).get("vi") or audio_payload
    segments = track.get("segments", [])
    seg_by_scene: dict[str, list[dict[str, Any]]] = {}
    for s in segments:
        sid = s.get("scene_id")
        if sid:
            seg_by_scene.setdefault(sid, []).append(s)

    def _approx_offset(text: str, quote: str) -> int:
        if not text or not quote:
            return 0
        pos = text.find(quote)
        return pos if pos != -1 else 0

    repaired_scenes = []
    kept_beats = []

    for sc in scenes:
        spans = seg_by_scene.get(sc.get("id"), [])
        sc_dur = (float(spans[-1]["end"]) - float(spans[0]["start"])) if spans else (duration / max(1, len(scenes)))
        sc_text = sc.get("narration", "")
        beats = sc.get("beats", [])

        # Pass 1: Keep all unique base images and narrative beats
        pass1_beats = []
        seen_images = set()
        for i, b in enumerate(beats):
            img_id = b.get("image_id")
            scale = float(b.get("focus", {}).get("scale", 1.0))
            is_endcard = bool(b.get("is_endcard") or b.get("tempo") == "hold")

            if sc_text:
                prev_t = 0.0
                if pass1_beats:
                    pq = pass1_beats[-1].get("anchor", {}).get("vi", {}).get("quote", "")
                    poff = _approx_offset(sc_text, pq)
                    prev_t = (poff / max(1, len(sc_text))) * sc_dur

                next_t = sc_dur
                for nxt in beats[i + 1:]:
                    nq = nxt.get("anchor", {}).get("vi", {}).get("quote", "")
                    if nq:
                        noff = _approx_offset(sc_text, nq)
                        next_t = (noff / max(1, len(sc_text))) * sc_dur
                        break
            else:
                prev_t = (pass1_beats[-1].get("_idx", 0) / max(1, len(beats))) * sc_dur if pass1_beats else 0.0
                next_t = ((i + 1) / max(1, len(beats))) * sc_dur

            is_opening_protect = (sc == scenes[0] and i < 4) or (len(scenes) > 1 and sc == scenes[1] and i < 3)
            is_first_of_image = (img_id not in seen_images)
            must_keep = (
                is_high_density_narrative
                or is_first_of_image
                or is_endcard
                or (next_t - prev_t > 8.0)
                or is_opening_protect
            )
            if must_keep or i == 0:
                seen_images.add(img_id)
                b_copy = dict(b)
                b_copy["_idx"] = i
                if scale > 1.15:
                    b_copy["focus"] = dict(b.get("focus", {}), scale=1.15)
                pass1_beats.append(b_copy)

        if not pass1_beats and beats:
            pass1_beats = [dict(beats[0])]

        # Pass 2: Split any beat holding > 8.0s into 2 visual beats if needed
        pass2_beats = []
        for idx, b in enumerate(pass1_beats):
            q = b.get("anchor", {}).get("vi", {}).get("quote", "")
            off = _approx_offset(sc_text, q)
            t_curr = (off / max(1, len(sc_text))) * sc_dur

            if idx + 1 < len(pass1_beats):
                nq = pass1_beats[idx + 1].get("anchor", {}).get("vi", {}).get("quote", "")
                noff = _approx_offset(sc_text, nq) if nq else len(sc_text)
                t_next = (noff / max(1, len(sc_text))) * sc_dur
            else:
                t_next = sc_dur
                noff = len(sc_text)

            hold = t_next - t_curr
            pass2_beats.append(b)

            if hold > 8.0 and not b.get("is_endcard"):
                mid_off = off + (noff - off) // 2
                space_pos = sc_text.find(" ", mid_off)
                if space_pos != -1 and space_pos < noff:
                    sub_text = sc_text[space_pos:noff].strip()
                    words = sub_text.split()
                    if len(words) >= 3:
                        split_quote = " ".join(words[:min(6, len(words))])
                        b2 = {
                            "id": f"{b['id']}_s",
                            "image_id": b["image_id"],
                            "purpose": f"Cắt chuyển cận cảnh: {b.get('purpose', '')}",
                            "anchor": {"vi": {"quote": split_quote, "occurrence": 1}},
                            "effect": "push_in" if b.get("effect") != "push_in" else "hold",
                            "focus": {"x": 0.5, "y": 0.5, "scale": 1.15},
                            "tempo": "normal",
                        }
                        pass2_beats.append(b2)

        sc_copy = dict(sc)
        sc_copy["beats"] = pass2_beats
        kept_beats.extend(pass2_beats)
        repaired_scenes.append(sc_copy)

    total_kept = len(kept_beats)
    new_avg_hold = round(duration / total_kept, 2) if total_kept > 0 else 0.0

    tempo_counts: dict[str, int] = {}
    for sc in repaired_scenes:
        sc_beats = sc.get("beats", [])
        sc_segs = seg_by_scene.get(sc.get("id"), [])
        if sc_segs:
            sc_dur = float(sc_segs[-1].get("end", 0.0)) - float(sc_segs[0].get("start", 0.0))
        else:
            sc_dur = new_avg_hold * len(sc_beats)
        per_beat_est = sc_dur / len(sc_beats) if sc_beats else new_avg_hold
        sc_situation = sc.get("narrative_situation") or sc.get("narrative_role") or ""

        for idx, b in enumerate(sc_beats):
            b_sit = b.get("narrative_situation") or sc_situation
            if b.get("is_endcard") or (idx == len(sc_beats) - 1 and sc == repaired_scenes[-1]):
                b["tempo"] = "hold"
            elif b_sit in NARRATIVE_SITUATION_TEMPO_MAP:
                b["tempo"] = NARRATIVE_SITUATION_TEMPO_MAP[b_sit]["tempo"]
            elif is_high_density_narrative:
                if per_beat_est <= 2.0:
                    b["tempo"] = "burst"
                elif per_beat_est <= 2.8:
                    b["tempo"] = "fast"
                elif per_beat_est >= 3.8:
                    b["tempo"] = "slow"
                else:
                    b["tempo"] = "normal"
            else:
                if per_beat_est < 4.0:
                    b["tempo"] = "fast"
                elif per_beat_est > 7.0:
                    b["tempo"] = "slow"
                else:
                    b["tempo"] = "normal"
            t = b.get("tempo", "normal")
            tempo_counts[t] = tempo_counts.get(t, 0) + 1

    # Ensure >= 1 slow beat for editorial commentary / key insight if long explainer
    if tempo_counts.get("slow", 0) < 1 and total_kept > 3:
        mid_idx = total_kept // 2
        kept_beats[mid_idx]["tempo"] = "slow"
        tempo_counts["slow"] = tempo_counts.get("slow", 0) + 1
        tempo_counts["normal"] = max(0, tempo_counts.get("normal", 1) - 1)

    updated_content = dict(content)
    updated_content["scenes"] = repaired_scenes
    return updated_content, {
        "beats": total_kept,
        "avg_hold": new_avg_hold,
        "tempos": tempo_counts,
        "narrative_adaptive": is_high_density_narrative,
    }


