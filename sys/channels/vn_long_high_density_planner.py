"""Vietnamese High-Density Long (16:9) Blueprint Planner & Two-Tier Visual-State DAG Engine.

Structures 8m30s – 13m00s (510s – 780s) Vietnamese Long 16:9 explainer videos across
8–12 YouTube chapters into the empirically proven Two-Tier 240–350 Visual-State DAG
tailored per Vietnamese channel niche across all 20 VN channels.
"""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from visual_pacing import check_see_say_beat_density, check_tempo_beats  # noqa: E402


class VisualEventKind(str, Enum):
    """Explicit See-Say visual event types for high-density long-form storytelling."""

    ANCHOR_ESTABLISH = "ANCHOR_ESTABLISH"  # based_on=None, new diorama/environment
    ENUMERATION_BURST = "ENUMERATION_BURST"  # 0.8s-1.6s, based_on=anchor, lights up list item
    MECHANISM_STEP_BUILD = "MECHANISM_STEP_BUILD"  # 1.6s-2.6s, based_on=anchor, reaction/cross-section
    ANGLE_CUTAWAY = "ANGLE_CUTAWAY"  # 1.3s-2.2s, based_on=anchor, Wide -> ECU -> Over-shoulder
    SPATIAL_COGNITIVE_HOLD = "SPATIAL_COGNITIVE_HOLD"  # 3.8s-6.5s, max 8% of beats, slow 2x-zoompan orbit


CAMERA_MOVES: tuple[str, ...] = (
    "zoom_in",
    "pan_right",
    "pan_up",
    "zoom_out",
    "pan_left",
    "pan_down",
    "orbit_cw",
    "static",
    "orbit_ccw",
)

DIRECTIONAL_XFADE_MAP: dict[str, str] = {
    "pan_right": "smoothright",
    "pan_left": "smoothleft",
    "pan_up": "smoothup",
    "pan_down": "smoothdown",
    "zoom_in": "fade",
    "zoom_out": "fade",
    "orbit_cw": "dissolve",
    "orbit_ccw": "dissolve",
    "static": "cut",
}

CONFLICTING_TRANSITIONS: dict[str, set[str]] = {
    "pan_right": {"smoothleft"},
    "pan_left": {"smoothright"},
    "pan_up": {"smoothdown"},
    "pan_down": {"smoothup"},
}


@dataclass(frozen=True)
class VNLongDensityProfile:
    """Channel niche density profile for 8m30s - 13m00s Vietnamese long 16:9 videos."""

    channel_id: str
    archetype: str
    target_states_range: Tuple[int, int]
    target_avg_hold_range: Tuple[float, float]
    tier1_anchors_range: Tuple[int, int]
    tier2_builds_range: Tuple[int, int]
    target_chapters_range: Tuple[int, int] = (8, 12)
    duration_seconds_range: Tuple[float, float] = (510.0, 780.0)
    max_spatial_hold_ratio: float = 0.08
    description: str = ""


