"""Unit tests for Google Flow Native Thumbnail Generator."""

import tempfile
from pathlib import Path
from sys.tools.generate_sensational_thumbnails import (
    FLOW_THUMBNAIL_BLUEPRINTS,
    clean_and_resize_flow_thumbnail,
    generate_flow_native_thumbnails,
)

from PIL import Image


def test_20_channels_blueprint_completeness():
    """Verify all 20 Vietnamese channels have full 11-field Flow Native Blueprints."""
    expected_channels = [
        "ai_binh_dan",
        "ban_do_quyen_luc",
        "banh_rang",
        "chanh_niem_ke",
        "co_the_ke",
        "dia_com",
        "ho_so_ky_la",
        "la_ban_hoc_thuat",
        "loi_sang_soi",
        "luat_doi_thuong",
        "luat_ngam",
        "minh_triet_song",
        "nao_luoi",
        "nghe_song_sot",
        "su_ke_lai",
        "tam_tinh_dem",
        "thuong_cho_kheo",
        "tui_tien",
        "ua_sao_vay",
        "vu_tru_ti_hon",
    ]
    required_fields = [
        "niche",
        "visual_style",
        "shock_concept",
        "decorations",
        "brand_identity",
        "hook_text",
        "text_placement_16x9",
        "text_placement_9x16",
        "text_size_spec",
        "font_spec",
        "flow_prompt_16x9",
        "flow_prompt_9x16",
    ]
    assert len(expected_channels) == 20
    for ch in expected_channels:
        assert ch in FLOW_THUMBNAIL_BLUEPRINTS, f"Missing channel blueprint: {ch}"
        bp = FLOW_THUMBNAIL_BLUEPRINTS[ch]
        for f in required_fields:
            assert f in bp, f"Field '{f}' missing in blueprint for {ch}"
            assert len(str(bp[f])) > 0, f"Field '{f}' empty in blueprint for {ch}"

        # Hook text must be 2-4 uppercase words
        hook_words = bp["hook_text"].strip().split()
        assert 2 <= len(hook_words) <= 4, f"Hook text '{bp['hook_text']}' not 2-4 words in {ch}"

        # Prompts must explicitly contain the hook text and safe zone guidelines
        hook_16x9 = bp.get("hook_text_16x9") or bp["hook_text"]
        hook_9x16 = bp.get("hook_text_9x16") or bp["hook_text"]
        assert hook_16x9 in bp["flow_prompt_16x9"]
        assert hook_9x16 in bp["flow_prompt_9x16"]
        assert "TOP-LEFT SAFE ZONE" in bp["flow_prompt_16x9"]
        assert "UPPER-CENTER SAFE ZONE" in bp["flow_prompt_9x16"]

        if "hook_text_16x9" in bp:
            hook_16x9_words = bp["hook_text_16x9"].strip().split()
            assert 2 <= len(hook_16x9_words) <= 4, f"Hook text 16x9 '{bp['hook_text_16x9']}' not 2-4 words in {ch}"


def test_clean_and_resize_flow_thumbnail_16x9():
    """Test sparkle removal, 1.05x overscan crop, and 1280x720 resize under 2MB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_p = Path(tmpdir)
        raw_beluga = tmp_p / "raw_16x9.png"
        # Flow BELUGA 16:9 native resolution is 1376x768
        Image.new("RGB", (1376, 768), (248, 240, 220)).save(raw_beluga)

        out_thumb = tmp_p / "thumb_16x9.png"
        res = clean_and_resize_flow_thumbnail(raw_beluga, aspect="16:9", out_path=out_thumb)

        assert res.is_file()
        assert res.stat().st_size <= 1_950_000
        im = Image.open(res)
        assert im.size == (1280, 720)


def test_clean_and_resize_flow_thumbnail_9x16():
    """Test sparkle removal, 1.05x overscan crop, and 1080x1920 resize under 2MB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_p = Path(tmpdir)
        raw_beluga = tmp_p / "raw_9x16.png"
        # Flow BELUGA 9:16 native resolution is 768x1376
        Image.new("RGB", (768, 1376), (20, 25, 40)).save(raw_beluga)

        out_thumb = tmp_p / "thumb_9x16.png"
        res = clean_and_resize_flow_thumbnail(raw_beluga, aspect="9:16", out_path=out_thumb)

        assert res.is_file()
        assert res.stat().st_size <= 1_950_000
        im = Image.open(res)
        assert im.size == (1080, 1920)


def test_generate_flow_native_thumbnails_dry_run():
    """Test batch generator in dry-run mode for channels."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_p = Path(tmpdir)
        results = generate_flow_native_thumbnails(
            channels=["tui_tien", "nao_luoi"],
            aspect="both",
            work_dir=tmp_p,
            dry_run=True,
        )
        assert len(results) == 4
        for _k, p in results.items():
            assert p.is_file()
            assert p.stat().st_size <= 1_950_000
