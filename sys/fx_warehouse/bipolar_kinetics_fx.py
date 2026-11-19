"""Continuous Kinetic Motion, Specular Glint & Procedural Transition FX (`kinetics-v52`).

Standalone, Colab-T4-portable FX module for Bipolar Dual-Canvas rendering
(``Map <-> Paper``). Zero hardcoded episode topics, zero FFmpeg ``xfade``,
and zero canned fade/hard-cut transitions.

Provides:
1. Continuous Kinetic Helpers & Entrance Spring Physics:
   - ``clamp01``, ``smoothstep``, ``ease_out_cubic``, ``ease_out_back``
   - ``motion_float_transform`` (organic dual-harmonic ambient float + optional stop-motion)
   - ``entrance_spring_params`` (6 tactile editorial entrance curves)
   - ``apply_patch_transform`` (PIL RGBA transform with identity fast-bypass)
   - ``apply_highlighter_glint`` (2.2s diagonal warm-white sweep inside yellow rects)
   - ``apply_pill_specular_sheen`` (Dymo shimmer sweep + live LTR wipe cursor glint)
   - ``compute_marching_dash_phase`` & ``border_pulse_gain`` (0.80..1.25)

2. Custom Procedural Transitions (CPU NumPy + PyTorch CUDA, zero FFmpeg xfade):
   - ``CONCRETE_TRANSITIONS``: ``whip_pan_blur``, ``torn_paper_wipe``,
     ``zoom_punch_whoosh``, ``card_slide``, ``shutter_snap``
   - ``choose_procedural_transition``
   - ``compose_transition_numpy``
   - ``compose_transition_torch``
"""
from __future__ import annotations

import hashlib
import math
from typing import Any

import numpy as np
from PIL import Image

try:
    import torch
    import torch.nn.functional as F

    _HAS_TORCH = True
except Exception:  # pragma: no cover - optional on local CPU
    torch = None  # type: ignore[assignment]
    F = None  # type: ignore[assignment]
    _HAS_TORCH = False


CONCRETE_TRANSITIONS: tuple[str, ...] = (
    "whip_pan_blur",
    "torn_paper_wipe",
    "zoom_punch_whoosh",
    "card_slide",
    "shutter_snap",
)

_TWO_BEAT_TRANSITIONS: tuple[str, ...] = (
    "whip_pan_blur",
    "torn_paper_wipe",
    "zoom_punch_whoosh",
    "card_slide",
)

_TORN_PAPER_FIBER_RGB = (234, 232, 225)  # #EAE8E1
_TORN_PAPER_FIBER_F = (234.0 / 255.0, 232.0 / 255.0, 225.0 / 255.0)
_SHUTTER_BACKDROP_F = 20.0 / 255.0  # #141414

__all__ = [
    "CONCRETE_TRANSITIONS",
    "apply_highlighter_glint",
    "apply_patch_transform",
    "apply_pill_specular_sheen",
    "border_pulse_gain",
    "choose_procedural_transition",
    "clamp01",
    "compose_transition_numpy",
    "compose_transition_torch",
    "compute_marching_dash_phase",
    "ease_out_back",
    "ease_out_cubic",
    "entrance_spring_params",
    "motion_float_transform",
    "smoothstep",
]


# ---------------------------------------------------------------------------
# 1. Scalar Easing Curves & Deterministic Seed Hashing
# ---------------------------------------------------------------------------
def clamp01(t: float) -> float:
    """Clamp scalar ``t`` to ``[0.0, 1.0]``."""
    v = float(t)
    if v <= 0.0:
        return 0.0
    if v >= 1.0:
        return 1.0
    return v


def smoothstep(t: float) -> float:
    """Hermite C1 smoothstep easing on ``[0.0, 1.0]``."""
    c = clamp01(t)
    return c * c * (3.0 - 2.0 * c)


