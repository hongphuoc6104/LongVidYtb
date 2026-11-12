"""Unit tests for 20 Vietnamese Long (16:9) Publication & Thumbnail Pipeline.

Tests:
1. parse_metadata_file with tags, chapters starting at 00:00, title <= 55 chars,
   banned CTA rejection, and language/category parsing.
2. Channel Identity Lock mismatch raising CHANNEL_IDENTITY_MISMATCH and
   Google Sign-In lock raising GOOGLE_AUTH_REQUIRED.
3. Tag formatting and safe truncation safely under 480 total chars (YouTube 500 cap).
4. Updated Flow thumbnail blueprints for co_the_ke, ua_sao_vay, chanh_niem_ke
   (hook_text_16x9, safe zones, dry_run poster synthesis).
5. publish_20_long_batch manifest asset validation, stale MP4 gate, and Review Gate.
6. audit_20_channels_readiness dry-run execution and summary reporting.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.tools.audit_20_channels_readiness import audit_20_channels
from sys.tools.build_publish_kit import assert_no_banned_cta
from sys.tools.generate_sensational_thumbnails import (
    FLOW_THUMBNAIL_BLUEPRINTS,
    _synthesize_dry_run_poster,
)
from sys.tools.publish_20_long_batch import (
    publish_20_long_batch,
    validate_long_video_assets,
)
from sys.tools.publish_youtube_cdp import (
    format_and_truncate_tags,
    parse_metadata_file,
    publish_single_video,
)


def test_parse_metadata_file_comprehensive(tmp_path: Path):
    """Test parse_metadata_file with title <= 55, chapters starting at 00:00, tags, language, and category."""
    md_content = """# Gói Xuất Bản YouTube Long 16:9

## 1. Tiêu đề (Title)
```text
Bí Mật Tự Động Hóa Công Việc Bằng AI Trong 1 Giờ
```

## 2. Mô tả (Description) & Dấu thời gian (Chapters)
```text
Khám phá quy trình tự động hóa công việc bằng AI giúp bạn giải phóng hàng giờ thao tác thủ công mỗi ngày.

📑 Nội dung chính (Chapters):
00:00 - Hồi 01: Cơn Bão Tự Động Hóa
01:25 - Hồi 02: Bóc Tách 3 Tác Vụ Đốt Thời Gian
03:04 - Hồi 03: Bản Thiết Kế Dòng Chảy

#TuDongHoa #AI
```

## 3. Thẻ từ khóa (Tags)
```text
AI Bình Dân, tự động hóa bằng AI, quy trình làm việc, no code
```

## Ngôn ngữ (Language)
```text
Tiếng Việt
```

## Danh mục (Category)
```text
Khoa học và Công nghệ
```

