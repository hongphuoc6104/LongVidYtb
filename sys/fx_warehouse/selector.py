"""Content-Aware AI Effect Selector & Bespoke Per-Video Router.

Routes beat-level narrative intent (`beat_text`, `video_topic`, `channel_id`) to
the shared sub-warehouses (`camera_vfx`, `hud_widgets`, `hud_forensic_v2`,
`audio_sfx_bgm`) while enforcing archetype comfort guardrails, static-camera
pin locks for radar/split/triptych beats, pause-tier cadence hints, and dynamic
`bespoke_hud_spec` / `bespoke_sfx_spec` generation.
"""
from __future__ import annotations

import re
from typing import Any

from .archetypes import (
    ARCHETYPE_PROFILES,
    CHANNEL_ARCHETYPE_MAP,
    get_channel_archetype,
    resolve_niche_fx_blueprint,
)
from .camera_vfx import get_camera_motion

STATIC_CAMERA_HUDS: frozenset[str] = frozenset({
    "radar_bezier_trajectory",
    "laser_split_screen",
    "triptych_3col_evidence",
    "calibrated_radar_overlay",
})

PAUSE_TIER_DURATIONS: dict[str, float] = {
    "T0": 0.14,  # Micro breath between rapid narrative clauses
    "T1": 0.28,  # Standard investigative / explanatory beat separation
    "T2": 0.45,  # Dramatic reveal / mechanical warning transition
    "T3": 0.65,  # Climax silence / fatal realization / closing verdict
}

_KW_SPLIT = re.compile(r"(so sánh|đối chiếu|trái ngược|ngược lại|khác với|chia đôi|hai mặt|thay vì|một bên|\bvs\b)")
_KW_TRIPTYCH = re.compile(r"(ba mắt xích|3 mắt xích|ba nguyên nhân|3 bước|ba yếu tố|3 quy luật|ba bài học|ba giai đoạn|3 lý do)")
_KW_VERDICT = re.compile(r"(phán quyết|kết luận|cải tổ|bài học lớn nhất|tóm lại|thay đổi vĩnh viễn)")
_KW_RADAR = re.compile(r"(bản đồ|radar|tọa độ|quỹ đạo|biển đông|eo biển|tuyến đường|bay qua|lộ trình|thành phố|thủ đô|quốc gia|biên giới|athens)")
_KW_CVR = re.compile(r"(hộp đen|\bcvr\b|đếm ngược|oxy não|90 giây|nhịp tim|sinh tồn)")
_KW_OSCILLOSCOPE = re.compile(r"(tần số|sóng âm|còi|âm thanh|báo động|trùng âm|nhầm còi)")
_KW_XRAY = re.compile(r"(cơ chế|x-ray|cấu tạo|bên trong|van điều áp|công tắc|mạch điện|tế bào|động cơ|chế độ|gạt sang|chỉnh tay)")
_KW_MINDFUL = re.compile(r"(chánh niệm|buông bỏ|tĩnh lặng|hơi thở|minh triết|đêm khuya|bình yên|thiền|chậm lại|tâm trí|thư thái)")
_KW_STAMP = re.compile(r"(hôn mê|thảm họa|tử vong|sai lầm|cảnh báo khẩn|sụp đổ|phá sản|nguy hiểm|mất kiểm soát|nghiêm trọng)")
_KW_DOSSIER = re.compile(r"(hồ sơ|tư liệu|nhân chứng|tài liệu mật|bằng chứng|tiếp viên|vụ án|điều tra|năm \d{4})")
_KW_STAT = re.compile(r"(\d+(?:[.,]\d+)?\s*(?:%|phần trăm|mét|m\b|km|tỷ|triệu|nghìn|độ c|giờ|phút|usd|đồng))")
_KW_HIGHLIGHT = re.compile(r"(quy tắc|mẹo|bí quyết|nguyên lý|điểm mấu chốt|từ khóa|ghi nhớ|tư duy|não bộ|thói quen|lãi kép)")


