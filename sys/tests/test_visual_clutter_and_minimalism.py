"""Tests for visual minimalism directives, clutter-free prompts, and visual clutter gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
import pytest
from channels.registry import channels, get_channel
from PIL import Image
from tools.channel_production_common import (
    BANNED_CLUTTER_WORDS,
    BANNED_TEXTURE_WORDS,
    CLEAN_COMPOSITION_DIRECTIVE,
    CLEAN_COMPOSITION_DIRECTIVE_VI,
    CLEAN_NEGATIVE_DIRECTIVE,
    CLEAN_STYLE_REPLACEMENT,
    compile_channel_scene_prompt,
    compile_channel_thumb_prompt,
    sanitize_banned_texture_styles,
)
from tools.visual_clutter_gate import (
    evaluate_image,
    scan_run_directory,
    score_negative_space,
)

EXPECTED_TEXTURE_WORDS: List[str] = [
    "woodcut",
    "scratchboard",
    "stipple",
    "hedcut",
    "halftone",
    "etching",
    "engraving",
    "intaglio",
    "linocut",
    "charcoal",
    "copperplate",
    "risograph",
    "lithograph",
    "gouge lines",
]

ENGLISH_CHANNEL_IDS: List[str] = [
    "en_lazy_brain",
    "en_crowd_strings",
    "en_kindred_sketch",
    "en_first_principles",
    "en_wallet_anatomy",
    "en_macro_gears",
    "en_plain_sight_ai",
    "en_career_leverage",
    "en_fine_print",
    "en_inside_vessel",
    "en_kitchen_molecules",
    "en_wait_how",
    "en_cold_case_ink",
    "en_choke_point",
    "en_pocket_cosmos",
    "en_second_arrow",
    "en_parable_lamp",
    "en_bamboo_marble",
]


class TestVisualRegistryMinimalism:
    """Verify registry English channels adhere to clean minimalist 3-tone standard."""

    def test_eighteen_english_channels_exist(self) -> None:
        all_ch = channels()
        en_found = [cid for cid, ch in all_ch.items() if getattr(ch, "language", "vi") == "en"]
        assert len(en_found) == 18
        assert sorted(en_found) == sorted(ENGLISH_CHANNEL_IDS)

    @pytest.mark.parametrize("channel_id", ENGLISH_CHANNEL_IDS)
    def test_english_channel_visual_has_no_banned_words(self, channel_id: str) -> None:
        ch = get_channel(channel_id)
        vis = ch.visual

        for field_name in ("style_description", "thumbnail_rule", "label", "cast_appearance", "outfit"):
            text = (getattr(vis, field_name, "") or "").lower()
            for banned in BANNED_CLUTTER_WORDS:
                assert banned not in text, (
                    f"Banned buzzword '{banned}' detected in {channel_id}.visual.{field_name}: {text}"
                )

    @pytest.mark.parametrize("channel_id", ENGLISH_CHANNEL_IDS)
    def test_english_channel_has_distinct_3_tone_palette(self, channel_id: str) -> None:
        ch = get_channel(channel_id)
        palette = ch.visual.palette
        assert len(palette) == 3, f"Channel {channel_id} palette must have exactly 3 hex codes, got {len(palette)}"
        for color in palette:
            assert color.startswith("#") and len(color) == 7, f"Invalid hex code '{color}' in {channel_id}"

    def test_all_18_english_palettes_are_distinct(self) -> None:
        palettes = [get_channel(cid).visual.palette for cid in ENGLISH_CHANNEL_IDS]
        assert len(set(palettes)) == 18, "Each English channel must maintain a distinct 3-tone palette"


class TestCompiledPromptsMinimalism:
    """Verify compiled scene and thumbnail prompts include directives and no clutter buzzwords."""

    @pytest.mark.parametrize("channel_id", ENGLISH_CHANNEL_IDS)
    def test_compiled_scene_prompt_contains_directives_and_no_banned_words(self, channel_id: str) -> None:
        ch = get_channel(channel_id)
        brief = {"style": ch.visual.style_description}
        content = {"characters": [{"id": "CH01", "name": "Hero", "appearance": "hero", "outfit": "clean"}]}
        sc = {"id": "SC01", "character_ids": ["CH01"]}
        img = {
            "id": "SC01_I1",
            "description": "A single minimal pivot point balancing a glowing orb",
            "has_character": False,
        }

        prompt = compile_channel_scene_prompt(ch, brief, content, sc, img, aspect_ratio="9:16")

        assert CLEAN_COMPOSITION_DIRECTIVE in prompt
        assert CLEAN_NEGATIVE_DIRECTIVE in prompt

        # Outside the negative directive itself, the prompt must contain zero banned words
        prompt_positive = prompt.replace(CLEAN_NEGATIVE_DIRECTIVE, "").lower()
        for banned in BANNED_CLUTTER_WORDS:
            assert banned not in prompt_positive, f"Banned word '{banned}' found in compiled prompt for {channel_id}"

    @pytest.mark.parametrize("channel_id", ENGLISH_CHANNEL_IDS)
    def test_compiled_thumb_prompt_contains_directives_and_no_banned_words(self, channel_id: str) -> None:
        ch = get_channel(channel_id)
        brief = {"style": ch.visual.style_description}
        thumb_scene = "A single minimal geometric pivot balancing a glowing gold sphere"
        thumb_text = "WHY IT BREAKS"

        prompt = compile_channel_thumb_prompt(ch, brief, thumb_scene, thumb_text, aspect_ratio="9:16")

        assert CLEAN_COMPOSITION_DIRECTIVE in prompt
        assert CLEAN_NEGATIVE_DIRECTIVE in prompt

        prompt_positive = prompt.replace(CLEAN_NEGATIVE_DIRECTIVE, "").lower()
        for banned in BANNED_CLUTTER_WORDS:
            assert banned not in prompt_positive, f"Banned word '{banned}' found in thumb prompt for {channel_id}"

    def test_fourteen_banned_texture_words_registered(self) -> None:
        for word in EXPECTED_TEXTURE_WORDS:
            assert word in BANNED_TEXTURE_WORDS, f"Missing banned texture word: {word}"
            assert word in BANNED_CLUTTER_WORDS, f"BANNED_CLUTTER_WORDS missing: {word}"

    @pytest.mark.parametrize("banned_term", EXPECTED_TEXTURE_WORDS)
    def test_compiler_replaces_banned_texture_styles_with_clean_vector(self, banned_term: str) -> None:
        ch = get_channel("en_first_principles")
        brief = {"style": f"An authentic tactile {banned_term} print on archival rag paper"}
        content = {"characters": []}
        sc = {"id": "SC01"}
        img = {
            "id": "SC01_I1",
            "description": f"A single metallic fulcrum with {banned_term} shading details",
            "has_character": False,
        }

        scene_prompt = compile_channel_scene_prompt(ch, brief, content, sc, img, aspect_ratio="9:16")
        thumb_prompt = compile_channel_thumb_prompt(
            ch, brief, f"A hero pivot with {banned_term} lines", "CORE LOGIC", aspect_ratio="9:16"
        )

        assert CLEAN_STYLE_REPLACEMENT in scene_prompt
        assert CLEAN_STYLE_REPLACEMENT in thumb_prompt

        scene_positive = scene_prompt.replace(CLEAN_NEGATIVE_DIRECTIVE, "").lower()
        thumb_positive = thumb_prompt.replace(CLEAN_NEGATIVE_DIRECTIVE, "").lower()

        assert banned_term not in scene_positive
        assert banned_term not in thumb_positive

    def test_sanitize_banned_texture_styles_direct(self) -> None:
        raw_text = "Hand-carved woodcut and scratchboard with stipple, hedcut engraving and gouge lines"
        cleaned = sanitize_banned_texture_styles(raw_text)
        for term in EXPECTED_TEXTURE_WORDS:
            assert term not in cleaned.lower()
        assert CLEAN_STYLE_REPLACEMENT in cleaned

    def test_vietnamese_channel_gets_vi_composition_directive_and_negative_directive(self) -> None:
        ch = get_channel("nao_luoi")
        brief = {"style": ch.visual.style_description}
        content = {"characters": []}
        sc = {"id": "SC01"}
        img = {"id": "SC01_I1", "description": "Người que nhìn đồng hồ", "has_character": True}

        prompt = compile_channel_scene_prompt(ch, brief, content, sc, img, aspect_ratio="9:16")

        assert CLEAN_COMPOSITION_DIRECTIVE_VI in prompt
        assert CLEAN_NEGATIVE_DIRECTIVE in prompt
        assert "Nguệch Ngoạc" in prompt or "7-color" in prompt or "stickman" in prompt


class TestVisualClutterGate:
    """Verify visual clutter gate distinguishes clean minimalist images from cluttered noisy images."""

    def test_gate_passes_flat_minimalist_image(self, tmp_path: Path) -> None:
        # Create a synthetic image with 85% solid background and 15% clean subject
        w, h = 1080, 1920
        arr = np.full((h, w), 245, dtype=np.uint8)
        # Small centered dark rectangle (approx 15% of total tiles)
        arr[800:1120, 400:680] = 30
        img = Image.fromarray(arr)
        img_path = tmp_path / "clean_minimal.jpg"
        img.save(img_path)

        score = score_negative_space(img_path)
        passed, eval_score = evaluate_image(img_path, threshold=0.60)

        assert score >= 0.80, f"Expected high negative space score, got {score}"
        assert passed is True
        assert eval_score == score

    def test_gate_fails_noisy_cluttered_image(self, tmp_path: Path) -> None:
        # Create a noisy image filled with high-frequency noise and dense grid lines
        w, h = 1080, 1920
        np.random.seed(42)
        arr = np.random.randint(50, 200, size=(h, w), dtype=np.uint8)
        # Add dense grid lines every 16 pixels
        arr[::16, :] = 0
        arr[:, ::16] = 255
        img = Image.fromarray(arr)
        img_path = tmp_path / "noisy_clutter.jpg"
        img.save(img_path)

        score = score_negative_space(img_path)
        passed, eval_score = evaluate_image(img_path, threshold=0.60)

        assert score <= 0.15, f"Expected low negative space score for noisy image, got {score}"
        assert passed is False
        assert eval_score == score

    def test_scan_run_directory_writes_clutter_report(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "test_run"
        img_dir = run_dir / "revisions" / "images" / "1"
        img_dir.mkdir(parents=True)

        # 1 clean image
        clean_arr = np.full((512, 512), 240, dtype=np.uint8)
        Image.fromarray(clean_arr).save(img_dir / "SC01_I1.jpg")

        # 1 noisy image
        np.random.seed(123)
        noisy_arr = np.random.randint(0, 255, size=(512, 512), dtype=np.uint8)
        Image.fromarray(noisy_arr).save(img_dir / "SC01_I2.jpg")

        report = scan_run_directory(run_dir, threshold=0.60)
        assert report["passed"] is False

        report_file = run_dir / "clutter_report.json"
        assert report_file.exists()

        saved_data = json.loads(report_file.read_text(encoding="utf-8"))
        assert saved_data["total_images"] == 2
        assert saved_data["passing_count"] == 1
        assert saved_data["failing_count"] == 1
        assert saved_data["passed"] is False
        assert len(saved_data["failing_images"]) == 1
        assert saved_data["failing_images"][0]["filename"] == "SC01_I2.jpg"


class TestCompetitorDialogueFormulaAndV2Pilots:
    """Verify all 18 English channels have competitor dialogue formulas, pause cadences, and V2 pilot reports."""

    REBUILT_EN_SLUGS: List[str] = [
        "en-first-principles",
        "en-scale-and-bone",
        "en-pocket-cosmos",
        "en-deep-time-strata",
        "en-inside-vessel",
        "en-macro-gears",
        "en-fine-print",
        "en-crowd-strings",
        "en-cold-case-ink",
        "en-choke-point",
        "en-root-and-canopy",
        "en-spawn-to-apex",
        "en-second-arrow",
        "en-bamboo-marble",
        "en-kindred-sketch",
        "en-lazy-brain",
        "en-career-leverage",
        "en-wallet-anatomy",
    ]

    @pytest.mark.parametrize("slug", REBUILT_EN_SLUGS)
    def test_rebuilt_spec_has_competitor_dialogue_formula_and_cadence(self, slug: str) -> None:
        spec_path = (
            Path(__file__).resolve().parents[1]
            / "channels"
            / "en_rebuilt_style_specs"
            / slug
            / f"{slug}_rebuilt_spec.json"
        )
        assert spec_path.exists(), f"Missing rebuilt spec for {slug}"
        data = json.loads(spec_path.read_text(encoding="utf-8"))

        formula = data.get("competitor_dialogue_formula", {})
        assert formula.get("competitor_verbatim_transcript_20s"), f"{slug} missing verbatim transcript"
        assert formula.get("sentence_structure_formula_vi"), f"{slug} missing sentence structure formula"
        assert formula.get("pause_and_cadence_formula_vi"), f"{slug} missing pause cadence formula"
        assert formula.get("transition_and_camera_formula_vi"), f"{slug} missing transition formula"

        beats = data.get("beats", [])
        assert len(beats) == 8, f"{slug} must have 8 beats"
        for b in beats:
            assert b.get("formula_stage"), f"{slug} {b.get('beat_id')} missing formula_stage"
            assert 0.10 <= float(b.get("pause_after_sec", 0)) <= 0.65, f"{slug} invalid pause_after_sec"
            assert b.get("camera_motion"), f"{slug} {b.get('beat_id')} missing camera_motion"
            assert b.get("transition"), f"{slug} {b.get('beat_id')} missing transition"

        report_path = spec_path.parent / "pilot_build_report.json"
        assert report_path.exists(), f"Missing pilot_build_report.json for {slug}"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert "VN_KINETIC_1WORD_RED_YELLOW_ASS" in report.get("subtitle_style_9x16", "")
        assert report.get("transition_engine") == "2x_supersampled_zoompan_plus_xfade"
        assert 15.0 <= float(report.get("duration_sec", 0)) <= 27.0