## 6. Bình luận ghim (Pinned Comment)
```text
Tác vụ nào đang ngốn nhiều thời gian nhất của bạn? Chia sẻ bên dưới nhé!
```
"""
    md_file = tmp_path / "youtube_long.md"
    md_file.write_text(md_content, encoding="utf-8")

    meta = parse_metadata_file(md_file)
    assert meta["title"] == "Bí Mật Tự Động Hóa Công Việc Bằng AI Trong 1 Giờ"
    assert len(meta["title"]) <= 55
    assert "00:00 - Hồi 01: Cơn Bão Tự Động Hóa" in meta["description"]
    assert "AI Bình Dân" in meta["tags"]
    assert meta["language"] == "Tiếng Việt"
    assert meta["category"] == "Khoa học và Công nghệ"
    assert "Tác vụ nào" in meta["pinned_comment"]

    # Verify no banned CTAs in title & description
    assert_no_banned_cta(meta["title"])
    assert_no_banned_cta(meta["description"])
    assert_no_banned_cta(meta["pinned_comment"])

    # Banned CTA check must reject forbidden phrases
    with pytest.raises(ValueError, match="BANNED_CTA_IN_PUBLISH_KIT"):
        assert_no_banned_cta("Hãy bấm đăng ký kênh ngay hôm nay!")


def test_channel_identity_lock_mismatch():
    """Verify Channel Identity Lock raises CHANNEL_IDENTITY_MISMATCH on channel mismatch."""
    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client.evaluate.return_value = "https://studio.youtube.com/channel/UC_DIFFERENT_999"
        mock_client.get_channel_info.return_value = {
            "title": "Studio",
            "url": "https://studio.youtube.com/channel/UC_DIFFERENT_999",
            "channelId": "UC_DIFFERENT_999",
            "channelName": "Other Channel",
        }
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="CHANNEL_IDENTITY_MISMATCH"):
            asyncio.run(
                publish_single_video(
                    video_path="/dummy/path.mp4",
                    title="Test Video Title",
                    description="Test Description",
                    expected_channel_id="UC_EXPECTED_111",
                    bypass_review_gate=True,
                )
            )


def test_google_auth_required_lock():
    """Verify Google Sign-In redirect raises GOOGLE_AUTH_REQUIRED immediately."""
    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client.evaluate.return_value = "https://accounts.google.com/v3/signin/identifier"
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="GOOGLE_AUTH_REQUIRED"):
            asyncio.run(
                publish_single_video(
                    video_path="/dummy/path.mp4",
                    title="Test Video Title",
                    description="Test Description",
                    bypass_review_gate=True,
                )
            )


def test_tag_formatting_and_safe_truncation():
    """Test tag formatting, deduplication, hash-stripping, and safe truncation under 480 chars."""
    # Build list of 40 tags of ~25 characters each (total > 1000 chars)
    raw_tags = [f"#Tag_{i:02d}_LongDetailedTopicName" for i in range(40)]
    clean = format_and_truncate_tags(raw_tags, max_chars=480)

    assert len(clean) > 0
    # Every tag should have no leading hash
    for t in clean:
        assert not t.startswith("#")

    # Joined length must not exceed 480
    joined = ",".join(clean)
    assert len(joined) <= 480
    assert len(joined) > 350

    # Comma-separated string parsing with duplicates
    csv_input = "AI Bình Dân, ai binh dan, #Tự động hóa, AI Bình Dân, Máy học"
    csv_clean = format_and_truncate_tags(csv_input, max_chars=480)
    assert "AI Bình Dân" in csv_clean
    assert "Tự động hóa" in csv_clean
    assert "Máy học" in csv_clean
    # Deduplication check
    assert len([t for t in csv_clean if t.lower() == "ai bình dân"]) == 1


def test_updated_thumbnail_blueprints_and_dry_run(tmp_path: Path):
    """Test updated 16:9 Flow blueprints for co_the_ke, ua_sao_vay, chanh_niem_ke, and dry-run synthesis."""
    # 1. co_the_ke
    bp_ctk = FLOW_THUMBNAIL_BLUEPRINTS["co_the_ke"]
    assert bp_ctk.get("hook_text_16x9") == "THIẾU NGỦ PHÁ NÃO!"
    assert "THIẾU NGỦ PHÁ NÃO!" in bp_ctk["flow_prompt_16x9"]
    assert "TOP-LEFT SAFE ZONE" in bp_ctk["flow_prompt_16x9"]
    assert "ĂN ĐÊM PHÁ BỤNG!" in bp_ctk["flow_prompt_9x16"]  # Shorts contract untouched

    # 2. ua_sao_vay
    bp_usv = FLOW_THUMBNAIL_BLUEPRINTS["ua_sao_vay"]
    assert bp_usv.get("hook_text_16x9") == "BÍ MẬT TRỤC GƯƠNG!"
    assert "BÍ MẬT TRỤC GƯƠNG!" in bp_usv["flow_prompt_16x9"]
    assert "TOP-LEFT SAFE ZONE" in bp_usv["flow_prompt_16x9"]
    assert "PHẢN XẠ 0.1 GIÂY!" in bp_usv["flow_prompt_9x16"]

    # 3. chanh_niem_ke
    bp_cnk = FLOW_THUMBNAIL_BLUEPRINTS["chanh_niem_ke"]
    assert bp_cnk.get("hook_text_16x9") == "BUÔNG BỎ ÂU LO!"
    assert "BUÔNG BỎ ÂU LO!" in bp_cnk["flow_prompt_16x9"]
    assert "TOP-LEFT SAFE ZONE" in bp_cnk["flow_prompt_16x9"]
    assert "MŨI TÊN THỨ 2!" in bp_cnk["flow_prompt_9x16"]

    # 4. Synthesize dry-run posters in 16:9 and 9:16
    poster_16x9 = tmp_path / "thumb_co_the_ke_16x9.png"
    _synthesize_dry_run_poster("co_the_ke", "16:9", poster_16x9)
    assert poster_16x9.is_file()
    assert poster_16x9.stat().st_size <= 2_000_000
    with Image.open(poster_16x9) as im:
        assert im.size == (1280, 720)

    poster_9x16 = tmp_path / "thumb_co_the_ke_9x16.png"
    _synthesize_dry_run_poster("co_the_ke", "9:16", poster_9x16)
    assert poster_9x16.is_file()
    with Image.open(poster_9x16) as im:
        assert im.size == (1080, 1920)


def test_publish_20_long_manifest_validation_and_stale_gate(tmp_path: Path):
    """Test asset validation, thumbnail rules, title constraints, and the stale MP4 gate."""
    ch_dir = tmp_path / "video" / "vn_pilot_test_slug_long"
    ch_dir.mkdir(parents=True)

    mp4_file = ch_dir / "vn_pilot_test_slug_long_16x9.mp4"
    srt_file = ch_dir / "vn_pilot_test_slug_long_16x9.srt"
    thumb_file = ch_dir / "vn_pilot_test_slug_long_thumbnail_16x9.png"
    md_file = ch_dir / "publish" / "youtube_long.md"
    md_file.parent.mkdir(parents=True)

    # Create dummy files
    mp4_file.write_bytes(b"\x00" * 1024)
    srt_file.write_text("1\n00:00:00,000 --> 00:00:05,000\nXin chào\n", encoding="utf-8")
    Image.new("RGB", (1280, 720), (240, 240, 240)).save(thumb_file)
    md_file.write_text("## 1. Tiêu đề\nTest Valid Title\n## 2. Mô tả\nTest Description\n", encoding="utf-8")

    channel_data = {
        "channel_id": "test_slug",
        "video_path": str(mp4_file.relative_to(tmp_path)),
        "srt_path": str(srt_file.relative_to(tmp_path)),
        "thumbnail_path": str(thumb_file.relative_to(tmp_path)),
        "youtube_long_md_path": str(md_file.relative_to(tmp_path)),
        "youtube_title": "Test Valid Title",
        "description": "Test Description",
    }

    # Ensure MP4 is newer than spec
    time.sleep(0.05)
    mp4_file.touch()

    validated = validate_long_video_assets("test_slug", channel_data, allow_stale=False, root_dir=tmp_path)
    assert validated["title"] == "Test Valid Title"
    assert validated["video_path"] == str(mp4_file)

    # 1. Stale MP4 Gate:
    # A newer youtube_long.md must NOT trigger STALE_MP4_REJECTED (SEO kits authored post-render)
    time.sleep(0.05)
    md_file.touch()
    valid_after_md = validate_long_video_assets("test_slug", channel_data, allow_stale=False, root_dir=tmp_path)
    assert valid_after_md["title"] == "Test Valid Title"

    # A newer aligned spec MUST trigger STALE_MP4_REJECTED
    spec_file = ch_dir / "test_slug_long_aligned_spec.json"
    spec_file.write_text("{}", encoding="utf-8")
    time.sleep(0.05)
    spec_file.touch()
    with pytest.raises(ValueError, match="STALE_MP4_REJECTED"):
        validate_long_video_assets("test_slug", channel_data, allow_stale=False, root_dir=tmp_path)

    # Allowing stale bypasses error
    bypassed = validate_long_video_assets("test_slug", channel_data, allow_stale=True, root_dir=tmp_path)
    assert bypassed["title"] == "Test Valid Title"

    # 2. Title length > 55 chars
    long_title_data = dict(channel_data, youtube_title="A" * 56)
    with pytest.raises(ValueError, match="TITLE_TOO_LONG"):
        validate_long_video_assets("test_slug", long_title_data, allow_stale=True, root_dir=tmp_path)

    # 3. Invalid thumbnail dimensions
    bad_thumb = ch_dir / "bad_thumb.png"
    Image.new("RGB", (640, 360), (0, 0, 0)).save(bad_thumb)
    bad_thumb_data = dict(channel_data, thumbnail_path=str(bad_thumb.relative_to(tmp_path)))
    with pytest.raises(ValueError, match="INVALID_THUMBNAIL_DIMENSIONS"):
        validate_long_video_assets("test_slug", bad_thumb_data, allow_stale=True, root_dir=tmp_path)


def test_publish_20_long_batch_dry_run_workflow(tmp_path: Path):
    """Test batch publishing in dry_run mode with atomic report writing and mock updates."""
    # Setup mock channel map & manifest in tmp_path
    channels_dir = tmp_path / "sys" / "channels"
    channels_dir.mkdir(parents=True)
    video_dir = tmp_path / "video"
    video_dir.mkdir(parents=True)

    ch_slug = "ai_binh_dan"
    ch_folder = video_dir / f"vn_pilot_{ch_slug}_long"
    ch_folder.mkdir(parents=True)

    mp4_file = ch_folder / f"vn_pilot_{ch_slug}_long_16x9.mp4"
    srt_file = ch_folder / f"vn_pilot_{ch_slug}_long_16x9.srt"
    thumb_file = ch_folder / f"vn_pilot_{ch_slug}_long_thumbnail_16x9.png"
    md_file = ch_folder / "publish" / "youtube_long.md"
    md_file.parent.mkdir(parents=True)

    mp4_file.write_bytes(b"\x00" * 2048)
    srt_file.write_text("1\n00:00:00,000 --> 00:00:05,000\nSub text\n", encoding="utf-8")
    Image.new("RGB", (1280, 720), (200, 200, 200)).save(thumb_file)
    md_file.write_text("## 1. Tiêu đề\nAI Bình Dân Tự Động Hóa\n## 2. Mô tả\nMô tả chi tiết\n", encoding="utf-8")

    mp4_file.touch()

    # Channel map
    map_data = {
        "channels": {
            ch_slug: {
                "profile_id": "profile_13",
                "cdp_port": 9234,
                "youtube_channel_id": "UCCu0MJ5uQVLyrUETn4peCoA",
                "handle": "@AIBinhDanVN",
            }
        }
    }
    map_path = channels_dir / "youtube_channel_map.json"
    map_path.write_text(json.dumps(map_data), encoding="utf-8")

    # Release links
    ai_ch_dir = channels_dir / ch_slug
    ai_ch_dir.mkdir(parents=True)
    rel_path = ai_ch_dir / "release_links.json"
    rel_path.write_text(json.dumps({"long": {}}), encoding="utf-8")

    # Manifest
    manifest_data = {
        "channels": {
            ch_slug: {
                "channel_id": ch_slug,
                "video_path": str(mp4_file.relative_to(tmp_path)),
                "srt_path": str(srt_file.relative_to(tmp_path)),
                "thumbnail_path": str(thumb_file.relative_to(tmp_path)),
                "youtube_long_md_path": str(md_file.relative_to(tmp_path)),
                "youtube_title": "AI Bình Dân Tự Động Hóa",
                "description": "Mô tả chi tiết",
                "tags_str": "AI, automation",
            }
        }
    }
    mf_path = video_dir / "publish_manifest_20_long.json"
    mf_path.write_text(json.dumps(manifest_data), encoding="utf-8")

    rep_path = video_dir / "published_20_long_report.json"

    # Verify real repository review queue is untouched
    real_queue_file = REPO_ROOT / "sys" / "channels" / "video_review_queue.json"
    real_queue_before = real_queue_file.read_text(encoding="utf-8") if real_queue_file.exists() else None

    # Run batch in dry_run mode
    summary = publish_20_long_batch(
        manifest_path=mf_path,
        channels=[ch_slug],
        max_workers=2,
        approve_batch=True,
        allow_stale=True,
        dry_run=True,
        report_path=rep_path,
        root_dir=tmp_path,
    )

    if real_queue_before is not None:
        assert real_queue_file.read_text(encoding="utf-8") == real_queue_before, (
            "publish_20_long_batch modified real video_review_queue.json during tmp_path test!"
        )

    assert summary["total_targets"] == 1
    assert summary["published_count"] == 1
    assert summary["failed_count"] == 0
    assert rep_path.is_file()

    report_content = json.loads(rep_path.read_text(encoding="utf-8"))
    assert ch_slug in report_content["published_items"]
    assert report_content["published_items"][ch_slug]["status"] == "PUBLISHED"
    assert "https://youtu.be/" in report_content["published_items"][ch_slug]["video_url"]

    # Verify release_links.json was updated
    rel_updated = json.loads(rel_path.read_text(encoding="utf-8"))
    assert rel_updated["long"]["youtube_url"] == report_content["published_items"][ch_slug]["video_url"]


def test_audit_20_channels_readiness_dry_run(tmp_path: Path):
    """Verify audit_20_channels dry run scans all 20 channels and writes summary report."""
    out_file = tmp_path / "vn_20_channels_readiness_dry.json"
    report = audit_20_channels(dry_run=True, output_file=out_file)
    assert out_file.is_file()
    assert report["total_channels"] == 20
    assert report["ready_count"] == 20
    assert report["channel_mismatch_count"] == 0
    assert report["dry_run"] is True
    assert "ai_binh_dan" in report["channels"]
    assert report["channels"]["ai_binh_dan"]["expected_channel_id"] == "UCCu0MJ5uQVLyrUETn4peCoA"


def test_parse_metadata_file_bullet_format(tmp_path: Path):
    """Test parse_metadata_file with bullet points for language, category, and ## 5. Pinned Comment."""
    md_content = """# Gói Xuất Bản YouTube Long 16:9

## 1. Tiêu đề (Title)
```text
Bí Quyết Tự Học Sâu Nhớ Lâu Cho Người Bận Rộn
```

## 2. Mô tả (Description) & Dấu thời gian (Chapters)
```text
Quy trình tự học sâu giúp bạn lưu giữ 90% kiến thức.

📑 Nội dung chính (Chapters):
00:00 - Hồi 01: Vòng Lặp Học Nhanh Quên
01:30 - Hồi 02: Kỹ Thuật Feynman
```

## 3. Thẻ từ khóa (Tags)
```text
học sâu, feynman, active recall
```

## 4. Cài đặt YouTube Studio (Ngôn ngữ, Danh mục, Card, End Screen)
- **Ngôn ngữ video**: Tiếng Việt
- **Danh mục (Category)**: Khoa học và Công nghệ
- **Thẻ thông tin (Info Card)**: Vị trí 05:14

## 5. Bình luận ghim (Pinned Comment)
```text
Bạn đang áp dụng phương pháp ghi nhớ nào? Bình luận bên dưới nhé!
```
"""
    md_file = tmp_path / "youtube_long_bullet.md"
    md_file.write_text(md_content, encoding="utf-8")

    meta = parse_metadata_file(md_file)
    assert meta["title"] == "Bí Quyết Tự Học Sâu Nhớ Lâu Cho Người Bận Rộn"
    assert meta["language"] == "Tiếng Việt"
    assert meta["category"] == "Khoa học và Công nghệ"
    assert "Bình luận bên dưới nhé!" in meta["pinned_comment"]


