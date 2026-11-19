"""Forensic Aviation Telemetry HUD v2 (30fps RGBA PIL Renderer, Colab-Portable).

Standalone, zero-relative-import module providing 10 animated 30fps RGBA PIL HUD
widgets + unified `render_forensic_hud_v2(...)` entrypoint for `Hồ Sơ Kỳ Lạ`
and aviation forensic explainer productions (`Option A / B / C` at 2K 16:9,
1080p, or 9:16 portrait).

Can be imported directly from `sys.fx_warehouse.hud_forensic_v2` or bundled /
inlined inside Colab remote worker scripts without package dependencies beyond
Python stdlib and `Pillow`.
"""
from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Calibrated 2K Map Anchors for `S4_B01.png` (2560x1440 NASA/ISS Attica Night)
# Verified directly against pixel luminance & coastal geometry:
# - Athens metro hub: bright radial city grid core around (675, 830)
# - Grammatiko hills: mainland NE Attica ridge north of Marathon Bay (1115, 365)
# - Aegean corridor: open South Euboean Gulf / Aegean approach water (1540, 560)
# ---------------------------------------------------------------------------
VERIFIED_MAP_ANCHORS_2K: dict[str, tuple[int, int]] = {
    "athens": (675, 830),
    "grammatiko": (1115, 365),
    "aegean_corridor": (1540, 560),
    "aegean_entry": (1860, 740),
    "radar_center": (895, 598),
    "avoidance_ctrl": (1015, 675),
}

FORENSIC_HUD_V2_CATALOG: dict[str, str] = {
    "alt_pressure_divergence": "Dual curve: ship altitude 10.400M vs cabin pressure drop with 3.600M & 4.300M thresholds.",
    "dual_horn_pulse": "Non-overlapping 2.0Hz (250ms ON / 250ms OFF) dual-burst comparator for Takeoff Config vs Cabin Alt.",
    "hypoxia_tuc_meter": "CO2 clearance vs SpO2 drop paradox with animated 30-90s TUC survival bar.",
    "swiss_cheese_align": "4 sequential defense slices sliding into alignment as red laser pierces through.",
    "classic_vs_ng_compare": "1997 Boeing 737 Classic (1 dim P5 lamp) vs 2006 Post-Helios (2 separated eye-level lamps).",
    "fuel_avoidance_vector": "Dual fuel bars dropping to 0% (ENG 1 11:50, ENG 2 12:00) + Athens avoidance vector to Grammatiko 12:04.",
    "calibrated_radar_overlay": "Dynamic Bezier trajectory & radar sweep anchored to calibrated Athens/Grammatiko/Aegean coords.",
    "lemmino_hairline_hud": "Ultra-clean 1px hairline forensic typography/timeline for LEMMiNO Noir (Option B).",
    "chapter_title_bumper": "Cinematic minimalist 3.0s dossier chapter title card (CH02..CH10 / Style 01..04).",
    "man_auto_switch": "Overhead P5 cabin pressure selector schematic (AUTO -> MAN) showing manual lock and open outflow valve.",
}

_HUD_ALIASES: dict[str, str] = {
    "render_alt_pressure_divergence": "alt_pressure_divergence",
    "alt_pressure": "alt_pressure_divergence",
    "render_dual_horn_pulse": "dual_horn_pulse",
    "dual_horn": "dual_horn_pulse",
    "render_hypoxia_tuc_meter": "hypoxia_tuc_meter",
    "hypoxia_tuc": "hypoxia_tuc_meter",
    "render_swiss_cheese_align": "swiss_cheese_align",
    "swiss_cheese": "swiss_cheese_align",
    "render_classic_vs_ng_compare": "classic_vs_ng_compare",
    "classic_vs_ng": "classic_vs_ng_compare",
    "render_fuel_avoidance_vector": "fuel_avoidance_vector",
    "fuel_avoidance": "fuel_avoidance_vector",
    "render_calibrated_radar_overlay": "calibrated_radar_overlay",
    "calibrated_radar": "calibrated_radar_overlay",
    "render_lemmino_hairline_hud": "lemmino_hairline_hud",
    "lemmino_hairline": "lemmino_hairline_hud",
    "render_chapter_title_bumper": "chapter_title_bumper",
    "chapter_bumper": "chapter_title_bumper",
    "render_man_auto_switch": "man_auto_switch",
    "man_auto": "man_auto_switch",
}

_CUSTOM_FONT_DIR: Path | None = None
_FONT_PATH_CACHE: dict[str, str | None] = {}
_FONT_CACHE: dict[tuple[int, str], ImageFont.FreeTypeFont] = {}


def set_font_dir(font_dir: str | Path | None) -> None:
    """Optionally override font search directory (useful inside Colab bundles)."""
    global _CUSTOM_FONT_DIR
    _CUSTOM_FONT_DIR = Path(font_dir) if font_dir else None
    _FONT_PATH_CACHE.clear()
    _FONT_CACHE.clear()


def _resolve_font_path(style: str) -> str | None:
    if style in _FONT_PATH_CACHE:
        return _FONT_PATH_CACHE[style]
    filenames = {
        # NotoSans renders uppercase Vietnamese stacked diacritics (Ồ/Ổ/Ổ) cleanly without NotoMono glyph defects
        "mono": ("NotoSans-Regular.ttf", "NotoSans-Bold.ttf", "DejaVuSans.ttf"),
        "reg": ("NotoSans-Regular.ttf", "DejaVuSans.ttf"),
        "bold": ("NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
    }.get(style, ("NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf"))

    search_dirs: list[Path] = []
    if _CUSTOM_FONT_DIR is not None:
        search_dirs.append(_CUSTOM_FONT_DIR)
    env_dir = os.environ.get("VP_FONT_DIR")
    if env_dir:
        search_dirs.append(Path(env_dir))
    try:
        here = Path(__file__).resolve().parent
        search_dirs.extend([here / "fonts", here.parent / "assets" / "fonts"])
    except NameError:
        pass
    search_dirs.extend([
        Path.cwd() / "fonts",
        Path("/dev/shm/vp_hskl_full_fx_2k/fonts"),
        Path.home() / ".local/share/fonts",
        Path("/usr/share/fonts/truetype/noto"),
        Path("/usr/share/fonts/truetype/dejavu"),
    ])

    chosen: str | None = None
    for fname in filenames:
        for d in search_dirs:
            cand = d / fname
            if cand.is_file():
                chosen = str(cand)
                break
        if chosen:
            break

    if chosen is None:
        for root in (Path.home() / ".local/share/fonts", Path("/usr/share/fonts")):
            if not root.is_dir():
                continue
            for fname in filenames:
                hit = next(root.rglob(fname), None)
                if hit is not None and hit.is_file():
                    chosen = str(hit)
                    break
            if chosen:
                break

    _FONT_PATH_CACHE[style] = chosen
    return chosen


def _get_font(size: int, style: str = "bold") -> ImageFont.FreeTypeFont:
    sz = max(10, int(round(size)))
    key = (sz, style)
    if key not in _FONT_CACHE:
        path = _resolve_font_path(style)
        _FONT_CACHE[key] = ImageFont.truetype(path, sz) if path else ImageFont.load_default()
    return _FONT_CACHE[key]


def _ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def _ease_in_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 4.0 * x * x * x if x < 0.5 else 1.0 - ((-2.0 * x + 2.0) ** 3) / 2.0


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _norm_variant(variant: str | None) -> str:
    v = str(variant or "A").strip().upper()
    return v[0] if v and v[0] in ("A", "B", "C") else "A"


def _theme(variant: str) -> dict[str, Any]:
    v = _norm_variant(variant)
    if v == "B":
        return {
            "variant": "B",
            "card_bg": (7, 9, 13, 198),
            "sub_bg": (11, 14, 20, 186),
            "border": (232, 223, 200, 145),
            "border_w": 1,
            "radius": 6,
            "crimson": (205, 58, 52, 245),
            "cyan": (132, 208, 224, 235),
            "brass": (212, 168, 72, 245),
            "mint": (94, 198, 158, 240),
            "white": (244, 246, 248, 255),
            "parchment": (232, 223, 200, 245),
            "muted": (166, 176, 190, 235),
            "grid": (232, 223, 200, 28),
        }
    if v == "C":
        return {
            "variant": "C",
            "card_bg": (10, 12, 18, 238),
            "sub_bg": (16, 20, 30, 240),
            "border": (245, 184, 56, 225),
            "border_w": 3,
            "radius": 10,
            "crimson": (235, 54, 48, 255),
            "cyan": (42, 218, 255, 255),
            "brass": (245, 184, 56, 255),
            "mint": (52, 220, 158, 255),
            "white": (250, 251, 253, 255),
            "parchment": (242, 232, 206, 255),
            "muted": (184, 196, 214, 245),
            "grid": (255, 255, 255, 36),
        }
    return {
        "variant": "A",
        "card_bg": (10, 14, 22, 226),
        "sub_bg": (14, 20, 32, 228),
        "border": (205, 52, 48, 215),
        "border_w": 2,
        "radius": 14,
        "crimson": (205, 52, 48, 255),
        "cyan": (32, 212, 248, 255),
        "brass": (212, 168, 72, 255),
        "mint": (52, 211, 153, 255),
        "white": (246, 248, 250, 255),
        "parchment": (232, 223, 200, 255),
        "muted": (182, 194, 210, 245),
        "grid": (255, 255, 255, 32),
    }


def _layout_ctx(width: int, height: int) -> dict[str, Any]:
    w = max(320, int(width))
    h = max(320, int(height))
    portrait = h > w
    s = (w / 1440.0 * 0.90) if portrait else min(w / 2560.0, h / 1440.0)
    margin_x = max(20, int(round(64 * s)))
    right_margin_x = max(20, int(round(190 * s))) if portrait else margin_x
    top_safe = max(72, int(round(h * (0.105 if not portrait else 0.115))))
    bottom_safe = int(round(h * (0.836 if not portrait else 0.785)))
    return {
        "w": w,
        "h": h,
        "s": s,
        "portrait": portrait,
        "margin_x": margin_x,
        "right_margin_x": right_margin_x,
        "top_safe": top_safe,
        "bottom_safe": bottom_safe,
        "max_card_w": w - margin_x - right_margin_x,
        "px": lambda val: int(round(val * s)),
        "lw": lambda val: max(1, int(round(val * s))),
    }


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    tb = draw.textbbox((0, 0), text, font=font)
    return tb[0], tb[1], tb[2] - tb[0], tb[3] - tb[1]


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_w: int,
    base_size: int,
    style: str = "bold",
    min_size: int = 12,
) -> ImageFont.FreeTypeFont:
    sz = max(min_size, int(round(base_size)))
    while sz > min_size:
        f = _get_font(sz, style)
        _, _, tw, _ = _text_size(draw, text, f)
        if tw <= max_w:
            return f
        sz -= max(1, sz // 14)
    return _get_font(min_size, style)


def _draw_text_top(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    shadow: bool = False,
) -> tuple[int, int]:
    """Draw text using exact top-left bounding box alignment so Vietnamese diacritics never clip."""
    bx0, by0, tw, th = _text_size(draw, text, font)
    tx, ty = int(round(x - bx0)), int(round(y - by0))
    if shadow:
        draw.text((tx + 2, ty + 2), text, font=font, fill=(0, 0, 0, min(200, fill[3])))
    draw.text((tx, ty), text, font=font, fill=fill)
    return tw, th


def _draw_pill(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    bg: tuple[int, int, int, int],
    fg: tuple[int, int, int, int],
    outline: tuple[int, int, int, int] | None = None,
    pad_x: int = 16,
    pad_y: int = 9,
    radius: int = 8,
    outline_w: int = 2,
) -> tuple[int, int]:
    bx0, by0, tw, th = _text_size(draw, text, font)
    pw, ph = tw + pad_x * 2, th + pad_y * 2
    draw.rounded_rectangle([x, y, x + pw, y + ph], radius=radius, fill=bg, outline=outline, width=outline_w if outline else 0)
    draw.text((x + pad_x - bx0, y + pad_y - by0), text, font=font, fill=fg)
    return pw, ph


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int, max_lines: int = 3) -> list[str]:
    words = text.strip().split()
    if not words:
        return []
    _, _, full_w, _ = _text_size(draw, " ".join(words), font)
    if full_w <= max_w:
        return [" ".join(words)]
    # When text fits cleanly on 2 balanced lines, pick the split that minimizes line imbalance
    if max_lines >= 2 and len(words) >= 4:
        best_split: tuple[int, str, str] | None = None
        for idx in range(1, len(words)):
            l1 = " ".join(words[:idx])
            l2 = " ".join(words[idx:])
            w1 = _text_size(draw, l1, font)[2]
            w2 = _text_size(draw, l2, font)[2]
            if w1 <= max_w and w2 <= max_w:
                score = max(w1, w2) + abs(w1 - w2)
                if best_split is None or score < best_split[0]:
                    best_split = (score, l1, l2)
        if best_split is not None:
            return [best_split[1], best_split[2]]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        cand = f"{cur} {w}"
        _, _, cw, _ = _text_size(draw, cand, font)
        if cw <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = w
            if len(lines) >= max_lines:
                break
    if len(lines) < max_lines:
        lines.append(cur)
    return lines[:max_lines]


