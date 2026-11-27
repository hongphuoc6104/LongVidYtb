"""V12 Live-Action 12-Slot Shot Coverage Planner, Prompt Compiler & Diversity Validator.

Implements Thread C (`04_live_action_shot_coverage_and_microbeats.json`) for `@SuKeLaiVN`:
1. **12-Slot Camera & Coverage Matrix** (`CAMERA_COVERAGE_MATRIX_12_SLOT`) uniting all
   **6 Missing Live-Action Shot Classes** (`MACRO_PROP`, `OTS_DIRTY`, `GROUND_MUD`,
   `GODS_EYE`, `REACTION_MICRO`, `ENV_SENSORY`) with the **6 Core Cinema Coverage Classes**
   (`WIDE_ESTABLISHING`, `LOW_HERO_SCALE`, `TWO_SHOT_BLOCKING`, `DUTCH_CHAOS_IMPACT`,
   `TRACKING_STEADICAM`, `EDITORIAL_STAGE_CUTAWAY`).
2. **Zero-Face / Zero-Human Prompt Sanitizer** (`strip_character_portraits_from_prompt`):
   Explicitly strips `[Cast Lock — ...]`, named historical personages, and full-face/portrait
   clauses from `MACRO_PROP` and `ENV_SENSORY` prompts so Flow BELUGA generates pure tactile
   close-ups and zero-human atmospheric B-roll rather than centered human portraits.
3. **6 Multi-Shot Scene Coverage Formulas** (`MULTI_SHOT_COVERAGE_FORMULAS`):
   `Command Decision`, `Ambush Eruption`, `Forensic Evidence`, `Battle Impact`,
   `Time-Passage Bridge`, and `Psychological Duel`.
4. **Dual-Model Prompt Compiler** (`compile_v12_coverage_prompts`):
   Compiles BELUGA `0c` image prompts + `veo_3_1_lite` (`10c` Seam Mode) + `macaron_cookie`
   (`Omni 1.2 Flash Frame-Link`) motion prompts while banning deprecated `veo_3_1_fast` and
   `omni_1_1`.
5. **V12 Coverage Validator** (`validate_v12_shot_coverage`):
   Enforces `>= 30%` non-portrait beats on Shorts, `>= 15%` `MACRO_PROP` on Longs,
   `0` three-in-a-row medium portraits, `0` repetitive back-of-head silhouettes, and
   strict zero-face / zero-human hygiene on `MACRO_PROP` & `ENV_SENSORY`.
"""

from __future__ import annotations

import copy
import re
from dataclasses import asdict, dataclass
from typing import Any, Literal

FormatProfile = Literal["short_9x16", "long_16x9"]

DEFAULT_FILM_LOCK_9X16 = (
    "35mm vertical 9:16 cinema stock, Kodak Vision3 500T, crisp clear-air optical depth, "
    "natural fine silver-halide grain, plain unmarked silk banners, zero text, zero captions, "
    "zero watermarks, zero UI overlays"
)

DEFAULT_FILM_LOCK_16X9 = (
    "35mm widescreen 16:9 cinema stock, Kodak Vision3 500T, crisp clear-air optical depth, "
    "natural fine silver-halide grain, plain unmarked silk banners, zero text, zero captions, "
    "zero watermarks, zero UI overlays"
)

ALLOWED_FLOW_VIDEO_MODELS: tuple[str, ...] = (
    "veo_3_1_lite",
    "macaron_cookie",
    "omni_flash",
)

DEPRECATED_FLOW_VIDEO_MODELS: tuple[str, ...] = (
    "veo_3_1_fast",
    "omni_1_1",
    "veo_extend",
    "veo_3_1_quality",
)

MISSING_LIVE_ACTION_SHOT_CLASSES: tuple[str, ...] = (
    "MACRO_PROP",
    "OTS_DIRTY",
    "GROUND_MUD",
    "GODS_EYE",
    "REACTION_MICRO",
    "ENV_SENSORY",
)

CORE_CINEMA_SHOT_CLASSES: tuple[str, ...] = (
    "WIDE_ESTABLISHING",
    "LOW_HERO_SCALE",
    "TWO_SHOT_BLOCKING",
    "DUTCH_CHAOS_IMPACT",
    "TRACKING_STEADICAM",
    "EDITORIAL_STAGE_CUTAWAY",
)

V12_SHOT_CLASSES: tuple[str, ...] = (
    "GODS_EYE",
    "OTS_DIRTY",
    "MACRO_PROP",
    "WIDE_ESTABLISHING",
    "REACTION_MICRO",
    "GROUND_MUD",
    "TWO_SHOT_BLOCKING",
    "ENV_SENSORY",
    "LOW_HERO_SCALE",
    "TRACKING_STEADICAM",
    "DUTCH_CHAOS_IMPACT",
    "EDITORIAL_STAGE_CUTAWAY",
)

NON_PORTRAIT_SHOT_CLASSES: frozenset[str] = frozenset({
    "MACRO_PROP",
    "OTS_DIRTY",
    "GROUND_MUD",
    "GODS_EYE",
    "ENV_SENSORY",
    "EDITORIAL_STAGE_CUTAWAY",
})

MEDIUM_PORTRAIT_SHOT_CLASSES: frozenset[str] = frozenset({
    "WIDE_ESTABLISHING",
    "LOW_HERO_SCALE",
    "TWO_SHOT_BLOCKING",
    "DUTCH_CHAOS_IMPACT",
})

SHOT_CLASS_ALIASES: dict[str, str] = {
    # Canonical self-mappings
    **{c: c for c in V12_SHOT_CLASSES},
    # Research 04 & legacy slot aliases
    "MEDIUM_COMMAND": "TWO_SHOT_BLOCKING",
    "LOW_HERO": "LOW_HERO_SCALE",
    "ATMOSPHERIC": "ENV_SENSORY",
    "TIGHT_ACTION": "DUTCH_CHAOS_IMPACT",
    "SILHOUETTE_SCALE": "LOW_HERO_SCALE",
    # Research 06 20-beat director grammar aliases
    "EXTREME_MACRO_TACTILE": "MACRO_PROP",
    "SILK_CALLIGRAPHY_MACRO": "MACRO_PROP",
    "POV_HANDS_TACTILE_MACRO": "MACRO_PROP",
    "LACQUER_BRONZE_RELIEF_MACRO": "MACRO_PROP",
    "DIRTY_OTS": "OTS_DIRTY",
    "GROUND_ANKLE_MUD_POV": "GROUND_MUD",
    "SUBMERGED_WATERLINE_POV": "GROUND_MUD",
    "SUBMERGED_KEEL_OVERHEAD_POV": "GROUND_MUD",
    "POV_UPWARD_LOOM": "LOW_HERO_SCALE",
    "GODS_EYE_FORMATION_90": "GODS_EYE",
    "PLUMB_LINE_90_OVERHEAD": "GODS_EYE",
    "REACTION_MICRO_ACTING": "REACTION_MICRO",
    "TELEPHOTO_85_135_OCULAR": "REACTION_MICRO",
    "ENVIRONMENTAL_SENSORY": "ENV_SENSORY",
    "WIDE_ESTABLISHING_CANYON": "WIDE_ESTABLISHING",
    "HIGH_CLIFF_AERIAL": "WIDE_ESTABLISHING",
    "ELEVATED_DIAGONAL_WIDE": "WIDE_ESTABLISHING",
    "WIDE_NAVAL_COLLISION": "WIDE_ESTABLISHING",
    "WIDE_PALACE_INTERIOR": "WIDE_ESTABLISHING",
    "LOW_ANGLE_ARCHITECTURAL": "LOW_HERO_SCALE",
    "LOW_ANGLE_CANYON_LOOM": "LOW_HERO_SCALE",
    "LOW_ANGLE_HERO": "LOW_HERO_SCALE",
    "LOW_ANGLE_NAVAL_LOOM": "LOW_HERO_SCALE",
    "LOW_ANGLE_SCULPTURAL_HERO": "LOW_HERO_SCALE",
    "LOW_ANGLE_SHIELD_WALL": "LOW_HERO_SCALE",
    "WORM_EYE_18MM_CRANE": "LOW_HERO_SCALE",
    "SYMMETRICAL_TWO_SHOT_PROFILE": "TWO_SHOT_BLOCKING",
    "SYMMETRICAL_STORYBOOK_TABLEAU": "TWO_SHOT_BLOCKING",
    "SCULPTURAL_RIVERBANK_TABLEAU": "TWO_SHOT_BLOCKING",
    "SCULPTURAL_COMBAT_TABLEAU": "DUTCH_CHAOS_IMPACT",
    "MEDIUM_SHADOW_SILHOUETTE": "TWO_SHOT_BLOCKING",
    "MEDIUM_VILLAGE_HEARTH": "TWO_SHOT_BLOCKING",
    "MEDIUM_DECK_IMPACT": "DUTCH_CHAOS_IMPACT",
    "DOORWAY_RECEDING_FRAME": "TRACKING_STEADICAM",
    "TIGHT_ACTION_IMPACT": "DUTCH_CHAOS_IMPACT",
    "HANDHELD_45_SHUTTER_SHOCK": "DUTCH_CHAOS_IMPACT",
    "LACQUER_TO_FLESH_MORPH": "DUTCH_CHAOS_IMPACT",
    "FLESH_TO_BRONZE_CRYSTALLIZE": "DUTCH_CHAOS_IMPACT",
    "STEADICAM_40MM_TRACKING": "TRACKING_STEADICAM",
    "LATERAL_CAVALRY_TRACKING": "TRACKING_STEADICAM",
    "LATERAL_OAR_TRACKING": "TRACKING_STEADICAM",
    "ARCHIVAL_TABLETOP_90": "EDITORIAL_STAGE_CUTAWAY",
    "SLOW_GIANT_MAP_V9": "EDITORIAL_STAGE_CUTAWAY",
    "SPLIT_SCREEN_2PX_DIPTYCH": "EDITORIAL_STAGE_CUTAWAY",
    "WATERLINE_CROSS_SECTION_SLICE": "EDITORIAL_STAGE_CUTAWAY",
    "LONGITUDINAL_CROSS_SECTION_RIG": "EDITORIAL_STAGE_CUTAWAY",
    "WOODBLOCK_DO_PAPER_REDLINE": "EDITORIAL_STAGE_CUTAWAY",
    "STEADICAM_SKY_TRACKED_MATH": "EDITORIAL_STAGE_CUTAWAY",
    "OPTICAL_FREEZE_FORK": "EDITORIAL_STAGE_CUTAWAY",
    "OPTICAL_SPEEDRAMP_RINGS": "EDITORIAL_STAGE_CUTAWAY",
    "CARVED_STONE_LACQUER_STELE": "EDITORIAL_STAGE_CUTAWAY",
}


