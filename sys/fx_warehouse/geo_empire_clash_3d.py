"""Cinema-Grade 3D Perspective Geo-Terrain & Faction Clash Animator.

Inspired by @MapEmpirex (3D territory expansion), @diathesuviet (Vietnamese
strategic geography), and @BalltlasHistory (heraldic faction token collision).

Renders 1920x1080@30fps `.mp4` clips with:
1. True 3D tilted camera fly-over via cv2.warpPerspective float32 homography.
2. Animated territory control tint + luminous frontline wave, tidal/chokepoint
   physics revealing submerged stake traps.
3. Circular/shield faction tokens with period heraldic emblems, animated
   fleet/column splines, kinetic impact shockwave rings, live counter tick-down.
4. Clean plug-in API: render_geo_empire_clash_mp4(scene_spec, out_mp4_path, ...)

Zero flat MS-Paint ovals. Zero static PowerPoint slides. Zero smoke wipes.
"""

from __future__ import annotations

import copy
import math
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
ENGINE_VERSION = "1.2.0"
SYS_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SYS_DIR / "assets"

FONT_CANDIDATES: tuple[str, ...] = (
    str(ASSETS_DIR / "fonts" / "su_ke_lai" / "BeVietnamPro-ExtraBold.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)

FONT_CONDENSED_CANDIDATES: tuple[str, ...] = (
    str(ASSETS_DIR / "fonts" / "su_ke_lai" / "BeVietnamPro-ExtraBold.ttf"),
    str(ASSETS_DIR / "fonts" / "chanh_niem_ke" / "Oswald-Bold.ttf"),
    str(ASSETS_DIR / "fonts" / "chanh_niem_ke" / "BarlowCondensed-ExtraBold.ttf"),
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}

# Faction heraldic palettes (period-accurate)
FACTION_PALETTES: dict[str, dict[str, tuple[int, int, int]]] = {
    "dai_viet": {
        "primary": (172, 36, 28),          # Vermilion-cinnabar lacquer
        "secondary": (236, 194, 110),      # Imperial burnished gold
        "emblem_fg": (250, 242, 226),      # Warm ivory
        "shield_rim": (200, 160, 80),      # Gold rim
        "glow": (255, 100, 60),            # Vermilion glow
        "trail": (188, 42, 32),            # Vermilion ribbon
    },
    "southern_han": {
        "primary": (40, 66, 88),           # Iron-indigo
        "secondary": (182, 200, 214),      # Oxidized silver
        "emblem_fg": (232, 240, 246),      # Silver-white
        "shield_rim": (120, 140, 160),     # Iron rim
        "glow": (100, 160, 220),           # Blue-steel glow
        "trail": (52, 84, 110),            # Indigo ribbon
    },
    "song_dynasty": {
        "primary": (45, 72, 95),           # Song steel-blue
        "secondary": (190, 205, 220),      # Silver-blue
        "emblem_fg": (240, 245, 250),      # Bright silver
        "shield_rim": (130, 150, 170),     # Iron-blue rim
        "glow": (110, 170, 230),           # Song glow
        "trail": (55, 90, 120),            # Steel ribbon
    },
    "yuan_mongol": {
        "primary": (50, 50, 60),           # Dark iron
        "secondary": (180, 170, 150),      # Steppe gold-iron
        "emblem_fg": (220, 215, 200),      # Bone-white
        "shield_rim": (140, 130, 110),     # Bronze-iron rim
        "glow": (200, 180, 100),           # Golden steppe glow
        "trail": (100, 90, 70),            # Dark bronze trail
    },
    "siamese": {
        "primary": (60, 50, 70),           # Dark purple-indigo
        "secondary": (200, 185, 160),      # Warm bronze
        "emblem_fg": (240, 235, 220),      # Ivory
        "shield_rim": (150, 130, 100),     # Bronze rim
        "glow": (180, 150, 80),            # Bronze glow
        "trail": (80, 65, 90),             # Purple trail
    },
    "qing_dynasty": {
        "primary": (55, 45, 60),           # Manchurian dark iron-purple
        "secondary": (195, 180, 155),      # Warm bone
        "emblem_fg": (230, 225, 210),      # Bone-white
        "shield_rim": (145, 125, 100),     # Iron-bronze rim
        "glow": (190, 160, 90),            # Golden glow
        "trail": (70, 55, 75),             # Dark trail
    },
}

# Sovereignty labels — always rendered when Vietnam regional sea is in view
SOVEREIGNTY_LABELS: tuple[dict[str, Any], ...] = (
    {"text": "HOÀNG SA", "lon": 112.0, "lat": 16.5},
    {"text": "TRƯỜNG SA", "lon": 114.0, "lat": 9.5},
)


# ---------------------------------------------------------------------------
# Math / Easing Helpers
# ---------------------------------------------------------------------------
def _clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if val < lo else (hi if val > hi else val)


def _ease_in_out_cubic(t: float) -> float:
    x = _clamp(t)
    return 4.0 * x * x * x if x < 0.5 else 1.0 - ((-2.0 * x + 2.0) ** 3) / 2.0


def _ease_out_cubic(t: float) -> float:
    u = 1.0 - _clamp(t)
    return 1.0 - u * u * u


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * _clamp(t)


def _lerp_color(
    c0: tuple[int, int, int], c1: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    f = _clamp(t)
    return (
        int(c0[0] + (c1[0] - c0[0]) * f),
        int(c0[1] + (c1[1] - c0[1]) * f),
        int(c0[2] + (c1[2] - c0[2]) * f),
    )


def _catmull_rom_spline(
    pts: list[tuple[float, float]], subdivisions: int = 16
) -> list[tuple[float, float]]:
    """Smooth Catmull-Rom spline through control points."""
    if len(pts) < 2:
        return list(pts)
    if len(pts) == 2:
        p0, p1 = pts[0], pts[1]
        return [
            (p0[0] + (p1[0] - p0[0]) * (i / subdivisions),
             p0[1] + (p1[1] - p0[1]) * (i / subdivisions))
            for i in range(subdivisions + 1)
        ]
    ext = [
        (2.0 * pts[0][0] - pts[1][0], 2.0 * pts[0][1] - pts[1][1]),
        *pts,
        (2.0 * pts[-1][0] - pts[-2][0], 2.0 * pts[-1][1] - pts[-2][1]),
    ]
    out: list[tuple[float, float]] = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for s in range(subdivisions):
            t = s / float(subdivisions)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                (2.0 * p1[0])
                + (-p0[0] + p2[0]) * t
                + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2.0 * p1[1])
                + (-p0[1] + p2[1]) * t
                + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
            )
            out.append((x, y))
    out.append(pts[-1])
    return out


def _sample_spline_at(
    pts: list[tuple[float, float]], progress: float
) -> tuple[tuple[float, float], float]:
    """Sample position and heading angle along polyline at arc-length progress [0..1]."""
    p = _clamp(progress)
    if len(pts) < 2:
        pt = pts[0] if pts else (0.5, 0.5)
        return pt, 0.0
    seg_lens = [
        math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        for i in range(len(pts) - 1)
    ]
    total = max(1e-6, sum(seg_lens))
    target = total * p
    acc = 0.0
    for i, sl in enumerate(seg_lens):
        if acc + sl >= target or i == len(seg_lens) - 1:
            frac = _clamp((target - acc) / max(1e-6, sl))
            px = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * frac
            py = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * frac
            ang = math.atan2(
                pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]
            )
            return (px, py), ang
        acc += sl
    return pts[-1], 0.0


# ---------------------------------------------------------------------------
# Font Utilities
# ---------------------------------------------------------------------------
def _get_font(
    size: int, condensed: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    key = ("condensed" if condensed else "display", max(9, size))
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    candidates = FONT_CONDENSED_CANDIDATES if condensed else FONT_CANDIDATES
    for p in candidates:
        if Path(p).is_file():
            fnt = ImageFont.truetype(p, max(9, size))
            _FONT_CACHE[key] = fnt
            return fnt
    fnt = ImageFont.load_default()
    _FONT_CACHE[key] = fnt
    return fnt


def _composite_feathered_scrim(
    pil_img: Image.Image,
    x0: int,
    y0: int,
    content_w: int,
    content_h: int,
    alpha_max: int = 135,
) -> Image.Image:
    """Composite a 100% seamless Gaussian-feathered shadow cloud (zero clipped edges)."""
    blur_r = max(8, int(content_h * 0.45))
    margin = blur_r * 3
    patch_w = max(8, content_w + margin * 2)
    patch_h = max(8, content_h + margin * 2)

    mask = Image.new("L", (patch_w, patch_h), 0)
    ImageDraw.Draw(mask).ellipse(
        [margin, margin, margin + content_w, margin + content_h],
        fill=int(_clamp(alpha_max, 0, 255)),
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_r))

    overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    scrim_rgba = Image.merge("RGBA", (
        Image.new("L", (patch_w, patch_h), 6),
        Image.new("L", (patch_w, patch_h), 8),
        Image.new("L", (patch_w, patch_h), 12),
        mask,
    ))
    overlay.paste(scrim_rgba, (int(x0 - margin), int(y0 - margin)))
    return Image.alpha_composite(pil_img.convert("RGBA"), overlay).convert("RGB")


