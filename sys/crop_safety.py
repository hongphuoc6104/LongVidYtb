"""Video Pilot — Crop-Safety Engine Module.

Enforces framing safety across EVERY beat (crops and non-crop camera motions):
1. Lettering safe-zone:
   Lettering bbox must be FULLY CONTAINED or FULLY EXCLUDED by visible rect
   at BOTH start and end of camera motion (zero partial intersection).
   Default lettering bbox: [0.0, 0.0, 1.0, 0.14] (upper third: 0-14% of height, full width).
2. Primary-subject head safe-zone:
   Head bbox must never be partially intersected by the visible rect.
   Sidecar metadata is used if available; otherwise uses documented head safe-zone heuristic
   or falls back to a centered, less-zoomed crop.
3. Camera motion visible rects:
   Computes exact visible rect at start and end of motion using Remotion overscan
   (BASE_OVERSCAN = 1.045) and camera.mjs speed budgets.
4. Auto-repair & Graceful degradation:
   - For focus-crops below lettering: shifts focusY downwards to safely exclude lettering.
   - For full-scene / containing beats: anchors focusY=0.0 and centers focusX=0.5 to keep lettering fully inside.
   - If head is sliced: centers pivot and reduces zoom amplitude.
   - If no safe crop exists, gracefully degrades to full frame (scale=1.0) with gentle push-in.
5. Pre-render validator gate:
   Fails fast with clear descriptive error messages on any violating beat.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger("video_pilot.crop_safety")

# Canonical renderer overscan constant matching Remotion renderer
BASE_OVERSCAN: float = 1.045

# Safety margin (2% frame size) to prevent raster/subpixel clipping at edges
SAFETY_MARGIN: float = 0.02

# Default conservative lettering bbox: upper third, 0-14% of frame height, with 3% canvas margins
DEFAULT_LETTERING_XMIN: float = 0.03
DEFAULT_LETTERING_YMIN: float = 0.0
DEFAULT_LETTERING_XMAX: float = 0.97
DEFAULT_LETTERING_YMAX: float = 0.14

# Heuristic primary-subject head safe-zone (normalized coordinates [0, 1])
# In 2D explainer compositions, stickman heads sit in upper-mid torso band
HEAD_HEURISTIC_YMIN: float = 0.18
HEAD_HEURISTIC_YMAX: float = 0.45
HEAD_HEURISTIC_CENTER_XMIN: float = 0.32
HEAD_HEURISTIC_CENTER_XMAX: float = 0.68
HEAD_HEURISTIC_RIGHT_XMIN: float = 0.55
HEAD_HEURISTIC_RIGHT_XMAX: float = 0.95
HEAD_HEURISTIC_LEFT_XMIN: float = 0.05
HEAD_HEURISTIC_LEFT_XMAX: float = 0.45


@dataclass(frozen=True)
class Rect:
    """Normalized 2D rectangle in [0.0, 1.0] image space."""
    x1: float  # left
    y1: float  # top
    x2: float  # right
    y2: float  # bottom

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    def contains(self, other: Rect, tolerance: float = 1e-4) -> bool:
        """Return True if this rect fully contains the other rect."""
        return (
            self.x1 <= other.x1 + tolerance
            and self.y1 <= other.y1 + tolerance
            and self.x2 >= other.x2 - tolerance
            and self.y2 >= other.y2 - tolerance
        )

    def intersects(self, other: Rect, tolerance: float = 1e-4) -> bool:
        """Return True if this rect and the other rect have non-empty overlap."""
        inter_x1 = max(self.x1, other.x1)
        inter_y1 = max(self.y1, other.y1)
        inter_x2 = min(self.x2, other.x2)
        inter_y2 = min(self.y2, other.y2)
        return (inter_x1 < inter_x2 - tolerance) and (inter_y1 < inter_y2 - tolerance)

    def relationship_with(self, target: Rect, tolerance: float = 1e-4) -> str:
        """Classify relationship with target rect.

        Returns:
            'contained': target is 100% inside this rect (safe).
            'excluded': target and this rect have zero overlap (safe).
            'partial': target partially overlaps boundary (unsafe clip/slice defect).
        """
        if not self.intersects(target, tolerance=tolerance):
            return "excluded"
        if self.contains(target, tolerance=tolerance):
            return "contained"
        return "partial"

    def to_list(self) -> List[float]:
        return [round(self.x1, 4), round(self.y1, 4), round(self.x2, 4), round(self.y2, 4)]


@dataclass
class CropSafetyViolation:
    """Detailed record of a crop-safety rule violation."""
    scene_id: str
    beat_id: str
    image_id: str
    rule: str  # 'LETTERING_CLIPPED' or 'HEAD_SLICED'
    message: str
    visible_rect_start: Rect
    visible_rect_end: Rect
    target_bbox: Rect
    focus: Dict[str, Any]


def compute_visible_rect(
    focus_x: float,
    focus_y: float,
    scale: float,
    base_overscan: float = BASE_OVERSCAN,
) -> Rect:
    """Compute the normalized visible image rect under Remotion CSS transform.

    Remotion applies:
        transformOrigin: `${focusX}% ${focusY}%`
        transform: `scale(${scale * base_overscan})`
    The resulting viewport [0, 1] x [0, 1] maps back to image coordinates:
        x_min = cx * (1 - 1/S)
        x_max = cx + (1 - cx) / S
        y_min = cy * (1 - 1/S)
        y_max = cy + (1 - cy) / S
    where S = scale * base_overscan.
    """
    effective_scale = max(1.0, float(scale)) * float(base_overscan)
    cx = max(0.0, min(1.0, float(focus_x)))
    cy = max(0.0, min(1.0, float(focus_y)))

    inv_s = 1.0 / effective_scale
    x1 = cx * (1.0 - inv_s)
    x2 = cx + (1.0 - cx) * inv_s
    y1 = cy * (1.0 - inv_s)
    y2 = cy + (1.0 - cy) * inv_s

    return Rect(x1=round(x1, 5), y1=round(y1, 5), x2=round(x2, 5), y2=round(y2, 5))


def compute_motion_visible_rects(
    focus: Optional[Dict[str, Any]] = None,
    camera_motion: str = "hold",
    duration: float = 3.0,
    base_overscan: float = BASE_OVERSCAN,
    shot_type: str = "full_scene",
    is_endcard: bool = False,
    has_lettering: bool = False,
) -> Tuple[Rect, Rect]:
    """Compute visible image rect at BOTH start and end of camera motion matching camera.mjs."""
    f = focus if (focus and isinstance(focus, dict)) else {}
    raw_scale = float(f.get("scale", 1.0))
    is_crop = raw_scale > 1.0
    crop_scale = min(1.6, max(1.0, raw_scale)) if is_crop else None

    raw_x = float(f.get("x", 0.5))
    raw_y = float(f.get("y", 0.42))

    motion = (camera_motion or "hold").strip().lower()
    inward = motion in ("zoom_in", "push_in", "punch_in", "drift_diag_in")
    outward = motion in ("zoom_out", "pull_back", "drift_diag_out")

    locked = is_crop or motion in ("hold", "static") or is_endcard or shot_type in ("white_card", "white_isolated", "macro_prop")
    moving = not locked and (inward or outward) and duration >= 2.4
    amplitude = min(0.015, (0.004 * duration) / (1.5 * base_overscan)) if moving else 0.0

    if crop_scale:
        scale_start = crop_scale * base_overscan
        scale_end = crop_scale * base_overscan
        half_span = 0.5 / scale_start
        min_center = half_span
        max_center = max(min_center, 1.0 - half_span)
        cx = min(max_center, max(min_center, raw_x))
        cy = min(max_center, max(min_center, raw_y))
    else:
        # For lettered frames, amplitude is capped at 0.005 to prevent edge clipping
        effective_amp = min(amplitude, 0.005) if has_lettering else amplitude
        scale_start = max(1.0, 1.0 + effective_amp * (1.0 if outward else 0.0)) * base_overscan
        scale_end = max(1.0, 1.0 + effective_amp * (0.0 if outward else 1.0)) * base_overscan
        if has_lettering:
            cx = min(0.65, max(0.35, raw_x))
            cy = raw_y if raw_y <= 0.05 else 0.0
        else:
            cx = min(0.65, max(0.35, raw_x))
            cy = min(0.58, max(0.35, raw_y))

    v_start = compute_visible_rect(cx, cy, scale_start / base_overscan, base_overscan=base_overscan)
    v_end = compute_visible_rect(cx, cy, scale_end / base_overscan, base_overscan=base_overscan)
    return v_start, v_end


def detect_image_lettering_bbox(img_path: Path) -> Optional[Rect]:
    """Inspect genuine rendered image pixels to extract actual hand-lettering bounds if present."""
    if not img_path.is_file():
        return None
    if img_path.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv", ".avi"):
        return None
    try:
        import numpy as np
        from PIL import Image

        with Image.open(img_path) as im:
            rgb = im.convert("RGB")
            arr = np.array(rgb)
            h, w, _ = arr.shape
            top_h = int(h * 0.45)
            top_slice = arr[:top_h, :, :]
            gray = np.mean(top_slice, axis=2)
            dark_y, dark_x = np.where(gray < 90)
            if len(dark_y) > 60:
                y1 = max(0.0, float(dark_y.min()) / h)
                y2 = min(0.45, float(dark_y.max()) / h)
                x1 = max(0.0, float(dark_x.min()) / w)
                x2 = min(1.0, float(dark_x.max()) / w)
                return Rect(x1=round(x1, 4), y1=round(y1, 4), x2=round(x2, 4), y2=round(y2, 4))
    except Exception:
        pass
    return None


def resolve_lettering_bbox(
    beat: Dict[str, Any],
    image_meta: Optional[Dict[str, Any]] = None,
    sidecar: Optional[Dict[str, Any]] = None,
    image_path: Optional[Path] = None,
) -> Optional[Rect]:
    """Determine whether lettering exists and return its bounding box.

    Returns None if no hand-lettering is present on this image.
    """
    b = beat or {}
    im = image_meta or {}
    sc = sidecar or {}

    explicit_bbox = (
        b.get("lettering_bbox")
        or im.get("lettering_bbox")
        or sc.get("lettering_bbox")
        or b.get("emphasis_bbox")
        or im.get("emphasis_bbox")
        or sc.get("emphasis_bbox")
    )
    if explicit_bbox:
        if isinstance(explicit_bbox, (list, tuple)) and len(explicit_bbox) == 4:
            return Rect(*[float(v) for v in explicit_bbox])
        if isinstance(explicit_bbox, dict):
            return Rect(
                x1=float(explicit_bbox.get("x1", explicit_bbox.get("x", 0.0))),
                y1=float(explicit_bbox.get("y1", explicit_bbox.get("y", 0.0))),
                x2=float(explicit_bbox.get("x2", explicit_bbox.get("x1", 0.0) + explicit_bbox.get("w", 1.0))),
                y2=float(explicit_bbox.get("y2", explicit_bbox.get("y1", 0.0) + explicit_bbox.get("h", 0.14))),
            )

    emp_text = (
        b.get("emphasis_text")
        or im.get("emphasis_text")
        or sc.get("emphasis_text")
    )
    has_text = bool(emp_text and str(emp_text).strip())
    if not has_text:
        vis_texts = b.get("visible_text") or im.get("visible_text") or []
        if isinstance(vis_texts, list) and vis_texts:
            has_text = any(isinstance(t, dict) and t.get("text") for t in vis_texts)

    if not has_text:
        return None

    if image_path and image_path.is_file():
        detected = detect_image_lettering_bbox(image_path)
        if detected:
            return detected

    return Rect(
        x1=DEFAULT_LETTERING_XMIN,
        y1=DEFAULT_LETTERING_YMIN,
        x2=DEFAULT_LETTERING_XMAX,
        y2=DEFAULT_LETTERING_YMAX,
    )


def resolve_head_bbox(
    beat: Dict[str, Any],
    image_meta: Optional[Dict[str, Any]] = None,
    sidecar: Optional[Dict[str, Any]] = None,
) -> Optional[Rect]:
    """Determine whether primary character exists and return primary-subject head bbox.

    Uses sidecar metadata if available; otherwise uses documented head safe-zone heuristic.
    Returns None if the frame contains no character actor.
    """
    b = beat or {}
    im = image_meta or {}
    sc = sidecar or {}

    explicit_bbox = (
        b.get("head_bbox")
        or im.get("head_bbox")
        or sc.get("head_bbox")
        or b.get("primary_head_bbox")
        or im.get("primary_head_bbox")
        or sc.get("primary_head_bbox")
    )
    if explicit_bbox:
        if isinstance(explicit_bbox, (list, tuple)) and len(explicit_bbox) == 4:
            return Rect(*[float(v) for v in explicit_bbox])
        if isinstance(explicit_bbox, dict):
            return Rect(
                x1=float(explicit_bbox.get("x1", explicit_bbox.get("x", 0.0))),
                y1=float(explicit_bbox.get("y1", explicit_bbox.get("y", 0.0))),
                x2=float(explicit_bbox.get("x2", explicit_bbox.get("x1", 0.0) + explicit_bbox.get("w", 0.3))),
                y2=float(explicit_bbox.get("y2", explicit_bbox.get("y1", 0.0) + explicit_bbox.get("h", 0.27))),
            )

    has_char = False
    shot_type = str(im.get("shot_type") or b.get("shot_type") or "").strip().lower()
    char_ids = im.get("character_ids") or b.get("character_ids") or []
    if char_ids or shot_type in ("full_scene", "variation", "character"):
        has_char = True

    desc = f"{b.get('description', '')} {im.get('description', '')} {sc.get('prompt', '')}".lower()
    if any(k in desc for k in ("stickman", "người que", "ch01", "actor", "nhân vật", "young employee", "barista")):
        has_char = True

    if not has_char:
        return None

    raw_x = float((b.get("focus") or {}).get("x", 0.5))
    if raw_x > 0.60 or "right" in desc or "bên phải" in desc:
        return Rect(
            x1=HEAD_HEURISTIC_RIGHT_XMIN,
            y1=HEAD_HEURISTIC_YMIN,
            x2=HEAD_HEURISTIC_RIGHT_XMAX,
            y2=HEAD_HEURISTIC_YMAX,
        )
    if raw_x < 0.40 or "left" in desc or "bên trái" in desc:
        return Rect(
            x1=HEAD_HEURISTIC_LEFT_XMIN,
            y1=HEAD_HEURISTIC_YMIN,
            x2=HEAD_HEURISTIC_LEFT_XMAX,
            y2=HEAD_HEURISTIC_YMAX,
        )
    return Rect(
        x1=HEAD_HEURISTIC_CENTER_XMIN,
        y1=HEAD_HEURISTIC_YMIN,
        x2=HEAD_HEURISTIC_CENTER_XMAX,
        y2=HEAD_HEURISTIC_YMAX,
    )


def check_beat_crop_safety(
    beat: Dict[str, Any],
    scene_id: str = "SC01",
    image_meta: Optional[Dict[str, Any]] = None,
    sidecar: Optional[Dict[str, Any]] = None,
    duration: float = 3.0,
    base_overscan: float = BASE_OVERSCAN,
    image_path: Optional[Path] = None,
) -> List[CropSafetyViolation]:
    """Check a single beat against Crop-Safety rules.

    Evaluates the visible rect at BOTH start and end of camera motion across EVERY beat.
    Returns empty list if beat satisfies all rules.
    """
    b = beat or {}
    im = image_meta or {}

    # Skip video clips (.mp4) from static image crop analysis
    b_src = str(b.get("src") or b.get("path") or "")
    im_path = str(im.get("path") or im.get("src") or "")
    if (
        b.get("kind") == "video"
        or b_src.lower().endswith(".mp4")
        or im_path.lower().endswith(".mp4")
        or (image_path is not None and image_path.suffix.lower() in (".mp4", ".mov", ".webm"))
    ):
        return []

    focus = b.get("focus") or {}
    raw_scale = float(focus.get("scale", 1.0)) if isinstance(focus, dict) else 1.0
    camera_motion = str(b.get("camera_motion") or b.get("effect") or "hold")
    shot_type = str(im.get("shot_type") or b.get("shot_type") or "full_scene")
    is_endcard = bool(b.get("is_endcard") or im.get("is_endcard") or b.get("spec") == "endcard")

    lettering_box = resolve_lettering_bbox(b, image_meta=im, sidecar=sidecar, image_path=image_path)
    has_lettering = bool(lettering_box is not None)

    # Use actual authored focus.y to detect top-edge clipping if focusY was not anchored
    raw_y = float(focus.get("y", 0.42)) if isinstance(focus, dict) else 0.42
    is_y_anchored = (raw_y <= 0.05)
    v_start, v_end = compute_motion_visible_rects(
        focus=focus if isinstance(focus, dict) else None,
        camera_motion=camera_motion,
        duration=duration,
        base_overscan=base_overscan,
        shot_type=shot_type,
        is_endcard=is_endcard,
        has_lettering=has_lettering and is_y_anchored,
    )

    violations: List[CropSafetyViolation] = []
    beat_id = str(b.get("id", "B_UNKNOWN"))
    image_id = str(b.get("image_id", "IMG_UNKNOWN"))

    # 1. Lettering safety check: must fully contain or fully exclude (never partial cut)
    if lettering_box:
        padded_target = Rect(
            x1=lettering_box.x1,
            y1=lettering_box.y1,
            x2=lettering_box.x2,
            y2=min(1.0, lettering_box.y2 + SAFETY_MARGIN),
        )
        rel_start = v_start.relationship_with(padded_target)
        rel_end = v_end.relationship_with(padded_target)

        # Detect top clipping: if lettering starts at top (y1 < 0.05) and vy1 > 0.010, the top is clipped
        top_clipped_start = (lettering_box.y1 < 0.05 and v_start.y1 > 0.010)
        top_clipped_end = (lettering_box.y1 < 0.05 and v_end.y1 > 0.010)

        # For full-frame beats anchored to top (scale <= 1.0 and vy1 <= 0.01), standard overscan is safe
        is_full_frame_anchored = (raw_scale <= 1.0 and is_y_anchored and v_start.y1 <= 0.010 and v_end.y1 <= 0.010 and v_start.y2 >= lettering_box.y2)

        if not is_full_frame_anchored and (rel_start == "partial" or rel_end == "partial" or (rel_start != rel_end) or top_clipped_start or top_clipped_end):
            msg = (
                f"CROP_LETTERING_CLIPPED: Beat {beat_id} in {scene_id} ({image_id}) partially intersects "
                f"lettering bbox [{lettering_box.x1:.2f}, {lettering_box.y1:.2f}, {lettering_box.x2:.2f}, {lettering_box.y2:.2f}]. "
                f"Visible rect start={v_start.to_list()} (rel={rel_start}), end={v_end.to_list()} (rel={rel_end}). "
                f"Focus: {focus}."
            )
            violations.append(CropSafetyViolation(
                scene_id=scene_id,
                beat_id=beat_id,
                image_id=image_id,
                rule="LETTERING_CLIPPED",
                message=msg,
                visible_rect_start=v_start,
                visible_rect_end=v_end,
                target_bbox=lettering_box,
                focus=focus if isinstance(focus, dict) else {},
            ))

    # 2. Primary-subject head safety check: never cut through head bbox
    head_box = resolve_head_bbox(b, image_meta=im, sidecar=sidecar)
    if head_box and raw_scale > 1.05:
        rel_start = v_start.relationship_with(head_box)
        rel_end = v_end.relationship_with(head_box)
        if rel_start == "partial" or rel_end == "partial":
            msg = (
                f"CROP_HEAD_SLICED: Beat {beat_id} in {scene_id} ({image_id}) cuts through primary-subject head bbox "
                f"[{head_box.x1:.2f}, {head_box.y1:.2f}, {head_box.x2:.2f}, {head_box.y2:.2f}]. "
                f"Visible rect start={v_start.to_list()}, end={v_end.to_list()}. "
                f"Focus: {focus}."
            )
            violations.append(CropSafetyViolation(
                scene_id=scene_id,
                beat_id=beat_id,
                image_id=image_id,
                rule="HEAD_SLICED",
                message=msg,
                visible_rect_start=v_start,
                visible_rect_end=v_end,
                target_bbox=head_box,
                focus=focus if isinstance(focus, dict) else {},
            ))

    return violations


def adjust_beat_crop(
    beat: Dict[str, Any],
    scene_id: str = "SC01",
    image_meta: Optional[Dict[str, Any]] = None,
    sidecar: Optional[Dict[str, Any]] = None,
    duration: float = 3.0,
    base_overscan: float = BASE_OVERSCAN,
    image_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Adjust a violating beat to satisfy all CropSafety rules across every beat.

    Priority:
    1. For focus-crop beats below lettering: shift focusY downwards to safely EXCLUDE lettering.
    2. For full-scene / non-crop beats or containing crops: anchor pivot focusY=0.0 and center focusX=0.5
       to keep lettering fully inside without top-edge clipping from BASE_OVERSCAN.
    3. Reduce zoom amplitude or fall back to centered less-zoomed crop if head is sliced.
    4. If no safe crop exists, degrade gracefully: use full image with gentle push-in (scale=1.0).

    Returns the updated beat dictionary.
    """
    repaired_beat = dict(beat)
    violations = check_beat_crop_safety(
        repaired_beat,
        scene_id=scene_id,
        image_meta=image_meta,
        sidecar=sidecar,
        duration=duration,
        base_overscan=base_overscan,
        image_path=image_path,
    )
    if not violations:
        return repaired_beat

    focus = repaired_beat.get("focus") or {}
    scale = float(focus.get("scale", 1.0)) if isinstance(focus, dict) else 1.0
    raw_x = float(focus.get("x", 0.5)) if isinstance(focus, dict) else 0.5
    raw_y = float(focus.get("y", 0.42)) if isinstance(focus, dict) else 0.42
    lettering_box = resolve_lettering_bbox(beat, image_meta=image_meta, sidecar=sidecar, image_path=image_path)

    # Strategy 1: If scale > 1.0 and crop center is low (raw_y >= 0.40), try to EXCLUDE lettering
    if scale > 1.0 and lettering_box and raw_y >= 0.40:
        effective_scale = scale * base_overscan
        inv_s = 1.0 / effective_scale
        if (1.0 - inv_s) > 0.05:
            target_ymin = min(0.85, lettering_box.y2 + SAFETY_MARGIN + 0.005)
            needed_cy = target_ymin / (1.0 - inv_s)
            if needed_cy <= 0.85:
                test_focus = {"x": raw_x, "y": round(max(raw_y, needed_cy), 3), "scale": scale}
                test_beat = dict(repaired_beat, focus=test_focus)
                if not check_beat_crop_safety(test_beat, scene_id, image_meta, sidecar, duration, base_overscan, image_path=image_path):
                    repaired_beat["focus"] = test_focus
                    return repaired_beat

    # Strategy 2: Keep lettering FULLY INSIDE by anchoring pivot to top and shifting toward text
    if lettering_box:
        cy = 0.0
        if lettering_box.x2 > 0.95 and lettering_box.x1 > 0.04:
            cx = 0.55
        elif lettering_box.x1 < 0.05 and lettering_box.x2 < 0.96:
            cx = 0.45
        else:
            cx = 0.50

        clamped_scale = min(1.15, scale) if scale > 1.0 else 1.0
        test_focus = {"x": cx, "y": cy, "scale": clamped_scale}
        raw_motion = repaired_beat.get("camera_motion") or repaired_beat.get("effect") or "hold"
        new_motion = "hold" if scale > 1.0 else ("push_in" if raw_motion in ("zoom_in", "push_in", "punch_in") else raw_motion)
        test_beat = dict(repaired_beat, focus=test_focus, camera_motion=new_motion, effect=new_motion)
        if not check_beat_crop_safety(test_beat, scene_id, image_meta, sidecar, duration, base_overscan, image_path=image_path):
            repaired_beat["focus"] = test_focus
            repaired_beat["camera_motion"] = new_motion
            repaired_beat["effect"] = new_motion
            return repaired_beat

    # Strategy 3: Fall back to a centered, less-zoomed crop (Head safe-zone fallback)
    for test_scale in (1.15, 1.10):
        test_focus = {"x": 0.5, "y": 0.0 if lettering_box else 0.42, "scale": test_scale}
        test_beat = dict(repaired_beat, focus=test_focus)
        if not check_beat_crop_safety(test_beat, scene_id, image_meta, sidecar, duration, base_overscan, image_path=image_path):
            repaired_beat["focus"] = test_focus
            return repaired_beat

    # Strategy 4: Degrade gracefully to full image with gentle push-in
    logger.info(f"  [>] CropSafety degrade: Beat {beat.get('id')} in {scene_id} reverts to full-frame gentle push-in.")
    repaired_beat["focus"] = {"x": 0.5, "y": 0.0 if lettering_box else 0.42, "scale": 1.0}
    repaired_beat["camera_motion"] = "push_in"
    repaired_beat["effect"] = "push_in"
    return repaired_beat