def test_check_studio_readiness_tiers():
    """Verify check_studio_readiness accurately parses enabled vs eligible tiers."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)

    # Mock evaluate for intermediate "Đã bật"
    async def mock_eval_enabled(expr: str):
        if "window.location.href" in expr:
            return "https://studio.youtube.com/channel/UC_MOCK_123"
        if "getStatus" in expr or "t1, t2, t3" in expr:
            return {"t1": "Đã bật", "t2": "Đã bật", "t3": "Đủ điều kiện"}
        if "settingsBtn" in expr:
            return True
        if "is_visible" in expr or "dlg_ready" in expr or "dialog-type=" in expr or "tp-yt-paper-dialog" in expr:
            return True
        if "channelTab" in expr or "featTab" in expr:
            return True
        if "closeBtn" in expr:
            return True
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_enabled)
    client.call = AsyncMock()
    client.get_channel_info = AsyncMock(return_value={"channelId": "UC_MOCK_123", "channelName": "Test Channel"})

    readiness = asyncio.run(client.check_studio_readiness())
    assert readiness["authenticated"] is True
    assert readiness["channel_id"] == "UC_MOCK_123"
    assert readiness["standard_features"] is True
    assert readiness["intermediate_features"] is True
    assert readiness["tier2_eligible"] is True
    assert readiness["tier3_eligible"] is False
    assert readiness["audit_method"] == "settings_feature_eligibility"
    assert readiness["tier2_status_text"] == "Đã bật"
    assert readiness["tier3_status_text"] == "Đủ điều kiện"

    # Mock evaluate for intermediate "Đủ điều kiện" (intermediate must NOT be enabled)
    async def mock_eval_eligible(expr: str):
        if "window.location.href" in expr:
            return "https://studio.youtube.com/channel/UC_MOCK_123"
        if "getStatus" in expr or "t1, t2, t3" in expr:
            return {"t1": "Đã bật", "t2": "Đủ điều kiện", "t3": "Đủ điều kiện"}
        if "settingsBtn" in expr:
            return True
        if "is_visible" in expr or "dlg_ready" in expr or "dialog-type=" in expr or "tp-yt-paper-dialog" in expr:
            return True
        if "channelTab" in expr or "featTab" in expr:
            return True
        if "closeBtn" in expr:
            return True
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_eligible)
    readiness_eligible = asyncio.run(client.check_studio_readiness())
    assert readiness_eligible["tier2_eligible"] is False
    assert readiness_eligible["intermediate_features"] is False
    assert readiness_eligible["tier2_status_text"] == "Đủ điều kiện"


def test_check_studio_readiness_lazy_mount_and_shadow_polling():
    """Verify check_studio_readiness retries lazy-mounted Kênh item & supports bounded English/Vietnamese status parsing."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    ch_attempts = {"n": 0}
    feat_attempts = {"n": 0}

    async def mock_eval_lazy(expr: str):
        if "window.location.href" in expr:
            return "https://studio.youtube.com/channel/UC_LAZY_123"
        if "settingsBtn" in expr:
            return True
        if "is_visible" in expr or "dlg_ready" in expr or "dialog-type=" in expr or "tp-yt-paper-dialog" in expr:
            return True
        if "channelTab" in expr:
            ch_attempts["n"] += 1
            return ch_attempts["n"] >= 3  # Simulate 2 lazy-mount ticks before li#channel mounts
        if "featTab" in expr:
            feat_attempts["n"] += 1
            return feat_attempts["n"] >= 2
        if "tiers_mounted" in expr or ("tính năng bậc trung" in expr and "getStatus" not in expr):
            return True
        if "getStatus" in expr or "t1, t2, t3" in expr:
            return {"t1": "Enabled", "t2": "Enabled", "t3": "Enabled"}
        if "closeBtn" in expr:
            return True
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_lazy)
    client.call = AsyncMock()
    client.get_channel_info = AsyncMock(return_value={"channelId": "UC_LAZY_123", "channelName": "Cơ Thể Kể"})

    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = asyncio.run(client.check_studio_readiness())

    assert ch_attempts["n"] == 3
    assert feat_attempts["n"] == 2
    assert res["standard_features"] is True
    assert res["intermediate_features"] is True
    assert res["advanced_features"] is True
    assert res["tier2_eligible"] is True
    assert res["tier3_eligible"] is True
    assert res["tier1_status_text"] == "Enabled"
    assert res["tier2_status_text"] == "Enabled"
    assert res["audit_method"] == "settings_feature_eligibility"


