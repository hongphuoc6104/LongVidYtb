"""Tests for `vp-notebooklm-vault` (3-Vault grounding) and `fact_grounding_linter`."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.fact_grounding_linter import lint_fact_grounding
from tools.notebooklm_vault import (
    NotebookLMBridge,
    export_chanh_niem_ke_manifest_seed,
    export_research_architect_sources,
    format_youtube_sources_block,
    parse_notebooklm_markdown_to_fact_vault,
    render_channel_master_prompts,
    validate_fact_vault,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
VAULT_CLI = SYS_DIR / "tools" / "notebooklm_vault.py"
LINTER_CLI = SYS_DIR / "tools" / "fact_grounding_linter.py"

SAMPLE_VN_NOTES = """
# Research Notes

## 1. Key facts
- Vào 3 giờ sáng, tuyến thượng thận bắt đầu tăng tiết cortisol tự nhiên thêm khoảng 25 phần trăm để chuẩn bị đánh thức cơ thể [NIH Endocrine Review].
- Nếu bạn mất ngủ liên tiếp 5 đêm, nồng độ cortisol buổi tối cao hơn người ngủ đủ giấc tới 37 phần trăm [Harvard Health].
- Nhịp sinh học chuẩn kéo dài trung bình 24.2 giờ nếu không có ánh sáng mặt trời điều chỉnh [Nature Reviews Neuroscience].
- Thiếu ngủ mãn tính làm giảm khả năng ghi nhớ ngắn hạn 40 phần trăm chỉ sau một tuần [WHO Sleep Report].
- Một nghiên cứu thử nghiệm gợi ý uống trà hoa cúc giúp giảm 912 điểm stress (report-only) [Summary Report].

## 2. Most surprising hook fact
Chính hormone giúp bạn tỉnh táo vào buổi sáng lại là thứ khiến tim đập thình thịch lúc 3 giờ sáng khi bạn căng thẳng.

## 3. How it works
Khi não bộ nhận nhầm áp lực công việc là mối đe dọa sinh tồn, vùng hạ đồi phát tín hiệu qua tuyến yên xuống tuyến thượng thận để bơm cortisol sớm hơn 2 tiếng.

## 4. Analogies & Vietnam Micro-Bridges
- Ở Việt Nam, tình trạng này giống như việc người gác cổng chung cư tại Hà Nội bật chuông báo cháy lúc 3 giờ sáng chỉ vì thấy một làn khói bếp từ căn hộ tầng dưới.
- Tưởng tượng ví tiền chỉ còn 50 nghìn đồng nhưng đồng hồ báo thức vẫn giục bạn chạy ra chợ sớm hai tiếng.

## 5. Visual appearance notes
Cross-section of glowing amber adrenal gland and neural signal pulse in deep navy biomedical studio space, clean negative space.

## 6. Common misconception and correction
Nhiều người nghĩ thức giấc lúc 3 giờ sáng là do yếu thận; thực tế đó là đỉnh cortisol sớm bị lệch pha do stress kéo dài.

## 7. Spoken numbers & Pronunciation Glossary
- Cortisol -> Co ti dôn
- NIH -> Viện Y Tế Quốc Gia Hoa Kỳ