def validate_scenes_crop_safety(
    scenes: Sequence[Dict[str, Any]],
    images_dir: Optional[Path] = None,
    raise_on_error: bool = False,
    base_overscan: float = BASE_OVERSCAN,
) -> List[CropSafetyViolation]:
    """Validate all beats across scenes against CropSafety rules.

    Args:
        scenes: List of scene dictionaries (from content.json or timeline).
        images_dir: Optional path to revisions/images/1 directory to inspect sidecars.
        raise_on_error: If True, raises ValueError on the first violation.
        base_overscan: Overscan multiplier (default 1.045).

    Returns:
        List of all CropSafetyViolations found.
    """
    all_violations: List[CropSafetyViolation] = []

    for sc in scenes:
        scene_id = str(sc.get("id") or sc.get("scene_id") or "SC_UNKNOWN")
        images_by_id = {im["id"]: im for im in sc.get("images", []) if isinstance(im, dict) and "id" in im}
        beats = sc.get("beats") or sc.get("images") or []

        for b in beats:
            if not isinstance(b, dict):
                continue
            img_id = b.get("image_id") or b.get("id")
            im_meta = images_by_id.get(img_id, {})

            # Attempt to read sidecar if images_dir provided
            sidecar: Optional[Dict[str, Any]] = None
            image_path: Optional[Path] = None
            if images_dir and images_dir.is_dir() and img_id:
                for candidate_json in (
                    images_dir / f"{img_id}_9x16.json",
                    images_dir / f"{img_id}_16x9.json",
                    images_dir / f"{img_id}.json",
                ):
                    if candidate_json.is_file():
                        try:
                            sidecar = json.loads(candidate_json.read_text(encoding="utf-8"))
                            break
                        except Exception:
                            pass
                for candidate_img in (
                    images_dir / f"{img_id}_9x16.jpg",
                    images_dir / f"{img_id}_16x9.jpg",
                    images_dir / f"{img_id}.jpg",
                ):
                    if candidate_img.is_file():
                        image_path = candidate_img
                        break

            v_list = check_beat_crop_safety(
                beat=b,
                scene_id=scene_id,
                image_meta=im_meta,
                sidecar=sidecar,
                duration=float(sc.get("duration", 3.0)),
                base_overscan=base_overscan,
                image_path=image_path,
            )
            all_violations.extend(v_list)

    if raise_on_error and all_violations:
        lines = [f"Found {len(all_violations)} Crop-Safety violation(s):"]
        for v in all_violations:
            lines.append(f"  - [{v.rule}] {v.message}")
        raise ValueError("\n".join(lines))

    return all_violations