@dataclass(frozen=True)
class ShotClassSpec:
    """Optical, compositional, and motion contract for a single V12 shot class."""

    slot: int
    code: str
    shot_type: str
    lens_spec: str
    angle_spec: str
    composition_rule: str
    default_camera_move: str
    default_duration_short_sec: float
    default_duration_long_sec: float
    is_non_portrait: bool
    is_medium_portrait: bool
    zero_face_strict: bool
    zero_human_strict: bool
    beluga_template: str
    veo_motion_suffix: str
    narrative_function: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CAMERA_COVERAGE_MATRIX_12_SLOT: tuple[ShotClassSpec, ...] = (
    ShotClassSpec(
        slot=1,
        code="GODS_EYE",
        shot_type="God's-Eye Overhead Formation",
        lens_spec="35mm-50mm orthographic",
        angle_spec="70°-90° perpendicular-down",
        composition_rule="NO horizon visible; ground or dark river water fills 100% of frame; geometric formation pattern.",
        default_camera_move="slow_crane_descend",
        default_duration_short_sec=2.5,
        default_duration_long_sec=4.5,
        is_non_portrait=True,
        is_medium_portrait=False,
        zero_face_strict=True,
        zero_human_strict=False,
        beluga_template=(
            "Bird's-eye 70-90 degree perpendicular overhead shot looking straight down at {subject_detail} "
            "across {location_detail}, NO horizon line visible, terrain fills 100% of frame, crisp geometric "
            "military formation pattern, {lighting_key}, deep-focus 35mm cinema lens, {film_lock}."
        ),
        veo_motion_suffix=(
            "slow descending vertical crane from high overhead, geometric formation patterns clear, "
            "perpendicular-down perspective, steady 35mm optical tracking"
        ),
        narrative_function="Terrain geometry, stake-grid or troop formation patterns, strategic overview",
    ),
    ShotClassSpec(
        slot=2,
        code="OTS_DIRTY",
        shot_type="Over-The-Shoulder Dirty Single",
        lens_spec="50mm-85mm",
        angle_spec="shoulder-height asymmetrical dirty single",
        composition_rule=(
            "Foreground shoulder/helmet edge in soft bokeh occupies 25-35% of one frame edge; "
            "sharp middle-distance subject occupies 65-75%; never centered back-of-head silhouette."
        ),
        default_camera_move="slow_push_past_shoulder",
        default_duration_short_sec=2.5,
        default_duration_long_sec=3.8,
        is_non_portrait=True,
        is_medium_portrait=False,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "Over-the-shoulder dirty single on 50mm cinema lens, soft-focus foreground armor shoulder edge "
            "occupying 30% of left frame edge in shallow bokeh, sharp focus beyond on {subject_detail} inside "
            "{location_detail}, {lighting_key}, two-plane spatial depth tension, asymmetrical depth framing, "
            "lips firmly closed, {film_lock}."
        ),
        veo_motion_suffix=(
            "slow 4cm/s push-in past blurred foreground shoulder edge, strong foreground-to-background "
            "parallax separation, sharp focus locked on middle-distance action"
        ),
        narrative_function="Spatial tension, psychological weight, two-plane scene layering",
    ),
    ShotClassSpec(
        slot=3,
        code="MACRO_PROP",
        shot_type="Extreme Macro Tactile Prop Insert",
        lens_spec="100mm-135mm macro",
        angle_spec="table/hand-level 30-60cm macro",
        composition_rule=(
            "Physical object/prop fills 60-80% of frame; 100% bokeh background; anonymous hand/fingers "
            "may touch edge ONLY; ZERO human face or character portrait in frame."
        ),
        default_camera_move="ultra_slow_macro_push_in",
        default_duration_short_sec=2.0,
        default_duration_long_sec=3.0,
        is_non_portrait=True,
        is_medium_portrait=False,
        zero_face_strict=True,
        zero_human_strict=False,
        beluga_template=(
            "Extreme 100mm-135mm f/2.0 macro close-up of {prop_detail} inside {location_detail}, "
            "tactile object fills 75% of frame, razor-thin shallow depth of field with 100% bokeh background, "
            "NO human face visible, NO character portrait, zero facial features in frame, crisp physical "
            "metallurgy/wood/ink/mud surface texture, {lighting_key}, {film_lock}."
        ),
        veo_motion_suffix=(
            "ultra-slow 0.3cm/s macro push-in toward tactile prop detail, subtle physical micro-movement "
            "of water/sparks/ink/fibers, shallow rack focus drift, zero human face"
        ),
        narrative_function="Zero-face physical detail, tactile materiality, immediate action consequence",
    ),
    ShotClassSpec(
        slot=4,
        code="WIDE_ESTABLISHING",
        shot_type="Wide Theater Establishing",
        lens_spec="24mm-35mm anamorphic",
        angle_spec="elevated ridge or river horizon",
        composition_rule="Sweeping geography dominates >=65% of frame; disciplined period formations at true scale.",
        default_camera_move="crane_up",
        default_duration_short_sec=2.8,
        default_duration_long_sec=3.4,
        is_non_portrait=False,
        is_medium_portrait=True,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "Wide 24mm-35mm establishing cinema shot of {location_detail} featuring {subject_detail}, "
            "monumental historical geography and disciplined scale, {lighting_key}, deep-focus clarity, "
            "lips firmly closed, {film_lock}."
        ),
        veo_motion_suffix=(
            "smooth elevated crane rise revealing full geographical corridor and formation scale, "
            "clear-air horizon, steady cinema dolly"
        ),
        narrative_function="Geography, army/fleet scale, environmental context",
    ),
    ShotClassSpec(
        slot=5,
        code="REACTION_MICRO",
        shot_type="Reaction Micro-Acting ECU",
        lens_spec="85mm-135mm f/1.4",
        angle_spec="eye-level extreme ocular close-up",
        composition_rule="Eyes occupy upper-third line with catchlights; forehead-to-chin crop; 100% bokeh; lips closed.",
        default_camera_move="barely_perceptible_ocular_drift",
        default_duration_short_sec=1.6,
        default_duration_long_sec=2.5,
        is_non_portrait=False,
        is_medium_portrait=False,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "Extreme close-up 135mm f/1.4 ocular micro-acting shot of {subject_detail} in {location_detail}, "
            "eyes positioned on upper-third line reflecting crisp torch/daylight catchlights, razor-thin DoF "
            "on iris, 100% warm/cold bokeh background, tense jaw, lips firmly closed, {lighting_key}, {film_lock}."
        ),
        veo_motion_suffix=(
            "near-static 135mm frame with barely perceptible 0.2cm/s drift toward eyes, subtle chest/shoulder "
            "breathing rhythm and iris catchlight shimmer, lips closed"
        ),
        narrative_function="Emotional processing, silent command weight, human cost",
    ),
    ShotClassSpec(
        slot=6,
        code="GROUND_MUD",
        shot_type="Ground-Level Boots-in-Mud / Waterline POV",
        lens_spec="24mm ultra-wide",
        angle_spec="0-30cm ankle or waterline height",
        composition_rule="Mud/water/terrain occupies lower 40% of frame; sandals/hooves/stakes/oars tower upward.",
        default_camera_move="low_tracking_alongside",
        default_duration_short_sec=2.2,
        default_duration_long_sec=3.0,
        is_non_portrait=True,
        is_medium_portrait=False,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "Ground-level 24mm ultra-wide shot at 0-30cm ankle/waterline height pressed into {location_detail}, "
            "churned mud, water ripples, sandals, or ironwood stakes dominating lower 40% of frame while "
            "{subject_detail} towers above in dramatic perspective exaggeration, {lighting_key}, deep focus, {film_lock}."
        ),
        veo_motion_suffix=(
            "low ground-level 24mm tracking at ankle/waterline height, mud and water droplets splashing "
            "near lens, strong perspective parallax against towering hulls or marching columns"
        ),
        narrative_function="Visceral physical immersion, soldier's-eye scale exaggeration, approaching threat",
    ),
    ShotClassSpec(
        slot=7,
        code="TWO_SHOT_BLOCKING",
        shot_type="Two-Shot Spatial Command Blocking",
        lens_spec="50mm",
        angle_spec="180-degree profile or diagonal spatial blocking",
        composition_rule="Two opposing or coordinating figures staged in depth across lateral axis; zero flat front mugshot.",
        default_camera_move="truck_lateral",
        default_duration_short_sec=2.6,
        default_duration_long_sec=3.2,
        is_non_portrait=False,
        is_medium_portrait=True,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "50mm lateral spatial blocking shot staging {subject_detail} in multi-plane depth inside "
            "{location_detail}, crisp 180-degree dramatic axis tension, {lighting_key}, lips firmly closed, {film_lock}."
        ),
        veo_motion_suffix=(
            "controlled lateral 50mm dolly tracking across spatial blocking axis, natural multi-plane parallax, "
            "lips closed in silent physical gesture"
        ),
        narrative_function="Tactical coordination, council confrontation, spatial blocking",
    ),
    ShotClassSpec(
        slot=8,
        code="ENV_SENSORY",
        shot_type="Environmental Sensory B-Roll",
        lens_spec="35mm-85mm",
        angle_spec="selective-focus architectural or riverine surface",
        composition_rule="ZERO human figures anywhere in frame; pure natural forces (rain, tide, wind, embers) fill 70-100%.",
        default_camera_move="static_contemplative_hold",
        default_duration_short_sec=2.0,
        default_duration_long_sec=3.5,
        is_non_portrait=True,
        is_medium_portrait=False,
        zero_face_strict=True,
        zero_human_strict=True,
        beluga_template=(
            "Pure environmental sensory B-roll of {env_detail} at {location_detail}, NO human figures visible "
            "anywhere in frame, zero people, zero faces, organic natural movement of water currents, monsoon "
            "rain on terracotta tiles, wind, or dying embers filling 80% of composition, {lighting_key}, "
            "selective 50mm-85mm texture focus, {film_lock}."
        ),
        veo_motion_suffix=(
            "contemplative steady hold with organic natural motion of rain, river tide eddies, wind, or "
            "ember smoke ONLY, zero human figures entering frame"
        ),
        narrative_function="Breathing beat, temporal transition, sensory atmosphere between intense cuts",
    ),
    ShotClassSpec(
        slot=9,
        code="LOW_HERO_SCALE",
        shot_type="Low-Angle Monumental Scale",
        lens_spec="18mm-35mm",
        angle_spec="low upward angle against sky or timber eaves",
        composition_rule="Camera looks upward at 25-40° framing monumental architecture, war hulls, or vanguard banner.",
        default_camera_move="push_in",
        default_duration_short_sec=2.4,
        default_duration_long_sec=3.1,
        is_non_portrait=False,
        is_medium_portrait=True,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "Low-angle 28mm upward cinema shot framing {subject_detail} towering against {location_detail}, "
            "monumental architectural and historical gravity, three-quarter front-diagonal angle, {lighting_key}, "
            "lips firmly closed, {film_lock}."
        ),
        veo_motion_suffix=(
            "deliberate low-angle dolly push-in emphasizing vertical monumental scale and wind motion "
            "across plain unmarked banners"
        ),
        narrative_function="Monumental authority, citadel/hull scale, decisive turning point",
    ),
    ShotClassSpec(
        slot=10,
        code="TRACKING_STEADICAM",
        shot_type="Continuous Ground Steadicam Glide",
        lens_spec="35mm-40mm",
        angle_spec="human eye/chest height lateral or forward follow",
        composition_rule="40mm spherical Steadicam pacing alongside moving column, wharf, or corridor; side-three-quarter angle.",
        default_camera_move="tracking_alongside",
        default_duration_short_sec=2.8,
        default_duration_long_sec=3.4,
        is_non_portrait=False,
        is_medium_portrait=False,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "Fluid 40mm spherical Steadicam side-three-quarter tracking shot moving alongside {subject_detail} "
            "through {location_detail}, immersive human-scale kinetic depth, {lighting_key}, "
            "lips firmly closed, {film_lock}."
        ),
        veo_motion_suffix=(
            "unbroken 40mm Steadicam lateral-forward glide pacing alongside subject movement, foreground "
            "pillars/trees passing cleanly for kinetic depth"
        ),
        narrative_function="Living-world immersion, forced-march momentum, unbroken spatial continuity",
    ),
    ShotClassSpec(
        slot=11,
        code="DUTCH_CHAOS_IMPACT",
        shot_type="Kinetic Impact & Collision Detail",
        lens_spec="28mm-85mm",
        angle_spec="12° canted kinetic impact plane",
        composition_rule="High-energy physical collision — hull hitting ironwood stake, shield brace, volley impact.",
        default_camera_move="hard_impact_track",
        default_duration_short_sec=1.8,
        default_duration_long_sec=2.4,
        is_non_portrait=False,
        is_medium_portrait=False,
        zero_face_strict=False,
        zero_human_strict=False,
        beluga_template=(
            "High-shutter 45-degree kinetic combat collision shot on 50mm-85mm cinema lens capturing "
            "{subject_detail} clashing inside {location_detail}, flying wood splinters, water spray, and "
            "forged iron sparks in crisp focus, {lighting_key}, lips firmly closed, {film_lock}."
        ),
        veo_motion_suffix=(
            "urgent kinetic tracking into physical impact moment, flying wood/water/spark physics, "
            "crisp shutter clarity without motion mud"
        ),
        narrative_function="Climactic physical collision, ambush eruption, kinetic shock",
    ),
    ShotClassSpec(
        slot=12,
        code="EDITORIAL_STAGE_CUTAWAY",
        shot_type="30fps Zero-Box Analytical Stage Cutaway",
        lens_spec="35mm-Ortho / GIS-v9",
        angle_spec="90° tabletop / shaded relief / cross-section plane",
        composition_rule=(
            "Dedicated non-actor analytical cutaway (Slow Giant-Type Map V9, dark-ironwood coroner desk, "
            "2px bronze diptych, weapon cross-section, or Dó-paper folio); ZERO dark HUD pills or VS boxes."
        ),
        default_camera_move="slow_zenital_push",
        default_duration_short_sec=4.5,
        default_duration_long_sec=8.5,
        is_non_portrait=True,
        is_medium_portrait=False,
        zero_face_strict=True,
        zero_human_strict=True,
        beluga_template=(
            "90-degree perpendicular overhead documentary analytical plate of {prop_detail} across "
            "{location_detail}, >=60% calm negative space, NO human face, NO human figures, crisp museum-grade "
            "topographic/wood/Dó-paper materiality, {lighting_key}, {film_lock}."
        ),
        veo_motion_suffix=(
            "smooth deterministic 30fps float32 camera glide across analytical stage, zero integer jitter, "
            "zero smoke transitions"
        ),
        narrative_function="Cartographic maneuver, forensic timeline proof, physics cross-section breakdown",
    ),
)