def test_wait_for_upload_complete_active_percentage():
    """Verify wait_for_upload_complete does NOT return True when upload percentage is still active."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)

    calls = [
        {"text": "42% · còn 2 phút", "doneDisabled": False},
        {"text": "85% · còn 30 giây", "doneDisabled": False},
        {"text": "100% đã xử lý", "doneDisabled": False},
    ]

    async def mock_eval_progress(expr: str):
        if "statusEl" in expr:
            return calls.pop(0) if calls else {"text": "100% đã xử lý", "doneDisabled": False}
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_progress)

    res = asyncio.run(client.wait_for_upload_complete(max_wait_sec=10.0))
    assert res is True
    # Ensure all states were consumed up to 100%
    assert len(calls) == 0


def test_wait_for_upload_complete_processing_states():
    """Verify wait_for_upload_complete accepts 'Đang xử lý đến HD ...' and 'Không tìm thấy vấn đề nào'."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)

    # 1. 'Đang xử lý đến HD (95%)' with doneDisabled=False -> should return True
    client.evaluate = AsyncMock(return_value={"text": "Đang xử lý đến HD (95%)", "doneDisabled": False})
    res1 = asyncio.run(client.wait_for_upload_complete(max_wait_sec=5.0))
    assert res1 is True

    # 2. 'Kiểm tra hoàn tất. Không tìm thấy vấn đề nào.' with doneDisabled=False -> should return True
    client.evaluate = AsyncMock(return_value={"text": "Kiểm tra hoàn tất. Không tìm thấy vấn đề nào.", "doneDisabled": False})
    res2 = asyncio.run(client.wait_for_upload_complete(max_wait_sec=5.0))
    assert res2 is True

    # 3. 'Đã tải video lên' with doneDisabled=False -> should return True
    client.evaluate = AsyncMock(return_value={"text": "Đã tải video lên (100%)", "doneDisabled": False})
    res3 = asyncio.run(client.wait_for_upload_complete(max_wait_sec=5.0))
    assert res3 is True


