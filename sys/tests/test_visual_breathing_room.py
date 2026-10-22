"""Tests for character breathing room and setting description verbosity guards (R1-R4)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.visual_quality import (
    check_abstract_card_clustering,
    check_atomic_variation_continuity,
    check_character_breathing_room,
    check_setting_description_verbosity,
    check_ungrounded_environment_scenes,
)
from tools.script_diversity_linter import lint_script


def _make_beat_scene(scene_id: str, shot_type: str, char_ids: list[str] | None = None, desc: str = "", **kwargs) -> dict:
    beat = {
        "id": f"{scene_id}_I1",
        "shot_type": shot_type,
        "character_ids": char_ids if char_ids is not None else (["CH01"] if shot_type in {"full_scene", "variation"} else []),
        "description": desc,
    }
    beat.update(kwargs)
    return {
        "id": scene_id,
        "setting": "A quiet room under soft light.",
        "narration": f"Narration for scene {scene_id} explaining the research model.",
        "images": [beat],
    }


# =========================================================================
# Group 1: Character Streak Rule (Max 4 Consecutive Character Beats)
# =========================================================================

def test_consecutive_character_beats_under_or_equal_to_four_passes():
    scenes = [
        _make_beat_scene("SC01", "full_scene"),
        _make_beat_scene("SC02", "variation"),
        _make_beat_scene("SC03", "full_scene"),
        _make_beat_scene("SC04", "variation"),
        _make_beat_scene("SC05", "still_life"),  # rest
        _make_beat_scene("SC06", "full_scene"),
        _make_beat_scene("SC07", "variation"),
        _make_beat_scene("SC08", "full_scene"),
        _make_beat_scene("SC09", "variation"),
        _make_beat_scene("SC10", "environment"),  # rest
    ]
    violations = check_character_breathing_room(scenes)
    streak_violations = [v for v in violations if v["type"] == "CHARACTER_STREAK_EXCEEDED"]
    assert len(streak_violations) == 0, f"Expected 0 streak violations, got {streak_violations}"


def test_consecutive_character_beats_exceeding_four_fails():
    scenes = [
        _make_beat_scene("SC01", "full_scene"),
        _make_beat_scene("SC02", "variation"),
        _make_beat_scene("SC03", "full_scene"),
        _make_beat_scene("SC04", "variation"),
        _make_beat_scene("SC05", "full_scene"),  # 5th consecutive
    ]
    violations = check_character_breathing_room(scenes)
    streak_violations = [v for v in violations if v["type"] == "CHARACTER_STREAK_EXCEEDED"]
    assert len(streak_violations) == 1
    assert streak_violations[0]["streak"] == 5
    assert streak_violations[0]["scene_id"] == "SC05"
    assert "Excessive consecutive character beats (5 > 4)" in streak_violations[0]["message"]


def test_consecutive_character_beats_longer_streak_accumulates_violations():
    scenes = [
        _make_beat_scene(f"SC{i:02d}", "full_scene")
        for i in range(1, 7)
    ]
    violations = check_character_breathing_room(scenes)
    streak_violations = [v for v in violations if v["type"] == "CHARACTER_STREAK_EXCEEDED"]
    assert len(streak_violations) == 2  # streak 5 and streak 6
    assert streak_violations[0]["streak"] == 5
    assert streak_violations[1]["streak"] == 6
    assert streak_violations[0]["beat_index"] == 4
    assert streak_violations[1]["beat_index"] == 5


def test_rest_beat_resets_streak_counter():
    scenes = [
        _make_beat_scene("SC01", "full_scene"),
        _make_beat_scene("SC02", "variation"),
        _make_beat_scene("SC03", "full_scene"),
        _make_beat_scene("SC04", "variation"),
        _make_beat_scene("SC05", "still_life"),  # rest resets streak to 0
        _make_beat_scene("SC06", "full_scene"),
        _make_beat_scene("SC07", "variation"),
        _make_beat_scene("SC08", "full_scene"),
        _make_beat_scene("SC09", "variation"),
    ]
    violations = check_character_breathing_room(scenes)
    streak_violations = [v for v in violations if v["type"] == "CHARACTER_STREAK_EXCEEDED"]
    assert len(streak_violations) == 0


# =========================================================================
# Group 2: Rolling 10-Beat Window Rule (>= 30% Rest Beats)
# =========================================================================

def test_ten_beat_window_with_three_rest_beats_passes():
    # Sequence of 10: [C, C, R, C, C, R, C, C, R, C]
    pattern = ["full_scene", "full_scene", "still_life", "full_scene", "full_scene",
               "environment", "full_scene", "full_scene", "white_card", "full_scene"]
    scenes = [_make_beat_scene(f"SC{i:02d}", shot) for i, shot in enumerate(pattern, 1)]
    violations = check_character_breathing_room(scenes)
    ratio_violations = [v for v in violations if v["type"] == "LOW_CHARACTER_FREE_RATIO"]
    assert len(ratio_violations) == 0


def test_ten_beat_window_with_two_rest_beats_fails():
    # Sequence of 10: 2 rest + 8 character (20% rest < 30%)
    pattern = ["full_scene", "full_scene", "still_life", "full_scene", "full_scene",
               "environment", "full_scene", "full_scene", "variation", "full_scene"]
    # Notice: to avoid streak > 4, we place rest beats at indices 2 and 5:
    # 0, 1 (2 C) -> 2 (R) -> 3, 4 (2 C) -> 5 (R) -> 6, 7, 8, 9 (4 C).
    scenes = [_make_beat_scene(f"SC{i:02d}", shot) for i, shot in enumerate(pattern, 1)]
    violations = check_character_breathing_room(scenes)
    ratio_violations = [v for v in violations if v["type"] == "LOW_CHARACTER_FREE_RATIO"]
    assert len(ratio_violations) == 1
    assert ratio_violations[0]["character_free_count"] == 2
    assert ratio_violations[0]["ratio"] == 0.2
    assert "Insufficient visual breathing room in 10-beat window (2/10 < 30%)" in ratio_violations[0]["message"]


def test_ten_beat_window_with_zero_rest_beats_fails():
    scenes = [_make_beat_scene(f"SC{i:02d}", "full_scene") for i in range(1, 11)]
    violations = check_character_breathing_room(scenes)
    ratio_violations = [v for v in violations if v["type"] == "LOW_CHARACTER_FREE_RATIO"]
    streak_violations = [v for v in violations if v["type"] == "CHARACTER_STREAK_EXCEEDED"]
    assert len(ratio_violations) >= 1
    assert ratio_violations[0]["character_free_count"] == 0
    assert len(streak_violations) >= 1


def test_sequence_under_ten_beats_skips_ratio_check():
    # Only 6 beats: 4 full_scene + 2 still_life
    pattern = ["full_scene", "full_scene", "still_life", "full_scene", "full_scene", "still_life"]
    scenes = [_make_beat_scene(f"SC{i:02d}", shot) for i, shot in enumerate(pattern, 1)]
    violations = check_character_breathing_room(scenes)
    ratio_violations = [v for v in violations if v["type"] == "LOW_CHARACTER_FREE_RATIO"]
    assert len(ratio_violations) == 0
    assert len(violations) == 0


# =========================================================================
# Group 3: Shot Type Classification & Edge Cases
# =========================================================================

def test_character_free_shot_types_classified_correctly():
    rest_shots = ["still_life", "environment", "white_card"]
    scenes = [
        _make_beat_scene(f"SC{i:02d}", shot, char_ids=[], desc="An archival object on a flat table.")
        for i, shot in enumerate(rest_shots, 1)
    ]
    violations = check_character_breathing_room(scenes)
    assert len(violations) == 0


def test_character_shot_types_classified_correctly():
    # 5 full_scene or variation beats must trigger streak
    scenes = [
        _make_beat_scene("SC01", "full_scene"),
        _make_beat_scene("SC02", "variation"),
        _make_beat_scene("SC03", "full_scene"),
        _make_beat_scene("SC04", "variation"),
        _make_beat_scene("SC05", "full_scene"),
    ]
    violations = check_character_breathing_room(scenes)
    assert any(v["type"] == "CHARACTER_STREAK_EXCEEDED" for v in violations)


def test_macro_prop_classification_by_character_presence():
    # macro_prop with human hand keyword in description counts as character beat
    hand_prop = _make_beat_scene("SC01", "macro_prop", char_ids=[], desc="A student hand holding a pencil over notes.")
    # macro_prop without character or human keywords counts as rest beat
    pure_prop = _make_beat_scene("SC02", "macro_prop", char_ids=[], desc="An open textbook with highlighted sentences on wooden desk.")
    # macro_prop with character_ids counts as character beat
    id_prop = _make_beat_scene("SC03", "macro_prop", char_ids=["CH01"], desc="Magnifying glass over paper.")

    # 4 pure_props + 1 hand_prop: streak should be 1
    scenes = [
        pure_prop,
        _make_beat_scene("SC04", "still_life"),
        _make_beat_scene("SC05", "environment"),
        _make_beat_scene("SC06", "white_card"),
        hand_prop,
    ]
    violations = check_character_breathing_room(scenes)
    assert len(violations) == 0

    # 5 consecutive character beats (mix of full_scene, hand_prop, id_prop)
    streak_scenes = [
        _make_beat_scene("SC11", "full_scene"),
        _make_beat_scene("SC12", "full_scene"),
        hand_prop,
        id_prop,
        _make_beat_scene("SC15", "full_scene"),
    ]
    streak_violations = check_character_breathing_room(streak_scenes)
    assert any(v["type"] == "CHARACTER_STREAK_EXCEEDED" for v in streak_violations)


def test_explicit_boolean_flags_override():
    # character_free: True overrides full_scene
    scenes = [
        _make_beat_scene(f"SC{i:02d}", "full_scene", character_free=True)
        for i in range(1, 6)
    ]
    violations = check_character_breathing_room(scenes)
    assert len(violations) == 0

    # has_character: True overrides still_life
    forced_char_scenes = [
        _make_beat_scene(f"SC{i:02d}", "still_life", has_character=True)
        for i in range(1, 6)
    ]
    forced_violations = check_character_breathing_room(forced_char_scenes)
    assert any(v["type"] == "CHARACTER_STREAK_EXCEEDED" for v in forced_violations)


# =========================================================================
# Group 4: Setting Description Verbosity
# =========================================================================

def test_setting_within_eight_words_passes():
    scenes = [
        {"id": "SC01", "setting": "Vietnamese student desk under warm lamp."},
        {"id": "SC02", "setting": "Dim library corridor with morning sun."},
    ]
    violations = check_setting_description_verbosity(scenes)
    assert len(violations) == 0


def test_setting_at_ten_words_boundary_passes_default_linter():
    # Exactly 10 words
    ten_words = "One two three four five six seven eight nine ten."
    scenes = [{"id": "SC01", "setting": ten_words}]
    violations = check_setting_description_verbosity(scenes, max_words=10)
    assert len(violations) == 0


def test_setting_exceeding_ten_words_fails():
    eleven_words = "A Vietnamese student desk at night, green lamp, highlighter, blue textbook."
    assert len(eleven_words.split()) == 11
    scenes = [{"id": "SC01", "setting": eleven_words}]
    violations = check_setting_description_verbosity(scenes, max_words=10)
    assert len(violations) == 1
    assert violations[0]["type"] == "SETTING_DESCRIPTION_TOO_VERBOSE"
    assert violations[0]["word_count"] == 11
    assert violations[0]["max_allowed"] == 10
    assert "Setting description exceeds 10 words (11 words)" in violations[0]["message"]


def test_setting_custom_eight_words_threshold():
    nine_words = "A quiet study room with books and desk lamp."
    scenes = [{"id": "SC01", "setting": nine_words}]
    violations_strict = check_setting_description_verbosity(scenes, max_words=8)
    assert len(violations_strict) == 1
    assert violations_strict[0]["word_count"] == 9
    assert violations_strict[0]["max_allowed"] == 8

    violations_default = check_setting_description_verbosity(scenes, max_words=10)
    assert len(violations_default) == 0


def test_empty_or_missing_setting_does_not_raise():
    scenes = [
        {"id": "SC01", "setting": ""},
        {"id": "SC02"},
        {"id": "SC03", "setting": "   \n\t  "},
    ]
    violations = check_setting_description_verbosity(scenes)
    assert len(violations) == 0


# =========================================================================
# Group 5: Full Pipeline & Linter Integration
# =========================================================================

def test_lint_script_end_to_end_with_breathing_room():
    scenes = [
        _make_beat_scene("SC01", "full_scene"),
        _make_beat_scene("SC02", "variation"),
        _make_beat_scene("SC03", "full_scene"),
        _make_beat_scene("SC04", "variation"),
        _make_beat_scene("SC05", "full_scene"),  # 5th streak
    ]
    # Add excessive setting description
    scenes[0]["setting"] = "A very long detailed room description with multiple lamps and books and papers scattered everywhere."
    result = lint_script(scenes, enforce_breathing_room=True)
    assert result["status"] == "FAIL"
    types = {v["type"] for v in result["violations"]}
    assert "CHARACTER_STREAK_EXCEEDED" in types
    assert "SETTING_DESCRIPTION_TOO_VERBOSE" in types


def test_lint_script_passes_fully_compliant_story():
    # 10 beats compliant story: 7 character + 3 rest, alternating <= 4 streaks, <= 8 words settings
    pattern = ["full_scene", "variation", "still_life", "full_scene", "variation",
               "environment", "full_scene", "variation", "white_card", "full_scene"]
    scenes = []
    for i, shot in enumerate(pattern, 1):
        sc = _make_beat_scene(f"SC{i:02d}", shot)
        sc["setting"] = "Quiet laboratory under soft LED light."  # 6 words
        scenes.append(sc)

    result = lint_script(scenes)
    # Filter to only visual breathing room & verbosity violations
    pacing_violations = [
        v for v in result["violations"]
        if v["type"] in {"CHARACTER_STREAK_EXCEEDED", "LOW_CHARACTER_FREE_RATIO", "SETTING_DESCRIPTION_TOO_VERBOSE"}
    ]
    assert len(pacing_violations) == 0


def test_cli_diversity_linter_subcommand_exit_codes(tmp_path: Path):
    # Compliant script file
    pattern = ["full_scene", "variation", "still_life", "full_scene", "variation",
               "environment", "full_scene", "variation", "white_card", "full_scene"]
    compliant_scenes = []
    for i, shot in enumerate(pattern, 1):
        sc = _make_beat_scene(f"SC{i:02d}", shot)
        sc["setting"] = "Quiet laboratory under soft LED light."
        compliant_scenes.append(sc)

    compliant_file = tmp_path / "compliant_content.json"
    compliant_file.write_text(json.dumps({"topic": "Compliant Research", "scenes": compliant_scenes}), encoding="utf-8")

    # Non-compliant script file (streak 5)
    failing_scenes = [_make_beat_scene(f"SC{i:02d}", "full_scene") for i in range(1, 6)]
    failing_file = tmp_path / "failing_content.json"
    failing_file.write_text(json.dumps({"topic": "Failing Research", "scenes": failing_scenes}), encoding="utf-8")

    # Test CLI invocation on failing file
    repo_root = Path(__file__).resolve().parents[2]
    cli_tool = repo_root / "sys/tools/script_diversity_linter.py"
    venv_py = repo_root / "sys/.venv/bin/python"
    py_bin = str(venv_py) if venv_py.is_file() else sys.executable

    res_fail = subprocess.run([py_bin, str(cli_tool), str(failing_file)], capture_output=True, text=True)
    assert res_fail.returncode == 1
    assert "CHARACTER_STREAK_EXCEEDED" in res_fail.stdout

    # Test non-existent file
    res_notfound = subprocess.run([py_bin, str(cli_tool), str(tmp_path / "non_existent.json")], capture_output=True, text=True)
    assert res_notfound.returncode == 2


# =========================================================================
# Group 5: Narrative & Metaphor Guardrails (HD2D)
# =========================================================================

def test_abstract_card_clustering_guardrail():
    # <= 2 abstract cards pass
    ok_scenes = [
        _make_beat_scene("SC01", "visual_diagram"),
        _make_beat_scene("SC02", "cutaway_detail"),
        _make_beat_scene("SC03", "full_scene"),
    ]
    assert len(check_abstract_card_clustering(ok_scenes)) == 0

    # > 2 abstract cards fail
    bad_scenes = [
        _make_beat_scene("SC01", "visual_diagram"),
        _make_beat_scene("SC02", "cutaway_detail"),
        _make_beat_scene("SC03", "white_card"),
    ]
    violations = check_abstract_card_clustering(bad_scenes)
    assert len(violations) == 1
    assert violations[0]["type"] == "CONSECUTIVE_ABSTRACT_CARDS_EXCEEDED"
    assert violations[0]["streak"] == 3


def test_ungrounded_environment_guardrail():
    # Environment with story setting passes
    ok_scene = _make_beat_scene("SC01", "environment")
    ok_scene["setting"] = "Quiet coastal rocky peak under dawn light."
    assert len(check_ungrounded_environment_scenes([ok_scene])) == 0

    # Environment without character, setting or metaphor fails
    bad_scene = _make_beat_scene("SC02", "environment", char_ids=[], desc="Empty field of grass.")
    bad_scene["setting"] = ""
    bad_scene["character_ids"] = []
    violations = check_ungrounded_environment_scenes([bad_scene])
    assert len(violations) == 1
    assert violations[0]["type"] == "UNGROUNDED_ENVIRONMENT_SCENE"


def test_atomic_variation_continuity_guardrail():
    # Valid variation referencing prior full_scene in same scene passes
    valid_scene = {
        "id": "SC01",
        "setting": "A student desk.",
        "images": [
            {"id": "SC01_I1", "shot_type": "full_scene", "description": "Student at desk."},
            {"id": "SC01_I2", "shot_type": "variation", "based_on": "SC01_I1", "description": "Student slumps shoulders."},
        ],
    }
    assert len(check_atomic_variation_continuity([valid_scene])) == 0

    # Broken variation with missing or invalid based_on fails
    broken_scene = {
        "id": "SC02",
        "setting": "A student desk.",
        "images": [
            {"id": "SC02_I1", "shot_type": "full_scene", "description": "Student at desk."},
            {"id": "SC02_I2", "shot_type": "variation", "based_on": "NON_EXISTENT_BEAT", "description": "Student writes."},
        ],
    }
    violations = check_atomic_variation_continuity([broken_scene])
    assert len(violations) == 1
    assert violations[0]["type"] == "BROKEN_VARIATION_CONTINUITY"