SHOT_CLASS_REGISTRY: dict[str, ShotClassSpec] = {spec.code: spec for spec in CAMERA_COVERAGE_MATRIX_12_SLOT}


# ---------------------------------------------------------------------------
# 6 Multi-Shot Scene Coverage Formulas (04_live_action_shot_coverage)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoverageFormulaSlot:
    slot: int
    shot_class: str
    duration_short_sec: float
    duration_long_sec: float
    description: str


@dataclass(frozen=True)
class MultiShotCoverageFormula:
    formula_id: str
    formula_code: str
    name: str
    purpose: str
    narrative_function: str
    slots: tuple[CoverageFormulaSlot, ...]

    @property
    def total_short_duration_sec(self) -> float:
        return round(sum(s.duration_short_sec for s in self.slots), 2)

    @property
    def total_long_duration_sec(self) -> float:
        return round(sum(s.duration_long_sec for s in self.slots), 2)

    def to_dict(self) -> dict[str, Any]:
        raw = asdict(self)
        raw["total_short_duration_sec"] = self.total_short_duration_sec
        raw["total_long_duration_sec"] = self.total_long_duration_sec
        return raw


MULTI_SHOT_COVERAGE_FORMULAS: dict[str, MultiShotCoverageFormula] = {
    "command_decision": MultiShotCoverageFormula(
        formula_id="command_decision",
        formula_code="formula_A",
        name="Command Decision",
        purpose="Cover a commander receiving intelligence and locking a decisive tactical order",
        narrative_function="Establishing -> Blocking -> Reaction -> Consequence",
        slots=(
            CoverageFormulaSlot(1, "GODS_EYE", 3.0, 3.5, "Overhead troop/terrain layout establishing tactical problem"),
            CoverageFormulaSlot(2, "OTS_DIRTY", 2.5, 3.0, "OTS past scout's blurred shoulder to command tent briefing"),
            CoverageFormulaSlot(3, "REACTION_MICRO", 1.5, 2.2, "135mm ECU commander's eyes processing intelligence"),
            CoverageFormulaSlot(4, "MACRO_PROP", 2.0, 2.8, "100mm zero-face macro: cinnabar seal pressed onto deployment order"),
        ),
    ),
    "ambush_eruption": MultiShotCoverageFormula(
        formula_id="ambush_eruption",
        formula_code="formula_B",
        name="Ambush Eruption",
        purpose="Cover the eerie calm immediately before and during a sudden ambush strike",
        narrative_function="Establishing -> Blocking -> Tactile Insert -> Consequence -> Analytical Cut",
        slots=(
            CoverageFormulaSlot(1, "ENV_SENSORY", 2.5, 3.0, "Zero-human river surface eddies and rustling reed silence"),
            CoverageFormulaSlot(2, "GROUND_MUD", 2.0, 2.5, "Ankle-height sandals/hooves bursting through mud"),
            CoverageFormulaSlot(3, "MACRO_PROP", 1.5, 2.2, "100mm zero-face macro: bronze crossbow trigger snapping"),
            CoverageFormulaSlot(4, "REACTION_MICRO", 1.5, 2.2, "135mm ECU opposing vanguard eyes registering shock"),
            CoverageFormulaSlot(5, "GODS_EYE", 3.0, 3.5, "90-degree overhead ambush encirclement geometry revealed"),
        ),
    ),
    "forensic_evidence": MultiShotCoverageFormula(
        formula_id="forensic_evidence",
        formula_code="formula_C",
        name="Forensic Evidence",
        purpose="Cover discovery and timeline cross-examination of a primary chronicle or physical clue",
        narrative_function="Spatial Context -> Tactile Evidence -> Emotional Impact -> Breathing Beat",
        slots=(
            CoverageFormulaSlot(1, "OTS_DIRTY", 3.0, 3.2, "OTS past witness shoulder toward Dó-paper folio on dark wood"),
            CoverageFormulaSlot(2, "MACRO_PROP", 3.5, 3.4, "100mm zero-face macro: wet ink characters & imperial wax seal"),
            CoverageFormulaSlot(3, "REACTION_MICRO", 2.0, 2.4, "135mm ECU investigator/scribe eyes widening in candlelight"),
            CoverageFormulaSlot(4, "ENV_SENSORY", 2.0, 3.0, "Zero-human beeswax candle flame & rain on palace roof tiles"),
        ),
    ),
    "battle_impact": MultiShotCoverageFormula(
        formula_id="battle_impact",
        formula_code="formula_D",
        name="Battle Impact",
        purpose="Cover the climactic physical collision of naval or infantry forces",
        narrative_function="Ground-Level Chaos -> Spatial Tension -> Tactile Impact -> Human Cost -> Strategic Consequence",
        slots=(
            CoverageFormulaSlot(1, "GROUND_MUD", 2.0, 2.5, "24mm ground/waterline spray under charging boots or oars"),
            CoverageFormulaSlot(2, "OTS_DIRTY", 2.0, 2.6, "50mm dirty OTS behind shield-wall facing incoming wave"),
            CoverageFormulaSlot(3, "MACRO_PROP", 1.5, 2.2, "100mm zero-face macro: iron-capped lim stake shearing oak hull"),
            CoverageFormulaSlot(4, "REACTION_MICRO", 1.5, 2.2, "135mm ECU combatant's breathless eyes amid torch sparks"),
            CoverageFormulaSlot(5, "GODS_EYE", 3.0, 3.5, "90-degree overhead shattered formation & burning hulls"),
        ),
    ),
    "time_passage_bridge": MultiShotCoverageFormula(
        formula_id="time_passage_bridge",
        formula_code="formula_E",
        name="Time-Passage Bridge",
        purpose="Bridge elapsed hours, tides, or decades between historical acts without static slides",
        narrative_function="Breathing Beat -> Physical Time Marker -> New Temporal Context",
        slots=(
            CoverageFormulaSlot(1, "ENV_SENSORY", 3.0, 3.4, "Zero-human dusk rain streaming off curved citadel tiles"),
            CoverageFormulaSlot(2, "MACRO_PROP", 2.0, 2.6, "100mm zero-face macro: water-clock drip / tide dropping on stake"),
            CoverageFormulaSlot(3, "ENV_SENSORY", 2.5, 3.2, "Zero-human golden dawn mist lifting over silent estuary"),
        ),
    ),
    "psychological_duel": MultiShotCoverageFormula(
        formula_id="psychological_duel",
        formula_code="formula_F",
        name="Psychological Duel",
        purpose="Cross-cut two opposing commanders' mind games across warm vs cold lighting axes",
        narrative_function="Intimate A -> Tactile A -> Counter B -> Tactile B -> Spatial Confrontation -> Strategic Overview",
        slots=(
            CoverageFormulaSlot(1, "REACTION_MICRO", 2.0, 2.4, "135mm ECU Commander A eyes in warm Caravaggio torchlight"),
            CoverageFormulaSlot(2, "MACRO_PROP", 1.5, 2.0, "100mm zero-face macro: wooden command tally placed on map"),
            CoverageFormulaSlot(3, "REACTION_MICRO", 2.0, 2.4, "135mm ECU Commander B eyes in cold steel-blue moonlight"),
            CoverageFormulaSlot(4, "MACRO_PROP", 1.5, 2.0, "100mm zero-face macro: gauntleted fingers tightening on saber hilt"),
            CoverageFormulaSlot(5, "OTS_DIRTY", 2.5, 3.0, "50mm dirty OTS framing opposing fleet/camp across water"),
            CoverageFormulaSlot(6, "GODS_EYE", 3.0, 3.4, "90-degree overhead opposing formations converging into trap"),
        ),
    ),
}

