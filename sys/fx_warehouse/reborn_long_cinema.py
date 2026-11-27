"""Reborn Long Cinema Engine — 4-Mode Visual Language & Dynamic Acoustic Breathing.

Reinvents the Long 16:9 video format (1920x1080@30fps) to feel like a 2026
foreign million-view investigative/historical documentary (Fern, Imperial,
The Operations Room, Epic History TV).

Visual contract: ``su_ke_lai_35mm_live_action_v3`` — 35mm Kodak Vision3 500T
Clear-Air live-action cinema.  Zero stickmen / 2D doodle.  Moving-cinema beats
use Dual-Model Flow Router; spatial beats use real WGS84 + 3D geo-empire clash.

Architectural breakthroughs over the old produce_su_ke_lai_long_m1.py engine:

1. **Dynamic Acoustic Breathing & Hard Silence Drops**:
   - Per-beat `pre_silence_sec` / `post_sfx_hold_sec` (0.3s–2.2s).
   - `[silence_drop]` / `[sfx_solo:...]` beats where narration STOPS and
     diegetic 48kHz stereo SFX carries the tension.
   - `-0.24s` J-cut audio pre-laps.
   - 5-stem cinema mixing: narration + diegetic_sfx + silence_bed +
     bgm_tension + room_tone mastered to -11.0 LUFS / -1.0 dBTP @ 48000Hz.

2. **4-Mode Visual Language Choreography (1920x1080@30fps)**:
   a) `moving_cinema`: Native 16:9 moving Flow .mp4 clips via Dual-Model
      Router (veo_3_1_lite Seam + macaron_cookie Frame-Link).
   b) `spatial_terrain_ops`: Real WGS84 satellite/shaded-relief with smooth
      30fps sub-pixel camera fly-in via gis_map_baker.py.
   c) `forensic_evidence_reveal`: Tactile archival primary-chronicle /
      countdown clock / force-comparison with optical masking.
   d) `macro_parallax_still`: High-res 16:9 BELUGA frame with genuine
      float32 2.5D depth/camera motion (≤ 3.5s max hold).

3. **Production & Hardware Locks (AGENTS.md non-negotiable)**:
   - Colab T4 FFmpeg h264_nvenc only.
   - GlobalFlowProductionLock around Flow CDP.
   - Bottom-right channel logo at W-w-36:H-h-36 + delogo.

Reuses proven building blocks from:
- camera_vfx.py (8 sub-pixel 2.5D camera motions)
- gis_map_baker.py (WGS84 terrain baking)
- audio_sfx_bgm.py (25 stereo SFX stems)
- audio_suspense_v2.py (4-act suspense mixer)
- selector.py (content-aware FX selection)
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ENGINE_ID = "reborn_long_cinema"
ENGINE_VERSION = "1.0.0"
REBORN_PIPELINE_VERSION = "11.5.0"

DEFAULT_COLOR_GRADE = "kodak_2383_anti_ai"
VALID_COLOR_GRADES: tuple[str, ...] = ("kodak_2383_anti_ai", "none")
DEFAULT_COLAB_RENDER_WORKERS = 6

TARGET_SR = 48000
FPS = 30
WIDTH = 1920
HEIGHT = 1080
RESOLUTION = "1080p"

TARGET_LUFS = -11.0
MAX_TRUE_PEAK_DBTP = -1.0
J_CUT_PRELAP_SEC = -0.24
MIX_STEM_COUNT = 5

WATERMARK_POS = "W-w-36:H-h-36"
DELOGO_ENABLED = True

# Duration bounds for pilot showcase and full-length episode (sec)
PILOT_MIN_DURATION_SEC = 70.0
PILOT_MAX_DURATION_SEC = 95.0
FULL_MIN_DURATION_SEC = 520.0
FULL_MAX_DURATION_SEC = 660.0
DEFAULT_MAX_BEATS = 120
DEFAULT_MAX_CHUNK_BEATS = 16

# Per-beat silence drop bounds
SILENCE_MIN_SEC = 0.3
SILENCE_MAX_SEC = 2.2

# Macro parallax max hold
MACRO_PARALLAX_MAX_HOLD_SEC = 3.5

# Spatial terrain max consecutive hold (radar-user4: never pure map >14s)
SPATIAL_TERRAIN_MAX_CONSECUTIVE_SEC = 14.0

# Moving cinema clip duration ranges
RAPID_TENSION_RANGE = (1.8, 2.6)
CONTINUOUS_CHAIN_RANGE = (4.5, 6.5)

# Radar-verified foreign documentary benchmarks (2025–2026, 475K–22.4M views)
# Source: research_foreign_tactical_history.json + research_foreign_essay_cinema.json
COLD_OPEN_SFX_LEAD_IN_RANGE = (2.5, 4.0)  # sec of diegetic SFX before Beat 0
TARGET_LRA_RANGE = (5.5, 10.5)  # LU loudness range (break flat ~2 LU TTS)
WPM_MODULATION_RANGE = (75, 165)  # non-uniform cadence swings
POST_HOOK_SILENCE_DROP_RANGE = (1.5, 3.0)  # sec silence after paradox question

# Chain bridge transition durations (from V8.0 / ERR-20261122-01)
TRANSITION_DURATIONS: dict[str, float] = {
    "seam_chain_bridge": 0.28,
    "map_camera_zoom_match": 0.55,
    "optical_anamorphic_dissolve": 0.45,
    "hard_cut_j_cut": 0.0,
    "obsidian_act_fade": 0.40,
    "continuous_cut": 0.0,
}

# Canonical OpenCV 8-bit Lab (L in [0..255], a/b centered at 128) Act palettes
# used by `match_frame_to_act_palette()` so consecutive shots stay color-harmonized.
CANONICAL_ACT_PALETTES: dict[str, dict[str, Any]] = {
    "night_torch_ambush": {
        "lab_mean": (76.0, 130.5, 133.5),
        "lab_std": (46.0, 8.5, 12.0),
        "description": "Pre-dawn river torchlight: deep obsidian slate + restrained warm ember",
    },
    "imperial_court_tension": {
        "lab_mean": (94.0, 131.5, 136.0),
        "lab_std": (48.0, 9.0, 12.5),
        "description": "Candlelit throne hall / political conspiracy: aged bronze + muted vermilion",
    },
    "twilight_steel_prep": {
        "lab_mean": (98.0, 127.5, 126.5),
        "lab_std": (48.0, 7.5, 10.5),
        "description": "Overcast tidal karst & iron forge: cold limestone slate + soot iron",
    },
    "high_tide_river_ops": {
        "lab_mean": (112.0, 126.8, 127.8),
        "lab_std": (46.0, 7.2, 10.2),
        "description": "Overcast maritime estuary: muted silver-slate water + weathered timber",
    },
    "storm_clash_climax": {
        "lab_mean": (92.0, 130.0, 131.5),
        "lab_std": (50.0, 9.2, 12.2),
        "description": "Ebb-tide river clash: storm slate shadows + muted ironwood & firelight",
    },
    "dawn_citadel_triumph": {
        "lab_mean": (118.0, 130.5, 136.5),
        "lab_std": (46.0, 8.0, 12.0),
        "description": "Muted golden-hour dawn over ancient citadel: warm sandstone + soft haze",
    },
    "neutral_35mm_doc": {
        "lab_mean": (104.0, 128.5, 130.5),
        "lab_std": (47.0, 8.0, 11.0),
        "description": "Balanced Kodak 2383 35mm documentary baseline",
    },
}

ACT_INDEX_TO_PALETTE: dict[int, str] = {
    1: "night_torch_ambush",
    2: "imperial_court_tension",
    3: "twilight_steel_prep",
    4: "high_tide_river_ops",
    5: "storm_clash_climax",
    6: "dawn_citadel_triumph",
}

# V11.5 Hard Anti-AI Visual & Historical QA Rules (SSOT)
ANTI_AI_QA_RULES: dict[str, Any] = {
    "version": "11.5.0",
    "historical_flag_anachronisms": {
        "banned_terms": [
            "red flag with yellow star",
            "yellow star flag",
            "vietnam national flag",
            "modern vietnamese flag",
            "communist flag",
            "five-pointed star banner",
            "gold star red banner",
            "cờ đỏ sao vàng",
        ],
        "required_replacement": (
            "plain weathered period-accurate hemp, indigo, or faded bronze pennants "
            "with zero letters, zero modern emblems, and zero stars"
        ),
    },
    "anti_plastic_cgi_bans": {
        "banned_terms": [
            "plastic skin",
            "waxy skin",
            "airbrushed",
            "porcelain smooth skin",
            "unreal engine",
            "octane render",
            "cgi 3d render",
            "hyper glossy",
            "tilt-shift",
            "miniature diorama",
            "toy-like",
            "symmetrical clone crowd",
            "identical twin soldiers",
            "neon cyan",
            "cyberpunk glow",
        ],
        "required_look": (
            "authentic 35mm Kodak Vision3 celluloid cinematography, weathered natural skin pores, "
            "asymmetric organic crowds with varied stances and gear, matte historical fabrics, "
            "natural optical depth of field"
        ),
    },
    "physics_and_motion_bans": {
        "banned_defects": [
            "floating_oars",
            "dry_deck_waterfalls",
            "180_deg_hull_flip",
            "opposite_wind_sails",
            "morphed_hands_or_extra_fingers",
            "frozen_slide",
        ],
        "prompt_red_flags": [
            "floating oars",
            "waterfall on wooden deck",
            "ship flipping 180",
            "sails blowing opposite",
        ],
    },
    "character_continuity_rules": {
        "require_reference_media_ids": True,
        "same_profile_media_lock": True,
        "max_refs_per_beat": 3,
    },
    "color_continuity_thresholds": {
        "max_delta_e_consecutive": 22.0,
        "max_luma_jump": 38.0,
        "max_saturation_p95": 185.0,
        "max_neon_cyan_ratio": 0.08,
    },
    "negative_prompt_guardrail": (
        "Shot on real 35mm Kodak Vision3 cinema film, weathered matte historical textures, "
        "organic asymmetric crowds, plain unmarked historical pennants, zero modern national flags, "
        "zero yellow stars, zero plastic waxy CGI skin, zero tilt-shift miniature look, "
        "zero neon teal-orange AI glow, no text, no letters, no watermarks."
    ),
}

# Permanently banned transitions (from PLAYBOOK.md ERR-20261122-01)
BANNED_TRANSITIONS: tuple[str, ...] = (
    "dust_smoke_cloud",
    "river_mist_map_dive",
    "directional_flow_chain_transition",
    "horizontal_whip_slide",
    "procedural_fog_wipe",
    "procedural_mist_wipe",
    "smoothleft",
    "smoothright",
    "smoothup",
    "smoothdown",
)

# Diegetic SFX catalog for silence_drop / sfx_solo beats
DIEGETIC_SFX_CATALOG: dict[str, dict[str, Any]] = {
    "ticking_countdown_pulse": {
        "duration_sec": 2.0,
        "freq_hz": 2.0,
        "stereo_width": 0.3,
        "description": "Metronomic countdown tick building suspense.",
    },
    "cannon_thunder": {
        "duration_sec": 1.8,
        "freq_hz": 42.0,
        "stereo_width": 0.9,
        "description": "Period-authentic cannon blast with reverb tail.",
    },
    "wooden_hull_creak": {
        "duration_sec": 2.5,
        "freq_hz": 180.0,
        "stereo_width": 0.6,
        "description": "Wooden ship hull stress creaking under pressure.",
    },
    "night_river_wind": {
        "duration_sec": 3.0,
        "freq_hz": 0.0,
        "stereo_width": 0.8,
        "description": "Atmospheric night wind across river water surface.",
    },
    "war_drum_impact": {
        "duration_sec": 0.8,
        "freq_hz": 56.0,
        "stereo_width": 0.5,
        "description": "Single heavy war drum impact with bronze overtones.",
    },
    "sub_bass_drop": {
        "duration_sec": 1.2,
        "freq_hz": 36.0,
        "stereo_width": 0.2,
        "description": "Deep sub-bass drop before the hook question.",
    },
}


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class VisualMode(str, Enum):
    """The 4 visual language modes in the choreography."""
    MOVING_CINEMA = "moving_cinema"
    SPATIAL_TERRAIN_OPS = "spatial_terrain_ops"
    FORENSIC_EVIDENCE_REVEAL = "forensic_evidence_reveal"
    MACRO_PARALLAX_STILL = "macro_parallax_still"


class ChainPattern(str, Enum):
    """Moving cinema chain patterns."""
    BALANCED_2BEAT = "balanced_2beat"
    TENSION_RAPID = "tension_rapid"
    CONTINUOUS_LONG_TAKE = "continuous_long_take"


class ForensicLayout(str, Enum):
    """Forensic evidence reveal layout types."""
    COUNTDOWN_CLOCK = "countdown_clock"
    PRIMARY_CHRONICLE = "primary_chronicle"
    FORCE_COMPARISON = "force_comparison"


class TransitionType(str, Enum):
    """Allowed professional transitions (V8.0 rules)."""
    SEAM_CHAIN_BRIDGE = "seam_chain_bridge"
    MAP_CAMERA_ZOOM_MATCH = "map_camera_zoom_match"
    OPTICAL_ANAMORPHIC_DISSOLVE = "optical_anamorphic_dissolve"
    HARD_CUT_J_CUT = "hard_cut_j_cut"
    OBSIDIAN_ACT_FADE = "obsidian_act_fade"
    CONTINUOUS_CUT = "continuous_cut"


class DeliveryMode(str, Enum):
    """Voice delivery profiles for prosody sculpting."""
    MEASURED_AUTHORITY = "measured_authority"
    TENSE_WHISPER = "tense_whisper"
    URGENT_ESCALATION = "urgent_escalation"
    REFLECTIVE_LESSON = "reflective_lesson"
    SILENCE = "silence"


# ---------------------------------------------------------------------------
# Data Classes — Spec Schema
# ---------------------------------------------------------------------------
@dataclass
class MovingCinemaSpec:
    """Spec for a moving_cinema visual beat."""
    prompt: str = ""
    chain_pattern: str = "balanced_2beat"
    clip_duration_range: tuple[float, float] = RAPID_TENSION_RANGE
    seam_mode: bool = True
    model: str = "veo_3_1_lite"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.prompt.strip():
            errors.append("moving_cinema.prompt must not be empty")
        lo, hi = self.clip_duration_range
        if lo < 1.0 or hi > 8.0 or lo > hi:
            errors.append(
                f"clip_duration_range ({lo}, {hi}) out of bounds [1.0, 8.0]"
            )
        if self.model not in ("veo_3_1_lite", "macaron_cookie"):
            errors.append(
                f"model must be veo_3_1_lite or macaron_cookie, got {self.model}"
            )
        return errors


@dataclass
class SpatialTerrainSpec:
    """Spec for a spatial_terrain_ops visual beat."""
    region_key: str = "east_asia_vietnam"
    preset: str = ""
    geo_clash_spec: str | dict[str, Any] | None = None  # preset name or custom dict for geo_empire_clash_3d
    prompt: str = ""
    camera_pitch_deg: float = 38.0
    camera_start_zoom: float = 1.0
    camera_end_zoom: float = 3.5
    camera_fly_duration_sec: float = 4.0
    camera_easing: str = "ease_in_out_cubic"
    tactical_callouts: list[dict[str, Any]] = field(default_factory=list)
    sovereignty_labels: list[dict[str, Any]] = field(default_factory=list)
    tidal_animation: dict[str, Any] = field(default_factory=dict)
    waypoint_step: int = 0
    de_modernize: bool = True
    sovereignty_markers: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.camera_start_zoom < 0.5 or self.camera_end_zoom > 12.0:
            errors.append("camera zoom out of safe range [0.5, 12.0]")
        if self.camera_fly_duration_sec < 1.0 or self.camera_fly_duration_sec > 10.0:
            errors.append("camera_fly_duration_sec must be in [1.0, 10.0]")
        return errors


@dataclass
class ForensicRevealSpec:
    """Spec for a forensic_evidence_reveal visual beat."""
    layout: str = "countdown_clock"
    timestamp_text: str = ""
    headline_text: str = ""
    prompt: str = ""
    spotlight_mask: bool = True
    depth_of_field_blur: float = 12.0
    zero_rectangles: bool = True
    zero_left_stripes: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        valid_layouts = {e.value for e in ForensicLayout}
        if self.layout not in valid_layouts:
            errors.append(
                f"forensic layout must be one of {valid_layouts}, got {self.layout}"
            )
        if self.depth_of_field_blur < 0.0 or self.depth_of_field_blur > 50.0:
            errors.append("depth_of_field_blur out of [0, 50] range")
        if not self.zero_rectangles:
            errors.append("zero_rectangles must be True (0 PowerPoint boxes)")
        if not self.zero_left_stripes:
            errors.append("zero_left_stripes must be True")
        return errors


@dataclass
class MacroParallaxSpec:
    """Spec for a macro_parallax_still visual beat."""
    prompt: str = ""
    max_hold_sec: float = 3.5
    camera_motion: str = "parallax_push_in"
    depth_layers: int = 2
    float32_subpixel: bool = True

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.prompt.strip():
            errors.append("macro_parallax_still.prompt must not be empty")
        if self.max_hold_sec > MACRO_PARALLAX_MAX_HOLD_SEC:
            errors.append(
                f"max_hold_sec ({self.max_hold_sec}) exceeds limit "
                f"({MACRO_PARALLAX_MAX_HOLD_SEC}s)"
            )
        if not self.float32_subpixel:
            errors.append(
                "float32_subpixel must be True to avoid 15Hz zoompan jitter"
            )
        return errors


@dataclass
class CharacterAnchorSpec:
    """Canonical character/troop archetype for Stage A0 Flow `reference_media_ids` locking."""
    character_id: str
    name_vi: str
    faction: str = "dai_viet"
    dynasty_era: str = "10th century Dai Viet"
    face_and_age_dna: str = ""
    armor_and_wardrobe_lock: str = ""
    signature_props: list[str] = field(default_factory=list)
    color_palette_hex: list[str] = field(default_factory=list)
    anti_anachronism_bans: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    anchor_image_path: str = ""
    profile_media_ids: dict[str, str] = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        cid = (self.character_id or "").strip()
        if not cid or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,63}", cid):
            errors.append(
                f"character_id {self.character_id!r} must be lowercase snake/kebab case (2..64 chars)"
            )
        if not (self.name_vi or "").strip():
            errors.append(f"character {cid!r}: name_vi is required")
        if not (self.face_and_age_dna or "").strip():
            errors.append(f"character {cid!r}: face_and_age_dna is required to lock visual identity")
        if not (self.armor_and_wardrobe_lock or "").strip():
            errors.append(f"character {cid!r}: armor_and_wardrobe_lock is required to lock costume continuity")
        combined = f"{self.face_and_age_dna} {self.armor_and_wardrobe_lock}".lower()
        for pat in (
            r"(?<!zero\s)(?<!no\s)\b(?:celebrity|movie\s+star|hollywood\s+actor|likeness\s+of)\b",
            r"(?<!zero\s)(?<!no\s)\b(?:red\s+flag\s+with\s+yellow\s+star|vietnam\s+national\s+flag|cờ\s+đỏ\s+sao\s+vàng)\b",
        ):
            if re.search(pat, combined):
                errors.append(
                    f"character {cid!r}: prohibited celebrity-likeness or modern-flag phrase in character DNA"
                )
        return errors


@dataclass
class BeatSpec:
    """A single beat in the reborn long cinema timeline."""
    beat_id: str = ""
    beat_index: int = 0
    visual_mode: str = "moving_cinema"
    tts_text: str = ""

    # Acoustic breathing
    pre_silence_sec: float = 0.0
    post_sfx_hold_sec: float = 0.0
    is_silence_drop: bool = False
    sfx_solo_id: str | None = None
    diegetic_sfx: str | None = None

    # Visual mode sub-specs (only the active mode's spec is populated)
    moving_cinema: MovingCinemaSpec | None = None
    spatial_terrain_ops: SpatialTerrainSpec | None = None
    forensic_evidence_reveal: ForensicRevealSpec | None = None
    macro_parallax_still: MacroParallaxSpec | None = None

    # Shared visual properties
    camera_move: str = "parallax_push_in"
    vfx_shader: str = "kodak_35mm_grain"
    show_keyword: bool = False
    main_word: str = ""
    target_keyword: str = ""
    delivery_mode: str = "measured_authority"
    segment: str = ""
    visual_submode: str = ""
    hud_callout: dict[str, Any] | None = None
    reuse_pilot_clip: str | None = None
    character_ids: list[str] = field(default_factory=list)
    act_palette: str = ""

    def effective_visual_channel(self) -> str:
        """Distinguish Flow aerial/underwater tactical beats from ground POV beats."""
        if self.visual_mode == VisualMode.MOVING_CINEMA.value:
            seg_l = (self.segment or "").lower()
            sub_l = (self.visual_submode or "").lower()
            if (
                self.hud_callout
                or any(k in sub_l for k in ("tactical", "aerial", "cutaway", "underwater"))
                or any(k in seg_l for k in ("tactical", "aerial", "geo_", "tidal", "trap"))
            ):
                return "moving_cinema_tactical"
        return self.visual_mode

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.beat_id:
            errors.append("beat_id is required")

        valid_modes = {e.value for e in VisualMode}
        if self.visual_mode not in valid_modes:
            errors.append(
                f"visual_mode must be one of {valid_modes}, got {self.visual_mode}"
            )

        # Silence/SFX-solo beats need no TTS text
        if not self.is_silence_drop and not self.tts_text.strip():
            errors.append(f"beat {self.beat_id}: tts_text required for non-silence beats")

        # Validate silence bounds
        if self.pre_silence_sec < 0.0 or self.pre_silence_sec > SILENCE_MAX_SEC:
            errors.append(
                f"pre_silence_sec ({self.pre_silence_sec}) out of [0, {SILENCE_MAX_SEC}]"
            )
        if self.post_sfx_hold_sec < 0.0 or self.post_sfx_hold_sec > SILENCE_MAX_SEC:
            errors.append(
                f"post_sfx_hold_sec ({self.post_sfx_hold_sec}) out of "
                f"[0, {SILENCE_MAX_SEC}]"
            )

        # Validate SFX solo ID
        if self.sfx_solo_id and self.sfx_solo_id not in DIEGETIC_SFX_CATALOG:
            errors.append(
                f"sfx_solo_id {self.sfx_solo_id!r} not in DIEGETIC_SFX_CATALOG"
            )

        # Seekbar-safe guard for tactical HUD callouts (ZERO text below y=0.76*H)
        if isinstance(self.hud_callout, dict):
            anchor = self.hud_callout.get("anchor_xy")
            if isinstance(anchor, (list, tuple)) and len(anchor) >= 2:
                ay = float(anchor[1])
                if ay > 0.76:
                    errors.append(
                        f"beat {self.beat_id}: hud_callout anchor_xy y={ay:.2f} > 0.76 "
                        f"(player seekbar hazard)"
                    )

        # Validate the active visual mode's sub-spec
        active_spec = self._get_active_visual_spec()
        if active_spec is not None:
            errors.extend(active_spec.validate())

        return errors

    def _get_active_visual_spec(
        self,
    ) -> MovingCinemaSpec | SpatialTerrainSpec | ForensicRevealSpec | MacroParallaxSpec | None:
        mapping: dict[str, Any] = {
            VisualMode.MOVING_CINEMA.value: self.moving_cinema,
            VisualMode.SPATIAL_TERRAIN_OPS.value: self.spatial_terrain_ops,
            VisualMode.FORENSIC_EVIDENCE_REVEAL.value: self.forensic_evidence_reveal,
            VisualMode.MACRO_PARALLAX_STILL.value: self.macro_parallax_still,
        }
        return mapping.get(self.visual_mode)


@dataclass
class ChapterSpec:
    """A chapter containing multiple beats."""
    chapter_idx: int = 1
    chapter_header: str = "CHƯƠNG I"
    chapter_title: str = ""
    chapter_style: str = "minimal_center_card"
    beats: list[BeatSpec] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.chapter_title.strip():
            errors.append(f"chapter {self.chapter_idx}: chapter_title is required")
        if self.chapter_style not in ("minimal_center_card", "in_scene_cinema_title"):
            errors.append(
                f"chapter_style must be minimal_center_card or "
                f"in_scene_cinema_title, got {self.chapter_style}"
            )
        for b in self.beats:
            errors.extend(b.validate())
        return errors


@dataclass
class TransitionRules:
    """Transition rules for the entire video."""
    intra_chain: str = "continuous_cut"
    scene_boundary: str = "optical_anamorphic_dissolve"
    map_entry: str = "map_camera_zoom_match"
    act_break: str = "obsidian_act_fade"

    def validate(self) -> list[str]:
        errors: list[str] = []
        for attr_name in ("intra_chain", "scene_boundary", "map_entry", "act_break"):
            val = getattr(self, attr_name)
            if val in BANNED_TRANSITIONS:
                errors.append(f"transition {attr_name}={val!r} is BANNED")
            if val not in TRANSITION_DURATIONS:
                errors.append(
                    f"transition {attr_name}={val!r} not in allowed set: "
                    f"{set(TRANSITION_DURATIONS.keys())}"
                )
        return errors


@dataclass
class PilotSpec:
    """Top-level spec for the reborn long cinema pilot."""
    engine: str = ENGINE_ID
    engine_version: str = ENGINE_VERSION
    channel_id: str = "su_ke_lai"
    job_id: str = "vn_su_ke_lai_reborn_pilot"
    format: str = "long_16x9"
    resolution: str = RESOLUTION
    fps: int = FPS
    target_duration_range: tuple[float, float] = (PILOT_MIN_DURATION_SEC, PILOT_MAX_DURATION_SEC)

    # Audio
    sample_rate: int = TARGET_SR
    audio_channels: int = 2
    target_lufs: float = TARGET_LUFS
    max_true_peak_dbtp: float = MAX_TRUE_PEAK_DBTP
    voice_id: str = "VietNarrator_su_ke_lai"
    voice_profile: str = "sys/assets/voices/ch_su_ke_lai/profile.json"

    # Acoustic breathing
    j_cut_prelap_sec: float = J_CUT_PRELAP_SEC
    cold_open_sfx_lead_in_sec: float = 3.2  # diegetic SFX before Beat 0 (radar: 2.5–4.0s)
    mix_stems: list[str] = field(
        default_factory=lambda: [
            "narration",
            "diegetic_sfx",
            "silence_bed",
            "bgm_tension",
            "room_tone",
        ]
    )

    # Chapters & beats
    chapters: list[ChapterSpec] = field(default_factory=list)

    # Transitions
    transitions: TransitionRules = field(default_factory=TransitionRules)

    # Watermark
    watermark_path: str = "sys/channels/su_ke_lai/assets/watermark_150x150.png"
    watermark_position: str = WATERMARK_POS
    delogo: bool = DELOGO_ENABLED

    # Thumbnail (Flow-native, zero PIL/HTML overlay)
    thumbnail_prompt: str = ""
    thumbnail_max_size_bytes: int = 2_000_000  # 2MB

    # Optional final MP4 output filename (e.g. from output_paths.final_mp4)
    output_mp4_name: str = ""

    # V11.5 Character Bible & Master 35mm Color Grade
    character_roster: list[CharacterAnchorSpec] = field(default_factory=list)
    color_grade: str = DEFAULT_COLOR_GRADE

    def validate(self) -> list[str]:
        """Validate entire spec; returns list of error strings (empty = valid)."""
        errors: list[str] = []

        # Engine check
        if self.engine != ENGINE_ID:
            errors.append(f"engine must be {ENGINE_ID!r}, got {self.engine!r}")
        if self.resolution not in ("1080p", "1440p", "360p"):
            errors.append(f"unsupported resolution {self.resolution!r}")
        if self.fps != FPS:
            errors.append(f"fps must be {FPS}, got {self.fps}")
        if self.sample_rate != TARGET_SR:
            errors.append(f"sample_rate must be {TARGET_SR}")

        # Voice gate: NEVER vi-VN-NamMinhNeural (ERR-20261108-03)
        if "NamMinh" in self.voice_id or "vi-VN-NamMinh" in self.voice_id:
            errors.append(
                "BLOCKED: vi-VN-NamMinhNeural is permanently banned. "
                "Use VietNarrator_<channel_id> via Colab T4 OmniVoice."
            )

        # J-cut
        if self.j_cut_prelap_sec > 0.0:
            errors.append("j_cut_prelap_sec must be <= 0 (negative = pre-lap)")

        # Cold open SFX lead-in (radar benchmark: 2.5–4.0s, never start TTS at 0.0)
        if self.cold_open_sfx_lead_in_sec < COLD_OPEN_SFX_LEAD_IN_RANGE[0]:
            errors.append(
                f"cold_open_sfx_lead_in_sec must be >= {COLD_OPEN_SFX_LEAD_IN_RANGE[0]}s "
                f"(0/10 breakout channels start TTS at 0.0s)"
            )

        # Stem count
        if len(self.mix_stems) != MIX_STEM_COUNT:
            errors.append(
                f"mix_stems must have exactly {MIX_STEM_COUNT} stems, "
                f"got {len(self.mix_stems)}"
            )

        # Chapters
        if not self.chapters:
            errors.append("at least 1 chapter required")
        for ch in self.chapters:
            errors.extend(ch.validate())

        # Transitions
        errors.extend(self.transitions.validate())

        # Watermark position
        if self.watermark_position != WATERMARK_POS:
            errors.append(
                f"watermark must be pinned at {WATERMARK_POS!r} "
                f"(got {self.watermark_position!r})"
            )

        # V11.5 Color grade check
        if self.color_grade not in VALID_COLOR_GRADES:
            errors.append(
                f"color_grade must be one of {VALID_COLOR_GRADES}, got {self.color_grade!r}"
            )

        # V11.5 Character roster validation & referential integrity
        roster_ids: set[str] = set()
        for ch_anchor in self.character_roster:
            errors.extend(ch_anchor.validate())
            if ch_anchor.character_id in roster_ids:
                errors.append(f"duplicate character_id in character_roster: {ch_anchor.character_id!r}")
            roster_ids.add(ch_anchor.character_id)

        if roster_ids:
            for b in self.all_beats():
                for cid in b.character_ids:
                    if cid not in roster_ids:
                        errors.append(
                            f"beat {b.beat_id}: unknown character_id {cid!r} not found in character_roster"
                        )

        return errors

    def all_beats(self) -> list[BeatSpec]:
        """Flatten all beats across all chapters."""
        result: list[BeatSpec] = []
        for ch in self.chapters:
            result.extend(ch.beats)
        return result

    def beat_count(self) -> int:
        return sum(len(ch.beats) for ch in self.chapters)

    def visual_mode_distribution(self) -> dict[str, int]:
        """Count how many beats use each visual mode."""
        dist: dict[str, int] = {}
        for b in self.all_beats():
            dist[b.visual_mode] = dist.get(b.visual_mode, 0) + 1
        return dist

    def silence_drop_count(self) -> int:
        return sum(1 for b in self.all_beats() if b.is_silence_drop)


# ---------------------------------------------------------------------------
# Spec Parsing (JSON -> PilotSpec)
# ---------------------------------------------------------------------------
def _parse_moving_cinema(raw: dict[str, Any] | None) -> MovingCinemaSpec | None:
    if not raw:
        return None
    dr = raw.get("clip_duration_range", list(RAPID_TENSION_RANGE))
    return MovingCinemaSpec(
        prompt=str(raw.get("prompt", "")),
        chain_pattern=str(raw.get("chain_pattern", "balanced_2beat")),
        clip_duration_range=(float(dr[0]), float(dr[1])) if len(dr) >= 2 else RAPID_TENSION_RANGE,
        seam_mode=bool(raw.get("seam_mode", True)),
        model=str(raw.get("model", "veo_3_1_lite")),
    )


def _parse_spatial_terrain(raw: dict[str, Any] | None) -> SpatialTerrainSpec | None:
    if not raw:
        return None
    cam = raw.get("camera_fly_in", {})
    preset = str(raw.get("preset") or "")
    geo_spec = raw.get("geo_clash_spec")
    if geo_spec is None and preset:
        geo_spec = preset
    return SpatialTerrainSpec(
        region_key=str(raw.get("region_key", "east_asia_vietnam")),
        preset=preset,
        geo_clash_spec=geo_spec,
        prompt=str(raw.get("prompt") or ""),
        camera_pitch_deg=float(raw.get("camera_pitch_deg", 38.0)),
        camera_start_zoom=float(cam.get("start_zoom", 1.0)),
        camera_end_zoom=float(cam.get("end_zoom", 3.5)),
        camera_fly_duration_sec=float(cam.get("duration_sec", 4.0)),
        camera_easing=str(cam.get("easing", "ease_in_out_cubic")),
        tactical_callouts=list(raw.get("tactical_callouts", [])),
        sovereignty_labels=list(raw.get("sovereignty_labels", [])),
        tidal_animation=dict(raw.get("tidal_animation") or {}),
        waypoint_step=int(raw.get("waypoint_step") or 0),
        de_modernize=bool(raw.get("de_modernize", True)),
        sovereignty_markers=bool(raw.get("sovereignty_markers", True)),
    )


def _parse_forensic_reveal(raw: dict[str, Any] | None) -> ForensicRevealSpec | None:
    if not raw:
        return None
    raw_ts = raw.get("timestamp_text")
    return ForensicRevealSpec(
        layout=str(raw.get("layout", "countdown_clock")),
        timestamp_text="" if raw_ts is None else str(raw_ts),
        headline_text=str(raw.get("headline_text") or ""),
        prompt=str(raw.get("prompt") or ""),
        spotlight_mask=bool(raw.get("spotlight_mask", True)),
        depth_of_field_blur=float(raw.get("depth_of_field_blur", 12.0)),
        zero_rectangles=bool(raw.get("zero_rectangles", True)),
        zero_left_stripes=bool(raw.get("zero_left_stripes", True)),
    )


def _parse_macro_parallax(raw: dict[str, Any] | None) -> MacroParallaxSpec | None:
    if not raw:
        return None
    return MacroParallaxSpec(
        prompt=str(raw.get("prompt", "")),
        max_hold_sec=float(raw.get("max_hold_sec", 3.5)),
        camera_motion=str(raw.get("camera_motion", "parallax_push_in")),
        depth_layers=int(raw.get("depth_layers", 2)),
        float32_subpixel=bool(raw.get("float32_subpixel", True)),
    )


def _parse_character_anchor(raw: dict[str, Any]) -> CharacterAnchorSpec:
    def _to_str_list(val: Any) -> list[str]:
        if isinstance(val, list):
            return [str(x).strip() for x in val if str(x).strip()]
        if isinstance(val, str) and val.strip():
            return [x.strip() for x in val.split(",") if x.strip()]
        return []

    raw_pm = raw.get("profile_media_ids")
    pm_dict = {str(k): str(v) for k, v in raw_pm.items() if k and v} if isinstance(raw_pm, dict) else {}
    return CharacterAnchorSpec(
        character_id=str(raw.get("character_id") or "").strip(),
        name_vi=str(raw.get("name_vi") or "").strip(),
        faction=str(raw.get("faction") or "dai_viet").strip(),
        dynasty_era=str(raw.get("dynasty_era") or "10th century Dai Viet").strip(),
        face_and_age_dna=str(raw.get("face_and_age_dna") or raw.get("face_dna") or "").strip(),
        armor_and_wardrobe_lock=str(
            raw.get("armor_and_wardrobe_lock") or raw.get("wardrobe_lock") or ""
        ).strip(),
        signature_props=_to_str_list(raw.get("signature_props") or raw.get("signature_weapons_and_props")),
        color_palette_hex=_to_str_list(raw.get("color_palette_hex")),
        anti_anachronism_bans=_to_str_list(raw.get("anti_anachronism_bans")),
        aliases=_to_str_list(raw.get("aliases")),
        anchor_image_path=str(raw.get("anchor_image_path") or "").strip(),
        profile_media_ids=pm_dict,
    )


def _parse_beat(raw: dict[str, Any]) -> BeatSpec:
    mc_raw = raw.get("moving_cinema") or {}
    hud = raw.get("hud_callout")
    if hud is None and isinstance(mc_raw, dict):
        hud = mc_raw.get("hud_callout")
    raw_cids = raw.get("character_ids")
    if raw_cids is None and isinstance(mc_raw, dict):
        raw_cids = mc_raw.get("character_ids")
    char_ids = [str(c).strip() for c in raw_cids if str(c).strip()] if isinstance(raw_cids, list) else []
    return BeatSpec(
        beat_id=str(raw.get("beat_id", "")),
        beat_index=int(raw.get("beat_index", 0)),
        visual_mode=str(raw.get("visual_mode", "moving_cinema")),
        tts_text=str(raw.get("tts_text", "")),
        pre_silence_sec=float(raw.get("pre_silence_sec", 0.0)),
        post_sfx_hold_sec=float(raw.get("post_sfx_hold_sec", 0.0)),
        is_silence_drop=bool(raw.get("is_silence_drop", False)),
        sfx_solo_id=raw.get("sfx_solo_id"),
        diegetic_sfx=raw.get("diegetic_sfx"),
        moving_cinema=_parse_moving_cinema(raw.get("moving_cinema")),
        spatial_terrain_ops=_parse_spatial_terrain(raw.get("spatial_terrain_ops")),
        forensic_evidence_reveal=_parse_forensic_reveal(
            raw.get("forensic_evidence_reveal")
        ),
        macro_parallax_still=_parse_macro_parallax(raw.get("macro_parallax_still")),
        camera_move=str(raw.get("camera_move", "parallax_push_in")),
        vfx_shader=str(raw.get("vfx_shader", "kodak_35mm_grain")),
        show_keyword=bool(raw.get("show_keyword", False)),
        main_word=str(raw.get("main_word", "")),
        target_keyword=str(raw.get("target_keyword", "")),
        delivery_mode=str(raw.get("delivery_mode", "measured_authority")),
        segment=str(raw.get("segment") or ""),
        visual_submode=str(raw.get("visual_submode") or (mc_raw.get("visual_submode") if isinstance(mc_raw, dict) else "") or ""),
        hud_callout=dict(hud) if isinstance(hud, dict) else None,
        reuse_pilot_clip=str(raw["reuse_pilot_clip"]) if raw.get("reuse_pilot_clip") else None,
        character_ids=char_ids,
        act_palette=str(raw.get("act_palette") or ""),
    )


def _parse_chapter(raw: dict[str, Any]) -> ChapterSpec:
    beats = [_parse_beat(b) for b in raw.get("beats", [])]
    return ChapterSpec(
        chapter_idx=int(raw.get("chapter_idx", 1)),
        chapter_header=str(raw.get("chapter_header", "CHƯƠNG I")),
        chapter_title=str(raw.get("chapter_title", "")),
        chapter_style=str(raw.get("chapter_style", "minimal_center_card")),
        beats=beats,
    )


def load_pilot_spec(spec_path: Path | str) -> PilotSpec:
    """Load and parse a pilot_spec.json file into a validated PilotSpec."""
    path = Path(spec_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return parse_pilot_spec(data)


def parse_pilot_spec(data: dict[str, Any]) -> PilotSpec:
    """Parse a raw dict into a PilotSpec object."""
    chapters = [_parse_chapter(ch) for ch in data.get("chapters", [])]

    trans_raw = data.get("transitions", {})
    transitions = TransitionRules(
        intra_chain=str(trans_raw.get("intra_chain", "continuous_cut")),
        scene_boundary=str(trans_raw.get("scene_boundary", "optical_anamorphic_dissolve")),
        map_entry=str(trans_raw.get("map_entry", "map_camera_zoom_match")),
        act_break=str(trans_raw.get("act_break", "obsidian_act_fade")),
    )

    audio_raw = data.get("audio", {})
    ab_raw = data.get("acoustic_breathing", {})
    thumb_raw = data.get("thumbnail", {})
    dr = data.get("target_duration_sec", [PILOT_MIN_DURATION_SEC, PILOT_MAX_DURATION_SEC])

    raw_roster = data.get("character_roster") or []
    character_roster = [
        _parse_character_anchor(item)
        for item in raw_roster
        if isinstance(item, dict)
    ]

    return PilotSpec(
        engine=str(data.get("engine", ENGINE_ID)),
        engine_version=str(data.get("engine_version", ENGINE_VERSION)),
        channel_id=str(data.get("channel_id", "su_ke_lai")),
        job_id=str(data.get("job_id", "vn_su_ke_lai_reborn_pilot")),
        format=str(data.get("format", "long_16x9")),
        resolution=str(data.get("resolution", RESOLUTION)),
        fps=int(data.get("fps", FPS)),
        target_duration_range=(float(dr[0]), float(dr[1])) if len(dr) >= 2 else (PILOT_MIN_DURATION_SEC, PILOT_MAX_DURATION_SEC),
        sample_rate=int(audio_raw.get("sample_rate", TARGET_SR)),
        audio_channels=int(audio_raw.get("channels", 2)),
        target_lufs=float(audio_raw.get("target_lufs", TARGET_LUFS)),
        max_true_peak_dbtp=float(audio_raw.get("max_true_peak_dbtp", MAX_TRUE_PEAK_DBTP)),
        voice_id=str(audio_raw.get("voice_id", "VietNarrator_su_ke_lai")),
        voice_profile=str(audio_raw.get("voice_profile", "sys/assets/voices/ch_su_ke_lai/profile.json")),
        j_cut_prelap_sec=float(ab_raw.get("j_cut_prelap_sec", J_CUT_PRELAP_SEC)),
        cold_open_sfx_lead_in_sec=float(ab_raw.get("cold_open_sfx_lead_in_sec", 3.2)),
        mix_stems=list(ab_raw.get("mix_stems", ["narration", "diegetic_sfx", "silence_bed", "bgm_tension", "room_tone"])),
        chapters=chapters,
        transitions=transitions,
        watermark_path=str(data.get("watermark", {}).get("path", "sys/channels/su_ke_lai/assets/watermark_150x150.png")),
        watermark_position=str(data.get("watermark", {}).get("position", WATERMARK_POS)),
        delogo=bool(data.get("watermark", {}).get("delogo", True)),
        thumbnail_prompt=str(thumb_raw.get("prompt", "")),
        thumbnail_max_size_bytes=int(thumb_raw.get("max_size_bytes", 2_000_000)),
        output_mp4_name=str((data.get("output_paths") or {}).get("final_mp4") or ""),
        character_roster=character_roster,
        color_grade=str(data.get("color_grade") or DEFAULT_COLOR_GRADE),
    )


# ---------------------------------------------------------------------------
# Timeline Builder — converts PilotSpec into a rendered timeline
# ---------------------------------------------------------------------------
def _ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out for smooth camera fly-ins."""
    t = max(0.0, min(1.0, t))
    return 4.0 * t * t * t if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0


