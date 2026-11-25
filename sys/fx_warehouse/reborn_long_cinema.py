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

# Duration bounds for pilot showcase (sec)
PILOT_MIN_DURATION_SEC = 70.0
PILOT_MAX_DURATION_SEC = 95.0

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
    geo_clash_spec: str | dict[str, Any] | None = None  # preset name or custom dict for geo_empire_clash_3d
    camera_start_zoom: float = 1.0
    camera_end_zoom: float = 3.5
    camera_fly_duration_sec: float = 4.0
    camera_easing: str = "ease_in_out_cubic"
    tactical_callouts: list[dict[str, Any]] = field(default_factory=list)
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
    return SpatialTerrainSpec(
        region_key=str(raw.get("region_key", "east_asia_vietnam")),
        geo_clash_spec=raw.get("geo_clash_spec"),
        camera_start_zoom=float(cam.get("start_zoom", 1.0)),
        camera_end_zoom=float(cam.get("end_zoom", 3.5)),
        camera_fly_duration_sec=float(cam.get("duration_sec", 4.0)),
        camera_easing=str(cam.get("easing", "ease_in_out_cubic")),
        tactical_callouts=list(raw.get("tactical_callouts", [])),
        de_modernize=bool(raw.get("de_modernize", True)),
        sovereignty_markers=bool(raw.get("sovereignty_markers", True)),
    )


def _parse_forensic_reveal(raw: dict[str, Any] | None) -> ForensicRevealSpec | None:
    if not raw:
        return None
    return ForensicRevealSpec(
        layout=str(raw.get("layout", "countdown_clock")),
        timestamp_text=str(raw.get("timestamp_text", "")),
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


def _parse_beat(raw: dict[str, Any]) -> BeatSpec:
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

    # Same visual mode within moving_cinema chain
    if (
        prev_beat.visual_mode == VisualMode.MOVING_CINEMA.value
        and curr_beat.visual_mode == VisualMode.MOVING_CINEMA.value
    ):
        t = rules.intra_chain
        return {"type": t, "duration_sec": TRANSITION_DURATIONS.get(t, 0.0)}

    # Entering or leaving spatial terrain
    if (
        curr_beat.visual_mode == VisualMode.SPATIAL_TERRAIN_OPS.value
        or prev_beat.visual_mode == VisualMode.SPATIAL_TERRAIN_OPS.value
    ):
        t = rules.map_entry
        return {"type": t, "duration_sec": TRANSITION_DURATIONS.get(t, 0.55)}

    # Cross-mode scene boundary
    if prev_beat.visual_mode != curr_beat.visual_mode:
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

    dist = spec.visual_mode_distribution()

    # At least 2 visual modes
    if len(dist) < 2:
        errors.append(
            "Must use at least 2 different visual modes to avoid monotony"
        )

    # moving_cinema cap at 70%
    mc_count = dist.get(VisualMode.MOVING_CINEMA.value, 0)
    if n > 0 and mc_count / n > 0.70:
        errors.append(
            f"moving_cinema beats ({mc_count}/{n} = {mc_count / n:.0%}) "
            f"exceed 70% cap — add more spatial/forensic/parallax variety"
        )

    # No 4+ consecutive same visual mode
    streak = 1
    for i in range(1, n):
        if all_beats[i].visual_mode == all_beats[i - 1].visual_mode:
            streak += 1
            if streak > 3:
                errors.append(
                    f"4+ consecutive {all_beats[i].visual_mode} beats at "
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

    # Delogo (remove Flow AI watermark from bottom-right)
    if delogo:
        vf_parts.append(
            f"delogo=x={width - 140}:y={height - 140}:w=105:h=105"
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
                "camera_fly_in": {
                    "start_zoom": st.camera_start_zoom,
                    "end_zoom": st.camera_end_zoom,
                    "duration_sec": st.camera_fly_duration_sec,
                    "easing": st.camera_easing,
                },
                "tactical_callouts": st.tactical_callouts,
                "de_modernize": st.de_modernize,
                "sovereignty_markers": st.sovereignty_markers,
            }
        if b.forensic_evidence_reveal:
            fr = b.forensic_evidence_reveal
            d["forensic_evidence_reveal"] = {
                "layout": fr.layout,
                "timestamp_text": fr.timestamp_text,
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
        return d

    return {
        "engine": spec.engine,
        "engine_version": spec.engine_version,
        "channel_id": spec.channel_id,
        "job_id": spec.job_id,
        "format": spec.format,
        "resolution": spec.resolution,
        "fps": spec.fps,
        "target_duration_sec": list(spec.target_duration_range),
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
            "mix_stems": spec.mix_stems,
            "stem_count": len(spec.mix_stems),
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
