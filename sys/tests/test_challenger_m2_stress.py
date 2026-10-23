"""Empirical Challenger M2.2 Stress Test Suite.

Comprehensive adversarial stress harness for Milestone M2:
1. Matrix stress test of prompt compilation across all models, all 10 shot types, and purposes in 1.7.0.
2. Verification of negative clearance directives against YouTube subtitle boxes, letterbox bars, and player controls.
3. Strict verification of label height (< 5%), uppercase constraints, word count (<= 6), character length (<= 45).
4. Adversarial stress test of FLOW_LAZINESS_VIOLATION and FLOW_CONCEPT_OBJECT_MISMATCH gates.
5. Verification of 0 active worker PGIDs in ProcessGroupManager registry and 0 lingering Chrome worker processes.
"""
import copy
import json
import os
import re
from pathlib import Path
import pytest

from flow_prompts import compile_prompt, PromptError, registry
from explainer_contract import validate_clearance_and_labels
from flow_cdp.process_manager import (
    DEFAULT_REGISTRY_FILE,
    ProcessGroupManager,
    clean_singleton_locks,
    is_pid_alive,
    is_port_listening,
)

MODELS_170 = ["NanoBananaPro", "NanoBanana2", "NanoBanana2Lite"]
MODEL_LABELS_170 = ["Nano Banana Pro", "Nano Banana 2", "Nano Banana 2 Lite"]

SHOT_TYPES_170 = [
    "full_scene",
    "variation",
    "macro_prop",
    "white_card",
    "white_isolated",
    "concept_metaphor",
    "visual_diagram",
    "cutaway_detail",
    "still_life",
    "environment",
]

BASE_REF = {
    "media_id": "00000000-0000-0000-0000-000000000001",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}


# ==============================================================================
# 1. PROMPT COMPILATION MATRIX STRESS TESTS
# ==============================================================================

