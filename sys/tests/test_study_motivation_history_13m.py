from pathlib import Path
import json
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
if str(SYS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(SYS_DIR / "tools"))

from build_study_motivation_history_13m import (
    CHAPTER_METADATA,
    RAW_SCENES_DATA,
    create_study_motivation_13m_topic,
    get_academic_sources,
    get_required_points,
)
from content_contract import validate_brief, validate_content
from script_cadence_checker import ScriptCadenceChecker, count_syllables


def test_study_motivation_chapter_and_scene_counts():
    assert len(CHAPTER_METADATA) == 8
    assert len(RAW_SCENES_DATA) == 48

    total_duration = sum(ch["duration"] for ch in CHAPTER_METADATA)
    assert total_duration == 780.0

    scene_durations = sum(sc["duration"] for sc in RAW_SCENES_DATA)
    assert scene_durations == 780.0


def test_study_motivation_sources_and_facts_protocol():
    sources = get_academic_sources()
    assert len(sources) == 8

    total_facts = 0
    for src in sources:
        assert src["id"].startswith("SRC0")
        assert len(src["facts"]) >= 1
        for f in src["facts"]:
            total_facts += 1
            syl = count_syllables(f)
            assert syl <= 20, f"Fact '{f}' exceeds 20 syllables: {syl}"
    assert total_facts == 16


def test_study_motivation_claims_embedded_verbatim():
    facts = []
    for src in get_academic_sources():
        facts.extend(src["facts"])

    scene_by_id = {sc["scene_id"]: sc for sc in RAW_SCENES_DATA}
    claimed_facts = []
    for sc in RAW_SCENES_DATA:
        if sc.get("claim"):
            quote, src_id, fact = sc["claim"]
            assert quote in sc["narration"]
            assert quote == fact
            claimed_facts.append(fact)

    assert len(claimed_facts) == 16
    assert set(claimed_facts) == set(facts)


def test_study_motivation_cadence_drift():
    checker = ScriptCadenceChecker(nominal_rate=4.0)
    content_path = Path("sys/runs/study-motivation-16x9-13m/content.json")
    assert content_path.is_file(), "content.json must exist"

    report = checker.check_file(content_path)

    assert report["total_scenes"] == 48
    assert report["total_duration"] == 780.0
    assert report["max_drift"] <= 0.25
    assert report["warnings_count"] == 0
    assert report["status"] == "PASS"


def test_study_motivation_schema_contracts():
    root = "sys"
    brief_path = Path("sys/runs/study-motivation-16x9-13m/brief.json")
    content_path = Path("sys/runs/study-motivation-16x9-13m/content.json")
    assert brief_path.is_file()
    assert content_path.is_file()

    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    content = json.loads(content_path.read_text(encoding="utf-8"))

    validate_brief(root, brief)
    validate_content(root, brief, content["brief_revision"], content["brief_hash"], content)


def test_study_motivation_bundle_manifest_and_templates_contract():
    bundle_dir = ROOT / "sys" / "exports" / "study_motivation_bundle"
    manifest_path = bundle_dir / "manifest" / "manifest_study_motivation_8ch.json"
    assert manifest_path.is_file(), "manifest_study_motivation_8ch.json must exist"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["project"] == "study-motivation-16x9-13m"
    assert manifest["total_chapters"] == 8
    assert manifest["total_scenes"] == 48
    assert len(manifest["shots"]) >= 280
    assert manifest["total_duration_seconds"] == 780.0

    for s in manifest["shots"]:
        assert "target_filename" in s and s["target_filename"], f"Missing target_filename in {s}"
        assert "filename" in s and s["filename"], f"Missing filename in {s}"
        assert "prompt" in s and s["prompt"], f"Missing prompt in {s}"
        assert "effect" in s and s["effect"], f"Missing effect in {s}"
        assert 0.6 <= s["hold_duration"] <= 3.80, f"Shot hold out of range: {s['hold_duration']}"

    templates_dir = bundle_dir / "templates"
    for ch in range(1, 9):
        tpl_path = templates_dir / f"ch{ch}_props_template.json"
        assert tpl_path.is_file(), f"Missing template {tpl_path}"
        tpl = json.loads(tpl_path.read_text(encoding="utf-8"))
        assert tpl["aspect_ratio"] == "16:9"
        assert tpl["primary_language"] == "vi"
        assert tpl["fps"] == 30
        assert tpl["width"] == 1920
        assert tpl["height"] == 1080
        assert tpl["outputs"][0]["subtitles"] is False
        assert tpl["outputs"][0]["language"] == "vi"
        scenes = tpl["tracks"]["vi"]["scenesByAspect"]["16:9"]
        assert len(scenes) == 6
        for sc in scenes:
            assert "start" in sc and "end" in sc and "images" in sc
            sc_dur = round(float(sc["end"]) - float(sc["start"]), 3)
            imgs = sc["images"]
            assert len(imgs) >= 1
            prev_eff = None
            for i, im in enumerate(imgs):
                t0 = float(im["at"])
                t1 = float(imgs[i + 1]["at"]) if i + 1 < len(imgs) else sc_dur
                hold = round(t1 - t0, 3)
                assert 0.6 <= hold <= 3.80, f"Ch{ch} {sc['id']} hold {hold}s out of bounds"
                eff = im["effect"]
                assert eff != prev_eff, f"Consecutive duplicate effect {eff} in Ch{ch} {sc['id']}"
                prev_eff = eff


def test_study_motivation_chrome_profile_ports_invariance():
    script_path = ROOT / "sys" / "scripts" / "setup_and_launch_3_chrome_profiles.sh"
    assert script_path.is_file()
    content = script_path.read_text(encoding="utf-8")
    assert "--remote-debugging-port=9225" in content
    assert "9225" in content
    assert "--remote-debugging-port=9222" not in content

    cdp_client_path = ROOT / "sys" / "flow_cdp" / "cdp_direct_client.py"
    assert cdp_client_path.is_file()
    cdp_content = cdp_client_path.read_text(encoding="utf-8")
    assert '"cdp_port": 9225' in cdp_content


def test_study_motivation_rebuild_templates_clean_execution():
    if str(ROOT / "sys" / "exports" / "study_motivation_bundle" / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "sys" / "exports" / "study_motivation_bundle" / "scripts"))
    from rebuild_templates import verify_templates_and_cues

    bundle_dir = ROOT / "sys" / "exports" / "study_motivation_bundle"
    stats = verify_templates_and_cues(bundle_dir)
    assert stats["total_shots"] >= 280
    assert stats["max_hold"] <= 3.80
    assert stats["max_cue_drift"] <= 0.005