# SSOT Density Profiles for all 20 Vietnamese channels
VN_LONG_DENSITY_PROFILES: Dict[str, VNLongDensityProfile] = {
    # --------------------------------------------------------------------------
    # 1. High-Velocity Investigative / Explainer Channels (11)
    # Target: 260 - 350 visual states (1.6s - 2.3s avg hold)
    # --------------------------------------------------------------------------
    "ho_so_ky_la": VNLongDensityProfile(
        channel_id="ho_so_ky_la",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="2D Noir & Red-String Dossier: rapid clue reveals, pinboard builds, clause-synced micro-zooms",
    ),
    "luat_ngam": VNLongDensityProfile(
        channel_id="luat_ngam",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Noir underworld rules & legal loopholes: rapid case cutaways, contract clause highlights",
    ),
    "su_ke_lai": VNLongDensityProfile(
        channel_id="su_ke_lai",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Historical battle chronicle: tactical troop movement builds, timeline bursts, commander angle cutaways",
    ),
    "nao_luoi": VNLongDensityProfile(
        channel_id="nao_luoi",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Psychology & cognitive bias: Feynman stickman diorama builds, rapid psychological example bursts",
    ),
    "ua_sao_vay": VNLongDensityProfile(
        channel_id="ua_sao_vay",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Surprising science & curiosity gap: rapid cause-and-effect reaction chains, sticker-pop builds",
    ),
    "tui_tien": VNLongDensityProfile(
        channel_id="tui_tien",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Consumer economics & pricing dissects: bill line-item bursts, money flow progressive builds",
    ),
    "luat_doi_thuong": VNLongDensityProfile(
        channel_id="luat_doi_thuong",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Everyday legal rights: dispute angle cuts, fine print highlights, clause dissection builds",
    ),
    "ai_binh_dan": VNLongDensityProfile(
        channel_id="ai_binh_dan",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Practical AI & automation for everyday people: UI step-by-step builds, prompt contrast bursts",
    ),
    "nghe_song_sot": VNLongDensityProfile(
        channel_id="nghe_song_sot",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Survival skills & emergency psychology: step-by-step reaction builds, hazard cutaways",
    ),
    "dia_com": VNLongDensityProfile(
        channel_id="dia_com",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Food science & culinary myths: ingredient dissection bursts, cooking reaction progressive steps",
    ),
    "co_the_ke": VNLongDensityProfile(
        channel_id="co_the_ke",
        archetype="high_velocity_investigative",
        target_states_range=(260, 350),
        target_avg_hold_range=(1.6, 2.3),
        tier1_anchors_range=(100, 125),
        tier2_builds_range=(160, 225),
        description="Human anatomy personified: organ dialogue cutaways, cellular mechanism builds, symptom bursts",
    ),

    # --------------------------------------------------------------------------
    # 2. Scale / Map / Infrastructure / Academic Channels (6)
    # Target: 220 - 290 visual states (2.1s - 2.8s avg hold)
    # --------------------------------------------------------------------------
    "ban_do_quyen_luc": VNLongDensityProfile(
        channel_id="ban_do_quyen_luc",
        archetype="scale_map_academic",
        target_states_range=(220, 290),
        target_avg_hold_range=(2.1, 2.8),
        tier1_anchors_range=(90, 110),
        tier2_builds_range=(130, 180),
        description="2D Tactical Cartography: geopolitical border shifts, trade corridor progressive layer builds",
    ),
    "banh_rang": VNLongDensityProfile(
        channel_id="banh_rang",
        archetype="scale_map_academic",
        target_states_range=(220, 290),
        target_avg_hold_range=(2.1, 2.8),
        tier1_anchors_range=(90, 110),
        tier2_builds_range=(130, 180),
        description="Macroeconomics & Industrial Logistics: supply chain blueprints, factory flow progressive schematics",
    ),
    "la_ban_hoc_thuat": VNLongDensityProfile(
        channel_id="la_ban_hoc_thuat",
        archetype="scale_map_academic",
        target_states_range=(220, 290),
        target_avg_hold_range=(2.1, 2.8),
        tier1_anchors_range=(90, 110),
        tier2_builds_range=(130, 180),
        description="Academic research & epistemology: research paper framework builds, citation and data graph layers",
    ),
    "vu_tru_ti_hon": VNLongDensityProfile(
        channel_id="vu_tru_ti_hon",
        archetype="scale_map_academic",
        target_states_range=(220, 290),
        target_avg_hold_range=(2.1, 2.8),
        tier1_anchors_range=(90, 110),
        tier2_builds_range=(130, 180),
        description="Astrophysics & micro-quantum scale: cosmic zoom progressive builds, planetary orbit layers",
    ),
    "thuong_cho_kheo": VNLongDensityProfile(
        channel_id="thuong_cho_kheo",
        archetype="scale_map_academic",
        target_states_range=(220, 290),
        target_avg_hold_range=(2.1, 2.8),
        tier1_anchors_range=(90, 110),
        tier2_builds_range=(130, 180),
        description="Interpersonal dynamics & relationship architecture: conversational diorama layers, perspective shifts",
    ),
    "loi_sang_soi": VNLongDensityProfile(
        channel_id="loi_sang_soi",
        archetype="scale_map_academic",
        target_states_range=(220, 290),
        target_avg_hold_range=(2.1, 2.8),
        tier1_anchors_range=(90, 110),
        tier2_builds_range=(130, 180),
        description="Ethical dilemmas & moral philosophy: moral thought experiment frameworks, consequence tree builds",
    ),

    # --------------------------------------------------------------------------
    # 3. Contemplative / Stoic / Midnight Sanctuary Channels (3)
    # Target: 150 - 210 visual states (3.2s - 4.5s avg hold)
    # --------------------------------------------------------------------------
    "chanh_niem_ke": VNLongDensityProfile(
        channel_id="chanh_niem_ke",
        archetype="contemplative_sanctuary",
        target_states_range=(150, 210),
        target_avg_hold_range=(3.2, 4.5),
        tier1_anchors_range=(60, 80),
        tier2_builds_range=(90, 130),
        description="Sumi-e Zen Ink Wash: mindful breath holds, organic ink wash progressions, serene visual contemplation",
    ),
    "minh_triet_song": VNLongDensityProfile(
        channel_id="minh_triet_song",
        archetype="contemplative_sanctuary",
        target_states_range=(150, 210),
        target_avg_hold_range=(3.2, 4.5),
        tier1_anchors_range=(60, 80),
        tier2_builds_range=(90, 130),
        description="Stoic philosophy & living wisdom: contemplative metaphorical holds, philosopher perspective shifts",
    ),
    "tam_tinh_dem": VNLongDensityProfile(
        channel_id="tam_tinh_dem",
        archetype="contemplative_sanctuary",
        target_states_range=(150, 210),
        target_avg_hold_range=(3.2, 4.5),
        tier1_anchors_range=(60, 80),
        tier2_builds_range=(90, 130),
        description="Midnight sanctuary & quiet reflection: solitary nocturnal dioramas, gentle poetic atmospheric builds",
    ),
}


