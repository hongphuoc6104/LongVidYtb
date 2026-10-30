"""Unit tests for the 8-channel TikTok (short_9x16) + YouTube (long_16x9) system."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from analytics.channel_metrics import VideoMetric, judge, judge_all, load_metrics
from channels.registry import (
     apply_channel,
    channel_cast,
    channel_for_style,
    channel_ids,
    channel_profile_stamp,
    channels,
    get_channel,
    writer_brief,
)
from flow_prompts.compiler import find_visual_cliche
from tools.generate_channel_plans import WEEK1_BUNDLES, generate_all_plans, render_channel_plan
from tools.script_hook_scorer import score_script
from tools.setup_channel_workspaces import build_channel_config
from visual_style import render_style

EXPECTED_IDS = [
    "nao_luoi",
    "tui_tien",
    "ua_sao_vay",
    "su_ke_lai",
    "thuong_cho_kheo",
    "ho_so_ky_la",
    "co_the_ke",
    "ai_binh_dan",
]


def test_eight_channels_registered_and_complete() -> None:
    assert channel_ids() == EXPECTED_IDS
    all_channels = channels()
    assert len(all_channels) == 8
    for cid, ch in all_channels.items():
        assert ch.id == cid
        assert ch.git_branch == f"channel/{cid.replace('_', '-')}"
        assert ch.workspace_dirname == f"channel-{cid.replace('_', '-')}"
        assert ch.platform_routing == {"tiktok": "short_9x16", "youtube": "long_16x9"}
        assert ch.short_spec.format_profile == "short_9x16"
        assert ch.long_spec.format_profile == "long_16x9"
        assert ch.speed_optimization is not None
        assert ch.speed_optimization.fast_short_max_images <= 8
        assert ch.speed_optimization.spinoff_shorts_per_long >= 4
        assert any(r.format == "short" for r in ch.references)
        assert any(r.format == "long" for r in ch.references)
        assert find_visual_cliche(ch.visual.style_description) is None


def test_visual_style_recognizes_all_channel_styles() -> None:
    for ch in channels().values():
        resolved = render_style({"style": ch.visual.style_description})
        assert resolved == ch.visual.profile_id
        if ch.visual.profile_id.startswith("ch_"):
            matched = channel_for_style(ch.visual.style_description)
            assert matched is not None and matched.id == ch.id


def test_apply_channel_and_provenance_stamp() -> None:
    base_brief = {
        "schema_version": "3.0",
        "topic": "Test topic",
        "outputs": [{"aspect_ratio": "9:16", "language": "vi", "subtitles": True}],
        "seo_keywords": ["test"],
    }
    updated = apply_channel(base_brief, "tui_tien")
    stamp = channel_profile_stamp("tui_tien")
    assert updated["channel_profile"] == stamp
    assert len(stamp["sha256"]) == 64
    assert "grid-paper" in updated["style"]
    assert updated["outputs"][0]["voice"] == "VietNarrator"
    assert "taichinhcanhan" in updated["seo_keywords"]
    cast = channel_cast("tui_tien", "CH01")
    assert cast["id"] == "CH01"
    assert "glasses" in cast["appearance"]


def test_writer_brief_and_plan_generation(tmp_path: Path) -> None:
    wb = writer_brief("ai_binh_dan", "short_9x16")
    assert "channel/ai-binh-dan" in wb
    assert "screen_capture_hybrid" in wb
    assert set(WEEK1_BUNDLES.keys()) == set(EXPECTED_IDS)
    written = generate_all_plans(tmp_path)
    assert len(written) == 8
    for p in written:
        text = p.read_text(encoding="utf-8")
        assert "TikTok (`short_9x16`" in text
        assert "YouTube (`long_16x9`" in text
        assert "Tối Ưu Thời Gian Sản Xuất" in text


def test_channel_plans_committed_in_repo() -> None:
    channels_dir = Path(__file__).resolve().parents[1] / "channels"
    for cid in EXPECTED_IDS:
        plan_file = channels_dir / cid / "PLAN.md"
        assert plan_file.is_file(), f"Missing {plan_file}"
        content = render_channel_plan(get_channel(cid))
        assert len(content) > 1000


def test_script_hook_scorer_distinguishes_strong_and_weak_scripts() -> None:
    strong = [
        "Vì sao bạn luôn lướt điện thoại tới 2 giờ sáng?",
        "Nhưng điều bất ngờ là não bạn không hề nghiện màn hình.",
        "Nó đang cố đòi lại tự do sau một ngày bị ép làm việc.",
        "Hiện tượng này gọi là trả thù giờ đi ngủ.",
        "Bạn có đang bị như vậy mỗi tối không, bình luận số 1 nhé?",
    ]
    res_good = score_script(strong, "nao_luoi", "short_9x16")
    assert res_good.score >= 70
    assert not res_good.needs_rewrite

    weak = [
        "Trong nghiên cứu khoa học hiện đại có rất nhiều khái niệm phức tạp cần được phân tích kỹ lưỡng qua nhiều bước dài dòng.",
        "Chúng ta sẽ cùng tìm hiểu tổng quan lịch sử phát triển của lĩnh vực này.",
    ]
    res_bad = score_script(weak, "nao_luoi", "short_9x16")
    assert res_bad.score < 60
    assert res_bad.needs_rewrite
    assert len(res_bad.suggestions) >= 3


def test_channel_metrics_kill_iterate_scale(tmp_path: Path) -> None:
    csv_path = tmp_path / "metrics.csv"
    csv_path.write_text(
        "channel_id,platform,video_id,format,views,avg_watch_pct,completion_pct,shares,new_followers,ctr_pct\n"
        "nao_luoi,tiktok,v1,short_9x16,8500,55,48,120,45,0\n"
        "tui_tien,tiktok,v2,short_9x16,700,32,28,5,2,0\n"
        "su_ke_lai,tiktok,v3,short_9x16,120,15,10,0,0,0\n"
        "su_ke_lai,tiktok,v4,short_9x16,150,18,12,0,0,0\n"
        "su_ke_lai,tiktok,v5,short_9x16,90,14,9,0,0,0\n"
        "su_ke_lai,tiktok,v6,short_9x16,110,16,11,0,0,0\n"
        "su_ke_lai,tiktok,v7,short_9x16,130,17,10,0,0,0\n"
        "su_ke_lai,tiktok,v8,short_9x16,140,15,11,0,0,0\n",
        encoding="utf-8",
    )
    rows = load_metrics(csv_path)
    verdicts = {v.channel_id: v for v in judge_all(rows)}
    assert verdicts["nao_luoi"].decision == "scale"
    assert verdicts["tui_tien"].decision == "iterate"
    assert verdicts["su_ke_lai"].decision == "kill"

    long_win = judge(
        "ho_so_ky_la",
        [VideoMetric("ho_so_ky_la", "youtube", "yt1", "long_16x9", views=2000, avg_watch_pct=42.0, ctr_pct=5.5)],
    )
    assert long_win.decision == "scale"


def test_build_channel_config_structure() -> None:
    cfg = build_channel_config(get_channel("ua_sao_vay"))
    assert cfg["git_branch"] == "channel/ua-sao-vay"
    assert cfg["platform_routing"] == {"tiktok": "short_9x16", "youtube": "long_16x9"}
    assert cfg["speed_optimization"]["spinoff_shorts_per_long"] == 6
    with pytest.raises(ValueError):
        get_channel("non_existent_channel")
    raw = json.dumps(cfg, ensure_ascii=False)
    assert "channel/ua-sao-vay" in raw
