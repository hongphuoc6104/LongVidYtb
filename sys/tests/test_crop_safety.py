"""Video Pilot — Tests for Crop-Safety Engine Module.

Reproduces and validates:
(a) Flow-native hand-lettering clipping defects (tui_tien / ua_sao_vay).
(b) Primary-subject head slicing defects (ai_binh_dan).
Also verifies:
- Visible rect computation with BASE_OVERSCAN (1.045).
- Motion visible rects at start and end of camera moves.
- Lettering contain vs exclude rules.
- Primary-subject head safe-zone heuristic.
- Pre-render validator gate and error reporting.
- Graceful degradation to full frame push-in.
"""

from __future__ import annotations

import pytest
from crop_safety import (
    BASE_OVERSCAN,
    Rect,
    adjust_beat_crop,
    check_beat_crop_safety,
    compute_motion_visible_rects,
    compute_visible_rect,
    enforce_scenes_crop_safety,
    validate_scenes_crop_safety,
)


def test_rect_relationships():
    """Verify Rect contains, intersects, and relationship_with calculations."""
    r_full = Rect(0.0, 0.0, 1.0, 1.0)
    r_sub = Rect(0.2, 0.2, 0.8, 0.8)
    r_outside = Rect(0.85, 0.85, 0.95, 0.95)
    r_partial = Rect(0.7, 0.7, 0.9, 0.9)

    assert r_full.contains(r_sub)
    assert not r_sub.contains(r_full)
    assert r_sub.relationship_with(r_outside) == "excluded"
    assert r_sub.relationship_with(r_partial) == "partial"
    assert r_full.relationship_with(r_sub) == "contained"


def test_compute_visible_rect_matches_remotion_transform():
    """Verify physical image visible bounds under Remotion CSS scale and overscan."""
    # Scale = 1.0: visible rect is shrunk by 1 / 1.045 = 0.9569 (overscan)
    v1 = compute_visible_rect(0.5, 0.5, 1.0, base_overscan=BASE_OVERSCAN)
    assert v1.x1 == pytest.approx(0.5 * (1.0 - 1.0 / 1.045), abs=1e-4)
    assert v1.x2 == pytest.approx(0.5 + 0.5 / 1.045, abs=1e-4)

    # Scale = 2.0: visible rect width is 1 / (2.0 * 1.045) = 0.47847
    v2 = compute_visible_rect(0.5, 0.5, 2.0, base_overscan=BASE_OVERSCAN)
    assert v2.width == pytest.approx(1.0 / (2.0 * 1.045), abs=1e-4)

    # Origin at (0, 0): visible min should be 0.0
    v_topleft = compute_visible_rect(0.0, 0.0, 1.5, base_overscan=BASE_OVERSCAN)
    assert v_topleft.x1 == 0.0
    assert v_topleft.y1 == 0.0


def test_compute_motion_visible_rects_bounds():
    """Verify visible rects are evaluated at both start and end of camera motion."""
    focus = {"x": 0.5, "y": 0.5, "scale": 1.3}
    # Static hold: start and end rects must be identical
    v_start, v_end = compute_motion_visible_rects(focus, camera_motion="hold", duration=3.0)
    assert v_start == v_end

    # Push-in motion on full-frame beat: scale increases from start to end, visible rect shrinks
    focus_full = {"x": 0.5, "y": 0.5, "scale": 1.0}
    v_start_move, v_end_move = compute_motion_visible_rects(focus_full, camera_motion="push_in", duration=4.0)
    assert v_start_move.width > v_end_move.width
    assert v_start_move.height > v_end_move.height


def test_reproduce_defect_a_lettering_clipped_at_top():
    """Defect (a) reproduction: focus crop cuts lettering top (e.g. tui_tien SC01_B2)."""
    # Author authored focus y=0.35 with scale=1.35 on a lettered source
    beat = {
        "id": "SC01_B2",
        "image_id": "SC01_V01",
        "focus": {"x": 0.5, "y": 0.35, "scale": 1.35},
        "emphasis_text": "35 NGHÌN",
    }
    violations = check_beat_crop_safety(beat)
    assert len(violations) == 1
    assert violations[0].rule == "LETTERING_CLIPPED"
    assert "partially intersects lettering bbox" in violations[0].message

    # Auto-adjust must repair by shifting focusY to safely exclude lettering or anchoring to 0.0
    repaired = adjust_beat_crop(beat)
    assert check_beat_crop_safety(repaired) == []
    assert float(repaired["focus"]["y"]) <= 0.05 or float(repaired["focus"]["y"]) >= 0.50


