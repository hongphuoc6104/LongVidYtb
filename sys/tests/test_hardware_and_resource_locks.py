"""Unit tests verifying hardware budget governor, OS resource locks, and partition integrity.

Covers the 6 core optimization & anti-contention invariants:
1. `has_sufficient_dev_shm` and `build_optimized_chrome_launch` flag construction.
2. `ProcessGroupManager` cross-process registry merging and live foreign owner protection.
3. Kernel `flock` primitives (`ProfilePortLock`, `JobExecutionLock`, `GlobalBrowserSlot`)
   blocking excess concurrency across real OS processes and auto-releasing on termination.
4. Channel resource partitions (100% mutually disjoint Flow profiles & Colab accounts,
   exclusion of unauthenticated `profile_11` and disabled `account-02`, and cold-standby
   YouTube Studio profile placement).
5. Zero-CPU zip stored media bundling (`ZIP_STORED` for media, `ZIP_DEFLATED` for metadata).
6. Singleton lock cleanup and PID lifecycle validation.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

SYS_DIR = Path(__file__).resolve().parent.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from colab_bridge.job_protocol import STORE_ONLY_SUFFIXES, bundle  # noqa: E402
from colab_bridge.protocol import file_hash  # noqa: E402
from flow_cdp.process_manager import (  # noqa: E402
    ProcessGroupManager,
    clean_singleton_locks,
    clean_stale_chrome_tmp_artifacts,
    is_pid_alive,
)
from flow_cdp.resource_locks import (  # noqa: E402
    GlobalBrowserSlot,
    JobExecutionLock,
    ProfilePortLock,
    build_optimized_chrome_launch,
    compute_optimal_browser_slots,
    has_sufficient_dev_shm,
    is_port_locked_by_another_process,
)
from tools.channel_production_common import (  # noqa: E402
    CHANNEL_RESOURCE_PARTITIONS,
    get_channel_slice,
)


class HardwareAndResourceLocksTests(unittest.TestCase):
    """Test suite for hardware-aware Chrome flags, cross-process locks, and resource partitions."""

    def test_dev_shm_detection_and_chrome_flags(self) -> None:
        """Verify dev/shm tmpfs detection and GPU/low-footprint Chrome launch flag construction."""
        # 1. Dev shm detection with valid path vs non-existent path
        self.assertTrue(
            has_sufficient_dev_shm(min_free_mb=64, shm_path="/dev/shm"),
            "Host /dev/shm should have at least 64 MiB available tmpfs RAM",
        )
        self.assertFalse(
            has_sufficient_dev_shm(min_free_mb=512, shm_path="/nonexistent_path_dev_shm_test"),
            "Non-existent shm path must return False",
        )

        # 2. build_optimized_chrome_launch omits --disable-dev-shm-usage when /dev/shm is sufficient
        cmd_shm, _ = build_optimized_chrome_launch(
            binary="google-chrome",
            user_data_dir="/tmp/test_ud",
            profile_dir="Default",
            port=9222,
            url="https://flow.google.com/",
            shm_path="/dev/shm",
        )
        self.assertNotIn(
            "--disable-dev-shm-usage",
            cmd_shm,
            "Should omit --disable-dev-shm-usage on workstation host with sufficient /dev/shm",
        )

        # 3. build_optimized_chrome_launch includes --disable-dev-shm-usage on constrained/missing shm
        cmd_no_shm, _ = build_optimized_chrome_launch(
            binary="google-chrome",
            user_data_dir="/tmp/test_ud",
            profile_dir="Default",
            port=9222,
            url="https://flow.google.com/",
            shm_path="/nonexistent_path_dev_shm_test",
        )
        self.assertIn(
            "--disable-dev-shm-usage",
            cmd_no_shm,
            "Must fall back to --disable-dev-shm-usage when /dev/shm is constrained or missing",
        )

        # 4. GPU hardware acceleration flags when DISPLAY is set
        cmd_gpu, env_gpu = build_optimized_chrome_launch(
            binary="google-chrome",
            user_data_dir="/tmp/test_ud",
            profile_dir="Default",
            port=9222,
            url="https://flow.google.com/",
            headless=True,
            env={"DISPLAY": ":0"},
        )
        gpu_flags = [
            "--enable-gpu-rasterization",
            "--ignore-gpu-blocklist",
            "--enable-zero-copy",
            "--disable-software-rasterizer",
            "--use-gl=angle",
            "--use-angle=gl",
            "--ozone-platform=x11",
        ]
        for gf in gpu_flags:
            self.assertIn(gf, cmd_gpu, f"GPU flag {gf} must be present when DISPLAY is available")
        self.assertEqual(env_gpu.get("DISPLAY"), ":0")
        self.assertEqual(env_gpu.get("__NV_PRIME_RENDER_OFFLOAD"), "1")
        self.assertEqual(env_gpu.get("__GLX_VENDOR_LIBRARY_NAME"), "nvidia")
        self.assertTrue(
            any(f.startswith("--force-gpu-mem-available-mb=") for f in cmd_gpu),
            "Should allocate 90% VRAM budget via --force-gpu-mem-available-mb when GPU is detected",
        )

        # 5. Low-footprint and stability flags
        required_flags = [
            "--disable-extensions",
            "--disable-component-update",
            "--component-updater=url-source=http://127.0.0.1:1",
            "--num-raster-threads=2",
            "--window-size=800,600",
            "--disk-cache-size=67108864",
            "--media-cache-size=16777216",
            "--remote-debugging-port=9222",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--disable-sync",
            "--headless=new",
            "--hide-scrollbars",
            "--mute-audio",
        ]
        for rf in required_flags:
            self.assertIn(rf, cmd_gpu, f"Required optimization flag {rf} must be present in Chrome launch args")

    def test_cross_process_registry_merge_and_foreign_owner_protection(self) -> None:
        """Verify registry read-modify-write merges entries and preserves live foreign owner instances."""
        with tempfile.TemporaryDirectory() as td:
            reg_file = Path(td) / "chrome_pids_global.json"

            # Pre-populate on-disk registry with:
            # - Process B: live foreign process (owner_pid = os.getppid())
            # - Process C: dead orphan process (owner_pid = 99999999)
            foreign_live_pid = os.getppid()
            self.assertTrue(is_pid_alive(foreign_live_pid), "Parent PID must be alive for foreign owner test")
            dead_orphan_pid = 99999999
            self.assertFalse(is_pid_alive(dead_orphan_pid), "PID 99999999 must not be alive")

            initial_data = {
                "updated_at": time.time(),
                "processes": {
                    "9302": {
                        "port": 9302,
                        "pid": foreign_live_pid,
                        "pgid": foreign_live_pid,
                        "owner_pid": foreign_live_pid,
                        "user_data_dir": str(Path(td) / "prof_b"),
                        "profile_dir": "Profile B",
                        "started_at": time.time(),
                        "headless": True,
                    },
                    "9303": {
                        "port": 9303,
                        "pid": dead_orphan_pid,
                        "pgid": dead_orphan_pid,
                        "owner_pid": dead_orphan_pid,
                        "user_data_dir": str(Path(td) / "prof_c"),
                        "profile_dir": "Profile C",
                        "started_at": time.time() - 3600,
                        "headless": True,
                    },
                },
            }
            reg_file.write_text(json.dumps(initial_data, indent=2), encoding="utf-8")

            # Initialize ProcessGroupManager for Process A (current process)
            mgr_a = ProcessGroupManager(registry_file=reg_file, auto_cleanup_on_exit=False)

            # Process A registers its own active process on port 9301
            current_pid = os.getpid()
            mgr_a.active_processes[9301] = {
                "port": 9301,
                "pid": current_pid,
                "pgid": current_pid,
                "owner_pid": current_pid,
                "user_data_dir": str(Path(td) / "prof_a"),
                "profile_dir": "Profile A",
                "started_at": time.time(),
                "headless": True,
            }

            # 1. Verify _save_registry() merges active_processes into on-disk registry without wiping
            mgr_a._save_registry()
            disk_data = json.loads(reg_file.read_text(encoding="utf-8"))
            disk_procs = disk_data.get("processes", {})

            self.assertIn("9301", disk_procs, "Process A (port 9301) must be in merged registry")
            self.assertIn("9302", disk_procs, "Process B (port 9302) must be preserved in merged registry")
            self.assertIn("9303", disk_procs, "Process C (port 9303) must be preserved in merged registry")
            self.assertEqual(disk_procs["9302"]["owner_pid"], foreign_live_pid)

            # 2. Verify terminate_all(include_foreign_live_owners=False) removes A and dead orphan C,
            #    while strictly preserving live foreign owner B
            with patch("flow_cdp.process_manager.time.sleep", return_value=None):
                closed = mgr_a.terminate_all(include_foreign_live_owners=False)

            self.assertIn(9301, closed, "Process A port 9301 should be reaped")
            self.assertIn(9303, closed, "Dead orphan Process C port 9303 should be reaped")
            self.assertNotIn(9302, closed, "Live foreign owner Process B port 9302 must NOT be reaped")

            post_teardown = json.loads(reg_file.read_text(encoding="utf-8")).get("processes", {})
            self.assertNotIn("9301", post_teardown, "Port 9301 must be removed from disk registry")
            self.assertNotIn("9303", post_teardown, "Dead orphan port 9303 must be removed from disk registry")
            self.assertIn("9302", post_teardown, "Live foreign owner port 9302 MUST remain in disk registry")
            self.assertEqual(post_teardown["9302"]["owner_pid"], foreign_live_pid)

    def test_cross_process_flock_primitives(self) -> None:
        """Verify ProfilePortLock, JobExecutionLock, and GlobalBrowserSlot block across real OS processes."""
        with tempfile.TemporaryDirectory() as td:
            locks_dir = Path(td) / "locks"

            child_helper_code = """