class TestPromptCompilationMatrix170:
    """Stress test prompt compilation across models, shot types, purposes, and entity policies."""

    @pytest.mark.parametrize("model", MODELS_170 + MODEL_LABELS_170)
    @pytest.mark.parametrize("shot_type", [s for s in SHOT_TYPES_170 if s != "variation"])
    def test_all_models_and_standalone_shot_types_compile(self, model, shot_type):
        spec = {
            "description": f"A student examines a detailed anatomical model in a classroom for {shot_type}.",
            "aspect_ratio": "16:9",
            "shot_type": shot_type,
            "has_character": shot_type not in ("still_life", "environment"),
            "character_free": shot_type in ("still_life", "environment"),
        }
        res = compile_prompt(model, "scene", spec, version="1.7.0")
        assert res["version"] == "1.7.0"
        assert res["purpose"] == "scene"
        assert len(res["sha256"]) == 64
        assert "strictly forbid white-on-black YouTube subtitle boxes" in res["prompt"]
        assert "Render a 100% full-bleed illustration" in res["prompt"]

    @pytest.mark.parametrize("model", MODELS_170)
    def test_variation_shot_type_requires_base_reference_and_preserve_change(self, model):
        # Missing base_reference
        spec_no_base = {
            "description": "The student turns the page of the notebook.",
            "aspect_ratio": "16:9",
            "shot_type": "variation",
            "preserve": ["notebook outline on table"],
            "change": ["page turned to page 2"],
        }
        with pytest.raises(PromptError, match="FLOW_BASE_REFERENCE_REQUIRED"):
            compile_prompt(model, "variation", spec_no_base, version="1.7.0")

        # Missing change
        spec_no_change = {
            "description": "The student turns the page of the notebook.",
            "aspect_ratio": "16:9",
            "shot_type": "variation",
            "base_reference": BASE_REF,
            "preserve": ["notebook outline on table"],
        }
        with pytest.raises(PromptError, match="FLOW_VARIATION_INVALID"):
            compile_prompt(model, "variation", spec_no_change, version="1.7.0")

        # Valid variation
        spec_valid = {
            "description": "The student turns the page of the notebook.",
            "aspect_ratio": "16:9",
            "shot_type": "variation",
            "base_reference": BASE_REF,
            "preserve": ["notebook outline on desk"],
            "change": ["page flipped over to show diagram"],
            "has_character": True,
        }
        res = compile_prompt(model, "variation", spec_valid, version="1.7.0")
        assert res["purpose"] == "variation"
        assert "A Base scene reference is declared" in res["prompt"]

    def test_deprecated_purposes_rejected(self):
        spec = {
            "description": "Simple background scenery.",
            "aspect_ratio": "16:9",
            "shot_type": "environment",
        }
        for bad_purpose in ("layer_background", "layer_sticker"):
            with pytest.raises(PromptError, match="FLOW_LAYERING_DISABLED"):
                compile_prompt("NanoBananaPro", bad_purpose, spec, version="1.7.0")

    def test_invalid_models_rejected(self):
        spec = {
            "description": "Valid non-cliche description of a student writing.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
        }
        for bad_model in ("NanoBananaUltra", "GPT-4", "DALL-E-3", "Midjourney-v6", ""):
            with pytest.raises(PromptError, match="FLOW_MODEL_UNSUPPORTED"):
                compile_prompt(bad_model, "scene", spec, version="1.7.0")

    def test_invalid_shot_types_rejected(self):
        for bad_shot in ("drone_shot", "dolly_zoom", "cinematic_pan", "action_cam"):
            spec = {
                "description": "Valid action description.",
                "aspect_ratio": "16:9",
                "shot_type": bad_shot,
            }
            with pytest.raises(PromptError, match="FLOW_SHOT_TYPE_UNSUPPORTED"):
                compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")

    def test_entity_policy_strict_170_rules(self):
        # Contradictory flags
        spec_contradictory = {
            "description": "A researcher reads a manuscript in a library.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "has_character": True,
            "character_free": True,
        }
        with pytest.raises(PromptError, match="FLOW_ENTITY_POLICY_INVALID"):
            compile_prompt("NanoBananaPro", "scene", spec_contradictory, version="1.7.0")

        # Non-boolean flag
        spec_non_bool = {
            "description": "A researcher reads a manuscript in a library.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "has_character": "yes",
        }
        with pytest.raises(PromptError, match="FLOW_ENTITY_POLICY_INVALID"):
            compile_prompt("NanoBananaPro", "scene", spec_non_bool, version="1.7.0")

        # Character reference without has_character
        spec_char_ref_without_char = {
            "description": "An empty classroom desk.",
            "aspect_ratio": "16:9",
            "shot_type": "still_life",
            "has_character": False,
            "character_reference": BASE_REF,
        }
        with pytest.raises(PromptError, match="FLOW_ENTITY_POLICY_INVALID"):
            compile_prompt("NanoBananaPro", "scene", spec_char_ref_without_char, version="1.7.0")

    def test_character_free_suppresses_cast_rule_in_prompt(self):
        spec = {
            "description": "A clean wooden desk with a microscope and notes.",
            "aspect_ratio": "16:9",
            "shot_type": "still_life",
            "has_character": False,
            "character_free": True,
        }
        res = compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")
        assert "Strict character-free composition: absolutely no human figures" in res["prompt"]
        assert "When people are explicitly requested" not in res["prompt"]

    def test_compilation_determinism_and_uniqueness(self):
        spec1 = {
            "description": "A scholar writes notes with a fountain pen in an archive.",
            "aspect_ratio": "16:9",
            "shot_type": "macro_prop",
            "allowed_text": ["GHI CHÉP"],
        }
        res1_a = compile_prompt("NanoBananaPro", "scene", spec1, version="1.7.0")
        res1_b = compile_prompt("NanoBananaPro", "scene", spec1, version="1.7.0")
        assert res1_a["sha256"] == res1_b["sha256"]
        assert res1_a["prompt"] == res1_b["prompt"]

        # Different model produces distinct output
        res2 = compile_prompt("NanoBanana2", "scene", spec1, version="1.7.0")
        assert res1_a["sha256"] != res2["sha256"]