## 8. Report-only & Conflicts/Gaps
- Claim 912 điểm stress chỉ xuất hiện ở bản tóm tắt report-only, chưa có nguồn gốc xác nhận.
"""


def test_parse_and_validate_fact_vault_quarantines_report_only() -> None:
    vault = parse_notebooklm_markdown_to_fact_vault(
        md_text=SAMPLE_VN_NOTES,
        topic="Tại sao bạn hay tỉnh giấc lúc 3 giờ sáng",
        channel_id="co_the_ke",
        format_profile="short_9x16",
    )
    assert vault["research_mode"] == "fast_research"
    assert len(vault["verified_facts"]) == 4
    assert len(vault["report_only_claims"]) >= 1
    assert "Cortisol" in vault["pronunciation_glossary"]
    assert len(vault["vietnam_micro_bridges"]) >= 1

    val = validate_fact_vault(vault, min_verified_facts=4)
    assert val["valid"] is True
    assert val["verified_fact_count"] == 4
    assert val["report_only_count"] >= 1

    # Contaminating verified_facts with a report-only item must fail validation
    bad_vault = json.loads(json.dumps(vault))
    bad_vault["verified_facts"].append({
        "id": "F99",
        "claim_vi": "Uống trà giảm 912 điểm stress",
        "source_name": "report-only",
        "status": "report-only",
    })
    bad_val = validate_fact_vault(bad_vault, min_verified_facts=4)
    assert bad_val["valid"] is False
    assert any("REPORT_ONLY_IN_VERIFIED" in e for e in bad_val["errors"])


def test_master_prompts_and_exports_across_channels() -> None:
    for ch_id in ("co_the_ke", "luat_doi_thuong", "chanh_niem_ke", "en_choke_point", "tam_tinh_dem"):
        prompts = render_channel_master_prompts(ch_id, "Test Topic", format_profile="long_16x9")
        assert "Deep Research" in prompts["notebook_3_research_box"]
        assert "report-only" in prompts["notebook_3_chat_prompt"]
        assert "Veo 3.1 Lite" in prompts["notebook_2_flow_rules_prompt"]

    cnk_notes = SAMPLE_VN_NOTES + "\n## 9. Chronicle GIS Anchors\n- Chernobyl Reactor 4: 30.0992, 51.3895\n"
    cnk_vault = parse_notebooklm_markdown_to_fact_vault(cnk_notes, "Chernobyl", "chanh_niem_ke", "long_16x9")
    seed = export_chanh_niem_ke_manifest_seed(cnk_vault)
    assert len(seed["pin_coordinates"]) == 1
    assert abs(seed["pin_coordinates"][0]["lon"] - 30.0992) < 1e-4

    sources = export_research_architect_sources(cnk_vault)
    assert len(sources) >= 3
    yt_block = format_youtube_sources_block(cnk_vault, language="vi")
    assert "Nguồn tham khảo:" in yt_block
    assert "NIH Endocrine Review" in yt_block
    assert "report-only" not in yt_block.lower()


def test_fact_grounding_linter_blocks_report_only_ungrounded_numbers_and_unsafe_claims() -> None:
    vault = parse_notebooklm_markdown_to_fact_vault(
        md_text=SAMPLE_VN_NOTES,
        topic="Cortisol 3 giờ sáng",
        channel_id="co_the_ke",
        format_profile="short_9x16",
    )

    good_script = {
        "channel_id": "co_the_ke",
        "scenes": [
            {"id": "SC01", "narration": "Đúng 3 giờ sáng mắt bạn mở trừng trừng như bị ai bật công tắc."},
            {"id": "SC02", "narration": "Ở Hà Nội cảnh này giống hệt bác bảo vệ bật chuông báo cháy vì làn khói bếp."},
            {"id": "SC03", "narration": "Tuyến thượng thận bơm cortisol tăng thêm 25 phần trăm và làm trí nhớ giảm 40 phần trăm."},
        ],
    }
    good_res = lint_fact_grounding(good_script, vault, channel_id="co_the_ke", strict=True)
    assert good_res["valid"] is True, good_res["errors"]
    assert good_res["skipped_report_only_count"] >= 1

    leaked_script = {
        "channel_id": "co_the_ke",
        "scenes": [
            {"id": "SC01", "narration": "Một nghiên cứu báo cáo uống trà giúp giảm 912 điểm stress ngay lập tức."},
        ],
    }
    leaked_res = lint_fact_grounding(leaked_script, vault, channel_id="co_the_ke", strict=True)
    assert leaked_res["valid"] is False
    assert any("REPORT_ONLY_LEAKAGE" in e for e in leaked_res["errors"])

    ungrounded_script = {
        "channel_id": "co_the_ke",
        "scenes": [
            {"id": "SC01", "narration": "Khoảng 784 phần trăm người trưởng thành gặp hiện tượng này."},
        ],
    }
    strict_res = lint_fact_grounding(ungrounded_script, vault, channel_id="co_the_ke", strict=True)
    assert strict_res["valid"] is False
    assert any("UNGROUNDED_NUMBERS" in e for e in strict_res["errors"])

    medical_claim_script = {
        "channel_id": "co_the_ke",
        "scenes": [
            {"id": "SC01", "narration": "Mẹo này sẽ chữa khỏi hoàn toàn chứng mất ngủ và thay thế thuốc."},
        ],
    }
    med_res = lint_fact_grounding(medical_claim_script, vault, channel_id="co_the_ke", strict=False)
    assert med_res["valid"] is False
    assert any("MEDICAL_CLAIM_FORBIDDEN" in e for e in med_res["errors"])


def test_bridge_capabilities_and_cli_roundtrip(tmp_path: Path) -> None:
    caps = NotebookLMBridge.detect_capabilities()
    assert caps["web_import_available"] is True
    assert caps["offline_fallback_available"] is True
    assert "recommended_mode" in caps

    notes_file = tmp_path / "notes.md"
    notes_file.write_text(SAMPLE_VN_NOTES, encoding="utf-8")
    vault_file = tmp_path / "fact_vault.json"
    script_file = tmp_path / "content.json"
    script_file.write_text(
        json.dumps({
            "channel_id": "co_the_ke",
            "scenes": [{"id": "SC01", "narration": "Lúc 3 giờ sáng cortisol tăng 25 phần trăm và trí nhớ giảm 40 phần trăm."}],
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    imp = subprocess.run(
        [
            sys.executable, str(VAULT_CLI), "import-notes",
            "--channel", "co_the_ke", "--topic", "Cortisol", "--format", "short_9x16",
            "--input", str(notes_file), "--output", str(vault_file),
        ],
        capture_output=True, text=True, check=False,
    )
    assert imp.returncode == 0, imp.stderr + imp.stdout
    assert vault_file.is_file()

    lint = subprocess.run(
        [
            sys.executable, str(LINTER_CLI),
            "--content", str(script_file), "--vault", str(vault_file),
            "--channel", "co_the_ke", "--strict",
        ],
        capture_output=True, text=True, check=False,
    )
    assert lint.returncode == 0, lint.stderr + lint.stdout


def test_serialized_detail_short_prompt_and_fact_threshold() -> None:
    prompts = render_channel_master_prompts(
        channel_id="su_ke_lai",
        topic="Chiến dịch Tết Kỷ Dậu 1789",
        format_profile="serialized_detail_short",
    )
    assert "8-14" in prompts["notebook_3_chat_prompt"]
    assert "Tập 1 / Tập 2 / Tập 3" in prompts["notebook_3_chat_prompt"]
    assert "chronological" in prompts["notebook_1_pattern_prompt"]

    vault = parse_notebooklm_markdown_to_fact_vault(
        md_text=SAMPLE_VN_NOTES,
        topic="Đêm Hà Hồi 1789",
        channel_id="su_ke_lai",
        format_profile="serialized_detail_short",
    )
    assert vault["research_mode"] == "deep_research"
    # Fewer than 8 verified facts should fail serialized_detail_short default gate
    val_low = validate_fact_vault(vault)
    assert val_low["valid"] is False
    assert val_low["required_min_facts"] == 8
