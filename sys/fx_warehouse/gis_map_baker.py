"""Topic-agnostic Web Mercator GIS Map Baker & Luminance-Preserving Renderer.

Permanent reusable module for Video Pilot World-A maps:
1. Downloads & caches ESRI World Imagery + ESRI World Hillshade XYZ tiles.
2. Loads Natural Earth 10m land, 250+ country polygons, land boundary lines,
   and `vietnam_sovereignty_override.geojson` (locking Hoang Sa & Truong Sa to VNM).
3. Pre-bakes Web Mercator (EPSG:3857) isotropic 16:9 region plates into compact
   `.npz` files containing:
     - `l_base`: normalized terrain luminance (uint8, snow peaks 0.78..0.98)
     - `land_mask`: anti-aliased land/island mask (uint8)
     - `country_id_map`: per-pixel country index (int16) for all 250+ countries
     - `country_records_json`: metadata mapping id -> {iso_a3, adm0_a3, admin, name}
     - `border_lines_json`: clipped neutral land boundary polylines in [0..1]
     - `country_borders_json`: per-country boundary rings in [0..1]
     - `meta_json`: region bounds, Mercator bounds, dimensions, flags
4. Provides both fast NumPy/OpenCV `colorize_relief_plate()` and PyTorch CUDA
   `blend_map_gpu()` 3-stop luminance-preserving colorize + high-pass detail.
5. Provides crisp screen-space `render_gis_vector_overlays()` with glowing
   territory borders, arc-length dotted trails, SVG Map Pin Badges (`resvg_py`),
   Bullseye Ripples with centered white pointer labels, and single-pass
   screen-space `HOÀNG SA` / `TRƯỜNG SA` sovereignty markers.
"""

from __future__ import annotations

import io
import json
import math
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import resvg_py
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely import transform as shapely_transform
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPolygon, Polygon, box, shape
from shapely.ops import unary_union

# ---------------------------------------------------------------------------
# Paths & Constants
# ---------------------------------------------------------------------------
SYS_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SYS_DIR / "assets"
GIS_CACHE_DIR = ASSETS_DIR / "gis_cache"
GEOJSON_DIR = GIS_CACHE_DIR / "geojson"
TILES_DIR = GIS_CACHE_DIR / "tiles"
PREBAKED_DIR = GIS_CACHE_DIR / "prebaked"
MAP_ICONS_DIR = ASSETS_DIR / "map_icons"

ESRI_IMAGERY_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_HILLSHADE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}"

MAX_MERC_LAT = 85.05112878
OCEAN_RGB = (8, 11, 14)  # #080B0E

# Canonical territory 3-stop ramps: (dark_valley L=0.15, mid_plain L=0.45, snow_peak L=0.95)
TERRITORY_RAMPS: dict[str, dict[str, Any]] = {
    "red": {
        "dark": (0x3A / 255.0, 0x12 / 255.0, 0x14 / 255.0),     # #3A1214
        "mid": (0x7B / 255.0, 0x36 / 255.0, 0x38 / 255.0),      # #7B3638
        "snow": (0xE4 / 255.0, 0x96 / 255.0, 0x96 / 255.0),     # #E49696
        "border": (255, 107, 107),                               # #FF6B6B
        "trail": (216, 48, 42),                                  # #D8302A
        "badge": (184, 29, 36),                                  # #B81D24
    },
    "blue": {
        "dark": (0x16 / 255.0, 0x2C / 255.0, 0x3D / 255.0),     # #162C3D
        "mid": (0x3A / 255.0, 0x67 / 255.0, 0x88 / 255.0),      # #3A6788
        "snow": (0x8C / 255.0, 0xC2 / 255.0, 0xEB / 255.0),     # #8CC2EB
        "border": (115, 184, 255),                               # #73B8FF
        "trail": (58, 128, 188),                                 # #3A80BC
        "badge": (37, 99, 168),                                  # #2563A8
    },
    "amber": {
        "dark": (0x4A / 255.0, 0x33 / 255.0, 0x0E / 255.0),     # #4A330E
        "mid": (0x9E / 255.0, 0x72 / 255.0, 0x27 / 255.0),      # #9E7227
        "snow": (0xEB / 255.0, 0xD0 / 255.0, 0x8A / 255.0),     # #EBD08A
        "border": (229, 181, 28),                                # #E5B51C
        "trail": (229, 181, 28),                                 # #E5B51C
        "badge": (158, 114, 39),                                 # #9E7227
    },
    "neutral": {
        "dark": (0x3B / 255.0, 0x3E / 255.0, 0x3C / 255.0),     # #3B3E3C
        "mid": (0x8A / 255.0, 0x8D / 255.0, 0x8A / 255.0),      # #8A8D8A
        "snow": (0xF2 / 255.0, 0xF2 / 255.0, 0xEE / 255.0),     # #F2F2EE
        "border": (255, 255, 255),                               # #FFFFFF
        "trail": (220, 222, 218),
        "badge": (92, 95, 92),
    },
}

ROLE_ALIASES: dict[str, str] = {
    "red": "red",
    "danger": "red",
    "axis": "red",
    "enemy": "red",
    "ussr": "red",
    "vietnam": "red",
    "blue": "blue",
    "safe": "blue",
    "allies": "blue",
    "ally": "blue",
    "amber": "amber",
    "warning": "amber",
    "yellow": "amber",
    "gold": "amber",
    "neutral": "neutral",
    "white": "neutral",
    "highlight": "neutral",
}

DEFAULT_COUNTRY_GROUPS: dict[str, list[str]] = {
    "USSR": ["RUS", "UKR", "BLR", "LTU", "LVA", "EST", "MDA", "GEO", "ARM", "AZE", "KAZ", "UZB", "TKM", "KGZ", "TJK"],
    "SOVIET_UNION": ["RUS", "UKR", "BLR", "LTU", "LVA", "EST", "MDA", "GEO", "ARM", "AZE", "KAZ", "UZB", "TKM", "KGZ", "TJK"],
    "INDOCHINA": ["VNM", "LAO", "KHM"],
    "SCANDINAVIA": ["NOR", "SWE", "FIN", "DNK"],
    "UK": ["GBR"],
    "BRITAIN": ["GBR"],
    "GREAT BRITAIN": ["GBR"],
    "UNITED KINGDOM": ["GBR"],
    "USA": ["USA"],
    "UNITED STATES": ["USA"],
    "RUSSIA_WEST": ["RUS"],
    "VIETNAM": ["VNM"],
    "VIỆT NAM": ["VNM"],
    "GERMANY": ["DEU"],
    "ĐỨC": ["DEU"],
    "AUSTRIA": ["AUT"],
    "ÁO": ["AUT"],
    "FRANCE": ["FRA"],
    "PHÁP": ["FRA"],
    "POLAND": ["POL"],
    "BA LAN": ["POL"],
    "UKRAINE": ["UKR"],
    "BELARUS": ["BLR"],
    "CHINA": ["CHN"],
    "TRUNG QUỐC": ["CHN"],
    "JAPAN": ["JPN"],
    "NHẬT BẢN": ["JPN"],
    "INDIA": ["IND"],
    "ẤN ĐỘ": ["IND"],
    "ITALY": ["ITA"],
    "SPAIN": ["ESP"],
    "ROMANIA": ["ROU"],
    "TURKEY": ["TUR"],
}

DEFAULT_REGION_CONFIGS: dict[str, dict[str, Any]] = {
    "europe": {
        "lon_min": -14.0,
        "lon_max": 54.0,
        "lat_min": 34.0,
        "lat_max": 70.5,
        "zoom_tile": 6,
        "width": 5760,
        "height": 3240,
        "force_vn_islands": False,
    },
    "chernobyl_europe": {
        "lon_min": -14.0,
        "lon_max": 54.0,
        "lat_min": 34.0,
        "lat_max": 70.5,
        "zoom_tile": 6,
        "width": 5760,
        "height": 3240,
        "force_vn_islands": False,
    },
    "east_asia_vietnam": {
        "lon_min": 90.0,
        "lon_max": 142.0,
        "lat_min": 3.5,
        "lat_max": 42.0,
        "zoom_tile": 6,
        "width": 5760,
        "height": 3240,
        "force_vn_islands": True,
    },
    "world": {
        "lon_min": -130.0,
        "lon_max": 155.0,
        "lat_min": -38.0,
        "lat_max": 68.0,
        "zoom_tile": 4,
        "width": 5760,
        "height": 3240,
        "force_vn_islands": True,
    },
}

HOANG_SA_DOTS: tuple[tuple[float, float], ...] = (
    (111.20, 15.78),
    (111.58, 16.68),
    (111.60, 16.53),
    (112.03, 16.83),
    (112.33, 16.83),
    (112.73, 16.66),
    (112.28, 16.12),
)

TRUONG_SA_DOTS: tuple[tuple[float, float], ...] = (
    (111.92, 8.65),
    (112.92, 8.85),
    (114.03, 10.02),
    (114.37, 9.69),
    (114.47, 10.37),
    (115.37, 10.24),
    (115.83, 10.72),
    (113.85, 7.90),
)