# ==============================================================================
# 2. NEGATIVE CLEARANCE DIRECTIVES VERIFICATION
# ==============================================================================

class TestNegativeClearanceDirectives:
    """Stress test negative clearance directives and contract detection."""

    def test_compiler_appends_exact_negative_clearance_clause(self):
        spec = {
            "description": "A researcher organizes printed research papers in archival binders.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
        }
        res = compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")
        prompt = res["prompt"]
        assert "Explicit negative clearance directive:" in prompt
        assert "strictly forbid white-on-black YouTube subtitle boxes" in prompt
        assert "caption bars" in prompt
        assert "letterbox bars" in prompt
        assert "browser player controls" in prompt
        assert "zero reserved subtitle areas" in prompt

    def test_full_frame_170_wipes_caption_clearance_in_normalized_data(self):
        spec = {
            "description": "An instructor draws a geometric diagram on a whiteboard.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "caption_clearance": {"edge": "bottom", "fraction": 0.20},
        }
        res = compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")
        # In full frame versions (1.3.0+), caption_clearance is forced to None
        assert '"caption_clearance": null' in res["prompt"]

    @pytest.mark.parametrize("violation_term", [
        "subtitle box",
        "subtitle boxes",
        "letterbox",
        "letterbox bars",
        "player control",
        "player controls",
    ])
    def test_explainer_contract_catches_clearance_terms_in_description(self, violation_term):
        content = {
            "scenes": [
                {
                    "images": [
                        {
                            "id": "SC01_IMG01",
                            "description": f"An illustration with a prominent {violation_term} visible at the bottom.",
                        }
                    ]
                }
            ]
        }
        errors = validate_clearance_and_labels(content)
        assert any(
            "CLEARANCE_VIOLATION" in e and violation_term in e
            for e in errors
        ), f"Expected CLEARANCE_VIOLATION for '{violation_term}', got: {errors}"

    def test_explainer_contract_catches_reserved_caption_clearance_band(self):
        content = {
            "scenes": [
                {
                    "images": [
                        {
                            "id": "SC02_IMG01",
                            "description": "A clean whiteboard diagram with formulas.",
                            "caption_clearance": {"edge": "bottom", "fraction": 0.25},
                        }
                    ]
                }
            ]
        }
        errors = validate_clearance_and_labels(content)
        assert any("prohibits caption clearance bands" in e for e in errors)


# ==============================================================================
# 3. LABEL HEIGHT (< 5%) AND UPPERCASE CONSTRAINTS
# ==============================================================================

