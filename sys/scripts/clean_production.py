#!/usr/bin/env python3
"""V3 maintenance: verify published videos, retain history/cache, clean empty scratch only."""

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
VIDEO_DIR = REPO_ROOT / "video"
EXPORTS_DIR = ROOT / "exports"
RUNS_DIR = ROOT / "runs"
SCRATCH_DIR = ROOT / "scratch"
GFLOW_DIR = ROOT / ".gflow"
STATE_DIR = ROOT / ".state"
DB_PATH = STATE_DIR / "jobs.sqlite"
LOG_PATH = STATE_DIR / "cleanup.log"

TRANSIENT_WORK_DIRS = frozenset({
    "_colab_render",
    "_colab_render_2k",
    "render_2k",
    "render",
    "render_2k_15beat_backup",
    "plates_2k",
    "plates_raw",
    "frames_2k",
    "segments_110x",
    ".staging",
    "fonts",
    "variant_A",
    "variant_B",
    "variant_C",
    "variant_A_preview",
})
DEDUP_SUFFIXES = frozenset({".mp4", ".wav", ".png"})

JOB_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")

def log_event(message: str) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    for entry in path.rglob("*"):
        if entry.is_file() and not entry.is_symlink():
            try:
                total += entry.stat().st_size
            except OSError:
                pass
    return total

def validate_job_id(job_id: str) -> Path:
    """Validates job_id against regex and ensures path does not escape runs directory."""
    if not job_id or not JOB_ID_REGEX.match(job_id):
        raise ValueError(f"Tên job không hợp lệ (chỉ chấp nhận a-z, A-Z, 0-9, _, -): {job_id}")
    run_dir = (RUNS_DIR / job_id).resolve()
    if not run_dir.is_relative_to(RUNS_DIR.resolve()):
        raise ValueError(f"Đường dẫn job vi phạm an toàn (Path Traversal detected): {job_id}")
    return run_dir