def compute_beat_timing(
    spec: PilotSpec,
    beat_durations: dict[str, float],
) -> list[dict[str, Any]]:
    """Compute absolute timing for each beat given TTS durations.

    Args:
        spec: The validated PilotSpec.
        beat_durations: Map of beat_id -> narration duration in seconds
            (from OmniVoice synthesis). Silence-drop beats have 0.0.

    Returns:
        List of timing dicts with keys: beat_id, chapter_idx, visual_mode,
        out_start, out_end, narration_start, narration_end,
        pre_silence_sec, post_sfx_hold_sec, j_cut_offset.
    """
    timeline: list[dict[str, Any]] = []
    cursor = 0.0

    for ch in spec.chapters:
        for beat in ch.beats:
            bid = beat.beat_id
            narr_dur = beat_durations.get(bid, 0.0)

            # Pre-silence: empty air before narration starts
            pre_sil = max(0.0, min(SILENCE_MAX_SEC, beat.pre_silence_sec))

            # Post-SFX hold: silence/SFX after narration ends
            post_hold = max(0.0, min(SILENCE_MAX_SEC, beat.post_sfx_hold_sec))

            # For silence_drop beats: the entire beat is non-speech
            if beat.is_silence_drop:
                sfx_dur = 0.0
                if beat.sfx_solo_id and beat.sfx_solo_id in DIEGETIC_SFX_CATALOG:
                    sfx_dur = DIEGETIC_SFX_CATALOG[beat.sfx_solo_id]["duration_sec"]
                beat_total = max(pre_sil + sfx_dur + post_hold, 1.0)
            else:
                beat_total = pre_sil + narr_dur + post_hold

            # J-cut offset for audio pre-lap
            j_offset = spec.j_cut_prelap_sec if cursor > 0.0 else 0.0

            out_start = cursor
            out_end = cursor + beat_total

            timeline.append({
                "beat_id": bid,
                "chapter_idx": ch.chapter_idx,
                "visual_mode": beat.visual_mode,
                "out_start": round(out_start, 4),
                "out_end": round(out_end, 4),
                "duration_sec": round(beat_total, 4),
                "narration_start": round(out_start + pre_sil, 4),
                "narration_end": round(out_start + pre_sil + narr_dur, 4),
                "narration_duration_sec": round(narr_dur, 4),
                "pre_silence_sec": round(pre_sil, 4),
                "post_sfx_hold_sec": round(post_hold, 4),
                "j_cut_offset": round(j_offset, 4),
                "is_silence_drop": beat.is_silence_drop,
                "sfx_solo_id": beat.sfx_solo_id,
                "delivery_mode": beat.delivery_mode,
            })

            cursor = out_end

    return timeline