def normalize_channel_id(channel_id: str) -> str:
    """Normalize channel ID string to underscored canonical form."""
    norm = (channel_id or "").strip().lower().replace("-", "_")
    return norm


def get_vn_long_density_profile(channel_id: str) -> VNLongDensityProfile:
    """Retrieve the high-density long 16:9 profile for a Vietnamese channel."""
    norm = normalize_channel_id(channel_id)
    if norm in VN_LONG_DENSITY_PROFILES:
        return VN_LONG_DENSITY_PROFILES[norm]
    raise KeyError(f"Unknown VN channel ID '{channel_id}'. Available: {sorted(VN_LONG_DENSITY_PROFILES.keys())}")


def list_all_vn_long_density_profiles() -> Dict[str, VNLongDensityProfile]:
    """Return all 20 Vietnamese channel long-form density profiles."""
    return dict(VN_LONG_DENSITY_PROFILES)


@dataclass
class YouTubeChapter:
    """Structured YouTube Chapter for 8m30s - 13m00s long-form explainer."""

    chapter_index: int
    title: str
    start_sec: float
    end_sec: float
    narrative_role: str = ""
    summary: str = ""

    @property
    def duration_sec(self) -> float:
        return self.end_sec - self.start_sec


@dataclass
class VisualState:
    """Single node in the Two-Tier Visual-State DAG."""

    id: str
    chapter_index: int
    event_kind: VisualEventKind
    based_on: Optional[str]  # None for Tier 1 ANCHOR_ESTABLISH; parent anchor/state ID for Tier 2
    at: float  # Absolute time in video (seconds)
    hold: float  # Duration in seconds
    tempo: str  # "burst", "fast", "normal", "slow", "hold"
    camera_move: str  # "zoom_in", "pan_right", etc.
    xfade: str  # "smoothright", "fade", "cut", "dissolve", etc.
    prompt_spec: str = ""
    emphasis_text: Optional[str] = None


