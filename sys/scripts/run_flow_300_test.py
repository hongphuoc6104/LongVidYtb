#!/usr/bin/env python3
"""Graduated 5-Tier 300-Image Ramp-Up Runner & Verification Harness for Flow CDP.

Tiers & Hard Watchdog Timeouts (Calibrated ~30s/Round SLA):
- Batch 1 (Smoke / Warm-up):       10 images  | 4 workers  (3 rounds)  | Hard Timeout: 120.0s (2.0 min) | Target: ~75-90s
- Batch 2 (Short / Chapter):       30 images  | 6 workers  (5 rounds)  | Hard Timeout: 210.0s (3.5 min) | Target: ~150-165s
- Batch 3 (Standard Explainer):    60 images  | 9 workers  (7 rounds)  | Hard Timeout: 300.0s (5.0 min) | Target: ~210-230s
- Batch 4 (Bulk Video):            90 images  | 11 workers (9 rounds)  | Hard Timeout: 390.0s (6.5 min) | Target: ~270-300s
- Batch 5 (Max Stress Test):      110 images  | 12 workers (10 rounds) | Hard Timeout: 480.0s (8.0 min) | Target: ~300-330s
- Total:                          300 images  |                        | Global Limit: 1500.0s (25.0 min)

Guarantees:
1. Native `--headless=new` with DISPLAY stripped (zero X11 desktop window popups).
2. PersistentWorkerPool reuse across each batch (zero per-image WebSocket reconnect churn).
3. Registry 1.7.0 Editorial Visual DNA + Tactile Documentary Render Overlay (overscan watermark crop,
   archival paper weave, and Academic Citation Card HUD).
4. Two-stage PIL verification (`im.verify()` + `im.load()`) and aspect ratio check (< 3% tolerance).
5. Standardized sidecar JSON (`jobId`, `forgeId`, `profile_id`, `prompt`, `latency`, `sha256`).
6. Zero-dependency `/proc` RAM sampler (before, peak, after, leaked MB) and `ProcessGroupManager` orphan cleanup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import statistics
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from flow_cdp.cdp_direct_client import PROFILES
from flow_cdp.persistent_pool import PersistentWorkerPool
from flow_cdp.process_manager import get_process_manager
from tools.editorial_compositor import build_editorial_task_spec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("flow_300_rampup")

# 5-Tier Graduated Ramp-Up Specification with Calibrated Workers & Strict Watchdog Timeouts
BATCH_SPECS = [
    {
        "batch_num": 1,
        "name": "batch_1",
        "tier": "Smoke / Warm-up (3 rounds)",
        "count": 10,
        "start_idx": 1,
        "end_idx": 10,
        "workers": 4,
        "timeout_seconds": 120.0,  # 2.0 min hard cap (Expected: ~75-90s)
    },
    {
        "batch_num": 2,
        "name": "batch_2",
        "tier": "Short / Chapter Tier (5 rounds)",
        "count": 30,
        "start_idx": 11,
        "end_idx": 40,
        "workers": 6,
        "timeout_seconds": 210.0,  # 3.5 min hard cap (Expected: ~150-165s)
    },
    {
        "batch_num": 3,
        "name": "batch_3",
        "tier": "Standard Explainer Tier (7 rounds)",
        "count": 60,
        "start_idx": 41,
        "end_idx": 100,
        "workers": 9,
        "timeout_seconds": 300.0,  # 5.0 min hard cap (Expected: ~210-230s)
    },
    {
        "batch_num": 4,
        "name": "batch_4",
        "tier": "Bulk Video Tier (9 rounds)",
        "count": 90,
        "start_idx": 101,
        "end_idx": 190,
        "workers": 11,
        "timeout_seconds": 390.0,  # 6.5 min hard cap (Expected: ~270-300s)
    },
    {
        "batch_num": 5,
        "name": "batch_5",
        "tier": "Max Stress Test (10 rounds)",
        "count": 110,
        "start_idx": 191,
        "end_idx": 300,
        "workers": 12,
        "timeout_seconds": 480.0,  # 8.0 min hard cap (Expected: ~300-330s)
    },
]

GLOBAL_TIMEOUT_SECONDS = 1500.0  # 25.0 min hard ceiling


def build_300_tasks(base_out_dir: Path) -> dict[int, list[dict[str, Any]]]:
    """Build all 300 tasks partitioned into the 5 graduated batches using Editorial Visual DNA."""
    batches: dict[int, list[dict[str, Any]]] = {}

    for b_spec in BATCH_SPECS:
        b_num = b_spec["batch_num"]
        b_dir = base_out_dir / b_spec["name"]
        tasks = [
            build_editorial_task_spec(idx=idx, batch_num=b_num, out_dir=b_dir)
            for idx in range(b_spec["start_idx"], b_spec["end_idx"] + 1)
        ]
        batches[b_num] = tasks
    return batches


def read_system_ram_mb() -> float:
    """Read current system used RAM in MB from /proc/meminfo."""
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            mem = {}
            for line in f:
                if ":" in line:
                    k, v = line.split(":", 1)
                    mem[k.strip()] = int(v.strip().split()[0])
        total_kb = mem.get("MemTotal", 0)
        avail_kb = mem.get("MemAvailable", mem.get("MemFree", 0))
        return round((total_kb - avail_kb) / 1024.0, 1)
    except Exception:
        return 0.0


def read_chrome_cdp_rss_mb() -> tuple[float, int]:
    """Sum RSS memory (MB) and process count of all running google-chrome-cdp processes."""
    page_size = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096
    total_rss_bytes = 0
    proc_count = 0
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return 0.0, 0
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cmdline = (entry / "cmdline").read_bytes().decode("utf-8", errors="ignore")
            if "google-chrome-cdp" in cmdline:
                statm = (entry / "statm").read_text(encoding="utf-8").split()
                if len(statm) >= 2:
                    rss_pages = int(statm[1])
                    total_rss_bytes += rss_pages * page_size
                    proc_count += 1
        except Exception:
            continue
    return round(total_rss_bytes / (1024.0 * 1024.0), 1), proc_count


class RAMSampler:
    """Background daemon sampling system RAM and Chrome CDP RSS every 1.0s."""

    def __init__(self) -> None:
        self.stop_event = threading.Event()
        self.sys_samples: list[float] = []
        self.chrome_rss_samples: list[float] = []
        self.max_chrome_procs: int = 0
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self.stop_event.clear()
        self._sample_once()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _sample_once(self) -> None:
        self.sys_samples.append(read_system_ram_mb())
        rss_mb, cnt = read_chrome_cdp_rss_mb()
        self.chrome_rss_samples.append(rss_mb)
        if cnt > self.max_chrome_procs:
            self.max_chrome_procs = cnt

    def _loop(self) -> None:
        while not self.stop_event.wait(1.0):
            self._sample_once()

    def stop(self) -> None:
        self.stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self._sample_once()

    @property
    def peak_sys_mb(self) -> float:
        return max(self.sys_samples) if self.sys_samples else 0.0

    @property
    def peak_chrome_rss_mb(self) -> float:
        return max(self.chrome_rss_samples) if self.chrome_rss_samples else 0.0


def verify_image_and_sidecar(img_path: Path, expected_ratio: str = "16:9") -> dict[str, Any]:
    """Perform strict two-stage PIL verification and sidecar schema audit."""
    if not img_path.is_file():
        return {"valid": False, "reason": f"Image missing: {img_path}"}
    fsize = img_path.stat().st_size
    if fsize < 5000:
        return {"valid": False, "reason": f"Image too small ({fsize} bytes)"}

    # Stage 1: Container & checksum verification
    try:
        with Image.open(img_path) as im:
            im.verify()
    except Exception as exc:
        return {"valid": False, "reason": f"PIL verify() failed: {exc}"}

    # Stage 2: Full pixel load & aspect ratio verification
    try:
        with Image.open(img_path) as im:
            im.load()
            w, h = im.size
    except Exception as exc:
        return {"valid": False, "reason": f"PIL load() failed: {exc}"}

    target_ratio = (16.0 / 9.0) if expected_ratio == "16:9" else (9.0 / 16.0)
    actual_ratio = w / h if h else 0.0
    if abs(actual_ratio - target_ratio) / target_ratio > 0.03:
        return {"valid": False, "reason": f"Aspect ratio mismatch: {w}x{h} ({actual_ratio:.3f})"}

    # Stage 3: Sidecar verification
    sidecar_path = img_path.with_suffix(".json")
    if not sidecar_path.is_file():
        return {"valid": False, "reason": f"Sidecar missing: {sidecar_path}"}

    try:
        sc = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"valid": False, "reason": f"Invalid sidecar JSON: {exc}"}

    required_keys = ("jobId", "forgeId", "profile_id", "prompt", "latency", "sha256")
    missing = [k for k in required_keys if not sc.get(k) and sc.get(k) != 0]
    if missing:
        return {"valid": False, "reason": f"Sidecar missing keys: {missing}"}

    actual_sha = hashlib.sha256(img_path.read_bytes()).hexdigest()
    if sc.get("sha256") != actual_sha:
        return {"valid": False, "reason": "SHA256 mismatch between image and sidecar"}

    return {
        "valid": True,
        "width": w,
        "height": h,
        "size_bytes": fsize,
        "latency": float(sc.get("latency", 0.0)),
        "profile_id": sc.get("profile_id"),
    }


def load_enabled_profiles() -> list[dict[str, Any]]:
    """Load enabled profiles from ~/.config/video-pilot/flow/profiles.json mapped to PROFILES."""
    reg_path = Path.home() / ".config/video-pilot/flow/profiles.json"
    disabled_ids: set[str] = set()
    if reg_path.is_file():
        try:
            data = json.loads(reg_path.read_text(encoding="utf-8"))
            for p in data.get("profiles", []):
                if not p.get("enabled", True):
                    disabled_ids.add(p["id"])
        except Exception:
            pass
    return [dict(p) for p in PROFILES if p["name"] not in disabled_ids]


def run_single_batch(
    b_spec: dict[str, Any],
    tasks: list[dict[str, Any]],
    base_out_dir: Path,
    global_deadline: float,
) -> dict[str, Any]:
    """Execute one graduated batch with PersistentWorkerPool, hard watchdog, and teardown."""
    b_num = b_spec["batch_num"]
    b_name = b_spec["name"]
    b_dir = base_out_dir / b_name
    b_dir.mkdir(parents=True, exist_ok=True)

    # Filter out already verified tasks (idempotent resume support)
    pending_tasks = []
    pre_verified = 0
    for t in tasks:
        dest_file = b_dir / t["filename"]
        chk = verify_image_and_sidecar(dest_file, t["ratio"])
        if chk["valid"]:
            pre_verified += 1
        else:
            pending_tasks.append(t)

    if not pending_tasks:
        report_path = b_dir / "batch_report.json"
        if report_path.is_file():
            try:
                existing_rep = json.loads(report_path.read_text(encoding="utf-8"))
                if existing_rep.get("elapsed_seconds", 0) > 0 and existing_rep.get("verified_images") == len(tasks):
                    logger.info("=== BATCH %d ALREADY FULLY VERIFIED (%d/%d images) in %.1fs ===", b_num, len(tasks), len(tasks), existing_rep["elapsed_seconds"])
                    return existing_rep
            except Exception:
                pass

    timeout_sec = b_spec["timeout_seconds"]
    remaining_global = max(10.0, global_deadline - time.monotonic())
    effective_timeout = min(timeout_sec, remaining_global)

    logger.info(
        "=== STARTING BATCH %d (%s): %d images (%d pending, %d already verified) | Workers=%d | Hard Timeout=%.1fs ===",
        b_num, b_spec["tier"], b_spec["count"], len(pending_tasks), pre_verified, b_spec["workers"], effective_timeout
    )

    ram_before_sys = read_system_ram_mb()
    ram_before_chrome, _ = read_chrome_cdp_rss_mb()
    sampler = RAMSampler()
    sampler.start()

    t_start = time.monotonic()
    watchdog_triggered = False
    profiles = load_enabled_profiles()
    proc_mgr = get_process_manager()

    pool = PersistentWorkerPool(
        target_workers=b_spec["workers"],
        cooldown_seconds=600.0,
        pacing_seconds=1.5,
        stagger_seconds=0.3,
        headless=True,
        profiles=profiles,
        proc_mgr=proc_mgr,
        default_out_dir=b_dir,
    )

    completed_in_run = 0

    def on_task_done(task: dict[str, Any], res: dict[str, Any] | None, err: Exception | None) -> None:
        nonlocal completed_in_run
        if res and not err:
            completed_in_run += 1
            elapsed = time.monotonic() - t_start
            logger.info(
                "[Batch %d] Progress: %d/%d completed (%s on %s in %.1fs, elapsed %.1fs/%.1fs)",
                b_num,
                pre_verified + completed_in_run,
                b_spec["count"],
                task["filename"],
                res.get("profile_id"),
                res.get("latency", 0.0),
                elapsed,
                effective_timeout,
            )

    if pending_tasks:
        for t in pending_tasks:
            t["callback"] = on_task_done
            pool.submit_task(t, priority=10)

        # Watchdog timer thread to enforce strict timeout ceiling
        def watchdog_func() -> None:
            nonlocal watchdog_triggered
            watchdog_triggered = True
            logger.error(
                "[WATCHDOG ALERT] Batch %d exceeded hard timeout of %.1fs! Triggering immediate abort & failover.",
                b_num, effective_timeout
            )
            pool.abort_event.set()

        timer = threading.Timer(effective_timeout, watchdog_func)
        timer.daemon = True
        timer.start()
        try:
            with pool:
                pool.wait_completion(timeout=effective_timeout + 2.0)
                timer.cancel()
        finally:
            timer.cancel()

    t_tasks_done = time.monotonic()
    gen_elapsed_sec = round(t_tasks_done - t_start, 2)
    elapsed_sec = round(time.monotonic() - t_start, 2)
    sampler.stop()

    # Ensure all spawned Chrome processes are cleanly reaped after the batch
    proc_mgr.terminate_all()
    time.sleep(0.5)

    ram_after_sys = read_system_ram_mb()
    ram_after_chrome, lingering_procs = read_chrome_cdp_rss_mb()

    # Verify all images in batch directory
    verified_count = 0
    failed_verifications = []
    latencies: list[float] = []
    profile_dist: dict[str, int] = {}

    for t in tasks:
        dest_file = b_dir / t["filename"]
        chk = verify_image_and_sidecar(dest_file, t["ratio"])
        if chk["valid"]:
            verified_count += 1
            if chk["latency"] > 0:
                latencies.append(chk["latency"])
            pid = chk.get("profile_id") or "unknown"
            profile_dist[pid] = profile_dist.get(pid, 0) + 1
        else:
            failed_verifications.append({"id": t["id"], "file": t["filename"], "reason": chk["reason"]})

    avg_lat = round(statistics.mean(latencies), 2) if latencies else 0.0
    p50_lat = round(statistics.median(latencies), 2) if latencies else 0.0
    max_lat = round(max(latencies), 2) if latencies else 0.0
    min_lat = round(min(latencies), 2) if latencies else 0.0
    throughput_per_min = round((verified_count / elapsed_sec) * 60.0, 2) if elapsed_sec > 0 else 0.0

    report = {
        "batch_num": b_num,
        "name": b_name,
        "tier": b_spec["tier"],
        "target_images": b_spec["count"],
        "verified_images": verified_count,
        "failed_count": len(failed_verifications),
        "workers_configured": b_spec["workers"],
        "hard_timeout_seconds": timeout_sec,
        "elapsed_seconds": gen_elapsed_sec,
        "total_batch_seconds": elapsed_sec,
        "within_timeout": (not watchdog_triggered) and (gen_elapsed_sec <= timeout_sec),
        "watchdog_triggered": watchdog_triggered,
        "throughput_images_per_min": throughput_per_min,
        "latency_stats": {
            "avg_s": avg_lat,
            "p50_s": p50_lat,
            "min_s": min_lat,
            "max_s": max_lat,
        },
        "ram_metrics": {
            "sys_before_mb": ram_before_sys,
            "sys_peak_mb": sampler.peak_sys_mb,
            "sys_after_mb": ram_after_sys,
            "chrome_rss_before_mb": ram_before_chrome,
            "chrome_rss_peak_mb": sampler.peak_chrome_rss_mb,
            "chrome_rss_after_teardown_mb": ram_after_chrome,
            "lingering_chrome_procs_after_teardown": lingering_procs,
        },
        "incidents_count": len(pool.incidents),
        "incidents": pool.incidents,
        "profile_distribution": profile_dist,
        "failed_verifications": failed_verifications,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    report_path = b_dir / "batch_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(
        "=== BATCH %d SUMMARY: Verified=%d/%d | Elapsed=%.1fs/%.1fs | Avg Latency=%.2fs | Peak Chrome RSS=%.1fMB | Post-Teardown Procs=%d ===",
        b_num, verified_count, b_spec["count"], elapsed_sec, timeout_sec, avg_lat, sampler.peak_chrome_rss_mb, lingering_procs
    )
    return report


def write_comparative_reports(base_out_dir: Path, batch_reports: list[dict[str, Any]], total_elapsed: float) -> None:
    """Write comparison_report.json and COMPARISON_REPORT.md across completed batches."""
    total_target = sum(r["target_images"] for r in batch_reports)
    total_verified = sum(r["verified_images"] for r in batch_reports)
    summary = {
        "total_target_images": total_target,
        "total_verified_images": total_verified,
        "total_elapsed_seconds": round(total_elapsed, 2),
        "global_timeout_seconds": GLOBAL_TIMEOUT_SECONDS,
        "within_global_timeout": total_elapsed <= GLOBAL_TIMEOUT_SECONDS,
        "batches": batch_reports,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    json_path = base_out_dir / "comparison_report.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Báo Cáo Kiểm Thử 300 Ảnh Theo Mô Hình Bậc Thang (Graduated Ramp-Up)",
        "",
        f"- **Tổng số ảnh hợp lệ**: `{total_verified} / {total_target}`",
        f"- **Tổng thời gian thực thi**: `{total_elapsed:.1f}s` ({total_elapsed / 60.0:.2f} phút) / Ngưỡng tối đa `{GLOBAL_TIMEOUT_SECONDS / 60.0:.1f}` phút",
        "",
        "| Đợt | Cấp độ (Tier) | Số ảnh (Đạt/Mục tiêu) | Workers | Thời gian chạy | Ngưỡng tối đa | Độ trễ TB (s) | Tốc độ (ảnh/phút) | Peak Chrome RAM (MB) | Tiến trình sót sau dọn dẹp |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in batch_reports:
        lat = r["latency_stats"]
        ram = r["ram_metrics"]
        status_icon = "PASS" if (r["verified_images"] == r["target_images"] and r["within_timeout"]) else "WARN"
        lines.append(
            f"| **Batch {r['batch_num']}** ({status_icon}) | {r['tier']} | `{r['verified_images']}/{r['target_images']}` | "
            f"{r['workers_configured']} | `{r['elapsed_seconds']:.1f}s` ({r['elapsed_seconds']/60.0:.2f}m) | "
            f"`{r['hard_timeout_seconds']:.0f}s` ({r['hard_timeout_seconds']/60.0:.1f}m) | `{lat['avg_s']:.2f}s` | "
            f"`{r['throughput_images_per_min']:.1f}` | `{ram['chrome_rss_peak_mb']:.1f} MB` | `{ram['lingering_chrome_procs_after_teardown']}` |"
        )

    md_path = base_out_dir / "COMPARISON_REPORT.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="5-Tier 300-Image Graduated Ramp-Up Runner")
    parser.add_argument("--batch", type=int, choices=[1, 2, 3, 4, 5], help="Run a specific batch (1..5)")
    parser.add_argument("--out-dir", type=str, default=str(SYS_DIR / "runs" / "test-300-images"))
    parser.add_argument("--clean-batch", action="store_true", help="Remove existing images in target batch before running")
    args = parser.parse_args()

    base_out_dir = Path(args.out_dir).resolve()
    base_out_dir.mkdir(parents=True, exist_ok=True)
    all_batches = build_300_tasks(base_out_dir)

    target_specs = [s for s in BATCH_SPECS if args.batch is None or s["batch_num"] == args.batch]
    if args.clean_batch:
        for b_spec in target_specs:
            b_dir = base_out_dir / b_spec["name"]
            if b_dir.is_dir():
                shutil.rmtree(b_dir)

    global_start = time.monotonic()
    global_deadline = global_start + GLOBAL_TIMEOUT_SECONDS

    reports: list[dict[str, Any]] = []
    for b_spec in target_specs:
        b_num = b_spec["batch_num"]
        rep = run_single_batch(b_spec, all_batches[b_num], base_out_dir, global_deadline)
        reports.append(rep)

    # Also load any previously completed batch reports so comparison_report is cumulative
    all_reports: list[dict[str, Any]] = []
    for b_spec in BATCH_SPECS:
        rep_file = base_out_dir / b_spec["name"] / "batch_report.json"
        if rep_file.is_file():
            try:
                all_reports.append(json.loads(rep_file.read_text(encoding="utf-8")))
            except Exception:
                pass

    total_elapsed = sum(r.get("elapsed_seconds", 0.0) for r in all_reports)
    write_comparative_reports(base_out_dir, all_reports, total_elapsed)

    failed = any(r["verified_images"] < r["target_images"] or not r["within_timeout"] for r in reports)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