_FORMULA_LOOKUP: dict[str, str] = {}
for _fid, _fobj in MULTI_SHOT_COVERAGE_FORMULAS.items():
    _FORMULA_LOOKUP[_fid.lower()] = _fid
    _FORMULA_LOOKUP[_fobj.formula_code.lower()] = _fid
    _FORMULA_LOOKUP[re.sub(r"[^a-z0-9]+", "_", _fobj.name.lower()).strip("_")] = _fid


# ---------------------------------------------------------------------------
# Named-Character & Portrait Sanitizer for Zero-Face / Zero-Human Shots
# ---------------------------------------------------------------------------

_NAMED_HISTORICAL_PERSONAGES: tuple[str, ...] = (
    "Hưng Đạo Đại Vương Trần Quốc Tuấn",
    "Bảo Nghĩa Vương Trần Bình Trọng",
    "Nhân Huệ Vương Trần Khánh Dư",
    "Trần Quốc Tuấn",
    "Hưng Đạo Vương",
    "Trần Bình Trọng",
    "Trần Khánh Dư",
    "Trần Quang Khải",
    "Trần Nhân Tông",
    "Trần Thái Tông",
    "Trần Thủ Độ",
    "Phạm Ngũ Lão",
    "Yết Kiêu",
    "Dã Tượng",
    "Lý Thường Kiệt",
    "Lý Công Uẩn",
    "Lý Thái Tổ",
    "Lý Thánh Tông",
    "Ngô Quyền",
    "Đinh Bộ Lĩnh",
    "Lê Hoàn",
    "Lê Đại Hành",
    "Lê Lợi",
    "Lê Thái Tổ",
    "Lê Thái Tông",
    "Lê Thánh Tông",
    "Nguyễn Trãi",
    "Nguyễn Thị Lộ",
    "Trần Nguyên Hãn",
    "Lưu Nhân Chú",
    "Trần Lựu",
    "Hồ Quý Ly",
    "Hồ Nguyên Trừng",
    "Quang Trung",
    "Nguyễn Huệ",
    "Đào Duy Từ",
    "Ô Mã Nhi",
    "Thoát Hoan",
    "Toa Đô",
    "Quách Quỳ",
    "Triệu Tiết",
    "Liễu Thăng",
    "Vương Thông",
    "Mộc Thạnh",
    "Tôn Sĩ Nghị",
    "Sầm Nghi Đống",
    "Hoằng Tháo",
)