# ---------------------------------------------------------------------------
# Omni 1.2 Flash (macaron_cookie) Native Variable-Duration Shot Planner
# ---------------------------------------------------------------------------
OMNI_1_2_VARIABLE_DURATIONS: tuple[int, ...] = (4, 6, 8, 10)
OMNI_1_2_CREDIT_COSTS: dict[int, int] = {4: 12, 6: 18, 8: 24, 10: 30}


def plan_omni_1_2_variable_duration_shot(
    beat: BeatSpec | dict[str, Any],
    beat_audio_dur_sec: float,
    next_beat_frame: str | Path | None = None,
    *,
    overhang_sec: float = 0.0,
) -> dict[str, Any]:
    """Route a `moving_cinema` beat onto native Omni 1.2 Flash (`macaron_cookie`) duration.

    Exploits all 4 native variable clip durations (`4s`, `6s`, `8s`, `10s`) in
    both Start-Frame (`macaron_cookie_i2v_{4s|6s|8s|10s}`) and Frame-Link
    (`macaron_cookie_i2v_fl_{4s|6s|8s|10s}`) modes so every beat plays at
    natural `1.0x` real-time speed with zero slow-mo stretch or loop:

    - `<= 4.0s`: `OMNI_1_2_FLASH_4S` (`duration_seconds=4`, tight single-action kinetic cut)
    - `4.0s–5.8s`: `OMNI_1_2_FLASH_6S` (`duration_seconds=6`, medium POV / weapon physics)
    - `5.8s–7.8s`: `OMNI_1_2_FLASH_8S` (`duration_seconds=8`, continuous trajectory glide)
    - `> 7.8s`: `OMNI_1_2_FLASH_10S` (`duration_seconds=10`, epic unbroken long-take with 3-phase choreography)
    """
    if isinstance(beat, BeatSpec):
        beat_id = beat.beat_id
        base_prompt = beat.moving_cinema.prompt if beat.moving_cinema else ""
        is_silence_drop = beat.is_silence_drop
    else:
        beat_id = str(beat.get("beat_id") or "")
        mc_raw = beat.get("moving_cinema") or {}
        base_prompt = str(mc_raw.get("prompt") or beat.get("prompt") or "")
        is_silence_drop = bool(beat.get("is_silence_drop", False))

    dur_in = max(0.1, float(beat_audio_dur_sec))
    effective_dur = dur_in + max(0.0, float(overhang_sec))

    if effective_dur <= 4.0:
        duration_seconds = 4
        shot_tier = "short_kinetic_4s"
        choreo_cue = (
            "[0-4s] tight single-action explosive 35mm kinetic beat, crisp shutter clarity, "
            "natural 1.0x real-time motion, zero slow-motion drift"
        )
    elif effective_dur <= 5.8:
        duration_seconds = 6
        shot_tier = "medium_pov_6s"
        choreo_cue = (
            "[0-3s] establish intimate warrior POV action in crisp 35mm depth -> "
            "[3-6s] dynamic camera push into decisive physical tension, 1.0x real-time motion"
        )
    elif effective_dur <= 7.8:
        duration_seconds = 8
        shot_tier = "continuous_glide_8s"
        choreo_cue = (
            "[0-4s] smooth unbroken 35mm camera trajectory establishing tactical geography -> "
            "[4-8s] continuous glide tightening into dramatic horizon reveal, 1.0x real-time motion"
        )
    else:
        duration_seconds = 10
        shot_tier = "epic_unbroken_long_take_10s"
        choreo_cue = (
            "[0-3.2s] quiet atmospheric dark river glide across torchlit timber and tidal water -> "
            "[3.2-7.0s] camera advances revealing decisive human/fleet scale in crisp 35mm chiaroscuro -> "
            "[7.0-10.0s] deliberate slow tension push-in holding unbroken 1.0x real-time motion"
        )

    has_end_frame = bool(next_beat_frame is not None and str(next_beat_frame).strip())
    end_image_path = str(next_beat_frame) if has_end_frame else None
    model_alias = f"OMNI_1_2_FLASH_{duration_seconds}S"
    resolved_model = (
        f"macaron_cookie_i2v_fl_{duration_seconds}s"
        if has_end_frame
        else f"macaron_cookie_i2v_{duration_seconds}s"
    )
    transition_mode = "frame_link" if has_end_frame else "seam"

    cleaned_base = base_prompt.strip()
    if "[0-" in cleaned_base:
        motion_prompt = cleaned_base
    elif cleaned_base:
        motion_prompt = f"{cleaned_base}; choreography: {choreo_cue}"
    else:
        motion_prompt = choreo_cue

    if is_silence_drop and "silent" not in motion_prompt.lower():
        motion_prompt = f"{motion_prompt}; intense non-verbal visual tension beat"

    return {
        "beat_id": beat_id,
        "beat_audio_dur_sec": round(dur_in, 4),
        "effective_dur_sec": round(effective_dur, 4),
        "duration_seconds": duration_seconds,
        "target_duration": float(duration_seconds),
        "model_alias": model_alias,
        "resolved_model": resolved_model,
        "has_end_frame": has_end_frame,
        "end_image_path": end_image_path,
        "transition_mode": transition_mode,
        "shot_tier": shot_tier,
        "credit_cost": OMNI_1_2_CREDIT_COSTS[duration_seconds],
        "motion_prompt": motion_prompt,
        "expected_playback_speed": round(max(1.0, dur_in / float(duration_seconds)), 4),
    }


