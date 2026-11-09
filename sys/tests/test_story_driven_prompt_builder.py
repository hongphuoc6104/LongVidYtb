#!/usr/bin/env python3
"""Unit tests for Video Pilot Story-Driven Prompt Builder and Master Spec Generator."""

import json
from pathlib import Path

import pytest
from tools.story_driven_prompt_builder import (
    CHANNEL_STYLE_PROFILES,
    build_story_driven_prompt,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYS_DIR = ROOT_DIR / "sys"


class TestStoryDrivenPromptBuilder:
    """Tests for build_story_driven_prompt function."""

    def test_culinary_science_dia_com(self):
        narr = "Trên mặt chảo gang nóng rực, những giọt mỡ bò đang nhảy múa và nổ lách tách."
        prompt = build_story_driven_prompt(narr, "dia-com", event_kind="ANGLE_CUTAWAY")
        assert "Cinematic macro culinary food science photography" in prompt
        assert "Dynamic perspective cutaway showing:" in prompt
        assert "droplets of beef fat sizzling" in prompt or "cast-iron" in prompt
        assert "8k" not in prompt.lower()
        assert "strictly zero text overlays" in prompt
        assert "focusing on key element in Hồi" not in prompt

    def test_noir_forensic_ho_so_ky_la(self):
        narr = "đầu máy tám tám tám tám dẫn đầu bốn mươi bảy toa hàng bắt đầu lăn bánh."
        prompt = build_story_driven_prompt(narr, "ho-so-ky-la", event_kind="ENUMERATION_BURST")
        assert "Atmospheric 3D noir forensic crime-scene diorama" in prompt
        assert "Macro close-up cutaway burst focusing on:" in prompt
        assert "8888" in prompt or "locomotive" in prompt
        assert "8k" not in prompt.lower()
        assert "strictly zero text overlays" in prompt

    def test_2d_doodle_nao_luoi(self):
        narr = "Chắc hẳn bạn từng tự nhủ chỉ cầm điện thoại lướt mạng năm phút trước khi đi ngủ."
        prompt = build_story_driven_prompt(narr, "nao-luoi", event_kind="ANCHOR_ESTABLISH")
        assert "Hand-drawn 2D Vietnamese indie doodle explainer illustration" in prompt
        assert "Nghech Ngoac" in prompt
        assert all(ord(c) < 128 for c in prompt)  # Strict pure ASCII
        assert "stickman" in prompt
        assert "#3B82C4" in prompt
        assert "8k" not in prompt.lower()
        assert "strictly zero text overlays" in prompt

    def test_tactical_atlas_ban_do_quyen_luc(self):
        narr = "Dòng hải lưu hẹp uốn lượn như một chiếc phễu khổng lồ kẹp giữa đại dương."
        prompt = build_story_driven_prompt(narr, "ban-do-quyen-luc", event_kind="ANCHOR_ESTABLISH")
        assert "High-altitude strategic 3D orbital satellite map rendering" in prompt
        assert "Strait of Malacca" in prompt or "funnel-shaped" in prompt
        assert "8k" not in prompt.lower()
        assert "photorealistic" not in prompt.lower()
        assert all(ord(c) < 128 for c in prompt)  # Strict pure ASCII
        assert "strictly zero text overlays" in prompt

    def test_zen_mindfulness_chanh_niem_ke(self):
        narr = "Mũi tên thứ hai chính là sự phán xét và dằn vặt của tâm trí."
        prompt = build_story_driven_prompt(narr, "chanh-niem-ke", event_kind="ANGLE_CUTAWAY")
        assert "Cinematic Wabi-Sabi & Zen Sumi-e mindfulness visual" in prompt
        assert "second arrow" in prompt or "mental overthinking" in prompt
        assert "8k" not in prompt.lower()
        assert "strictly zero text overlays" in prompt

    def test_consumer_finance_tui_tien(self):
        narr = "Ly vừa năm mươi lăm nghìn, nhưng chỉ thêm bốn nghìn nữa bạn được ly lớn."
        prompt = build_story_driven_prompt(narr, "tui-tien", event_kind="ANGLE_CUTAWAY")
        assert "Cinematic commercial documentary tabletop photography" in prompt
        assert "three tiered glass cups" in prompt or "decoy" in prompt or "coffee" in prompt
        assert "8k" not in prompt.lower()
        assert "strictly zero text overlays" in prompt

    def test_channel_slug_alias_resolution(self):
        narr = "Kiểm tra hệ thống an toàn."
        p1 = build_story_driven_prompt(narr, "dia-com")
        p2 = build_story_driven_prompt(narr, "dia_com")
        p3 = build_story_driven_prompt(narr, "ch_dia_com")
        assert p1 == p2 == p3

    def test_event_kind_framing_variations(self):
        narr = "Làn khói mỏng bốc lên nghi ngút."
        p_anchor = build_story_driven_prompt(narr, "dia-com", event_kind="ANCHOR_ESTABLISH")
        p_burst = build_story_driven_prompt(narr, "dia-com", event_kind="ENUMERATION_BURST")
        p_angle = build_story_driven_prompt(narr, "dia-com", event_kind="ANGLE_CUTAWAY")
        p_mech = build_story_driven_prompt(narr, "dia-com", event_kind="MECHANISM_STEP")

        assert "Establishing wide diorama:" in p_anchor
        assert "Macro close-up cutaway burst focusing on:" in p_burst
        assert "Dynamic perspective cutaway showing:" in p_angle
        assert "Visual mechanism cutaway demonstrating:" in p_mech

    def test_all_20_profiles_registered(self):
        expected_slugs = [
            "dia-com", "ho-so-ky-la", "tui-tien", "ban-do-quyen-luc", "chanh-niem-ke",
            "nao-luoi", "ai-binh-dan", "ua-sao-vay", "su-ke-lai", "thuong-cho-kheo",
            "co-the-ke", "luat-ngam", "luat-doi-thuong", "banh-rang", "vu-tru-ti-hon",
            "nghe-song-sot", "la-ban-hoc-thuat", "loi-sang-soi", "minh-triet-song", "tam-tinh-dem"
        ]
        for slug in expected_slugs:
            assert slug in CHANNEL_STYLE_PROFILES


class TestAll20ChannelsMasterSpecsIntegrity:
    """Verify that all 20 VN Long Master Specs have story-driven prompts with 0 generic boilerplate."""

    @pytest.mark.parametrize(
        "channel_slug",
        [
            "dia-com", "ho-so-ky-la", "tui-tien", "ban-do-quyen-luc", "chanh-niem-ke",
            "nao-luoi", "ai-binh-dan", "ua-sao-vay", "su-ke-lai", "thuong-cho-kheo",
            "co-the-ke", "luat-ngam", "luat-doi-thuong", "banh-rang", "vu-tru-ti-hon",
            "nghe-song-sot", "la-ban-hoc-thuat", "loi-sang-soi", "minh-triet-song", "tam-tinh-dem"
        ]
    )
    def test_channel_master_spec_zero_generic_boilerplate(self, channel_slug):
        spec_path = SYS_DIR / f"channels/vn_rebuilt_style_specs/{channel_slug}/{channel_slug}_long_master_spec.json"
        assert spec_path.is_file(), f"Missing master spec for {channel_slug}"

        data = json.loads(spec_path.read_text(encoding="utf-8"))
        beats = data.get("beats", data.get("visual_states", []))
        assert len(beats) >= 150, f"Channel {channel_slug} has only {len(beats)} beats"

        # Check that 0 beats have old generic boilerplate
        generic_beats = [
            b for b in beats
            if "establishing diorama for Hồi" in b.get("prompt", "")
            or "focusing on key element in Hồi" in b.get("prompt", "")
            or "shifting perspective on" in b.get("prompt", "")
        ]
        assert len(generic_beats) == 0, f"Found {len(generic_beats)} generic prompts in {channel_slug}"

        # Check that NO beats have 8K buzzwords
        eight_k_beats = [b for b in beats if "8k" in b.get("prompt", "").lower()]
        assert len(eight_k_beats) == 0, f"Found {len(eight_k_beats)} prompts with 8k in {channel_slug}"

        # Check that every beat has non-empty narration and prompt
        for b in beats:
            assert b.get("narration"), f"Empty narration in beat {b.get('id')}"
            assert b.get("prompt"), f"Empty prompt in beat {b.get('id')}"
            assert "strictly zero text overlays" in b.get("prompt", "")