class TestLabelConstraints170:
    """Stress test uppercase Vietnamese, concise limits, and height thresholds (< 5%)."""

    @pytest.mark.parametrize("valid_label", [
        "TƯ DUY",
        "NHẬN THỨC",
        "PHƯƠNG PHÁP LUẬN",
        "BẢN CHẤT TRI THỨC",
        "ĐỌC SÂU",
        "Ý TƯỞNG CỐT LÕI",
        "BƯỚC 1: XÁC MINH (100%)",
        "QUY TẮC 80/20",
    ])
    def test_valid_uppercase_vietnamese_labels_accepted(self, valid_label):
        spec = {
            "description": "An analyst examines statistical charts and documents in a quiet room.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "allowed_text": [valid_label],
        }
        res = compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")
        assert valid_label in res["prompt"]
        assert "Label constraint:" in res["prompt"]
        assert "< 5% frame height" in res["prompt"]

    @pytest.mark.parametrize("invalid_label,reason", [
        ("Tư duy", "mixed case"),
        ("nhận thức", "all lowercase"),
        ("TU DUy", "trailing lowercase letter"),
        ("Cognitive Bias", "mixed case english"),
        ("ĐỌC SÂU VÀ PHÂN TÍCH RẤT KỸ LƯỠNG MỖI NGÀY", "exceeds 6 words"),
        ("MỘT HAI BA BỐN NĂM SÁU BẢY", "7 words"),
        ("ĐÂY LÀ MỘT DÒNG NHÃN CHỮ CỰC KỲ DÀI VƯỢT QUÁ BỐN MƯƠI LĂM KÝ TỰ", "exceeds 45 chars"),
    ])
    def test_invalid_labels_rejected_by_compiler(self, invalid_label, reason):
        spec = {
            "description": "An analyst reviews research findings on paper documents.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "allowed_text": [invalid_label],
        }
        with pytest.raises(PromptError, match="FLOW_VISIBLE_TEXT_INVALID"):
            compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")

    @pytest.mark.parametrize("height_key", ["height", "max_height", "proportion", "frame_height"])
    @pytest.mark.parametrize("bad_height", [0.05, 0.05001, 0.08, 0.15, 0.5])
    def test_label_height_at_or_above_5_percent_rejected_by_compiler(self, height_key, bad_height):
        spec = {
            "description": "A researcher labels files on a wooden desk.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "allowed_text": [
                {"text": "HỒ SƠ", height_key: bad_height}
            ],
        }
        with pytest.raises(PromptError, match="exceeds compact proportion"):
            compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")

    @pytest.mark.parametrize("height_key", ["height", "max_height", "proportion", "frame_height"])
    @pytest.mark.parametrize("good_height", [0.0499, 0.04, 0.035, 0.02, 0.01])
    def test_label_height_below_5_percent_accepted_by_compiler(self, height_key, good_height):
        spec = {
            "description": "A researcher organizes files and notebooks on a wooden desk.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "allowed_text": [
                {"text": "HỒ SƠ", height_key: good_height}
            ],
        }
        res = compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")
        assert "HỒ SƠ" in res["prompt"]

    def test_explainer_contract_catches_label_errors(self):
        # 1. Lowercase label
        content_lower = {
            "scenes": [{"images": [{"id": "IMG_LOWER", "description": "Chart.", "allowed_text": ["Tư Duy"]}]}]
        }
        errs = validate_clearance_and_labels(content_lower)
        assert any("LABEL_NOT_UPPERCASE" in e for e in errs)

        # 2. Too many words
        content_verbose = {
            "scenes": [{"images": [{"id": "IMG_VERBOSE", "description": "Chart.", "allowed_text": ["A B C D E F G"]}]}]
        }
        errs = validate_clearance_and_labels(content_verbose)
        assert any("LABEL_NOT_CONCISE" in e for e in errs)

        # 3. Height >= 5%
        content_tall = {
            "scenes": [{"images": [{"id": "IMG_TALL", "description": "Chart.", "allowed_text": [{"text": "NHÃN", "height": 0.06}]}]}]
        }
        errs = validate_clearance_and_labels(content_tall)
        assert any("LABEL_HEIGHT_EXCEEDED" in e for e in errs)


# ==============================================================================
# 4. ADVERSARIAL STRESS TEST: CLICHE & CONCEPT MISMATCH GATES
# ==============================================================================

