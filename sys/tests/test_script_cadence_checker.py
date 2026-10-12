#!/usr/bin/env python3
"""Test suite for script cadence checker tool and acoustic dead-air formula.

Validates:
1. Exact syllable counting and dead-air calculations on the 6 benchmark scenes (SC01-SC06)
   from voice-cadence-pacing.md.
2. Dramatic pause extraction ([pause:900ms]).
3. Detection of speech rate warnings (> 4.5 syl/s, < 3.2 syl/s).
4. Detection of dead-air / timeline drift (> 0.5s) and duration too short overhead.
5. JSON and Markdown parser compatibility (tables, headings with spaces, Vietnamese headers, non-scene sections).
6. CLI interface execution.
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
        "narration": "Hãy nghĩ về một buổi sáng quen thuộc của bạn: tiếng chuông báo thức réo vang inh ỏi phá tan giấc ngủ, bạn thức dậy trong mệt mỏi, và ngay tối nay bạn lại nơm nớp lo sợ ngày mai sẽ tiếp tục lặp lại.",
        "expected_target_syl": 45,
        "expected_actual_syl": 45,
        "expected_p_tail": 0.70,
        "expected_est_audio": 11.95,
        "expected_drift": -0.05,
    },
    {
        "id": "SC02",
        "duration": 12.0,
        "narration": "Giờ đây, hãy thử quay ngược dòng thời gian về năm mươi ngàn năm trước. Liệu tổ tiên săn bắt hái lượm của chúng ta có thực sự phải trải qua một kiếp sống khốn khổ và mệt mỏi như chúng ta vẫn hằng tưởng tượng?",
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
        checker = ScriptCadenceChecker()
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
        checker = ScriptCadenceChecker()
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
        playbook_path = ROOT.parent / ".agents/skills/vp-channel-patterns/references/voice-cadence-pacing.md"
        checker = ScriptCadenceChecker()
        result = checker.check_file(playbook_path)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["total_scenes"], 6)
        self.assertEqual(result["total_target_syllables"], 284)
        self.assertEqual(result["total_actual_syllables"], 284)
        self.assertLessEqual(result["max_drift"], 0.30)



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
        # 17 (2) + giờ (1) + tuần (1) = 4
        self.assertEqual(count_syllables("17 giờ/tuần", lang="vi"), 4)
        # 2.4 (3: hai phẩy bốn) + giờ (1) + ngày (1) = 5
        self.assertEqual(count_syllables("2.4 giờ/ngày", lang="vi"), 5)
        # 50.000 (3: năm mươi nghìn) + năm (1) + trước (1) = 5
        self.assertEqual(count_syllables("50.000 năm trước", lang="vi"), 5)
        # 90.000 (3: chín mươi nghìn) + giờ (1) + làm (1) + việc (1) + trong (1) + đời (1) = 8
        self.assertEqual(count_syllables("90.000 giờ làm việc trong đời", lang="vi"), 8)
        # 40-50 (4: bốn mươi năm mươi) + giờ (1) = 5
        self.assertEqual(count_syllables("40-50 giờ", lang="vi"), 5)
        # English loan words and acronyms
        self.assertEqual(count_syllables("smartphone", lang="vi"), 2)
        self.assertEqual(count_syllables("wifi", lang="vi"), 2)
        self.assertEqual(count_syllables("data", lang="vi"), 2)
        self.assertEqual(count_syllables("AI", lang="vi"), 2)

    def test_count_commas_ignores_numbers(self):
        # Decimal and thousands commas should not be counted as speech pauses
        self.assertEqual(count_commas("chiếm 2,4 giờ mỗi ngày và 50,000 năm"), 0)
        # Natural clause commas and semicolons should be counted
        self.assertEqual(count_commas("Chào bạn, đây là 2,4 giờ, và 50,000 năm; bạn hiểu chưa?"), 3)

    def test_calculate_target_syllables_formula(self):
        # Normal intermediate scene: (12.0 - 0.70) * 4.0 = 45.2 -> 45
        self.assertEqual(calculate_target_syllables(12.0, is_last=False), 45)
        # Final scene: (11.0 - 0.35) * 4.0 = 42.6 -> 43
        self.assertEqual(calculate_target_syllables(11.0, is_last=True), 43)
        # Scene with dramatic pause 0.9s: (12.0 - 0.70 - 0.90) * 4.0 = 10.4 * 4.0 = 41.6 -> 42
        self.assertEqual(calculate_target_syllables(12.0, is_last=False, pause_seconds=0.9), 42)


class ThresholdWarningTests(unittest.TestCase):
    """Test detection of speech rate and timeline drift warnings."""

    def test_speech_rate_too_fast_warning(self):
        checker = ScriptCadenceChecker()
        # 45 syllables in 8.0s -> net duration = 8.0 - 0.7 = 7.3s -> rate = 45 / 7.3 = 6.16 syl/s (> 4.5)
        scene = {
            "id": "FAST",
            "duration": 8.0,
            "narration": "Hãy nghĩ về một buổi sáng quen thuộc của bạn: tiếng chuông báo thức réo vang inh ỏi phá tan giấc ngủ, bạn thức dậy trong mệt mỏi, và ngay tối nay bạn lại nơm nớp lo sợ ngày mai sẽ tiếp tục lặp lại.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertGreater(res["warnings_count"], 0)
        self.assertTrue(any("RATE_TOO_FAST" in w for w in res["scenes"][0]["warnings"]))

    def test_speech_rate_too_slow_warning(self):
        checker = ScriptCadenceChecker()
        # 10 syllables in 12.0s -> net = 11.3s -> rate = 10 / 11.3 = 0.88 syl/s (< 3.2)
        scene = {
            "id": "SLOW",
            "duration": 12.0,
            "narration": "Hãy nghĩ về một buổi sáng quen thuộc của bạn.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("RATE_TOO_SLOW" in w for w in res["scenes"][0]["warnings"]))

    def test_short_duration_overhead_warning(self):
        checker = ScriptCadenceChecker()
        # Intermediate scene: 0.5s duration with 8 syllables (p_tail is 0.7s) -> duration <= p_tail, overhead exceeded
        scenes = [
            {"id": "SHORT", "duration": 0.5, "narration": "Xin chào tất cả các bạn hôm nay."},
            {"id": "FINAL", "duration": 10.0, "narration": "Câu chuyện tiếp tục ở phân cảnh tiếp theo của chúng ta."},
        ]
        res = checker.check_scenes(scenes)
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("DURATION_TOO_SHORT" in w for w in res["scenes"][0]["warnings"]))
        # Should not falsely trigger RATE_TOO_SLOW
        self.assertFalse(any("RATE_TOO_SLOW" in w for w in res["scenes"][0]["warnings"]))

    def test_dead_air_warning(self):
        checker = ScriptCadenceChecker()
        # Scene duration is 15.0s, but only has 10 syllables -> est audio = 10/4 + 0.7 = 3.2s -> drift = -11.8s (< -0.5s)
        scene = {
            "id": "DEAD",
            "duration": 15.0,
            "narration": "Hãy nghĩ về một buổi sáng quen thuộc của bạn.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertTrue(any("DEAD_AIR" in w for w in res["scenes"][0]["warnings"]))

    def test_timeline_drift_overflow_warning(self):
        checker = ScriptCadenceChecker()
        # Scene duration is 10.0s, but has 60 syllables -> est audio = 60/4 + 0.7 = 15.7s -> drift = +5.7s (> 0.5s)
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
        # 5 sentences with 2+ short hooks (< 6 syl) triggers SENTENCE_FRAGMENTATION
        scene = {
            "id": "FRAG",
            "duration": 10.0,
            "narration": "Tám giờ sáng. Cà phê nguội. Bạn ngồi yên trước màn hình. Công việc dồn lại. Bạn không thể gõ phím.",
        }
        res = checker.check_scenes([scene])
        self.assertEqual(res["status"], "WARN")
        self.assertEqual(res["scenes"][0]["sentence_count"], 5)
        self.assertTrue(any("SENTENCE_FRAGMENTATION" in w for w in res["scenes"][0]["warnings"]))

        # <= 4 sentences with > 2 micro-sentences (< 6 syl) also triggers SENTENCE_FRAGMENTATION
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
        assert any("SCENE_TOO_LONG" in w for w in res["scenes"][0]["warnings"])

        short_scene = {
            "id": "SHORT",
            "duration": 5.0,
            "narration": "Hạch hạnh nhân lập tức kích hoạt phản xạ trốn chạy.",
        }
        res_ok = checker.check_scenes([short_scene])
        self.assertFalse(any("SCENE_TOO_LONG" in w for w in res_ok["scenes"][0]["warnings"]))
        assert not any("SCENE_TOO_LONG" in w for w in res_ok["scenes"][0]["warnings"])



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
Hãy nghĩ về một buổi sáng quen thuộc của bạn.
[Visual: Stick figure thức dậy]

## SC02 (14.0s)
Giờ đây, hãy thử quay ngược dòng thời gian về năm mươi ngàn năm trước.
        """
        parsed = parse_markdown_script(md)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "SC01")
        self.assertEqual(parsed[0]["duration"], 12.0)
        self.assertIn("Hãy nghĩ về một buổi sáng", parsed[0]["narration"])
        self.assertNotIn("[Visual:", parsed[0]["narration"])

        self.assertEqual(parsed[1]["id"], "SC02")
        self.assertEqual(parsed[1]["duration"], 14.0)

    def test_parse_markdown_header_with_spaces_and_diacritics(self):
        md = """
### Scene 1 [12s]
Hãy nghĩ về một buổi sáng quen thuộc.

## Phân cảnh 02 (14.5s)
Giờ đây hãy thử quay ngược dòng thời gian.
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
| SC01 | 12.0s | Hãy nghĩ về một buổi sáng. |
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
        # Should pick the 3-scene table over the 1-scene summary table
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
                [sys.executable, str(cli_script), tmp_path, "--json", "--strict"],
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
            # Should fail with non-zero exit code due to --strict on rate warning
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
            assert any("SCENE_TOO_LONG" in w for w in data["scenes"][0]["warnings"])
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
        assert len(violations) == 4

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
        assert len(namedrop_violations) >= 3

    def test_direct_concise_narration_passes_cleanly(self):
        from script_diversity_linter import check_formulaic_transitions

        scenes = [
            {"id": "SC01", "narration": "Mỗi lần trì hoãn, não bạn đang kích hoạt cơ chế sinh tồn."},
            {"id": "SC02", "narration": "Hạch hạnh nhân xem áp lực công việc như mối đe dọa trực tiếp."},
        ]
        violations = check_formulaic_transitions(scenes)
        self.assertEqual(len(violations), 0)
        assert len(violations) == 0


if __name__ == "__main__":
    unittest.main()
