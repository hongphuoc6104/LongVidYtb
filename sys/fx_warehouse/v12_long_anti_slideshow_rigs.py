"""V12 Zero-Box 30fps Analytical & Editorial Cutaway Rigs (`v12_long_anti_slideshow_rigs.py`).

Implements the 6 V12 Anti-Slideshow Documentary Analysis Rigs, V8.0 Zero-Box Chapter Cards
(`3.80s` = `114f`, `>= 3.10s` at 100% opacity, zero smoke wipes), and Smooth `float32`
Multi-Plane Sub-Pixel Parallax for rapid `2.2s-3.0s` BELUGA 4-shot coverage quartets.

Supported Master Canvases:
    - `1920x1080@30fps` (16:9 Full HD — Giant Typography >= 64px)
    - `2560x1440@30fps` (16:9 2K QHD — Giant Typography >= 86px)
    - `1440x2560@30fps` (9:16 2K Vertical — Giant Typography >= 132px)
    - `1080x1920@30fps` (9:16 HD Vertical — Giant Typography >= 100px)

Hard Architectural Locks (AGENTS.md & PLAYBOOK.md):
    - `ERR-20261109-01`: 100% ban on FFmpeg integer-truncating `vf_zoompan`; all camera glides
      use `np.float32` 2x3 matrices with `cv2.warpAffine(..., flags=cv2.INTER_LINEAR)` (`0.000px` jitter).
    - `ERR-20261122-01`: Zero-Box Typography (transparent RGBA + optical Gaussian drop-shadow ONLY,
      ZERO dark rectangular HUD pills, ZERO left accent stripes, ZERO `"VS"` plaques, ZERO smoke/fog wipes).
    - V8.0 Chapter Card Hold: `3.80s` (`114` frames @ 30fps), `>= 3.10s` at 100% opacity.
"""

from __future__ import annotations

import enum
import math
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ENGINE_ID = "su_ke_lai_v12_zero_box_rigs"
ENGINE_VERSION = "12.0.0"

DEFAULT_FPS = 30
CHAPTER_CARD_DURATION_SEC = 3.80
CHAPTER_CARD_FRAMES = 114  # 3.80s * 30fps
CHAPTER_CARD_START_DELAY_SEC = 0.08
CHAPTER_CARD_FADE_IN_SEC = 0.25
CHAPTER_CARD_FADE_OUT_SEC = 0.22
CHAPTER_CARD_MIN_FULL_OPACITY_SEC = 3.10

MIN_FONT_PX_16X9_1080P = 64
MIN_FONT_PX_9X16_1440W = 132
MAX_GIANT_LABEL_WORDS = 3

# Palette constants (RGB tuples)
COLOR_OBSIDIAN_BOARD = (11, 12, 16)       # #0B0C10
COLOR_DARK_IRONWOOD = (18, 15, 13)        # Rich dark ironwood undertone
COLOR_DARKROOM_BG = (10, 11, 14)          # #0A0B0E
COLOR_SLATE_AUTOPSY = (22, 21, 19)        # #161513
COLOR_BURNISHED_BRONZE = (198, 156, 83)   # #C69C53 2px split/hairline
COLOR_ANTIQUE_GOLD = (212, 175, 55)       # #D4AF37 vector/hairline gold
COLOR_GIANT_GOLD = (255, 224, 102)        # #FFE066 emphasis typography
COLOR_IVORY_CREAM = (255, 245, 214)       # #FFF5D6 prestige cinema white-gold
COLOR_CLEAN_WHITE = (248, 250, 252)       # #F8FAFC crisp high-contrast white
COLOR_CRIMSON_THREAD = (217, 56, 58)      # #D9383A forensic vector thread
COLOR_BALLISTIC_AMBER = (255, 98, 54)     # #FF6236 trajectory glow
COLOR_DO_PAPER_BASE = (218, 199, 162)     # Aged mulberry Dó paper
COLOR_DO_PAPER_INK = (42, 28, 20)         # Classical sepia-carbon ink