def plan_pilot_omni_1_2_manifest(
    spec: PilotSpec,
    beat_durations: dict[str, float],
    frames_dir: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Plan native Omni 1.2 Flash (`4s/6s/8s/10s`) shots for all `moving_cinema` beats.

    Automatically links consecutive same-chapter `moving_cinema` beats with
    Frame-Link (`macaron_cookie_i2v_fl_{4s|6s|8s|10s}`) whenever `frames_dir`
    contains the next beat's anchor frame (or when `frames_dir` is provided for
    planning before generation).
    """
    all_beats = spec.all_beats()
    ch_by_beat: dict[str, int] = {}
    for ch in spec.chapters:
        for b in ch.beats:
            ch_by_beat[b.beat_id] = ch.chapter_idx

    fdir = Path(frames_dir) if frames_dir is not None else None
    planned: list[dict[str, Any]] = []

    for idx, beat in enumerate(all_beats):
        if beat.visual_mode != VisualMode.MOVING_CINEMA.value or not beat.moving_cinema:
            continue

        dur_sec = beat_durations.get(beat.beat_id)
        if dur_sec is None:
            mc_range = beat.moving_cinema.clip_duration_range
            dur_sec = float(mc_range[1]) if mc_range and len(mc_range) >= 2 else 4.8

        next_frame: str | None = None
        if idx + 1 < len(all_beats):
            nxt = all_beats[idx + 1]
            same_chapter = ch_by_beat.get(beat.beat_id) == ch_by_beat.get(nxt.beat_id)
            if same_chapter and nxt.visual_mode == VisualMode.MOVING_CINEMA.value and fdir is not None:
                cand = fdir / f"{nxt.beat_id}.png"
                if cand.is_file() or not fdir.exists():
                    next_frame = str(cand)

        shot = plan_omni_1_2_variable_duration_shot(
            beat, beat_audio_dur_sec=dur_sec, next_beat_frame=next_frame,
        )
        planned.append(shot)

    return planned


def resolve_transition(
    prev_beat: BeatSpec | None,
    curr_beat: BeatSpec,
    rules: TransitionRules,
) -> dict[str, Any]:
    """Determine the appropriate transition between two adjacent beats.

    Returns dict with 'type' and 'duration_sec'.
    """
    if prev_beat is None:
        return {"type": "none", "duration_sec": 0.0}

    prev_ch = prev_beat.effective_visual_channel()
    curr_ch = curr_beat.effective_visual_channel()

    # Same visual channel within moving_cinema chain (both ground POV or both tactical aerial)
    if prev_ch == curr_ch and prev_beat.visual_mode == VisualMode.MOVING_CINEMA.value:
        t = rules.intra_chain
        return {"type": t, "duration_sec": TRANSITION_DURATIONS.get(t, 0.0)}

    # Entering or leaving spatial terrain / Flow aerial tactical cutaway
    if (
        curr_ch in (VisualMode.SPATIAL_TERRAIN_OPS.value, "moving_cinema_tactical")
        or prev_ch in (VisualMode.SPATIAL_TERRAIN_OPS.value, "moving_cinema_tactical")
    ):
        t = rules.map_entry
        return {"type": t, "duration_sec": TRANSITION_DURATIONS.get(t, 0.55)}

    # Cross-mode scene boundary
    if prev_ch != curr_ch:
        t = rules.scene_boundary
        return {"type": t, "duration_sec": TRANSITION_DURATIONS.get(t, 0.45)}

    # Default fallback
    t = rules.scene_boundary
    return {"type": t, "duration_sec": TRANSITION_DURATIONS.get(t, 0.45)}


# ---------------------------------------------------------------------------
# Diegetic SFX Synthesizer
# ---------------------------------------------------------------------------
def synthesize_diegetic_sfx(
    sfx_id: str,
    duration_sec: float | None = None,
    seed: int = 1789,
) -> np.ndarray:
    """Synthesize a 48kHz stereo diegetic SFX waveform.

    Returns ndarray of shape (n_samples, 2) float32.
    """
    if sfx_id not in DIEGETIC_SFX_CATALOG:
        raise ValueError(f"Unknown diegetic SFX: {sfx_id!r}")

    spec = DIEGETIC_SFX_CATALOG[sfx_id]
    dur = duration_sec or spec["duration_sec"]
    n = int(round(dur * TARGET_SR))
    t = np.arange(n, dtype=np.float32) / float(TARGET_SR)
    rng = np.random.default_rng(seed + sum(ord(c) for c in sfx_id))
    stereo_w = float(spec["stereo_width"])

    if sfx_id == "ticking_countdown_pulse":
        freq = spec["freq_hz"]
        tick_period = 1.0 / freq
        # Sharp percussive ticks
        mono = np.zeros(n, dtype=np.float32)
        for i in range(int(dur * freq)):
            tick_start = int(round(i * tick_period * TARGET_SR))
            tick_len = min(int(0.03 * TARGET_SR), n - tick_start)
            if tick_len > 0:
                tt = np.arange(tick_len, dtype=np.float32) / float(TARGET_SR)
                tick = np.sin(2.0 * math.pi * 1200.0 * tt) * np.exp(-tt * 80.0)
                mono[tick_start : tick_start + tick_len] += tick * 0.7

    elif sfx_id == "cannon_thunder":
        # Low-frequency body + noise burst
        body = np.sin(
            2.0 * math.pi * (spec["freq_hz"] * t + 24.0 * (1.0 - np.exp(-t * 8.0)) / 8.0)
        ) * np.exp(-t * 2.5)
        noise = rng.normal(0.0, 0.6, n).astype(np.float32)
        lp_kernel = np.ones(96, dtype=np.float32) / 96.0
        noise_lp = np.convolve(noise, lp_kernel, mode="same")
        env = np.exp(-t * 1.8) * np.minimum(1.0, t / 0.005)
        mono = (body * 0.7 + noise_lp * env * 0.5).astype(np.float32)

    elif sfx_id == "wooden_hull_creak":
        # Filtered noise with resonances
        noise = rng.normal(0.0, 1.0, n).astype(np.float32)
        lp_kernel = np.ones(48, dtype=np.float32) / 48.0
        filtered = np.convolve(noise, lp_kernel, mode="same")
        env_slow = np.sin(math.pi * t / dur) ** 0.8
        resonance = 0.3 * np.sin(2.0 * math.pi * spec["freq_hz"] * t) * np.exp(-t * 1.2)
        mono = (filtered * env_slow * 0.4 + resonance).astype(np.float32)

    elif sfx_id == "night_river_wind":
        # Broadband wind noise shaped with slow LFO
        noise = rng.normal(0.0, 1.0, n).astype(np.float32)
        lp_kernel = np.ones(128, dtype=np.float32) / 128.0
        wind = np.convolve(noise, lp_kernel, mode="same")
        lfo = 0.5 + 0.5 * np.sin(2.0 * math.pi * 0.3 * t)
        env = np.sin(math.pi * t / dur) ** 0.6
        mono = (wind * lfo * env * 0.5).astype(np.float32)

    elif sfx_id == "war_drum_impact":
        freq = spec["freq_hz"]
        phase = 2.0 * math.pi * (freq * t + 48.0 * (1.0 - np.exp(-t * 14.0)) / 14.0)
        body = np.sin(phase) * np.exp(-t * 5.5)
        bronze = 0.3 * np.sin(2.0 * math.pi * 168.0 * t) * np.exp(-t * 7.0)
        hit = rng.normal(0.0, 0.3, n).astype(np.float32) * np.exp(-t * 60.0)
        mono = (body + bronze + hit).astype(np.float32)

    elif sfx_id == "sub_bass_drop":
        freq = spec["freq_hz"]
        # Descending sub-bass sweep
        f_sweep = freq * (1.0 + 2.0 * np.exp(-t * 3.0))
        phase = 2.0 * math.pi * np.cumsum(f_sweep) / float(TARGET_SR)
        env = np.exp(-t * 1.5) * np.minimum(1.0, t / 0.008)
        mono = (np.sin(phase) * env * 0.8).astype(np.float32)

    else:
        # Fallback: simple tone
        mono = (
            np.sin(2.0 * math.pi * 220.0 * t) * np.exp(-t * 3.0) * 0.5
        ).astype(np.float32)

    # Normalize
    mono = np.nan_to_num(mono, nan=0.0, posinf=0.0, neginf=0.0)
    peak = float(np.max(np.abs(mono))) + 1e-6
    mono = (mono / peak * 0.85).astype(np.float32)

    # Stereo spread
    left = mono * (1.0 - stereo_w * 0.5)
    right = np.roll(mono, max(1, int(0.0004 * TARGET_SR))) * (1.0 - stereo_w * 0.5)
    stereo = np.stack([left, right], axis=1).astype(np.float32)

    return stereo


# ---------------------------------------------------------------------------
# 5-Stem Cinema Mix Layout
# ---------------------------------------------------------------------------
@dataclass
class CinemaMixStem:
    """A single stem in the 5-stem cinema mix."""
    name: str
    waveform: np.ndarray  # (n_samples, 2) float32
    gain_db: float = 0.0

    @property
    def n_samples(self) -> int:
        return len(self.waveform)


def build_5stem_cinema_mix(
    stems: list[CinemaMixStem],
    total_samples: int,
    target_lufs: float = TARGET_LUFS,
) -> dict[str, Any]:
    """Mix 5 cinema stems into a master stereo bus.

    Stems: narration, diegetic_sfx, silence_bed, bgm_tension, room_tone.
    Returns dict with 'master' (ndarray), 'stem_peaks', 'estimated_lufs'.
    """
    if len(stems) != MIX_STEM_COUNT:
        raise ValueError(
            f"Expected {MIX_STEM_COUNT} stems, got {len(stems)}: "
            f"{[s.name for s in stems]}"
        )

    bus = np.zeros((total_samples, 2), dtype=np.float64)
    stem_peaks: dict[str, float] = {}

    for stem in stems:
        gain_linear = 10.0 ** (stem.gain_db / 20.0)
        padded = np.zeros((total_samples, 2), dtype=np.float32)
        copy_len = min(len(stem.waveform), total_samples)
        padded[:copy_len] = stem.waveform[:copy_len]
        bus += padded.astype(np.float64) * gain_linear
        stem_peaks[stem.name] = float(np.max(np.abs(padded[:copy_len])))

    # Soft clip and normalize
    bus = np.nan_to_num(bus, nan=0.0, posinf=0.0, neginf=0.0)
    peak = float(np.max(np.abs(bus))) + 1e-8
    # Target peak based on LUFS
    target_peak = 10.0 ** ((target_lufs + 10.0) / 20.0)
    master = (bus * min(1.0, target_peak / peak)).astype(np.float32)

    return {
        "master": master,
        "stem_peaks": stem_peaks,
        "estimated_lufs": target_lufs,
        "total_samples": total_samples,
        "sample_rate": TARGET_SR,
    }


# ---------------------------------------------------------------------------
# Spatial Terrain Camera Fly-In (30fps sub-pixel float32)
# ---------------------------------------------------------------------------
def compute_terrain_camera_keyframes(
    terrain_spec: SpatialTerrainSpec,
    fps: int = FPS,
) -> list[dict[str, float]]:
    """Compute per-frame camera keyframes for smooth 30fps sub-pixel fly-in.

    Returns list of dicts with keys: frame, t, zoom, cx, cy.
    Uses float32 sub-pixel precision to avoid integer jitter (ERR-20261109-01).
    """
    total_frames = int(round(terrain_spec.camera_fly_duration_sec * fps))
    if total_frames < 1:
        return [{"frame": 0, "t": 0.0, "zoom": terrain_spec.camera_start_zoom, "cx": 0.5, "cy": 0.5}]

    z0 = terrain_spec.camera_start_zoom
    z1 = terrain_spec.camera_end_zoom
    keyframes: list[dict[str, float]] = []

    for frame_idx in range(total_frames):
        t = frame_idx / max(1, total_frames - 1)
        eased = _ease_in_out_cubic(t)
        zoom = z0 + (z1 - z0) * eased
        # Center stays fixed (target callout center computed by producer)
        keyframes.append({
            "frame": float(frame_idx),
            "t": round(float(t), 6),
            "zoom": round(float(zoom), 6),
            "cx": 0.5,
            "cy": 0.5,
        })

    return keyframes


# ---------------------------------------------------------------------------
# Macro Parallax 2.5D Float32 Camera
# ---------------------------------------------------------------------------
def compute_parallax_camera_keyframes(
    parallax_spec: MacroParallaxSpec,
    fps: int = FPS,
) -> list[dict[str, float]]:
    """Compute per-frame 2.5D parallax camera keyframes.

    Uses float32 sub-pixel precision. No vf_zoompan integer jitter.
    Max hold: 3.5s per ERR-20261109-01.
    """
    from fx_warehouse.camera_vfx import get_camera_motion

    cam = get_camera_motion(parallax_spec.camera_motion)
    dur = min(parallax_spec.max_hold_sec, MACRO_PARALLAX_MAX_HOLD_SEC)
    total_frames = int(round(dur * fps))
    if total_frames < 1:
        return [{"frame": 0, "t": 0.0, "zoom": float(cam["z0"]), "cx": 0.5, "cy": 0.5}]

    keyframes: list[dict[str, float]] = []
    z0, z1 = float(cam["z0"]), float(cam["z1"])
    x0, x1 = float(cam["x0"]), float(cam["x1"])
    y0, y1 = float(cam["y0"]), float(cam["y1"])

    for frame_idx in range(total_frames):
        t = frame_idx / max(1, total_frames - 1)
        eased = _ease_in_out_cubic(t)
        zoom = z0 + (z1 - z0) * eased
        cx = 0.5 + (x0 + (x1 - x0) * eased)
        cy = 0.5 + (y0 + (y1 - y0) * eased)
        keyframes.append({
            "frame": float(frame_idx),
            "t": round(float(t), 6),
            "zoom": round(float(zoom), 6),
            "cx": round(float(cx), 6),
            "cy": round(float(cy), 6),
        })

    return keyframes


# ---------------------------------------------------------------------------
# Forensic Evidence Reveal Compositor
# ---------------------------------------------------------------------------
def build_forensic_reveal_layout(
    reveal_spec: ForensicRevealSpec,
    width: int = WIDTH,
    height: int = HEIGHT,
) -> dict[str, Any]:
    """Plan the forensic evidence reveal layout.

    Returns layout descriptor for the producer to composite (PIL RGBA).
    Enforces: zero rectangles, zero left stripes, spotlight optical masking.
    """
    if not reveal_spec.zero_rectangles:
        raise ValueError("Forensic reveal MUST have zero_rectangles=True")
    if not reveal_spec.zero_left_stripes:
        raise ValueError("Forensic reveal MUST have zero_left_stripes=True")

    layout: dict[str, Any] = {
        "type": reveal_spec.layout,
        "width": width,
        "height": height,
        "timestamp_text": reveal_spec.timestamp_text,
        "headline_text": reveal_spec.headline_text,
        "prompt": reveal_spec.prompt,
        "spotlight_mask": reveal_spec.spotlight_mask,
        "depth_of_field_blur_px": reveal_spec.depth_of_field_blur,
        "constraints": {
            "zero_rectangular_boxes": True,
            "zero_left_stripes": True,
            "zero_solid_card_borders": True,
        },
    }

    if reveal_spec.layout == ForensicLayout.COUNTDOWN_CLOCK.value:
        layout["clock"] = {
            "text": reveal_spec.timestamp_text,
            "font_size_px": int(height * 0.06),
            "position": "top_left_inset",
            "glow_radius_px": 8,
        }
    elif reveal_spec.layout == ForensicLayout.FORCE_COMPARISON.value:
        layout["split"] = {
            "mode": "diagonal_optical",
            "left_label": "",
            "right_label": "",
            "divider_style": "light_beam",
        }
    elif reveal_spec.layout == ForensicLayout.PRIMARY_CHRONICLE.value:
        layout["chronicle"] = {
            "text_style": "handwritten_serif",
            "parchment_overlay": True,
            "opacity": 0.85,
        }

    return layout


# ---------------------------------------------------------------------------
# Visual Mode Distribution Validator
# ---------------------------------------------------------------------------
def validate_visual_choreography(spec: PilotSpec) -> list[str]:
    """Validate that the 4-mode visual choreography breaks monotony.

    Rules:
    - No more than 3 consecutive beats of the same visual mode.
    - At least 2 different visual modes must be used.
    - moving_cinema must not exceed 70% of total beats.
    - At least 1 silence_drop beat for acoustic breathing.
    """
    errors: list[str] = []
    all_beats = spec.all_beats()
    n = len(all_beats)
    if n == 0:
        return ["No beats found"]

    channels = [b.effective_visual_channel() for b in all_beats]
    dist: dict[str, int] = {}
    for ch_name in channels:
        dist[ch_name] = dist.get(ch_name, 0) + 1

    # At least 2 visual channels
    if len(dist) < 2:
        errors.append(
            "Must use at least 2 different visual modes to avoid monotony"
        )

    # Scale choreography caps cleanly for full-length multi-act documentaries (>= 30 beats)
    # while keeping strict 70% / max-3-streak gates on short pilots.
    is_full_episode = n >= 30
    mc_cap = 0.78 if is_full_episode else 0.70
    max_streak = 5 if is_full_episode else 3

    # Pure ground/POV moving_cinema cap (tactical aerial Flow beats count separately)
    mc_count = dist.get(VisualMode.MOVING_CINEMA.value, 0)
    if n > 0 and mc_count / n > mc_cap:
        errors.append(
            f"moving_cinema beats ({mc_count}/{n} = {mc_count / n:.0%}) "
            f"exceed {mc_cap:.0%} cap — add more spatial/tactical/forensic/parallax variety"
        )

    # No consecutive same visual channel beyond max_streak
    streak = 1
    for i in range(1, n):
        if channels[i] == channels[i - 1]:
            streak += 1
            if streak > max_streak:
                errors.append(
                    f"{max_streak + 1}+ consecutive {channels[i]} beats at "
                    f"index {i - streak + 1}..{i} — break with a different mode"
                )
        else:
            streak = 1

    # Spatial terrain max consecutive hold (radar-user4: never pure map >14s)
    spatial_streak_sec = 0.0
    for beat in all_beats:
        if beat.visual_mode == VisualMode.SPATIAL_TERRAIN_OPS.value:
            # Approximate beat duration from silence + hold
            beat_dur = (beat.pre_silence_sec or 0.0) + (beat.post_sfx_hold_sec or 0.0) + 3.0
            spatial_streak_sec += beat_dur
            if spatial_streak_sec > SPATIAL_TERRAIN_MAX_CONSECUTIVE_SEC:
                errors.append(
                    f"spatial_terrain_ops consecutive hold ~{spatial_streak_sec:.1f}s "
                    f"exceeds {SPATIAL_TERRAIN_MAX_CONSECUTIVE_SEC}s max — "
                    f"alternate with moving_cinema (target 60/40 mix)"
                )
                break
        else:
            spatial_streak_sec = 0.0

    return errors


# ---------------------------------------------------------------------------
# FFmpeg Render Command Builder (for Colab T4 h264_nvenc)
# ---------------------------------------------------------------------------
def build_nvenc_render_cmd(
    input_frames_pattern: str,
    input_audio: str,
    output_mp4: str,
    *,
    fps: int = FPS,
    width: int = WIDTH,
    height: int = HEIGHT,
    watermark_path: str | None = None,
    delogo: bool = True,
) -> list[str]:
    """Build the FFmpeg h264_nvenc command for Colab Tesla T4 render.

    This is the SOLE encoder per AGENTS.md — zero local CPU fallback.
    """
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-framerate", str(fps),
        "-i", input_frames_pattern,
        "-i", input_audio,
    ]

    # Build complex filtergraph
    vf_parts: list[str] = []

    # Delogo strictly contained inside 116x116 bottom-right badge at W-w-36:H-h-36
    # (1920x1080 -> x=1772..1880, y=932..1040 inside badge [1768..1884, 928..1044])
    if delogo:
        vf_parts.append(
            f"delogo=x={width - 148}:y={height - 148}:w=108:h=108"
        )

    # Lanczos scale to exact resolution
    vf_parts.append(f"scale={width}:{height}:flags=lanczos")

    # Watermark overlay at W-w-36:H-h-36
    if watermark_path:
        cmd.extend(["-i", watermark_path])
        if vf_parts:
            vf = ",".join(vf_parts)
            cmd.extend([
                "-filter_complex",
                f"[0:v]{vf}[v];[v][2:v]overlay=W-w-36:H-h-36[out]",
                "-map", "[out]",
                "-map", "1:a",
            ])
        else:
            cmd.extend([
                "-filter_complex",
                "[0:v][2:v]overlay=W-w-36:H-h-36[out]",
                "-map", "[out]",
                "-map", "1:a",
            ])
    else:
        if vf_parts:
            cmd.extend(["-vf", ",".join(vf_parts)])

    # h264_nvenc encoder settings (Tesla T4)
    cmd.extend([
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-b:v", "10M",
        "-bf", "0",
        "-g", str(fps),
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", str(TARGET_SR),
        "-ac", "2",
        output_mp4,
    ])

    return cmd


# ---------------------------------------------------------------------------
# Sharded & Monolithic Asset Discovery + Exact Frame Timeline Planner
# ---------------------------------------------------------------------------
def _find_sequence_files(seq_dir: Path) -> list[Path]:
    """Return sorted frame files (.jpg/.jpeg/.png) inside a sequence directory."""
    if not seq_dir.is_dir():
        return []
    files = [
        p for p in seq_dir.iterdir()
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    return sorted(files, key=lambda p: p.name)


def _find_tactical_overlay_png(beat_id: str, out_dir: Path) -> Path | None:
    """Locate optional seekbar-safe RGBA tactical HUD overlay PNG (`tactical_overlays/<beat_id>.png`)."""
    for cand in (
        out_dir / "tactical_overlays" / f"{beat_id}.png",
        out_dir / "tactical_overlays" / f"{beat_id}_overlay.png",
    ):
        if cand.is_file() and cand.stat().st_size > 500:
            return cand
    return None


def resolve_beat_asset_source(beat: BeatSpec, out_dir: Path) -> dict[str, Any]:
    """Locate visual asset for a beat across sharded or monolithic directories.

    Supports both sharded swarm directories (`flow_clips/`, `tactical_overlays/`,
    `geo_seqs/`, `forensic/`, `parallax_seqs/`, `frames/`) and monolithic `visual/`.
    Prefers native Flow `flow_clips/<beat_id>.mp4` + `tactical_overlays/<beat_id>.png`
    over legacy `geo_seqs/` whenever a native Flow clip exists for the beat.
    """
    bid = beat.beat_id
    bidx = beat.beat_index
    overlay_p = _find_tactical_overlay_png(bid, out_dir)

    def _with_overlay(res: dict[str, Any]) -> dict[str, Any]:
        if overlay_p is not None:
            res["overlay_path"] = overlay_p
        return res

    if beat.visual_mode in (VisualMode.MOVING_CINEMA.value, VisualMode.SPATIAL_TERRAIN_OPS.value):
        mp4_candidates = [
            out_dir / "flow_clips" / f"{bid}.mp4",
            out_dir / "flow_clips" / f"{bid}_flow.mp4",
            out_dir / "flow_clips" / f"clip_{bidx:02d}.mp4",
            out_dir / "flow_clips" / f"clip_{bidx:03d}.mp4",
            out_dir / "flow_clips" / f"beat_{bidx:02d}.mp4",
            out_dir / "flow_clips" / f"beat_{bidx + 1:02d}.mp4",
            out_dir / "visual" / f"{bid}_flow.mp4",
            out_dir / "visual" / f"{bid}.mp4",
        ]
        # Also scan flow_clips/ for any file matching beat_id
        flow_clips_dir = out_dir / "flow_clips"
        if flow_clips_dir.is_dir():
            for f in sorted(flow_clips_dir.glob("*.mp4")):
                if f.stem == bid or f.stem.startswith(f"{bid}_") or f.stem.endswith(f"_{bid}"):
                    mp4_candidates.insert(0, f)
        for cand in mp4_candidates:
            if cand.is_file() and cand.stat().st_size > 10_000:
                return _with_overlay({"source_kind": "video_mp4", "path": cand})

    if beat.visual_mode == VisualMode.SPATIAL_TERRAIN_OPS.value:
        seq_dirs = [
            out_dir / "geo_seqs" / bid,
            out_dir / "visual" / f"{bid}_terrain_frames",
            out_dir / "geo_seqs" / f"beat_{bidx:02d}",
            out_dir / "geo_seqs" / f"beat_{bidx:03d}",
        ]
        for sdir in seq_dirs:
            frames = _find_sequence_files(sdir)
            if frames:
                return _with_overlay({"source_kind": "frame_seq", "dir": sdir, "frames": frames})
        mp4_cands = [
            out_dir / "geo_seqs" / f"{bid}.mp4",
            out_dir / "visual" / f"{bid}_terrain.mp4",
        ]
        for cand in mp4_cands:
            if cand.is_file() and cand.stat().st_size > 10_000:
                return _with_overlay({"source_kind": "video_mp4", "path": cand})

    if beat.visual_mode == VisualMode.FORENSIC_EVIDENCE_REVEAL.value:
        # Priority 1: Lightweight dual-layer animated plate (< 600KB/beat vs ~50MB JPEG seq!)
        dual_dir = out_dir / "forensic" / bid
        if dual_dir.is_dir():
            bd_cand = next(
                (p for p in (dual_dir / "backdrop.jpg", dual_dir / "backdrop.jpeg", dual_dir / "backdrop.png") if p.is_file() and p.stat().st_size > 1_000),
                None,
            )
            txt_cand = next(
                (p for p in (dual_dir / "spotlight_text.png", dual_dir / "text_overlay.png") if p.is_file() and p.stat().st_size > 500),
                None,
            )
            if bd_cand is not None and txt_cand is not None:
                return _with_overlay({
                    "source_kind": "forensic_dual_plate",
                    "backdrop_path": bd_cand,
                    "text_path": txt_cand,
                })

        # Priority 2: Lightweight single pre-composited plate (< 500KB/beat!)
        img_cands = [
            out_dir / "forensic" / f"{bid}.png",
            out_dir / "forensic" / f"{bid}.jpg",
            out_dir / "forensic" / f"{bid}.jpeg",
            out_dir / "forensic" / bid / "plate.png",
            out_dir / "forensic" / bid / "plate.jpg",
            out_dir / "visual" / f"{bid}_forensic.png",
        ]
        for cand in img_cands:
            if cand.is_file() and cand.stat().st_size > 1_000:
                return _with_overlay({"source_kind": "single_image", "path": cand})

        # Priority 3: Legacy full JPEG sequence (backward compatibility)
        seq_dirs = [
            out_dir / "forensic" / bid,
            out_dir / "visual" / f"{bid}_forensic_frames",
            out_dir / "forensic" / f"beat_{bidx:02d}",
            out_dir / "forensic" / f"beat_{bidx:03d}",
        ]
        for sdir in seq_dirs:
            frames = _find_sequence_files(sdir)
            if frames:
                return _with_overlay({"source_kind": "frame_seq", "dir": sdir, "frames": frames})

    if beat.visual_mode == VisualMode.MACRO_PARALLAX_STILL.value:
        seq_dirs = [
            out_dir / "parallax_seqs" / bid,
            out_dir / "visual" / f"{bid}_parallax",
        ]
        for sdir in seq_dirs:
            frames = _find_sequence_files(sdir)
            if frames:
                return {"source_kind": "frame_seq", "dir": sdir, "frames": frames}

    # Fallback check for still frame in frames/ or visual/
    still_cands = [
        out_dir / "frames" / f"{bid}.png",
        out_dir / "frames" / f"beat_{bidx:02d}.png",
        out_dir / "frames" / f"{bid}_beluga.png",
        out_dir / "visual" / f"{bid}_beluga.png",
    ]
    for cand in still_cands:
        if cand.is_file() and cand.stat().st_size > 1_000:
            return {"source_kind": "single_image", "path": cand}

    raise FileNotFoundError(
        f"Missing rendered visual asset for beat {bid!r} (mode={beat.visual_mode}) in {out_dir}"
    )


def _extract_span_sec(entry: Any) -> tuple[float | None, float | None, float | None]:
    """Extract (t_start, t_end, duration_sec) from flexible timing dict/list."""
    if isinstance(entry, (list, tuple)) and len(entry) >= 2:
        s = float(entry[0])
        e = float(entry[1])
        d = float(entry[2]) if len(entry) >= 3 else max(0.0, e - s)
        return s, e, d
    if not isinstance(entry, dict):
        return None, None, None

    s_val = None
    for k in ("visual_start", "t_start", "start_sec", "out_start", "start"):
        if entry.get(k) is not None:
            s_val = float(entry[k])
            break
    e_val = None
    for k in ("visual_end", "t_end", "end_sec", "out_end", "end"):
        if entry.get(k) is not None:
            e_val = float(entry[k])
            break
    d_val = None
    for k in ("visual_duration_sec", "duration_sec", "total_duration_sec", "duration"):
        if entry.get(k) is not None:
            d_val = float(entry[k])
            break

    if s_val is not None and e_val is None and d_val is not None:
        e_val = s_val + d_val
    if s_val is not None and e_val is not None and d_val is None:
        d_val = max(0.0, e_val - s_val)
    return s_val, e_val, d_val


def load_clean_windows_map(paths: list[Path | str]) -> dict[str, tuple[float, float]]:
    """Load & merge `@motion-police` `clean_window_sec` maps from 1+ audit JSON files.

    Supports `motion_action_audit.json`, `motion_audit_part1.json`, and
    `motion_audit_part2.json` schemas (`clean_window_sec_map`, `clean_window_sec`,
    `clips`, `audits`, `beats`).
    """
    merged: dict[str, tuple[float, float]] = {}

    def _add(bid: str, val: Any) -> None:
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            s, e = float(val[0]), float(val[1])
            if e > s + 0.1:
                merged[str(bid)] = (round(max(0.0, s), 4), round(e, 4))

    for raw_p in paths:
        p = Path(raw_p)
        if not p.is_file():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        for map_key in ("clean_window_sec_map", "clean_windows", "clean_window_sec"):
            sub = data.get(map_key)
            if isinstance(sub, dict):
                for bid, win in sub.items():
                    _add(str(bid), win)
        for list_key in ("clips", "audits", "beats"):
            sub = data.get(list_key)
            if isinstance(sub, list):
                for item in sub:
                    if isinstance(item, dict) and item.get("beat_id") and item.get("clean_window_sec"):
                        _add(str(item["beat_id"]), item["clean_window_sec"])
            elif isinstance(sub, dict):
                for bid, item in sub.items():
                    if isinstance(item, dict) and item.get("clean_window_sec"):
                        _add(str(bid), item["clean_window_sec"])

    return merged


def parse_audio_timings_to_render_segments(
    spec: PilotSpec,
    timings_data: dict[str, Any],
    total_audio_dur: float,
    fps: int = FPS,
    clean_windows: dict[str, tuple[float, float]] | None = None,
) -> list[dict[str, Any]]:
    """Convert flexible `audio_timings.json` into frame-exact render segments.

    Guarantees:
    - All beats in `spec.all_beats()` are mapped in order.
    - Any cold-open lead-in (`0 .. first_beat_start`) is absorbed into beat 0's
      visual window so video starts at `t=0.0` with zero black gap.
    - `sum(seg['base_frames']) == round(total_audio_dur * fps)` to the exact frame.
    - Transition overhang frames (`overhang_frames`) are computed per boundary so
      FFmpeg `xfade` preserves exact A/V sync across the entire timeline.
    - Optional `@motion-police` `clean_window_sec` caps are attached per beat.
    """
    all_beats = spec.all_beats()
    if not all_beats:
        raise ValueError("Spec contains zero beats")

    total_frames = max(len(all_beats), int(round(total_audio_dur * fps)))

    ch_by_beat: dict[str, int] = {}
    for ch in spec.chapters:
        for b in ch.beats:
            ch_by_beat[b.beat_id] = ch.chapter_idx

    # Index beat timing entries by beat_id
    by_id: dict[str, Any] = {}
    raw_beats = timings_data.get("beats")
    if isinstance(raw_beats, dict):
        by_id.update(raw_beats)
    elif isinstance(raw_beats, list):
        for item in raw_beats:
            if isinstance(item, dict) and item.get("beat_id"):
                by_id[str(item["beat_id"])] = item

    for alt_key in ("timeline", "segments", "beat_timings"):
        alt = timings_data.get(alt_key)
        if isinstance(alt, dict):
            for k, v in alt.items():
                by_id.setdefault(str(k), v)
        elif isinstance(alt, list):
            for item in alt:
                if isinstance(item, dict) and item.get("beat_id"):
                    by_id.setdefault(str(item["beat_id"]), item)

    # Extract raw start/end or durations per beat
    starts: list[float] = []
    ends: list[float] = []
    cursor = float(timings_data.get("cold_open_sec") or spec.cold_open_sfx_lead_in_sec or 0.0)

    for idx, beat in enumerate(all_beats):
        ent = by_id.get(beat.beat_id)
        s_val, e_val, d_val = _extract_span_sec(ent) if ent is not None else (None, None, None)
        if s_val is not None and e_val is not None and e_val > s_val:
            b_start, b_end = s_val, e_val
        elif d_val is not None and d_val > 0:
            b_start = cursor if idx > 0 else 0.0
            b_end = b_start + d_val
        else:
            fallback_d = max(1.8, (beat.pre_silence_sec or 0.0) + (beat.post_sfx_hold_sec or 0.0) + (0.0 if beat.is_silence_drop else 3.2))
            b_start = cursor if idx > 0 else 0.0
            b_end = b_start + fallback_d
        starts.append(b_start)
        ends.append(b_end)
        cursor = b_end

    # Contiguous visual windows covering [0.0 .. total_audio_dur]:
    # Beat 0 starts at 0.0 (covering cold-open SFX lead-in visually);
    # each beat i covers [win_start_i .. win_start_{i+1}], last beat ends at total_audio_dur.
    win_boundaries: list[float] = [0.0]
    for i in range(1, len(all_beats)):
        boundary = max(win_boundaries[-1] + (1.0 / fps), starts[i])
        win_boundaries.append(min(boundary, total_audio_dur - (len(all_beats) - i) * (1.0 / fps)))
    win_boundaries.append(total_audio_dur)

    # Convert visual boundaries to integer cumulative frame indices -> exact sum == total_frames
    cum_frames = [int(round(t * fps)) for t in win_boundaries]
    cum_frames[0] = 0
    cum_frames[-1] = total_frames
    for i in range(1, len(cum_frames)):
        if cum_frames[i] <= cum_frames[i - 1]:
            cum_frames[i] = cum_frames[i - 1] + 1
    # Back-propagate if monotonic clamp pushed past total_frames
    for i in range(len(cum_frames) - 2, 0, -1):
        max_allowed = cum_frames[i + 1] - 1
        if cum_frames[i] > max_allowed:
            cum_frames[i] = max(i, max_allowed)

    cw_map = clean_windows or {}
    segments: list[dict[str, Any]] = []
    for i, beat in enumerate(all_beats):
        base_f = max(1, cum_frames[i + 1] - cum_frames[i])
        curr_ch = ch_by_beat.get(beat.beat_id, 1)
        if i < len(all_beats) - 1:
            nxt_beat = all_beats[i + 1]
            nxt_ch = ch_by_beat.get(nxt_beat.beat_id, curr_ch)
            if nxt_ch != curr_ch:
                tr_type = spec.transitions.act_break
                tr_dur = TRANSITION_DURATIONS.get(tr_type, 0.40)
            else:
                tr_info = resolve_transition(beat, nxt_beat, spec.transitions)
                tr_type = tr_info["type"]
                tr_dur = float(tr_info["duration_sec"])
            ov_f = int(round(tr_dur * fps))
            # Clamp overhang so it never exceeds 33% of either adjacent beat
            next_base_f = max(1, cum_frames[i + 2] - cum_frames[i + 1])
            ov_f = min(ov_f, max(0, base_f // 3), max(0, next_base_f // 3))
        else:
            tr_type = "none"
            ov_f = 0

        xfade_name = "none"
        if ov_f > 0:
            xfade_name = "fadeblack" if tr_type == "obsidian_act_fade" else "fade"

        seg_d: dict[str, Any] = {
            "index": i,
            "beat_id": beat.beat_id,
            "chapter_idx": curr_ch,
            "visual_mode": beat.visual_mode,
            "is_flow_clip": beat.visual_mode == VisualMode.MOVING_CINEMA.value,
            "visual_start_sec": round(cum_frames[i] / float(fps), 4),
            "visual_end_sec": round(cum_frames[i + 1] / float(fps), 4),
            "base_frames": base_f,
            "overhang_frames": ov_f,
            "encode_frames": base_f + ov_f,
            "transition_out": tr_type,
            "xfade_transition": xfade_name,
        }
        if beat.beat_id in cw_map:
            seg_d["clean_window_sec"] = [cw_map[beat.beat_id][0], cw_map[beat.beat_id][1]]
        segments.append(seg_d)

    return segments


def partition_segments_into_chunks(
    segments: list[dict[str, Any]],
    *,
    max_chunk_beats: int = DEFAULT_MAX_CHUNK_BEATS,
    fps: int = FPS,
) -> list[dict[str, Any]]:
    """Partition timeline segments into Act-aligned Colab T4 chunks (`<= max_chunk_beats`).

    Prevents Colab RAM OOM when rendering 85–120 beat (9–10.5 min) documentaries by
    limiting every FFmpeg filtergraph to `<= 16` inputs, then joining rendered chunks
    losslessly (`-f concat -c:v copy`) with exact frame count preservation:
    `sum(c['chunk_frames'] for c in chunks) == sum(s['base_frames'] for s in segments)`.
    """
    if not segments:
        return []
    cap = max(2, int(max_chunk_beats))

    # 1) Group segments contiguously by chapter_idx
    act_groups: list[list[dict[str, Any]]] = []
    for seg in segments:
        seg_copy = dict(seg)
        ch_id = int(seg_copy.get("chapter_idx", 1))
        if not act_groups or int(act_groups[-1][0].get("chapter_idx", 1)) != ch_id:
            act_groups.append([seg_copy])
        else:
            act_groups[-1].append(seg_copy)

    # 2) If total beats fit inside one small chunk (e.g. <= cap and 1..2 acts), keep single chunk;
    #    otherwise keep Act-aligned chunks and split any Act exceeding `cap` evenly.
    raw_chunks: list[list[dict[str, Any]]] = []
    if len(segments) <= cap:
        raw_chunks = [[dict(s) for s in segments]]
    else:
        for grp in act_groups:
            if len(grp) <= cap:
                raw_chunks.append(grp)
            else:
                n_sub = math.ceil(len(grp) / float(cap))
                sub_size = math.ceil(len(grp) / float(n_sub))
                for start_i in range(0, len(grp), sub_size):
                    raw_chunks.append(grp[start_i : start_i + sub_size])

    # 3) Normalize boundary overhangs to 0 and apply obsidian Act fades on cross-chapter chunk joins
    chunks: list[dict[str, Any]] = []
    for c_idx, c_segs in enumerate(raw_chunks):
        # Last segment of a chunk NEVER overhangs into the next chunk so concat is frame-exact
        last_s = c_segs[-1]
        last_s["overhang_frames"] = 0
        last_s["encode_frames"] = int(last_s["base_frames"])
        last_s["xfade_transition"] = "none"

        chunk_frames = sum(int(s["base_frames"]) for s in c_segs)
        prev_ch = int(raw_chunks[c_idx - 1][-1].get("chapter_idx", 1)) if c_idx > 0 else None
        curr_start_ch = int(c_segs[0].get("chapter_idx", 1))
        curr_end_ch = int(c_segs[-1].get("chapter_idx", 1))
        next_ch = int(raw_chunks[c_idx + 1][0].get("chapter_idx", 1)) if (c_idx + 1 < len(raw_chunks)) else None

        is_act_entry = prev_ch is not None and prev_ch != curr_start_ch
        is_act_exit = next_ch is not None and next_ch != curr_end_ch
        fade_in_sec = 0.25 if (is_act_entry and chunk_frames > fps) else 0.0
        fade_out_sec = 0.30 if (is_act_exit and chunk_frames > fps) else 0.0

        chunks.append({
            "chunk_index": c_idx,
            "chapter_idx": curr_start_ch,
            "chunk_frames": chunk_frames,
            "fade_in_sec": fade_in_sec,
            "fade_out_sec": fade_out_sec,
            "segments": c_segs,
        })

    return chunks


MAX_COLAB_UPLOAD_PART_BYTES = 24_000_000  # < 26MB safe margin under Colab ~35MB HTTP upload cap


def build_sharded_render_bundles(
    file_entries: list[tuple[Path, str]],
    inline_entries: list[tuple[str, str | bytes]],
    bundle_dir: Path,
    *,
    max_part_bytes: int = MAX_COLAB_UPLOAD_PART_BYTES,
) -> list[Path]:
    """Pack render assets into `< 24MB` `ZIP_STORED` parts (`bundle_00.zip`, `bundle_01.zip`, ...).

    Avoids Colab's ~35MB single-upload HTTP 413 ceiling when bundling 150–250MB
    of 1080p frame sequences and Flow clips.
    """
    import zipfile

    bundle_dir.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    part_idx = 0
    cur_bytes = 0
    zf: zipfile.ZipFile | None = None

    def _open_next() -> zipfile.ZipFile:
        nonlocal part_idx, cur_bytes, zf
        if zf is not None:
            zf.close()
        zp = bundle_dir / f"bundle_{part_idx:02d}.zip"
        part_idx += 1
        cur_bytes = 0
        parts.append(zp)
        zf = zipfile.ZipFile(zp, "w", compression=zipfile.ZIP_STORED)
        return zf

    cur_zf = _open_next()
    for arcname, payload in inline_entries:
        raw_b = payload.encode("utf-8") if isinstance(payload, str) else payload
        entry_sz = len(raw_b) + 160
        if cur_bytes > 0 and (cur_bytes + entry_sz) > max_part_bytes:
            cur_zf = _open_next()
        cur_zf.writestr(arcname, raw_b)
        cur_bytes += entry_sz

    for local_path, arcname in file_entries:
        entry_sz = int(local_path.stat().st_size) + 160
        if cur_bytes > 0 and (cur_bytes + entry_sz) > max_part_bytes:
            cur_zf = _open_next()
        cur_zf.write(local_path, arcname)
        cur_bytes += entry_sz

    if zf is not None:
        zf.close()
    return parts


# ---------------------------------------------------------------------------
# V11.5 Character Bible & Flow `reference_media_ids` Consistency Lock
# ---------------------------------------------------------------------------
def _strip_vi_accents(text: str) -> str:
    import unicodedata

    mapped = str(text or "").replace("đ", "d").replace("Đ", "D")
    decomp = unicodedata.normalize("NFD", mapped)
    return "".join(ch for ch in decomp if unicodedata.category(ch) != "Mn")


def _sanitize_character_dna(text: str) -> str:
    """Strip celebrity likeness triggers and CJK ideographs before sending to Flow."""
    try:
        from short_engine.character_bible import sanitize_benign_face_dna

        return sanitize_benign_face_dna(text)
    except Exception:
        cleaned = re.sub(
            r"(?i:\b(?:resembling|look(?:s|ing)?\s+like|in\s+the\s+likeness\s+of|likeness\s+of|played\s+by|portrayed\s+by))\s+"
            r"[A-Z][a-zA-Z.'-]+(?:\s+[A-Z][a-zA-Z.'-]+){0,3}",
            "original historical archetype",
            str(text or "").strip(),
        )
        cleaned = re.sub(r"[\u4e00-\u9fff]+", "", cleaned)
        return re.sub(r"\s{2,}", " ", cleaned).strip(" ,;-")


def build_character_anchor_prompt(char: CharacterAnchorSpec) -> str:
    """Build canonical 16:9 Stage A0 character reference portrait/turnaround prompt for Flow BELUGA."""
    face_dna = _sanitize_character_dna(char.face_and_age_dna)
    wardrobe = _sanitize_character_dna(char.armor_and_wardrobe_lock)
    props_str = ", ".join(char.signature_props) if char.signature_props else "period-accurate historical gear"
    palette_str = (
        f"restrained muted palette ({', '.join(char.color_palette_hex[:4])})"
        if char.color_palette_hex
        else "restrained muted earth, weathered bronze, and aged iron palette"
    )
    bans = list(char.anti_anachronism_bans)
    bans_low = " ".join(bans).lower()
    if "flag" not in bans_low:
        bans.append("zero modern national flags or yellow stars")
    if "samurai" not in bans_low:
        bans.append("no Japanese samurai armor or European medieval plate")
    ban_clause = ", ".join(bans)

    return (
        f"16:9 35mm cinema character reference sheet showing front-facing medium portrait on left "
        f"and three-quarter profile stance on right of an original {char.dynasty_era} historical figure "
        f"({char.faction} faction), {face_dna}; wearing {wardrobe}; holding {props_str}; "
        f"{palette_str}; neutral overcast 35mm Kodak Vision3 500T film daylight on plain weathered slate backdrop, "
        f"natural weathered skin pores, matte worn textiles, authentic optical lens depth, "
        f"plain unmarked historical pennants only, {ban_clause}, "
        f"zero celebrity likeness, zero plastic waxy CGI skin, zero airbrushed look, "
        f"no text, no labels, no letters, no watermarks."
    )


def inject_character_reference_prompt(
    prompt: str,
    characters: list[CharacterAnchorSpec],
    *,
    has_reference_images: bool = True,
) -> str:
    """Inject Flow `reference_media_ids` continuity directive and wardrobe locks into a scene prompt."""
    base = str(prompt or "").strip()
    if not characters:
        return base

    char_summaries: list[str] = []
    for ch in characters[:3]:
        wardrobe_short = _sanitize_character_dna(ch.armor_and_wardrobe_lock)[:140]
        face_short = _sanitize_character_dna(ch.face_and_age_dna)[:120]
        char_summaries.append(f"{ch.character_id} ({face_short}; {wardrobe_short})")
    joined = "; ".join(char_summaries)

    low_base = base.lower()
    prefix = ""
    if has_reference_images and "using the attached reference image" not in low_base:
        prefix = (
            "Using the attached reference image(s), maintain the exact same face, age, costume, "
            f"armor palette, and 35mm cinema realism for {joined}. "
        )
    elif not has_reference_images and "maintain strict 35mm character continuity" not in low_base:
        prefix = f"Maintain strict 35mm character continuity for {joined}. "

    out = f"{prefix}{base}".strip()
    out_low = out.lower()
    if "modern national flag" not in out_low and "yellow star" not in out_low:
        out = (
            f"{out.rstrip('. ')}, plain unmarked period-accurate pennants only, "
            "zero modern national flags or yellow stars, zero plastic waxy CGI skin."
        )
    return out


# ---------------------------------------------------------------------------
# V11.5 Unified Master Color Harmony & Kodak 2383 35mm Anti-AI Grade
# ---------------------------------------------------------------------------
def compute_act_reference_lab(
    frames_bgr: list[np.ndarray],
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Compute robust median OpenCV 8-bit Lab `(mean, std)` across representative Act frames."""
    import cv2

    means: list[np.ndarray] = []
    stds: list[np.ndarray] = []
    for img in frames_bgr:
        if img is None or getattr(img, "size", 0) == 0:
            continue
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        means.append(lab.reshape(-1, 3).mean(axis=0))
        stds.append(lab.reshape(-1, 3).std(axis=0))
    if not means:
        p = CANONICAL_ACT_PALETTES["neutral_35mm_doc"]
        return tuple(p["lab_mean"]), tuple(p["lab_std"])
    med_mean = np.median(np.stack(means, axis=0), axis=0)
    med_std = np.median(np.stack(stds, axis=0), axis=0)
    return (
        (float(med_mean[0]), float(med_mean[1]), float(med_mean[2])),
        (float(med_std[0]), float(med_std[1]), float(med_std[2])),
    )


