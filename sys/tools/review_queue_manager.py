#!/usr/bin/env python3
"""Video Review Queue Manager for Video Pilot (sys/tools/review_queue_manager.py).

Enforces mandatory approval gates before publishing any video asset to YouTube.
Maintains the single-source-of-truth review queue (sys/channels/video_review_queue.json),
tracks quality review decisions, and captures granular repair feedback.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

# Add repo root and sys directory to path
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

DEFAULT_QUEUE_PATH = SYS_DIR / "channels" / "video_review_queue.json"
DEFAULT_MAP_PATH = SYS_DIR / "channels" / "youtube_channel_map.json"

VALID_STATUSES = {"PENDING_REVIEW", "APPROVED", "REJECTED", "PUBLISHED"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("review_queue_manager")


# 20 Canonical Vietnamese Channels
VN_CHANNELS: dict[str, dict[str, str]] = {
    "ai_binh_dan": {"slug": "ai-binh-dan", "channel_name": "AI Bình Dân"},
    "co_the_ke": {"slug": "co-the-ke", "channel_name": "Cơ Thể Kể"},
    "ho_so_ky_la": {"slug": "ho-so-ky-la", "channel_name": "Hồ Sơ Kỳ Lạ"},
    "nao_luoi": {"slug": "nao-luoi", "channel_name": "Não Lười"},
    "su_ke_lai": {"slug": "su-ke-lai", "channel_name": "Sử Kể Lại"},
    "thuong_cho_kheo": {"slug": "thuong-cho-kheo", "channel_name": "Thương Cho Khéo"},
    "tui_tien": {"slug": "tui-tien", "channel_name": "Túi Tiền Biết Nói"},
    "ua_sao_vay": {"slug": "ua-sao-vay", "channel_name": "Ủa Sao Vậy?"},
    "luat_ngam": {"slug": "luat-ngam", "channel_name": "Luật Ngầm Đám Đông"},
    "ban_do_quyen_luc": {"slug": "ban-do-quyen-luc", "channel_name": "Bản Đồ Quyền Lực"},
    "dia_com": {"slug": "dia-com", "channel_name": "Đĩa Cơm Khoa Học"},
    "luat_doi_thuong": {"slug": "luat-doi-thuong", "channel_name": "Luật Đời Thường"},
    "banh_rang": {"slug": "banh-rang", "channel_name": "Bánh Răng Thế Giới"},
    "vu_tru_ti_hon": {"slug": "vu-tru-ti-hon", "channel_name": "Vũ Trụ Tí Hon"},
    "nghe_song_sot": {"slug": "nghe-song-sot", "channel_name": "Nghề Sống Sót"},
    "la_ban_hoc_thuat": {"slug": "la-ban-hoc-thuat", "channel_name": "La Bàn Học Thuật"},
    "chanh_niem_ke": {"slug": "chanh-niem-ke", "channel_name": "Chánh Niệm Kể"},
    "loi_sang_soi": {"slug": "loi-sang-soi", "channel_name": "Lời Sáng Soi"},
    "minh_triet_song": {"slug": "minh-triet-song", "channel_name": "Minh Triết Sống"},
    "tam_tinh_dem": {"slug": "tam-tinh-dem", "channel_name": "Tâm Tĩnh Đêm"},
}


def load_review_queue(queue_path: Optional[Union[str, Path]] = None) -> dict[str, Any]:
    """Load video review queue from JSON file.

    If file does not exist, returns initialized queue structure.
    """
    path = Path(queue_path or DEFAULT_QUEUE_PATH).resolve()
    if not path.is_file():
        return {
            "schema_version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "items": {},
        }

    lock_path = path.with_suffix(".lock")
    try:
        with open(lock_path, "w", encoding="utf-8") as lock_fh:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_SH)
            try:
                content = path.read_text(encoding="utf-8")
            finally:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
    except Exception:
        content = path.read_text(encoding="utf-8")

    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            data = {}
        data.setdefault("schema_version", "1.0")
        data.setdefault("items", {})
        return data
    except json.JSONDecodeError:
        logger.warning("Corrupted review queue at %s; returning empty structure", path)
        return {
            "schema_version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "items": {},
        }


def save_review_queue(data: dict[str, Any], queue_path: Optional[Union[str, Path]] = None) -> Path:
    """Save video review queue to JSON atomically with file lock."""
    path = Path(queue_path or DEFAULT_QUEUE_PATH).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    lock_path = path.with_suffix(".lock")
    temp_path = path.with_suffix(f".tmp.{os.getpid()}")

    with open(lock_path, "w", encoding="utf-8") as lock_fh:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            with open(temp_path, "w", encoding="utf-8") as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                tf.write("\n")
            temp_path.replace(path)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
    return path


def register_video_for_review(
    job_id: str,
    channel_id: str,
    format_profile: str,
    title: str = "",
    mp4_path: str = "",
    thumbnail_path: str = "",
    srt_path: str = "",
    duration_sec: float = 0.0,
    competitor_formula: str = "",
    channel_name: str = "",
    queue_path: Optional[Union[str, Path]] = None,
    reset_status: bool = False,
) -> dict[str, Any]:
    """Register or update a video asset in the review queue.

    Preserves existing status and review_notes unless reset_status is True.
    """
    path = Path(queue_path or DEFAULT_QUEUE_PATH).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    op_lock_path = path.with_suffix(".op.lock")
    with open(op_lock_path, "a", encoding="utf-8") as op_lock_fh:
        fcntl.flock(op_lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            queue = load_review_queue(queue_path)
            items = queue.setdefault("items", {})

            existing = items.get(job_id)

            if existing and not reset_status:
                status = existing.get("status", "PENDING_REVIEW")
                review_notes = existing.get("review_notes", "")
                reviewed_at = existing.get("reviewed_at")
                published_url = existing.get("published_url")
                c_name = channel_name or existing.get("channel_name", "")
                c_id = channel_id or existing.get("channel_id", "")
                f_prof = format_profile or existing.get("format_profile", "long_16x9")
                v_title = title or existing.get("title", "")
                v_mp4 = mp4_path or existing.get("mp4_path", "")
                v_thumb = thumbnail_path or existing.get("thumbnail_path", "")
                v_srt = srt_path or existing.get("srt_path", "")
                v_dur = float(duration_sec) if duration_sec > 0.0 else existing.get("duration_sec", 0.0)
                v_comp = competitor_formula or existing.get("competitor_formula", "")
            else:
                status = "PENDING_REVIEW"
                review_notes = ""
                reviewed_at = None
                published_url = None
                c_name = channel_name
                c_id = channel_id
                f_prof = format_profile
                v_title = title
                v_mp4 = mp4_path
                v_thumb = thumbnail_path
                v_srt = srt_path
                v_dur = float(duration_sec)
                v_comp = competitor_formula

            item = {
                "job_id": job_id,
                "channel_id": c_id,
                "channel_name": c_name,
                "format_profile": f_prof,
                "title": v_title,
                "mp4_path": v_mp4,
                "thumbnail_path": v_thumb,
                "srt_path": v_srt,
                "duration_sec": v_dur,
                "competitor_formula": v_comp,
                "status": status,
                "review_notes": review_notes,
                "reviewed_at": reviewed_at,
                "published_url": published_url,
            }

            items[job_id] = item
            save_review_queue(queue, queue_path)
            return item
        finally:
            fcntl.flock(op_lock_fh.fileno(), fcntl.LOCK_UN)


def set_review_decision(
    job_id: str,
    status: str,
    review_notes: str = "",
    queue_path: Optional[Union[str, Path]] = None,
    published_url: Optional[str] = None,
) -> dict[str, Any]:
    """Record a review decision for a video job.

    Validates status in {"PENDING_REVIEW", "APPROVED", "REJECTED", "PUBLISHED"}.
    Raises ValueError for invalid status, or KeyError if job_id is not in queue.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}")

    path = Path(queue_path or DEFAULT_QUEUE_PATH).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    op_lock_path = path.with_suffix(".op.lock")
    with open(op_lock_path, "a", encoding="utf-8") as op_lock_fh:
        fcntl.flock(op_lock_fh.fileno(), fcntl.LOCK_EX)
        try:
            queue = load_review_queue(queue_path)
            items = queue.setdefault("items", {})

            if job_id not in items:
                raise KeyError(f"Job '{job_id}' not found in review queue.")

            item = items[job_id]
            item["status"] = status

            if review_notes:
                item["review_notes"] = review_notes

            if status in {"APPROVED", "REJECTED"}:
                item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
            elif status == "PENDING_REVIEW":
                item["reviewed_at"] = None

            if published_url:
                item["published_url"] = published_url
            elif status == "PUBLISHED" and not item.get("published_url"):
                item["published_url"] = published_url

            save_review_queue(queue, queue_path)
            return item
        finally:
            fcntl.flock(op_lock_fh.fileno(), fcntl.LOCK_UN)