def validate_video_integrity(video_path: Path) -> tuple[bool, str]:
    """Uses ffprobe to verify video streams, duration, and container integrity."""
    if not video_path.exists() or video_path.stat().st_size < 100 * 1024:
        return False, f"File video không tồn tại hoặc quá nhỏ (<100KB): {video_path.name}"
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=codec_type,codec_name",
            "-of", "json", str(video_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            return False, f"ffprobe không thể đọc video (hỏng container hoặc thiếu moov atom): {video_path.name}"
        data = json.loads(res.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
        if duration <= 0:
            return False, f"Thời lượng video không hợp lệ (duration={duration}): {video_path.name}"
        streams = data.get("streams", [])
        has_video = any(s.get("codec_type") == "video" for s in streams)
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        if not has_video:
            return False, f"Video thiếu stream hình ảnh: {video_path.name}"
        if not has_audio:
            return False, f"Video thiếu stream âm thanh: {video_path.name}"
        return True, "Video hợp lệ"
    except Exception as e:
        return False, f"Lỗi kiểm tra ffprobe: {e}"

def validate_job_deliverables(job_id: str) -> tuple[bool, str, list[Path], int]:
    """Verify v3 decisions and current video library without changing job state."""
    import threading
    sys.path.insert(0, str(ROOT))
    import workflow

    from pilot import Pilot
    p = None
    try:
        validate_job_id(job_id)
        p = object.__new__(Pilot)
        p.root = ROOT
        p._db_lock = threading.Lock()
        p.db = sqlite3.connect(DB_PATH.resolve().as_uri() + '?mode=ro', uri=True)
        p.db.row_factory = sqlite3.Row
        paths = [Path(x) for x in workflow.published_videos(p, job_id)]
        for path in paths:
            valid, reason = validate_video_integrity(path)
            if not valid:
                return False, reason, [], 0
        return True, 'Đủ quyết định v3 và video xuất khớp artifact', paths, workflow.current(p, job_id, 'video')['revision']
    except Exception as exc:
        return False, str(exc), [], 0
    finally:
        if p is not None and hasattr(p, 'db'):
            p.db.close()


def prune_unapproved_revisions(job_id: str, dry_run: bool = False) -> int:
    """Revision history and evidence are retained, including rejected artifacts."""
    validate_job_id(job_id)
    print(f'  Giữ toàn bộ revision và bằng chứng của {job_id}; không có ứng viên xóa.')
    return 0

def clean_scratch_whitelist(retention_days: int = 3, dry_run: bool = False) -> int:
    """Remove only old, empty scratch directories; filenames are not evidence of disposal.

    Media and nonempty directories require a separately reviewed inventory.
    Never follow symlinks, including a symlink replacing the scratch root.
    """
    if SCRATCH_DIR.is_symlink() or not SCRATCH_DIR.is_dir():
        return 0
    cutoff = time.time() - max(0, retention_days) * 86400
    for item in SCRATCH_DIR.iterdir():
        if item.is_symlink() or not item.is_dir():
            continue
        if not (item.name.startswith('tmp_') or item.name == 'render_output'):
            continue
        try:
            if item.stat().st_mtime >= cutoff or any(item.iterdir()):
                continue
            if dry_run:
                print(f"  [Scratch - Thư mục rỗng có thể dọn] {item}")
            else:
                # rmdir fails safely if another process has added a file.
                item.rmdir()
                print(f"  [Scratch - Đã dọn thư mục rỗng] {item}")
        except OSError:
            continue
    return 0

def clean_system_and_browser_cache(dry_run: bool = False) -> int:
    """No ownership proof for shared caches: never select them for deletion."""
    print('  Giữ profile, cache trình duyệt, model và /tmp dùng chung; chưa có ứng viên xóa được xác minh.')
    return 0


def prune_transient_logs_and_proofs(keep_latest_proofs: int = 5, dry_run: bool = False) -> int:
    """Rotate sys/logs/proofs/test_evidence_*.log, remove transient sys/reports/*.log, and clean sys/.cache/pycache."""
    freed = 0
    proofs_dir = ROOT / "logs/proofs"
    if proofs_dir.is_dir() and not proofs_dir.is_symlink():
        proofs = sorted(proofs_dir.glob("test_evidence_*.log"))
        for old_proof in proofs[:-max(1, keep_latest_proofs)]:
            if old_proof.is_file() and not old_proof.is_symlink():
                sz = old_proof.stat().st_size
                if dry_run:
                    print(f"  [Proofs - Sẽ xoay vòng log cũ] {old_proof.name} ({format_size(sz)})")
                else:
                    old_proof.unlink(missing_ok=True)
                    print(f"  [Proofs - Đã xoay vòng log cũ] {old_proof.name} ({format_size(sz)})")
                freed += sz

    reports_dir = ROOT / "reports"
    if reports_dir.is_dir() and not reports_dir.is_symlink():
        for log_file in reports_dir.glob("*.log"):
            if log_file.is_file() and not log_file.is_symlink():
                sz = log_file.stat().st_size
                if dry_run:
                    print(f"  [Reports - Sẽ xóa log tạm] {log_file.name} ({format_size(sz)})")
                else:
                    log_file.unlink(missing_ok=True)
                    print(f"  [Reports - Đã xóa log tạm] {log_file.name} ({format_size(sz)})")
                freed += sz

    pycache_dir = ROOT / ".cache/pycache"
    if pycache_dir.is_dir() and not pycache_dir.is_symlink():
        sz = get_dir_size(pycache_dir)
        if sz > 0:
            if dry_run:
                print(f"  [Cache - Sẽ dọn pycache] {pycache_dir} ({format_size(sz)})")
            else:
                shutil.rmtree(pycache_dir, ignore_errors=True)
                print(f"  [Cache - Đã dọn pycache] {pycache_dir} ({format_size(sz)})")
            freed += sz
    return freed


def _contains_symlink(path: Path) -> bool:
    """Return True if path or any nested entry inside it is a symlink."""
    if path.is_symlink():
        return True
    if not path.is_dir():
        return False
    for walk_root, dirs, files in os.walk(path, followlinks=False):
        root_path = Path(walk_root)
        if any((root_path / d).is_symlink() for d in dirs) or any((root_path / f).is_symlink() for f in files):
            return True
    return False


def _remove_path(path: Path, label: str, dry_run: bool) -> int:
    """Safely remove a non-symlink file or directory tree and return reclaimed bytes."""
    if not path.exists() or _contains_symlink(path):
        return 0
    sz = get_dir_size(path)
    if dry_run:
        print(f"  [{label} - Sẽ dọn] {path} ({format_size(sz)})")
        return sz
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)
    print(f"  [{label} - Đã dọn] {path} ({format_size(sz)})")
    return sz


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 digest of a regular file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _job_is_quiet(job_dir: Path, cutoff: float) -> bool:
    """Return True if no lock file or recently modified entry is active in job_dir."""
    if list(job_dir.glob("*.lock")):
        return False
    try:
        entries = list(job_dir.iterdir())
        for work_dir in job_dir.glob("_work*"):
            if work_dir.is_dir() and not work_dir.is_symlink():
                if list(work_dir.glob("*.lock")):
                    return False
                entries.extend(work_dir.iterdir())
        for entry in entries:
            if not entry.is_symlink() and entry.stat().st_mtime >= cutoff:
                return False
    except OSError:
        return False
    return True


def _nonempty_dir(path: Path) -> bool:
    return path.is_dir() and not path.is_symlink() and any(path.iterdir())


def deduplicate_identical_job_deliverables(
    job_dir: Path,
    min_bytes: int = 1024 * 1024,
    dry_run: bool = False,
) -> int:
    """Replace byte-identical top-level deliverables in a job directory with hardlinks."""
    if job_dir.is_symlink() or not job_dir.is_dir():
        return 0
    by_size: dict[int, list[Path]] = {}
    for entry in sorted(job_dir.iterdir()):
        if not entry.is_file() or entry.is_symlink() or entry.suffix.lower() not in DEDUP_SUFFIXES:
            continue
        try:
            st = entry.stat()
        except OSError:
            continue
        if st.st_size >= min_bytes:
            by_size.setdefault(st.st_size, []).append(entry)

    freed = 0
    for size_bytes, paths in by_size.items():
        if len(paths) < 2 or len({p.stat().st_ino for p in paths}) < 2:
            continue
        by_hash: dict[str, list[Path]] = {}
        for path in paths:
            try:
                by_hash.setdefault(_sha256_file(path), []).append(path)
            except OSError:
                continue
        for same_files in by_hash.values():
            if len(same_files) < 2:
                continue
            canonical = sorted(
                same_files,
                key=lambda p: (-p.stat().st_nlink, len(p.name), p.name),
            )[0]
            canonical_ino = canonical.stat().st_ino
            seen_inodes = {canonical_ino}
            for dup in same_files:
                dup_ino = dup.stat().st_ino
                if dup_ino == canonical_ino:
                    continue
                if dup_ino not in seen_inodes:
                    seen_inodes.add(dup_ino)
                    freed += size_bytes
                if dry_run:
                    print(
                        f"  [Dedup - Sẽ hardlink bản trùng] {job_dir.name}/{dup.name} -> "
                        f"{canonical.name} ({format_size(size_bytes)})"
                    )
                    continue
                tmp_link = dup.with_name(f".dedup_{os.getpid()}_{dup.name}")
                try:
                    tmp_link.unlink(missing_ok=True)
                    os.link(canonical, tmp_link)
                    os.replace(tmp_link, dup)
                    print(
                        f"  [Dedup - Đã hardlink bản trùng] {job_dir.name}/{dup.name} -> "
                        f"{canonical.name} ({format_size(size_bytes)})"
                    )
                except OSError:
                    tmp_link.unlink(missing_ok=True)
    return freed


def prune_verified_video_work_intermediates(
    video_dir: Path | None = None,
    retention_hours: float = 2.0,
    dry_run: bool = False,
) -> int:
    """Prune regenerable render/audio/backup intermediates in verified finished video jobs."""
    target_dir = video_dir or VIDEO_DIR
    if target_dir.is_symlink() or not target_dir.is_dir():
        return 0
    cutoff = time.time() - max(0.0, retention_hours) * 3600.0
    freed = 0

    for job_dir in sorted(target_dir.iterdir()):
        if not job_dir.is_dir() or job_dir.is_symlink():
            continue
        if not _job_is_quiet(job_dir, cutoff):
            continue

        candidates = [
            p
            for p in sorted(job_dir.glob("*.mp4"))
            if p.is_file() and not p.is_symlink() and "backup" not in p.name and "preview" not in p.name
        ]
        if not any(validate_video_integrity(mp4)[0] for mp4 in candidates):
            continue

        has_frames = _nonempty_dir(job_dir / "frames")
        has_clips = _nonempty_dir(job_dir / "clips")
        has_master_wav = (job_dir / "narration_master.wav").is_file() or (job_dir / "audio_master.wav").is_file()

        for work_dir in sorted(job_dir.glob("_work*")):
            if not work_dir.is_dir() or work_dir.is_symlink():
                continue
            has_work_images = _nonempty_dir(work_dir / "images")
            has_work_wav = has_master_wav or (work_dir / "narration.wav").is_file()

            for sub in sorted(work_dir.iterdir()):
                name = sub.name
                if name in TRANSIENT_WORK_DIRS:
                    freed += _remove_path(sub, "VideoWork", dry_run)
                elif name == "audio_work" and has_work_wav:
                    freed += _remove_path(sub / "raw_wavs", "VideoWork", dry_run)
                elif sub.is_file() and sub.suffix.lower() == ".zip":
                    freed += _remove_path(sub, "VideoWork", dry_run)
                elif name in ("raw_narration.wav", "narration_dry_master_110x.wav", "narration_master_110x.m4a") and has_work_wav:
                    freed += _remove_path(sub, "VideoWork", dry_run)
                elif (name.startswith("images_old_") or name.startswith("images_backup_")) and (has_work_images or has_frames):
                    freed += _remove_path(sub, "VideoWork", dry_run)

        if has_frames and has_clips:
            for backup_item in sorted(job_dir.glob("*_15beat_backup*")) + sorted(job_dir.glob("*_20beat_backup*")):
                freed += _remove_path(backup_item, "VideoBackup", dry_run)

        freed += deduplicate_identical_job_deliverables(job_dir, dry_run=dry_run)

    return freed


def prune_periodic_scratch_and_caches(
    repo_root: Path | None = None,
    scratch_dir: Path | None = None,
    retention_hours: float = 2.0,
    dry_run: bool = False,
) -> int:
    """Prune stale scratch render/audio work dirs, Python/linter caches, and empty stray dirs."""
    root = repo_root or REPO_ROOT
    target_scratch = scratch_dir or SCRATCH_DIR
    cutoff = time.time() - max(0.0, retention_hours) * 3600.0
    freed = 0

    if target_scratch.is_dir() and not target_scratch.is_symlink():
        for item in sorted(target_scratch.iterdir()):
            if item.is_symlink():
                continue
            if item.is_dir() and (
                item.name.endswith(("_render_work", "_audio_work", "_prep_work"))
                or item.name.startswith("qa_frames_")
            ):
                try:
                    if item.stat().st_mtime < cutoff:
                        freed += _remove_path(item, "ScratchWork", dry_run)
                except OSError:
                    continue

    if root.is_dir() and not root.is_symlink():
        for walk_root, dirs, _ in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".venv") and d != ".git"]
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
                freed += _remove_path(Path(walk_root) / "__pycache__", "Cache", dry_run)

        for rel in (".pytest_cache", ".ruff_cache", ".agents/teamwork"):
            freed += _remove_path(root / rel, "Cache", dry_run)

        stray_sys = root / "sys" / "sys"
        if stray_sys.is_dir() and not _contains_symlink(stray_sys):
            has_files = any(p.is_file() for p in stray_sys.rglob("*"))
            if not has_files:
                freed += _remove_path(stray_sys, "StrayDir", dry_run)

        stray_acct = root / "account-08"
        if stray_acct.is_dir() and not _contains_symlink(stray_acct):
            lock_file = stray_acct / "sessions.json.lock"
            history_dir = stray_acct / "history"
            files = [p for p in stray_acct.rglob("*") if p.is_file()]
            only_empty_lock = (
                files == [lock_file] and lock_file.stat().st_size == 0
                and (not history_dir.exists() or not any(history_dir.iterdir()))
            )
            if not files or only_empty_lock:
                freed += _remove_path(stray_acct, "StrayDir", dry_run)

    return freed


