#!/usr/bin/env python3
"""Test Suite: Verification of Conveyor Stations and QA Invariants."""

from pathlib import Path
import tempfile

from conveyor.ast_checker import check_test_suite_integrity, inspect_test_file
from conveyor.critique_html import generate_critique_html, scan_critique
from conveyor.playbook_validator import validate_playbook


def test_station_1_critique_scan():
    """Verify that critique scanner executes cleanly and generates valid HTML."""
    repo_root = Path(__file__).resolve().parents[2]
    passed, summary = scan_critique(repo_root)
    assert "checks" in summary, "Expected 'checks' list in critique summary"
    assert len(summary["checks"]) >= 3, "Expected at least 3 checks in critique summary"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_html = Path(tmp_dir) / "critique_test.html"
        generate_critique_html(summary, tmp_html)
        assert tmp_html.is_file(), "Critique HTML report was not created"
        html_text = tmp_html.read_text(encoding="utf-8")
        assert "Trạm 1: Phản Biện" in html_text, "Report header missing in HTML"
        assert "<table" in html_text, "Table missing in HTML"


def test_station_2_ast_integrity_detection():
    """Verify AST checker catches assertion-less fake tests and accepts valid tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_test_file = Path(tmp_dir) / "test_fake.py"
        # Test file with 1 empty test and 1 valid test
        fake_test_file.write_text(
            "def test_empty():\n"
            "    pass\n\n"
            "def test_valid():\n"
            "    assert 1 == 1\n",
            encoding="utf-8",
        )

        violations = inspect_test_file(fake_test_file)
        assert len(violations) == 1, f"Expected 1 violation, got {len(violations)}"
        assert violations[0]["function"] == "test_empty", f"Unexpected function flagged: {violations[0]}"

        # Scan folder using check_test_suite_integrity
        ok, report = check_test_suite_integrity([fake_test_file])
        assert not ok, "Integrity check should have failed on fake test"
        assert report["violations_count"] == 1, "Expected exactly 1 violation count"


def test_station_2_ast_integrity_on_real_suite():
    """Verify that our current newly written test files pass 100% AST assertion integrity."""
    repo_root = Path(__file__).resolve().parents[2]
    target_tests = [
        repo_root / "sys/tests/test_tools_readiness.py",
        repo_root / "sys/tests/test_pipeline_stations.py",
        repo_root / "sys/tests/test_research_story_architect.py",
        repo_root / "sys/tests/test_script_cadence_checker.py",
        repo_root / "sys/tests/test_format_separation.py",
    ]
    ok, report = check_test_suite_integrity(target_tests)
    assert ok, f"Expected active assertions in all test functions, violations: {report['violations']}"
    assert report["violations_count"] == 0, "No violations allowed in official conveyor test suite"


def test_station_3_playbook_validator_valid():
    """Verify that project PLAYBOOK.md strictly conforms to all 6 mandatory fields."""
    repo_root = Path(__file__).resolve().parents[2]
    playbook_file = repo_root / "PLAYBOOK.md"
    assert playbook_file.is_file(), "PLAYBOOK.md must exist in root"

    ok, report = validate_playbook(playbook_file)
    assert ok, f"PLAYBOOK.md failed schema validation: {report.get('violations')}"
    assert report["valid_entries"] >= 1, "At least 1 valid lesson entry required in PLAYBOOK.md"


def test_station_3_playbook_validator_catches_missing_fields():
    """Verify that playbook validator flags entries missing any of the 6 fields."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        bad_playbook = Path(tmp_dir) / "BAD_PLAYBOOK.md"
        bad_playbook.write_text(
            "# Playbook\n\n"
            "### [ERR-001] Missing fields test\n"
            "- **Triệu chứng:** Error happened\n"
            "- **Nguyên nhân cốt lõi:** Bug\n",
            encoding="utf-8",
        )

        ok, report = validate_playbook(bad_playbook)
        assert not ok, "Validation should have failed for incomplete entry"
        assert len(report["violations"]) == 1, "Expected 1 violation"
        missing = report["violations"][0]["missing_fields"]
        assert any("Tái hiện E2E" in m for m in missing), "Should report missing Reproduction Path"
        assert any("Quy tắc phòng ngừa vàng" in m for m in missing), "Should report missing Golden Rule"