import sys
from pathlib import Path

sys_dir = sys.argv[4]
if sys_dir not in sys.path:
    sys.path.insert(0, sys_dir)

from flow_cdp.resource_locks import ProfilePortLock, JobExecutionLock, GlobalBrowserSlot

lock_type = sys.argv[1]
arg = sys.argv[2]
locks_dir = Path(sys.argv[3])

if lock_type == 'port':
    lock = ProfilePortLock(port=int(arg), locks_dir=locks_dir)
elif lock_type == 'job':
    lock = JobExecutionLock(job_id=arg, locks_dir=locks_dir)
elif lock_type == 'slot':
    lock = GlobalBrowserSlot(max_slots=int(arg), locks_dir=locks_dir)
else:
    sys.exit(1)

if lock.try_acquire():
    print("ACQUIRED", flush=True)
    try:
        sys.stdin.read()
    except (KeyboardInterrupt, EOFError):
        pass
else:
    print("FAILED", flush=True)
"""
            # Subprocess helper launcher
            def spawn_child(l_type: str, l_arg: str) -> subprocess.Popen:
                proc = subprocess.Popen(
                    [sys.executable, "-c", child_helper_code, l_type, l_arg, str(locks_dir), str(SYS_DIR)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                assert proc.stdout is not None
                line = proc.stdout.readline().strip()
                self.assertEqual(line, "ACQUIRED", f"Child failed to acquire {l_type} {l_arg}")
                return proc

            # A. Test ProfilePortLock
            test_port = 9295
            child_port = spawn_child("port", str(test_port))
            try:
                # Parent attempt while child holds lock must fail
                parent_port_lock = ProfilePortLock(port=test_port, locks_dir=locks_dir)
                self.assertFalse(parent_port_lock.try_acquire(), "Port lock should be blocked by child")
                self.assertTrue(
                    is_port_locked_by_another_process(test_port, locks_dir=locks_dir),
                    "Port lock should register as locked by another process",
                )

                # Kill child with SIGKILL: OS flock must automatically release
                child_port.send_signal(signal.SIGKILL)
                child_port.wait()
                time.sleep(0.05)

                self.assertTrue(
                    parent_port_lock.try_acquire(),
                    "Parent must acquire port lock after child terminates",
                )
                parent_port_lock.release()
            finally:
                if child_port.poll() is None:
                    child_port.kill()
                    child_port.wait()

            # B. Test JobExecutionLock
            job_name = "test_qa_job_alpha"
            child_job = spawn_child("job", job_name)
            try:
                parent_job_lock = JobExecutionLock(job_id=job_name, locks_dir=locks_dir)
                self.assertFalse(parent_job_lock.try_acquire(), "Job lock should be blocked by child")

                child_job.send_signal(signal.SIGKILL)
                child_job.wait()
                time.sleep(0.05)

                self.assertTrue(
                    parent_job_lock.try_acquire(),
                    "Parent must acquire job lock after child terminates",
                )
                parent_job_lock.release()
            finally:
                if child_job.poll() is None:
                    child_job.kill()
                    child_job.wait()

            # C. Test GlobalBrowserSlot with max_slots=2
            slot_p1 = spawn_child("slot", "2")
            slot_p2 = spawn_child("slot", "2")
            try:
                parent_slot = GlobalBrowserSlot(max_slots=2, locks_dir=locks_dir)
                # Both slots 0 and 1 are held: parent must be blocked
                self.assertFalse(parent_slot.try_acquire(), "Parent must be blocked when all 2 slots are occupied")

                # Kill child 1: frees one slot
                slot_p1.send_signal(signal.SIGKILL)
                slot_p1.wait()
                time.sleep(0.05)

                # Parent can now acquire
                self.assertTrue(parent_slot.try_acquire(), "Parent must acquire slot after one child exits")
                self.assertIn(parent_slot.slot_index, (0, 1))
                parent_slot.release()
            finally:
                for sp in (slot_p1, slot_p2):
                    if sp.poll() is None:
                        sp.kill()
                        sp.wait()

    def test_channel_resource_partitions_100_percent_disjoint(self) -> None:
        """Verify across all 39 channels: Wave-1 disjoint slices, exclusion of invalid profiles/accounts, and YT standby."""
        yt_map_file = SYS_DIR / "channels/youtube_channel_map.json"
        yt_data: dict[str, dict] | None = None
        if yt_map_file.is_file():
            yt_data = json.loads(yt_map_file.read_text(encoding="utf-8"))["channels"]

        expected_channels = len(yt_data) if yt_data is not None else 38
        self.assertEqual(len(CHANNEL_RESOURCE_PARTITIONS), expected_channels, f"Must partition all {expected_channels} fleet channels")
        if yt_data is not None:
            self.assertEqual(set(CHANNEL_RESOURCE_PARTITIONS.keys()), set(yt_data.keys()))

        wave1_channels = {
            "nao_luoi",
            "tui_tien",
            "ua_sao_vay",
            "su_ke_lai",
            "thuong_cho_kheo",
            "ho_so_ky_la",
            "co_the_ke",
            "ai_binh_dan",
        }
        seen_wave1_flow_profiles: dict[str, str] = {}
        seen_wave1_colab_accounts: dict[str, str] = {}
        seen_youtube_profiles: dict[str, str] = {}

        for ch_name, part in CHANNEL_RESOURCE_PARTITIONS.items():
            flow_profs = part["flow_profiles"]
            colab_accs = part["colab_accounts"]
            yt_prof = part["youtube_profile"]

            self.assertGreaterEqual(len(flow_profs), 2, f"{ch_name} must have at least 2 Flow profiles")
            self.assertGreaterEqual(len(colab_accs), 1, f"{ch_name} must have at least 1 Colab account")

            # Invariant 1: Valid 19-profile Flow pool only (no profile_11, no disabled account-02)
            valid_flow_pool = {f"profile_{i}" for i in range(1, 21) if i != 11}
            for fp in flow_profs:
                self.assertIn(fp, valid_flow_pool, f"{ch_name} flow_profile {fp} must belong to valid 19-profile Flow pool")
            self.assertNotIn("account-02", colab_accs, f"{ch_name} must not contain disabled account-02")

            # Invariant 2: Dedicated 1-to-1 YouTube Studio profile matches SSOT map; if shared with Flow pool, placed LAST
            if yt_data is not None:
                expected_yt = yt_data[ch_name]["profile_id"]
                self.assertEqual(yt_prof, expected_yt, f"{ch_name} youtube_profile must match youtube_channel_map.json")
            if ch_name not in ("en_scale_and_bone", "en_root_and_canopy", "en_spawn_to_apex", "en_deep_time_strata"):
                self.assertNotIn(
                    yt_prof,
                    seen_youtube_profiles,
                    f"YouTube profile {yt_prof} in {ch_name} collides with {seen_youtube_profiles.get(yt_prof)}",
                )
                seen_youtube_profiles[yt_prof] = ch_name
            if yt_prof in flow_profs:
                self.assertEqual(
                    flow_profs[-1],
                    yt_prof,
                    f"{ch_name} YouTube Studio profile must be placed LAST in flow_profiles as non-primary standby",
                )

            # Invariant 3 & 4: Wave-1 concurrent 8-channel batch has 100% mutually disjoint Flow & Colab slices
            if ch_name in wave1_channels:
                for fp in flow_profs:
                    self.assertNotIn(
                        fp,
                        seen_wave1_flow_profiles,
                        f"Flow profile {fp} in {ch_name} collides with {seen_wave1_flow_profiles.get(fp)}",
                    )
                    seen_wave1_flow_profiles[fp] = ch_name
                for ca in colab_accs:
                    self.assertNotIn(
                        ca,
                        seen_wave1_colab_accounts,
                        f"Colab account {ca} in {ch_name} collides with {seen_wave1_colab_accounts.get(ca)}",
                    )
                    seen_wave1_colab_accounts[ca] = ch_name

            # Invariant 5: get_channel_slice helper consistency
            slice_fps, slice_cas, slice_sess = get_channel_slice(ch_name)
            self.assertEqual(slice_fps, flow_profs)
            self.assertEqual(slice_cas, colab_accs)
            self.assertEqual(slice_sess, part["session"])

    def test_zero_cpu_zip_stored_media_bundling(self) -> None:
        """Verify job_protocol.bundle stores media files with ZIP_STORED and text/json with ZIP_DEFLATED."""
        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            jpg_file = base_dir / "sample.jpg"
            jpg_file.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 200)

            png_file = base_dir / "sample.png"
            png_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)

            json_file = base_dir / "content.json"
            json_file.write_text(json.dumps({"title": "Test Title", "scenes": []}), encoding="utf-8")

            txt_file = base_dir / "notes.txt"
            txt_file.write_text("Plain text production instructions", encoding="utf-8")

            request = {
                "operation": "render",
                "files": [
                    {
                        "name": "assets/sample.jpg",
                        "local_path": str(jpg_file),
                        "size": jpg_file.stat().st_size,
                        "sha256": file_hash(jpg_file),
                    },
                    {
                        "name": "assets/sample.png",
                        "local_path": str(png_file),
                        "size": png_file.stat().st_size,
                        "sha256": file_hash(png_file),
                    },
                    {
                        "name": "data/content.json",
                        "local_path": str(json_file),
                        "size": json_file.stat().st_size,
                        "sha256": file_hash(json_file),
                    },
                    {
                        "name": "docs/notes.txt",
                        "local_path": str(txt_file),
                        "size": txt_file.stat().st_size,
                        "sha256": file_hash(txt_file),
                    },
                ],
            }

            bundle_zip = base_dir / "render_job.zip"
            bundle(request, bundle_zip)

            self.assertTrue(bundle_zip.is_file(), "Bundle zip file must be generated")

            # Verify compression types in archive
            with zipfile.ZipFile(bundle_zip, "r") as zf:
                info_map = {item.filename: item.compress_type for item in zf.infolist()}

                # Media files must use ZIP_STORED (compress_type = 0) to avoid re-compressing encoded media
                self.assertEqual(
                    info_map["assets/sample.jpg"],
                    zipfile.ZIP_STORED,
                    ".jpg media must be bundled with ZIP_STORED",
                )
                self.assertEqual(
                    info_map["assets/sample.png"],
                    zipfile.ZIP_STORED,
                    ".png media must be bundled with ZIP_STORED",
                )

                # Text and JSON files must use ZIP_DEFLATED (compress_type = 8)
                self.assertEqual(
                    info_map["data/content.json"],
                    zipfile.ZIP_DEFLATED,
                    ".json files must be bundled with ZIP_DEFLATED",
                )
                self.assertEqual(
                    info_map["docs/notes.txt"],
                    zipfile.ZIP_DEFLATED,
                    ".txt files must be bundled with ZIP_DEFLATED",
                )
                self.assertEqual(
                    info_map["request.json"],
                    zipfile.ZIP_DEFLATED,
                    "request.json manifest must be bundled with ZIP_DEFLATED",
                )

            # Ensure STORE_ONLY_SUFFIXES set contains standard media formats
            for ext in (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mp3", ".zip"):
                self.assertIn(ext, STORE_ONLY_SUFFIXES)

    def test_singleton_lock_cleanup_and_port_probing(self) -> None:
        """Verify clean_singleton_locks removes Chromium lock files/symlinks."""
        with tempfile.TemporaryDirectory() as td:
            ud_dir = Path(td) / "user_data"
            prof_dir = ud_dir / "Default"
            prof_dir.mkdir(parents=True)

            # Create mock singleton files/symlinks in both directories
            (ud_dir / "SingletonLock").touch()
            (ud_dir / "SingletonCookie").touch()
            (prof_dir / "SingletonSocket").touch()

            cleaned = clean_singleton_locks(ud_dir, "Default")
            self.assertEqual(len(cleaned), 3, "Should clean exactly 3 singleton lock files")
            self.assertFalse((ud_dir / "SingletonLock").exists())
            self.assertFalse((ud_dir / "SingletonCookie").exists())
            self.assertFalse((prof_dir / "SingletonSocket").exists())

    def test_stale_chrome_tmp_url_fetcher_cleanup(self) -> None:
        """Verify stale owned url_fetcher_* dirs are swept while recent/open/other dirs stay intact."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stale_dir = root / "url_fetcher_stale_001"
            fresh_dir = root / "url_fetcher_fresh_002"
            open_dir = root / "url_fetcher_open_003"
            other_dir = root / "unrelated_folder"
            for d in (stale_dir, fresh_dir, open_dir, other_dir):
                d.mkdir()
                (d / "payload.bin").write_bytes(b"x" * 64)

            old_ts = time.time() - 3600
            os.utime(stale_dir, (old_ts, old_ts))
            os.utime(open_dir, (old_ts, old_ts))
            os.utime(other_dir, (old_ts, old_ts))

            # Hold an open file descriptor inside open_dir so /proc/<pid>/fd protects it
            with open(open_dir / "payload.bin", "rb"):
                cleaned = clean_stale_chrome_tmp_artifacts(tmp_dir=root, min_age_seconds=600.0)

            self.assertEqual(cleaned, [str(stale_dir.resolve())])
            self.assertFalse(stale_dir.exists())
            self.assertTrue(fresh_dir.exists())
            self.assertTrue(open_dir.exists())
            self.assertTrue(other_dir.exists())

    def test_compute_optimal_browser_slots(self) -> None:
        """Verify dynamic calculation of optimal Chrome browser slots based on GPU VRAM and env."""
        # 1. Explicit env var overrides GPU detection
        with patch.dict(os.environ, {"VP_MAX_CHROME_INSTANCES": "12"}):
            self.assertEqual(compute_optimal_browser_slots(), 12)
        with patch.dict(os.environ, {"VP_MAX_CHROME_INSTANCES": "4"}):
            self.assertEqual(compute_optimal_browser_slots(), 4)

        # 2. No env var -> uses get_gpu_vram_mb
        with patch.dict(os.environ, {}, clear=True):
            # No GPU detected -> fallback 8
            with patch("flow_cdp.resource_locks.get_gpu_vram_mb", return_value=None):
                self.assertEqual(compute_optimal_browser_slots(), 8)

            # Quadro P620 (1843 MiB): (1843 - 180) // 110 = 15 slots
            with patch("flow_cdp.resource_locks.get_gpu_vram_mb", return_value=1843):
                self.assertEqual(compute_optimal_browser_slots(), 15)

            # High-end GPU (8000 MiB): clamped to max 16
            with patch("flow_cdp.resource_locks.get_gpu_vram_mb", return_value=8000):
                self.assertEqual(compute_optimal_browser_slots(), 16)

            # Constrained GPU (400 MiB): clamped to min 8
            with patch("flow_cdp.resource_locks.get_gpu_vram_mb", return_value=400):
                self.assertEqual(compute_optimal_browser_slots(), 8)


if __name__ == "__main__":
    unittest.main()
