"""V12 Zero-Box unit tests for `sys/fx_warehouse/hud_widgets.py`."""
from __future__ import annotations

import numpy as np
import pytest
from fx_warehouse import (
    HUD_WIDGET_CATALOG,
    auto_select_beat_fx,
    build_bespoke_topic_hud_patch,
    render_hud_widget_patch,
)
from fx_warehouse.hud_widgets import is_zero_box_enabled
from PIL import Image, ImageDraw


def _assert_zero_box_rgba(img: Image.Image, label: str, *, min_bright_px: int = 120) -> None:
    """Assert `img` is transparent RGBA shadow-only typography with no dark box backdrop."""
    assert img.mode == "RGBA", f"{label}: expected RGBA, got {img.mode}"
    arr = np.asarray(img, dtype=np.uint8)
    alpha = arr[:, :, 3]
    rgb_max = arr[:, :, :3].max(axis=2)

    # All 4 corners must stay completely transparent (no full-patch dark card)
    for cy, cx in ((0, 0), (0, -1), (-1, 0), (-1, -1)):
        assert int(alpha[cy, cx]) == 0, f"{label}: non-transparent corner {(cy, cx)} alpha={alpha[cy, cx]}"

    # Opaque/semi-opaque coverage stays low (only glyphs + thin hairlines, never a filled box)
    opaque_ratio = float((alpha >= 130).mean())
    assert opaque_ratio <= 0.25, f"{label}: expected <=25% opaque pixels, got {opaque_ratio:.2%}"

    # No 2D dark rectangular box (rows with >=120 dark opaque px must stay sparse, never >=30 rows)
    dark_opaque = (alpha >= 130) & (rgb_max < 42)
    wide_dark_rows = 0
    for row in dark_opaque:
        if int(row.sum()) < 120:
            continue
        padded = np.concatenate(([False], row, [False]))
        diffs = np.diff(padded.astype(np.int8))
        starts = np.where(diffs == 1)[0]
        ends = np.where(diffs == -1)[0]
        if len(starts) and int((ends - starts).max()) >= 120:
            wide_dark_rows += 1
    assert wide_dark_rows < 30, f"{label}: detected dark rectangular box spanning {wide_dark_rows} rows"

    # Crisp legible foreground typography/strokes must be present
    bright_px = int(((alpha >= 170) & (rgb_max >= 165)).sum())
    assert bright_px >= min_bright_px, f"{label}: too few bright text pixels ({bright_px})"


def test_is_zero_box_enabled_triggers_and_defaults() -> None:
    assert is_zero_box_enabled(None, zero_box=False) is False
    assert is_zero_box_enabled({}, zero_box=False) is False
    assert is_zero_box_enabled({"channel_id": "ho_so_ky_la"}, zero_box=False) is False
    assert is_zero_box_enabled({"channel_id": "tui_tien", "style_mode": "legacy"}, zero_box=False) is False

    assert is_zero_box_enabled({}, zero_box=True) is True
    assert is_zero_box_enabled({"zero_box": True}) is True
    assert is_zero_box_enabled({"style_mode": "v12_zero_box"}) is True
    assert is_zero_box_enabled({"channel_id": "su_ke_lai"}) is True
    assert is_zero_box_enabled({"channel_id": "su-ke-lai"}) is True
    assert is_zero_box_enabled({"kicker": "SU_KE_LAI • BESPOKE HUD"}) is True
    assert is_zero_box_enabled({"kind": "zero_box_chapter_card"}) is True
    assert is_zero_box_enabled({"kind": "boxless_chronicle_quote"}) is True


