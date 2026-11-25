"""Multi-Archetype & Bilingual (VI/EN) V4 Short Packs, Spec Scaffolder & VN->EN Twin Cloner.

Generalizes `su_ke_lai`'s proven V4 Viral Breakout Short Engine (`viral_fast_loop_short`
and `serialized_detail_short`) across all 38 physical channels (20 VN + 18 EN) grouped
under the 5 Niche Archetypes without duplicating engine code per channel.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from channels.lifecycle_ssot import (
    get_twin_channel_id,
    get_wave_for_channel,
    resolve_canonical_channel_id,
)
from channels.registry import get_channel
from fx_warehouse.archetypes import get_channel_archetype

SYS_DIR = Path(__file__).resolve().parents[1]

CLEAR_AIR_DIRECTIVE = (
    "crisp optical clarity, deep-focus lens depth, dramatic directional key lighting, "
    "clean focal subject with >=60% negative space, zero text in frame."
)

SEAM_ROTATION: tuple[str, ...] = (
    "edge_pass",
    "dark_opening",
    "leaves_wipe",
    "white_flash",
    "final_hold",
)

CAMERA_ROTATION: tuple[str, ...] = (
    "push_in",
    "pull_back",
    "truck_lateral",
    "tracking_alongside",
    "crane_up",
    "orbit",
)

FORBIDDEN_TITLE_PREFIX_RE = re.compile(
    r"^\s*(?:P\d+|Phần\s*\d+|Tập\s*\d+|Part\s*\d+|Ep\.?\s*\d+)\s*[:\-–—]?\s*",
    re.IGNORECASE,
)

ARCHETYPE_SHORT_THEMES: dict[str, dict[str, Any]] = {
    "su_ke_lai": {
        "theme_id": "heroic_vietnam_epic",
        "bgm_mode": "heroic_vietnam_epic",
        "primary_bgm": "bgm_geopolitics_pulse.wav",
        "secondary_bgm": "bgm_forensic_noir_drone.wav",
        "vacuum_stem": "heartbeat_lub_dub.wav",
        "banner_bar_rgba": (198, 44, 34, 245),
        "banner_accent_rgba": (255, 216, 102, 255),
        "default_speaking_rate": 1.30,
    },
    "archetype_1_forensic_noir": {
        "theme_id": "forensic_noir_suspense",
        "bgm_mode": "archetype_dual_5act",
        "primary_bgm": "bgm_forensic_noir_drone.wav",
        "secondary_bgm": "bgm_geopolitics_pulse.wav",
        "vacuum_stem": "heartbeat_lub_dub.wav",
        "banner_bar_rgba": (205, 52, 48, 245),
        "banner_accent_rgba": (212, 168, 72, 255),
        "default_speaking_rate": 1.14,
    },
    "archetype_2_geopolitics_history": {
        "theme_id": "geopolitical_strategic_pulse",
        "bgm_mode": "archetype_dual_5act",
        "primary_bgm": "bgm_geopolitics_pulse.wav",
        "secondary_bgm": "bgm_forensic_noir_drone.wav",
        "vacuum_stem": "heartbeat_lub_dub.wav",
        "banner_bar_rgba": (180, 132, 42, 245),
        "banner_accent_rgba": (32, 212, 248, 255),
        "default_speaking_rate": 1.18,
    },
    "archetype_3_science_xray": {
        "theme_id": "scifi_biotech_xray",
        "bgm_mode": "archetype_dual_5act",
        "primary_bgm": "bgm_scifi_biotech_pad.wav",
        "secondary_bgm": "bgm_geopolitics_pulse.wav",
        "vacuum_stem": "heartbeat_lub_dub.wav",
        "banner_bar_rgba": (18, 152, 190, 245),
        "banner_accent_rgba": (255, 216, 102, 255),
        "default_speaking_rate": 1.15,
    },
    "archetype_4_doodle_explainer": {
        "theme_id": "curious_explainer_momentum",
        "bgm_mode": "archetype_dual_5act",
        "primary_bgm": "bgm_curious_acoustic_loop.wav",
        "secondary_bgm": "bgm_scifi_biotech_pad.wav",
        "vacuum_stem": "clock_tick.wav",
        "banner_bar_rgba": (42, 108, 184, 245),
        "banner_accent_rgba": (245, 158, 11, 255),
        "default_speaking_rate": 1.16,
    },
    "archetype_5_mindful_healing": {
        "theme_id": "zen_reflective_swell",
        "bgm_mode": "archetype_dual_5act",
        "primary_bgm": "bgm_zen_night_healing.wav",
        "secondary_bgm": "bgm_zen_night_healing.wav",
        "vacuum_stem": "singing_bowl_zen.wav",
        "banner_bar_rgba": (148, 116, 68, 245),
        "banner_accent_rgba": (232, 200, 142, 255),
        "default_speaking_rate": 1.04,
    },
}


@dataclass(frozen=True)
class ChannelShortPack:
    """Resolved Short V4 production pack for any of the 38 channels."""

    channel_id: str
    channel_name: str
    language: str
    archetype_id: str
    rollout_wave: str
    twin_channel_id: str
    theme_id: str
    bgm_mode: str
    primary_bgm: str
    secondary_bgm: str
    vacuum_stem: str
    banner_bar_rgba: tuple[int, int, int, int]
    banner_accent_rgba: tuple[int, int, int, int]
    default_speaking_rate: float
    voice_id: str
    voice_dir: Path
    watermark_path: Path
    visual_style_lock: str


def _load_channel_lock_json(channel_id: str) -> dict[str, Any]:
    for cand in (
        SYS_DIR / "channels" / channel_id / "channel_v2_production_lock.json",
        SYS_DIR / "channels" / channel_id.replace("_", "-") / "channel_v2_production_lock.json",
    ):
        if cand.is_file():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


def get_channel_short_pack(channel_id: str) -> ChannelShortPack:
    """Resolve complete V4 Short pack (archetype BGM, banner palette, voice, watermark, style)."""
    cid = resolve_canonical_channel_id(channel_id)
    reg = get_channel(cid)
    archetype_id = get_channel_archetype(cid)
    theme_key = "su_ke_lai" if cid == "su_ke_lai" else archetype_id
    theme = ARCHETYPE_SHORT_THEMES.get(theme_key, ARCHETYPE_SHORT_THEMES["archetype_4_doodle_explainer"])

    lock_data = _load_channel_lock_json(cid)
    vg = lock_data.get("visual_grammar") if isinstance(lock_data.get("visual_grammar"), dict) else {}
    style_desc = str(vg.get("visual_style_lock") or reg.visual.style_description or "").strip()
    if "zero text in frame" not in style_desc.lower():
        style_desc = f"{style_desc}, {CLEAR_AIR_DIRECTIVE}" if style_desc else CLEAR_AIR_DIRECTIVE

    voice_dir = SYS_DIR / "assets" / "voices" / f"ch_{cid}"
    watermark_path = SYS_DIR / "channels" / cid / "assets" / "watermark_150x150.png"
    if not watermark_path.is_file():
        alt_wm = SYS_DIR / "channels" / cid.replace("_", "-") / "assets" / "watermark_150x150.png"
        if alt_wm.is_file():
            watermark_path = alt_wm

    lang = "en" if cid.startswith("en_") else "vi"
    voice_id = f"VietNarrator_{cid}" if lang == "vi" else f"EnNarrator_{cid}"

    return ChannelShortPack(
        channel_id=cid,
        channel_name=reg.name,
        language=lang,
        archetype_id=archetype_id,
        rollout_wave=get_wave_for_channel(cid),
        twin_channel_id=get_twin_channel_id(cid),
        theme_id=theme["theme_id"],
        bgm_mode=theme["bgm_mode"],
        primary_bgm=theme["primary_bgm"],
        secondary_bgm=theme["secondary_bgm"],
        vacuum_stem=theme["vacuum_stem"],
        banner_bar_rgba=tuple(theme["banner_bar_rgba"]),
        banner_accent_rgba=tuple(theme["banner_accent_rgba"]),
        default_speaking_rate=float(lock_data.get("speaking_rate") or theme["default_speaking_rate"]),
        voice_id=voice_id,
        voice_dir=voice_dir,
        watermark_path=watermark_path,
        visual_style_lock=style_desc,
    )


def default_bgm_plan_for_channel(channel_id: str, beats: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a 5-Act BGM & silence-vacuum plan tailored to the channel's archetype."""
    pack = get_channel_short_pack(channel_id)
    beat_ids = [str(b.get("beat_id") or f"B{idx:02d}") for idx, b in enumerate(beats)]
    n = len(beat_ids)
    vac_idx = max(0, int(round(n * 0.65)) - 1) if n >= 4 else 0
    vac_bid = beat_ids[vac_idx] if beat_ids else "B00"
    climax_start = min(n - 1, vac_idx + 1) if n >= 2 else 0
    climax_end = max(climax_start, int(round(n * 0.85)) - 1) if n >= 3 else climax_start
    climax_beats = beat_ids[climax_start : climax_end + 1]
    proud_beats = beat_ids[climax_end + 1 :] if climax_end + 1 < n else ([beat_ids[-1]] if beat_ids else [])

    act_dynamics: list[dict[str, Any]] = []
    if n >= 6:
        mid_a = beat_ids[0]
        mid_b = beat_ids[max(0, climax_start - 1)]
        hi_a = beat_ids[climax_start]
        hi_b = beat_ids[-1]
        act_dynamics = [
            {"beats": f"{mid_a}-{mid_b}", "bgm": pack.secondary_bgm, "role": "tension_setup"},
            {"beats": f"{hi_a}-{hi_b}", "bgm": pack.primary_bgm, "role": "climax_and_payoff"},
        ]

    return {
        "mode": pack.bgm_mode,
        "theme_id": pack.theme_id,
        "primary_bgm": pack.primary_bgm,
        "secondary_bgm": pack.secondary_bgm,
        "speech_level_db": -17.5 if pack.bgm_mode == "heroic_vietnam_epic" else -22.5,
        "pause_level_db": -12.5 if pack.bgm_mode == "heroic_vietnam_epic" else -16.5,
        "silence_vacuum": {
            "beat_id": vac_bid,
            "heartbeat_stem": pack.vacuum_stem,
        },
        "climax_beats": climax_beats,
        "proud_beats": proud_beats,
        "act_dynamics": act_dynamics,
    }


