#!/usr/bin/env python3
"""Challenger test suite for Milestone M2: Hand-Drawn 2D Explainer Story Architect & Impostor Job Rewrite.

Empirical verification covering:
- Challenge Task 1: Action Progression (sequential variations share based_on, preserve locks room geometry, character action shifts).
- Challenge Task 2: Blackout Elimination (still_life=0, environment=0, 4 contextual characters, 76 non-empty descriptions).
- Challenge Task 3: 6 Exact Claims Preservation (exact substrings of respective scene narration and brief facts).
- Dynamic Semantic See-Say Engine (extraction, dynamic synthesis, alignment validation).
- Anti-laziness deterministic rejection and regex precision (no false positives on "hand-drawn").
- Full backward compatibility for legacy 3-tuple callers.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from content_contract import validate_brief, validate_content
from tools.build_impostor_paradox_job import build_topic, count_total_beats
from tools.research_story_architect import (
    _HUMAN_ACTOR_KEYWORDS_RE,
    ResearchedBeat,
    build_scenes_from_story_rows,
    derive_see_say_visual_action,
    extract_sentence_semantic_elements,
    validate_see_say_alignment,
)


class TestM2SemanticStoryArchitect(unittest.TestCase):
    """Test F7, F8, F9 features in research_story_architect.py."""

    def test_semantic_element_extraction_general_dynamic_reasoning(self):
        """Extract verbs, nouns, and metrics without hardcoded domain knowledge."""
        s1 = "Bảy mươi phần trăm sinh viên giỏi tin rằng thành công của họ chỉ là do may mắn ngẫu nhiên."
        elem1 = extract_sentence_semantic_elements(s1)
        self.assertTrue(any("bảy mươi" in m.lower() or "70" in m for m in elem1["metrics"]))
        self.assertTrue(len(elem1["nouns"]) > 0)

        s2 = "Bản nháp thô năm trăm từ đánh bại một nghìn giờ đọc thêm trong tuyệt vọng."
        elem2 = extract_sentence_semantic_elements(s2)
        self.assertTrue(any("năm trăm" in m.lower() or "500" in m for m in elem2["metrics"]))
        self.assertTrue(any("một nghìn" in m.lower() or "1000" in m for m in elem2["metrics"]))
        self.assertTrue(len(elem2["contrasts"]) > 0)

    def test_derive_see_say_visual_action_for_diagram_and_metaphor(self):
        """Derive active hand-drawn visual descriptions for sentences lacking explicit visual specs."""
        s = "Bảy mươi phần trăm sinh viên giỏi thừa nhận họ nghĩ mình chỉ gặp may."
        action = derive_see_say_visual_action(s, shot_type="visual_diagram", setting="Clean white background")
        self.assertTrue(
            "70%" in action
            or "Bảy mươi phần trăm" in action
            or "diagram" in action.lower()
            or "infographic" in action.lower()
        )

        action_meta = derive_see_say_visual_action(
            s, shot_type="concept_metaphor", setting="Dark workspace", character_id="CH01"
        )
        self.assertTrue(len(action_meta) > 10)

    def test_see_say_alignment_validation(self):
        """Confirm alignment validator verifies entities and detects severe disconnects."""
        sentence = "Bản nháp thô 500 từ đánh bại một nghìn giờ đọc thêm."
        good_visual = "Hand-drawn comparison: rough draft 500 words paper weighing more than 1000 hours book stack."
        self.assertTrue(validate_see_say_alignment(sentence, good_visual))

        # Adversarial disconnected visual must return False
        disconnected_sentence = "Bảy mươi phần trăm sinh viên lo sợ"
        disconnected_visual = "A purple elephant dancing on Mars."
        self.assertFalse(validate_see_say_alignment(disconnected_sentence, disconnected_visual))

    def test_semantic_element_extraction_cross_domain(self):
        """Verify dynamic semantic extraction across Biology, Economics, History, and Physics without hardcoded topic templates."""
        bio = extract_sentence_semantic_elements("Tế bào hồng cầu vận chuyển oxy qua các mao mạch đến từng mô cơ quan.")
        self.assertTrue(len(bio["nouns"]) > 0, f"Expected nouns in Biology: {bio}")

        econ = extract_sentence_semantic_elements("Lạm phát phi mã khiến sức mua của đồng tiền sụt giảm nghiêm trọng trên thị trường.")
        self.assertTrue(len(econ["nouns"]) > 0, f"Expected nouns in Economics: {econ}")

        hist = extract_sentence_semantic_elements("Đoàn thuyền chiến của quân Tây Sơn tiến thẳng vào cửa sông Gianh trong đêm bão.")
        self.assertTrue(len(hist["nouns"]) > 0, f"Expected nouns in History: {hist}")

        phys = extract_sentence_semantic_elements("Các hạt electron dịch chuyển tạo thành dòng điện trong dây dẫn kim loại.")
        self.assertTrue(len(phys["nouns"]) > 0, f"Expected nouns in Physics: {phys}")

    def test_contextual_character_parsing_and_resolution(self):
        """Test shot_type:char_spec parsing with multi-character and character-free markers."""
        rows = [
            ("Hai nhà tâm lý học phỏng vấn sinh viên.", "full_scene:CH01,CH02|Two psychologists interview a high-achieving student."),
            ("Biểu đồ chẩn đoán nhịp tim.", "concept_metaphor:none|Diagnostic chart showing heart rate lines."),
            ("Sinh viên giải thích thành tích.", "variation:CH01|The student gestures toward academic records."),
            ("Bục vinh danh một trăm năm mươi người.", "visual_diagram:free|Podium with 150 gold medals."),
        ]
        story_rows = [("Cuộc phỏng vấn", "An academic consultation office.", rows)]
        scenes = build_scenes_from_story_rows(story_rows, character_id="CH01")
        self.assertEqual(len(scenes), 1)
        sc = scenes[0]
        self.assertEqual(sc.visual_beats[0].character_ids, ["CH01", "CH02"])
        self.assertEqual(sc.visual_beats[1].character_ids, [])
        self.assertEqual(sc.visual_beats[2].character_ids, ["CH01"])
        self.assertEqual(sc.visual_beats[3].character_ids, [])
        self.assertIn("CH01", sc.character_ids)
        self.assertIn("CH02", sc.character_ids)

    def test_action_progression_variation_continuity_and_expression_shift(self):
        """Test continuous action progression: full_scene -> variation -> variation."""
        rows = [
            ("Sinh viên ngồi trước laptop.", "full_scene:CH01|Researcher sits calmly at desk."),
            ("Mở tài liệu đọc.", "variation:CH01|The researcher smiles and turns page."),
            ("Bắt đầu gõ phím.", "variation:CH01|The researcher grins with joy while typing rapidly."),
        ]
        story_rows = [("Hành động", "A quiet workspace.", rows)]
        scenes = build_scenes_from_story_rows(story_rows, character_id="CH01")
        beats = scenes[0].visual_beats
        self.assertIsNone(beats[0].based_on)
        self.assertEqual(beats[1].based_on, "SC01_I1")
        self.assertEqual(beats[2].based_on, "SC01_I1")
        self.assertTrue(beats[1].allow_expression_shift)
        self.assertTrue(beats[2].allow_expression_shift)

    def test_consecutive_variations_action_progression(self):
        """Test triple consecutive variations maintain base beat reference and room geometry lock."""
        rows = [
            ("Câu 1.", "full_scene:CH01|Researcher stands before academic audience."),
            ("Câu 2.", "variation:CH01|Researcher smiles with relief."),
            ("Câu 3.", "variation:CH01|Researcher opens notebook and points to diagram."),
            ("Câu 4.", "variation:CH01|Researcher turns to committee with confident expression shift."),
        ]
        story = [("Tiêu đề", "An academic auditorium.", rows)]
        scenes = build_scenes_from_story_rows(story, character_id="CH01")
        sc = scenes[0]
        self.assertEqual(len(sc.visual_beats), 4)
        base_id = sc.visual_beats[0].image_id
        for i in range(1, 4):
            beat = sc.visual_beats[i]
            self.assertEqual(beat.shot_type, "variation")
            self.assertEqual(beat.based_on, base_id)
            self.assertIn("Keep the exact camera angle, room geometry and props", beat.preserve)
            self.assertTrue(len(beat.change.strip()) > 0)

    def test_human_actor_regex_avoids_false_positives_on_hand_drawn(self):
        """Verify _HUMAN_ACTOR_KEYWORDS_RE does not match 'hand-drawn' while matching actual actors."""
        non_actors = [
            "Hand-drawn column chart on clean white background",
            "Hand-drawn concept metaphor with pure white canvas",
            "hand-drawn sketch of balance scale",
        ]
        for text in non_actors:
            self.assertIsNone(
                _HUMAN_ACTOR_KEYWORDS_RE.search(text),
                f"Falsely matched non-actor text: {text}",
            )

        actors = [
            "Hand hovers above keyboard keys",
            "Researcher sits at desk",
            "Cartoon four-finger hand hammering keys",
            "Student staring at blank paper",
            "Psychologists interview candidate",
        ]
        for text in actors:
            self.assertIsNotNone(
                _HUMAN_ACTOR_KEYWORDS_RE.search(text),
                f"Failed to match genuine actor text: {text}",
            )

    def test_anti_laziness_guardrails_empirical_rejection(self):
        """Verify ResearchedBeat deterministically rejects banned laziness patterns."""
        banned_phrases = [
            "sits and thinks",
            "sitting quietly",
            "staring at laptop",
            "pondering",
            "coffee mug on desk",
            "books resting on table",
            "desk lamp glowing",
            "empty room",
            "A conceptual metaphor of",
            "An abstract illustration of",
        ]
        for phrase in banned_phrases:
            with self.assertRaises(ValueError) as ctx:
                ResearchedBeat(
                    image_id="SC01_I1",
                    description=f"A room. {phrase}",
                    anchor_quote="test",
                    anchor_occurrence=1,
                    reason="test",
                    character_ids=["CH01"],
                    effect="cut",
                    shot_type="full_scene",
                )
            self.assertIn("LAZY_VISUAL_ACTION_FORBIDDEN", str(ctx.exception))

    def test_variation_beat_requires_based_on_and_preserve(self):
        """Verify variation beats require non-empty based_on, preserve, and change."""
        with self.assertRaises(ValueError):
            ResearchedBeat(
                image_id="SC01_I2",
                description="A room. Character moves.",
                anchor_quote="test",
                anchor_occurrence=1,
                reason="test",
                character_ids=["CH01"],
                effect="cut",
                shot_type="variation",
                based_on=None,
                preserve="Keep camera",
                change="Character moves",
            )
        with self.assertRaises(ValueError):
            ResearchedBeat(
                image_id="SC01_I2",
                description="A room. Character moves.",
                anchor_quote="test",
                anchor_occurrence=1,
                reason="test",
                character_ids=["CH01"],
                effect="cut",
                shot_type="variation",
                based_on="SC01_I1",
                preserve="",
                change="Character moves",
            )

    def test_backward_compatibility_with_legacy_3tuple_callers(self):
        """Existing 3-tuple callers (title, setting, rows) without :char syntax must work cleanly."""
        legacy_rows = [
            ("Câu đầu tiên mở màn.", "full_scene|A student at desk."),
            ("Câu thứ hai tiếp diễn.", "variation|Student turns head."),
            ("Câu thứ ba kết thúc.", "still_life|An open book on table."),
        ]
        legacy_story = [("Tiêu đề", "A simple room.", legacy_rows)]
        scenes = build_scenes_from_story_rows(legacy_story, character_id="CH01")
        self.assertEqual(len(scenes), 1)
        self.assertEqual(scenes[0].visual_beats[0].character_ids, ["CH01"])
        self.assertEqual(scenes[0].visual_beats[1].character_ids, ["CH01"])
        self.assertEqual(scenes[0].visual_beats[2].character_ids, [])


class TestM2ImpostorParadoxProductionRewrite(unittest.TestCase):
    """Test F10 & F11: Impostor Paradox Job Rewrite & Blueprint Recompilation."""

    @classmethod
    def setUpClass(cls):
        cls.blueprint_dir = SYS_DIR / "blueprints" / "impostor-paradox-9x16"
        cls.brief = json.loads((cls.blueprint_dir / "brief.json").read_text(encoding="utf-8"))
        cls.content = json.loads((cls.blueprint_dir / "content.json").read_text(encoding="utf-8"))
        cls.topic = build_topic()

    def test_four_contextual_characters_declared(self):
        """Job declares CH01, CH02, CH03, CH04 contextual roles."""
        char_ids = [c["id"] for c in self.content["characters"]]
        self.assertEqual(char_ids, ["CH01", "CH02", "CH03", "CH04"])

    def test_zero_blackout_scenes_and_forbidden_cliches(self):
        """All 5 blackout scenes (SC02, SC04, SC09, SC14, SC18) eliminated with zero still_life/environment."""
        for sc in self.content["scenes"]:
            for im in sc["images"]:
                self.assertNotIn(
                    im.get("shot_type"),
                    ("still_life", "environment"),
                    f"Forbidden passive shot in {im['id']}",
                )
                desc = im.get("description", "").lower()
                for banned in ("coffee mug", "seagull", "sea foam", "sunset ocean", "vintage clock"):
                    self.assertNotIn(banned, desc, f"Banned cliché {banned} found in {im['id']}")

    def test_blackout_elimination_and_all_76_beats_non_empty(self):
        """Verify empirical criteria: still_life=0, environment=0, 4 chars, 76 non-empty descriptions."""
        still_lifes = sum(
            1 for sc in self.content["scenes"] for im in sc["images"] if im.get("shot_type") == "still_life"
        )
        environments = sum(
            1 for sc in self.content["scenes"] for im in sc["images"] if im.get("shot_type") == "environment"
        )
        self.assertEqual(still_lifes, 0, f"Found {still_lifes} still_life shots!")
        self.assertEqual(environments, 0, f"Found {environments} environment shots!")

        char_ids = [c["id"] for c in self.content.get("characters", [])]
        self.assertEqual(char_ids, ["CH01", "CH02", "CH03", "CH04"])

        total_images = 0
        for sc in self.content["scenes"]:
            for im in sc["images"]:
                total_images += 1
                desc = im.get("description", "")
                self.assertTrue(len(desc.strip()) > 0, f"Empty description in {im['id']}")
        self.assertEqual(total_images, 76, f"Expected exactly 76 visual beats, found {total_images}")

        # Verify all 76 beats have non-empty anchor quotes matching scene narration
        total_beats = 0
        for sc in self.content["scenes"]:
            narration = sc["narration"]
            for b in sc.get("beats", []):
                total_beats += 1
                quote = b.get("anchor", {}).get("vi", {}).get("quote", "")
                self.assertTrue(len(quote.strip()) > 0, f"Empty quote in beat {b.get('id')}")
                self.assertIn(
                    quote,
                    narration,
                    f"Beat quote {quote!r} not in {sc['id']} narration: {narration!r}",
                )
        self.assertEqual(total_beats, 76, f"Expected 76 beat anchors, found {total_beats}")

    def test_action_progression_in_blueprint_content(self):
        """Verify that sequential variations in content.json share based_on and preserve room geometry."""
        variation_count = 0
        for sc in self.content["scenes"]:
            scene_images = sc["images"]
            scene_img_ids = [im["id"] for im in scene_images]
            for im in scene_images:
                if im.get("shot_type") == "variation":
                    variation_count += 1
                    based_on = im.get("based_on")
                    self.assertIsNotNone(based_on, f"Variation {im['id']} missing based_on")
                    self.assertIn(based_on, scene_img_ids, f"Variation {im['id']} based_on {based_on} not in scene {sc['id']}")
                    self.assertLess(
                        scene_img_ids.index(based_on),
                        scene_img_ids.index(im["id"]),
                        f"Variation {im['id']} based_on {based_on} must precede variation beat",
                    )
                    preserve = im.get("preserve", "")
                    self.assertIn(
                        "Keep the exact camera angle, room geometry and props",
                        preserve,
                        f"Variation {im['id']} missing room geometry lock in preserve",
                    )
                    # Description must differ from the base beat description (action shift)
                    base_im = next(x for x in scene_images if x["id"] == based_on)
                    self.assertNotEqual(
                        im.get("description"),
                        base_im.get("description"),
                        f"Variation {im['id']} description identical to base {base_im['id']}",
                    )
        self.assertGreaterEqual(variation_count, 11, f"Expected at least 11 variation shots, found {variation_count}")

    def test_six_academic_claims_exact_substring_preservation(self):
        """All 6 academic claims preserved byte-for-byte in narration."""
        scenes_map = {sc["id"]: sc for sc in self.content["scenes"]}
        claims = [
            ("SC07", "Năm một nghìn chín trăm bảy mươi tám, hai nhà tâm lý học thực hiện cuộc khảo sát."),
            ("SC08", "Bảy mươi phần trăm trong số họ thú nhận, họ luôn nghĩ mình chỉ gặp may mắn."),
            ("SC10", "Não người giỏi đối xử với lời khen, như một tín hiệu cảnh báo nguy hiểm."),
            ("SC11", "Người thật sự thiếu năng lực lại tự tin nhất."),
            ("SC14", "Bạn nhìn thấy hàng nghìn khoảng trống mới."),
            ("SC16", "Bản nháp thô năm trăm từ, đánh bại một nghìn giờ đọc thêm."),
        ]
        for sc_id, claim in claims:
            self.assertIn(sc_id, scenes_map)
            narration = scenes_map[sc_id]["narration"]
            self.assertIn(claim, narration, f"Claim not found in {sc_id} narration: {claim}")

    def test_six_exact_claims_in_content_claims_list(self):
        """Verify content['claims'] has exactly 6 entries matching expected quotes and sources."""
        claims_list = self.content.get("claims", [])
        self.assertEqual(len(claims_list), 6, f"Expected 6 claims in content.json, found {len(claims_list)}")
        expected_claims = {
            "Năm một nghìn chín trăm bảy mươi tám, hai nhà tâm lý học thực hiện cuộc khảo sát.": "SRC01",
            "Bảy mươi phần trăm trong số họ thú nhận, họ luôn nghĩ mình chỉ gặp may mắn.": "SRC01",
            "Não người giỏi đối xử với lời khen, như một tín hiệu cảnh báo nguy hiểm.": "SRC02",
            "Người thật sự thiếu năng lực lại tự tin nhất.": "SRC03",
            "Bạn nhìn thấy hàng nghìn khoảng trống mới.": "SRC03",
            "Bản nháp thô năm trăm từ, đánh bại một nghìn giờ đọc thêm.": "SRC04",
        }
        for item in claims_list:
            quote = item.get("quote")
            self.assertIn(quote, expected_claims, f"Unexpected claim quote: {quote}")
            self.assertEqual(item.get("source_id"), expected_claims[quote])

    def test_total_beats_and_scene_count(self):
        """Total 76 visual beats across 19 scenes."""
        self.assertEqual(len(self.topic.scenes), 19)
        self.assertEqual(count_total_beats(self.topic.scenes), 76)
        self.assertEqual(len(self.content["scenes"]), 19)
        total_images = sum(len(sc["images"]) for sc in self.content["scenes"])
        self.assertEqual(total_images, 76)

    def test_contract_validation_passes_cleanly(self):
        """Full schema 3.0 and content contract validation passes with zero errors."""
        validate_brief(SYS_DIR, self.brief)
        validate_content(SYS_DIR, self.brief, 1, self.content["brief_hash"], self.content)


if __name__ == "__main__":
    unittest.main()
