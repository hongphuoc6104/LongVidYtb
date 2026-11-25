"""35mm Film Stock Optical Grading, Color LUT & Anamorphic Lens FX Compiler (10x10 Styles).

Provides hardware-ready FFmpeg filter chains (validated for Colab Tesla T4 `h264_nvenc`
single-pass and multi-branch `filter_complex` pipelines) AND 32-bit float `numpy`/`PIL`
optical frame processors across all 10 Short (`S01..S10`) and 10 Long (`L01..L10`)
historical cinema styles.

Core Optical & Photochemical Stages:
1. Scene-referred highlight isolation -> 35mm red-emulsion anti-halation scatter +
   subtle Panavision horizontal anamorphic flare whisper (strictly above high specular
   thresholds so midtones and shadows remain 100% haze/fog-free).
2. 3x3 photochemical dye cross-coupling matrix (`colorchannelmixer` / float32 matrix).
3. Selective hue & bipolar faction chroma sculpting (e.g. cold steel + crimson pop on
   `S02`; warm Đại Việt vermilion vs cold Yuan/Ming cobalt-steel on `S07`/`L07`;
   sumi-e cinnabar seal -> golden-hour 35mm bloom on `S10`/`L04`).
4. 3-zone shadow / midtone / highlight split-toning + filmic S-curve with soft highlight
   shoulder roll-off.
5. Optical MTF micro-contrast (`unsharp`), gentle cosine-fourth peripheral vignette, and
   midtone-weighted silver-halide 35mm film grain (`4 * Y * (1 - Y)` — zero black mud).
"""
from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SYS_DIR = Path(__file__).resolve().parents[1]

CINEMA_GRADE_IDS: tuple[str, ...] = (
    "kodak_500t_torch_battle",
    "pov_adrenaline_grit",
    "imperial_cartography_gold",
    "noir_silver_dossier",
    "chronicle_split_contrast",
    "macro_metallurgy_crisp",
    "duel_bipolar_crimson_cobalt",
    "humanist_35mm_natural",
    "chrono_tension_teal_amber",
    "eastern_lacquer_ink_to_cinema",
)

SHORT_STYLE_IDS: tuple[str, ...] = (
    "S01",
    "S02",
    "S03",
    "S04",
    "S05",
    "S06",
    "S07",
    "S08",
    "S09",
    "S10",
)

LONG_STYLE_IDS: tuple[str, ...] = (
    "L01",
    "L02",
    "L03",
    "L04",
    "L05",
    "L06",
    "L07",
    "L08",
    "L09",
    "L10",
)

ALL_20_STYLE_IDS: tuple[str, ...] = SHORT_STYLE_IDS + LONG_STYLE_IDS

CANONICAL_STYLE_NAMES: dict[str, str] = {
    "S01": "S01_PRESTIGE_BATTLE_CINEMA",
    "S02": "S02_POV_TIME_TRAVEL_SURVIVAL",
    "S03": "S03_TACTICAL_MAP_BLITZ",
    "S04": "S04_FORENSIC_MYSTERY_DOSSIER",
    "S05": "S05_MYTH_VS_CHRONICLE_SPLIT",
    "S06": "S06_ANCIENT_TECH_WEAPON_LAB",
    "S07": "S07_COMMANDER_PSYCHOLOGY_DUEL",
    "S08": "S08_MICRO_HISTORY_ORDINARY_EYES",
    "S09": "S09_DOMINO_BUTTERFLY_WHAT_IF",
    "S10": "S10_EASTERN_INK_TO_35MM_LEGEND",
    "L01": "L01_EPIC_CAMPAIGN_CHRONICLE",
    "L02": "L02_DARK_FORENSIC_INVESTIGATION",
    "L03": "L03_GRAND_STRATEGY_WAR_ROOM",
    "L04": "L04_FALL_AND_RISE_DYNASTY_IMMERSION",
    "L05": "L05_REALTIME_COUNTDOWN_CHRONICLE",
    "L06": "L06_EYEWITNESS_PRIMARY_LETTERS",
    "L07": "L07_BIOGRAPHY_OF_IRON_MINDS",
    "L08": "L08_24_HOURS_IN_ANCIENT_DAI_VIET",
    "L09": "L09_GEOPOLITICAL_CHESSBOARD",
    "L10": "L10_MILITARY_ENGINEERING_AUTOPSY",
}

STYLE_TO_GRADE_MAP: dict[str, str] = {
    # 1. kodak_500t_torch_battle (S01, L01)
    "S01": "kodak_500t_torch_battle",
    "L01": "kodak_500t_torch_battle",
    # 2. pov_adrenaline_grit (S02)
    "S02": "pov_adrenaline_grit",
    # 3. imperial_cartography_gold (S03, L03, L09)
    "S03": "imperial_cartography_gold",
    "L03": "imperial_cartography_gold",
    "L09": "imperial_cartography_gold",
    # 4. noir_silver_dossier (S04, L02)
    "S04": "noir_silver_dossier",
    "L02": "noir_silver_dossier",
    # 5. chronicle_split_contrast (S05, L06)
    "S05": "chronicle_split_contrast",
    "L06": "chronicle_split_contrast",
    # 6. macro_metallurgy_crisp (S06, L10)
    "S06": "macro_metallurgy_crisp",
    "L10": "macro_metallurgy_crisp",
    # 7. duel_bipolar_crimson_cobalt (S07, L07)
    "S07": "duel_bipolar_crimson_cobalt",
    "L07": "duel_bipolar_crimson_cobalt",
    # 8. humanist_35mm_natural (S08, L08)
    "S08": "humanist_35mm_natural",
    "L08": "humanist_35mm_natural",
    # 9. chrono_tension_teal_amber (S09, L05)
    "S09": "chrono_tension_teal_amber",
    "L05": "chrono_tension_teal_amber",
    # 10. eastern_lacquer_ink_to_cinema (S10, L04)
    "S10": "eastern_lacquer_ink_to_cinema",
    "L04": "eastern_lacquer_ink_to_cinema",
}


@dataclass(frozen=True)
class OpticalGradeProfile:
    """Complete photochemical & anamorphic lens specification for one cinema LUT."""

    grade_id: str
    title_en: str
    film_stock_lens: str
    era_signature: str
    style_ids: tuple[str, ...]
    # 3x3 RGB dye-coupling matrix (row-sum ~1.0 to preserve neutral exposure)
    rgb_matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    # 3-zone split-toning shifts (rs, gs, bs), (rm, gm, bm), (rh, gh, bh)
    shadow_shift: tuple[float, float, float]
    midtone_shift: tuple[float, float, float]
    highlight_shift: tuple[float, float, float]
    # Tone curve & global saturation
    contrast: float
    gamma: float
    saturation: float
    toe_power: float
    shoulder_rolloff: float
    # FFmpeg master curve control points (strictly monotonic, space-separated)
    ffmpeg_master_curve: str
    # Selective color-science mode ("none", "crimson_pop", "bipolar_duel", "chronicle_state", "lacquer_bloom")
    chroma_mode: str
    # Emulsion halation & anamorphic streak physics
    halation_threshold: float
    halation_strength: float
    halation_tint: tuple[float, float, float]
    anamorphic_streak_strength: float
    anamorphic_tint: tuple[float, float, float]
    # Optical MTF micro-contrast, peripheral vignette & 35mm luma grain
    microcontrast_amount: float
    microcontrast_radius: float
    vignette_strength: float
    ffmpeg_vignette_angle: str | None
    grain_sigma: float
    ffmpeg_luma_noise: int


