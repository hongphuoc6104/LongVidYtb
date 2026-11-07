#!/usr/bin/env python3
"""Video Pilot — Multi-Platform Publish Kit Generator.

Generates localized, platform-specific publication kits (Markdown)
under video/<job_id>/publish/ adhering to Video Pilot Anti-Flop & CTA guidelines:

For short_9x16:
- tiktok.md: Caption <= 150 chars with hook, 3-5 hashtags, pinned comment pointing to long, bio-link instruction
- facebook.md: Caption with link to long, first-comment text
- youtube_shorts.md: Title <= 55 chars, description, instruction to set "Related video" = long URL

For long_16x9:
- youtube_long.md: Title, description with chapters computed from measured scene start times
  in sys/runs/<job>/revisions/audio/1/output.json (when present), tags, end-screen instructions
  for the final 20s, a card at mid_cta timestamp, pinned comment

Release links come from sys/channels/<id>/release_links.json with placeholder:
[CHÈN LINK VIDEO DÀI KHI ĐĂNG]
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SYS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from channels.registry import get_channel  # noqa: E402

PLACEHOLDER_LINK = "[CHÈN LINK VIDEO DÀI KHI ĐĂNG]"

# Banned CTA phrases per contract §3.4
BANNED_CTA_PHRASES: Tuple[str, ...] = (
    "đừng quên like",
    "nhấn chuông",
    "bấm chuông",
    "like share",
    "like và share",
    "like, share",
    "subscribe",
    "đăng ký kênh",
    "ấn theo dõi ngay",
    "bấm theo dõi ngay",
    "hãy like",
    "nhớ like",
    "để ủng hộ kênh",
)


def assert_no_banned_cta(text: str, context: str = "") -> None:
    """Validate that text contains zero banned pushy CTA phrases."""
    text_lower = text.lower()
    for phrase in BANNED_CTA_PHRASES:
        if phrase in text_lower:
            raise ValueError(f"BANNED_CTA_IN_PUBLISH_KIT ({context}): found prohibited phrase '{phrase}'")


def format_timestamp(seconds: float) -> str:
    """Format seconds into MM:SS or HH:MM:SS for YouTube chapters."""
    total_sec = max(0, int(math.floor(seconds)))
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def get_release_links_path(channel_id: str, root_dir: Optional[Path] = None) -> Path:
    """Resolve path to sys/channels/<id>/release_links.json."""
    effective_root = root_dir or REPO_ROOT
    return effective_root / "sys" / "channels" / channel_id / "release_links.json"


def init_release_links(channel_id: str, root_dir: Optional[Path] = None) -> Path:
    """Create a release_links.json template if not already present."""
    channel = get_channel(channel_id)
    slug = channel.slug
    links_file = get_release_links_path(channel_id, root_dir)
    links_file.parent.mkdir(parents=True, exist_ok=True)

    template: Dict[str, Any] = {
        "long": {
            "job_id": f"{slug}-week1-16x9",
            "youtube_url": None,
        },
        "shorts": {
            f"{slug}-week1-9x16-v2": {
                "tiktok_url": None,
                "facebook_url": None,
                "youtube_shorts_url": None,
            }
        },
    }

    if links_file.exists():
        try:
            existing = json.loads(links_file.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                # Merge existing without overwriting valid URLs
                if "long" in existing and isinstance(existing["long"], dict):
                    template["long"].update(existing["long"])
                if "shorts" in existing and isinstance(existing["shorts"], dict):
                    for k, v in existing["shorts"].items():
                        if k not in template["shorts"]:
                            template["shorts"][k] = v
                        elif isinstance(v, dict):
                            template["shorts"][k].update(v)
        except Exception:
            pass

    links_file.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return links_file


def load_release_links(channel_id: str, root_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load release_links.json, falling back to empty template structure."""
    links_file = get_release_links_path(channel_id, root_dir)
    if links_file.exists():
        try:
            return json.loads(links_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"long": {"job_id": f"{get_channel(channel_id).slug}-week1-16x9", "youtube_url": None}, "shorts": {}}