def _infer_bespoke_theme(arch_id: str) -> str:
    if arch_id == "archetype_4_doodle_explainer":
        return "light"
    if arch_id == "archetype_5_mindful_healing":
        return "warm"
    return "dark"


def _build_auto_bespoke_specs(
    beat_text: str,
    video_topic: str | None,
    blueprint: dict[str, Any],
    ovr: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    topic_label = (video_topic or beat_text or "CHUYÊN ĐỀ ĐẶC THÙ").strip()
    arch_id = blueprint["archetype_id"]
    theme = _infer_bespoke_theme(arch_id)

    hud_spec = dict(ovr.get("bespoke_hud_spec") or {})
    hud_spec.setdefault("is_bespoke", True)
    hud_spec.setdefault("kind", blueprint.get("preferred_bespoke_hud_kind", "telemetry_card"))
    hud_spec.setdefault("theme", theme)
    hud_spec.setdefault("kicker", f"{blueprint['channel_id'].upper()} • BESPOKE HUD")
    hud_spec.setdefault("headline", topic_label[:48])
    hud_spec.setdefault("subline", (beat_text or topic_label)[:58])
    hud_spec.setdefault("accent_rgba", blueprint["accent_rgba"])
    hud_spec.setdefault("secondary_rgba", blueprint["secondary_rgba"])
    hud_spec.setdefault("topic", topic_label)

    sfx_spec = dict(ovr.get("bespoke_sfx_spec") or {})
    sfx_spec.setdefault("is_bespoke", True)
    sfx_spec.setdefault("profile", blueprint.get("preferred_bespoke_sfx_profile", "forensic_pulse"))
    sfx_spec.setdefault("topic", topic_label)
    sfx_spec.setdefault("dur", 1.1)
    return hud_spec, sfx_spec


def _infer_hud_v2_hint(txt: str, hud: str, arch_id: str) -> str | None:
    """Return the relevant `hud_forensic_v2` widget hint for a beat, or None."""
    if arch_id == "archetype_5_mindful_healing":
        return None
    if hud in ("radar_bezier_trajectory", "calibrated_radar_overlay") or _KW_RADAR.search(txt):
        return "calibrated_radar_overlay"
    if _KW_OSCILLOSCOPE.search(txt) or re.search(r"(còi báo động|horn|cabin altitude)", txt):
        return "dual_horn_pulse"
    if _KW_CVR.search(txt) or re.search(r"(thiếu oxy|hypoxia|\btuc\b|bất tỉnh|oxy não)", txt):
        return "hypoxia_tuc_meter"
    if hud == "triptych_3col_evidence" or re.search(r"(swiss cheese|lỗ hổng|phòng tuyến|xuyên qua)", txt):
        return "swiss_cheese_align"
    if hud == "laser_split_screen" and (
        arch_id == "archetype_1_forensic_noir"
        or re.search(r"(thế hệ|chỉnh tay|tự động|\bclassic\b|\bng\b)", txt)
    ):
        return "classic_vs_ng_compare"
    if arch_id in ("archetype_1_forensic_noir", "archetype_3_science_cosmos", "archetype_2_power_history") and re.search(
        r"(áp suất|độ cao|cabin|\bpsi\b|\bfeet\b|\bft\b|chênh lệch|van điều áp|dump valve)", txt
    ):
        return "alt_pressure_divergence"
    if arch_id == "archetype_1_forensic_noir" and re.search(
        r"(nhiên liệu|hết xăng|cạn dầu|vùng tránh|holding|bay vòng|rơi xuống|chúi mũi)", txt
    ):
        return "fuel_avoidance_vector"
    if arch_id in ("archetype_1_forensic_noir", "archetype_2_power_history") and re.search(
        r"(^chương\s+\d+|mở màn|hồi kết|kết cục|\bchapter\b)", txt
    ):
        return "chapter_title_bumper"
    if arch_id == "archetype_1_forensic_noir" and hud in (
        "lemmino_dossier_card",
        "verdict_lower_third",
        "altitude_stat_counter",
        "xray_mode_switch_particles",
        "kinetic_stamp_slam",
    ):
        return "lemmino_hairline_hud"
    return None


def _infer_pause_tier(
    txt: str,
    hud: str,
    hud_v2_hint: str | None,
    beat_index: int,
    total_beats: int,
) -> tuple[str, float]:
    """Classify recommended post-beat breath duration into T0..T3 tiers."""
    if (
        _KW_STAMP.search(txt)
        or _KW_CVR.search(txt)
        or re.search(r"(im lặng hoàn toàn|bi kịch|tử nạn|kết thúc|không ai sống|ngừng thở|rơi tự do)", txt)
        or (total_beats >= 3 and beat_index == total_beats - 1)
    ):
        tier = "T3"
    elif (
        _KW_VERDICT.search(txt)
        or _KW_OSCILLOSCOPE.search(txt)
        or _KW_XRAY.search(txt)
        or hud_v2_hint in ("dual_horn_pulse", "hypoxia_tuc_meter", "swiss_cheese_align", "chapter_title_bumper")
        or hud in ("verdict_lower_third", "dual_oscilloscope_compare", "kinetic_stamp_slam")
    ):
        tier = "T2"
    elif hud in STATIC_CAMERA_HUDS or _KW_DOSSIER.search(txt) or _KW_STAT.search(txt) or hud_v2_hint is not None:
        tier = "T1"
    else:
        tier = "T0"
    return tier, PAUSE_TIER_DURATIONS[tier]


def auto_select_beat_fx(
    beat_text: str,
    channel_id: str,
    beat_index: int = 0,
    total_beats: int = 1,
    overrides: dict[str, Any] | None = None,
    video_topic: str | None = None,
    allow_bespoke: bool = True,
) -> dict[str, Any]:
    """Select the best camera, HUD, VFX, SFX & BGM—or generate bespoke specs when presets don't fit."""
    arch_id = get_channel_archetype(channel_id)
    arch = ARCHETYPE_PROFILES[arch_id]
    txt = (beat_text or "").lower().strip()
    ovr = dict(overrides or {})
    blueprint = resolve_niche_fx_blueprint(channel_id, video_topic=video_topic or beat_text, overrides=ovr)

    camera = arch["default_camera"]
    hud = "typewriter_telemetry_tag"
    vfx = arch["default_vfx"]
    sfx = "whoosh_soft.wav"
    matched_preset = True

    if _KW_SPLIT.search(txt):
        hud, camera, sfx = "laser_split_screen", "static_clean", "laser_split_whoosh.wav"
    elif _KW_TRIPTYCH.search(txt):
        hud, camera, sfx = "triptych_3col_evidence", "static_clean", "card_lock_thud.wav"
    elif _KW_VERDICT.search(txt):
        hud, camera, sfx = "verdict_lower_third", "parallax_push_in", "sub_bass_boom.wav"
    elif _KW_RADAR.search(txt):
        hud, camera, sfx = "radar_bezier_trajectory", "static_clean", "radar_sonar_ping.wav"
    elif _KW_CVR.search(txt):
        hud, camera, vfx, sfx = "countdown_cvr_waveform", "parallax_push_in", "hypoxic_vignette", "heartbeat_lub_dub.wav"
    elif _KW_OSCILLOSCOPE.search(txt):
        hud, camera, vfx, sfx = "dual_oscilloscope_compare", "parallax_pull_out", "chromatic_glitch_pulse", "caution_chime_double.wav"
    elif _KW_XRAY.search(txt):
        hud, camera, sfx = "xray_mode_switch_particles", "parallax_push_in", "rotary_switch_click.wav"
    elif _KW_MINDFUL.search(txt):
        hud, camera, vfx, sfx = "calligraphy_quote_dissolve", "breathing_drift", "warm_dust_motes", "singing_bowl_zen.wav"
    elif _KW_STAMP.search(txt):
        hud, camera, vfx, sfx = "kinetic_stamp_slam", "parallax_push_in", "camera_shake_impulse", "stamp_slam_hit.wav"
    elif _KW_DOSSIER.search(txt):
        hud, camera, sfx = "lemmino_dossier_card", "anamorphic_pan_lr", "dossier_slide_whoosh.wav"
    elif _KW_STAT.search(txt):
        hud, camera, sfx = "altitude_stat_counter", "parallax_push_in", "sub_bass_boom.wav"
    elif _KW_HIGHLIGHT.search(txt):
        hud, camera, sfx = "highlighter_stroke_bar", "breathing_drift", "pen_highlight.wav"
    elif arch_id == "archetype_4_doodle_explainer":
        hud, camera, sfx = "doodle_spring_pop_badge", "breathing_drift", "pop_clean.wav"
        matched_preset = False
    elif arch_id == "archetype_5_mindful_healing":
        hud, camera, sfx = "calligraphy_quote_dissolve", "breathing_drift", "singing_bowl_zen.wav"
        matched_preset = False
    elif total_beats >= 3 and beat_index == total_beats - 1:
        hud, camera, sfx = "verdict_lower_third", "parallax_push_in", "sub_bass_boom.wav"
    else:
        matched_preset = False

    has_explicit_bespoke = bool(ovr.get("bespoke_hud_spec") or ovr.get("bespoke_sfx_spec") or ovr.get("force_bespoke"))
    topic_triggers_bespoke = bool(video_topic) or bool(blueprint["matched_topic_triggers"])
    is_bespoke = bool(allow_bespoke and (has_explicit_bespoke or (topic_triggers_bespoke and not matched_preset)))

    bespoke_hud_spec: dict[str, Any] | None = None
    bespoke_sfx_spec: dict[str, Any] | None = None
    if is_bespoke:
        bespoke_hud_spec, bespoke_sfx_spec = _build_auto_bespoke_specs(beat_text, video_topic, blueprint, ovr)
        if "hud" not in ovr and (ovr.get("bespoke_hud_spec") or not matched_preset):
            hud = "bespoke_topic_hud"

    # Enforce archetype comfort guardrails unless caller explicitly overrides `vfx` or `allow_unsafe_vfx`
    if "vfx" not in ovr and not ovr.get("allow_unsafe_vfx", False):
        if vfx in arch["disallowed_vfx"]:
            vfx = arch["default_vfx"]

    chosen_hud = ovr.get("hud", hud)
    hud_v2_hint = ovr["hud_v2_hint"] if "hud_v2_hint" in ovr else _infer_hud_v2_hint(txt, str(chosen_hud), arch_id)

    # Lock camera to static_clean on anchored map/radar/split/triptych beats to eliminate pin drift
    if "camera" in ovr:
        chosen_camera = ovr["camera"]
    elif str(chosen_hud) in STATIC_CAMERA_HUDS or hud_v2_hint == "calibrated_radar_overlay":
        chosen_camera = "static_clean"
    else:
        chosen_camera = camera

    inferred_tier, inferred_pause = _infer_pause_tier(txt, str(chosen_hud), hud_v2_hint, beat_index, total_beats)
    pause_tier = str(ovr.get("pause_tier", inferred_tier))
    recommended_pause_sec = float(
        ovr.get("recommended_pause_sec", PAUSE_TIER_DURATIONS.get(pause_tier, inferred_pause))
    )

    result: dict[str, Any] = {
        "channel_id": channel_id,
        "archetype_id": arch_id,
        "camera": chosen_camera,
        "hud": chosen_hud,
        "vfx": ovr.get("vfx", vfx),
        "sfx": ovr.get("sfx", sfx),
        "bgm": ovr.get("bgm", arch["default_bgm"]),
        "accent_rgba": ovr.get("accent_rgba", arch["accent_rgba"]),
        "camera_params": get_camera_motion(chosen_camera),
        "is_bespoke": is_bespoke,
        "bespoke_used": is_bespoke,
        "pause_tier": pause_tier,
        "recommended_pause_sec": recommended_pause_sec,
        "hud_v2_hint": hud_v2_hint,
    }
    if bespoke_hud_spec is not None:
        result["bespoke_hud_spec"] = bespoke_hud_spec
    if bespoke_sfx_spec is not None:
        result["bespoke_sfx_spec"] = bespoke_sfx_spec
    return result
