"""Comprehensive Unit Tests for Video Review Queue Manager and Approval Gate."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tools.build_review_dashboard import build_review_dashboard
from tools.publish_youtube_cdp import publish_single_video
from tools.review_queue_manager import (
    apply_review_decisions,
    check_publish_permission,
    get_rejected_jobs,
    load_review_queue,
    register_video_for_review,
    save_review_queue,
    set_review_decision,
    sync_all_channel_runs,
)


@pytest.fixture
def tmp_queue_path(tmp_path: Path) -> Path:
    """Provide temporary path for review queue JSON."""
    return tmp_path / "test_video_review_queue.json"


def test_load_and_save_queue(tmp_queue_path: Path) -> None:
    """Test loading non-existent file returns default schema, and saving works."""
    data = load_review_queue(tmp_queue_path)
    assert data["schema_version"] == "1.0"
    assert "updated_at" in data
    assert data["items"] == {}

    data["items"]["job_1"] = {"job_id": "job_1", "status": "PENDING_REVIEW"}
    saved_path = save_review_queue(data, tmp_queue_path)
    assert saved_path == tmp_queue_path
    assert tmp_queue_path.is_file()

    reloaded = load_review_queue(tmp_queue_path)
    assert "job_1" in reloaded["items"]
    assert reloaded["items"]["job_1"]["status"] == "PENDING_REVIEW"


def test_register_video_for_review(tmp_queue_path: Path) -> None:
    """Test registering a new video asset and updating existing without resetting review state."""
    item = register_video_for_review(
        job_id="ai-binh-dan-batch3-16x9",
        channel_id="ai_binh_dan",
        channel_name="AI Bình Dân",
        format_profile="long_16x9",
        title="5 Tuyệt Chiêu AI",
        mp4_path="/path/to/video.mp4",
        thumbnail_path="/path/to/thumb.jpg",
        srt_path="/path/to/subs.srt",
        duration_sec=320.5,
        competitor_formula="Hook in 3s with paradox",
        queue_path=tmp_queue_path,
    )

    assert item["job_id"] == "ai-binh-dan-batch3-16x9"
    assert item["channel_id"] == "ai_binh_dan"
    assert item["channel_name"] == "AI Bình Dân"
    assert item["format_profile"] == "long_16x9"
    assert item["status"] == "PENDING_REVIEW"
    assert item["review_notes"] == ""
    assert item["reviewed_at"] is None
    assert item["duration_sec"] == 320.5
    assert item["competitor_formula"] == "Hook in 3s with paradox"

    # Approve item
    set_review_decision(
        job_id="ai-binh-dan-batch3-16x9",
        status="APPROVED",
        review_notes="Approved by Lead",
        queue_path=tmp_queue_path,
    )

    # Re-registering with updated media path should preserve approval status and notes
    updated = register_video_for_review(
        job_id="ai-binh-dan-batch3-16x9",
        channel_id="ai_binh_dan",
        format_profile="long_16x9",
        mp4_path="/new/path/video.mp4",
        queue_path=tmp_queue_path,
        reset_status=False,
    )
    assert updated["status"] == "APPROVED"
    assert updated["review_notes"] == "Approved by Lead"
    assert updated["mp4_path"] == "/new/path/video.mp4"

    # Registering with reset_status=True resets approval back to PENDING_REVIEW
    reset_item = register_video_for_review(
        job_id="ai-binh-dan-batch3-16x9",
        channel_id="ai_binh_dan",
        format_profile="long_16x9",
        queue_path=tmp_queue_path,
        reset_status=True,
    )
    assert reset_item["status"] == "PENDING_REVIEW"
    assert reset_item["review_notes"] == ""
    assert reset_item["reviewed_at"] is None


def test_set_review_decision_and_validation(tmp_queue_path: Path) -> None:
    """Test valid decisions, timestamps, and invalid status validation."""
    register_video_for_review(
        job_id="job_approval_test",
        channel_id="chanh_niem_ke",
        format_profile="short_9x16",
        queue_path=tmp_queue_path,
    )

    # Invalid status
    with pytest.raises(ValueError, match="Invalid status 'INVALID_STATUS'"):
        set_review_decision("job_approval_test", "INVALID_STATUS", queue_path=tmp_queue_path)

    # Nonexistent job
    with pytest.raises(KeyError, match="Job 'nonexistent_job' not found"):
        set_review_decision("nonexistent_job", "APPROVED", queue_path=tmp_queue_path)

    # Approve
    appr = set_review_decision("job_approval_test", "APPROVED", "Ready to publish", queue_path=tmp_queue_path)
    assert appr["status"] == "APPROVED"
    assert appr["review_notes"] == "Ready to publish"
    assert appr["reviewed_at"] is not None

    # Reject
    rej = set_review_decision(
        "job_approval_test",
        "REJECTED",
        "Fix audio clip at 0:15",
        queue_path=tmp_queue_path,
    )
    assert rej["status"] == "REJECTED"
    assert rej["review_notes"] == "Fix audio clip at 0:15"
    assert rej["reviewed_at"] is not None

    # Reset to pending clears timestamp
    pend = set_review_decision("job_approval_test", "PENDING_REVIEW", queue_path=tmp_queue_path)
    assert pend["status"] == "PENDING_REVIEW"
    assert pend["reviewed_at"] is None

    # Publish records url
    pub = set_review_decision(
        "job_approval_test",
        "PUBLISHED",
        published_url="https://youtu.be/xyz123",
        queue_path=tmp_queue_path,
    )
    assert pub["status"] == "PUBLISHED"
    assert pub["published_url"] == "https://youtu.be/xyz123"


def test_check_publish_permission(tmp_queue_path: Path) -> None:
    """Test hard permission check returns True ONLY for APPROVED status."""
    # Not found in queue
    allowed, reason = check_publish_permission("unknown_job", queue_path=tmp_queue_path)
    assert not allowed
    assert reason == "NOT_FOUND"

    # Pending
    register_video_for_review("job_perm", "co_the_ke", "long_16x9", queue_path=tmp_queue_path)
    allowed, reason = check_publish_permission("job_perm", queue_path=tmp_queue_path)
    assert not allowed
    assert reason == "PENDING_REVIEW"

    # Rejected
    set_review_decision("job_perm", "REJECTED", "Narration muffled", queue_path=tmp_queue_path)
    allowed, reason = check_publish_permission("job_perm", queue_path=tmp_queue_path)
    assert not allowed
    assert reason == "REJECTED"

    # Published (already published cannot republish without approval)
    set_review_decision("job_perm", "PUBLISHED", queue_path=tmp_queue_path)
    allowed, reason = check_publish_permission("job_perm", queue_path=tmp_queue_path)
    assert not allowed
    assert reason == "PUBLISHED"

    # Approved - ONLY THIS YIELDS TRUE
    set_review_decision("job_perm", "APPROVED", queue_path=tmp_queue_path)
    allowed, reason = check_publish_permission("job_perm", queue_path=tmp_queue_path)
    assert allowed
    assert reason == "APPROVED"


def test_get_rejected_jobs(tmp_queue_path: Path) -> None:
    """Test listing only rejected jobs that contain actionable review notes."""
    register_video_for_review("job_ok", "ai_binh_dan", "long_16x9", queue_path=tmp_queue_path)
    register_video_for_review("job_rej_with_note", "ai_binh_dan", "short_9x16", queue_path=tmp_queue_path)
    register_video_for_review("job_rej_no_note", "co_the_ke", "long_16x9", queue_path=tmp_queue_path)

    set_review_decision("job_ok", "APPROVED", queue_path=tmp_queue_path)
    set_review_decision("job_rej_with_note", "REJECTED", "Re-render scene 4 thumbnail", queue_path=tmp_queue_path)
    set_review_decision("job_rej_no_note", "REJECTED", "", queue_path=tmp_queue_path)

    rejected = get_rejected_jobs(tmp_queue_path)
    assert len(rejected) == 1
    assert rejected[0]["job_id"] == "job_rej_with_note"
    assert rejected[0]["review_notes"] == "Re-render scene 4 thumbnail"


def test_apply_review_decisions_dashboard_export(tmp_queue_path: Path, tmp_path: Path) -> None:
    """Test importing and applying review decisions in dict, list, and JSON file formats."""
    # Register initial items
    register_video_for_review("job_batch_1", "nao_luoi", "long_16x9", queue_path=tmp_queue_path)
    register_video_for_review("job_batch_2", "nao_luoi", "short_9x16", queue_path=tmp_queue_path)

    # 1. Dict mapping format
    decisions_dict = {
        "job_batch_1": {"status": "APPROVED", "review_notes": "All checks green"},
        "job_batch_2": {"status": "REJECTED", "review_notes": "Hook syllable count > 24"},
    }
    applied = apply_review_decisions(decisions_dict, queue_path=tmp_queue_path)
    assert len(applied) == 2

    allowed_1, _ = check_publish_permission("job_batch_1", queue_path=tmp_queue_path)
    allowed_2, _ = check_publish_permission("job_batch_2", queue_path=tmp_queue_path)
    assert allowed_1 is True
    assert allowed_2 is False

    # 2. List format via JSON file
    json_file = tmp_path / "decisions_export.json"
    json_data = [
        {"job_id": "job_batch_2", "status": "APPROVED", "review_notes": "Repaired syllable count"},
        {"job_id": "job_batch_new", "status": "APPROVED", "review_notes": "Direct pass"},
    ]
    json_file.write_text(json.dumps(json_data), encoding="utf-8")

    applied_file = apply_review_decisions(json_file, queue_path=tmp_queue_path)
    assert len(applied_file) == 2

    allowed_2_after, _ = check_publish_permission("job_batch_2", queue_path=tmp_queue_path)
    allowed_new, _ = check_publish_permission("job_batch_new", queue_path=tmp_queue_path)
    assert allowed_2_after is True
    assert allowed_new is True


def test_sync_all_channel_runs(tmp_queue_path: Path) -> None:
    """Test scanning all 20 Vietnamese channels produces exactly 40 jobs (20 channels x 2 formats)."""
    summary = sync_all_channel_runs(batch_tag="testbatch", queue_path=tmp_queue_path)
    assert summary["synced_operations"] >= 40
    assert summary["total_jobs"] >= 40

    queue = load_review_queue(tmp_queue_path)
    # Check that canonical jobs exist
    assert "ai-binh-dan-testbatch-16x9" in queue["items"]
    assert "ai-binh-dan-testbatch-9x16" in queue["items"]
    assert "tam-tinh-dem-testbatch-16x9" in queue["items"]
    assert "tam-tinh-dem-testbatch-9x16" in queue["items"]

    # All newly synced jobs must start in PENDING_REVIEW
    assert queue["items"]["ai-binh-dan-testbatch-16x9"]["status"] == "PENDING_REVIEW"


def test_publish_youtube_cdp_approval_gate(tmp_queue_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test publish_youtube_cdp hard-blocks unapproved jobs and allows approved jobs."""
    # Point default queue to temporary queue
    import tools.review_queue_manager as rqm
    monkeypatch.setattr(rqm, "DEFAULT_QUEUE_PATH", tmp_queue_path)

    # 1. Unapproved job: must raise RuntimeError with exact prefix
    register_video_for_review(
        job_id="test-gate-job-16x9",
        channel_id="ai_binh_dan",
        format_profile="long_16x9",
        queue_path=tmp_queue_path,
    )

    with pytest.raises(RuntimeError, match="PUBLISH_BLOCKED_BY_REVIEW_GATE: Job 'test-gate-job-16x9' is not APPROVED"):
        asyncio.run(
            publish_single_video(
                video_path="/dummy/path/test-gate-job-16x9.mp4",
                title="Test Title",
                description="Test Desc",
                job_id="test-gate-job-16x9",
                bypass_review_gate=False,
            )
        )

    # 2. Approved job: passes gate (mocking YouTubeCDPClient to avoid actual Chrome launch)
    set_review_decision("test-gate-job-16x9", "APPROVED", queue_path=tmp_queue_path)

    with patch("tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client.evaluate.return_value = "https://studio.youtube.com"
        mock_client.get_channel_info.return_value = {"channelName": "AI Bình Dân", "channelId": "UC123"}
        mock_client.extract_video_url.return_value = "https://youtu.be/assigned123"
        mock_client.publish_and_finish.return_value = "https://youtu.be/assigned123"
        mock_client_cls.return_value = mock_client

        result = asyncio.run(
            publish_single_video(
                video_path="/dummy/path/test-gate-job-16x9.mp4",
                title="Test Title",
                description="Test Desc",
                job_id="test-gate-job-16x9",
                bypass_review_gate=False,
            )
        )

        assert result["status"] == "PUBLISHED"
        assert result["video_url"] == "https://youtu.be/assigned123"

        # Verify queue was updated to PUBLISHED
        queue = load_review_queue(tmp_queue_path)
        assert queue["items"]["test-gate-job-16x9"]["status"] == "PUBLISHED"
        assert queue["items"]["test-gate-job-16x9"]["published_url"] == "https://youtu.be/assigned123"

    # 3. Bypass gate flag allows publishing even when PENDING_REVIEW
    register_video_for_review(
        job_id="test-bypass-job-16x9",
        channel_id="ai_binh_dan",
        format_profile="long_16x9",
        queue_path=tmp_queue_path,
    )
    with patch("tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client.evaluate.return_value = "https://studio.youtube.com"
        mock_client.get_channel_info.return_value = {"channelName": "AI Bình Dân", "channelId": "UC123"}
        mock_client.extract_video_url.return_value = "https://youtu.be/bypass123"
        mock_client.publish_and_finish.return_value = "https://youtu.be/bypass123"
        mock_client_cls.return_value = mock_client

        bypass_res = asyncio.run(
            publish_single_video(
                video_path="/dummy/path/test-bypass-job-16x9.mp4",
                title="Bypass Title",
                description="Bypass Desc",
                job_id="test-bypass-job-16x9",
                bypass_review_gate=True,
            )
        )
        assert bypass_res["status"] == "PUBLISHED"


def test_build_review_dashboard(tmp_queue_path: Path, tmp_path: Path) -> None:
    """Verify build_review_dashboard generates valid HTML with 20 VN channels, controls, and textareas."""
    # Ensure queue has all 20 channels x 2 formats
    sync_all_channel_runs(batch_tag="testdash", queue_path=tmp_queue_path)

    out_file = tmp_path / "test_review_dashboard.html"
    paths = build_review_dashboard(queue_path=tmp_queue_path, output_paths=[out_file])

    assert len(paths) == 1
    assert paths[0] == out_file
    assert out_file.is_file()

    html_content = out_file.read_text(encoding="utf-8")

    # 1. Top-level section & Counter Bar
    assert "Trạm Duyệt Video & Ghi Chú Sửa Lỗi" in html_content
    assert "counter-total" in html_content
    assert "counter-pending" in html_content
    assert "counter-approved" in html_content
    assert "counter-rejected" in html_content

    # 2. Bulk action buttons
    assert "review_decisions.json" in html_content
    assert "Copy Lệnh Áp Dụng" in html_content

    # 3. Quick-tag chips
    assert "+ Sửa Hook 3s đầu" in html_content
    assert "+ Đổi ảnh Start-End cảnh bị lỗi" in html_content
    assert "+ Chỉnh lại giọng đọc/nhịp" in html_content
    assert "+ Sửa tiêu đề/Thumbnail" in html_content
    assert "+ Sửa nội dung kịch bản" in html_content

    # 4. Interactive review controls & textareas
    assert "setJobDecision" in html_content
    assert "review-notes-textarea" in html_content
    assert "VP_VIDEO_REVIEW_QUEUE_V1" in html_content

    # 5. All 20 Vietnamese channels present in HTML
    vn_channel_ids = [
        "ai_binh_dan", "co_the_ke", "ho_so_ky_la", "nao_luoi", "su_ke_lai",
        "thuong_cho_kheo", "tui_tien", "ua_sao_vay", "luat_ngam", "ban_do_quyen_luc",
        "dia_com", "luat_doi_thuong", "banh_rang", "vu_tru_ti_hon", "nghe_song_sot",
        "la_ban_hoc_thuat", "chanh_niem_ke", "loi_sang_soi", "minh_triet_song", "tam_tinh_dem"
    ]
    for cid in vn_channel_ids:
        assert f'data-channel-id="{cid}"' in html_content

