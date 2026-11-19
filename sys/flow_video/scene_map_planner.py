"""Two-Stage Scene Map Planner & Dynamic Channel-Bible Positive-Framing Compiler.

Implements:
- Stage 1: Channel-agnostic Scene Map (`SceneMap` / `SceneMapEntry`) locking Cast/Ref DAG,
  Camera Moves (never repeating consecutively), Anti-Morph Routing (`veo_3_1_lite` 10c Seam vs
  `omni_flash` Frame-Link), and Exit Seams with viewing-comfort policies.
- Stage 2: Dynamic Channel Style Bible lookup across all 38 VN/EN channels + positive-framing
  image prompt compiler & timecoded video prompt compiler.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from .motion_library import (  # noqa: E402
    CAMERA_MOVES,
    EXIT_SEAMS,
    apply_positive_framing,
    build_timecoded_video_prompt,
    get_channel_lens_spec,
    get_channel_motion_policy,
)


@dataclass
class SceneMapEntry:
    scene_id: str
    time_range: str
    vo_snippet: str
    location: str
    hero_subject: str
    cast_spec: str = "none"  # "none" | "NEW: ..." | "SAME as SC01: ..."
    reference_scene_ids: list[str] = field(default_factory=list)
    camera_move: str = "push_in"
    exit_seam: str = "dark_opening"  # "leaves_wipe" | "dark_opening" | "white_flash" | "dust_smoke_cloud" | "edge_pass" | "final_hold"
    seam_color: str = "black"
    seam_prop: str = ""
    transition_mode: str = "seam"  # "seam" | "frame_link" | "soft_fade"
    video_model: str = "veo_3_1_lite"
    beat_role: str = "context"  # "hook" | "context" | "mechanism" | "twist" | "payoff" | "chapter_beat"
    lighting_key: str = "daylight"
    time_of_day: str = "midday"
    hero_count_phrase: str = ""
    hero_frame_region: str = "centered in the center third"
    person_count: int = 0
    secondary_motion: str = "subtle atmospheric air drift"
    same_world_continuous: bool = False
    scene_type: str = "live_action"  # "live_action" | "tactical_sand_table"
    delivery_mode: str = "narrative_cinema"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SceneMapEntry:
        return cls(
            scene_id=str(data["scene_id"]),
            time_range=str(data.get("time_range", "0-8s")),
            vo_snippet=str(data.get("vo_snippet", "")),
            location=str(data.get("location", "")),
            hero_subject=str(data.get("hero_subject", "")),
            cast_spec=str(data.get("cast_spec", "none")),
            reference_scene_ids=[str(x) for x in (data.get("reference_scene_ids") or [])],
            camera_move=str(data.get("camera_move", "push_in")),
            exit_seam=str(data.get("exit_seam", "dark_opening")),
            seam_color=str(data.get("seam_color", "black")),
            seam_prop=str(data.get("seam_prop", "")),
            transition_mode=str(data.get("transition_mode", "seam")),
            video_model=str(data.get("video_model", "veo_3_1_lite")),
            beat_role=str(data.get("beat_role", "context")),
            lighting_key=str(data.get("lighting_key", "daylight")),
            time_of_day=str(data.get("time_of_day", "midday")),
            hero_count_phrase=str(data.get("hero_count_phrase", "")),
            hero_frame_region=str(data.get("hero_frame_region", "centered in the center third")),
            person_count=int(data.get("person_count", 0)),
            secondary_motion=str(data.get("secondary_motion", "subtle atmospheric air drift")),
            same_world_continuous=bool(data.get("same_world_continuous", False)),
            scene_type=str(data.get("scene_type") or "live_action"),
            delivery_mode=str(data.get("delivery_mode") or "narrative_cinema"),
        )


@dataclass
class SceneMap:
    job_id: str
    channel_id: str
    format_profile: str = "short_9x16"
    clip_duration_sec: int = 8
    approved: bool = False
    scenes: list[SceneMapEntry] = field(default_factory=list)
    series_meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "channel_id": self.channel_id,
            "format_profile": self.format_profile,
            "clip_duration_sec": self.clip_duration_sec,
            "approved": self.approved,
            "series_meta": dict(self.series_meta),
            "scenes": [s.to_dict() for s in self.scenes],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SceneMap:
        return cls(
            job_id=str(data.get("job_id", "scene_map_job")),
            channel_id=str(data.get("channel_id", "ho_so_ky_la")),
            format_profile=str(data.get("format_profile", "short_9x16")),
            clip_duration_sec=int(data.get("clip_duration_sec", 8)),
            approved=bool(data.get("approved", False)),
            scenes=[SceneMapEntry.from_dict(s) for s in (data.get("scenes") or [])],
            series_meta=dict(data.get("series_meta") or {}),
        )

    def to_json_file(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def from_json_file(cls, path: str | Path) -> SceneMap:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def to_markdown_table(self) -> str:
        lines = [
            "| Scene | Time | VO | Location | Hero | Cast | Ref | Camera | Mode | Model | Exit Seam |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for s in self.scenes:
            refs = ",".join(s.reference_scene_ids) if s.reference_scene_ids else "none"
            lines.append(
                f"| {s.scene_id} | {s.time_range} | {s.vo_snippet[:38]} | {s.location} | "
                f"{s.hero_subject} | {s.cast_spec} | {refs} | {s.camera_move} | "
                f"{s.transition_mode} | {s.video_model} | {s.exit_seam} ({s.seam_color}) |"
            )
        return "\n".join(lines)


def _cast_signature(cast_spec: str) -> str:
    low = (cast_spec or "none").strip().lower()
    if low == "none" or not low:
        return "none"
    m = re.match(r"^(?:same\s+as\s+)([a-z0-9_-]+)", low)
    if m:
        return f"ref:{m.group(1)}"
    return low


def _casts_compatible_for_frame_link(scene_a: SceneMapEntry, scene_b: SceneMapEntry) -> bool:
    """Frame-Link is only safe if both scenes have no people OR share the same cast."""
    sig_a = _cast_signature(scene_a.cast_spec)
    sig_b = _cast_signature(scene_b.cast_spec)
    if sig_a == "none" and sig_b == "none":
        return True
    if sig_a == "none" or sig_b == "none":
        return False
    if sig_b.startswith(f"ref:{scene_a.scene_id.lower()}"):
        return True
    return scene_a.scene_id in scene_b.reference_scene_ids or (sig_a == sig_b and sig_a.startswith("ref:"))


def route_pair_transition_mode(
    scene_a: SceneMapEntry,
    scene_b: SceneMapEntry | None,
    channel_id: str,
    prefer_credit_saving: bool = True,
) -> tuple[str, str]:
    """Select optimal `(transition_mode, video_model)` balancing anti-morph quality & credits."""
    policy = get_channel_motion_policy(channel_id)
    default_mode = policy["default_transition_mode"]

    if scene_b is None or scene_a.exit_seam == "final_hold":
        return (default_mode, "veo_3_1_lite")

    if not policy["allow_exit_seams"]:
        return ("soft_fade", "veo_3_1_lite")

    same_light = (scene_a.lighting_key or "").lower() == (scene_b.lighting_key or "").lower()
    cast_ok = _casts_compatible_for_frame_link(scene_a, scene_b)
    want_frame_link = scene_a.same_world_continuous or scene_b.same_world_continuous or (not prefer_credit_saving)

    if want_frame_link and cast_ok and same_light:
        return ("frame_link", "omni_flash")

    return (default_mode, "veo_3_1_lite")


def apply_auto_routing(
    scene_map: SceneMap,
    prefer_credit_saving: bool = True,
) -> SceneMap:
    """Populate `transition_mode`, `video_model`, and safe `exit_seam` for every scene in place."""
    policy = get_channel_motion_policy(scene_map.channel_id)
    n = len(scene_map.scenes)
    for idx, sc in enumerate(scene_map.scenes):
        nxt = scene_map.scenes[idx + 1] if idx + 1 < n else None
        if nxt is None:
            sc.exit_seam = "final_hold"
            sc.seam_color = "none"
        mode, model = route_pair_transition_mode(sc, nxt, scene_map.channel_id, prefer_credit_saving=prefer_credit_saving)
        sc.transition_mode = mode
        sc.video_model = model
        if not policy["allow_exit_seams"] and sc.exit_seam != "final_hold":
            sc.exit_seam = "final_hold"
            sc.seam_color = "none"
    return scene_map


def resolve_channel_style_bible(channel_id: str) -> dict[str, str]:
    """Resolve channel visual Style Bible dynamically across all 38 VN/EN channels."""
    slug = channel_id.replace("_", "-")
    try:
        from channels.vn_flow_video_formulas import VN_FLOW_VIDEO_FORMULAS
        if channel_id in VN_FLOW_VIDEO_FORMULAS:
            entry = VN_FLOW_VIDEO_FORMULAS[channel_id]
            return {
                "label": str(entry.get("new_visual_label", channel_id)),
                "style_description": apply_positive_framing(str(entry.get("style_description", ""))),
                "continuity_anchor": apply_positive_framing(str(entry.get("continuity_anchor", ""))),
            }
    except Exception:
        pass

    try:
        from channels.en_flow_video_formulas import EN_FLOW_VIDEO_FORMULAS
        if channel_id in EN_FLOW_VIDEO_FORMULAS:
            entry = EN_FLOW_VIDEO_FORMULAS[channel_id]
            return {
                "label": str(entry.get("new_visual_label", channel_id)),
                "style_description": apply_positive_framing(str(entry.get("style_description", ""))),
                "continuity_anchor": apply_positive_framing(str(entry.get("continuity_anchor", ""))),
            }
    except Exception:
        pass

    try:
        from tools.story_driven_prompt_builder import CHANNEL_STYLE_PROFILES
        if slug in CHANNEL_STYLE_PROFILES:
            prof = CHANNEL_STYLE_PROFILES[slug]
            return {
                "label": prof.benchmark,
                "style_description": apply_positive_framing(f"{prof.style_prefix} {prof.aesthetic_traits}"),
                "continuity_anchor": apply_positive_framing(prof.aesthetic_traits),
            }
    except Exception:
        pass

    return {
        "label": channel_id,
        "style_description": "Clean documentary cinematography with crisp directional lighting and plain unmarked surfaces",
        "continuity_anchor": "Consistent optical depth-of-field and coherent atmospheric color grading",
    }


def validate_scene_map(scene_map: SceneMap) -> dict[str, Any]:
    """Validate Stage 1 Scene Map contracts and estimate dual-model Flow credit savings."""
    errors: list[str] = []
    warnings: list[str] = []
    policy = get_channel_motion_policy(scene_map.channel_id)
    scenes = scene_map.scenes

    if not scenes:
        errors.append("EMPTY_SCENE_MAP: SceneMap requires at least 1 scene")

    seen_ids: set[str] = set()
    veo_lite_clips = 0
    omni_clips = 0
    omni_clip_cost = 24 if scene_map.clip_duration_sec >= 8 else (18 if scene_map.clip_duration_sec >= 6 else 12)

    for idx, sc in enumerate(scenes):
        is_last = idx == len(scenes) - 1
        if sc.scene_id in seen_ids:
            errors.append(f"DUPLICATE_SCENE_ID: {sc.scene_id}")

        if idx == 0 and sc.reference_scene_ids:
            errors.append("SC01_REFERENCE_FORBIDDEN: first scene cannot attach earlier reference_scene_ids")

        if idx > 0 and len(scenes) >= 3 and sc.camera_move == scenes[idx - 1].camera_move:
            errors.append(
                f"CONSECUTIVE_CAMERA_DUPLICATE: {sc.scene_id} repeats camera_move={sc.camera_move!r} from {scenes[idx - 1].scene_id}"
            )

        if sc.person_count > 3:
            errors.append(f"CAST_OVERFLOW: {sc.scene_id} has {sc.person_count} individual people (max 3)")

        same_m = re.match(r"^\s*SAME\s+as\s+([A-Za-z0-9_-]+)", sc.cast_spec, re.IGNORECASE)
        if same_m:
            ref_id = same_m.group(1)
            if ref_id not in seen_ids:
                errors.append(f"INVALID_CAST_REF: {sc.scene_id} references {ref_id} before it appears")
            if ref_id not in sc.reference_scene_ids:
                errors.append(f"MISSING_REFERENCE_ATTACH: {sc.scene_id} repeats cast from {ref_id} without listing it in reference_scene_ids")

        for ref in sc.reference_scene_ids:
            if ref not in seen_ids:
                errors.append(f"FORWARD_REF: {sc.scene_id} attaches unseen reference {ref}")

        if is_last and sc.exit_seam != "final_hold":
            errors.append(f"FINAL_SCENE_HOLD_REQUIRED: final scene {sc.scene_id} must use exit_seam='final_hold'")

        if not is_last and not policy["allow_exit_seams"] and sc.exit_seam in ("white_flash", "edge_pass"):
            errors.append(
                f"COMFORT_POLICY_VIOLATION: {scene_map.channel_id} ({policy['archetype_id']}) forbids {sc.exit_seam} on {sc.scene_id}"
            )

        if sc.transition_mode == "frame_link":
            if "lite" in sc.video_model.lower():
                errors.append(f"FRAME_LINK_MODEL_MISMATCH: {sc.scene_id} cannot run frame_link on {sc.video_model}; use omni_flash")
            if not is_last and not _casts_compatible_for_frame_link(sc, scenes[idx + 1]):
                errors.append(
                    f"FRAME_LINK_CAST_MORPH_RISK: {sc.scene_id} -> {scenes[idx + 1].scene_id} changes cast; use Veo 3.1 Lite Seam mode"
                )
            if not is_last and (sc.lighting_key or "").lower() != (scenes[idx + 1].lighting_key or "").lower():
                warnings.append(
                    f"FRAME_LINK_LIGHTING_SHIFT: {sc.scene_id} ({sc.lighting_key}) -> {scenes[idx + 1].scene_id} ({scenes[idx + 1].lighting_key})"
                )

        if "lite" in sc.video_model.lower():
            veo_lite_clips += 1
        else:
            omni_clips += 1
        seen_ids.add(sc.scene_id)

    total_credits = veo_lite_clips * 10 + omni_clips * omni_clip_cost
    all_omni_credits = len(scenes) * omni_clip_cost
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "credit_summary": {
            "clip_count": len(scenes),
            "veo_lite_clips": veo_lite_clips,
            "omni_clips": omni_clips,
            "total_credits": total_credits,
            "all_omni_baseline_credits": all_omni_credits,
            "credits_saved": max(0, all_omni_credits - total_credits),
        },
    }


def compile_scene_image_prompts(
    scene_map: SceneMap,
    style_bible_override: str | None = None,
) -> list[dict[str, Any]]:
    """Stage 2: Compile ordered, positive-framing BELUGA image prompts using Channel Style Bible."""
    bible = resolve_channel_style_bible(scene_map.channel_id)
    style_block = apply_positive_framing(style_bible_override or bible["style_description"])
    aspect_label = "Vertical 9:16" if scene_map.format_profile == "short_9x16" else "Widescreen 16:9"
    compiled: list[dict[str, Any]] = []

    for sc in scene_map.scenes:
        parts: list[str] = []
        if sc.reference_scene_ids:
            parts.append(
                f"Using the attached reference image(s) ({', '.join(sc.reference_scene_ids)}), "
                f"keep the exact same subject and environment continuity: {sc.cast_spec}."
            )
        count_txt = sc.hero_count_phrase or f"One clear {sc.hero_subject}"
        is_portrait = scene_map.format_profile in ("short_9x16", "serialized_detail_short")
        if is_portrait:
            parts.append(
                f"Vertical 9:16 frame with key focal detail placed strictly between 20% and 65% of vertical frame height, "
                f"clear of lower caption band and bottom-right UI zone. {count_txt}, {sc.hero_frame_region}."
            )
        else:
            parts.append(f"{aspect_label} frame. {count_txt}, {sc.hero_frame_region}.")

        cast_low = (sc.cast_spec or "none").strip().lower()
        is_formation = any(kw in cast_low for kw in ("army", "troops", "rows", "fleet", "đoàn quân", "binh sĩ"))
        if sc.scene_type == "tactical_sand_table":
            parts.append(
                "Tactical Command Sand Table (practical 35mm photography): overhead 45-degree angle inside a dark timber war tent lit by warm 2200K oil-lamp lighting. "
                "Hand-molded wet earth and raw clay topography relief across the command table, populated with rough hand-carved plain unmarked vermilion and dark-indigo wooden troop blocks. "
                "A commander's weathered hand positions one wooden block across the sculpted clay relief, rendered with shallow 35mm cinema depth of field, authentic raw wood grain, and subtle floating dust motes. "
                "Strictly plain raw wet clay, coarse rough-hewn timber grain, and unmarked hand-carved wooden blocks throughout every visible surface."
            )
            if cast_low != "none":
                parts.append(f"Tactical staging detail: {sc.cast_spec}.")
        elif cast_low == "none" and sc.person_count == 0:
            parts.append("Block A Uninhabited Frame: pure physical subject and terrain with zero stray figures.")
        elif is_formation:
            parts.append(
                f"Block B Ensemble Formation: {sc.cast_spec}, arranged calmly in neat formed rows holding the lower half under open upper sky."
            )
        elif sc.person_count >= 2:
            parts.append(
                f"Block B Small Group: {sc.cast_spec}, grouped naturally inside one third of the frame with calm closed-mouth poses so clear camera travel space stays open."
            )
        else:
            parts.append(
                f"Block B Single Subject Framing: {sc.cast_spec}, positioned in the left or right third at mid-distance turned slightly across or away from camera, calm closed-mouth pose with relaxed hands so only the camera moves."
            )

        parts.append(f"Setting: {sc.location} during {sc.time_of_day} ({sc.lighting_key} lighting).")
        cam_rule = CAMERA_MOVES.get(sc.camera_move, CAMERA_MOVES["push_in"])["composition_rule"]
        parts.append(
            f"Composition & 3-Layer Depth: {cam_rule} Distinct foreground, midground, and background depth layers for clean parallax movement."
        )

        seam_spec = EXIT_SEAMS.get(sc.exit_seam)
        if seam_spec and sc.transition_mode == "seam":
            parts.append(f"Exit seam setup: {seam_spec['start_image_setup']}")

        parts.append(
            f"Channel style: {style_block}. Plain unmarked surfaces, authentic material grain, and generous breathing room."
        )
        prompt_txt = apply_positive_framing(" ".join(parts))

        compiled.append({
            "scene_id": sc.scene_id,
            "scene_type": sc.scene_type,
            "delivery_mode": sc.delivery_mode,
            "reference_scene_ids": list(sc.reference_scene_ids),
            "camera_move": sc.camera_move,
            "transition_mode": sc.transition_mode,
            "video_model": sc.video_model,
            "image_prompt": prompt_txt,
        })
    return compiled


_VESSEL_OR_RIVER_RE = re.compile(
    r"\b(?:river|ferry|barge|hull|fleet|estuary|junk)s?\b",
    re.IGNORECASE,
)


def compile_scene_video_prompts(scene_map: SceneMap) -> list[dict[str, Any]]:
    """Stage 2: Compile timecoded low-risk video prompts for each approved scene."""
    bible = resolve_channel_style_bible(scene_map.channel_id)
    lens_spec = get_channel_lens_spec(scene_map.channel_id)
    out: list[dict[str, Any]] = []
    n = len(scene_map.scenes)
    for idx, sc in enumerate(scene_map.scenes):
        nxt = scene_map.scenes[idx + 1] if idx + 1 < n else None
        is_sand_table = sc.scene_type == "tactical_sand_table"
        if is_sand_table:
            has_person = False
            anti_surfaces = "wooden command table, sculpted clay relief, and carved wooden blocks"
        else:
            has_person = sc.cast_spec.lower() != "none" or sc.person_count > 0
            if scene_map.channel_id == "su_ke_lai" and not _VESSEL_OR_RIVER_RE.search(
                f"{sc.location} {sc.hero_subject}"
            ):
                anti_surfaces = "timber fortifications, walls, banners, shields, and plain tunics"
            else:
                anti_surfaces = "masts, hulls, buildings, walls, and uniforms"
        prompt = build_timecoded_video_prompt(
            camera_move=sc.camera_move,
            hero_subject=sc.hero_subject,
            setting=sc.location,
            model=sc.video_model,
            clip_duration_sec=scene_map.clip_duration_sec,
            transition_mode=sc.transition_mode,
            exit_seam=sc.exit_seam,
            seam_prop=sc.seam_prop,
            beat_role=sc.beat_role,
            secondary_motion=sc.secondary_motion,
            has_person=has_person,
            next_subject=nxt.hero_subject if nxt else "",
            next_location=nxt.location if nxt else "",
            style_cue=bible["label"],
            anti_symbol_surfaces=anti_surfaces,
            lens_spec=lens_spec,
            scene_type=sc.scene_type,
        )
        out.append({
            "scene_id": sc.scene_id,
            "video_model": sc.video_model,
            "transition_mode": sc.transition_mode,
            "exit_seam": sc.exit_seam,
            "clip_duration_sec": scene_map.clip_duration_sec,
            "video_prompt": prompt,
        })
    return out