def match_frame_to_act_palette(
    img_bgr: np.ndarray,
    target_lab_mean: tuple[float, float, float] | str | int | None = None,
    target_lab_std: tuple[float, float, float] | None = None,
    *,
    blend: float = 0.55,
    chroma_damp: float = 0.88,
) -> np.ndarray:
    """Apply clamped Reinhard CIE Lab palette transfer to harmonize shots within an Act.

    Prevents consecutive AI shots from jumping wildly between warm/cool/neon hues while
    preserving natural lighting contrast and dampening digital AI chroma spikes.
    """
    import cv2

    if img_bgr is None or getattr(img_bgr, "size", 0) == 0:
        raise ValueError("img_bgr must be a non-empty BGR ndarray")

    blend_f = max(0.0, min(1.0, float(blend)))
    damp_f = max(0.5, min(1.0, float(chroma_damp)))

    if target_lab_mean is None:
        preset = CANONICAL_ACT_PALETTES["neutral_35mm_doc"]
        t_mean = np.array(preset["lab_mean"], dtype=np.float32)
        t_std = np.array(target_lab_std or preset["lab_std"], dtype=np.float32)
    elif isinstance(target_lab_mean, int):
        pkey = ACT_INDEX_TO_PALETTE.get(int(target_lab_mean), "neutral_35mm_doc")
        preset = CANONICAL_ACT_PALETTES[pkey]
        t_mean = np.array(preset["lab_mean"], dtype=np.float32)
        t_std = np.array(target_lab_std or preset["lab_std"], dtype=np.float32)
    elif isinstance(target_lab_mean, str):
        preset = CANONICAL_ACT_PALETTES.get(target_lab_mean, CANONICAL_ACT_PALETTES["neutral_35mm_doc"])
        t_mean = np.array(preset["lab_mean"], dtype=np.float32)
        t_std = np.array(target_lab_std or preset["lab_std"], dtype=np.float32)
    else:
        t_mean = np.array(target_lab_mean, dtype=np.float32)
        t_std = np.array(target_lab_std, dtype=np.float32) if target_lab_std is not None else None

    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    src_mean = lab.reshape(-1, 3).mean(axis=0)
    src_std = np.maximum(lab.reshape(-1, 3).std(axis=0), 1e-3)

    if t_std is None:
        scale = np.ones(3, dtype=np.float32)
    else:
        scale = np.clip(t_std / src_std, 0.65, 1.35)

    matched = (lab - src_mean[None, None, :]) * scale[None, None, :] + t_mean[None, None, :]
    # Damp digital AI neon oversaturation on a/b chrominance channels around neutral 128
    matched[..., 1] = 128.0 + (matched[..., 1] - 128.0) * damp_f
    matched[..., 2] = 128.0 + (matched[..., 2] - 128.0) * damp_f

    blended = np.clip((1.0 - blend_f) * lab + blend_f * matched, 0.0, 255.0).astype(np.uint8)
    return cv2.cvtColor(blended, cv2.COLOR_LAB2BGR)