def _slugify_ascii(text: str) -> str:
    import unicodedata

    norm = unicodedata.normalize("NFKD", text or "")
    ascii_only = "".join(ch for ch in norm if not unicodedata.combining(ch))
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_only).strip("_").lower()
    return slug[:36] or "topic"


def _clamp_youtube_title(raw_title: str, *, suffix: str = " #Shorts", max_chars: int = 55) -> str:
    clean = FORBIDDEN_TITLE_PREFIX_RE.sub("", str(raw_title or "").strip())
    clean = re.sub(r"#shorts\b", "", clean, flags=re.IGNORECASE).strip(" :|-")
    budget = max(12, max_chars - len(suffix))
    if len(clean) > budget:
        words = clean[:budget].rsplit(" ", 1)[0].strip()
        clean = words or clean[:budget].strip()
    return f"{clean}{suffix}".strip()


def build_v4_short_spec_scaffold(
    channel_id: str,
    topic_title: str,
    *,
    format_profile: str = "viral_fast_loop_short",
    job_id: str | None = None,
    hook_line: str = "",
    option_a: str = "",
    option_b: str = "",
    series_id: str = "",
    series_title: str = "",
    series_order: int = 0,
    series_total: int = 0,
) -> dict[str, Any]:
    """Create a complete V4 Short `short_spec.json` scaffold for ANY of the 38 channels."""
    pack = get_channel_short_pack(channel_id)
    fmt = str(format_profile or "viral_fast_loop_short").strip()
    if fmt not in ("viral_fast_loop_short", "serialized_detail_short"):
        fmt = "viral_fast_loop_short"

    n_beats = 16 if fmt == "viral_fast_loop_short" else 20
    est_beat_sec = 3.8 if fmt == "viral_fast_loop_short" else 5.4
    prefix = "en" if pack.language == "en" else "vn"
    eff_job_id = job_id or f"{prefix}_{pack.channel_id}_{_slugify_ascii(topic_title)}_v4_short"
    yt_title = _clamp_youtube_title(topic_title)
    is_en = pack.language == "en"

    default_hook = (
        hook_line.strip()
        or (
            f"Wait—why did {topic_title.split(':')[0].strip()} actually happen?"
            if is_en
            else f"Khoan đã—sự thật đằng sau {topic_title.split(':')[0].strip()} là gì?"
        )
    )
    default_hook = re.sub(r"\[pause:[^\]]+\]", " ", default_hook).strip()
    hook_words = default_hook.split()
    if len(hook_words) > 18:
        default_hook = " ".join(hook_words[:16])

    opt_a = option_a.strip() or ("Factor A (Hidden mechanics)" if is_en else "Yếu tố A (Cơ chế ngầm)")
    opt_b = option_b.strip() or ("Factor B (Human decision)" if is_en else "Yếu tố B (Quyết định con người)")
    debate_question = (
        f"In your view, what drove the outcome: (A) {opt_a} or (B) {opt_b}?"
        if is_en
        else f"Theo bạn, điều gì quyết định cục diện: (A) {opt_a} hay (B) {opt_b}?"
    )

    beats: list[dict[str, Any]] = []
    hud_stamps: list[dict[str, Any]] = []
    cur_t = 0.0
    for idx in range(n_beats):
        bid = f"B{idx:02d}"
        frac = idx / float(max(1, n_beats - 1))
        if idx == 0:
            act, role, deliv = 1, "hook", "punchy_hook"
        elif frac < 0.35:
            act, role, deliv = 2, "context", "tactical_breakdown"
        elif frac < 0.65:
            act, role, deliv = 3, "mechanism", "tactical_breakdown"
        elif frac < 0.85:
            act, role, deliv = 4, "climax", "climax_surge"
        else:
            act, role, deliv = 5, "payoff", "reflective_lesson"

        is_live_video = (idx == 0) or (act == 4) or (idx % 5 in (0, 1, 3))
        asset_override = "flow_video" if is_live_video else "2k_native_kenburns"
        seam_idx = idx % (len(SEAM_ROTATION) - 1)
        exit_seam = "final_hold" if idx == n_beats - 1 else SEAM_ROTATION[seam_idx]
        cam = CAMERA_ROTATION[idx % len(CAMERA_ROTATION)]

        if idx == 0:
            spoken = default_hook
            banner_txt = " ".join(re.sub(r"[^\w\s]", "", topic_title).upper().split()[:3]) or "TRUTH REVEALED"
            hud_stamps.append({
                "beat_id": bid,
                "kind": "heroic_banner",
                "headline": banner_txt,
                "font_size": 136,
                "anchor_y": 150,
                "bar_rgba": list(pack.banner_bar_rgba),
                "accent_rgba": list(pack.banner_accent_rgba),
            })
        elif idx == n_beats - 1:
            spoken = debate_question
            hud_stamps.append({
                "beat_id": bid,
                "kind": "heroic_banner",
                "headline": "CHOOSE A OR B" if is_en else "CHỌN A HAY B",
                "font_size": 136,
                "anchor_y": 150,
                "bar_rgba": list(pack.banner_bar_rgba),
                "accent_rgba": list(pack.banner_accent_rgba),
            })
        elif idx == int(round(n_beats * 0.65)) - 1:
            spoken = (
                f"Everything shifted in one crucial moment. [pause:500ms] Notice the turning point in {topic_title}."
                if is_en
                else f"Mọi thứ xoay trục ngay khoảnh khắc quyết định. [pause:500ms] Hãy nhìn điểm bùng nổ của {topic_title}."
            )
        else:
            spoken = (
                f"Scene {idx + 1} reveals the hidden constraint behind {topic_title}."
                if is_en
                else f"Nhịp {idx + 1} bóc tách mắt xích ẩn đằng sau {topic_title}."
            )

        clean_display = re.sub(r"\[pause:[^\]]+\]", "", spoken).strip()
        beats.append({
            "beat_id": bid,
            "act": act,
            "role": role,
            "beat_role": role,
            "delivery_mode": deliv,
            "scene_type": "live_action",
            "asset_mode_override": asset_override,
            "camera_move": cam,
            "exit_seam": exit_seam,
            "transition_mode": "frame_link" if (idx > 0 and idx % 4 == 2 and is_live_video) else "seam_mode",
            "start_sec": round(cur_t, 3),
            "end_sec": round(cur_t + est_beat_sec, 3),
            "duration_sec": est_beat_sec,
            "display_text": clean_display,
            "tts_text": spoken,
            "visual_prompt": (
                f"{pack.visual_style_lock} Visual focus for beat {bid} ({role}) of '{topic_title}'. "
                "9:16 vertical composition, clean central hero subject inside 20%-65% safe zone."
            ),
        })
        cur_t += est_beat_sec

    bgm_plan = default_bgm_plan_for_channel(pack.channel_id, beats)
    spec_out: dict[str, Any] = {
        "schema_version": "4.0",
        "job_id": eff_job_id,
        "channel_id": pack.channel_id,
        "channel_name": pack.channel_name,
        "language": pack.language,
        "archetype_id": pack.archetype_id,
        "rollout_wave": pack.rollout_wave,
        "twin_channel_id": pack.twin_channel_id,
        "format_profile": fmt,
        "visual_mode": "hybrid_2k",
        "render_mode": "single_pass",
        "youtube_title": yt_title,
        "base_omnivoice_speed": 1.06 if pack.language == "en" else 1.12,
        "visual_style_lock": pack.visual_style_lock,
        "watermark_path": str(pack.watermark_path.relative_to(SYS_DIR.parent))
        if pack.watermark_path.is_file()
        else "",
        "bgm_plan": bgm_plan,
        "hud_stamps": hud_stamps,
        "cta_plan": {
            "bridge": "",
            "close": debate_question,
            "pinned_comment": debate_question,
            "option_a": opt_a,
            "option_b": opt_b,
        },
        "pinned_comment": debate_question,
        "beats": beats,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    clean_sid = str(series_id or "").strip()
    clean_stitle = str(series_title or "").strip()
    if clean_sid or clean_stitle:
        eff_sid = clean_sid or f"{pack.channel_id}_{_slugify_ascii(clean_stitle)}"
        spec_out["series_id"] = eff_sid
        spec_out["series_title"] = clean_stitle or eff_sid
        spec_out["series_order"] = int(series_order or 0)
        spec_out["series_total"] = int(series_total or 0)
    return spec_out


def validate_v4_short_spec(short_spec: dict[str, Any]) -> list[str]:
    """Validate adherence to the 5 Viral V4 Short Laws regardless of channel/language."""
    errors: list[str] = []
    title = str(short_spec.get("youtube_title") or "").strip()
    if not title:
        errors.append("MISSING_YOUTUBE_TITLE")
    else:
        if len(title) > 55:
            errors.append(f"TITLE_TOO_LONG:{len(title)}>55")
        if FORBIDDEN_TITLE_PREFIX_RE.match(title):
            errors.append("FORBIDDEN_SERIAL_PREFIX_IN_TITLE")

    beats = list(short_spec.get("beats") or [])
    if len(beats) < 12:
        errors.append(f"TOO_FEW_BEATS:{len(beats)}<12")
    else:
        b0_tts = str(beats[0].get("tts_text") or beats[0].get("display_text") or "")
        if "[pause:" in b0_tts.lower():
            errors.append("PAUSE_FORBIDDEN_IN_B00_HOOK")
        if len(b0_tts.split()) > 18:
            errors.append(f"B00_HOOK_TOO_LONG:{len(b0_tts.split())}>18_words")

    smoke_count = sum(1 for b in beats if str(b.get("exit_seam") or "").strip() == "dust_smoke_cloud")
    if smoke_count > 1:
        errors.append(f"TOO_MANY_SMOKE_SEAMS:{smoke_count}>1")

    for st in short_spec.get("hud_stamps") or []:
        if str(st.get("kind") or "heroic_banner") == "heroic_banner":
            words = str(st.get("headline") or "").strip().split()
            if not (1 <= len(words) <= 4):
                errors.append(f"BANNER_WORD_COUNT_INVALID:{len(words)}")
            if int(st.get("font_size") or 136) < 132:
                errors.append(f"BANNER_FONT_TOO_SMALL:{st.get('font_size')}")

    pinned = str(short_spec.get("pinned_comment") or (short_spec.get("cta_plan") or {}).get("pinned_comment") or "").strip()
    if not pinned:
        errors.append("MISSING_DEBATE_PINNED_COMMENT")
    return errors


def clone_vn_short_spec_to_en_twin(
    vn_spec: dict[str, Any],
    *,
    target_en_channel_id: str | None = None,
    translated_title: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Clone a proven VN V4 Short spec onto its symmetric EN twin channel."""
    src_cid = resolve_canonical_channel_id(str(vn_spec.get("channel_id") or ""))
    en_cid = resolve_canonical_channel_id(target_en_channel_id or get_twin_channel_id(src_cid))
    if not en_cid or not en_cid.startswith("en_"):
        raise ValueError(f"Could not resolve English twin channel for {src_cid!r} -> {en_cid!r}")

    en_pack = get_channel_short_pack(en_cid)
    cloned = copy.deepcopy(vn_spec)
    src_title = str(vn_spec.get("youtube_title") or vn_spec.get("job_id") or "Mystery Explained")
    new_title = _clamp_youtube_title(translated_title or src_title)
    new_job_id = job_id or f"en_{en_cid}_{_slugify_ascii(new_title)}_v4_short"

    cloned["schema_version"] = "4.0"
    cloned["job_id"] = new_job_id
    cloned["channel_id"] = en_pack.channel_id
    cloned["channel_name"] = en_pack.channel_name
    cloned["language"] = "en"
    cloned["archetype_id"] = en_pack.archetype_id
    cloned["rollout_wave"] = en_pack.rollout_wave
    cloned["twin_channel_id"] = src_cid
    cloned["cloned_from_vn"] = {
        "source_channel_id": src_cid,
        "source_job_id": str(vn_spec.get("job_id") or ""),
        "source_title": src_title,
        "cloned_at": datetime.now(timezone.utc).isoformat(),
    }
    cloned["youtube_title"] = new_title
    if vn_spec.get("series_id"):
        src_sid = str(vn_spec["series_id"]).strip()
        cloned["series_id"] = src_sid if src_sid.endswith("_en") else f"{src_sid}_en"
        if vn_spec.get("series_title"):
            cloned["series_title"] = f"{str(vn_spec['series_title']).strip()} (EN)"
        cloned["series_order"] = int(vn_spec.get("series_order") or 0)
        cloned["series_total"] = int(vn_spec.get("series_total") or 0)
    cloned["visual_style_lock"] = en_pack.visual_style_lock
    cloned["base_omnivoice_speed"] = 1.06
    cloned["watermark_path"] = (
        str(en_pack.watermark_path.relative_to(SYS_DIR.parent))
        if en_pack.watermark_path.is_file()
        else ""
    )

    beats = list(cloned.get("beats") or [])
    cloned["bgm_plan"] = default_bgm_plan_for_channel(en_pack.channel_id, beats)
    for beat in beats:
        bid = str(beat.get("beat_id") or "")
        beat["visual_prompt"] = (
            f"{en_pack.visual_style_lock} Beat {bid} scene adaptation for '{new_title}'. "
            "9:16 vertical frame, clear central focal subject, zero text in frame."
        )
        beat["needs_en_localization"] = True

    for stamp in cloned.get("hud_stamps") or []:
        if str(stamp.get("kind") or "heroic_banner") == "heroic_banner":
            stamp["bar_rgba"] = list(en_pack.banner_bar_rgba)
            stamp["accent_rgba"] = list(en_pack.banner_accent_rgba)

    return cloned
