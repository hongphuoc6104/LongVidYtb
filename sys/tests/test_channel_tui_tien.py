"""Unit tests for Channel tui_tien (Túi Tiền Biết Nói).

Validates:
1. Channel registration, visual profile (ch_ledger_doodle), active channel sync.
2. Automated builder (sys/channels/tui_tien/builder.py) for short_9x16 and long_16x9.
3. Fast-short constraints: <= 6 Flow images, >= 50% VND ledger Remotion/diagram cards.
4. Schema 3.0 contracts, hook scoring (>= 70), and acoustic cadence drift (<= 0.3s).
5. Week 1 sample production bundle in sys/runs/tui-tien-week1-9x16.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools"), str(SYS_DIR / "content")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import get_channel  # noqa: E402
from channels.tui_tien.builder import (  # noqa: E402
    CHANNEL_ID,
    build_tui_tien_long,
    build_tui_tien_package,
    build_tui_tien_short,
)
from content.research_story_architect import validate_production_bundle  # noqa: E402
from tools.script_cadence_checker import count_syllables  # noqa: E402
from tools.script_hook_scorer import score_script  # noqa: E402


def test_tui_tien_profile_and_active_channel() -> None:
    ch = get_channel(CHANNEL_ID)
    assert ch.id == "tui_tien"
    assert ch.name == "Túi Tiền Biết Nói"
    assert ch.niche == "Tiền và kinh tế đời sống"
    assert ch.visual.profile_id == "ch_ledger_doodle"
    assert ch.voice == "VietNarrator"
    assert ch.speed == 1.0

    # Speed optimization assertions
    assert ch.speed_optimization is not None
    assert ch.speed_optimization.render_mode == "hybrid_motion"
    assert ch.speed_optimization.fast_short_max_images <= 6
    assert ch.speed_optimization.remotion_motion_ratio == 0.50
    assert ch.speed_optimization.spinoff_shorts_per_long == 4

    # Verify active channel file corresponds to tui_tien when inside worktree
    active_path = SYS_DIR / "channels" / "active_channel.json"
    if active_path.is_file():
        active_data = json.loads(active_path.read_text(encoding="utf-8"))
        assert active_data["channel_id"] == "tui_tien"
        assert active_data["visual_profile_id"] == "ch_ledger_doodle"
        assert active_data["channel_profile_stamp"]["sha256"] == ch.sha256

    # Verify PLAN.md exists
    plan_path = SYS_DIR / "channels" / "tui_tien" / "PLAN.md"
    assert plan_path.is_file()
    plan_text = plan_path.read_text(encoding="utf-8")
    assert "túi tiền biết nói" in plan_text.casefold()
    assert "ch_ledger_doodle" in plan_text


def test_tui_tien_short_package_generation(tmp_path: Path) -> None:
    out_dir = tmp_path / "test_short_9x16"
    res = build_tui_tien_short(output_dir=out_dir)

    assert res["valid_contracts"] is True, f"Contract errors: {res['contract_errors']}"
    assert len(res["contract_errors"]) == 0
    assert len(res["packaging_warnings"]) == 0

    # Verify fast_short constraints
    assert res["total_images"] <= 6, f"Expected <= 6 Flow images, got {res['total_images']}"
    assert res["is_fast_short_compliant"] is True
    assert res["diagram_cards"] >= 2

    # Verify hook score >= 70
    hook_score = res["hook_score"]
    assert hook_score["score"] >= 70, f"Hook score too low: {hook_score['score']}"
    assert hook_score["hook_syllables"] <= 18

    # Verify cadence max drift <= 0.3s
    cadence = res["cadence_report"]
    assert cadence.get("max_drift", 0.0) <= 0.30

    # Verify expected files exist
    assert (out_dir / "brief.json").is_file()
    assert (out_dir / "content.json").is_file()
    assert (out_dir / "script.json").is_file()
    assert (out_dir / "cadence_report.json").is_file()
    assert (out_dir / "draft" / "outline.json").is_file()
    assert (out_dir / "draft" / "content.json").is_file()

    # Verify brief metadata
    brief = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    assert brief["schema_version"] == "3.0"
    assert brief["format_profile"] == "short_9x16"
    assert brief["aspect_ratio"] == "9:16"
    assert brief["channel_profile"]["id"] == "tui_tien"
    assert len(brief["packaging"]["youtube_title"]) <= 55


def test_tui_tien_long_package_generation(tmp_path: Path) -> None:
    out_dir = tmp_path / "test_long_16x9"
    res = build_tui_tien_long(output_dir=out_dir)

    assert res["valid_contracts"] is True, f"Contract errors: {res['contract_errors']}"
    assert len(res["contract_errors"]) == 0

    brief = json.loads((out_dir / "brief.json").read_text(encoding="utf-8"))
    assert brief["schema_version"] == "3.0"
    assert brief["format_profile"] == "long_16x9"
    assert brief["aspect_ratio"] == "16:9"
    assert len(brief["packaging"]["youtube_title"]) <= 55

    # Verify 4 spin-off shorts attached
    assert "spinoff_shorts" in brief
    spinoffs = brief["spinoff_shorts"]
    assert len(spinoffs) == 4
    for sp in spinoffs:
        assert sp["format_profile"] == "short_9x16"
        assert count_syllables(sp["opening_hook"]) <= 18


def test_tui_tien_custom_topic_generation(tmp_path: Path) -> None:
    custom_topic = "Vì sao siêu thị để sữa và bánh mì ở cuối cửa hàng"
    out_dir = tmp_path / "custom_short"
    res = build_tui_tien_package(
        format_profile="short_9x16",
        topic_title=custom_topic,
        output_dir=out_dir,
    )

    assert res["valid_contracts"] is True
    assert res["total_images"] <= 6
    assert res["hook_score"]["score"] >= 70
    assert res["cadence_report"].get("max_drift", 0.0) <= 0.30

    content = json.loads((out_dir / "content.json").read_text(encoding="utf-8"))
    assert len(content["scenes"]) == 5


def test_tui_tien_week1_sample_run_artifact() -> None:
    run_dir = SYS_DIR / "runs" / "tui-tien-week1-9x16"
    if not run_dir.is_dir() or not (run_dir / "brief.json").is_file():
        build_tui_tien_short(output_dir=run_dir)
    assert run_dir.is_dir(), f"Sample run directory {run_dir} does not exist"

    brief_file = run_dir / "brief.json"
    content_file = run_dir / "content.json"
    script_file = run_dir / "script.json"
    cadence_file = run_dir / "cadence_report.json"

    assert brief_file.is_file()
    assert content_file.is_file()
    assert script_file.is_file()
    assert cadence_file.is_file()

    brief_data = json.loads(brief_file.read_text(encoding="utf-8"))
    content_data = json.loads(content_file.read_text(encoding="utf-8"))

    # Validate Schema 3.0 contracts
    valid, errors = validate_production_bundle(
        system_root=SYS_DIR,
        brief_data=brief_data,
        content_data=content_data,
        brief_revision=1,
    )
    assert valid is True, f"Validation failed: {errors}"
    assert len(errors) == 0

    # Validate fast_short image count <= 6
    total_images = sum(len(sc.get("images", [])) for sc in content_data.get("scenes", []))
    assert total_images <= 6

    # Score Hook
    narrations = [sc["narration"] for sc in content_data["scenes"]]
    hook_score = score_script(narrations, channel_id="tui_tien", format_profile="short_9x16")
    assert hook_score.score >= 70
    assert hook_score.hook_syllables <= 18

    # Opening scene pause check: zero pause in SC01
    assert "[pause:" not in content_data["scenes"][0]["narration"]
