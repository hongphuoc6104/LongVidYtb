"""Unit tests for V2 Script Bundle Exporter (export_v2_bundle.py)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.export_v2_bundle import (  # noqa: E402
    compute_bundle_statistics,
    export_v2_bundle,
    run_cta_lint,
    validate_v2_spec,
)

SAMPLE_SHORT_V2 = {
    "job_id": "nao-luoi-week1-9x16-v2",
    "format_profile": "short_9x16",
    "parent_long_id": "nao-luoi-week1-16x9",
    "topic": "Vì sao càng tự trách bản thân bạn lại càng trì hoãn?",
    "goal": "Giải mã cơ chế phòng vệ tâm lý và trao giải pháp",
    "audience": "Gen Z và người trẻ đi làm",
    "min_duration": 25.0,
    "max_duration": 75.0,
    "packaging": {
        "youtube_title": "Vì Sao Càng Tự Trách Bạn Càng Trì Hoãn?",
        "visual_hook": "Vì sao bạn nằm lướt điện thoại cả tiếng đồng hồ dù mai thi?",
        "text_overlay": "BẪY TỰ TRÁCH",
        "contrast_pair": "Tự trách mệt mỏi vs Tự trắc ẩn hành động",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["trì hoãn", "tự trách", "tâm lý học"],
    },
    "sources": [
        {
            "id": "SRC01",
            "title": "Bedtime Procrastination Study",
            "reference": "Frontiers in Psychology, 2014",
            "facts": ["Trì hoãn là điều hòa cảm xúc ngắn hạn."],
        }
    ],
    "cta_plan": {
        "bridge": "Vì sao não lại đòi thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười.",
        "close": "Lưu lại và gửi cho đứa bạn hay thức khuya chung với bạn nhé?",
        "endcard_text": "NÃO LƯỜI",
        "mid_cta": None,
    },
    "scenes": [
        {
            "title": "Cú tát thức khuya",
            "setting": "Góc bàn học đêm với ánh đèn bàn le lói",
            "tone": "narrative_warm",
            "phase": "lived_friction",
            "source_ids": ["SRC01"],
            "claim_facts": [],
            "rows": [
                {
                    "narration": "Vì sao bạn nằm lướt điện thoại cả tiếng đồng hồ dù mai thi? Nhưng điều bất ngờ là, bạn càng tự mắng thì ngón tay lại càng không thể dừng lại.",
                    "visuals": [
                        {
                            "id": "SC01_I1",
                            "anchor": "Vì sao bạn nằm",
                            "spec": "full_scene:CH01|Stickman lying on bed with glowing smartphone screen in dark room",
                            "tempo": "fast",
                            "emphasis_text": "KHÔNG THỂ DỪNG",
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC01_I2",
                            "anchor": "Nhưng điều bất ngờ",
                            "spec": "variation:CH01|Stickman holding head in frustration with clock ticking midnight",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": "SC01_I1",
                            "focus": None,
                        },
                        {
                            "id": "SC01_I3",
                            "anchor": "bạn càng tự mắng",
                            "spec": "concept_metaphor:CH01|Ticking midnight clock with red warning glow",
                            "tempo": "fast",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC01_I4",
                            "anchor": "ngón tay lại càng",
                            "spec": "cutaway_detail:CH01|Close up of thumb scrolling endlessly on glowing phone",
                            "tempo": "fast",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                    ],
                }
            ],
        },
        {
            "title": "Cơ chế tâm lý",
            "setting": "Khung nền trắng tối giản minh họa não bộ",
            "tone": "analytical",
            "phase": "mechanism_reveal",
            "source_ids": ["SRC01"],
            "claim_facts": [],
            "rows": [
                {
                    "narration": "Bộ não đang bảo vệ bạn khỏi cảm giác căng thẳng tức thì của công việc. Nó chủ động chọn dopamine ngắn hạn để xoa dịu nỗi sợ thất bại đang âm ỉ.",
                    "visuals": [
                        {
                            "id": "SC02_I1",
                            "anchor": "Bộ não đang",
                            "spec": "concept_metaphor:CH01|Doodle diagram of brain shielding itself from red alarm bells",
                            "tempo": "slow",
                            "emphasis_text": None,
                            "reuse_image": "v1_SC02_I1",
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC02_I2",
                            "anchor": "khỏi cảm giác",
                            "spec": "variation:CH01|Brain sweating under heavy pressure stone",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": "SC01_I1",
                            "focus": None,
                        },
                        {
                            "id": "SC02_I3",
                            "anchor": "Nó chủ động chọn",
                            "spec": "macro_prop:CH01|Sparkling candy dopamine icon held by stickman",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC02_I4",
                            "anchor": "để xoa dịu",
                            "spec": "cutaway_detail:CH01|Stickman smiling briefly with warm coffee cup",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                    ],
                }
            ],
        },
        {
            "title": "Cầu nối và kết thúc",
            "setting": "Phông nền ấm áp kết nối",
            "tone": "reflective",
            "phase": "resolution",
            "source_ids": [],
            "claim_facts": [],
            "rows": [
                {
                    "narration": "Vì sao não lại đòi thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười. Lưu lại và gửi cho đứa bạn hay thức khuya chung với bạn nhé?",
                    "visuals": [
                        {
                            "id": "SC03_I1",
                            "anchor": "Vì sao não lại",
                            "spec": "cutaway_detail:CH01|Stickman pointing towards YouTube video preview frame",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC03_I2",
                            "anchor": "Bản dài mình",
                            "spec": "full_scene:CH01|Full explainer thumbnail preview card with play button",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC03_I3",
                            "anchor": "Lưu lại và gửi",
                            "spec": "macro_prop:CH01|Paper airplane sending message to friend",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC03_I4",
                            "anchor": "hay thức khuya",
                            "spec": "endcard",
                            "tempo": "hold",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                    ],
                }
            ],
        },
    ],
}

SAMPLE_LONG_V2 = {
    "job_id": "nao-luoi-week1-16x9",
    "format_profile": "long_16x9",
    "topic": "Tại sao càng tự trách bản thân bạn lại càng trì hoãn?",
    "goal": "Phân tích khoa học thần kinh về sự trì hoãn và cung cấp kỹ thuật vượt qua",
    "audience": "Gen Z và người trẻ đi làm",
    "min_duration": 120.0,
    "max_duration": 600.0,
    "packaging": {
        "youtube_title": "Càng Tự Trách Bạn Càng Trì Hoãn?",
        "visual_hook": "Vì sao bạn nằm lướt điện thoại dù bài thi sáng mai chưa ôn?",
        "text_overlay": "BẪY TỰ TRÁCH",
        "contrast_pair": "Tự trừng phạt vs Tự trắc ẩn",
        "funnel_tier": "tier_1_broad",
        "seo_keywords": ["trì hoãn", "tự trách", "tâm lý"],
    },
    "sources": [
        {
            "id": "SRC01",
            "title": "Study on Self-Compassion and Procrastination",
            "reference": "Psychology Science, 2012",
            "facts": ["Tự trắc ẩn giảm căng thẳng và tăng động lực."],
        }
    ],
    "cta_plan": {
        "bridge": None,
        "mid_cta": "Nếu thấy điều này quen thuộc, lưu lại để nghe kỹ giải pháp ở phần sau.",
        "close": "Nếu video này có ích, gửi cho người bạn thân đang cùng vượt qua áp lực.",
        "endcard_text": "NÃO LƯỜI",
    },
    "scenes": [
        {
            "title": "Bàn học đêm",
            "setting": "Góc bàn học đêm với ánh đèn",
            "tone": "narrative_warm",
            "phase": "lived_friction",
            "source_ids": ["SRC01"],
            "claim_facts": [],
            "rows": [
                {
                    "narration": "Vì sao bạn nằm lướt điện thoại cả tiếng đồng hồ dù bài chưa xong? Nhưng điều bất ngờ là bạn càng tự mắng thì tay lại càng không dừng.",
                    "visuals": [
                        {
                            "id": "SC01_I1",
                            "anchor": "Vì sao bạn nằm",
                            "spec": "full_scene:CH01|Stickman at dark desk under yellow lamp",
                            "tempo": "normal",
                            "emphasis_text": "TỰ MẮNG",
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        }
                    ],
                }
            ],
        },
        {
            "title": "Khoa học hạch hạnh nhân",
            "setting": "Minh họa hệ thần kinh trung ương",
            "tone": "analytical",
            "phase": "mechanism_reveal",
            "source_ids": ["SRC01"],
            "claim_facts": [],
            "rows": [
                {
                    "narration": "Hạch hạnh nhân phát tín hiệu báo động đỏ trước sự đe dọa thất bại. Nếu thấy điều này quen thuộc, lưu lại để nghe kỹ giải pháp ở phần sau.",
                    "visuals": [
                        {
                            "id": "SC02_I1",
                            "anchor": "Hạch hạnh nhân",
                            "spec": "concept_metaphor:CH01|Amygdala with flashing red siren beacon",
                            "tempo": "slow",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC02_I2",
                            "anchor": "Nếu thấy điều này",
                            "spec": "variation:CH01|Brain calming down with deep breath icon",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": "SC01_I1",
                            "focus": None,
                        },
                    ],
                }
            ],
        },
        {
            "title": "Đúc kết và hành động",
            "setting": "Không gian thư thái buổi sớm",
            "tone": "reflective",
            "phase": "resolution",
            "source_ids": [],
            "claim_facts": [],
            "rows": [
                {
                    "narration": "Hãy tha thứ cho bản thân trước khi bắt đầu nhiệm vụ nhỏ hai phút. Nếu video này có ích, gửi cho người bạn thân đang cùng vượt qua áp lực.",
                    "visuals": [
                        {
                            "id": "SC03_I1",
                            "anchor": "Hãy tha thứ",
                            "spec": "cutaway_detail:CH01|Two stickmen encouraging each other",
                            "tempo": "normal",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                        {
                            "id": "SC03_I2",
                            "anchor": "Nếu video này",
                            "spec": "endcard",
                            "tempo": "hold",
                            "emphasis_text": None,
                            "reuse_image": None,
                            "based_on": None,
                            "focus": None,
                        },
                    ],
                }
            ],
        },
    ],
}


def _create_mock_channel_workspace(tmp_path: Path, channel_id: str = "nao_luoi") -> Path:
    ws = tmp_path / f"channel-{channel_id}"
    ch_dir = ws / "sys" / "channels" / channel_id
    ch_dir.mkdir(parents=True)

    script_content = f"""