OPTICAL_GRADE_CATALOG: dict[str, OpticalGradeProfile] = {
    "kodak_500t_torch_battle": OpticalGradeProfile(
        grade_id="kodak_500t_torch_battle",
        title_en="Kodak 500T Torch Battle",
        film_stock_lens="Kodak Vision3 500T 5219 · Panavision C-Series Anamorphic",
        era_signature="Caravaggio warm amber highlights + deep Prussian-indigo shadows",
        style_ids=("S01", "L01"),
        rgb_matrix=(
            (1.05, -0.03, -0.02),
            (-0.01, 1.01, 0.00),
            (-0.04, 0.02, 1.02),
        ),
        shadow_shift=(-0.065, -0.020, 0.095),
        midtone_shift=(0.020, 0.005, -0.020),
        highlight_shift=(0.115, 0.045, -0.085),
        contrast=1.13,
        gamma=0.94,
        saturation=1.12,
        toe_power=1.08,
        shoulder_rolloff=0.26,
        ffmpeg_master_curve="0/0 0.22/0.19 0.52/0.53 0.82/0.86 1/0.99",
        chroma_mode="none",
        halation_threshold=0.74,
        halation_strength=0.22,
        halation_tint=(1.00, 0.42, 0.10),
        anamorphic_streak_strength=0.10,
        anamorphic_tint=(1.00, 0.68, 0.28),
        microcontrast_amount=0.42,
        microcontrast_radius=1.6,
        vignette_strength=0.17,
        ffmpeg_vignette_angle="PI/5.4",
        grain_sigma=0.014,
        ffmpeg_luma_noise=4,
    ),
    "pov_adrenaline_grit": OpticalGradeProfile(
        grade_id="pov_adrenaline_grit",
        title_en="POV Adrenaline Grit",
        film_stock_lens="35mm ENR Silver-Retention Bleach-Bypass · 24mm Subjective Prime",
        era_signature="High-microcontrast desaturated cold steel + crimson blood/fire pop",
        style_ids=("S02",),
        rgb_matrix=(
            (1.06, -0.04, -0.02),
            (0.14, 0.68, 0.18),
            (0.10, 0.18, 0.72),
        ),
        shadow_shift=(-0.055, 0.005, 0.065),
        midtone_shift=(-0.030, 0.005, 0.035),
        highlight_shift=(0.045, -0.010, 0.015),
        contrast=1.20,
        gamma=0.93,
        saturation=0.72,
        toe_power=1.12,
        shoulder_rolloff=0.20,
        ffmpeg_master_curve="0/0 0.20/0.16 0.50/0.51 0.82/0.87 1/0.99",
        chroma_mode="crimson_pop",
        halation_threshold=0.78,
        halation_strength=0.16,
        halation_tint=(1.00, 0.24, 0.08),
        anamorphic_streak_strength=0.06,
        anamorphic_tint=(0.82, 0.90, 1.00),
        microcontrast_amount=0.72,
        microcontrast_radius=1.4,
        vignette_strength=0.22,
        ffmpeg_vignette_angle="PI/4.8",
        grain_sigma=0.018,
        ffmpeg_luma_noise=5,
    ),
    "imperial_cartography_gold": OpticalGradeProfile(
        grade_id="imperial_cartography_gold",
        title_en="Imperial Cartography Gold",
        film_stock_lens="Kodak Vision3 250D 5207 · Zeiss Master Archival Brass",
        era_signature="Warm parchment brass + crisp iron-gall ink contrast",
        style_ids=("S03", "L03", "L09"),
        rgb_matrix=(
            (1.04, 0.02, -0.06),
            (0.01, 1.01, -0.02),
            (-0.04, -0.01, 1.05),
        ),
        shadow_shift=(-0.020, -0.015, -0.010),
        midtone_shift=(0.065, 0.038, -0.065),
        highlight_shift=(0.105, 0.072, -0.085),
        contrast=1.15,
        gamma=0.96,
        saturation=1.04,
        toe_power=1.09,
        shoulder_rolloff=0.22,
        ffmpeg_master_curve="0/0 0.20/0.17 0.52/0.54 0.84/0.88 1/1",
        chroma_mode="none",
        halation_threshold=0.80,
        halation_strength=0.14,
        halation_tint=(1.00, 0.72, 0.24),
        anamorphic_streak_strength=0.0,
        anamorphic_tint=(1.00, 0.80, 0.35),
        microcontrast_amount=0.58,
        microcontrast_radius=1.3,
        vignette_strength=0.10,
        ffmpeg_vignette_angle="PI/6.2",
        grain_sigma=0.010,
        ffmpeg_luma_noise=3,
    ),
    "noir_silver_dossier": OpticalGradeProfile(
        grade_id="noir_silver_dossier",
        title_en="Noir Silver Dossier",
        film_stock_lens="Eastman Double-X / Silver-Gelatin Hybrid · Chiaroscuro 50mm",
        era_signature="Deep chiaroscuro obsidian shadows + candlelit parchment skin tones",
        style_ids=("S04", "L02"),
        rgb_matrix=(
            (0.92, 0.06, 0.02),
            (0.05, 0.90, 0.05),
            (0.03, 0.07, 0.90),
        ),
        shadow_shift=(-0.045, -0.030, 0.045),
        midtone_shift=(0.045, 0.018, -0.038),
        highlight_shift=(0.085, 0.052, -0.045),
        contrast=1.18,
        gamma=0.91,
        saturation=0.74,
        toe_power=1.14,
        shoulder_rolloff=0.28,
        ffmpeg_master_curve="0/0 0.24/0.18 0.54/0.53 0.84/0.87 1/0.98",
        chroma_mode="none",
        halation_threshold=0.76,
        halation_strength=0.18,
        halation_tint=(1.00, 0.64, 0.26),
        anamorphic_streak_strength=0.05,
        anamorphic_tint=(1.00, 0.78, 0.48),
        microcontrast_amount=0.46,
        microcontrast_radius=1.5,
        vignette_strength=0.26,
        ffmpeg_vignette_angle="PI/4.4",
        grain_sigma=0.016,
        ffmpeg_luma_noise=4,
    ),
    "chronicle_split_contrast": OpticalGradeProfile(
        grade_id="chronicle_split_contrast",
        title_en="Chronicle Split Contrast",
        film_stock_lens="Dual-State Archival Slate -> Kodak 2383 Verified Chronicle Gold",
        era_signature="Cold slate myth state -> warm antique-gold verified chronicle state",
        style_ids=("S05", "L06"),
        rgb_matrix=(
            (1.03, 0.00, -0.03),
            (0.00, 1.01, -0.01),
            (-0.03, 0.02, 1.01),
        ),
        shadow_shift=(-0.075, -0.010, 0.085),
        midtone_shift=(0.045, 0.028, -0.045),
        highlight_shift=(0.120, 0.078, -0.090),
        contrast=1.14,
        gamma=0.95,
        saturation=1.06,
        toe_power=1.07,
        shoulder_rolloff=0.24,
        ffmpeg_master_curve="0/0 0.22/0.19 0.50/0.52 0.82/0.86 1/0.99",
        chroma_mode="chronicle_state",
        halation_threshold=0.77,
        halation_strength=0.17,
        halation_tint=(1.00, 0.74, 0.28),
        anamorphic_streak_strength=0.05,
        anamorphic_tint=(0.95, 0.82, 0.45),
        microcontrast_amount=0.48,
        microcontrast_radius=1.4,
        vignette_strength=0.15,
        ffmpeg_vignette_angle="PI/5.6",
        grain_sigma=0.012,
        ffmpeg_luma_noise=3,
    ),
    "macro_metallurgy_crisp": OpticalGradeProfile(
        grade_id="macro_metallurgy_crisp",
        title_en="Macro Metallurgy Crisp",
        film_stock_lens="Fuji Eterna Vivid 500T 8547 · 100mm Zeiss Macro Master Prime",
        era_signature="Razor-sharp specular bronze/iron/oak micro-detail + optical separation",
        style_ids=("S06", "L10"),
        rgb_matrix=(
            (1.04, -0.02, -0.02),
            (-0.02, 1.04, -0.02),
            (-0.02, -0.01, 1.03),
        ),
        shadow_shift=(-0.035, 0.000, 0.045),
        midtone_shift=(0.015, 0.012, -0.010),
        highlight_shift=(0.065, 0.042, -0.030),
        contrast=1.16,
        gamma=0.95,
        saturation=1.08,
        toe_power=1.06,
        shoulder_rolloff=0.18,
        ffmpeg_master_curve="0/0 0.20/0.18 0.50/0.51 0.82/0.86 1/1",
        chroma_mode="none",
        halation_threshold=0.84,
        halation_strength=0.10,
        halation_tint=(1.00, 0.62, 0.26),
        anamorphic_streak_strength=0.0,
        anamorphic_tint=(1.00, 0.85, 0.60),
        microcontrast_amount=0.86,
        microcontrast_radius=1.15,
        vignette_strength=0.11,
        ffmpeg_vignette_angle="PI/6.0",
        grain_sigma=0.009,
        ffmpeg_luma_noise=2,
    ),
    "duel_bipolar_crimson_cobalt": OpticalGradeProfile(
        grade_id="duel_bipolar_crimson_cobalt",
        title_en="Duel Bipolar Crimson-Cobalt",
        film_stock_lens="Kodak Vision3 500T Bipolar Print · Anamorphic 50mm Duel",
        era_signature="Faction-coded warm Đại Việt vermilion vs cold Yuan/Ming cobalt-steel",
        style_ids=("S07", "L07"),
        rgb_matrix=(
            (1.08, -0.05, -0.03),
            (-0.03, 0.98, 0.05),
            (-0.05, -0.01, 1.06),
        ),
        shadow_shift=(-0.095, -0.020, 0.125),
        midtone_shift=(0.015, -0.015, 0.020),
        highlight_shift=(0.130, -0.005, -0.070),
        contrast=1.16,
        gamma=0.94,
        saturation=1.16,
        toe_power=1.09,
        shoulder_rolloff=0.23,
        ffmpeg_master_curve="0/0 0.22/0.18 0.50/0.51 0.80/0.85 1/0.99",
        chroma_mode="bipolar_duel",
        halation_threshold=0.75,
        halation_strength=0.20,
        halation_tint=(1.00, 0.28, 0.12),
        anamorphic_streak_strength=0.09,
        anamorphic_tint=(0.70, 0.84, 1.00),
        microcontrast_amount=0.50,
        microcontrast_radius=1.5,
        vignette_strength=0.19,
        ffmpeg_vignette_angle="PI/5.0",
        grain_sigma=0.014,
        ffmpeg_luma_noise=4,
    ),
    "humanist_35mm_natural": OpticalGradeProfile(
        grade_id="humanist_35mm_natural",
        title_en="Humanist 35mm Natural",
        film_stock_lens="Kodak Vision3 200T 5213 · Cooke S4/i Spherical Intimate 50mm",
        era_signature="Organic soft highlight roll-off, earthy mud/hemp/river tones",
        style_ids=("S08", "L08"),
        rgb_matrix=(
            (1.01, 0.02, -0.03),
            (0.02, 1.00, -0.02),
            (-0.02, 0.03, 0.99),
        ),
        shadow_shift=(0.010, 0.015, -0.010),
        midtone_shift=(0.032, 0.022, -0.028),
        highlight_shift=(0.055, 0.042, -0.035),
        contrast=1.05,
        gamma=0.98,
        saturation=0.95,
        toe_power=1.02,
        shoulder_rolloff=0.34,
        ffmpeg_master_curve="0/0.01 0.24/0.23 0.54/0.55 0.82/0.84 1/0.97",
        chroma_mode="none",
        halation_threshold=0.76,
        halation_strength=0.15,
        halation_tint=(1.00, 0.58, 0.24),
        anamorphic_streak_strength=0.0,
        anamorphic_tint=(1.00, 0.76, 0.48),
        microcontrast_amount=0.22,
        microcontrast_radius=1.8,
        vignette_strength=0.13,
        ffmpeg_vignette_angle="PI/5.8",
        grain_sigma=0.015,
        ffmpeg_luma_noise=4,
    ),
    "chrono_tension_teal_amber": OpticalGradeProfile(
        grade_id="chrono_tension_teal_amber",
        title_en="Chrono Tension Teal-Amber",
        film_stock_lens="IMAX 65mm / Vision3 500T Thriller · Panavision Primo",
        era_signature="High-tension clockwork teal-amber contrast + edge vignette",
        style_ids=("S09", "L05"),
        rgb_matrix=(
            (1.05, -0.03, -0.02),
            (-0.02, 1.03, -0.01),
            (-0.04, 0.05, 0.99),
        ),
        shadow_shift=(-0.085, 0.038, 0.072),
        midtone_shift=(-0.035, 0.018, 0.028),
        highlight_shift=(0.108, 0.042, -0.082),
        contrast=1.17,
        gamma=0.93,
        saturation=1.10,
        toe_power=1.10,
        shoulder_rolloff=0.24,
        ffmpeg_master_curve="0/0 0.21/0.17 0.50/0.51 0.81/0.86 1/0.99",
        chroma_mode="none",
        halation_threshold=0.75,
        halation_strength=0.18,
        halation_tint=(1.00, 0.52, 0.14),
        anamorphic_streak_strength=0.08,
        anamorphic_tint=(0.45, 0.88, 0.98),
        microcontrast_amount=0.56,
        microcontrast_radius=1.4,
        vignette_strength=0.25,
        ffmpeg_vignette_angle="PI/4.3",
        grain_sigma=0.013,
        ffmpeg_luma_noise=4,
    ),
    "eastern_lacquer_ink_to_cinema": OpticalGradeProfile(
        grade_id="eastern_lacquer_ink_to_cinema",
        title_en="Eastern Lacquer Ink to Cinema",
        film_stock_lens="Sumi-e Cinnabar Lacquer Scroll -> Golden-Hour 35mm Vision3 Bloom",
        era_signature="Sumi-e monochrome/vermilion seal -> lush golden-hour 35mm bloom",
        style_ids=("S10", "L04"),
        rgb_matrix=(
            (1.07, -0.03, -0.04),
            (-0.01, 1.00, 0.01),
            (-0.05, 0.01, 1.04),
        ),
        shadow_shift=(0.022, -0.018, -0.028),
        midtone_shift=(0.048, 0.018, -0.042),
        highlight_shift=(0.135, 0.078, -0.095),
        contrast=1.13,
        gamma=0.95,
        saturation=1.14,
        toe_power=1.08,
        shoulder_rolloff=0.30,
        ffmpeg_master_curve="0/0 0.22/0.19 0.52/0.54 0.80/0.86 1/0.99",
        chroma_mode="lacquer_bloom",
        halation_threshold=0.70,
        halation_strength=0.28,
        halation_tint=(1.00, 0.64, 0.18),
        anamorphic_streak_strength=0.11,
        anamorphic_tint=(1.00, 0.78, 0.34),
        microcontrast_amount=0.38,
        microcontrast_radius=1.6,
        vignette_strength=0.18,
        ffmpeg_vignette_angle="PI/5.2",
        grain_sigma=0.013,
        ffmpeg_luma_noise=3,
    ),
}

