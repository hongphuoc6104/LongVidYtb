"""Validated standalone short plans sharing a landscape master's image/audio assets."""

from __future__ import annotations


def short_plans(brief: dict, content: dict) -> list[dict]:
    """Require authored four-part bodies after an independent hook, never raw chapters."""
    if not brief.get("omni_platform"):
        return []
    if brief.get("aspect_ratio") != "16:9" or not brief.get("reframe_mode"):
        raise ValueError("OMNI_MASTER: require 16:9 master and reframe_mode=true")
    plans = brief.get("spinoff_shorts", [])
    if not 2 <= len(plans) <= 3:
        raise ValueError("OMNI_SHORT_COUNT: author 2–3 standalone shorts")
    scenes = {scene["id"]: scene for scene in content["scenes"]}
    ids = set()
    for plan in plans:
        hook = plan.get("opening_hook", "").strip()
        if not hook or len(hook.split()) > 18 or "[pause:" in hook:
            raise ValueError("OMNI_SHORT_HOOK: require <=18 syllables and no pause")
        if plan["id"] in ids:
            raise ValueError("OMNI_SHORT_ID: duplicate ID")
        ids.add(plan["id"])
        body = plan.get("body", [])
        if len(body) != 4:
            raise ValueError("OMNI_SHORT_BODY: author four independent body scenes")
        for part in body:
            scene = scenes.get(part["parent_scene_id"])
            if scene is None or part["image_id"] not in {image["id"] for image in scene["images"]}:
                raise ValueError("OMNI_SHORT_REFERENCE: missing parent scene/image")
            if not part.get("segment_text", "").strip() or part["segment_text"] not in scene["narration"]:
                raise ValueError("OMNI_SHORT_TEXT: body must match a parent narration chunk")
    return plans