_PORTRAIT_CLAUSE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\[Cast Lock\s*[—\-:][^\]]*\]", re.IGNORECASE),
    re.compile(r"\b(?:close-up|medium|wide|intimate|front-facing|heroic)\s+portrait(?:\s+of\s+(?:expressive\s+|weathered\s+)?face)?\b", re.IGNORECASE),
    re.compile(r"\bportrait(?:\s+of\s+(?:expressive\s+|weathered\s+)?face)?\b", re.IGNORECASE),
    re.compile(r"\b(?:facial\s+expression|expressive\s+eyes|expressive\s+face|weathered\s+face|face\s+of|piercing\s+gaze|fiery\s+gaze|eyes\s+filling\s+upper\s+third|forehead\s+to\s+chin|jaw\s+clenching|lips\s+firmly\s+closed|lips\s+closed|closed\s+mouths?)\b", re.IGNORECASE),
    re.compile(r"\b(?:chiến\s+binh\s+và\s+tướng\s+lĩnh|tướng\s+lĩnh|danh\s+tướng|thống\s+soái|hoàng\s+đế|vua|chiến\s+binh|người\s+lính)\b", re.IGNORECASE),
    re.compile(r"\b(?:heroic\s+|weathered\s+|palace\s+)?(?:warriors?|commanders?|generals?|emperors?|monarchs?|soldiers?|scholars?|courtiers?|scribes?|envoys?|scouts?|guards?|eunuchs?)(?:\s+(?:standing(?:\s+guard)?|looking|gazing|staring|watching|leading))?\b", re.IGNORECASE),
    re.compile(r"\b(?:back-of-head|back\s+of\s+(?:the\s+)?head|rear\s+silhouette|from\s+behind\s+silhouette)(?:\s+silhouette)?\b", re.IGNORECASE),
)

_HUMAN_BODY_PATTERNS_FOR_ENV: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:calloused\s+|weathered\s+|mud-stained\s+|trembling\s+|palace\s+)?(?:hands?|fingers?|fingertips?|knuckles?|"
        r"forearms?|arms?|palms?|shoulders?|boots?|sandals?|people|figures?|persons?|humans?|troops?|armies|army|"
        r"crowds?|silhouettes?|soldiers?|warriors?|commanders?|generals?|guards?|scribes?|scholars?|eunuchs?|"
        r"monarchs?|emperors?|courtiers?|envoys?|scouts?)(?:\s+standing(?:\s+guard)?)?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:bàn\s+tay|ngón\s+tay|cánh\s+tay|bờ\s+vai|bước\s+chân|đoàn\s+quân|binh\s+sĩ|lính\s+gác|người)\b", re.IGNORECASE),
)

_BACK_OF_HEAD_BAN_REGEX = re.compile(
    r"\b(?:back-of-head|back\s+of\s+(?:the\s+)?head|rear\s+back-of-head|centered\s+rear\s+silhouette|from\s+behind\s+silhouette)\b",
    re.IGNORECASE,
)

_DEFAULT_TACTILE_PROPS: tuple[str, ...] = (
    "iron-capped ironwood river stake glistening with dark estuarine mud and wood shavings",
    "carved imperial cinnabar seal pressing into wet vermilion wax on aged Dó-paper chronicle",
    "cast-bronze crossbow trigger mechanism locking a feathered iron bolt under tension",
    "pine-soot ink brush tip tracing wet characters across fibrous mulberry parchment",
    "rain droplets streaming down lacquered iron lamellar armor plates tied with hemp cord",
    "burning pitch-soaked reed fuse scattering orange sparks across wet timber plank",
)

_DEFAULT_ENV_DETAILS: tuple[str, ...] = (
    "monsoon rain streaming off curved ancient terracotta palace roof tiles at night",
    "ebbing river tide current swirling in dark eddies around half-submerged ironwood stakes at dawn",
    "thin curls of ember smoke rising from an extinguished watchfire over wet riverbank stones",
    "morning wind rippling an unmarked crimson silk battle pennant against limestone karst cliffs",
)


def normalize_shot_class(raw_code: str | None) -> str:
    """Normalize any V12, research, or legacy shot class string to one of the 12 canonical codes."""
    cleaned = re.sub(r"[^A-Z0-9]+", "_", str(raw_code or "").strip().upper()).strip("_")
    if cleaned in SHOT_CLASS_ALIASES:
        return SHOT_CLASS_ALIASES[cleaned]
    if "MACRO" in cleaned or "PROP" in cleaned or "TACTILE" in cleaned:
        return "MACRO_PROP"
    if "OTS" in cleaned or "SHOULDER" in cleaned:
        return "OTS_DIRTY"
    if "MUD" in cleaned or "GROUND" in cleaned or "WATERLINE" in cleaned or "SUBMERGED" in cleaned:
        return "GROUND_MUD"
    if "GOD" in cleaned or "OVERHEAD" in cleaned or "90" in cleaned or "BIRD" in cleaned:
        return "GODS_EYE"
    if "REACTION" in cleaned or "OCULAR" in cleaned or "ECU" in cleaned or "135MM" in cleaned:
        return "REACTION_MICRO"
    if "ENV" in cleaned or "BROLL" in cleaned or "SENSORY" in cleaned:
        return "ENV_SENSORY"
    if "CUTAWAY" in cleaned or "MAP" in cleaned or "TABLETOP" in cleaned or "CROSS_SECTION" in cleaned:
        return "EDITORIAL_STAGE_CUTAWAY"
    if "STEADICAM" in cleaned or "TRACKING" in cleaned:
        return "TRACKING_STEADICAM"
    if "DUTCH" in cleaned or "IMPACT" in cleaned or "ACTION" in cleaned:
        return "DUTCH_CHAOS_IMPACT"
    if "LOW" in cleaned or "HERO" in cleaned or "WORM" in cleaned:
        return "LOW_HERO_SCALE"
    if "TWO_SHOT" in cleaned or "BLOCKING" in cleaned or "MEDIUM" in cleaned:
        return "TWO_SHOT_BLOCKING"
    return "WIDE_ESTABLISHING"


def get_shot_class_spec(shot_class: str) -> ShotClassSpec:
    """Return the `ShotClassSpec` for a canonical or aliased shot class."""
    return SHOT_CLASS_REGISTRY[normalize_shot_class(shot_class)]


def scrub_back_of_head_silhouettes(text: str) -> str:
    """Remove repetitive centered rear back-of-head silhouette phrasing from prompts."""
    cleaned = _BACK_OF_HEAD_BAN_REGEX.sub("asymmetrical side-three-quarter depth framing", str(text or ""))
    return re.sub(r"\s{2,}", " ", cleaned).strip(" ,.;")


def strip_character_portraits_from_prompt(
    raw_text: str,
    *,
    zero_human: bool = False,
    fallback_index: int = 0,
) -> str:
    """Strip named human character portraits and full-face clauses for `MACRO_PROP` / `ENV_SENSORY`.

    When `zero_human=False` (`MACRO_PROP`), strips named characters, `[Cast Lock — ...]`,
    full-body warrior descriptions, and facial portrait cues so Flow BELUGA focuses 100% on
    the physical prop/tactile surface.
    When `zero_human=True` (`ENV_SENSORY`), also strips hands, fingers, soldiers, and any
    human body references so Flow BELUGA renders pure zero-human environmental B-roll.
    """
    text = str(raw_text or "")
    for name in sorted(_NAMED_HISTORICAL_PERSONAGES, key=len, reverse=True):
        text = re.sub(re.escape(name), "", text, flags=re.IGNORECASE)

    for pat in _PORTRAIT_CLAUSE_PATTERNS:
        text = pat.sub("", text)

    if zero_human:
        for h_pat in _HUMAN_BODY_PATTERNS_FOR_ENV:
            text = h_pat.sub("", text)

    # Clean orphaned connectors and punctuation
    text = re.sub(r"^(?:\s*(?:and|with|by|of|holding|wearing|facing)\b\s*)+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:of|with|by|for|and|wearing|holding|facing|on)\s*(?=[,.;]|$)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*[,;:]\s*[,;:]+", ", ", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" ,.;:-—")

    # If the caller only supplied a person description (leaving < 12 meaningful chars), provide period prop/env
    alpha_chars = re.sub(r"[^A-Za-zÀ-ỹ0-9]", "", text)
    if len(alpha_chars) < 12:
        if zero_human:
            return _DEFAULT_ENV_DETAILS[fallback_index % len(_DEFAULT_ENV_DETAILS)]
        return _DEFAULT_TACTILE_PROPS[fallback_index % len(_DEFAULT_TACTILE_PROPS)]
    return text