def test_publish_and_finish_processing_modal(tmp_path: Path):
    """Verify publish_and_finish accepts 'Xử lý video' modal and sets _last_publish_accepted."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    shot_path = tmp_path / "proc_modal.png"

    async def mock_eval(expr: str):
        if "#done-button" in expr and "click" in expr:
            return True
        if "ytcp-confirmation-dialog" in expr:
            return None
        if "ytcp-video-share-dialog" in expr and "querySelector('a')" in expr:
            return {"found": False}
        if "ytcp-video-processing-dialog" in expr or "độ nét chuẩn" in expr:
            return {"detected": True, "link": "https://youtu.be/processed_123"}
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval)
    client.capture_screenshot = AsyncMock()

    url = asyncio.run(client.publish_and_finish(screenshot_path=shot_path))
    assert client._last_publish_accepted is True
    assert url == "https://youtu.be/processed_123"


def test_publish_single_video_oembed_pending_fallback_vs_draft(tmp_path: Path):
    """Verify publish_single_video marks oembed_pending_processing=True for queued SD vs raises on draft."""

    dummy_mp4 = tmp_path / "test_long.mp4"
    dummy_mp4.write_bytes(b"\x00" * 1024)

    # Case A: oEmbed fails, but verify_video_edit_page shows "Đang xử lý (SD)" & accepted -> succeeds with oembed_pending_processing
    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls, \
         patch("urllib.request.urlopen", side_effect=Exception("HTTP 404 Not Found")), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client._last_publish_accepted = True
        mock_client.evaluate.return_value = "https://studio.youtube.com/channel/UC_VALID"
        mock_client.get_channel_info.return_value = {
            "channelId": "UC_VALID",
            "channelName": "Test Channel",
        }
        mock_client.publish_and_finish.return_value = "https://youtu.be/vid_long_sd"
        mock_client.verify_video_edit_page.return_value = {
            "live_title": "Test Video Title",
            "visibility_text": "Đang xử lý (SD)",
            "is_draft_or_private": False,
            "has_chapters_00_00": True,
            "has_custom_thumbnail": True,
            "tags_chip_count": 5,
        }
        mock_client_cls.return_value = mock_client

        res = asyncio.run(
            publish_single_video(
                video_path=dummy_mp4,
                title="Test Video Title",
                description="Test Description",
                bypass_review_gate=True,
                is_short=False,
            )
        )
        assert res["status"] == "PUBLISHED"
        assert res["oembed_ok"] is False
        assert res["oembed_pending_processing"] is True
        assert res["edit_verification"]["visibility_text"] == "Đang xử lý (SD)"

    # Case B: oEmbed fails, and verify_video_edit_page shows "Bản nháp" and not accepted -> raises PUBLIC_VERIFICATION_FAILED
    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls, \
         patch("urllib.request.urlopen", side_effect=Exception("HTTP 404 Not Found")), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client._last_publish_accepted = False
        mock_client.evaluate.return_value = "https://studio.youtube.com/channel/UC_VALID"
        mock_client.get_channel_info.return_value = {
            "channelId": "UC_VALID",
            "channelName": "Test Channel",
        }
        mock_client.publish_and_finish.return_value = "https://youtu.be/vid_long_draft"
        mock_client.verify_video_edit_page.return_value = {
            "live_title": "Test Video Title",
            "visibility_text": "Bản nháp",
            "is_draft_or_private": True,
        }
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="PUBLIC_VERIFICATION_FAILED"):
            asyncio.run(
                publish_single_video(
                    video_path=dummy_mp4,
                    title="Test Video Title",
                    description="Test Description",
                    bypass_review_gate=True,
                    is_short=False,
                )
            )


def test_upload_srt_inside_open_captions_modal(tmp_path: Path):
    """Verify _upload_srt_inside_open_captions_modal handles 3-dot menu -> upload item -> confirm -> DOM.setFileInputFiles -> publish."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    dummy_srt = tmp_path / "sub.srt"
    dummy_srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nHello\n", encoding="utf-8")

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    client.call = AsyncMock()
    client.get_remote_object = AsyncMock(return_value={"objectId": "remote_obj_123"})

    async def mock_eval(expr: str):
        if "findDirect" in expr and "moreBtn" in expr:
            return {"action": "more_menu_clicked"}
        if "tp-yt-paper-item[test-id=\"upload\"]" in expr and "Array.from" in expr:
            return True
        if "ytve-captions-editor-upload-dialog" in expr and "#confirm-button" in expr:
            return True
        if "#publish-button" in expr:
            return True
        if "modal.offsetParent !== null" in expr:
            return False  # Modal successfully closed
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = asyncio.run(client._upload_srt_inside_open_captions_modal(dummy_srt))
    assert res is True
    client.call.assert_any_call(
        "DOM.setFileInputFiles",
        {"files": [str(dummy_srt)], "objectId": "remote_obj_123"},
    )