def enforce_scenes_crop_safety(
    scenes: Sequence[Dict[str, Any]],
    images_dir: Optional[Path] = None,
    base_overscan: float = BASE_OVERSCAN,
) -> Tuple[List[Dict[str, Any]], int]:
    """Auto-repair all beats across scenes in-place.

    Returns:
        (repaired_scenes, count_of_repaired_beats)
    """
    repaired_scenes: List[Dict[str, Any]] = []
    repair_count = 0

    for sc in scenes:
        sc_copy = dict(sc)
        images_by_id = {im["id"]: im for im in sc_copy.get("images", []) if isinstance(im, dict) and "id" in im}

        if "beats" in sc_copy and isinstance(sc_copy["beats"], list):
            new_beats = []
            for b in sc_copy["beats"]:
                img_id = b.get("image_id")
                im_meta = images_by_id.get(img_id, {})
                sidecar = None
                image_path = None
                if images_dir and images_dir.is_dir() and img_id:
                    for cand_json in (images_dir / f"{img_id}_9x16.json", images_dir / f"{img_id}_16x9.json", images_dir / f"{img_id}.json"):
                        if cand_json.is_file():
                            try:
                                sidecar = json.loads(cand_json.read_text(encoding="utf-8"))
                                break
                            except Exception:
                                pass
                    for cand_img in (images_dir / f"{img_id}_9x16.jpg", images_dir / f"{img_id}_16x9.jpg", images_dir / f"{img_id}.jpg"):
                        if cand_img.is_file():
                            image_path = cand_img
                            break

                repaired = adjust_beat_crop(
                    beat=b,
                    scene_id=sc_copy.get("id", "SC"),
                    image_meta=im_meta,
                    sidecar=sidecar,
                    duration=float(sc_copy.get("duration", 3.0)),
                    base_overscan=base_overscan,
                    image_path=image_path,
                )
                if repaired.get("focus") != b.get("focus") or repaired.get("camera_motion") != b.get("camera_motion"):
                    repair_count += 1
                new_beats.append(repaired)
            sc_copy["beats"] = new_beats

        if "images" in sc_copy and isinstance(sc_copy["images"], list):
            new_images = []
            for im in sc_copy["images"]:
                img_id = im.get("id")
                sidecar = None
                image_path = None
                if images_dir and images_dir.is_dir() and img_id:
                    for cand_json in (images_dir / f"{img_id}_9x16.json", images_dir / f"{img_id}_16x9.json", images_dir / f"{img_id}.json"):
                        if cand_json.is_file():
                            try:
                                sidecar = json.loads(cand_json.read_text(encoding="utf-8"))
                                break
                            except Exception:
                                pass
                    for cand_img in (images_dir / f"{img_id}_9x16.jpg", images_dir / f"{img_id}_16x9.jpg", images_dir / f"{img_id}.jpg"):
                        if cand_img.is_file():
                            image_path = cand_img
                            break
                repaired = adjust_beat_crop(
                    beat=im,
                    scene_id=sc_copy.get("id", "SC"),
                    image_meta=im,
                    sidecar=sidecar,
                    duration=float(sc_copy.get("duration", 3.0)),
                    base_overscan=base_overscan,
                    image_path=image_path,
                )
                if repaired.get("focus") != im.get("focus") or repaired.get("camera_motion") != im.get("camera_motion"):
                    repair_count += 1
                new_images.append(repaired)
            sc_copy["images"] = new_images

        repaired_scenes.append(sc_copy)

    return repaired_scenes, repair_count