# ---------------------------------------------------------------------------
# Dual-Model Prompt Compiler (BELUGA + veo_3_1_lite Seam + macaron_cookie)
# ---------------------------------------------------------------------------


def compile_v12_coverage_prompts(
    *,
    shot_class: str,
    subject_or_prop: str,
    location: str,
    lighting_key: str = "dramatic Caravaggio torchlight and directional dawn chiaroscuro",
    film_lock: str | None = None,
    format_profile: FormatProfile = "short_9x16",
    next_shot_class: str | None = None,
    next_subject_hint: str | None = None,
    prefer_frame_link: bool = False,
    beat_index: int = 0,
) -> dict[str, Any]:
    """Compile BELUGA image + `veo_3_1_lite` Seam + `macaron_cookie` Frame-Link prompts for a beat."""
    canon_class = normalize_shot_class(shot_class)
    spec = SHOT_CLASS_REGISTRY[canon_class]
    resolved_lock = (
        film_lock.strip().rstrip(".")
        if film_lock and film_lock.strip()
        else (DEFAULT_FILM_LOCK_9X16 if format_profile == "short_9x16" else DEFAULT_FILM_LOCK_16X9)
    )

    clean_loc = scrub_back_of_head_silhouettes(location or "period-accurate Đại Việt riverine terrain")
    if spec.zero_human_strict:
        clean_loc = strip_character_portraits_from_prompt(
            clean_loc, zero_human=True, fallback_index=beat_index
        )
        env_detail = strip_character_portraits_from_prompt(
            subject_or_prop, zero_human=True, fallback_index=beat_index
        )
        prop_detail = env_detail
        subj_detail = env_detail
    elif spec.zero_face_strict:
        prop_detail = strip_character_portraits_from_prompt(
            subject_or_prop, zero_human=False, fallback_index=beat_index
        )
        if canon_class == "GODS_EYE":
            # Overhead formations can show tiny distant geometric troop formations without portrait faces
            subj_detail = scrub_back_of_head_silhouettes(
                re.sub(r"\[Cast Lock\s*[—\-:][^\]]*\]", "", str(subject_or_prop or "disciplined Đại Việt formation"))
            ).strip() or prop_detail
        else:
            subj_detail = prop_detail
        env_detail = prop_detail
    else:
        subj_detail = scrub_back_of_head_silhouettes(
            subject_or_prop or "period-accurate Đại Việt vanguard in lacquered lamellar armor"
        )
        prop_detail = subj_detail
        env_detail = clean_loc

    beluga_prompt = spec.beluga_template.format(
        subject_detail=subj_detail,
        prop_detail=prop_detail,
        env_detail=env_detail,
        location_detail=clean_loc,
        lighting_key=lighting_key,
        film_lock=resolved_lock,
    )
    beluga_prompt = re.sub(r"\s{2,}", " ", beluga_prompt).strip()

    # Veo 3.1 Lite 10c Seam prompt (start_frame only)
    focal_anchor = prop_detail if spec.zero_face_strict else subj_detail
    veo_seam_prompt = (
        f"{spec.shot_type} ({spec.lens_spec}) at {clean_loc}: {focal_anchor}; "
        f"{spec.veo_motion_suffix}; zero text, zero watermarks."
    )
    veo_seam_prompt = re.sub(r"\s{2,}", " ", veo_seam_prompt).strip()

    # macaron_cookie Omni 1.2 Flash Frame-Link prompt (start_frame -> end_frame continuous chain)
    next_canon = normalize_shot_class(next_shot_class) if next_shot_class else canon_class
    next_spec = SHOT_CLASS_REGISTRY[next_canon]
    next_desc = (
        strip_character_portraits_from_prompt(next_subject_hint or focal_anchor, zero_human=next_spec.zero_human_strict, fallback_index=beat_index + 1)
        if next_spec.zero_face_strict
        else scrub_back_of_head_silhouettes(next_subject_hint or focal_anchor)
    )
    macaron_frame_link_prompt = (
        f"Seamless 2-frame continuous cinema motion from {spec.shot_type} ({focal_anchor}) "
        f"into {next_spec.shot_type} ({next_desc}) inside {clean_loc}, preserving exact lighting "
        f"temperature and spatial geography across frames, zero smoke/fog wipes, zero text."
    )
    macaron_frame_link_prompt = re.sub(r"\s{2,}", " ", macaron_frame_link_prompt).strip()

    recommended_model = "macaron_cookie" if prefer_frame_link else "veo_3_1_lite"
    return {
        "shot_class": canon_class,
        "shot_type": spec.shot_type,
        "lens_mm": spec.lens_spec,
        "camera_move": spec.default_camera_move,
        "is_non_portrait": spec.is_non_portrait,
        "zero_face_enforced": spec.zero_face_strict,
        "zero_human_enforced": spec.zero_human_strict,
        "allowed_text": None,
        "recommended_video_model": recommended_model,
        "beluga_image_prompt": beluga_prompt,
        "veo_3_1_lite_seam_prompt": veo_seam_prompt,
        "macaron_cookie_frame_link_prompt": macaron_frame_link_prompt,
    }


def resolve_coverage_formula(formula_key: str) -> MultiShotCoverageFormula:
    """Resolve one of the 6 V12 Multi-Shot Coverage Formulas by ID, code, or title."""
    norm = re.sub(r"[^a-z0-9]+", "_", str(formula_key or "").strip().lower()).strip("_")
    if norm in _FORMULA_LOOKUP:
        return MULTI_SHOT_COVERAGE_FORMULAS[_FORMULA_LOOKUP[norm]]
    for cand_norm, fid in _FORMULA_LOOKUP.items():
        if norm and (norm in cand_norm or cand_norm in norm):
            return MULTI_SHOT_COVERAGE_FORMULAS[fid]
    raise KeyError(
        f"Unknown coverage formula {formula_key!r}; expected one of {tuple(MULTI_SHOT_COVERAGE_FORMULAS.keys())}"
    )


def expand_multi_shot_formula(
    formula_key: str,
    *,
    subject: str = "Đại Việt river vanguard in lacquered lamellar armor",
    prop: str = "iron-tipped ironwood river stake & bronze command seal",
    location: str = "Bạch Đằng tidal estuary at dawn",
    lighting_key: str = "dramatic directional dawn sunlight and warm torchlight",
    film_lock: str | None = None,
    format_profile: FormatProfile = "short_9x16",
    start_sec: float = 0.0,
    beat_id_prefix: str = "B",
    start_index: int = 0,
) -> list[dict[str, Any]]:
    """Expand a Multi-Shot Coverage Formula into compiled V12 beat dicts."""
    formula = resolve_coverage_formula(formula_key)
    beats_out: list[dict[str, Any]] = []
    cur_t = float(start_sec)
    n_slots = len(formula.slots)

    for idx, slot in enumerate(formula.slots):
        dur = slot.duration_short_sec if format_profile == "short_9x16" else slot.duration_long_sec
        next_slot = formula.slots[idx + 1] if idx + 1 < n_slots else None
        is_macro_or_env = slot.shot_class in ("MACRO_PROP", "ENV_SENSORY")
        subj_input = prop if slot.shot_class == "MACRO_PROP" else (slot.description if is_macro_or_env else subject)
        use_fl = idx < n_slots - 1 and slot.shot_class != "ENV_SENSORY"

        compiled = compile_v12_coverage_prompts(
            shot_class=slot.shot_class,
            subject_or_prop=subj_input,
            location=location,
            lighting_key=lighting_key,
            film_lock=film_lock,
            format_profile=format_profile,
            next_shot_class=next_slot.shot_class if next_slot else None,
            next_subject_hint=next_slot.description if next_slot else None,
            prefer_frame_link=use_fl,
            beat_index=start_index + idx,
        )
        b_idx = start_index + idx
        b_id = f"{beat_id_prefix}{b_idx:02d}" if format_profile == "short_9x16" else f"{beat_id_prefix}{b_idx:03d}"
        b_start = round(cur_t, 2)
        b_end = round(cur_t + dur, 2)
        cur_t = b_end

        beats_out.append({
            "beat_index": b_idx,
            "beat_id": b_id,
            "id": b_id,
            "formula_id": formula.formula_id,
            "formula_name": formula.name,
            "formula_slot": slot.slot,
            "shot_class": compiled["shot_class"],
            "shot_type": compiled["shot_type"],
            "lens_mm": compiled["lens_mm"],
            "camera_move": compiled["camera_move"],
            "is_non_portrait": compiled["is_non_portrait"],
            "duration_sec": dur,
            "duration": dur,
            "start_sec": b_start,
            "end_sec": b_end,
            "allowed_text": None,
            "video_model": compiled["recommended_video_model"],
            "prompt": compiled["beluga_image_prompt"],
            "motion_prompt": (
                compiled["macaron_cookie_frame_link_prompt"]
                if use_fl
                else compiled["veo_3_1_lite_seam_prompt"]
            ),
            "veo_seam_prompt": compiled["veo_3_1_lite_seam_prompt"],
            "frame_link_prompt": compiled["macaron_cookie_frame_link_prompt"],
            "narrative_desc": slot.description,
        })
    return beats_out