def ease_out_cubic(t: float) -> float:
    """Cubic decelerating ease-out curve on ``[0.0, 1.0]``."""
    c = clamp01(t)
    inv = 1.0 - c
    return 1.0 - inv * inv * inv


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Overshoot spring ease-out curve on ``[0.0, 1.0]``."""
    c = clamp01(t)
    tm1 = c - 1.0
    return 1.0 + (overshoot + 1.0) * (tm1 * tm1 * tm1) + overshoot * (tm1 * tm1)


def _seed_phases(seed: int | str) -> tuple[float, float, float, float]:
    """Derive 4 deterministic phases in ``[0, 2*pi)`` from ``seed``."""
    digest = hashlib.sha256(str(seed).encode("utf-8")).digest()
    tau = 2.0 * math.pi
    p0 = (int.from_bytes(digest[0:4], "little") / 4294967296.0) * tau
    p1 = (int.from_bytes(digest[4:8], "little") / 4294967296.0) * tau
    p2 = (int.from_bytes(digest[8:12], "little") / 4294967296.0) * tau
    p3 = (int.from_bytes(digest[12:16], "little") / 4294967296.0) * tau
    return p0, p1, p2, p3


# ---------------------------------------------------------------------------
# 2. Continuous Kinetic Float & Entrance Spring Physics
# ---------------------------------------------------------------------------
def motion_float_transform(
    t_beat: float,
    seed: int | str,
    amp_x: float = 3.0,
    amp_y: float = 4.5,
    amp_deg: float = 0.55,
    amp_scale: float = 0.014,
    stop_motion_hz: float = 0.0,
) -> tuple[float, float, float, float]:
    """Return ``(dx, dy, d_angle_deg, scale_mul)`` for continuous organic float.

    Uses non-harmonic dual-frequency sinusoids with deterministic phase derived
    from ``seed``. Optional ``stop_motion_hz`` (e.g. ``12.0``) quantizes time
    to an editorial stop-motion cadence.
    """
    t_val = float(t_beat)
    if stop_motion_hz > 0.0:
        hz = float(stop_motion_hz)
        t_val = math.floor(t_val * hz) / hz

    ph0, ph1, ph2, ph3 = _seed_phases(seed)
    dx = float(amp_x) * (0.68 * math.sin(1.45 * t_val + ph0) + 0.32 * math.cos(0.79 * t_val + ph1))
    dy = float(amp_y) * (0.70 * math.cos(1.22 * t_val + ph1) + 0.30 * math.sin(0.67 * t_val + ph2))
    d_angle_deg = float(amp_deg) * (
        0.72 * math.sin(1.05 * t_val + ph2) + 0.28 * math.cos(0.58 * t_val + ph3)
    )
    scale_mul = 1.0 + float(amp_scale) * (
        0.65 * math.sin(1.30 * t_val + ph3) + 0.35 * math.cos(0.71 * t_val + ph0)
    )
    return dx, dy, d_angle_deg, scale_mul


def entrance_spring_params(
    t_beat: float,
    trigger_t: float,
    enter_dur: float = 0.34,
    style: str = "pop_up",
    scale_px: float = 1.0,
) -> tuple[float, float, float, float, float]:
    """Return ``(dx, dy, d_angle_deg, scale_mul, alpha_mul)`` for element entrance.

    Supported styles: ``pop_up``, ``slide_left``, ``slide_right``,
    ``slap_down``, ``cutout_pop``, ``stamp_slam``.
    """
    dt = float(t_beat) - float(trigger_t)
    dur = max(1e-4, float(enter_dur))
    st = str(style or "pop_up").lower().strip()
    sc = float(scale_px)

    if dt <= 0.0:
        if st == "slide_left":
            return 78.0 * sc, 0.0, 1.6, 0.96, 0.0
        if st == "slide_right":
            return -78.0 * sc, 0.0, -1.6, 0.96, 0.0
        if st == "slap_down":
            return 0.0, -44.0 * sc, 3.2, 1.24, 0.0
        if st == "cutout_pop":
            return 0.0, 22.0 * sc, 4.5, 0.58, 0.0
        if st == "stamp_slam":
            return 0.0, -18.0 * sc, -3.8, 1.42, 0.0
        return 0.0, 34.0 * sc, -2.2, 0.72, 0.0

    if dt >= dur:
        return 0.0, 0.0, 0.0, 1.0, 1.0

    p = clamp01(dt / dur)
    cub = ease_out_cubic(p)
    alpha_mul = clamp01(ease_out_cubic(clamp01(p / 0.35)))

    if st == "slide_left":
        back = ease_out_back(p, 1.15)
        return 78.0 * sc * (1.0 - back), 0.0, 1.6 * (1.0 - cub), 0.96 + 0.04 * cub, alpha_mul

    if st == "slide_right":
        back = ease_out_back(p, 1.15)
        return -78.0 * sc * (1.0 - back), 0.0, -1.6 * (1.0 - cub), 0.96 + 0.04 * cub, alpha_mul

    if st == "slap_down":
        back = ease_out_back(p, 1.35)
        return 0.0, -44.0 * sc * (1.0 - back), 3.2 * (1.0 - cub), 1.24 - 0.24 * back, alpha_mul

    if st == "cutout_pop":
        back = ease_out_back(p, 2.05)
        wobble = math.cos(p * math.pi * 1.5)
        return 0.0, 22.0 * sc * (1.0 - back), 4.5 * (1.0 - cub) * wobble, 0.58 + 0.42 * back, alpha_mul

    if st == "stamp_slam":
        back = ease_out_back(p, 1.10)
        slam_alpha = clamp01(p / 0.18)
        return 0.0, -18.0 * sc * (1.0 - cub), -3.8 * (1.0 - cub), 1.42 - 0.42 * back, slam_alpha

    # Default: pop_up
    back = ease_out_back(p, 1.60)
    return 0.0, 34.0 * sc * (1.0 - back), -2.2 * (1.0 - cub), 0.72 + 0.28 * back, alpha_mul


def apply_patch_transform(
    patch: Image.Image,
    d_angle_deg: float = 0.0,
    scale_mul: float = 1.0,
    alpha_mul: float = 1.0,
) -> Image.Image:
    """Apply rotation, uniform scale, and alpha attenuation to an RGBA patch.

    Performs a zero-copy identity bypass when parameters are within ``1e-3``
    of identity on an RGBA image.
    """
    ang = float(d_angle_deg)
    sc = float(scale_mul)
    al = clamp01(float(alpha_mul))

    if abs(ang) < 1e-3 and abs(sc - 1.0) < 1e-3 and abs(al - 1.0) < 1e-3:
        return patch if patch.mode == "RGBA" else patch.convert("RGBA")

    if al <= 0.001:
        return Image.new("RGBA", patch.size, (0, 0, 0, 0))

    out = patch if patch.mode == "RGBA" else patch.convert("RGBA")

    if abs(sc - 1.0) >= 1e-3:
        s_clamped = max(0.05, sc)
        nw = max(1, int(round(out.width * s_clamped)))
        nh = max(1, int(round(out.height * s_clamped)))
        out = out.resize((nw, nh), Image.Resampling.BICUBIC)

    if abs(ang) >= 1e-3:
        out = out.rotate(ang, resample=Image.Resampling.BICUBIC, expand=True)

    if al < 0.999:
        arr = np.asarray(out, dtype=np.uint8).copy()
        arr[..., 3] = np.clip(np.round(arr[..., 3].astype(np.float32) * al), 0, 255).astype(np.uint8)
        out = Image.fromarray(arr, mode="RGBA")

    return out


# ---------------------------------------------------------------------------
# 3. Specular Sheen, Highlighter Glint & Map Border Pulse
# ---------------------------------------------------------------------------
def apply_highlighter_glint(
    img: Image.Image,
    hl_rects: list[tuple[int, int, int, int]],
    t_beat: float,
) -> Image.Image:
    """Sweep a diagonal warm-white sheen across ``hl_rects`` every ``2.2s``."""
    if not hl_rects:
        return img

    cycle_s = 2.2
    phase = (float(t_beat) % cycle_s) / cycle_s
    if phase > 0.56:
        return img

    sweep_p = clamp01(phase / 0.56)
    center = -0.10 + 1.22 * sweep_p
    inv_bw = 1.0 / 0.14

    w_img, h_img = img.size
    is_rgba = img.mode == "RGBA"
    base = img if (img.mode in ("RGB", "RGBA")) else img.convert("RGBA")
    out_arr = np.asarray(base, dtype=np.uint8).copy()
    modified = False

    sheen_rgb = np.array([255.0, 250.0, 232.0], dtype=np.float32)

    for rect in hl_rects:
        x0 = max(0, int(rect[0]))
        y0 = max(0, int(rect[1]))
        x1 = min(w_img, int(rect[2]))
        y1 = min(h_img, int(rect[3]))
        rw = x1 - x0
        rh = y1 - y0
        if rw <= 1 or rh <= 1:
            continue

        xs = np.arange(rw, dtype=np.float32)[None, :]
        ys = np.arange(rh, dtype=np.float32)[:, None]
        denom = max(1.0, float(rw) + 0.45 * float(rh))
        u = (xs + 0.45 * ys) / denom
        band = np.exp(-(((u - center) * inv_bw) ** 2))
        if float(band.max()) < 0.02:
            continue

        roi = out_arr[y0:y1, x0:x1]
        strength = (band * 0.40)[..., None]
        if is_rgba or base.mode == "RGBA":
            alpha_mask = (roi[..., 3] > 8).astype(np.float32)[..., None]
            strength = strength * alpha_mask

        rgb_f = roi[..., :3].astype(np.float32)
        blended = rgb_f * (1.0 - strength) + sheen_rgb * strength
        roi[..., :3] = np.clip(np.round(blended), 0, 255).astype(np.uint8)
        modified = True

    if not modified:
        return img
    return Image.fromarray(out_arr, mode=base.mode)


def apply_pill_specular_sheen(
    patch: Image.Image,
    t_beat: float,
    seed: int | str = 0,
    cycle_s: float = 2.6,
) -> Image.Image:
    """Apply subtle Dymo tape specular shimmer + crisp LTR wipe cursor glint."""
    w, h = patch.size
    if w <= 1 or h <= 1:
        return patch

    rgba = patch if patch.mode == "RGBA" else patch.convert("RGBA")
    arr = np.asarray(rgba, dtype=np.uint8)
    alpha = arr[..., 3]
    opaque_mask = alpha > 24
    if not np.any(opaque_mask):
        return patch

    ph_off = (_seed_phases(seed)[0] / (2.0 * math.pi)) * 0.35
    cyc = max(0.25, float(cycle_s))
    t_val = float(t_beat)
    phase = ((t_val + ph_off) % cyc) / cyc

    has_sweep = phase <= 0.48
    col_opaque = opaque_mask.any(axis=0)
    rightmost = int(np.flatnonzero(col_opaque)[-1])
    has_cursor = (0.0 <= t_val < 0.32) and (4 <= rightmost < w - 4)

    if not has_sweep and not has_cursor:
        return patch

    out = arr.copy()
    rgb_f = out[..., :3].astype(np.float32)
    mask_f = opaque_mask.astype(np.float32)[..., None]

    if has_sweep:
        sweep_p = clamp01(phase / 0.48)
        center = -0.12 + 1.24 * sweep_p
        xs = np.arange(w, dtype=np.float32)[None, :]
        ys = np.arange(h, dtype=np.float32)[:, None]
        u = (xs + 0.38 * ys) / max(1.0, float(w) + 0.38 * float(h))
        band = np.exp(-(((u - center) / 0.085) ** 2)) * 0.18
        sheen = band[..., None] * mask_f
        spec_col = np.array([255.0, 253.0, 244.0], dtype=np.float32)
        rgb_f = rgb_f * (1.0 - sheen) + spec_col * sheen

    if has_cursor:
        x_lo = max(0, rightmost - 2)
        x_hi = min(w, rightmost + 1)
        c_mask = opaque_mask[:, x_lo:x_hi].astype(np.float32)[..., None]
        cursor_col = np.array([255.0, 250.0, 230.0], dtype=np.float32)
        rgb_f[:, x_lo:x_hi] = (
            rgb_f[:, x_lo:x_hi] * (1.0 - 0.52 * c_mask) + cursor_col * (0.52 * c_mask)
        )

    out[..., :3] = np.clip(np.round(rgb_f), 0, 255).astype(np.uint8)
    return Image.fromarray(out, mode="RGBA")


def compute_marching_dash_phase(t_beat: float, speed: float = 1.8) -> float:
    """Return normalized marching-dash phase in ``[0.0, 1.0)`` advancing at ``speed`` Hz."""
    return (float(t_beat) * float(speed)) % 1.0


def border_pulse_gain(t_beat: float, freq: float = 1.8) -> float:
    """Return sinusoidal border/tracer intensity multiplier in ``[0.80, 1.25]``."""
    osc = 0.5 + 0.5 * math.sin(2.0 * math.pi * float(freq) * float(t_beat))
    return 0.80 + 0.45 * osc


# ---------------------------------------------------------------------------
# 4. Custom Procedural Transitions (Selection, CPU NumPy & PyTorch CUDA)
# ---------------------------------------------------------------------------
def choose_procedural_transition(
    prev_beat: dict[str, Any] | None,
    cur_beat: dict[str, Any],
    beat_idx: int,
) -> tuple[str, float]:
    """Deterministically choose a non-canned procedural transition and duration.

    Never returns ``"fade"`` or ``"hard_cut"``. Returns ``("shutter_snap", 0.24)``
    when ``prev_beat is None``; otherwise selects among ``whip_pan_blur``,
    ``torn_paper_wipe``, ``zoom_punch_whoosh``, and ``card_slide`` based on beat
    world/region/scene context.
    """
    if prev_beat is None or int(beat_idx) <= 0:
        raw_d = cur_beat.get("transition_dur")
        dur = max(0.18, min(0.36, float(raw_d))) if raw_d is not None else 0.24
        return "shutter_snap", dur

    explicit = str(cur_beat.get("transition") or "").lower().strip()
    if explicit in _TWO_BEAT_TRANSITIONS:
        default_d = 0.34 if explicit == "torn_paper_wipe" else 0.28
        raw_d = cur_beat.get("transition_dur")
        dur = max(0.20, min(0.42, float(raw_d))) if raw_d is not None else default_d
        return explicit, dur

    prev_w = str(prev_beat.get("world") or "paper").lower().strip()
    cur_w = str(cur_beat.get("world") or "paper").lower().strip()
    prev_reg = str(prev_beat.get("region") or (prev_beat.get("camera") or {}).get("region") or "").lower().strip()
    cur_reg = str(cur_beat.get("region") or (cur_beat.get("camera") or {}).get("region") or "").lower().strip()
    prev_sc = str(prev_beat.get("scene_id") or "")
    cur_sc = str(cur_beat.get("scene_id") or "")

    # Title cards & year rewind cards always use a dynamic match-cut zoom burst
    if (
        cur_w == "title_card"
        or prev_w == "title_card"
        or bool(cur_beat.get("year_rewind") or cur_beat.get("year_rewind_card"))
    ):
        return "zoom_punch_whoosh", 0.28

    # Cross-world Map <-> Paper transitions alternate zoom burst & torn-paper wipe
    if {prev_w, cur_w} == {"paper", "map"}:
        if int(beat_idx) % 2 == 0:
            return "zoom_punch_whoosh", 0.28
        return "torn_paper_wipe", 0.34

    # Map -> Map transitions
    if prev_w == "map" and cur_w == "map":
        if prev_reg and cur_reg and prev_reg != cur_reg:
            return "whip_pan_blur", 0.28
        return ("zoom_punch_whoosh", 0.28) if (int(beat_idx) % 2 == 0) else ("card_slide", 0.28)

    # Paper -> Paper transitions
    is_heavy_media = bool(
        cur_beat.get("polaroid")
        or cur_beat.get("polaroids")
        or cur_beat.get("cutout")
        or cur_beat.get("schematic")
    )
    if is_heavy_media:
        return "whip_pan_blur", 0.28

    if prev_sc and cur_sc and prev_sc != cur_sc:
        return "torn_paper_wipe", 0.34

    return "card_slide", 0.28


def _normalize_kind(kind: str, has_prev: bool) -> str:
    k = str(kind or "").lower().strip()
    if not has_prev or k == "shutter_snap":
        return "shutter_snap"
    if k in _TWO_BEAT_TRANSITIONS:
        return k
    if k in ("fade", "dissolve", "cross_dissolve"):
        return "torn_paper_wipe"
    return "whip_pan_blur"


# ---------------------------------------------------------------------------
# 4A. NumPy CPU Transition Implementations (H, W, 3 uint8)
# ---------------------------------------------------------------------------
def _pil_scale_center_rgb(rgb: np.ndarray, zoom: float) -> np.ndarray:
    h, w = rgb.shape[:2]
    if abs(zoom - 1.0) < 1e-3:
        return rgb
    img = Image.fromarray(rgb, mode="RGB")
    if zoom > 1.0:
        cw = max(2, int(round(w / zoom)))
        ch = max(2, int(round(h / zoom)))
        x0 = (w - cw) // 2
        y0 = (h - ch) // 2
        return np.asarray(img.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.Resampling.BILINEAR), dtype=np.uint8)
    nw = max(2, int(round(w * zoom)))
    nh = max(2, int(round(h * zoom)))
    scaled = np.asarray(img.resize((nw, nh), Image.Resampling.BILINEAR), dtype=np.uint8)
    # Mirror-pad borders so zoom-out never shows harsh black bars
    pad_l = (w - nw) // 2
    pad_r = w - nw - pad_l
    pad_t = (h - nh) // 2
    pad_b = h - nh - pad_t
    return np.pad(scaled, ((pad_t, pad_b), (pad_l, pad_r), (0, 0)), mode="reflect")


def _box_blur_1d_numpy(img_f: np.ndarray, axis: int, radius: int) -> np.ndarray:
    if radius <= 0:
        return img_f
    if axis == 1:
        pad = np.pad(img_f, ((0, 0), (radius, radius), (0, 0)), mode="edge")
        zero = np.zeros((pad.shape[0], 1, pad.shape[2]), dtype=np.float64)
        cs = np.cumsum(np.concatenate([zero, pad.astype(np.float64)], axis=1), axis=1)
        out = (cs[:, 2 * radius + 1 :] - cs[:, : -2 * radius - 1]) / float(2 * radius + 1)
    else:
        pad = np.pad(img_f, ((radius, radius), (0, 0), (0, 0)), mode="edge")
        zero = np.zeros((1, pad.shape[1], pad.shape[2]), dtype=np.float64)
        cs = np.cumsum(np.concatenate([zero, pad.astype(np.float64)], axis=0), axis=0)
        out = (cs[2 * radius + 1 :, :] - cs[: -2 * radius - 1, :]) / float(2 * radius + 1)
    return out.astype(np.float32)


def _directional_blur_numpy(img_f: np.ndarray, ux: float, uy: float, blur_px: int) -> np.ndarray:
    """Apply a 1px-continuous 2-pass triangular directional blur (zero discrete echoes)."""
    if blur_px <= 1:
        return img_f
    r1 = max(1, int(round(blur_px * 0.55)))
    r2 = max(1, int(round(blur_px * 0.45)))
    axis = 1 if abs(ux) >= abs(uy) else 0
    return _box_blur_1d_numpy(_box_blur_1d_numpy(img_f, axis, r1), axis, r2)


def _whip_pan_blur_numpy(
    prev_rgb: np.ndarray,
    cur_rgb: np.ndarray,
    p: float,
    seed: int,
) -> np.ndarray:
    h, w = cur_rgb.shape[:2]
    dir_idx = int(seed) % 4
    dirs = ((-1.0, 0.0), (1.0, 0.0), (0.0, -1.0), (0.0, 1.0))
    ux, uy = dirs[dir_idx]
    prog = ease_out_cubic(p)
    comp = np.empty((h, w, 3), dtype=np.float32)

    if ux < 0.0:  # cur enters from right, pushes prev left
        split = max(0, min(w, int(round((1.0 - prog) * w))))
        if split > 0:
            comp[:, :split] = prev_rgb[:, w - split :]
        if split < w:
            comp[:, split:] = cur_rgb[:, : w - split]
    elif ux > 0.0:  # cur enters from left, pushes prev right
        split = max(0, min(w, int(round(prog * w))))
        if split > 0:
            comp[:, :split] = cur_rgb[:, w - split :]
        if split < w:
            comp[:, split:] = prev_rgb[:, : w - split]
    elif uy < 0.0:  # cur enters from bottom, pushes prev up
        split = max(0, min(h, int(round((1.0 - prog) * h))))
        if split > 0:
            comp[:split, :] = prev_rgb[h - split :, :]
        if split < h:
            comp[split:, :] = cur_rgb[: h - split, :]
    else:  # cur enters from top, pushes prev down
        split = max(0, min(h, int(round(prog * h))))
        if split > 0:
            comp[:split, :] = cur_rgb[h - split :, :]
        if split < h:
            comp[split:, :] = prev_rgb[: h - split, :]

    blur_amt = math.sin(math.pi * p) ** 1.15
    blur_px = int(round(0.018 * max(w, h) * blur_amt))
    comp = _directional_blur_numpy(comp, ux, uy, blur_px)
    return np.clip(np.round(comp), 0, 255).astype(np.uint8)


def _torn_paper_wipe_numpy(
    prev_rgb: np.ndarray,
    cur_rgb: np.ndarray,
    p: float,
    seed: int,
) -> np.ndarray:
    h, w = cur_rgb.shape[:2]
    ph0, ph1, ph2, ph3 = _seed_phases(seed)
    ltr = (int(seed) % 2) == 0

    xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    ys = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]

    deckle = (
        0.038 * np.sin(7.0 * ys + ph0)
        + 0.022 * np.sin(17.0 * ys + ph1)
        + 0.013 * np.cos(31.0 * ys + ph2)
        + 0.007 * np.sin(53.0 * ys + ph3)
    )
    slope = 0.12 * ys if ltr else -0.12 * ys
    prog = ease_out_cubic(p)
    if ltr:
        edge = -1.18 + 2.36 * prog + deckle + slope
        d = edge - xs
    else:
        edge = 1.18 - 2.36 * prog - deckle + slope
        d = xs - edge

    cur_mask = np.clip(d / 0.006, 0.0, 1.0)[..., None]

    # Cast shadow onto prev ahead of the advancing paper tear
    sh_band = np.clip(1.0 + d / 0.044, 0.0, 1.0) * (d <= 0.0)
    sh_gain = (1.0 - 0.50 * (sh_band * sh_band * (3.0 - 2.0 * sh_band)))[..., None]

    # #EAE8E1 torn paper fiber edge along newly revealed cur boundary
    fiber_band = np.clip(1.0 - d / 0.022, 0.0, 1.0) * (d > 0.0)
    fiber_tex = 0.78 + 0.22 * np.sin(47.0 * ys + 19.0 * xs)
    fiber_a = np.clip(fiber_band * fiber_tex * 0.88, 0.0, 1.0)[..., None]
    fiber_col = np.array(_TORN_PAPER_FIBER_RGB, dtype=np.float32)

    prev_f = prev_rgb.astype(np.float32) * sh_gain
    cur_f = cur_rgb.astype(np.float32) * (1.0 - fiber_a) + fiber_col * fiber_a
    out = prev_f * (1.0 - cur_mask) + cur_f * cur_mask
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _zoom_punch_whoosh_numpy(
    prev_rgb: np.ndarray,
    cur_rgb: np.ndarray,
    p: float,
) -> np.ndarray:
    h, w = cur_rgb.shape[:2]
    whoosh = math.sin(math.pi * p)
    z_prev = 1.0 + 0.26 * (p ** 1.15)
    z_cur = 0.86 + 0.14 * ease_out_back(p, 1.15)

    prev_z = _pil_scale_center_rgb(prev_rgb, z_prev).astype(np.float32)
    if whoosh > 0.06:
        pz_a = _pil_scale_center_rgb(prev_rgb, max(1.0, z_prev * (1.0 - 0.032 * whoosh))).astype(np.float32)
        pz_b = _pil_scale_center_rgb(prev_rgb, z_prev * (1.0 + 0.032 * whoosh)).astype(np.float32)
        prev_z = 0.50 * prev_z + 0.25 * pz_a + 0.25 * pz_b

    cur_z = _pil_scale_center_rgb(cur_rgb, z_cur).astype(np.float32)
    cross = smoothstep(clamp01((p - 0.12) / 0.72))
    comp = prev_z * (1.0 - cross) + cur_z * cross

    if whoosh > 0.01:
        xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
        ys = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
        r2 = np.clip((xs * xs + ys * ys) * 0.55, 0.0, 1.0)
        vig = (1.0 - 0.28 * whoosh * r2)[..., None]
        comp = comp * vig

    return np.clip(np.round(comp), 0, 255).astype(np.uint8)


def _card_slide_numpy(
    prev_rgb: np.ndarray,
    cur_rgb: np.ndarray,
    p: float,
    seed: int,
) -> np.ndarray:
    h, w = cur_rgb.shape[:2]
    from_right = (int(seed) % 2) == 0
    ep = ease_out_cubic(p)
    tilt_deg = (2.4 if from_right else -2.4) * (1.0 - ep)
    tilt_rad = math.radians(tilt_deg)
    dx = (1.0 - ep) * (2.05 if from_right else -2.05)
    dy = -0.06 * math.sin(math.pi * p)

    aspect = float(w) / max(1.0, float(h))
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    ys = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
    sx = (xs - dx) * aspect
    sy = ys - dy
    lx = (sx * cos_t + sy * sin_t) / aspect
    ly = -sx * sin_t + sy * cos_t

    # Cast shadow underneath sliding card
    sh_d = np.maximum(np.abs(lx + (0.045 if from_right else -0.045)), np.abs(ly - 0.045))
    sh_alpha = np.clip((1.07 - sh_d) / 0.08, 0.0, 1.0)
    prev_f = prev_rgb.astype(np.float32) * (1.0 - 0.45 * sh_alpha)[..., None]

    # Transform cur_rgb via PIL AFFINE in C-speed using pixel center mapping
    cx_p = w * 0.5
    cy_p = h * 0.5
    tx_px = dx * (w * 0.5)
    ty_px = dy * (h * 0.5)
    a = cos_t
    b = sin_t
    c = cx_p - a * (cx_p + tx_px) - b * (cy_p + ty_px)
    d = -sin_t
    e = cos_t
    f = cy_p - d * (cx_p + tx_px) - e * (cy_p + ty_px)
    cur_warped = Image.fromarray(cur_rgb, mode="RGB").transform(
        (w, h),
        Image.Transform.AFFINE,
        (a, b, c, d, e, f),
        resample=Image.Resampling.BILINEAR,
    )
    cur_f = np.asarray(cur_warped, dtype=np.float32)

    card_edge = np.maximum(np.abs(lx), np.abs(ly))
    card_a = np.clip((1.0 - card_edge) / 0.006, 0.0, 1.0)[..., None]
    rim_a = np.clip(1.0 - np.abs(card_edge - 0.992) / 0.010, 0.0, 1.0) * (card_edge <= 1.003)
    rim_col = np.array(_TORN_PAPER_FIBER_RGB, dtype=np.float32)
    cur_f = cur_f * (1.0 - 0.65 * rim_a[..., None]) + rim_col * (0.65 * rim_a[..., None])

    out = prev_f * (1.0 - card_a) + cur_f * card_a
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _shutter_snap_numpy(cur_rgb: np.ndarray, p: float) -> np.ndarray:
    h, w = cur_rgb.shape[:2]
    ep = ease_out_cubic(p)
    sp = ease_out_back(p, 1.35)
    z = 0.90 + 0.10 * sp
    cur_z = _pil_scale_center_rgb(cur_rgb, z).astype(np.float32)

    half_s = 0.18 + 0.84 * ep
    xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    ys = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
    edge_d = np.maximum(np.abs(xs) / half_s, np.abs(ys) / half_s)
    card_a = np.clip((1.0 - edge_d) / 0.010, 0.0, 1.0)[..., None]
    rim_a = (
        np.clip(1.0 - np.abs(edge_d - 0.985) / 0.015, 0.0, 1.0) * (edge_d <= 1.005)
    )[..., None]

    bg = np.full((h, w, 3), 20.0, dtype=np.float32)
    out = bg * (1.0 - card_a) + cur_z * card_a
    rim_col = np.array(_TORN_PAPER_FIBER_RGB, dtype=np.float32)
    rim_mix = rim_a * (0.65 * (1.0 - 0.5 * ep))
    out = out * (1.0 - rim_mix) + rim_col * rim_mix

    flash = 18.0 * max(0.0, 1.0 - p / 0.28)
    if flash > 0.05:
        out = out + flash * card_a

    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def compose_transition_numpy(
    prev_rgb: np.ndarray | None,
    cur_rgb: np.ndarray,
    kind: str,
    t_beat: float,
    trans_dur: float,
    seed: int = 0,
) -> np.ndarray:
    """Compose a procedural transition frame on CPU NumPy ``(H, W, 3) uint8``.

    Safely returns ``cur_rgb`` unchanged once ``t_beat >= trans_dur``.
    """
    dur = float(trans_dur)
    t_val = float(t_beat)
    if dur <= 1e-4 or t_val >= dur:
        return cur_rgb

    p = clamp01(t_val / dur)
    if p >= 1.0:
        return cur_rgb

    k = _normalize_kind(kind, has_prev=(prev_rgb is not None))
    if k == "shutter_snap" or prev_rgb is None:
        return _shutter_snap_numpy(cur_rgb, p)

    if prev_rgb.shape[:2] != cur_rgb.shape[:2]:
        h, w = cur_rgb.shape[:2]
        prev_rgb = np.asarray(
            Image.fromarray(prev_rgb, mode="RGB").resize((w, h), Image.Resampling.BILINEAR),
            dtype=np.uint8,
        )

    if k == "torn_paper_wipe":
        return _torn_paper_wipe_numpy(prev_rgb, cur_rgb, p, seed)
    if k == "zoom_punch_whoosh":
        return _zoom_punch_whoosh_numpy(prev_rgb, cur_rgb, p)
    if k == "card_slide":
        return _card_slide_numpy(prev_rgb, cur_rgb, p, seed)
    return _whip_pan_blur_numpy(prev_rgb, cur_rgb, p, seed)


# ---------------------------------------------------------------------------
# 4B. PyTorch CUDA/CPU Transition Implementations (1, 3, H, W float32 [0,1])
# ---------------------------------------------------------------------------
def _whip_pan_blur_torch(
    prev_t: "torch.Tensor",
    cur_t: "torch.Tensor",
    p: float,
    gx0: "torch.Tensor",
    gy0: "torch.Tensor",
    seed: int,
) -> "torch.Tensor":
    dir_idx = int(seed) % 4
    dirs = ((-1.0, 0.0), (1.0, 0.0), (0.0, -1.0), (0.0, 1.0))
    ux, uy = dirs[dir_idx]
    prog = ease_out_cubic(p)

    if ux < 0.0:  # cur enters from right
        split = 1.0 - 2.0 * prog
        gx_p = gx0 + 2.0 * prog
        gx_c = gx0 - 2.0 * (1.0 - prog)
        gy_p = gy0
        gy_c = gy0
        mask = ((gx0 - split) / 0.015).clamp(0.0, 1.0)
    elif ux > 0.0:  # cur enters from left
        split = -1.0 + 2.0 * prog
        gx_p = gx0 - 2.0 * prog
        gx_c = gx0 + 2.0 * (1.0 - prog)
        gy_p = gy0
        gy_c = gy0
        mask = ((split - gx0) / 0.015).clamp(0.0, 1.0)
    elif uy < 0.0:  # cur enters from bottom
        split = 1.0 - 2.0 * prog
        gx_p = gx0
        gx_c = gx0
        gy_p = gy0 + 2.0 * prog
        gy_c = gy0 - 2.0 * (1.0 - prog)
        mask = ((gy0 - split) / 0.015).clamp(0.0, 1.0)
    else:  # cur enters from top
        split = -1.0 + 2.0 * prog
        gx_p = gx0
        gx_c = gx0
        gy_p = gy0 - 2.0 * prog
        gy_c = gy0 + 2.0 * (1.0 - prog)
        mask = ((split - gy0) / 0.015).clamp(0.0, 1.0)

    grid_p = torch.stack([gx_p, gy_p], dim=-1).unsqueeze(0)
    grid_c = torch.stack([gx_c, gy_c], dim=-1).unsqueeze(0)
    p_s = F.grid_sample(prev_t, grid_p, mode="bilinear", padding_mode="border", align_corners=True)
    c_s = F.grid_sample(cur_t, grid_c, mode="bilinear", padding_mode="border", align_corners=True)
    m = mask.unsqueeze(0).unsqueeze(0)
    comp = p_s * (1.0 - m) + c_s * m

    blur_amt = math.sin(math.pi * p) ** 1.15
    half_span = 0.026 * blur_amt
    if half_span > 0.0015:
        n_half = 12  # 25 dense taps, <= 2.8px spacing even at 2K
        raw_w = [0.54 + 0.46 * math.cos(math.pi * (i / float(n_half + 1))) for i in range(-n_half, n_half + 1)]
        w_sum = sum(raw_w)
        center_wt = raw_w[n_half] / w_sum
        acc = comp * center_wt
        for idx_i, rw in enumerate(raw_w):
            k = idx_i - n_half
            if k == 0:
                continue
            off = (k / float(n_half)) * half_span
            wt = rw / w_sum
            b_grid = torch.stack([gx0 - ux * off, gy0 - uy * off], dim=-1).unsqueeze(0)
            acc = acc + F.grid_sample(comp, b_grid, mode="bilinear", padding_mode="border", align_corners=True) * wt
        comp = acc

    return comp.clamp(0.0, 1.0)


def _torn_paper_wipe_torch(
    prev_t: "torch.Tensor",
    cur_t: "torch.Tensor",
    p: float,
    gx0: "torch.Tensor",
    gy0: "torch.Tensor",
    seed: int,
) -> "torch.Tensor":
    ph0, ph1, ph2, ph3 = _seed_phases(seed)
    ltr = (int(seed) % 2) == 0

    deckle = (
        0.038 * torch.sin(7.0 * gy0 + ph0)
        + 0.022 * torch.sin(17.0 * gy0 + ph1)
        + 0.013 * torch.cos(31.0 * gy0 + ph2)
        + 0.007 * torch.sin(53.0 * gy0 + ph3)
    )
    slope = (0.12 * gy0) if ltr else (-0.12 * gy0)
    prog = ease_out_cubic(p)
    if ltr:
        edge = -1.18 + 2.36 * prog + deckle + slope
        d = edge - gx0
    else:
        edge = 1.18 - 2.36 * prog - deckle + slope
        d = gx0 - edge

    cur_mask = (d / 0.006).clamp(0.0, 1.0).unsqueeze(0).unsqueeze(0)

    sh_band = (1.0 + d / 0.044).clamp(0.0, 1.0) * (d <= 0.0).to(cur_t.dtype)
    sh_smooth = sh_band * sh_band * (3.0 - 2.0 * sh_band)
    sh_gain = (1.0 - 0.50 * sh_smooth).unsqueeze(0).unsqueeze(0)

    fiber_band = (1.0 - d / 0.022).clamp(0.0, 1.0) * (d > 0.0).to(cur_t.dtype)
    fiber_tex = 0.78 + 0.22 * torch.sin(47.0 * gy0 + 19.0 * gx0)
    fiber_a = (fiber_band * fiber_tex * 0.88).clamp(0.0, 1.0).unsqueeze(0).unsqueeze(0)
    fiber_col = cur_t.new_tensor(_TORN_PAPER_FIBER_F).view(1, 3, 1, 1)

    prev_shaded = prev_t * sh_gain
    cur_edged = cur_t * (1.0 - fiber_a) + fiber_col * fiber_a
    return (prev_shaded * (1.0 - cur_mask) + cur_edged * cur_mask).clamp(0.0, 1.0)


def _zoom_punch_whoosh_torch(
    prev_t: "torch.Tensor",
    cur_t: "torch.Tensor",
    p: float,
    gx0: "torch.Tensor",
    gy0: "torch.Tensor",
) -> "torch.Tensor":
    whoosh = math.sin(math.pi * p)
    z_prev = 1.0 + 0.26 * (p ** 1.15)
    z_cur = 0.86 + 0.14 * ease_out_back(p, 1.15)

    g_prev = torch.stack([gx0 / z_prev, gy0 / z_prev], dim=-1).unsqueeze(0)
    prev_z = F.grid_sample(prev_t, g_prev, mode="bilinear", padding_mode="border", align_corners=True)
    if whoosh > 0.06:
        z_a = max(1.0, z_prev * (1.0 - 0.032 * whoosh))
        z_b = z_prev * (1.0 + 0.032 * whoosh)
        p_a = F.grid_sample(
            prev_t, torch.stack([gx0 / z_a, gy0 / z_a], dim=-1).unsqueeze(0),
            mode="bilinear", padding_mode="border", align_corners=True,
        )
        p_b = F.grid_sample(
            prev_t, torch.stack([gx0 / z_b, gy0 / z_b], dim=-1).unsqueeze(0),
            mode="bilinear", padding_mode="border", align_corners=True,
        )
        prev_z = 0.50 * prev_z + 0.25 * p_a + 0.25 * p_b

    pad_cur = "reflection" if z_cur < 1.0 else "border"
    g_cur = torch.stack([gx0 / z_cur, gy0 / z_cur], dim=-1).unsqueeze(0)
    cur_z = F.grid_sample(cur_t, g_cur, mode="bilinear", padding_mode=pad_cur, align_corners=True)

    cross = smoothstep(clamp01((p - 0.12) / 0.72))
    comp = prev_z * (1.0 - cross) + cur_z * cross

    if whoosh > 0.01:
        r2 = ((gx0 * gx0 + gy0 * gy0) * 0.55).clamp(0.0, 1.0)
        vig = (1.0 - 0.28 * whoosh * r2).unsqueeze(0).unsqueeze(0)
        comp = comp * vig

    return comp.clamp(0.0, 1.0)


def _card_slide_torch(
    prev_t: "torch.Tensor",
    cur_t: "torch.Tensor",
    p: float,
    gx0: "torch.Tensor",
    gy0: "torch.Tensor",
    seed: int,
) -> "torch.Tensor":
    from_right = (int(seed) % 2) == 0
    ep = ease_out_cubic(p)
    tilt_deg = (2.4 if from_right else -2.4) * (1.0 - ep)
    tilt_rad = math.radians(tilt_deg)
    dx = (1.0 - ep) * (2.05 if from_right else -2.05)
    dy = -0.06 * math.sin(math.pi * p)

    h, w = int(cur_t.shape[2]), int(cur_t.shape[3])
    aspect = float(w) / max(1.0, float(h))
    cos_t = math.cos(tilt_rad)
    sin_t = math.sin(tilt_rad)

    sx = (gx0 - dx) * aspect
    sy = gy0 - dy
    lx = (sx * cos_t + sy * sin_t) / aspect
    ly = -sx * sin_t + sy * cos_t

    cur_warped = F.grid_sample(
        cur_t,
        torch.stack([lx, ly], dim=-1).unsqueeze(0),
        mode="bilinear",
        padding_mode="border",
        align_corners=True,
    )

    sh_d = torch.maximum(torch.abs(lx + (0.045 if from_right else -0.045)), torch.abs(ly - 0.045))
    sh_alpha = ((1.07 - sh_d) / 0.08).clamp(0.0, 1.0).unsqueeze(0).unsqueeze(0)
    prev_shaded = prev_t * (1.0 - 0.45 * sh_alpha)

    card_edge = torch.maximum(torch.abs(lx), torch.abs(ly))
    card_a = ((1.0 - card_edge) / 0.006).clamp(0.0, 1.0).unsqueeze(0).unsqueeze(0)
    rim_a = (
        (1.0 - torch.abs(card_edge - 0.992) / 0.010).clamp(0.0, 1.0)
        * (card_edge <= 1.003).to(cur_t.dtype)
    ).unsqueeze(0).unsqueeze(0)
    rim_col = cur_t.new_tensor(_TORN_PAPER_FIBER_F).view(1, 3, 1, 1)
    cur_rimmed = cur_warped * (1.0 - 0.65 * rim_a) + rim_col * (0.65 * rim_a)

    return (prev_shaded * (1.0 - card_a) + cur_rimmed * card_a).clamp(0.0, 1.0)


def _shutter_snap_torch(
    cur_t: "torch.Tensor",
    p: float,
    gx0: "torch.Tensor",
    gy0: "torch.Tensor",
) -> "torch.Tensor":
    ep = ease_out_cubic(p)
    sp = ease_out_back(p, 1.35)
    z = 0.90 + 0.10 * sp
    pad_m = "reflection" if z < 1.0 else "border"
    cur_z = F.grid_sample(
        cur_t,
        torch.stack([gx0 / z, gy0 / z], dim=-1).unsqueeze(0),
        mode="bilinear",
        padding_mode=pad_m,
        align_corners=True,
    )

    half_s = 0.18 + 0.84 * ep
    edge_d = torch.maximum(torch.abs(gx0) / half_s, torch.abs(gy0) / half_s)
    card_a = ((1.0 - edge_d) / 0.010).clamp(0.0, 1.0).unsqueeze(0).unsqueeze(0)
    rim_a = (
        (1.0 - torch.abs(edge_d - 0.985) / 0.015).clamp(0.0, 1.0)
        * (edge_d <= 1.005).to(cur_t.dtype)
    ).unsqueeze(0).unsqueeze(0)

    bg = torch.full_like(cur_t, _SHUTTER_BACKDROP_F)
    out = bg * (1.0 - card_a) + cur_z * card_a
    rim_col = cur_t.new_tensor(_TORN_PAPER_FIBER_F).view(1, 3, 1, 1)
    rim_mix = rim_a * (0.65 * (1.0 - 0.5 * ep))
    out = out * (1.0 - rim_mix) + rim_col * rim_mix

    flash = (18.0 / 255.0) * max(0.0, 1.0 - p / 0.28)
    if flash > 0.0005:
        out = out + flash * card_a

    return out.clamp(0.0, 1.0)


def compose_transition_torch(
    prev_t: "torch.Tensor | None",
    cur_t: "torch.Tensor",
    kind: str,
    t_beat: float,
    trans_dur: float,
    gx0: "torch.Tensor",
    gy0: "torch.Tensor",
    seed: int = 0,
) -> "torch.Tensor":
    """Compose a procedural transition frame on PyTorch CUDA/CPU ``(1, 3, H, W)``.

    Zero CPU copy; returns ``cur_t`` directly when ``t_beat >= trans_dur``.
    """
    if not _HAS_TORCH:  # pragma: no cover
        raise RuntimeError("PyTorch is required for compose_transition_torch.")

    dur = float(trans_dur)
    t_val = float(t_beat)
    if dur <= 1e-4 or t_val >= dur:
        return cur_t

    p = clamp01(t_val / dur)
    if p >= 1.0:
        return cur_t

    if gx0.dim() == 3:
        gx0 = gx0.squeeze(0)
    if gy0.dim() == 3:
        gy0 = gy0.squeeze(0)

    k = _normalize_kind(kind, has_prev=(prev_t is not None))
    if k == "shutter_snap" or prev_t is None:
        return _shutter_snap_torch(cur_t, p, gx0, gy0)
    if k == "torn_paper_wipe":
        return _torn_paper_wipe_torch(prev_t, cur_t, p, gx0, gy0, seed)
    if k == "zoom_punch_whoosh":
        return _zoom_punch_whoosh_torch(prev_t, cur_t, p, gx0, gy0)
    if k == "card_slide":
        return _card_slide_torch(prev_t, cur_t, p, gx0, gy0, seed)
    return _whip_pan_blur_torch(prev_t, cur_t, p, gx0, gy0, seed)