def build_35mm_anti_ai_grade_filter(
    color_grade: str = DEFAULT_COLOR_GRADE,
    *,
    include_grain: bool = True,
    chapter_idx: int | None = None,
) -> str:
    """Build the unified Kodak 2383 35mm anti-AI de-plasticizer FFmpeg filter chain.

    Strips digital AI sharpening sheen, selectively tames neon cyan/lime/yellow artifacts,
    unifies cool-slate shadows & warm bronze-amber highlight roll-off across all Acts,
    lifts obsidian shadow toe, and applies fine temporal 35mm grain before `h264_nvenc`.
    """
    grade = str(color_grade or DEFAULT_COLOR_GRADE).strip().lower()
    if grade not in VALID_COLOR_GRADES:
        raise ValueError(f"Unsupported color_grade {color_grade!r}; expected one of {VALID_COLOR_GRADES}")
    if grade == "none":
        return ""

    # Subtle per-Act shadow/highlight balance nudge (tiny +-0.008 so entire film shares 1 print LUT)
    act_warmth = {
        1: -0.006,  # Pre-dawn river ambush: slightly cooler shadow floor
        2: 0.005,   # Imperial court candlelight: tiny bronze midtone warmth
        3: -0.004,  # Karst timber/forge prep: crisp slate neutrality
        4: -0.003,  # High-tide overcast estuary
        5: 0.004,   # Battle clash firelight
        6: 0.008,   # Co Loa golden-hour dawn
    }.get(int(chapter_idx) if chapter_idx is not None else 0, 0.0)

    rh = round(0.032 + act_warmth, 4)
    bh = round(-0.028 - act_warmth, 4)

    parts = [
        # 1) Micro-soften synthetic AI crispness / plastic specular edge halos
        "unsharp=3:3:-0.18:3:3:-0.08",
        # 2) Surgically pull back digital AI neon cyan, artificial foliage lime, & toxic yellow
        "selectivecolor=correction_method=relative:cyans=-0.28 0.08 0.05 0:greens=-0.16 0.04 0.06 0:yellows=0 0.04 -0.10 0",
        # 3) Restrained 35mm saturation + balanced filmic contrast
        "hue=s=0.91",
        "eq=contrast=1.05:brightness=-0.012:saturation=0.94:gamma=0.98",
        # 4) Unified Kodak 2383 split tone: cool-slate shadows, bronze mids, warm amber highs
        f"colorbalance=rs=-0.025:gs=-0.008:bs=0.028:rm=0.012:gm=0.002:bm=-0.018:rh={rh}:gh=0.014:bh={bh}",
        # 5) Lifted matte print shadow toe (0.02) + gentle highlight roll-off (0.96)
        "curves=master='0/0.02 0.25/0.23 0.5/0.50 0.78/0.80 1/0.96'",
    ]
    if include_grain:
        parts.append("noise=alls=4:allf=t+u")
    return ",".join(parts)


# ---------------------------------------------------------------------------
# V11.5 Hard Anti-AI Visual & Historical QA Validator + Color Continuity Audit
# ---------------------------------------------------------------------------
def _has_unnegated_term(text: str, term: str) -> bool:
    """Return True if `term` appears in `text` without a preceding negation cue."""
    if not text or not term:
        return False
    low = text.lower()
    t_esc = re.escape(term.lower())
    for m in re.finditer(rf"(?<![a-z0-9]){t_esc}(?![a-z0-9])", low):
        window = low[max(0, m.start() - 32) : m.start()]
        if re.search(r"\b(?:no|zero|without|never|avoid|ban(?:ned)?|free\s+of|not)\b[^.,;]{0,20}$", window):
            continue
        return True
    return False


