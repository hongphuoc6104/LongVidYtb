"""Camera selection shared by authoring and the remote timeline."""
from typing import List, Optional

_FALLBACK_POOL = ("zoom_in", "pan_right", "zoom_out", "pan_left")


def _match_explicit_or_keyword_effect(text: str) -> Optional[str]:
    if text in ("zoom_in", "zoom_out", "punch_in", "pan_left", "pan_right", "hold"):
        return text
    if any(k in text for k in ("hold", "static", "white_card", "sơ đồ tĩnh", "bảng đối chiếu", "sơ đồ đối chiếu")):
        return "hold"
    if any(k in text for k in ("extreme", "macro", "đặc tả", "nhấn", "punch", "reveal", "shock", "bất ngờ", "giật mình")):
        return "punch_in"
    if any(k in text for k in ("wide", "establishing", "pull", "zoom_out", "zoom out", "toàn cảnh", "rộng", "mở rộng")):
        return "zoom_out"
    if any(k in text for k in ("left", "trái", "ngược", "quay lại", "đối lập", "contrast")):
        return "pan_left"
    if any(k in text for k in ("pan", "tracking", "quét", "lia", "đối xứng", "ngang", "timeline", "dòng thời gian")):
        return "pan_right"
    if any(k in text for k in ("detail", "focus", "tension", "cận cảnh", "tập trung")):
        return "zoom_in"
    return None


def select_semantic_camera_effect(
    framing_or_camera: str,
    prev_effect: Optional[str] = None,
    beat_index: Optional[int] = None,
) -> str:
    """Map framing or camera direction to a semantic Remotion camera effect without consecutive duplicates."""
    text = (framing_or_camera or "").strip().lower()
    matched = _match_explicit_or_keyword_effect(text)
    if matched is not None:
        eff = matched
    elif beat_index is not None:
        eff = _FALLBACK_POOL[beat_index % len(_FALLBACK_POOL)]
    else:
        eff = "zoom_in"

    if prev_effect is not None and eff == prev_effect:
        if beat_index is not None:
            idx = _FALLBACK_POOL.index(eff) if eff in _FALLBACK_POOL else 0
            eff = _FALLBACK_POOL[(idx + 1) % len(_FALLBACK_POOL)]
        else:
            eff = "pan_right" if prev_effect != "pan_right" else "zoom_in"
    return eff


def assign_scene_camera_effects(camera_descriptions: List[str]) -> List[str]:
    """Assign semantic camera effects across a sequence of shots with zero consecutive duplicates."""
    effects: List[str] = []
    prev: Optional[str] = None
    for idx, desc in enumerate(camera_descriptions):
        text = (desc or "").strip().lower()
        use_index = idx if _match_explicit_or_keyword_effect(text) is None else None
        eff = select_semantic_camera_effect(desc, prev_effect=prev, beat_index=use_index)
        effects.append(eff)
        prev = eff
    return effects


def scene_camera_motions(scene: dict) -> list[str]:
    """Resolve legacy cut/fade transitions to non-repeating in-frame movements."""
    images = {image['id']: image for image in scene.get('images', [])}
    motions: list[str] = []
    beats = scene.get('beats', [])
    use_pool = len(beats) > 2
    for idx, beat in enumerate(beats):
        motion = beat.get('camera_motion', beat.get('effect', 'auto'))
        if motion in ('auto', 'cut', 'fade'):
            image = images.get(beat['image_id'], {})
            combined = image.get('description', '') + ' ' + scene.get('camera', '')
            use_index = idx if (use_pool and _match_explicit_or_keyword_effect(combined.strip().lower()) is None) else None
            motion = select_semantic_camera_effect(
                combined,
                motions[-1] if motions else None,
                beat_index=use_index,
            )
        motions.append(motion)
    return motions
