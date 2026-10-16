#!/usr/bin/env python3
"""Test suite for script cadence checker tool and acoustic dead-air formula.

Validates:
1. Exact syllable counting and dead-air calculations on the 6 benchmark scenes (SC01-SC06)
   from voice-cadence-pacing.md (updated with Truth-Slap Hook, 0 banned phrases).
2. Dramatic pause extraction ([pause:900ms]).
3. Detection of speech rate warnings (> 4.5 syl/s, < 3.2 syl/s).
4. Detection of dead-air / timeline drift (> 0.5s) and duration too short overhead.
5. Detection of OPENING_SCENE_PAUSE_FORBIDDEN and OPENING_HOOK_TOO_LONG.
6. JSON and Markdown parser compatibility (tables, headings with spaces, Vietnamese headers, non-scene sections).
7. CLI interface execution.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from script_cadence_checker import (  # noqa: E402
    ScriptCadenceChecker,
    calculate_target_syllables,
    count_commas,
    count_english_syllables_in_word,
    count_syllables,
    extract_pauses,
    parse_json_script,
    parse_markdown_script,
)

BENCHMARK_SCENES = [
    {
        "id": "SC01",
        "duration": 12.0,
        "narration": "Chuông báo thức sáu giờ sáng thực chất là tờ hóa đơn đòi nợ thời gian của bạn. Tiếng chuông réo vang inh ỏi phá tan giấc ngủ ngon. Bạn thức dậy mệt mỏi, và tối nay lại nơm nớp lo ngày mai lặp lại.",
        "expected_target_syl": 45,
        "expected_actual_syl": 45,
        "expected_p_tail": 0.70,
        "expected_est_audio": 11.95,
        "expected_drift": -0.05,
    },
    {
        "id": "SC02",
        "duration": 12.0,
        "narration": "Quay ngược dòng thời gian về năm mươi ngàn năm trước, một nghịch lý lớn chợt hiện ra. Tổ tiên săn bắt hái lượm nơi hoang dã đã sống ra sao? Liệu họ có thực sự sống kiếp khốn khổ, mệt mỏi như ta lầm tưởng?",
        "expected_target_syl": 45,
        "expected_actual_syl": 46,
        "expected_p_tail": 0.70,
        "expected_est_audio": 12.20,
        "expected_drift": 0.20,
    },
    {
        "id": "SC03",
        "duration": 14.0,
        "narration": "Các cuốn sách giáo khoa lịch sử từ trước đến nay vẫn thường miêu tả cuộc sống tiền sử như một chuỗi ngày triền miên chìm trong đói khát, hiểm nguy rình rập và cuộc chiến sinh tồn tàn khốc không có lấy một phút giây nào được thảnh thơi ngơi nghỉ.",
        "expected_target_syl": 53,
        "expected_actual_syl": 52,
        "expected_p_tail": 0.70,
        "expected_est_audio": 13.70,
        "expected_drift": -0.30,
    },
    {
        "id": "SC04",
        "duration": 14.0,
        "narration": "Thế nhưng, khi các nhà khảo cổ học tiến hành khai quật cẩn thận hàng loạt bộ hài cốt cổ xưa trên khắp các châu lục, những lớp trầm tích địa tầng đã hé lộ một bức tranh hoàn toàn trái ngược với những định kiến sai lầm bấy lâu nay của chúng ta.",
        "expected_target_syl": 53,
        "expected_actual_syl": 54,
        "expected_p_tail": 0.70,
        "expected_est_audio": 14.20,
        "expected_drift": 0.20,
    },
    {
        "id": "SC05",
        "duration": 12.0,
        "narration": "Thời hiện đại chúng ta tự hào sở hữu máy giặt tự động, xe hơi tiện nghi và siêu thị đầy ắp thức ăn — nhưng đã bao giờ bạn tự hỏi ai mới thực sự là người phải lao động vất vả nhiều giờ hơn?",
        "expected_target_syl": 45,
        "expected_actual_syl": 45,
        "expected_p_tail": 0.70,
        "expected_est_audio": 11.95,
        "expected_drift": -0.05,
    },
    {
        "id": "SC06",
        "duration": 11.0,
        "narration": "Bạn kiệt sức gục ngã trước những núi hồ sơ giấy tờ dưới tiếng đồng hồ tích tắc, trong khi người tiền sử đang nằm thảnh thơi tận hưởng buổi hoàng hôn êm đềm bên đống lửa ấm áp của bộ tộc.",
        "expected_target_syl": 43,
        "expected_actual_syl": 42,
        "expected_p_tail": 0.35,
        "expected_est_audio": 10.85,
        "expected_drift": -0.15,
    },
]


class BenchmarkCadenceTests(unittest.TestCase):
    """Test the 6 canonical benchmark scenes from voice-cadence-pacing.md."""

    def test_individual_benchmark_scenes_match_empirical_table(self):
        checker = ScriptCadenceChecker(forbid_opening_pause=True, max_opening_hook_syllables=18)
        input_scenes = [{"id": s["id"], "duration": s["duration"], "narration": s["narration"]} for s in BENCHMARK_SCENES]
        result = checker.check_scenes(input_scenes)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["warnings_count"], 0)
        self.assertEqual(len(result["scenes"]), 6)

        for i, expected in enumerate(BENCHMARK_SCENES):
            scene_res = result["scenes"][i]
            self.assertEqual(scene_res["scene_id"], expected["id"])
            self.assertAlmostEqual(scene_res["duration"], expected["duration"], places=2)
            self.assertAlmostEqual(scene_res["p_tail"], expected["expected_p_tail"], places=2)
            self.assertEqual(scene_res["target_syllables"], expected["expected_target_syl"])
            self.assertEqual(scene_res["actual_syllables"], expected["expected_actual_syl"])
            self.assertAlmostEqual(scene_res["estimated_audio_duration"], expected["expected_est_audio"], places=2)
            self.assertAlmostEqual(scene_res["drift"], expected["expected_drift"], places=2)
            self.assertEqual(scene_res["status"], "PASS")

    def test_benchmark_aggregate_totals(self):
        checker = ScriptCadenceChecker(forbid_opening_pause=True, max_opening_hook_syllables=18)
        input_scenes = [{"id": s["id"], "duration": s["duration"], "narration": s["narration"]} for s in BENCHMARK_SCENES]
        result = checker.check_scenes(input_scenes)

        self.assertAlmostEqual(result["total_duration"], 75.0, places=2)
        self.assertEqual(result["total_target_syllables"], 284)
        self.assertEqual(result["total_actual_syllables"], 284)
        self.assertAlmostEqual(result["total_estimated_audio"], 74.85, places=2)
        self.assertAlmostEqual(result["net_drift"], -0.15, places=2)
        self.assertLessEqual(result["max_drift"], 0.30)
        self.assertEqual(result["status"], "PASS")

    def test_parse_and_check_live_voice_cadence_pacing_doc(self):
        from script_diversity_linter import check_formulaic_transitions

        playbook_path = ROOT.parent / ".agents/skills/vp-channel-patterns/references/voice-cadence-pacing.md"
        checker = ScriptCadenceChecker(forbid_opening_pause=True, max_opening_hook_syllables=18)
        result = checker.check_file(playbook_path)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["total_scenes"], 6)
        self.assertEqual(result["total_target_syllables"], 284)
        self.assertEqual(result["total_actual_syllables"], 284)
        self.assertLessEqual(result["max_drift"], 0.30)

        # Ensure live voice-cadence-pacing.md has 0 banned formulaic transitions ("Hãy nghĩ về...")
        parsed_scenes = parse_markdown_script(playbook_path.read_text(encoding="utf-8"))
        self.assertEqual(check_formulaic_transitions(parsed_scenes), [])


class SyllableAndPauseTests(unittest.TestCase):
    """Test pause extraction and syllable counting."""

    def test_dramatic_pause_extraction(self):
        text = "Các cuốn sách nói rằng họ chết đói... [pause:900ms] nhưng các bộ hài cốt lại kể chuyện khác."
        total_sec, pauses, clean = extract_pauses(text)
        self.assertAlmostEqual(total_sec, 0.9, places=2)
        self.assertEqual(len(pauses), 1)
        self.assertEqual(pauses[0]["seconds"], 0.9)
        self.assertNotIn("[pause:900ms]", clean)

    def test_second_formatted_pauses(self):
        text = "Mọi thứ dừng lại [pause:1.2s] rồi tiếp tục [pause:500ms]."
        total_sec, pauses, clean = extract_pauses(text)
        self.assertAlmostEqual(total_sec, 1.7, places=2)
        self.assertEqual(len(pauses), 2)
        self.assertAlmostEqual(pauses[0]["seconds"], 1.2, places=2)
        self.assertAlmostEqual(pauses[1]["seconds"], 0.5, places=2)

    def test_vietnamese_syllable_count_with_emdash_and_punctuation(self):
        text = "Thời hiện đại chúng ta tự hào sở hữu máy giặt tự động — nhưng ai mới thực sự mệt hơn?"
        syl = count_syllables(text, lang="vi")
        self.assertEqual(syl, 20)

    def test_english_syllable_counter(self):
        self.assertEqual(count_syllables("civilization", lang="en"), 5)
        self.assertEqual(count_syllables("machine", lang="en"), 2)
        self.assertEqual(count_syllables("skeleton", lang="en"), 3)
        self.assertEqual(count_syllables("ancient", lang="en"), 2)
        self.assertEqual(count_syllables("time", lang="en"), 1)
        self.assertEqual(count_syllables("mystery", lang="en"), 3)

    def test_english_split_vowels_hiatus(self):
        self.assertEqual(count_english_syllables_in_word("video"), 3)
        self.assertEqual(count_english_syllables_in_word("audio"), 3)
        self.assertEqual(count_english_syllables_in_word("media"), 3)
        self.assertEqual(count_english_syllables_in_word("area"), 3)
        self.assertEqual(count_english_syllables_in_word("idea"), 3)
        self.assertEqual(count_english_syllables_in_word("radio"), 3)
        self.assertEqual(count_english_syllables_in_word("studio"), 3)
        self.assertEqual(count_english_syllables_in_word("piano"), 3)
        self.assertEqual(count_english_syllables_in_word("creative"), 3)
        self.assertEqual(count_english_syllables_in_word("creation"), 3)

    def test_vietnamese_compounds_numbers_and_slashes(self):
        self.assertEqual(count_syllables("17 giờ/tuần", lang="vi"), 4)
        self.assertEqual(count_syllables("2.4 giờ/ngày", lang="vi"), 5)
        self.assertEqual(count_syllables("50.000 năm trước", lang="vi"), 5)
        self.assertEqual(count_syllables("90.000 giờ làm việc trong đời", lang="vi"), 8)
        self.assertEqual(count_syllables("40-50 giờ", lang="vi"), 5)
        self.assertEqual(count_syllables("smartphone", lang="vi"), 2)
        self.assertEqual(count_syllables("wifi", lang="vi"), 2)
        self.assertEqual(count_syllables("data", lang="vi"), 2)
        self.assertEqual(count_syllables("AI", lang="vi"), 2)

    def test_count_commas_ignores_numbers(self):
        self.assertEqual(count_commas("chiếm 2,4 giờ mỗi ngày và 50,000 năm"), 0)
        self.assertEqual(count_commas("Chào bạn, đây là 2,4 giờ, và 50,000 năm; bạn hiểu chưa?"), 3)

    def test_calculate_target_syllables_formula(self):
        self.assertEqual(calculate_target_syllables(12.0, is_last=False), 45)
        self.assertEqual(calculate_target_syllables(11.0, is_last=True), 43)
        self.assertEqual(calculate_target_syllables(12.0, is_last=False, pause_seconds=0.9), 42)


class ThresholdWarningTests(unittest.TestCase):
    """Test detection of speech rate, timeline drift, opening pause, and opening hook warnings."""

    def test_speech_rate_too_fast_warning(self):
        checker = ScriptCadenceChecker()
        scene = {
            "id": "FAST",
            "duration": 8.0,
            "narration": "Chuông báo thức sáu giờ sáng thực chất là tờ hóa đơn đòi nợ thời gian của bạn. Tiếng chuông réo vang inh ỏi phá tan giấc ngủ ngon. Bạn thức dậy mệt mỏi, và tối nay lại nơm nớp lo ngày mai lặp lại.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertGreater(res["warnings_count"], 0)
        self.assertTrue(any("RATE_TOO_FAST" in w for w in res["scenes"][0]["warnings"]))

    def test_speech_rate_too_slow_warning(self):
        checker = ScriptCadenceChecker()
        scene = {
            "id": "SLOW",
            "duration": 12.0,
            "narration": "Đọc lại giáo trình năm lần chỉ ru ngủ não bạn.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("RATE_TOO_SLOW" in w for w in res["scenes"][0]["warnings"]))

    def test_short_duration_overhead_warning(self):
        checker = ScriptCadenceChecker()
        scenes = [
            {"id": "SHORT", "duration": 0.5, "narration": "Xin chào tất cả các bạn hôm nay."},
            {"id": "FINAL", "duration": 10.0, "narration": "Câu chuyện tiếp tục ở phân cảnh tiếp theo của chúng ta."},
        ]
        res = checker.check_scenes(scenes)
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("DURATION_TOO_SHORT" in w for w in res["scenes"][0]["warnings"]))
        self.assertFalse(any("RATE_TOO_SLOW" in w for w in res["scenes"][0]["warnings"]))

    def test_dead_air_warning(self):
        checker = ScriptCadenceChecker()
        scene = {
            "id": "DEAD",
            "duration": 15.0,
            "narration": "Đọc lại giáo trình năm lần chỉ ru ngủ não bạn.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("DEAD_AIR" in w for w in res["scenes"][0]["warnings"]))

    def test_timeline_drift_overflow_warning(self):
        checker = ScriptCadenceChecker()
        words = " ".join(["từ"] * 60)
        scene = {
            "id": "OVERFLOW",
            "duration": 10.0,
            "narration": words,
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("TIMELINE_DRIFT" in w for w in res["scenes"][0]["warnings"]))

    def test_sentence_fragmentation_warning(self):
        checker = ScriptCadenceChecker()
        scene = {
            "id": "FRAG",
            "duration": 10.0,
            "narration": "Tám giờ sáng. Cà phê nguội. Bạn ngồi yên trước màn hình. Công việc dồn lại. Bạn không thể gõ phím.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertEqual(res["scenes"][0]["sentence_count"], 5)
        self.assertTrue(any("SENTENCE_FRAGMENTATION" in w for w in res["scenes"][0]["warnings"]))

        micro_scene = {
            "id": "MICRO_FRAG",
            "duration": 8.0,
            "narration": "Tám giờ sáng. Cà phê nguội. Mắt mỏi mệt. Bạn vẫn ngồi nhìn màn hình máy tính trắng trơn suốt một tiếng đồng hồ.",
        }
        res_micro = checker.check_scenes([micro_scene])
        self.assertEqual(res_micro["status"], "WARN")
        self.assertEqual(res_micro["scenes"][0]["sentence_count"], 4)
        self.assertTrue(any("SENTENCE_FRAGMENTATION" in w for w in res_micro["scenes"][0]["warnings"]))

    def test_concise_scene_max_syllables_warning(self):
        checker = ScriptCadenceChecker(max_syllables=20)
        long_scene = {
            "id": "LONG",
            "duration": 10.0,
            "narration": "Đây là một câu chuyện rất dài dòng về nghiên cứu khoa học xã hội và hành vi con người trong xã hội hiện đại ngày nay.",
        }
        res = checker.check_scenes([long_scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("SCENE_TOO_LONG" in w for w in res["scenes"][0]["warnings"]))

        short_scene = {
            "id": "SHORT",
            "duration": 5.0,
            "narration": "Hạch hạnh nhân lập tức kích hoạt phản xạ trốn chạy.",
        }
        res_ok = checker.check_scenes([short_scene])
        self.assertFalse(any("SCENE_TOO_LONG" in w for w in res_ok["scenes"][0]["warnings"]))

    def test_sentence_too_long_warning(self):
        checker = ScriptCadenceChecker(max_sentence_syllables=25)
        scene = {
            "id": "LONG_SENT",
            "duration": 15.0,
            "narration": "Dòng dữ liệu thời gian thực báo hiệu người dùng mang mã số tám bốn chín hai bắt đầu cựa mình thức giấc sau một đêm dài say ngủ thật sự.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("SENTENCE_TOO_LONG" in w for w in res["scenes"][0]["warnings"]))

        scene_ok = {
            "id": "OK_SENT",
            "duration": 6.0,
            "narration": "Trên màn hình, mã số tám bốn chín hai bắt đầu cựa mình thức giấc.",
        }
        res_ok = checker.check_scenes([scene_ok])
        self.assertFalse(any("SENTENCE_TOO_LONG" in w for w in res_ok["scenes"][0]["warnings"]))

    def test_breathless_clause_warning(self):
        checker = ScriptCadenceChecker(max_clause_syllables=18)
        scene = {
            "id": "NO_COMMA",
            "duration": 8.0,
            "narration": "Đây chính là khoảnh khắc vàng khi sức đề kháng tâm lý của con người rơi xuống điểm thấp nhất trong một ngày dài.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("BREATHLESS_CLAUSE" in w for w in res["scenes"][0]["warnings"]))

        scene_ok = {
            "id": "WITH_COMMA",
            "duration": 8.0,
            "narration": "Đây chính là khoảnh khắc vàng, khi sức đề kháng tâm lý, rơi xuống điểm thấp nhất trong ngày.",
        }
        res_ok = checker.check_scenes([scene_ok])
        self.assertFalse(any("BREATHLESS_CLAUSE" in w for w in res_ok["scenes"][0]["warnings"]))

    def test_excessive_dramatic_pauses_warning(self):
        checker = ScriptCadenceChecker(max_dramatic_pauses=2)
        scenes = [
            {"id": "SC01", "duration": 8.0, "narration": "Câu một. [pause:800ms] Câu hai."},
            {"id": "SC02", "duration": 8.0, "narration": "Câu ba. [pause:800ms] Câu bốn."},
            {"id": "SC03", "duration": 8.0, "narration": "Câu năm. [pause:800ms] Câu sáu."},
        ]
        res = checker.check_scenes(scenes)
        self.assertEqual(res["status"], "WARN")
        for sc in res["scenes"]:
            self.assertTrue(any("EXCESSIVE_DRAMATIC_PAUSES" in w for w in sc["warnings"]))

    def test_opening_scene_pause_forbidden_and_hook_length_warnings(self):
        checker = ScriptCadenceChecker(forbid_opening_pause=True, max_opening_hook_syllables=18)
        bad_opening = [
            {
                "id": "SC01",
                "duration": 10.0,
                "narration": "Việc đọc đi đọc lại một cuốn giáo trình đại học tới năm lần liên tiếp thực chất chỉ đang tạo ra ảo giác năng lực giả tạo. [pause:800ms] Bạn vẫn không hiểu bản chất.",
            },
            {
                "id": "SC02",
                "duration": 9.0,
                "narration": "Tám mươi phần trăm sinh viên mở Word gõ ngay. [pause:900ms] Nhưng giáo sư đọc ngược lại.",
            },
        ]
        res = checker.check_scenes(bad_opening)
        self.assertEqual(res["status"], "WARN")
        sc1_warns = res["scenes"][0]["warnings"]
        sc2_warns = res["scenes"][1]["warnings"]
        self.assertTrue(any("OPENING_SCENE_PAUSE_FORBIDDEN" in w for w in sc1_warns))
        self.assertTrue(any("OPENING_HOOK_TOO_LONG" in w for w in sc1_warns))
        # SC02 is allowed to have a dramatic pause
        self.assertFalse(any("OPENING_SCENE_PAUSE_FORBIDDEN" in w for w in sc2_warns))

    def test_reproduction_err_20261014_01(self):
        """End-to-end reproduction of ERR-20261014-01 cadence gaming."""
        checker = ScriptCadenceChecker(
            max_sentence_syllables=25,
            max_clause_syllables=18,
            max_dramatic_pauses=1,
            forbid_opening_pause=True,
        )
        attention_sample = [
            {
                "id": "SC01",
                "duration": 15.0,
                "narration": "Sáu giờ ba mươi phút sáng tại Thung lũng Silicon, màn hình máy chủ trung tâm rực sáng ánh đèn tín hiệu. [pause:800ms] Dòng dữ liệu thời gian thực báo hiệu người dùng mang mã số tám bốn chín hai bắt đầu cựa mình thức giấc sau một đêm dài say ngủ thật sự.",
            },
            {
                "id": "SC02",
                "duration": 15.0,
                "narration": "Đây chính là khoảnh khắc vàng khi sức đề kháng tâm lý của con người rơi xuống điểm thấp nhất trong một ngày dài. [pause:800ms] Lượng hormone tỉnh táo này chưa kịp dâng lên trong máu, khiến vùng não lý trí hoàn toàn buông lỏng mọi cơ chế cảnh giác và đề phòng tự nhiên.",
            },
        ]
        res = checker.check_scenes(attention_sample)
        self.assertEqual(res["status"], "WARN")
        all_warnings = [w for sc in res["scenes"] for w in sc["warnings"]]
        self.assertTrue(any("SENTENCE_TOO_LONG" in w for w in all_warnings))
        self.assertTrue(any("BREATHLESS_CLAUSE" in w for w in all_warnings))
        self.assertTrue(any("EXCESSIVE_DRAMATIC_PAUSES" in w for w in all_warnings))
        self.assertTrue(any("OPENING_SCENE_PAUSE_FORBIDDEN" in w for w in all_warnings))


class ScriptParserTests(unittest.TestCase):
    """Test parsing JSON and Markdown formats."""

    def test_parse_json_formats(self):
        json_list = json.dumps([{"id": "SC01", "duration": 12.0, "narration": "Thoại mẫu."}])
        parsed = parse_json_script(json_list)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[0]["duration"], 12.0)

        json_dict = json.dumps({"scenes": [{"id": "SC02", "duration": 10.0, "narration": "Thoại 2."}]})
        parsed2 = parse_json_script(json_dict)
        self.assertEqual(len(parsed2), 1)
        self.assertEqual(parsed2[0]["id"], "SC02")

    def test_parse_markdown_header_format(self):
        md = """