# ---------------------------------------------------------------------------
# 12-Slot Coverage Sequence Planner & Repair Engine
# ---------------------------------------------------------------------------

DEFAULT_SHORT_20BEAT_COVERAGE: tuple[str, ...] = (
    "MACRO_PROP",
    "LOW_HERO_SCALE",
    "OTS_DIRTY",
    "GROUND_MUD",
    "REACTION_MICRO",
    "WIDE_ESTABLISHING",
    "MACRO_PROP",
    "DUTCH_CHAOS_IMPACT",
    "EDITORIAL_STAGE_CUTAWAY",
    "GODS_EYE",
    "TWO_SHOT_BLOCKING",
    "MACRO_PROP",
    "REACTION_MICRO",
    "ENV_SENSORY",
    "TRACKING_STEADICAM",
    "OTS_DIRTY",
    "DUTCH_CHAOS_IMPACT",
    "MACRO_PROP",
    "GODS_EYE",
    "WIDE_ESTABLISHING",
)

DEFAULT_LONG_CHAPTER_COVERAGE_CYCLE: tuple[str, ...] = (
    "WIDE_ESTABLISHING",
    "OTS_DIRTY",
    "MACRO_PROP",
    "REACTION_MICRO",
    "GROUND_MUD",
    "DUTCH_CHAOS_IMPACT",
    "GODS_EYE",
    "MACRO_PROP",
    "TWO_SHOT_BLOCKING",
    "ENV_SENSORY",
    "TRACKING_STEADICAM",
    "MACRO_PROP",
    "EDITORIAL_STAGE_CUTAWAY",
    "LOW_HERO_SCALE",
    "OTS_DIRTY",
    "REACTION_MICRO",
)


def _select_deterministic_shot_sequence(
    n_beats: int,
    format_profile: FormatProfile,
    preferred_sequence: list[str] | tuple[str, ...] | None = None,
) -> list[str]:
    """Build a coverage-compliant sequence of `n_beats` shot classes with 0 portrait runs >= 3."""
    if n_beats <= 0:
        return []

    base = (
        [normalize_shot_class(c) for c in preferred_sequence]
        if preferred_sequence
        else list(
            DEFAULT_SHORT_20BEAT_COVERAGE
            if format_profile == "short_9x16"
            else DEFAULT_LONG_CHAPTER_COVERAGE_CYCLE
        )
    )
    seq = [base[i % len(base)] for i in range(n_beats)]

    # Break any >= 3 consecutive medium portraits deterministically
    run_len = 0
    non_portrait_cycle = ("MACRO_PROP", "OTS_DIRTY", "GROUND_MUD", "GODS_EYE", "ENV_SENSORY")
    np_cursor = 0
    for i, sc in enumerate(seq):
        if sc in MEDIUM_PORTRAIT_SHOT_CLASSES:
            run_len += 1
            if run_len >= 3:
                replacement = non_portrait_cycle[np_cursor % len(non_portrait_cycle)]
                if i > 0 and seq[i - 1] == replacement:
                    replacement = non_portrait_cycle[(np_cursor + 1) % len(non_portrait_cycle)]
                seq[i] = replacement
                np_cursor += 1
                run_len = 0
        else:
            run_len = 0

    # Enforce Long >= 15% MACRO_PROP (aim >= 18% safety margin)
    if format_profile == "long_16x9":
        min_macro = max(1, int((n_beats * 0.18) + 0.999))
        cur_macro = sum(1 for c in seq if c == "MACRO_PROP")
        idx = 2
        while cur_macro < min_macro and idx < n_beats:
            if seq[idx] != "MACRO_PROP" and seq[idx] != "EDITORIAL_STAGE_CUTAWAY":
                prev_ok = idx == 0 or seq[idx - 1] != "MACRO_PROP"
                next_ok = idx == n_beats - 1 or seq[idx + 1] != "MACRO_PROP"
                if prev_ok and next_ok:
                    seq[idx] = "MACRO_PROP"
                    cur_macro += 1
            idx += 3
        # Fallback pass if stride-3 couldn't place enough on tiny beat arrays
        for idx2 in range(n_beats):
            if cur_macro >= min_macro:
                break
            if seq[idx2] not in ("MACRO_PROP", "EDITORIAL_STAGE_CUTAWAY"):
                seq[idx2] = "MACRO_PROP"
                cur_macro += 1

    # Enforce Short >= 30% non-portrait (aim >= 40% safety margin) + MACRO_PROP & ENV_SENSORY presence
    else:
        min_np = max(1, int((n_beats * 0.40) + 0.999))
        cur_np = sum(1 for c in seq if c in NON_PORTRAIT_SHOT_CLASSES)
        idx = 0
        while cur_np < min_np and idx < n_beats:
            if seq[idx] not in NON_PORTRAIT_SHOT_CLASSES:
                seq[idx] = non_portrait_cycle[np_cursor % len(non_portrait_cycle)]
                np_cursor += 1
                cur_np += 1
            idx += 2
        if n_beats >= 6 and "MACRO_PROP" not in seq:
            seq[min(2, n_beats - 1)] = "MACRO_PROP"
        if n_beats >= 8 and "ENV_SENSORY" not in seq:
            seq[min(6, n_beats - 2)] = "ENV_SENSORY"

    return seq


def plan_v12_shot_coverage(
    beats: list[dict[str, Any]],
    *,
    format_profile: FormatProfile = "short_9x16",
    preferred_sequence: list[str] | tuple[str, ...] | None = None,
    film_lock: str | None = None,
    lighting_key: str = "dramatic Caravaggio torchlight and directional dawn chiaroscuro",
) -> list[dict[str, Any]]:
    """Enrich a list of beat dicts in-copy with 12-slot shot coverage & sanitized prompts."""
    planned = copy.deepcopy(beats or [])
    n = len(planned)
    if n == 0:
        return planned

    caller_classes = [
        normalize_shot_class(b.get("shot_class")) if b.get("shot_class") else None
        for b in planned
    ]
    base_seq = _select_deterministic_shot_sequence(
        n,
        format_profile=format_profile,
        preferred_sequence=(
            [c for c in caller_classes if c is not None]
            if all(c is not None for c in caller_classes) and preferred_sequence is None
            else preferred_sequence
        ),
    )

    for idx, beat in enumerate(planned):
        sc = base_seq[idx]
        next_sc = base_seq[idx + 1] if idx + 1 < n else None
        raw_subj = str(
            beat.get("prop_subject")
            or beat.get("hero_subject")
            or beat.get("visual_staging_direction")
            or beat.get("prompt")
            or ""
        )
        raw_loc = str(beat.get("location") or "period-accurate Đại Việt riverine terrain")
        next_hint = (
            str(planned[idx + 1].get("hero_subject") or planned[idx + 1].get("location") or "")
            if idx + 1 < n
            else None
        )
        prefer_fl = str(beat.get("video_model") or "") == "macaron_cookie" or str(
            beat.get("cut_to_next") or ""
        ) == "frame_link_unbroken"

        compiled = compile_v12_coverage_prompts(
            shot_class=sc,
            subject_or_prop=raw_subj,
            location=raw_loc,
            lighting_key=str(beat.get("lighting_key") or lighting_key),
            film_lock=film_lock,
            format_profile=format_profile,
            next_shot_class=next_sc,
            next_subject_hint=next_hint,
            prefer_frame_link=prefer_fl,
            beat_index=idx,
        )
        beat["shot_class"] = compiled["shot_class"]
        beat["shot_type"] = compiled["shot_type"]
        beat["lens_mm"] = compiled["lens_mm"]
        beat["camera_move"] = compiled["camera_move"]
        beat["is_non_portrait"] = compiled["is_non_portrait"]
        beat["allowed_text"] = None
        if str(beat.get("video_model") or "") in DEPRECATED_FLOW_VIDEO_MODELS or not beat.get("video_model"):
            beat["video_model"] = compiled["recommended_video_model"]
        beat["prompt"] = compiled["beluga_image_prompt"]
        beat["motion_prompt"] = (
            compiled["macaron_cookie_frame_link_prompt"]
            if beat["video_model"] == "macaron_cookie"
            else compiled["veo_3_1_lite_seam_prompt"]
        )
        beat["veo_seam_prompt"] = compiled["veo_3_1_lite_seam_prompt"]
        beat["frame_link_prompt"] = compiled["macaron_cookie_frame_link_prompt"]

    return planned


