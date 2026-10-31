"""Tests for tempo-aware visual hold validation (contract §3.3)."""

from __future__ import annotations

from visual_pacing import (
    check_tempo_beats,
    summarize_tempo_beats,
)


def test_valid_short_tempo_beats_passes():
    """Realistic short_9x16 visual beats: avg hold ~2.4s, >=1 slow beat, <=35% emphasis."""
    beats = [
        {"id": "B01", "tempo": "fast", "hold": 1.2, "emphasis_text": "2 GIỜ SÁNG"},
        {"id": "B02", "tempo": "fast", "hold": 1.4},
        {"id": "B03", "tempo": "normal", "hold": 2.6},
        {"id": "B04", "tempo": "normal", "hold": 2.8},
        {"id": "B05", "tempo": "slow", "hold": 4.2},  # Key insight
        {"id": "B06", "tempo": "fast", "hold": 1.5},
        {"id": "B07", "tempo": "normal", "hold": 2.5},
        {"id": "B08", "tempo": "hold", "hold": 2.0},  # Endcard
    ]
    errors = check_tempo_beats(beats, format_profile="short_9x16")
    assert errors == [], f"Expected clean pacing pass, got: {errors}"

    metrics = summarize_tempo_beats(beats, format_profile="short_9x16")
    assert metrics["total_beats"] == 8
    assert 2.0 <= metrics["avg_hold"] <= 3.0
    assert metrics["has_slow_insight"] is True
    assert metrics["emphasis_count"] == 1
    assert metrics["emphasis_ratio"] <= 0.35
    assert metrics["tempo_counts"]["fast"] == 3
    assert metrics["tempo_counts"]["slow"] == 1


def test_valid_long_tempo_beats_passes():
    """Realistic long_16x9 visual beats within windows and avg hold ~5.5s."""
    beats = [
        {"id": "B01", "tempo": "fast", "hold": 3.0},
        {"id": "B02", "tempo": "normal", "hold": 5.5},
        {"id": "B03", "tempo": "normal", "hold": 6.0},
        {"id": "B04", "tempo": "slow", "hold": 8.0},  # Key insight
        {"id": "B05", "tempo": "fast", "hold": 3.5},
        {"id": "B06", "tempo": "normal", "hold": 5.0},
        {"id": "B07", "tempo": "hold", "hold": 7.5},
    ]
    errors = check_tempo_beats(beats, format_profile="long_16x9")
    assert errors == [], f"Expected clean long pacing pass, got: {errors}"

    metrics = summarize_tempo_beats(beats, format_profile="long_16x9")
    assert 4.5 <= metrics["avg_hold"] <= 7.5
    assert metrics["has_slow_insight"] is True


def test_tempo_hold_tolerance_allows_15_percent():
    """Test ±15% tolerance: fast in short_9x16 is [0.9, 1.8], with tolerance [0.765, 2.07]."""
    # 2.0s is inside tolerance (<= 2.07s)
    beats = [
        {"id": "B01", "tempo": "fast", "hold": 2.0},
        {"id": "B02", "tempo": "normal", "hold": 2.5},
        {"id": "B03", "tempo": "slow", "hold": 4.0},
        {"id": "B04", "tempo": "hold", "hold": 2.0},
    ]
    errors = check_tempo_beats(beats, format_profile="short_9x16")
    assert not any("TEMPO_HOLD_INVALID" in err for err in errors)

    # 2.3s is outside tolerance (> 2.07s)
    beats_bad = [
        {"id": "B01", "tempo": "fast", "hold": 2.3},
        {"id": "B02", "tempo": "normal", "hold": 2.5},
        {"id": "B03", "tempo": "slow", "hold": 4.0},
        {"id": "B04", "tempo": "hold", "hold": 2.0},
    ]
    errors_bad = check_tempo_beats(beats_bad, format_profile="short_9x16")
    assert any("TEMPO_HOLD_INVALID" in err for err in errors_bad)


def test_consecutive_tempo_run_detection():
    # 4 consecutive normal beats exceeds max allowed run of 3
    beats = [
        {"id": "B01", "tempo": "normal", "hold": 2.5},
        {"id": "B02", "tempo": "normal", "hold": 2.5},
        {"id": "B03", "tempo": "normal", "hold": 2.5},
        {"id": "B04", "tempo": "normal", "hold": 2.5},
        {"id": "B05", "tempo": "slow", "hold": 4.0},
    ]
    errors = check_tempo_beats(beats, format_profile="short_9x16")
    assert any("CONSECUTIVE_TEMPO_EXCEEDED" in err for err in errors)

    # Fast run of 5 is allowed; run of 6 is rejected
    beats_fast_6 = [
        {"id": f"B{i}", "tempo": "fast", "hold": 1.2} for i in range(1, 7)
    ] + [{"id": "B07", "tempo": "slow", "hold": 4.0}]
    errors_fast = check_tempo_beats(beats_fast_6, format_profile="short_9x16")
    assert any("CONSECUTIVE_TEMPO_EXCEEDED" in err for err in errors_fast)


def test_missing_slow_insight_beat_detected():
    beats = [
        {"id": "B01", "tempo": "fast", "hold": 1.2},
        {"id": "B02", "tempo": "normal", "hold": 2.5},
        {"id": "B03", "tempo": "hold", "hold": 2.0},
    ]
    errors = check_tempo_beats(beats, format_profile="short_9x16")
    assert any("TEMPO_PACING_MISSING_SLOW" in err for err in errors)


def test_emphasis_ratio_exceeded():
    beats = [
        {"id": "B01", "tempo": "fast", "hold": 1.2, "emphasis_text": "TEXT 1"},
        {"id": "B02", "tempo": "normal", "hold": 2.5, "emphasis_text": "TEXT 2"},
        {"id": "B03", "tempo": "slow", "hold": 4.0},
    ]
    # 2/3 = 66.7% > 35%
    errors = check_tempo_beats(beats, format_profile="short_9x16")
    assert any("EMPHASIS_RATIO_EXCEEDED" in err for err in errors)


def test_retime_long_beats_to_measured_audio_satisfies_pacing():
    from visual_pacing import retime_long_beats_to_measured_audio

    # 16 scenes, total 80 beats (48 base + 32 crops), duration 280.84s
    scenes = []
    for s_idx in range(1, 17):
        sc_beats = []
        for b_idx in range(1, 6):
            is_crop = (b_idx in (3, 5))
            sc_beats.append({
                "id": f"SC{s_idx:02d}_B{b_idx}",
                "image_id": f"SC{s_idx:02d}_L0{1 if b_idx <= 2 else 2}",
                "tempo": "normal",
                "focus": {"x": 0.5, "y": 0.5, "scale": 1.35 if is_crop else 1.0},
            })
        scenes.append({"id": f"SC{s_idx:02d}", "beats": sc_beats})

    content = {"scenes": scenes}
    audio_payload = {"duration": 280.84}

    updated_content, meta = retime_long_beats_to_measured_audio(content, audio_payload)
    assert 4.25 <= meta["avg_hold"] <= 8.05
    assert meta["tempos"].get("slow", 0) >= 1

    all_beats = [b for sc in updated_content["scenes"] for b in sc["beats"]]
    assert len(all_beats) == meta["beats"]