@dataclass
class HighDensityLongPlan:
    """Complete Two-Tier 240-350 Visual-State DAG Plan for a Vietnamese Long 16:9 Explainer."""

    channel_id: str
    format_profile: str
    total_duration_sec: float
    chapters: List[YouTubeChapter]
    visual_states: List[VisualState]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to serializable dictionary."""
        return {
            "channel_id": self.channel_id,
            "format_profile": self.format_profile,
            "total_duration_sec": self.total_duration_sec,
            "chapters": [asdict(ch) for ch in self.chapters],
            "visual_states": [
                {
                    **asdict(vs),
                    "event_kind": vs.event_kind.value if isinstance(vs.event_kind, VisualEventKind) else str(vs.event_kind),
                }
                for vs in self.visual_states
            ],
            "metadata": self.metadata,
        }


def generate_default_chapters(
    total_duration_sec: float = 630.0,
    channel_id: str = "tui_tien",
) -> List[YouTubeChapter]:
    """Generate 10 canonical YouTube chapters for an 8m30s - 13m00s explainer video."""
    dur = float(total_duration_sec)
    ratios = [
        ("Hook & Nghịch lý khởi đầu", 0.071, "hook_cold_open"),
        ("Bóc tách hiện thực trần trụi", 0.095, "foundation_setup"),
        ("Dòng chảy ngầm vô hình", 0.103, "mechanism_step"),
        ("Bẫy tâm lý & Sai lầm phổ biến", 0.111, "escalation"),
        ("Cơ chế giải phẫu cốt lõi", 0.111, "mechanism_step"),
        ("Cú lật ngược tư duy", 0.119, "counter_intuitive_twist"),
        ("Bản đồ đối chiếu thực chiến", 0.119, "deep_dive"),
        ("Mô hình hành động đột phá", 0.111, "climax_payoff"),
        ("Quy tắc sống còn & Bài học", 0.103, "resolution_synthesis"),
        ("Hành động ngay & Kết nối phễu", 0.057, "cta_bridge"),
    ]

    chapters: List[YouTubeChapter] = []
    current_t = 0.0
    for idx, (title, ratio, role) in enumerate(ratios, 1):
        if idx == len(ratios):
            end_t = dur
        else:
            end_t = round(current_t + dur * ratio, 2)
        chapters.append(
            YouTubeChapter(
                chapter_index=idx,
                title=f"Hồi {idx:02d}: {title}",
                start_sec=current_t,
                end_sec=end_t,
                narrative_role=role,
            )
        )
        current_t = end_t
    return chapters


def plan_long_visual_states_from_chapters(
    channel_id: str,
    chapters: Optional[List[Dict[str, Any] | YouTubeChapter]] = None,
    total_duration_sec: Optional[float] = None,
    target_states_override: Optional[int] = None,
) -> HighDensityLongPlan:
    """Structure any 8m30s - 13m00s long video into a Two-Tier 240-350 Visual-State DAG.

    Aligns with empirical ground truth: ~100-125 base anchors + ~160-225 progressive builds,
    satisfies visual_pacing.py checks, and guarantees camera entropy and xfade direction matching.
    """
    profile = get_vn_long_density_profile(channel_id)

    # 1. Parse or generate chapters
    parsed_chapters: List[YouTubeChapter] = []
    if chapters:
        for idx, ch in enumerate(chapters, 1):
            if isinstance(ch, YouTubeChapter):
                parsed_chapters.append(ch)
            else:
                parsed_chapters.append(
                    YouTubeChapter(
                        chapter_index=int(ch.get("chapter_index", idx)),
                        title=str(ch.get("title", f"Hồi {idx:02d}")),
                        start_sec=float(ch.get("start_sec", 0.0)),
                        end_sec=float(ch.get("end_sec", 0.0)),
                        narrative_role=str(ch.get("narrative_role", "")),
                        summary=str(ch.get("summary", "")),
                    )
                )
    else:
        dur = total_duration_sec if total_duration_sec and total_duration_sec > 0 else 630.0
        parsed_chapters = generate_default_chapters(dur, profile.channel_id)

    total_dur = parsed_chapters[-1].end_sec - parsed_chapters[0].start_sec

    # 2. Determine target visual states count
    if target_states_override is not None:
        target_states = target_states_override
    else:
        # Scale nominal baseline by duration relative to 630s (10m30s)
        mid_target = (profile.target_states_range[0] + profile.target_states_range[1]) // 2
        nominal_hold = 630.0 / mid_target
        target_states = int(round(total_dur / nominal_hold))
        target_states = max(profile.target_states_range[0], min(profile.target_states_range[1], target_states))

    # 3. Chapter-level state count allocation
    num_chapters = len(parsed_chapters)
    raw_chapter_counts: List[int] = []
    for ch in parsed_chapters:
        ch_ratio = ch.duration_sec / max(1.0, total_dur)
        # Hook cold open gets a slight density boost
        boost = 1.15 if ch.narrative_role == "hook_cold_open" or ch.chapter_index == 1 else 1.0
        raw_chapter_counts.append(max(5, int(round(target_states * ch_ratio * boost))))

    # Rebalance so sum exactly equals target_states
    diff = target_states - sum(raw_chapter_counts)
    idx = 0
    while diff != 0:
        c_idx = (idx % (num_chapters - 1)) + 1  # Distribute across body chapters
        if diff > 0:
            raw_chapter_counts[c_idx] += 1
            diff -= 1
        else:
            if raw_chapter_counts[c_idx] > 6:
                raw_chapter_counts[c_idx] -= 1
                diff += 1
        idx += 1

    # 4. Generate Two-Tier Visual-State DAG inside each chapter
    all_visual_states: List[VisualState] = []
    spatial_hold_budget = max(1, int(target_states * profile.max_spatial_hold_ratio))
    spatial_holds_used = 0

    camera_idx = 0
    last_camera_move: Optional[str] = None
    consecutive_cam_count = 0

    emphasis_phrases = [
        "ĐIỂM NÚT THEN CHỐT",
        "BẪY VÔ HÌNH",
        "SỐC CHI PHÍ",
        "QUY TẮC SỐNG CÒN",
        "CÚ LẬT NGƯỢC",
        "SỰ THẬT BẤT NGỜ",
        "DÒNG TIỀN BIẾN MẤT",
        "BẢN ĐỒ CHIẾN LƯỢC",
    ]
    phrase_idx = 0

    for ch_idx, (ch, ch_states_count) in enumerate(zip(parsed_chapters, raw_chapter_counts, strict=True), 1):
        is_hook_chapter = (ch_idx == 1 or ch.narrative_role == "hook_cold_open")

        is_contemplative = (profile.archetype == "contemplative_sanctuary")

        # Decide cluster structure: each cluster has 1 anchor + (1 to 3) progressive builds
        # Target ~35%-40% anchors, ~60%-65% progressive builds
        num_clusters = max(2, int(round(ch_states_count * 0.38)))
        cluster_sizes = [1] * num_clusters
        remaining_in_ch = ch_states_count - num_clusters
        c_i = 0
        while remaining_in_ch > 0:
            cluster_sizes[c_i % num_clusters] += 1
            remaining_in_ch -= 1
            c_i += 1

        ch_states_unretimed: List[VisualState] = []

        for clust_idx, c_size in enumerate(cluster_sizes, 1):
            anchor_id = f"CH{ch_idx:02d}_A{clust_idx:02d}"
            # Tier 1: Anchor Establish
            anchor_tempo = "normal"
            anchor_hold_nominal = 3.3 if is_contemplative else 2.4

            anchor_state = VisualState(
                id=anchor_id,
                chapter_index=ch_idx,
                event_kind=VisualEventKind.ANCHOR_ESTABLISH,
                based_on=None,
                at=0.0,
                hold=anchor_hold_nominal,
                tempo=anchor_tempo,
                camera_move="",  # will be assigned in entropy step
                xfade="",
                prompt_spec=f"Establishing diorama for {ch.title} - Scene {clust_idx:02d}",
            )
            ch_states_unretimed.append(anchor_state)

            # Tier 2: Progressive Builds / Clause-Synced Angle Cuts
            for b_idx in range(1, c_size):
                build_id = f"{anchor_id}_B{b_idx:02d}"

                # Assign visual event kind
                if is_contemplative:
                    if spatial_holds_used < spatial_hold_budget and b_idx == c_size - 1 and clust_idx % 3 == 0 and not is_hook_chapter:
                        event_kind = VisualEventKind.SPATIAL_COGNITIVE_HOLD
                        spatial_holds_used += 1
                    elif b_idx % 2 == 1:
                        event_kind = VisualEventKind.MECHANISM_STEP_BUILD
                    else:
                        event_kind = VisualEventKind.ANGLE_CUTAWAY
                elif is_hook_chapter:
                    event_kind = VisualEventKind.ENUMERATION_BURST if (b_idx % 2 == 1) else VisualEventKind.ANGLE_CUTAWAY
                elif spatial_holds_used < spatial_hold_budget and b_idx == c_size - 1 and clust_idx % 3 == 0 and not is_hook_chapter:
                    event_kind = VisualEventKind.SPATIAL_COGNITIVE_HOLD
                    spatial_holds_used += 1
                elif b_idx % 2 == 1:
                    event_kind = VisualEventKind.MECHANISM_STEP_BUILD
                else:
                    event_kind = VisualEventKind.ANGLE_CUTAWAY

                # Event characteristics
                if is_contemplative:
                    if event_kind == VisualEventKind.SPATIAL_COGNITIVE_HOLD:
                        b_tempo = "slow"
                        b_hold = 4.50
                    elif event_kind == VisualEventKind.ANGLE_CUTAWAY:
                        b_tempo = "fast"
                        b_hold = 2.40
                    else:
                        b_tempo = "normal"
                        b_hold = 3.30
                else:
                    if event_kind == VisualEventKind.ENUMERATION_BURST:
                        b_tempo = "burst"
                        b_hold = 1.15
                    elif event_kind == VisualEventKind.ANGLE_CUTAWAY:
                        b_tempo = "fast"
                        b_hold = 1.75
                    elif event_kind == VisualEventKind.MECHANISM_STEP_BUILD:
                        b_tempo = "normal"
                        b_hold = 2.35
                    elif event_kind == VisualEventKind.SPATIAL_COGNITIVE_HOLD:
                        b_tempo = "slow"
                        b_hold = 4.20
                    else:
                        b_tempo = "normal"
                        b_hold = 2.20

                # Optional emphasis text (<= 20% of beats)
                has_emphasis = (len(all_visual_states) + len(ch_states_unretimed)) % 6 == 0
                emp_text = emphasis_phrases[phrase_idx % len(emphasis_phrases)] if has_emphasis else None
                if has_emphasis:
                    phrase_idx += 1

                build_state = VisualState(
                    id=build_id,
                    chapter_index=ch_idx,
                    event_kind=event_kind,
                    based_on=anchor_id,
                    at=0.0,
                    hold=b_hold,
                    tempo=b_tempo,
                    camera_move="",
                    xfade="",
                    prompt_spec=f"Progressive build {b_idx} on {anchor_id}",
                    emphasis_text=emp_text,
                )
                ch_states_unretimed.append(build_state)

        # In hook chapter, calibrate lead window starts
        lead_count = 0
        if is_hook_chapter:
            if is_contemplative and len(ch_states_unretimed) >= 6:
                lead_count = 6
                lead_holds = [2.10, 2.10, 1.80, 2.20, 2.20, 2.10]
                lead_tempos = ["normal", "normal", "fast", "normal", "normal", "normal"]
            elif not is_contemplative and len(ch_states_unretimed) >= 9:
                lead_count = 9
                lead_holds = [1.25, 1.35, 1.10, 1.30, 1.40, 1.10, 1.40, 1.40, 2.20]
                lead_tempos = ["fast", "fast", "burst", "fast", "fast", "burst", "fast", "fast", "normal"]

            for i in range(lead_count):
                ch_states_unretimed[i].hold = lead_holds[i]
                ch_states_unretimed[i].tempo = lead_tempos[i]

        lead_sum = sum(ch_states_unretimed[i].hold for i in range(lead_count))
        subsequent = ch_states_unretimed[lead_count:]
        sub_needed = max(0.001, ch.duration_sec - lead_sum)

        if subsequent:
            sum_init = sum(s.hold for s in subsequent)
            scale_factor = sub_needed / max(0.001, sum_init)
            for s in subsequent:
                raw_h = s.hold * scale_factor
                if s.tempo == "burst":
                    s.hold = round(max(0.85, min(1.65, raw_h)), 3)
                elif s.tempo == "fast":
                    s.hold = round(max(1.40, min(2.40, raw_h)), 3)
                elif s.tempo == "normal":
                    s.hold = round(max(2.00, min(3.80, raw_h)), 3)
                elif s.tempo == "slow":
                    s.hold = round(max(3.60, min(5.50, raw_h)), 3)
                elif s.tempo == "hold":
                    s.hold = round(max(2.00, min(7.50, raw_h)), 3)

            # Fine-tune leftover seconds evenly across subsequent beats
            diff_h = sub_needed - sum(s.hold for s in subsequent)
            adj_per_beat = diff_h / len(subsequent)
            for s in subsequent:
                s.hold = round(s.hold + adj_per_beat, 3)

            # Reconcile exact sub_needed down to 0.001s
            rem_diff = round(sub_needed - sum(s.hold for s in subsequent), 3)
            if rem_diff != 0.0:
                subsequent[0].hold = round(subsequent[0].hold + rem_diff, 3)

            # Assign matching tempo based on final hold
            for s in subsequent:
                h = s.hold
                if s.event_kind == VisualEventKind.SPATIAL_COGNITIVE_HOLD or h > 4.10:
                    s.tempo = "slow"
                elif h < 1.35:
                    s.tempo = "burst"
                elif h < 2.00:
                    s.tempo = "fast"
                else:
                    s.tempo = "normal"

        # 6. Assign timestamps, camera moves, and directional xfade
        curr_time = ch.start_sec
        for s in ch_states_unretimed:
            s.at = round(curr_time, 4)
            curr_time += s.hold

            # Camera move assignment enforcing max 2 consecutive identical moves
            cam = CAMERA_MOVES[camera_idx % len(CAMERA_MOVES)]
            if cam == last_camera_move:
                consecutive_cam_count += 1
                if consecutive_cam_count >= 2:
                    camera_idx += 1
                    cam = CAMERA_MOVES[camera_idx % len(CAMERA_MOVES)]
                    consecutive_cam_count = 1
            else:
                consecutive_cam_count = 1
            last_camera_move = cam
            camera_idx += 1

            s.camera_move = cam
            s.xfade = DIRECTIONAL_XFADE_MAP.get(cam, "fade")

        all_visual_states.extend(ch_states_unretimed)

    # 6b. Global tempo run limiter to ensure 0 consecutive runs exceed limits across chapter seams
    cur_t: Optional[str] = None
    run_len = 0
    for s in all_visual_states:
        if s.tempo == cur_t:
            run_len += 1
            max_r = 4 if s.tempo == "fast" else 2
            if run_len > max_r:
                h = s.hold
                if s.tempo == "normal":
                    if h <= 2.80:
                        s.tempo = "fast"
                    elif h >= 3.00:
                        s.tempo = "slow"
                    else:
                        s.tempo = "fast"
                elif s.tempo == "slow":
                    if h <= 4.14:
                        s.tempo = "normal"
                    elif h <= 2.80:
                        s.tempo = "fast"
                elif s.tempo == "fast":
                    if 1.70 <= h <= 2.80:
                        s.tempo = "normal"
                    elif 1.19 <= h <= 2.05:
                        s.tempo = "burst"
                elif s.tempo == "burst":
                    if 1.19 <= h <= 2.05:
                        s.tempo = "fast"
                cur_t = s.tempo
                run_len = 1
        else:
            cur_t = s.tempo
            run_len = 1

    # 7. Ensure at least one slow insight beat exists overall
    slow_count = sum(1 for s in all_visual_states if s.tempo == "slow")
    if slow_count == 0 and len(all_visual_states) > 10:
        mid_idx = len(all_visual_states) // 2
        all_visual_states[mid_idx].event_kind = VisualEventKind.SPATIAL_COGNITIVE_HOLD
        all_visual_states[mid_idx].tempo = "slow"
        all_visual_states[mid_idx].hold = 4.0

    # 8. Compute metadata metrics
    tier1_count = sum(1 for s in all_visual_states if s.based_on is None)
    tier2_count = sum(1 for s in all_visual_states if s.based_on is not None)
    avg_hold = round(total_dur / len(all_visual_states), 3) if all_visual_states else 0.0

    metadata = {
        "channel_id": profile.channel_id,
        "archetype": profile.archetype,
        "total_states": len(all_visual_states),
        "tier1_anchors": tier1_count,
        "tier2_builds": tier2_count,
        "avg_hold": avg_hold,
        "spatial_holds": sum(1 for s in all_visual_states if s.event_kind == VisualEventKind.SPATIAL_COGNITIVE_HOLD),
        "spatial_hold_ratio": round(
            sum(1 for s in all_visual_states if s.event_kind == VisualEventKind.SPATIAL_COGNITIVE_HOLD) / max(1, len(all_visual_states)),
            4,
        ),
        "emphasis_count": sum(1 for s in all_visual_states if s.emphasis_text),
        "emphasis_ratio": round(sum(1 for s in all_visual_states if s.emphasis_text) / max(1, len(all_visual_states)), 4),
    }

    return HighDensityLongPlan(
        channel_id=profile.channel_id,
        format_profile="long_16x9_high_density",
        total_duration_sec=total_dur,
        chapters=parsed_chapters,
        visual_states=all_visual_states,
        metadata=metadata,
    )


def to_renderer_scenes(plan: HighDensityLongPlan | Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert a HighDensityLongPlan into standard Video Pilot renderer scenes."""
    if isinstance(plan, dict):
        _channel_id = plan.get("channel_id", "")
        chapters = [YouTubeChapter(**c) if isinstance(c, dict) else c for c in plan["chapters"]]
        raw_states = plan["visual_states"]
        states = [
            VisualState(
                id=s["id"],
                chapter_index=s["chapter_index"],
                event_kind=VisualEventKind(s["event_kind"]),
                based_on=s.get("based_on"),
                at=float(s["at"]),
                hold=float(s["hold"]),
                tempo=s["tempo"],
                camera_move=s["camera_move"],
                xfade=s["xfade"],
                prompt_spec=s.get("prompt_spec", ""),
                emphasis_text=s.get("emphasis_text"),
            )
            if isinstance(s, dict)
            else s
            for s in raw_states
        ]
    else:
        _channel_id = plan.channel_id
        chapters = plan.chapters
        states = plan.visual_states

    scenes: List[Dict[str, Any]] = []
    for ch in chapters:
        ch_states = [s for s in states if s.chapter_index == ch.chapter_index]
        scene_dict = {
            "id": f"SC{ch.chapter_index:02d}",
            "title": ch.title,
            "start": round(ch.start_sec, 4),
            "end": round(ch.end_sec, 4),
            "narrative_role": ch.narrative_role,
            "images": [
                {
                    "id": s.id,
                    "at": round(max(0.0, s.at - ch.start_sec), 4),
                    "hold": round(s.hold, 4),
                    "based_on": s.based_on,
                    "event_kind": s.event_kind.value if hasattr(s.event_kind, "value") else str(s.event_kind),
                    "tempo": s.tempo,
                    "camera_move": s.camera_move,
                    "xfade": s.xfade,
                    "emphasis_text": s.emphasis_text,
                }
                for s in ch_states
            ],
            "beats": [
                {
                    "id": s.id,
                    "image_id": s.id,
                    "at": round(max(0.0, s.at - ch.start_sec), 4),
                    "hold": round(s.hold, 4),
                    "tempo": s.tempo,
                    "based_on": s.based_on,
                    "emphasis_text": s.emphasis_text,
                }
                for s in ch_states
            ],
        }
        scenes.append(scene_dict)
    return scenes