# ---------------------------------------------------------------------------
# Coverage Diversity & Hygiene Validator
# ---------------------------------------------------------------------------

_FACE_PORTRAIT_LEAK_RE = re.compile(
    r"(?:\[Cast Lock\s*[—\-:]|\bclose-up\s+portrait\s+of\b|\bfront-facing\s+portrait\b|"
    r"\bexpressive\s+face\b|\bfire-lit\s+face\b|\beyes\s+filling\s+upper\s+third\b)",
    re.IGNORECASE,
)


def validate_v12_shot_coverage(
    beats_or_spec: list[dict[str, Any]] | dict[str, Any],
    *,
    format_profile: FormatProfile | None = None,
) -> dict[str, Any]:
    """Validate V12 12-Slot Shot Coverage & Zero-Face Hygiene across Short or Long specs."""
    if isinstance(beats_or_spec, dict):
        beats = [b for b in (beats_or_spec.get("beats") or []) if isinstance(b, dict)]
        fmt_raw = str(
            format_profile
            or beats_or_spec.get("format_profile")
            or beats_or_spec.get("format")
            or ("long_16x9" if beats_or_spec.get("aspect_ratio") == "16:9" else "short_9x16")
        )
    else:
        beats = [b for b in (beats_or_spec or []) if isinstance(b, dict)]
        fmt_raw = str(format_profile or "short_9x16")

    fmt: FormatProfile = "long_16x9" if "long" in fmt_raw.lower() or "16x9" in fmt_raw.lower() else "short_9x16"
    total = len(beats)
    violations: list[str] = []
    if total == 0:
        return {
            "passed": False,
            "format_profile": fmt,
            "total_beats": 0,
            "class_counts": {},
            "non_portrait_ratio": 0.0,
            "macro_prop_ratio": 0.0,
            "max_consecutive_medium_portraits": 0,
            "back_of_head_silhouette_count": 0,
            "face_leak_beats": [],
            "deprecated_model_beats": [],
            "violations": ["empty_beats"],
        }

    class_counts: dict[str, int] = {c: 0 for c in V12_SHOT_CLASSES}
    non_portrait_count = 0
    max_consec_portraits = 0
    cur_consec_portraits = 0
    back_of_head_count = 0
    face_leak_beats: list[str] = []
    deprecated_model_beats: list[str] = []

    for idx, b in enumerate(beats):
        bid = str(b.get("beat_id") or b.get("id") or f"B{idx:02d}")
        raw_sc = str(b.get("shot_class") or b.get("shot_type") or "WIDE_ESTABLISHING")
        sc = normalize_shot_class(raw_sc)
        class_counts[sc] = class_counts.get(sc, 0) + 1

        if sc in NON_PORTRAIT_SHOT_CLASSES:
            non_portrait_count += 1

        if sc in MEDIUM_PORTRAIT_SHOT_CLASSES:
            cur_consec_portraits += 1
            max_consec_portraits = max(max_consec_portraits, cur_consec_portraits)
        else:
            cur_consec_portraits = 0

        prompt_txt = str(b.get("prompt") or "")
        motion_txt = str(b.get("motion_prompt") or "")
        combined_txt = f"{prompt_txt} {motion_txt}"

        if _BACK_OF_HEAD_BAN_REGEX.search(combined_txt):
            back_of_head_count += 1

        # Zero-face / zero-human check on MACRO_PROP & ENV_SENSORY
        if sc == "MACRO_PROP":
            has_named_person = any(
                re.search(re.escape(nm), prompt_txt, flags=re.IGNORECASE)
                for nm in _NAMED_HISTORICAL_PERSONAGES
            )
            if _FACE_PORTRAIT_LEAK_RE.search(prompt_txt) or has_named_person or "no human face" not in prompt_txt.lower():
                face_leak_beats.append(bid)
        elif sc == "ENV_SENSORY":
            has_named_person = any(
                re.search(re.escape(nm), prompt_txt, flags=re.IGNORECASE)
                for nm in _NAMED_HISTORICAL_PERSONAGES
            )
            if (
                _FACE_PORTRAIT_LEAK_RE.search(prompt_txt)
                or has_named_person
                or "no human figures" not in prompt_txt.lower()
            ):
                face_leak_beats.append(bid)

        v_model = str(b.get("video_model") or "").strip().lower()
        if v_model in DEPRECATED_FLOW_VIDEO_MODELS:
            deprecated_model_beats.append(bid)

    non_portrait_ratio = round(non_portrait_count / float(total), 4)
    macro_prop_ratio = round(class_counts.get("MACRO_PROP", 0) / float(total), 4)

    if fmt == "short_9x16" and non_portrait_ratio < 0.30:
        violations.append(f"short_non_portrait_ratio_below_30pct:{non_portrait_ratio:.3f}")
    if fmt == "long_16x9":
        if macro_prop_ratio < 0.15:
            violations.append(f"long_macro_prop_ratio_below_15pct:{macro_prop_ratio:.3f}")
        if non_portrait_ratio < 0.30:
            violations.append(f"long_non_portrait_ratio_below_30pct:{non_portrait_ratio:.3f}")

    if max_consec_portraits >= 3:
        violations.append(f"three_or_more_consecutive_medium_portraits:{max_consec_portraits}")
    if back_of_head_count > 0:
        violations.append(f"repetitive_back_of_head_silhouettes:{back_of_head_count}")
    if face_leak_beats:
        violations.append(f"macro_or_env_portrait_leak:{','.join(face_leak_beats[:6])}")
    if deprecated_model_beats:
        violations.append(f"deprecated_flow_models:{','.join(deprecated_model_beats[:6])}")

    return {
        "passed": len(violations) == 0,
        "format_profile": fmt,
        "total_beats": total,
        "class_counts": class_counts,
        "distinct_shot_classes_used": sum(1 for v in class_counts.values() if v > 0),
        "non_portrait_count": non_portrait_count,
        "non_portrait_ratio": non_portrait_ratio,
        "macro_prop_count": class_counts.get("MACRO_PROP", 0),
        "macro_prop_ratio": macro_prop_ratio,
        "max_consecutive_medium_portraits": max_consec_portraits,
        "back_of_head_silhouette_count": back_of_head_count,
        "face_leak_beats": face_leak_beats,
        "deprecated_model_beats": deprecated_model_beats,
        "violations": violations,
    }


__all__ = [
    "ALLOWED_FLOW_VIDEO_MODELS",
    "CAMERA_COVERAGE_MATRIX_12_SLOT",
    "CORE_CINEMA_SHOT_CLASSES",
    "DEFAULT_LONG_CHAPTER_COVERAGE_CYCLE",
    "DEFAULT_SHORT_20BEAT_COVERAGE",
    "DEPRECATED_FLOW_VIDEO_MODELS",
    "MEDIUM_PORTRAIT_SHOT_CLASSES",
    "MISSING_LIVE_ACTION_SHOT_CLASSES",
    "MULTI_SHOT_COVERAGE_FORMULAS",
    "NON_PORTRAIT_SHOT_CLASSES",
    "SHOT_CLASS_ALIASES",
    "SHOT_CLASS_REGISTRY",
    "V12_SHOT_CLASSES",
    "CoverageFormulaSlot",
    "MultiShotCoverageFormula",
    "ShotClassSpec",
    "compile_v12_coverage_prompts",
    "expand_multi_shot_formula",
    "get_shot_class_spec",
    "normalize_shot_class",
    "plan_v12_shot_coverage",
    "resolve_coverage_formula",
    "scrub_back_of_head_silhouettes",
    "strip_character_portraits_from_prompt",
    "validate_v12_shot_coverage",
]