# Build fast case-insensitive lookup table covering S01..S10, L01..L10, full names, and grade IDs.
_STYLE_LOOKUP: dict[str, str] = {}
for _gid in CINEMA_GRADE_IDS:
    _STYLE_LOOKUP[_gid.lower()] = _gid
for _sid, _gid in STYLE_TO_GRADE_MAP.items():
    _STYLE_LOOKUP[_sid.lower()] = _gid
    _full = CANONICAL_STYLE_NAMES[_sid]
    _STYLE_LOOKUP[_full.lower()] = _gid


def resolve_optical_grade_id(style_id: str) -> str:
    """Resolve `S01..S10`, `L01..L10`, full style slug, or direct grade ID to canonical `grade_id`."""
    raw = str(style_id or "").strip()
    if not raw:
        raise ValueError("style_id must be a non-empty string")
    low = raw.lower()
    if low in _STYLE_LOOKUP:
        return _STYLE_LOOKUP[low]
    prefix = low.split("_", 1)[0].upper()
    if prefix in STYLE_TO_GRADE_MAP:
        return STYLE_TO_GRADE_MAP[prefix]
    raise KeyError(
        f"Unknown style_id or grade_id {style_id!r}; expected S01..S10, L01..L10, or one of {CINEMA_GRADE_IDS}"
    )