def test_publish_single_video_subtitles_post_publish_retry(tmp_path: Path):
    """Verify publish_single_video retries subtitles post-publish on /edit if wizard attachment fails."""
    dummy_mp4 = tmp_path / "test_long.mp4"
    dummy_mp4.write_bytes(b"\x00" * 1024)
    dummy_srt = tmp_path / "test_sub.srt"
    dummy_srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nXin chào\n", encoding="utf-8")

    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls, \
         patch("urllib.request.urlopen") as mock_urlopen, \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        mock_client = AsyncMock()
        mock_client.terminate_browser = MagicMock()
        mock_client.evaluate.return_value = "https://studio.youtube.com/channel/UC_VALID"
        mock_client.get_channel_info.return_value = {
            "channelId": "UC_VALID",
            "channelName": "Test Channel",
        }
        # Wizard fails to attach subtitles on Step 2
        mock_client.attach_subtitles_on_elements_step.return_value = False
        mock_client.publish_and_finish.return_value = "https://youtu.be/vid_sub_retry"
        # Post-publish fallback succeeds
        mock_client.attach_subtitles_post_publish.return_value = True
        mock_client_cls.return_value = mock_client

        res = asyncio.run(
            publish_single_video(
                video_path=dummy_mp4,
                title="Test Video",
                description="Test Description",
                subtitles_path=dummy_srt,
                bypass_review_gate=True,
                is_short=False,
            )
        )
        assert res["status"] == "PUBLISHED"
        assert res["subtitles_uploaded"] is True
        mock_client.attach_subtitles_post_publish.assert_awaited_once_with(
            "https://youtu.be/vid_sub_retry", dummy_srt.resolve()
        )


