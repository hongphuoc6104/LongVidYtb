#!/usr/bin/env python3
"""Unit tests for all architectural & human-naturalness pipeline upgrades."""
from __future__ import annotations

import math
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from PIL import Image, ImageDraw

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for p in (str(ROOT_DIR), str(SYS_DIR), str(SYS_DIR / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import adapters  # noqa: E402
import audio_processing  # noqa: E402
import remote_audio  # noqa: E402
from colab_bridge import job_protocol, protocol, worker  # noqa: E402
from content_contract import ContractError, validate_content  # noqa: E402
from flow_cdp.validate_asset import check_bottom_blank_gap, validate_asset  # noqa: E402
from research_story_architect import (  # noqa: E402
    build_brief_v3,
    build_content_v3,
    build_scenes_from_story_rows,
    compute_brief_hash,
    create_demo_trial_topic,
)
from script_diversity_linter import (  # noqa: E402
    check_historical_backtracking,
    check_sentence_rhythm_variance,
    compute_sentence_rhythm_metrics,
    lint_script,
)
from scripts.subtitles import resolve_anchor_timestamp, subtitle_cues  # noqa: E402
from vn_text_normalizer import (  # noqa: E402
    detect_unnormalized_tokens,
    enforce_tts_normalization_gate,
    normalize_for_tts,
    split_utterances_by_pause,
)


class TestHumanNaturalnessUpgrades(unittest.TestCase):
    """Comprehensive verification of pipeline tightness and human-grade synthesis upgrades."""

    def test_vn_text_normalizer_pause_splitting_and_foreign_gate(self):
        raw = "Năm 1963, giáo sư Jaak Panksepp phát hiện dopamine [pause:900ms] chỉ mất 1,5 giây!"
        norm = normalize_for_tts(raw)
        self.assertIn("một nghìn chín trăm sáu mươi ba", norm)
        self.assertIn("Giác Păng-xép", norm)
        self.assertIn("đô-pa-min", norm)
        self.assertIn("một phẩy năm", norm)
        self.assertEqual(detect_unnormalized_tokens(norm), [])

        parts = split_utterances_by_pause(raw, default_tail_pause=0.35)
        self.assertEqual(len(parts), 2)
        self.assertAlmostEqual(parts[0]["pause_after"], 0.90, places=2)
        self.assertAlmostEqual(parts[1]["pause_after"], 0.35, places=2)

        # Un-transliterated English token must trigger gate
        with self.assertRaisesRegex(ValueError, "UNNORMALIZED_FOREIGN_TOKEN"):
            enforce_tts_normalization_gate("Bộ não thực hiện quá trình neuroplasticity mạnh mẽ.")

    def test_primary_scene_request_and_worker_tts_normalization_pipeline(self):
        scene = {
            "id": "SC02",
            "tone": "reflective_slow",
            "narration": "Tám mươi phần trăm sinh viên mở Word gõ ngay. [pause:900ms] Nhưng bài báo Q1 của Feynman không bắt đầu ở đó.",
        }
        req = remote_audio.primary_scene_request(scene, scene["narration"], "vi", adapters.DEFAULT_PAUSE, 0, False)
        self.assertEqual(
            req["texts"],
            [
                "Tám mươi phần trăm sinh viên mở Word gõ ngay.",
                "Nhưng bài báo Q1 của Feynman không bắt đầu ở đó.",
            ],
        )
        self.assertEqual(req["gaps"], [0.9])
        self.assertEqual(req["tone"], "reflective_slow")

        # Worker-side synthesis normalizer converts loanwords and numbers without mutating segment text
        synth_text = worker._normalize_vi_tts_text("Năm 2026, 80% bài báo Q1 không dùng Word hay Feynman [pause:900ms] đâu.")
        self.assertNotIn("[pause", synth_text)
        self.assertIn("tám mươi phần trăm", synth_text)
        self.assertIn("quy một", synth_text)
        self.assertIn("Guốc", synth_text)
        self.assertIn("Phây-man", synth_text)

    def test_flash_agent_story_rows_builder_and_focus_clamping(self):
        rows = [
            (
                "Trang sách vàng",
                "A Vietnamese student desk at night with a yellow highlighter.",
                [
                    ("Trang sách vàng kín, đầu bạn vẫn trống.", "macro_prop|An open highlighted textbook."),
                    ("Bạn gạch thêm một dòng.", "full_scene|A student highlights one more line at the desk."),
                    ("Rồi gấp cuốn sách lại.", "variation|The same student closes the textbook."),
                ],
            )
        ]
        scenes = build_scenes_from_story_rows(rows)
        self.assertEqual(len(scenes), 1)
        self.assertEqual(len(scenes[0].visual_beats), 3)
        self.assertEqual(scenes[0].visual_beats[2].based_on, "SC01_I2")
        self.assertIn("Expression lock", scenes[0].visual_beats[2].preserve)

        # Out-of-bounds focus coordinates from Flash agent are clamped safely to central region
        scenes[0].visual_beats[0].focus_x = 0.05
        scenes[0].visual_beats[0].focus_y = 0.95
        topic = create_demo_trial_topic()
        topic.scenes[0] = scenes[0]
        topic.scenes[0].requirements = ["R01"]
        brief = build_brief_v3(topic)
        content = build_content_v3(topic, brief, compute_brief_hash(brief))
        beat_focus = content["scenes"][0]["beats"][0]["focus"]
        self.assertGreaterEqual(beat_focus["x"], 0.35)
        self.assertLessEqual(beat_focus["x"], 0.65)
        self.assertGreaterEqual(beat_focus["y"], 0.35)
        self.assertLessEqual(beat_focus["y"], 0.58)

    def test_script_diversity_linter_custom_chronology_and_rhythm_variance(self):
        robotic_scenes = [
            {"scene_id": f"SC0{i}", "chapter": 1, "narration": "Con người luôn tìm kiếm niềm vui mỗi ngày. Chúng ta thường quên đi mục tiêu dài hạn."}
            for i in range(1, 6)
        ]
        rhythm_violations = check_sentence_rhythm_variance(robotic_scenes, min_stddev_syllables=2.0)
        self.assertEqual(len(rhythm_violations), 1)
        self.assertEqual(rhythm_violations[0]["type"], "ROBOTIC_SENTENCE_CADENCE")

        natural_scenes = [
            {
                "scene_id": "SC01",
                "chapter": 1,
                "narration": "Dừng lại đi. Bạn đang tự bào mòn chính mình bằng những danh sách việc cần làm dài dằng dặc mỗi buổi sáng sớm.",
            },
            {
                "scene_id": "SC02",
                "chapter": 2,
                "narration": "Tại sao vậy? Khi hệ thần kinh phải xử lý hàng chục thông báo cùng lúc, vùng vỏ não trước trán nhanh chóng rơi vào trạng thái cạn kiệt năng lượng.",
            },
        ]
        metrics = compute_sentence_rhythm_metrics(natural_scenes)
        self.assertGreater(metrics["stddev_syllables"], 4.0)
        self.assertGreaterEqual(metrics["short_punchy_count"], 2)

        # Custom chronology rules override
        custom_rules = {1: ["tương lai xa", "năm 2099"]}
        bt_violations = check_historical_backtracking(
            [{"scene_id": "SC01", "chapter": 1, "narration": "Câu chuyện diễn ra vào năm 2099."}],
            custom_chronology_rules=custom_rules,
        )
        self.assertEqual(len(bt_violations), 1)
        self.assertEqual(bt_violations[0]["keyword"], "năm 2099")

        lint_res = lint_script(natural_scenes, custom_chronology_rules=custom_rules)
        self.assertEqual(lint_res["status"], "PASS")
        self.assertIn("rhythm_metrics", lint_res)

    def test_content_contract_enforces_tone_camera_intent_and_phonetic_gate(self):
        topic = create_demo_trial_topic()
        brief = build_brief_v3(topic)
        bhash = compute_brief_hash(brief)
        content = build_content_v3(topic, brief, bhash, brief_revision=1)

        # Valid human storytelling annotations pass cleanly
        content["scenes"][0]["tone"] = "narrative_warm"
        content["scenes"][0]["j_l_cut_offset"] = -0.18
        content["scenes"][0]["beats"][0]["camera_intent"] = "establish"
        validate_content(SYS_DIR, brief, 1, bhash, content)

        # Invalid tone is rejected
        bad_content = build_content_v3(topic, brief, bhash, brief_revision=1)
        bad_content["scenes"][0]["tone"] = "robotic_monotone"
        with self.assertRaises(ContractError):
            validate_content(SYS_DIR, brief, 1, bhash, bad_content)

    def test_protocol_tone_speed_modulation_and_acoustic_word_alignment(self):
        self.assertEqual(protocol.resolve_tone_speed(1.22, None), 1.22)
        self.assertAlmostEqual(protocol.resolve_tone_speed(1.22, "reflective_slow"), round(1.22 * 0.92, 3), places=3)
        self.assertAlmostEqual(protocol.resolve_tone_speed(1.22, "analytical_crisp"), round(1.22 * 1.02, 3), places=3)

        # Synthetic 2-second speech waveform at 48kHz
        import numpy as np
        sr = 48000
        t = np.linspace(0, 2.0, sr * 2, endpoint=False, dtype=np.float32)
        env = np.abs(np.sin(2 * math.pi * 2.5 * t)).astype(np.float32)
        w = (0.3 * np.sin(2 * math.pi * 180.0 * t) * env).astype(np.float32)
        text = "Con người tiền sử sống rất thảnh thơi."
        word_ts = worker._extract_word_timestamps_acoustic(w, text, sr=sr)
        self.assertEqual(len(word_ts), 8)
        self.assertGreaterEqual(word_ts[0]["start"], 0.0)
        self.assertLessEqual(word_ts[-1]["end"], 2.0)

        seg = {
            "scene_id": "SC01",
            "text": text,
            "start": 5.0,
            "content_end": 7.0,
            "end": 7.7,
            "word_timestamps": word_ts,
        }
        cues = subtitle_cues([seg], aspect_ratio="16:9")
        self.assertGreaterEqual(len(cues), 1)
        anchor_t = resolve_anchor_timestamp(seg, "thảnh thơi", occurrence=1)
        self.assertGreater(anchor_t, 5.5)
        self.assertLess(anchor_t, 7.0)

    def test_audio_processing_sidechain_ducking_and_micro_sfx(self):
        sr = 48000
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            narr_path = tmp_dir / "narration.wav"
            bgm_path = tmp_dir / "bgm.wav"
            out_path = tmp_dir / "mixed.wav"

            # 1.0s narration: first 0.5s voiced, second 0.5s pause
            voiced = [int(9000 * math.sin(2 * math.pi * 200 * i / sr)) for i in range(sr // 2)]
            silent = [0] * (sr // 2)
            narr_samples = voiced + silent
            with wave.open(str(narr_path), "wb") as wf:
                wf.setparams((1, 2, sr, len(narr_samples), "NONE", "not compressed"))
                wf.writeframes(struct.pack(f"<{len(narr_samples)}h", *narr_samples))

            # Constant amplitude BGM
            bgm_samples = [int(6000 * math.sin(2 * math.pi * 110 * i / sr)) for i in range(sr)]
            with wave.open(str(bgm_path), "wb") as bf:
                bf.setparams((1, 2, sr, len(bgm_samples), "NONE", "not compressed"))
                bf.writeframes(struct.pack(f"<{len(bgm_samples)}h", *bgm_samples))

            report = audio_processing.mix_sound_design(
                narr_path,
                out_path,
                cfg={"bgm_duck_gain": 0.06, "bgm_swell_gain": 0.25},
                bgm_wav=bgm_path,
                sfx_events=[{"kind": "pop", "at": 0.1, "duration": 0.15}, {"kind": "whoosh", "at": 0.55, "duration": 0.2}],
            )
            self.assertEqual(report["frames"], sr)
            self.assertEqual(audio_processing.frames_of(out_path), sr)
            self.assertEqual(report["sfx_events_applied"], 2)
            self.assertTrue(report["bgm_mixed"])

    def test_validate_asset_catches_unintended_bottom_blank_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            img_path = Path(tmp) / "scene_gap.png"
            im = Image.new("RGB", (1920, 1080), (180, 200, 220))
            draw = ImageDraw.Draw(im)
            # Make bottom 22% pure white
            draw.rectangle([0, int(1080 * 0.78), 1920, 1080], fill=(255, 255, 255))
            im.save(img_path, format="PNG")

            gap_res = check_bottom_blank_gap(im)
            self.assertTrue(gap_res["hasBottomBlankGap"])
            self.assertGreater(gap_res["bottomBlankRatio"], 0.95)

            with self.assertRaisesRegex(ValueError, "bottom blank margin"):
                validate_asset(img_path, "16:9", require_full_bleed=True)


if __name__ == "__main__":
    unittest.main()