def validate_beat_anti_ai_contract(
    beat: BeatSpec | dict[str, Any],
    *,
    character_roster: list[CharacterAnchorSpec] | dict[str, CharacterAnchorSpec] | None = None,
    historical_era_year: int | None = None,
) -> list[str]:
    """Validate a beat against V11.5 Anti-AI visual, historical flag, physics, and character locks."""
    if isinstance(beat, BeatSpec):
        beat_id = beat.beat_id
        visual_mode = beat.visual_mode
        tts_text = beat.tts_text
        char_ids = list(beat.character_ids)
        prompts: list[str] = []
        if beat.moving_cinema and beat.moving_cinema.prompt:
            prompts.append(beat.moving_cinema.prompt)
        if beat.spatial_terrain_ops and beat.spatial_terrain_ops.prompt:
            prompts.append(beat.spatial_terrain_ops.prompt)
        if beat.forensic_evidence_reveal and beat.forensic_evidence_reveal.prompt:
            prompts.append(beat.forensic_evidence_reveal.prompt)
        if beat.macro_parallax_still and beat.macro_parallax_still.prompt:
            prompts.append(beat.macro_parallax_still.prompt)
    else:
        beat_id = str(beat.get("beat_id") or "")
        visual_mode = str(beat.get("visual_mode") or "moving_cinema")
        tts_text = str(beat.get("tts_text") or "")
        mc_raw = beat.get("moving_cinema") or {}
        raw_cids = beat.get("character_ids")
        if raw_cids is None and isinstance(mc_raw, dict):
            raw_cids = mc_raw.get("character_ids")
        char_ids = [str(c).strip() for c in raw_cids if str(c).strip()] if isinstance(raw_cids, list) else []
        prompts = []
        for sub_key in ("moving_cinema", "spatial_terrain_ops", "forensic_evidence_reveal", "macro_parallax_still"):
            sub = beat.get(sub_key)
            if isinstance(sub, dict) and sub.get("prompt"):
                prompts.append(str(sub["prompt"]))
        if beat.get("prompt"):
            prompts.append(str(beat["prompt"]))

    combined_prompt = " ".join(prompts).strip()
    violations: list[str] = []

    # 1) Historical flag anachronisms (pre-1940 or unspecified historical documentary)
    if historical_era_year is None or historical_era_year < 1940:
        for term in ANTI_AI_QA_RULES["historical_flag_anachronisms"]["banned_terms"]:
            if _has_unnegated_term(combined_prompt, term):
                violations.append(
                    f"beat {beat_id}: historical_flag_anachronism detected ({term!r}) — "
                    f"use {ANTI_AI_QA_RULES['historical_flag_anachronisms']['required_replacement']}"
                )

    # 2) Plastic / waxy CGI / clone-crowd / tilt-shift / neon bans
    for term in ANTI_AI_QA_RULES["anti_plastic_cgi_bans"]["banned_terms"]:
        if _has_unnegated_term(combined_prompt, term):
            violations.append(
                f"beat {beat_id}: anti_plastic_cgi_violation detected ({term!r})"
            )

    # 3) Physics & motion defect red flags
    for term in ANTI_AI_QA_RULES["physics_and_motion_bans"]["prompt_red_flags"]:
        if _has_unnegated_term(combined_prompt, term):
            violations.append(
                f"beat {beat_id}: physics_motion_red_flag detected ({term!r})"
            )

    # 4) Story moving_cinema beats must include explicit `no text` / `zero text` guardrail
    if visual_mode == VisualMode.MOVING_CINEMA.value and combined_prompt:
        if not re.search(r"\b(?:no|zero|without)\s+(?:text|letters|captions|writing|inscriptions)\b", combined_prompt.lower()):
            violations.append(
                f"beat {beat_id}: moving_cinema prompt missing explicit 'no text' guardrail (risk of garbled AI signs/flags)"
            )

    # 5) Character roster referential integrity & undeclared named character detection
    roster_map: dict[str, CharacterAnchorSpec] = {}
    if isinstance(character_roster, dict):
        roster_map = dict(character_roster)
    elif isinstance(character_roster, list):
        roster_map = {c.character_id: c for c in character_roster}

    if roster_map:
        max_refs = int(ANTI_AI_QA_RULES["character_continuity_rules"]["max_refs_per_beat"])
        if len(char_ids) > max_refs:
            violations.append(
                f"beat {beat_id}: {len(char_ids)} character_ids exceeds max {max_refs} Flow reference_media_ids per shot"
            )
        for cid in char_ids:
            if cid not in roster_map:
                violations.append(
                    f"beat {beat_id}: character_id {cid!r} not declared in character_roster"
                )
        if visual_mode == VisualMode.MOVING_CINEMA.value and combined_prompt:
            prompt_ascii = _strip_vi_accents(combined_prompt).lower()
            tts_ascii = _strip_vi_accents(tts_text).lower()
            for cid, ch_spec in roster_map.items():
                if cid in char_ids:
                    continue
                # Check explicit named proper characters (skip generic troop archetypes unless named in prompt)
                cand_names = [ch_spec.name_vi, *ch_spec.aliases]
                for cname in cand_names:
                    cname_ascii = _strip_vi_accents(cname).strip().lower()
                    if len(cname_ascii) >= 5 and (
                        re.search(rf"(?<![a-z0-9]){re.escape(cname_ascii)}(?![a-z0-9])", prompt_ascii)
                        or (
                            len(cname_ascii.split()) >= 2
                            and re.search(rf"(?<![a-z0-9]){re.escape(cname_ascii)}(?![a-z0-9])", tts_ascii)
                            and any(k in prompt_ascii for k in ("commander", "general", "prince", "emperor", "king", "admiral", "hero", "portrait", "close-up"))
                        )
                    ):
                        violations.append(
                            f"beat {beat_id}: character_continuity_missing — {ch_spec.name_vi!r} ({cid}) appears "
                            f"without declaring character_ids=[{cid!r}] for Flow reference_media_ids lock"
                        )
                        break

    return violations