def _draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    p0: tuple[float, float],
    p1: tuple[float, float],
    fill: tuple[int, int, int, int],
    width: int = 2,
    dash: float = 12.0,
    gap: float = 8.0,
) -> None:
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    dist = math.hypot(dx, dy)
    if dist < 1.0:
        return
    ux, uy = dx / dist, dy / dist
    pos = 0.0
    while pos < dist:
        end = min(dist, pos + dash)
        draw.line(
            [(p0[0] + ux * pos, p0[1] + uy * pos), (p0[0] + ux * end, p0[1] + uy * end)],
            fill=fill,
            width=width,
        )
        pos += dash + gap


def _place_card_xy(ctx: dict[str, Any], pw: int, ph: int, spec: dict[str, Any], centered: bool = False) -> tuple[int, int]:
    align = str(spec.get("align", "bottom_center" if centered else "bottom_left")).lower()
    mx = ctx["margin_x"]
    rmx = ctx.get("right_margin_x", mx)
    if "center" in align:
        x0 = (mx + max(0, (ctx["w"] - mx - rmx - pw) // 2)) if ctx["portrait"] else (ctx["w"] - pw) // 2
    elif "right" in align:
        x0 = ctx["w"] - rmx - pw
    else:
        x0 = mx
    if "top" in align:
        y0 = ctx["top_safe"]
    elif align == "center":
        y0 = max(ctx["top_safe"], (ctx["h"] - ph) // 2)
    else:
        y0 = ctx["bottom_safe"] - ph
    x0 = int(spec.get("x0", x0))
    y0 = int(spec.get("y0", y0))
    max_x0 = ctx["w"] - pw - (rmx if ctx["portrait"] else 8)
    return max(8, min(max_x0, x0)), max(8, min(ctx["h"] - ph - 8, y0))


def _apply_slide_y(ctx: dict[str, Any], y0: int, ph: int, slide_dy: int, spec: dict[str, Any]) -> int:
    """Apply slide offset while keeping portrait cards clear of bottom caption safe-zone."""
    y0_slide = y0 + slide_dy
    if ctx["portrait"] and "y0" not in spec:
        return min(y0_slide, ctx["bottom_safe"] - ph)
    return y0_slide


def _draw_card_shell(
    draw: ImageDraw.ImageDraw,
    x0: int,
    y0: int,
    pw: int,
    ph: int,
    th: dict[str, Any],
    ctx: dict[str, Any],
    accent: tuple[int, int, int, int] | None = None,
) -> None:
    acc = accent or th["border"]
    rad = ctx["px"](th["radius"])
    bw = max(1, ctx["lw"](th["border_w"]))
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=rad, fill=th["card_bg"], outline=acc, width=bw)
    if th["variant"] == "C":
        tick = ctx["px"](18)
        lw_c = max(2, ctx["lw"](4))
        for cx, cy, sx_d, sy_d in (
            (x0, y0, 1, 1),
            (x0 + pw, y0, -1, 1),
            (x0, y0 + ph, 1, -1),
            (x0 + pw, y0 + ph, -1, -1),
        ):
            draw.line([(cx, cy), (cx + sx_d * tick, cy)], fill=th["brass"], width=lw_c)
            draw.line([(cx, cy), (cx, cy + sy_d * tick)], fill=th["brass"], width=lw_c)
    elif th["variant"] == "A":
        bar_w = max(4, ctx["px"](6))
        draw.rounded_rectangle([x0, y0 + ctx["px"](12), x0 + bar_w, y0 + ph - ctx["px"](12)], radius=2, fill=acc)


# ---------------------------------------------------------------------------
# 1. Altitude vs Cabin Pressure Divergence
# ---------------------------------------------------------------------------

def render_alt_pressure_divergence(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render animated dual divergence curve: ship altitude 10.400M vs cabin pressure drop."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    dur_s = max(0.25, float(dur))
    prog = _ease_out_cubic(_clamp01(t_beat / min(dur_s * 0.72, 1.8)))
    slide = _ease_out_cubic(_clamp01(t_beat / 0.28))

    pw = ctx["max_card_w"] if ctx["portrait"] else min(px(1100), ctx["max_card_w"])
    ph = px(375 if not ctx["portrait"] else 430)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec)
    y0 = _apply_slide_y(ctx, y0, ph, int(round((1.0 - slide) * px(28))), spec)

    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=th["crimson"])

    pad = px(26)
    badge_txt = str(spec.get("status_badge", "MẤT ÁP SUẤT CABIN"))
    f_badge = _fit_font(d, badge_txt, pw // 3, px(20), "bold", 11)
    bx0, by0, btw, bth = _text_size(d, badge_txt, f_badge)
    bw_p = btw + px(26)
    badge_x = x0 + pw - pad - bw_p
    badge_y = y0 + px(16)
    _draw_pill(d, badge_x, badge_y, badge_txt, f_badge, th["crimson"], th["white"], radius=px(6))

    kicker = str(spec.get("kicker", "PHÂN TÍCH HỘP ĐEN FDR • ĐỘ CAO TÀU vs ÁP SUẤT CABIN"))
    f_kick = _fit_font(d, kicker, max(120, badge_x - (x0 + pad) - px(20)), px(22), "mono", 12)
    _draw_text_top(d, x0 + pad, y0 + px(22), kicker, f_kick, th["brass"])

    hdr_y = y0 + px(64)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=max(1, lw(1)))

    # Split: left plot + right live numeric readouts
    right_w = px(350) if not ctx["portrait"] else int(pw * 0.35)
    plot_x0 = x0 + pad + px(12)
    plot_x1 = x0 + pw - pad - right_w - px(22)
    plot_y0 = hdr_y + px(18)
    plot_y1 = y0 + ph - px(38)
    plot_w = max(80, plot_x1 - plot_x0)
    plot_h = max(80, plot_y1 - plot_y0)

    d.rounded_rectangle([plot_x0, plot_y0, plot_x1, plot_y1], radius=px(8), fill=th["sub_bg"], outline=th["grid"], width=1)

    # Vertical positions inside plot (y increases downward):
    # Top = 10.400M, 4.300M mask drop = 40%, 3.600M horn = 66%, 0M ground = 88%
    y_ground = plot_y0 + int(plot_h * 0.88)
    y_horn = plot_y0 + int(plot_h * 0.66)
    y_mask = plot_y0 + int(plot_h * 0.40)
    y_cruise = plot_y0 + int(plot_h * 0.16)

    for gy in (y_cruise, y_mask, y_horn, y_ground):
        d.line([(plot_x0 + px(8), gy), (plot_x1 - px(8), gy)], fill=(255, 255, 255, 22), width=1)

    # Threshold dashed lines
    _draw_dashed_line(d, (plot_x0 + px(8), y_horn), (plot_x1 - px(8), y_horn), th["brass"], width=max(1, lw(2)), dash=px(10), gap=px(6))
    _draw_dashed_line(d, (plot_x0 + px(8), y_mask), (plot_x1 - px(8), y_mask), th["crimson"], width=max(1, lw(2)), dash=px(10), gap=px(6))

    # Compute dual curves up to prog
    n_pts = max(4, int(round(64 * prog)))
    ship_pts: list[tuple[float, float]] = []
    press_pts: list[tuple[float, float]] = []
    for i in range(n_pts):
        u = i / 63.0
        px_i = plot_x0 + px(14) + u * (plot_w - px(28))
        climb_u = 1.0 - math.exp(-3.4 * u)
        climb_u /= 1.0 - math.exp(-3.4)
        sy = y_ground - climb_u * (y_ground - y_cruise)
        ship_pts.append((px_i, sy))

        if u < 0.18:
            py_i = y_ground - (climb_u * 0.72) * (y_ground - y_cruise)
        else:
            drop_u = min(1.0, (u - 0.18) / 0.76)
            safe_anchor = y_ground - 0.36 * (y_ground - y_cruise)
            py_i = safe_anchor + (drop_u ** 1.25) * (y_ground + px(4) - safe_anchor)
        press_pts.append((px_i, py_i))

    # Draw subtle alpha-composited divergence wedge + curves BEFORE threshold labels
    if len(ship_pts) >= 2:
        poly = ship_pts + list(reversed(press_pts))
        wedge_ov = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(wedge_ov, "RGBA").polygon(poly, fill=(th["crimson"][0], th["crimson"][1], th["crimson"][2], 46))
        canvas.alpha_composite(wedge_ov)
        d = ImageDraw.Draw(canvas, "RGBA")
        d.line(ship_pts, fill=th["cyan"], width=max(2, lw(4)))
        d.line(press_pts, fill=th["crimson"], width=max(2, lw(4)))
        sx_tip, sy_tip = ship_pts[-1]
        px_tip, py_tip = press_pts[-1]
        r_dot = max(4, px(7))
        d.ellipse([sx_tip - r_dot, sy_tip - r_dot, sx_tip + r_dot, sy_tip + r_dot], fill=th["cyan"], outline=th["white"], width=lw(2))
        d.ellipse([px_tip - r_dot, py_tip - r_dot, px_tip + r_dot, py_tip + r_dot], fill=th["crimson"], outline=th["white"], width=lw(2))

    # Threshold pill badges drawn ON TOP so curves never overwrite Vietnamese text
    f_mark = _fit_font(d, "4.300M RƠI MẶT NẠ", plot_w // 2, px(17), "bold", 10)
    _, _, mw_horn, mh_horn = _text_size(d, "3.600M CÒI BÁO", f_mark)
    _, _, mw_mask, mh_mask = _text_size(d, "4.300M RƠI MẶT NẠ", f_mark)
    pill_h_est = max(mh_horn, mh_mask) + px(8)
    _draw_pill(d, plot_x1 - mw_horn - px(44), y_horn - pill_h_est // 2, "3.600M CÒI BÁO", f_mark, (22, 18, 10, 236), th["brass"], outline=th["brass"], pad_x=px(10), pad_y=px(4), radius=px(5), outline_w=1)
    _draw_pill(d, plot_x1 - mw_mask - px(44), y_mask - pill_h_est // 2, "4.300M RƠI MẶT NẠ", f_mark, (28, 10, 14, 236), th["crimson"], outline=th["crimson"], pad_x=px(10), pad_y=px(4), radius=px(5), outline_w=1)

    # Axis time label
    f_ax = _fit_font(d, "00:00  ->  10.400M CRUISE", plot_w, px(16), "mono", 10)
    _draw_text_top(d, plot_x0 + px(10), plot_y1 + px(6), "CẤT CÁNH (0M)", f_ax, th["muted"])
    _, _, ax_w, _ = _text_size(d, "TRẦN BAY (10.400M)", f_ax)
    _draw_text_top(d, plot_x1 - ax_w - px(10), plot_y1 + px(6), "TRẦN BAY (10.400M)", f_ax, th["muted"])

    # Right side telemetry readouts
    rx0 = plot_x1 + px(18)
    rx1 = x0 + pw - pad
    box_h = (plot_y1 - plot_y0 - px(14)) // 2
    alt_cur = int(round(10400 * prog))
    alt_str = f"{alt_cur:,}M".replace(",", ".")
    p_kpa = 101.0 - 76.0 * prog

    # Box 1: Ship Altitude
    d.rounded_rectangle([rx0, plot_y0, rx1, plot_y0 + box_h], radius=px(8), fill=th["sub_bg"], outline=th["cyan"], width=max(1, lw(2)))
    f_lbl = _fit_font(d, "ĐỘ CAO TÀU: 10.400M", rx1 - rx0 - px(24), px(22), "bold", 11)
    _draw_text_top(d, rx0 + px(14), plot_y0 + px(14), f"ĐỘ CAO TÀU: {alt_str}", f_lbl, th["cyan"])
    f_sub = _fit_font(d, "CHẾ ĐỘ LÁI TỰ ĐỘNG 34.000 FT", rx1 - rx0 - px(24), px(17), "mono", 10)
    _draw_text_top(d, rx0 + px(14), plot_y0 + px(54), "LÁI TỰ ĐỘNG • 34.000 FT", f_sub, th["white"])

    # Box 2: Cabin Pressure Drop
    by2 = plot_y0 + box_h + px(14)
    d.rounded_rectangle([rx0, by2, rx1, plot_y1], radius=px(8), fill=(26, 10, 14, 232), outline=th["crimson"], width=max(1, lw(2)))
    f_lbl2 = _fit_font(d, "ÁP SUẤT CABIN: TỤT", rx1 - rx0 - px(24), px(22), "bold", 11)
    _draw_text_top(d, rx0 + px(14), by2 + px(14), "ÁP SUẤT CABIN: TỤT", f_lbl2, th["crimson"])
    _draw_text_top(d, rx0 + px(14), by2 + px(54), f"{p_kpa:04.1f} kPa • VAN ĐUÔI MỞ", f_sub, th["parchment"])

    return canvas


# ---------------------------------------------------------------------------
# 2. Dual Horn Pulse Comparator (2.0Hz 250ms ON / 250ms OFF, Overlap-Fixed)
# ---------------------------------------------------------------------------

def render_dual_horn_pulse(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render authentic 2.0Hz 250ms ON / 250ms OFF burst comparator without badge/title overlap."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    pw = ctx["max_card_w"] if ctx["portrait"] else min(px(1080), ctx["max_card_w"])
    ph = px(332 if not ctx["portrait"] else 370)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec)
    slide = _ease_out_cubic(_clamp01(t_beat / 0.25))
    y0 = _apply_slide_y(ctx, y0, ph, int(round((1.0 - slide) * px(24))), spec)

    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=th["crimson"])

    pad = px(26)
    # 1. Measure & place right badge FIRST so left title NEVER collides with it
    badge_txt = str(spec.get("badge", "TRÙNG ÂM 100%"))
    f_badge = _fit_font(d, badge_txt, pw // 3, px(21), "bold", 11)
    _, _, btw, bth = _text_size(d, badge_txt, f_badge)
    badge_w = btw + px(28)
    badge_x = x0 + pw - pad - badge_w
    badge_y = y0 + px(16)
    _draw_pill(d, badge_x, badge_y, badge_txt, f_badge, th["crimson"], th["white"], radius=px(7), pad_x=px(14), pad_y=px(7))

    # 2. Fit left title strictly within remaining width before badge_x - gap
    title_txt = str(spec.get("title", "ĐỐI CHIẾU CÒI BÁO 2.0HZ • 3.600M"))
    max_title_w = max(100, badge_x - (x0 + pad) - px(28))
    f_title = _fit_font(d, title_txt, max_title_w, px(22), "mono", 11)
    _draw_text_top(d, x0 + pad, y0 + px(22), title_txt, f_title, th["brass"])

    hdr_y = y0 + px(64)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=max(1, lw(1)))

    # Two oscilloscope rows
    lbl_col_w = min(px(340), int(pw * 0.36))
    wave_x0 = x0 + pad + lbl_col_w + px(16)
    wave_x1 = x0 + pw - pad
    wave_w = max(120, wave_x1 - wave_x0)
    row_area_top = hdr_y + px(14)
    row_area_bot = y0 + ph - px(34)
    row_gap = px(14)
    row_h = max(48, (row_area_bot - row_area_top - row_gap) // 2)

    lanes = [
        (row_area_top, str(spec.get("wave1_label", spec.get("label_a", "CẢNH BÁO CẤT CÁNH (MẶT ĐẤT)"))), "250ms BẬT / 250ms TẮT • 2.0Hz", th["cyan"]),
        (row_area_top + row_h + row_gap, str(spec.get("wave2_label", spec.get("label_b", "MẤT ÁP SUẤT CABIN (3.600M)"))), "NHỊP XUNG GIỐNG HỆT 100%", th["crimson"]),
    ]

    # Window spans 2.0 seconds = 4 full 0.50s cycles of 2.0Hz (250ms ON / 250ms OFF)
    win_sec = 2.0
    t_scroll = float(t_beat) * 0.65

    for ly0, label, sub_lbl, col in lanes:
        ly1 = ly0 + row_h
        mid_y = (ly0 + ly1) * 0.5
        amp_h = row_h * 0.36
        d.rounded_rectangle([wave_x0, ly0, wave_x1, ly1], radius=px(8), fill=th["sub_bg"], outline=th["grid"], width=1)
        d.line([(wave_x0 + px(6), mid_y), (wave_x1 - px(6), mid_y)], fill=(255, 255, 255, 36), width=1)

        f_l = _fit_font(d, label, lbl_col_w, px(21), "bold", 10)
        f_s = _fit_font(d, sub_lbl, lbl_col_w, px(16), "mono", 9)
        _draw_text_top(d, x0 + pad, ly0 + px(12), label, f_l, col)
        _draw_text_top(d, x0 + pad, ly0 + px(46), sub_lbl, f_s, th["muted"])

        # Draw 250ms ON / 250ms OFF rectangular gate shading & nasal harmonic burst
        n_samp = max(120, wave_w // 2)
        pts: list[tuple[float, float]] = []
        in_on_block = False
        block_x_start = wave_x0
        for i in range(n_samp + 1):
            frac = i / float(n_samp)
            sx = wave_x0 + px(6) + frac * (wave_w - px(12))
            t_sim = frac * win_sec + t_scroll
            cyc = t_sim % 0.50  # 0.50s period = 2.0 Hz
            is_on = cyc < 0.25
            # Soft 6ms edge ramp inside 250ms ON window
            if is_on:
                edge = min(cyc / 0.008, (0.25 - cyc) / 0.008, 1.0)
                if not in_on_block:
                    in_on_block = True
                    block_x_start = sx
                carrier = (
                    0.56 * math.sin(t_sim * 2.0 * math.pi * 22.0)
                    + 0.28 * math.sin(t_sim * 2.0 * math.pi * 44.0 + 0.4)
                    + 0.16 * math.sin(t_sim * 2.0 * math.pi * 66.0)
                )
                sy = mid_y - carrier * amp_h * edge
            else:
                if in_on_block:
                    in_on_block = False
                    d.rectangle([block_x_start, ly0 + px(6), sx, ly1 - px(6)], fill=(col[0], col[1], col[2], 24))
                sy = mid_y
            pts.append((sx, sy))
        if in_on_block:
            d.rectangle([block_x_start, ly0 + px(6), wave_x1 - px(6), ly1 - px(6)], fill=(col[0], col[1], col[2], 24))
        if len(pts) >= 2:
            d.line(pts, fill=col, width=max(2, lw(3)))

    # Vertical dashed alignment sync ticks & time markers
    f_t = _fit_font(d, "0.25s ON", wave_w // 4, px(15), "mono", 9)
    for k in range(5):
        tx = wave_x0 + px(6) + int((k / 4.0) * (wave_w - px(12)))
        _draw_dashed_line(d, (tx, row_area_top + px(2)), (tx, row_area_bot - px(2)), (255, 255, 255, 42), width=1, dash=px(6), gap=px(6))
    _draw_text_top(d, wave_x0 + px(10), row_area_bot + px(6), "250ms ON", f_t, th["brass"])
    _draw_text_top(d, wave_x0 + wave_w // 2 - px(45), row_area_bot + px(6), "250ms OFF", f_t, th["muted"])
    _, _, tw_r, _ = _text_size(d, "2.0Hz ĐỒNG BỘ", f_t)
    _draw_text_top(d, wave_x1 - tw_r - px(8), row_area_bot + px(6), "2.0Hz ĐỒNG BỘ", f_t, th["crimson"])

    return canvas


# ---------------------------------------------------------------------------
# 3. Hypoxia TUC & CO2-SpO2 Paradox Meter
# ---------------------------------------------------------------------------

def render_hypoxia_tuc_meter(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render CO2 normal clearance vs SpO2 collapse + animated TUC: 30-90 GIÂY bar."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    dur_s = max(0.25, float(dur))
    u = _clamp01(t_beat / dur_s)
    prog = _ease_out_cubic(_clamp01(t_beat / min(dur_s * 0.85, 2.2)))

    pw = ctx["max_card_w"] if ctx["portrait"] else min(px(1080), ctx["max_card_w"])
    ph = px(352 if not ctx["portrait"] else 410)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec)

    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=th["crimson"])

    pad = px(26)
    badge_txt = str(spec.get("badge", "10.400M • KHÔNG CẢM GIÁC NGẠT"))
    f_b = _fit_font(d, badge_txt, pw // 3, px(19), "bold", 10)
    _, _, btw, _ = _text_size(d, badge_txt, f_b)
    badge_x = x0 + pw - pad - btw - px(28)
    _draw_pill(d, badge_x, y0 + px(16), badge_txt, f_b, (28, 16, 22, 235), th["brass"], outline=th["brass"], pad_x=px(14), pad_y=px(6), radius=px(6), outline_w=1)

    kicker = str(spec.get("kicker", "SINH LÝ THIẾU OXY GIẢM ÁP • TỤT NHẬN THỨC THẦM LẶNG"))
    f_k = _fit_font(d, kicker, max(120, badge_x - (x0 + pad) - px(20)), px(21), "mono", 10)
    _draw_text_top(d, x0 + pad, y0 + px(21), kicker, f_k, th["parchment"])

    hdr_y = y0 + px(62)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=1)

    # Top row: 2 side-by-side cards (CO2 normal vs SpO2 plummeting)
    col_gap = px(18)
    col_w = (pw - pad * 2 - col_gap) // 2
    box_y0 = hdr_y + px(14)
    box_h = px(136)

    # Left: CO2 THẢI ĐỀU -> KHÔNG NGẠT
    lx0 = x0 + pad
    d.rounded_rectangle([lx0, box_y0, lx0 + col_w, box_y0 + box_h], radius=px(10), fill=th["sub_bg"], outline=th["mint"], width=max(1, lw(2)))
    f_ch = _fit_font(d, "CO2 THẢI ĐỀU -> KHÔNG NGẠT", col_w - px(28), px(22), "bold", 10)
    _draw_text_top(d, lx0 + px(14), box_y0 + px(14), "CO2 THẢI ĐỀU -> KHÔNG NGẠT", f_ch, th["mint"])
    f_cs = _fit_font(d, "HỆ THẦN KINH KHÔNG NHẬN TÍN HIỆU BÁO ĐỘNG", col_w - px(28), px(17), "reg", 9)
    _draw_text_top(d, lx0 + px(14), box_y0 + px(48), "KHÔNG CẢM GIÁC KHÓ THỞ", f_cs, th["white"])
    # Steady flat/breathing wave
    wave_y = box_y0 + px(102)
    pts_co2 = []
    for xi in range(lx0 + px(16), lx0 + col_w - px(16), max(2, px(5))):
        ph_c = (xi - lx0) * 0.045 - t_beat * 5.0
        pts_co2.append((xi, wave_y + math.sin(ph_c) * px(12)))
    if len(pts_co2) >= 2:
        d.line(pts_co2, fill=th["mint"], width=max(2, lw(3)))

    # Right: SpO2 TỤT ĐỘT NGỘT -> MẤT TỈNH TÁO
    rx0 = lx0 + col_w + col_gap
    spo2_val = int(round(98.0 - 44.0 * prog))
    d.rounded_rectangle([rx0, box_y0, rx0 + col_w, box_y0 + box_h], radius=px(10), fill=(26, 10, 14, 232), outline=th["crimson"], width=max(1, lw(2)))
    f_rh = _fit_font(d, "SpO2 TỤT ĐỘT NGỘT -> MẤT TỈNH TÁO", col_w - px(28), px(22), "bold", 10)
    _draw_text_top(d, rx0 + px(14), box_y0 + px(14), "SpO2 TỤT ĐỘT NGỘT -> MẤT TỈNH TÁO", f_rh, th["crimson"])
    _draw_text_top(d, rx0 + px(14), box_y0 + px(48), f"OXY MÁU: {spo2_val}% (NGUY KỊCH < 70%)", f_cs, th["white"])
    # Falling saturation curve
    pts_spo2 = []
    n_sp = max(6, int(round(40 * max(0.25, prog))))
    for i in range(n_sp):
        sf = i / 39.0
        sx = rx0 + px(16) + sf * (col_w - px(32))
        sy = box_y0 + px(82) + (sf ** 1.45) * px(36)
        pts_spo2.append((sx, sy))
    if len(pts_spo2) >= 2:
        d.line(pts_spo2, fill=th["crimson"], width=max(2, lw(4)))

    # Bottom: Animated TUC: 30-90 GIÂY bar
    tuc_y0 = box_y0 + box_h + px(16)
    tuc_y1 = y0 + ph - px(18)
    d.rounded_rectangle([lx0, tuc_y0, x0 + pw - pad, tuc_y1], radius=px(10), fill=th["sub_bg"], outline=th["grid"], width=1)

    tuc_title = str(spec.get("tuc_label", "THỜI GIAN TỈNH TÁO: 30–90 GIÂY"))
    rem_sec = max(0.0, 90.0 * (1.0 - 0.68 * u))
    f_tuc = _fit_font(d, tuc_title, pw // 2, px(28), "bold", 13)
    _draw_text_top(d, lx0 + px(16), tuc_y0 + px(12), tuc_title, f_tuc, th["brass"])

    rem_txt = f"THỜI GIAN TỈNH TÁO CÒN LẠI: {rem_sec:04.1f}s"
    f_rem = _fit_font(d, rem_txt, pw // 2, px(22), "mono", 11)
    _, _, rw, _ = _text_size(d, rem_txt, f_rem)
    _draw_text_top(d, x0 + pw - pad - px(16) - rw, tuc_y0 + px(16), rem_txt, f_rem, th["crimson"] if rem_sec < 50 else th["white"])

    bar_x0 = lx0 + px(16)
    bar_x1 = x0 + pw - pad - px(16)
    bar_y0 = tuc_y0 + px(58)
    bar_y1 = bar_y0 + px(22)
    bar_w = max(40, bar_x1 - bar_x0)
    d.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=px(7), fill=(255, 255, 255, 28))
    fill_ratio = max(0.05, 1.0 - 0.72 * prog)
    d.rounded_rectangle([bar_x0, bar_y0, bar_x0 + int(bar_w * fill_ratio), bar_y1], radius=px(7), fill=th["crimson"])

    # Zone tick labels cleanly below bar
    f_zt = _fit_font(d, "90S MẤT TỈNH TÁO", bar_w // 3, px(15), "mono", 9)
    _draw_text_top(d, bar_x0, bar_y1 + px(6), "0S (MẤT Ý THỨC)", f_zt, th["crimson"])
    _, _, mtw, _ = _text_size(d, "30-90 GIÂY NGUY HIỂM", f_zt)
    _draw_text_top(d, bar_x0 + (bar_w - mtw) // 2, bar_y1 + px(6), "30-90 GIÂY NGUY HIỂM", f_zt, th["brass"])
    _, _, rtw, _ = _text_size(d, "15 PHÚT BÌNH THƯỜNG", f_zt)
    _draw_text_top(d, bar_x1 - rtw, bar_y1 + px(6), "15 PHÚT BÌNH THƯỜNG", f_zt, th["muted"])

    return canvas


# ---------------------------------------------------------------------------
# 4. Swiss Cheese 4-Layer Sequential Alignment + Piercing Red Laser
# ---------------------------------------------------------------------------

def render_swiss_cheese_align(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render 4 sequential defense slices sliding into alignment as a red laser pierces through."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    dur_s = max(0.3, float(dur))
    u = _clamp01(t_beat / dur_s)

    pw = min(px(1640), ctx["max_card_w"])
    ph = px(445 if not ctx["portrait"] else 490)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec, centered=True)

    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=th["brass"])

    pad = px(28)
    aligned_all = u >= 0.56
    status_txt = "XUYÊN THỦNG 4 LỚP PHÒNG THỦ" if aligned_all else "ĐANG CĂN THẲNG HÀNG LỖI..."
    f_st = _fit_font(d, status_txt, pw // 3, px(19), "bold", 10)
    _, _, stw, _ = _text_size(d, status_txt, f_st)
    st_x = x0 + pw - pad - stw - px(28)
    _draw_pill(
        d, st_x, y0 + px(16), status_txt, f_st,
        th["crimson"] if aligned_all else th["sub_bg"],
        th["white"] if aligned_all else th["brass"],
        outline=th["crimson"] if aligned_all else th["brass"],
        pad_x=px(14), pad_y=px(6), radius=px(6), outline_w=max(1, lw(2)),
    )

    kicker = str(spec.get("kicker", "CHUỖI MẮT XÍCH PHÁP Y • MÔ HÌNH PHÔ MAI THỤY SĨ"))
    f_k = _fit_font(d, kicker, max(120, st_x - (x0 + pad) - px(20)), px(22), "mono", 10)
    _draw_text_top(d, x0 + pad, y0 + px(21), kicker, f_k, th["brass"])

    hdr_y = y0 + px(62)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=1)

    slices = list(spec.get("slices", ["NÚT MAN P5", "3X CHECKLIST", "CÒI KÉP 3.600M", "HYPOXIA 90S"]))[:4]
    n_sl = len(slices)
    gap = px(26)
    sl_w = (pw - pad * 2 - gap * (n_sl - 1)) // n_sl

    # Fixed header row for slice titles above moving plates -> zero collision with sliding plates or laser
    lbl_y = hdr_y + px(12)
    lbl_h = px(48)
    track_top = lbl_y + lbl_h + px(12)
    track_bot = y0 + ph - px(22)
    track_h = max(120, track_bot - track_top)
    plate_h = int(track_h * 0.68)
    y_axis = track_top + track_h // 2

    # Reference dotted target axis
    _draw_dashed_line(d, (x0 + pad, y_axis), (x0 + pw - pad, y_axis), (255, 255, 255, 42), width=1, dash=px(8), gap=px(6))

    init_offsets = [px(-46), px(44), px(-40), px(48)]
    hole_r = max(10, px(24))
    hole_centers: list[tuple[int, int]] = []

    for idx, label in enumerate(slices):
        sx = x0 + pad + idx * (sl_w + gap)
        # Top fixed badge for slice name
        d.rounded_rectangle([sx, lbl_y, sx + sl_w, lbl_y + lbl_h], radius=px(8), fill=th["sub_bg"], outline=th["grid"], width=1)
        full_lbl = f"0{idx + 1}. {label}"
        f_sl = _fit_font(d, full_lbl, sl_w - px(20), px(21), "bold", 10)
        _, _, ltw, lth = _text_size(d, full_lbl, f_sl)
        _draw_text_top(d, sx + (sl_w - ltw) // 2, lbl_y + (lbl_h - lth) // 2, full_lbl, f_sl, th["white"])

        # Sequential slide into vertical alignment
        t_start = 0.06 + idx * 0.10
        align_u = _ease_in_out_cubic(_clamp01((u - t_start) / 0.24))
        cur_off = int(round(init_offsets[idx % 4] * (1.0 - align_u)))
        is_locked = align_u >= 0.96

        py_c = y_axis + cur_off
        py_top = py_c - plate_h // 2
        py_bot = py_c + plate_h // 2

        plate_x0 = sx + px(28)
        plate_x1 = sx + sl_w - px(28)
        # Subtle 3D thickness slab shadow on right
        slab_dx = max(4, px(10))
        d.rounded_rectangle([plate_x0 + slab_dx, py_top + px(6), plate_x1 + slab_dx, py_bot + px(6)], radius=px(10), fill=(24, 30, 44, 175))
        outline_col = th["crimson"] if is_locked else th["muted"]
        d.rounded_rectangle([plate_x0, py_top, plate_x1, py_bot], radius=px(10), fill=(28, 36, 52, 232), outline=outline_col, width=max(1, lw(3 if is_locked else 2)))

        # Decorative swiss holes on top/bottom away from center aperture
        small_r = max(4, hole_r // 2)
        d.ellipse([plate_x0 + px(22), py_top + px(16), plate_x0 + px(22) + small_r * 2, py_top + px(16) + small_r * 2], fill=(8, 10, 16, 220), outline=(255, 255, 255, 35))
        d.ellipse([plate_x1 - px(22) - small_r * 2, py_bot - px(16) - small_r * 2, plate_x1 - px(22), py_bot - px(16)], fill=(8, 10, 16, 220), outline=(255, 255, 255, 35))

        # Main vulnerability hole at py_c
        hx = (plate_x0 + plate_x1) // 2
        hy = py_c
        hole_centers.append((hx, hy))
        d.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r], fill=(5, 7, 11, 248), outline=th["crimson"] if is_locked else th["brass"], width=max(2, lw(3)))

    # Piercing red forensic laser line once slices align (u >= 0.52 -> 0.90)
    if u >= 0.50:
        laser_u = _ease_out_cubic(_clamp01((u - 0.50) / 0.36))
        lx_start = x0 + pad + px(6)
        lx_full = x0 + pw - pad - px(6)
        lx_cur = int(round(lx_start + (lx_full - lx_start) * laser_u))
        # Outer red glow, bright red core, white-hot center line
        d.line([(lx_start, y_axis), (lx_cur, y_axis)], fill=(205, 52, 48, 105), width=max(6, lw(16)))
        d.line([(lx_start, y_axis), (lx_cur, y_axis)], fill=(255, 72, 66, 240), width=max(3, lw(6)))
        d.line([(lx_start, y_axis), (lx_cur, y_axis)], fill=(255, 232, 226, 255), width=max(1, lw(2)))

        for hx, hy in hole_centers:
            if lx_cur >= hx:
                ir = hole_r + px(6)
                d.ellipse([hx - ir, hy - ir, hx + ir, hy + ir], outline=(255, 90, 80, 220), width=max(1, lw(2)))

    return canvas


# ---------------------------------------------------------------------------
# 5. 1997 Boeing 737 Classic vs 2006 Post-Helios Redesign Comparison
# ---------------------------------------------------------------------------

def render_classic_vs_ng_compare(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render clean comparison card: 1997 Classic (1 dim P5 lamp) vs 2006 Post-Helios (2 eye-level lamps)."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    reveal_r = _ease_out_cubic(_clamp01((t_beat - 0.14) / 0.42))

    pw = min(px(1480), ctx["max_card_w"])
    ph = px(370 if not ctx["portrait"] else 430)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec, centered=True)

    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=th["brass"])

    pad = px(26)
    kicker = str(spec.get("kicker", "CẢI TỔ AN TOÀN HÀNG KHÔNG • TÁCH BIỆT ĐÈN CẢNH BÁO BUỒNG LÁI"))
    f_k = _fit_font(d, kicker, pw - pad * 2, px(21), "mono", 10)
    _draw_text_top(d, x0 + pad, y0 + px(18), kicker, f_k, th["brass"])

    hdr_y = y0 + px(56)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=1)

    mid_x = x0 + pw // 2
    col_gap = px(24)
    panel_y0 = hdr_y + px(14)
    panel_y1 = y0 + ph - px(20)
    l_x0, l_x1 = x0 + pad, mid_x - col_gap // 2
    r_x0, r_x1 = mid_x + col_gap // 2, x0 + pw - pad
    l_w = l_x1 - l_x0
    r_w = r_x1 - r_x0

    # Left Panel: 1997 BOEING 737 CLASSIC (1 ĐÈN P5 MỜ)
    d.rounded_rectangle([l_x0, panel_y0, l_x1, panel_y1], radius=px(10), fill=th["sub_bg"], outline=th["crimson"], width=max(1, lw(2)))
    left_title = str(spec.get("left_title", "1997 BOEING 737 CLASSIC (1 ĐÈN P5 MỜ)"))
    f_lt = _fit_font(d, left_title, l_w - px(28), px(22), "bold", 10)
    _draw_text_top(d, l_x0 + px(16), panel_y0 + px(14), left_title, f_lt, th["crimson"])

    # Overhead P5 dim lamp schematic
    p5_x0, p5_y0, p5_x1, p5_y1 = l_x0 + px(16), panel_y0 + px(58), l_x1 - px(16), panel_y1 - px(52)
    d.rounded_rectangle([p5_x0, p5_y0, p5_x1, p5_y1], radius=px(8), fill=(18, 20, 26, 230), outline=(255, 255, 255, 42), width=1)
    lamp_w, lamp_h = px(156), px(42)
    lx_c = p5_x0 + px(28)
    ly_c = (p5_y0 + p5_y1 - lamp_h) // 2
    d.rounded_rectangle([lx_c, ly_c, lx_c + lamp_w, ly_c + lamp_h], radius=px(5), fill=(48, 42, 24, 210), outline=(140, 120, 68, 160), width=1)
    f_lamp = _fit_font(d, "ALT WARN (MỜ)", lamp_w - px(12), px(17), "mono", 9)
    _draw_text_top(d, lx_c + px(12), ly_c + px(11), "1 ĐÈN P5 MỜ", f_lamp, (190, 170, 110, 220))
    f_note = _fit_font(d, "TRÊN TRẦN KHUẤT TẦM MẮT • CHUNG 1 CÒI", p5_x1 - (lx_c + lamp_w + px(24)), px(19), "reg", 9)
    _draw_text_top(d, lx_c + lamp_w + px(18), ly_c + px(2), "NẰM TRÊN TRẦN P5 (KHUẤT MẮT)", f_note, th["parchment"])
    _draw_text_top(d, lx_c + lamp_w + px(18), ly_c + px(26), "1 CÒI KÉP DỄ NHẦM LỖI CẤT CÁNH", f_note, th["muted"])
    f_bot = _fit_font(d, "RỦI RO NHẬN THỨC CAO", l_w - px(32), px(18), "mono", 9)
    _draw_text_top(d, l_x0 + px(16), panel_y1 - px(36), "NGUY CƠ NHẦM LẪN NGHIÊM TRỌNG", f_bot, th["crimson"])

    # Center glowing brass divider
    div_top = panel_y0 + int((panel_y1 - panel_y0) * (1.0 - reveal_r) * 0.5)
    div_bot = panel_y1 - int((panel_y1 - panel_y0) * (1.0 - reveal_r) * 0.5)
    d.line([(mid_x, div_top), (mid_x, div_bot)], fill=th["brass"], width=max(2, lw(4)))

    # Right Panel: 2006 POST-HELIOS (2 ĐÈN TÁCH BIỆT TRƯỚC MẮT)
    d.rounded_rectangle([r_x0, panel_y0, r_x1, panel_y1], radius=px(10), fill=th["sub_bg"], outline=th["cyan"], width=max(1, lw(2)))
    right_title = str(spec.get("right_title", "2006 POST-HELIOS (2 ĐÈN TÁCH BIỆT TRƯỚC MẮT)"))
    f_rt = _fit_font(d, right_title, r_w - px(28), px(22), "bold", 10)
    _draw_text_top(d, r_x0 + px(16), panel_y0 + px(14), right_title, f_rt, th["cyan"])

    g_x0, g_y0, g_x1, g_y1 = r_x0 + px(16), panel_y0 + px(58), r_x1 - px(16), panel_y1 - px(52)
    d.rounded_rectangle([g_x0, g_y0, g_x1, g_y1], radius=px(8), fill=(12, 18, 28, 232), outline=(32, 212, 248, 85), width=1)
    pulse = 0.65 + 0.35 * math.sin(t_beat * 10.0)
    lamp2_w = (g_x1 - g_x0 - px(52)) // 2
    lamp2_h = px(54)
    ly2 = (g_y0 + g_y1 - lamp2_h) // 2

    # Lamp 1: CABIN ALTITUDE
    l1_txt = str(spec.get("right_lamp1", "ÁP SUẤT CABIN"))
    l1_x = g_x0 + px(16)
    d.rounded_rectangle([l1_x, ly2, l1_x + lamp2_w, ly2 + lamp2_h], radius=px(6), fill=(185, 38, 36, int(190 + 60 * pulse)), outline=th["white"], width=max(1, lw(2)))
    f_l1 = _fit_font(d, l1_txt, lamp2_w - px(16), px(20), "bold", 10)
    _, _, l1w, l1h = _text_size(d, l1_txt, f_l1)
    _draw_text_top(d, l1_x + (lamp2_w - l1w) // 2, ly2 + (lamp2_h - l1h) // 2, l1_txt, f_l1, th["white"])

    # Lamp 2: TAKEOFF CONFIG
    l2_txt = str(spec.get("right_lamp2", "LỖI CẤT CÁNH"))
    l2_x = l1_x + lamp2_w + px(20)
    d.rounded_rectangle([l2_x, ly2, l2_x + lamp2_w, ly2 + lamp2_h], radius=px(6), fill=(26, 98, 125, 225), outline=th["cyan"], width=max(1, lw(2)))
    f_l2 = _fit_font(d, l2_txt, lamp2_w - px(16), px(20), "bold", 10)
    _, _, l2w, l2h = _text_size(d, l2_txt, f_l2)
    _draw_text_top(d, l2_x + (lamp2_w - l2w) // 2, ly2 + (lamp2_h - l2h) // 2, l2_txt, f_l2, th["white"])

    _draw_text_top(d, r_x0 + px(16), panel_y1 - px(36), "BẮT BUỘC TRƯỚC TẦM MẮT • TÁCH BIỆT 2 ĐÈN ĐỘC LẬP", f_bot, th["mint"])

    return canvas


# ---------------------------------------------------------------------------
# 6. Fuel Exhaustion & Athens Avoidance Vector HUD
# ---------------------------------------------------------------------------

def render_fuel_avoidance_vector(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render dual fuel bars dropping to 0% (ENG 1 11:50, ENG 2 12:00) + Athens avoidance badge."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    dur_s = max(0.25, float(dur))
    u = _clamp01(t_beat / dur_s)

    pw = ctx["max_card_w"] if ctx["portrait"] else min(px(1080), ctx["max_card_w"])
    ph = px(332 if not ctx["portrait"] else 375)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec)
    slide = _ease_out_cubic(_clamp01(t_beat / 0.25))
    y0 = _apply_slide_y(ctx, y0, ph, int(round((1.0 - slide) * px(24))), spec)

    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=th["crimson"])

    pad = px(26)
    clock_min = 48 + int(round(16 * _ease_out_cubic(_clamp01(u / 0.85))))
    hh = 11 + clock_min // 60
    mm = clock_min % 60
    clock_txt = f"GIỜ BAY: {hh:02d}:{mm:02d} LT"
    f_clk = _fit_font(d, clock_txt, pw // 3, px(20), "mono", 10)
    _, _, cw, _ = _text_size(d, clock_txt, f_clk)
    clk_x = x0 + pw - pad - cw - px(28)
    _draw_pill(d, clk_x, y0 + px(16), clock_txt, f_clk, th["sub_bg"], th["brass"], outline=th["brass"], pad_x=px(14), pad_y=px(6), radius=px(6), outline_w=1)

    kicker = str(spec.get("kicker", "CẠN KIỆT NHIÊN LIỆU • QUỸ ĐẠO LƯỢN TRÁNH ĐÔ THỊ"))
    f_k = _fit_font(d, kicker, max(120, clk_x - (x0 + pad) - px(20)), px(21), "mono", 10)
    _draw_text_top(d, x0 + pad, y0 + px(21), kicker, f_k, th["parchment"])

    hdr_y = y0 + px(62)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=1)

    # Dual Fuel Bars dropping sequentially to 0%
    eng1_lvl = max(0.0, 1.0 - _ease_out_cubic(_clamp01(u / 0.42)))
    eng2_lvl = max(0.0, 1.0 - _ease_out_cubic(_clamp01((u - 0.14) / 0.56)))

    lbl_w = min(px(300), int(pw * 0.34))
    bar_x0 = x0 + pad + lbl_w + px(14)
    pct_w = px(148)
    bar_x1 = x0 + pw - pad - pct_w - px(12)
    bar_w = max(80, bar_x1 - bar_x0)

    rows = [
        (hdr_y + px(20), str(spec.get("eng1_label", "ĐỘNG CƠ 1 TẮT 11:50")), eng1_lvl, 0.18),
        (hdr_y + px(92), str(spec.get("eng2_label", "ĐỘNG CƠ 2 TẮT 12:00")), eng2_lvl, 0.24),
    ]
    for ry, r_lbl, lvl, init_cap in rows:
        bh = px(48)
        is_empty = lvl <= 0.015
        col = th["crimson"] if is_empty or lvl < 0.35 else th["brass"]
        f_rl = _fit_font(d, r_lbl, lbl_w, px(24), "bold", 11)
        _draw_text_top(d, x0 + pad, ry + px(10), r_lbl, f_rl, th["white"] if not is_empty else th["crimson"])

        d.rounded_rectangle([bar_x0, ry + px(8), bar_x1, ry + bh - px(8)], radius=px(7), fill=th["sub_bg"], outline=col, width=max(1, lw(2)))
        fill_w = int(round((bar_w - px(6)) * lvl * init_cap / 0.24)) if lvl > 0.015 else 0
        if fill_w > 4:
            d.rounded_rectangle([bar_x0 + px(3), ry + px(11), bar_x0 + px(3) + fill_w, ry + bh - px(11)], radius=px(5), fill=col)
            for tk in (0.25, 0.50, 0.75):
                tx = bar_x0 + int(round((bar_x1 - bar_x0) * tk))
                d.line([(tx, ry + px(10)), (tx, ry + bh - px(10))], fill=(10, 14, 22, 110), width=1)
        else:
            for tk in (0.25, 0.50, 0.75):
                tx = bar_x0 + int(round((bar_x1 - bar_x0) * tk))
                d.line([(tx, ry + bh - px(15)), (tx, ry + bh - px(10))], fill=(255, 255, 255, 45), width=1)
            f_emp = _fit_font(d, "CẠN NHIÊN LIỆU (0.0%)", bar_w - px(24), px(15), "mono", 9)
            _draw_text_top(d, bar_x0 + px(14), ry + px(14), "CẠN NHIÊN LIỆU (0.0%)", f_emp, (th["crimson"][0], th["crimson"][1], th["crimson"][2], 195))

        pct_val = int(round(lvl * init_cap * 100.0))
        pct_txt = "0% TẮT MÁY" if is_empty else f"{pct_val:2d}% DẦU"
        f_p = _fit_font(d, pct_txt, pct_w, px(19), "mono", 10)
        _draw_text_top(d, bar_x1 + px(14), ry + px(12), pct_txt, f_p, th["crimson"] if is_empty else th["parchment"])

    # Avoidance Vector Footer Badge
    foot_y0 = hdr_y + px(172)
    foot_y1 = y0 + ph - px(18)
    badge_txt = str(spec.get("avoidance_badge", "NÉ THỦ ĐÔ ATHENS -> ĐỒI GRAMMATIKO 12:04"))
    d.rounded_rectangle([x0 + pad, foot_y0, x0 + pw - pad, foot_y1], radius=px(9), fill=(26, 14, 16, 232), outline=th["brass"], width=max(1, lw(2)))
    f_av = _fit_font(d, badge_txt, pw - pad * 2 - px(48), px(25), "bold", 11)
    _, _, av_w, av_h = _text_size(d, badge_txt, f_av)
    _draw_text_top(d, x0 + (pw - av_w) // 2, foot_y0 + (foot_y1 - foot_y0 - av_h) // 2, badge_txt, f_av, th["brass"])

    return canvas


# ---------------------------------------------------------------------------
# 7. Calibrated Radar Overlay (Dynamic Coordinates, Zero Drift)
# ---------------------------------------------------------------------------

def _scale_anchor(pt: tuple[float, float], width: int, height: int, coord_space: str) -> tuple[float, float]:
    if coord_space == "target":
        return float(pt[0]), float(pt[1])
    return float(pt[0]) * (width / 2560.0), float(pt[1]) * (height / 1440.0)


def render_calibrated_radar_overlay(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render Bezier dashed flight arc + rotating radar sweep cone anchored dynamically to verified map coords."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    dur_s = max(0.3, float(dur))
    coord_space = str(spec.get("coord_space", "2k")).lower()

    p_ath = _scale_anchor(spec.get("athens_xy", VERIFIED_MAP_ANCHORS_2K["athens"]), width, height, coord_space)
    p_gram = _scale_anchor(spec.get("grammatiko_xy", VERIFIED_MAP_ANCHORS_2K["grammatiko"]), width, height, coord_space)
    p_aegean = _scale_anchor(spec.get("aegean_xy", VERIFIED_MAP_ANCHORS_2K["aegean_corridor"]), width, height, coord_space)
    p_entry = _scale_anchor(spec.get("aegean_entry_xy", VERIFIED_MAP_ANCHORS_2K["aegean_entry"]), width, height, coord_space)
    default_mid = ((p_ath[0] + p_gram[0]) * 0.5, (p_ath[1] + p_gram[1]) * 0.5)
    p_rc = _scale_anchor(spec["radar_center_xy"], width, height, coord_space) if "radar_center_xy" in spec else default_mid
    p_ctrl = _scale_anchor(spec.get("control_xy", VERIFIED_MAP_ANCHORS_2K["avoidance_ctrl"]), width, height, coord_space)

    # 1. Calibrated Radar Concentric Rings + Sweep Cone centered strictly at p_rc
    rcx, rcy = p_rc
    max_r = px(float(spec.get("radar_radius_2k", 460)))
    sweep_deg = (t_beat * 125.0) % 360.0
    n_wedges = 18
    sweep_span = 42.0
    for wi in range(n_wedges):
        frac = wi / float(n_wedges)
        a0 = math.radians(sweep_deg - sweep_span * (1.0 - frac))
        a1 = math.radians(sweep_deg - sweep_span * (1.0 - (wi + 1) / float(n_wedges)))
        alpha = int(round((24 if th["variant"] == "B" else 42) * ((wi + 1) / float(n_wedges)) ** 1.7))
        poly = [(rcx, rcy)]
        for ang in (a0, (a0 + a1) * 0.5, a1):
            poly.append((rcx + max_r * math.cos(ang), rcy + max_r * math.sin(ang)))
        d.polygon(poly, fill=(th["cyan"][0], th["cyan"][1], th["cyan"][2], alpha))

    # Leading edge radar beam
    rad_lead = math.radians(sweep_deg)
    d.line([(rcx, rcy), (rcx + max_r * math.cos(rad_lead), rcy + max_r * math.sin(rad_lead))], fill=(th["cyan"][0], th["cyan"][1], th["cyan"][2], 175), width=max(1, lw(2)))

    # Concentric radar rings & subtle cardinal ticks
    for rf in (0.30, 0.56, 0.80, 1.00):
        rr = max_r * rf
        ring_a = 95 if abs(rf - 0.70) < 0.16 else 55
        d.ellipse([rcx - rr, rcy - rr, rcx + rr, rcy + rr], outline=(th["cyan"][0], th["cyan"][1], th["cyan"][2], ring_a), width=max(1, lw(2 if rf == 1.0 else 1)))
    d.line([(rcx - max_r, rcy), (rcx + max_r, rcy)], fill=(th["cyan"][0], th["cyan"][1], th["cyan"][2], 42), width=1)
    d.line([(rcx, rcy - max_r), (rcx, rcy + max_r)], fill=(th["cyan"][0], th["cyan"][1], th["cyan"][2], 42), width=1)

    # 2. Aegean Approach Corridor Dashed Track (faint incoming glide path before Athens turn)
    if spec.get("show_aegean_approach", True):
        app_ctrl = ((p_entry[0] + p_ath[0]) * 0.52, p_aegean[1] - px(40))
        app_pts: list[tuple[float, float]] = []
        for k in range(51):
            tt = k / 50.0
            bx = (1 - tt) ** 2 * p_entry[0] + 2 * (1 - tt) * tt * app_ctrl[0] + tt ** 2 * p_ath[0]
            by = (1 - tt) ** 2 * p_entry[1] + 2 * (1 - tt) * tt * app_ctrl[1] + tt ** 2 * p_ath[1]
            app_pts.append((bx, by))
        for k in range(0, len(app_pts) - 1, 3):
            d.line([app_pts[k], app_pts[min(len(app_pts) - 1, k + 2)]], fill=(th["cyan"][0], th["cyan"][1], th["cyan"][2], 185), width=max(1, lw(3)))

        # Aegean corridor waypoint marker
        ax, ay = p_aegean
        d.ellipse([ax - px(6), ay - px(6), ax + px(6), ay + px(6)], fill=th["cyan"], outline=th["white"], width=1)
        ae_lbl = str(spec.get("aegean_label", "HÀNH LANG AEGEAN"))
        f_ae = _fit_font(d, ae_lbl, px(260), px(18), "mono", 10)
        ae_x = int(ax + px(16))
        if ctx["portrait"]:
            _, _, ae_tw, _ = _text_size(d, ae_lbl, f_ae)
            ae_x = min(width - (ae_tw + px(10) * 2) - ctx["right_margin_x"], ae_x)
        _draw_pill(d, ae_x, int(ay + px(10)), ae_lbl, f_ae, (8, 14, 24, 210), th["cyan"], outline=(th["cyan"][0], th["cyan"][1], th["cyan"][2], 140), pad_x=px(10), pad_y=px(5), radius=px(5), outline_w=1)

    # 3. Primary Progressive Avoidance Bezier Dashed Trajectory (Athens -> Grammatiko)
    arc_prog = _ease_out_cubic(_clamp01((t_beat - 0.10) / min(1.15, dur_s * 0.72)))
    steps = 90
    max_k = max(2, int(round(steps * arc_prog)))
    pts: list[tuple[float, float]] = []
    for k in range(max_k + 1):
        tt = k / float(steps)
        bx = (1 - tt) ** 2 * p_ath[0] + 2 * (1 - tt) * tt * p_ctrl[0] + tt ** 2 * p_gram[0]
        by = (1 - tt) ** 2 * p_ath[1] + 2 * (1 - tt) * tt * p_ctrl[1] + tt ** 2 * p_gram[1]
        pts.append((bx, by))
    for k in range(0, len(pts) - 1, 3):
        d.line([pts[k], pts[min(len(pts) - 1, k + 2)]], fill=th["crimson"], width=max(2, lw(6)))

    # Moving aircraft pulse dot at trajectory head
    if pts:
        hx, hy = pts[-1]
        hr = max(4, px(8))
        d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=th["white"], outline=th["crimson"], width=max(2, lw(3)))

    # 4. Pulsing Reticles + Clamped Non-Overlapping Callout Badges
    def _draw_reticle(pt: tuple[float, float], label: str, side: str, acc: tuple[int, int, int, int], pop_u: float) -> None:
        cx, cy = pt
        pulse_r = px(38) + int(round(px(8) * math.sin(t_beat * 7.5)))
        outer_r = px(62)
        d.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r], outline=(acc[0], acc[1], acc[2], 115), width=max(1, lw(2)))
        d.ellipse([cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r], outline=acc, width=max(2, lw(4)))
        dot_r = max(5, px(10))
        d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=acc, outline=th["white"], width=max(1, lw(2)))
        if pop_u <= 0.05:
            return
        f_lbl = _fit_font(d, label, int(width * 0.32), px(25), "bold", 11)
        bx0, by0, tw, th_t = _text_size(d, label, f_lbl)
        bw = tw + px(34)
        bh = th_t + px(22)
        offset = px(76)
        lx = int(round((cx + offset) if side == "right" else (cx - offset - bw)))
        right_pad = ctx["right_margin_x"] if ctx["portrait"] else px(28)
        lx = max(px(28), min(width - bw - right_pad, lx))
        ly = int(round(max(ctx["top_safe"] + px(10), min(ctx["bottom_safe"] - bh - px(10), cy - bh // 2))))
        anchor_x = lx if side == "right" else (lx + bw)
        if (side == "right" and anchor_x > cx + pulse_r) or (side == "left" and anchor_x < cx - pulse_r):
            line_sx = cx + (pulse_r if side == "right" else -pulse_r)
            d.line([(line_sx, cy), (anchor_x, ly + bh // 2)], fill=acc, width=max(1, lw(3)))
        d.rounded_rectangle([lx, ly, lx + bw, ly + bh], radius=px(9), fill=th["card_bg"], outline=acc, width=max(1, lw(2)))
        d.text((lx + px(17) - bx0, ly + px(11) - by0), label, font=f_lbl, fill=th["white"])

    ath_lbl = str(spec.get("athens_label", "THỦ ĐÔ ATHENS • KHU ĐÔ THỊ ĐÔNG DÂN"))
    gram_lbl = str(spec.get("grammatiko_label", "GRAMMATIKO • CÚ BẺ LÁI TRÁNH ĐÔ THỊ (12:04)"))
    _draw_reticle(p_ath, ath_lbl, "left", th["crimson"], _ease_out_cubic(_clamp01(t_beat / 0.25)))
    _draw_reticle(p_gram, gram_lbl, "right", th["brass"], _ease_out_cubic(_clamp01((t_beat - 0.50) / 0.30)))

    return canvas


# ---------------------------------------------------------------------------
# 8. LEMMiNO Hairline Forensic HUD (Option B Ultra-Minimal, No Heavy Boxes)
# ---------------------------------------------------------------------------

def render_lemmino_hairline_hud(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
) -> Image.Image:
    """Render ultra-clean 1px hairline forensic lower-third rule without spoilers or heavy boxes."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme("B")
    ctx = _layout_ctx(width, height)
    px = ctx["px"]
    hair = max(1, int(round(min(width / 2560.0, height / 1440.0))))

    dur_s = max(0.25, float(dur))
    prog = _ease_out_cubic(_clamp01(t_beat / min(dur_s * 0.72, 1.8)))
    env_in = 0.25 + 0.75 * _ease_out_cubic(_clamp01(t_beat / 0.25))
    rem = max(0.0, dur_s - float(t_beat))
    env_out = _ease_out_cubic(_clamp01(rem / 0.28)) if (dur_s >= 1.5 and rem < 0.28) else 1.0
    alpha = int(round(255 * env_in * env_out))

    mode = str(spec.get("mode", "timeline")).lower()
    kicker = str(spec.get("kicker", "14.08.2005 • HỒ SƠ CHUYẾN BAY"))
    headline = str(spec.get("headline", "HELIOS 522"))
    metric = str(spec.get("metric", "")).strip()

    mx = ctx["margin_x"]
    rmx = ctx.get("right_margin_x", mx)
    span_w = min(px(1180), ctx["max_card_w"])
    x0 = mx if not ctx["portrait"] else mx + max(0, (width - mx - rmx - span_w) // 2)
    x1 = x0 + span_w
    base_y = ctx["bottom_safe"] - px(136)
    rule_y = base_y + px(86)

    col_parch = (th["parchment"][0], th["parchment"][1], th["parchment"][2], alpha)
    col_white = (th["white"][0], th["white"][1], th["white"][2], alpha)
    col_brass = (th["brass"][0], th["brass"][1], th["brass"][2], alpha)
    col_red = (th["crimson"][0], th["crimson"][1], th["crimson"][2], alpha)
    col_rule = (232, 223, 200, int(alpha * 0.44))

    # Whisper-light borderless cinema scrim keeps small hairline typography crisp over bright terrain
    has_markers = bool(list(spec.get("markers") or [])[:5])
    scrim_y1 = rule_y + (px(36) if has_markers else px(14))
    d.rounded_rectangle(
        [x0 - px(14), base_y - px(10), x1 + px(14), scrim_y1],
        radius=px(8),
        fill=(8, 10, 14, int(alpha * 0.44)),
    )

    # Minimal vertical accent tick + clean time/place headline (NO box, NO spoilers)
    d.line([(x0, base_y), (x0, base_y + px(68))], fill=col_brass, width=max(1, hair * 2))
    k_max_w = int(span_w * (0.68 if metric else 0.94))
    f_k = _fit_font(d, kicker, k_max_w, px(24), "mono", 10)
    _draw_text_top(d, x0 + px(16), base_y, kicker, f_k, col_brass, shadow=True)

    if metric:
        f_m = _fit_font(d, metric, int(span_w * 0.30), px(24), "mono", 11)
        _, _, mw, _ = _text_size(d, metric, f_m)
        _draw_text_top(d, x1 - mw, base_y, metric, f_m, col_parch, shadow=True)

    f_h = _fit_font(d, headline, span_w - px(24), px(38), "bold", 13)
    _draw_text_top(d, x0 + px(16), base_y + px(32), headline, f_h, col_white, shadow=True)
    if mode == "wave":
        d.line([(x0, rule_y), (x1, rule_y)], fill=col_rule, width=hair)
        pts = []
        for xi in range(x0, x1 + 1, max(2, px(5))):
            u_x = (xi - x0) / float(max(1, span_w))
            env = math.sin(u_x * math.pi)
            val = math.sin((xi - x0) * 0.04 - t_beat * 18.0) * px(18) * env
            pts.append((xi, rule_y + val))
        if len(pts) >= 2:
            d.line(pts, fill=col_red, width=max(1, hair * 2))
    else:
        d.line([(x0, rule_y), (x1, rule_y)], fill=col_rule, width=hair)
        cur_x = int(round(x0 + span_w * prog))
        d.line([(x0, rule_y), (cur_x, rule_y)], fill=col_brass, width=max(1, hair * 2))
        r_dot = max(3, px(4))
        d.ellipse([cur_x - r_dot, rule_y - r_dot, cur_x + r_dot, rule_y + r_dot], fill=col_brass, outline=col_white, width=hair)

        # Render optional bottom markers ONLY if explicitly provided in spec (never hardcode future spoilers)
        markers = list(spec.get("markers") or [])[:5]
        if markers:
            f_mk = _fit_font(d, str(markers[0]), max(90, span_w // max(1, len(markers)) - px(12)), px(16), "mono", 9)
            n_m = max(1, len(markers))
            for mi, m_txt in enumerate(markers):
                mx_i = x0 + int(round((mi / float(max(1, n_m - 1))) * span_w)) if n_m > 1 else x0
                d.line([(mx_i, rule_y - px(6)), (mx_i, rule_y + px(6))], fill=col_parch, width=hair)
                _, _, mtw, _ = _text_size(d, str(m_txt), f_mk)
                tx = mx_i if mi == 0 else (mx_i - mtw if mi == n_m - 1 else mx_i - mtw // 2)
                _draw_text_top(d, max(x0, min(x1 - mtw, tx)), rule_y + px(12), str(m_txt), f_mk, col_parch, shadow=True)

    return canvas


# ---------------------------------------------------------------------------
# 9. Chapter Title Bumper (Minimalist 3.0s Docudrama Dossier Card)
# ---------------------------------------------------------------------------

def render_chapter_title_bumper(
    ch_num: str | int,
    ch_title: str,
    subtitle: str,
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render minimalist cinematic chapter card (`CHƯƠNG 02..10` / Style 01..04)."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    dur_s = max(0.35, float(dur))
    t = max(0.0, float(t_beat))
    fade_in_t = min(0.36, dur_s * 0.22)
    fade_out_t = min(0.36, dur_s * 0.22)
    if t < fade_in_t:
        env = _ease_out_cubic(t / max(1e-4, fade_in_t))
    elif t > dur_s - fade_out_t:
        env = _ease_out_cubic(max(0.0, (dur_s - t) / max(1e-4, fade_out_t)))
    else:
        env = 1.0
    if env <= 0.01:
        return canvas

    # Deep serene cinema backdrop scrim (zero grid clutter)
    bg_a = int(round((238 if th["variant"] == "B" else 232) * env))
    d.rectangle([0, 0, width, height], fill=(5, 7, 11, bg_a))

    raw_num = str(ch_num).strip()
    if isinstance(ch_num, int):
        eyebrow = f"CHƯƠNG {ch_num:02d}"
    elif raw_num.upper().startswith("CH") and raw_num[2:].isdigit():
        eyebrow = f"CHƯƠNG {int(raw_num[2:]):02d}"
    elif raw_num.isdigit():
        eyebrow = f"CHƯƠNG {int(raw_num):02d}"
    else:
        eyebrow = (raw_num or "CHƯƠNG 01").upper()

    max_w = int(width * 0.74)
    cx = width // 2
    cy = int(height * 0.49)

    def _with_a(col: tuple[int, int, int, int], mul: float = 1.0) -> tuple[int, int, int, int]:
        return col[0], col[1], col[2], int(round(col[3] * env * mul))

    # Minimalist bare brass eyebrow (no red pill box)
    f_k = _fit_font(d, eyebrow, max_w, px(24), "bold", 12)
    _, _, kw, _ = _text_size(d, eyebrow, f_k)
    _draw_text_top(d, cx - kw // 2, cy - px(142), eyebrow, f_k, _with_a(th["brass"], 0.92))

    # Crisp 4-5 word Vietnamese headline
    title_clean = str(ch_title or "").strip() or eyebrow
    f_t = _get_font(px(64 if not ctx["portrait"] else 50), "bold")
    title_lines = _wrap_text(d, title_clean, f_t, max_w, max_lines=2)
    if sum(len(ln) for ln in title_lines) < len(title_clean) * 0.78:
        f_t = _fit_font(d, title_clean, max_w * 2, px(48), "bold", 20)
        title_lines = _wrap_text(d, title_clean, f_t, max_w, max_lines=2)

    title_slide = int(round((1.0 - _ease_out_cubic(_clamp01(t / 0.34))) * px(16)))
    line_gap = px(14)
    line_heights = [_text_size(d, ln, f_t)[3] for ln in title_lines] or [px(56)]
    tot_th = sum(line_heights) + line_gap * max(0, len(title_lines) - 1)
    ty_cur = cy - tot_th // 2 - px(16) + title_slide
    for ln, lh in zip(title_lines, line_heights, strict=False):
        _, _, l_w, _ = _text_size(d, ln, f_t)
        _draw_text_top(d, cx - l_w // 2, ty_cur, ln, f_t, _with_a(th["white"]), shadow=True)
        ty_cur += lh + line_gap

    # Clean expanding brass hairline rule
    rule_w = int(round(min(max_w * 0.42, px(540)) * _ease_out_cubic(_clamp01((t - 0.08) / 0.36))))
    rule_y = ty_cur + px(16)
    if rule_w > 4:
        d.line([(cx - rule_w // 2, rule_y), (cx + rule_w // 2, rule_y)], fill=_with_a(th["brass"], 0.85), width=max(1, lw(2)))

    # Subtle timestamp / place subline
    sub_clean = str(subtitle or "").strip()
    if sub_clean:
        sub_a = _ease_out_cubic(_clamp01((t - 0.16) / 0.28))
        f_s = _fit_font(d, sub_clean, max_w, px(26), "reg", 12)
        sub_lines = _wrap_text(d, sub_clean, f_s, max_w, max_lines=2)
        sy_cur = rule_y + px(22)
        for sln in sub_lines:
            _, _, slw, slh = _text_size(d, sln, f_s)
            _draw_text_top(d, cx - slw // 2, sy_cur, sln, f_s, _with_a(th["parchment"], sub_a * 0.88))
            sy_cur += slh + px(8)

    return canvas


# ---------------------------------------------------------------------------
# 10. Overhead P5 MAN / AUTO Switch & Outflow Valve Schematic
# ---------------------------------------------------------------------------

def render_man_auto_switch(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Render overhead P5 selector (AUTO -> MAN) + locked-open outflow valve schematic."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    th = _theme(variant)
    ctx = _layout_ctx(width, height)
    px, lw = ctx["px"], ctx["lw"]

    turn_u = _ease_in_out_cubic(_clamp01((float(t_beat) - 0.25) / 1.15))
    slide = _ease_out_cubic(_clamp01(t_beat / 0.28))

    pw = ctx["max_card_w"] if ctx["portrait"] else min(px(1100), ctx["max_card_w"])
    ph = px(355 if not ctx["portrait"] else 410)
    x0, y0 = _place_card_xy(ctx, pw, ph, spec)
    y0 = _apply_slide_y(ctx, y0, ph, int(round((1.0 - slide) * px(24))), spec)

    accent_col = th["crimson"] if turn_u > 0.72 else th["brass"]
    _draw_card_shell(d, x0, y0, pw, ph, th, ctx, accent=accent_col)

    pad = px(26)
    badge_txt = str(spec.get("status_badge", "NẤC MAN • VAN ĐUÔI MỞ CỨNG" if turn_u > 0.72 else "AUTO -> MAN"))
    f_b = _fit_font(d, badge_txt, pw // 3 + px(40), px(19), "bold", 10)
    _, _, btw, _ = _text_size(d, badge_txt, f_b)
    badge_x = x0 + pw - pad - btw - px(28)
    _draw_pill(
        d, badge_x, y0 + px(16), badge_txt, f_b,
        th["crimson"] if turn_u > 0.72 else th["sub_bg"],
        th["white"] if turn_u > 0.72 else th["brass"],
        outline=th["crimson"] if turn_u > 0.72 else th["brass"],
        pad_x=px(14), pad_y=px(6), radius=px(6), outline_w=max(1, lw(1)),
    )

    kicker = str(spec.get("kicker", "BẢNG TRẦN P5 • CÔNG TẮC ĐIỀU ÁP CABIN"))
    f_k = _fit_font(d, kicker, max(120, badge_x - (x0 + pad) - px(20)), px(21), "mono", 10)
    _draw_text_top(d, x0 + pad, y0 + px(21), kicker, f_k, th["brass"])

    hdr_y = y0 + px(62)
    d.line([(x0 + pad, hdr_y), (x0 + pw - pad, hdr_y)], fill=th["grid"], width=1)

    gap = px(20)
    body_y0 = hdr_y + px(14)
    body_y1 = y0 + ph - px(18)
    left_w = int((pw - pad * 2 - gap) * 0.48)
    lx0, lx1 = x0 + pad, x0 + pad + left_w
    rx0, rx1 = lx1 + gap, x0 + pw - pad

    # Left panel: P5 rotary switch (AUTO -> STBY -> MAN)
    d.rounded_rectangle([lx0, body_y0, lx1, body_y1], radius=px(10), fill=th["sub_bg"], outline=th["grid"], width=1)
    knob_cx = (lx0 + lx1) // 2
    knob_cy = body_y0 + int((body_y1 - body_y0) * 0.56)
    dial_r = max(24, min(px(58), (body_y1 - body_y0) // 3))

    # Selector stops (-138 deg AUTO, -90 deg STBY, -42 deg MAN)
    stops = [
        (-138.0, "AUTO", th["mint"], turn_u < 0.30),
        (-90.0, "DỰ PHÒNG", th["muted"], 0.30 <= turn_u <= 0.72),
        (-42.0, "MAN", th["crimson"], turn_u > 0.72),
    ]
    arc_r = dial_r + px(18)
    for deg, lbl, scol, active in stops:
        rad = math.radians(deg)
        sx = knob_cx + math.cos(rad) * arc_r
        sy = knob_cy + math.sin(rad) * arc_r
        dr = px(5) if active else px(3)
        d.ellipse([sx - dr, sy - dr, sx + dr, sy + dr], fill=scol if active else th["grid"])
        f_lbl = _fit_font(d, lbl, px(110), px(17), "bold" if active else "mono", 9)
        _, _, ltw, lth = _text_size(d, lbl, f_lbl)
        if deg < -100:
            tx = int(round(sx - ltw - px(10)))
            ty = int(round(sy - lth * 0.6))
        elif deg > -80:
            tx = int(round(sx + px(10)))
            ty = int(round(sy - lth * 0.6))
        else:
            tx = int(round(sx - ltw // 2))
            ty = int(round(sy - lth - px(8)))
        tx = max(lx0 + px(10), min(lx1 - ltw - px(10), tx))
        ty = max(body_y0 + px(8), min(body_y1 - lth - px(8), ty))
        _draw_text_top(d, tx, ty, lbl, f_lbl, scol if active else th["muted"])

    # Outer metal bezel + rotating pointer
    ring_col = th["crimson"] if turn_u > 0.72 else th["brass"]
    d.ellipse([knob_cx - dial_r, knob_cy - dial_r, knob_cx + dial_r, knob_cy + dial_r], fill=(22, 27, 38, 245), outline=ring_col, width=max(2, lw(3)))
    inner_r = int(dial_r * 0.72)
    d.ellipse([knob_cx - inner_r, knob_cy - inner_r, knob_cx + inner_r, knob_cy + inner_r], fill=(34, 41, 56, 250), outline=(255, 255, 255, 45), width=1)
    ptr_deg = -138.0 + 96.0 * turn_u
    ptr_rad = math.radians(ptr_deg)
    d.line(
        [(knob_cx - math.cos(ptr_rad) * dial_r * 0.32, knob_cy - math.sin(ptr_rad) * dial_r * 0.32),
         (knob_cx + math.cos(ptr_rad) * dial_r * 0.88, knob_cy + math.sin(ptr_rad) * dial_r * 0.88)],
        fill=th["crimson"] if turn_u > 0.72 else th["white"],
        width=max(3, lw(6)),
    )

    knob_note = "TỰ ĐỘNG ĐIỀU ÁP: ĐÃ NGẮT" if turn_u > 0.72 else "ĐANG CHUYỂN SANG CHẾ ĐỘ TAY..."
    f_kn = _fit_font(d, knob_note, left_w - px(24), px(17), "bold", 9)
    _, _, knw, _ = _text_size(d, knob_note, f_kn)
    _draw_text_top(d, knob_cx - knw // 2, body_y1 - px(32), knob_note, f_kn, th["crimson"] if turn_u > 0.72 else th["parchment"])

    # Right panel: Outflow valve schematic (sealed vs locked open)
    d.rounded_rectangle([rx0, body_y0, rx1, body_y1], radius=px(10), fill=th["sub_bg"], outline=th["crimson"] if turn_u > 0.72 else th["grid"], width=max(1, lw(2 if turn_u > 0.72 else 1)))
    r_pad = px(18)
    r_title = "VAN XẢ ĐUÔI (OUTFLOW VALVE)"
    f_rt = _fit_font(d, r_title, rx1 - rx0 - r_pad * 2, px(19), "bold", 10)
    _draw_text_top(d, rx0 + r_pad, body_y0 + px(12), r_title, f_rt, th["white"])

    # Cross-section fuselage bottom duct + hinged valve door
    duct_x0, duct_x1 = rx0 + r_pad, rx1 - r_pad
    wall_y = body_y0 + int((body_y1 - body_y0) * 0.44)
    hinge_x = (duct_x0 + duct_x1) // 2 + px(20)
    gap_w = px(92)
    d.line([(duct_x0, wall_y), (hinge_x - gap_w, wall_y)], fill=(170, 185, 205, 220), width=max(3, lw(5)))
    d.line([(hinge_x + px(8), wall_y), (duct_x1, wall_y)], fill=(170, 185, 205, 220), width=max(3, lw(5)))

    # Valve flap swings downward as turn_u -> 1.0
    flap_ang = math.radians(176.0 - 44.0 * turn_u)
    flap_len = float(gap_w)
    fx_end = hinge_x + math.cos(flap_ang) * flap_len
    fy_end = wall_y + math.sin(flap_ang) * flap_len
    d.line([(hinge_x, wall_y), (fx_end, fy_end)], fill=th["crimson"] if turn_u > 0.55 else th["cyan"], width=max(4, lw(6)))
    d.ellipse([hinge_x - px(5), wall_y - px(5), hinge_x + px(5), wall_y + px(5)], fill=th["brass"], outline=th["white"], width=1)

    # Animated escaping compressed air streaks once open
    if turn_u > 0.35:
        flow_phase = (float(t_beat) * 2.2) % 1.0
        for fi in range(3):
            p = (flow_phase + fi * 0.33) % 1.0
            sx = hinge_x - px(58) + fi * px(20) - p * px(18)
            sy = wall_y - px(14) + p * px(62)
            ex = sx - px(10)
            ey = sy + px(16)
            fa = int(round(230 * math.sin(p * math.pi) * _clamp01((turn_u - 0.35) / 0.4)))
            d.line([(sx, sy), (ex, ey)], fill=(th["crimson"][0], th["crimson"][1], th["crimson"][2], fa), width=max(2, lw(3)))

    s1 = "TRẠNG THÁI: GHIM MỞ TỐI ĐA" if turn_u > 0.72 else "TRẠNG THÁI: CHUẨN BỊ ĐÓNG"
    s2 = "KHÍ NÉN PHỤT THẲNG RA NGOÀI KHI TĂNG GA"
    f_s1 = _fit_font(d, s1, rx1 - rx0 - r_pad * 2, px(19), "bold", 10)
    f_s2 = _fit_font(d, s2, rx1 - rx0 - r_pad * 2, px(16), "reg", 9)
    _draw_text_top(d, rx0 + r_pad, body_y1 - px(58), s1, f_s1, th["crimson"] if turn_u > 0.72 else th["mint"])
    _draw_text_top(d, rx0 + r_pad, body_y1 - px(32), s2, f_s2, th["parchment"])

    return canvas


def _apply_canvas_fade(canvas: Image.Image, t_beat: float, dur: float) -> Image.Image:
    """Apply smooth 0.22s ease-in (non-empty at t=0.05) and 0.28s ease-out envelope for persistent clusters."""
    dur_s = max(0.25, float(dur))
    t = max(0.0, float(t_beat))
    env_in = 0.25 + 0.75 * _ease_out_cubic(_clamp01(t / 0.22)) if t < 0.22 else 1.0
    rem = max(0.0, dur_s - t)
    env_out = _ease_out_cubic(_clamp01(rem / 0.28)) if (dur_s >= 1.5 and rem < 0.28) else 1.0
    env = env_in * env_out
    if env < 0.995:
        alpha_band = canvas.getchannel("A").point(lambda a: int(round(a * env)))
        canvas.putalpha(alpha_band)
    return canvas


# ---------------------------------------------------------------------------
# 11. Unified Entrypoint
# ---------------------------------------------------------------------------

def render_forensic_hud_v2(
    hud_id: str,
    spec: dict[str, Any] | None,
    t_beat: float,
    dur: float,
    width: int = 2560,
    height: int = 1440,
    variant: str = "A",
) -> Image.Image:
    """Unified entrypoint returning an RGBA `PIL.Image.Image` of size `(width, height)`."""
    raw_id = str(hud_id or "").strip().lower()
    canon = _HUD_ALIASES.get(raw_id, raw_id)
    cfg = dict(spec or {})

    if canon == "alt_pressure_divergence":
        return _apply_canvas_fade(render_alt_pressure_divergence(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "dual_horn_pulse":
        return _apply_canvas_fade(render_dual_horn_pulse(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "hypoxia_tuc_meter":
        return _apply_canvas_fade(render_hypoxia_tuc_meter(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "swiss_cheese_align":
        return _apply_canvas_fade(render_swiss_cheese_align(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "classic_vs_ng_compare":
        return _apply_canvas_fade(render_classic_vs_ng_compare(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "fuel_avoidance_vector":
        return _apply_canvas_fade(render_fuel_avoidance_vector(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "calibrated_radar_overlay":
        return _apply_canvas_fade(render_calibrated_radar_overlay(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "man_auto_switch":
        return _apply_canvas_fade(render_man_auto_switch(cfg, t_beat, dur, width=width, height=height, variant=variant), t_beat, dur)
    if canon == "lemmino_hairline_hud":
        return render_lemmino_hairline_hud(cfg, t_beat, dur, width=width, height=height)
    if canon == "chapter_title_bumper":
        return render_chapter_title_bumper(
            cfg.get("ch_num", "CH01"),
            str(cfg.get("ch_title", cfg.get("title", "CHƯƠNG 01"))),
            str(cfg.get("subtitle", cfg.get("subline", ""))),
            t_beat,
            dur,
            width=width,
            height=height,
            variant=variant,
        )
    raise ValueError(f"Unknown forensic HUD v2 widget id: {hud_id!r}. Available: {sorted(FORENSIC_HUD_V2_CATALOG)}")


__all__ = [
    "FORENSIC_HUD_V2_CATALOG",
    "VERIFIED_MAP_ANCHORS_2K",
    "render_alt_pressure_divergence",
    "render_calibrated_radar_overlay",
    "render_chapter_title_bumper",
    "render_classic_vs_ng_compare",
    "render_dual_horn_pulse",
    "render_forensic_hud_v2",
    "render_fuel_avoidance_vector",
    "render_hypoxia_tuc_meter",
    "render_lemmino_hairline_hud",
    "render_man_auto_switch",
    "render_swiss_cheese_align",
    "set_font_dir",
]
