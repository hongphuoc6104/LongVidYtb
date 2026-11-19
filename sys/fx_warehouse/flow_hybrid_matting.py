"""Reusable Flow CDP post-processing & AI matting pipeline for Chánh Niệm Kể.

Topic-agnostic asset preparation utilities:
1. `clean_and_crop_flow_image`: inverse-alpha Flow BELUGA corner sparkle removal + center overscan crop.
2. `matte_portrait_or_sprite`: AI matting (`rembg` `birefnet-portrait` / `birefnet-general` / `u2net` when
   available) with smart border-seeded GrabCut + soft edge-defringe fallback, followed by
   `scipy.ndimage.distance_transform_edt` anti-aliased `#FFFFFF` sticker outline (`6.0px`) and soft drop shadow.
3. `prepare_cutaway_illustration`: sparkle removal, overscan crop, and uniform `#F4F3EE` paper normalization
   for 2D technical cutaway / blueprint illustrations.
"""

from __future__ import annotations

import importlib.util
import logging
import math
from collections import deque
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps
from scipy.ndimage import binary_fill_holes, distance_transform_edt

logger = logging.getLogger("fx_warehouse.flow_hybrid_matting")

SYS_DIR = Path(__file__).resolve().parents[1]
_SPARKLE_MODULE: Any = None
_REMBG_SESSIONS: dict[str, Any] = {}