def test_reproduce_tck_sc01_b4_lettering_clipped():
    """Defect reproduction: thuong-cho-kheo SC01_B4 clips 'BỨC TƯỜNG VÔ HÌNH' at top edge during push_in."""
    beat = {
        "id": "SC01_B4",
        "image_id": "SC01_V03",
        "effect": "push_in",
        "camera_motion": "push_in",
        "focus": {"x": 0.5, "y": 0.42, "scale": 1.0},
        "emphasis_text": "BỨC TƯỜNG VÔ HÌNH",
        "shot_type": "variation",
        "tempo": "fast",
    }
    violations = check_beat_crop_safety(beat, scene_id="SC01", duration=3.5)
    assert len(violations) == 1
    assert violations[0].rule == "LETTERING_CLIPPED"
    assert "partially intersects lettering bbox" in violations[0].message

    # Auto-adjust must repair by anchoring focusY=0.0 and centering focusX=0.5
    repaired = adjust_beat_crop(beat, scene_id="SC01", duration=3.5)
    assert float(repaired["focus"]["y"]) <= 0.05
    assert float(repaired["focus"]["x"]) == 0.5
    assert check_beat_crop_safety(repaired, scene_id="SC01", duration=3.5) == []


def test_reproduce_tui_tien_sc03_b1_lettering_clipped():
    """Defect reproduction: tui-tien SC03_B1 clips '7 NGHÌN' at top and right edge during zoom_in."""
    beat = {
        "id": "SC03_B1",
        "image_id": "SC03_V08",
        "effect": "zoom_in",
        "camera_motion": "zoom_in",
        "focus": {"x": 0.5, "y": 0.5, "scale": 1.0},
        "emphasis_text": "7 NGHÌN",
        "lettering_bbox": [0.05, 0.0, 0.96, 0.30],
        "shot_type": "full_scene",
        "tempo": "normal",
    }
    violations = check_beat_crop_safety(beat, scene_id="SC03", duration=3.0)
    assert len(violations) == 1
    assert violations[0].rule == "LETTERING_CLIPPED"
    assert "partially intersects lettering bbox" in violations[0].message

    # Auto-repair must shift pivot toward lettering (cy=0.0, cx=0.55) and reduce zoom amplitude
    repaired = adjust_beat_crop(beat, scene_id="SC03", duration=3.0)
    assert float(repaired["focus"]["y"]) <= 0.05
    assert float(repaired["focus"]["x"]) >= 0.50
    assert check_beat_crop_safety(repaired, scene_id="SC03", duration=3.0) == []


def test_reproduce_defect_a_lettering_clipped_at_right_edge():
    """Defect (a) reproduction: focus crop cuts wide lettering right edge (tui_tien SC04 / ua_sao_vay)."""
    # Lettering spans wide horizontally [0.06, 0.0, 0.95, 0.14]
    beat = {
        "id": "SC04_B3",
        "image_id": "SC04_V13",
        "focus": {"x": 0.5, "y": 0.5, "scale": 1.35},
        "emphasis_text": "APP CẮT 4K",
        "lettering_bbox": [0.06, 0.05, 0.95, 0.14],
    }
    # Visible rect at scale 1.35 has x2 = 0.5 + 0.5/(1.35*1.045) = 0.8544 < 0.95
    # Since y=0.5 has vy1=0.1456 which touches the bottom of the lettering, it cuts the right side
    violations = check_beat_crop_safety(beat)
    assert len(violations) == 1
    assert violations[0].rule == "LETTERING_CLIPPED"

    repaired = adjust_beat_crop(beat)
    assert check_beat_crop_safety(repaired) == []