def check_publish_permission(job_id: str, queue_path: Optional[Union[str, Path]] = None) -> tuple[bool, str]:
    """Check whether a video is permitted to be published to YouTube.

    Returns (True, "APPROVED") ONLY if job_id exists in queue and status == "APPROVED".
    Otherwise returns (False, reason) where reason is the current status or "NOT_FOUND".
    """
    queue = load_review_queue(queue_path)
    items = queue.get("items", {})
    if job_id not in items:
        return False, "NOT_FOUND"

    item_status = items[job_id].get("status", "PENDING_REVIEW")
    if item_status == "APPROVED":
        return True, "APPROVED"

    return False, item_status


def get_rejected_jobs(queue_path: Optional[Union[str, Path]] = None) -> list[dict[str, Any]]:
    """Return all items where status == 'REJECTED' and review_notes is non-empty."""
    queue = load_review_queue(queue_path)
    rejected: list[dict[str, Any]] = []
    for item in queue.get("items", {}).values():
        if item.get("status") == "REJECTED" and bool(str(item.get("review_notes", "")).strip()):
            rejected.append(item)
    return rejected


def _get_video_duration(mp4_path: Union[str, Path]) -> float:
    """Extract video duration in seconds via ffprobe."""
    p = Path(mp4_path)
    if not p.is_file():
        return 0.0
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(p.resolve()),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if res.returncode == 0 and res.stdout.strip():
            return round(float(res.stdout.strip()), 2)
    except Exception:
        pass
    return 0.0


