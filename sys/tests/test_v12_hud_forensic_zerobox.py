"""V12 Zero-Box Cinema Typography & Hairline tests for `fx_warehouse.hud_forensic_v2`."""
from __future__ import annotations

import numpy as np
from fx_warehouse.hud_forensic_v2 import (
    FORENSIC_HUD_V2_CATALOG,
    _draw_card_shell,
    _draw_pill,
    _get_font,
    _layout_ctx,
    _resolve_zero_box,
    _theme,
    render_forensic_hud_v2,
    render_lemmino_hairline_hud,
)
from PIL import Image, ImageDraw


def test_resolve_zero_box_auto_detection() -> None:
    assert _resolve_zero_box(None) is False
    assert _resolve_zero_box({}) is False
    assert _resolve_zero_box({"channel_id": "ho_so_ky_la"}) is False
    assert _resolve_zero_box({"zero_box": False}) is False

    assert _resolve_zero_box({}, zero_box=True) is True
    assert _resolve_zero_box({"zero_box": True}) is True
    assert _resolve_zero_box({"channel_id": "su_ke_lai"}) is True
    assert _resolve_zero_box({"channel_id": " su_ke_lai "}) is True


def test_draw_pill_and_card_shell_skip_fills_in_zero_box() -> None:
    # 1. _draw_card_shell with zero_box=True leaves canvas 100% transparent
    ctx = _layout_ctx(1280, 720)
    th = _theme("A")
    c_box = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    _draw_card_shell(ImageDraw.Draw(c_box, "RGBA"), 100, 100, 500, 200, th, ctx, zero_box=False)
    assert int((np.asarray(c_box)[:, :, 3] > 0).sum()) > 50_000

    c_zb = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    _draw_card_shell(ImageDraw.Draw(c_zb, "RGBA"), 100, 100, 500, 200, th, ctx, zero_box=True)
    assert int(np.asarray(c_zb)[:, :, 3].max()) == 0

    # 2. _draw_pill with zero_box=True skips dark pill rect fill & preserves dimensions
    font = _get_font(22, "bold")
    p_box = Image.new("RGBA", (400, 120), (0, 0, 0, 0))
    pw1, ph1 = _draw_pill(
        ImageDraw.Draw(p_box, "RGBA"),
        20,
        20,
        "SỬ KỂ LẠI",
        font,
        (10, 14, 22, 226),
        (255, 255, 255, 255),
        outline=(212, 168, 72, 245),
        zero_box=False,
    )
    p_zb = Image.new("RGBA", (400, 120), (0, 0, 0, 0))
    pw2, ph2 = _draw_pill(
        ImageDraw.Draw(p_zb, "RGBA"),
        20,
        20,
        "SỬ KỂ LẠI",
        font,
        (10, 14, 22, 226),
        (255, 255, 255, 255),
        outline=(212, 168, 72, 245),
        zero_box=True,
    )
    assert (pw1, ph1) == (pw2, ph2)

    arr_box = np.asarray(p_box, dtype=np.uint8)
    arr_zb = np.asarray(p_zb, dtype=np.uint8)
    # Padding pixel inside the pill fill (past radius=8 corner, before text at x=36, y=29)
    assert arr_box[25, 30, 3] > 180
    assert arr_zb[25, 30, 3] == 0
    # Text + optical drop-shadow still render crisply
    assert int((arr_zb[:, :, 3] > 120).sum()) > 100
    assert int((arr_zb[:, :, 3] > 0).sum()) < int((arr_box[:, :, 3] > 0).sum()) * 0.55