def test_wait_for_upload_complete_tier2_duration_abort():
    """Verify wait_for_upload_complete raises TIER2_DURATION_OR_VERIFICATION_REQUIRED immediately when >15m banner is present and publish is disabled."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    client.evaluate = AsyncMock(
        return_value={
            "text": "Quá trình xử lý bị hủy. Video dài hơn 15 phút.",
            "errText": "Quá trình xử lý bị hủy. Video dài hơn 15 phút.",
            "doneDisabled": True,
        }
    )

    with pytest.raises(RuntimeError, match="TIER2_DURATION_OR_VERIFICATION_REQUIRED: Quá trình xử lý bị hủy"):
        asyncio.run(client.wait_for_upload_complete(max_wait_sec=10.0))


def test_verify_video_edit_page_details_and_bottom_screenshot(tmp_path: Path):
    """Verify verify_video_edit_page collects language_text, category_text, tags_sample, and creates _bottom screenshot."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    shot_path = tmp_path / "edit_qa.png"
    client.call = AsyncMock()
    client.capture_screenshot = AsyncMock()
    client.dismiss_studio_interstitials = AsyncMock(return_value=False)

    async def mock_eval(expr: str):
        if "tags_sample" in expr:
            return {
                "live_title": "Video Chuyên Sâu AI",
                "description_length": 500,
                "has_chapters_00_00": True,
                "has_custom_thumbnail": True,
                "tags_chip_count": 6,
                "tags_sample": ["AI", "Khoa học", "Công nghệ", "Tự động hóa", "Machine Learning"],
                "subtitles_present": True,
                "subtitles_status": "Tiếng Việt (đã thêm)",
                "language_text": "Tiếng Việt",
                "category_text": "Khoa học và Công nghệ",
                "visibility_text": "Công khai",
            }
        if "Boolean" in expr:
            return True
        if "#toggle-button" in expr:
            return "TOGGLED"
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = asyncio.run(client.verify_video_edit_page("https://youtu.be/abc123xyz", screenshot_path=shot_path))

    assert res["live_title"] == "Video Chuyên Sâu AI"
    assert res["tags_chip_count"] == 6
    assert len(res["tags_sample"]) == 5
    assert res["language_text"] == "Tiếng Việt"
    assert res["category_text"] == "Khoa học và Công nghệ"
    assert res["subtitles_present"] is True
    assert res["is_draft_or_private"] is False
    expected_bottom = tmp_path / "edit_qa_bottom.png"
    client.capture_screenshot.assert_any_call(shot_path)
    client.capture_screenshot.assert_any_call(expected_bottom)


