"""Empirical Challenger 1 Stress Harness — Milestone M1: HD2D Contract & Registry.

This test suite executes rigorous adversarial checks, generators, oracles,
and stress harnesses against prompt compiler 1.6.0, registry 1.6.0,
character suppression, style purity, and the Banned Laziness Lexicon.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest
from flow_prompts import PromptError, compile, compile_pinned, create_pin, registry
from pilot import ROOT
from visual_style import STYLE_DESCRIPTION, STYLE_ID, STYLE_VERSION, render_style

ALL_10_SHOT_TYPES = [
    "concept_metaphor",
    "visual_diagram",
    "cutaway_detail",
    "full_scene",
    "variation",
    "macro_prop",
    "white_card",
    "white_isolated",
    "still_life",
    "environment",
]

MODELS = ["NanoBananaPro", "NanoBanana2", "NanoBanana2Lite"]
RATIOS = ["16:9", "9:16"]

BASE_REF = {
    "media_id": "00000000-0000-4000-8000-000000000001",
    "sha256": "a" * 64,
}


def base_payload(shot_type: str, ratio: str = "16:9") -> dict:
    payload = {
        "description": "An active scholar tears open an ancient parchment tax scroll on a stone desk.",
        "aspect_ratio": ratio,
        "shot_type": shot_type,
        "allowed_text": [{"text": "CLAIM 01", "placement": "upper-left"}],
    }
    if shot_type == "variation":
        payload["base_reference"] = copy.deepcopy(BASE_REF)
        payload["preserve"] = ["Preserve stone desk geometry and warm ambient lighting."]
        payload["change"] = ["The scholar rolls up the parchment scroll with both hands."]
    return payload


# ==============================================================================
# SECTION 1: Exhaustive Compilation Across All 10 Shot Types & Models & Ratios
# ==============================================================================


@pytest.mark.parametrize("shot_type", ALL_10_SHOT_TYPES)
@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("ratio", RATIOS)
def test_all_10_shot_types_compile_deterministically(shot_type: str, model: str, ratio: str) -> None:
    purpose = "variation" if shot_type == "variation" else "scene"
    data = base_payload(shot_type, ratio)

    # First compilation
    res1 = compile(model, purpose, data, "1.6.0")
    # Second compilation with reversed keys to verify key-order invariance
    reversed_data = dict(reversed(list(data.items())))
    res2 = compile(model, purpose, reversed_data, "1.6.0")

    assert res1 == res2, f"Compiler output nondeterministic for {shot_type} on {model}"
    assert res1["version"] == "1.6.0"
    assert res1["sha256"] == hashlib.sha256(res1["prompt"].encode("utf-8")).hexdigest()
    assert res1["template_id"] == f"flow.{res1['model_id']}.{purpose}"

    # Verify JSON block in prompt parses back and matches visual data
    json_block = res1["prompt"].split("Visual data (JSON; learner strings are exact data):\n\n")[1]
    parsed_visual = json.loads(json_block)
    assert parsed_visual["shot_type"] == shot_type
    assert parsed_visual["aspect_ratio"] == ratio
    assert parsed_visual["caption_clearance"] is None  # Full frame clearance invariant


def test_variation_shot_type_enforces_base_reference_and_purpose() -> None:
    # Variation without base reference fails
    bad_data = {
        "description": "Scholar raises arm.",
        "aspect_ratio": "16:9",
        "shot_type": "variation",
        "preserve": ["Keep room."],
        "change": ["Raise arm."],
    }
    with pytest.raises(PromptError, match="FLOW_BASE_REFERENCE_REQUIRED"):
        compile("NanoBanana2", "variation", bad_data, "1.6.0")

    # Variation shot_type with purpose != 'variation' fails
    with pytest.raises(PromptError, match="FLOW_BASE_REFERENCE_REQUIRED"):
        compile("NanoBanana2", "scene", {**bad_data, "base_reference": BASE_REF}, "1.6.0")


# ==============================================================================
# SECTION 2: Character Suppression Contract Verification
# ==============================================================================


@pytest.mark.parametrize("shot_type", ["visual_diagram", "cutaway_detail"])
def test_diagram_and_cutaway_strictly_character_free_by_default(shot_type: str) -> None:
    spec = registry("1.6.0")
    data = base_payload(shot_type)
    res = compile("NanoBanana2", "scene", data, "1.6.0")
    prompt = res["prompt"]

    assert "Strict character-free composition" in prompt
    assert "absolutely no human figures" in prompt
    assert "round white head" not in prompt
    assert "dot or oval eyes" not in prompt
    assert "thin stick limbs" not in prompt
    assert "simplified cartoon hands" not in prompt
    assert spec["cast_rule"] not in prompt


def test_visual_diagram_with_explicit_character_component() -> None:
    # When a diagram explicitly includes a figure (has_character=True), cast_rule is restored
    spec = registry("1.6.0")
    data = base_payload("visual_diagram")
    data["has_character"] = True
    res = compile("NanoBanana2", "scene", data, "1.6.0")
    prompt = res["prompt"]

    assert "Strict character-free composition" not in prompt
    assert spec["cast_rule"] in prompt
    assert "round white head" in prompt


def test_concept_metaphor_character_suppression_switch() -> None:
    spec = registry("1.6.0")

    # Default: character-based metaphor
    d_char = base_payload("concept_metaphor")
    r_char = compile("NanoBanana2", "scene", d_char, "1.6.0")
    assert "Strict character-free composition" not in r_char["prompt"]
    assert spec["cast_rule"] in r_char["prompt"]

    # Explicit character_free=True: character-free metaphor (e.g. balancing clay jars)
    d_free = base_payload("concept_metaphor")
    d_free["character_free"] = True
    r_free = compile("NanoBanana2", "scene", d_free, "1.6.0")
    assert "Strict character-free composition" in r_free["prompt"]
    assert spec["cast_rule"] not in r_free["prompt"]
    assert "round white head" not in r_free["prompt"]


@pytest.mark.parametrize("shot_type", ["still_life", "environment"])
def test_legacy_rest_shots_strictly_character_free(shot_type: str) -> None:
    spec = registry("1.6.0")
    data = base_payload(shot_type)
    res = compile("NanoBanana2", "scene", data, "1.6.0")
    assert "Strict character-free composition" in res["prompt"]
    assert spec["cast_rule"] not in res["prompt"]


@pytest.mark.parametrize("shot_type", ["full_scene", "variation", "macro_prop", "white_card", "white_isolated"])
def test_character_bearing_shots_retain_cast_rule(shot_type: str) -> None:
    spec = registry("1.6.0")
    purpose = "variation" if shot_type == "variation" else "scene"
    data = base_payload(shot_type)
    res = compile("NanoBanana2", purpose, data, "1.6.0")
    assert "Strict character-free composition" not in res["prompt"]
    assert spec["cast_rule"] in res["prompt"]
    assert "round white head" in res["prompt"]


# ==============================================================================
# SECTION 3: HD2D Style Purity & Clean Concept Cards
# ==============================================================================


@pytest.mark.parametrize("shot_type", ALL_10_SHOT_TYPES)
def test_hd2d_style_invariants_across_all_shot_types(shot_type: str) -> None:
    purpose = "variation" if shot_type == "variation" else "scene"
    data = base_payload(shot_type)
    res = compile("NanoBanana2", purpose, data, "1.6.0")
    prompt = res["prompt"]

    # Hand-drawn 2D explainer styling invariants
    assert "Hand-drawn 2D explainer illustration" in prompt
    assert "earth-toned foundation" in prompt
    assert "terracotta, warm ochre, sage green, navy, warm gray" in prompt
    assert "fine-to-medium warm-charcoal contours" in prompt
    assert "60-30-10 color ratio" in prompt
    assert "25–35% calm open canvas" in prompt
    assert "clean pure white #FFFFFF" in prompt

    # Negative directives forbidding photographic/3D clutter
    assert "No decorative clutter" in prompt
    assert "photographic room interiors" in prompt
    assert "photorealism" in prompt
    assert "lens blur" in prompt
    assert "3D rendering" in prompt


@pytest.mark.parametrize("shot_type", ["white_card", "visual_diagram", "white_isolated"])
def test_clean_white_canvas_for_diagrams_and_cards(shot_type: str) -> None:
    data = base_payload(shot_type)
    res = compile("NanoBanana2", "scene", data, "1.6.0")
    prompt = res["prompt"]
    assert "#FFFFFF" in prompt
    # Shot type specification requires pure white background
    if shot_type == "visual_diagram":
        assert "clean pure white #FFFFFF field" in prompt
    elif shot_type == "white_card":
        assert "clean pure white #FFFFFF concept card" in prompt
    elif shot_type == "white_isolated":
        assert "clean pure white #FFFFFF field" in prompt


# ==============================================================================
# SECTION 4: Adversarial Stress Testing of Banned Laziness Lexicon
# ==============================================================================

BANNED_LAZINESS_TEST_MATRIX = [
    # Passive character actions
    ("sits and thinks", "passive character action"),
    ("sitting quietly", "passive character action"),
    ("staring at laptop", "passive character action"),
    ("staring at screen", "passive character action"),
    ("staring at paper", "passive character action"),
    ("staring at wall", "passive character action"),
    ("pondering", "passive character action"),
    ("feeling stressed", "passive character action"),
    ("lost in thought", "passive character action"),
    # Lazy still-life clichés
    ("coffee mug on desk", "lazy still-life cliché"),
    ("books resting on table", "lazy still-life cliché"),
    ("desk lamp glowing", "lazy still-life cliché"),
    ("empty room", "lazy still-life cliché"),
    ("scattered papers on desk", "lazy still-life cliché"),
    ("vintage clock", "lazy still-life cliché"),
    ("reading lamp", "lazy still-life cliché"),
    # Evasive abstract phrasing
    ("a conceptual metaphor of", "evasive abstract phrasing"),
    ("an abstract illustration of", "evasive abstract phrasing"),
    ("a symbolic representation of", "evasive abstract phrasing"),
]


@pytest.mark.parametrize("phrase,expected_category", BANNED_LAZINESS_TEST_MATRIX)
def test_banned_laziness_lexicon_direct_rejection(phrase: str, expected_category: str) -> None:
    # Direct appearance in description
    data = {
        "description": f"The scene depicts {phrase} in the center.",
        "aspect_ratio": "16:9",
        "shot_type": "full_scene",
    }
    with pytest.raises(PromptError) as ctx:
        compile("NanoBanana2", "scene", data, "1.6.0")
    msg = str(ctx.value)
    assert "LAZY_VISUAL_ACTION_FORBIDDEN" in msg
    assert expected_category in msg


@pytest.mark.parametrize("phrase,_", BANNED_LAZINESS_TEST_MATRIX)
def test_banned_laziness_lexicon_casing_variations(phrase: str, _: str) -> None:
    # Test UPPERCASE
    upper_phrase = phrase.upper()
    data = {"description": f"A figure {upper_phrase} here.", "aspect_ratio": "16:9", "shot_type": "full_scene"}
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN"):
        compile("NanoBanana2", "scene", data, "1.6.0")

    # Test Title Case
    title_phrase = phrase.title()
    data = {"description": f"A figure {title_phrase} here.", "aspect_ratio": "16:9", "shot_type": "full_scene"}
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN"):
        compile("NanoBanana2", "scene", data, "1.6.0")


@pytest.mark.parametrize("phrase,_", BANNED_LAZINESS_TEST_MATRIX)
def test_banned_laziness_lexicon_whitespace_and_punctuation(phrase: str, _: str) -> None:
    # Multiple spaces between words (for multi-word phrases)
    if " " in phrase:
        spaced_phrase = re.sub(r"\s+", "   ", phrase)
        data = {"description": f"A figure {spaced_phrase} here.", "aspect_ratio": "16:9", "shot_type": "full_scene"}
        with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN"):
            compile("NanoBanana2", "scene", data, "1.6.0")

    # Embedded at end of sentence with punctuation
    data = {"description": f"Before the event, the person {phrase}.", "aspect_ratio": "16:9", "shot_type": "full_scene"}
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN"):
        compile("NanoBanana2", "scene", data, "1.6.0")


def test_banned_laziness_across_all_data_fields() -> None:
    # 1. In 'preserve'
    d_preserve = {
        "description": "Scholar tears paper.",
        "aspect_ratio": "16:9",
        "shot_type": "variation",
        "base_reference": BASE_REF,
        "preserve": ["Keep the coffee mug on desk."],
        "change": ["Tear paper."],
    }
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN: preserve contains lazy still-life cliché"):
        compile("NanoBanana2", "variation", d_preserve, "1.6.0")

    # 2. In 'change'
    d_change = {
        "description": "Scholar tears paper.",
        "aspect_ratio": "16:9",
        "shot_type": "variation",
        "base_reference": BASE_REF,
        "preserve": ["Keep room."],
        "change": ["The scholar sits and thinks."],
    }
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN: change contains passive character action"):
        compile("NanoBanana2", "variation", d_change, "1.6.0")

    # 3. In 'allowed_text'
    d_text = {
        "description": "Scholar tears paper.",
        "aspect_ratio": "16:9",
        "shot_type": "full_scene",
        "allowed_text": ["sits and thinks"],
    }
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN: allowed_text contains passive character action"):
        compile("NanoBanana2", "scene", d_text, "1.6.0")

    # 4. In 'composition'
    d_comp = {
        "description": "Scholar tears paper.",
        "aspect_ratio": "16:9",
        "shot_type": "full_scene",
        "composition": "A conceptual metaphor of time passing.",
    }
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN: composition contains evasive abstract phrasing"):
        compile("NanoBanana2", "scene", d_comp, "1.6.0")


def test_valid_active_verbs_do_not_trigger_false_positives() -> None:
    active_descriptions = [
        "A student shatters a thick stone obstacle with a massive iron mallet.",
        "The farmer crushes salt crystals between two rough granite stones.",
        "The researcher climbs a steep rocky peak overlooking dense sea mist.",
        "The narrator tears open the royal decree exposing the fraudulent seals.",
        "A scholar plants a wooden staff firmly into the dry riverbed.",
        "A hand balances two heavy clay jars on a rustic timber scale.",
        "A column chart displays 70% imposter self-doubt towering over peer accolades.",
        "A cross-section of the soup cauldron exposes layered sediment and salt grains.",
    ]
    for desc in active_descriptions:
        data = {"description": desc, "aspect_ratio": "16:9", "shot_type": "concept_metaphor"}
        res = compile("NanoBanana2", "scene", data, "1.6.0")
        assert res["sha256"]


def test_historical_versions_exempt_from_160_laziness_rejection() -> None:
    # Historical version 1.5.0 should compile phrases like "sitting quietly" or "empty room"
    # because they were allowed in legacy versions, preserving byte-exact immutability
    legacy_data = {
        "description": "A figure sitting quietly in an empty room under soft light.",
        "aspect_ratio": "16:9",
        "shot_type": "full_scene",
    }
    res_150 = compile("NanoBanana2", "scene", legacy_data, "1.5.0")
    assert res_150["version"] == "1.5.0"
    assert "sitting quietly" in res_150["prompt"]

    # But version 1.6.0 MUST reject it
    with pytest.raises(PromptError, match="LAZY_VISUAL_ACTION_FORBIDDEN"):
        compile("NanoBanana2", "scene", legacy_data, "1.6.0")


# ==============================================================================
# SECTION 5: Historical Immutability Ledger Check (SHA-256)
# ==============================================================================


def test_all_historical_registries_remain_byte_identical() -> None:
    historical_hashes = {
        "1.0.0": "13c6656ec627da3b05cb01ae87bfb348a5714f62d4e4d792a539854fe4ed4b23",
        "1.0.1": "069e87e74bb808f88cc8bb689d4b1b84d759bfb80370d623de04c246536c05ce",
        "1.1.0": "b2a41021a795158e89b9f39b1984b8e110f2ff3d2397ef07256a01a3d40f2dae",
        "1.2.0": "d574d19eceadcd3db31d3b9c5729c4cca7f5c55333d1c6f1b4dd83019289403b",
        "1.3.0": "6c689b6af72b779ed477998797f94b8703824403e1d1d02d5be85290976d6176",
        "1.4.0": "09c268d08b87500fee71b7de3068e002511623006557fd75b9dd55c0e94f4a09",
        "1.5.0": "37de6f79cfed9e2b85636e690bfe5f238c966c9ec887b0898957f0a06b06fb26",
    }
    versions_dir = Path(__file__).resolve().parents[1] / "flow_prompts/versions"
    for ver, expected_sha in historical_hashes.items():
        reg_file = versions_dir / ver / "registry.json"
        assert reg_file.is_file(), f"Registry file missing for {ver}"
        actual_sha = hashlib.sha256(reg_file.read_bytes()).hexdigest()
        assert actual_sha == expected_sha, f"Historical registry {ver} was mutated! SHA256 mismatch."


# ==============================================================================
# SECTION 6: Renderer Vignette Module Compatibility
# ==============================================================================


def test_renderer_vignette_bypasses_hd2d() -> None:
    module = (ROOT / "renderer/visual-style.mjs").as_uri()
    cmd = [
        "node",
        "--input-type=module",
        "-e",
        f"import {{vignetteBackground as v}} from '{module}'; "
        f"console.log(JSON.stringify(v({{visual_style_profile: '{STYLE_ID}'}})));",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    res = json.loads(proc.stdout.strip())
    assert res is None, "Vignette should be None for handdrawn_2d_explainer profile"


# ==============================================================================
# SECTION 7: Content Schema and Contract Alignment
# ==============================================================================


def test_content_schema_v3_contains_all_10_shot_types() -> None:
    schema_path = ROOT / "schemas/content-v3.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    # Extract shot_type enum from images schema
    shot_enum = schema["properties"]["scenes"]["items"]["properties"]["images"]["items"]["properties"]["shot_type"]["enum"]
    for shot in ALL_10_SHOT_TYPES:
        assert shot in shot_enum, f"Shot type {shot} missing from schemas/content-v3.json"
    assert len(shot_enum) == 10


def test_style_system_constants_synchronized() -> None:
    assert STYLE_VERSION == "1.6.0"
    assert STYLE_ID == "handdrawn_2d_explainer"
    assert render_style({"style": STYLE_DESCRIPTION}) == STYLE_ID