# Kịch bản Mẫu

## SC01 (12.0s)
Đọc lại giáo trình năm lần chỉ ru ngủ não bạn.
[Visual: Stick figure thức dậy]

## SC02 (14.0s)
Quay ngược dòng thời gian về năm mươi ngàn năm trước.
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[0]["duration"], 12.0)
        self.assertIn("Đọc lại giáo trình", parsed[0]["narration"])
        self.assertNotIn("[Visual:", parsed[0]["narration"])

        self.assertEqual(parsed[1]["id"], "SC02")
        self.assertEqual(parsed[1]["duration"], 14.0)

    def test_parse_markdown_header_with_spaces_and_diacritics(self):
        md = """
### Scene 1 [12s]
Đọc lại giáo trình năm lần chỉ ru ngủ não bạn.

## Phân cảnh 02 (14.5s)
Quay ngược dòng thời gian về năm mươi ngàn năm trước.
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "Scene 1")
        self.assertEqual(parsed[0]["duration"], 12.0)
        self.assertEqual(parsed[1]["id"], "Phân cảnh 02")
        self.assertEqual(parsed[1]["duration"], 14.5)

    def test_parse_markdown_excludes_trailing_non_scene_sections(self):
        md = """
## SC01 (10.0s)
Câu thoại của cảnh thứ nhất.