def _extract_video_title(run_dir: Optional[Path], video_dir: Optional[Path]) -> str:
    """Extract YouTube video title from content.json, brief.json, or youtube_*.md."""
    if run_dir and run_dir.exists():
        for fname in ("content.json", "brief.json", "outline.json"):
            fp = run_dir / fname
            if fp.is_file():
                try:
                    data = json.loads(fp.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        t = data.get("topic") or data.get("title")
                        if t and isinstance(t, str):
                            return t.strip()
                except Exception:
                    pass

    if video_dir and video_dir.exists():
        for fname in ("youtube_long.md", "youtube_shorts.md"):
            fp = video_dir / fname
            if fp.is_file():
                try:
                    content = fp.read_text(encoding="utf-8")
                    m = re.search(r"## 1\. Tiêu đề[^\n]*\n```(?:text)?\n(.*?)\n```", content, re.DOTALL)
                    if m:
                        return m.group(1).strip()
                except Exception:
                    pass
    return ""


def _extract_competitor_formula(
    run_dir: Optional[Path],
    ch_dir: Optional[Path],
    channel_id: str = "",
) -> str:
    """Extract competitor formula summary from competitor_research.json or registry fallback."""
    for base in [run_dir, ch_dir]:
        if base and base.exists():
            comp_file = base / "competitor_research.json"
            if comp_file.is_file():
                try:
                    data = json.loads(comp_file.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        for k in (
                            "competitor_formula",
                            "formula",
                            "summary",
                            "hook_formula",
                            "core_formula",
                            "description",
                        ):
                            if data.get(k):
                                return str(data[k]).strip()
                    elif isinstance(data, str):
                        return data.strip()
                except Exception:
                    pass

    # Registry benchmark & hook formula fallback
    if channel_id:
        try:
            from channels.registry import get_channel

            ch = get_channel(channel_id)
            if ch:
                ref_parts = [f"{r.name} ({r.platform})" for r in ch.references[:2]]
                hook = ch.hook_formulas[0] if ch.hook_formulas else ""
                parts = []
                if ref_parts:
                    parts.append("Benchmark: " + ", ".join(ref_parts))
                if hook:
                    parts.append(f"Hook: '{hook}'")
                return " | ".join(parts)
        except Exception:
            pass
    return ""


def _discover_job_media(
    job_id: str,
    format_profile: str,
    repo_root: Path,
) -> tuple[str, str, str]:
    """Discover mp4_path, thumbnail_path, and srt_path for a job on disk."""
    video_dir = repo_root / "video" / job_id
    run_dir = repo_root / "sys" / "runs" / job_id
    is_short = format_profile == "short_9x16"

    # 1. MP4
    mp4_path = ""
    mp4_candidates = [
        video_dir / f"{job_id}.mp4",
        video_dir / ("video_9x16.mp4" if is_short else "video_16x9.mp4"),
        video_dir / ("vi_9x16_sub.mp4" if is_short else "vi_16x9_nosub.mp4"),
        run_dir / f"{job_id}.mp4",
        run_dir / "final.mp4",
    ]
    for cand in mp4_candidates:
        if cand.is_file() and cand.stat().st_size > 0:
            mp4_path = str(cand.resolve())
            break
    if not mp4_path and video_dir.is_dir():
        for cand in sorted(video_dir.glob("*.mp4")):
            if cand.is_file() and cand.stat().st_size > 0:
                mp4_path = str(cand.resolve())
                break

    # 2. Thumbnail
    thumb_path = ""
    thumb_candidates = [
        video_dir / ("thumbnail_9x16.jpg" if is_short else "thumbnail_16x9.jpg"),
        video_dir / ("thumbnail_9x16.png" if is_short else "thumbnail_16x9.png"),
        video_dir / "cover.jpg",
        video_dir / "cover.png",
        run_dir / ("thumbnail_9x16.jpg" if is_short else "thumbnail_16x9.jpg"),
        run_dir / "cover.jpg",
    ]
    for cand in thumb_candidates:
        if cand.is_file() and cand.stat().st_size > 0:
            thumb_path = str(cand.resolve())
            break
    if not thumb_path and video_dir.is_dir():
        for cand in sorted(video_dir.glob("thumbnail*.jpg")):
            if cand.is_file() and cand.stat().st_size > 0:
                thumb_path = str(cand.resolve())
                break

    # 3. Subtitles SRT
    srt_path = ""
    srt_candidates = [
        video_dir / f"{job_id}.srt",
        video_dir / "subtitles.srt",
        video_dir / ("vi_9x16.srt" if is_short else "vi_16x9.srt"),
        run_dir / f"{job_id}.srt",
        run_dir / "subtitles.srt",
    ]
    for cand in srt_candidates:
        if cand.is_file() and cand.stat().st_size > 0:
            srt_path = str(cand.resolve())
            break
    if not srt_path and video_dir.is_dir():
        for cand in sorted(video_dir.glob("*.srt")):
            if cand.is_file() and cand.stat().st_size > 0:
                srt_path = str(cand.resolve())
                break

    return mp4_path, thumb_path, srt_path


def get_vietnamese_channels() -> dict[str, dict[str, str]]:
    """Return dictionary of 20 Vietnamese channels mapped to slug and channel_name."""
    channels = dict(VN_CHANNELS)
    if DEFAULT_MAP_PATH.is_file():
        try:
            mdata = json.loads(DEFAULT_MAP_PATH.read_text(encoding="utf-8"))
            for ch_id, ch_info in mdata.get("channels", {}).items():
                if not ch_id.startswith("en_"):
                    slug = ch_info.get("slug") or ch_id.replace("_", "-")
                    name = ch_info.get("channel_name") or ch_id
                    channels[ch_id] = {"slug": slug, "channel_name": name}
        except Exception as e:
            logger.warning("Could not read youtube_channel_map.json: %s", e)
    return channels


def sync_all_channel_runs(
    batch_tag: Optional[str] = "batch3",
    queue_path: Optional[Union[str, Path]] = None,
) -> dict[str, Any]:
    """Scan sys/runs/* and video/* for all 20 Vietnamese channels and update review queue.

    Ensures all canonical jobs for batch_tag are registered, discovers existing media,
    and preserves previously recorded review decisions.
    """
    vn_map = get_vietnamese_channels()
    synced_count = 0
    repo_root = REPO_ROOT

    # 1. Process canonical jobs for each channel
    for ch_id, meta in vn_map.items():
        slug = meta["slug"]
        c_name = meta["channel_name"]
        formats = [
            ("long_16x9", "16x9"),
            ("short_9x16", "9x16"),
        ]
        for f_prof, suffix in formats:
            if batch_tag:
                job_id = f"{slug}-{batch_tag}-{suffix}"
            else:
                job_id = f"{slug}-{suffix}"

            video_dir = repo_root / "video" / job_id
            run_dir = repo_root / "sys" / "runs" / job_id
            ch_dir = repo_root / "sys" / "channels" / ch_id

            mp4, thumb, srt = _discover_job_media(job_id, f_prof, repo_root)
            title = _extract_video_title(run_dir, video_dir)
            dur = _get_video_duration(mp4) if mp4 else 0.0
            formula = _extract_competitor_formula(run_dir, ch_dir, channel_id=ch_id)

            register_video_for_review(
                job_id=job_id,
                channel_id=ch_id,
                channel_name=c_name,
                format_profile=f_prof,
                title=title,
                mp4_path=mp4,
                thumbnail_path=thumb,
                srt_path=srt,
                duration_sec=dur,
                competitor_formula=formula,
                queue_path=queue_path,
                reset_status=False,
            )
            synced_count += 1

    # 2. Also scan disk for any other directories matching VN slugs
    slug_to_id = {v["slug"]: (k, v["channel_name"]) for k, v in vn_map.items()}
    candidate_dirs: set[str] = set()

    for base_folder in [repo_root / "video", repo_root / "sys" / "runs"]:
        if base_folder.is_dir():
            for d in base_folder.iterdir():
                if d.is_dir() and not d.name.startswith("."):
                    # Check if belongs to one of the 20 VN channels
                    for s in slug_to_id:
                        if d.name.startswith(s):
                            if not batch_tag or batch_tag in d.name:
                                candidate_dirs.add(d.name)
                            break

    for job_id in candidate_dirs:
        # Determine channel and format
        matched_slug = None
        for s in slug_to_id:
            if job_id.startswith(s):
                matched_slug = s
                break
        if not matched_slug:
            continue

        ch_id, c_name = slug_to_id[matched_slug]
        f_prof = "short_9x16" if "9x16" in job_id else "long_16x9"

        video_dir = repo_root / "video" / job_id
        run_dir = repo_root / "sys" / "runs" / job_id
        ch_dir = repo_root / "sys" / "channels" / ch_id

        mp4, thumb, srt = _discover_job_media(job_id, f_prof, repo_root)
        title = _extract_video_title(run_dir, video_dir)
        dur = _get_video_duration(mp4) if mp4 else 0.0
        formula = _extract_competitor_formula(run_dir, ch_dir, channel_id=ch_id)

        register_video_for_review(
            job_id=job_id,
            channel_id=ch_id,
            channel_name=c_name,
            format_profile=f_prof,
            title=title,
            mp4_path=mp4,
            thumbnail_path=thumb,
            srt_path=srt,
            duration_sec=dur,
            competitor_formula=formula,
            queue_path=queue_path,
            reset_status=False,
        )
        synced_count += 1

    queue = load_review_queue(queue_path)
    logger.info(
        "Synced review queue (%d operations, %d total jobs in queue)",
        synced_count,
        len(queue.get("items", {})),
    )
    return {
        "synced_operations": synced_count,
        "total_jobs": len(queue.get("items", {})),
        "queue_path": str(Path(queue_path or DEFAULT_QUEUE_PATH).resolve()),
        "jobs": list(queue.get("items", {}).keys()),
    }


def apply_review_decisions(
    decisions: Union[dict[str, Any], list[dict[str, Any]], str, Path],
    queue_path: Optional[Union[str, Path]] = None,
) -> list[dict[str, Any]]:
    """Batch apply review decisions from a JSON file, dict mapping, or list of objects.

    Accepts:
    1. Path to JSON file.
    2. Dict mapping: { "<job_id>": { "status": "APPROVED", "review_notes": "..." } }
    3. Dict with items wrapper: { "items": { ... } }
    4. List of dicts: [ { "job_id": "...", "status": "APPROVED", "review_notes": "..." } ]
    """
    raw_data: Any = decisions
    if isinstance(decisions, (str, Path)):
        p = Path(decisions)
        if not p.is_file():
            raise FileNotFoundError(f"Decisions file not found: {p}")
        raw_data = json.loads(p.read_text(encoding="utf-8"))

    results: list[dict[str, Any]] = []

    # Format 1 & 3: dict
    if isinstance(raw_data, dict):
        items_dict = raw_data.get("items", raw_data.get("decisions", raw_data))
        for j_id, entry in items_dict.items():
            if isinstance(entry, dict) and "status" in entry:
                st = entry["status"]
                notes = entry.get("review_notes", "")
                pub_url = entry.get("published_url")
                # Auto-register if not yet present in queue
                q = load_review_queue(queue_path)
                if j_id not in q.get("items", {}):
                    f_prof = "short_9x16" if "9x16" in j_id else "long_16x9"
                    register_video_for_review(job_id=j_id, channel_id="", format_profile=f_prof, queue_path=queue_path)
                item = set_review_decision(
                    job_id=j_id,
                    status=st,
                    review_notes=notes,
                    queue_path=queue_path,
                    published_url=pub_url,
                )
                results.append(item)

    # Format 4: list
    elif isinstance(raw_data, list):
        for entry in raw_data:
            if isinstance(entry, dict) and "job_id" in entry and "status" in entry:
                j_id = entry["job_id"]
                st = entry["status"]
                notes = entry.get("review_notes", "")
                pub_url = entry.get("published_url")
                q = load_review_queue(queue_path)
                if j_id not in q.get("items", {}):
                    f_prof = "short_9x16" if "9x16" in j_id else "long_16x9"
                    register_video_for_review(job_id=j_id, channel_id="", format_profile=f_prof, queue_path=queue_path)
                item = set_review_decision(
                    job_id=j_id,
                    status=st,
                    review_notes=notes,
                    queue_path=queue_path,
                    published_url=pub_url,
                )
                results.append(item)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Video Review & Approval Queue Manager for Video Pilot")
    parser.add_argument("--queue", help="Path to video_review_queue.json override")
    parser.add_argument("--sync", action="store_true", help="Sync all 20 Vietnamese channel runs to review queue")
    parser.add_argument("--batch", default="batch3", help="Batch tag for sync (default: batch3)")
    parser.add_argument("--set-status", dest="set_status_job", help="Set review status for specific job ID")
    parser.add_argument(
        "--status",
        choices=["PENDING_REVIEW", "APPROVED", "REJECTED", "PUBLISHED"],
        help="Target status for --set-status",
    )
    parser.add_argument("--note", "--review-notes", dest="note", default="", help="Review notes/repair feedback")
    parser.add_argument("--url", "--published-url", dest="published_url", help="Live published URL if status=PUBLISHED")
    parser.add_argument("--check", help="Check publish permission for job ID")
    parser.add_argument("--list-rejected", action="store_true", help="List all rejected jobs requiring repair")
    parser.add_argument("--apply-json", help="Batch apply review decisions from a JSON file")
    parser.add_argument("--build-dashboard", action="store_true", help="Build interactive HTML review dashboard")

    args = parser.parse_args()

    if args.build_dashboard:
        try:
            from tools.build_review_dashboard import build_review_dashboard
        except ImportError:
            from sys.tools.build_review_dashboard import build_review_dashboard
        out_paths = build_review_dashboard(queue_path=args.queue)
        print("Built review dashboard at:")
        for p in out_paths:
            print(f"  - {p}")
        return

    if args.sync:
        res = sync_all_channel_runs(batch_tag=args.batch, queue_path=args.queue)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    if args.set_status_job:
        if not args.status:
            parser.error("--status is required when using --set-status")
        item = set_review_decision(
            job_id=args.set_status_job,
            status=args.status,
            review_notes=args.note,
            queue_path=args.queue,
            published_url=args.published_url,
        )
        print(json.dumps(item, indent=2, ensure_ascii=False))
        return

    if args.check:
        allowed, reason = check_publish_permission(args.check, queue_path=args.queue)
        result = {
            "job_id": args.check,
            "allowed": allowed,
            "status": reason,
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if allowed else 1)

    if args.list_rejected:
        rejected = get_rejected_jobs(queue_path=args.queue)
        print(json.dumps(rejected, indent=2, ensure_ascii=False))
        return

    if args.apply_json:
        results = apply_review_decisions(args.apply_json, queue_path=args.queue)
        print(f"Applied {len(results)} review decisions from {args.apply_json}:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
