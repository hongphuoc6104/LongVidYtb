"""Tests for CTA contract, tone linter, and placement rules (contract §3.4)."""

from __future__ import annotations

import pytest
from tools.cta_tone_linter import (
    count_syllables_whitespace,
    lint_cta,
    strip_diacritics,
)


def test_strip_diacritics_normalization():
    assert strip_diacritics("Đừng quên like nhé!") == "dung quen like nhe!"
    assert strip_diacritics("Bấm chuông & subscribe") == "bam chuong & subscribe"
    assert strip_diacritics("Não Lười") == "nao luoi"


def test_count_syllables_whitespace():
    assert count_syllables_whitespace("Gửi cho đứa bạn hay thức khuya chung.") == 8
    assert count_syllables_whitespace("Vì sao não lại đòi lại thời gian? [pause:300ms] Bản dài trên YouTube.") == 12


def test_valid_short_cta_plan_passes():
    brief = {
        "format_profile": "short_9x16",
        "parent_long_id": "nao-luoi-week1-16x9",
        "cta_plan": {
            "bridge": "Vì sao não lại đòi lại thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười.",
            "close": "Gửi cho đứa bạn hay thức khuya chung với bạn đi.",
            "endcard_text": "BẢN ĐẦY ĐỦ TRÊN YOUTUBE",
            "mid_cta": None,
        },
    }
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Đúng hai giờ sáng, bạn vẫn nằm bấm điện thoại."},
            {
                "id": "SC02",
                "narration": "Vì sao não lại đòi lại thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười. Gửi cho đứa bạn hay thức khuya chung với bạn đi.",
            },
        ]
    }
    errors = lint_cta(brief, content)
    assert errors == [], f"Expected clean CTA pass, got: {errors}"


def test_valid_long_cta_plan_passes():
    brief = {
        "format_profile": "long_16x9",
        "cta_plan": {
            "close": "Nếu thấy hữu ích, ở lại cùng Não Lười khám phá thêm những nghịch lý tiếp theo.",
            "endcard_text": "THEO DÕI NÃO LƯỜI",
            "mid_cta": "Nếu nhận ra mình trong câu chuyện này, ghi nhớ một điều sau đây.",
        },
    }
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu một quan sát sâu sắc."},
            {"id": "SC02", "narration": "Nếu nhận ra mình trong câu chuyện này, ghi nhớ một điều sau đây. Giải thích cơ chế."},
            {"id": "SC03", "narration": "Nếu thấy hữu ích, ở lại cùng Não Lười khám phá thêm những nghịch lý tiếp theo."},
        ]
    }
    errors = lint_cta(brief, content)
    assert errors == [], f"Expected clean long CTA pass, got: {errors}"


@pytest.mark.parametrize(
    "banned_phrase",
    [
        "Đừng quên like và share nhé",
        "Hãy bấm chuông để theo dõi",
        "Nhấn chuông thông báo",
        "Đăng ký kênh để ủng hộ",
        "LIKE SHARE SUBSCRIBE",
        "Ấn theo dõi ngay",
        "Nhớ like video nha",
    ],
)
def test_banned_phrases_detected_insensitively(banned_phrase: str):
    brief = {
        "format_profile": "short_9x16",
        "parent_long_id": "nao-luoi-week1-16x9",
        "cta_plan": {
            "bridge": "Bản dài có trên YouTube.",
            "close": banned_phrase,
            "endcard_text": "BẢN ĐẦY ĐỦ",
        },
    }
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu."},
            {"id": "SC02", "narration": f"Bản dài có trên YouTube. {banned_phrase}"},
        ]
    }
    errors = lint_cta(brief, content)
    assert any("CTA_BANNED_PHRASE" in err for err in errors)


def test_short_missing_parent_long_id_rejected():
    brief = {
        "format_profile": "short_9x16",
        "cta_plan": {
            "bridge": "Bản dài có trên YouTube.",
            "close": "Gửi cho bạn bè nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ",
        },
    }
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu."},
            {"id": "SC02", "narration": "Bản dài có trên YouTube. Gửi cho bạn bè nhé."},
        ]
    }
    errors = lint_cta(brief, content)
    assert any("CTA_MISSING_PARENT_LONG_ID" in err for err in errors)


def test_syllable_budget_violations():
    # Bridge > 22 syllables
    long_bridge = "Một hai ba bốn năm sáu bảy tám chín mười mười một mười hai mười ba mười bốn mười lăm mười sáu mười bảy mười tám mười chín hai mươi hai mốt hai hai hai ba hai bốn"
    brief = {
        "format_profile": "short_9x16",
        "parent_long_id": "long-01",
        "cta_plan": {
            "bridge": long_bridge,
            "close": "Câu kết ngắn gọn.",
            "endcard_text": "BẢN ĐẦY ĐỦ",
        },
    }
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu."},
            {"id": "SC02", "narration": f"{long_bridge} Câu kết ngắn gọn."},
        ]
    }
    errors = lint_cta(brief, content)
    assert any("CTA_BRIDGE_SYLLABLES_EXCEEDED" in err for err in errors)


def test_placement_inside_opening_hook_rejected():
    brief = {
        "format_profile": "short_9x16",
        "parent_long_id": "long-01",
        "cta_plan": {
            "bridge": "Bản dài có trên YouTube.",
            "close": "Gửi cho đứa bạn thân nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ",
        },
    }
    # CTA placed in SC01
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Chào bạn, gửi cho đứa bạn thân nhé."},
            {"id": "SC02", "narration": "Bản dài có trên YouTube."},
        ]
    }
    errors = lint_cta(brief, content)
    assert any("CTA_INSIDE_HOOK" in err for err in errors)


def test_measured_timing_placement_checks():
    brief = {
        "format_profile": "short_9x16",
        "parent_long_id": "long-01",
        "cta_plan": {
            "bridge": "Bản dài có trên YouTube.",
            "close": "Gửi cho đứa bạn thân nhé.",
            "endcard_text": "BẢN ĐẦY ĐỦ",
        },
    }
    content = {
        "scenes": [
            {"id": "SC01", "narration": "Mở đầu bài nói."},
            {"id": "SC02", "narration": "Bản dài có trên YouTube. Gửi cho đứa bạn thân nhé."},
        ]
    }

    # Timing: total 40s, bridge at 20s (not in final 15% >= 34s)
    bad_timings = {
        "total_duration": 40.0,
        "bridge_start": 20.0,
        "close_start": 36.0,
    }
    errors = lint_cta(brief, content, timings=bad_timings)
    assert any("CTA_NOT_IN_FINAL_WINDOW" in err for err in errors)

    # Clean timing: total 40s, bridge at 35s, close at 37s (both in final 15% >= 34s)
    good_timings = {
        "total_duration": 40.0,
        "bridge_start": 35.0,
        "close_start": 37.0,
    }
    clean_errors = lint_cta(brief, content, timings=good_timings)
    assert clean_errors == []