class TestClicheAndConceptMismatchGates:
    """Stress test FLOW_LAZINESS_VIOLATION and FLOW_CONCEPT_OBJECT_MISMATCH."""

    @pytest.mark.parametrize("cliche_token", [
        "funnel", "funnels",
        "gear", "gears",
        "lightbulb", "light bulbs",
        "glowing brain", "glowing brains",
        "exploding brain", "exploding brains",
        "abstract void", "dark charcoal void",
        "metaphor of",
        "symbolizing", "symbolising",
        "puzzle", "puzzle piece", "puzzle pieces", "puzzle blocks",
        "iceberg", "icebergs",
        "hamster wheel", "hamster wheels",
        "treadmill", "treadmills",
    ])
    def test_banned_170_cliches_trigger_flow_laziness_violation(self, cliche_token):
        spec = {
            "description": f"Illustration showing a {cliche_token} to explain the concept.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
        }
        with pytest.raises(PromptError, match="FLOW_LAZINESS_VIOLATION"):
            compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")

    def test_160_backwards_compatibility_uses_lazy_visual_action_forbidden(self):
        spec_160 = {
            "description": "A character sits and thinks quietly in an empty room.",
            "aspect_ratio": "16:9",
            "shot_type": "concept_metaphor",
        }
        with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN"):
            compile_prompt("NanoBananaPro", "scene", spec_160, version="1.6.0")

    @pytest.mark.parametrize("culinary_prop", ["salt", "salts", "soup", "soups", "cauldron", "cauldrons", "shallow saucer", "chopsticks", "rice bowl"])
    def test_culinary_props_in_cognitive_scene_trigger_concept_mismatch(self, culinary_prop):
        spec = {
            "description": f"A student pours {culinary_prop} onto a plate while studying.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "allowed_text": ["TƯ DUY"],
        }
        with pytest.raises(PromptError, match="FLOW_CONCEPT_OBJECT_MISMATCH"):
            compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")

    def test_reading_label_with_manuscripts_accepted(self):
        spec = {
            "description": "An archivist studies ancient manuscripts on an oak table.",
            "aspect_ratio": "16:9",
            "shot_type": "full_scene",
            "allowed_text": ["ĐỌC SÂU"],
        }
        res = compile_prompt("NanoBananaPro", "scene", spec, version="1.7.0")
        assert "manuscripts" in res["prompt"]


# ==============================================================================
# 5. PROCESS GROUP & WORKER ISOLATION AUDIT
# ==============================================================================

class TestProcessGroupAndWorkerIsolation:
    """Verify zero active worker PGIDs and zero lingering Chrome worker processes."""

    def test_registry_file_has_zero_active_processes(self):
        reg_file = DEFAULT_REGISTRY_FILE
        assert reg_file.exists(), f"Registry file {reg_file} should exist"
        data = json.loads(reg_file.read_text(encoding="utf-8"))
        processes = data.get("processes", {})
        assert len(processes) == 0, f"Expected 0 active worker PGIDs in registry, found {len(processes)}: {processes}"

    def test_process_group_manager_active_processes_is_empty(self):
        pm = ProcessGroupManager()
        assert len(pm.active_processes) == 0, f"ProcessGroupManager active_processes must be empty, got {pm.active_processes}"

    def test_zero_lingering_cdp_worker_chrome_processes(self):
        """Audit /proc to ensure no chrome instances are running with --remote-debugging-port or flow_cdp profiles."""
        proc_dir = Path("/proc")
        leaked_workers = []
        for entry in proc_dir.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                cmdline_path = entry / "cmdline"
                if not cmdline_path.is_file():
                    continue
                cmdline = cmdline_path.read_bytes().decode("utf-8", errors="ignore")
                # Look for Chrome workers spawned with remote-debugging-port or flow_cdp/chrome-profile
                if ("remote-debugging-port" in cmdline or "chrome-profile" in cmdline) and ("chrome" in cmdline.lower() or "chromium" in cmdline.lower()):
                    leaked_workers.append((entry.name, cmdline[:150]))
            except (OSError, PermissionError):
                continue
        assert len(leaked_workers) == 0, f"Found lingering CDP worker processes: {leaked_workers}"

    def test_clean_singleton_locks_operation(self, tmp_path):
        """Verify lock cleaner removes SingletonLock, SingletonCookie, SingletonSocket."""
        user_dir = tmp_path / "user_data"
        prof_dir = user_dir / "Default"
        prof_dir.mkdir(parents=True)
        (user_dir / "SingletonLock").symlink_to("127.0.0.1:+1234")
        (user_dir / "SingletonCookie").write_text("cookie")
        (prof_dir / "SingletonSocket").symlink_to("/tmp/socket")

        cleaned = clean_singleton_locks(user_dir, "Default")
        assert len(cleaned) == 3
        assert not (user_dir / "SingletonLock").exists()
        assert not (user_dir / "SingletonCookie").exists()
        assert not (prof_dir / "SingletonSocket").exists()
