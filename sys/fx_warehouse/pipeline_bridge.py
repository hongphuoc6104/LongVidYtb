"""Unified Pipeline Bridge for Modular Motion, 30fps HUD, GPU VFX & Procedural Audio.

Connects the sharded `sys/fx_warehouse/` architecture (`archetypes`, `camera_vfx`,
`hud_widgets`, `audio_sfx_bgm`, `selector`, `hud_forensic_v2`, `audio_suspense_v2`)
to the general Dual-Mode batch production script (`sys/tools/produce_vn_dual_mode.py`).
Supports two-tier branching:
1. Shared Production Spine -> Channel Niche Archetype Branch (`CHANNEL_ARCHETYPE_MAP`)
2. Per-Video / Per-Beat Topic & Bespoke Branch (`--video-topic`, trigger keywords,
   `bespoke_hud_spec`, `bespoke_sfx_spec`).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .archetypes import ARCHETYPE_PROFILES, CHANNEL_ARCHETYPE_MAP, resolve_niche_fx_blueprint
from .audio_sfx_bgm import BGM_DIR, SFX_DIR, ensure_warehouse_audio_assets, synthesize_bespoke_topic_sfx
from .audio_suspense_v2 import VARIANT_PROFILES
from .hud_forensic_v2 import FORENSIC_HUD_V2_CATALOG
from .selector import auto_select_beat_fx

FX_MODE_CHOICES: tuple[str, ...] = ("static", "auto_niche", "full_fx", "forensic_v2")

# Canonical user prompt keywords usable across ANY of the 20 channels.
TRIGGER_KEYWORD_TABLE: tuple[dict[str, Any], ...] = (
    {
        "id": "static_clean",
        "patterns": (r"\[static_clean\]", r"\bstatic_clean\b", r"\b2d_minimal\b", r"khung t[ĩi]nh"),
        "target_mode": "static",
        "allow_bespoke": False,
        "force_bespoke": False,
        "description": "Khóa khung tĩnh Lanczos + fade thuần 2D (tắt HUD/shader động).",
    },
    {
        "id": "forensic_v2",
        "patterns": (
            r"\[forensic_v2\]",
            r"\bforensic_v2\b",
            r"\bsuspense_v2\b",
            r"\bnoir_diorama\b",
            r"h[ồo] s[ơo] trinh th[áa]m",
            r"[âa]m thanh c[ăa]ng th[ẳa]ng",
        ),
        "target_mode": "forensic_v2",
        "allow_bespoke": True,
        "force_bespoke": False,
        "description": "Kích hoạt bộ HUD trinh thám v2 (9 widget) + audio_suspense_v2 (A/B/C).",
    },
    {
        "id": "full_fx",
        "patterns": (
            r"\[full_fx\]",
            r"\bfull_fx\b",
            r"\bhud_30fps\b",
            r"\bhud 30fps\b",
            r"\bmotion_graphic\b",
            r"\btelemetry_hud\b",
            r"\bsound_design_pro\b",
        ),
        "target_mode": "full_fx",
        "allow_bespoke": True,
        "force_bespoke": False,
        "description": "Bật full Motion 2.5D + 30fps HUD + GPU VFX + SFX/BGM theo ngách.",
    },
    {
        "id": "pro_fx",
        "patterns": (
            r"\[pro_fx\]",
            r"\bpro_fx\b",
            r"\bauto_niche\b",
            r"\bmotion_fx\b",
            r"2\.5d\s*parallax",
            r"d[ựu]ng chuy[êe]n nghi[ệe]p",
            r"hi[ệe]u [ứu]ng chuy[êe]n nghi[ệe]p",
        ),
        "target_mode": "auto_niche",
        "allow_bespoke": True,
        "force_bespoke": False,
        "description": "Tự rẽ nhánh ngách + kéo hiệu ứng thông minh từ kho chung cho mọi kênh.",
    },
    {
        "id": "bespoke_fx",
        "patterns": (
            r"\[bespoke_fx\]",
            r"\bbespoke_fx\b",
            r"\bbespoke_hud\b",
            r"\bbespoke_sfx\b",
            r"hi[ệe]u [ứu]ng ri[êe]ng",
            r"ch[ủu] [đd][ềe] ri[êe]ng",
        ),
        "target_mode": "full_fx",
        "allow_bespoke": True,
        "force_bespoke": True,
        "description": "Không ép dùng preset cũ; ép tổng hợp HUD/SFX riêng theo chủ đề video.",
    },
)


def _slugify(value: str, fallback: str = "bespoke_item") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower()).strip("_")
    return cleaned[:64] or fallback


def resolve_fx_intent_from_text(
    text: str,
    channel_id: str | None = None,
    requested_mode: str = "static",
) -> dict[str, Any]:
    """Parse universal cross-channel FX trigger keywords and respect niche comfort rules."""
    mode = requested_mode if requested_mode in FX_MODE_CHOICES else "static"
    norm_ch = (channel_id or "").strip().replace("-", "_")
    arch_id = CHANNEL_ARCHETYPE_MAP.get(norm_ch, "archetype_1_forensic_noir")

    matched_ids: list[str] = []
    allow_bespoke = mode != "static"
    force_bespoke = False
    inferred_mode = mode

    lowered = (text or "").strip().lower()
    if lowered:
        for rule in TRIGGER_KEYWORD_TABLE:
            if any(re.search(pat, lowered) for pat in rule["patterns"]):
                matched_ids.append(str(rule["id"]))
                if rule["id"] == "static_clean":
                    inferred_mode = "static"
                    allow_bespoke = False
                    force_bespoke = False
                    break
                if mode == "static":
                    inferred_mode = str(rule["target_mode"])
                if rule["allow_bespoke"]:
                    allow_bespoke = True
                if rule["force_bespoke"]:
                    force_bespoke = True
                    if inferred_mode == "auto_niche":
                        inferred_mode = "full_fx"

    effective_mode = mode if mode != "static" else inferred_mode

    comfort_downgraded = False
    if effective_mode == "forensic_v2" and arch_id == "archetype_5_mindful_healing":
        effective_mode = "auto_niche"
        comfort_downgraded = True

    return {
        "requested_mode": mode,
        "effective_mode": effective_mode,
        "channel_id": norm_ch,
        "archetype_id": arch_id,
        "matched_keywords": matched_ids,
        "allow_bespoke": allow_bespoke if effective_mode != "static" else False,
        "force_bespoke": force_bespoke if effective_mode != "static" else False,
        "comfort_downgraded": comfort_downgraded,
    }


def _build_bespoke_topic_fallback(
    beat_text: str,
    beat_idx: int,
    video_topic: str,
    blueprint: dict[str, Any],
) -> dict[str, Any]:
    """Synthesize a non-forced bespoke HUD + SFX bundle when `[BESPOKE_FX]` is requested."""
    ch_id = blueprint["channel_id"]
    kind = str(blueprint.get("preferred_bespoke_hud_kind") or "telemetry_card")
    topic_label = (video_topic or ch_id).strip()[:44] or ch_id
    excerpt = re.sub(r"\s+", " ", beat_text or "").strip()[:48]
    theme = "light" if blueprint["archetype_id"] == "archetype_4_doodle_explainer" else (
        "warm" if blueprint["archetype_id"] == "archetype_5_mindful_healing" else "dark"
    )
    return {
        "bespoke_hud_spec": {
            "kind": kind,
            "theme": theme,
            "accent_rgba": blueprint["accent_rgba"],
            "secondary_rgba": blueprint["secondary_rgba"],
            "title": topic_label.upper(),
            "subtitle": f"BEAT {beat_idx + 1:02d} • {excerpt}" if excerpt else f"BEAT {beat_idx + 1:02d}",
            "value": f"B{beat_idx + 1:02d}",
            "caption": blueprint["bespoke_synthesis_policy"][:72],
        },
        "bespoke_sfx_spec": {
            "name": f"{_slugify(ch_id)}_{_slugify(video_topic, 'topic')}_b{beat_idx + 1:02d}",
            "profile": blueprint.get("preferred_bespoke_sfx_profile", "forensic_pulse"),
            "duration": 0.9,
        },
    }


def plan_and_prepare_dual_mode_fx(
    channel_slug: str,
    beats: list[dict[str, Any]],
    beat_durations: list[float],
    work_dir: Path,
    fx_mode: str = "static",
    video_topic: str = "",
    spec_data: dict[str, Any] | None = None,
    prepare_audio_assets: bool = True,
) -> dict[str, Any]:
    """Plan Shared+Niche+Bespoke beat FX, prepare bespoke SFX WAVs, and write `fx_plan.json`.

    Preserves exact legacy behavior when `fx_mode == "static"` and no trigger keyword
    or spec `fx_mode` enables the warehouse.
    """
    spec = dict(spec_data or {})
    spec_mode = str(spec.get("fx_mode") or "").strip().lower()
    seed_mode = fx_mode if fx_mode != "static" else (spec_mode if spec_mode in FX_MODE_CHOICES else "static")
    topic_str = " ".join(
        p for p in (video_topic, str(spec.get("video_topic") or ""), str(spec.get("title") or "")) if p
    ).strip()

    channel_id = channel_slug.strip().replace("-", "_")
    intent = resolve_fx_intent_from_text(topic_str, channel_id=channel_id, requested_mode=seed_mode)
    eff_mode = intent["effective_mode"]

    work_dir.mkdir(parents=True, exist_ok=True)
    plan_path = work_dir / "fx_plan.json"

    if eff_mode == "static":
        static_summary: dict[str, Any] = {
            "schema_version": "vp_fx_plan_v1",
            "enabled": False,
            "fx_mode": "static",
            "channel_id": channel_id,
            "archetype_id": intent["archetype_id"],
            "matched_keywords": intent["matched_keywords"],
            "total_beats": len(beats),
            "hud_beats": 0,
            "bespoke_beats": 0,
            "bespoke_sfx_files": [],
            "fx_plan_path": str(plan_path.resolve()),
        }
        plan_path.write_text(json.dumps(static_summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return static_summary

    blueprint = resolve_niche_fx_blueprint(
        channel_id=channel_id,
        video_topic=topic_str,
        overrides=spec.get("fx_overrides") if isinstance(spec.get("fx_overrides"), dict) else None,
    )
    arch = ARCHETYPE_PROFILES[blueprint["archetype_id"]]

    if prepare_audio_assets:
        ensure_warehouse_audio_assets(force=False)

    bespoke_sfx_dir = work_dir / "fx_assets" / "bespoke_sfx"
    synthesized_sfx_paths: dict[str, str] = {}

    cue_beats: list[dict[str, Any]] = []
    hud_widgets_used: set[str] = set()
    sfx_used: set[str] = set()
    vfx_used: set[str] = set()
    cameras_used: set[str] = set()
    bespoke_beats = 0
    hud_beats = 0
    t_cur = 0.0

    for idx, beat in enumerate(beats):
        dur = float(beat_durations[idx]) if idx < len(beat_durations) else float(beat.get("duration") or 2.5)
        beat_text = str(beat.get("narration") or beat.get("text") or beat.get("visual_prompt") or "")
        beat_ovr = dict(beat.get("fx_overrides")) if isinstance(beat.get("fx_overrides"), dict) else None

        sel = auto_select_beat_fx(
            beat_text=beat_text,
            channel_id=channel_id,
            beat_index=idx,
            total_beats=len(beats),
            overrides=beat_ovr,
            video_topic=topic_str,
            allow_bespoke=intent["allow_bespoke"],
        )

        # In explicit bespoke mode, synthesize a topic-matched bespoke spec on key beats if needed.
        if intent["force_bespoke"] and not sel["bespoke_used"] and (not sel["hud"] or idx == 0):
            fb_ovr = _build_bespoke_topic_fallback(beat_text, idx, topic_str, blueprint)
            merged_ovr = {**(beat_ovr or {}), **fb_ovr}
            sel = auto_select_beat_fx(
                beat_text=beat_text,
                channel_id=channel_id,
                beat_index=idx,
                total_beats=len(beats),
                overrides=merged_ovr,
                video_topic=topic_str,
                allow_bespoke=True,
            )

        if sel["hud"]:
            hud_beats += 1
            hud_widgets_used.add(str(sel["hud"]))
        if sel["bespoke_used"]:
            bespoke_beats += 1
        sfx_name = str(sel["sfx"])
        sfx_used.add(sfx_name)
        vfx_used.add(str(sel["vfx"]))
        cameras_used.add(str(sel["camera"]))

        sfx_wav_path = str((SFX_DIR / sfx_name).resolve()) if (SFX_DIR / sfx_name).is_file() else ""
        if prepare_audio_assets and sel.get("bespoke_sfx_spec"):
            b_spec = dict(sel["bespoke_sfx_spec"])
            slug = _slugify(str(b_spec.get("name", f"bespoke_b{idx + 1}")))
            if slug not in synthesized_sfx_paths:
                out_wav = bespoke_sfx_dir / f"{slug}.wav"
                synthesize_bespoke_topic_sfx(b_spec, output_path=out_wav, seed=42 + idx)
                synthesized_sfx_paths[slug] = str(out_wav.resolve())
            sfx_wav_path = synthesized_sfx_paths[slug]

        # Annotate beat dictionary cleanly for downstream tools while keeping `camera_motion` backward-safe.
        beat["fx_selected"] = {
            "camera": sel["camera"],
            "vfx": sel["vfx"],
            "hud": sel["hud"],
            "sfx": sfx_name,
            "bespoke_used": sel["bespoke_used"],
        }

        cue_beats.append({
            "beat_index": idx,
            "t_start": round(t_cur, 4),
            "duration": round(dur, 4),
            "camera": sel["camera"],
            "vfx": sel["vfx"],
            "hud": sel["hud"],
            "sfx": sfx_name,
            "sfx_path": sfx_wav_path,
            "bespoke_used": sel["bespoke_used"],
            "bespoke_hud_spec": sel.get("bespoke_hud_spec"),
            "bespoke_sfx_spec": sel.get("bespoke_sfx_spec"),
        })
        t_cur += dur

    bgm_file = arch["default_bgm"]
    bgm_path = str((BGM_DIR / bgm_file).resolve()) if (BGM_DIR / bgm_file).is_file() else ""

    forensic_v2_info: dict[str, Any] = {"enabled": False}
    if eff_mode == "forensic_v2":
        variant = str(spec.get("suspense_variant") or "B").upper()
        if variant not in VARIANT_PROFILES:
            variant = "B"
        forensic_v2_info = {
            "enabled": True,
            "hud_catalog_count": len(FORENSIC_HUD_V2_CATALOG),
            "hud_widgets": sorted(FORENSIC_HUD_V2_CATALOG.keys()),
            "suspense_variant": variant,
            "suspense_profile_label": VARIANT_PROFILES[variant]["name"],
        }

    plan_payload: dict[str, Any] = {
        "schema_version": "vp_fx_plan_v1",
        "enabled": True,
        "fx_mode": eff_mode,
        "channel_id": channel_id,
        "archetype_id": blueprint["archetype_id"],
        "archetype_label": blueprint["archetype_label"],
        "video_topic": topic_str,
        "bgm_loop": bgm_file,
        "bgm_path": bgm_path,
        "disallowed_vfx": list(blueprint["disallowed_vfx"]),
        "matched_topic_triggers": list(blueprint["matched_topic_triggers"]),
        "matched_keywords": list(intent["matched_keywords"]),
        "comfort_downgraded": intent["comfort_downgraded"],
        "forensic_v2": forensic_v2_info,
        "stats": {
            "total_beats": len(beats),
            "hud_beats": hud_beats,
            "bespoke_beats": bespoke_beats,
            "unique_hud_widgets": sorted(hud_widgets_used),
            "unique_sfx": sorted(sfx_used),
            "unique_cameras": sorted(cameras_used),
            "unique_vfx": sorted(vfx_used),
        },
        "bespoke_sfx_files": sorted(synthesized_sfx_paths.values()),
        "beats": cue_beats,
        "fx_plan_path": str(plan_path.resolve()),
    }
    plan_path.write_text(json.dumps(plan_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "enabled": True,
        "fx_mode": eff_mode,
        "channel_id": channel_id,
        "archetype_id": blueprint["archetype_id"],
        "archetype_label": blueprint["archetype_label"],
        "bgm_loop": bgm_file,
        "total_beats": len(beats),
        "hud_beats": hud_beats,
        "bespoke_beats": bespoke_beats,
        "bespoke_sfx_files": sorted(synthesized_sfx_paths.values()),
        "matched_topic_triggers": list(blueprint["matched_topic_triggers"]),
        "matched_keywords": list(intent["matched_keywords"]),
        "disallowed_vfx": list(blueprint["disallowed_vfx"]),
        "forensic_v2": forensic_v2_info,
        "fx_plan_path": str(plan_path.resolve()),
    }