def get_optical_grade_profile(style_id: str) -> OpticalGradeProfile:
    """Return the `OpticalGradeProfile` mapped to `style_id` (or direct `grade_id`)."""
    return OPTICAL_GRADE_CATALOG[resolve_optical_grade_id(style_id)]


def list_optical_grades() -> list[dict[str, Any]]:
    """Return serializable metadata for all 10 Cinema Film-Stock LUT profiles."""
    out: list[dict[str, Any]] = []
    for gid in CINEMA_GRADE_IDS:
        p = OPTICAL_GRADE_CATALOG[gid]
        out.append(
            {
                "grade_id": p.grade_id,
                "title_en": p.title_en,
                "film_stock_lens": p.film_stock_lens,
                "era_signature": p.era_signature,
                "style_ids": list(p.style_ids),
                "canonical_styles": [CANONICAL_STYLE_NAMES[s] for s in p.style_ids],
            }
        )
    return out


def _resolve_act_modifiers(profile: OpticalGradeProfile, act: int) -> dict[str, Any]:
    """Compute act-aware color-science parameters across Acts 1..6."""
    act_clamped = max(1, min(6, int(act)))
    rgb_matrix = profile.rgb_matrix
    sh = list(profile.shadow_shift)
    md = list(profile.midtone_shift)
    hi = list(profile.highlight_shift)
    contrast = profile.contrast
    gamma = profile.gamma
    saturation = profile.saturation

    if profile.chroma_mode == "chronicle_state":
        if act_clamped == 1:
            # Cold slate myth state (0-3s / Act 1)
            rgb_matrix = (
                (0.90, 0.05, 0.05),
                (0.03, 0.96, 0.01),
                (0.02, 0.06, 0.92),
            )
            sh = [-0.085, 0.005, 0.105]
            md = [-0.045, 0.010, 0.055]
            hi = [-0.055, 0.015, 0.075]
            saturation = 0.78
            contrast = 1.15
            gamma = 0.94
        elif act_clamped >= 4:
            hi = [hi[0] + 0.025, hi[1] + 0.015, hi[2] - 0.015]
            saturation = min(1.22, saturation + 0.05)
    elif profile.chroma_mode == "lacquer_bloom":
        if act_clamped == 1:
            # Classical sumi-e monochrome scroll with selective cinnabar/vermilion seal pop
            rgb_matrix = (
                (0.96, 0.02, 0.02),
                (0.26, 0.54, 0.20),
                (0.24, 0.52, 0.24),
            )
            sh = [0.015, -0.010, -0.015]
            md = [0.030, 0.012, -0.025]
            hi = [0.065, 0.040, -0.045]
            saturation = 0.80
            contrast = 1.18
            gamma = 0.93
        elif act_clamped >= 4:
            hi = [hi[0] + 0.020, hi[1] + 0.015, hi[2] - 0.015]
            saturation = min(1.24, saturation + 0.05)
    else:
        if act_clamped == 1:
            # Act 1 Hook: slightly tauter shadow coolness & crisp entry contrast
            contrast += 0.02
            sh[2] += 0.015
        elif act_clamped == 3:
            contrast += 0.015
            saturation *= 1.02
        elif act_clamped == 4:
            # Act 4 Climax: heightened dynamic punch & warm specular intensity
            contrast += 0.035
            saturation *= 1.05
            hi[0] += 0.025
            hi[2] -= 0.015
            gamma -= 0.01
        elif act_clamped >= 5:
            # Act 5-6 Resolution: gentler roll-off & historical resonance
            contrast = max(1.03, contrast - 0.02)
            gamma += 0.015
            hi[0] += 0.015
            hi[1] += 0.010

    def _clip_cb(vec: list[float]) -> tuple[float, float, float]:
        return (
            float(np.clip(vec[0], -0.95, 0.95)),
            float(np.clip(vec[1], -0.95, 0.95)),
            float(np.clip(vec[2], -0.95, 0.95)),
        )

    return {
        "act": act_clamped,
        "rgb_matrix": rgb_matrix,
        "shadow_shift": _clip_cb(sh),
        "midtone_shift": _clip_cb(md),
        "highlight_shift": _clip_cb(hi),
        "contrast": round(float(np.clip(contrast, 0.85, 1.45)), 4),
        "gamma": round(float(np.clip(gamma, 0.78, 1.18)), 4),
        "saturation": round(float(np.clip(saturation, 0.40, 1.55)), 4),
    }