def _get_clean_beluga_sparkle_pil():
    """Lazily load `clean_beluga_sparkle_pil` without requiring caller sys.path tweaks."""
    global _SPARKLE_MODULE
    if _SPARKLE_MODULE is None:
        sparkle_path = SYS_DIR / "flow_video" / "sparkle_unblend.py"
        spec = importlib.util.spec_from_file_location("sparkle_unblend", str(sparkle_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot locate sparkle_unblend module at {sparkle_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SPARKLE_MODULE = mod
    return _SPARKLE_MODULE.clean_beluga_sparkle_pil


def clean_and_crop_flow_image(raw_path: str | Path, crop_pct: float = 0.025) -> Image.Image:
    """Remove Flow BELUGA bottom-right sparkle and apply center overscan crop (~1.045x-1.05x)."""
    p = Path(raw_path)
    if not p.is_file():
        raise FileNotFoundError(f"Raw Flow image not found: {p}")
    clean_fn = _get_clean_beluga_sparkle_pil()
    with Image.open(p) as im:
        rgba = im.convert("RGBA")
    w_raw, h_raw = rgba.size
    cleaned = clean_fn(rgba)

    # Polish tiny JPEG ringing residual around the BELUGA star ROI when corner patch is uniform
    roi: tuple[int, int, int, int] | None = None
    if (w_raw, h_raw) == (1024, 1024):
        roi = (h_raw - 136, h_raw - 68, w_raw - 136, w_raw - 68)
    elif (w_raw, h_raw) in ((768, 1376), (1376, 768)):
        roi = (h_raw - 132, h_raw - 64, w_raw - 132, w_raw - 64)
    if roi is not None:
        y0, y1, x0, x1 = roi
        arr = np.asarray(cleaned, dtype=np.uint8).copy()
        ring = np.concatenate(
            [
                arr[max(0, y0 - 8) : y0, x0:x1, :3].reshape(-1, 3),
                arr[y1 : min(h_raw, y1 + 8), x0:x1, :3].reshape(-1, 3),
                arr[y0:y1, max(0, x0 - 8) : x0, :3].reshape(-1, 3),
                arr[y0:y1, x1 : min(w_raw, x1 + 8), :3].reshape(-1, 3),
            ],
            axis=0,
        )
        if len(ring) >= 32 and float(np.std(ring)) < 10.0:
            ring_med = np.median(ring, axis=0)
            patch = arr[y0:y1, x0:x1, :3].astype(np.float32)
            diff = np.linalg.norm(patch - ring_med[None, None, :], axis=2)
            mask = (diff > 2.5) & (diff < 22.0)
            if np.any(mask):
                patch[mask] = ring_med
                arr[y0:y1, x0:x1, :3] = np.round(patch).astype(np.uint8)
                cleaned = Image.fromarray(arr, mode="RGBA")

    w, h = cleaned.size
    pct = max(0.0, min(0.15, float(crop_pct)))
    if pct <= 0.0:
        return cleaned
    mx = max(1, int(round(w * pct)))
    my = max(1, int(round(h * pct)))
    if mx * 2 >= w or my * 2 >= h:
        return cleaned
    return cleaned.crop((mx, my, w - mx, h - my))


def _extract_alpha_rembg(img_rgb: Image.Image, *, is_portrait: bool = True) -> np.ndarray | None:
    """Attempt AI background matting via `rembg` (CUDAExecutionProvider -> CPUExecutionProvider)."""
    try:
        import onnxruntime as ort  # type: ignore[import-not-found]
        import rembg  # type: ignore[import-not-found]
    except Exception:
        return None

    avail_providers = set(ort.get_available_providers())
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if "CUDAExecutionProvider" in avail_providers
        else ["CPUExecutionProvider"]
    )
    model_candidates = (
        ["birefnet-portrait", "birefnet-general", "u2net"]
        if is_portrait
        else ["birefnet-general", "u2net"]
    )
    for model_name in model_candidates:
        try:
            sess = _REMBG_SESSIONS.get(model_name)
            if sess is None:
                sess = rembg.new_session(model_name, providers=providers)
                _REMBG_SESSIONS[model_name] = sess
            out = rembg.remove(
                img_rgb,
                session=sess,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=15,
                alpha_matting_erode_size=6,
            )
            alpha = np.asarray(out.convert("RGBA"))[..., 3].astype(np.float32) / 255.0
            if np.max(alpha) > 0.1 and np.min(alpha) < 0.9:
                logger.info("Matting via rembg (%s, providers=%s)", model_name, providers[0])
                return alpha
        except Exception as exc:
            logger.debug("rembg model %s unavailable/failed: %s", model_name, exc)
    return None


def _estimate_flat_bg_color(arr_rgb: np.ndarray) -> tuple[np.ndarray, float]:
    """Estimate flat studio backdrop RGB from top/left/right border strips (preserving bottom bust cut)."""
    h, w, _ = arr_rgb.shape
    strip = max(4, min(14, min(h, w) // 40))
    samples = np.concatenate(
        [
            arr_rgb[:strip, :, :].reshape(-1, 3),
            arr_rgb[: int(h * 0.65), :strip, :].reshape(-1, 3),
            arr_rgb[: int(h * 0.65), -strip:, :].reshape(-1, 3),
        ],
        axis=0,
    ).astype(np.float32)
    bg_rgb = np.median(samples, axis=0)
    dists = np.linalg.norm(samples - bg_rgb, axis=1)
    inliers = samples[dists <= max(18.0, float(np.percentile(dists, 75)))]
    if len(inliers) >= 16:
        bg_rgb = np.median(inliers, axis=0)
        bg_std = float(np.std(np.linalg.norm(inliers - bg_rgb, axis=1)))
    else:
        bg_std = float(np.std(dists))
    return bg_rgb.astype(np.float32), bg_std


def _flood_border_bg(dist_bg: np.ndarray, tol: float) -> np.ndarray:
    """Find pixels connected to top/left/right borders (or bottom corners) within color tolerance."""
    h, w = dist_bg.shape
    cand = dist_bg <= tol
    visited = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()

    def _seed(y: int, x: int) -> None:
        if cand[y, x] and not visited[y, x]:
            visited[y, x] = True
            q.append((y, x))

    for x in range(w):
        _seed(0, x)
        if x < max(8, w // 12) or x >= w - max(8, w // 12):
            _seed(h - 1, x)
    for y in range(h):
        _seed(y, 0)
        _seed(y, w - 1)

    while q:
        cy, cx = q.popleft()
        if cy > 0 and cand[cy - 1, cx] and not visited[cy - 1, cx]:
            visited[cy - 1, cx] = True
            q.append((cy - 1, cx))
        if cy + 1 < h and cand[cy + 1, cx] and not visited[cy + 1, cx]:
            visited[cy + 1, cx] = True
            q.append((cy + 1, cx))
        if cx > 0 and cand[cy, cx - 1] and not visited[cy, cx - 1]:
            visited[cy, cx - 1] = True
            q.append((cy, cx - 1))
        if cx + 1 < w and cand[cy, cx + 1] and not visited[cy, cx + 1]:
            visited[cy, cx + 1] = True
            q.append((cy, cx + 1))
    return visited


def _extract_alpha_grabcut_smart(arr_rgb: np.ndarray, *, is_portrait: bool = True) -> np.ndarray:
    """Smart border-seeded GrabCut + soft edge alpha matting & color de-fringing.

    Protects white shirt collars/highlights enclosed within dark clothing while cleanly
    separating hair strands, rims, and sprite contours from uniform studio backgrounds.
    """
    h, w, _ = arr_rgb.shape
    rgb_f = arr_rgb.astype(np.float32)
    bg_rgb, bg_std = _estimate_flat_bg_color(arr_rgb)
    dist_bg = np.linalg.norm(rgb_f - bg_rgb[None, None, :], axis=2)

    tight_tol = max(14.0, bg_std * 3.8 + 8.5)
    border_bg = _flood_border_bg(dist_bg, tol=tight_tol)

    # Identify enclosed interior silhouette so white collars/shirts are never treated as background
    filled_fg = binary_fill_holes(~border_bg)
    enclosed_interior = filled_fg & border_bg

    # Build GrabCut trimap
    gc_mask = np.full((h, w), cv2.GC_PR_FGD, dtype=np.uint8)

    k_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    sure_bg = cv2.erode(border_bg.astype(np.uint8), k_erode, iterations=1) > 0
    k_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    near_border_bg = (cv2.dilate(border_bg.astype(np.uint8), k_dilate, iterations=1) > 0) & (~sure_bg)

    gc_mask[near_border_bg & (dist_bg < max(46.0, tight_tol * 2.6))] = cv2.GC_PR_BGD
    gc_mask[dist_bg >= max(44.0, tight_tol * 2.4)] = cv2.GC_FGD
    if is_portrait:
        # Enclosed bright areas (white shirt collar/teeth/eye whites) stay foreground
        gc_mask[enclosed_interior] = cv2.GC_FGD
    else:
        # For sprites (e.g. gaps under chassis/rotors), interior pure-bg holes are evaluated as PR_BGD
        interior_pure = (~border_bg) & (dist_bg <= min(10.0, tight_tol * 0.6))
        gc_mask[interior_pure] = cv2.GC_PR_BGD

    gc_mask[sure_bg] = cv2.GC_BGD

    if np.any(gc_mask == cv2.GC_BGD) and np.any((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD)):
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        bgr = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
        try:
            cv2.grabCut(bgr, gc_mask, (0, 0, w, h), bgd_model, fgd_model, 4, cv2.GC_INIT_WITH_MASK)
        except Exception as exc:
            logger.debug("GrabCut refinement skipped: %s", exc)
        fg_bin = (gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD)
    else:
        fg_bin = ~border_bg

    # Keep main foreground component(s) to eliminate tiny background speckles
    num_lbl, labels, stats, _ = cv2.connectedComponentsWithStats(fg_bin.astype(np.uint8), connectivity=8)
    if num_lbl > 1:
        areas = stats[1:, cv2.CC_STAT_AREA]
        max_area = float(np.max(areas)) if len(areas) else 0.0
        min_keep = max(64.0, max_area * (0.04 if is_portrait else 0.015))
        keep = np.zeros((h, w), dtype=bool)
        for lbl_idx in range(1, num_lbl):
            if stats[lbl_idx, cv2.CC_STAT_AREA] >= min_keep:
                keep |= labels == lbl_idx
        fg_bin = keep

    if is_portrait:
        fg_bin = binary_fill_holes(fg_bin)

    # Soft alpha estimation in a narrow 3px boundary band around `fg_bin`
    dist_inside = distance_transform_edt(fg_bin)
    dist_outside = distance_transform_edt(~fg_bin)
    alpha = fg_bin.astype(np.float32)

    edge_band = (dist_inside <= 2.5) & (dist_outside <= 2.5)
    # Use color distance from bg_rgb to assign smooth subpixel alpha on anti-aliased hair/ink edges
    color_alpha = np.clip((dist_bg - tight_tol * 0.55) / max(18.0, 48.0 - tight_tol * 0.55), 0.0, 1.0)
    geom_alpha = np.clip(0.5 + (dist_inside - dist_outside) * 0.35, 0.0, 1.0)
    alpha[edge_band] = 0.55 * color_alpha[edge_band] + 0.45 * geom_alpha[edge_band]
    # Guarantee clean 0 outside 3px margin
    alpha[dist_outside > 3.0] = 0.0
    alpha[dist_inside > 3.0] = 1.0

    # Light Gaussian feather (0.6px) for natural anti-aliased contour
    alpha = cv2.GaussianBlur(alpha, (3, 3), sigmaX=0.6, sigmaY=0.6)
    alpha[dist_outside > 4.0] = 0.0
    alpha[dist_inside > 4.0] = 1.0
    return np.clip(alpha, 0.0, 1.0).astype(np.float32)


def _defringe_edges(arr_rgb: np.ndarray, alpha_f: np.ndarray, bg_rgb: np.ndarray) -> np.ndarray:
    """Remove studio backdrop color bleed from semi-transparent edge pixels."""
    out = arr_rgb.astype(np.float32).copy()
    semi = (alpha_f > 0.04) & (alpha_f < 0.96)
    if np.any(semi):
        a = alpha_f[semi][:, None]
        bg = bg_rgb[None, :]
        unmixed = (out[semi] - (1.0 - a) * bg) / np.maximum(a, 0.25)
        out[semi] = np.clip(unmixed, 0.0, 255.0)
    return np.round(out).astype(np.uint8)


def _suppress_green_spill(arr_rgb: np.ndarray, alpha_f: np.ndarray) -> np.ndarray:
    """Despill bright chroma-green fringes if a sprite was generated on #00FF00."""
    out = arr_rgb.astype(np.float32).copy()
    edge = (alpha_f > 0.02) & (alpha_f < 0.98)
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    rb_avg = 0.5 * (r + b)
    spill = edge & (g > rb_avg + 18.0)
    if np.any(spill):
        out[..., 1][spill] = np.minimum(g[spill], rb_avg[spill] + 10.0)
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _apply_bw_silver_gelatin(arr_rgb: np.ndarray, alpha_f: np.ndarray) -> np.ndarray:
    """Convert RGB to high-contrast silver-gelatin B&W using only foreground luminance statistics."""
    rgb_img = Image.fromarray(arr_rgb, mode="RGB")
    gray = np.asarray(ImageOps.grayscale(rgb_img), dtype=np.float32)
    fg_pixels = gray[alpha_f > 0.5]
    if fg_pixels.size > 64:
        lo = float(np.percentile(fg_pixels, 1.2))
        hi = float(np.percentile(fg_pixels, 98.8))
        if hi > lo + 8.0:
            gray = np.clip((gray - lo) * (255.0 / (hi - lo)), 0.0, 255.0)
    gray_img = Image.fromarray(np.round(gray).astype(np.uint8), mode="L")
    gray_img = ImageEnhance.Contrast(gray_img).enhance(1.14)
    g_arr = np.asarray(gray_img, dtype=np.uint8)
    return np.stack([g_arr, g_arr, g_arr], axis=-1)


def apply_smooth_sticker_outline_and_shadow(
    fg_rgba: Image.Image,
    *,
    border_px: float = 6.0,
    outline_color: tuple[int, int, int] = (255, 255, 255),
    add_drop_shadow: bool = True,
    shadow_dx: int = 8,
    shadow_dy: int = 12,
    shadow_blur: float = 10.0,
    shadow_alpha: float = 0.42,
    shadow_color: tuple[int, int, int] = (10, 10, 8),
) -> Image.Image:
    """Add smooth `distance_transform_edt` white sticker outline + soft drop shadow."""
    fg_arr = np.asarray(fg_rgba.convert("RGBA"))
    pad = int(
        math.ceil(
            max(0.0, float(border_px))
            + (float(shadow_blur) * 3.0 + max(abs(shadow_dx), abs(shadow_dy)) if add_drop_shadow else 0.0)
            + 8
        )
    )
    h, w, _ = fg_arr.shape
    padded_fg = np.zeros((h + pad * 2, w + pad * 2, 4), dtype=np.uint8)
    padded_fg[pad : pad + h, pad : pad + w, :] = fg_arr

    alpha_f = padded_fg[..., 3].astype(np.float32) / 255.0
    if border_px > 0.0:
        binary_fg = alpha_f > 0.5
        dist_out = distance_transform_edt(~binary_fg)
        t = np.clip((dist_out - (float(border_px) - 0.8)) / 1.6, 0.0, 1.0)
        outline_alpha = 1.0 - (t * t * (3.0 - 2.0 * t))
        outline_alpha = np.maximum(outline_alpha, alpha_f)
    else:
        outline_alpha = alpha_f

    out_h, out_w = padded_fg.shape[:2]
    outline_arr = np.zeros((out_h, out_w, 4), dtype=np.uint8)
    outline_arr[..., 0] = outline_color[0]
    outline_arr[..., 1] = outline_color[1]
    outline_arr[..., 2] = outline_color[2]
    outline_arr[..., 3] = np.clip(np.round(outline_alpha * 255.0), 0, 255).astype(np.uint8)

    outline_img = Image.fromarray(outline_arr, mode="RGBA")
    fg_img = Image.fromarray(padded_fg, mode="RGBA")
    sticker = Image.alpha_composite(outline_img, fg_img)

    if add_drop_shadow and shadow_alpha > 0.0:
        sh_mask = Image.fromarray(outline_arr[..., 3], mode="L")
        if shadow_dx != 0 or shadow_dy != 0:
            sh_mask = ImageChops.offset(sh_mask, shadow_dx, shadow_dy)
        if shadow_blur > 0.0:
            sh_mask = sh_mask.filter(ImageFilter.GaussianBlur(radius=float(shadow_blur)))
        sh_alpha_arr = np.asarray(sh_mask, dtype=np.float32) * float(shadow_alpha)
        sh_arr = np.zeros((out_h, out_w, 4), dtype=np.uint8)
        sh_arr[..., 0] = shadow_color[0]
        sh_arr[..., 1] = shadow_color[1]
        sh_arr[..., 2] = shadow_color[2]
        sh_arr[..., 3] = np.clip(np.round(sh_alpha_arr), 0, 255).astype(np.uint8)
        shadow_img = Image.fromarray(sh_arr, mode="RGBA")
        sticker = Image.alpha_composite(shadow_img, sticker)

    bbox = sticker.getbbox()
    if bbox:
        x0 = max(0, bbox[0] - 2)
        y0 = max(0, bbox[1] - 2)
        x1 = min(out_w, bbox[2] + 2)
        y1 = min(out_h, bbox[3] + 2)
        sticker = sticker.crop((x0, y0, x1, y1))
    return sticker


def matte_portrait_or_sprite(
    raw_path: str | Path,
    out_path: str | Path,
    target_height: int = 920,
    border_px: float = 6.0,
    bw_tone: bool = True,
    *,
    crop_pct: float = 0.025,
    use_rembg: bool = True,
    add_drop_shadow: bool = True,
    shadow_dx: int = 8,
    shadow_dy: int = 12,
    shadow_blur: float = 10.0,
    shadow_alpha: float = 0.42,
) -> Path:
    """Clean Flow sparkle, segment subject cleanly, apply smooth 6px `#FFFFFF` border & soft drop shadow."""
    cleaned = clean_and_crop_flow_image(raw_path, crop_pct=crop_pct)
    rgb_img = cleaned.convert("RGB")
    arr_rgb = np.asarray(rgb_img, dtype=np.uint8)
    bg_rgb, _ = _estimate_flat_bg_color(arr_rgb)

    alpha_f: np.ndarray | None = None
    if use_rembg:
        alpha_f = _extract_alpha_rembg(rgb_img, is_portrait=bw_tone)
    if alpha_f is None:
        alpha_f = _extract_alpha_grabcut_smart(arr_rgb, is_portrait=bw_tone)

    # Remove studio background bleed at edge pixels
    clean_rgb = _defringe_edges(arr_rgb, alpha_f, bg_rgb)
    # Suppress chroma-green spill if sprite used #00FF00 background
    if bg_rgb[1] > max(bg_rgb[0], bg_rgb[2]) + 40.0:
        clean_rgb = _suppress_green_spill(clean_rgb, alpha_f)

    if bw_tone:
        clean_rgb = _apply_bw_silver_gelatin(clean_rgb, alpha_f)

    fg_rgba = Image.fromarray(
        np.dstack([clean_rgb, np.clip(np.round(alpha_f * 255.0), 0, 255).astype(np.uint8)]),
        mode="RGBA",
    )

    # Tightly crop to subject before scaling to `target_height` so border_px stays exact at target scale
    bbox = fg_rgba.getbbox()
    if bbox:
        fg_rgba = fg_rgba.crop(bbox)

    th = max(64, int(target_height))
    fw, fh = fg_rgba.size
    tw = max(1, int(round(fw * (th / max(1, fh)))))
    fg_resized = fg_rgba.resize((tw, th), Image.Resampling.LANCZOS)

    sticker = apply_smooth_sticker_outline_and_shadow(
        fg_resized,
        border_px=float(border_px),
        outline_color=(255, 255, 255),
        add_drop_shadow=add_drop_shadow,
        shadow_dx=shadow_dx,
        shadow_dy=shadow_dy,
        shadow_blur=shadow_blur,
        shadow_alpha=shadow_alpha,
    )

    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    sticker.save(out_p, format="PNG", optimize=True)
    return out_p


def prepare_cutaway_illustration(
    raw_path: str | Path,
    out_path: str | Path,
    width: int = 1440,
    height: int = 810,
    *,
    crop_pct: float = 0.025,
    paper_bg_rgb: tuple[int, int, int] = (244, 243, 238),
) -> Path:
    """Clean sparkle, overscan crop, and normalize light `#F4F3EE` paper background for 2D cutaways."""
    cleaned = clean_and_crop_flow_image(raw_path, crop_pct=crop_pct).convert("RGB")
    tw, th = max(64, int(width)), max(64, int(height))

    # Sample border background color before resizing
    src_arr = np.asarray(cleaned, dtype=np.float32)
    sh, sw, _ = src_arr.shape
    border_px = max(6, min(20, min(sh, sw) // 30))
    b_samples = np.concatenate(
        [
            src_arr[:border_px, :, :].reshape(-1, 3),
            src_arr[-border_px:, :, :].reshape(-1, 3),
            src_arr[:, :border_px, :].reshape(-1, 3),
            src_arr[:, -border_px:, :].reshape(-1, 3),
        ],
        axis=0,
    )
    lum = b_samples.mean(axis=1)
    light_samples = b_samples[lum >= 190.0]
    src_bg = np.median(light_samples if len(light_samples) >= 32 else b_samples, axis=0)

    # Preserve aspect ratio onto exact (tw, th) paper canvas without geometric distortion
    scale = min(tw / max(1, cleaned.width), th / max(1, cleaned.height))
    rw = max(1, int(round(cleaned.width * scale)))
    rh = max(1, int(round(cleaned.height * scale)))
    resized = cleaned.resize((rw, rh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (tw, th), tuple(int(round(c)) for c in src_bg))
    ox = (tw - rw) // 2
    oy = (th - rh) // 2
    canvas.paste(resized, (ox, oy))

    # Gently normalize outer paper field to uniform `#F4F3EE` without touching ink/shading
    arr = np.asarray(canvas, dtype=np.float32)
    target = np.array(paper_bg_rgb, dtype=np.float32)
    dist = np.linalg.norm(arr - src_bg[None, None, :], axis=2)
    # Smooth blend factor: 1.0 where pixel matches backdrop within ~10 units, 0.0 beyond ~26 units
    blend = 1.0 - np.clip((dist - 10.0) / 16.0, 0.0, 1.0)
    blend = blend * blend * (3.0 - 2.0 * blend)
    arr = arr * (1.0 - blend[..., None]) + target[None, None, :] * blend[..., None]

    out_img = Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), mode="RGB")
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out_p, format="PNG", optimize=True)
    return out_p


__all__ = [
    "apply_smooth_sticker_outline_and_shadow",
    "clean_and_crop_flow_image",
    "matte_portrait_or_sprite",
    "prepare_cutaway_illustration",
]