def validate_high_density_long_plan(plan: HighDensityLongPlan | Dict[str, Any]) -> List[str]:
    """Validate a Two-Tier 240-350 Visual-State DAG Plan against channel contracts.

    Enforces:
    1. Total states in channel target range (e.g., 260-350 for investigative).
    2. Duration and chapter structure (8-12 chapters, each >= 10s).
    3. DAG parent validity (every based_on references a valid prior state).
    4. Max 2 consecutive identical camera moves (entropy rule).
    5. Directional xfade matching (no conflicting pan/transition pairs).
    6. Spatial cognitive hold ratio <= 8%.
    7. Clean pass through visual_pacing.py (check_tempo_beats & check_see_say_beat_density).
    """
    errors: List[str] = []

    if isinstance(plan, dict):
        channel_id = normalize_channel_id(plan.get("channel_id", ""))
        chapters_raw = plan.get("chapters", [])
        chapters = [YouTubeChapter(**c) if isinstance(c, dict) else c for c in chapters_raw]
        states_raw = plan.get("visual_states", [])
        states = [
            VisualState(
                id=s["id"],
                chapter_index=s["chapter_index"],
                event_kind=VisualEventKind(s["event_kind"]),
                based_on=s.get("based_on"),
                at=float(s["at"]),
                hold=float(s["hold"]),
                tempo=s["tempo"],
                camera_move=s["camera_move"],
                xfade=s["xfade"],
                prompt_spec=s.get("prompt_spec", ""),
                emphasis_text=s.get("emphasis_text"),
            )
            if isinstance(s, dict)
            else s
            for s in states_raw
        ]
        total_duration_sec = float(plan.get("total_duration_sec", 0.0))
    else:
        channel_id = normalize_channel_id(plan.channel_id)
        chapters = plan.chapters
        states = plan.visual_states
        total_duration_sec = plan.total_duration_sec

    if channel_id not in VN_LONG_DENSITY_PROFILES:
        errors.append(f"UNKNOWN_CHANNEL: '{channel_id}' is not one of the 20 VN channels")
        return errors

    profile = VN_LONG_DENSITY_PROFILES[channel_id]

    if total_duration_sec < 120.0:
        errors.append(f"TOTAL_DURATION_TOO_SHORT: duration {total_duration_sec:.2f}s is too short for long explainer")

    # Chapter structure validation
    if not 8 <= len(chapters) <= 12:
        errors.append(f"CHAPTER_COUNT_OUT_OF_RANGE: expected 8-12 chapters, got {len(chapters)}")

    prev_end = 0.0
    for ch in chapters:
        ch_dur = ch.end_sec - ch.start_sec
        if ch_dur < 10.0:
            errors.append(f"CHAPTER_TOO_SHORT: Chapter {ch.chapter_index} duration {ch_dur:.2f}s < min 10.0s")
        if abs(ch.start_sec - prev_end) > 0.05:
            errors.append(
                f"CHAPTER_DISCONTINUOUS: Chapter {ch.chapter_index} start {ch.start_sec:.2f}s != previous end {prev_end:.2f}s"
            )
        prev_end = ch.end_sec

    # Total states target range validation
    total_states = len(states)
    min_states, max_states = profile.target_states_range
    # Allow 10% tolerance around range for varying durations
    if total_states < int(min_states * 0.90) or total_states > int(max_states * 1.10):
        errors.append(
            f"VISUAL_STATES_OUT_OF_TARGET: channel '{channel_id}' has {total_states} states "
            f"(target [{min_states}, {max_states}])"
        )

    # DAG Parent Validity check
    seen_ids: set[str] = set()
    tier1_count = 0
    tier2_count = 0
    for s in states:
        if s.id in seen_ids:
            errors.append(f"DUPLICATE_VISUAL_STATE_ID: '{s.id}' is declared more than once")
        seen_ids.add(s.id)

        if s.event_kind == VisualEventKind.ANCHOR_ESTABLISH:
            tier1_count += 1
            if s.based_on is not None and s.based_on != "":
                errors.append(
                    f"INVALID_DAG_ANCHOR: ANCHOR_ESTABLISH '{s.id}' must have based_on=None, got '{s.based_on}'"
                )
        else:
            tier2_count += 1
            if not s.based_on:
                errors.append(
                    f"MISSING_DAG_PARENT: Tier-2 progressive event '{s.id}' kind '{s.event_kind}' must have a valid based_on"
                )
            elif s.based_on not in seen_ids:
                errors.append(
                    f"DAG_PARENT_NOT_FOUND: event '{s.id}' points to parent '{s.based_on}' which was not yet declared"
                )

    # Camera entropy: max 2 consecutive identical camera moves
    consecutive_cam = 1
    prev_cam: Optional[str] = None
    for s in states:
        if s.camera_move == prev_cam:
            consecutive_cam += 1
            if consecutive_cam > 2:
                errors.append(
                    f"CAMERA_ENTROPY_VIOLATION: '{s.camera_move}' repeated {consecutive_cam} times at state '{s.id}' (max 2)"
                )
        else:
            prev_cam = s.camera_move
            consecutive_cam = 1

    # Directional xfade matching: no conflicting pan/transition pairs
    for s in states:
        conflicts = CONFLICTING_TRANSITIONS.get(s.camera_move, set())
        if s.xfade in conflicts:
            errors.append(
                f"DIRECTIONAL_XFADE_CONFLICT: camera move '{s.camera_move}' cannot use conflicting xfade '{s.xfade}' at '{s.id}'"
            )

    # Spatial cognitive hold ratio <= 8%
    spatial_count = sum(1 for s in states if s.event_kind == VisualEventKind.SPATIAL_COGNITIVE_HOLD)
    spatial_ratio = spatial_count / max(1, total_states)
    if spatial_ratio > 0.08:
        errors.append(
            f"SPATIAL_HOLD_RATIO_EXCEEDED: {spatial_count}/{total_states} ({spatial_ratio:.1%}) beats are spatial holds (max 8%)"
        )

    # Visual Pacing integration checks
    scenes = to_renderer_scenes(plan)
    pacing_density_errors = check_see_say_beat_density(scenes, format_profile="long_16x9_high_density")
    for err in pacing_density_errors:
        errors.append(f"PACING_DENSITY: {err}")

    beats_for_tempo = [
        {
            "id": s.id,
            "tempo": s.tempo,
            "hold": s.hold,
            "at": s.at,
            "emphasis_text": s.emphasis_text,
        }
        for s in states
    ]
    tempo_errors = check_tempo_beats(beats_for_tempo, format_profile="long_16x9_high_density")
    for err in tempo_errors:
        errors.append(f"PACING_TEMPO: {err}")

    return errors
