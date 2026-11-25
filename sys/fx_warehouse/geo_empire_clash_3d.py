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
ENGINE_VERSION = "1.1.0"
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

    # Apply ridges
    for ridge in (ridges or []):
        pts = ridge.get("points", [])
        height_val = ridge.get("height", 0.6)
        sigma = ridge.get("sigma", 0.08)
        ridge_mask = np.zeros((h, w), dtype=np.float32)
        for px, py in pts:
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            dist = np.sqrt(((xx / w - px) ** 2) + ((yy / h - py) ** 2))
            ridge_mask = np.maximum(ridge_mask, np.exp(-dist ** 2 / (2.0 * sigma ** 2)))
        terrain = np.clip(terrain + ridge_mask * height_val * 0.4, 0, 1)

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


# GIS bbox presets for real ESRI relief terrain
_GIS_BBOX_PRESETS: dict[str, dict[str, Any]] = {
    "bach_dang": {
        "lon_min": 106.55, "lat_min": 20.75,
        "lon_max": 107.05, "lat_max": 21.05,
        "region_key": "bach_dang_estuary",
    },
    "nhu_nguyet": {
        "lon_min": 105.90, "lat_min": 21.10,
        "lon_max": 106.40, "lat_max": 21.45,
        "region_key": "nhu_nguyet_river",
    },
    "northern_dai_viet": {
        "lon_min": 104.5, "lat_min": 18.5,
        "lon_max": 110.0, "lat_max": 23.5,
        "region_key": "northern_dai_viet",
    },
}


def _load_gis_terrain_canvas(
    width: int,
    height: int,
    gis_bbox: dict[str, Any] | str | None = None,
    terrain_cfg: dict[str, Any] | None = None,
    seed: int = 42,
) -> np.ndarray:
    """Load real ESRI relief terrain via gis_map_baker, falling back to procedural.

    Priority:
      1. If gis_map_baker + prebaked .npz available → colorize_relief_plate (real GIS).
      2. Else → _generate_procedural_terrain (offline test fallback).
    """
    if gis_bbox is not None:
        bbox = _GIS_BBOX_PRESETS.get(gis_bbox) if isinstance(gis_bbox, str) else dict(gis_bbox)
        if bbox:
            try:
                from fx_warehouse.gis_map_baker import (  # noqa: F811
                    bake_region,
                    colorize_relief_plate,
                    load_prebaked_region,
                )
                rk = bbox.get("region_key", "custom_geo_empire")
                bake_region(
                    rk,
                    lon_min=bbox.get("lon_min"),
                    lon_max=bbox.get("lon_max"),
                    lat_min=bbox.get("lat_min"),
                    lat_max=bbox.get("lat_max"),
                    width=width,
                    height=height,
                )
                npz_data = load_prebaked_region(rk)
                plate = colorize_relief_plate(npz_data)
                # Resize to target canvas dimensions
                if plate.shape[:2] != (height, width):
                    plate = cv2.resize(plate, (width, height), interpolation=cv2.INTER_LANCZOS4)
                return plate
            except Exception:
                pass  # Fallback to procedural

    # Offline fallback: procedural terrain
    cfg = terrain_cfg or {}
    return _generate_procedural_terrain(
        width, height,
        rivers=cfg.get("rivers"),
        ridges=cfg.get("ridges"),
        sea_region=cfg.get("sea_region"),
        seed=seed,
    )


