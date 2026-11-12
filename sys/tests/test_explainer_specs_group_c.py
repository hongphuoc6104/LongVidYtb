"""Unit tests for Group C Explainer Visual Specs:
1. ban_do_quyen_luc (255 beats)
2. banh_rang (255 beats)
3. ho_so_ky_la (310 beats)
4. luat_ngam (305 beats)
5. su_ke_lai (305 beats)
"""

import json
import re
from pathlib import Path

import pytest

ROOT_DIR = Path("/home/hongphuoc6104/Desktop/vp-agent-core")
SLUGS = ["ban_do_quyen_luc", "banh_rang", "ho_so_ky_la", "luat_ngam", "su_ke_lai"]
EXPECTED_BEATS = {
    "ban_do_quyen_luc": 255,
    "banh_rang": 255,
    "ho_so_ky_la": 310,
    "luat_ngam": 305,
    "su_ke_lai": 305,
}
VALID_EXPLAINER_TYPES = {
    "CAUSE_EFFECT_DIAGRAM",
    "MECHANISM_CUTAWAY",
    "OBJECT_MACRO",
    "SPLIT_COMPARISON",
    "STEP_ENUMERATION",
    "SITUATIONAL_ACTION",
}
FIRST_5_TYPES = {
    "CAUSE_EFFECT_DIAGRAM",
    "MECHANISM_CUTAWAY",
    "OBJECT_MACRO",
    "SPLIT_COMPARISON",
    "STEP_ENUMERATION",
}


@pytest.mark.parametrize("slug", SLUGS)
def test_group_c_spec_exists_and_valid_json(slug):
    p = ROOT_DIR / f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
    assert p.is_file(), f"Spec file {p} does not exist"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data["job_id"] == f"vn_pilot_{slug}_long"
    assert "chapters" in data and len(data["chapters"]) == 10
    assert "beats" in data
    assert len(data["beats"]) == EXPECTED_BEATS[slug]


@pytest.mark.parametrize("slug", SLUGS)
def test_group_c_beat_schema_and_prompts(slug):
    p = ROOT_DIR / f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    beats = data["beats"]

    for i, b in enumerate(beats):
        assert b["beat_id"] == f"B{i:03d}"
        assert isinstance(b["narration"], str) and len(b["narration"]) > 0
        assert isinstance(b["duration"], (int, float)) and b["duration"] > 0
        assert b["explainer_type"] in VALID_EXPLAINER_TYPES

        # Prompt verification
        prompt = b["prompt"]
        assert isinstance(prompt, str)
        words = prompt.split()
        assert 35 <= len(words) <= 65, f"{slug} {b['beat_id']}: word count {len(words)} not in [35, 65]"
        assert prompt.endswith(", zero text overlay, no watermarks")
        assert "detailed visual narrative illustration" not in prompt.lower()
        assert "continuing scene continuity" not in prompt.lower()
        assert "repetitive generic landscape" not in prompt.lower()
        # FHD+ 1080p requirement: zero "8k" or "8K"
        assert not re.search(r"\b8k\b", prompt, re.I), f"{slug} {b['beat_id']}: contains 8K term in {prompt}"


@pytest.mark.parametrize("slug", SLUGS)
def test_group_c_prompts_100pct_unique(slug):
    p = ROOT_DIR / f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    beats = data["beats"]

    prompts = [b["prompt"].strip() for b in beats]
    unique_prompts = set(prompts)
    assert len(unique_prompts) == len(beats), (
        f"{slug}: expected {len(beats)} unique prompts, got {len(unique_prompts)} ({len(beats) - len(unique_prompts)} duplicates)"
    )

    # Core subjects uniqueness check on new beats
    new_beats = [b for b in beats if b.get("reuse_old_image_idx") is None]
    cores = [b["prompt"].split(",")[1].strip()[:60].lower() for b in new_beats]
    assert len(set(cores)) == len(cores), (
        f"{slug}: Duplicate core subjects: {len(set(cores))}/{len(cores)}"
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_group_c_explainer_types_distribution(slug):
    p = ROOT_DIR / f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    beats = data["beats"]

    first_5_count = sum(1 for b in beats if b["explainer_type"] in FIRST_5_TYPES)
    pct = first_5_count / len(beats) * 100.0
    assert pct >= 85.0, f"{slug}: First 5 explainer types {pct:.2f}% < 85%"


@pytest.mark.parametrize("slug", SLUGS)
def test_group_c_reuse_quotas(slug):
    p = ROOT_DIR / f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    beats = data["beats"]

    reuse_count = sum(1 for b in beats if b["reuse_old_image_idx"] is not None)
    new_count = sum(1 for b in beats if b["reuse_old_image_idx"] is None)

    if slug in ("ban_do_quyen_luc", "banh_rang"):
        assert reuse_count == 98, f"{slug}: expected 98 reused, got {reuse_count}"
        assert new_count == 157, f"{slug}: expected 157 new, got {new_count}"
    elif slug in ("luat_ngam", "su_ke_lai"):
        assert reuse_count == 117, f"{slug}: expected 117 reused, got {reuse_count}"
        assert new_count == 188, f"{slug}: expected 188 new, got {new_count}"
    elif slug == "ho_so_ky_la":
        assert reuse_count == 220, f"ho_so_ky_la: expected 220 kept strong shots, got {reuse_count}"
        assert new_count == 90, f"ho_so_ky_la: expected 90 replaced generic shots, got {new_count}"


@pytest.mark.parametrize("slug", SLUGS)
def test_group_c_durations_sum(slug):
    p = ROOT_DIR / f"video/vn_pilot_{slug}_long/{slug}_long_explainer_spec.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    beats = data["beats"]

    total_sum = round(sum(b["duration"] for b in beats), 4)
    expected = data["total_duration_sec"]
    assert abs(total_sum - expected) < 0.01, f"{slug}: Durations sum {total_sum} != total {expected}"