def test_reproduce_defect_b_stickman_face_sliced_at_right():
    """Defect (b) reproduction: focus crop cuts stickman head at right edge (ai_binh_dan SC03)."""
    # Actor placed on right side; author zoomed in with focus x=0.7, y=0.45, scale=1.3
    beat = {
        "id": "SC03_B3",
        "image_id": "SC03_V08",
        "focus": {"x": 0.7, "y": 0.45, "scale": 1.3},
        "shot_type": "full_scene",
        "description": "Stickman in violet shirt reviews contract on the right side",
    }
    violations = check_beat_crop_safety(beat)
    assert len(violations) == 1
    assert violations[0].rule == "HEAD_SLICED"
    assert "cuts through primary-subject head bbox" in violations[0].message

    # Auto-adjust must repair by centering or degrading to push-in
    repaired = adjust_beat_crop(beat)
    assert check_beat_crop_safety(repaired) == []
    # Scaled down or degraded to push-in
    assert float(repaired["focus"]["scale"]) <= 1.15 or repaired.get("camera_motion") == "push_in"


def test_reproduce_defect_b_with_explicit_sidecar_head_bbox():
    """Defect (b) reproduction with explicit head bbox in sidecar metadata."""
    beat = {
        "id": "SC05_B2",
        "image_id": "SC05_V02",
        "focus": {"x": 0.65, "y": 0.45, "scale": 1.4},
        "shot_type": "full_scene",
    }
    sidecar = {
        "head_bbox": [0.60, 0.20, 0.92, 0.42]
    }
    violations = check_beat_crop_safety(beat, sidecar=sidecar)
    assert len(violations) == 1
    assert violations[0].rule == "HEAD_SLICED"

    repaired = adjust_beat_crop(beat, sidecar=sidecar)
    assert check_beat_crop_safety(repaired, sidecar=sidecar) == []


def test_graceful_degradation_to_gentle_push_in():
    """Verify that when no safe crop exists, beat degrades to full frame push-in."""
    # Extreme crop that cannot exclude lettering and cannot avoid slicing character
    beat = {
        "id": "SC99_B1",
        "image_id": "SC99_V01",
        "focus": {"x": 0.85, "y": 0.20, "scale": 1.6},
        "emphasis_text": "CỰC KỲ NGUY HIỂM",
        "lettering_bbox": [0.0, 0.0, 1.0, 0.35],
        "head_bbox": [0.1, 0.1, 0.9, 0.9],
        "shot_type": "full_scene",
    }
    repaired = adjust_beat_crop(beat)
    assert repaired["focus"]["scale"] == 1.0
    assert repaired["camera_motion"] == "push_in"
    assert check_beat_crop_safety(repaired) == []


def test_validate_scenes_crop_safety_pre_render_gate():
    """Verify pre-render gate validator flags violations and raises ValueError on error."""
    scenes = [
        {
            "id": "SC01",
            "duration": 5.0,
            "images": [{"id": "IMG01", "shot_type": "full_scene"}],
            "beats": [
                {"id": "B1", "image_id": "IMG01", "focus": {"x": 0.5, "y": 0.5, "scale": 1.0}},
                {"id": "B2", "image_id": "IMG01", "focus": {"x": 0.5, "y": 0.35, "scale": 1.35}, "emphasis_text": "HOT"},
            ]
        }
    ]
    violations = validate_scenes_crop_safety(scenes, raise_on_error=False)
    assert len(violations) == 1
    assert violations[0].rule == "LETTERING_CLIPPED"

    with pytest.raises(ValueError, match="Found 1 Crop-Safety violation"):
        validate_scenes_crop_safety(scenes, raise_on_error=True)


def test_enforce_scenes_crop_safety_batch_repair():
    """Verify batch scene repair adjusts all violating beats in-place."""
    scenes = [
        {
            "id": "SC01",
            "duration": 5.0,
            "images": [{"id": "IMG01", "shot_type": "full_scene"}],
            "beats": [
                {"id": "B1", "image_id": "IMG01", "focus": {"x": 0.5, "y": 0.5, "scale": 1.0}},
                {"id": "B2", "image_id": "IMG01", "focus": {"x": 0.5, "y": 0.35, "scale": 1.35}, "emphasis_text": "HOT"},
                {"id": "B3", "image_id": "IMG01", "focus": {"x": 0.7, "y": 0.45, "scale": 1.3}},
            ]
        }
    ]
    repaired_scenes, count = enforce_scenes_crop_safety(scenes)
    assert count == 2
    # Re-validate repaired scenes: must be 100% compliant
    violations = validate_scenes_crop_safety(repaired_scenes, raise_on_error=False)
    assert len(violations) == 0