SHORT_V2 = {repr(SAMPLE_SHORT_V2)}
LONG_V2 = {repr(SAMPLE_LONG_V2)}
"""
    (ch_dir / "script_v2.py").write_text(script_content, encoding="utf-8")
    return ws


def test_validate_v2_spec_valid_and_invalid() -> None:
    errors = validate_v2_spec(SAMPLE_SHORT_V2, "nao_luoi")
    assert errors == []

    # Invalid spec missing parent_long_id on short
    invalid_short = dict(SAMPLE_SHORT_V2)
    invalid_short.pop("parent_long_id")
    errors2 = validate_v2_spec(invalid_short, "nao_luoi")
    assert any("parent_long_id" in e for e in errors2)

    # Invalid spec missing close on long
    invalid_long = dict(SAMPLE_LONG_V2)
    invalid_long["cta_plan"] = {"mid_cta": "Lưu lại"}
    errors3 = validate_v2_spec(invalid_long, "nao_luoi")
    assert any("close" in e.lower() for e in errors3)


def test_cta_linter_and_banned_phrases() -> None:
    violations = run_cta_lint(SAMPLE_SHORT_V2, "nao_luoi")
    assert violations == []

    bad_spec = dict(SAMPLE_SHORT_V2)
    bad_spec["cta_plan"] = dict(SAMPLE_SHORT_V2["cta_plan"])
    bad_spec["cta_plan"]["close"] = "Đừng quên like và chia sẻ video này."
    violations2 = run_cta_lint(bad_spec, "nao_luoi")
    assert any("BANNED_CTA_PHRASE" in v for v in violations2)


def test_compute_bundle_statistics() -> None:
    from tools.export_v2_bundle import topic_from_v2_spec
    topic = topic_from_v2_spec(SAMPLE_SHORT_V2, "nao_luoi")
    stats = compute_bundle_statistics(SAMPLE_SHORT_V2, topic)

    assert stats["beats"] == 12
    assert stats["flow_images_to_generate"] == 10
    assert stats["reused_images"] == 2
    assert stats["emphasis_ratio"] == 0.083
    assert stats["estimated_duration"] > 0.0


def test_export_v2_bundle_short_e2e(tmp_path: Path) -> None:
    ws = _create_mock_channel_workspace(tmp_path, "nao_luoi")
    out_dir = ws / "sys" / "runs" / SAMPLE_SHORT_V2["job_id"]

    summary = export_v2_bundle(
        channel_id="nao_luoi",
        format_profile="short_9x16",
        out_dir=out_dir,
        root_dir=ws,
    )

    assert summary["channel_id"] == "nao_luoi"
    assert summary["format"] == "short_9x16"
    assert summary["job_id"] == "nao-luoi-week1-9x16-v2"
    assert summary["beats"] == 12
    assert summary["flow_images_to_generate"] == 10
    assert summary["reused_images"] == 2
    assert summary["hook_score"] >= 70
    assert summary["cadence_status"] == "PASS"

    assert (out_dir / "brief.json").exists()
    assert (out_dir / "content.json").exists()
    assert (out_dir / "script.json").exists()
    assert (out_dir / "cadence_report.json").exists()


def test_export_v2_bundle_long_e2e(tmp_path: Path) -> None:
    ws = _create_mock_channel_workspace(tmp_path, "nao_luoi")
    out_dir = ws / "sys" / "runs" / SAMPLE_LONG_V2["job_id"]

    summary = export_v2_bundle(
        channel_id="nao_luoi",
        format_profile="long_16x9",
        out_dir=out_dir,
        root_dir=ws,
    )

    assert summary["channel_id"] == "nao_luoi"
    assert summary["format"] == "long_16x9"
    assert summary["job_id"] == "nao-luoi-week1-16x9"
    assert summary["beats"] == 5
    assert summary["hook_score"] >= 70
    assert (out_dir / "content.json").exists()


def test_export_v2_bundle_rejects_low_hook_score(tmp_path: Path) -> None:
    ws = tmp_path / "channel-nao-luoi"
    ch_dir = ws / "sys" / "channels" / "nao_luoi"
    ch_dir.mkdir(parents=True)

    bad_hook_spec = dict(SAMPLE_SHORT_V2)
    bad_hook_spec["scenes"] = [
        {
            "title": "Báo cáo số liệu",
            "setting": "Văn phòng tối giản",
            "rows": [
                {
                    "narration": "Báo cáo tổng hợp số liệu thông thường được lưu trữ trong danh mục định kỳ này.",
                    "visuals": [
                        {
                            "id": "SC01_I1",
                            "anchor": "Báo cáo tổng hợp",
                            "spec": "full_scene:CH01|Office desk with reports",
                            "tempo": "normal",
                        },
                        {
                            "id": "SC01_I2",
                            "anchor": "trong danh mục",
                            "spec": "cutaway_detail:CH01|Documents list",
                            "tempo": "normal",
                        },
                    ],
                }
            ],
        },
        {
            "title": "Chi tiết thống kê",
            "setting": "Bảng dữ liệu",
            "rows": [
                {
                    "narration": "Mỗi bảng biểu bao gồm các thông số cơ bản về quy trình hoạt động hàng ngày.",
                    "visuals": [
                        {
                            "id": "SC02_I1",
                            "anchor": "Mỗi bảng biểu",
                            "spec": "visual_diagram:CH01|Simple data table",
                            "tempo": "normal",
                        },
                        {
                            "id": "SC02_I2",
                            "anchor": "về quy trình",
                            "spec": "cutaway_detail:CH01|Workflow arrows",
                            "tempo": "normal",
                        },
                    ],
                }
            ],
        },
        {
            "title": "Kết luận",
            "setting": "Phòng làm việc",
            "rows": [
                {
                    "narration": "Vì sao não lại đòi thời gian kiểu này? Bản dài mình mổ xẻ trên YouTube Não Lười. Lưu lại và gửi cho đứa bạn hay thức khuya chung với bạn nhé?",
                    "visuals": [
                        {
                            "id": "SC03_I1",
                            "anchor": "Vì sao não lại",
                            "spec": "cutaway_detail:CH01|Desk",
                            "tempo": "normal",
                        },
                        {
                            "id": "SC03_I2",
                            "anchor": "Lưu lại và gửi",
                            "spec": "endcard",
                            "tempo": "hold",
                        },
                    ],
                }
            ],
        },
    ]
    (ch_dir / "script_v2.py").write_text(f"SHORT_V2 = {repr(bad_hook_spec)}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Hook score .* below required threshold 70"):
        export_v2_bundle(
            channel_id="nao_luoi",
            format_profile="short_9x16",
            root_dir=ws,
        )