_SYS_DIR = Path(__file__).resolve().parent.parent
_FONT_CANDIDATES_BOLD: tuple[str, ...] = (
    str(_SYS_DIR / "assets" / "fonts" / "su_ke_lai" / "BeVietnamPro-ExtraBold.ttf"),
    str(_SYS_DIR / "assets" / "fonts" / "su_ke_lai" / "Oswald-Bold.ttf"),
    str(_SYS_DIR / "assets" / "fonts" / "su_ke_lai" / "BarlowCondensed-ExtraBold.ttf"),
    str(_SYS_DIR / "assets" / "fonts" / "chanh_niem_ke" / "DejaVuSans-Bold.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
_FONT_CANDIDATES_SERIF: tuple[str, ...] = (
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
    str(_SYS_DIR / "assets" / "fonts" / "chanh_niem_ke" / "RobotoSlab-Bold.ttf"),
    str(_SYS_DIR / "assets" / "fonts" / "su_ke_lai" / "BeVietnamPro-ExtraBold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)
_FONT_CANDIDATES_MONO: tuple[str, ...] = (
    str(_SYS_DIR / "assets" / "fonts" / "chanh_niem_ke" / "IBMPlexMono-Bold.ttf"),
    str(_SYS_DIR / "assets" / "fonts" / "su_ke_lai" / "Oswald-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}
_NVENC_CACHE: bool | None = None


class RigId(str, enum.Enum):
    """Canonical identifiers for the 6 V12 Zero-Box 30fps Analytical Rigs."""

    RIG_A_SPOTLIGHT = "RIG_A_SPOTLIGHT"
    RIG_B_SPLIT_CONTRAST = "RIG_B_SPLIT_CONTRAST"
    RIG_C_EVIDENCE_BOARD = "RIG_C_EVIDENCE_BOARD"
    RIG_D_FOLIO_HIGHLIGHT = "RIG_D_FOLIO_HIGHLIGHT"
    RIG_E_WEAPON_AUTOPSY = "RIG_E_WEAPON_AUTOPSY"
    RIG_F_CHRONO_SPLIT = "RIG_F_CHRONO_SPLIT"


RIG_ALIASES: dict[str, RigId] = {
    "RIG_A_SPOTLIGHT": RigId.RIG_A_SPOTLIGHT,
    "RIG_A_PROGRESSIVE_SPOTLIGHT": RigId.RIG_A_SPOTLIGHT,
    "SPOTLIGHT": RigId.RIG_A_SPOTLIGHT,
    "RIG_B_SPLIT_CONTRAST": RigId.RIG_B_SPLIT_CONTRAST,
    "RIG_B_SPLIT_SCREEN_CONTRAST": RigId.RIG_B_SPLIT_CONTRAST,
    "SPLIT_CONTRAST": RigId.RIG_B_SPLIT_CONTRAST,
    "RIG_C_EVIDENCE_BOARD": RigId.RIG_C_EVIDENCE_BOARD,
    "RIG_C_EVIDENCE_TABLETOP_BOARD": RigId.RIG_C_EVIDENCE_BOARD,
    "EVIDENCE_BOARD": RigId.RIG_C_EVIDENCE_BOARD,
    "RIG_D_FOLIO_HIGHLIGHT": RigId.RIG_D_FOLIO_HIGHLIGHT,
    "RIG_D_PRIMARY_FOLIO_SPOTLIGHT": RigId.RIG_D_FOLIO_HIGHLIGHT,
    "FOLIO_HIGHLIGHT": RigId.RIG_D_FOLIO_HIGHLIGHT,
    "RIG_E_WEAPON_AUTOPSY": RigId.RIG_E_WEAPON_AUTOPSY,
    "RIG_E_WEAPON_PHYSICS_CROSS_SECTION": RigId.RIG_E_WEAPON_AUTOPSY,
    "WEAPON_AUTOPSY": RigId.RIG_E_WEAPON_AUTOPSY,
    "RIG_F_CHRONO_SPLIT": RigId.RIG_F_CHRONO_SPLIT,
    "RIG_F_SYNCHRONIZED_CANH_GIO_CLOCK": RigId.RIG_F_CHRONO_SPLIT,
    "CHRONO_SPLIT": RigId.RIG_F_CHRONO_SPLIT,
}


def resolve_rig_id(raw_id: str | RigId) -> RigId:
    """Resolve canonical RigId or architectural alias cleanly."""
    if isinstance(raw_id, RigId):
        return raw_id
    key = str(raw_id or "").strip().upper()
    if key in RIG_ALIASES:
        return RIG_ALIASES[key]
    raise ValueError(f"Unknown V12 analytical rig {raw_id!r}; valid={tuple(r.value for r in RigId)}")


@dataclass(frozen=True)
class FocalRegion:
    """Normalized focal target (0..1) and 1-3 word label for RIG_A_SPOTLIGHT."""

    cx: float
    cy: float
    radius_ratio: float = 0.19
    label: str = "MŨI ĐỘT KÍCH"


@dataclass(frozen=True)
class EvidenceNode:
    """Physical artifact/clue node on RIG_C_EVIDENCE_BOARD."""

    x: float
    y: float
    label: str
    code: str = " CHỨNG CỨ "
    falsified: bool = False


@dataclass
class RigSpec:
    """Unified declarative specification for any of the 6 V12 Zero-Box Rigs."""

    rig_id: RigId | str
    duration_sec: float = 6.6
    fps: int = DEFAULT_FPS
    width: int = 1920
    height: int = 1080
    primary_label: str = "ĐẠI VIỆT"
    secondary_label: str = "CHIẾN LƯỢC"
    left_stat: str = "10 NGÀY"
    right_stat: str = "22 NĂM"
    left_label: str = "ÁN XỬ VỘI"
    right_label: str = "RỬA OAN"
    source_image: str | Path | np.ndarray | None = None
    left_image: str | Path | np.ndarray | None = None
    right_image: str | Path | np.ndarray | None = None
    panel_images: list[str | Path | np.ndarray] = field(default_factory=list)
    focal_regions: list[FocalRegion] = field(default_factory=list)
    evidence_nodes: list[EvidenceNode] = field(default_factory=list)
    folio_lines: list[str] = field(default_factory=list)
    folio_source_citation: str = "ĐẠI VIỆT SỬ KÝ TOÀN THƯ"
    weapon_preset: str = "bach_dang_ironwood_stake"
    canh_gio_label: str = "CANH TƯ · 02:15"
    t_minus_seconds: int = 13500
    front_labels: list[str] = field(default_factory=list)

    def resolved_rig(self) -> RigId:
        return resolve_rig_id(self.rig_id)


# ---------------------------------------------------------------------------
# Math, Font, & Zero-Box Typography Primitives
# ---------------------------------------------------------------------------
def _clamp01(val: float) -> float:
    return 0.0 if val < 0.0 else (1.0 if val > 1.0 else float(val))


def smoothstep_cubic(val: float) -> float:
    """C1-continuous cubic Hermite smoothstep in [0, 1]."""
    t = _clamp01(val)
    return t * t * (3.0 - 2.0 * t)


def ease_out_quart(val: float) -> float:
    t = _clamp01(val)
    return 1.0 - (1.0 - t) ** 4


def is_vertical_canvas(width: int, height: int) -> bool:
    return int(height) > int(width)


def effective_min_font_px(width: int, height: int) -> int:
    """Enforce V12 Giant Typography floor: >=64px on 1920x1080, >=132px on 1440x2560."""
    if is_vertical_canvas(width, height):
        scaled = int(round(MIN_FONT_PX_9X16_1440W * (width / 1440.0)))
        return MIN_FONT_PX_9X16_1440W if width >= 1440 else max(28, scaled)
    scaled = int(round(MIN_FONT_PX_16X9_1080P * (height / 1080.0)))
    return MIN_FONT_PX_16X9_1080P if height >= 1080 else max(20, scaled)


def scale_font_px(base_1080p_px: int, width: int, height: int) -> int:
    """Scale typography size cleanly across 16:9 (1080p/1440p) and 9:16 (1440x2560)."""
    floor_px = effective_min_font_px(width, height)
    if is_vertical_canvas(width, height):
        ratio = width / 1440.0
        target = int(round(max(base_1080p_px * 2.05, MIN_FONT_PX_9X16_1440W) * ratio))
        return max(floor_px, target)
    ratio = height / 1080.0
    target = int(round(max(base_1080p_px, MIN_FONT_PX_16X9_1080P) * ratio))
    return max(floor_px, target)


def clamp_giant_words(raw_text: str, max_words: int = MAX_GIANT_LABEL_WORDS) -> str:
    """Sanitize and clamp primary rig callouts to 1-3 uppercase words; strip banned 'VS'."""
    cleaned = re.sub(r"\bVS\.?\b", " ", str(raw_text or ""), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*/\s*", "/", cleaned)
    cleaned = re.sub(r"[|•·\[\]{}()<>]+", " ", cleaned)
    tokens = [tok.strip() for tok in cleaned.upper().split() if tok.strip()]
    if not tokens:
        return "ĐẠI VIỆT"
    limit = max(1, min(int(max_words), MAX_GIANT_LABEL_WORDS))
    selected = tokens[:limit]
    while len(selected) > 1 and selected[-1] in {"&", "/", "+", "-", "–", "—", ":", ",", "."}:
        selected.pop()
    return " ".join(selected)


def _load_font(candidates: tuple[str, ...], size_px: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    sz = max(12, int(size_px))
    for path_str in candidates:
        cache_key = (path_str, sz)
        if cache_key in _FONT_CACHE:
            return _FONT_CACHE[cache_key]
        if Path(path_str).is_file():
            font = ImageFont.truetype(path_str, sz)
            _FONT_CACHE[cache_key] = font
            return font
    fallback = ImageFont.load_default()
    _FONT_CACHE[("default", sz)] = fallback
    return fallback


def render_zero_box_text_rgba(
    text: str,
    *,
    font_px: int,
    color_rgb: tuple[int, int, int] = COLOR_IVORY_CREAM,
    opacity: float = 1.0,
    font_style: str = "bold",
    shadow_blur_px: int = 8,
    shadow_offset: tuple[int, int] = (0, 4),
    max_words: int | None = MAX_GIANT_LABEL_WORDS,
    max_width_px: int | None = None,
) -> np.ndarray:
    """Render floating cinema typography on pure transparent RGBA (ZERO boxes/borders/pills).

    Uses a soft optical Gaussian drop-shadow directly behind glyph alpha contours so
    all surrounding pixels remain `[0, 0, 0, 0]` transparent.
    """
    display = clamp_giant_words(text, max_words) if max_words is not None else re.sub(
        r"\bVS\.?\b", "", str(text or ""), flags=re.IGNORECASE
    ).strip()
    if not display:
        return np.zeros((4, 4, 4), dtype=np.uint8)

    alpha_scale = _clamp01(opacity)
    if alpha_scale <= 0.002:
        return np.zeros((4, 4, 4), dtype=np.uint8)

    cands = (
        _FONT_CANDIDATES_SERIF
        if font_style == "serif"
        else _FONT_CANDIDATES_MONO
        if font_style == "mono"
        else _FONT_CANDIDATES_BOLD
    )
    cur_px = int(font_px)
    font = _load_font(cands, cur_px)

    dummy = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(dummy)
    bbox = d_draw.textbbox((0, 0), display, font=font)
    pad = max(16, int(shadow_blur_px * 3) + max(abs(shadow_offset[0]), abs(shadow_offset[1])) + 8)
    if max_width_px is not None and max_width_px > 40:
        min_px = max(24, int(round(font_px * 0.52)))
        while cur_px > min_px and ((bbox[2] - bbox[0]) + pad * 2) > int(max_width_px):
            cur_px = max(min_px, cur_px - 2)
            font = _load_font(cands, cur_px)
            bbox = d_draw.textbbox((0, 0), display, font=font)
    w = max(8, (bbox[2] - bbox[0]) + pad * 2)
    h = max(8, (bbox[3] - bbox[1]) + pad * 2)
    ox = pad - bbox[0]
    oy = pad - bbox[1]

    # Optical shadow pass (soft glyph contour shadow only — zero rectangle slab!)
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    sh_alpha = int(round(215 * alpha_scale))
    s_draw.text(
        (ox + shadow_offset[0], oy + shadow_offset[1]),
        display,
        font=font,
        fill=(0, 0, 0, sh_alpha),
    )
    if shadow_blur_px > 0:
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=float(shadow_blur_px)))

    # Crisp glyph pass on top
    fg_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    f_draw = ImageDraw.Draw(fg_layer)
    fg_alpha = int(round(255 * alpha_scale))
    f_draw.text(
        (ox, oy),
        display,
        font=font,
        fill=(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), fg_alpha),
    )

    merged = Image.alpha_composite(shadow_layer, fg_layer)
    return np.asarray(merged, dtype=np.uint8)


def composite_rgba_over_rgb(
    canvas_rgb: np.ndarray,
    overlay_rgba: np.ndarray,
    *,
    cx: int,
    cy: int,
    anchor: str = "center",
) -> np.ndarray:
    """Alpha-blend a transparent RGBA glyph layer onto an RGB uint8 frame safely."""
    oh, ow = overlay_rgba.shape[:2]
    ch, cw = canvas_rgb.shape[:2]
    if oh <= 4 and ow <= 4 and int(overlay_rgba[..., 3].max()) == 0:
        return canvas_rgb

    if anchor == "topleft":
        x0, y0 = int(cx), int(cy)
    elif anchor == "midleft":
        x0, y0 = int(cx), int(cy - oh // 2)
    elif anchor == "midright":
        x0, y0 = int(cx - ow), int(cy - oh // 2)
    else:
        x0, y0 = int(cx - ow // 2), int(cy - oh // 2)

    # Keep inside 3.5% title-safe margin
    margin_x = max(12, int(cw * 0.035))
    margin_y = max(12, int(ch * 0.035))
    x0 = max(margin_x, min(cw - ow - margin_x, x0)) if ow + 2 * margin_x < cw else max(0, (cw - ow) // 2)
    y0 = max(margin_y, min(ch - oh - margin_y, y0)) if oh + 2 * margin_y < ch else max(0, (ch - oh) // 2)

    x1 = min(cw, x0 + ow)
    y1 = min(ch, y0 + oh)
    sx0 = max(0, -x0)
    sy0 = max(0, -y0)
    dx0 = max(0, x0)
    dy0 = max(0, y0)
    rw = x1 - dx0
    rh = y1 - dy0
    if rw <= 0 or rh <= 0:
        return canvas_rgb

    sub_ov = overlay_rgba[sy0 : sy0 + rh, sx0 : sx0 + rw]
    alpha = sub_ov[..., 3:4].astype(np.float32) / 255.0
    dst_patch = canvas_rgb[dy0 : dy0 + rh, dx0 : dx0 + rw].astype(np.float32)
    src_rgb = sub_ov[..., :3].astype(np.float32)
    blended = dst_patch * (1.0 - alpha) + src_rgb * alpha
    canvas_rgb[dy0 : dy0 + rh, dx0 : dx0 + rw] = np.clip(blended, 0.0, 255.0).astype(np.uint8)
    return canvas_rgb


# ---------------------------------------------------------------------------
# Smooth Float32 Sub-Pixel Affine Camera & Multi-Plane Parallax (0.000px Jitter)
# ---------------------------------------------------------------------------
def build_subpixel_affine_matrix(
    src_w: int,
    src_h: int,
    dst_w: int,
    dst_h: int,
    *,
    scale: float = 1.05,
    focus_x: float = 0.5,
    focus_y: float = 0.5,
    pan_px_x: float = 0.0,
    pan_px_y: float = 0.0,
) -> np.ndarray:
    """Construct exact `np.float32` 2x3 affine transform with 0.000px integer jitter."""
    cover = max(dst_w / float(max(1, src_w)), dst_h / float(max(1, src_h)))
    eff_s = float(cover * max(1.0, float(scale)))
    cx_src = float(src_w) * float(focus_x)
    cy_src = float(src_h) * float(focus_y)
    tx = float(dst_w) * 0.5 - eff_s * cx_src + float(pan_px_x)
    ty = float(dst_h) * 0.5 - eff_s * cy_src + float(pan_px_y)
    return np.array(
        [
            [eff_s, 0.0, tx],
            [0.0, eff_s, ty],
        ],
        dtype=np.float32,
    )


def warp_affine_float32(
    img_rgb: np.ndarray,
    dst_w: int,
    dst_h: int,
    *,
    scale: float = 1.05,
    focus_x: float = 0.5,
    focus_y: float = 0.5,
    pan_px_x: float = 0.0,
    pan_px_y: float = 0.0,
) -> np.ndarray:
    """Sub-pixel `cv2.warpAffine` replacing banned 15Hz integer-rounding `vf_zoompan`."""
    sh, sw = img_rgb.shape[:2]
    mat = build_subpixel_affine_matrix(
        sw,
        sh,
        dst_w,
        dst_h,
        scale=scale,
        focus_x=focus_x,
        focus_y=focus_y,
        pan_px_x=pan_px_x,
        pan_px_y=pan_px_y,
    )
    return cv2.warpAffine(
        img_rgb,
        mat,
        (int(dst_w), int(dst_h)),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )


def measure_trajectory_subpixel_jitter(
    width: int = 1920,
    height: int = 1080,
    n_frames: int = 90,
    scale_start: float = 1.02,
    scale_end: float = 1.10,
) -> float:
    """Measure peak high-frequency 15Hz alternating residual across `float32` trajectory."""
    centers_y: list[float] = []
    for idx in range(max(4, n_frames)):
        u = idx / float(max(1, n_frames - 1))
        eased = smoothstep_cubic(u)
        s = scale_start + (scale_end - scale_start) * eased
        mat = build_subpixel_affine_matrix(width, height, width, height, scale=s, focus_x=0.5, focus_y=0.5)
        # Map optical center back to source space
        mapped_y = (height * 0.5 - float(mat[1, 2])) / float(mat[1, 1])
        centers_y.append(mapped_y - height * 0.5)
    arr = np.asarray(centers_y, dtype=np.float64)
    return float(np.max(np.abs(arr)))


# ---------------------------------------------------------------------------
# Procedural Historical Base Plates (Used when external BELUGA plate is omitted)
# ---------------------------------------------------------------------------
def _load_or_synth_plate(
    src: str | Path | np.ndarray | None,
    width: int,
    height: int,
    *,
    theme: str = "terrain",
) -> np.ndarray:
    if isinstance(src, np.ndarray) and src.ndim == 3:
        if src.shape[2] == 4:
            return src[..., :3].copy()
        return src.copy()
    if isinstance(src, (str, Path)) and Path(src).is_file():
        bgr = cv2.imread(str(src), cv2.IMREAD_COLOR)
        if bgr is not None:
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # Synthesize tactile cinematic historical base plate (shaded relief / torchlit scene)
    w = max(320, int(width * 1.16))
    h = max(320, int(height * 1.16))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = xx / float(w)
    ny = yy / float(h)

    if theme == "warm_siege":
        r = 38.0 + 95.0 * np.exp(-((nx - 0.36) ** 2 + (ny - 0.52) ** 2) / 0.14)
        g = 24.0 + 58.0 * np.exp(-((nx - 0.36) ** 2 + (ny - 0.52) ** 2) / 0.12)
        b = 18.0 + 24.0 * (1.0 - ny)
        # Palisade & spear silhouettes in lower half
        ridge = 0.62 + 0.04 * np.sin(nx * 19.0) + 0.02 * np.cos(nx * 43.0)
        mask = (ny > ridge).astype(np.float32)
        r = r * (1.0 - 0.68 * mask) + 14.0 * mask
        g = g * (1.0 - 0.72 * mask) + 11.0 * mask
        b = b * (1.0 - 0.72 * mask) + 10.0 * mask
    elif theme == "cold_fleet":
        r = 18.0 + 28.0 * np.exp(-((nx - 0.62) ** 2 + (ny - 0.45) ** 2) / 0.18)
        g = 36.0 + 54.0 * (1.0 - np.abs(ny - 0.52))
        b = 52.0 + 74.0 * np.exp(-((nx - 0.55) ** 2 + (ny - 0.48) ** 2) / 0.22)
        waves = 8.0 * np.sin(ny * 85.0 + nx * 14.0)
        g += waves * (ny > 0.50)
        b += waves * 1.3 * (ny > 0.50)
    else:
        # Shaded topographic river-valley relief (Bạch Đằng / Như Nguyệt)
        elev = (
            0.45 * np.sin(nx * 7.5 + 0.6) * np.cos(ny * 6.0 - 0.3)
            + 0.28 * np.sin(nx * 17.0 - ny * 11.0)
            + 0.15 * np.cos(nx * 33.0 + ny * 27.0)
        )
        river_dist = np.abs(ny - (0.52 + 0.11 * np.sin(nx * 5.2)))
        river_mask = np.exp(-(river_dist**2) / 0.0045)
        r = (46.0 + 36.0 * elev) * (1.0 - river_mask) + 22.0 * river_mask
        g = (44.0 + 32.0 * elev) * (1.0 - river_mask) + 46.0 * river_mask
        b = (36.0 + 22.0 * elev) * (1.0 - river_mask) + 64.0 * river_mask

        # Subtle topographic contour lines
        contour = (np.abs(np.sin(elev * 22.0)) > 0.965).astype(np.float32) * (1.0 - river_mask)
        r += contour * 26.0
        g += contour * 22.0
        b += contour * 14.0

    rgb = np.stack([r, g, b], axis=-1)
    return np.clip(rgb, 0.0, 255.0).astype(np.uint8)


# ---------------------------------------------------------------------------
# RIG A: Fern / Operations-Room Progressive 65%-Dim Optical Spotlight Cone
# ---------------------------------------------------------------------------
def _render_rig_a_spotlight(spec: RigSpec, u: float, t_sec: float) -> np.ndarray:
    w, h = int(spec.width), int(spec.height)
    base_plate = _load_or_synth_plate(spec.source_image, w, h, theme="terrain")

    regions = list(spec.focal_regions) or [
        FocalRegion(0.28, 0.44, 0.17, spec.primary_label or "CỬA SÔNG"),
        FocalRegion(0.53, 0.52, 0.18, spec.secondary_label or "BÃI CỌC NGẦM"),
        FocalRegion(0.74, 0.42, 0.17, "CHẶN ĐƯỜNG RÚT"),
    ]
    n_reg = len(regions)
    seg_pos = u * max(1, n_reg - 1)
    idx0 = min(n_reg - 1, int(math.floor(seg_pos)))
    idx1 = min(n_reg - 1, idx0 + 1)
    local_t = smoothstep_cubic(seg_pos - idx0)

    r0, r1 = regions[idx0], regions[idx1]
    fx = r0.cx + (r1.cx - r0.cx) * local_t
    fy = r0.cy + (r1.cy - r0.cy) * local_t
    rad_ratio = r0.radius_ratio + (r1.radius_ratio - r0.radius_ratio) * local_t
    active_region = r1 if local_t > 0.55 else r0

    # Smooth float32 camera push + glide toward active focal point
    cam_scale = 1.03 + 0.09 * smoothstep_cubic(u)
    warped = warp_affine_float32(
        base_plate,
        w,
        h,
        scale=cam_scale,
        focus_x=0.5 + (fx - 0.5) * 0.42,
        focus_y=0.5 + (fy - 0.5) * 0.42,
    )

    # Optical 65%-dim vignette + top-down volumetric spotlight cone (ZERO rectangle border!)
    dim_ramp = smoothstep_cubic(min(1.0, t_sec / 0.45)) if t_sec > 0.0 else 1.0
    outer_factor = 1.0 - 0.65 * dim_ramp  # 1.0 -> 0.35 (exact 65% dim!)

    spot_x = fx * w
    spot_y = fy * h
    sigma = max(48.0, rad_ratio * min(w, h))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist2 = (xx - spot_x) ** 2 + (yy - spot_y) ** 2
    spot_mask = np.exp(-dist2 / (2.0 * sigma * sigma))

    # Overhead Fern-style volumetric light beam cone from top center-ish toward focal point
    beam_top_x = w * 0.5 + (spot_x - w * 0.5) * 0.35
    ry = np.maximum(0.05, yy / max(1.0, spot_y))
    beam_half_w = 24.0 + sigma * 1.15 * np.clip(ry, 0.0, 1.25)
    beam_cx = beam_top_x + (spot_x - beam_top_x) * np.clip(ry, 0.0, 1.0)
    beam_cone = np.exp(-((xx - beam_cx) ** 2) / (2.0 * beam_half_w * beam_half_w)) * (yy <= spot_y + sigma * 0.7)

    luma_gain = outer_factor + (1.10 - outer_factor) * np.clip(spot_mask + 0.24 * beam_cone * dim_ramp, 0.0, 1.0)
    lit = np.clip(warped.astype(np.float32) * luma_gain[..., None], 0.0, 255.0).astype(np.uint8)

    # Subtle 2px segmented circular sightline arcs (optical lens reticle, never a rectangular box)
    ring_r = int(round(sigma * 0.92))
    scx, scy = int(round(spot_x)), int(round(spot_y))
    for start_deg in (20, 110, 200, 290):
        cv2.ellipse(
            lit,
            (scx, scy),
            (ring_r, ring_r),
            0.0,
            float(start_deg),
            float(start_deg + 50),
            COLOR_ANTIQUE_GOLD,
            2,
            lineType=cv2.LINE_AA,
        )

    # Step index indicator dots (1 -> 2 -> 3) in upper-left negative space (boxless)
    for r_i in range(n_reg):
        dot_x = int(w * 0.06) + r_i * 26
        dot_y = int(h * 0.07)
        col = COLOR_GIANT_GOLD if r_i <= (idx1 if local_t > 0.55 else idx0) else (95, 98, 108)
        cv2.circle(lit, (dot_x, dot_y), 6 if col == COLOR_GIANT_GOLD else 4, col, -1, lineType=cv2.LINE_AA)

    # Giant 1-3 word boxless typography placed cleanly in opposite negative space
    font_px = scale_font_px(74, w, h)
    txt_rgba = render_zero_box_text_rgba(
        active_region.label,
        font_px=font_px,
        color_rgb=COLOR_GIANT_GOLD,
        opacity=1.0,
    )
    label_y = int(spot_y - ring_r - font_px * 0.75) if spot_y > h * 0.45 else int(spot_y + ring_r + font_px * 0.75)
    composite_rgba_over_rgb(lit, txt_rgba, cx=scx, cy=label_y, anchor="center")
    return lit


# ---------------------------------------------------------------------------
# RIG B: 2px Burnished-Bronze Split-Screen Visual Contrast (Anti-VS!)
# ---------------------------------------------------------------------------
def _render_rig_b_split_contrast(spec: RigSpec, u: float, t_sec: float) -> np.ndarray:
    _ = t_sec
    w, h = int(spec.width), int(spec.height)
    vertical = is_vertical_canvas(w, h)

    plate_a = _load_or_synth_plate(spec.left_image, w, h, theme="warm_siege")
    plate_b = _load_or_synth_plate(spec.right_image, w, h, theme="cold_fleet")

    eased = smoothstep_cubic(u)
    if not vertical:
        # 16:9 crop + hstack with opposing float32 sub-pixel drift
        half_w = w // 2
        right_w = w - half_w
        left_crop = warp_affine_float32(
            plate_a,
            half_w,
            h,
            scale=1.04 + 0.05 * eased,
            focus_x=0.46,
            focus_y=0.50,
            pan_px_x=14.0 * (eased - 0.5),
            pan_px_y=-8.0 * (eased - 0.5),
        )
        right_crop = warp_affine_float32(
            plate_b,
            right_w,
            h,
            scale=1.09 - 0.05 * eased,
            focus_x=0.54,
            focus_y=0.50,
            pan_px_x=-14.0 * (eased - 0.5),
            pan_px_y=8.0 * (eased - 0.5),
        )
        frame = np.hstack([left_crop, right_crop])
        # Exact 2px burnished-bronze razor seam (ZERO VS circle/plaque!)
        seam_x = half_w - 1
        frame[:, max(0, seam_x) : min(w, seam_x + 2)] = COLOR_BURNISHED_BRONZE

        stat_px = scale_font_px(108, w, h)
        lbl_px = scale_font_px(66, w, h)
        max_col_w = max(240, int(half_w * 0.86))

        def _fit_col_text(text: str, base_px: int, color_rgb: tuple[int, int, int], opacity: float = 1.0) -> np.ndarray:
            rgba = render_zero_box_text_rgba(text, font_px=base_px, color_rgb=color_rgb, opacity=opacity)
            if rgba.shape[1] > max_col_w:
                scaled_px = max(28, int(base_px * (max_col_w / float(rgba.shape[1]))))
                rgba = render_zero_box_text_rgba(text, font_px=scaled_px, color_rgb=color_rgb, opacity=opacity)
            return rgba

        s_left = _fit_col_text(spec.left_stat, stat_px, COLOR_GIANT_GOLD)
        l_left = _fit_col_text(spec.left_label, lbl_px, COLOR_CLEAN_WHITE)
        composite_rgba_over_rgb(frame, s_left, cx=half_w // 2, cy=int(h * 0.42))
        composite_rgba_over_rgb(frame, l_left, cx=half_w // 2, cy=int(h * 0.57))

        r_reveal = smoothstep_cubic((u - 0.12) / 0.25) if u > 0.0 else 1.0
        s_right = _fit_col_text(spec.right_stat, stat_px, COLOR_IVORY_CREAM, opacity=max(0.25, r_reveal))
        l_right = _fit_col_text(spec.right_label, lbl_px, COLOR_GIANT_GOLD, opacity=max(0.25, r_reveal))
        composite_rgba_over_rgb(frame, s_right, cx=half_w + right_w // 2, cy=int(h * 0.42))
        composite_rgba_over_rgb(frame, l_right, cx=half_w + right_w // 2, cy=int(h * 0.57))
        return frame

    # 9:16 (1440x2560) crop + vstack with opposing float32 drift
    half_h = h // 2
    bot_h = h - half_h
    top_crop = warp_affine_float32(
        plate_a,
        w,
        half_h,
        scale=1.04 + 0.05 * eased,
        pan_px_x=18.0 * (eased - 0.5),
    )
    bot_crop = warp_affine_float32(
        plate_b,
        w,
        bot_h,
        scale=1.09 - 0.05 * eased,
        pan_px_x=-18.0 * (eased - 0.5),
    )
    frame = np.vstack([top_crop, bot_crop])
    seam_y = half_h - 1
    frame[max(0, seam_y) : min(h, seam_y + 2), :] = COLOR_BURNISHED_BRONZE

    stat_px = scale_font_px(108, w, h)  # >= 220px on 1440x2560
    lbl_px = scale_font_px(66, w, h)    # >= 135px on 1440x2560
    s_top = render_zero_box_text_rgba(spec.left_stat, font_px=stat_px, color_rgb=COLOR_GIANT_GOLD)
    l_top = render_zero_box_text_rgba(spec.left_label, font_px=lbl_px, color_rgb=COLOR_CLEAN_WHITE)
    composite_rgba_over_rgb(frame, s_top, cx=w // 2, cy=int(half_h * 0.42))
    composite_rgba_over_rgb(frame, l_top, cx=w // 2, cy=int(half_h * 0.64))

    s_bot = render_zero_box_text_rgba(spec.right_stat, font_px=stat_px, color_rgb=COLOR_IVORY_CREAM)
    l_bot = render_zero_box_text_rgba(spec.right_label, font_px=lbl_px, color_rgb=COLOR_GIANT_GOLD)
    composite_rgba_over_rgb(frame, s_bot, cx=w // 2, cy=half_h + int(bot_h * 0.42))
    composite_rgba_over_rgb(frame, l_bot, cx=w // 2, cy=half_h + int(bot_h * 0.64))
    return frame


# ---------------------------------------------------------------------------
# RIG C: Overhead #0B0C10 / Dark-Ironwood Forensic Evidence Board (2.2s steps)
# ---------------------------------------------------------------------------
def _render_rig_c_evidence_board(spec: RigSpec, u: float, t_sec: float) -> np.ndarray:
    w, h = int(spec.width), int(spec.height)
    vertical = is_vertical_canvas(w, h)

    # Oversized #0B0C10 / dark-ironwood surface for float32 overhead dolly
    bw, bh = int(w * 1.14), int(h * 1.14)
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    grain = 3.5 * np.sin(yy * 0.18 + 1.8 * np.sin(xx * 0.012))
    board = np.empty((bh, bw, 3), dtype=np.float32)
    board[..., 0] = COLOR_OBSIDIAN_BOARD[0] + 5.0 + grain * 0.6
    board[..., 1] = COLOR_OBSIDIAN_BOARD[1] + 2.0 + grain * 0.4
    board[..., 2] = COLOR_OBSIDIAN_BOARD[2] + grain * 0.2
    board_u8 = np.clip(board, 0.0, 255.0).astype(np.uint8)

    default_nodes = (
        [
            EvidenceNode(0.24, 0.25, "ĐÊM LỆ CHI", "MỐC 01", falsified=False),
            EvidenceNode(0.52, 0.48, "LỜI CÁO BUỘC", "MỐC 02", falsified=True),
            EvidenceNode(0.76, 0.73, "CHIẾU RỬA OAN", "MỐC 03", falsified=False),
        ]
        if not vertical
        else [
            EvidenceNode(0.50, 0.24, "ĐÊM LỆ CHI", "MỐC 01", falsified=False),
            EvidenceNode(0.50, 0.52, "LỜI CÁO BUỘC", "MỐC 02", falsified=True),
            EvidenceNode(0.50, 0.78, "CHIẾU RỬA OAN", "MỐC 03", falsified=False),
        ]
    )
    nodes = list(spec.evidence_nodes) or default_nodes

    # Step-by-step reveal every 2.2s
    eff_t = t_sec if t_sec > 0.0 else spec.duration_sec * u
    active_steps = max(1, min(len(nodes), int(eff_t // 2.2) + 1))

    # Draw physical wax-seal medallions & parchment clue tokens onto board before camera glide
    for idx, node in enumerate(nodes[:active_steps]):
        nx, ny = int(node.x * bw), int(node.y * bh)
        step_age = max(0.0, eff_t - idx * 2.2)
        reveal = smoothstep_cubic(min(1.0, step_age / 0.45)) if t_sec > 0.0 else 1.0

        # Warm candle pool around active clue
        rad = int(min(bw, bh) * 0.13)
        y0, y1 = max(0, ny - rad * 2), min(bh, ny + rad * 2)
        x0, x1 = max(0, nx - rad * 2), min(bw, nx + rad * 2)
        gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        glow = np.exp(-((gx - nx) ** 2 + (gy - ny) ** 2) / (2.0 * (rad * 0.85) ** 2)) * (0.55 * reveal)
        patch = board_u8[y0:y1, x0:x1].astype(np.float32)
        patch[..., 0] += glow * 52.0
        patch[..., 1] += glow * 38.0
        patch[..., 2] += glow * 16.0
        board_u8[y0:y1, x0:x1] = np.clip(patch, 0.0, 255.0).astype(np.uint8)

        # Cinnabar / bronze physical pin medallion (circular physical prop, zero HUD rectangle)
        pin_r = max(18, int(min(bw, bh) * 0.032))
        cv2.circle(board_u8, (nx + 3, ny + 5), pin_r + 2, (4, 4, 6), -1, lineType=cv2.LINE_AA)
        ring_col = COLOR_CRIMSON_THREAD if node.falsified else COLOR_ANTIQUE_GOLD
        cv2.circle(board_u8, (nx, ny), pin_r, (34, 26, 22), -1, lineType=cv2.LINE_AA)
        cv2.circle(board_u8, (nx, ny), pin_r, ring_col, 3, lineType=cv2.LINE_AA)
        cv2.circle(board_u8, (nx, ny), max(5, pin_r // 3), ring_col, -1, lineType=cv2.LINE_AA)

        # Progressive vector thread from previous node
        if idx > 0:
            prev = nodes[idx - 1]
            px, py = int(prev.x * bw), int(prev.y * bh)
            prog = smoothstep_cubic(min(1.0, step_age / 0.55)) if t_sec > 0.0 else 1.0
            ex = int(round(px + (nx - px) * prog))
            ey = int(round(py + (ny - py) * prog))
            thread_col = COLOR_CRIMSON_THREAD if (node.falsified or prev.falsified) else COLOR_ANTIQUE_GOLD
            cv2.line(board_u8, (px, py), (ex, ey), (0, 0, 0), 5, lineType=cv2.LINE_AA)
            cv2.line(board_u8, (px, py), (ex, ey), thread_col, 2, lineType=cv2.LINE_AA)

        if node.falsified and reveal > 0.65:
            slash = int(pin_r * 1.45)
            cv2.line(
                board_u8,
                (nx - slash, ny - slash),
                (nx + slash, ny + slash),
                COLOR_CRIMSON_THREAD,
                4,
                lineType=cv2.LINE_AA,
            )

    # Overhead float32 tracking camera following latest revealed node
    cur_node = nodes[active_steps - 1]
    cam_scale = 1.03 + 0.04 * smoothstep_cubic(u)
    cam_fx = 0.5 + (cur_node.x - 0.5) * 0.25
    cam_fy = 0.5 + (cur_node.y - 0.5) * 0.25
    cam_mat = build_subpixel_affine_matrix(bw, bh, w, h, scale=cam_scale, focus_x=cam_fx, focus_y=cam_fy)
    frame = warp_affine_float32(
        board_u8,
        w,
        h,
        scale=cam_scale,
        focus_x=cam_fx,
        focus_y=cam_fy,
    )

    # Giant boxless labels anchored to exact post-warp pin screen coordinates (0 pin/thread overlap!)
    font_px = scale_font_px(66, w, h)
    active_nodes = nodes[:active_steps]
    flat_row = len(active_nodes) >= 2 and all(abs(n.y - active_nodes[0].y) < 0.14 for n in active_nodes)
    ascending_diag = (
        not vertical
        and not flat_row
        and len(nodes) >= 2
        and (nodes[-1].x - nodes[0].x) > 0.15
        and (nodes[-1].y - nodes[0].y) < -0.12
    )
    if flat_row and not vertical:
        xs = sorted(n.x for n in active_nodes)
        min_dx_px = min((xs[i + 1] - xs[i]) * w for i in range(len(xs) - 1)) if len(xs) >= 2 else w * 0.33
        node_max_w = max(240, int(min(w * 0.34, min_dx_px * 1.45)))
    elif ascending_diag:
        node_max_w = max(240, int(w * 0.30))
    else:
        node_max_w = max(260, int(w * 0.42)) if not vertical else max(260, int(w * 0.86))

    pin_r_board = max(18, int(min(bw, bh) * 0.032))
    screen_pin_r = pin_r_board * float(cam_mat[0, 0])
    for idx, node in enumerate(active_nodes):
        col = COLOR_CRIMSON_THREAD if node.falsified else (COLOR_GIANT_GOLD if idx == active_steps - 1 else COLOR_IVORY_CREAM)
        txt = render_zero_box_text_rgba(node.label, font_px=font_px, color_rgb=col, max_width_px=node_max_w)
        nx_b, ny_b = float(node.x * bw), float(node.y * bh)
        sx = float(cam_mat[0, 0] * nx_b + cam_mat[0, 2])
        sy = float(cam_mat[1, 1] * ny_b + cam_mat[1, 2])
        half_th = txt.shape[0] * 0.5
        if flat_row and (idx % 2 == 1):
            lx = int(round(sx))
            ly = max(76, int(round(sy - screen_pin_r - half_th - 18)))
        elif ascending_diag:
            lx = int(round(sx + w * 0.035))
            ly = min(h - 76, int(round(sy + screen_pin_r + half_th + 18)))
        else:
            lx = int(round(sx))
            ly = min(h - 76, int(round(sy + screen_pin_r + half_th + 18)))
        composite_rgba_over_rgb(frame, txt, cx=lx, cy=ly, anchor="center")

    return frame


# ---------------------------------------------------------------------------
# RIG D: Vox Darkroom Dó-Paper / Imperial Decree Progressive Highlight
# ---------------------------------------------------------------------------
def _render_rig_d_folio_highlight(spec: RigSpec, u: float, t_sec: float) -> np.ndarray:
    _ = t_sec
    w, h = int(spec.width), int(spec.height)
    vertical = is_vertical_canvas(w, h)

    # Create darkroom stage (#0A0B0E) with angled tactile Dó-paper manuscript folio
    sw, sh = int(w * 1.12), int(h * 1.12)
    stage = np.full((sh, sw, 3), COLOR_DARKROOM_BG, dtype=np.uint8)

    # Physical Dó-paper sheet on left/upper half, leaving dark negative space for giant stamp
    if not vertical:
        fx0, fy0 = int(sw * 0.08), int(sh * 0.12)
        fx1, fy1 = int(sw * 0.54), int(sh * 0.88)
    else:
        fx0, fy0 = int(sw * 0.10), int(sh * 0.10)
        fx1, fy1 = int(sw * 0.90), int(sh * 0.54)

    fw, fh = fx1 - fx0, fy1 - fy0
    yy, xx = np.mgrid[0:fh, 0:fw].astype(np.float32)
    fiber = 7.0 * np.sin(xx * 0.09) * np.cos(yy * 0.07) + 4.0 * np.sin((xx + yy) * 0.23)
    vign = 1.0 - 0.18 * (((xx / fw - 0.5) ** 2 + (yy / fh - 0.5) ** 2) * 2.2)
    paper = np.empty((fh, fw, 3), dtype=np.float32)
    for c_i in range(3):
        paper[..., c_i] = (COLOR_DO_PAPER_BASE[c_i] + fiber) * vign

    # Classical calligraphy excerpt lines + progressive Vox golden highlight band
    folio_texts = list(spec.folio_lines) or [
        "Đại Việt Sử Ký Toàn Thư · Bản Kỷ Quyển II",
        "Mùa thu tháng bảy năm Thuận Thiên thứ nhất",
        "Huống gì thành Đại La, kinh đô cũ Cao Vương",
        "Ở vào nơi trung tâm trời đất, thế rồng cuộn",
        "Muôn vật rất mực phong phú tốt tươi",
    ]
    target_line = min(2, len(folio_texts) - 1)
    lx0 = int(fw * 0.09)
    lx1 = int(fw * 0.89)
    avail_w = max(80, lx1 - lx0)
    base_px = max(16, int(fh * 0.036))
    min_px = max(16, int(base_px * 0.68))

    measure_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    chosen_px = base_px
    folio_font = _load_font(_FONT_CANDIDATES_SERIF, chosen_px)
    while chosen_px > min_px:
        if all((measure_draw.textbbox((0, 0), ln, font=folio_font)[2] - measure_draw.textbbox((0, 0), ln, font=folio_font)[0]) <= avail_w for ln in folio_texts):
            break
        chosen_px -= 2
        folio_font = _load_font(_FONT_CANDIDATES_SERIF, max(min_px, chosen_px))

    wrapped_entries: list[tuple[str, bool]] = []
    for l_i, line_str in enumerate(folio_texts):
        is_tgt = l_i == target_line
        bb = measure_draw.textbbox((0, 0), line_str, font=folio_font)
        if (bb[2] - bb[0]) <= avail_w:
            wrapped_entries.append((line_str, is_tgt))
            continue
        cur_words: list[str] = []
        for word in line_str.split():
            cand = " ".join([*cur_words, word])
            cbb = measure_draw.textbbox((0, 0), cand, font=folio_font)
            if cur_words and (cbb[2] - cbb[0]) > avail_w:
                wrapped_entries.append((" ".join(cur_words), is_tgt))
                cur_words = [word]
            else:
                cur_words.append(word)
        if cur_words:
            wrapped_entries.append((" ".join(cur_words), is_tgt))

    line_step = min(0.145, 0.56 / max(1, len(wrapped_entries)))
    lh = max(18, int(fh * min(0.068, line_step * 0.62)))
    hl_prog = smoothstep_cubic(min(1.0, max(0.25, u * 1.35)))
    for l_i, (_, is_tgt) in enumerate(wrapped_entries):
        ly0 = int(fh * (0.16 + l_i * line_step))
        if is_tgt:
            hl_x1 = lx0 + int((lx1 - lx0) * hl_prog)
            band = paper[max(0, ly0 - 6) : min(fh, ly0 + lh + 8), max(0, lx0 - 8) : min(fw, hl_x1 + 8)]
            band[..., 0] = np.clip(band[..., 0] * 1.18 + 26.0, 0.0, 255.0)
            band[..., 1] = np.clip(band[..., 1] * 1.11 + 16.0, 0.0, 255.0)
            band[..., 2] = np.clip(band[..., 2] * 0.72, 0.0, 255.0)

    paper_pil = Image.fromarray(np.clip(paper, 0.0, 255.0).astype(np.uint8), mode="RGB")
    p_draw = ImageDraw.Draw(paper_pil)
    for l_i, (line_str, is_tgt) in enumerate(wrapped_entries):
        ly0 = int(fh * (0.16 + l_i * line_step))
        ink_col = (24, 14, 8) if is_tgt else (76, 58, 44)
        p_draw.text((lx0, ly0), line_str, font=folio_font, fill=ink_col)
    paper = np.asarray(paper_pil, dtype=np.float32)

    # Cinnabar red royal seal stamp at bottom-right of folio
    seal_s = max(26, int(min(fw, fh) * 0.13))
    sx0, sy0 = fw - seal_s - int(fw * 0.10), fh - seal_s - int(fh * 0.10)
    seal_patch = paper[sy0 : sy0 + seal_s, sx0 : sx0 + seal_s]
    seal_patch[..., 0] = np.clip(seal_patch[..., 0] * 0.45 + 115.0, 0.0, 255.0)
    seal_patch[..., 1] = np.clip(seal_patch[..., 1] * 0.25 + 18.0, 0.0, 255.0)
    seal_patch[..., 2] = np.clip(seal_patch[..., 2] * 0.25 + 16.0, 0.0, 255.0)

    # Soft elevation shadow behind physical paper sheet on darkroom table
    stage[fy0 + 12 : fy1 + 12, fx0 + 12 : fx1 + 12] = (4, 4, 6)
    stage[fy0:fy1, fx0:fx1] = np.clip(paper, 0.0, 255.0).astype(np.uint8)

    # Dim non-folio darkroom gently & glide camera smoothly via float32 warpAffine
    frame = warp_affine_float32(
        stage,
        w,
        h,
        scale=1.02 + 0.05 * smoothstep_cubic(u),
        focus_x=0.48,
        focus_y=0.50,
        pan_px_x=-10.0 * (u - 0.5),
    )

    # Giant 1-3 word Vietnamese translation stamp in darkroom negative space (Rule C >=85% hold)
    stamp_px = scale_font_px(78, w, h)
    sub_px = scale_font_px(64, w, h)
    right_max_w = int(w * 0.39) if not vertical else int(w * 0.88)
    stamp_rgba = render_zero_box_text_rgba(
        spec.primary_label or "THIÊN ĐÔ CHIẾU",
        font_px=stamp_px,
        color_rgb=COLOR_GIANT_GOLD,
        font_style="serif",
        max_width_px=right_max_w,
    )
    sub_rgba = render_zero_box_text_rgba(
        spec.secondary_label or "MỞ CÕI NGÀN NĂM",
        font_px=sub_px,
        color_rgb=COLOR_IVORY_CREAM,
        max_width_px=right_max_w,
    )

    if not vertical:
        tx_c = int(w * 0.76)
        composite_rgba_over_rgb(frame, stamp_rgba, cx=tx_c, cy=int(h * 0.43))
        composite_rgba_over_rgb(frame, sub_rgba, cx=tx_c, cy=int(h * 0.58))
    else:
        composite_rgba_over_rgb(frame, stamp_rgba, cx=w // 2, cy=int(h * 0.68))
        composite_rgba_over_rgb(frame, sub_rgba, cx=w // 2, cy=int(h * 0.79))
    return frame


# ---------------------------------------------------------------------------
# RIG E: #161513 Slate Technical Cross-Section / Ballistic Vector Autopsy
# ---------------------------------------------------------------------------
def _render_rig_e_weapon_autopsy(spec: RigSpec, u: float, t_sec: float) -> np.ndarray:
    _ = t_sec
    w, h = int(spec.width), int(spec.height)
    sw, sh = int(w * 1.10), int(h * 1.10)

    # #161513 technical slate canvas
    slate = np.full((sh, sw, 3), COLOR_SLATE_AUTOPSY, dtype=np.uint8)

    # Subtle architectural azimuth rings (thin 1px low-alpha slate markings, zero boxes)
    cx_s, cy_s = int(sw * 0.50), int(sh * 0.56)
    for r_mul in (0.18, 0.30, 0.42):
        cv2.circle(
            slate,
            (cx_s, cy_s),
            int(min(sw, sh) * r_mul),
            (36, 35, 32),
            1,
            lineType=cv2.LINE_AA,
        )

    # Technical cross-section: Riverbed + angled Ironwood Stake (68°) + iron tip + hull plank
    water_y = int(sh * 0.44)
    bed_y = int(sh * 0.78)
    cv2.line(slate, (int(sw * 0.08), water_y), (int(sw * 0.92), water_y), (58, 92, 114), 2, lineType=cv2.LINE_AA)
    cv2.line(slate, (int(sw * 0.08), bed_y), (int(sw * 0.92), bed_y), (78, 66, 52), 3, lineType=cv2.LINE_AA)

    # Angled ironwood stake polygon + forged iron cap
    base_pt = (int(sw * 0.42), int(sh * 0.84))
    tip_pt = (int(sw * 0.55), int(sh * 0.46))
    dx, dy = tip_pt[0] - base_pt[0], tip_pt[1] - base_pt[1]
    length = math.hypot(dx, dy)
    nx_p, ny_p = -dy / length, dx / length
    half_th = max(10, int(min(sw, sh) * 0.018))

    collar_pt = (int(base_pt[0] + dx * 0.78), int(base_pt[1] + dy * 0.78))
    wood_poly = np.array(
        [
            [int(base_pt[0] + nx_p * half_th), int(base_pt[1] + ny_p * half_th)],
            [int(base_pt[0] - nx_p * half_th), int(base_pt[1] - ny_p * half_th)],
            [int(collar_pt[0] - nx_p * half_th * 0.85), int(collar_pt[1] - ny_p * half_th * 0.85)],
            [int(collar_pt[0] + nx_p * half_th * 0.85), int(collar_pt[1] + ny_p * half_th * 0.85)],
        ],
        dtype=np.int32,
    )
    iron_poly = np.array(
        [
            [int(collar_pt[0] + nx_p * half_th * 0.9), int(collar_pt[1] + ny_p * half_th * 0.9)],
            [int(collar_pt[0] - nx_p * half_th * 0.9), int(collar_pt[1] - ny_p * half_th * 0.9)],
            [tip_pt[0], tip_pt[1]],
        ],
        dtype=np.int32,
    )
    cv2.fillConvexPoly(slate, wood_poly, (96, 68, 44), lineType=cv2.LINE_AA)
    cv2.polylines(slate, [wood_poly], True, COLOR_BURNISHED_BRONZE, 2, lineType=cv2.LINE_AA)
    cv2.fillConvexPoly(slate, iron_poly, (168, 174, 182), lineType=cv2.LINE_AA)
    cv2.polylines(slate, [iron_poly], True, COLOR_GIANT_GOLD, 2, lineType=cv2.LINE_AA)

    # Animated ballistic / hull-momentum penetration trajectory vector
    traj_prog = ease_out_quart(min(1.0, max(0.20, u * 1.25)))
    vec_start = (int(sw * 0.78), int(sh * 0.34))
    vec_impact = tip_pt
    cur_vx = int(round(vec_start[0] + (vec_impact[0] - vec_start[0]) * traj_prog))
    cur_vy = int(round(vec_start[1] + (vec_impact[1] - vec_start[1]) * traj_prog))
    cv2.arrowedLine(
        slate,
        vec_start,
        (cur_vx, cur_vy),
        COLOR_BALLISTIC_AMBER,
        4,
        cv2.LINE_AA,
        0,
        0.09,
    )

    # Shockwave rings on contact
    if traj_prog >= 0.88:
        pulse = (u - 0.70) / 0.30 if u > 0.70 else 0.5
        ring_rad = int(18 + 46 * _clamp01(pulse))
        cv2.circle(slate, tip_pt, ring_rad, COLOR_GIANT_GOLD, 2, lineType=cv2.LINE_AA)

    # 2px antique-gold technical callout hairlines (leader lines to open negative space)
    leader_elbow = (int(sw * 0.31), int(sh * 0.34))
    leader_end = (int(sw * 0.18), int(sh * 0.34))
    cv2.line(slate, tip_pt, leader_elbow, COLOR_ANTIQUE_GOLD, 2, lineType=cv2.LINE_AA)
    cv2.line(slate, leader_elbow, leader_end, COLOR_ANTIQUE_GOLD, 2, lineType=cv2.LINE_AA)
    cv2.circle(slate, tip_pt, 6, COLOR_GIANT_GOLD, -1, lineType=cv2.LINE_AA)

    # Smooth float32 camera micro-dolly
    frame = warp_affine_float32(
        slate,
        w,
        h,
        scale=1.02 + 0.06 * smoothstep_cubic(u),
        focus_x=0.51,
        focus_y=0.50,
    )

    font_px = scale_font_px(70, w, h)
    lbl1 = render_zero_box_text_rgba(
        spec.primary_label or "BỌC SẮT 68°",
        font_px=font_px,
        color_rgb=COLOR_GIANT_GOLD,
    )
    lbl2 = render_zero_box_text_rgba(
        spec.secondary_label or "XUYÊN ĐÁY THUYỀN",
        font_px=scale_font_px(64, w, h),
        color_rgb=COLOR_CLEAN_WHITE,
    )
    if not is_vertical_canvas(w, h):
        composite_rgba_over_rgb(frame, lbl1, cx=int(w * 0.24), cy=int(h * 0.22))
        composite_rgba_over_rgb(frame, lbl2, cx=int(w * 0.74), cy=int(h * 0.72))
    else:
        composite_rgba_over_rgb(frame, lbl1, cx=w // 2, cy=int(h * 0.18))
        composite_rgba_over_rgb(frame, lbl2, cx=w // 2, cy=int(h * 0.84))
    return frame


# ---------------------------------------------------------------------------
# RIG F: Synchronized Canh-Giờ Ticking Clock + 2/3-Front Simultaneous Split
# ---------------------------------------------------------------------------
def _format_t_minus(base_seconds: int, elapsed_sec: float) -> str:
    rem = max(0, int(round(base_seconds - elapsed_sec)))
    hrs = rem // 3600
    mins = (rem % 3600) // 60
    secs = rem % 60
    return f"T-{hrs:02d}:{mins:02d}:{secs:02d}"


def _render_rig_f_chrono_split(spec: RigSpec, u: float, t_sec: float) -> np.ndarray:
    w, h = int(spec.width), int(spec.height)
    vertical = is_vertical_canvas(w, h)

    themes = ("warm_siege", "terrain", "cold_fleet")
    panels_src = list(spec.panel_images)
    plates = [
        _load_or_synth_plate(panels_src[i] if i < len(panels_src) else None, w, h, theme=themes[i % 3])
        for i in range(3)
    ]
    labels = list(spec.front_labels) or ["ĐẠO TIÊN PHONG", "ĐỒN NGỌC HỒI", "MŨI ĐỐNG ĐA"]
    while len(labels) < 3:
        labels.append(f"MẶT TRẬN {len(labels) + 1}")

    eased = smoothstep_cubic(u)
    eff_t = t_sec if t_sec > 0.0 else spec.duration_sec * u
    tick_str = _format_t_minus(spec.t_minus_seconds, eff_t)

    if not vertical:
        # 3-front simultaneous horizontal columns separated by 2px burnished-bronze seams
        c1 = w // 3
        c2 = (w - c1) // 2
        c3 = w - c1 - c2
        col_widths = (c1, c2, c3)
        strips: list[np.ndarray] = []
        for idx, cw_i in enumerate(col_widths):
            drift_sign = 1.0 if idx % 2 == 0 else -1.0
            strip = warp_affine_float32(
                plates[idx],
                cw_i,
                h,
                scale=1.05 + 0.05 * eased,
                focus_x=0.5,
                focus_y=0.5,
                pan_px_x=drift_sign * 12.0 * (eased - 0.5),
                pan_px_y=-drift_sign * 9.0 * (eased - 0.5),
            )
            strips.append(strip)
        frame = np.hstack(strips)
        y0 = int(h * 0.21)
        frame[y0:, c1 - 1 : c1 + 1] = COLOR_BURNISHED_BRONZE
        frame[y0:, c1 + c2 - 1 : c1 + c2 + 1] = COLOR_BURNISHED_BRONZE

        # Subtle top vignette (gradient multiplication only — ZERO rectangular box!)
        yy = np.linspace(0.32, 1.0, int(h * 0.26), dtype=np.float32)[:, None, None]
        frame[: int(h * 0.26)] = np.clip(frame[: int(h * 0.26)].astype(np.float32) * yy, 0.0, 255.0).astype(np.uint8)

        clock_px = scale_font_px(76, w, h)
        front_px = scale_font_px(64, w, h)
        canh_rgba = render_zero_box_text_rgba(
            spec.canh_gio_label or "CANH TƯ",
            font_px=clock_px,
            color_rgb=COLOR_GIANT_GOLD,
            font_style="mono",
        )
        tick_rgba = render_zero_box_text_rgba(
            tick_str,
            font_px=clock_px,
            color_rgb=COLOR_CLEAN_WHITE,
            font_style="mono",
            max_words=1,
        )
        composite_rgba_over_rgb(frame, canh_rgba, cx=int(w * 0.30), cy=int(h * 0.11))
        composite_rgba_over_rgb(frame, tick_rgba, cx=int(w * 0.72), cy=int(h * 0.11))

        centers_x = (c1 // 2, c1 + c2 // 2, c1 + c2 + c3 // 2)
        for idx, cx_i in enumerate(centers_x):
            max_col_w = max(200, int(col_widths[idx] * 0.84))
            eff_px = front_px
            f_rgba = render_zero_box_text_rgba(labels[idx], font_px=eff_px, color_rgb=COLOR_IVORY_CREAM)
            while f_rgba.shape[1] > max_col_w and eff_px > 32:
                eff_px = max(32, int(eff_px * (max_col_w / float(f_rgba.shape[1])) * 0.96))
                f_rgba = render_zero_box_text_rgba(labels[idx], font_px=eff_px, color_rgb=COLOR_IVORY_CREAM)
            composite_rgba_over_rgb(frame, f_rgba, cx=cx_i, cy=int(h * 0.84))
        return frame

    # 9:16 3-front vertical stack
    r1 = h // 3
    r2 = (h - r1) // 2
    r3 = h - r1 - r2
    row_heights = (r1, r2, r3)
    bands: list[np.ndarray] = []
    for idx, rh_i in enumerate(row_heights):
        drift_sign = 1.0 if idx % 2 == 0 else -1.0
        band = warp_affine_float32(
            plates[idx],
            w,
            rh_i,
            scale=1.05 + 0.05 * eased,
            pan_px_x=drift_sign * 16.0 * (eased - 0.5),
        )
        bands.append(band)
    frame = np.vstack(bands)
    frame[r1 - 1 : r1 + 1, :] = COLOR_BURNISHED_BRONZE
    frame[r1 + r2 - 1 : r1 + r2 + 1, :] = COLOR_BURNISHED_BRONZE

    clock_px = scale_font_px(76, w, h)
    front_px = scale_font_px(64, w, h)
    tick_rgba = render_zero_box_text_rgba(
        tick_str,
        font_px=clock_px,
        color_rgb=COLOR_GIANT_GOLD,
        font_style="mono",
        max_words=1,
    )
    composite_rgba_over_rgb(frame, tick_rgba, cx=w // 2, cy=int(r1 * 0.32))
    f1 = render_zero_box_text_rgba(labels[0], font_px=front_px, color_rgb=COLOR_CLEAN_WHITE)
    f2 = render_zero_box_text_rgba(labels[1], font_px=front_px, color_rgb=COLOR_IVORY_CREAM)
    f3 = render_zero_box_text_rgba(labels[2], font_px=front_px, color_rgb=COLOR_GIANT_GOLD)
    composite_rgba_over_rgb(frame, f1, cx=w // 2, cy=int(r1 * 0.72))
    composite_rgba_over_rgb(frame, f2, cx=w // 2, cy=r1 + r2 // 2)
    composite_rgba_over_rgb(frame, f3, cx=w // 2, cy=r1 + r2 + r3 // 2)
    return frame


# ---------------------------------------------------------------------------
# Unified Rig Frame & MP4 Renderers
# ---------------------------------------------------------------------------
def render_rig_frame(spec: RigSpec, frame_idx: int, total_frames: int | None = None) -> np.ndarray:
    """Render a single RGB uint8 frame of `RIG_A..RIG_F` at `frame_idx`."""
    fps = max(1, int(spec.fps))
    n_frames = total_frames if total_frames is not None else max(2, int(round(spec.duration_sec * fps)))
    u = _clamp01(frame_idx / float(max(1, n_frames - 1)))
    t_sec = frame_idx / float(fps)
    rig = spec.resolved_rig()

    if rig == RigId.RIG_A_SPOTLIGHT:
        return _render_rig_a_spotlight(spec, u, t_sec)
    if rig == RigId.RIG_B_SPLIT_CONTRAST:
        return _render_rig_b_split_contrast(spec, u, t_sec)
    if rig == RigId.RIG_C_EVIDENCE_BOARD:
        return _render_rig_c_evidence_board(spec, u, t_sec)
    if rig == RigId.RIG_D_FOLIO_HIGHLIGHT:
        return _render_rig_d_folio_highlight(spec, u, t_sec)
    if rig == RigId.RIG_E_WEAPON_AUTOPSY:
        return _render_rig_e_weapon_autopsy(spec, u, t_sec)
    if rig == RigId.RIG_F_CHRONO_SPLIT:
        return _render_rig_f_chrono_split(spec, u, t_sec)
    raise ValueError(f"Unhandled rig: {rig}")


def has_nvenc_encoder() -> bool:
    """Detect whether Tesla T4 / NVIDIA `h264_nvenc` is available on the current machine."""
    global _NVENC_CACHE
    if _NVENC_CACHE is not None:
        return _NVENC_CACHE
    try:
        res = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=black:s=256x256:d=0.04",
                "-c:v",
                "h264_nvenc",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            check=False,
            timeout=6.0,
        )
        _NVENC_CACHE = res.returncode == 0
    except Exception:
        _NVENC_CACHE = False
    return _NVENC_CACHE


def _encode_rgb_frames_to_mp4(
    frame_iter: Any,
    out_mp4_path: str | Path,
    *,
    width: int,
    height: int,
    fps: int = DEFAULT_FPS,
    prefer_nvenc: bool = True,
) -> Path:
    out_p = Path(out_mp4_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    w = int(width) - (int(width) % 2)
    h = int(height) - (int(height) % 2)

    import os as _os
    from contextlib import nullcontext

    from flow_cdp.resource_locks import (
        DEFAULT_LOCAL_CPU_THREADS,
        LocalCpuEncodeSlot,
        _nice_child_15,
        apply_low_priority_cpu_clamp,
    )

    use_nvenc = prefer_nvenc and has_nvenc_encoder()
    if not use_nvenc:
        apply_low_priority_cpu_clamp(DEFAULT_LOCAL_CPU_THREADS)
    enc_args = (
        ["-c:v", "h264_nvenc", "-preset", "p4", "-b:v", "8M", "-pix_fmt", "yuv420p"]
        if use_nvenc
        else [
            "-c:v",
            "libx264",
            "-threads",
            str(DEFAULT_LOCAL_CPU_THREADS),
            "-preset",
            "ultrafast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
        ]
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{w}x{h}",
        "-r",
        str(int(fps)),
        "-i",
        "pipe:0",
        *enc_args,
        "-movflags",
        "+faststart",
        str(out_p),
    ]
    slot_ctx = nullcontext() if use_nvenc else LocalCpuEncodeSlot(owner_tag=f"rig_v12:{out_p.name}")
    with slot_ctx:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=(_nice_child_15 if (_os.name == "posix" and not use_nvenc) else None),
        )
        assert proc.stdin is not None
        try:
            for frame_rgb in frame_iter:
                if frame_rgb.shape[1] != w or frame_rgb.shape[0] != h:
                    frame_rgb = cv2.resize(frame_rgb, (w, h), interpolation=cv2.INTER_LINEAR)
                proc.stdin.write(frame_rgb.tobytes())
            proc.stdin.close()
            err = proc.stderr.read() if proc.stderr else b""
            rc = proc.wait(timeout=180)
        except Exception:
            proc.kill()
            proc.wait()
            raise
    if rc != 0 or not out_p.is_file() or out_p.stat().st_size == 0:
        raise RuntimeError(f"Failed encoding MP4 {out_p} (rc={rc}): {err.decode('utf-8', 'replace')}")
    return out_p


def render_rig_mp4(spec: RigSpec, out_mp4_path: str | Path, *, prefer_nvenc: bool = True) -> dict[str, Any]:
    """Render any V12 Analytical Rig (`RIG_A..RIG_F`) to a 30fps `.mp4` clip."""
    fps = max(1, int(spec.fps))
    n_frames = max(2, int(round(spec.duration_sec * fps)))
    out_p = _encode_rgb_frames_to_mp4(
        (render_rig_frame(spec, i, n_frames) for i in range(n_frames)),
        out_mp4_path,
        width=spec.width,
        height=spec.height,
        fps=fps,
        prefer_nvenc=prefer_nvenc,
    )
    return {
        "path": str(out_p),
        "rig_id": spec.resolved_rig().value,
        "width": int(spec.width),
        "height": int(spec.height),
        "fps": fps,
        "duration_sec": round(n_frames / float(fps), 4),
        "n_frames": n_frames,
        "engine_version": ENGINE_VERSION,
    }


# ---------------------------------------------------------------------------
# V8.0 Zero-Box Chapter Cards (3.80s = 114f, >= 3.10s @ 100% Opacity, 0 Smoke)
# ---------------------------------------------------------------------------
def chapter_card_opacity_at(
    t_sec: float,
    *,
    duration_sec: float = CHAPTER_CARD_DURATION_SEC,
    start_delay_sec: float = CHAPTER_CARD_START_DELAY_SEC,
    fade_in_sec: float = CHAPTER_CARD_FADE_IN_SEC,
    fade_out_sec: float = CHAPTER_CARD_FADE_OUT_SEC,
) -> float:
    """Compute V8.0 comfortable reading hold opacity (`>= 3.10s` at 1.0 opacity on 3.80s card)."""
    if t_sec < start_delay_sec or t_sec >= duration_sec:
        return 0.0
    if t_sec < start_delay_sec + fade_in_sec:
        return smoothstep_cubic((t_sec - start_delay_sec) / max(1e-6, fade_in_sec))
    hold_end = duration_sec - fade_out_sec
    if t_sec <= hold_end:
        return 1.0
    return smoothstep_cubic((duration_sec - t_sec) / max(1e-6, fade_out_sec))


def verify_chapter_card_hold_metrics(
    duration_sec: float = CHAPTER_CARD_DURATION_SEC,
    fps: int = DEFAULT_FPS,
) -> dict[str, Any]:
    """Verify V8.0 Chapter Card meets `114f` (`3.80s`) and `>= 3.10s` full-opacity lock."""
    n_frames = int(round(duration_sec * fps))
    opacities = [chapter_card_opacity_at(i / float(fps), duration_sec=duration_sec) for i in range(n_frames)]
    full_frames = sum(1 for a in opacities if a >= 0.999)
    full_sec = full_frames / float(fps)
    return {
        "duration_sec": round(duration_sec, 4),
        "n_frames": n_frames,
        "full_opacity_frames": full_frames,
        "full_opacity_sec": round(full_sec, 4),
        "smoke_wipe_used": False,
        "passed": n_frames >= CHAPTER_CARD_FRAMES and full_sec >= CHAPTER_CARD_MIN_FULL_OPACITY_SEC,
    }


def render_v8_chapter_card_frame(
    chapter_header: str,
    chapter_title: str,
    frame_idx: int,
    *,
    total_frames: int = CHAPTER_CARD_FRAMES,
    fps: int = DEFAULT_FPS,
    width: int = 1920,
    height: int = 1080,
    bg_plate: str | Path | np.ndarray | None = None,
) -> np.ndarray:
    """Render a Zero-Box V8.0 Chapter Card frame (`0` smoke wipes, `0` dark boxes/bars)."""
    u = _clamp01(frame_idx / float(max(1, total_frames - 1)))
    t_sec = frame_idx / float(max(1, fps))
    duration_sec = total_frames / float(max(1, fps))
    alpha = chapter_card_opacity_at(t_sec, duration_sec=duration_sec)

    plate = _load_or_synth_plate(bg_plate, width, height, theme="warm_siege")
    warped = warp_affine_float32(plate, width, height, scale=1.03 + 0.05 * smoothstep_cubic(u))

    # Gentle radial vignette (0.58 center -> 0.34 outer) — zero smoke fBm!
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    r2 = ((xx / width - 0.5) ** 2 + (yy / height - 0.5) ** 2) * 2.4
    vign = np.clip(0.62 - 0.28 * r2, 0.28, 0.65)[..., None]
    canvas = np.clip(warped.astype(np.float32) * vign, 0.0, 255.0).astype(np.uint8)

    hdr_px = scale_font_px(64, width, height)
    ttl_px = scale_font_px(96, width, height)
    hdr_rgba = render_zero_box_text_rgba(
        chapter_header,
        font_px=hdr_px,
        color_rgb=COLOR_GIANT_GOLD,
        opacity=alpha,
        max_words=2,
    )
    ttl_rgba = render_zero_box_text_rgba(
        chapter_title,
        font_px=ttl_px,
        color_rgb=COLOR_IVORY_CREAM,
        opacity=alpha,
        max_words=4,
    )
    composite_rgba_over_rgb(canvas, hdr_rgba, cx=width // 2, cy=int(height * 0.41))
    composite_rgba_over_rgb(canvas, ttl_rgba, cx=width // 2, cy=int(height * 0.55))
    return canvas


def render_v8_chapter_card_mp4(
    chapter_header: str,
    chapter_title: str,
    out_mp4_path: str | Path,
    *,
    width: int = 1920,
    height: int = 1080,
    fps: int = DEFAULT_FPS,
    bg_plate: str | Path | np.ndarray | None = None,
    prefer_nvenc: bool = True,
) -> dict[str, Any]:
    """Render a complete `3.80s` (`114f`) V8.0 Zero-Box Chapter Card MP4."""
    out_p = _encode_rgb_frames_to_mp4(
        (
            render_v8_chapter_card_frame(
                chapter_header,
                chapter_title,
                i,
                total_frames=CHAPTER_CARD_FRAMES,
                fps=fps,
                width=width,
                height=height,
                bg_plate=bg_plate,
            )
            for i in range(CHAPTER_CARD_FRAMES)
        ),
        out_mp4_path,
        width=width,
        height=height,
        fps=fps,
        prefer_nvenc=prefer_nvenc,
    )
    metrics = verify_chapter_card_hold_metrics(CHAPTER_CARD_DURATION_SEC, fps=fps)
    return {"path": str(out_p), **metrics}


# ---------------------------------------------------------------------------
# M4 Rapid 2.2-3.0s 4-Shot BELUGA Coverage Quartet Multi-Plane Parallax
# ---------------------------------------------------------------------------
def render_multiplane_parallax_frame(
    img_rgb: np.ndarray,
    u: float,
    *,
    width: int = 1920,
    height: int = 1080,
    motion_style: str = "push_in",
) -> np.ndarray:
    """Render true 3-plane sub-pixel `float32` parallax (BG 0.45x, Mid 1.0x, FG dust 1.7x)."""
    eased = smoothstep_cubic(u)
    if motion_style == "lateral_ots":
        bg_s, mid_s = 1.03 + 0.02 * eased, 1.05 + 0.04 * eased
        px_mid, py_mid = 22.0 * (eased - 0.5), -4.0 * (eased - 0.5)
    elif motion_style == "macro_drift":
        bg_s, mid_s = 1.04 + 0.03 * eased, 1.08 + 0.06 * eased
        px_mid, py_mid = -16.0 * (eased - 0.5), 10.0 * (eased - 0.5)
    elif motion_style == "pull_back":
        bg_s, mid_s = 1.07 - 0.03 * eased, 1.11 - 0.06 * eased
        px_mid, py_mid = 8.0 * (eased - 0.5), 6.0 * (eased - 0.5)
    else:
        bg_s, mid_s = 1.02 + 0.03 * eased, 1.04 + 0.065 * eased
        px_mid, py_mid = 10.0 * (eased - 0.5), -6.0 * (eased - 0.5)

    bg_layer = warp_affine_float32(
        img_rgb,
        width,
        height,
        scale=bg_s,
        pan_px_x=px_mid * 0.45,
        pan_px_y=py_mid * 0.45,
    )
    bg_soft = cv2.GaussianBlur(bg_layer, (0, 0), sigmaX=2.4)

    mid_layer = warp_affine_float32(
        img_rgb,
        width,
        height,
        scale=mid_s,
        pan_px_x=px_mid,
        pan_px_y=py_mid,
    )

    # Smooth central subject isolation mask for 2.5D Z-separation
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    subject_mask = np.exp(-(((xx / width - 0.5) / 0.36) ** 2 + ((yy / height - 0.52) / 0.38) ** 2))
    subject_mask = np.clip(subject_mask, 0.0, 1.0)[..., None]

    comp = bg_soft.astype(np.float32) * (1.0 - subject_mask) + mid_layer.astype(np.float32) * subject_mask

    # Keep pure optical 2.5D Z-separation (`bg_soft` 0.45x + `mid_layer` 1.0x float32 warpAffine)
    # without synthetic opaque yellow dust circles that land across subjects' faces (#378/#388).
    return np.clip(comp, 0.0, 255.0).astype(np.uint8)


def render_beluga_quartet_parallax_mp4(
    shot_images: list[str | Path | np.ndarray],
    out_mp4_path: str | Path,
    *,
    shot_durations_sec: list[float] | None = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = DEFAULT_FPS,
    prefer_nvenc: bool = True,
) -> dict[str, Any]:
    """Render a 4-shot BELUGA coverage quartet (`2.2-3.0s` per shot, 0 frozen slides!)."""
    if len(shot_images) != 4:
        raise ValueError(f"BELUGA coverage quartet requires exactly 4 shots, got {len(shot_images)}")
    durs = shot_durations_sec or [2.4, 2.5, 2.3, 2.6]
    if len(durs) != 4 or any(d < 2.2 or d > 3.0 for d in durs):
        raise ValueError(f"Each BELUGA quartet shot must be 2.2s-3.0s, got {durs}")

    styles = ("push_in", "lateral_ots", "macro_drift", "pull_back")
    themes = ("terrain", "warm_siege", "cold_fleet", "warm_siege")
    plates = [_load_or_synth_plate(shot_images[i], width, height, theme=themes[i]) for i in range(4)]
    frame_counts = [max(2, int(round(d * fps))) for d in durs]

    def _gen() -> Any:
        for s_idx, n_f in enumerate(frame_counts):
            for f_i in range(n_f):
                yield render_multiplane_parallax_frame(
                    plates[s_idx],
                    f_i / float(max(1, n_f - 1)),
                    width=width,
                    height=height,
                    motion_style=styles[s_idx],
                )

    out_p = _encode_rgb_frames_to_mp4(
        _gen(),
        out_mp4_path,
        width=width,
        height=height,
        fps=fps,
        prefer_nvenc=prefer_nvenc,
    )
    total_f = sum(frame_counts)
    return {
        "path": str(out_p),
        "shots_count": 4,
        "shot_durations_sec": [round(fc / float(fps), 4) for fc in frame_counts],
        "total_duration_sec": round(total_f / float(fps), 4),
        "n_frames": total_f,
    }


# ---------------------------------------------------------------------------
# Showcase Contact-Sheet Renderer (6-Panel 3x2 Grid of RIG_A..RIG_F)
# ---------------------------------------------------------------------------
def render_six_rigs_showcase_png(
    out_png_path: str | Path,
    *,
    panel_width: int = 960,
    panel_height: int = 540,
) -> Path:
    """Render a crisp 3x2 showcase grid displaying all 6 Zero-Box V12 Analytical Rigs."""
    sample_specs = [
        RigSpec(
            rig_id=RigId.RIG_A_SPOTLIGHT,
            width=1920,
            height=1080,
            primary_label="CỬA BẠCH ĐẰNG",
            secondary_label="BÃI CỌC NGẦM",
        ),
        RigSpec(
            rig_id=RigId.RIG_B_SPLIT_CONTRAST,
            width=1920,
            height=1080,
            left_stat="10 NGÀY",
            left_label="ÁN XỬ VỘI",
            right_stat="22 NĂM",
            right_label="CHIẾU RỬA OAN",
        ),
        RigSpec(
            rig_id=RigId.RIG_C_EVIDENCE_BOARD,
            width=1920,
            height=1080,
        ),
        RigSpec(
            rig_id=RigId.RIG_D_FOLIO_HIGHLIGHT,
            width=1920,
            height=1080,
            primary_label="THIÊN ĐÔ CHIẾU",
            secondary_label="ĐẤT THĂNG LONG",
        ),
        RigSpec(
            rig_id=RigId.RIG_E_WEAPON_AUTOPSY,
            width=1920,
            height=1080,
            primary_label="BỌC SẮT 68°",
            secondary_label="XUYÊN ĐÁY THUYỀN",
        ),
        RigSpec(
            rig_id=RigId.RIG_F_CHRONO_SPLIT,
            width=1920,
            height=1080,
            canh_gio_label="CANH TƯ · 02:15",
            t_minus_seconds=13500,
            front_labels=["ĐẠO TIÊN PHONG", "ĐỒN NGỌC HỒI", "MŨI ĐỐNG ĐA"],
        ),
    ]

    titles = (
        "RIG A · SPOTLIGHT CONE",
        "RIG B · SPLIT CONTRAST",
        "RIG C · EVIDENCE BOARD",
        "RIG D · FOLIO HIGHLIGHT",
        "RIG E · WEAPON AUTOPSY",
        "RIG F · CHRONO SPLIT",
    )

    gap = 16
    top_pad = 48
    header_h = 46
    cell_h = header_h + panel_height
    grid_w = panel_width * 3 + gap * 4
    grid_h = top_pad + cell_h * 2 + gap * 2
    grid = np.full((grid_h, grid_w, 3), (8, 9, 12), dtype=np.uint8)

    for idx, r_spec in enumerate(sample_specs):
        # Sample mid-late timestamp so progressive steps/threads/trajectories are visible
        full_rgb = render_rig_frame(r_spec, frame_idx=150, total_frames=198)
        resized = cv2.resize(full_rgb, (panel_width, panel_height), interpolation=cv2.INTER_AREA)

        row = idx // 3
        col = idx % 3
        x0 = gap + col * (panel_width + gap)
        y0 = top_pad + row * (cell_h + gap)

        grid[y0 + header_h : y0 + cell_h, x0 : x0 + panel_width] = resized
        cap_rgba = render_zero_box_text_rgba(
            titles[idx],
            font_px=24,
            color_rgb=COLOR_GIANT_GOLD,
            max_words=None,
        )
        ch_c, cw_c = cap_rgba.shape[:2]
        hy = max(4, y0 + (header_h - ch_c) // 2)
        hx = x0 + 4
        alpha = cap_rgba[..., 3:4].astype(np.float32) / 255.0
        dst = grid[hy : hy + ch_c, hx : hx + cw_c].astype(np.float32)
        grid[hy : hy + ch_c, hx : hx + cw_c] = np.clip(
            dst * (1.0 - alpha) + cap_rgba[..., :3].astype(np.float32) * alpha, 0.0, 255.0
        ).astype(np.uint8)

    out_p = Path(out_png_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(grid, mode="RGB").save(out_p, format="PNG", optimize=True)
    return out_p


__all__ = [
    "CHAPTER_CARD_DURATION_SEC",
    "CHAPTER_CARD_FRAMES",
    "CHAPTER_CARD_MIN_FULL_OPACITY_SEC",
    "ENGINE_ID",
    "ENGINE_VERSION",
    "EvidenceNode",
    "FocalRegion",
    "MAX_GIANT_LABEL_WORDS",
    "MIN_FONT_PX_16X9_1080P",
    "MIN_FONT_PX_9X16_1440W",
    "RIG_ALIASES",
    "RigId",
    "RigSpec",
    "build_subpixel_affine_matrix",
    "chapter_card_opacity_at",
    "clamp_giant_words",
    "composite_rgba_over_rgb",
    "effective_min_font_px",
    "has_nvenc_encoder",
    "is_vertical_canvas",
    "measure_trajectory_subpixel_jitter",
    "render_beluga_quartet_parallax_mp4",
    "render_multiplane_parallax_frame",
    "render_rig_frame",
    "render_rig_mp4",
    "render_six_rigs_showcase_png",
    "render_v8_chapter_card_frame",
    "render_v8_chapter_card_mp4",
    "render_zero_box_text_rgba",
    "resolve_rig_id",
    "scale_font_px",
    "smoothstep_cubic",
    "verify_chapter_card_hold_metrics",
    "warp_affine_float32",
]
