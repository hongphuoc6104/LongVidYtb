"""Unit and regression tests for early visual prompt cliché gate (FLOW_CLICHE_FORBIDDEN).

Ensures visual prompt clichés are blocked early during content validation and scene authoring
rather than failing late at image generation.
"""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from content_contract import ContractError, validate_brief, validate_content
from flow_prompts import (
    BANNED_CLICHES,
    PromptError,
    check_visual_prompt_text,
    find_visual_cliche,
)
from pilot import ROOT, read
from scripts.story_plan import validate_plan


def _v3_fixture():
    b = read(ROOT / "examples/story-v3/brief.json")
    c = read(ROOT / "examples/story-v3/content.json")
    c["brief_hash"] = "TEST_HASH"
    return b, c


class TestFlowPromptsClicheHelper(unittest.TestCase):
    """Test helper functions exposed by flow_prompts / compiler."""

    def test_find_visual_cliche_detects_all_banned_cliches(self):
        samples = [
            ("Detailed brain cutaway showing hippocampus", "brain cutaway cliché"),
            ("A character using an abacus frame", "abacus cliché"),
            ("Turn the industrial pipe valve clockwise", "pipe valve cliché"),
            ("A heavy iron anchor dropped onto the deck", "iron anchor cliché"),
            ("Show a split-screen comparison between two worlds", "split screen cliché"),
            ("split screen with desk on left and lab on right", "split screen cliché"),
            ("dichotomy screen dividing past and future", "split screen cliché"),
            ("a splitscreen view of two workflows", "split screen cliché"),
            ("Bố cục màn hình chia đôi đối chiếu tài liệu", "split screen cliché"),
            ("Hình minh họa lát cắt não chi tiết", "brain cutaway cliché"),
            ("Khung cảnh có van ống nước công nghiệp", "pipe valve cliché"),
            ("Hình ảnh mỏ neo sắt trên boong tàu", "iron anchor cliché"),
            ("Nhân vật sử dụng chiếc bàn tính cổ", "abacus cliché"),
        ]
        for text, expected_name in samples:
            matched = find_visual_cliche(text)
            self.assertEqual(matched, expected_name, f"Failed to match {expected_name} in: {text}")

    def test_find_visual_cliche_returns_none_for_clean_text(self):
        clean_samples = [
            "A researcher examining a dataset on a laptop.",
            "Close-up of a fountain pen signing an academic journal acceptance letter.",
            "Two researchers discussing results in a well-lit library archive.",
            "",
            None,
        ]
        for text in clean_samples:
            self.assertIsNone(find_visual_cliche(text))

    def test_check_visual_prompt_text_raises_prompt_error(self):
        with self.assertRaises(PromptError) as ctx:
            check_visual_prompt_text("split screen comparison", field="description")
        self.assertIn("FLOW_CLICHE_FORBIDDEN", str(ctx.exception))
        self.assertIn("split screen cliché", str(ctx.exception))

    def test_check_visual_prompt_text_passes_clean_text(self):
        text = "A clean university library desk with notebooks and a laptop."
        result = check_visual_prompt_text(text, field="description")
        self.assertEqual(result, text)


class TestContentContractEarlyClicheGate(unittest.TestCase):
    """Test validate_content blocks visual clichés early across all visual fields."""

    def test_validate_content_blocks_split_screen_in_setting(self):
        b, c = _v3_fixture()
        c["scenes"][0]["setting"] = "Modern office with split screen partition"
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("setting", err_str.lower())

    def test_validate_content_blocks_cliche_in_image_description(self):
        b, c = _v3_fixture()
        c["scenes"][0]["images"][0]["description"] = "A split screen layout showing student on left and AI on right"
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("description", err_str.lower())

    def test_validate_content_blocks_cliche_in_image_preserve(self):
        b, c = _v3_fixture()
        c["scenes"][0]["images"][0]["preserve"] = "Keep split screen division from previous frame"
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("preserve", err_str.lower())

    def test_validate_content_blocks_cliche_in_image_change(self):
        b, c = _v3_fixture()
        c["scenes"][0]["images"][0]["change"] = "Add an iron anchor to the right side"
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("change", err_str.lower())

    def test_validate_content_blocks_cliche_in_visible_text(self):
        b, c = _v3_fixture()
        c["scenes"][0]["images"][0]["visible_text"] = [
            {"text": "split screen", "placement": "upper-right", "object": "banner"}
        ]
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("visible_text", err_str.lower())

    def test_validate_content_blocks_cliche_in_character_appearance(self):
        b, c = _v3_fixture()
        c["characters"][0]["appearance"] = "A stick figure with brain cutaway anatomy"
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("appearance", err_str.lower())

    def test_validate_content_blocks_cliche_in_character_outfit(self):
        b, c = _v3_fixture()
        c["characters"][0]["outfit"] = "Shirt decorated with an iron anchor emblem"
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("outfit", err_str.lower())

    def test_validate_content_blocks_cliche_in_style(self):
        b, c = _v3_fixture()
        c["style"] = "Editorial illustration featuring split screen comparison"
        b["style"] = c["style"]
        with self.assertRaises(ContractError) as ctx:
            validate_content(ROOT, b, 1, "TEST_HASH", c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("style", err_str.lower())

    def test_validate_brief_blocks_cliche_in_style(self):
        b, _ = _v3_fixture()
        b["style"] = "Editorial 2D scene with an abacus on the desk"
        with self.assertRaises(ContractError) as ctx:
            validate_brief(ROOT, b)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)
        self.assertIn("style", err_str.lower())

    def test_validate_plan_in_story_plan_blocks_cliches(self):
        b, c = _v3_fixture()
        c["scenes"][0]["images"][0]["description"] = "Brain cutaway showing thought processes"
        with self.assertRaises(ContractError) as ctx:
            validate_plan(b, c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)

    def test_validate_plan_blocks_cliche_in_character_and_style(self):
        b, c = _v3_fixture()
        c["characters"][0]["appearance"] = "A stick figure with brain cutaway"
        with self.assertRaises(ContractError) as ctx:
            validate_plan(b, c)
        err_str = str(ctx.exception)
        self.assertIn("FLOW_CLICHE_FORBIDDEN", err_str)



if __name__ == "__main__":
    unittest.main()


