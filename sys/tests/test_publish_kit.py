"""Unit tests for Multi-Platform Publish Kit Generator (build_publish_kit.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.build_publish_kit import (  # noqa: E402
    BANNED_CTA_PHRASES,
    PLACEHOLDER_LINK,
    assert_no_banned_cta,
    build_publish_kit,
    format_timestamp,
    init_release_links,
    load_release_links,
)


def _setup_mock_run(
    tmp_path: Path,
    job_id: str,
    format_profile: str,
    with_audio_output: bool = True,
) -> Path:
    run_dir = tmp_path / "sys" / "runs" / job_id
    run_dir.mkdir(parents=True)

    brief_data = {
        "job_id": job_id,
        "format_profile": format_profile,
        "topic": "Tại sao càng tự trách bản thân bạn lại càng trì hoãn?",
        "packaging": {
            "youtube_title": "Càng Tự Trách Bạn Càng Trì Hoãn?",
            "visual_hook": "Vì sao bạn nằm lướt điện thoại cả tiếng đồng hồ dù mai thi?",
            "seo_keywords": ["trì hoãn", "tự trách", "tâm lý học", "gen z"],
            "cta_plan": {
                "bridge": "Bản dài mình mổ xẻ trên YouTube Não Lười.",
                "close": "Lưu video lại và gửi cho bạn thân nhé.",
                "mid_cta": "Nếu thấy điều này quen thuộc, lưu lại để nghe kỹ giải pháp.",
            },
        },
    }
    (run_dir / "brief.json").write_text(json.dumps(brief_data, ensure_ascii=False, indent=2), encoding="utf-8")

    content_data = {
        "job_id": job_id,
        "format_profile": format_profile,
        "topic": "Tại sao càng tự trách bản thân bạn lại càng trì hoãn?",
        "scenes": [
            {
                "id": "SC01",
                "title": "Bàn học đêm và điện thoại",
                "duration": 10.5,
                "narration": "Vì sao bạn nằm lướt điện thoại dù mai thi?",
            },
            {
                "id": "SC02",
                "title": "Báo động hạch hạnh nhân",
                "duration": 15.0,
                "narration": "Hạch hạnh nhân báo động đỏ.",
            },
            {
                "id": "SC03",
                "title": "Liều thuốc tự trắc ẩn",
                "duration": 12.0,
                "narration": "Hãy tha thứ cho bản thân trước khi hành động.",
            },
        ],
    }
    (run_dir / "content.json").write_text(json.dumps(content_data, ensure_ascii=False, indent=2), encoding="utf-8")

    if with_audio_output:
        audio_dir = run_dir / "revisions" / "audio" / "1"
        audio_dir.mkdir(parents=True)
        audio_output = {
            "schema_version": "1.0",
            "job_id": job_id,
            "payload": {
                "duration": 37.5,
                "segments": [
                    {"scene_id": "SC01", "start": 0.0, "end": 10.5},
                    {"scene_id": "SC02", "start": 10.5, "end": 25.5},
                    {"scene_id": "SC03", "start": 25.5, "end": 37.5},
                ],
            },
        }
        (audio_dir / "output.json").write_text(json.dumps(audio_output, indent=2), encoding="utf-8")

    return run_dir


def test_init_and_load_release_links(tmp_path: Path) -> None:
    links_file = init_release_links("nao_luoi", root_dir=tmp_path)
    assert links_file.exists()

    data = load_release_links("nao_luoi", root_dir=tmp_path)
    assert "long" in data
    assert data["long"]["job_id"] == "nao-luoi-week1-16x9"
    assert data["long"]["youtube_url"] is None
    assert "shorts" in data
    assert "nao-luoi-week1-9x16-v2" in data["shorts"]

    # Calling init again merges and preserves existing data
    data["long"]["youtube_url"] = "https://youtube.com/watch?v=12345"
    links_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    init_release_links("nao_luoi", root_dir=tmp_path)
    reloaded = load_release_links("nao_luoi", root_dir=tmp_path)
    assert reloaded["long"]["youtube_url"] == "https://youtube.com/watch?v=12345"


def test_build_publish_kit_short_9x16(tmp_path: Path) -> None:
    job_id = "nao-luoi-week1-9x16-v2"
    _setup_mock_run(tmp_path, job_id, "short_9x16")

    # 1. Test with null long URL -> placeholder
    summary = build_publish_kit("nao_luoi", job_id, root_dir=tmp_path)
    assert summary["channel_id"] == "nao_luoi"
    assert summary["format_profile"] == "short_9x16"
    assert summary["long_url"] == PLACEHOLDER_LINK

    publish_dir = Path(summary["publish_dir"])
    tiktok_file = publish_dir / "tiktok.md"
    fb_file = publish_dir / "facebook.md"
    yt_shorts_file = publish_dir / "youtube_shorts.md"

    assert tiktok_file.exists()
    assert fb_file.exists()
    assert yt_shorts_file.exists()

    # Verify TikTok constraints
    tiktok_text = tiktok_file.read_text(encoding="utf-8")
    assert PLACEHOLDER_LINK in tiktok_text
    assert "## 1. Caption" in tiktok_text
    assert "## 2. Bình luận ghim" in tiktok_text
    assert "## 3. Hướng dẫn Bio Link" in tiktok_text

    # Extract caption between code block and check length <= 150 chars
    lines = tiktok_text.splitlines()
    caption_line = ""
    in_block = False
    for line in lines:
        if line.strip() == "```text":
            in_block = True
            continue
        if in_block and line.strip() == "```":
            break
        if in_block:
            caption_line = line.strip()
    assert len(caption_line) <= 150
    assert len(caption_line) > 20

    # Verify YouTube Shorts constraints
    yt_text = yt_shorts_file.read_text(encoding="utf-8")
    assert "## 1. Tiêu đề Shorts" in yt_text
    assert "## 3. Cài đặt Video liên quan" in yt_text
    # Extract short title
    yt_lines = yt_text.splitlines()
    short_title = ""
    in_block = False
    for line in yt_lines:
        if line.strip() == "```text":
            in_block = True
            continue
        if in_block and line.strip() == "```":
            break
        if in_block:
            short_title = line.strip()
    assert len(short_title) <= 55

    # Verify Facebook constraints
    fb_text = fb_file.read_text(encoding="utf-8")
    assert "## 1. Caption" in fb_text
    assert "## 2. First Comment" in fb_text
    assert PLACEHOLDER_LINK in fb_text


def test_build_publish_kit_short_with_real_url(tmp_path: Path) -> None:
    job_id = "nao-luoi-week1-9x16-v2"
    _setup_mock_run(tmp_path, job_id, "short_9x16")

    # Set real URL in release_links.json
    links_file = init_release_links("nao_luoi", root_dir=tmp_path)
    links_data = json.loads(links_file.read_text(encoding="utf-8"))
    links_data["long"]["youtube_url"] = "https://youtu.be/abcdef123"
    links_file.write_text(json.dumps(links_data, indent=2), encoding="utf-8")

    summary = build_publish_kit("nao_luoi", job_id, root_dir=tmp_path)
    assert summary["long_url"] == "https://youtu.be/abcdef123"

    tiktok_text = (Path(summary["publish_dir"]) / "tiktok.md").read_text(encoding="utf-8")
    assert "https://youtu.be/abcdef123" in tiktok_text
    assert PLACEHOLDER_LINK not in tiktok_text


def test_build_publish_kit_long_16x9(tmp_path: Path) -> None:
    job_id = "nao-luoi-week1-16x9"
    _setup_mock_run(tmp_path, job_id, "long_16x9", with_audio_output=True)

    summary = build_publish_kit("nao_luoi", job_id, root_dir=tmp_path)
    assert summary["format_profile"] == "long_16x9"

    yt_long_file = Path(summary["publish_dir"]) / "youtube_long.md"
    assert yt_long_file.exists()
    fb_long_file = Path(summary["publish_dir"]) / "facebook.md"
    assert fb_long_file.exists()

    content = yt_long_file.read_text(encoding="utf-8")
    assert "## 1. Tiêu đề (Title)" in content
    assert "## 2. Mô tả (Description) & Dấu thời gian (Chapters)" in content
    assert "## 4. Cài đặt Màn hình kết thúc" in content
    assert "## 5. Thẻ thông tin" in content
    assert "## 6. Bình luận ghim" in content

    # Check chapters start with 00:00
    assert "00:00 - Bàn học đêm và điện thoại" in content
    assert "00:10 - Báo động hạch hạnh nhân" in content
    assert "00:25 - Liều thuốc tự trắc ẩn" in content

    # Check End screen activation (total 37.5s - 20s = 17.5s -> 00:17)
    assert "00:17" in content

    # Check Info card timestamp
    assert "## 5. Thẻ thông tin (Info Card — Vị trí Mid-CTA)" in content


def test_build_publish_kit_long_without_audio_output(tmp_path: Path) -> None:
    job_id = "nao-luoi-week1-16x9"
    _setup_mock_run(tmp_path, job_id, "long_16x9", with_audio_output=False)

    summary = build_publish_kit("nao_luoi", job_id, root_dir=tmp_path)
    yt_long_file = Path(summary["publish_dir"]) / "youtube_long.md"
    assert yt_long_file.exists()
    fb_long_file = Path(summary["publish_dir"]) / "facebook.md"
    assert fb_long_file.exists()

    content = yt_long_file.read_text(encoding="utf-8")
    # Even without measured output.json, chapters must start at 00:00
    assert "00:00 - Bàn học đêm và điện thoại" in content


def test_assert_no_banned_cta() -> None:
    # Clean text passes
    assert_no_banned_cta("Chia sẻ suy nghĩ của bạn bên dưới cùng Não Lười nhé.")

    # Banned phrases raise ValueError
    for phrase in BANNED_CTA_PHRASES:
        with pytest.raises(ValueError, match="BANNED_CTA_IN_PUBLISH_KIT"):
            assert_no_banned_cta(f"Nhớ {phrase} ngay để theo dõi video mới nhất!")


def test_format_timestamp() -> None:
    assert format_timestamp(0.0) == "00:00"
    assert format_timestamp(65.4) == "01:05"
    assert format_timestamp(3665.0) == "01:01:05"
