"""30fps HUD & Layout Widget Sub-Warehouse + Bespoke Topic HUD Builder.

Holds the 14 shared HUD widgets (`HUD_WIDGET_CATALOG`), PIL font/easing helpers,
`render_hud_widget_patch(...)`, `register_bespoke_hud_widget(...)`, and
`build_bespoke_topic_hud_patch(...)` for dynamically rendering topic-specific
HUD cards, diagrams, and meters without forcing ill-fitting presets.

Supports `zero_box: bool = False` (auto-enabled for `style_mode == "v12_zero_box"`,
`channel_id == "su_ke_lai"`, or `zero_box=True` in `spec`) so cinema/history
channels render crisp shadow-only typography and thin hairlines on transparent
RGBA with zero dark `rounded_rectangle` boxes or `VS` pills.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HUD_WIDGET_CATALOG: dict[str, dict[str, Any]] = {
    "typewriter_telemetry_tag": {"kind": "corner_hud", "description": "Thẻ telemetry góc trên phải gõ từng ký tự + đèn REC nhấp nháy."},
    "altitude_stat_counter": {"kind": "data_hud", "description": "Đồng hồ đếm số liệu tăng dần theo easing + thanh tiến độ."},
    "kinetic_stamp_slam": {"kind": "impact_hud", "description": "Thẻ đóng dấu đập mạnh từ scale 1.42 -> 1.00 nhấn mạnh sự kiện sốc."},
    "xray_mode_switch_particles": {"kind": "tech_hud", "description": "Công tắc chuyển trạng thái (AUTO -> MAN) + luồng hạt khí/năng lượng X-Ray."},
    "dual_oscilloscope_compare": {"kind": "tech_hud", "description": "Dao động ký sóng đôi đối chiếu 2 tín hiệu với huy hiệu TRÙNG KHỚP."},
    "countdown_cvr_waveform": {"kind": "forensic_hud", "description": "Đồng hồ đếm ngược sinh tồn + sóng âm hộp đen CVR phản ứng giọng nói."},
    "lemmino_dossier_card": {"kind": "editorial_hud", "description": "Thẻ hồ sơ nhân vật/sự kiện tối giản trượt cubic-bezier từ mép trái."},
    "radar_bezier_trajectory": {"kind": "map_layout", "description": "Bia ngắm radar nhấp nháy + đường bay/lộ trình Bezier nét đứt tự vẽ."},
    "laser_split_screen": {"kind": "split_layout", "description": "Nhãn đối chiếu hai bên cho bố cục chia đôi tia laser."},
    "triptych_3col_evidence": {"kind": "triptych_layout", "description": "Tiêu đề 3 cột chứng cứ trượt nối tiếp + đóng dấu điểm nhấn."},
    "verdict_lower_third": {"kind": "editorial_hud", "description": "Thanh lower-third kết luận/phán quyết cải tổ trượt từ bên trái."},
    "doodle_spring_pop_badge": {"kind": "doodle_hud", "description": "Huy hiệu bật nảy lò xo (spring pop-in) cho khái niệm, tiền tệ, tâm lý."},
    "highlighter_stroke_bar": {"kind": "doodle_hud", "description": "Thanh bút dạ quang quét ngang làm nổi bật quy luật/từ khóa cốt lõi."},
    "calligraphy_quote_dissolve": {"kind": "mindful_hud", "description": "Thẻ trích dẫn triết lý viền vàng mờ ấm tan chậm cho ngách chánh niệm."},
}

BESPOKE_HUD_WIDGETS: dict[str, dict[str, Any]] = {}
_FONT_CACHE: dict[tuple[int, str], ImageFont.FreeTypeFont] = {}

_HISTORICAL_STAMP_KINDS = frozenset({
    "zero_box_chapter_card",
    "boxless_chronicle_quote",
    "chronicle_stamp",
    "zero_box_hook_title",
    "zero_box_dateline",
    "prestige_dateline",
    "v7_hook_headline",
    "v7_stat_versus",
    "gis_tactical_map_v8",
})

_ZERO_BOX_ONLY_KINDS = frozenset({
    "zero_box_chapter_card",
    "boxless_chronicle_quote",
    "chronicle_stamp",
    "zero_box_hook_title",
    "zero_box_dateline",
})


def _get_font(size: int, style: str = "bold") -> ImageFont.FreeTypeFont:
    key = (size, style)
    if key not in _FONT_CACHE:
        candidates = {
            "mono": ("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
            "reg": ("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            "bold": ("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        }.get(style, ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",))
        chosen = next((p for p in candidates if Path(p).is_file()), None)
        _FONT_CACHE[key] = ImageFont.truetype(chosen, size) if chosen else ImageFont.load_default()
    return _FONT_CACHE[key]


def _ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def is_zero_box_enabled(spec: dict[str, Any] | None = None, zero_box: bool = False) -> bool:
    """Return True when Zero-Box cinema typography must be used instead of boxed cards."""
    if zero_box:
        return True
    if not spec:
        return False
    if bool(spec.get("zero_box")):
        return True
    if str(spec.get("style_mode", "")).strip().lower() == "v12_zero_box":
        return True
    if str(spec.get("channel_id", "")).strip().lower().replace("-", "_") == "su_ke_lai":
        return True
    if str(spec.get("kicker", "")).strip().upper().startswith("SU_KE_LAI"):
        return True
    if str(spec.get("kind", "")).strip().lower() in _ZERO_BOX_ONLY_KINDS:
        return True
    return False


def _scale_alpha(rgba: tuple[int, int, int, int], alpha_scale: float) -> tuple[int, int, int, int]:
    return (rgba[0], rgba[1], rgba[2], max(0, min(255, int(round(rgba[3] * alpha_scale)))))


def _draw_shadow_text(
    canvas: Image.Image,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    *,
    shadow_sigma: float = 2.0,
    shadow_offset: tuple[int, int] = (2, 2),
    shadow_alpha: int = 205,
) -> None:
    """Draw crisp shadow-only typography with Gaussian optical drop-shadow and zero backing box."""
    if not text or fill[3] <= 0:
        return
    a_ratio = max(0.0, min(1.0, fill[3] / 255.0))
    eff_shadow_a = max(0, min(255, int(round(shadow_alpha * a_ratio))))
    x, y = int(xy[0]), int(xy[1])
    if eff_shadow_a > 2:
        shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_layer, "RGBA")
        sdraw.text(
            (x + shadow_offset[0], y + shadow_offset[1]),
            text,
            font=font,
            fill=(0, 0, 0, eff_shadow_a),
            stroke_width=2,
            stroke_fill=(0, 0, 0, eff_shadow_a),
        )
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_sigma))
        canvas.alpha_composite(shadow_layer)
    fdraw = ImageDraw.Draw(canvas, "RGBA")
    fdraw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        stroke_width=1,
        stroke_fill=(8, 8, 12, max(0, min(220, int(round(205 * a_ratio))))),
    )


def _draw_hairline(
    canvas: Image.Image,
    p0: tuple[int, int],
    p1: tuple[int, int],
    fill: tuple[int, int, int, int],
    width: int = 2,
) -> None:
    """Draw a thin horizontal/vertical filament with subtle 1px shadow (no filled boxes)."""
    if fill[3] <= 0:
        return
    d = ImageDraw.Draw(canvas, "RGBA")
    sh_a = max(0, min(190, int(round(fill[3] * 0.65))))
    d.line([(p0[0] + 1, p0[1] + 2), (p1[0] + 1, p1[1] + 2)], fill=(0, 0, 0, sh_a), width=width)
    d.line([p0, p1], fill=fill, width=width)


def _draw_hairline_progress(
    canvas: Image.Image,
    x0: int,
    y: int,
    span_w: int,
    ratio: float,
    track_rgba: tuple[int, int, int, int],
    active_rgba: tuple[int, int, int, int],
    *,
    show_diamond: bool = True,
) -> None:
    """Draw a boxless graduated filament meter with diamond tip marker."""
    clamped = max(0.0, min(1.0, ratio))
    _draw_hairline(canvas, (x0, y), (x0 + span_w, y), track_rgba, width=2)
    cur_x = x0 + max(4, int(round(span_w * clamped)))
    _draw_hairline(canvas, (x0, y), (cur_x, y), active_rgba, width=3)
    if show_diamond:
        d = ImageDraw.Draw(canvas, "RGBA")
        dm = 6
        d.polygon(
            [(cur_x, y - dm), (cur_x + dm, y), (cur_x, y + dm), (cur_x - dm, y)],
            fill=active_rgba,
        )


def _render_zero_box_editorial_patch(
    kicker: str,
    headline: str,
    subline: str,
    *,
    pw: int,
    ph: int,
    acc: tuple[int, int, int, int],
    fg_col: tuple[int, int, int, int],
    sub_col: tuple[int, int, int, int],
    alpha_scale: float = 1.0,
    show_filament: bool = True,
    kicker_size: int = 22,
    headline_size: int = 36,
    subline_size: int = 22,
) -> Image.Image:
    """Render clean shadow-only typography block with optional thin gold filament on transparent RGBA."""
    patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    if alpha_scale <= 0.01:
        return patch
    pad_x = 28
    _draw_shadow_text(patch, (pad_x, 18), kicker, _get_font(kicker_size, "mono"), _scale_alpha(acc, alpha_scale))
    _draw_shadow_text(
        patch,
        (pad_x, 54),
        headline,
        _get_font(headline_size, "bold"),
        _scale_alpha(fg_col, alpha_scale),
    )
    if show_filament:
        _draw_hairline(patch, (pad_x, 106), (pad_x + 56, 106), _scale_alpha(acc, alpha_scale * 0.9), width=2)
    if subline:
        sub_x = pad_x + (72 if show_filament else 0)
        sub_y = 94 if show_filament else 112
        _draw_shadow_text(
            patch,
            (sub_x, sub_y),
            subline,
            _get_font(subline_size, "bold"),
            _scale_alpha(sub_col, alpha_scale),
        )
    return patch


def register_bespoke_hud_widget(
    widget_id: str,
    spec: dict[str, Any] | None = None,
    renderer: Callable[..., tuple[int, int, Image.Image] | None] | None = None,
    kind: str = "bespoke_hud",
    description: str = "",
    promote: bool = False,
) -> dict[str, Any]:
    """Register a custom per-video HUD widget spec or renderer."""
    entry: dict[str, Any] = {
        "kind": kind,
        "description": description or f"Bespoke HUD widget '{widget_id}'",
        "spec": dict(spec or {}),
        "renderer": renderer,
        "is_bespoke": True,
    }
    BESPOKE_HUD_WIDGETS[widget_id] = entry
    if promote:
        HUD_WIDGET_CATALOG[widget_id] = {"kind": kind, "description": entry["description"], "is_bespoke": True}
    return entry


def build_bespoke_topic_hud_patch(
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    amp: float = 0.3,
    width: int = 2560,
    height: int = 1440,
    zero_box: bool = False,
) -> tuple[int, int, Image.Image]:
    """Dynamically render a topic-specific custom HUD card, diagram, or meter from `spec`."""
    use_zero_box = is_zero_box_enabled(spec, zero_box=zero_box)
    kind = str(spec.get("kind", "telemetry_card")).lower()
    theme = str(spec.get("theme", "dark")).lower()
    default_acc = (232, 194, 106, 255) if use_zero_box else (32, 212, 248, 255)
    acc = tuple(spec.get("accent_rgba", default_acc))
    sec = tuple(spec.get("secondary_rgba", (212, 168, 72, 255)))

    if use_zero_box:
        fg_col = (248, 244, 232, 255)
        sub_col = (224, 214, 192, 245)
        bg_col = (0, 0, 0, 0)
    elif theme in ("light", "doodle"):
        bg_col = (250, 248, 240, 238)
        fg_col = (18, 24, 38, 255)
        sub_col = (71, 85, 105, 255)
    elif theme in ("warm", "mindful"):
        bg_col = (18, 14, 12, 212)
        fg_col = (250, 244, 232, 255)
        sub_col = (232, 200, 142, 255)
    else:
        bg_col = (10, 14, 22, 226)
        fg_col = (246, 248, 250, 255)
        sub_col = (182, 194, 210, 255)

    slide = _ease_out_cubic(min(1.0, t_beat / 0.32))
    prog = _ease_out_cubic(min(1.0, t_beat / max(0.35, min(0.85, dur * 0.6))))
    default_kicker = "CHUYÊN ĐỀ LỊCH SỬ • ZERO-BOX" if use_zero_box else "CHUYÊN ĐỀ ĐẶC THÙ • BESPOKE HUD"
    kicker = str(spec.get("kicker", default_kicker))
    headline = str(spec.get("headline", spec.get("topic", "PHÂN TÍCH CHUYÊN SÂU")))
    default_subline = "" if (use_zero_box and kind in _HISTORICAL_STAMP_KINDS) else "DỮ LIỆU ĐƯỢC TỔNG HỢP THEO NGỮ CẢNH VIDEO"
    subline = str(spec.get("subline", default_subline))

    if kind in ("metric_meter", "gauge"):
        pw, ph = 760, 200
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        val = float(spec.get("value", 78.0))
        max_val = max(1.0, float(spec.get("max_value", 100.0)))
        unit = str(spec.get("unit", "%"))
        cur_val = val * prog
        ratio = max(0.0, min(1.0, cur_val / max_val))
        val_txt = f"{cur_val:.1f} {unit}" if abs(val % 1) > 1e-3 else f"{int(round(cur_val))} {unit}"
        if use_zero_box:
            _draw_shadow_text(patch, (28, 18), kicker, _get_font(21, "mono"), acc)
            _draw_shadow_text(patch, (28, 50), headline[:42], _get_font(34, "bold"), fg_col)
            _draw_shadow_text(patch, (28, 96), val_txt, _get_font(44, "bold"), sec)
            _draw_hairline_progress(patch, 28, 168, pw - 56, ratio, (255, 255, 255, 72), acc)
        else:
            d = ImageDraw.Draw(patch, "RGBA")
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=16, fill=bg_col, outline=acc, width=3)
            d.text((28, 18), kicker, font=_get_font(21, "mono"), fill=acc)
            d.text((28, 50), headline[:42], font=_get_font(34, "bold"), fill=fg_col)
            d.text((28, 96), val_txt, font=_get_font(44, "bold"), fill=sec)
            d.rounded_rectangle([28, 160, pw - 28, 176], radius=8, fill=(255, 255, 255, 36))
            d.rounded_rectangle([28, 160, 28 + max(12, int((pw - 56) * ratio)), 176], radius=8, fill=acc)
        return 64, int(1000 + (1.0 - slide) * 36), patch

    if kind in ("timeline_nodes", "chain"):
        nodes = list(spec.get("nodes", ["01. KHỞI NGUỒN", "02. CƠ CHẾ", "03. TÁC ĐỘNG"]))[:4]
        pw, ph = 1120, 184
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        if use_zero_box:
            _draw_shadow_text(patch, (28, 16), kicker, _get_font(21, "mono"), acc)
            _draw_shadow_text(patch, (28, 46), headline[:58], _get_font(28, "bold"), fg_col)
            _draw_hairline(patch, (60, 122), (60 + int((pw - 120) * prog), 122), sec, width=3)
        else:
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=16, fill=bg_col, outline=acc, width=3)
            d.text((28, 16), kicker, font=_get_font(21, "mono"), fill=acc)
            d.text((28, 46), headline[:58], font=_get_font(28, "bold"), fill=fg_col)
            d.line([(60, 122), (60 + int((pw - 120) * prog), 122)], fill=sec, width=4)
        n_nodes = max(1, len(nodes))
        span_w = (pw - 80) // n_nodes
        d = ImageDraw.Draw(patch, "RGBA")
        for idx, label in enumerate(nodes):
            cx = 60 + idx * span_w + span_w // 4
            active = prog >= (idx / max(1, n_nodes))
            col = acc if active else sub_col
            if use_zero_box:
                d.ellipse([cx - 9, 113, cx + 9, 131], fill=col, outline=fg_col, width=2)
                _draw_shadow_text(
                    patch,
                    (max(24, cx - 50), 142),
                    str(label)[:20],
                    _get_font(20, "bold"),
                    fg_col if active else sub_col,
                )
            else:
                d.ellipse([cx - 12, 110, cx + 12, 134], fill=col, outline=fg_col, width=2)
                d.text((max(24, cx - 50), 142), str(label)[:20], font=_get_font(20, "bold"), fill=fg_col if active else sub_col)
        return 64, int(1005 + (1.0 - slide) * 36), patch

    if kind in ("comparison_matrix", "split_card", "v7_stat_versus"):
        pw, ph = 980, 196
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        left_title = str(spec.get("left_title") or spec.get("left_label") or "BIẾN SỐ A")
        left_val = str(spec.get("left_value") or spec.get("left_stat") or "GIÁ TRỊ BAN ĐẦU")
        right_title = str(spec.get("right_title") or spec.get("right_label") or "BIẾN SỐ B")
        right_val = str(spec.get("right_value") or spec.get("right_stat") or "KẾT QUẢ ĐỐI CHIẾU")
        if use_zero_box:
            # Zero-Box contrast: never draw boxed card or VS badge pill; thin vertical filament only.
            _draw_shadow_text(patch, (28, 16), kicker, _get_font(21, "mono"), acc)
            _draw_hairline(patch, (pw // 2, 54), (pw // 2, ph - 24), sec, width=2)
            _draw_shadow_text(patch, (28, 56), left_title[:26], _get_font(24, "mono"), sec)
            _draw_shadow_text(patch, (28, 96), left_val[:28], _get_font(32, "bold"), fg_col)
            _draw_shadow_text(patch, (pw // 2 + 28, 56), right_title[:26], _get_font(24, "mono"), acc)
            _draw_shadow_text(patch, (pw // 2 + 28, 96), right_val[:28], _get_font(32, "bold"), fg_col)
        else:
            d = ImageDraw.Draw(patch, "RGBA")
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=16, fill=bg_col, outline=acc, width=3)
            d.text((28, 16), kicker, font=_get_font(21, "mono"), fill=acc)
            d.line([(pw // 2, 54), (pw // 2, ph - 20)], fill=sec, width=3)
            d.text((28, 56), left_title[:26], font=_get_font(24, "mono"), fill=sec)
            d.text((28, 96), left_val[:28], font=_get_font(32, "bold"), fill=fg_col)
            d.text((pw // 2 + 28, 56), right_title[:26], font=_get_font(24, "mono"), fill=acc)
            d.text((pw // 2 + 28, 96), right_val[:28], font=_get_font(32, "bold"), fill=fg_col)
        return 64, int(1000 + (1.0 - slide) * 36), patch

    if kind in ("sonar_radial", "map_pin"):
        pw, ph = 780, 210
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        if not use_zero_box:
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=16, fill=bg_col, outline=acc, width=3)
        cx, cy = 105, 105
        for r in (28, 52, 76):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(acc[0], acc[1], acc[2], 130), width=2)
        ang = t_beat * 2.8 + amp * 0.5
        d.line([(cx, cy), (cx + int(74 * math.cos(ang)), cy + int(74 * math.sin(ang)))], fill=sec, width=4)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=acc)
        if use_zero_box:
            _draw_shadow_text(patch, (210, 26), kicker, _get_font(21, "mono"), acc)
            _draw_shadow_text(patch, (210, 66), headline[:34], _get_font(34, "bold"), fg_col)
            _draw_shadow_text(patch, (210, 122), subline[:44], _get_font(22, "reg"), sub_col)
        else:
            d.text((210, 26), kicker, font=_get_font(21, "mono"), fill=acc)
            d.text((210, 66), headline[:34], font=_get_font(34, "bold"), fill=fg_col)
            d.text((210, 122), subline[:44], font=_get_font(22, "reg"), fill=sub_col)
        return 64, int(990 + (1.0 - slide) * 36), patch

    # Default ("telemetry_card") and Zero-Box historical stamp kinds
    pw, ph = 880, 184
    if use_zero_box:
        patch = _render_zero_box_editorial_patch(
            kicker,
            headline[:48],
            subline[:56],
            pw=pw,
            ph=ph,
            acc=sec,
            fg_col=fg_col,
            sub_col=sub_col,
            show_filament=bool(subline),
        )
        return 64, int(1010 + (1.0 - slide) * 24), patch

    patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(patch, "RGBA")
    d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=14, fill=bg_col, outline=acc, width=3)
    d.rectangle([0, 0, 10, ph - 2], fill=sec)
    d.text((34, 20), kicker, font=_get_font(22, "mono"), fill=sec)
    d.text((34, 58), headline[:44], font=_get_font(36, "bold"), fill=fg_col)
    d.text((34, 118), subline[:56], font=_get_font(22, "bold"), fill=sub_col)
    x_slide = int(round(-pw + (pw + 64) * slide))
    return x_slide, 1010, patch


def render_hud_widget_patch(
    widget_id: str,
    spec: dict[str, Any],
    t_beat: float,
    dur: float,
    amp: float = 0.3,
    width: int = 2560,
    height: int = 1440,
    zero_box: bool = False,
) -> tuple[int, int, Image.Image] | None:
    """Render any of the 14 shared HUD widgets or bespoke topic HUDs as (x0, y0, RGBA PIL.Image)."""
    use_zero_box = is_zero_box_enabled(spec, zero_box=zero_box)

    if widget_id in BESPOKE_HUD_WIDGETS:
        entry = BESPOKE_HUD_WIDGETS[widget_id]
        merged = {**entry.get("spec", {}), **spec}
        if use_zero_box:
            merged["zero_box"] = True
        if callable(entry.get("renderer")):
            return entry["renderer"](merged, t_beat, dur, amp=amp, width=width, height=height)
        return build_bespoke_topic_hud_patch(merged, t_beat, dur, amp=amp, width=width, height=height, zero_box=use_zero_box)

    if widget_id == "bespoke_topic_hud" or spec.get("is_bespoke") or widget_id in _HISTORICAL_STAMP_KINDS:
        delegated_spec = dict(spec)
        if widget_id in _HISTORICAL_STAMP_KINDS:
            delegated_spec.setdefault("kind", widget_id)
        return build_bespoke_topic_hud_patch(delegated_spec, t_beat, dur, amp=amp, width=width, height=height, zero_box=use_zero_box)

    acc = tuple(spec.get("accent_rgba", (212, 168, 72, 255) if use_zero_box else (205, 52, 48, 255)))
    u = max(0.0, min(1.0, t_beat / max(0.25, dur)))
    white = (246, 248, 250, 255)
    ivory = (248, 244, 232, 255)
    parchment = (232, 223, 200, 255)
    brass = (212, 168, 72, 255)
    crimson = (205, 52, 48, 255)
    cyan = (32, 212, 248, 255)
    muted = (182, 194, 210, 255)
    dark_card = (10, 14, 22, 222)

    if widget_id == "typewriter_telemetry_tag":
        tag = str(spec.get("tag", "HỒ SƠ DỮ LIỆU • 30FPS TELEMETRY"))
        chars_vis = max(1, min(len(tag), int(math.floor(t_beat * 44.0)) + 2))
        shown = tag[:chars_vis]
        f_tag = _get_font(24, "mono")
        dt = ImageDraw.Draw(Image.new("RGBA", (10, 10)), "RGBA")
        tb_full = dt.textbbox((0, 0), tag, font=f_tag)
        tw, th = (tb_full[2] - tb_full[0]) + 62, (tb_full[3] - tb_full[1]) + 26
        patch = Image.new("RGBA", (tw + 4, th + 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        dot_c = (235, 55, 50, 255) if (int(t_beat * 4.0) % 2 == 0) else (110, 30, 28, 200)
        if use_zero_box:
            d.ellipse([16, th // 2 - 5, 26, th // 2 + 5], fill=dot_c)
            _draw_shadow_text(patch, (38, 12 - tb_full[1]), shown, f_tag, parchment)
            if chars_vis < len(tag) or (int(t_beat * 3.0) % 2 == 0):
                sb = dt.textbbox((0, 0), shown, font=f_tag)
                cx = 38 + (sb[2] - sb[0]) + 4
                _draw_hairline(patch, (cx, 12), (cx, th - 12), acc, width=2)
        else:
            d.rounded_rectangle([0, 0, tw, th], radius=10, fill=(8, 11, 18, 206), outline=acc, width=2)
            d.ellipse([16, th // 2 - 6, 28, th // 2 + 6], fill=dot_c)
            d.text((38, 12 - tb_full[1]), shown, font=f_tag, fill=parchment)
            if chars_vis < len(tag) or (int(t_beat * 3.0) % 2 == 0):
                sb = dt.textbbox((0, 0), shown, font=f_tag)
                cx = 38 + (sb[2] - sb[0]) + 4
                d.rectangle([cx, 11, cx + 11, th - 11], fill=acc)
        return width - 64 - patch.width, 48, patch

    if widget_id == "altitude_stat_counter":
        pw, ph = 680, 175
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        slide_in = _ease_out_cubic(min(1.0, t_beat / 0.25))
        prog = _ease_out_cubic(min(1.0, t_beat / 0.58))
        target_val = float(spec.get("target_value", 10400))
        unit = str(spec.get("unit", "MÉT"))
        kicker = str(spec.get("kicker", "CHỈ SỐ ĐỊNH LƯỢNG • PHÂN TÍCH DỮ LIỆU"))
        val_i = int(round(target_val * prog))
        val_str = f"{val_i:,} {unit}".replace(",", ".")
        if use_zero_box:
            a_sc = max(0.15, slide_in)
            _draw_shadow_text(patch, (28, 18), kicker, _get_font(22, "mono"), _scale_alpha(acc, a_sc))
            _draw_shadow_text(patch, (28, 56), val_str, _get_font(68, "bold"), _scale_alpha(ivory, a_sc))
            _draw_hairline_progress(patch, 28, 152, pw - 56, prog, (255, 255, 255, 70), _scale_alpha(acc, a_sc))
        else:
            d = ImageDraw.Draw(patch, "RGBA")
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=14, fill=(10, 14, 22, int(222 * slide_in)), outline=acc, width=3)
            d.text((28, 18), kicker, font=_get_font(22, "mono"), fill=acc)
            d.text((28, 56), val_str, font=_get_font(68, "bold"), fill=white)
            d.rounded_rectangle([28, 148, pw - 28, 158], radius=5, fill=(255, 255, 255, 35))
            d.rounded_rectangle([28, 148, 28 + int((pw - 56) * prog), 158], radius=5, fill=acc)
        return 64, int(1020 + (1.0 - slide_in) * 40), patch

    if widget_id == "kinetic_stamp_slam":
        if t_beat < 0.10:
            return None
        p = min(1.0, (t_beat - 0.10) / 0.20)
        sc = 1.42 - 0.42 * _ease_out_cubic(p)
        if 0.85 <= p < 1.0:
            sc += 0.03 * math.sin((p - 0.85) * 40.0)
        base_w, base_h = 840, 178
        kicker = str(spec.get("kicker", "CẢNH BÁO TRẠNG THÁI"))
        headline = str(spec.get("headline", "ĐIỂM BÙNG PHÁT"))
        subline = str(spec.get("subline", "XÁC NHẬN DỮ LIỆU CHÍNH XÁC"))
        if use_zero_box:
            patch = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
            _draw_shadow_text(patch, (34, 22), kicker, _get_font(24, "mono"), brass)
            _draw_shadow_text(patch, (34, 58), headline, _get_font(54, "bold"), crimson)
            _draw_shadow_text(patch, (34, 126), subline, _get_font(23, "bold"), ivory)
        else:
            patch = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
            d = ImageDraw.Draw(patch, "RGBA")
            d.rounded_rectangle([4, 4, base_w - 4, base_h - 4], radius=16, fill=(14, 10, 14, 232), outline=crimson, width=5)
            d.text((34, 22), kicker, font=_get_font(24, "mono"), fill=brass)
            d.text((34, 58), headline, font=_get_font(54, "bold"), fill=crimson)
            d.text((34, 126), subline, font=_get_font(23, "bold"), fill=white)
        if abs(sc - 1.0) > 0.01:
            nw, nh = int(round(base_w * sc)), int(round(base_h * sc))
            patch = patch.resize((nw, nh), Image.Resampling.BILINEAR)
            return max(12, 64 - (nw - base_w) // 4), max(140, 1010 - (nh - base_h) // 2), patch
        return 64, 1010, patch

    if widget_id == "xray_mode_switch_particles":
        pw, ph = 780, 190
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        kicker = str(spec.get("kicker", "X-RAY CƠ CHẾ // CHUYỂN TRẠNG THÁI"))
        left_label = str(spec.get("left_label", "AUTO (MẶC ĐỊNH)"))
        right_label = str(spec.get("right_label", "MAN (CAN THIỆP)"))
        flip_u = _ease_out_cubic(min(1.0, max(0.0, (t_beat - 0.25) / 0.35)))
        if use_zero_box:
            _draw_shadow_text(patch, (26, 18), kicker, _get_font(22, "mono"), brass)
            _draw_shadow_text(patch, (26, 66), left_label, _get_font(24, "bold"), ivory if flip_u < 0.5 else muted)
            _draw_shadow_text(patch, (336, 66), right_label, _get_font(24, "bold"), brass if flip_u > 0.3 else muted)
            active_x0, active_x1 = (26, 260) if flip_u < 0.5 else (336, 580)
            _draw_hairline(patch, (active_x0, 104), (active_x1, 104), crimson if flip_u > 0.3 else brass, width=3)
            _draw_hairline(patch, (26, 145), (pw - 26, 145), (255, 255, 255, 72), width=2)
            d = ImageDraw.Draw(patch, "RGBA")
            for k in range(12):
                px = 42 + int(((k / 12.0 + t_beat * 0.95) % 1.0) * (pw - 88))
                d.ellipse([px - 6, 139, px + 6, 151], fill=brass)
        else:
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=14, fill=(8, 14, 24, 218), outline=cyan, width=2)
            d.text((26, 18), kicker, font=_get_font(22, "mono"), fill=cyan)
            d.rounded_rectangle([26, 56, 300, 108], radius=10, fill=(32, 212, 248, int(190 * (1.0 - flip_u))), outline=(255, 255, 255, 50), width=2)
            d.text((54, 68), left_label, font=_get_font(23, "bold"), fill=white if flip_u < 0.5 else muted)
            d.rounded_rectangle([320, 56, 630, 108], radius=10, fill=(205, 52, 48, int(40 + 190 * flip_u)), outline=crimson if flip_u > 0.3 else (255, 255, 255, 50), width=3)
            d.text((346, 68), right_label, font=_get_font(23, "bold"), fill=white if flip_u > 0.3 else muted)
            d.rounded_rectangle([26, 128, pw - 26, 162], radius=8, fill=(14, 24, 38, 220), outline=cyan, width=2)
            for k in range(12):
                px = 42 + int(((k / 12.0 + t_beat * 0.95) % 1.0) * (pw - 88))
                d.ellipse([px - 7, 138, px + 7, 152], fill=cyan)
        return 64, 1005, patch

    if widget_id == "dual_oscilloscope_compare":
        pw, ph = 880, 210
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        kicker = str(spec.get("kicker", "ĐỐI CHIẾU TÍN HIỆU ĐÔI • PHỔ TẦN SỐ"))
        badge = str(spec.get("badge", "TRÙNG ÂM 100%"))
        w1 = str(spec.get("wave1_label", "TÍN HIỆU MẪU A"))
        w2 = str(spec.get("wave2_label", "TÍN HIỆU MẪU B"))
        if use_zero_box:
            _draw_shadow_text(patch, (26, 18), kicker, _get_font(21, "mono"), brass)
            _draw_shadow_text(patch, (pw - 236, 18), badge, _get_font(20, "bold"), crimson)
            _draw_shadow_text(patch, (26, 81), w1, _get_font(20, "bold"), crimson)
            _draw_shadow_text(patch, (26, 142), w2, _get_font(20, "bold"), brass)
        else:
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=14, fill=(8, 14, 24, 220), outline=crimson, width=2)
            d.text((26, 18), kicker, font=_get_font(21, "mono"), fill=brass)
            d.rounded_rectangle([pw - 246, 12, pw - 16, 48], radius=8, fill=crimson)
            d.text((pw - 226, 18), badge, font=_get_font(20, "bold"), fill=white)
            d.text((26, 81), w1, font=_get_font(20, "bold"), fill=crimson)
            d.text((26, 142), w2, font=_get_font(20, "bold"), fill=cyan)
        pts1, pts2 = [], []
        pm = 0.5 + 0.5 * math.sin(t_beat * 14.0) + amp * 0.4
        for xi in range(280, pw - 26, 8):
            yv = math.sin((xi - 280) * 0.045 - t_beat * 16.0) * (10.0 + 14.0 * pm) * math.sin((xi - 280) / float(pw - 306) * math.pi)
            pts1.append((xi, 95 + yv))
            pts2.append((xi, 156 + yv))
        if len(pts1) > 1:
            d = ImageDraw.Draw(patch, "RGBA")
            d.line(pts1, fill=crimson, width=4)
            d.line(pts2, fill=brass if use_zero_box else cyan, width=4)
        return 64, 985, patch

    if widget_id == "countdown_cvr_waveform":
        pw, ph = 860, 210
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        rem_s = max(0.0, float(spec.get("countdown_from", 90.0)) * (1.0 - u))
        kicker = str(spec.get("kicker", "BLACK BOX TELEMETRY • THỜI GIAN ĐẾM NGƯỢC"))
        metric_txt = f"{spec.get('metric_prefix', 'THỜI GIAN CÒN LẠI')}: {rem_s:04.1f}s"
        val_col = crimson if rem_s < 45 else brass
        if use_zero_box:
            _draw_shadow_text(patch, (28, 18), kicker, _get_font(21, "mono"), parchment)
            _draw_shadow_text(patch, (28, 52), metric_txt, _get_font(48, "bold"), val_col)
            _draw_hairline_progress(patch, 28, 128, 392, 1.0 - u, (255, 255, 255, 64), crimson)
        else:
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=14, fill=(7, 8, 12, 226), outline=crimson, width=2)
            d.text((28, 18), kicker, font=_get_font(21, "mono"), fill=parchment)
            d.text((28, 52), metric_txt, font=_get_font(48, "bold"), fill=val_col)
            d.rounded_rectangle([28, 122, 420, 134], radius=6, fill=(255, 255, 255, 30))
            d.rounded_rectangle([28, 122, 28 + max(8, int(392 * (1.0 - u))), 134], radius=6, fill=crimson)
        pts = [(xi, 172 + math.sin(xi * 0.08 - t_beat * 26.0) * (5.0 + 34.0 * amp) * math.sin((xi - 28) / float(pw - 56) * math.pi)) for xi in range(28, pw - 28, 6)]
        if len(pts) > 1:
            d = ImageDraw.Draw(patch, "RGBA")
            d.line(pts, fill=crimson, width=4)
        return 64, 985, patch

    if widget_id == "lemmino_dossier_card":
        pw, ph = 840, 168
        slide = _ease_out_cubic(min(1.0, t_beat / 0.38))
        kicker = str(spec.get("kicker", "TƯ LIỆU LƯU TRỮ • CHỨNG CỨ ĐỘC LẬP"))
        headline = str(spec.get("headline", "HỒ SƠ NHÂN VẬT / SỰ KIỆN"))
        subline = str(spec.get("subline", "MỐC THỜI GIAN ĐƯỢC XÁC MINH TRONG TÀI LIỆU"))
        if use_zero_box:
            patch = _render_zero_box_editorial_patch(
                kicker,
                headline,
                subline,
                pw=pw,
                ph=ph,
                acc=brass,
                fg_col=ivory,
                sub_col=parchment,
                alpha_scale=max(0.15, slide),
                show_filament=True,
            )
            return 64, int(1020 + (1.0 - slide) * 24), patch
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=12, fill=(10, 12, 18, 224), outline=parchment, width=2)
        d.rectangle([0, 0, 10, ph - 2], fill=brass)
        d.text((34, 20), kicker, font=_get_font(22, "mono"), fill=brass)
        d.text((34, 56), headline, font=_get_font(36, "bold"), fill=white)
        d.text((34, 112), subline, font=_get_font(22, "bold"), fill=parchment)
        x_slide = int(round(-pw + (pw + 64) * slide))
        return x_slide, 1020, patch

    if widget_id == "radar_bezier_trajectory":
        patch = Image.new("RGBA", (width, 920), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        oy = 160
        p0, p1, pm = (860, 820 - oy), (1720, 420 - oy), (1180, 470 - oy)
        prog = _ease_out_cubic(min(1.0, max(0.0, (t_beat - 0.12) / 1.0)))
        pts = [((1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * pm[0] + tt ** 2 * p1[0], (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * pm[1] + tt ** 2 * p1[1]) for tt in (k / 80.0 for k in range(max(2, int(80 * prog)) + 1))]
        for k in range(0, len(pts) - 1, 3):
            d.line([pts[k], pts[min(len(pts) - 1, k + 2)]], fill=crimson, width=7)
        for pt, col in ((p0, crimson), (p1, brass)):
            pr = 40 + int(10 * math.sin(t_beat * 7.5))
            d.ellipse([pt[0] - pr, pt[1] - pr, pt[0] + pr, pt[1] + pr], outline=col, width=4)
            d.ellipse([pt[0] - 10, pt[1] - 10, pt[0] + 10, pt[1] + 10], fill=col, outline=white, width=2)
        return 0, oy, patch

    if widget_id == "laser_split_screen":
        slide = _ease_out_cubic(min(1.0, max(0.0, (t_beat - 0.15) / 0.35)))
        if slide <= 0.02:
            return None
        patch = Image.new("RGBA", (width, 160), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        pw = width // 2
        off = int(round((1.0 - slide) * 140))
        for bx, k_t, t_t, col in (
            (52 - off, str(spec.get("left_kicker", "PHƯƠNG ÁN A")), str(spec.get("left_title", "KỊCH BẢN BAN ĐẦU")), crimson),
            (pw + 62 + off, str(spec.get("right_kicker", "PHƯƠNG ÁN B")), str(spec.get("right_title", "BIẾN ĐỘNG THỰC TẾ")), brass),
        ):
            if use_zero_box:
                _draw_shadow_text(patch, (bx + 28, 22), k_t, _get_font(22, "mono"), col)
                _draw_shadow_text(patch, (bx + 28, 56), t_t, _get_font(34, "bold"), ivory)
                _draw_hairline(patch, (bx + 28, 108), (bx + 240, 108), col, width=2)
            else:
                d.rounded_rectangle([bx, 8, bx + 540, 128], radius=14, fill=dark_card, outline=col, width=3)
                d.text((bx + 28, 22), k_t, font=_get_font(22, "mono"), fill=col)
                d.text((bx + 28, 56), t_t, font=_get_font(34, "bold"), fill=white)
        return 0, 160, patch

    if widget_id == "triptych_3col_evidence":
        patch = Image.new("RGBA", (width, 130), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        col_w = (width - 128 - 56) // 3
        headers = list(spec.get("headers", ["01. NGUYÊN NHÂN", "02. BƯỚC NGOẶT", "03. HỆ QUẢ"]))[:3]
        for ci, h_txt in enumerate(headers):
            cx = 64 + ci * (col_w + 28)
            col_c = brass if ci == 1 else (ivory if use_zero_box else white)
            if use_zero_box:
                _draw_shadow_text(patch, (cx + 32, 22), h_txt, _get_font(32, "bold"), col_c)
                _draw_hairline(patch, (cx + 32, 74), (cx + 220, 74), col_c, width=2)
            else:
                d.rectangle([cx, 0, cx + col_w, 84], fill=(8, 12, 20, 224), outline=brass if ci == 1 else (255, 255, 255, 60), width=3)
                d.text((cx + 32, 22), h_txt, font=_get_font(32, "bold"), fill=col_c)
        return 0, 140, patch

    if widget_id == "verdict_lower_third":
        v_slide = _ease_out_cubic(min(1.0, t_beat / 0.34))
        pw, ph = 1480, 136
        kicker = str(spec.get("kicker", "KẾT LUẬN TRỌNG TÂM"))
        headline = str(spec.get("headline", "BÀI HỌC CỐT LÕI VÀ TÁC ĐỘNG DÀI HẠN"))
        if use_zero_box:
            patch = _render_zero_box_editorial_patch(
                kicker,
                headline,
                "",
                pw=pw,
                ph=ph,
                acc=brass,
                fg_col=ivory,
                sub_col=parchment,
                alpha_scale=max(0.15, v_slide),
                show_filament=True,
                kicker_size=23,
                headline_size=34,
            )
            return 64, int(960 + (1.0 - v_slide) * 24), patch
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=14, fill=dark_card, outline=brass, width=3)
        d.text((28, 16), kicker, font=_get_font(23, "mono"), fill=brass)
        d.text((28, 54), headline, font=_get_font(34, "bold"), fill=white)
        return int(round(64 - (1.0 - v_slide) * 320)), 960, patch

    if widget_id == "doodle_spring_pop_badge":
        p = min(1.0, t_beat / 0.28)
        sc = _ease_out_cubic(p) + 0.08 * math.sin(p * math.pi * 2.0) * (1.0 - p)
        bw, bh = 620, 136
        kicker = str(spec.get("kicker", "ĐIỂM MẤU CHỐT"))
        headline = str(spec.get("headline", "NGUYÊN LÝ GHI NHỚ NHANH"))
        if use_zero_box:
            patch = _render_zero_box_editorial_patch(
                kicker,
                headline,
                "",
                pw=bw,
                ph=bh,
                acc=acc,
                fg_col=ivory,
                sub_col=parchment,
                show_filament=False,
                kicker_size=22,
                headline_size=36,
            )
        else:
            patch = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
            d = ImageDraw.Draw(patch, "RGBA")
            d.rounded_rectangle([4, 4, bw - 4, bh - 4], radius=22, fill=(250, 248, 240, 240), outline=acc, width=5)
            d.text((28, 22), kicker, font=_get_font(22, "bold"), fill=acc)
            d.text((28, 60), headline, font=_get_font(36, "bold"), fill=(18, 24, 38, 255))
        nw, nh = max(20, int(bw * max(0.2, sc))), max(20, int(bh * max(0.2, sc)))
        if (nw, nh) != (bw, bh):
            patch = patch.resize((nw, nh), Image.Resampling.BILINEAR)
        return 64, 995, patch

    if widget_id == "highlighter_stroke_bar":
        pw, ph = 820, 128
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        prog = _ease_out_cubic(min(1.0, t_beat / 0.42))
        bar_w = max(24, int((pw - 56) * prog))
        kicker = str(spec.get("kicker", "QUY LUẬT CẦN NHỚ"))
        headline = str(spec.get("headline", "GẠCH CHÂN Ý CỐT LÕI TRONG VIDEO"))
        if use_zero_box:
            _draw_shadow_text(patch, (28, 16), kicker, _get_font(22, "mono"), brass)
            _draw_shadow_text(patch, (28, 52), headline, _get_font(32, "bold"), ivory)
            _draw_hairline(patch, (28, 102), (28 + bar_w, 102), brass, width=4)
        else:
            d = ImageDraw.Draw(patch, "RGBA")
            d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=16, fill=(252, 246, 225, 236), outline=(217, 119, 6, 255), width=3)
            d.rounded_rectangle([28, 56, 28 + bar_w, 96], radius=8, fill=(253, 224, 71, 220))
            d.text((28, 16), kicker, font=_get_font(22, "mono"), fill=(146, 64, 14, 255))
            d.text((38, 58), headline, font=_get_font(32, "bold"), fill=(17, 24, 39, 255))
        return 64, 1005, patch

    if widget_id == "calligraphy_quote_dissolve":
        alpha_u = _ease_out_cubic(min(1.0, t_beat / 0.65))
        pw, ph = 920, 150
        kicker = str(spec.get("kicker", "CHIÊM NGHIỆM • NHỊP THỞ CHẬM"))
        headline = str(spec.get("headline", "Khi tâm tĩnh lại, mọi câu trả lời đều tự sáng rõ."))
        if use_zero_box:
            patch = _render_zero_box_editorial_patch(
                kicker,
                headline,
                "",
                pw=pw,
                ph=ph,
                acc=(232, 200, 142, 255),
                fg_col=(250, 244, 232, 255),
                sub_col=parchment,
                alpha_scale=alpha_u,
                show_filament=False,
                kicker_size=22,
                headline_size=34,
            )
            return 64, 995, patch
        patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(patch, "RGBA")
        a_bg = int(195 * alpha_u)
        a_fg = int(245 * alpha_u)
        d.rounded_rectangle([0, 0, pw - 2, ph - 2], radius=18, fill=(14, 12, 10, a_bg), outline=(232, 200, 142, int(190 * alpha_u)), width=2)
        d.text((36, 24), kicker, font=_get_font(22, "mono"), fill=(232, 200, 142, a_fg))
        d.text((36, 68), headline, font=_get_font(34, "bold"), fill=(250, 244, 232, a_fg))
        return 64, 995, patch

    return None