# ---------------------------------------------------------------------------
# Territory Frontline Rendering
# ---------------------------------------------------------------------------
def _draw_territory_tint(
    canvas: np.ndarray,
    territory_polygons: list[dict[str, Any]],
    t_norm: float,
) -> np.ndarray:
    """Apply animated territory control tint + luminous frontline wave."""
    h, w = canvas.shape[:2]
    out = canvas.astype(np.float32) / 255.0

    for terr in territory_polygons:
        faction = terr.get("faction", "dai_viet")
        palette = FACTION_PALETTES.get(faction, FACTION_PALETTES["dai_viet"])
        region = terr.get("region", {})  # x0,y0,x1,y1 normalized
        advance = _clamp(terr.get("advance_start", 0.3) +
                         (terr.get("advance_end", 0.7) - terr.get("advance_start", 0.3)) *
                         _ease_in_out_cubic(t_norm))

        x0 = int(region.get("x0", 0.0) * w)
        y0 = int(region.get("y0", 0.0) * h)
        x1 = int(region.get("x1", 0.5) * w)
        y1 = int(region.get("y1", 1.0) * h)

        # Territory tint mask
        tint_mask = np.zeros((h, w), dtype=np.float32)
        tint_mask[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = 1.0
        tint_mask = cv2.GaussianBlur(tint_mask, (0, 0), sigmaX=w * 0.02)

        # Advance-dependent coverage
        advance_x = x0 + int((x1 - x0) * advance)
        advance_mask = np.zeros((h, w), dtype=np.float32)
        advance_mask[max(0, y0):min(h, y1), max(0, x0):min(w, advance_x)] = 1.0
        advance_mask = cv2.GaussianBlur(advance_mask, (0, 0), sigmaX=w * 0.015)

        combined = tint_mask * advance_mask

        # Apply color tint
        tint_color = np.array(palette["primary"], dtype=np.float32) / 255.0
        tint_strength = 0.25
        for c in range(3):
            out[..., c] = out[..., c] * (1.0 - combined * tint_strength) + \
                          tint_color[c] * combined * tint_strength

        # Luminous frontline edge glow
        glow_color = np.array(palette["glow"], dtype=np.float32) / 255.0
        edge_width = max(3, int(w * 0.006))
        edge_col = max(0, min(w - 1, advance_x))
        glow_strip = np.zeros((h, w), dtype=np.float32)
        left = max(0, edge_col - edge_width)
        right = min(w, edge_col + edge_width)
        glow_strip[max(0, y0):min(h, y1), left:right] = 1.0
        glow_strip = cv2.GaussianBlur(glow_strip, (0, 0), sigmaX=edge_width * 0.8)
        # Pulsing glow
        pulse = 0.6 + 0.4 * math.sin(t_norm * math.pi * 6.0)
        for c in range(3):
            out[..., c] = np.clip(
                out[..., c] + glow_strip * glow_color[c] * pulse * 0.7,
                0, 1
            )

    return np.clip(out * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Tidal / Chokepoint Physics
# ---------------------------------------------------------------------------
def _draw_tidal_physics(
    canvas: np.ndarray,
    tidal_spec: dict[str, Any] | None,
    t_norm: float,
) -> np.ndarray:
    """Render tidal ebb revealing submerged stake traps."""
    if not tidal_spec or not tidal_spec.get("enabled"):
        return canvas

    h, w = canvas.shape[:2]
    out = canvas.copy()

    start_m = tidal_spec.get("start_m", 1.4)
    end_m = tidal_spec.get("end_m", -3.8)
    threshold_m = tidal_spec.get("stake_threshold_m", -1.2)
    current_m = _lerp(start_m, end_m, _ease_in_out_cubic(t_norm))

    # Stake trap visualization
    stake_beds = tidal_spec.get("stake_beds", [])
    if current_m < threshold_m:
        reveal_progress = _clamp((threshold_m - current_m) / max(0.1, threshold_m - end_m))
        for bed in stake_beds:
            p0 = bed.get("p0", (0.4, 0.5))
            p1 = bed.get("p1", (0.6, 0.5))
            rows = bed.get("rows", 3)
            count = bed.get("count", 8)
            for row in range(rows):
                for col in range(count):
                    frac_x = col / max(1, count - 1)
                    frac_y = row / max(1, rows - 1) * 0.03
                    sx = int(_lerp(p0[0], p1[0], frac_x) * w)
                    sy = int((_lerp(p0[1], p1[1], frac_x) + frac_y) * h)
                    # Iron-tipped stake: dark brown with iron tip
                    if 0 <= sx < w and 0 <= sy < h:
                        stake_len = max(3, int(h * 0.012 * reveal_progress))
                        cv2.line(
                            out,
                            (sx, sy),
                            (sx, sy - stake_len),
                            (60, 40, 25),
                            max(1, int(w * 0.0015)),
                            cv2.LINE_AA,
                        )
                        # Iron tip
                        cv2.circle(out, (sx, sy - stake_len), max(1, int(w * 0.002)),
                                   (140, 130, 120), -1, cv2.LINE_AA)

    # Tidal level indicator bar (bottom-left HUD)
    bar_x = int(w * 0.03)
    bar_y = int(h * 0.75)
    bar_w_px = int(w * 0.015)
    bar_h_px = int(h * 0.18)
    # Background
    cv2.rectangle(out, (bar_x, bar_y), (bar_x + bar_w_px, bar_y + bar_h_px),
                  (20, 25, 35), -1)
    cv2.rectangle(out, (bar_x, bar_y), (bar_x + bar_w_px, bar_y + bar_h_px),
                  (100, 110, 130), 1, cv2.LINE_AA)
    # Water level fill
    level_frac = _clamp((current_m - end_m) / max(0.1, start_m - end_m))
    fill_top = bar_y + bar_h_px - int(bar_h_px * level_frac)
    water_color = (60, 100, 140) if current_m > 0 else (40, 70, 100)
    cv2.rectangle(out, (bar_x + 1, fill_top), (bar_x + bar_w_px - 1, bar_y + bar_h_px - 1),
                  water_color, -1)
    # Threshold line
    thresh_frac = _clamp((threshold_m - end_m) / max(0.1, start_m - end_m))
    thresh_y = bar_y + bar_h_px - int(bar_h_px * thresh_frac)
    cv2.line(out, (bar_x - 4, thresh_y), (bar_x + bar_w_px + 4, thresh_y),
             (220, 80, 60), 1, cv2.LINE_AA)

    return out


# ---------------------------------------------------------------------------
# Faction Shield / Heraldic Token Rendering
# ---------------------------------------------------------------------------
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
    """Draw a crisp circular heraldic faction token with emblem and badge text."""
    out = canvas.copy()
    palette = FACTION_PALETTES.get(faction, FACTION_PALETTES["dai_viet"])

    # Outer shield glow ring
    glow_r = int(radius * 1.4)
    glow_alpha = 0.3 + 0.15 * math.sin(pulse_phase * math.pi * 2.0)
    overlay = out.copy()
    cv2.circle(overlay, (cx, cy), glow_r, palette["glow"], -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, glow_alpha, out, 1.0 - glow_alpha, 0, out)

    # Shield body (filled circle)
    body_color = palette["primary"] if not damaged else (80, 30, 30)
    cv2.circle(out, (cx, cy), radius, body_color, -1, cv2.LINE_AA)

    # Shield rim
    rim_thickness = max(2, int(radius * 0.12))
    cv2.circle(out, (cx, cy), radius, palette["shield_rim"], rim_thickness, cv2.LINE_AA)

    # Inner emblem circle
    inner_r = int(radius * 0.55)
    cv2.circle(out, (cx, cy), inner_r, palette["secondary"], max(1, int(radius * 0.06)), cv2.LINE_AA)

    # Simple emblem symbol: Đông Sơn bronze drum sunburst for Đại Việt, cross for enemy
    emblem_color = palette["emblem_fg"]
    sym_r = int(inner_r * 0.5)
    if faction == "dai_viet":
        # Đông Sơn bronze drum concentric sunburst (period-accurate, not modern star)
        # Concentric circle (war drum ring)
        cv2.circle(out, (cx, cy), int(sym_r * 0.8), emblem_color,
                   max(1, int(radius * 0.04)), cv2.LINE_AA)
        cv2.circle(out, (cx, cy), int(sym_r * 0.35), emblem_color,
                   max(1, int(radius * 0.03)), cv2.LINE_AA)
        # Radial sunburst spokes (12 rays like Đông Sơn bronze drum)
        n_rays = 12
        for i in range(n_rays):
            ang = i * 2.0 * math.pi / n_rays - math.pi / 2.0
            inner_pt = (int(cx + sym_r * 0.35 * math.cos(ang)),
                        int(cy + sym_r * 0.35 * math.sin(ang)))
            outer_pt = (int(cx + sym_r * 0.8 * math.cos(ang)),
                        int(cy + sym_r * 0.8 * math.sin(ang)))
            cv2.line(out, inner_pt, outer_pt, emblem_color,
                     max(1, int(radius * 0.03)), cv2.LINE_AA)
        # Center dot
        cv2.circle(out, (cx, cy), max(2, int(sym_r * 0.12)), emblem_color, -1, cv2.LINE_AA)
    else:
        # Cross/sword pattern for enemy factions
        cv2.line(out, (cx - sym_r, cy), (cx + sym_r, cy), emblem_color,
                 max(1, int(radius * 0.08)), cv2.LINE_AA)
        cv2.line(out, (cx, cy - sym_r), (cx, cy + sym_r), emblem_color,
                 max(1, int(radius * 0.08)), cv2.LINE_AA)

    # Badge text below token
    if badge_text:
        font_size = max(10, int(radius * 0.42))
        pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        fnt = _get_font(font_size, condensed=True)
        bbox = draw.textbbox((0, 0), badge_text, font=fnt)
        tw = bbox[2] - bbox[0]
        tx = cx - tw // 2
        ty = cy + radius + max(4, int(radius * 0.15))
        # Shadow
        draw.text((tx + 1, ty + 1), badge_text, fill=(0, 0, 0), font=fnt)
        # Text
        text_color = (255, 200, 100) if not damaged else (200, 60, 50)
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

    # Soft Gaussian scrim behind HUD text (zero solid rectangles)
    scrim_overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    scrim_draw = ImageDraw.Draw(scrim_overlay)
    scrim_h = int(h * 0.065)
    for _sy in range(bar_y - 4, bar_y + scrim_h):
        alpha_v = max(0, min(100, int(90 * (1.0 - abs(_sy - (bar_y + scrim_h // 2)) / (scrim_h * 0.6)))))
        scrim_draw.line([(bar_margin - 10, _sy), (bar_margin + bar_width + 10, _sy)],
                        fill=(5, 5, 10, alpha_v))
    pil_img = Image.alpha_composite(pil_img.convert("RGBA"), scrim_overlay).convert("RGB")
    draw = ImageDraw.Draw(pil_img)

    # Power ratio thin line (1px, not a bar)
    split_x = bar_margin + int(bar_width * ratio)
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.line(cv2_img, (bar_margin, bar_y + 2), (split_x, bar_y + 2),
             (28, 36, 172), 2, cv2.LINE_AA)
    cv2.line(cv2_img, (split_x, bar_y + 2), (bar_margin + bar_width, bar_y + 2),
             (88, 66, 40), 2, cv2.LINE_AA)
    # Small dot at split
    cv2.circle(cv2_img, (split_x, bar_y + 2), 4, (200, 190, 170), -1, cv2.LINE_AA)

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

    # Soft Gaussian scrim (zero solid rectangular borders)
    scrim_pad = int(h * 0.012)
    scrim_w = tw + scrim_pad * 4
    scrim_h_px = (bbox[3] - bbox[1]) + scrim_pad * 2
    scrim_img = Image.new("L", (scrim_w, scrim_h_px), 0)
    scrim_draw_tmp = ImageDraw.Draw(scrim_img)
    scrim_draw_tmp.ellipse(
        [0, 0, scrim_w, scrim_h_px],
        fill=140,
    )
    scrim_img = scrim_img.filter(ImageFilter.GaussianBlur(radius=max(3, scrim_pad)))
    overlay_img = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    scrim_rgba = Image.merge("RGBA", (
        Image.new("L", scrim_img.size, 10),
        Image.new("L", scrim_img.size, 10),
        Image.new("L", scrim_img.size, 15),
        scrim_img,
    ))
    overlay_img.paste(scrim_rgba, (tx - scrim_pad * 2, ty - scrim_pad))
    pil_img = Image.alpha_composite(pil_img.convert("RGBA"), overlay_img).convert("RGB")
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
def _draw_callout_arcs(
    canvas: np.ndarray,
    callouts: list[dict[str, Any]],
    camera: PerspectiveCamera3D,
    cam_cx: float,
    cam_cy: float,
    pitch_deg: float,
    zoom: float,
    t_norm: float,
) -> np.ndarray:
    """Draw clean range/width callout arcs with labels (zero rectangular boxes)."""
    out = canvas.copy()
    h, w = canvas.shape[:2]

    for callout in callouts:
        t_appear = callout.get("t_appear", 0.0)
        if t_norm < t_appear:
            continue
        fade = _clamp((t_norm - t_appear) / 0.08)

        uv = callout.get("uv", (0.5, 0.5))
        label = callout.get("label", "")
        sub = callout.get("sub", "")
        offset = callout.get("offset", (0.1, -0.05))

        # Project to screen
        sx, sy = camera.project_point(uv[0], uv[1], cam_cx, cam_cy, pitch_deg, zoom)
        if not (0 <= sx < w and 0 <= sy < h):
            continue

        ex = sx + offset[0] * w
        ey = sy + offset[1] * h

        # Leader line (arc)
        alpha = fade * 0.8
        line_color = (int(200 * alpha), int(190 * alpha), int(170 * alpha))
        cv2.line(out, (int(sx), int(sy)), (int(ex), int(ey)),
                 line_color, 1, cv2.LINE_AA)
        # Dot at anchor
        cv2.circle(out, (int(sx), int(sy)), max(3, int(w * 0.003)),
                   (int(255 * alpha), int(220 * alpha), int(140 * alpha)),
                   -1, cv2.LINE_AA)

        # Label text
        if label:
            pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            lbl_size = max(11, int(h * 0.018))
            lbl_fnt = _get_font(lbl_size, condensed=True)
            lbl_color = (int(250 * fade), int(240 * fade), int(220 * fade))
            draw.text((int(ex) + 4, int(ey) - lbl_size - 2), label,
                      fill=lbl_color, font=lbl_fnt)
            if sub:
                sub_size = max(9, lbl_size - 4)
                sub_fnt = _get_font(sub_size, condensed=True)
                sub_color = (int(200 * fade), int(190 * fade), int(160 * fade))
                draw.text((int(ex) + 4, int(ey) + 2), sub,
                          fill=sub_color, font=sub_fnt)
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
    """Render HOÀNG SA / TRƯỜNG SA sovereignty markers when sea region is in frame.

    Active when spec contains 'sovereignty_markers': True, or when the terrain
    includes a sea_region indicating regional Vietnam sea is visible.
    """
    if not spec.get("sovereignty_markers", True):
        return canvas

    # Only render if terrain has a sea region (indicating regional sea is visible)
    terrain_cfg = spec.get("terrain", {})
    sea = terrain_cfg.get("sea_region")
    if not sea:
        return canvas

    h, w = canvas.shape[:2]
    out = canvas.copy()

    for label_info in SOVEREIGNTY_LABELS:
        text = label_info["text"]
        # Map sovereignty label coords to approximate canvas UV.
        # Use sea region's center area and offset for each label.
        # Hoang Sa is in upper-right sea, Truong Sa in lower-right sea.
        sea_x0 = sea.get("x0", 0.75)
        sea_y0 = sea.get("y0", 0.0)
        sea_x1 = sea.get("x1", 1.0)
        sea_y1 = sea.get("y1", 1.0)

        if text == "HOÀNG SA":
            uv_x = (sea_x0 + sea_x1) * 0.5
            uv_y = sea_y0 + (sea_y1 - sea_y0) * 0.3
        else:  # TRƯỜNG SA
            uv_x = (sea_x0 + sea_x1) * 0.5
            uv_y = sea_y0 + (sea_y1 - sea_y0) * 0.65

        # Project to screen
        sx, sy = camera.project_point(uv_x, uv_y, cam_cx, cam_cy, pitch_deg, zoom)
        if not (-20 <= sx < w + 20 and -20 <= sy < h + 20):
            continue

        # Render sovereignty text with crosshair marker
        pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        sov_size = max(10, int(h * 0.015))
        sov_fnt = _get_font(sov_size, condensed=True)
        sov_bbox = draw.textbbox((0, 0), text, font=sov_fnt)
        tw = sov_bbox[2] - sov_bbox[0]

        tx = int(sx) - tw // 2
        ty = int(sy) - sov_size // 2

        # Crosshair marker
        marker_r = max(4, int(h * 0.006))
        cv2.circle(out, (int(sx), int(sy)), marker_r, (200, 180, 100), 1, cv2.LINE_AA)
        cv2.line(out, (int(sx) - marker_r - 2, int(sy)), (int(sx) + marker_r + 2, int(sy)),
                 (200, 180, 100), 1, cv2.LINE_AA)
        cv2.line(out, (int(sx), int(sy) - marker_r - 2), (int(sx), int(sy) + marker_r + 2),
                 (200, 180, 100), 1, cv2.LINE_AA)

        # Text below crosshair
        pil_img = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        label_y = int(sy) + marker_r + 3
        # Shadow
        draw.text((tx + 1, label_y + 1), text, fill=(0, 0, 0), font=sov_fnt)
        # Main text — golden sovereignty color
        draw.text((tx, label_y), text, fill=(220, 190, 100), font=sov_fnt)
        # "QĐ." prefix below
        qd_text = f"QĐ. {text}"
        qd_bbox = draw.textbbox((0, 0), qd_text, font=sov_fnt)
        qd_w = qd_bbox[2] - qd_bbox[0]
        qd_x = int(sx) - qd_w // 2
        draw.text((qd_x + 1, label_y + sov_size + 2), qd_text,
                  fill=(0, 0, 0), font=sov_fnt)
        draw.text((qd_x, label_y + sov_size + 1), qd_text,
                  fill=(180, 160, 90), font=sov_fnt)

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
            "subtitle_vi": "CỌC GỖ BỌC SẮT ĐẠI PHÁ HOẰNG THÁO",
            "year": 938,
            "date_stamp": "MÙA ĐÔNG 938 • CỬA SÔNG BẠCH ĐẰNG",
            "summary_vi": "Ngô Quyền dàn trận cọc gỗ bọc sắt tại cửa sông Bạch Đằng, nhử chiến thuyền Lưu Hoằng Tháo lúc triều cường vào sâu, đợi triều rút mắc cọc rồi tung quân đánh tiêu diệt gọn.",
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
                "right_name": "NAM HÁN (HOẰNG THÁO)",
                "left_stat_start": "THUỶ QUÂN NGÔ QUYỀN",
                "left_stat_end": "TOÀN THẮNG • HOẰNG THÁO TỬ TRẬN",
                "right_stat_start": "CHIẾN THUYỀN LƯU HOẰNG THÁO",
                "right_stat_end": "HẠM ĐỘI BỊ ĐẮM GỌN",
                "ratio_start": 0.45,
                "ratio_end": 0.88,
            },
            "phases": [
                {"t_max": 0.35, "label": "PHA I • NGÔ QUYỀN NHỬ THUYỀN NAM HÁN VÀO CỬA SÔNG LÚC TRIỀU CƯỜNG"},
                {"t_max": 0.70, "label": "PHA II • TRIỀU RÚT LỘ BÃI CỌC SẮT — THUYỀN ĐỊCH MẮC CỌC"},
                {"t_max": 1.01, "label": "PHA III • TUNG QUÂN ĐÁNH ĐẮM TOÀN BỘ — HOẰNG THÁO TỬ TRẬN"},
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
                {"faction": "southern_han", "badge": "HOẰNG THÁO",
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
    """Return a deep copy of a named preset."""
    key = str(preset_id).strip().lower()
    if key not in GEO_EMPIRE_PRESETS:
        valid = ", ".join(sorted(GEO_EMPIRE_PRESETS))
        raise KeyError(f"Unknown preset '{preset_id}'. Valid: {valid}")
    return copy.deepcopy(GEO_EMPIRE_PRESETS[key])


# ---------------------------------------------------------------------------
# Scene Spec Resolution
# ---------------------------------------------------------------------------
def _resolve_scene_spec(scene_spec: str | dict[str, Any]) -> dict[str, Any]:
    """Normalize a preset name or custom dict into a full scene spec."""
    if isinstance(scene_spec, str):
        return get_geo_empire_preset(scene_spec)
    spec = copy.deepcopy(scene_spec)
    base = spec.get("base_preset") or spec.get("preset_id")
    if base and str(base) in GEO_EMPIRE_PRESETS and "terrain" not in spec:
        preset = get_geo_empire_preset(str(base))
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

    # 1. Load terrain: real GIS ESRI relief if available, else procedural fallback
    terrain_cfg = spec.get("terrain", {})
    terrain_canvas = _load_gis_terrain_canvas(
        canvas_w, canvas_h,
        gis_bbox=spec.get("gis_bbox"),
        terrain_cfg=terrain_cfg,
        seed=spec.get("seed", 42),
    )

    # 2. Apply territory tints + frontline glow
    terrain_canvas = _draw_territory_tint(
        terrain_canvas, spec.get("territories", []), t
    )

    # 3. Apply tidal physics + stake traps
    terrain_canvas = _draw_tidal_physics(
        terrain_canvas, spec.get("tidal"), t
    )

    # 4. 3D Perspective camera warp
    cam_spec = spec.get("camera", {})
    cam_start = cam_spec.get("start", {"cx": 0.5, "cy": 0.4, "pitch": 32.0, "zoom": 1.5})
    cam_end = cam_spec.get("end", {"cx": 0.5, "cy": 0.55, "pitch": 45.0, "zoom": 2.5})

    ease_t = _ease_in_out_cubic(t)
    cam_cx = _lerp(cam_start["cx"], cam_end["cx"], ease_t)
    cam_cy = _lerp(cam_start["cy"], cam_end["cy"], ease_t)
    pitch = _lerp(cam_start["pitch"], cam_end["pitch"], ease_t)
    zoom = _lerp(cam_start["zoom"], cam_end["zoom"], ease_t)

    camera = PerspectiveCamera3D(canvas_w, canvas_h, width, height)
    frame = camera.warp_canvas(terrain_canvas, cam_cx, cam_cy, pitch, zoom)

    # 5. Draw faction unit tokens
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

        # Project to screen
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

    # 7. Draw callout arcs
    frame = _draw_callout_arcs(
        frame, spec.get("callouts", []),
        camera, cam_cx, cam_cy, pitch, zoom, t,
    )

    # 8. HUD overlays
    frame = _draw_troop_counter(frame, spec, t)
    frame = _draw_phase_label(frame, spec, t)
    frame = _draw_title_card(frame, spec, t)
    frame = _draw_compass(frame)

    # 9. Sovereignty labels (HOÀNG SA / TRƯỜNG SA) when sea region in view
    frame = _draw_sovereignty_labels(frame, spec, camera, cam_cx, cam_cy, pitch, zoom)

    # Convert BGR to RGB for output
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


# ---------------------------------------------------------------------------
# Public API: render_geo_empire_clash_mp4
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
    """Render a 3D perspective geo-terrain & faction clash animation to MP4.

    Args:
        scene_spec: Preset name string (e.g. 'bach_dang_938_ngo_quyen') or
                    custom scene spec dict.
        out_mp4_path: Output .mp4 file path.
        width: Output width (default 1920). Must be even.
        height: Output height (default 1080). Must be even.
        fps: Frame rate (default 30).
        duration_sec: Clip duration in seconds (default 4.8).
        crf: H.264 CRF quality (default 18, lower = higher quality).

    Returns:
        dict with keys: path, width, height, fps, duration_sec, n_frames,
        preset_id, engine_version.
    """
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg binary not found in PATH")

    out_path = Path(out_mp4_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Enforce even dimensions for yuv420p
    w = int(width) - (int(width) % 2)
    h = int(height) - (int(height) % 2)
    fps_i = max(1, int(fps))
    dur_f = max(0.2, float(duration_sec))
    n_frames = max(2, int(round(dur_f * fps_i)))

    spec = _resolve_scene_spec(scene_spec)

    cmd = [
        ffmpeg_bin,
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}",
        "-r", str(fps_i),
        "-i", "-",
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", str(int(crf)),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_path),
    ]

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
        raise RuntimeError(f"render_geo_empire_clash_mp4 failed (exit {ret}): {err_msg}")

    return {
        "path": str(out_path),
        "width": w,
        "height": h,
        "fps": fps_i,
        "duration_sec": dur_f,
        "n_frames": n_frames,
        "preset_id": spec.get("preset_id", "custom"),
        "engine_version": ENGINE_VERSION,
    }
