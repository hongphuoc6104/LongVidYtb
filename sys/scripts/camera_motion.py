"""Camera selection shared by authoring and the remote timeline."""
from typing import List, Optional


def select_semantic_camera_effect(
    framing_or_camera: str,
    prev_effect: Optional[str] = None,
) -> str:
    """Map framing or camera direction to a semantic Remotion camera effect without consecutive duplicates."""
    text = (framing_or_camera or "").strip().lower()
    if text in ("zoom_in", "zoom_out", "punch_in", "pan_left", "pan_right"):
        eff = text
    elif any(k in text for k in ("extreme", "macro", "đặc tả", "nhấn", "punch")):
        eff = "punch_in"
    elif any(k in text for k in ("wide", "establishing", "pull", "zoom_out", "zoom out", "toàn cảnh", "rộng", "mở rộng")):
        eff = "zoom_out"
    elif any(k in text for k in ("left", "trái", "ngược", "quay lại", "đối lập")):
        eff = "pan_left"
    elif any(k in text for k in ("pan", "tracking", "quét", "lia", "đối xứng", "ngang")):
        eff = "pan_right"
    else:
        eff = "zoom_in"

    if prev_effect is not None and eff == prev_effect:
        eff = "pan_right" if prev_effect != "pan_right" else "zoom_in"
    return eff


def assign_scene_camera_effects(camera_descriptions: List[str]) -> List[str]:
    """Assign semantic camera effects across a sequence of shots with zero consecutive duplicates."""
    effects: List[str] = []
    prev: Optional[str] = None
    for desc in camera_descriptions:
        eff = select_semantic_camera_effect(desc, prev_effect=prev)
        effects.append(eff)
        prev = eff
    return effects



def scene_camera_motions(scene: dict) -> list[str]:
    """Resolve legacy cut/fade transitions to non-repeating in-frame movements."""
    images = {image['id']: image for image in scene.get('images', [])}
    motions: list[str] = []
    for beat in scene.get('beats', []):
        motion = beat.get('camera_motion', beat.get('effect', 'auto'))
        if motion in ('auto', 'cut', 'fade'):
            image = images.get(beat['image_id'], {})
            motion = select_semantic_camera_effect(
                image.get('description', '') + ' ' + scene.get('camera', ''), motions[-1] if motions else None)
        motions.append(motion)
    return motions