@lru_cache(maxsize=1)
def get_sovereignty_bbox() -> dict[str, Any]:
    """Return exact lon/lat bounds & archipelago anchors for `HOÀNG SA` & `TRƯỜNG SA`."""
    all_lons: list[float] = [pt[0] for pt in HOANG_SA_DOTS + TRUONG_SA_DOTS] + [112.9, 116.1]
    all_lats: list[float] = [pt[1] for pt in HOANG_SA_DOTS + TRUONG_SA_DOTS] + [16.3, 9.7]
    arch_bounds: dict[str, tuple[float, float, float, float]] = {}

    vn_override_path = GEOJSON_DIR / "vietnam_sovereignty_override.geojson"
    if vn_override_path.is_file():
        try:
            ov_raw = json.loads(vn_override_path.read_text(encoding="utf-8"))
            for feat in ov_raw.get("features") or []:
                props = feat.get("properties") or {}
                arch = str(props.get("ARCHIPELAGO") or "").upper()
                geom_raw = feat.get("geometry")
                if geom_raw:
                    g = shape(geom_raw)
                    if not g.is_empty:
                        minx, miny, maxx, maxy = g.bounds
                        all_lons.extend([float(minx), float(maxx)])
                        all_lats.extend([float(miny), float(maxy)])
                        if arch:
                            arch_bounds[arch] = (float(minx), float(miny), float(maxx), float(maxy))
        except Exception:
            pass

    return {
        "lon_min": min(all_lons),
        "lat_min": min(all_lats),
        "lon_max": max(all_lons),
        "lat_max": max(all_lats),
        "hoang_sa_bbox": arch_bounds.get("HOANG_SA", (111.19, 15.77, 112.74, 16.85)),
        "truong_sa_bbox": arch_bounds.get("TRUONG_SA", (111.90, 7.88, 116.10, 10.75)),
        "anchors": [
            (111.20, 16.83),
            (112.95, 16.30),
            (111.92, 7.90),
            (116.10, 10.72),
            (116.10, 9.70),
        ],
    }


def portrait_safe_center_bias(
    cam_cx: float,
    cam_cy: float,
    cam_zoom: float,
    screen_w: int = 1080,
    screen_h: int = 1920,
    safe_right_rail_px: int = 168,
    safe_left_px: int = 48,
    canvas_aspect: float = 16.0 / 9.0,
) -> tuple[float, float]:
    """Shift `(cam_cx, cam_cy)` rightward slightly so focal content sits inside `x in [48..912]`."""
    aspect_screen = screen_w / max(1.0, float(screen_h))
    if aspect_screen >= 1.0:
        return float(cam_cx), float(cam_cy)
    half_h = 0.5 / max(1.0, float(cam_zoom))
    half_w = half_h * (aspect_screen / canvas_aspect)
    # Visual safe-zone center in [0..1] screen fraction is slightly left of 0.50 due to right action rail
    usable_cx_frac = 0.5 * (safe_left_px + (screen_w - safe_right_rail_px)) / max(1.0, float(screen_w))
    bias_dx = (0.5 - usable_cx_frac) * (2.0 * half_w)
    return float(cam_cx) + bias_dx, float(cam_cy)


# ---------------------------------------------------------------------------
# Web Mercator (EPSG:3857) Coordinate Helpers
# ---------------------------------------------------------------------------
def lonlat_to_merc_unit(lon: float, lat: float) -> tuple[float, float]:
    """Convert (lon, lat) in degrees to Web Mercator unit square [0..1, 0..1] (N=0, S=1)."""
    lat_c = max(-MAX_MERC_LAT, min(MAX_MERC_LAT, float(lat)))
    mx = (float(lon) + 180.0) / 360.0
    lat_rad = math.radians(lat_c)
    my = (1.0 - math.log(math.tan(math.pi / 4.0 + lat_rad / 2.0)) / math.pi) / 2.0
    return mx, my


def merc_unit_to_lonlat(mx: float, my: float) -> tuple[float, float]:
    """Inverse of `lonlat_to_merc_unit`: Web Mercator unit [0..1] -> (lon, lat)."""
    lon = float(mx) * 360.0 - 180.0
    n = math.pi * (1.0 - 2.0 * float(my))
    lat = math.degrees(math.atan(math.sinh(n)))
    return lon, lat


def _lonlat_array_to_merc_unit(coords: np.ndarray) -> np.ndarray:
    """Vectorized (N, 2) lon/lat -> Web Mercator unit [0..1, 0..1]."""
    lon = coords[:, 0]
    lat = np.clip(coords[:, 1], -MAX_MERC_LAT, MAX_MERC_LAT)
    mx = (lon + 180.0) / 360.0
    lat_rad = np.radians(lat)
    my = (1.0 - np.log(np.tan(np.pi / 4.0 + lat_rad / 2.0)) / np.pi) / 2.0
    return np.column_stack((mx, my))


def compute_isotropic_merc_bounds(
    lon_min: float,
    lon_max: float,
    lat_min: float,
    lat_max: float,
    width: int,
    height: int,
) -> dict[str, float]:
    """Expand shorter Mercator axis symmetrically so canvas aspect matches width/height isotropically."""
    mx0, my1 = lonlat_to_merc_unit(lon_min, lat_min)
    mx1, my0 = lonlat_to_merc_unit(lon_max, lat_max)
    dx = max(1e-6, mx1 - mx0)
    dy = max(1e-6, my1 - my0)
    target_ar = float(width) / max(1.0, float(height))

    if dx / dy < target_ar:
        new_dx = dy * target_ar
        cx = 0.5 * (mx0 + mx1)
        mx0 = cx - 0.5 * new_dx
        mx1 = cx + 0.5 * new_dx
        if mx0 < 0.0:
            mx1 = min(1.0, mx1 - mx0)
            mx0 = 0.0
        if mx1 > 1.0:
            mx0 = max(0.0, mx0 - (mx1 - 1.0))
            mx1 = 1.0
    else:
        new_dy = dx / target_ar
        cy = 0.5 * (my0 + my1)
        my0 = cy - 0.5 * new_dy
        my1 = cy + 0.5 * new_dy
        if my0 < 0.0:
            my1 = min(1.0, my1 - my0)
            my0 = 0.0
        if my1 > 1.0:
            my0 = max(0.0, my0 - (my1 - 1.0))
            my1 = 1.0

    act_lon_min, act_lat_max = merc_unit_to_lonlat(mx0, my0)
    act_lon_max, act_lat_min = merc_unit_to_lonlat(mx1, my1)
    return {
        "mx0": float(mx0),
        "mx1": float(mx1),
        "my0": float(my0),
        "my1": float(my1),
        "lon_min": float(act_lon_min),
        "lon_max": float(act_lon_max),
        "lat_min": float(act_lat_min),
        "lat_max": float(act_lat_max),
    }


def lonlat_to_region_norm(lon: float, lat: float, meta: dict[str, Any]) -> tuple[float, float]:
    """Project (lon, lat) into normalized [0..1, 0..1] coordinates of a baked region."""
    mx, my = lonlat_to_merc_unit(lon, lat)
    b = meta["merc_bounds"] if "merc_bounds" in meta else meta
    nx = (mx - b["mx0"]) / max(1e-9, b["mx1"] - b["mx0"])
    ny = (my - b["my0"]) / max(1e-9, b["my1"] - b["my0"])
    return float(nx), float(ny)


def region_norm_to_screen(
    nx: float,
    ny: float,
    cam_cx: float,
    cam_cy: float,
    cam_zoom: float,
    screen_w: int,
    screen_h: int,
    canvas_aspect: float = 16.0 / 9.0,
) -> tuple[float, float]:
    """Map normalized [0..1] region coordinate through active camera viewport."""
    aspect_screen = screen_w / max(1.0, float(screen_h))
    if aspect_screen >= canvas_aspect:
        half_w = 0.5 / cam_zoom
        half_h = half_w * (canvas_aspect / aspect_screen)
    else:
        half_h = 0.5 / cam_zoom
        half_w = half_h * (aspect_screen / canvas_aspect)

    sx = (nx - (cam_cx - half_w)) / max(1e-6, 2.0 * half_w) * screen_w
    sy = (ny - (cam_cy - half_h)) / max(1e-6, 2.0 * half_h) * screen_h
    return sx, sy


def screen_to_region_norm(
    sx: float,
    sy: float,
    cam_cx: float,
    cam_cy: float,
    cam_zoom: float,
    screen_w: int,
    screen_h: int,
    canvas_aspect: float = 16.0 / 9.0,
) -> tuple[float, float]:
    """Inverse of `region_norm_to_screen`."""
    aspect_screen = screen_w / max(1.0, float(screen_h))
    if aspect_screen >= canvas_aspect:
        half_w = 0.5 / cam_zoom
        half_h = half_w * (canvas_aspect / aspect_screen)
    else:
        half_h = 0.5 / cam_zoom
        half_w = half_h * (aspect_screen / canvas_aspect)
    nx = (cam_cx - half_w) + (sx / max(1.0, float(screen_w))) * (2.0 * half_w)
    ny = (cam_cy - half_h) + (sy / max(1.0, float(screen_h))) * (2.0 * half_h)
    return nx, ny