# ---------------------------------------------------------------------------
# 3D Perspective Camera (cv2.warpPerspective float32 homography)
# ---------------------------------------------------------------------------
class PerspectiveCamera3D:
    """3D tilted camera projecting a large terrain canvas into screen space.

    Uses cv2.warpPerspective with float32 homography for sub-pixel smooth
    fly-over (zero integer jitter). Animates pitch (32°->48°), altitude zoom,
    and pan tracking.
    """

    def __init__(
        self,
        canvas_w: int,
        canvas_h: int,
        screen_w: int = 1920,
        screen_h: int = 1080,
    ) -> None:
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.screen_w = screen_w
        self.screen_h = screen_h

    def compute_homography(
        self,
        cam_cx: float,
        cam_cy: float,
        pitch_deg: float,
        zoom: float,
    ) -> np.ndarray:
        """Compute 3x3 homography matrix for perspective warp.

        cam_cx, cam_cy: normalized [0..1] look-at point on the canvas.
        pitch_deg: tilt angle (0=top-down, 90=horizon). Clamped 20..70.
        zoom: magnification factor (1.0 = full canvas visible).
        """
        pitch = _clamp(float(pitch_deg), 20.0, 70.0)
        z = max(0.3, float(zoom))
        cx_px = float(cam_cx) * self.canvas_w
        cy_px = float(cam_cy) * self.canvas_h

        # Virtual camera: scale then perspective tilt
        sw, sh = float(self.screen_w), float(self.screen_h)
        cw, _ch = float(self.canvas_w), float(self.canvas_h)

        # Scale to fit zoom level
        base_scale = (sw / cw) * z
        sx = base_scale
        sy = base_scale

        # Build transform: translate center to origin, scale, perspective, translate to screen center
        pitch_rad = math.radians(pitch)
        cos_p = math.cos(pitch_rad)
        sin_p = math.sin(pitch_rad)

        # Perspective foreshortening along Y axis
        # This creates the 3D tilt effect without full 3D projection
        # Perspective foreshortening params (used implicitly via getPerspectiveTransform)
        _ = cos_p, sin_p * 0.0004 / max(1.0, z)

        # Source quad: rectangle around look-at point on canvas
        half_w = sw / (2.0 * sx)
        half_h = sh / (2.0 * sy)

        src = np.array([
            [cx_px - half_w, cy_px - half_h],
            [cx_px + half_w, cy_px - half_h],
            [cx_px + half_w, cy_px + half_h],
            [cx_px - half_w, cy_px + half_h],
        ], dtype=np.float32)

        # Destination quad: screen rectangle with perspective tilt
        # Top edge pinched inward (3D convergence), bottom normal
        pinch_top = sw * 0.08 * (pitch / 70.0)  # more tilt = more pinch
        stretch_bottom = sh * 0.03 * (pitch / 70.0)

        dst = np.array([
            [pinch_top, -stretch_bottom * 0.5],
            [sw - pinch_top, -stretch_bottom * 0.5],
            [sw, sh + stretch_bottom],
            [0.0, sh + stretch_bottom],
        ], dtype=np.float32)

        # Compute perspective transform
        H = cv2.getPerspectiveTransform(src, dst)
        return H.astype(np.float32)

    def warp_canvas(
        self,
        canvas: np.ndarray,
        cam_cx: float,
        cam_cy: float,
        pitch_deg: float,
        zoom: float,
        bg_color: tuple[int, int, int] = (8, 11, 14),
    ) -> np.ndarray:
        """Warp the full terrain canvas through 3D perspective into screen space."""
        H = self.compute_homography(cam_cx, cam_cy, pitch_deg, zoom)
        return cv2.warpPerspective(
            canvas,
            H,
            (self.screen_w, self.screen_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=bg_color,
        )

    def project_point(
        self,
        canvas_nx: float,
        canvas_ny: float,
        cam_cx: float,
        cam_cy: float,
        pitch_deg: float,
        zoom: float,
    ) -> tuple[float, float]:
        """Project a normalized canvas point to screen pixel coordinates."""
        H = self.compute_homography(cam_cx, cam_cy, pitch_deg, zoom)
        pt = np.array([[[
            canvas_nx * self.canvas_w,
            canvas_ny * self.canvas_h
        ]]], dtype=np.float32)
        projected = cv2.perspectiveTransform(pt, H)
        return float(projected[0, 0, 0]), float(projected[0, 0, 1])


# ---------------------------------------------------------------------------
# Terrain Canvas Generator (procedural for offline use)
# ---------------------------------------------------------------------------
def _generate_procedural_terrain(
    width: int,
    height: int,
    rivers: list[dict[str, Any]] | None = None,
    ridges: list[dict[str, Any]] | None = None,
    sea_region: dict[str, Any] | None = None,
    seed: int = 42,
) -> np.ndarray:
    """Generate a procedural terrain canvas (RGB uint8) with rivers, ridges, and sea.

    Uses Perlin-like fractal noise for topography, blue channels for water,
    brown/green for land. No external tile downloads needed for fast tests.
    """
    rng = np.random.default_rng(seed)
    h, w = height, width

    # Base terrain: multi-octave fractal noise
    terrain = np.zeros((h, w), dtype=np.float32)
    for octave in range(5):
        freq = 2.0 ** octave
        amp = 1.0 / (1.0 + octave * 1.5)
        noise = rng.random((int(h / freq) + 2, int(w / freq) + 2)).astype(np.float32)
        noise_up = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
        terrain += noise_up * amp
    terrain = (terrain - terrain.min()) / max(1e-6, terrain.max() - terrain.min())

    # Apply ridges (fast coarse grid + bicubic upscale)
    if ridges:
        gh = max(16, h // 4)
        gw = max(16, w // 4)
        yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
        xx_n = xx / float(gw)
        yy_n = yy / float(gh)
        for ridge in ridges:
            pts = ridge.get("points", [])
            height_val = float(ridge.get("height", 0.6))
            sigma = float(ridge.get("sigma", 0.08))
            ridge_low = np.zeros((gh, gw), dtype=np.float32)
            inv_2s2 = 1.0 / max(1e-6, 2.0 * sigma * sigma)
            for px, py in pts:
                d2 = (xx_n - float(px)) ** 2 + (yy_n - float(py)) ** 2
                ridge_low = np.maximum(ridge_low, np.exp(-d2 * inv_2s2))
            ridge_up = cv2.resize(ridge_low, (w, h), interpolation=cv2.INTER_CUBIC)
            terrain = np.clip(terrain + ridge_up * height_val * 0.4, 0, 1)

    # Colorize terrain
    # Dark green lowlands -> brown hills -> gray-white peaks
    r = np.clip(0.18 + terrain * 0.55, 0, 1)
    g = np.clip(0.22 + terrain * 0.35 - terrain ** 2 * 0.2, 0, 1)
    b = np.clip(0.12 + terrain * 0.25, 0, 1)

    canvas = np.stack([r, g, b], axis=-1)

    # Sea region
    if sea_region:
        sea_mask = np.zeros((h, w), dtype=np.float32)
        sx0 = int(sea_region.get("x0", 0.6) * w)
        sy0 = int(sea_region.get("y0", 0.0) * h)
        sx1 = int(sea_region.get("x1", 1.0) * w)
        sy1 = int(sea_region.get("y1", 1.0) * h)
        sea_mask[max(0, sy0):min(h, sy1), max(0, sx0):min(w, sx1)] = 1.0
        sea_blur = cv2.GaussianBlur(sea_mask, (0, 0), sigmaX=w * 0.03)
        sea_color = np.array([0.03, 0.05, 0.12], dtype=np.float32)
        canvas = canvas * (1.0 - sea_blur[..., None]) + sea_color * sea_blur[..., None]

    # Rivers
    for river in (rivers or []):
        pts = river.get("points", [])
        widths = river.get("widths", [0.01] * len(pts))
        if len(pts) < 2:
            continue
        smooth = _catmull_rom_spline(pts, subdivisions=20)
        for i in range(len(smooth) - 1):
            x0 = int(smooth[i][0] * w)
            y0 = int(smooth[i][1] * h)
            x1 = int(smooth[i + 1][0] * w)
            y1 = int(smooth[i + 1][1] * h)
            frac = i / max(1, len(smooth) - 1)
            # Interpolate width
            if len(widths) > 1:
                seg_idx = min(int(frac * (len(widths) - 1)), len(widths) - 2)
                seg_frac = frac * (len(widths) - 1) - seg_idx
                rw = widths[seg_idx] + (widths[min(seg_idx + 1, len(widths) - 1)] - widths[seg_idx]) * seg_frac
            else:
                rw = widths[0]
            thickness = max(2, int(rw * w * 0.5))
            # Draw on float canvas
            river_color = (0.04, 0.08, 0.18)
            temp = (canvas * 255).astype(np.uint8)
            cv2.line(temp, (x0, y0), (x1, y1), tuple(int(c * 255) for c in river_color), thickness, cv2.LINE_AA)
            canvas = temp.astype(np.float32) / 255.0

    return np.clip(canvas * 255, 0, 255).astype(np.uint8)


# GIS bbox presets for real WGS84 / ESRI World Imagery + Hillshade relief terrain
_GIS_BBOX_PRESETS: dict[str, dict[str, Any]] = {
    "bach_dang": {
        "lon_min": 106.55, "lat_min": 20.75,
        "lon_max": 107.05, "lat_max": 21.05,
        "zoom_tile": 12,
        "region_key": "bach_dang_estuary_z12",
    },
    "nhu_nguyet": {
        "lon_min": 105.90, "lat_min": 21.10,
        "lon_max": 106.40, "lat_max": 21.45,
        "zoom_tile": 12,
        "region_key": "nhu_nguyet_river_z12",
    },
    "northern_dai_viet": {
        "lon_min": 104.5, "lat_min": 18.5,
        "lon_max": 110.0, "lat_max": 23.5,
        "zoom_tile": 7,
        "prebaked_key": "east_asia_vietnam",
        "region_key": "northern_dai_viet",
    },
    "east_asia_vietnam": {
        "lon_min": 104.0, "lat_min": 8.0,
        "lon_max": 116.5, "lat_max": 23.5,
        "zoom_tile": 6,
        "prebaked_key": "east_asia_vietnam",
        "region_key": "east_asia_vietnam",
    },
}

_TERRAIN_CANVAS_CACHE: dict[tuple[Any, ...], np.ndarray] = {}


def _demodernize_esri_relief(imagery_rgb: np.ndarray, hillshade_rgb: np.ndarray) -> np.ndarray:
    """Fuse z=12 ESRI World Imagery + Hillshade into a de-modernized Ancient Vietnam relief plate.

    Detects BOTH clear coastal sea and silty/turbid estuary channels (Bạch Đằng / Sông Chanh)
    via local texture smoothness + hillshade flatness + connected-component hydrography cleanup,
    rendering crisp deep obsidian-navy water against warm olive-parchment 3D karst relief
    (zero modern urban grids, zero harsh yellow Sobel contour blobs).
    Returns RGB uint8 array of shape (H, W, 3).
    """
    h, w = imagery_rgb.shape[:2]
    img_f = imagery_rgb.astype(np.float32) / 255.0
    hs_l = hillshade_rgb.astype(np.float32).mean(axis=-1) / 255.0

    r_ch, g_ch, b_ch = img_f[..., 0], img_f[..., 1], img_f[..., 2]
    lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch

    # 1. Local texture smoothness (estuary/sea water is smooth; urban/forest/karst is textured)
    s_l = max(1.5, w / 720.0)
    blur_l = cv2.GaussianBlur(lum, (0, 0), sigmaX=s_l)
    local_std = np.sqrt(
        np.maximum(cv2.GaussianBlur((lum - blur_l) ** 2, (0, 0), sigmaX=s_l * 1.4), 0.0)
    )

    # 2. Hillshade flatness (water is completely flat; karsts/ridges have steep slope gradients)
    hs_grad = np.hypot(
        cv2.Sobel(hs_l, cv2.CV_32F, 1, 0, ksize=3),
        cv2.Sobel(hs_l, cv2.CV_32F, 0, 1, ksize=3),
    )
    hs_flat = (hs_l > 0.94) & (hs_grad < 0.03)

    # 3. Clear coastal sea + silty/turbid river channel detection
    clear_water = (b_ch + 0.40 * g_ch - 1.12 * r_ch) > 0.03
    silty_water = (
        (local_std < 0.029)
        & (lum > 0.18)
        & (lum < 0.62)
        & ((r_ch - g_ch) < 0.05)
        & ((r_ch - b_ch) < 0.14)
    )
    raw_water = (hs_flat & (clear_water | silty_water)).astype(np.uint8) * 255

    # Morphological cleanup + connected-component filter to keep continuous river/sea channels
    k_o_sz = max(3, int(round(w / 360.0)) | 1)
    k_c_sz = max(5, int(round(w / 135.0)) | 1)
    clean_water = cv2.morphologyEx(
        raw_water, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_o_sz, k_o_sz))
    )
    clean_water = cv2.morphologyEx(
        clean_water, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_c_sz, k_c_sz))
    )

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(clean_water, connectivity=8)
    min_area = max(300, int(h * w * 0.0028))
    major_water = np.zeros_like(clean_water)
    for lbl in range(1, num_labels):
        if stats[lbl, cv2.CC_STAT_AREA] >= min_area:
            major_water[labels == lbl] = 255
    water_mask = cv2.GaussianBlur(
        major_water.astype(np.float32) / 255.0, (0, 0), sigmaX=max(1.2, w / 1050.0)
    )

    # 4. De-modernized ancient parchment-olive land driven by crisp z=12 karst hillshade
    img_ancient = cv2.GaussianBlur(img_f, (0, 0), sigmaX=max(3.5, w / 230.0))
    veg = np.clip((img_ancient[..., 1] - img_ancient[..., 0]) * 3.0 + 0.35, 0.0, 1.0)
    hs_relief = np.clip((hs_l - 0.52) / 0.46, 0.0, 1.0)
    hs_detail = hs_l - cv2.GaussianBlur(hs_l, (0, 0), sigmaX=max(4.0, w / 180.0))
    shade = np.clip(0.55 + 0.42 * (hs_relief - 0.85) + 1.55 * hs_detail, 0.12, 1.0)

    land_r = np.clip(0.26 + 0.36 * shade - 0.06 * veg, 0.0, 1.0)
    land_g = np.clip(0.28 + 0.33 * shade + 0.03 * veg, 0.0, 1.0)
    land_b = np.clip(0.19 + 0.21 * shade - 0.04 * veg, 0.0, 1.0)
    land_rgb = np.stack([land_r, land_g, land_b], axis=-1)

    # 5. Deep tactical obsidian-navy river & sea bathymetry with smooth coastal shoal gradient
    shoal = cv2.GaussianBlur(1.0 - water_mask, (0, 0), sigmaX=max(5.0, w / 115.0)) * water_mask
    water_r = np.clip(0.032 + 0.068 * shoal, 0.0, 1.0)
    water_g = np.clip(0.082 + 0.122 * shoal, 0.0, 1.0)
    water_b = np.clip(0.155 + 0.150 * shoal, 0.0, 1.0)
    water_rgb = np.stack([water_r, water_g, water_b], axis=-1)

    # Subtle dark bank occlusion at water-land shoreline (zero harsh yellow halo)
    bank_edge = np.clip(water_mask * (1.0 - water_mask) * 4.0, 0.0, 1.0)[..., None]
    wm = water_mask[..., None]
    fused = (land_rgb * (1.0 - wm) + water_rgb * wm) * (1.0 - 0.24 * bank_edge)
    return np.clip(np.round(fused * 255.0), 0, 255).astype(np.uint8)


