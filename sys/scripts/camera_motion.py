"""Camera selection shared by authoring and the remote timeline."""
from typing import List, Optional

_EDITORIAL_SEQUENCE = ("pan_right", "zoom_in", "hold", "zoom_out", "pan_left", "punch_in")

_PHASE_PREFERRED_EFFECTS = {
    "hook": ("punch_in", "zoom_in", "pan_right", "zoom_out"),
    "lead_in": ("zoom_in", "pan_right", "zoom_out", "pan_left"),
    "lived_friction": ("zoom_in", "pan_right", "zoom_out", "pan_left"),
    "problem": ("punch_in", "zoom_in", "pan_left", "zoom_out"),
    "empirical_conflict": ("zoom_in", "pan_left", "punch_in", "zoom_out"),
    "causal_mechanism": ("pan_right", "hold", "zoom_in", "zoom_out"),
    "explanation": ("zoom_in", "pan_right", "hold", "zoom_out"),
    "structural_model": ("pan_right", "hold", "zoom_in", "zoom_out"),
    "counter_argument": ("punch_in", "pan_left", "zoom_in", "zoom_out"),
    "takeaway": ("zoom_out", "hold", "zoom_in", "pan_right"),
    "closing": ("zoom_out", "hold", "pan_right", "zoom_in"),
    "actionable_resolution": ("zoom_out", "pan_right", "zoom_in", "hold"),
}


def _match_explicit_or_keyword_effect(text: str, shot_type: str = "") -> Optional[str]:
    st = (shot_type or "").strip().lower()
    if st in ("visual_diagram", "white_card", "white_isolated"):
        return "hold"
    if text in ("zoom_in", "zoom_out", "punch_in", "pan_left", "pan_right", "hold"):
        return text
    if any(k in text for k in ("hold", "static", "white_card", "visual_diagram", "sơ đồ tĩnh", "bảng đối chiếu", "sơ đồ đối chiếu", "clean white background")):
        return "hold"
    if any(k in text for k in ("extreme", "macro", "đặc tả", "nhấn", "punch", "reveal", "shock", "bất ngờ", "giật mình", "sự thật", "nghịch lý")):
        return "punch_in"
    if any(k in text for k in ("wide", "establishing", "pull", "zoom_out", "zoom out", "toàn cảnh", "rộng", "mở rộng", "bức tranh lớn", "tổng thể")):
        return "zoom_out"
    if any(k in text for k in ("left", "trái", "ngược", "quay lại", "đối lập", "contrast", "phản biện", "lật ngược")):
        return "pan_left"
    if any(k in text for k in ("pan", "tracking", "quét", "lia", "đối xứng", "ngang", "timeline", "dòng thời gian", "chuỗi nhân quả", "mũi tên")):
        return "pan_right"
    if any(k in text for k in ("detail", "focus", "tension", "cận cảnh", "tập trung", "chi tiết")):
        return "zoom_in"
    return None


def select_semantic_camera_effect(
    framing_or_camera: str,
    prev_effect: Optional[str] = None,
    beat_index: Optional[int] = None,
    shot_type: str = "",
    narrative_phase: str = "",
) -> str:
    """Map framing, shot_type, and narrative_phase to a purposeful Remotion camera effect without consecutive duplicates."""
    text = (framing_or_camera or "").strip().lower()
    matched = _match_explicit_or_keyword_effect(text, shot_type=shot_type)
    phase_key = (narrative_phase or "").strip().lower()
    pool = _PHASE_PREFERRED_EFFECTS.get(phase_key, _EDITORIAL_SEQUENCE)

    if matched is not None:
        eff = matched
    elif beat_index is not None:
        eff = pool[beat_index % len(pool)]
    else:
        eff = pool[0]

    if prev_effect is not None and eff == prev_effect:
        for candidate in pool:
            if candidate != prev_effect:
                eff = candidate
                break
        else:
            eff = "pan_right" if prev_effect != "pan_right" else "zoom_in"
    return eff


def assign_scene_camera_effects(
    camera_descriptions: List[str],
    narrative_phase: str = "",
) -> List[str]:
    """Assign semantic camera effects across a sequence of shots with zero consecutive duplicates."""
    effects: List[str] = []
    prev: Optional[str] = None
    for idx, desc in enumerate(camera_descriptions):
        text = (desc or "").strip().lower()
        use_index = idx if _match_explicit_or_keyword_effect(text) is None else None
        eff = select_semantic_camera_effect(
            desc,
            prev_effect=prev,
            beat_index=use_index,
            narrative_phase=narrative_phase,
        )
        effects.append(eff)
        prev = eff
    return effects


def scene_camera_motions(scene: dict) -> list[str]:
    """Resolve legacy cut/fade transitions to non-repeating purposeful movements."""
    images = {image['id']: image for image in scene.get('images', [])}
    motions: list[str] = []
    beats = scene.get('beats', [])
    use_pool = len(beats) > 2
    phase = str(scene.get('editorial_section') or scene.get('narrative_phase') or '')
    for idx, beat in enumerate(beats):
        motion = beat.get('camera_motion', beat.get('effect', 'auto'))
        if motion in ('auto', 'cut', 'fade'):
            image = images.get(beat['image_id'], {})
            shot_type = str(image.get('shot_type', ''))
            combined = image.get('description', '') + ' ' + scene.get('camera', '')
            use_index = idx if (use_pool and _match_explicit_or_keyword_effect(combined.strip().lower(), shot_type=shot_type) is None) else None
            motion = select_semantic_camera_effect(
                combined,
                motions[-1] if motions else None,
                beat_index=use_index,
                shot_type=shot_type,
                narrative_phase=phase,
            )
        motions.append(motion)
    return motions