def find_job_run_directory(job_id: str, root_dir: Optional[Path] = None) -> Path:
    """Locate sys/runs/<job_id> in current workspace, root_dir, or channel worktrees."""
    candidates: List[Path] = []
    if root_dir:
        candidates.append(root_dir / "sys" / "runs" / job_id)
    candidates.append(Path.cwd() / "sys" / "runs" / job_id)
    candidates.append(REPO_ROOT / "sys" / "runs" / job_id)

    # Search in channel worktrees if slug can be inferred
    parts = job_id.split("-")
    if len(parts) >= 2:
        potential_slug = parts[0]
        candidates.append(REPO_ROOT.parent / "vp-channels" / f"channel-{potential_slug}" / "sys" / "runs" / job_id)

    for c in candidates:
        if c.exists() and (c / "content.json").exists():
            return c

    # Fallback to candidate 0 or REPO_ROOT
    return candidates[0] if candidates else (REPO_ROOT / "sys" / "runs" / job_id)


def load_job_data(job_id: str, root_dir: Optional[Path] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Load brief.json and content.json for a job."""
    run_dir = find_job_run_directory(job_id, root_dir)
    content_file = run_dir / "content.json"
    brief_file = run_dir / "brief.json"

    if not content_file.exists():
        raise FileNotFoundError(f"Missing content.json for job '{job_id}' at {content_file}")

    content = json.loads(content_file.read_text(encoding="utf-8"))
    brief = {}
    if brief_file.exists():
        try:
            brief = json.loads(brief_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    return brief, content


def extract_chapters_from_audio_output(
    audio_output_file: Path,
    content_scenes: List[Dict[str, Any]],
) -> Tuple[List[str], Optional[float], float]:
    """Parse measured scene start times from revisions/audio/1/output.json.

    Enforces strict YouTube chapter rules:
    - Every chapter starts at 00:00.
    - Every chapter interval is strictly >= 10 seconds.
    - If Scene 1 is < 10s, merges Scene 1 and Scene 2 so the 2nd timestamp is >= 00:10.

    Returns:
        chapters: List of 'MM:SS - Scene Title' strings starting at 00:00.
        mid_cta_timestamp: Measured start time of scene around 35-45% of runtime.
        total_duration: Total audio duration in seconds.
    """
    if not content_scenes:
        return ["00:00 - Giới thiệu"], 0.0, 0.0

    raw_candidates: List[Tuple[float, str]] = []
    total_duration = 0.0

    if not audio_output_file.exists():
        # Fallback estimation without audio output
        cur_time = 0.0
        for idx, sc in enumerate(content_scenes, 1):
            title = sc.get("title") or f"Phần {idx}"
            raw_candidates.append((cur_time, title))
            cur_time += float(sc.get("duration", 8.0))
        total_duration = cur_time
    else:
        audio_data = json.loads(audio_output_file.read_text(encoding="utf-8"))
        payload = audio_data.get("payload", {})
        total_duration = float(payload.get("duration", 0.0))
        segments = payload.get("segments", [])

        scene_starts: Dict[str, float] = {}
        for seg in segments:
            sc_id = seg.get("scene_id")
            start = float(seg.get("start", 0.0))
            if sc_id and sc_id not in scene_starts:
                scene_starts[sc_id] = start

        for idx, sc in enumerate(content_scenes, 1):
            sc_id = sc.get("id", f"SC{idx:02d}")
            title = sc.get("title", f"Phần {idx}")
            start_sec = scene_starts.get(sc_id, 0.0)
            raw_candidates.append((start_sec, title))

    # Enforce YouTube chapter interval: strictly >= 10s between consecutive chapters
    MIN_CHAPTER_GAP_SEC = 10.0
    emitted: List[Tuple[float, str]] = []

    for idx, (cand_sec, cand_title) in enumerate(raw_candidates):
        if idx == 0:
            emitted.append((0.0, cand_title))
            continue

        last_sec, last_title = emitted[-1]
        # In YouTube, timestamps are rounded down to seconds by format_timestamp (MM:SS).
        # Interval between consecutive formatted timestamps must be >= 10 seconds.
        gap_sec = math.floor(cand_sec) - math.floor(last_sec)
        if gap_sec < MIN_CHAPTER_GAP_SEC:
            # Merge with previous chapter so we never emit an interval < 10s
            combined_title = f"{last_title} & {cand_title}"
            if len(combined_title) <= 60 and last_title.count("&") < 2:
                emitted[-1] = (last_sec, combined_title)
        else:
            emitted.append((cand_sec, cand_title))

    # Format chapters: first is always 00:00
    ordered_chapters: List[str] = [
        f"{format_timestamp(t) if i > 0 else '00:00'} - {title}"
        for i, (t, title) in enumerate(emitted)
    ]

    # Find mid-CTA scene (roughly 35-45% of total runtime)
    target_mid = total_duration * 0.40
    closest_sc_time: Optional[float] = None
    min_diff = float("inf")
    for start_sec, _ in raw_candidates:
        diff = abs(start_sec - target_mid)
        if diff < min_diff:
            min_diff = diff
            closest_sc_time = start_sec

    return ordered_chapters, closest_sc_time or target_mid, total_duration


def build_tiktok_kit(
    channel_name: str,
    channel_slug: str,
    job_id: str,
    topic: str,
    packaging: Dict[str, Any],
    long_url: str,
) -> str:
    """Build publish/tiktok.md: caption <= 150 chars with hook, 3-5 hashtags, bio-link, pinned comment."""
    hook = packaging.get("visual_hook") or topic
    # Clean hook to make it short and punchy
    hook = hook.split("?")[0].strip()
    if not hook.endswith("?"):
        hook += "?"

    # Select 3-4 hashtags
    raw_tags = packaging.get("seo_keywords", [])
    slug_tag = f"#{channel_slug.replace('-', '')}"
    tags = [slug_tag]
    for t in raw_tags:
        cleaned = re.sub(r"[^a-zA-Z0-9_\u00C0-\u024F\u1EA0-\u1EF9]", "", t).lower()
        if cleaned and f"#{cleaned}" not in tags and len(tags) < 4:
            tags.append(f"#{cleaned}")
    if len(tags) < 3:
        tags.extend(["#kienthuc", "#learnontiktok"])
        tags = tags[:4]

    tags_str = " ".join(tags)

    # Compose caption with maximum 150 chars constraint
    # Reserve space for tags_str + space
    max_hook_len = 150 - len(tags_str) - 2
    if len(hook) > max_hook_len:
        trimmed_hook = hook[: max(0, max_hook_len - 3)].rstrip() + "...?"
        caption = f"{trimmed_hook} {tags_str}".strip()
    else:
        caption = f"{hook} {tags_str}".strip()

    # Double-check length constraint
    if len(caption) > 150:
        caption = caption[:147] + "..."

    pinned_comment = f"Bản giải thích đầy đủ và chi tiết hơn mình để ở video dài nhé: {long_url}"
    assert_no_banned_cta(caption, "tiktok caption")
    assert_no_banned_cta(pinned_comment, "tiktok pinned comment")

    md = f"""# Kế Hoạch Xuất Bản TikTok — {job_id}

## 1. Caption (Tối đa 150 ký tự)
```text
{caption}
```
*(Số ký tự hiện tại: {len(caption)} / 150)*

## 2. Bình luận ghim (Pinned Comment)
```text
{pinned_comment}
```

## 3. Hướng dẫn Bio Link
1. Cập nhật liên kết video dài vào phần Bio trang TikTok của **{channel_name}**:
   `{long_url}`
2. Khi người xem hỏi thêm trong phần bình luận, nhẹ nhàng điều hướng người xem xem bản đầy đủ qua link Bio.
"""
    return md


def build_facebook_kit(
    channel_name: str,
    channel_slug: str,
    job_id: str,
    topic: str,
    packaging: Dict[str, Any],
    long_url: str,
) -> str:
    """Build publish/facebook.md: caption with link to long, first-comment text."""
    title = packaging.get("youtube_title") or topic
    visual_hook = packaging.get("visual_hook") or "Một góc nhìn bất ngờ ít người để ý."
    first_comment = f"👉 Bản phân tích đầy đủ và chi tiết từng bước xem tại đây nhé: {long_url}"

    fb_caption = f"""{title}

{visual_hook}

Nếu bạn muốn xem trọn vẹn luận điểm và các dẫn chứng đầy đủ, xem video dài tại: {long_url}"""

    assert_no_banned_cta(fb_caption, "facebook caption")
    assert_no_banned_cta(first_comment, "facebook first comment")

    md = f"""# Kế Hoạch Xuất Bản Facebook Reels — {job_id}

## 1. Caption (Mô tả bài đăng Reels)
```text
{fb_caption}
```

## 2. First Comment (Bình luận đầu tiên gắn link video dài)
```text
{first_comment}
```

## 3. Lưu ý khi đăng Facebook Reels
- Dán nội dung bình luận đầu tiên ngay sau khi video được đăng tải công khai.
- Không chỉnh sửa nội dung bài đăng quá nhiều lần trong 30 phút đầu tiên.
"""
    return md


def build_youtube_shorts_kit(
    channel_name: str,
    channel_slug: str,
    job_id: str,
    topic: str,
    packaging: Dict[str, Any],
    long_url: str,
) -> str:
    """Build publish/youtube_shorts.md: title <= 55 chars, description, Related video instruction."""
    raw_title = packaging.get("youtube_title") or topic
    # Enforce title <= 55 chars
    if len(raw_title) > 55:
        short_title = raw_title[:52].rstrip() + "..."
    else:
        short_title = raw_title

    desc = f"""{topic}

Bản phân tích đầy đủ và chi tiết có tại video dài của kênh {channel_name}.
Xem video liên quan: {long_url}

#Shorts #{channel_slug.replace('-', '')}"""

    pinned_comment = f"Bản phân tích đầy đủ chi tiết hơn mình để tại đây nha: {long_url}"

    assert_no_banned_cta(short_title, "youtube shorts title")
    assert_no_banned_cta(desc, "youtube shorts description")
    assert_no_banned_cta(pinned_comment, "youtube shorts pinned comment")

    md = f"""# Kế Hoạch Xuất Bản YouTube Shorts — {job_id}

## 1. Tiêu đề Shorts (Tối đa 55 ký tự)
```text
{short_title}
```
*(Độ dài tiêu đề: {len(short_title)} / 55 ký tự)*

## 2. Mô tả (Description)
```text
{desc}
```

## 3. Cài đặt Video liên quan (Related Video)
Trong **YouTube Studio** khi tải Shorts lên:
1. Tại thẻ **Chi tiết** -> mục **Video liên quan (Related video)**.
2. Chọn đúng video dài tương ứng:
   `{long_url}`
3. Khi người xem xem Shorts trên điện thoại, nút liên kết đến video dài sẽ hiển thị trực tiếp phía trên tiêu đề.

## 4. Bình luận ghim (Pinned Comment)
```text
{pinned_comment}
```
"""
    return md


def build_youtube_long_kit(
    channel_name: str,
    channel_slug: str,
    job_id: str,
    topic: str,
    packaging: Dict[str, Any],
    chapters: List[str],
    mid_cta_time: float,
    total_duration: float,
    long_url: str,
) -> str:
    """Build publish/youtube_long.md: title, description with chapters, tags, end-screen, card, pinned comment."""
    title = packaging.get("youtube_title") or topic
    seo_keywords = packaging.get("seo_keywords", [])
    tags_str = ", ".join(seo_keywords) if seo_keywords else f"{channel_name}, {topic}"

    chapters_block = "\n".join(chapters)
    end_screen_start = format_timestamp(max(0.0, total_duration - 20.0))
    mid_cta_str = format_timestamp(mid_cta_time)

    has_zero_chapter = any(ch.strip().startswith("00:00") for ch in chapters)
    intro_prefix = "" if has_zero_chapter else "00:00 - Giới thiệu\n"

    desc = f"""{topic}

{intro_prefix}{chapters_block}

---
Chào mừng bạn đến với kênh chính thức của {channel_name}.
Những câu chuyện và góc nhìn đằng sau hiện tượng được mổ xẻ dưới lăng kính khoa học và trải nghiệm gần gũi.

#kienthuc #{channel_slug.replace('-', '')}"""

    pinned_comment = (
        f"Góc nhìn nào trong video này khiến bạn thấy bất ngờ hoặc đồng cảm nhất? "
        f"Chia sẻ suy nghĩ của bạn bên dưới cùng {channel_name} nhé."
    )

    assert_no_banned_cta(title, "youtube long title")
    assert_no_banned_cta(desc, "youtube long description")
    assert_no_banned_cta(pinned_comment, "youtube long pinned comment")

    md = f"""# Kế Hoạch Xuất Bản YouTube Dài (16:9) — {job_id}

## 1. Tiêu đề (Title)
```text
{title}
```

## 2. Mô tả (Description) & Dấu thời gian (Chapters)
```text
{desc}
```

## 3. Thẻ từ khóa (Tags)
```text
{tags_str}
```

## 4. Cài đặt Màn hình kết thúc (End Screen — 20 giây cuối)
- **Thời điểm kích hoạt**: Từ **{end_screen_start}** đến hết video.
- **Thành phần gợi ý**:
  1. *Video phù hợp nhất với người xem* (hoặc video mới nhất).
  2. *Danh sách phát chủ đề liên quan*.
  3. *Nút Đăng ký kênh {channel_name}*.
- Đảm bảo các khung hình chữ nhật của End Screen không đè lên hình vẽ nhân vật chính ở giữa khung hình.

## 5. Thẻ thông tin (Info Card — Vị trí Mid-CTA)
- **Thời điểm chèn thẻ**: **{mid_cta_str}** (ngay sau luận điểm trọng tâm đầu tiên).
- **Loại thẻ**: Video liên quan hoặc Danh sách phát kiến thức của kênh.
- **Lời kêu gọi trên thẻ**: "Xem thêm chủ đề liên quan".

## 6. Bình luận ghim (Pinned Comment)
```text
{pinned_comment}
```
"""
    return md


def build_facebook_long_kit(
    channel_name: str,
    channel_slug: str,
    job_id: str,
    topic: str,
    packaging: Dict[str, Any],
    long_url: str,
) -> str:
    """Build publish/facebook.md for Long 16:9: caption, key takeaway, first comment."""
    title = packaging.get("youtube_title") or topic
    visual_hook = packaging.get("visual_hook") or "Một góc nhìn bất ngờ đằng sau hiện tượng ít ai để ý."
    first_comment = (
        f"Góc nhìn nào trong video này khiến bạn thấy bất ngờ hoặc đồng cảm nhất? "
        f"Chia sẻ suy nghĩ của bạn bên dưới cùng {channel_name} nhé."
    )

    fb_caption = f"""{title}

{visual_hook}

Chào mừng bạn đến với kênh chính thức của {channel_name}. Video này mổ xẻ những góc nhìn sâu sắc và câu chuyện thực tế dưới lăng kính khoa học.

#kienthuc #{channel_slug.replace('-', '')}"""

    assert_no_banned_cta(fb_caption, "facebook long caption")
    assert_no_banned_cta(first_comment, "facebook long first comment")

    md = f"""# Kế Hoạch Xuất Bản Facebook Video (16:9) — {job_id}

## 1. Caption (Mô tả bài đăng Video 16:9)
```text
{fb_caption}
```

## 2. First Comment (Bình luận tương tác đầu tiên)
```text
{first_comment}
```

## 3. Lưu ý khi đăng Facebook Video
- Đăng tải video tỷ lệ 16:9 chuẩn full HD.
- Gắn phụ đề SRT (subtitles.srt) hoặc bật tính năng phụ đề tự động.
- Ghim bình luận tương tác để kích thích thảo luận văn minh từ cộng đồng.
"""
    return md


def build_publish_kit(
    channel_id: str,
    job_id: str,
    out_dir: Optional[Path] = None,
    root_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Generate all platform publish kit markdown files for a job."""
    channel = get_channel(channel_id)
    effective_root = root_dir or REPO_ROOT

    # 1. Load job brief and content
    brief, content = load_job_data(job_id, root_dir)
    topic = content.get("topic") or brief.get("topic") or job_id
    packaging = brief.get("packaging") or content.get("packaging") or {}

    # Detect format profile
    fmt = brief.get("format_profile") or content.get("format_profile")
    if not fmt:
        if "16x9" in job_id or brief.get("aspect_ratio") == "16:9":
            fmt = "long_16x9"
        else:
            fmt = "short_9x16"

    # 2. Load release links
    links = load_release_links(channel_id, root_dir)
    long_info = links.get("long", {})
    long_url = long_info.get("youtube_url") or PLACEHOLDER_LINK

    # 3. Determine output directory: video/<job_id>/publish/
    if out_dir is None:
        publish_dir = effective_root / "video" / job_id / "publish"
    else:
        publish_dir = Path(out_dir).resolve()
    publish_dir.mkdir(parents=True, exist_ok=True)

    generated_files: List[Path] = []

    if fmt == "short_9x16":
        # Generate TikTok kit
        tiktok_content = build_tiktok_kit(
            channel_name=channel.name,
            channel_slug=channel.slug,
            job_id=job_id,
            topic=topic,
            packaging=packaging,
            long_url=long_url,
        )
        tiktok_file = publish_dir / "tiktok.md"
        tiktok_file.write_text(tiktok_content, encoding="utf-8")
        generated_files.append(tiktok_file)

        # Generate Facebook kit
        fb_content = build_facebook_kit(
            channel_name=channel.name,
            channel_slug=channel.slug,
            job_id=job_id,
            topic=topic,
            packaging=packaging,
            long_url=long_url,
        )
        fb_file = publish_dir / "facebook.md"
        fb_file.write_text(fb_content, encoding="utf-8")
        generated_files.append(fb_file)

        # Generate YouTube Shorts kit
        yt_shorts_content = build_youtube_shorts_kit(
            channel_name=channel.name,
            channel_slug=channel.slug,
            job_id=job_id,
            topic=topic,
            packaging=packaging,
            long_url=long_url,
        )
        yt_file = publish_dir / "youtube_shorts.md"
        yt_file.write_text(yt_shorts_content, encoding="utf-8")
        generated_files.append(yt_file)

    else:
        # Long 16:9 format
        run_dir = find_job_run_directory(job_id, root_dir)
        audio_output_file = run_dir / "revisions" / "audio" / "1" / "output.json"
        content_scenes = content.get("scenes", [])

        chapters, mid_cta_time, total_duration = extract_chapters_from_audio_output(
            audio_output_file,
            content_scenes,
        )

        yt_long_content = build_youtube_long_kit(
            channel_name=channel.name,
            channel_slug=channel.slug,
            job_id=job_id,
            topic=topic,
            packaging=packaging,
            chapters=chapters,
            mid_cta_time=mid_cta_time or (total_duration * 0.4),
            total_duration=total_duration,
            long_url=long_url,
        )
        yt_long_file = publish_dir / "youtube_long.md"
        yt_long_file.write_text(yt_long_content, encoding="utf-8")
        generated_files.append(yt_long_file)

        # Generate Facebook Video 16:9 kit
        fb_long_content = build_facebook_long_kit(
            channel_name=channel.name,
            channel_slug=channel.slug,
            job_id=job_id,
            topic=topic,
            packaging=packaging,
            long_url=long_url,
        )
        fb_long_file = publish_dir / "facebook.md"
        fb_long_file.write_text(fb_long_content, encoding="utf-8")
        generated_files.append(fb_long_file)

    return {
        "channel_id": channel_id,
        "job_id": job_id,
        "format_profile": fmt,
        "publish_dir": str(publish_dir),
        "files": [str(p) for p in generated_files],
        "long_url": long_url,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Vietnamese publication kit for Video Pilot deliverables")
    parser.add_argument("--channel", required=True, help="Channel identifier (e.g. nao_luoi)")
    parser.add_argument("--job", help="Job identifier (e.g. nao-luoi-week1-9x16-v2 or nao-luoi-week1-16x9)")
    parser.add_argument("--out", type=Path, default=None, help="Destination directory (default: video/<job_id>/publish/)")
    parser.add_argument("--root", type=Path, default=None, help="Workspace root directory")
    parser.add_argument("--init-links", action="store_true", help="Initialize release_links.json template")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.init_links:
        path = init_release_links(args.channel, args.root)
        print(json.dumps({"status": "INITIALIZED", "path": str(path)}, indent=2))
        if not args.job:
            return

    if not args.job:
        parser.error("--job is required unless only --init-links is specified")

    try:
        summary = build_publish_kit(
            channel_id=args.channel,
            job_id=args.job,
            out_dir=args.out,
            root_dir=args.root,
        )
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    except Exception as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
