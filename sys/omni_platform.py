"""Omni-platform short spinoff planning and re-anchoring."""
from __future__ import annotations

from typing import Any, Dict, List


def short_plans(brief: Dict[str, Any], content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate or retrieve standalone short spinoff plans from brief and content."""
    spinoffs = brief.get("spinoff_shorts") or []
    plans: List[Dict[str, Any]] = []
    scenes = content.get("scenes", [])

    for idx, item in enumerate(spinoffs, 1):
        plan_id = item.get("id") or f"SPINOFF_{idx:02d}"
        title = item.get("hook_title") or f"Short {idx}"
        body = item.get("body")
        if not body:
            # Fallback body selecting available parent scene segments
            body = []
            target_scenes = scenes[1:5] if len(scenes) >= 5 else scenes
            for sc in target_scenes:
                narration = sc.get("narration", "")
                first_sentence = (narration.split(".")[0].strip() + ".") if "." in narration else narration
                if first_sentence:
                    body.append({
                        "parent_scene_id": sc.get("id", "SC01"),
                        "segment_text": first_sentence
                    })
        plans.append({
            "id": plan_id,
            "hook_title": title,
            "body": body
        })
    return plans