## Ghi chú sản xuất
Lưu ý quan trọng: không được chèn phần này vào kịch bản audio.
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[0]["narration"], "Câu thoại của cảnh thứ nhất.")

    def test_parse_markdown_table_format(self):
        md = """
| Scene | Duration | Narration |
|---|---|---|
| SC01 | 12.0s | Chuông báo thức sáu giờ sáng. |
| SC02 | 11.0s | Bạn kiệt sức gục ngã. |
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[0]["duration"], 12.0)
        self.assertEqual(parsed[1]["id"], "SC02")
        self.assertEqual(parsed[1]["duration"], 11.0)

    def test_parse_markdown_table_vietnamese_column_headers(self):
        md = """
| Cảnh | Thời lượng | Lời thoại |
|---|---|---|
| SC01 | 12.0s | Xin chào các bạn. |
| SC02 | 10.0s | Hẹn gặp lại. |
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[0]["duration"], 12.0)
        self.assertEqual(parsed[0]["narration"], "Xin chào các bạn.")

    def test_parse_markdown_multiple_tables_selects_script_table(self):
        md = """
# Tổng quan

| ID | Duration | Narration Note | Status |
|---|---|---|---|
| Summary | 60s | Toàn bộ video tóm tắt | Done |

# Chi tiết phân cảnh

| Cảnh | Thời lượng | Lời thoại |
|---|---|---|
| SC01 | 12.0s | Câu thoại 1. |
| SC02 | 14.0s | Câu thoại 2. |
| SC03 | 11.0s | Câu thoại 3. |
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[2]["id"], "SC03")


class CliExecutionTests(unittest.TestCase):
    """Test CLI invocation."""

    def test_cli_execution_with_benchmark_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(BENCHMARK_SCENES, f, ensure_ascii=False)
            tmp_path = f.name

        try:
            cli_script = ROOT / "tools/script_cadence_checker.py"
            proc = subprocess.run(
                [sys.executable, str(cli_script), tmp_path, "--json", "--strict", "--forbid-opening-pause", "--max-opening-hook-syllables", "18"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "PASS")
            self.assertEqual(data["total_target_syllables"], 284)
            self.assertEqual(data["total_actual_syllables"], 284)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_cli_strict_fails_on_warning(self):
        bad_scene = [{"id": "FAIL", "duration": 5.0, "narration": "Chỉ có năm chữ này thôi"}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(bad_scene, f, ensure_ascii=False)
            tmp_path = f.name

        try:
            cli_script = ROOT / "tools/script_cadence_checker.py"
            proc = subprocess.run(
                [sys.executable, str(cli_script), tmp_path, "--strict"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_cli_max_syllables_flag(self):
        scene = [{"id": "TEST", "duration": 8.0, "narration": "Đây là một câu thoại có độ dài vượt qua mười lăm âm tiết quy định trong bài kiểm tra này."}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(scene, f, ensure_ascii=False)
            tmp_path = f.name

        try:
            cli_script = ROOT / "tools/script_cadence_checker.py"
            proc = subprocess.run(
                [sys.executable, str(cli_script), tmp_path, "--max-syllables", "10", "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "WARN")
            self.assertTrue(any("SCENE_TOO_LONG" in w for w in data["scenes"][0]["warnings"]))
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class ScriptDiversityLinterTests(unittest.TestCase):
    """Test script diversity linter for direct pacing, greetings ban, and academic name-drop ban."""

    def test_banned_greetings_and_filler_transitions(self):
        from script_diversity_linter import check_formulaic_transitions

        scenes = [
            {"id": "SC01", "narration": "Xin chào các bạn đã quay trở lại."},
            {"id": "SC02", "narration": "Chào mừng quý vị đến với kênh hôm nay."},
            {"id": "SC03", "narration": "Hãy nghĩ về một buổi sáng quen thuộc của bạn."},
            {"id": "SC04", "narration": "Để tìm câu trả lời cho hiện tượng này."},
        ]
        violations = check_formulaic_transitions(scenes)
        self.assertEqual(len(violations), 4)
        types = [v["type"] for v in violations]
        self.assertTrue(all(t == "FORMULAIC_TRANSITION" for t in types))

    def test_banned_academic_namedrops(self):
        from script_diversity_linter import check_formulaic_transitions

        scenes = [
            {"id": "SC01", "narration": "Giáo sư Robert Sapolsky đã chứng minh điều này."},
            {"id": "SC02", "narration": "Tiến sĩ Timothy Pychyl tại trường Đại học Carleton phát hiện ra."},
            {"id": "SC03", "narration": "Nghiên cứu năm 2018 của viện tâm lý cho thấy."},
        ]
        violations = check_formulaic_transitions(scenes)
        self.assertGreaterEqual(len(violations), 3)
        namedrop_violations = [v for v in violations if v["type"] == "ACADEMIC_NAMEDROP_BLOAT"]
        self.assertGreaterEqual(len(namedrop_violations), 3)

    def test_direct_concise_narration_passes_cleanly(self):
        from script_diversity_linter import check_formulaic_transitions

        scenes = [
            {"id": "SC01", "narration": "Mỗi lần trì hoãn, não bạn đang kích hoạt cơ chế sinh tồn."},
            {"id": "SC02", "narration": "Hạch hạnh nhân xem áp lực công việc như mối đe dọa trực tiếp."},
        ]
        violations = check_formulaic_transitions(scenes)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