def clamp_camera_center(
    cam_cx: float,
    cam_cy: float,
    cam_zoom: float,
    screen_w: int = 1920,
    screen_h: int = 1080,
    canvas_aspect: float = 16.0 / 9.0,
) -> tuple[float, float]:
    """Clamp camera center so viewport never crosses [0, 1] canvas bounds."""
    aspect_screen = screen_w / max(1.0, float(screen_h))
    if aspect_screen >= canvas_aspect:
        half_w = 0.5 / max(1.0, cam_zoom)
        half_h = half_w * (canvas_aspect / aspect_screen)
    else:
        half_h = 0.5 / max(1.0, cam_zoom)
        half_w = half_h * (aspect_screen / canvas_aspect)
    half_w = min(0.5, half_w)
    half_h = min(0.5, half_h)
    cx = max(half_w, min(1.0 - half_w, float(cam_cx)))
    cy = max(half_h, min(1.0 - half_h, float(cam_cy)))
    return cx, cy


# ---------------------------------------------------------------------------
# ESRI Tile Downloader & Stitched Mosaic
# ---------------------------------------------------------------------------
def _fetch_single_tile(layer_name: str, url_tmpl: str, z: int, x: int, y: int) -> tuple[int, int, np.ndarray]:
    """Download or load cached XYZ tile as RGB uint8 (256, 256, 3)."""
    n_tiles = 1 << z
    tx = x % n_tiles
    ty = max(0, min(n_tiles - 1, y))
    cache_path = TILES_DIR / layer_name / str(z) / str(tx) / f"{ty}.jpg"
    if cache_path.exists() and cache_path.stat().st_size > 100:
        arr = cv2.imread(str(cache_path), cv2.IMREAD_COLOR)
        if arr is not None and arr.shape[:2] == (256, 256):
            return x, y, cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    url = url_tmpl.format(z=z, x=tx, y=ty)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; VideoPilotGIS/1.0)"}
    last_err: Exception | None = None
    for _attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
            img_arr = np.frombuffer(raw, dtype=np.uint8)
            bgr = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            if bgr is not None and bgr.shape[:2] == (256, 256):
                tmp_path = cache_path.with_suffix(".jpg.tmp")
                tmp_path.write_bytes(raw)
                tmp_path.replace(cache_path)
                return x, y, cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = exc
    # Neutral fallback tile if server temporarily unavailable
    fallback_val = 128 if "hillshade" in layer_name else 40
    if last_err is not None:
        print(f"[gis_map_baker] tile fallback {layer_name} z={z} x={tx} y={ty}: {last_err}")
    return x, y, np.full((256, 256, 3), fallback_val, dtype=np.uint8)


def stitch_esri_tiles(
    layer_name: str,
    url_tmpl: str,
    merc_bounds: dict[str, float],
    zoom_tile: int,
    width: int,
    height: int,
    max_workers: int = 8,
) -> np.ndarray:
    """Fetch, cache, stitch, and subpixel-crop ESRI tiles to exact (height, width, 3)."""
    n_tiles = 1 << zoom_tile
    tx0 = int(math.floor(merc_bounds["mx0"] * n_tiles))
    tx1 = int(math.floor((merc_bounds["mx1"] - 1e-9) * n_tiles))
    ty0 = max(0, int(math.floor(merc_bounds["my0"] * n_tiles)))
    ty1 = min(n_tiles - 1, int(math.floor((merc_bounds["my1"] - 1e-9) * n_tiles)))

    cols = tx1 - tx0 + 1
    rows = ty1 - ty0 + 1
    mosaic = np.zeros((rows * 256, cols * 256, 3), dtype=np.uint8)

    coords = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_fetch_single_tile, layer_name, url_tmpl, zoom_tile, x, y) for x, y in coords]
        for fut in as_completed(futures):
            x, y, tile_rgb = fut.result()
            px = (x - tx0) * 256
            py = (y - ty0) * 256
            mosaic[py : py + 256, px : px + 256] = tile_rgb

    # Exact subpixel affine mapping from mosaic space to (width, height)
    sx0 = (merc_bounds["mx0"] * n_tiles - tx0) * 256.0
    sx1 = (merc_bounds["mx1"] * n_tiles - tx0) * 256.0
    sy0 = (merc_bounds["my0"] * n_tiles - ty0) * 256.0
    sy1 = (merc_bounds["my1"] * n_tiles - ty0) * 256.0

    src_w = max(1e-3, sx1 - sx0)
    src_h = max(1e-3, sy1 - sy0)
    scale_x = width / src_w
    scale_y = height / src_h
    mat = np.array(
        [
            [scale_x, 0.0, -sx0 * scale_x],
            [0.0, scale_y, -sy0 * scale_y],
        ],
        dtype=np.float32,
    )
    interp = cv2.INTER_AREA if scale_x < 1.0 else cv2.INTER_CUBIC
    return cv2.warpAffine(mosaic, mat, (width, height), flags=interp, borderMode=cv2.BORDER_REPLICATE)


# ---------------------------------------------------------------------------
# GeoJSON Loading + Sovereignty Override
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _load_gis_vectors() -> dict[str, Any]:
    """Load Natural Earth 10m land, countries, boundary lines & Vietnam sovereignty override."""
    land_path = GEOJSON_DIR / "ne_10m_land.geojson"
    countries_path = GEOJSON_DIR / "ne_10m_admin_0_countries.geojson"
    borders_path = GEOJSON_DIR / "ne_10m_admin_0_boundary_lines_land.geojson"
    vn_override_path = GEOJSON_DIR / "vietnam_sovereignty_override.geojson"

    for req_p in (land_path, countries_path, borders_path):
        if not req_p.exists():
            raise FileNotFoundError(f"Missing GIS GeoJSON asset: {req_p}")

    with land_path.open("r", encoding="utf-8") as f:
        land_raw = json.load(f)
    land_geoms = [shape(feat["geometry"]) for feat in land_raw.get("features", []) if feat.get("geometry")]

    override_features: list[dict[str, Any]] = []
    subtract_boxes: list[Any] = []
    remove_adm0: set[str] = set()
    if vn_override_path.exists():
        with vn_override_path.open("r", encoding="utf-8") as f:
            ov_raw = json.load(f)
        for feat in ov_raw.get("features", []):
            props = feat.get("properties") or {}
            if feat.get("geometry"):
                geom = shape(feat["geometry"])
                override_features.append({"props": props, "geom": geom})
                land_geoms.append(geom)
            if props.get("SUBTRACT_BBOX"):
                b = props["SUBTRACT_BBOX"]
                subtract_boxes.append(box(b[0], b[1], b[2], b[3]))
            for rm in props.get("REMOVE_ADM0_A3") or []:
                remove_adm0.add(str(rm).upper())

    with countries_path.open("r", encoding="utf-8") as f:
        c_raw = json.load(f)

    country_entries: list[dict[str, Any]] = []
    vnm_extra_geoms = [item["geom"] for item in override_features if str(item["props"].get("ISO_A3", "")).upper() == "VNM"]

    for feat in c_raw.get("features", []):
        if not feat.get("geometry"):
            continue
        p = feat.get("properties") or {}
        iso_a3 = str(p.get("ISO_A3") or "").upper()
        adm0_a3 = str(p.get("ADM0_A3") or "").upper()
        sov_a3 = str(p.get("SOV_A3") or "").upper()
        admin = str(p.get("ADMIN") or p.get("NAME") or "").strip()
        if iso_a3 in ("-99", "", "NONE"):
            iso_a3 = adm0_a3 if adm0_a3 not in ("-99", "", "NONE") else admin.upper()
        if adm0_a3 in remove_adm0 or iso_a3 in remove_adm0:
            continue

        geom = shape(feat["geometry"])
        if not geom.is_valid:
            geom = geom.buffer(0)

        # Strip Hoang Sa / Truong Sa polygons from any non-Vietnam country
        if iso_a3 != "VNM" and subtract_boxes:
            for sb in subtract_boxes:
                if geom.intersects(sb):
                    geom = geom.difference(sb)

        if iso_a3 == "VNM" and vnm_extra_geoms:
            geom = unary_union([geom] + vnm_extra_geoms)

        if geom.is_empty:
            continue

        country_entries.append(
            {
                "iso_a3": iso_a3,
                "adm0_a3": adm0_a3,
                "sov_a3": sov_a3,
                "admin": admin,
                "name": str(p.get("NAME") or admin),
                "geom": geom,
            }
        )

    with borders_path.open("r", encoding="utf-8") as f:
        b_raw = json.load(f)
    border_geoms = [shape(feat["geometry"]) for feat in b_raw.get("features", []) if feat.get("geometry")]

    return {
        "land_geoms": land_geoms,
        "countries": country_entries,
        "border_geoms": border_geoms,
    }


def _geom_to_polygons(geom: Any) -> list[Polygon]:
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, (MultiPolygon, GeometryCollection)):
        out: list[Polygon] = []
        for g in geom.geoms:
            out.extend(_geom_to_polygons(g))
        return out
    return []


def _geom_to_lines(geom: Any) -> list[LineString]:
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [geom]
    if isinstance(geom, (MultiLineString, GeometryCollection)):
        out: list[LineString] = []
        for g in geom.geoms:
            out.extend(_geom_to_lines(g))
        return out
    return []