def get_ffmpeg_grade_filter(style_id: str, act: int = 2) -> str:
    """Build hardware-ready linear FFmpeg `V->V` color & optical filter chain.

    Strictly pad-free and semicolon-free so it splices cleanly multiple times inside
    Colab Tesla T4 `h264_nvenc` `-filter_complex` graphs (`render_single_pass.py` / V10 Long)
    as well as standalone `-vf` invocations across FFmpeg 4.4..7.x.
    """
    profile = get_optical_grade_profile(style_id)
    mod = _resolve_act_modifiers(profile, act)
    m = mod["rgb_matrix"]
    sh = mod["shadow_shift"]
    md = mod["midtone_shift"]
    hi = mod["highlight_shift"]

    ccm = (
        f"colorchannelmixer="
        f"rr={m[0][0]:.4f}:rg={m[0][1]:.4f}:rb={m[0][2]:.4f}:"
        f"gr={m[1][0]:.4f}:gg={m[1][1]:.4f}:gb={m[1][2]:.4f}:"
        f"br={m[2][0]:.4f}:bg={m[2][1]:.4f}:bb={m[2][2]:.4f}"
    )
    cb = (
        f"colorbalance="
        f"rs={sh[0]:.4f}:gs={sh[1]:.4f}:bs={sh[2]:.4f}:"
        f"rm={md[0]:.4f}:gm={md[1]:.4f}:bm={md[2]:.4f}:"
        f"rh={hi[0]:.4f}:gh={hi[1]:.4f}:bh={hi[2]:.4f}"
    )
    curves_f = f"curves=m='{profile.ffmpeg_master_curve}'"
    eq_f = (
        f"eq=contrast={mod['contrast']:.4f}:"
        f"saturation={mod['saturation']:.4f}:"
        f"gamma={mod['gamma']:.4f}"
    )

    luma_amt = round(float(np.clip(profile.microcontrast_amount * 0.85, 0.12, 1.10)), 3)
    unsharp_f = f"unsharp=5:5:{luma_amt:.3f}:3:3:0.0"

    stages: list[str] = [
        ccm,
        cb,
        curves_f,
        "format=yuv420p",
        eq_f,
        unsharp_f,
    ]
    if profile.ffmpeg_vignette_angle:
        stages.append(f"vignette=angle={profile.ffmpeg_vignette_angle}")
    if profile.ffmpeg_luma_noise > 0:
        stages.append(f"noise=c0s={int(profile.ffmpeg_luma_noise)}:c0f=t+u")

    return ",".join(stages)


def _srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    return np.where(rgb <= 0.04045, rgb / 12.92, np.power((rgb + 0.055) / 1.055, 2.4))


def _linear_to_srgb(lin: np.ndarray) -> np.ndarray:
    c = np.clip(lin, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1.0 / 2.4) - 0.055)


def _fast_gaussian_rgb(arr01: np.ndarray, radius_px: float, *, horiz_stretch: float = 1.0) -> np.ndarray:
    """Fast smooth RGB float32 blur using downsampled PIL GaussianBlur + bicubic upsample."""
    if radius_px <= 0.25:
        return arr01
    h, w, _ = arr01.shape
    scale_y = 0.5 if min(h, w) >= 360 else 1.0
    scale_x = scale_y / max(1.0, float(horiz_stretch))
    dw = max(8, int(round(w * scale_x)))
    dh = max(8, int(round(h * scale_y)))

    u8 = np.clip(arr01 * 255.0 + 0.5, 0.0, 255.0).astype(np.uint8)
    pil_im = Image.fromarray(u8, mode="RGB")
    if (dw, dh) != (w, h):
        pil_im = pil_im.resize((dw, dh), Image.Resampling.BILINEAR)
    eff_r = max(0.6, float(radius_px) * scale_y)
    pil_blur = pil_im.filter(ImageFilter.GaussianBlur(radius=eff_r))
    if (dw, dh) != (w, h):
        pil_blur = pil_blur.resize((w, h), Image.Resampling.BICUBIC)
    return np.asarray(pil_blur, dtype=np.float32) / 255.0