def audit_color_continuity(
    frame_paths: list[Path | str],
    *,
    max_delta_e: float = 22.0,
    max_luma_jump: float = 38.0,
    max_sat_p95: float = 185.0,
    max_neon_ratio: float = 0.08,
) -> dict[str, Any]:
    """Audit cross-shot Lab ΔE color jumps, luminance spikes, and digital AI neon oversaturation."""
    import cv2

    per_frame: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    violations: list[str] = []

    max_de_seen = 0.0
    max_luma_seen = 0.0
    max_sat_seen = 0.0
    max_neon_seen = 0.0

    prev_cie: tuple[float, float, float] | None = None
    prev_name = ""

    for raw_p in frame_paths:
        p = Path(raw_p)
        img = cv2.imread(str(p))
        if img is None or img.size == 0:
            violations.append(f"{p.name}: unreadable or empty image")
            continue

        # Downsample large 1080p frames for fast deterministic statistics
        if img.shape[1] > 480:
            scale = 480.0 / float(img.shape[1])
            img_s = cv2.resize(img, (480, max(1, int(round(img.shape[0] * scale)))), interpolation=cv2.INTER_AREA)
        else:
            img_s = img

        lab = cv2.cvtColor(img_s, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_cie = float(lab[..., 0].mean()) * (100.0 / 255.0)
        a_cie = float(lab[..., 1].mean()) - 128.0
        b_cie = float(lab[..., 2].mean()) - 128.0

        hsv = cv2.cvtColor(img_s, cv2.COLOR_BGR2HSV)
        h_ch = hsv[..., 0]
        s_ch = hsv[..., 1]
        v_ch = hsv[..., 2]
        sat_p95 = float(np.percentile(s_ch, 95))
        neon_mask = (
            (s_ch > 175)
            & (v_ch > 135)
            & (
                ((h_ch >= 78) & (h_ch <= 105))   # artificial neon cyan/teal
                | ((h_ch >= 38) & (h_ch <= 74))  # radioactive AI lime/green
                | ((h_ch >= 138) & (h_ch <= 168))  # cyberpunk neon magenta
            )
        )
        neon_ratio = float(neon_mask.mean())

        max_sat_seen = max(max_sat_seen, sat_p95)
        max_neon_seen = max(max_neon_seen, neon_ratio)

        per_frame.append({
            "frame": p.name,
            "lab_cie": [round(l_cie, 2), round(a_cie, 2), round(b_cie, 2)],
            "sat_p95": round(sat_p95, 2),
            "neon_ratio": round(neon_ratio, 4),
        })

        if sat_p95 > max_sat_p95:
            violations.append(
                f"{p.name}: oversaturated AI chroma sat_p95={sat_p95:.1f} > {max_sat_p95:.1f}"
            )
        if neon_ratio > max_neon_ratio:
            violations.append(
                f"{p.name}: digital AI neon cyan/lime/magenta ratio={neon_ratio:.3f} > {max_neon_ratio:.3f}"
            )

        if prev_cie is not None:
            dl = abs(l_cie - prev_cie[0])
            da = a_cie - prev_cie[1]
            db = b_cie - prev_cie[2]
            delta_e = float(math.sqrt(dl * dl + da * da + db * db))
            max_de_seen = max(max_de_seen, delta_e)
            max_luma_seen = max(max_luma_seen, dl)
            transitions.append({
                "from": prev_name,
                "to": p.name,
                "delta_e": round(delta_e, 2),
                "luma_jump": round(dl, 2),
            })
            if delta_e > max_delta_e:
                violations.append(
                    f"{prev_name} -> {p.name}: Lab color jump delta_e={delta_e:.1f} > {max_delta_e:.1f}"
                )
            if dl > max_luma_jump:
                violations.append(
                    f"{prev_name} -> {p.name}: luminance jump dL={dl:.1f} > {max_luma_jump:.1f}"
                )

        prev_cie = (l_cie, a_cie, b_cie)
        prev_name = p.name

    return {
        "passed": len(violations) == 0 and len(per_frame) > 0,
        "frame_count": len(per_frame),
        "max_delta_e": round(max_de_seen, 2),
        "max_luma_jump": round(max_luma_seen, 2),
        "max_sat_p95": round(max_sat_seen, 2),
        "max_neon_ratio": round(max_neon_seen, 4),
        "per_frame": per_frame,
        "transitions": transitions,
        "violations": violations,
    }


REMOTE_REBORN_NVENC_SCRIPT = r'''import json
import shutil
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np

work = Path(__file__).resolve().parent
t0 = time.time()

gpu_out = subprocess.check_output(
    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
).strip()
if "T4" not in gpu_out:
    raise RuntimeError(f"COLAB_GPU_REQUIRED: Tesla T4 GPU required, got: {gpu_out}")

manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
fps = int(manifest.get("fps", 30))
w = int(manifest.get("width", 1920))
h = int(manifest.get("height", 1080))
total_frames = int(manifest["total_frames"])
delogo_filter = str(manifest.get("delogo_filter") or "")
use_delogo = bool(manifest.get("delogo", True)) and bool(delogo_filter)
wm_pos = str(manifest.get("watermark_position") or "W-w-36:H-h-36")
output_filename = Path(str(manifest.get("output_filename") or "reborn_long_showcase_1080p.mp4")).name
default_grade_filter = str(manifest.get("color_grade_filter") or "").strip()
chunk_only_mode = bool(manifest.get("chunk_only_mode", False))

# Support both chunked manifests (full 85–120 beat episodes) and legacy flat segment manifests
chunks = manifest.get("chunks")
if not chunks:
    segs_all = manifest["segments"]
    chunks = [{
        "chunk_index": 0,
        "chunk_frames": total_frames,
        "fade_in_sec": 0.0,
        "fade_out_sec": 0.0,
        "segments": segs_all,
    }]

nvenc_args = None
chosen_preset = "p4"
for preset in ("p4", "p5", "p6"):
    args = [
        "-c:v", "h264_nvenc", "-profile:v", "high", "-preset", preset,
        "-rc", "vbr", "-cq", "16", "-b:v", "12M", "-maxrate", "20M",
        "-bufsize", "30M", "-g", str(fps), "-bf", "0", "-pix_fmt", "yuv420p",
        "-video_track_timescale", str(fps * 1000),
    ]
    probe = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.1:r=30", *args, "-f", "null", "-"],
        capture_output=True,
    )
    if probe.returncode == 0:
        nvenc_args = args
        chosen_preset = preset
        break
if nvenc_args is None:
    raise RuntimeError("COLAB_NVENC_UNAVAILABLE")

mezz_args = [
    "-c:v", "h264_nvenc", "-profile:v", "high", "-preset", chosen_preset,
    "-rc", "vbr", "-cq", "13", "-b:v", "18M", "-maxrate", "28M",
    "-bufsize", "36M", "-g", "15", "-bf", "0", "-pix_fmt", "yuv420p",
]


def _probe_duration(p: Path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)],
        capture_output=True, text=True, check=True,
    )
    return max(0.1, float(res.stdout.strip()))


def _encode_piped_frames(
    seg_out: Path,
    enc_f: int,
    frame_iter,
    err_log: Path,
    tag: str,
) -> None:
    """Pipe float32-warped BGR24 frames straight into h264_nvenc (zero /dev/shm JPEG bloat)."""
    cmd = [
        "ffmpeg", "-y", "-nostats",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "pipe:0",
        "-vf", f"fps={fps},settb=1/{fps},trim=end_frame={enc_f},setpts=PTS-STARTPTS,setsar=1,format=yuv420p",
        "-an", *mezz_args, "-r", str(fps), str(seg_out),
    ]
    with open(err_log, "wb") as efh:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=efh)
        assert proc.stdin is not None
        try:
            for frame_bgr in frame_iter:
                proc.stdin.write(frame_bgr.tobytes())
        except BrokenPipeError:
            pass
        finally:
            try:
                proc.stdin.close()
            except BrokenPipeError:
                pass
        rc = proc.wait()
    if rc != 0:
        tail = err_log.read_text(encoding="utf-8", errors="replace")[-1800:] if err_log.is_file() else ""
        raise RuntimeError(f"{tag}_PIPE_NVENC_FAILED (rc={rc}):\n{tail}")


def _encode_single_segment(seg: dict, seg_out: Path, shm_tmp: Path) -> None:
    idx = int(seg["index"])
    enc_f = int(seg["encode_frames"])
    needed_dur = enc_f / float(fps)
    kind = str(seg["source_kind"])
    err_log = shm_tmp / f"err_{idx:03d}.log"

    if kind == "video_mp4":
        src_mp4 = work / seg["arc_path"]
        probed_dur = _probe_duration(src_mp4)

        # Honor @motion-police clean_window_sec cap so zero clip ever enters a late tail artifact
        cw = seg.get("clean_window_sec")
        cw_start = 0.0
        cw_end = probed_dur
        use_cw_trim = False
        if isinstance(cw, (list, tuple)) and len(cw) >= 2:
            c0 = max(0.0, float(cw[0]))
            c1 = min(probed_dur, float(cw[1]))
            if c1 > c0 + 0.35:
                cw_start, cw_end = c0, c1
                use_cw_trim = (cw_start > 0.01) or (cw_end < probed_dur - 0.02)

        clean_dur = max(0.25, cw_end - cw_start)
        cw_prefix = f"trim=start={cw_start:.4f}:end={cw_end:.4f},setpts=PTS-STARTPTS," if use_cw_trim else ""

        d_seg = f"{delogo_filter}," if (use_delogo and seg.get("is_flow_clip")) else ""
        post_vf = (
            f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={w}:{h},setsar=1,{d_seg}"
            f"eq=contrast=1.04:saturation=1.03,unsharp=3:3:0.30:3:3:0.15,"
            f"fps={fps},settb=1/{fps},trim=end_frame={enc_f},setpts=PTS-STARTPTS,format=yuv420p"
        )
        if clean_dur >= needed_dur - 0.04:
            # 100% real-time 1.0x natural motion — zero speed-warping on native 4s/6s/8s/10s clips!
            pad_s = max(0.0, needed_dur - clean_dur + 0.08)
            vf_1x = f"{cw_prefix}tpad=stop_mode=clone:stop_duration={pad_s:.3f},{post_vf}" if pad_s > 0.0 else f"{cw_prefix}{post_vf}"
            fc_base = f"[0:v]{vf_1x}[vbase]"
        else:
            ratio = (needed_dur + 0.15) / clean_dur
            if ratio <= 1.65:
                fc_base = f"[0:v]{cw_prefix}setpts=({ratio:.6f})*(PTS-STARTPTS),{post_vf}[vbase]"
            else:
                reps = max(2, int(needed_dur / clean_dur) + 2)
                fc_base = (
                    f"[0:v]{cw_prefix}fps={fps},settb=1/{fps},split=2[vf0][vr0];"
                    f"[vr0]reverse[vr1];"
                    f"[vf0][vr1]concat=n=2:v=1:a=0,loop=loop={reps}:size=32767:start=0,"
                    f"setpts=N/({fps}*TB),{post_vf}[vbase]"
                )

        ovl_arc = seg.get("overlay_arc_path")
        ovl_path = (work / ovl_arc) if ovl_arc else None
        if ovl_path is not None and ovl_path.is_file():
            fade_out_st = max(0.25, needed_dur - 0.25)
            fc_full = (
                f"{fc_base};"
                f"[1:v]scale={w}:{h}:flags=lanczos,format=rgba,"
                f"fade=t=in:st=0:d=0.22:alpha=1,"
                f"fade=t=out:st={fade_out_st:.3f}:d=0.22:alpha=1[ovl];"
                f"[vbase][ovl]overlay=0:0:shortest=1,format=yuv420p[vout]"
            )
            cmd = [
                "ffmpeg", "-y", "-nostats",
                "-i", str(src_mp4),
                "-loop", "1", "-framerate", str(fps), "-t", f"{needed_dur + 0.25:.3f}", "-i", str(ovl_path),
                "-filter_complex", fc_full, "-map", "[vout]", "-an", *mezz_args, "-r", str(fps), str(seg_out),
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-nostats",
                "-i", str(src_mp4),
                "-filter_complex", fc_base, "-map", "[vbase]", "-an", *mezz_args, "-r", str(fps), str(seg_out),
            ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"SEG_{idx}_MP4_FAILED:\n{r.stderr[-1800:]}")

    elif kind == "forensic_dual_plate":
        bd_img = cv2.imread(str(work / seg["backdrop_arc_path"]))
        txt_rgba = cv2.imread(str(work / seg["text_arc_path"]), cv2.IMREAD_UNCHANGED)
        if bd_img is None or txt_rgba is None:
            raise RuntimeError(f"Cannot read dual forensic plate for seg {idx}")
        bd_img = cv2.resize(bd_img, (w, h), interpolation=cv2.INTER_LANCZOS4)
        txt_rgba = cv2.resize(txt_rgba, (w, h), interpolation=cv2.INTER_LANCZOS4)
        if txt_rgba.ndim == 2:
            txt_bgr = cv2.cvtColor(txt_rgba, cv2.COLOR_GRAY2BGR).astype(np.float32)
            txt_a = np.ones((h, w, 1), dtype=np.float32)
        elif txt_rgba.shape[2] == 4:
            txt_bgr = txt_rgba[..., :3].astype(np.float32)
            txt_a = (txt_rgba[..., 3:4].astype(np.float32)) / 255.0
        else:
            txt_bgr = txt_rgba[..., :3].astype(np.float32)
            txt_a = np.ones((h, w, 1), dtype=np.float32)

        fade_in_f = max(1.0, min(enc_f * 0.14, fps * 0.35))

        def _gen_dual():
            for fi in range(enc_f):
                tn = fi / max(1, enc_f - 1)
                eased = 4 * tn * tn * tn if tn < 0.5 else 1 - ((-2 * tn + 2) ** 3) / 2
                sc = 1.0 + 0.042 * eased
                mat = np.float32([[sc, 0.0, (1.0 - sc) * w * 0.5], [0.0, sc, (1.0 - sc) * h * 0.5]])
                warped = cv2.warpAffine(bd_img, mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101).astype(np.float32)
                op = min(1.0, fi / fade_in_f)
                a = txt_a * op
                yield np.clip(warped * (1.0 - a) + txt_bgr * a, 0.0, 255.0).astype(np.uint8)

        _encode_piped_frames(seg_out, enc_f, _gen_dual(), err_log, f"SEG_{idx}_DUAL_FORENSIC")

    elif kind == "single_image":
        src_img = cv2.imread(str(work / seg["arc_path"]))
        if src_img is None:
            raise RuntimeError(f"Cannot read image for seg {idx}")
        src_img = cv2.resize(src_img, (w, h), interpolation=cv2.INTER_LANCZOS4)

        def _gen_still():
            for fi in range(enc_f):
                tn = fi / max(1, enc_f - 1)
                eased = 4 * tn * tn * tn if tn < 0.5 else 1 - ((-2 * tn + 2) ** 3) / 2
                sc = 1.0 + 0.038 * eased
                mat = np.float32([[sc, 0.0, (1.0 - sc) * w * 0.5], [0.0, sc, (1.0 - sc) * h * 0.5]])
                yield cv2.warpAffine(src_img, mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

        _encode_piped_frames(seg_out, enc_f, _gen_still(), err_log, f"SEG_{idx}_SINGLE_IMG")

    elif kind == "frame_seq":
        src_dir = work / seg["arc_dir"]
        files = sorted(
            [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")],
            key=lambda p: p.name,
        )
        if not files:
            raise RuntimeError(f"Empty frame_seq dir for seg {idx}: {src_dir}")
        ext = files[0].suffix.lower()
        norm_dir = shm_tmp / f"norm_{idx:03d}"
        norm_dir.mkdir(parents=True, exist_ok=True)
        for fi, fp in enumerate(files):
            (norm_dir / f"f_{fi:05d}{ext}").symlink_to(fp.resolve())
        n_src = len(files)
        if n_src >= enc_f:
            vf = f"fps={fps},settb=1/{fps},trim=end_frame={enc_f},setpts=PTS-STARTPTS,scale={w}:{h}:flags=lanczos,setsar=1,format=yuv420p"
        else:
            stretch = (needed_dur + 0.12) / max(1.0 / fps, n_src / float(fps))
            vf = f"setpts=({stretch:.6f})*(PTS-STARTPTS),fps={fps},settb=1/{fps},trim=end_frame={enc_f},setpts=PTS-STARTPTS,scale={w}:{h}:flags=lanczos,setsar=1,format=yuv420p"
        cmd = [
            "ffmpeg", "-y", "-nostats", "-framerate", str(fps), "-start_number", "0",
            "-i", str(norm_dir / f"f_%05d{ext}"), "-vf", vf, "-an", *mezz_args, "-r", str(fps), str(seg_out),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        shutil.rmtree(norm_dir, ignore_errors=True)
        if r.returncode != 0:
            raise RuntimeError(f"SEG_{idx}_SEQ_FAILED:\n{r.stderr[-1800:]}")
    else:
        raise RuntimeError(f"Unsupported source_kind={kind!r}")


shm_root = Path("/dev/shm/vp_reborn_nvenc")
chunks_dir = work / "_chunks"
shutil.rmtree(shm_root, ignore_errors=True)
shutil.rmtree(chunks_dir, ignore_errors=True)
shm_root.mkdir(parents=True, exist_ok=True)
chunks_dir.mkdir(parents=True, exist_ok=True)

try:
    chunk_mp4s: list[Path] = []
    wm_png = work / "watermark_150x150.png"

    for ch_obj in chunks:
        c_idx = int(ch_obj["chunk_index"])
        c_segs = ch_obj["segments"]
        c_frames = int(ch_obj["chunk_frames"])
        fade_in_s = float(ch_obj.get("fade_in_sec") or 0.0)
        fade_out_s = float(ch_obj.get("fade_out_sec") or 0.0)

        shm_chunk = shm_root / f"c_{c_idx:02d}"
        shutil.rmtree(shm_chunk, ignore_errors=True)
        shm_chunk.mkdir(parents=True, exist_ok=True)

        seg_mp4s: list[Path] = []
        for seg in c_segs:
            seg_out = shm_chunk / f"seg_{int(seg['index']):03d}.mp4"
            _encode_single_segment(seg, seg_out, shm_chunk)
            seg_mp4s.append(seg_out)

        # Stitch <=16 segments of this chunk + obsidian Act fade + watermark W-w-36:H-h-36
        cmd = ["ffmpeg", "-y", "-nostats"]
        for smp4 in seg_mp4s:
            cmd.extend(["-i", str(smp4)])
        wm_idx = len(seg_mp4s)
        cmd.extend(["-i", str(wm_png)])

        fc: list[str] = []
        for li, seg in enumerate(c_segs):
            ef = int(seg["encode_frames"])
            fc.append(f"[{li}:v]fps={fps},settb=1/{fps},trim=end_frame={ef},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[vs{li}]")

        if len(c_segs) == 1:
            fc.append(f"[vs0]trim=end_frame={c_frames},setpts=PTS-STARTPTS[vchunk_base]")
        else:
            prev = "[vs0]"
            cum_base = 0
            for li in range(len(c_segs) - 1):
                cum_base += int(c_segs[li]["base_frames"])
                ov = int(c_segs[li]["overhang_frames"])
                xf_name = str(c_segs[li].get("xfade_transition") or "fade")
                out_lbl = "[vraw]" if li == len(c_segs) - 2 else f"[vx{li}]"
                if ov > 0:
                    fc.append(
                        f"{prev}[vs{li + 1}]xfade=transition={xf_name}:"
                        f"duration={ov / float(fps):.6f}:offset={cum_base / float(fps):.6f},"
                        f"fps={fps},settb=1/{fps}{out_lbl}"
                    )
                else:
                    fc.append(f"{prev}[vs{li + 1}]concat=n=2:v=1:a=0,fps={fps},settb=1/{fps}{out_lbl}")
                prev = out_lbl
            fc.append(f"[vraw]fps={fps},settb=1/{fps},trim=end_frame={c_frames},setpts=PTS-STARTPTS[vchunk_base]")

        fade_filters: list[str] = []
        if fade_in_s > 0.0:
            fade_filters.append(f"fade=t=in:st=0:d={fade_in_s:.3f}")
        if fade_out_s > 0.0:
            fo_st = max(0.0, (c_frames / float(fps)) - fade_out_s)
            fade_filters.append(f"fade=t=out:st={fo_st:.4f}:d={fade_out_s:.3f}")

        # V11.5 Unified Kodak 2383 35mm anti-AI print grade applied uniformly BEFORE watermark
        chunk_grade = str(ch_obj.get("color_grade_filter") or default_grade_filter).strip()
        post_chain: list[str] = []
        if chunk_grade:
            post_chain.append(chunk_grade)
        post_chain.extend(fade_filters)
        if post_chain:
            fc.append(f"[vchunk_base]{','.join(post_chain)}[vchunk_lit]")
            v_pre_wm = "[vchunk_lit]"
        else:
            v_pre_wm = "[vchunk_base]"

        fc.append(
            f"{v_pre_wm}[{wm_idx}:v]overlay={wm_pos}:eof_action=repeat,"
            f"fps={fps},settb=1/{fps},trim=end_frame={c_frames},setpts=PTS-STARTPTS,format=yuv420p[vout]"
        )

        # In parallel multi-GPU chunk_only_mode, write finished chunk directly to work/ so it persists past cleanup
        chunk_mp4 = (work / f"chunk_{c_idx:02d}.mp4") if chunk_only_mode else (chunks_dir / f"chunk_{c_idx:02d}.mp4")
        cmd.extend([
            "-filter_complex", ";".join(fc),
            "-map", "[vout]", "-an",
            *nvenc_args, "-r", str(fps),
            str(chunk_mp4),
        ])
        res = subprocess.run(cmd, cwd=str(work), capture_output=True, text=True)
        shutil.rmtree(shm_chunk, ignore_errors=True)
        if res.returncode != 0:
            raise RuntimeError(f"CHUNK_{c_idx:02d}_NVENC_FAILED:\n{res.stderr[-2500:]}")
        chunk_mp4s.append(chunk_mp4)
        print(f"CHUNK_{c_idx:02d}_DONE frames={c_frames} bytes={chunk_mp4.stat().st_size}", flush=True)

    if chunk_only_mode:
        print(
            f"REBORN_CHUNK_WORKER_COMPLETE_SUCCESS chunks={len(chunk_mp4s)} elapsed={time.time() - t0:.2f}s",
            flush=True,
        )
    else:
        # Lossless concat of all Act-chunks + calibrated 48kHz stereo AAC mux (zero re-encode!)
        concat_txt = work / "chunks_concat.txt"
        concat_txt.write_text(
            "\n".join(f"file '{cp.resolve()}'" for cp in chunk_mp4s) + "\n",
            encoding="utf-8",
        )
        final_mp4 = work / output_filename
        mux_cmd = [
            "ffmpeg", "-y", "-nostats",
            "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-i", str(work / "master_audio.m4a"),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "copy",
            "-shortest", "-movflags", "+faststart",
            str(final_mp4),
        ]
        res_mux = subprocess.run(mux_cmd, cwd=str(work), capture_output=True, text=True)
        if res_mux.returncode != 0:
            raise RuntimeError(f"LOSSLESS_CONCAT_MUX_FAILED:\n{res_mux.stderr[-2500:]}")
        if not final_mp4.is_file() or final_mp4.stat().st_size < 500_000:
            raise RuntimeError("Final MP4 missing or unexpectedly small")
        print(
            f"REBORN_RENDER_COMPLETE_SUCCESS chunks={len(chunk_mp4s)} elapsed={time.time() - t0:.2f}s bytes={final_mp4.stat().st_size}",
            flush=True,
        )
finally:
    shutil.rmtree(shm_root, ignore_errors=True)
    shutil.rmtree(chunks_dir, ignore_errors=True)
'''


# ---------------------------------------------------------------------------
# Spec Export (PilotSpec -> JSON)
# ---------------------------------------------------------------------------
def export_pilot_spec_json(spec: PilotSpec) -> dict[str, Any]:
    """Export PilotSpec to a JSON-serializable dict."""
    def _beat_to_dict(b: BeatSpec) -> dict[str, Any]:
        d: dict[str, Any] = {
            "beat_id": b.beat_id,
            "beat_index": b.beat_index,
            "visual_mode": b.visual_mode,
            "tts_text": b.tts_text,
            "pre_silence_sec": b.pre_silence_sec,
            "post_sfx_hold_sec": b.post_sfx_hold_sec,
            "is_silence_drop": b.is_silence_drop,
            "sfx_solo_id": b.sfx_solo_id,
            "diegetic_sfx": b.diegetic_sfx,
            "camera_move": b.camera_move,
            "vfx_shader": b.vfx_shader,
            "show_keyword": b.show_keyword,
            "main_word": b.main_word,
            "target_keyword": b.target_keyword,
            "delivery_mode": b.delivery_mode,
        }
        if b.moving_cinema:
            d["moving_cinema"] = {
                "prompt": b.moving_cinema.prompt,
                "chain_pattern": b.moving_cinema.chain_pattern,
                "clip_duration_range": list(b.moving_cinema.clip_duration_range),
                "seam_mode": b.moving_cinema.seam_mode,
                "model": b.moving_cinema.model,
            }
        if b.spatial_terrain_ops:
            st = b.spatial_terrain_ops
            d["spatial_terrain_ops"] = {
                "region_key": st.region_key,
                "preset": st.preset,
                "geo_clash_spec": st.geo_clash_spec,
                "prompt": st.prompt,
                "camera_pitch_deg": st.camera_pitch_deg,
                "camera_fly_in": {
                    "start_zoom": st.camera_start_zoom,
                    "end_zoom": st.camera_end_zoom,
                    "duration_sec": st.camera_fly_duration_sec,
                    "easing": st.camera_easing,
                },
                "tactical_callouts": st.tactical_callouts,
                "sovereignty_labels": st.sovereignty_labels,
                "tidal_animation": st.tidal_animation,
                "waypoint_step": st.waypoint_step,
                "de_modernize": st.de_modernize,
                "sovereignty_markers": st.sovereignty_markers,
            }
        if b.forensic_evidence_reveal:
            fr = b.forensic_evidence_reveal
            d["forensic_evidence_reveal"] = {
                "layout": fr.layout,
                "timestamp_text": fr.timestamp_text,
                "headline_text": fr.headline_text,
                "prompt": fr.prompt,
                "spotlight_mask": fr.spotlight_mask,
                "depth_of_field_blur": fr.depth_of_field_blur,
                "zero_rectangles": fr.zero_rectangles,
                "zero_left_stripes": fr.zero_left_stripes,
            }
        if b.macro_parallax_still:
            mp = b.macro_parallax_still
            d["macro_parallax_still"] = {
                "prompt": mp.prompt,
                "max_hold_sec": mp.max_hold_sec,
                "camera_motion": mp.camera_motion,
                "depth_layers": mp.depth_layers,
                "float32_subpixel": mp.float32_subpixel,
            }
        if b.character_ids:
            d["character_ids"] = list(b.character_ids)
        if b.act_palette:
            d["act_palette"] = b.act_palette
        if b.hud_callout:
            d["hud_callout"] = dict(b.hud_callout)
        if b.reuse_pilot_clip:
            d["reuse_pilot_clip"] = b.reuse_pilot_clip
        return d

    out_dict: dict[str, Any] = {
        "engine": spec.engine,
        "engine_version": spec.engine_version,
        "channel_id": spec.channel_id,
        "job_id": spec.job_id,
        "format": spec.format,
        "resolution": spec.resolution,
        "fps": spec.fps,
        "target_duration_sec": list(spec.target_duration_range),
        "color_grade": spec.color_grade,
        "audio": {
            "sample_rate": spec.sample_rate,
            "channels": spec.audio_channels,
            "target_lufs": spec.target_lufs,
            "max_true_peak_dbtp": spec.max_true_peak_dbtp,
            "voice_id": spec.voice_id,
            "voice_profile": spec.voice_profile,
        },
        "acoustic_breathing": {
            "j_cut_prelap_sec": spec.j_cut_prelap_sec,
            "cold_open_sfx_lead_in_sec": spec.cold_open_sfx_lead_in_sec,
            "mix_stems": spec.mix_stems,
            "stem_count": len(spec.mix_stems),
        },
        "thumbnail": {
            "prompt": spec.thumbnail_prompt,
            "max_size_bytes": spec.thumbnail_max_size_bytes,
        },
        "chapters": [
            {
                "chapter_idx": ch.chapter_idx,
                "chapter_header": ch.chapter_header,
                "chapter_title": ch.chapter_title,
                "chapter_style": ch.chapter_style,
                "beats": [_beat_to_dict(b) for b in ch.beats],
            }
            for ch in spec.chapters
        ],
        "transitions": {
            "intra_chain": spec.transitions.intra_chain,
            "scene_boundary": spec.transitions.scene_boundary,
            "map_entry": spec.transitions.map_entry,
            "act_break": spec.transitions.act_break,
            "banned": list(BANNED_TRANSITIONS),
        },
        "watermark": {
            "path": spec.watermark_path,
            "position": spec.watermark_position,
            "delogo": spec.delogo,
        },
    }
    if spec.character_roster:
        out_dict["character_roster"] = [
            {
                "character_id": c.character_id,
                "name_vi": c.name_vi,
                "faction": c.faction,
                "dynasty_era": c.dynasty_era,
                "face_and_age_dna": c.face_and_age_dna,
                "armor_and_wardrobe_lock": c.armor_and_wardrobe_lock,
                "signature_props": list(c.signature_props),
                "color_palette_hex": list(c.color_palette_hex),
                "anti_anachronism_bans": list(c.anti_anachronism_bans),
                "aliases": list(c.aliases),
                "anchor_image_path": c.anchor_image_path,
                "profile_media_ids": dict(c.profile_media_ids),
            }
            for c in spec.character_roster
        ]
    if spec.output_mp4_name:
        out_dict["output_paths"] = {"final_mp4": spec.output_mp4_name}
    return out_dict