def _project_geom_to_norm(geom: Any, merc_bounds: dict[str, float]) -> Any:
    """Transform Shapely geometry from EPSG:4326 lon/lat directly to region [0..1, 0..1]."""
    mx0, mx1 = merc_bounds["mx0"], merc_bounds["mx1"]
    my0, my1 = merc_bounds["my0"], merc_bounds["my1"]
    dx = max(1e-9, mx1 - mx0)
    dy = max(1e-9, my1 - my0)

    def _fn(coords: np.ndarray) -> np.ndarray:
        merc = _lonlat_array_to_merc_unit(coords)
        merc[:, 0] = (merc[:, 0] - mx0) / dx
        merc[:, 1] = (merc[:, 1] - my0) / dy
        return merc

    return shapely_transform(geom, _fn)


def _rasterize_geom_list(
    norm_geoms: list[Any],
    width: int,
    height: int,
    dtype: Any,
    fill_values: list[int],
    line_aa: bool = False,
) -> np.ndarray:
    """Rasterize normalized [0..1, 0..1] Shapely geometries onto (height, width) canvas."""
    canvas = np.zeros((height, width), dtype=dtype)
    lt = cv2.LINE_AA if line_aa else cv2.LINE_8
    for geom, val in zip(norm_geoms, fill_values, strict=False):
        for poly in _geom_to_polygons(geom):
            ext = np.asarray(poly.exterior.coords, dtype=np.float64)
            ext[:, 0] *= width
            ext[:, 1] *= height
            rings = [np.round(ext).astype(np.int32)]
            for hole in poly.interiors:
                h_arr = np.asarray(hole.coords, dtype=np.float64)
                h_arr[:, 0] *= width
                h_arr[:, 1] *= height
                rings.append(np.round(h_arr).astype(np.int32))
            cv2.fillPoly(canvas, rings, int(val), lineType=lt)
    return canvas


def _extract_polylines_norm(geom: Any, min_pts: int = 2) -> list[list[list[float]]]:
    out: list[list[list[float]]] = []
    for line in _geom_to_lines(geom):
        coords = np.asarray(line.coords, dtype=np.float32)
        if len(coords) >= min_pts:
            out.append([[round(float(x), 5), round(float(y), 5)] for x, y in coords])
    return out


def _extract_polygon_rings_norm(geom: Any) -> list[list[list[float]]]:
    out: list[list[list[float]]] = []
    for poly in _geom_to_polygons(geom):
        ext = np.asarray(poly.exterior.coords, dtype=np.float32)
        if len(ext) >= 3:
            out.append([[round(float(x), 5), round(float(y), 5)] for x, y in ext])
    return out


