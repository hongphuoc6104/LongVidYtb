#!/usr/bin/env python3
"""Comprehensive test suite for Vietnamese text normalizer (vn_text_normalizer.py)
and linguistic/cadence/pause architecture.
Covers all 17 test groups from spec_miner_m1_1/test_specifications.md:
- Group 1: Number-to-Words Normalization (num_to_vn_words & normalize_for_tts)
- Group 2: Thousands Separator Disambiguation (Vietnamese Dot vs English Comma)
- Group 3: Decimals (Comma vs Dot Decimals)
- Group 4: Percentages (Integer & Decimal)
- Group 5: Years (Historical and Modern)
- Group 6: Slashes & Rates (Units, Fractions, Ratios)
- Group 7: Foreign Proper Nouns & Scientific Terms
- Group 8: Punctuation Sanitization
- Group 9: Gatekeeper Validation (detect_unnormalized_tokens & enforce_tts_normalization_gate)
- Group 10: Pause Splitting (split_utterances_by_pause)
- Group 11: Opening Hook Length Gate (OPENING_HOOK_TOO_LONG)
- Group 12: Opening Scene Pause Ban (OPENING_SCENE_PAUSE_FORBIDDEN)
- Group 13: Breathless Clause Gate (BREATHLESS_CLAUSE)
- Group 14: Dramatic Pause Duration Preservation & Clean Chunks
- Group 15: Dual Format Pause Budgets (format_v1)
- Group 16: Voice Profile Contract & Spinoff Hook Gate
- Group 17: Tone Speed Modulation & Bilingual Spans
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import adapters
from format_profiles import get_profile
from narration_pauses import settings_for_language, split_narration
from script_cadence_checker import ScriptCadenceChecker
from vn_text_normalizer import (
    detect_unnormalized_tokens,
    enforce_tts_normalization_gate,
    normalize_for_tts,
    num_to_vn_words,
    split_utterances_by_pause,
)


# ==============================================================================
# Group 1: Number-to-Words Normalization (num_to_vn_words & normalize_for_tts)
# ==============================================================================
class TestGroup01NumberToWords:
    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (0, "không"),
            (1, "một"),
            (2, "hai"),
            (3, "ba"),
            (4, "bốn"),
            (5, "năm"),
            (6, "sáu"),
            (7, "bảy"),
            (8, "tám"),
            (9, "chín"),
        ],
    )
    def test_single_digits(self, n: int, expected: str):
        assert num_to_vn_words(n) == expected

    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (10, "mười"),
            (11, "mười một"),
            (14, "mười bốn"),
            (15, "mười lăm"),
            (19, "mười chín"),
        ],
    )
    def test_teens(self, n: int, expected: str):
        assert num_to_vn_words(n) == expected

    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (20, "hai mươi"),
            (21, "hai mươi mốt"),
            (24, "hai mươi tư"),
            (25, "hai mươi lăm"),
            (31, "ba mươi mốt"),
            (34, "ba mươi tư"),
            (35, "ba mươi lăm"),
            (55, "năm mươi lăm"),
        ],
    )
    def test_tens_and_compound_units(self, n: int, expected: str):
        assert num_to_vn_words(n) == expected

    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (100, "một trăm"),
            (101, "một trăm lẻ một"),
            (104, "một trăm lẻ bốn"),
            (105, "một trăm lẻ năm"),
            (110, "một trăm mười"),
            (115, "một trăm mười lăm"),
            (121, "một trăm hai mươi mốt"),
            (124, "một trăm hai mươi tư"),
            (125, "một trăm hai mươi lăm"),
        ],
    )
    def test_hundreds_and_zero_padding(self, n: int, expected: str):
        assert num_to_vn_words(n) == expected

    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (1000, "một nghìn"),
            (1005, "một nghìn không trăm lẻ năm"),
            (1015, "một nghìn không trăm mười lăm"),
            (1021, "một nghìn không trăm hai mươi mốt"),
            (1050, "một nghìn không trăm năm mươi"),
            (1100, "một nghìn một trăm"),
            (100000, "một trăm nghìn"),
            (1000000, "một triệu"),
            (1250000, "một triệu hai trăm năm mươi nghìn"),
            (100000000, "một trăm triệu"),
        ],
    )
    def test_thousands_and_millions(self, n: int, expected: str):
        assert num_to_vn_words(n) == expected

    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (-5, "âm năm"),
            (-24, "âm hai mươi tư"),
        ],
    )
    def test_negative_numbers(self, n: int, expected: str):
        assert num_to_vn_words(n) == expected

    def test_negative_in_sentence(self):
        assert normalize_for_tts("Nhiệt độ giảm xuống -5 độ C.") == "Nhiệt độ giảm xuống âm năm độ C."
        assert normalize_for_tts("Sai số là -24 điểm.") == "Sai số là âm hai mươi tư điểm."


# ==============================================================================
# Group 2: Thousands Separator Disambiguation (Vietnamese Dot vs English Comma)
# ==============================================================================
class TestGroup02ThousandsSeparators:
    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("khoảng 50.000 năm trước", "khoảng năm mươi nghìn năm trước"),
            ("100.000 người tham gia", "một trăm nghìn người tham gia"),
            ("1.250.000 đô la", "một triệu hai trăm năm mươi nghìn đô la"),
            ("Dân số đạt 10.000 người.", "Dân số đạt mười nghìn người."),
        ],
    )
    def test_vietnamese_dot_thousands(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []

    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("50,000 năm trước", "năm mươi nghìn năm trước"),
            ("khoảng 100,000 người", "khoảng một trăm nghìn người"),
            ("hơn 1,000,000 đô la", "hơn một triệu đô la"),
            ("ngân sách 1,250,000 đô", "ngân sách một triệu hai trăm năm mươi nghìn đô"),
        ],
    )
    def test_english_comma_thousands(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert "phẩy" not in res
        assert detect_unnormalized_tokens(res) == []


# ==============================================================================
# Group 3: Decimals (Comma vs Dot Decimals)
# ==============================================================================
class TestGroup03Decimals:
    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("chiếm 2,4 giờ mỗi ngày", "chiếm hai phẩy bốn giờ mỗi ngày"),
            ("đạt 0,5 giây", "đạt không phẩy năm giây"),
            ("sai số 0,05 milimét", "sai số không phẩy không năm milimét"),
            ("hằng số pi xấp xỉ 3,14", "hằng số pi xấp xỉ ba phẩy mười bốn"),
            ("Tỷ lệ tăng 2,5 lần.", "Tỷ lệ tăng hai phẩy năm lần."),
        ],
    )
    def test_vietnamese_comma_decimals(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []

    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("chiếm 2.4 giờ mỗi ngày", "chiếm hai phẩy bốn giờ mỗi ngày"),
            ("đạt 0.5 giây", "đạt không phẩy năm giây"),
            ("sai số 0.05 milimét", "sai số không phẩy không năm milimét"),
            ("hằng số pi xấp xỉ 3.14", "hằng số pi xấp xỉ ba phẩy mười bốn"),
            ("ước lượng 3.1415", "ước lượng ba phẩy một nghìn bốn trăm mười lăm"),
        ],
    )
    def test_dot_decimals(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert "." not in res
        assert detect_unnormalized_tokens(res) == []


# ==============================================================================
# Group 4: Percentages (Integer & Decimal)
# ==============================================================================
class TestGroup04Percentages:
    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("đạt 81% chỉ tiêu", "đạt tám mươi mốt phần trăm chỉ tiêu"),
            ("100% chính xác", "một trăm phần trăm chính xác"),
            ("tăng 5%", "tăng năm phần trăm"),
            ("0% lỗi", "không phần trăm lỗi"),
        ],
    )
    def test_integer_percentages(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []

    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("tỷ lệ 81,5% thành công", "tỷ lệ tám mươi mốt phẩy năm phần trăm thành công"),
            ("tỷ lệ 81.5% thành công", "tỷ lệ tám mươi mốt phẩy năm phần trăm thành công"),
            ("tăng 0,5% mỗi tháng", "tăng không phẩy năm phần trăm mỗi tháng"),
            ("tăng 0.5% mỗi tháng", "tăng không phẩy năm phần trăm mỗi tháng"),
        ],
    )
    def test_decimal_percentages(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert "%" not in res
        assert detect_unnormalized_tokens(res) == []


# ==============================================================================
# Group 5: Years (Historical and Modern)
# ==============================================================================
class TestGroup05Years:
    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("Năm 1995 lịch sử", "Năm một nghìn chín trăm chín mươi lăm lịch sử"),
            ("năm 2024 hiện tại", "năm hai nghìn không trăm hai mươi tư hiện tại"),
            ("năm 2000 bắt đầu", "năm hai nghìn bắt đầu"),
            ("năm 1800 xưa kia", "năm một nghìn tám trăm xưa kia"),
            (
                "Từ năm 1975 đến năm 2024",
                "Từ năm một nghìn chín trăm bảy mươi lăm đến năm hai nghìn không trăm hai mươi tư",
            ),
        ],
    )
    def test_years(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []


# ==============================================================================
# Group 6: Slashes & Rates (Units, Fractions, Ratios)
# ==============================================================================
class TestGroup06SlashesAndRates:
    @pytest.mark.parametrize(
        ("inp", "expected"),
        [
            ("làm việc 17 giờ/tuần", "làm việc mười bảy giờ trên tuần"),
            ("vận tốc 60 km/h", "vận tốc sáu mươi ki-lô-mét trên giờ"),
            ("hoạt động 24/7 liên tục", "hoạt động hai mươi tư trên bảy liên tục"),
            ("chọn A và/hoặc B", "chọn A và hoặc B"),
            ("chiếm 1/3 dân số", "chiếm một phần ba dân số"),
            ("tốc độ đọc 500 từ/phút", "tốc độ đọc năm trăm từ trên phút"),
        ],
    )
    def test_slashes(self, inp: str, expected: str):
        res = normalize_for_tts(inp)
        assert res == expected
        assert "/" not in res
        assert detect_unnormalized_tokens(res) == []


# ==============================================================================
# Group 7: Foreign Proper Nouns & Scientific Terms
# ==============================================================================
class TestGroup07ForeignProperNouns:
    def test_researchers_and_scientists(self):
        text = "Nghiên cứu của Richard Lee và Polly Wiessner, cùng với Richard P. Feynman và James Suzman."
        expected = "Nghiên cứu của Ri-chát Li và Pô-li Uýt-nơ, cùng với Ri-chát Phây-man và Giêm Xút-man."
        res = normalize_for_tts(text)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []

    def test_tribal_and_geography(self):
        text = "Bộ tộc Ju/'hoansi tại Botswana sống trong sa mạc Kalahari."
        expected = "Bộ tộc Giu-hoan-si tại Bốt-xoa-na sống trong sa mạc Ka-la-ha-ri."
        res = normalize_for_tts(text)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []

    def test_neuroscience_terms(self):
        text = "Lượng dopamine và cortisol được điều tiết bởi prefrontal cortex và amygdala."
        expected = "Lượng đô-pa-min và cóc-ti-dôn được điều tiết bởi vỏ não trước trán và hạch hạnh nhân."
        res = normalize_for_tts(text)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []

    def test_modern_loanwords(self):
        text = "Homo sapiens dùng smartphone xem video trên TikTok và YouTube rồi gửi email."
        expected = "Hô-mô sa-pi-en dùng điện thoại thông minh xem vi-đê-ô trên Tích-tốc và Diu-túp rồi gửi i-meo."
        res = normalize_for_tts(text)
        assert res == expected
        assert detect_unnormalized_tokens(res) == []


# ==============================================================================
# Group 8: Punctuation Sanitization
# ==============================================================================
class TestGroup08PunctuationSanitization:
    def test_ellipses_and_dashes(self):
        text = "Suy nghĩ... hành động — kết quả: thành công; bài học."
        res = normalize_for_tts(text)
        assert "..." not in res
        assert "—" not in res
        assert ":" not in res
        assert ";" not in res
        assert ",," not in res
        assert res == "Suy nghĩ, hành động, kết quả, thành công, bài học."

    def test_unicode_punctuation_and_orphan_commas(self):
        text = ", Điểm một… – điểm hai: ; điểm ba. ,"
        res = normalize_for_tts(text)
        assert not res.startswith(",")
        assert not res.endswith(",")
        assert res == "Điểm một, điểm hai, điểm ba."


# ==============================================================================
# Group 9: Gatekeeper Validation (detect_unnormalized_tokens & enforce_tts_normalization_gate)
# ==============================================================================
class TestGroup09GatekeeperValidation:
    def test_clean_sentence_passes_gate(self):
        clean = "Năm một nghìn chín trăm chín mươi lăm, họ làm việc mười bảy giờ trên tuần."
        assert detect_unnormalized_tokens(clean) == []
        assert enforce_tts_normalization_gate(clean) == clean

    def test_unnormalized_digit_rejected(self):
        raw = "Còn 5 ngày nữa."
        issues = detect_unnormalized_tokens(raw)
        assert any(i["token"] == "5" for i in issues)

    def test_unnormalized_foreign_token_raises_in_gate(self):
        with pytest.raises(ValueError, match="UNNORMALIZED_FOREIGN_TOKEN"):
            enforce_tts_normalization_gate("Chiến lược marketing này.")

    def test_unnormalized_symbol_rejected(self):
        issues = detect_unnormalized_tokens("Đạt 50% chỉ tiêu.")
        assert any(i["token"] == "%" for i in issues)

        issues_slash = detect_unnormalized_tokens("Làm việc 17 giờ/tuần.")
        assert any(i["token"] == "/" for i in issues_slash)

    def test_foreign_words_rejected(self):
        for word in ["marketing", "workflow", "facebook", "flashback"]:
            issues = detect_unnormalized_tokens(f"Chiến lược {word} này.")
            assert len(issues) > 0

    def test_allowed_tokens_whitelist(self):
        text = "Chiến lược marketing này."
        assert len(detect_unnormalized_tokens(text)) > 0
        assert len(detect_unnormalized_tokens(text, allowed_tokens={"marketing"})) == 0


# ==============================================================================
# Group 10: Pause Splitting (split_utterances_by_pause)
# ==============================================================================
class TestGroup10PauseSplitting:
    def test_single_pause_split(self):
        text = "Việc này rất khó. [pause:800ms] Nhưng kết quả lại bất ngờ."
        parts = split_utterances_by_pause(text)
        assert len(parts) == 2
        assert parts[0]["text"] == "Việc này rất khó."
        assert parts[0]["pause_after"] == 0.8
        assert parts[1]["text"] == "Nhưng kết quả lại bất ngờ."
        assert parts[1]["pause_after"] == 0.0

    def test_adjacent_pause_tags_summed(self):
        text = "Dừng lại. [pause:200ms][pause:300ms] Bắt đầu tiếp."
        parts = split_utterances_by_pause(text)
        assert len(parts) == 2
        assert parts[0]["pause_after"] == 0.5

    def test_seconds_notation_pause(self):
        text = "Đợi một chút. [pause:1.2s] Xong."
        parts = split_utterances_by_pause(text)
        assert parts[0]["pause_after"] == 1.2


# ==============================================================================
# Group 11: Opening Hook Length Gate (OPENING_HOOK_TOO_LONG)
# ==============================================================================
class TestGroup11OpeningHookLengthGate:
    def test_opening_hook_under_18_syllables_passes(self):
        checker = ScriptCadenceChecker(max_opening_hook_syllables=18)
        # 18 syllables: "Chuông báo thức sáu giờ sáng thực chất là tờ hóa đơn đòi nợ thời gian của bạn."
        scenes = [
            {
                "id": "SC01",
                "duration": 6.0,
                "narration": "Chuông báo thức sáu giờ sáng thực chất là tờ hóa đơn đòi nợ thời gian của bạn.",
            }
        ]
        res = checker.check_scenes(scenes)
        warnings = res["scenes"][0]["warnings"]
        assert not any("OPENING_HOOK_TOO_LONG" in w for w in warnings)

    def test_opening_hook_exceeding_18_syllables_warns(self):
        checker = ScriptCadenceChecker(max_opening_hook_syllables=18)
        # 19 syllables: adds "hôm nay"
        scenes = [
            {
                "id": "SC01",
                "duration": 6.0,
                "narration": "Chuông báo thức sáu giờ sáng hôm nay thực chất là tờ hóa đơn đòi nợ thời gian của bạn.",
            }
        ]
        res = checker.check_scenes(scenes)
        warnings = res["scenes"][0]["warnings"]
        assert any("OPENING_HOOK_TOO_LONG" in w for w in warnings)

    def test_non_opening_scene_does_not_trigger_hook_warning(self):
        checker = ScriptCadenceChecker(max_opening_hook_syllables=18)
        scenes = [
            {"id": "SC01", "duration": 5.0, "narration": "Câu mở đầu ngắn."},
            {
                "id": "SC02",
                "duration": 8.0,
                "narration": "Chuông báo thức sáu giờ sáng hôm nay thực chất là tờ hóa đơn đòi nợ thời gian của bạn.",
            },
        ]
        res = checker.check_scenes(scenes)
        warnings_sc02 = res["scenes"][1]["warnings"]
        assert not any("OPENING_HOOK_TOO_LONG" in w for w in warnings_sc02)


# ==============================================================================
# Group 12: Opening Scene Pause Ban (OPENING_SCENE_PAUSE_FORBIDDEN)
# ==============================================================================
class TestGroup12OpeningScenePauseBan:
    def test_opening_scene_with_pause_warns(self):
        checker = ScriptCadenceChecker(forbid_opening_pause=True)
        scenes = [
            {
                "id": "SC01",
                "duration": 5.0,
                "narration": "Câu mở đầu. [pause:800ms] Không được dừng.",
            }
        ]
        res = checker.check_scenes(scenes)
        warnings = res["scenes"][0]["warnings"]
        assert any("OPENING_SCENE_PAUSE_FORBIDDEN" in w for w in warnings)

    def test_non_opening_scene_allows_pause(self):
        checker = ScriptCadenceChecker(forbid_opening_pause=True)
        scenes = [
            {"id": "SC01", "duration": 5.0, "narration": "Câu mở đầu không có dừng."},
            {
                "id": "SC02",
                "duration": 6.0,
                "narration": "Điểm mấu chốt ở đây. [pause:800ms] Bạn thấy chưa?",
            },
        ]
        res = checker.check_scenes(scenes)
        warnings_sc02 = res["scenes"][1]["warnings"]
        assert not any("OPENING_SCENE_PAUSE_FORBIDDEN" in w for w in warnings_sc02)

    def test_narration_pauses_split_opening_raises_error(self):
        settings = get_profile("short_9x16")["narration_pauses"]
        with pytest.raises(ValueError, match="OPENING_SCENE_PAUSE_FORBIDDEN"):
            split_narration("Chào bạn. [pause:800ms] Tiếp theo.", settings, opening=True)


# ==============================================================================
# Group 13: Breathless Clause Gate (BREATHLESS_CLAUSE)
# ==============================================================================
class TestGroup13BreathlessClauseGate:
    def test_clause_under_18_syllables_passes(self):
        checker = ScriptCadenceChecker(max_clause_syllables=18)
        scenes = [
            {
                "id": "SC01",
                "duration": 5.0,
                "narration": "Vế một có mười âm tiết thôi, vế hai cũng chỉ có mười âm tiết.",
            }
        ]
        res = checker.check_scenes(scenes)
        assert not any("BREATHLESS_CLAUSE" in w for w in res["scenes"][0]["warnings"])

    def test_clause_exceeding_18_syllables_warns(self):
        checker = ScriptCadenceChecker(max_clause_syllables=18)
        # 19 words without comma: "Một hai ba bốn năm sáu bảy tám chín mười mười một mười hai mười ba mười bốn mười lăm mười sáu mười bảy mười tám mười chín."
        scenes = [
            {
                "id": "SC01",
                "duration": 8.0,
                "narration": "Một thợ săn Kalahari chỉ cần mười bảy giờ mỗi tuần để kiếm đủ thức ăn cho cả gia đình.",
            }
        ]
        res = checker.check_scenes(scenes)
        assert any("BREATHLESS_CLAUSE" in w for w in res["scenes"][0]["warnings"])


# ==============================================================================
# Group 14: Dramatic Pause Duration Preservation & Clean Chunks
# ==============================================================================
class TestGroup14DramaticPausePreservation:
    def test_normalize_with_preserve_pauses(self):
        raw = "Việc này rất khó. [pause:800ms] Nhưng kết quả lại bất ngờ."
        norm = normalize_for_tts(raw, preserve_pauses=True)
        assert "[pause:800ms]" in norm
        chunks, gaps = adapters.chunks_with_gaps(norm)
        assert chunks == ["Việc này rất khó.", "Nhưng kết quả lại bất ngờ."]
        assert gaps == [0.8]
        assert not chunks[1].startswith(",")

    def test_multi_tag_summation_preserved(self):
        raw = "Dừng lại. [pause:200ms][pause:600ms] Tiếp tục."
        norm = normalize_for_tts(raw, preserve_pauses=True)
        assert "[pause:200ms]" in norm and "[pause:600ms]" in norm
        chunks, gaps = adapters.chunks_with_gaps(norm)
        assert gaps == [0.8]


# ==============================================================================
# Group 15: Dual Format Pause Budgets (format_v1)
# ==============================================================================
class TestGroup15DualFormatPauseBudgets:
    def test_short_9x16_vs_long_16x9_budgets(self):
        p_short = get_profile("short_9x16")["narration_pauses"]
        p_long = get_profile("long_16x9")["narration_pauses"]

        assert p_short["short_sentence"] == 0.16
        assert p_short["sentence"] == 0.22
        assert p_short["scene"] == 0.30
        assert p_short["tail"] == 0.15

        assert p_long["short_sentence"] == 0.20
        assert p_long["sentence"] == 0.28
        assert p_long["scene"] == 0.40
        assert p_long["tail"] == 0.25

    def test_dual_brief_resolves_to_16x9_clock(self):
        brief = {
            "aspect_ratio": "dual",
            "outputs": [
                {"aspect_ratio": "9:16", "language": "vi", "subtitles": True},
                {"aspect_ratio": "16:9", "language": "vi", "subtitles": False},
            ],
        }
        settings = settings_for_language(brief, "vi")
        assert settings["sentence"] == 0.28
        assert settings["short_sentence"] == 0.20


# ==============================================================================
# Group 16: Voice Profile Contract & Spinoff Hook Gate
# ==============================================================================
class TestGroup16VoiceProfileAndSpinoffHookGate:
    def test_canonical_viet_narrator_profile(self):
        profile_path = ROOT / "assets/voices/viet_narrator/profile.json"
        assert profile_path.is_file()
        import json
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        assert profile["voice"] == "VietNarrator"
        assert profile["source_speed"] == 1.0
        assert profile["sha256"] == "ec54c744434ab5569f3d7a3c542607ddbfd3bd02023a1d0232a17523fce32681"

    def test_spinoff_hook_duration_bounds(self, tmp_path):
        import json
        import wave

        from colab_bridge.protocol import validate_result

        folder = tmp_path
        models = {"vi": {"revision": "a" * 40}}
        req = {
            "request_id": "req_spinoff",
            "primary_language": "vi",
            "profiles": {"vi": {"voice": "VietNarrator"}},
            "models": models,
            "segments": [],
            "english": [],
            "spinoff_hooks": [{"id": "hook_01", "text": "Nghịch lý nhận thức", "item": 0}],
        }

        def write_spinoff_result(dur: float):
            wav_path = folder / "hook.wav"
            with wave.open(str(wav_path), "wb") as w:
                w.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
                w.writeframes(b"\x00\x20" * round(max(0.0, dur) * 48000))
            payload = {
                "request_id": "req_spinoff",
                "voice": "VietNarrator",
                "engine": {"backend": "colab-omnivoice", "models": models, "device": "Tesla T4"},
                "segments": [],
                "spinoff_hooks": [{"id": "hook_01", "text": "Nghịch lý nhận thức", "path": "hook.wav", "duration": dur}],
            }
            (folder / "tts-result.json").write_text(json.dumps(payload))

        # Valid durations (0 < d <= 3.0) pass validate_result
        for d in [2.5, 3.0]:
            write_spinoff_result(d)
            names = validate_result(folder, req)
            assert "hook.wav" in names

        # Invalid durations (d > 3.0 or d <= 0) raise ValueError("Standalone hook identity/duration mismatch")
        for d in [0.0, -0.5, 3.01, 3.5]:
            write_spinoff_result(d)
            with pytest.raises(ValueError, match="Standalone hook identity/duration mismatch"):
                validate_result(folder, req)


# ==============================================================================
# Group 17: Tone Speed Modulation & Bilingual Spans
# ==============================================================================
class TestGroup17ToneSpeedsAndBilingualSpans:
    def test_tone_speed_multipliers(self):
        from colab_bridge.protocol import TONE_SPEED_MULTIPLIERS, resolve_tone_speed

        assert TONE_SPEED_MULTIPLIERS["narrative_warm"] == 0.98
        assert TONE_SPEED_MULTIPLIERS["analytical_crisp"] == 1.02
        assert TONE_SPEED_MULTIPLIERS["reflective_slow"] == 0.92

        assert resolve_tone_speed(1.0, "narrative_warm") == 0.98
        assert resolve_tone_speed(1.0, "analytical_crisp") == 1.02
        assert resolve_tone_speed(1.0, "reflective_slow") == 0.92
        assert resolve_tone_speed(1.0, None) == 1.0

    def test_english_parts_extraction_and_span_gap(self):
        text = 'Nghiên cứu nói rằng: "Deep work requires intense focus." Hãy rèn luyện nó.'
        parts = adapters.english_parts(text, words=["deep work"])
        assert any(p["lang"] == "en" for p in parts)
        assert any(p["lang"] == "vi" for p in parts)