def _load_gis_terrain_canvas(
    width: int,
    height: int,
    gis_bbox: dict[str, Any] | str | None = None,
    terrain_cfg: dict[str, Any] | None = None,
    seed: int = 42,
    use_gis: bool = True,
) -> np.ndarray:
    """Load real WGS84/ESRI relief terrain via fx_warehouse.gis_map_baker.

    Priority:
      1. Real ESRI World Imagery + World Hillshade tiles (or prebaked .npz) via gis_map_baker.
      2. Offline test fallback: _generate_procedural_terrain when use_gis=False or unavailable.
    """
    bbox_key = ""
    bbox: dict[str, Any] | None = None
    if use_gis and gis_bbox is not None:
        if isinstance(gis_bbox, str):
            bbox_key = gis_bbox
            bbox = _GIS_BBOX_PRESETS.get(gis_bbox)
        elif isinstance(gis_bbox, dict):
            bbox = dict(gis_bbox)
            bbox_key = str(bbox.get("region_key", (
                bbox.get("lon_min"), bbox.get("lat_min"),
                bbox.get("lon_max"), bbox.get("lat_max"),
            )))

    cache_key = (
        bbox_key if bbox else f"proc:{repr(terrain_cfg)}",
        int(width),
        int(height),
        int(seed),
        bool(use_gis),
    )
    if cache_key in _TERRAIN_CANVAS_CACHE:
        return _TERRAIN_CANVAS_CACHE[cache_key].copy()

    if use_gis and bbox:
        try:
            from fx_warehouse.gis_map_baker import (
                ESRI_HILLSHADE_URL,
                ESRI_IMAGERY_URL,
                colorize_relief_plate,
                compute_isotropic_merc_bounds,
                load_prebaked_region,
                lonlat_to_region_norm,
                stitch_esri_tiles,
            )

            prebaked_key = bbox.get("prebaked_key")
            if prebaked_key:
                npz_data = load_prebaked_region(str(prebaked_key), auto_bake=False)
                full_plate = colorize_relief_plate(npz_data, territories_dict={"VNM": "amber"}, alpha=0.55)
                ph, pw = full_plate.shape[:2]
                u0, v1 = lonlat_to_region_norm(float(bbox["lon_min"]), float(bbox["lat_min"]), npz_data["meta"])
                u1, v0 = lonlat_to_region_norm(float(bbox["lon_max"]), float(bbox["lat_max"]), npz_data["meta"])
                x0 = max(0, min(pw - 2, int(u0 * pw)))
                x1 = max(x0 + 2, min(pw, int(u1 * pw)))
                y0 = max(0, min(ph - 2, int(v0 * ph)))
                y1 = max(y0 + 2, min(ph, int(v1 * ph)))
                cropped = full_plate[y0:y1, x0:x1]
                plate = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LANCZOS4)
            else:
                z_tile = int(bbox.get("zoom_tile", 12))
                # Stitch at crisp 2560x1440 tile grid then upscale Lanczos if canvas is 4K
                stitch_w = min(int(width), 2560)
                stitch_h = min(int(height), 1440)
                mb = compute_isotropic_merc_bounds(
                    float(bbox["lon_min"]), float(bbox["lon_max"]),
                    float(bbox["lat_min"]), float(bbox["lat_max"]),
                    stitch_w, stitch_h,
                )
                imagery_rgb = stitch_esri_tiles("esri_world_imagery", ESRI_IMAGERY_URL, mb, z_tile, stitch_w, stitch_h)
                hillshade_rgb = stitch_esri_tiles("esri_world_hillshade", ESRI_HILLSHADE_URL, mb, z_tile, stitch_w, stitch_h)
                plate = _demodernize_esri_relief(imagery_rgb, hillshade_rgb)
                if plate.shape[:2] != (height, width):
                    plate = cv2.resize(plate, (width, height), interpolation=cv2.INTER_LANCZOS4)

            if len(_TERRAIN_CANVAS_CACHE) > 16:
                _TERRAIN_CANVAS_CACHE.clear()
            _TERRAIN_CANVAS_CACHE[cache_key] = plate
            return plate.copy()
        except Exception:
            pass  # Offline test fallback to procedural terrain

    cfg = terrain_cfg or {}
    proc_plate = _generate_procedural_terrain(
        width, height,
        rivers=cfg.get("rivers"),
        ridges=cfg.get("ridges"),
        sea_region=cfg.get("sea_region"),
        seed=seed,
    )
    if len(_TERRAIN_CANVAS_CACHE) > 16:
        _TERRAIN_CANVAS_CACHE.clear()
    _TERRAIN_CANVAS_CACHE[cache_key] = proc_plate
    return proc_plate.copy()


