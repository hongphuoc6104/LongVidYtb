#!/usr/bin/env python3
"""Batch YouTube Publisher for 20 Vietnamese Long (16:9) Videos.

Orchestrates batch publishing from video/publish_manifest_20_long.json (or scanned directories),
enforcing pre-publish validation, Review Gate approval, Controlled Concurrency (max 2-3 workers),
Anti-IP-Ban Staggered Browser Launches, and Incremental Atomic Reporting.

Pre-Publish Gates:
1. MP4 video file exists.
2. .srt subtitles file exists.
3. Custom thumbnail exists (1280x720, < 2MB).
4. Title length <= 55 characters.
5. Zero banned CTAs in title, description, or pinned comment (assert_no_banned_cta).
6. Stale MP4 check: MP4 mtime >= spec mtime (reject stale MP4s unless --allow-stale).
7. Review Gate: Registers job and sets APPROVED if --approve-batch, else enforces check_publish_permission.
8. Resume-Safe: Skips already PUBLISHED channels unless --force.
"""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_cdp.resource_locks import stagger_cross_process_action
from sys.tools.build_publish_kit import assert_no_banned_cta
from sys.tools.publish_youtube_cdp import parse_metadata_file, publish_single_video
from sys.tools.review_queue_manager import (
    check_publish_permission,
    register_video_for_review,
    set_review_decision,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("publish_20_long_batch")

DEFAULT_MANIFEST_PATH = REPO_ROOT / "video" / "publish_manifest_20_long.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "video" / "published_20_long_report.json"
DEFAULT_CHANNEL_MAP_PATH = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"


def validate_long_video_assets(
    channel_slug: str,
    channel_data: dict[str, Any],
    allow_stale: bool = False,
    root_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Validate all assets for a channel Long video before initiating publication."""
    base_root = root_dir or REPO_ROOT
    norm_slug = channel_slug.strip().replace("-", "_").lower()

    # 1. Paths resolution
    rel_video = channel_data.get("video_path") or f"video/vn_pilot_{norm_slug}_long/vn_pilot_{norm_slug}_long_16x9.mp4"
    rel_srt = channel_data.get("srt_path") or f"video/vn_pilot_{norm_slug}_long/vn_pilot_{norm_slug}_long_16x9.srt"
    rel_thumb = channel_data.get("thumbnail_path") or f"video/vn_pilot_{norm_slug}_long/vn_pilot_{norm_slug}_long_thumbnail_16x9.png"
    rel_md = channel_data.get("youtube_long_md_path") or f"video/vn_pilot_{norm_slug}_long/publish/youtube_long.md"

    video_path = base_root / rel_video
    srt_path = base_root / rel_srt
    thumb_path = base_root / rel_thumb
    md_path = base_root / rel_md

    # Check existence
    if not video_path.is_file():
        raise FileNotFoundError(f"MISSING_MP4: Video file not found: {video_path}")
    if not srt_path.is_file():
        raise FileNotFoundError(f"MISSING_SRT: Subtitles file not found: {srt_path}")
    if not thumb_path.is_file():
        raise FileNotFoundError(f"MISSING_THUMBNAIL: Thumbnail file not found: {thumb_path}")

    # 2. Thumbnail dimension & size check
    thumb_size = thumb_path.stat().st_size
    if thumb_size > 2_000_000:
        raise ValueError(f"THUMBNAIL_TOO_LARGE: Thumbnail {thumb_path} is {thumb_size} bytes (max 2,000,000 bytes)")

    try:
        with Image.open(thumb_path) as im:
            if im.size != (1280, 720):
                raise ValueError(f"INVALID_THUMBNAIL_DIMENSIONS: expected (1280, 720), got {im.size} in {thumb_path}")
    except Exception as img_err:
        if "INVALID_THUMBNAIL_DIMENSIONS" in str(img_err):
            raise
        raise ValueError(f"CORRUPT_THUMBNAIL: Could not open {thumb_path}: {img_err}") from img_err

    # 3. Metadata & Title validation
    title = channel_data.get("youtube_title") or channel_data.get("title") or ""
    description = channel_data.get("description") or ""
    tags = channel_data.get("tags_str") or channel_data.get("tags") or ""
    language = channel_data.get("language") or "Tiếng Việt"
    category = channel_data.get("category") or "Giáo dục"
    pinned_comment = channel_data.get("pinned_comment") or ""

    if md_path.is_file():
        parsed_md = parse_metadata_file(md_path)
        if not title:
            title = parsed_md.get("title", "")
        if not description:
            description = parsed_md.get("description", "")
        if not tags:
            tags = parsed_md.get("tags", "")
        if parsed_md.get("language"):
            language = parsed_md["language"]
        if parsed_md.get("category"):
            category = parsed_md["category"]
        if parsed_md.get("pinned_comment"):
            pinned_comment = parsed_md["pinned_comment"]

    if not title:
        raise ValueError(f"EMPTY_TITLE: No title found for channel {norm_slug}")

    if len(title) > 55:
        raise ValueError(f"TITLE_TOO_LONG: Title has {len(title)} chars (limit 55): '{title}'")

    # 4. Zero banned CTAs check
    assert_no_banned_cta(title)
    if description:
        assert_no_banned_cta(description)
    if pinned_comment:
        assert_no_banned_cta(pinned_comment)

    # 5. Stale MP4 check
    spec_candidates = [
        video_path.parent / f"{norm_slug}_long_aligned_spec.json",
        video_path.parent / f"{norm_slug}_long_explainer_spec.json",
        base_root / f"sys/runs/vn_pilot_{norm_slug}_long/brief.json",
        base_root / f"sys/runs/vn_pilot_{norm_slug}_long/content.json",
    ]
    for sc in spec_candidates:
        if sc.is_file():
            if not allow_stale and video_path.stat().st_mtime < sc.stat().st_mtime:
                raise ValueError(
                    f"STALE_MP4_REJECTED: Video {video_path} (mtime={video_path.stat().st_mtime}) "
                    f"is older than spec file {sc} (mtime={sc.stat().st_mtime}). "
                    "Rendered before latest spec update! Use --allow-stale to force."
                )

    return {
        "channel_id": norm_slug,
        "video_path": str(video_path),
        "srt_path": str(srt_path),
        "thumbnail_path": str(thumb_path),
        "md_path": str(md_path) if md_path.is_file() else None,
        "title": title,
        "description": description,
        "tags": tags,
        "language": language,
        "category": category,
        "pinned_comment": pinned_comment,
    }


def update_channel_release_links(
    channel_slug: str,
    video_url: str,
    job_id: Optional[str] = None,
    root_dir: Optional[Path] = None,
) -> None:
    """Update sys/channels/<slug>/release_links.json with published YouTube long URL."""
    base_root = root_dir or REPO_ROOT
    norm_slug = channel_slug.strip().replace("-", "_").lower()
    rel_path = base_root / "sys" / "channels" / norm_slug / "release_links.json"
    if not rel_path.is_file():
        return

    lock_file = rel_path.with_suffix(".lock")
    try:
        with open(lock_file, "w", encoding="utf-8") as lk:
            fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
            try:
                data = json.loads(rel_path.read_text(encoding="utf-8"))
                if "long" not in data or not isinstance(data["long"], dict):
                    data["long"] = {}
                if job_id:
                    data["long"]["job_id"] = job_id
                data["long"]["youtube_url"] = video_url
                rel_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                logger.info("Updated release_links.json for %s with %s", norm_slug, video_url)
            finally:
                fcntl.flock(lk.fileno(), fcntl.LOCK_UN)
    except Exception as exc:
        logger.warning("Could not update release_links.json for %s: %s", norm_slug, exc)


def update_youtube_channel_map(
    channel_slug: str,
    video_url: str,
    title: str,
    root_dir: Optional[Path] = None,
) -> None:
    """Atomic update of sys/channels/youtube_channel_map.json."""
    base_root = root_dir or REPO_ROOT
    map_file = base_root / "sys" / "channels" / "youtube_channel_map.json"
    if not map_file.is_file():
        return

    norm_slug = channel_slug.strip().replace("-", "_").lower()
    lock_file = map_file.with_suffix(".lock")
    try:
        with open(lock_file, "w", encoding="utf-8") as lk:
            fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
            try:
                data = json.loads(map_file.read_text(encoding="utf-8"))
                channels = data.get("channels", {})
                if norm_slug in channels:
                    entry = channels[norm_slug]
                    entry["long_video_url"] = video_url
                    history = entry.setdefault("published_videos", [])
                    existing_urls = {v.get("video_url") for v in history if isinstance(v, dict)}
                    if video_url not in existing_urls:
                        history.append({
                            "video_url": video_url,
                            "title": title,
                            "format": "long_16x9",
                            "related_video_url": None,
                            "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        })
                    map_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    logger.info("Updated youtube_channel_map.json for %s with %s", norm_slug, video_url)
            finally:
                fcntl.flock(lk.fileno(), fcntl.LOCK_UN)
    except Exception as exc:
        logger.warning("Could not update youtube_channel_map.json for %s: %s", norm_slug, exc)


def publish_single_long_channel(
    channel_slug: str,
    channel_data: dict[str, Any],
    channel_map: dict[str, Any],
    approve_batch: bool = False,
    allow_stale: bool = False,
    dry_run: bool = False,
    visibility: str = "PUBLIC",
    root_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Validate, approve, and publish a single Long 16:9 video."""
    base_root = root_dir or REPO_ROOT
    norm_slug = channel_slug.strip().replace("-", "_").lower()
    job_id = f"vn_pilot_{norm_slug}_long"

    # Step 1: Asset Validation
    validated = validate_long_video_assets(
        norm_slug,
        channel_data,
        allow_stale=allow_stale,
        root_dir=base_root,
    )

    # Step 2: Review Gate Integration
    effective_queue_path = (base_root / "sys" / "channels" / "video_review_queue.json") if root_dir is not None else None
    if approve_batch:
        try:
            register_video_for_review(
                job_id=job_id,
                channel_id=norm_slug,
                format_profile="long_16x9",
                title=validated["title"],
                mp4_path=validated["video_path"],
                thumbnail_path=validated["thumbnail_path"],
                srt_path=validated["srt_path"],
                queue_path=effective_queue_path,
            )
            set_review_decision(job_id=job_id, status="APPROVED", queue_path=effective_queue_path)
            logger.info("Marked %s as APPROVED in Review Dashboard", job_id)
        except Exception as rev_err:
            logger.warning("Review queue update non-fatal error for %s: %s", job_id, rev_err)
    else:
        allowed, reason = check_publish_permission(job_id, queue_path=effective_queue_path)
        if not allowed:
            raise RuntimeError(
                f"PUBLISH_BLOCKED_BY_REVIEW_GATE: Job '{job_id}' is not APPROVED (status={reason}). "
                "Use --approve-batch to automatically approve."
            )

    # Profile config resolution
    ch_entry = channel_map.get("channels", {}).get(norm_slug, {})
    expected_uc = ch_entry.get("youtube_channel_id") or channel_data.get("youtube_channel_id")
    profile_cfg = {
        "id": ch_entry.get("profile_id", "profile_13"),
        "port": ch_entry.get("cdp_port", 9234),
        "directory": ch_entry.get("directory", "Profile 14"),
        "user_data_dir": ch_entry.get("user_data_dir", str(Path.home() / ".config/google-chrome-cdp-profile14")),
        "email": ch_entry.get("email", ""),
        "handle": ch_entry.get("handle"),
        "youtube_channel_id": expected_uc,
    }

    qa_dir = base_root / "video" / "qa_publish_20_long"
    qa_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = qa_dir / f"{job_id}_share.png"
    edit_screenshot_path = qa_dir / f"{job_id}_edit.png"

    if dry_run:
        logger.info("[DRY-RUN] Publishing %s (title='%s')", norm_slug, validated["title"])
        mock_url = f"https://youtu.be/dryrun_{norm_slug}_16x9"
        update_youtube_channel_map(norm_slug, mock_url, validated["title"], root_dir=base_root)
        update_channel_release_links(norm_slug, mock_url, job_id=job_id, root_dir=base_root)
        return {
            "status": "PUBLISHED",
            "channel_id": norm_slug,
            "channel_name": channel_data.get("channel_name", norm_slug),
            "video_url": mock_url,
            "title": validated["title"],
            "visibility": visibility,
            "thumbnail_uploaded": True,
            "subtitles_uploaded": True,
            "screenshot_path": str(screenshot_path),
            "edit_screenshot_path": str(edit_screenshot_path),
            "oembed_ok": True,
            "oembed_pending_processing": False,
            "edit_verification": {
                "live_title": validated["title"],
                "description_length": len(validated["description"]),
                "has_chapters_00_00": True,
                "has_custom_thumbnail": True,
                "tags_chip_count": 10,
                "subtitles_present": True,
                "visibility_text": "Công khai",
                "is_draft_or_private": False,
            },
            "dry_run": True,
        }

    # Live Publish
    logger.info("Launching Chrome for %s with anti-ban stagger...", norm_slug)
    stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)

    publish_res = asyncio.run(
        publish_single_video(
            video_path=validated["video_path"],
            title=validated["title"],
            description=validated["description"],
            thumbnail_path=validated["thumbnail_path"],
            subtitles_path=validated["srt_path"],
            visibility=visibility,
            is_short=False,
            tags=validated["tags"],
            language=validated["language"],
            category=validated["category"],
            strict_thumbnail=True,
            expected_channel_id=expected_uc,
            profile_cfg=profile_cfg,
            job_id=job_id,
            bypass_review_gate=(root_dir is not None),
            screenshot_path=screenshot_path,
            edit_screenshot_path=edit_screenshot_path,
        )
    )

    published_url = publish_res.get("video_url")
    if published_url:
        update_youtube_channel_map(norm_slug, published_url, validated["title"], root_dir=base_root)
        update_channel_release_links(norm_slug, published_url, job_id=job_id, root_dir=base_root)

    return publish_res


def publish_20_long_batch(
    manifest_path: Optional[Path] = None,
    channels: Optional[list[str]] = None,
    max_workers: int = 2,
    approve_batch: bool = False,
    allow_stale: bool = False,
    dry_run: bool = False,
    force: bool = False,
    visibility: str = "PUBLIC",
    report_path: Optional[Path] = None,
    root_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Execute complete batch publishing workflow across the 20 Vietnamese Long videos."""
    base_root = root_dir or REPO_ROOT
    mf_p = manifest_path or (base_root / "video" / "publish_manifest_20_long.json")
    rep_p = report_path or (base_root / "video" / "published_20_long_report.json")
    map_p = base_root / "sys" / "channels" / "youtube_channel_map.json"

    if not map_p.is_file():
        raise FileNotFoundError(f"youtube_channel_map.json not found at {map_p}")

    channel_map = json.loads(map_p.read_text(encoding="utf-8"))

    # Load or scan manifest
    manifest_channels: dict[str, Any] = {}
    if mf_p.is_file():
        raw_manifest = json.loads(mf_p.read_text(encoding="utf-8"))
        manifest_channels = raw_manifest.get("channels", {})
    else:
        logger.info("Manifest %s not found; auto-scanning channels from channel_map...", mf_p)
        for ch_key, ch_val in channel_map.get("channels", {}).items():
            if ch_key.startswith("en_"):
                continue
            manifest_channels[ch_key] = ch_val

    # Load existing report for resume safety
    existing_report: dict[str, Any] = {}
    if rep_p.is_file() and not force:
        try:
            existing_report = json.loads(rep_p.read_text(encoding="utf-8")).get("published_items", {})
        except Exception as e:
            logger.warning("Could not read existing report %s: %s", rep_p, e)

    target_keys = channels or list(manifest_channels.keys())
    # Filter to Vietnamese channels only
    target_keys = [k for k in target_keys if not k.startswith("en_")]

    effective_workers = min(max(1, max_workers), 3)  # Hard-cap <= 3
    logger.info(
        "=== BATCH LONG (16:9) PUBLISHER === (targets=%d, workers=%d, approve_batch=%s, dry_run=%s)",
        len(target_keys), effective_workers, approve_batch, dry_run,
    )

    published_items: dict[str, Any] = dict(existing_report)

    def _worker(slug: str) -> tuple[str, dict[str, Any]]:
        norm_slug = slug.strip().replace("-", "_").lower()
        if not force and norm_slug in published_items:
            prev = published_items[norm_slug]
            if prev.get("status") == "PUBLISHED" and prev.get("video_url"):
                logger.info("Channel %s already published (%s), skipping.", norm_slug, prev.get("video_url"))
                return norm_slug, prev

        cdata = manifest_channels.get(norm_slug, {})
        try:
            res = publish_single_long_channel(
                channel_slug=norm_slug,
                channel_data=cdata,
                channel_map=channel_map,
                approve_batch=approve_batch,
                allow_stale=allow_stale,
                dry_run=dry_run,
                visibility=visibility,
                root_dir=base_root,
            )
            return norm_slug, res
        except Exception as exc:
            logger.error("Failed to publish %s: %s", norm_slug, exc)
            return norm_slug, {"status": "FAILED", "error": str(exc), "channel_id": norm_slug}

    # Execute with worker pool
    with ThreadPoolExecutor(max_workers=effective_workers) as executor:
        futures = [executor.submit(_worker, k) for k in target_keys]
        for fut in futures:
            ch_slug, result = fut.result()
            published_items[ch_slug] = result

            # Incremental atomic save
            summary = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "total_targets": len(target_keys),
                "published_count": sum(1 for v in published_items.values() if v.get("status") == "PUBLISHED"),
                "failed_count": sum(1 for v in published_items.values() if v.get("status") == "FAILED"),
                "dry_run": dry_run,
                "published_items": published_items,
            }
            rep_p.parent.mkdir(parents=True, exist_ok=True)
            tmp_rep = rep_p.with_suffix(".tmp")
            tmp_rep.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            tmp_rep.replace(rep_p)

    final_summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_targets": len(target_keys),
        "published_count": sum(1 for v in published_items.values() if v.get("status") == "PUBLISHED"),
        "failed_count": sum(1 for v in published_items.values() if v.get("status") == "FAILED"),
        "dry_run": dry_run,
        "published_items": published_items,
    }
    return final_summary


def main():
    parser = argparse.ArgumentParser(description="Batch YouTube Publisher for 20 Vietnamese Long (16:9) Videos")
    parser.add_argument("--manifest", help="Custom publish_manifest_20_long.json path")
    parser.add_argument("--channels", nargs="*", help="Specific channels to publish (default: all 20)")
    parser.add_argument("--max-workers", type=int, default=2, help="Concurrency workers (default 2, hard-capped <= 3)")
    parser.add_argument("--approve-batch", action="store_true", help="Auto-approve jobs in Review Dashboard")
    parser.add_argument("--allow-stale", action="store_true", help="Allow publishing MP4s older than spec files")
    parser.add_argument("--dry-run", action="store_true", help="Simulate publish without Chrome or YouTube API")
    parser.add_argument("--force", action="store_true", help="Force republish even if already published in report")
    parser.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "UNLISTED", "PRIVATE"])
    parser.add_argument("--report", help="Custom published_20_long_report.json path")

    args = parser.parse_args()

    mf_path = Path(args.manifest).resolve() if args.manifest else None
    rep_path = Path(args.report).resolve() if args.report else None

    report = publish_20_long_batch(
        manifest_path=mf_path,
        channels=args.channels,
        max_workers=args.max_workers,
        approve_batch=args.approve_batch,
        allow_stale=args.allow_stale,
        dry_run=args.dry_run,
        force=args.force,
        visibility=args.visibility,
        report_path=rep_path,
    )

    print("\n=== BATCH 20 LONG PUBLISH COMPLETED ===")
    print(f"Total Targets: {report['total_targets']}")
    print(f"Published:     {report['published_count']}")
    print(f"Failed:        {report['failed_count']}")
    print(f"Dry Run:       {report['dry_run']}")
    print(f"Report saved:  {rep_path or DEFAULT_REPORT_PATH}")


if __name__ == "__main__":
    main()