def test_lemmino_hairline_hud_skips_rect_scrim_in_zero_box() -> None:
    spec_base = {
        "mode": "timeline",
        "kicker": "NĂM 1427 • CHI LĂNG",
        "headline": "ĐẠI PHÁ QUÂN MINH",
        "metric": "CANH TƯ",
        "markers": ["KHỞI BINH", "MAI PHỤC", "TOÀN THẮNG"],
    }
    legacy = render_lemmino_hairline_hud(spec_base, t_beat=0.9, dur=2.5, width=1280, height=720)
    zb_flag = render_lemmino_hairline_hud(spec_base, t_beat=0.9, dur=2.5, width=1280, height=720, zero_box=True)
    zb_spec = render_lemmino_hairline_hud({**spec_base, "zero_box": True}, t_beat=0.9, dur=2.5, width=1280, height=720)
    zb_chan = render_lemmino_hairline_hud({**spec_base, "channel_id": "su_ke_lai"}, t_beat=0.9, dur=2.5, width=1280, height=720)

    arr_leg = np.asarray(legacy, dtype=np.uint8)
    arr_zb = np.asarray(zb_flag, dtype=np.uint8)

    # All three zero_box activation paths produce identical output
    assert np.array_equal(arr_zb, np.asarray(zb_spec, dtype=np.uint8))
    assert np.array_equal(arr_zb, np.asarray(zb_chan, dtype=np.uint8))

    # Legacy mode fills the entire lower-third scrim rectangle with alpha ~ 112
    # Zero-box mode keeps non-text/non-hairline background purely transparent (much fewer opaque pixels)
    leg_nonzero = int((arr_leg[:, :, 3] > 0).sum())
    zb_nonzero = int((arr_zb[:, :, 3] > 0).sum())
    assert zb_nonzero > 500
    assert zb_nonzero < leg_nonzero * 0.35

    # Wave mode & 9:16 portrait safe-zone also render cleanly without rectangular scrim
    portrait = render_forensic_hud_v2(
        "lemmino_hairline_hud",
        {**spec_base, "channel_id": "su_ke_lai", "mode": "wave"},
        t_beat=0.8,
        dur=2.5,
        width=1440,
        height=2560,
    )
    p_alpha = np.asarray(portrait, dtype=np.uint8)[:, :, 3]
    ys, xs = np.where(p_alpha > 0)
    assert len(xs) > 100
    assert int(xs.max()) <= 1275
    assert int(ys.max()) <= 2015


def test_all_card_and_overlay_widgets_respect_zero_box_without_breaking_legacy() -> None:
    card_widgets = (
        "alt_pressure_divergence",
        "dual_horn_pulse",
        "hypoxia_tuc_meter",
        "swiss_cheese_align",
        "classic_vs_ng_compare",
        "fuel_avoidance_vector",
        "man_auto_switch",
    )
    for hud_id in card_widgets:
        leg = render_forensic_hud_v2(
            hud_id,
            {"channel_id": "ho_so_ky_la"},
            t_beat=0.85,
            dur=2.5,
            width=1280,
            height=720,
            variant="A",
        )
        zb_by_chan = render_forensic_hud_v2(
            hud_id,
            {"channel_id": "su_ke_lai"},
            t_beat=0.85,
            dur=2.5,
            width=1280,
            height=720,
            variant="A",
        )
        zb_by_arg = render_forensic_hud_v2(
            hud_id,
            {},
            t_beat=0.85,
            dur=2.5,
            width=1280,
            height=720,
            variant="A",
            zero_box=True,
        )
        arr_leg = np.asarray(leg, dtype=np.uint8)
        arr_zb = np.asarray(zb_by_chan, dtype=np.uint8)
        assert np.array_equal(arr_zb, np.asarray(zb_by_arg, dtype=np.uint8))

        leg_px = int((arr_leg[:, :, 3] > 0).sum())
        zb_px = int((arr_zb[:, :, 3] > 0).sum())
        assert zb_px > 500, f"{hud_id} rendered empty in zero_box mode"
        assert zb_px < leg_px * 0.45, f"{hud_id} did not strip dark card/panel fills in zero_box mode ({zb_px} vs {leg_px})"

    # Calibrated radar overlay & chapter_title_bumper also work across all catalog widgets
    for hud_id in sorted(FORENSIC_HUD_V2_CATALOG):
        im = render_forensic_hud_v2(
            hud_id,
            {"channel_id": "su_ke_lai", "ch_num": "CH02", "ch_title": "BẠCH ĐẰNG"},
            t_beat=0.85,
            dur=2.5,
            width=1280,
            height=720,
            variant="B",
        )
        assert im.mode == "RGBA" and im.size == (1280, 720)
        assert int((np.asarray(im, dtype=np.uint8)[:, :, 3] > 0).sum()) > 300