def _apply_core_color_science_float(
    rgb: np.ndarray,
    profile: OpticalGradeProfile,
    mod: dict[str, Any],
) -> np.ndarray:
    """Pure pointwise color-science transfer (usable on both 2D frames and 3D LUT cubes)."""
    mat = np.asarray(mod["rgb_matrix"], dtype=np.float32)
    x = np.einsum("...c,dc->...d", rgb, mat)
    x = np.clip(x, 0.0, 1.0)

    luma = 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]

    # Selective chroma / faction sculpting before split-toning
    sat = float(mod["saturation"])
    if profile.chroma_mode == "crimson_pop":
        # Desaturate global battlefield steel while popping warm crimson/fire vectors
        red_dom = np.clip((x[..., 0] - np.maximum(x[..., 1], x[..., 2]) - 0.03) / 0.26, 0.0, 1.0)
        local_sat = sat + (1.38 - sat) * red_dom
        x = luma[..., None] + (x - luma[..., None]) * local_sat[..., None]
    elif profile.chroma_mode == "bipolar_duel":
        # Polarize warm vermilion vs cold cobalt-steel; suppress muddy yellow-green middle
        rb_diff = x[..., 0] - x[..., 2]
        pole_weight = np.clip(np.abs(rb_diff) / 0.25, 0.0, 1.0)
        local_sat = sat * (0.86 + 0.26 * pole_weight)
        x = luma[..., None] + (x - luma[..., None]) * local_sat[..., None]
        warm_mask = np.clip(rb_diff / 0.30, 0.0, 1.0)
        cool_mask = np.clip(-rb_diff / 0.30, 0.0, 1.0)
        x[..., 0] += 0.035 * warm_mask * (1.0 - luma)
        x[..., 2] += 0.045 * cool_mask * (1.0 - 0.4 * luma)
    elif profile.chroma_mode == "lacquer_bloom" and mod["act"] == 1:
        # Sumi-e ink scroll with selective cinnabar/vermilion seal retention
        red_seal = np.clip((x[..., 0] - np.maximum(x[..., 1], x[..., 2]) - 0.05) / 0.22, 0.0, 1.0)
        local_sat = 0.22 + 1.08 * red_seal
        x = luma[..., None] + (x - luma[..., None]) * local_sat[..., None]
    else:
        x = luma[..., None] + (x - luma[..., None]) * sat

    x = np.clip(x, 0.0, 1.0)
    luma = 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]

    # 3-zone photochemical split-toning (shadows, midtones, highlights)
    w_sh = np.power(1.0 - luma, 2.2)[..., None] * (0.35 + 0.65 * np.clip(luma / 0.12, 0.0, 1.0))[..., None]
    w_md = (4.0 * luma * (1.0 - luma))[..., None]
    w_hi = np.power(luma, 2.0)[..., None] * (1.0 - 0.35 * np.clip((luma - 0.92) / 0.08, 0.0, 1.0))[..., None]

    sh_v = np.asarray(mod["shadow_shift"], dtype=np.float32)
    md_v = np.asarray(mod["midtone_shift"], dtype=np.float32)
    hi_v = np.asarray(mod["highlight_shift"], dtype=np.float32)
    x = x + 0.52 * (w_sh * sh_v + w_md * md_v + w_hi * hi_v)
    x = np.clip(x, 0.0, 1.0)

    # Gamma + C1-continuous photochemical Hurter-Driffield S-curve (zero black-crush clipping!)
    inv_gamma = 1.0 / max(0.5, float(mod["gamma"]))
    x = np.power(np.clip(x, 1e-6, 1.0), inv_gamma)

    pivot = 0.46
    c_toe = float(mod["contrast"]) * (0.94 + 0.55 * (float(profile.toe_power) - 1.0))
    c_shd = max(1.0, float(mod["contrast"]) * (1.0 - 0.32 * float(profile.shoulder_rolloff)))
    low_branch = pivot * np.power(np.clip(x / pivot, 0.0, 1.0), c_toe)
    high_branch = 1.0 - (1.0 - pivot) * np.power(np.clip((1.0 - x) / (1.0 - pivot), 0.0, 1.0), c_shd)
    x = np.where(x <= pivot, low_branch, high_branch)

    # Print-stock shadow tint preservation so Caravaggio indigo / cobalt / teal toes stay rich
    luma_post = 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
    deep_toe = (np.power(1.0 - luma_post, 2.6) * np.clip(luma_post / 0.025, 0.0, 1.0))[..., None]
    x = x + 0.24 * deep_toe * sh_v

    return np.clip(x, 0.0, 1.0).astype(np.float32)


def _deterministic_grain_seed(style_id: str, act: int, height: int, width: int) -> int:
    key = f"{resolve_optical_grade_id(style_id)}:{int(act)}:{int(height)}x{int(width)}".encode("utf-8")
    return int.from_bytes(hashlib.blake2b(key, digest_size=4).digest(), "little")


def apply_optical_grade_numpy(
    frame_rgb: np.ndarray,
    style_id: str,
    act: int = 2,
    *,
    include_halation: bool = True,
    include_grain: bool = True,
) -> np.ndarray:
    """Apply full 35mm film-stock color science & lens physics to an RGB `uint8` `(H, W, 3)` array."""
    if frame_rgb.ndim != 3 or frame_rgb.shape[2] != 3:
        raise ValueError(f"Expected (H, W, 3) RGB array, got shape={frame_rgb.shape}")

    profile = get_optical_grade_profile(style_id)
    mod = _resolve_act_modifiers(profile, act)
    h, w, _ = frame_rgb.shape
    min_dim = float(min(h, w))

    rgb = frame_rgb.astype(np.float32) / 255.0

    # 1. Scene-referred 35mm emulsion halation + subtle horizontal anamorphic flare on bright sources
    if include_halation and (profile.halation_strength > 0.0 or profile.anamorphic_streak_strength > 0.0):
        lin = _srgb_to_linear(rgb)
        luma_lin = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]

        if profile.halation_strength > 0.0:
            thr = float(profile.halation_threshold)
            hot = np.clip((luma_lin - thr) / max(1e-4, 1.0 - thr), 0.0, 1.0)
            hot = np.power(hot, 1.55)
            tint = np.asarray(profile.halation_tint, dtype=np.float32)
            em_src = hot[..., None] * tint[None, None, :]
            r_core = max(2.0, min_dim * 0.0085)
            r_wide = max(5.0, min_dim * 0.024)
            glow = 0.62 * _fast_gaussian_rgb(em_src, r_core) + 0.38 * _fast_gaussian_rgb(em_src, r_wide)
            lin = lin + float(profile.halation_strength) * glow

        if profile.anamorphic_streak_strength > 0.0:
            s_thr = max(0.82, float(profile.halation_threshold) + 0.06)
            spec = np.clip((luma_lin - s_thr) / max(1e-4, 1.0 - s_thr), 0.0, 1.0)
            spec = np.power(spec, 1.8)
            a_tint = np.asarray(profile.anamorphic_tint, dtype=np.float32)
            st_src = spec[..., None] * a_tint[None, None, :]
            streak = _fast_gaussian_rgb(st_src, max(3.0, min_dim * 0.012), horiz_stretch=5.5)
            lin = lin + float(profile.anamorphic_streak_strength) * streak

        # Soft highlight energy conservation before negative dye curve
        lin = lin / (1.0 + 0.22 * np.maximum(0.0, lin - 0.85))
        rgb = _linear_to_srgb(lin)

    # 2. Core photochemical color matrix, selective chroma, split-toning & filmic S-curve
    graded = _apply_core_color_science_float(rgb, profile, mod)

    # 3. Optical MTF micro-contrast (weighted away from deep shadow floor to avoid noise amplification)
    if profile.microcontrast_amount > 0.0:
        blur_mc = _fast_gaussian_rgb(graded, float(profile.microcontrast_radius) * max(1.0, min_dim / 720.0))
        detail = graded - blur_mc
        y_mc = 0.2126 * graded[..., 0] + 0.7152 * graded[..., 1] + 0.0722 * graded[..., 2]
        mc_mask = np.clip((y_mc - 0.04) / 0.14, 0.25, 1.0)[..., None]
        graded = np.clip(graded + float(profile.microcontrast_amount) * 0.55 * detail * mc_mask, 0.0, 1.0)

    # 4. Gentle cosine-fourth peripheral optical vignette (protects center & bottom-right readability)
    if profile.vignette_strength > 0.0:
        yy = (np.linspace(0.0, 1.0, h, dtype=np.float32) - 0.47)[:, None]
        xx = (np.linspace(0.0, 1.0, w, dtype=np.float32) - 0.50)[None, :]
        rad2 = (xx * xx + yy * yy) / 0.50
        vig = 1.0 - float(profile.vignette_strength) * np.power(np.clip(rad2, 0.0, 1.35), 1.35)
        vig = np.clip(vig, 1.0 - float(profile.vignette_strength) * 1.15, 1.0)
        graded = graded * vig[..., None]

    # 5. Natural fine 35mm silver-halide film grain (midtone bell `4*Y*(1-Y)` -> zero shadow fog/mud)
    if include_grain and profile.grain_sigma > 0.0:
        seed = _deterministic_grain_seed(style_id, mod["act"], h, w)
        rng = np.random.default_rng(seed)
        mono = rng.standard_normal((h, w), dtype=np.float32)
        # Subtle 3x3 dye-cloud spatial correlation so grain feels organic, never digital snow
        mono_pad = np.pad(mono, 1, mode="reflect")
        clump = (
            0.52 * mono
            + 0.12 * (mono_pad[:-2, 1:-1] + mono_pad[2:, 1:-1] + mono_pad[1:-1, :-2] + mono_pad[1:-1, 2:])
        )
        chroma_n = rng.standard_normal((h, w, 3), dtype=np.float32)
        grain_field = 0.86 * clump[..., None] + 0.14 * chroma_n
        y_g = 0.2126 * graded[..., 0] + 0.7152 * graded[..., 1] + 0.0722 * graded[..., 2]
        mid_bell = (4.0 * y_g * (1.0 - y_g)) ** 0.85
        graded = np.clip(graded + float(profile.grain_sigma) * grain_field * mid_bell[..., None], 0.0, 1.0)

    return np.clip(graded * 255.0 + 0.5, 0.0, 255.0).astype(np.uint8)