# ---------------------------------------------------------------------------
# Territory Frontline Rendering
# ---------------------------------------------------------------------------
def _draw_territory_tint(
    canvas: np.ndarray,
    territory_polygons: list[dict[str, Any]],
    t_norm: float,
) -> np.ndarray:
    """Apply animated territory control tint + organic curved luminous frontline wave."""
    if not territory_polygons:
        return canvas
    h, w = canvas.shape[:2]
    out = canvas.astype(np.float32) / 255.0

    # Compute smooth masks on 1/4-scale grid then bilinear-upscale (40x faster, sub-pixel smooth)
    gh = max(16, h // 4)
    gw = max(16, w // 4)
    yy_n = np.linspace(0.0, 1.0, gh, dtype=np.float32)[:, None]
    xx_n = np.linspace(0.0, 1.0, gw, dtype=np.float32)[None, :]

    for terr in territory_polygons:
        faction = terr.get("faction", "dai_viet")
        palette = FACTION_PALETTES.get(faction, FACTION_PALETTES["dai_viet"])
        region = terr.get("region", {})
        adv_s = float(terr.get("advance_start", 0.3))
        adv_e = float(terr.get("advance_end", 0.7))
        advance = _clamp(adv_s + (adv_e - adv_s) * _ease_in_out_cubic(t_norm))

        rx0 = float(region.get("x0", 0.0))
        ry0 = float(region.get("y0", 0.0))
        rx1 = float(region.get("x1", 0.5))
        ry1 = float(region.get("y1", 1.0))

        # Organic curved frontline wave along Y (MapEmpirex style, zero straight box edge)
        wave_offset = 0.016 * np.sin(yy_n * math.pi * 2.6 + float(t_norm) * 4.0)
        front_x = rx0 + (rx1 - rx0) * advance + wave_offset

        # Smooth sigmoid transition at region bounds and advancing frontline
        feather = 0.022
        in_y = (1.0 / (1.0 + np.exp(-(yy_n - ry0) / feather))) * (
            1.0 / (1.0 + np.exp(-(ry1 - yy_n) / feather))
        )
        in_x_left = 1.0 / (1.0 + np.exp(-(xx_n - rx0) / feather))
        in_front = 1.0 / (1.0 + np.exp(-(front_x - xx_n) / 0.016))

        combined_low = (in_y * in_x_left * in_front).astype(np.float32)
        combined = cv2.resize(combined_low, (w, h), interpolation=cv2.INTER_LINEAR)

        tint_color = np.array(palette["primary"], dtype=np.float32) / 255.0
        tint_strength = 0.25
        out = out * (1.0 - combined[..., None] * tint_strength) + (
            tint_color[None, None, :] * (combined[..., None] * tint_strength)
        )

        # Luminous pulsing frontline wave ribbon along front_x
        glow_color = np.array(palette["glow"], dtype=np.float32) / 255.0
        edge_sigma = 0.0075
        glow_low = (
            in_y * np.exp(-((xx_n - front_x) ** 2) / (2.0 * edge_sigma * edge_sigma))
        ).astype(np.float32)
        glow_strip = cv2.resize(glow_low, (w, h), interpolation=cv2.INTER_LINEAR)
        pulse = 0.65 + 0.35 * math.sin(float(t_norm) * math.pi * 6.0)
        out = np.clip(
            out + glow_strip[..., None] * glow_color[None, None, :] * (pulse * 0.72),
            0.0,
            1.0,
        )

    return np.clip(out * 255.0, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Tidal / Chokepoint Physics
# ---------------------------------------------------------------------------
def _draw_tidal_physics(
    canvas: np.ndarray,
    tidal_spec: dict[str, Any] | None,
    t_norm: float,
) -> np.ndarray:
    """Render tidal ebb shoal exposure and submerged iron-tipped stake traps (RGB canvas).

    Zero solid rectangular bars/boxes (V7 Law A).
    """
    if not tidal_spec or not tidal_spec.get("enabled"):
        return canvas

    h, w = canvas.shape[:2]
    out = canvas.copy()

    start_m = float(tidal_spec.get("start_m", 1.4))
    end_m = float(tidal_spec.get("end_m", -3.8))
    threshold_m = float(tidal_spec.get("stake_threshold_m", -1.2))
    current_m = _lerp(start_m, end_m, _ease_in_out_cubic(t_norm))
    ebb_frac = _clamp((start_m - current_m) / max(0.1, start_m - end_m))

    stake_beds = tidal_spec.get("stake_beds", [])
    # Subtle muddy shoal exposure halo along stake beds as tide recedes
    if ebb_frac > 0.05 and stake_beds:
        gh, gw = max(16, h // 4), max(16, w // 4)
        shoal_low = np.zeros((gh, gw), dtype=np.float32)
        for bed in stake_beds:
            p0 = bed.get("p0", (0.4, 0.5))
            p1 = bed.get("p1", (0.6, 0.5))
            cv2.line(
                shoal_low,
                (int(p0[0] * gw), int(p0[1] * gh)),
                (int(p1[0] * gw), int(p1[1] * gh)),
                1.0,
                max(3, int(gh * 0.045)),
                cv2.LINE_AA,
            )
        shoal_low = cv2.GaussianBlur(shoal_low, (0, 0), sigmaX=max(2.0, gw * 0.015))
        shoal_mask = cv2.resize(shoal_low, (w, h), interpolation=cv2.INTER_LINEAR)
        mud_rgb = np.array([78.0, 62.0, 42.0], dtype=np.float32)
        alpha_m = (shoal_mask * ebb_frac * 0.38)[..., None]
        out = np.clip(out.astype(np.float32) * (1.0 - alpha_m) + mud_rgb * alpha_m, 0, 255).astype(np.uint8)

    # Iron-tipped wooden stake field visualization
    show_xray = bool(tidal_spec.get("submerged_xray", False))
    if current_m < threshold_m or show_xray:
        if current_m < threshold_m:
            reveal_progress = _clamp((threshold_m - current_m) / max(0.1, threshold_m - end_m))
        else:
            reveal_progress = 0.45
        for bed in stake_beds:
            p0 = bed.get("p0", (0.4, 0.5))
            p1 = bed.get("p1", (0.6, 0.5))
            rows = int(bed.get("rows", 3))
            count = int(bed.get("count", 8))
            for row in range(rows):
                for col in range(count):
                    frac_x = col / max(1, count - 1)
                    frac_y = (row / max(1, rows - 1) - 0.5) * 0.032
                    sx = int(_lerp(p0[0], p1[0], frac_x) * w)
                    sy = int((_lerp(p0[1], p1[1], frac_x) + frac_y) * h)
                    if 0 <= sx < w and 0 <= sy < h:
                        stake_len = max(6, int(h * 0.017 * (0.35 + 0.65 * reveal_progress)))
                        base_hw = max(2, int(w * 0.0014))
                        mid_hw = max(1, int(w * 0.00095))
                        lean_x = max(1, int(stake_len * 0.22))
                        tip_x = sx + lean_x
                        tip_y = sy - stake_len
                        collar_y = sy - int(stake_len * 0.62)
                        collar_x = sx + int(lean_x * 0.62)

                        # Thin elliptical water-runoff foam ripple at stake base
                        rip_rx = max(3, int(w * 0.0030 * (0.65 + 0.35 * reveal_progress)))
                        rip_ry = max(2, int(rip_rx * 0.45))
                        cv2.ellipse(
                            out, (sx, sy + 1), (rip_rx, rip_ry), 0, 0, 360,
                            (95, 138, 168), max(1, int(w * 0.0005)), cv2.LINE_AA,
                        )

                        # Cast dark water shadow behind stake
                        sh_pts = np.array([
                            [sx - base_hw, sy],
                            [sx + base_hw, sy],
                            [sx - int(stake_len * 0.55), sy + int(stake_len * 0.28)],
                        ], dtype=np.int32)
                        cv2.fillPoly(out, [sh_pts], (14, 24, 34), cv2.LINE_AA)

                        # Tapered charred ironwood log body (RGB dark umber + ochre wood rim)
                        wood_pts = np.array([
                            [sx - base_hw, sy],
                            [sx + base_hw, sy],
                            [collar_x + mid_hw, collar_y],
                            [collar_x - mid_hw, collar_y],
                        ], dtype=np.int32)
                        cv2.fillPoly(out, [wood_pts], (66, 42, 24), cv2.LINE_AA)
                        cv2.line(
                            out, (sx + base_hw, sy), (collar_x + mid_hw, collar_y),
                            (118, 82, 48), max(1, int(w * 0.0004)), cv2.LINE_AA,
                        )

                        # Sharp tapered forged-iron triangular spearhead tip (zero round dots!)
                        iron_pts = np.array([
                            [collar_x - mid_hw - 1, collar_y + 1],
                            [collar_x + mid_hw + 1, collar_y + 1],
                            [tip_x, tip_y],
                        ], dtype=np.int32)
                        cv2.fillPoly(out, [iron_pts], (178, 188, 198), cv2.LINE_AA)
                        # Razor steel specular glint along leading edge
                        cv2.line(
                            out, (collar_x + mid_hw, collar_y), (tip_x, tip_y),
                            (242, 246, 250), max(1, int(w * 0.0005)), cv2.LINE_AA,
                        )

    return out


def _draw_tidal_hud(
    canvas: np.ndarray,
    tidal_spec: dict[str, Any] | None,
    t_norm: float,
) -> np.ndarray:
    """Draw floating tidal elevation & stake emergence readout (BGR canvas, zero boxes)."""
    if not tidal_spec or not tidal_spec.get("enabled"):
        return canvas

    h, w = canvas.shape[:2]
    start_m = float(tidal_spec.get("start_m", 1.4))
    end_m = float(tidal_spec.get("end_m", -3.8))
    threshold_m = float(tidal_spec.get("stake_threshold_m", -1.2))
    current_m = _lerp(start_m, end_m, _ease_in_out_cubic(t_norm))

    sign = "+" if current_m >= 0 else ""
    state_txt = "CỌC SẮT ĐÃ LỘ" if current_m < threshold_m else "TRIỀU ĐANG RÚT"
    readout = f"MỰC NƯỚC {sign}{current_m:.1f}M • {state_txt}"

    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    font_size = max(11, int(h * 0.017))
    fnt = _get_font(font_size, condensed=True)
    draw = ImageDraw.Draw(pil_img)
    bbox = draw.textbbox((0, 0), readout, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    tx = int(w * 0.04)
    ty = int(h * 0.78)

    # Seamless feathered Gaussian shadow scrim (zero clipped edges)
    pad = max(6, int(h * 0.008))
    pil_img = _composite_feathered_scrim(
        pil_img, tx - pad, ty - pad // 2, tw + pad * 2, th + pad, alpha_max=145
    )
    draw = ImageDraw.Draw(pil_img)

    txt_color = (245, 195, 110) if current_m < threshold_m else (175, 215, 235)
    draw.text((tx + 1, ty + 1), readout, fill=(0, 0, 0), font=fnt)
    draw.text((tx, ty), readout, fill=txt_color, font=fnt)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Faction Shield / Heraldic Token Rendering
# ---------------------------------------------------------------------------
def _rgb_to_bgr(c: tuple[int, int, int]) -> tuple[int, int, int]:
    return (int(c[2]), int(c[1]), int(c[0]))


def _draw_faction_token(
    canvas: np.ndarray,
    cx: int,
    cy: int,
    radius: int,
    faction: str,
    badge_text: str,
    damaged: bool = False,
    pulse_phase: float = 0.0,
) -> np.ndarray:
    """Draw a crisp circular heraldic faction token with Đông Sơn / period emblem (BGR canvas)."""
    out = canvas.copy()
    palette = FACTION_PALETTES.get(faction, FACTION_PALETTES["dai_viet"])

    # Outer shield glow ring
    glow_r = int(radius * 1.4)
    glow_alpha = 0.3 + 0.15 * math.sin(pulse_phase * math.pi * 2.0)
    overlay = out.copy()
    cv2.circle(overlay, (cx, cy), glow_r, _rgb_to_bgr(palette["glow"]), -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, glow_alpha, out, 1.0 - glow_alpha, 0, out)

    # Shield body (filled circle)
    body_bgr = _rgb_to_bgr(palette["primary"]) if not damaged else (30, 30, 85)
    cv2.circle(out, (cx, cy), radius, body_bgr, -1, cv2.LINE_AA)

    # Shield rim
    rim_thickness = max(2, int(radius * 0.12))
    cv2.circle(out, (cx, cy), radius, _rgb_to_bgr(palette["shield_rim"]), rim_thickness, cv2.LINE_AA)

    # Inner war-drum / heraldic ring
    inner_r = max(3, int(radius * 0.62))
    cv2.circle(out, (cx, cy), inner_r, _rgb_to_bgr(palette["secondary"]), max(1, int(radius * 0.06)), cv2.LINE_AA)

    # Period-accurate emblem: Đông Sơn bronze drum concentric sunburst for Đại Việt
    emblem_bgr = _rgb_to_bgr(palette["emblem_fg"])
    sym_r = max(2, int(inner_r * 0.78))
    if faction == "dai_viet":
        # Concentric Đông Sơn bronze drum tympanum rings + 12 radial sunburst rays
        cv2.circle(out, (cx, cy), sym_r, emblem_bgr, max(1, int(radius * 0.04)), cv2.LINE_AA)
        core_r = max(1, int(sym_r * 0.36))
        cv2.circle(out, (cx, cy), core_r, emblem_bgr, -1, cv2.LINE_AA)
        n_rays = 12
        for i in range(n_rays):
            ang = i * 2.0 * math.pi / n_rays - math.pi / 2.0
            inner_pt = (int(round(cx + core_r * math.cos(ang))),
                        int(round(cy + core_r * math.sin(ang))))
            outer_pt = (int(round(cx + sym_r * 0.92 * math.cos(ang))),
                        int(round(cy + sym_r * 0.92 * math.sin(ang))))
            cv2.line(out, inner_pt, outer_pt, emblem_bgr,
                     max(1, int(radius * 0.04)), cv2.LINE_AA)
    else:
        # Imperial northern iron halberd / crossed-lance crest for Northern dynasties
        s_len = max(2, int(sym_r * 0.75))
        cv2.line(out, (cx - s_len, cy), (cx + s_len, cy), emblem_bgr,
                 max(1, int(radius * 0.08)), cv2.LINE_AA)
        cv2.line(out, (cx, cy - s_len), (cx, cy + s_len), emblem_bgr,
                 max(1, int(radius * 0.08)), cv2.LINE_AA)

    # Floating badge text below token (soft shadow, zero rectangular box)
    if badge_text:
        font_size = max(10, int(radius * 0.42))
        pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        fnt = _get_font(font_size, condensed=True)
        bbox = draw.textbbox((0, 0), badge_text, font=fnt)
        tw = bbox[2] - bbox[0]
        tx = cx - tw // 2
        ty = cy + radius + max(4, int(radius * 0.15))
        draw.text((tx + 1, ty + 1), badge_text, fill=(0, 0, 0), font=fnt)
        text_color = (255, 200, 100) if not damaged else (220, 75, 60)
        draw.text((tx, ty), badge_text, fill=text_color, font=fnt)
        out = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    return out


# ---------------------------------------------------------------------------
# Shockwave Impact Rings
# ---------------------------------------------------------------------------
def _draw_shockwave_ring(
    canvas: np.ndarray,
    cx: int,
    cy: int,
    progress: float,
    max_radius: int,
    color: tuple[int, int, int] = (255, 180, 60),
) -> np.ndarray:
    """Draw kinetic impact shockwave ring expanding on clash."""
    if progress <= 0 or progress > 1.5:
        return canvas
    out = canvas.copy()
    p = _clamp(progress, 0.0, 1.0)
    r = int(max_radius * _ease_out_cubic(p))
    alpha = max(0.0, 1.0 - p * 1.2)
    if r < 2 or alpha < 0.02:
        return canvas
    overlay = out.copy()
    thickness = max(2, int(max_radius * 0.06 * (1.0 - p)))
    cv2.circle(overlay, (cx, cy), r, color, thickness, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha * 0.8, out, 1.0 - alpha * 0.8, 0, out)
    return out


# ---------------------------------------------------------------------------
# Counter / Tick-Down HUD
# ---------------------------------------------------------------------------
def _draw_troop_counter(
    canvas: np.ndarray,
    spec: dict[str, Any],
    t_norm: float,
) -> np.ndarray:
    """Draw live troop/ship counter tick-down as floating HUD text (zero rectangular bars)."""
    factions = spec.get("factions", {})
    if not factions:
        return canvas
    h, w = canvas.shape[:2]
    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    font_size = max(14, int(h * 0.022))
    fnt = _get_font(font_size, condensed=True)
    small_fnt = _get_font(max(10, font_size - 4), condensed=True)

    # Left faction (Đại Việt)
    left_name = factions.get("left_name", "ĐẠI VIỆT")
    left_stat = factions.get("left_stat_start", "")
    left_stat_end = factions.get("left_stat_end", "")
    if t_norm > 0.75 and left_stat_end:
        left_stat = left_stat_end

    # Right faction (Enemy)
    right_name = factions.get("right_name", "ĐỐI PHƯƠNG")
    right_stat = factions.get("right_stat_start", "")
    right_stat_end = factions.get("right_stat_end", "")
    if t_norm > 0.75 and right_stat_end:
        right_stat = right_stat_end

    # Power ratio (floating dot indicator instead of rectangular bar)
    ratio = _lerp(
        factions.get("ratio_start", 0.5),
        factions.get("ratio_end", 0.8),
        _ease_in_out_cubic(t_norm),
    )

    bar_y = int(h * 0.03)
    bar_margin = int(w * 0.08)
    bar_width = w - 2 * bar_margin

    # Seamless feathered Gaussian scrim behind left & right floating HUD labels
    scrim_h = max(18, int(h * 0.068))
    scrim_w_side = max(40, int(w * 0.28))
    pil_img = _composite_feathered_scrim(
        pil_img, bar_margin - 8, bar_y, scrim_w_side, scrim_h, alpha_max=145
    )
    pil_img = _composite_feathered_scrim(
        pil_img, bar_margin + bar_width - scrim_w_side + 8, bar_y, scrim_w_side, scrim_h, alpha_max=145
    )

    # Subtle glowing momentum balance dot (zero HP bar!)
    split_x = bar_margin + int(bar_width * ratio)
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.circle(cv2_img, (split_x, bar_y + 4), 3, (120, 190, 240), -1, cv2.LINE_AA)

    pil_img = Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    # Faction labels (floating text with shadow, no box)
    text_y = bar_y + max(8, int(h * 0.012))
    # Left label shadow + text
    draw.text((bar_margin + 1, text_y + 1), left_name, fill=(0, 0, 0), font=fnt)
    draw.text((bar_margin, text_y), left_name, fill=(255, 200, 120), font=fnt)
    draw.text((bar_margin + 1, text_y + font_size + 3), left_stat,
              fill=(0, 0, 0), font=small_fnt)
    draw.text((bar_margin, text_y + font_size + 2), left_stat,
              fill=(220, 210, 200), font=small_fnt)

    # Right-aligned
    r_bbox = draw.textbbox((0, 0), right_name, font=fnt)
    r_w = r_bbox[2] - r_bbox[0]
    draw.text((bar_margin + bar_width - r_w + 1, text_y + 1), right_name,
              fill=(0, 0, 0), font=fnt)
    draw.text((bar_margin + bar_width - r_w, text_y), right_name,
              fill=(180, 200, 220), font=fnt)
    r_stat_bbox = draw.textbbox((0, 0), right_stat, font=small_fnt)
    r_stat_w = r_stat_bbox[2] - r_stat_bbox[0]
    draw.text((bar_margin + bar_width - r_stat_w + 1, text_y + font_size + 3),
              right_stat, fill=(0, 0, 0), font=small_fnt)
    draw.text((bar_margin + bar_width - r_stat_w, text_y + font_size + 2),
              right_stat, fill=(190, 200, 210), font=small_fnt)

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Phase Label & Title HUD
# ---------------------------------------------------------------------------
def _draw_phase_label(
    canvas: np.ndarray,
    spec: dict[str, Any],
    t_norm: float,
) -> np.ndarray:
    """Draw current battle phase label at bottom of screen (floating text, no box)."""
    phases = spec.get("phases", [])
    if not phases:
        return canvas

    # Determine current phase
    current_phase = phases[0]
    for phase in phases:
        if t_norm <= phase.get("t_max", 1.0):
            current_phase = phase
            break
    else:
        current_phase = phases[-1]

    label = current_phase.get("label", "")
    if not label:
        return canvas

    h, w = canvas.shape[:2]
    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    font_size = max(14, int(h * 0.024))
    fnt = _get_font(font_size, condensed=True)

    bbox = draw.textbbox((0, 0), label, font=fnt)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) // 2
    ty = h - int(h * 0.065)

    # Seamless feathered Gaussian scrim (zero clipped borders)
    scrim_pad = max(6, int(h * 0.01))
    pil_img = _composite_feathered_scrim(
        pil_img,
        tx - scrim_pad * 2,
        ty - scrim_pad // 2,
        tw + scrim_pad * 4,
        (bbox[3] - bbox[1]) + scrim_pad,
        alpha_max=155,
    )
    draw = ImageDraw.Draw(pil_img)

    # Text
    draw.text((tx + 1, ty + 1), label, fill=(0, 0, 0), font=fnt)
    draw.text((tx, ty), label, fill=(240, 230, 210), font=fnt)

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Title Card
# ---------------------------------------------------------------------------
def _draw_title_card(
    canvas: np.ndarray,
    spec: dict[str, Any],
    t_norm: float,
) -> np.ndarray:
    """Draw battle title + date stamp in upper region, fading out after t=0.15."""
    if t_norm > 0.25:
        return canvas

    title = spec.get("title_vi", "")
    date_stamp = spec.get("date_stamp", "")
    if not title:
        return canvas

    alpha = 1.0 if t_norm < 0.15 else max(0.0, 1.0 - (t_norm - 0.15) / 0.10)
    if alpha < 0.02:
        return canvas

    h, w = canvas.shape[:2]
    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    title_size = max(18, int(h * 0.038))
    date_size = max(12, int(h * 0.018))
    title_fnt = _get_font(title_size)
    date_fnt = _get_font(date_size, condensed=True)

    # Center title
    t_bbox = draw.textbbox((0, 0), title, font=title_fnt)
    tw = t_bbox[2] - t_bbox[0]
    tx = (w - tw) // 2
    ty = int(h * 0.12)

    # Apply alpha via overlay
    title_color = (
        int(250 * alpha), int(240 * alpha), int(220 * alpha)
    )
    shadow_color = (int(10 * alpha), int(8 * alpha), int(6 * alpha))

    draw.text((tx + 2, ty + 2), title, fill=shadow_color, font=title_fnt)
    draw.text((tx, ty), title, fill=title_color, font=title_fnt)

    if date_stamp:
        d_bbox = draw.textbbox((0, 0), date_stamp, font=date_fnt)
        dw = d_bbox[2] - d_bbox[0]
        dx = (w - dw) // 2
        dy = ty + title_size + max(6, int(h * 0.01))
        date_color = (int(220 * alpha), int(190 * alpha), int(130 * alpha))
        draw.text((dx, dy), date_stamp, fill=date_color, font=date_fnt)

    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Callout Arcs
# ---------------------------------------------------------------------------
def _boxes_overlap(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
    margin: int = 8,
) -> bool:
    """Return True if two (x0, y0, x1, y1) axis-aligned bounding boxes overlap within margin."""
    return not (
        a[2] + margin <= b[0]
        or b[2] + margin <= a[0]
        or a[3] + margin <= b[1]
        or b[3] + margin <= a[1]
    )


def _draw_callout_arcs(
    canvas: np.ndarray,
    callouts: list[dict[str, Any]],
    camera: PerspectiveCamera3D,
    cam_cx: float,
    cam_cy: float,
    pitch_deg: float,
    zoom: float,
    t_norm: float,
    spec: dict[str, Any] | None = None,
) -> np.ndarray:
    """Draw clean collision-free range/width callout arcs with labels (zero boxes).

    Enforces strict clearance against:
    - Top faction HUD (`y >= 0.175 * h`)
    - Bottom phase HUD (`y <= 0.84 * h`)
    - Bottom-left compass/tidal readout & bottom-right watermark zone
    - Right-edge `QĐ. HOÀNG SA` / `QĐ. TRƯỜNG SA` sovereignty beacons (>= 240px clear)
    - Projected stake beds (auto-elevates callout cleanly above stake field)
    - Previously placed callout labels (zero label-on-label overlap)
    """
    if not callouts:
        return canvas
    out = canvas.copy()
    h, w = canvas.shape[:2]
    spec_d = spec or {}

    # Build forbidden AABB zones in screen pixel space
    forbidden: list[tuple[int, int, int, int]] = [
        (0, 0, w, int(h * 0.175)),                            # Top faction header HUD
        (0, int(h * 0.84), w, h),                             # Bottom phase HUD
        (0, int(h * 0.72), int(w * 0.34), h),                 # Bottom-left compass + tidal HUD
        (max(0, w - 240), max(0, h - 240), w, h),             # Bottom-right logo zone
    ]

    # Reserve right-side sovereignty corridor when sovereignty markers are active
    sov_flag = spec_d.get("sovereignty_markers")
    terrain_cfg = spec_d.get("terrain", {})
    sov_active = sov_flag is True or (
        sov_flag is None
        and (
            bool(terrain_cfg.get("sea_region"))
            or spec_d.get("gis_bbox") in ("east_asia_vietnam", "northern_dai_viet")
        )
    )
    if sov_active:
        # >= 240px clearance left of right-edge sovereignty beacons (x=0.895*w -> forbid x >= w - 460)
        sov_left = max(int(w * 0.68), w - int(max(320, w * 0.28)))
        forbidden.append((sov_left, int(h * 0.19), w, int(h * 0.56)))

    # Reserve projected stake-bed bounding boxes so labels never sit on top of stakes
    tidal_cfg = spec_d.get("tidal") or {}
    if tidal_cfg.get("enabled"):
        for bed in tidal_cfg.get("stake_beds", []):
            p0 = bed.get("p0", (0.4, 0.5))
            p1 = bed.get("p1", (0.6, 0.5))
            xs_b: list[float] = []
            ys_b: list[float] = []
            for u_p in (p0[0], (p0[0] + p1[0]) * 0.5, p1[0]):
                for dy in (-0.025, 0.025):
                    v_p = _lerp(p0[1], p1[1], 0.5) + dy
                    px, py = camera.project_point(u_p, v_p, cam_cx, cam_cy, pitch_deg, zoom)
                    xs_b.append(px)
                    ys_b.append(py)
            if xs_b and ys_b:
                pad_x = max(18, int(w * 0.018))
                pad_y = max(28, int(h * 0.042))
                forbidden.append((
                    int(min(xs_b)) - pad_x,
                    int(min(ys_b)) - pad_y,
                    int(max(xs_b)) + pad_x,
                    int(max(ys_b)) + pad_y,
                ))

    placed: list[tuple[int, int, int, int]] = []
    lbl_size = max(11, int(h * 0.018))
    sub_size = max(9, lbl_size - 4)
    lbl_fnt = _get_font(lbl_size, condensed=True)
    sub_fnt = _get_font(sub_size, condensed=True)
    safe_margin_x = max(18, int(w * 0.022))
    safe_top = int(h * 0.185)
    safe_bot = int(h * 0.825)

    for callout in callouts:
        t_appear = float(callout.get("t_appear", 0.0))
        if t_norm < t_appear:
            continue
        fade = _clamp((t_norm - t_appear) / 0.08)

        uv = callout.get("uv", (0.5, 0.5))
        label = str(callout.get("label", ""))
        sub = str(callout.get("sub", ""))
        offset = callout.get("offset", (0.1, -0.05))

        sx, sy = camera.project_point(uv[0], uv[1], cam_cx, cam_cy, pitch_deg, zoom)
        if not (0 <= sx < w and 0 <= sy < h):
            continue

        # Measure exact label+sub bounding box
        tmp_draw = ImageDraw.Draw(Image.new("RGB", (16, 16)))
        if label:
            l_bb = tmp_draw.textbbox((0, 0), label, font=lbl_fnt)
            lw, lh = l_bb[2] - l_bb[0], l_bb[3] - l_bb[1]
        else:
            lw, lh = 0, 0
        if sub:
            s_bb = tmp_draw.textbbox((0, 0), sub, font=sub_fnt)
            sw_p, sh_p = s_bb[2] - s_bb[0], s_bb[3] - s_bb[1]
        else:
            sw_p, sh_p = 0, 0

        box_w = max(lw, sw_p) + 12
        box_h = lh + (sh_p + 6 if sub else 0) + 8

        # Requested endpoint -> top-left of text block
        req_tx = int(sx + float(offset[0]) * w) + 4
        req_ty = int(sy + float(offset[1]) * h) - lbl_size - 2

        # Candidate search: requested first, then cleanly pushed clear of top HUD, sovereignty, stakes
        candidates: list[tuple[int, int]] = [(req_tx, req_ty)]
        # Push directly above stakes / anchor, left of sovereignty, below top HUD
        clamped_y = max(safe_top, min(safe_bot - box_h, req_ty))
        clamped_x = max(safe_margin_x, min(w - box_w - safe_margin_x, req_tx))
        candidates.append((clamped_x, clamped_y))
        for dy_frac in (-0.14, -0.20, 0.12, -0.26, 0.18, 0.0, -0.08, 0.08):
            for dx_frac in (0.0, -0.18, -0.28, 0.12, -0.10, 0.22, -0.36):
                cx_c = int(sx + dx_frac * w) - (box_w // 2 if dx_frac <= 0 else 0)
                cy_c = int(sy + dy_frac * h) - box_h // 2
                cx_c = max(safe_margin_x, min(w - box_w - safe_margin_x, cx_c))
                cy_c = max(safe_top, min(safe_bot - box_h, cy_c))
                candidates.append((cx_c, cy_c))

        best_tx, best_ty = clamped_x, clamped_y
        for cx_c, cy_c in candidates:
            if cx_c < safe_margin_x or cx_c + box_w > w - safe_margin_x:
                continue
            if cy_c < safe_top or cy_c + box_h > safe_bot:
                continue
            cand_box = (cx_c, cy_c, cx_c + box_w, cy_c + box_h)
            if any(_boxes_overlap(cand_box, fb, margin=12) for fb in forbidden):
                continue
            if any(_boxes_overlap(cand_box, pb, margin=14) for pb in placed):
                continue
            best_tx, best_ty = cx_c, cy_c
            break

        placed.append((best_tx, best_ty, best_tx + box_w, best_ty + box_h))

        # Leader line terminates cleanly at nearest left/right edge of text block
        ex = best_tx - 6 if best_tx > sx else best_tx + box_w + 2
        ey = best_ty + lh // 2 + 2

        alpha = fade * 0.85
        line_bgr = (int(175 * alpha), int(200 * alpha), int(220 * alpha))
        cv2.line(out, (int(sx), int(sy)), (int(ex), int(ey)), line_bgr, 1, cv2.LINE_AA)
        cv2.circle(
            out,
            (int(sx), int(sy)),
            max(3, int(w * 0.0028)),
            (int(120 * alpha), int(205 * alpha), int(245 * alpha)),
            -1,
            cv2.LINE_AA,
        )

        if label:
            pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
            pil_img = _composite_feathered_scrim(
                pil_img, best_tx - 6, best_ty - 4, box_w + 4, box_h + 2, alpha_max=int(130 * fade)
            )
            draw = ImageDraw.Draw(pil_img)
            lbl_color = (int(250 * fade), int(242 * fade), int(224 * fade))
            draw.text((best_tx + 1, best_ty + 1), label, fill=(0, 0, 0), font=lbl_fnt)
            draw.text((best_tx, best_ty), label, fill=lbl_color, font=lbl_fnt)
            if sub:
                sub_color = (int(215 * fade), int(198 * fade), int(162 * fade))
                draw.text((best_tx + 1, best_ty + lh + 5), sub, fill=(0, 0, 0), font=sub_fnt)
                draw.text((best_tx, best_ty + lh + 4), sub, fill=sub_color, font=sub_fnt)
            out = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    return out


# ---------------------------------------------------------------------------
# Sovereignty Labels (HOÀNG SA / TRƯỜNG SA)
# ---------------------------------------------------------------------------
def _draw_sovereignty_labels(
    canvas: np.ndarray,
    spec: dict[str, Any],
    camera: PerspectiveCamera3D,
    cam_cx: float,
    cam_cy: float,
    pitch_deg: float,
    zoom: float,
) -> np.ndarray:
    """Render QĐ. HOÀNG SA / QĐ. TRƯỜNG SA sovereignty markers when active or sea in view.

    Guaranteed visible inside safe screen bounds (never clipped off-screen and never
    overlapping bottom-right W-w-36:H-h-36 watermark zone). Zero rectangular boxes.
    """
    sov_flag = spec.get("sovereignty_markers")
    if sov_flag is False:
        return canvas

    terrain_cfg = spec.get("terrain", {})
    sea = terrain_cfg.get("sea_region")
    gis_bbox = spec.get("gis_bbox")
    if sov_flag is None and not sea and gis_bbox not in ("east_asia_vietnam", "northern_dai_viet"):
        return canvas

    h, w = canvas.shape[:2]
    out = canvas.copy()
    sov_size = max(10, int(h * 0.016))
    sub_size = max(9, sov_size - 3)
    sov_fnt = _get_font(sov_size, condensed=True)
    sub_fnt = _get_font(sub_size, condensed=True)

    sea_x0 = float(sea.get("x0", 0.75)) if isinstance(sea, dict) else 0.78
    sea_y0 = float(sea.get("y0", 0.0)) if isinstance(sea, dict) else 0.0
    sea_x1 = float(sea.get("x1", 1.0)) if isinstance(sea, dict) else 1.0
    sea_y1 = float(sea.get("y1", 1.0)) if isinstance(sea, dict) else 1.0

    anchors = (
        ("QĐ. HOÀNG SA", "VIỆT NAM", (sea_x0 + sea_x1) * 0.5, sea_y0 + (sea_y1 - sea_y0) * 0.28, int(h * 0.27)),
        ("QĐ. TRƯỜNG SA", "VIỆT NAM", (sea_x0 + sea_x1) * 0.5, sea_y0 + (sea_y1 - sea_y0) * 0.62, int(h * 0.41)),
    )

    for idx, (main_txt, sub_txt, _uv_x, _uv_y, fallback_sy) in enumerate(anchors):
        # Always park cleanly along right-hand East Sea corridor (above bottom-right logo,
        # clear of central battlefront and callout labels)
        sx = int(w * 0.895)
        sy = fallback_sy + idx * max(4, int(h * 0.01))

        marker_r = max(4, int(h * 0.006))
        # BGR warm antique gold crosshair
        gold_bgr = (105, 195, 238)
        cv2.circle(out, (sx, sy), marker_r, gold_bgr, 1, cv2.LINE_AA)
        cv2.circle(out, (sx, sy), max(1, marker_r // 3), gold_bgr, -1, cv2.LINE_AA)
        cv2.line(out, (sx - marker_r - 3, sy), (sx + marker_r + 3, sy), gold_bgr, 1, cv2.LINE_AA)
        cv2.line(out, (sx, sy - marker_r - 3), (sx, sy + marker_r + 3), gold_bgr, 1, cv2.LINE_AA)

        pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        m_bbox = draw.textbbox((0, 0), main_txt, font=sov_fnt)
        mw, mh = m_bbox[2] - m_bbox[0], m_bbox[3] - m_bbox[1]
        s_bbox = draw.textbbox((0, 0), sub_txt, font=sub_fnt)
        sw_px = s_bbox[2] - s_bbox[0]

        tx = min(w - mw - 14, max(12, sx - mw // 2))
        label_y = sy + marker_r + 4

        # Seamless feathered Gaussian shadow scrim under sovereignty text (zero boxes)
        pad = max(5, int(h * 0.006))
        scrim_w = max(mw, sw_px) + pad * 2
        scrim_h_px = mh + sub_size + pad + 4
        pil_img = _composite_feathered_scrim(
            pil_img, tx - pad, label_y - pad // 2, scrim_w, scrim_h_px, alpha_max=145
        )
        draw = ImageDraw.Draw(pil_img)

        draw.text((tx + 1, label_y + 1), main_txt, fill=(0, 0, 0), font=sov_fnt)
        draw.text((tx, label_y), main_txt, fill=(242, 206, 118), font=sov_fnt)
        sx_sub = min(w - sw_px - 14, max(12, sx - sw_px // 2))
        draw.text((sx_sub + 1, label_y + mh + 4), sub_txt, fill=(0, 0, 0), font=sub_fnt)
        draw.text((sx_sub, label_y + mh + 3), sub_txt, fill=(198, 176, 112), font=sub_fnt)

        out = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    return out


# ---------------------------------------------------------------------------
# Compass Rose
# ---------------------------------------------------------------------------
def _draw_compass(canvas: np.ndarray) -> np.ndarray:
    """Draw a small engraved compass in the bottom-left corner."""
    h, w = canvas.shape[:2]
    cx = int(w * 0.055)
    cy = h - int(h * 0.09)
    r = max(12, int(min(w, h) * 0.022))
    out = canvas.copy()

    # Ring
    cv2.circle(out, (cx, cy), r, (160, 150, 130), 1, cv2.LINE_AA)
    # N pointer
    cv2.line(out, (cx, cy - r + 2), (cx, cy - int(r * 0.3)),
             (220, 60, 50), max(1, r // 6), cv2.LINE_AA)
    # S pointer
    cv2.line(out, (cx, cy + int(r * 0.3)), (cx, cy + r - 2),
             (180, 170, 160), max(1, r // 8), cv2.LINE_AA)
    # E/W
    cv2.line(out, (cx - r + 2, cy), (cx + r - 2, cy),
             (140, 130, 120), max(1, r // 8), cv2.LINE_AA)
    # N label
    pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    n_fnt = _get_font(max(8, r // 2), condensed=True)
    draw.text((cx - 3, cy - r - max(8, r // 2) - 2), "N",
              fill=(220, 60, 50), font=n_fnt)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------------------
# Built-in Ancient Vietnam Presets
# ---------------------------------------------------------------------------
def _build_presets() -> dict[str, dict[str, Any]]:
    """Three ready-to-render Ancient Vietnam battle presets."""
    return {
        "bach_dang_938_ngo_quyen": {
            "preset_id": "bach_dang_938_ngo_quyen",
            "title_vi": "ĐẠI CHIẾN BẠCH ĐẰNG 938",
            "subtitle_vi": "CỌC GỖ BỌC SẮT ĐẠI PHÁ HOẰNG THAO",
            "year": 938,
            "date_stamp": "MÙA ĐÔNG 938 • CỬA SÔNG BẠCH ĐẰNG",
            "summary_vi": "Ngô Quyền dàn trận cọc gỗ bọc sắt tại cửa sông Bạch Đằng, nhử chiến thuyền Lưu Hoằng Thao lúc triều cường vào sâu, đợi triều rút mắc cọc rồi tung quân đánh tiêu diệt gọn.",
            "seed": 938,
            "canvas_size": (3840, 2160),
            "gis_bbox": "bach_dang",
            "sovereignty_markers": True,
            "camera": {
                "start": {"cx": 0.55, "cy": 0.40, "pitch": 32.0, "zoom": 1.8},
                "end": {"cx": 0.52, "cy": 0.52, "pitch": 44.0, "zoom": 2.6},
            },
            "terrain": {
                "rivers": [
                    {"points": [(0.1, 0.35), (0.3, 0.42), (0.5, 0.50), (0.7, 0.55), (0.9, 0.60)],
                     "widths": [0.03, 0.04, 0.06, 0.08, 0.12]},
                ],
                "ridges": [
                    {"points": [(0.2, 0.15), (0.4, 0.20), (0.6, 0.18)], "height": 0.7, "sigma": 0.08},
                    {"points": [(0.3, 0.70), (0.5, 0.72), (0.7, 0.68)], "height": 0.5, "sigma": 0.10},
                ],
                "sea_region": {"x0": 0.75, "y0": 0.0, "x1": 1.0, "y1": 1.0},
            },
            "factions": {
                "left_name": "ĐẠI VIỆT (NGÔ QUYỀN)",
                "right_name": "NAM HÁN (HOẰNG THAO)",
                "left_stat_start": "THUỶ QUÂN NGÔ QUYỀN",
                "left_stat_end": "TOÀN THẮNG • HOẰNG THAO TỬ TRẬN",
                "right_stat_start": "CHIẾN THUYỀN LƯU HOẰNG THAO",
                "right_stat_end": "HẠM ĐỘI BỊ ĐẮM GỌN",
                "ratio_start": 0.45,
                "ratio_end": 0.88,
            },
            "phases": [
                {"t_max": 0.35, "label": "PHA I • NGÔ QUYỀN NHỬ THUYỀN NAM HÁN VÀO CỬA SÔNG LÚC TRIỀU CƯỜNG"},
                {"t_max": 0.70, "label": "PHA II • TRIỀU RÚT LỘ BÃI CỌC SẮT — THUYỀN ĐỊCH MẮC CỌC"},
                {"t_max": 1.01, "label": "PHA III • TUNG QUÂN ĐÁNH ĐẮM TOÀN BỘ — HOẰNG THAO TỬ TRẬN"},
            ],
            "tidal": {
                "enabled": True,
                "start_m": 1.6,
                "end_m": -3.5,
                "stake_threshold_m": -1.0,
                "stake_beds": [
                    {"p0": (0.45, 0.48), "p1": (0.60, 0.52), "rows": 3, "count": 10},
                ],
            },
            "territories": [
                {"faction": "dai_viet", "region": {"x0": 0.0, "y0": 0.0, "x1": 0.50, "y1": 1.0},
                 "advance_start": 0.3, "advance_end": 0.9},
                {"faction": "southern_han", "region": {"x0": 0.55, "y0": 0.0, "x1": 1.0, "y1": 1.0},
                 "advance_start": 0.6, "advance_end": 0.15},
            ],
            "units": [
                {"faction": "dai_viet", "badge": "NGÔ QUYỀN",
                 "waypoints": [(0.35, 0.45), (0.45, 0.48), (0.55, 0.50)],
                 "t_start": 0.0, "t_end": 0.75},
                {"faction": "southern_han", "badge": "HOẰNG THAO",
                 "badge_damaged": "TỬ TRẬN", "damage_t": 0.65,
                 "waypoints": [(0.85, 0.40), (0.70, 0.48), (0.55, 0.52)],
                 "t_start": 0.05, "t_end": 0.70},
                {"faction": "dai_viet", "badge": "PHỤC BINH",
                 "waypoints": [(0.25, 0.65), (0.40, 0.55), (0.52, 0.50)],
                 "t_start": 0.40, "t_end": 0.85},
            ],
            "engagements": [
                {"uv": (0.52, 0.50), "trigger_t": 0.55, "label": "THUYỀN MẮC CỌC",
                 "color": (60, 82, 236), "max_radius": 80},
                {"uv": (0.55, 0.48), "trigger_t": 0.65, "label": "TỔNG CÔNG KÍCH",
                 "color": (52, 82, 236), "max_radius": 100},
            ],
            "callouts": [
                {"uv": (0.52, 0.50), "label": "BÃI CỌC BẠCH ĐẰNG", "sub": "CỌC GỖ BỌC SẮT",
                 "offset": (0.12, -0.08), "t_appear": 0.0},
                {"uv": (0.35, 0.30), "label": "NÚI ĐÁ BỌT — ĐÀI CHỈ HUY",
                 "sub": "NGÔ QUYỀN QUAN SÁT TRIỀU", "offset": (-0.14, -0.06), "t_appear": 0.0},
                {"uv": (0.80, 0.42), "label": "CỬA BIỂN BẠCH ĐẰNG",
                 "sub": "ĐƯỜNG VÀO CỦA NAM HÁN", "offset": (0.10, -0.05), "t_appear": 0.05},
            ],
        },

        "bach_dang_1288_tran_hung_dao": {
            "preset_id": "bach_dang_1288_tran_hung_dao",
            "title_vi": "ĐẠI CHIẾN BẠCH ĐẰNG 1288",
            "subtitle_vi": "BẪY CỌC GỖ LIM & THỦY TRIỀU RÚT ĐẠI PHÁ Ô MÃ NHI",
            "year": 1288,
            "date_stamp": "09/04/1288 • GIỜ MÃO → GIỜ THÌN",
            "summary_vi": "Nguyễn Khoái nhử 600 chiến thuyền Ô Mã Nhi vào cửa sông Bạch Đằng lúc triều cường; khi nước ròng rút mạnh, bãi cọc Yên Giang – Sông Chanh khóa chặt hạm đội Nguyên Mông.",
            "seed": 1288,
            "canvas_size": (3840, 2160),
            "gis_bbox": "bach_dang",
            "sovereignty_markers": True,
            "camera": {
                "start": {"cx": 0.50, "cy": 0.35, "pitch": 34.0, "zoom": 1.6},
                "end": {"cx": 0.55, "cy": 0.52, "pitch": 46.0, "zoom": 2.8},
            },
            "terrain": {
                "rivers": [
                    {"points": [(0.05, 0.30), (0.25, 0.38), (0.45, 0.48), (0.65, 0.54), (0.90, 0.62)],
                     "widths": [0.04, 0.05, 0.07, 0.09, 0.14]},
                    {"points": [(0.50, 0.42), (0.60, 0.58), (0.72, 0.78)],
                     "widths": [0.03, 0.04, 0.05]},
                ],
                "ridges": [
                    {"points": [(0.15, 0.12), (0.35, 0.18), (0.55, 0.22)], "height": 0.75, "sigma": 0.08},
                    {"points": [(0.20, 0.72), (0.40, 0.68)], "height": 0.45, "sigma": 0.09},
                ],
                "sea_region": {"x0": 0.78, "y0": 0.0, "x1": 1.0, "y1": 1.0},
            },
            "factions": {
                "left_name": "ĐẠI VIỆT (NHÀ TRẦN)",
                "right_name": "NGUYÊN MÔNG (Ô MÃ NHI)",
                "left_stat_start": "5 VẠN QUÂN • NGUYỄN KHOÁI",
                "left_stat_end": "5 VẠN QUÂN • TOÀN THẮNG",
                "right_stat_start": "600 THUYỀN • Ô MÃ NHI",
                "right_stat_end": "BỊ BẮT & ĐÁNH ĐẮM",
                "ratio_start": 0.46,
                "ratio_end": 0.88,
            },
            "phases": [
                {"t_max": 0.36, "label": "PHA I • NGUYỄN KHOÁI NHỬ ĐỊCH LÚC TRIỀU CƯỜNG"},
                {"t_max": 0.72, "label": "PHA II • TRIỀU RÚT -3.8M LỘ BÃI CỌC GỖ LIM YÊN GIANG"},
                {"t_max": 1.01, "label": "PHA III • ĐẠI QUÂN NHÀ TRẦN BAO VÂY BẮT SỐNG Ô MÃ NHI"},
            ],
            "tidal": {
                "enabled": True,
                "start_m": 1.4,
                "end_m": -3.8,
                "stake_threshold_m": -1.2,
                "stake_beds": [
                    {"p0": (0.48, 0.50), "p1": (0.62, 0.46), "rows": 3, "count": 11},
                    {"p0": (0.52, 0.56), "p1": (0.62, 0.52), "rows": 2, "count": 7},
                ],
            },
            "territories": [
                {"faction": "dai_viet", "region": {"x0": 0.0, "y0": 0.0, "x1": 0.48, "y1": 1.0},
                 "advance_start": 0.3, "advance_end": 0.85},
                {"faction": "yuan_mongol", "region": {"x0": 0.52, "y0": 0.0, "x1": 1.0, "y1": 1.0},
                 "advance_start": 0.6, "advance_end": 0.1},
            ],
            "units": [
                {"faction": "dai_viet", "badge": "NGUYỄN KHOÁI",
                 "waypoints": [(0.42, 0.44), (0.35, 0.40), (0.28, 0.35), (0.40, 0.42)],
                 "t_start": 0.0, "t_end": 0.75},
                {"faction": "yuan_mongol", "badge": "600 THUYỀN",
                 "badge_damaged": "MẮC CỌC • VỠ TRẬN", "damage_t": 0.58,
                 "waypoints": [(0.85, 0.35), (0.65, 0.45), (0.52, 0.50)],
                 "t_start": 0.05, "t_end": 0.65},
                {"faction": "dai_viet", "badge": "TRẦN HƯNG ĐẠO",
                 "waypoints": [(0.15, 0.25), (0.30, 0.38), (0.48, 0.48)],
                 "t_start": 0.45, "t_end": 0.90},
            ],
            "engagements": [
                {"uv": (0.52, 0.50), "trigger_t": 0.50, "label": "SẬP BẪY CỌC YÊN GIANG",
                 "color": (52, 82, 236), "max_radius": 90},
            ],
            "callouts": [
                {"uv": (0.52, 0.50), "label": "BÃI CỌC YÊN GIANG", "sub": "CỌC GỖ LIM BỊT SẮT",
                 "offset": (0.12, -0.07), "t_appear": 0.0},
                {"uv": (0.40, 0.22), "label": "NÚI TRÀNG KÊNH", "sub": "ĐÀI CHỈ HUY NHÀ TRẦN",
                 "offset": (0.13, -0.05), "t_appear": 0.0},
            ],
        },

        "nhu_nguyet_1077_ly_thuong_kiet": {
            "preset_id": "nhu_nguyet_1077_ly_thuong_kiet",
            "title_vi": "PHÒNG TUYẾN NHƯ NGUYỆT 1077",
            "subtitle_vi": "LÝ THƯỜNG KIỆT CHẶN ĐỨNG 10 VẠN QUÂN TỐNG TẠI SÔNG CẦU",
            "year": 1077,
            "date_stamp": "XUÂN 1077 • SÔNG NHƯ NGUYỆT (SÔNG CẦU)",
            "summary_vi": "Lý Thường Kiệt dựng phòng tuyến cọc gỗ sông Như Nguyệt chặn đứng 10 vạn quân Quách Quỳ, đêm vượt sông tập kích đại phá quân Tống.",
            "seed": 1077,
            "canvas_size": (3840, 2160),
            "gis_bbox": "nhu_nguyet",
            "sovereignty_markers": False,
            "camera": {
                "start": {"cx": 0.45, "cy": 0.38, "pitch": 35.0, "zoom": 1.5},
                "end": {"cx": 0.48, "cy": 0.60, "pitch": 42.0, "zoom": 2.4},
            },
            "terrain": {
                "rivers": [
                    {"points": [(0.10, 0.55), (0.30, 0.57), (0.50, 0.58), (0.75, 0.60), (0.95, 0.62)],
                     "widths": [0.03, 0.04, 0.05, 0.06, 0.08]},
                ],
                "ridges": [
                    {"points": [(0.15, 0.35), (0.35, 0.37), (0.55, 0.36)], "height": 0.8, "sigma": 0.08},
                    {"points": [(0.20, 0.75), (0.45, 0.78)], "height": 0.4, "sigma": 0.10},
                ],
                "sea_region": {"x0": 0.85, "y0": 0.3, "x1": 1.0, "y1": 0.8},
            },
            "factions": {
                "left_name": "ĐẠI VIỆT (NHÀ LÝ)",
                "right_name": "BẮC TỐNG (QUÁCH QUỲ)",
                "left_stat_start": "10 VẠN • LÝ THƯỜNG KIỆT",
                "left_stat_end": "GIỮ VỮNG BỜ CÕI ĐẠI VIỆT",
                "right_stat_start": "10 VẠN QUÂN TỐNG",
                "right_stat_end": "QUÁCH QUỲ XIN GIẢNG HÒA",
                "ratio_start": 0.50,
                "ratio_end": 0.80,
            },
            "phases": [
                {"t_max": 0.40, "label": "PHA I • 10 VẠN QUÂN TỐNG TIẾN VÀO ĐẠI VIỆT"},
                {"t_max": 0.75, "label": "PHA II • PHÒNG TUYẾN CỌC GỖ NHƯ NGUYỆT CHẶN QUÁCH QUỲ"},
                {"t_max": 1.01, "label": "PHA III • ĐÊM VƯỢT SÔNG TẬP KÍCH ĐẠI PHÁ QUÂN TỐNG"},
            ],
            "tidal": {
                "enabled": True,
                "start_m": 1.2,
                "end_m": -2.0,
                "stake_threshold_m": -0.5,
                "stake_beds": [
                    {"p0": (0.30, 0.57), "p1": (0.55, 0.59), "rows": 2, "count": 10},
                ],
            },
            "territories": [
                {"faction": "dai_viet", "region": {"x0": 0.0, "y0": 0.45, "x1": 0.80, "y1": 1.0},
                 "advance_start": 0.5, "advance_end": 0.85},
                {"faction": "song_dynasty", "region": {"x0": 0.0, "y0": 0.0, "x1": 0.80, "y1": 0.50},
                 "advance_start": 0.6, "advance_end": 0.2},
            ],
            "units": [
                {"faction": "dai_viet", "badge": "LÝ THƯỜNG KIỆT",
                 "waypoints": [(0.40, 0.65), (0.42, 0.58), (0.45, 0.52)],
                 "t_start": 0.30, "t_end": 0.90},
                {"faction": "song_dynasty", "badge": "10 VẠN • QUÁCH QUỲ",
                 "badge_damaged": "BỊ CHẶN TẠI SÔNG CẦU", "damage_t": 0.72,
                 "waypoints": [(0.45, 0.20), (0.44, 0.38), (0.46, 0.52)],
                 "t_start": 0.05, "t_end": 0.75},
            ],
            "engagements": [
                {"uv": (0.44, 0.56), "trigger_t": 0.65, "label": "ĐẠI THẮNG NHƯ NGUYỆT",
                 "color": (46, 68, 232), "max_radius": 100},
            ],
            "callouts": [
                {"uv": (0.42, 0.58), "label": "SÔNG NHƯ NGUYỆT", "sub": "LŨY CỌC NAM QUỐC SƠN HÀ",
                 "offset": (-0.14, 0.07), "t_appear": 0.0},
                {"uv": (0.45, 0.78), "label": "KINH ĐÔ THĂNG LONG", "sub": "HẬU PHƯƠNG ĐẠI VIỆT",
                 "offset": (0.13, 0.04), "t_appear": 0.0},
            ],
        },
    }


GEO_EMPIRE_PRESETS: dict[str, dict[str, Any]] = _build_presets()

# Sub-stage aliases used by pilot_spec.json beats (all resolve cleanly onto canonical presets)
_PRESET_STAGE_OVERRIDES: dict[str, dict[str, Any]] = {
    "bach_dang_estuary_quang_ninh_938": {
        "base_preset": "bach_dang_938_ngo_quyen",
        "sovereignty_markers": True,
        "camera": {
            "start": {"cx": 0.62, "cy": 0.44, "pitch": 34.0, "zoom": 1.35},
            "end": {"cx": 0.52, "cy": 0.50, "pitch": 42.0, "zoom": 2.45},
        },
    },
    "bach_dang_938_han_fleet_route": {
        "base_preset": "bach_dang_938_ngo_quyen",
        "sovereignty_markers": True,
        "camera": {
            "start": {"cx": 0.68, "cy": 0.45, "pitch": 33.0, "zoom": 1.55},
            "end": {"cx": 0.54, "cy": 0.50, "pitch": 43.0, "zoom": 2.35},
        },
        "tidal": {
            "enabled": True,
            "start_m": 2.8,
            "end_m": 2.2,
            "stake_threshold_m": -0.5,
            "stake_beds": [{"p0": (0.45, 0.48), "p1": (0.60, 0.52), "rows": 3, "count": 10}],
        },
    },
    "bach_dang_938_stake_field_submerged": {
        "base_preset": "bach_dang_938_ngo_quyen",
        "sovereignty_markers": False,
        "camera": {
            "start": {"cx": 0.54, "cy": 0.48, "pitch": 38.0, "zoom": 2.1},
            "end": {"cx": 0.52, "cy": 0.51, "pitch": 46.0, "zoom": 2.75},
        },
        "tidal": {
            "enabled": True,
            "start_m": 3.0,
            "end_m": 2.4,
            "stake_threshold_m": 0.0,
            "submerged_xray": True,
            "stake_beds": [{"p0": (0.44, 0.48), "p1": (0.60, 0.52), "rows": 3, "count": 12}],
        },
    },
    "bach_dang_938_tide_ebbing": {
        "base_preset": "bach_dang_938_ngo_quyen",
        "sovereignty_markers": False,
        "camera": {
            "start": {"cx": 0.53, "cy": 0.49, "pitch": 40.0, "zoom": 2.2},
            "end": {"cx": 0.51, "cy": 0.51, "pitch": 47.0, "zoom": 2.85},
        },
        "tidal": {
            "enabled": True,
            "start_m": 0.8,
            "end_m": -2.8,
            "stake_threshold_m": 0.2,
            "stake_beds": [{"p0": (0.44, 0.48), "p1": (0.60, 0.52), "rows": 3, "count": 12}],
        },
    },
    "bach_dang_938_full_trap_revealed": {
        "base_preset": "bach_dang_938_ngo_quyen",
        "sovereignty_markers": False,
        "camera": {
            "start": {"cx": 0.52, "cy": 0.50, "pitch": 42.0, "zoom": 2.5},
            "end": {"cx": 0.50, "cy": 0.50, "pitch": 48.0, "zoom": 2.1},
        },
        "tidal": {
            "enabled": True,
            "start_m": -2.6,
            "end_m": -3.6,
            "stake_threshold_m": -0.5,
            "stake_beds": [{"p0": (0.44, 0.48), "p1": (0.60, 0.52), "rows": 3, "count": 12}],
        },
    },
}


def list_geo_empire_presets() -> list[dict[str, Any]]:
    """Return metadata for all built-in presets."""
    out: list[dict[str, Any]] = []
    for pid, spec in GEO_EMPIRE_PRESETS.items():
        out.append({
            "preset_id": pid,
            "title_vi": spec["title_vi"],
            "year": spec["year"],
            "date_stamp": spec["date_stamp"],
            "summary_vi": spec["summary_vi"],
        })
    return out


def get_geo_empire_preset(preset_id: str) -> dict[str, Any]:
    """Return a deep copy of a named preset (including pilot stage aliases)."""
    key = str(preset_id).strip().lower()
    if key in GEO_EMPIRE_PRESETS:
        return copy.deepcopy(GEO_EMPIRE_PRESETS[key])
    if key in _PRESET_STAGE_OVERRIDES:
        ov = copy.deepcopy(_PRESET_STAGE_OVERRIDES[key])
        base_spec = copy.deepcopy(GEO_EMPIRE_PRESETS[ov.pop("base_preset")])
        base_spec.update(ov)
        base_spec["preset_id"] = key
        return base_spec
    valid = ", ".join(sorted(GEO_EMPIRE_PRESETS))
    raise KeyError(f"Unknown preset '{preset_id}'. Valid: {valid}")


# ---------------------------------------------------------------------------
# Scene Spec Resolution
# ---------------------------------------------------------------------------
def _resolve_scene_spec(scene_spec: str | dict[str, Any]) -> dict[str, Any]:
    """Normalize a preset name, stage alias, or spatial_terrain_ops dict into a full spec."""
    if isinstance(scene_spec, str):
        return get_geo_empire_preset(scene_spec)
    spec = copy.deepcopy(scene_spec)
    base = (
        spec.get("base_preset")
        or spec.get("preset")
        or spec.get("preset_id")
        or spec.get("region_key")
    )
    base_key = str(base).strip().lower() if base else ""
    if base_key and (base_key in GEO_EMPIRE_PRESETS or base_key in _PRESET_STAGE_OVERRIDES) and "terrain" not in spec:
        preset = get_geo_empire_preset(base_key)
        # Map optional pilot_spec spatial_terrain_ops overrides
        if "camera_fly_in" in spec or "camera_pitch_deg" in spec:
            fly = spec.get("camera_fly_in", {})
            p_deg = float(spec.get("camera_pitch_deg", preset["camera"]["start"]["pitch"]))
            preset["camera"] = {
                "start": {
                    "cx": preset["camera"]["start"]["cx"],
                    "cy": preset["camera"]["start"]["cy"],
                    "pitch": max(28.0, p_deg - 4.0),
                    "zoom": float(fly.get("start_zoom", preset["camera"]["start"]["zoom"])),
                },
                "end": {
                    "cx": preset["camera"]["end"]["cx"],
                    "cy": preset["camera"]["end"]["cy"],
                    "pitch": min(52.0, p_deg + 6.0),
                    "zoom": float(fly.get("end_zoom", preset["camera"]["end"]["zoom"])),
                },
            }
        if "tactical_callouts" in spec and "callouts" not in spec:
            mapped_callouts: list[dict[str, Any]] = []
            default_uvs = [(0.52, 0.50), (0.38, 0.34), (0.72, 0.44)]
            for idx, tc in enumerate(spec["tactical_callouts"]):
                uv = tc.get("uv", default_uvs[idx % len(default_uvs)])
                mapped_callouts.append({
                    "uv": uv,
                    "label": str(tc.get("label", "")),
                    "sub": str(tc.get("description", tc.get("sub", ""))),
                    "offset": tc.get("offset", (0.10, -0.06 if idx % 2 == 0 else 0.06)),
                    "t_appear": float(tc.get("t_appear", idx * 0.08)),
                })
            if mapped_callouts:
                spec["callouts"] = mapped_callouts
        preset.update(spec)
        return preset
    # Defaults for fully custom specs
    spec.setdefault("preset_id", "custom")
    spec.setdefault("title_vi", "CHIẾN DỊCH ĐỊA CHIẾN 3D")
    spec.setdefault("date_stamp", "LỊCH SỬ ĐẠI VIỆT")
    spec.setdefault("year", 1288)
    spec.setdefault("seed", 42)
    spec.setdefault("canvas_size", (3840, 2160))
    spec.setdefault("camera", {
        "start": {"cx": 0.5, "cy": 0.4, "pitch": 32.0, "zoom": 1.5},
        "end": {"cx": 0.5, "cy": 0.55, "pitch": 45.0, "zoom": 2.5},
    })
    spec.setdefault("terrain", {"rivers": [], "ridges": []})
    spec.setdefault("factions", {
        "left_name": "ĐẠI VIỆT", "right_name": "ĐỐI PHƯƠNG",
        "left_stat_start": "", "left_stat_end": "",
        "right_stat_start": "", "right_stat_end": "",
        "ratio_start": 0.5, "ratio_end": 0.8,
    })
    spec.setdefault("phases", [{"t_max": 1.01, "label": "DIỄN BIẾN CHIẾN DỊCH"}])
    spec.setdefault("tidal", {"enabled": False})
    spec.setdefault("territories", [])
    spec.setdefault("units", [])
    spec.setdefault("engagements", [])
    spec.setdefault("callouts", [])
    return spec


# ---------------------------------------------------------------------------
# Single Frame Renderer
# ---------------------------------------------------------------------------
def render_geo_empire_clash_frame(
    scene_spec: str | dict[str, Any],
    t_norm: float,
    width: int = 1920,
    height: int = 1080,
) -> np.ndarray:
    """Render a single frame at normalized time t_norm [0..1].

    Returns RGB uint8 array of shape (height, width, 3).
    """
    spec = _resolve_scene_spec(scene_spec)
    t = _clamp(float(t_norm))

    canvas_w, canvas_h = spec.get("canvas_size", (3840, 2160))

    # 1. Load terrain (RGB): real GIS ESRI relief via gis_map_baker, procedural offline fallback
    terrain_cfg = spec.get("terrain", {})
    terrain_canvas = _load_gis_terrain_canvas(
        canvas_w, canvas_h,
        gis_bbox=spec.get("gis_bbox"),
        terrain_cfg=terrain_cfg,
        seed=spec.get("seed", 42),
        use_gis=bool(spec.get("use_gis", True)),
    )

    # 2. Apply territory tints + frontline glow (RGB)
    terrain_canvas = _draw_territory_tint(
        terrain_canvas, spec.get("territories", []), t
    )

    # 3. Apply tidal physics + emerging stake traps (RGB)
    terrain_canvas = _draw_tidal_physics(
        terrain_canvas, spec.get("tidal"), t
    )

    # 4. 3D Perspective camera warp (float32 sub-pixel homography)
    cam_spec = spec.get("camera", {})
    cam_start = cam_spec.get("start", {"cx": 0.5, "cy": 0.4, "pitch": 32.0, "zoom": 1.5})
    cam_end = cam_spec.get("end", {"cx": 0.5, "cy": 0.55, "pitch": 45.0, "zoom": 2.5})

    ease_t = _ease_in_out_cubic(t)
    cam_cx = _lerp(cam_start["cx"], cam_end["cx"], ease_t)
    cam_cy = _lerp(cam_start["cy"], cam_end["cy"], ease_t)
    pitch = _lerp(cam_start["pitch"], cam_end["pitch"], ease_t)
    zoom = _lerp(cam_start["zoom"], cam_end["zoom"], ease_t)

    camera = PerspectiveCamera3D(canvas_w, canvas_h, width, height)
    warped_rgb = camera.warp_canvas(terrain_canvas, cam_cx, cam_cy, pitch, zoom)
    frame = cv2.cvtColor(warped_rgb, cv2.COLOR_RGB2BGR)

    # 5. Draw circular heraldic faction unit tokens (Đông Sơn drum sunburst for Đại Việt)
    for unit in spec.get("units", []):
        t_start = unit.get("t_start", 0.0)
        t_end = unit.get("t_end", 1.0)
        if t < t_start or t > t_end + 0.1:
            continue
        unit_progress = _clamp((t - t_start) / max(0.01, t_end - t_start))
        waypoints = unit.get("waypoints", [(0.5, 0.5)])
        if len(waypoints) > 2:
            smooth_wps = _catmull_rom_spline(waypoints, subdivisions=12)
        else:
            smooth_wps = waypoints
        pos, _heading = _sample_spline_at(smooth_wps, unit_progress)

        sx, sy = camera.project_point(pos[0], pos[1], cam_cx, cam_cy, pitch, zoom)
        if not (-50 <= sx < width + 50 and -50 <= sy < height + 50):
            continue

        faction = unit.get("faction", "dai_viet")
        badge = unit.get("badge", "")
        damaged = False
        if unit.get("badge_damaged") and t >= unit.get("damage_t", 999):
            badge = unit["badge_damaged"]
            damaged = True

        token_radius = max(14, int(min(width, height) * 0.022))
        frame = _draw_faction_token(
            frame, int(sx), int(sy), token_radius,
            faction, badge, damaged=damaged, pulse_phase=t * 3.0,
        )

    # 6. Draw shockwave engagement rings
    for eng in spec.get("engagements", []):
        trigger_t = eng.get("trigger_t", 0.5)
        if t < trigger_t:
            continue
        ring_progress = _clamp((t - trigger_t) / 0.15)
        uv = eng.get("uv", (0.5, 0.5))
        sx, sy = camera.project_point(uv[0], uv[1], cam_cx, cam_cy, pitch, zoom)
        if 0 <= sx < width and 0 <= sy < height:
            max_r = eng.get("max_radius", 80)
            color_bgr = eng.get("color", (60, 82, 236))
            frame = _draw_shockwave_ring(
                frame, int(sx), int(sy), ring_progress,
                max_r, color=color_bgr,
            )

    # 7. Draw collision-free callout arcs (zero rectangular boxes)
    frame = _draw_callout_arcs(
        frame, spec.get("callouts", []),
        camera, cam_cx, cam_cy, pitch, zoom, t,
        spec=spec,
    )

    # 8. Floating HUD overlays over soft Gaussian shadows (compass at bottom-left)
    frame = _draw_troop_counter(frame, spec, t)
    frame = _draw_tidal_hud(frame, spec.get("tidal"), t)
    frame = _draw_phase_label(frame, spec, t)
    frame = _draw_title_card(frame, spec, t)
    frame = _draw_compass(frame)

    # 9. Sovereignty labels (QĐ. HOÀNG SA / QĐ. TRƯỜNG SA) when active / regional sea in view
    frame = _draw_sovereignty_labels(frame, spec, camera, cam_cx, cam_cy, pitch, zoom)

    # Convert BGR back to RGB for callers
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


# ---------------------------------------------------------------------------
# Frame-Sequence & Colab T4 h264_nvenc Render Pipeline (ZERO local CPU fallback)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=4)
def has_nvenc_encoder(ffmpeg_bin: str | None = None) -> bool:
    """Return True iff the active ffmpeg binary exposes hardware h264_nvenc."""
    ff = ffmpeg_bin or shutil.which("ffmpeg")
    if not ff:
        return False
    try:
        res = subprocess.run(
            [ff, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return "h264_nvenc" in (res.stdout or "")
    except Exception:
        return False


def build_geo_empire_nvenc_cmd(
    out_mp4_path: str | Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    *,
    input_frames_pattern: str | None = None,
    crf: int = 18,
    ffmpeg_bin: str | None = None,
) -> list[str]:
    """Build FFmpeg Colab Tesla T4 h264_nvenc command (sole encoder per AGENTS.md)."""
    ff = ffmpeg_bin or shutil.which("ffmpeg") or "ffmpeg"
    w = int(width) - (int(width) % 2)
    h = int(height) - (int(height) % 2)
    fps_i = max(1, int(fps))

    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error"]
    if input_frames_pattern:
        cmd.extend(["-framerate", str(fps_i), "-i", str(input_frames_pattern)])
    else:
        cmd.extend([
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{w}x{h}",
            "-r", str(fps_i),
            "-i", "-",
        ])
    cmd.extend([
        "-an",
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-cq", str(int(crf)),
        "-b:v", "10M",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_mp4_path),
    ])
    return cmd


def render_geo_empire_clash_frame_sequence(
    scene_spec: str | dict[str, Any],
    out_dir: str | Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    *,
    duration_sec: float = 4.8,
    jpeg_quality: int = 92,
    fmt: str = "jpg",
) -> dict[str, Any]:
    """Render 3D geo-empire clash frames as a Q92 JPEG/PNG sequence for Colab T4 h264_nvenc.

    Produces `frame_0000.jpg` .. `frame_NNNN.jpg` inside `out_dir` with zero local CPU
    video encoding.
    """
    seq_dir = Path(out_dir)
    seq_dir.mkdir(parents=True, exist_ok=True)

    w = int(width) - (int(width) % 2)
    h = int(height) - (int(height) % 2)
    fps_i = max(1, int(fps))
    dur_f = max(0.2, float(duration_sec))
    n_frames = max(2, int(round(dur_f * fps_i)))
    ext = "png" if str(fmt).lower().lstrip(".") == "png" else "jpg"

    spec = _resolve_scene_spec(scene_spec)
    frame_paths: list[str] = []

    encode_params = (
        [cv2.IMWRITE_JPEG_QUALITY, int(_clamp(jpeg_quality, 50, 100))]
        if ext == "jpg"
        else []
    )

    for i in range(n_frames):
        t_norm = i / float(max(1, n_frames - 1))
        frame_rgb = render_geo_empire_clash_frame(spec, t_norm, w, h)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        fpath = seq_dir / f"frame_{i:04d}.{ext}"
        cv2.imwrite(str(fpath), frame_bgr, encode_params)
        frame_paths.append(str(fpath))

    return {
        "frames_dir": str(seq_dir),
        "frame_pattern": str(seq_dir / f"frame_%04d.{ext}"),
        "frame_paths": frame_paths,
        "width": w,
        "height": h,
        "fps": fps_i,
        "duration_sec": dur_f,
        "n_frames": n_frames,
        "preset_id": spec.get("preset_id", "custom"),
        "engine_version": ENGINE_VERSION,
    }


# ---------------------------------------------------------------------------
# Public API: render_geo_empire_clash_mp4 (Colab T4 h264_nvenc ONLY)
# ---------------------------------------------------------------------------
def render_geo_empire_clash_mp4(
    scene_spec: str | dict[str, Any],
    out_mp4_path: str | Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    *,
    duration_sec: float = 4.8,
    crf: int = 18,
) -> dict[str, Any]:
    """Render a 3D perspective geo-terrain & faction clash animation to MP4 via h264_nvenc.

    Per AGENTS.md §2, Colab Tesla T4 `FFmpeg h264_nvenc` is the sole video encoder
    (zero local CPU software encoder fallback). On hosts without `h264_nvenc`, callers
    should stage frames via `render_geo_empire_clash_frame_sequence()` and encode on Colab T4.
    """
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg binary not found in PATH")
    if not has_nvenc_encoder(ffmpeg_bin):
        raise RuntimeError(
            "h264_nvenc hardware encoder unavailable on this host; per AGENTS.md use "
            "render_geo_empire_clash_frame_sequence() locally and encode on Colab T4 h264_nvenc."
        )

    out_path = Path(out_mp4_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    w = int(width) - (int(width) % 2)
    h = int(height) - (int(height) % 2)
    fps_i = max(1, int(fps))
    dur_f = max(0.2, float(duration_sec))
    n_frames = max(2, int(round(dur_f * fps_i)))

    spec = _resolve_scene_spec(scene_spec)
    cmd = build_geo_empire_nvenc_cmd(
        out_path, w, h, fps_i, crf=crf, ffmpeg_bin=ffmpeg_bin,
    )

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(n_frames):
            t_norm = i / float(max(1, n_frames - 1))
            frame_rgb = render_geo_empire_clash_frame(spec, t_norm, w, h)
            proc.stdin.write(frame_rgb.tobytes())
        proc.stdin.close()
        stderr_bytes = proc.stderr.read() if proc.stderr else b""
        ret = proc.wait(timeout=120)
    except Exception:
        proc.kill()
        proc.wait()
        raise

    if ret != 0 or not out_path.is_file() or out_path.stat().st_size == 0:
        err_msg = stderr_bytes.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"render_geo_empire_clash_mp4 (h264_nvenc) failed (exit {ret}): {err_msg}")

    return {
        "path": str(out_path),
        "width": w,
        "height": h,
        "fps": fps_i,
        "duration_sec": dur_f,
        "n_frames": n_frames,
        "encoder": "h264_nvenc",
        "preset_id": spec.get("preset_id", "custom"),
        "engine_version": ENGINE_VERSION,
    }