# ---------------------------------------------------------------------------
# Pre-Bake Pipeline -> .npz
# ---------------------------------------------------------------------------
def bake_region(
    region_key: str,
    lon_min: float | None = None,
    lon_max: float | None = None,
    lat_min: float | None = None,
    lat_max: float | None = None,
    zoom_tile: int | None = None,
    width: int | None = None,
    height: int | None = None,
    force_vn_islands: bool | None = None,
    force_rebuild: bool = False,
    prebaked_dir: Path | None = None,
) -> Path:
    """Pre-bake a Web Mercator region plate (.npz) from ESRI Dual-Tiles + Natural Earth 10m."""
    cfg = dict(DEFAULT_REGION_CONFIGS.get(region_key, {}))
    lon0 = float(lon_min if lon_min is not None else cfg.get("lon_min", -14.0))
    lon1 = float(lon_max if lon_max is not None else cfg.get("lon_max", 54.0))
    lat0 = float(lat_min if lat_min is not None else cfg.get("lat_min", 34.0))
    lat1 = float(lat_max if lat_max is not None else cfg.get("lat_max", 70.5))
    z_tile = int(zoom_tile if zoom_tile is not None else cfg.get("zoom_tile", 6))
    w = int(width if width is not None else cfg.get("width", 5760))
    h = int(height if height is not None else cfg.get("height", 3240))
    if force_vn_islands is None:
        force_vn_islands = bool(cfg.get("force_vn_islands", False))

    out_dir = Path(prebaked_dir) if prebaked_dir is not None else PREBAKED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{region_key}.npz"
    if out_path.exists() and not force_rebuild:
        return out_path

    merc_bounds = compute_isotropic_merc_bounds(lon0, lon1, lat0, lat1, w, h)
    clip_lonlat = box(
        max(-179.99, merc_bounds["lon_min"] - 1.5),
        max(-85.0, merc_bounds["lat_min"] - 1.5),
        min(179.99, merc_bounds["lon_max"] + 1.5),
        min(85.0, merc_bounds["lat_max"] + 1.5),
    )

    print(
        f"[gis_map_baker] Baking {region_key} ({w}x{h}, z={z_tile}, "
        f"lon={merc_bounds['lon_min']:.2f}..{merc_bounds['lon_max']:.2f}, "
        f"lat={merc_bounds['lat_min']:.2f}..{merc_bounds['lat_max']:.2f})..."
    )

    # 1. Fetch & stitch Dual-Tiles (Imagery + Hillshade)
    imagery_rgb = stitch_esri_tiles("esri_world_imagery", ESRI_IMAGERY_URL, merc_bounds, z_tile, w, h)
    hillshade_rgb = stitch_esri_tiles("esri_world_hillshade", ESRI_HILLSHADE_URL, merc_bounds, z_tile, w, h)

    # 2. Project & rasterize Natural Earth 10m Land Mask (2x supersampled for razor AA)
    vectors = _load_gis_vectors()
    simplify_tol = 0.25 / max(1.0, float(w))

    land_norm_geoms: list[Any] = []
    for lg in vectors["land_geoms"]:
        if not lg.intersects(clip_lonlat):
            continue
        clipped = lg.intersection(clip_lonlat)
        if clipped.is_empty:
            continue
        ng = _project_geom_to_norm(clipped, merc_bounds).simplify(simplify_tol, preserve_topology=True)
        if not ng.is_empty:
            land_norm_geoms.append(ng)

    land_mask = _rasterize_geom_list(
        land_norm_geoms,
        w,
        h,
        dtype=np.uint8,
        fill_values=[255] * len(land_norm_geoms),
        line_aa=True,
    )

    # 3. Project & rasterize all countries in viewport into int16 ID map + border rings
    country_norm_geoms: list[Any] = []
    country_ids: list[int] = []
    country_records: list[dict[str, Any]] = []
    country_borders: dict[str, list[list[list[float]]]] = {}

    next_id = 1
    border_tol = 0.35 / max(1.0, float(w))
    norm_clip_box = box(-0.02, -0.02, 1.02, 1.02)
    for centry in vectors["countries"]:
        geom = centry["geom"]
        if not geom.intersects(clip_lonlat):
            continue
        clipped = geom.intersection(clip_lonlat)
        if clipped.is_empty:
            continue
        ng = _project_geom_to_norm(clipped, merc_bounds)
        ng_simp = ng.simplify(border_tol, preserve_topology=True).intersection(norm_clip_box)
        if ng_simp.is_empty:
            continue

        cid = next_id
        next_id += 1
        country_norm_geoms.append(ng_simp)
        country_ids.append(cid)
        country_records.append(
            {
                "id": cid,
                "iso_a3": centry["iso_a3"],
                "adm0_a3": centry["adm0_a3"],
                "sov_a3": centry["sov_a3"],
                "admin": centry["admin"],
                "name": centry["name"],
            }
        )
        rings = _extract_polygon_rings_norm(ng_simp)
        if rings:
            key = centry["iso_a3"]
            country_borders.setdefault(key, []).extend(rings)

    country_id_i32 = _rasterize_geom_list(
        country_norm_geoms,
        w,
        h,
        dtype=np.int32,
        fill_values=country_ids,
        line_aa=False,
    )
    country_id_map = country_id_i32.astype(np.int16)

    # Ensure every pixel inside a country is also inside land_mask (catches tiny sovereign islands)
    land_mask = np.maximum(land_mask, np.where(country_id_map > 0, np.uint8(255), np.uint8(0)))

    # 4. Clip & normalize land boundary lines (for crisp neutral 1px country borders)
    border_lines: list[list[list[float]]] = []
    for bg in vectors["border_geoms"]:
        if not bg.intersects(clip_lonlat):
            continue
        clipped = bg.intersection(clip_lonlat)
        if clipped.is_empty:
            continue
        ng = _project_geom_to_norm(clipped, merc_bounds).simplify(border_tol, preserve_topology=True)
        ng = ng.intersection(norm_clip_box)
        if not ng.is_empty:
            border_lines.extend(_extract_polylines_norm(ng))

    # 5. Step A: Normalized Terrain Luminance L_base (uint8, snow peaks 0.78..0.98)
    img_f = imagery_rgb.astype(np.float32) / 255.0
    hill_f = cv2.cvtColor(hillshade_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

    y_sat = 0.2126 * img_f[..., 0] + 0.7152 * img_f[..., 1] + 0.0722 * img_f[..., 2]
    y_mix = np.clip(0.78 * y_sat + 0.22 * (2.0 * hill_f - 1.0) * 0.45 + 0.05, 0.0, 1.0)

    land_bool = land_mask > 128
    if np.any(land_bool):
        land_vals = y_mix[land_bool]
        p2 = float(np.percentile(land_vals, 2.0))
        p99 = float(np.percentile(land_vals, 99.0))
    else:
        p2, p99 = 0.05, 0.90

    l0 = np.clip((y_mix - p2) / max(1e-4, p99 - p2), 0.0, 1.0)
    l_base_f = np.power(l0, 0.90) * (land_mask.astype(np.float32) / 255.0)
    l_base_u8 = np.clip(np.round(l_base_f * 255.0), 0, 255).astype(np.uint8)

    # Check if Vietnam islands fall inside region bounds
    has_vn_islands = bool(
        force_vn_islands
        or (
            merc_bounds["lon_min"] <= 115.5
            and merc_bounds["lon_max"] >= 111.0
            and merc_bounds["lat_min"] <= 17.5
            and merc_bounds["lat_max"] >= 7.5
        )
    )

    meta = {
        "region_key": region_key,
        "width": w,
        "height": h,
        "zoom_tile": z_tile,
        "merc_bounds": merc_bounds,
        "has_vn_islands": has_vn_islands,
    }
    if has_vn_islands:
        meta["sovereignty_bbox"] = get_sovereignty_bbox()

    np.savez_compressed(
        out_path,
        l_base=l_base_u8,
        land_mask=land_mask,
        country_id_map=country_id_map,
        country_records_json=np.array(json.dumps(country_records, ensure_ascii=False)),
        border_lines_json=np.array(json.dumps(border_lines)),
        country_borders_json=np.array(json.dumps(country_borders)),
        meta_json=np.array(json.dumps(meta, ensure_ascii=False)),
    )
    print(f"[gis_map_baker] Saved {out_path} ({out_path.stat().st_size / (1024 * 1024):.2f} MB, {len(country_records)} countries)")
    return out_path


def bake_all_default_regions(force_rebuild: bool = False) -> dict[str, Path]:
    """Pre-bake the 4 canonical regions (`europe`, `chernobyl_europe`, `east_asia_vietnam`, `world`)."""
    results: dict[str, Path] = {}
    for key in DEFAULT_REGION_CONFIGS:
        results[key] = bake_region(key, force_rebuild=force_rebuild)
    return results


_REGION_CACHE: dict[str, dict[str, Any]] = {}


def load_prebaked_region(
    region_key: str,
    prebaked_dir: Path | None = None,
    auto_bake: bool = True,
) -> dict[str, Any]:
    """Load pre-baked `.npz` region into memory with parsed JSON metadata."""
    base_dir = Path(prebaked_dir) if prebaked_dir is not None else PREBAKED_DIR
    cache_key = f"{base_dir}:{region_key}"
    if cache_key in _REGION_CACHE:
        return _REGION_CACHE[cache_key]

    npz_path = base_dir / f"{region_key}.npz"
    if not npz_path.exists():
        if auto_bake and region_key in DEFAULT_REGION_CONFIGS:
            bake_region(region_key, prebaked_dir=base_dir)
        else:
            raise FileNotFoundError(f"Pre-baked region not found: {npz_path}")

    with np.load(npz_path, allow_pickle=False) as z:
        data = {
            "l_base": z["l_base"],
            "land_mask": z["land_mask"],
            "country_id_map": z["country_id_map"],
            "country_records": json.loads(str(z["country_records_json"])),
            "border_lines": json.loads(str(z["border_lines_json"])),
            "country_borders": json.loads(str(z["country_borders_json"])),
            "meta": json.loads(str(z["meta_json"])),
            "path": str(npz_path),
        }
    _REGION_CACHE[cache_key] = data
    return data


# ---------------------------------------------------------------------------
# Country / Historical Group Resolution & Colorization
# ---------------------------------------------------------------------------
def _normalize_role(role: str) -> str:
    return ROLE_ALIASES.get(str(role).strip().lower(), "red")


def resolve_country_isos(
    key: str,
    country_records: list[dict[str, Any]],
    country_groups: dict[str, list[str]] | None = None,
) -> list[str]:
    """Resolve country name / ISO code / historical bloc (e.g. `USSR`) to matching ISO_A3 codes."""
    norm = str(key).strip().upper()
    groups = dict(DEFAULT_COUNTRY_GROUPS)
    if country_groups:
        for gk, gv in country_groups.items():
            groups[str(gk).strip().upper()] = [str(x).strip().upper() for x in gv]

    if norm in groups:
        targets = groups[norm]
    else:
        targets = [norm]

    matched_isos: list[str] = []
    for rec in country_records:
        iso = str(rec["iso_a3"]).upper()
        adm0 = str(rec["adm0_a3"]).upper()
        admin = str(rec["admin"]).upper()
        name = str(rec["name"]).upper()
        for t in targets:
            if t in (iso, adm0, admin, name):
                matched_isos.append(iso)
                break
    return list(dict.fromkeys(matched_isos))


def get_territory_mask(
    npz_data: dict[str, Any],
    country_or_group: str | list[str],
    country_groups: dict[str, list[str]] | None = None,
    feather_px: float = 1.2,
) -> tuple[np.ndarray, list[str]]:
    """Return float32 [0..1] land-clipped mask and matched ISO_A3 codes for a country or bloc."""
    records = npz_data["country_records"]
    id_map = npz_data["country_id_map"]
    keys = [country_or_group] if isinstance(country_or_group, str) else list(country_or_group)

    matched_isos: list[str] = []
    for k in keys:
        matched_isos.extend(resolve_country_isos(k, records, country_groups=country_groups))
    matched_isos = list(dict.fromkeys(matched_isos))

    target_ids = [rec["id"] for rec in records if str(rec["iso_a3"]).upper() in matched_isos]
    if not target_ids:
        return np.zeros(id_map.shape, dtype=np.float32), []

    raw_mask = np.isin(id_map, target_ids).astype(np.float32)
    if feather_px > 0.1:
        raw_mask = cv2.GaussianBlur(raw_mask, (0, 0), sigmaX=feather_px)
    return raw_mask, matched_isos


def colorize_relief_plate(
    npz_data: dict[str, Any],
    territories_dict: dict[str, str] | None = None,
    country_groups: dict[str, list[str]] | None = None,
    alpha: float = 0.92,
    include_vignette: bool = False,
) -> np.ndarray:
    """Fast NumPy/OpenCV 3-stop luminance-preserving colorize + ocean shelf shadow.

    Preserves snow peaks (e.g. Alps/Caucasus/Himalayas) as bright tinted highlights
    (`#E49696` on red, `#8CC2EB` on blue) and micro-detail via 5x5 high-pass injection.
    Returns RGB uint8 array of shape `(H, W, 3)`.
    """
    l_base = npz_data["l_base"].astype(np.float32) / 255.0
    land_mask = npz_data["land_mask"].astype(np.float32) / 255.0
    h, w = l_base.shape

    # Coastal shelf shadow around coastline
    shelf_sigma = max(4.0, w / 480.0)
    shelf_blur = cv2.GaussianBlur(land_mask, (0, 0), sigmaX=shelf_sigma)
    m_shelf = np.clip(shelf_blur - land_mask, 0.0, 1.0)

    ocean_rgb = np.array(OCEAN_RGB, dtype=np.float32) / 255.0
    ocean_plate = ocean_rgb[None, None, :] + 0.045 * m_shelf[..., None]
    land_neutral = (0.08 + 0.74 * l_base)[..., None]

    out = land_neutral * land_mask[..., None] + ocean_plate * (1.0 - land_mask[..., None])

    # High-pass micro-texture detail injection
    l_blur = cv2.blur(l_base, (5, 5))
    l_hi = ((l_base - l_blur) * 0.45)[..., None]

    t1 = np.clip((l_base - 0.14) / 0.36, 0.0, 1.0)[..., None]
    t2 = np.clip((l_base - 0.50) / 0.32, 0.0, 1.0)[..., None]

    for key, role_raw in (territories_dict or {}).items():
        role = _normalize_role(role_raw)
        ramp_cfg = TERRITORY_RAMPS[role]
        mask, _ = get_territory_mask(npz_data, key, country_groups=country_groups)
        if not np.any(mask > 0.01):
            continue

        c_d = np.array(ramp_cfg["dark"], dtype=np.float32)[None, None, :]
        c_m = np.array(ramp_cfg["mid"], dtype=np.float32)[None, None, :]
        c_s = np.array(ramp_cfg["snow"], dtype=np.float32)[None, None, :]

        ramp = (1.0 - t2) * ((1.0 - t1) * c_d + t1 * c_m) + t2 * c_s
        terr_rgb = np.clip(ramp + l_hi, 0.0, 1.0)
        eff_a = np.clip(mask * land_mask * float(alpha), 0.0, 0.96)[..., None]
        out = out * (1.0 - eff_a) + terr_rgb * eff_a

    if include_vignette:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r2 = ((xx / w - 0.5) * 2.0) ** 2 + ((yy / h - 0.5) * 2.0) ** 2
        vig = np.clip(1.0 - 0.18 * r2, 0.68, 1.0)[..., None]
        out = out * vig

    return np.clip(np.round(out * 255.0), 0, 255).astype(np.uint8)


def blend_map_gpu(
    l_base: Any,
    land_mask: Any,
    active_masks: list[tuple[Any, str, float]],
) -> Any:
    """PyTorch CUDA shader: 3-stop luminance-preserving territory colorize on GPU."""
    import torch
    import torch.nn.functional as F

    ocean_rgb = torch.tensor(
        [OCEAN_RGB[0] / 255.0, OCEAN_RGB[1] / 255.0, OCEAN_RGB[2] / 255.0],
        device=l_base.device,
        dtype=l_base.dtype,
    ).view(1, 3, 1, 1)
    land_l = 0.08 + 0.74 * l_base
    out = ocean_rgb * (1.0 - land_mask) + land_l.expand(-1, 3, -1, -1) * land_mask

    l_blur = F.avg_pool2d(l_base, kernel_size=5, stride=1, padding=2)
    l_hi = (l_base - l_blur) * 0.45

    t1 = torch.clamp((l_base - 0.14) / 0.36, 0.0, 1.0)
    t2 = torch.clamp((l_base - 0.50) / 0.32, 0.0, 1.0)

    for mask, role_raw, fade_a in active_masks:
        role = _normalize_role(role_raw)
        rc = TERRITORY_RAMPS[role]
        c_d = torch.tensor(rc["dark"], device=l_base.device, dtype=l_base.dtype).view(1, 3, 1, 1)
        c_m = torch.tensor(rc["mid"], device=l_base.device, dtype=l_base.dtype).view(1, 3, 1, 1)
        c_s = torch.tensor(rc["snow"], device=l_base.device, dtype=l_base.dtype).view(1, 3, 1, 1)

        ramp = (1.0 - t2) * ((1.0 - t1) * c_d + t1 * c_m) + t2 * c_s
        terr_rgb = torch.clamp(ramp + l_hi, 0.0, 1.0)
        eff_a = torch.clamp(mask * land_mask * float(fade_a), 0.0, 0.96)
        out = out * (1.0 - eff_a) + terr_rgb * eff_a

    return out


# ---------------------------------------------------------------------------
# Vector Graphics Primitives (Arc-Length Trails, SVG Pin Badges, Bullseye)
# ---------------------------------------------------------------------------
def sample_bezier_arclength(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    step_px: float = 20.0,
    progress: float = 1.0,
) -> tuple[list[tuple[float, float]], tuple[float, float], float]:
    """Sample evenly spaced arc-length dots along quadratic Bezier up to `progress` in [0..1].

    Returns `(dots, tip_xy, tangent_angle_rad)`.
    """
    n_dense = 256
    pts: list[tuple[float, float]] = []
    cum: list[float] = [0.0]
    for i in range(n_dense + 1):
        u = i / n_dense
        iu = 1.0 - u
        x = iu * iu * p0[0] + 2.0 * iu * u * p1[0] + u * u * p2[0]
        y = iu * iu * p0[1] + 2.0 * iu * u * p1[1] + u * u * p2[1]
        pts.append((x, y))
        if i > 0:
            cum.append(cum[-1] + math.hypot(x - pts[-2][0], y - pts[-2][1]))

    prog = max(0.0, min(1.0, float(progress)))
    total_len = cum[-1] * prog
    dots: list[tuple[float, float]] = []
    d_target = 0.0
    idx = 0
    step = max(4.0, float(step_px))
    while d_target <= total_len and idx < n_dense:
        while idx < n_dense and cum[idx + 1] < d_target:
            idx += 1
        seg_len = max(1e-6, cum[idx + 1] - cum[idx])
        frac = max(0.0, min(1.0, (d_target - cum[idx]) / seg_len))
        x = pts[idx][0] + frac * (pts[idx + 1][0] - pts[idx][0])
        y = pts[idx][1] + frac * (pts[idx + 1][1] - pts[idx][1])
        dots.append((x, y))
        d_target += step

    # Exact leading tip at `total_len`
    tip_idx = 0
    while tip_idx < n_dense - 1 and cum[tip_idx + 1] < total_len:
        tip_idx += 1
    seg_len = max(1e-6, cum[tip_idx + 1] - cum[tip_idx])
    frac = max(0.0, min(1.0, (total_len - cum[tip_idx]) / seg_len))
    tip_x = pts[tip_idx][0] + frac * (pts[tip_idx + 1][0] - pts[tip_idx][0])
    tip_y = pts[tip_idx][1] + frac * (pts[tip_idx + 1][1] - pts[tip_idx][1])
    ang = math.atan2(pts[tip_idx + 1][1] - pts[tip_idx][1], pts[tip_idx + 1][0] - pts[tip_idx][0])
    return dots, (tip_x, tip_y), ang


@lru_cache(maxsize=128)
def render_svg_icon_rgba(icon_name: str, size_px: int) -> Image.Image:
    """Render a white SVG vector icon from `sys/assets/map_icons/` using `resvg_py`."""
    name = str(icon_name).strip().lower()
    if name.endswith(".svg"):
        name = name[:-4]
    svg_path = MAP_ICONS_DIR / f"{name}.svg"
    if not svg_path.exists():
        svg_path = MAP_ICONS_DIR / "warning.svg"
    png_bytes = resvg_py.svg_to_bytes(svg_path=str(svg_path), width=int(size_px), height=int(size_px))
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


@lru_cache(maxsize=32)
def _get_label_font(size_px: int) -> ImageFont.FreeTypeFont:
    candidates = [
        ASSETS_DIR / "fonts" / "chanh_niem_ke" / "Oswald-Bold.ttf",
        ASSETS_DIR / "fonts" / "chanh_niem_ke" / "BarlowCondensed-ExtraBold.ttf",
        ASSETS_DIR / "fonts" / "chanh_niem_ke" / "RobotoCondensed-Bold.ttf",
        Path("/usr/share/fonts/truetype/roboto/unhinted/RobotoCondensed-Bold.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size=max(10, int(size_px)))
    return ImageFont.load_default()


def _draw_aa_polyline_cv2(
    bgr_or_bgra: np.ndarray,
    pts_px: np.ndarray,
    color: tuple[int, ...],
    thickness: int,
    closed: bool = False,
) -> None:
    if len(pts_px) < 2:
        return
    shift = 3
    scale = 1 << shift
    pts_sub = np.round(pts_px * scale).astype(np.int32).reshape((-1, 1, 2))
    cv2.polylines(bgr_or_bgra, [pts_sub], isClosed=closed, color=color, thickness=max(1, int(thickness)), lineType=cv2.LINE_AA, shift=shift)


def _draw_pin_badge(
    overlay: Image.Image,
    tip_x: float,
    tip_y: float,
    icon_name: str,
    role: str = "red",
    scale: float = 1.0,
) -> None:
    """Draw 44x44px rounded square Map Pin Badge with white border, bottom caret, and SVG icon."""
    rc = TERRITORY_RAMPS[_normalize_role(role)]
    fill_rgb = rc["badge"]

    box_sz = int(round(44.0 * scale))
    radius = max(3, int(round(7.0 * scale)))
    caret_h = max(4, int(round(9.0 * scale)))
    caret_half_w = max(4, int(round(7.0 * scale)))
    brd_w = max(2, int(round(2.2 * scale)))

    pad = brd_w + 10
    patch_w = box_sz + pad * 2
    patch_h = box_sz + caret_h + pad * 2

    # Build silhouette at 2x supersampling for ultra-crisp anti-aliased edges + caret
    ss = 2
    pw, ph = patch_w * ss, patch_h * ss
    bx0, by0 = pad * ss, pad * ss
    bx1, by1 = bx0 + box_sz * ss, by0 + box_sz * ss
    cx_s = (bx0 + bx1) // 2
    tip_s = by1 + caret_h * ss

    # Outer white border shape (expanded by brd_w)
    bw = brd_w * ss
    mask_white = Image.new("L", (pw, ph), 0)
    mw = ImageDraw.Draw(mask_white)
    mw.rounded_rectangle([bx0 - bw, by0 - bw, bx1 + bw, by1 + bw], radius=radius * ss + bw, fill=255)
    mw.polygon(
        [(cx_s - caret_half_w * ss - bw, by1), (cx_s + caret_half_w * ss + bw, by1), (cx_s, tip_s + bw + 1)],
        fill=255,
    )

    # Inner colored fill shape
    mask_fill = Image.new("L", (pw, ph), 0)
    mf = ImageDraw.Draw(mask_fill)
    mf.rounded_rectangle([bx0, by0, bx1, by1], radius=radius * ss, fill=255)
    mf.polygon(
        [(cx_s - caret_half_w * ss, by1 - 2), (cx_s + caret_half_w * ss, by1 - 2), (cx_s, tip_s)],
        fill=255,
    )

    # Drop shadow from white silhouette
    shadow_l = mask_white.filter(ImageFilter.GaussianBlur(radius=4 * ss))
    badge_ss = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sh_rgba = Image.new("RGBA", (pw, ph), (0, 0, 0, 120))
    badge_ss.paste(sh_rgba, (0, 3 * ss), shadow_l)
    badge_ss.paste(Image.new("RGBA", (pw, ph), (255, 255, 255, 255)), (0, 0), mask_white)
    badge_ss.paste(Image.new("RGBA", (pw, ph), (*fill_rgb, 255)), (0, 0), mask_fill)

    badge = badge_ss.resize((patch_w, patch_h), Image.Resampling.LANCZOS)

    # Composite pure-white SVG icon centered inside the 44x44 square
    ico_sz = max(14, int(round(box_sz * 0.72)))
    ico = render_svg_icon_rgba(icon_name, ico_sz)
    ix = pad + (box_sz - ico_sz) // 2
    iy = pad + (box_sz - ico_sz) // 2
    badge.alpha_composite(ico, (ix, iy))

    paste_x = int(round(tip_x - patch_w / 2.0))
    paste_y = int(round(tip_y - (pad + box_sz + caret_h)))
    overlay.alpha_composite(badge, (paste_x, paste_y))


def _draw_bullseye_and_label(
    overlay: Image.Image,
    px: float,
    py: float,
    label: str,
    scale: float = 1.0,
    ripple_phase: float = 0.35,
    dot_color: tuple[int, int, int] = (214, 40, 40),
) -> None:
    """Draw Bullseye Ripple (red center, thick white ring, white waves) + centered top white pointer label."""
    ss = 2
    r_max = int(round(48 * scale))
    patch_sz = (r_max + 8) * 2
    p_ss = patch_sz * ss
    c_ss = p_ss // 2
    bull_ss = Image.new("RGBA", (p_ss, p_ss), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bull_ss)

    # 3 concentric white ripple waves
    for k in range(3):
        prog = (ripple_phase + k / 3.0) % 1.0
        rr = int(round((11.0 + 30.0 * prog) * scale * ss))
        alpha = int(round(200 * (1.0 - prog) ** 1.3))
        if alpha > 8:
            bd.ellipse([c_ss - rr, c_ss - rr, c_ss + rr, c_ss + rr], outline=(255, 255, 255, alpha), width=max(2, int(round(1.8 * scale * ss))))

    # Subtle dark outer rim so bullseye stays visible over snow peaks
    r_outer = int(round(10.5 * scale * ss))
    bd.ellipse([c_ss - r_outer, c_ss - r_outer, c_ss + r_outer, c_ss + r_outer], fill=(0, 0, 0, 120))
    r_white = int(round(9.3 * scale * ss))
    bd.ellipse([c_ss - r_white, c_ss - r_white, c_ss + r_white, c_ss + r_white], fill=(255, 255, 255, 255))
    r_core = int(round(5.4 * scale * ss))
    bd.ellipse([c_ss - r_core, c_ss - r_core, c_ss + r_core, c_ss + r_core], fill=(*dot_color, 255))

    bull = bull_ss.resize((patch_sz, patch_sz), Image.Resampling.LANCZOS)
    overlay.alpha_composite(bull, (int(round(px - patch_sz / 2.0)), int(round(py - patch_sz / 2.0))))

    if not label:
        return

    # Centered White Pointer Label directly ABOVE bullseye (auto-flips below if near top edge)
    txt = str(label).strip().upper()
    font_sz = max(14, int(round(24.0 * scale)))
    font = _get_label_font(font_sz)
    dummy = ImageDraw.Draw(overlay)
    tb = dummy.textbbox((0, 0), txt, font=font)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]

    pad_x = int(round(12.0 * scale))
    pad_y = int(round(6.0 * scale))
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    caret_h = max(5, int(round(7.0 * scale)))
    caret_hw = max(5, int(round(6.5 * scale)))
    radius = max(3, int(round(4.0 * scale)))

    flip_below = (py - 18.0 * scale - caret_h - box_h) < max(24.0, overlay.height * 0.03)

    sh_pad = 12
    lp_w = (box_w + sh_pad * 2) * ss
    lp_h = (box_h + caret_h + sh_pad * 2) * ss
    lbl_ss = Image.new("RGBA", (lp_w, lp_h), (0, 0, 0, 0))
    mask_lbl = Image.new("L", (lp_w, lp_h), 0)
    md = ImageDraw.Draw(mask_lbl)

    bx0 = sh_pad * ss
    bx1 = bx0 + box_w * ss
    cx_b = (bx0 + bx1) // 2
    if not flip_below:
        by0 = sh_pad * ss
        by1 = by0 + box_h * ss
        md.rounded_rectangle([bx0, by0, bx1, by1], radius=radius * ss, fill=255)
        md.polygon([(cx_b - caret_hw * ss, by1 - 2), (cx_b + caret_hw * ss, by1 - 2), (cx_b, by1 + caret_h * ss)], fill=255)
    else:
        by0 = (sh_pad + caret_h) * ss
        by1 = by0 + box_h * ss
        md.rounded_rectangle([bx0, by0, bx1, by1], radius=radius * ss, fill=255)
        md.polygon([(cx_b - caret_hw * ss, by0 + 2), (cx_b + caret_hw * ss, by0 + 2), (cx_b, by0 - caret_h * ss)], fill=255)

    sh_l = mask_lbl.filter(ImageFilter.GaussianBlur(radius=4 * ss))
    lbl_ss.paste(Image.new("RGBA", (lp_w, lp_h), (0, 0, 0, 125)), (0, 2 * ss), sh_l)
    lbl_ss.paste(Image.new("RGBA", (lp_w, lp_h), (255, 255, 255, 255)), (0, 0), mask_lbl)

    lbl_img = lbl_ss.resize((box_w + sh_pad * 2, box_h + caret_h + sh_pad * 2), Image.Resampling.LANCZOS)
    ld = ImageDraw.Draw(lbl_img)
    text_y_box = sh_pad if not flip_below else (sh_pad + caret_h)
    text_x = sh_pad + pad_x - tb[0]
    text_y = text_y_box + pad_y - tb[1]
    ld.text((text_x, text_y), txt, font=font, fill=(17, 17, 17, 255))

    paste_x = int(round(px - (box_w + sh_pad * 2) / 2.0))
    paste_x = max(8, min(overlay.width - lbl_img.width - 8, paste_x))
    if not flip_below:
        paste_y = int(round(py - 14.0 * scale - caret_h - box_h - sh_pad))
    else:
        paste_y = int(round(py + 14.0 * scale - sh_pad))
    overlay.alpha_composite(lbl_img, (paste_x, paste_y))


def render_gis_vector_overlays(
    base_rgb: np.ndarray | Image.Image,
    npz_data: dict[str, Any],
    territories_dict: dict[str, str] | None = None,
    country_groups: dict[str, list[str]] | None = None,
    cam_cx: float = 0.5,
    cam_cy: float = 0.5,
    cam_zoom: float = 1.0,
    screen_w: int | None = None,
    screen_h: int | None = None,
    trails: list[dict[str, Any]] | None = None,
    pin_badges: list[dict[str, Any]] | None = None,
    bullseyes: list[dict[str, Any]] | None = None,
    highlight_zones: list[dict[str, Any]] | None = None,
    force_vn_islands: bool | None = None,
) -> Image.Image:
    """Render screen-space crisp vector overlays on top of a baked/cropped map frame.

    Includes:
    - 1px neutral country boundary lines (`#CFD1CC` @ 55%)
    - 2.5px glowing active territory borders (dissolved outer borders for blocs like `USSR`)
    - Tactical translucent `highlight_zones` (e.g. Rhineland / 30km exclusion ring)
    - Arc-length dotted trails (`o o o`) + 44x44px SVG Map Pin Badges (`resvg_py`)
    - Bullseye ripples + centered white pointer labels (`BRAUNAU AM INN`, `KIEV`, etc.)
    - Single-pass screen-space `HOÀNG SA` & `TRƯỜNG SA` markers when East Sea is in frame
    """
    if isinstance(base_rgb, Image.Image):
        frame_img = base_rgb.convert("RGB")
        sw = screen_w or frame_img.width
        sh = screen_h or frame_img.height
        if (frame_img.width, frame_img.height) != (sw, sh):
            frame_img = frame_img.resize((sw, sh), Image.Resampling.LANCZOS)
        frame_arr = np.asarray(frame_img, dtype=np.uint8)
    else:
        frame_arr = np.asarray(base_rgb, dtype=np.uint8)
        sh, sw = frame_arr.shape[:2]
        if screen_w and screen_h and (sw, sh) != (screen_w, screen_h):
            frame_arr = cv2.resize(frame_arr, (screen_w, screen_h), interpolation=cv2.INTER_AREA)
            sw, sh = screen_w, screen_h

    scale = max(0.65, min(2.0, sw / 1920.0))
    meta = npz_data["meta"]
    records = npz_data["country_records"]
    c_borders = npz_data["country_borders"]

    def _norm_to_px_arr(pts_norm: np.ndarray) -> np.ndarray:
        aspect_screen = sw / max(1.0, float(sh))
        aspect_canvas = 16.0 / 9.0
        if aspect_screen >= aspect_canvas:
            half_w = 0.5 / cam_zoom
            half_h = half_w * (aspect_canvas / aspect_screen)
        else:
            half_h = 0.5 / cam_zoom
            half_w = half_h * (aspect_screen / aspect_canvas)
        sx = (pts_norm[:, 0] - (cam_cx - half_w)) / max(1e-6, 2.0 * half_w) * sw
        sy = (pts_norm[:, 1] - (cam_cy - half_h)) / max(1e-6, 2.0 * half_h) * sh
        return np.column_stack((sx, sy))

    def _ll_to_px(lon: float, lat: float) -> tuple[float, float]:
        nx, ny = lonlat_to_region_norm(lon, lat, meta)
        return region_norm_to_screen(nx, ny, cam_cx, cam_cy, cam_zoom, sw, sh)

    # 1. Neutral 1px boundary lines + Glowing territory borders (rendered via OpenCV AA layers)
    border_overlay = np.zeros((sh, sw, 4), dtype=np.uint8)
    neutral_bgr_a = (204, 209, 207, 140)  # #CFD1CC @ ~55%
    for line in npz_data["border_lines"]:
        pts = _norm_to_px_arr(np.asarray(line, dtype=np.float32))
        if np.max(pts[:, 0]) < -20 or np.min(pts[:, 0]) > sw + 20 or np.max(pts[:, 1]) < -20 or np.min(pts[:, 1]) > sh + 20:
            continue
        _draw_aa_polyline_cv2(border_overlay, pts, neutral_bgr_a, max(1, int(round(1.1 * scale))), closed=False)

    # Glowing active territory borders (dissolve multi-country groups when >1 country)
    glow_layer = np.zeros((sh, sw, 4), dtype=np.uint8)
    core_layer = np.zeros((sh, sw, 4), dtype=np.uint8)
    for key, role_raw in (territories_dict or {}).items():
        role = _normalize_role(role_raw)
        brd_rgb = TERRITORY_RAMPS[role]["border"]
        isos = resolve_country_isos(key, records, country_groups=country_groups)
        if not isos:
            continue

        rings_to_draw: list[np.ndarray] = []
        if len(isos) > 1:
            # Dissolve group outer border so bloc (e.g. USSR) has unified glowing outline
            group_polys: list[Polygon] = []
            for iso in isos:
                for ring in c_borders.get(iso, []):
                    if len(ring) >= 3:
                        p = Polygon(ring)
                        if not p.is_valid:
                            p = p.buffer(0)
                        if not p.is_empty:
                            group_polys.append(p)
            if group_polys:
                dissolved = unary_union(group_polys)
                for dp in _geom_to_polygons(dissolved):
                    rings_to_draw.append(np.asarray(dp.exterior.coords, dtype=np.float32))
        else:
            for ring in c_borders.get(isos[0], []):
                if len(ring) >= 3:
                    rings_to_draw.append(np.asarray(ring, dtype=np.float32))

        glow_col = (*brd_rgb, 72)
        core_col = (*brd_rgb, 242)
        for ring_norm in rings_to_draw:
            pts = _norm_to_px_arr(ring_norm)
            if np.max(pts[:, 0]) < -30 or np.min(pts[:, 0]) > sw + 30 or np.max(pts[:, 1]) < -30 or np.min(pts[:, 1]) > sh + 30:
                continue
            _draw_aa_polyline_cv2(glow_layer, pts, glow_col, max(3, int(round(6.0 * scale))), closed=True)
            _draw_aa_polyline_cv2(core_layer, pts, core_col, max(2, int(round(2.4 * scale))), closed=True)

    # Composite OpenCV border layers onto PIL RGBA canvas
    canvas_rgba = Image.fromarray(frame_arr, mode="RGB").convert("RGBA")
    canvas_rgba = Image.alpha_composite(canvas_rgba, Image.fromarray(border_overlay, mode="RGBA"))
    canvas_rgba = Image.alpha_composite(canvas_rgba, Image.fromarray(glow_layer, mode="RGBA"))
    canvas_rgba = Image.alpha_composite(canvas_rgba, Image.fromarray(core_layer, mode="RGBA"))

    # 2. Tactical Highlight Zones (e.g. Rhineland or 30km exclusion buffer)
    if highlight_zones:
        zone_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        zd = ImageDraw.Draw(zone_layer, "RGBA")
        for hz in highlight_zones:
            pts_ll = hz.get("lonlats") or []
            if len(pts_ll) >= 3:
                pts_px = [_ll_to_px(lon, lat) for lon, lat in pts_ll]
                fill_rgba = tuple(hz.get("fill_rgba", (255, 255, 255, 56)))
                brd_rgba = tuple(hz.get("border_rgba", (255, 255, 255, 235)))
                zd.polygon(pts_px, fill=fill_rgba)
                zd.line(pts_px + [pts_px[0]], fill=brd_rgba, width=max(2, int(round(2.5 * scale))))
        canvas_rgba = Image.alpha_composite(canvas_rgba, zone_layer)

    # 3. Dotted Trails (Arc-Length) + Leading Pin Badges
    trail_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    td = ImageDraw.Draw(trail_layer, "RGBA")
    pending_badges: list[tuple[float, float, str, str, float]] = []

    for tr in trails or []:
        pts_ll = tr.get("lonlats") or []
        if len(pts_ll) < 2:
            continue
        p0 = _ll_to_px(*pts_ll[0])
        p2 = _ll_to_px(*pts_ll[-1])
        if len(pts_ll) >= 3:
            p1 = _ll_to_px(*pts_ll[1])
        else:
            p1 = (0.5 * (p0[0] + p2[0]), 0.5 * (p0[1] + p2[1]) - 0.12 * math.hypot(p2[0] - p0[0], p2[1] - p0[1]))

        role = _normalize_role(tr.get("role", "red"))
        dot_rgb = TERRITORY_RAMPS[role]["trail"]
        progress = float(tr.get("progress", 1.0))
        step_px = float(tr.get("step_px", 20.0)) * scale
        dots, tip_xy, _ = sample_bezier_arclength(p0, p1, p2, step_px=step_px, progress=progress)

        r_dot = 5.5 * scale
        r_rim = 7.2 * scale
        for dx, dy in dots[:-1] if len(dots) > 1 and tr.get("icon") else dots:
            td.ellipse([dx - r_rim, dy - r_rim + 2.0 * scale, dx + r_rim, dy + r_rim + 2.0 * scale], fill=(0, 0, 0, 115))
            td.ellipse([dx - r_rim, dy - r_rim, dx + r_rim, dy + r_rim], fill=(255, 255, 255, 245))
            td.ellipse([dx - r_dot, dy - r_dot, dx + r_dot, dy + r_dot], fill=(*dot_rgb, 255))

        if tr.get("icon") and progress > 0.05:
            pending_badges.append((tip_xy[0], tip_xy[1], str(tr["icon"]), role, float(tr.get("badge_scale", 1.0)) * scale))

    canvas_rgba = Image.alpha_composite(canvas_rgba, trail_layer)

    for pb in pin_badges or []:
        lon, lat = pb["lonlat"]
        bx, by = _ll_to_px(lon, lat)
        pending_badges.append(
            (bx, by, str(pb.get("icon", "infantry")), _normalize_role(pb.get("role", "red")), float(pb.get("scale", 1.0)) * scale)
        )

    for bx, by, icon_name, role, bscale in pending_badges:
        _draw_pin_badge(canvas_rgba, bx, by, icon_name=icon_name, role=role, scale=bscale)

    # 4. City Target Bullseyes + White Pointer Labels
    for be in bullseyes or []:
        lon, lat = be["lonlat"]
        bx, by = _ll_to_px(lon, lat)
        if bx < -40 or bx > sw + 40 or by < -40 or by > sh + 40:
            continue
        _draw_bullseye_and_label(
            canvas_rgba,
            bx,
            by,
            label=str(be.get("label", "")),
            scale=float(be.get("scale", 1.0)) * scale,
            ripple_phase=float(be.get("ripple_phase", 0.32)),
            dot_color=tuple(be.get("color", (214, 40, 40))),
        )

    # 5. Single-pass Screen-Space Vietnam Sovereignty Markers (HOÀNG SA & TRƯỜNG SA)
    show_vn = bool(force_vn_islands) if force_vn_islands is not None else bool(meta.get("has_vn_islands", False))
    if show_vn:
        vn_role = _normalize_role((territories_dict or {}).get("VIETNAM", (territories_dict or {}).get("VNM", "red")))
        dot_rgb = (210, 48, 48) if vn_role == "red" else tuple(int(c * 255) for c in TERRITORY_RAMPS[vn_role]["mid"])
        vn_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        vd = ImageDraw.Draw(vn_layer, "RGBA")
        dot_r = max(3.5, 4.5 * scale)
        for lon, lat in HOANG_SA_DOTS + TRUONG_SA_DOTS:
            vx, vy = _ll_to_px(lon, lat)
            if 0 <= vx <= sw and 0 <= vy <= sh:
                vd.ellipse([vx - dot_r - 1.5, vy - dot_r - 1.5, vx + dot_r + 1.5, vy + dot_r + 1.5], fill=(255, 255, 255, 235))
                vd.ellipse([vx - dot_r, vy - dot_r, vx + dot_r, vy + dot_r], fill=(*dot_rgb, 255))

        lbl_font = _get_label_font(max(16, int(round(20.0 * scale))))
        hs_x, hs_y = _ll_to_px(112.95, 16.55)
        ts_x, ts_y = _ll_to_px(114.80, 9.75)
        for txt, lx, ly in (("HOÀNG SA", hs_x, hs_y), ("TRƯỜNG SA", ts_x, ts_y)):
            if 0 <= lx <= sw and 0 <= ly <= sh:
                tx = lx + dot_r * 2.2
                ty = ly - 10.0 * scale
                vd.text((tx + 2, ty + 2), txt, font=lbl_font, fill=(0, 0, 0, 230))
                vd.text((tx, ty), txt, font=lbl_font, fill=(248, 248, 246, 250))

        canvas_rgba = Image.alpha_composite(canvas_rgba, vn_layer)

    return canvas_rgba


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pre-bake GIS terrain & vector `.npz` plates.")
    parser.add_argument("--regions", nargs="+", default=list(DEFAULT_REGION_CONFIGS.keys()))
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()

    for rkey in args.regions:
        bake_region(rkey, force_rebuild=args.rebuild)