def apply_optical_grade_pil(img: Image.Image, style_id: str, act: int = 2) -> Image.Image:
    """Apply 35mm film-stock color science, halation & fine grain to a `PIL.Image.Image`."""
    if not isinstance(img, Image.Image):
        raise TypeError(f"Expected PIL.Image.Image, got {type(img)!r}")

    orig_mode = img.mode
    alpha = img.getchannel("A") if "A" in img.getbands() else None
    rgb_im = img.convert("RGB")
    arr = np.asarray(rgb_im, dtype=np.uint8)
    graded_arr = apply_optical_grade_numpy(arr, style_id=style_id, act=act)
    out = Image.fromarray(graded_arr, mode="RGB")
    if orig_mode == "RGBA" and alpha is not None:
        out = out.convert("RGBA")
        out.putalpha(alpha)
    return out


def build_3d_lut_cube(style_id: str, act: int = 2, size: int = 17) -> np.ndarray:
    """Compile an exact `(size, size, size, 3)` float32 3D LUT cube (`[0.0, 1.0]`)."""
    if not (5 <= int(size) <= 65):
        raise ValueError(f"LUT cube size must be in 5..65, got {size}")
    n = int(size)
    profile = get_optical_grade_profile(style_id)
    mod = _resolve_act_modifiers(profile, act)
    axis = np.linspace(0.0, 1.0, n, dtype=np.float32)
    b_grid, g_grid, r_grid = np.meshgrid(axis, axis, axis, indexing="ij")
    lattice = np.stack([r_grid, g_grid, b_grid], axis=-1)
    return _apply_core_color_science_float(lattice, profile, mod)


def export_3d_lut_cube_file(style_id: str, out_path: Path, act: int = 2, size: int = 17) -> Path:
    """Export standard Adobe / FFmpeg `lut3d`-compatible `.cube` file."""
    cube = build_3d_lut_cube(style_id=style_id, act=act, size=size)
    gid = resolve_optical_grade_id(style_id)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f'TITLE "{gid}_act{int(act)}"',
        f"LUT_3D_SIZE {int(size)}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    flat = cube.reshape(-1, 3)
    lines.extend(f"{r:.6f} {g:.6f} {b:.6f}" for r, g, b in flat)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def validate_ffmpeg_grade_filter(
    filter_chain: str,
    *,
    width: int = 320,
    height: int = 180,
    ffmpeg_bin: str = "ffmpeg",
) -> dict[str, Any]:
    """Validate an FFmpeg grade filter chain via real `ffmpeg -f lavfi` frame execution."""
    if not filter_chain or ";" in filter_chain:
        raise ValueError(f"Grade filter must be non-empty and semicolon-free: {filter_chain!r}")
    cmd = [
        ffmpeg_bin,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        f"testsrc2=s={int(width)}x{int(height)}:r=30:d=0.10",
        "-vf",
        filter_chain,
        "-frames:v",
        "2",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "pipe:1",
    ]
    res = subprocess.run(cmd, capture_output=True, timeout=20)
    expected_bytes = int(width) * int(height) * 3 * 2
    ok = res.returncode == 0 and len(res.stdout) == expected_bytes
    arr = (
        np.frombuffer(res.stdout[: int(width) * int(height) * 3], dtype=np.uint8).reshape(int(height), int(width), 3)
        if ok
        else None
    )
    return {
        "valid": ok,
        "returncode": res.returncode,
        "stderr": res.stderr.decode("utf-8", errors="replace").strip(),
        "bytes_out": len(res.stdout),
        "mean_luma": float(arr.mean()) if arr is not None else 0.0,
        "std_luma": float(arr.std()) if arr is not None else 0.0,
    }