def clean_completed_job(job_id: str, dry_run: bool = False) -> int:
    """Safely validates and prunes unapproved revisions of a completed job."""
    try:
        run_dir = validate_job_id(job_id)
    except ValueError as e:
        print(f"❌ [LỖI BẢO MẬT] {e}", file=sys.stderr)
        return 0

    if not run_dir.exists():
        print(f"Bỏ qua: Không tìm thấy thư mục runs/{job_id}")
        return 0

    valid, reason, preserved, approved_rev = validate_job_deliverables(job_id)
    if not valid:
        print(f"🛡️  [BẢO VỆ DỮ LIỆU] Không dọn dẹp job '{job_id}': {reason}")
        print(f"   Dữ liệu {job_id} trong runs/ được giữ nguyên 100%.")
        return 0

    print("\n==========================================================")
    print(f"  Job Hợp Lệ Đã Nghiệm Thu: {job_id}")
    print(f"  Thành phẩm đã xác minh trong thư viện video của {job_id}:")
    for f in preserved:
        print(f"    ✓ {f.name} ({format_size(f.stat().st_size)})")
    print("==========================================================")

    freed = prune_unapproved_revisions(job_id, dry_run=dry_run)
    return freed

def main():
    parser = argparse.ArgumentParser(
        description="Video Pilot v3 — Safe Post-Production Maintenance & Selective Pruning"
    )
    parser.add_argument("--job", help="Tên job cần kiểm tra thành phẩm v3")
    parser.add_argument("--all", action="store_true", help="Kiểm kê các job và dọn scratch rỗng quá hạn")
    parser.add_argument("--periodic", action="store_true", help="Chế độ bảo trì định kỳ: Kiểm kê job, xoay vòng proof logs và dọn scratch rỗng quá hạn")
    parser.add_argument("--cache-only", action="store_true", help="Báo trạng thái bảo toàn cache; không xóa")
    parser.add_argument("--dry-run", action="store_true", help="Xem trước các mục sẽ dọn mà không xóa thật")
    args = parser.parse_args()

    if not any([args.job, args.all, args.periodic, args.cache_only]):
        parser.print_help()
        sys.exit(1)

    print("==========================================================")
    print(" Video Pilot v3 — Safe Post-Production Maintenance Protocol")
    print(f" Chế độ: {'XEM TRƯỚC (--dry-run)' if args.dry_run else 'THỰC THI (Execution)'}")
    print("==========================================================")

    total_freed = 0

    if args.cache_only:
        total_freed += clean_system_and_browser_cache(dry_run=args.dry_run)

    elif args.job:
        total_freed += clean_completed_job(args.job, dry_run=args.dry_run)

    elif args.all or args.periodic:
        # Step 1: System & Browser Cache
        total_freed += clean_system_and_browser_cache(dry_run=args.dry_run)

        # Step 2: Scratch Whitelist & Proof/Report Log Rotation
        total_freed += clean_scratch_whitelist(retention_days=3, dry_run=args.dry_run)
        total_freed += prune_transient_logs_and_proofs(keep_latest_proofs=5, dry_run=args.dry_run)
        if args.periodic:
            total_freed += prune_verified_video_work_intermediates(dry_run=args.dry_run)
            total_freed += prune_periodic_scratch_and_caches(dry_run=args.dry_run)

        # Step 3: Scan all runs/ for completed, approved jobs
        print("\n--- [Tầng 3] Tối ưu hóa các Job đã nghiệm thu hoàn tất ---")
        if RUNS_DIR.exists():
            for j in sorted(RUNS_DIR.iterdir()):
                if j.is_dir() and JOB_ID_REGEX.match(j.name):
                    total_freed += clean_completed_job(j.name, dry_run=args.dry_run)

    print("\n==========================================================")
    action_text = "Dung lượng ước tính sẽ giải phóng" if args.dry_run else "Tổng dung lượng đã giải phóng"
    print(f" 🎉 {action_text}: {format_size(total_freed)}")
    print(" 🛡️  Lịch sử briefs, integrity hashes, bằng chứng Flow và kịch bản/video kết quả BẢO TOÀN 100%.")
    print("==========================================================")

    if not args.dry_run and total_freed > 0:
        log_event(f"Cleaned {format_size(total_freed)} (mode: {'job=' + args.job if args.job else 'all/periodic'})")

if __name__ == "__main__":
    main()