def test_upload_thumbnail_strict_verification_rejects_tier2_lock_and_accepts_preview(tmp_path: Path):
    """Verify upload_thumbnail rejects hidden /edit placeholders or Tier-2 (?) tooltips and accepts real previews."""
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    thumb = tmp_path / "thumb_16x9.png"
    Image.new("RGB", (1280, 720), (10, 20, 30)).save(thumb)

    # Case 1: Tier-2 tooltip (?) visible & no real preview -> raises under strict_thumbnail=True, False under strict=False
    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    client.get_remote_object = AsyncMock(return_value={"objectId": "obj_file_input"})
    client.call = AsyncMock()

    async def mock_eval_locked(expr: str):
        if "ytcp-feature-eligibility-dialog" in expr:
            return False
        if "ytcp-thumbnail-uploader" in expr:
            return {
                "ok": False,
                "tooltipVisible": True,
                "previewVisible": False,
                "selectVisible": True,
                "hasSelectedAttr": False,
                "matchedSrc": None,
            }
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_locked)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(RuntimeError, match="CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED"):
            asyncio.run(client.upload_thumbnail(thumb, strict_thumbnail=True))
        assert asyncio.run(client.upload_thumbnail(thumb, strict_thumbnail=False)) is False

    # Case 2: Valid blob preview loads on second poll tick -> returns True
    polls = {"n": 0}

    async def mock_eval_ok(expr: str):
        if "ytcp-feature-eligibility-dialog" in expr:
            return False
        if "ytcp-thumbnail-uploader" in expr:
            polls["n"] += 1
            if polls["n"] == 1:
                return {"ok": False, "tooltipVisible": False, "previewVisible": False}
            return {
                "ok": True,
                "tooltipVisible": False,
                "previewVisible": True,
                "selectVisible": False,
                "hasSelectedAttr": True,
                "matchedSrc": "blob:https://studio.youtube.com/12345",
            }
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_ok)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        assert asyncio.run(client.upload_thumbnail(thumb, strict_thumbnail=True)) is True
    assert polls["n"] == 2
    client.call.assert_any_call(
        "DOM.setFileInputFiles",
        {"files": [str(thumb.resolve())], "objectId": "obj_file_input"},
    )


def test_verify_video_edit_page_thumbnail_guard_excludes_edit_placeholder():
    """Verify verify_video_edit_page JS check excludes hidden /edit placeholder img and #still-1 auto stills."""
    import inspect
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    src = inspect.getsource(YouTubeCDPClient.verify_video_edit_page)
    assert "#select-tooltip-icon" in src
    assert "src.includes('/edit')" in src
    assert "img.naturalWidth" in src
    assert "#still-1" not in src


def test_publish_and_finish_shadow_fixed_warning_dialog_and_draft_banner_guard(tmp_path: Path):
    """Verify publish_and_finish pierces Shadow DOM/fixed rect for 'Vẫn xuất bản', and draft banner blocks false PUBLIC."""
    import inspect
    from sys.tools.publish_youtube_cdp import YouTubeCDPClient

    pf_src = inspect.getsource(YouTubeCDPClient.publish_and_finish)
    assert "getBoundingClientRect" in pf_src
    assert "shadowRoot" in pf_src
    assert "vẫn xuất bản" in pf_src

    client = YouTubeCDPClient({"id": "profile_test", "port": 9234}, headless=True)
    shot_path = tmp_path / "share.png"
    clicks = {"anyway": 0}

    async def mock_eval_warn(expr: str):
        if "#done-button" in expr and "click" in expr:
            return True
        if "vẫn xuất bản" in expr:
            clicks["anyway"] += 1
            return "vẫn xuất bản" if clicks["anyway"] == 1 else None
        if "ytcp-video-share-dialog" in expr and "shareDialog" in expr:
            if clicks["anyway"] >= 1:
                return {"found": True, "link": "https://youtu.be/after_warn_123", "title": "Published"}
            return {"found": False}
        return None

    client.evaluate = AsyncMock(side_effect=mock_eval_warn)
    client.capture_screenshot = AsyncMock()
    with patch("asyncio.sleep", new_callable=AsyncMock):
        url = asyncio.run(client.publish_and_finish(screenshot_path=shot_path))
    assert clicks["anyway"] == 1
    assert client._last_publish_accepted is True
    assert url == "https://youtu.be/after_warn_123"

    # Also verify draft_banner_detected=True with empty visibility_text sets is_draft_or_private=True
    # and prevents publish_single_video from marking DRAFT as PUBLISHED even if accepted=True.
    edit_src = inspect.getsource(YouTubeCDPClient.verify_video_edit_page)
    assert "draft_banner_detected" in edit_src
    assert "trạng thái nháp" in edit_src

    dummy_mp4 = tmp_path / "test_draft_guard.mp4"
    dummy_mp4.write_bytes(b"\x00" * 1024)
    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls, \
         patch("urllib.request.urlopen", side_effect=Exception("HTTP 403 Forbidden")), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mc = AsyncMock()
        mc.terminate_browser = MagicMock()
        mc._last_publish_accepted = True
        mc.evaluate.return_value = "https://studio.youtube.com/channel/UC_VALID"
        mc.get_channel_info.return_value = {"channelId": "UC_VALID", "channelName": "AI Bình Dân"}
        mc.publish_and_finish.return_value = "https://youtu.be/still_draft"
        mc.verify_video_edit_page.return_value = {
            "live_title": "Test",
            "visibility_text": "",
            "draft_banner_detected": True,
            "draft_banner_text": "Video này đang ở trạng thái nháp Chỉnh sửa bản nháp",
            "is_draft_or_private": True,
        }
        mock_client_cls.return_value = mc
        with pytest.raises(RuntimeError, match="PUBLIC_VERIFICATION_FAILED"):
            asyncio.run(
                publish_single_video(
                    video_path=dummy_mp4,
                    title="Test",
                    description="Desc",
                    bypass_review_gate=True,
                    is_short=False,
                )
            )