def _load_showcase_font(size: int, *, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    bvp = SYS_DIR / "assets" / "fonts" / "su_ke_lai" / "BeVietnamPro-ExtraBold.ttf"
    candidates = (
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf",
        )
        if mono
        else (
            str(bvp),
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        )
    )
    for fp in candidates:
        if Path(fp).is_file():
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def render_optical_luts_showcase(
    source_frame_path: Path,
    out_png_path: Path,
    *,
    act: int = 2,
    tile_width: int = 440,
) -> Path:
    """Render a crisp `2x5` Cinema Film-Stock LUT Comparison Strip on a real 35mm frame."""
    source_frame_path = Path(source_frame_path)
    if not source_frame_path.is_file():
        raise FileNotFoundError(f"Source frame not found: {source_frame_path}")

    with Image.open(source_frame_path) as raw_im:
        src_rgb = raw_im.convert("RGB")

    tile_w = int(tile_width)
    tile_h = int(round(tile_w * (src_rgb.height / float(src_rgb.width))))
    src_resized = src_rgb.resize((tile_w, tile_h), Image.Resampling.LANCZOS)

    cols, rows = 5, 2
    pad_outer = 36
    gap_x, gap_y = 24, 28
    header_h = 132
    meta_h = 128
    card_w = tile_w
    card_h = tile_h + meta_h

    canvas_w = pad_outer * 2 + cols * card_w + (cols - 1) * gap_x
    canvas_h = header_h + rows * card_h + (rows - 1) * gap_y + pad_outer

    canvas = Image.new("RGB", (canvas_w, canvas_h), (10, 12, 16))
    draw = ImageDraw.Draw(canvas)

    f_title = _load_showcase_font(38, mono=False)
    f_sub = _load_showcase_font(20, mono=True)
    f_card_id = _load_showcase_font(20, mono=False)
    f_badge = _load_showcase_font(16, mono=True)
    f_desc = _load_showcase_font(15, mono=False)

    def _fit_text_px(txt: str, font_obj: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_px: int) -> str:
        bb = draw.textbbox((0, 0), txt, font=font_obj)
        if (bb[2] - bb[0]) <= max_px:
            return txt
        trimmed = txt
        while len(trimmed) > 4:
            trimmed = trimmed[:-1].rstrip()
            cand = trimmed + "…"
            cb = draw.textbbox((0, 0), cand, font=font_obj)
            if (cb[2] - cb[0]) <= max_px:
                return cand
        return trimmed

    # Top prestige cinema header
    draw.rectangle([0, 0, canvas_w, header_h - 14], fill=(15, 18, 25))
    draw.line([(pad_outer, header_h - 14), (canvas_w - pad_outer, header_h - 14)], fill=(218, 176, 84), width=3)
    draw.text(
        (pad_outer, 24),
        "10x10 CINEMA FILM-STOCK OPTICAL GRADING & ANAMORPHIC LENS FX MATRIX",
        font=f_title,
        fill=(248, 240, 220),
    )
    draw.text(
        (pad_outer, 76),
        f"35mm Emulsion Halation · Photochemical 3x3 Dye Matrix · Split-Toning · Luma-Weighted Grain | Source: {source_frame_path.name} (Act {act})",
        font=f_sub,
        fill=(212, 174, 92),
    )

    for idx, gid in enumerate(CINEMA_GRADE_IDS):
        r_idx, c_idx = divmod(idx, cols)
        x0 = pad_outer + c_idx * (card_w + gap_x)
        y0 = header_h + r_idx * (card_h + gap_y)

        prof = OPTICAL_GRADE_CATALOG[gid]
        # Showcase eastern_lacquer_ink_to_cinema left-half Act 1 sumi-e -> right-half Act 2 35mm bloom,
        # and chronicle_split_contrast left-half Act 1 cold myth -> right-half Act 2 chronicle gold!
        if gid in ("chronicle_split_contrast", "eastern_lacquer_ink_to_cinema"):
            g_act1 = apply_optical_grade_pil(src_resized, gid, act=1)
            g_act2 = apply_optical_grade_pil(src_resized, gid, act=act)
            a1_np = np.asarray(g_act1, dtype=np.float32)
            a2_np = np.asarray(g_act2, dtype=np.float32)
            ramp = np.clip((np.linspace(0.0, 1.0, tile_w, dtype=np.float32) - 0.34) / 0.14, 0.0, 1.0)[None, :, None]
            blended = np.clip(a1_np * (1.0 - ramp) + a2_np * ramp + 0.5, 0.0, 255.0).astype(np.uint8)
            graded_tile = Image.fromarray(blended, mode="RGB")
            t_draw = ImageDraw.Draw(graded_tile)
            split_x = int(round(tile_w * 0.41))
            t_draw.line([(split_x, 14), (split_x, tile_h - 14)], fill=(238, 198, 102), width=2)
        else:
            graded_tile = apply_optical_grade_pil(src_resized, gid, act=act)

        # Card background & border
        draw.rounded_rectangle(
            [x0 - 2, y0 - 2, x0 + card_w + 1, y0 + card_h + 1],
            radius=10,
            fill=(18, 21, 29),
            outline=(68, 76, 94),
            width=2,
        )
        canvas.paste(graded_tile, (x0, y0))

        # Top-left index + mapped style pill over tile
        styles_label = " · ".join(prof.style_ids)
        pill_text = f"#{idx + 1:02d}  {styles_label}"
        pb = draw.textbbox((0, 0), pill_text, font=f_badge)
        pw, ph = pb[2] - pb[0] + 22, pb[3] - pb[1] + 12
        draw.rounded_rectangle(
            [x0 + 12, y0 + 12, x0 + 12 + pw, y0 + 12 + ph],
            radius=6,
            fill=(10, 13, 20),
            outline=(226, 184, 88),
            width=2,
        )
        draw.text((x0 + 23 - pb[0], y0 + 18 - pb[1]), pill_text, font=f_badge, fill=(252, 220, 128))

        # Metadata footer with RGB tonal-response swatch bar
        fy = y0 + tile_h + 10
        draw.text((x0 + 12, fy), gid, font=f_card_id, fill=(246, 242, 232))

        # 5-step tonal gradient swatch graded through the exact LUT profile
        sw_w, sw_h = card_w - 24, 10
        grad_x = np.linspace(0.05, 0.96, sw_w, dtype=np.float32)[None, :, None]
        neutral_strip = np.repeat(np.repeat(grad_x, sw_h, axis=0), 3, axis=2)
        mod_sw = _resolve_act_modifiers(prof, act)
        graded_strip = (_apply_core_color_science_float(neutral_strip, prof, mod_sw) * 255.0 + 0.5).astype(np.uint8)
        canvas.paste(Image.fromarray(graded_strip, mode="RGB"), (x0 + 12, fy + 30))

        sig_line = _fit_text_px(prof.era_signature, f_desc, card_w - 24)
        draw.text((x0 + 12, fy + 48), sig_line, font=f_desc, fill=(198, 206, 220))

        arr_tile = np.asarray(graded_tile, dtype=np.float32)
        luma_t = 0.2126 * arr_tile[..., 0] + 0.7152 * arr_tile[..., 1] + 0.0722 * arr_tile[..., 2]
        dr_p95_p5 = float(np.percentile(luma_t, 95) - np.percentile(luma_t, 5))
        r_b_delta = float(arr_tile[..., 0].mean() - arr_tile[..., 2].mean())
        stats_txt = _fit_text_px(
            f"DR(p95-p5)={dr_p95_p5:5.1f}  R-B={r_b_delta:+5.1f}  Grain={prof.grain_sigma:.3f}",
            f_badge,
            card_w - 24,
        )
        draw.text((x0 + 12, fy + 76), stats_txt, font=f_badge, fill=(154, 178, 208))

        stock_short = _fit_text_px(prof.film_stock_lens.split("·")[0].strip(), f_desc, card_w - 24)
        draw.text((x0 + 12, fy + 99), stock_short, font=f_desc, fill=(216, 178, 96))

    out_png_path = Path(out_png_path)
    out_png_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_png_path, format="PNG", optimize=True)
    return out_png_path