@pytest.mark.parametrize(
    "trigger_spec,trigger_kwarg",
    [
        ({}, True),
        ({"zero_box": True}, False),
        ({"style_mode": "v12_zero_box"}, False),
        ({"channel_id": "su_ke_lai"}, False),
    ],
)
def test_bespoke_and_historical_stamps_never_draw_boxes_or_vs_pills(
    monkeypatch: pytest.MonkeyPatch,
    trigger_spec: dict[str, object],
    trigger_kwarg: bool,
) -> None:
    def _forbid_box(*args: object, **kwargs: object) -> None:
        raise AssertionError("Zero-Box mode must never invoke ImageDraw.rectangle or rounded_rectangle")

    monkeypatch.setattr(ImageDraw.ImageDraw, "rounded_rectangle", _forbid_box)
    monkeypatch.setattr(ImageDraw.ImageDraw, "rectangle", _forbid_box)

    kinds = (
        "metric_meter",
        "timeline_nodes",
        "comparison_matrix",
        "sonar_radial",
        "telemetry_card",
        "v7_stat_versus",
        "zero_box_chapter_card",
        "boxless_chronicle_quote",
        "chronicle_stamp",
        "zero_box_dateline",
    )
    for kind in kinds:
        spec = {
            **trigger_spec,
            "kind": kind,
            "kicker": "1427 • ẢI CHI LĂNG",
            "headline": "THẾ TRẬN MAI PHỤC",
            "subline": "Đại Việt Sử Ký Toàn Thư",
            "value": 9.0,
            "max_value": 10.0,
            "unit": "VẠN",
            "nodes": ["01. NHỬ ĐỊCH", "02. KHÉP VÒNG", "03. TRUY KÍCH"],
            "left_title": "LAM SƠN",
            "left_value": "1 VẠN",
            "right_title": "QUÂN MINH",
            "right_value": "9 VẠN",
        }
        x0, y0, patch = build_bespoke_topic_hud_patch(spec, t_beat=0.45, dur=3.0, amp=0.4, zero_box=trigger_kwarg)
        assert isinstance(x0, int) and isinstance(y0, int)
        assert patch.width >= 400 and patch.height >= 120
        _assert_zero_box_rgba(patch, f"bespoke:{kind}")


def test_all_14_catalog_widgets_and_historical_stamps_zero_box(monkeypatch: pytest.MonkeyPatch) -> None:
    def _forbid_box(*args: object, **kwargs: object) -> None:
        raise AssertionError("Zero-Box mode must never invoke ImageDraw.rectangle or rounded_rectangle")

    monkeypatch.setattr(ImageDraw.ImageDraw, "rounded_rectangle", _forbid_box)
    monkeypatch.setattr(ImageDraw.ImageDraw, "rectangle", _forbid_box)

    for widget_id in HUD_WIDGET_CATALOG:
        spec = {
            "channel_id": "su_ke_lai",
            "kicker": "CHÍNH SỬ • 1427",
            "headline": "CHIẾN THẮNG CHI LĂNG",
            "subline": "Liễu Thăng tử trận tại núi Mã Yên",
            "tag": "SỬ KỂ LẠI • 1427",
        }
        res = render_hud_widget_patch(widget_id, spec, t_beat=0.45, dur=2.5, amp=0.5)
        assert res is not None, f"{widget_id} returned None in zero_box mode"
        x0, y0, img = res
        assert isinstance(x0, int) and isinstance(y0, int)
        assert img.width >= 50 and img.height >= 40
        min_px = 40 if widget_id == "radar_bezier_trajectory" else 120
        _assert_zero_box_rgba(img, f"widget:{widget_id}", min_bright_px=min_px)

    # Historical stamp kinds also render cleanly when passed directly to render_hud_widget_patch
    for stamp_kind in ("zero_box_chapter_card", "boxless_chronicle_quote", "chronicle_stamp", "zero_box_hook_title"):
        res = render_hud_widget_patch(
            stamp_kind,
            {"kicker": "CHƯƠNG I", "headline": "LỜI THỀ LŨNG NHAI"},
            t_beat=0.45,
            dur=3.5,
            zero_box=True,
        )
        assert res is not None
        _assert_zero_box_rgba(res[2], f"stamp:{stamp_kind}")


def test_non_history_channels_preserve_backward_compatible_boxed_cards() -> None:
    # Non-history forensic/doodle channels without zero_box keep boxed card rendering
    x0, y0, boxed = build_bespoke_topic_hud_patch(
        {
            "channel_id": "ho_so_ky_la",
            "kind": "telemetry_card",
            "theme": "dark",
            "kicker": "BLACK BOX",
            "headline": "HELIOS 522",
            "subline": "FL340 cabin altitude",
        },
        t_beat=0.6,
        dur=2.5,
    )
    assert isinstance(x0, int) and isinstance(y0, int)
    arr = np.asarray(boxed, dtype=np.uint8)
    # Boxed card fills the interior with dark semi-opaque pixels (~226 alpha)
    assert int((arr[:, :, 3] >= 200).mean() * 100) >= 75

    # Selector integration for su_ke_lai auto-activates zero_box via SU_KE_LAI bespoke spec
    fx = auto_select_beat_fx(
        "Cấu trúc cọc gỗ ngầm dưới lòng sông Bạch Đằng khi thủy triều rút",
        channel_id="su_ke_lai",
        video_topic="Trận Bạch Đằng 1288",
        allow_bespoke=True,
    )
    _, _, zero_patch = build_bespoke_topic_hud_patch(fx["bespoke_hud_spec"], t_beat=0.45, dur=2.5)
    _assert_zero_box_rgba(zero_patch, "auto_select_su_ke_lai")
