"""Cross-Process OS Resource Locks & Hardware Budget Governor for Local Chrome Workers.

Provides kernel-backed `fcntl.flock` synchronization primitives (automatically released by
Linux upon process exit or SIGKILL) and hardware-aware Chrome flag construction tuned for
workstation hosts (e.g. Xeon 4C/8T + NVIDIA Quadro P620 2GB VRAM + tmpfs /dev/shm):

1. `has_sufficient_dev_shm`: Uses RAM `/dev/shm` tmpfs when >= 512 MiB is free, eliminating
   `--disable-dev-shm-usage` SSD `/tmp` I/O thrashing on bare-metal Linux while preserving
   fallback safety inside restricted 64 MiB Docker containers.
2. `build_optimized_chrome_launch`: Single SSOT builder for GPU-accelerated, low-footprint
   Chrome command-line flags and X11 display environment.
3. `ProfilePortLock`: Exclusive cross-process lock per CDP port preventing two jobs (or
   Flow CDP + YouTube Studio publisher) from colliding on the same browser instance.
4. `GlobalBrowserSlot`: Cross-process counting semaphore capping total concurrent Chrome
   instances across the entire machine (default 8 slots, configurable via
   `VP_MAX_CHROME_INSTANCES`) to prevent VRAM/RAM/Swap exhaustion.
5. `JobExecutionLock`: Exclusive per-job lock preventing duplicate `produce_channel_*`
   runners on the same `job_id`.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import time
from pathlib import Path
from typing import IO, Any

LOCKS_DIR = Path.home() / ".cache/video-pilot/locks"
DEFAULT_MAX_GLOBAL_BROWSERS = int(os.environ.get("VP_MAX_CHROME_INSTANCES", "16"))
DEFAULT_MAX_BROWSER_SLOTS = DEFAULT_MAX_GLOBAL_BROWSERS
MIN_DEV_SHM_FREE_MB = 512


def ensure_locks_dir(locks_dir: Path | None = None) -> Path:
    """Ensure the cross-process lock directory exists with user-private permissions."""
    target = (locks_dir or LOCKS_DIR).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    return target


def has_sufficient_dev_shm(min_free_mb: int = MIN_DEV_SHM_FREE_MB, shm_path: str | Path = "/dev/shm") -> bool:
    """Return True when `/dev/shm` exists and has at least `min_free_mb` MiB available.

    On bare-metal Linux workstations `/dev/shm` is a fast RAM `tmpfs` (typically 50% of RAM),
    whereas `--disable-dev-shm-usage` forces Chromium to spill IPC shared-memory tiles onto
    `/tmp` (often backed by a physical SATA/NVMe disk), causing severe I/O wait under multi-agent load.
    """
    p = Path(shm_path)
    if not p.is_dir():
        return False
    try:
        st = os.statvfs(str(p))
        free_bytes = st.f_bavail * st.f_frsize
        return free_bytes >= int(min_free_mb) * 1024 * 1024
    except OSError:
        return False


def detect_local_gpu_display(env: dict[str, str] | None = None) -> tuple[bool, dict[str, str]]:
    """Prepare environment variables for local X11/NVIDIA hardware acceleration if available."""
    base_env = dict(os.environ if env is None else env)
    has_display = bool(base_env.get("DISPLAY") or os.path.exists("/tmp/.X11-unix/X0"))
    if has_display:
        base_env["DISPLAY"] = base_env.get("DISPLAY") or ":0"
        if "XAUTHORITY" not in base_env:
            xauth = os.path.expanduser("~/.Xauthority")
            if os.path.exists(xauth):
                base_env["XAUTHORITY"] = xauth
    return has_display, base_env


def build_optimized_chrome_launch(
    binary: str,
    user_data_dir: str | Path,
    profile_dir: str | None,
    port: int,
    url: str,
    headless: bool = True,
    env: dict[str, str] | None = None,
    shm_path: str | Path = "/dev/shm",
    extra_args: list[str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    """Construct hardware-accelerated, low-contention Chrome CLI arguments and environment."""
    has_display, out_env = detect_local_gpu_display(env)
    if not has_display:
        if headless:
            out_env.pop("DISPLAY", None)
            out_env.pop("XAUTHORITY", None)
        else:
            out_env["DISPLAY"] = ":0"

    target_dir = Path(user_data_dir).expanduser().resolve()
    cmd: list[str] = [
        binary,
        f"--user-data-dir={target_dir}",
    ]
    if profile_dir:
        cmd.append(f"--profile-directory={profile_dir}")

    cmd.extend([
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-component-update",
        "--component-updater=url-source=http://127.0.0.1:1",
        "--disable-extensions",
        "--disable-component-extensions-with-background-pages",
        "--disable-sync",
        "--disable-translate",
        "--disable-default-apps",
        "--host-resolver-rules=MAP edgedl.me.gvt1.com ~NOTFOUND, MAP *.gvt1.com ~NOTFOUND",
        "--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode,OptimizationGuideModelDownloading,OptimizationGuideOnDeviceModel,OptimizationHints,OptimizationHintsFetching,OptimizationTargetPrediction,Translate",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-hang-monitor",
        "--window-size=800,600",
        "--num-raster-threads=2",
        "--disk-cache-size=67108864",
        "--media-cache-size=16777216",
    ])

    # Only fall back to disk-backed /tmp shared memory when /dev/shm is constrained (e.g. Docker 64MB)
    if not has_sufficient_dev_shm(MIN_DEV_SHM_FREE_MB, shm_path=shm_path):
        cmd.append("--disable-dev-shm-usage")

    if has_display:
        cmd.extend([
            "--enable-gpu-rasterization",
            "--ignore-gpu-blocklist",
            "--enable-zero-copy",
            "--use-gl=angle",
            "--use-angle=gl",
        ])

    if headless:
        cmd.extend([
            "--headless=new",
            "--hide-scrollbars",
            "--mute-audio",
        ])

    if extra_args:
        custom_window = next((a for a in extra_args if a.startswith("--window-size=")), None)
        if custom_window:
            cmd = [c for c in cmd if not c.startswith("--window-size=")]
        cmd.extend(extra_args)

    cmd.append(url)
    return cmd, out_env


class _FlockHandle:
    """Base kernel flock wrapper safe across forks, threads, and crashes."""

    def __init__(self, lock_path: Path, metadata: dict[str, Any] | None = None):
        self.lock_path = lock_path
        self.metadata = metadata or {}
        self._fh: IO[str] | None = None

    @property
    def acquired(self) -> bool:
        return self._fh is not None

    def try_acquire(self) -> bool:
        if self._fh is not None:
            return True
        self.lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fh = open(self.lock_path, "a+", encoding="utf-8")
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fh.close()
            return False
        except OSError:
            fh.close()
            return False

        try:
            fh.seek(0)
            fh.truncate()
            payload = {
                "pid": os.getpid(),
                "acquired_at": time.time(),
                **self.metadata,
            }
            fh.write(json.dumps(payload) + "\n")
            fh.flush()
        except OSError:
            pass
        self._fh = fh
        return True

    def acquire(self, timeout: float = 30.0, poll_interval: float = 0.25) -> bool:
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            if self.try_acquire():
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(min(poll_interval, max(0.01, deadline - time.monotonic())))

    def release(self) -> None:
        fh = self._fh
        self._fh = None
        if fh is not None:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                fh.close()
            except OSError:
                pass

    def __enter__(self) -> _FlockHandle:
        if not self.acquire():
            raise TimeoutError(f"Timed out acquiring lock {self.lock_path}")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.release()


class ProfilePortLock(_FlockHandle):
    """Exclusive cross-process lock for a Chrome CDP debugging port."""

    def __init__(self, port: int, owner_tag: str = "", locks_dir: Path | None = None):
        self.port = int(port)
        base = ensure_locks_dir(locks_dir)
        super().__init__(
            base / f"cdp_port_{self.port}.lock",
            metadata={"port": self.port, "owner": owner_tag},
        )


def is_port_locked_by_another_process(port: int, locks_dir: Path | None = None) -> bool:
    """Non-destructively probe whether another process currently holds `ProfilePortLock(port)`."""
    base = ensure_locks_dir(locks_dir)
    lock_file = base / f"cdp_port_{int(port)}.lock"
    if not lock_file.is_file():
        return False
    fh = open(lock_file, "a+", encoding="utf-8")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        return True
    except OSError:
        fh.close()
        return False
    else:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()
        return False


class GlobalBrowserSlot:
    """Cross-process counting semaphore capping total concurrent Chrome instances on the host."""

    def __init__(
        self,
        max_slots: int | None = None,
        owner_tag: str = "",
        locks_dir: Path | None = None,
    ):
        env_max = os.environ.get("VP_MAX_CHROME_INSTANCES")
        resolved_max = int(env_max) if (env_max and env_max.isdigit()) else DEFAULT_MAX_BROWSER_SLOTS
        self.max_slots = max(1, int(max_slots if max_slots is not None else resolved_max))
        self.owner_tag = owner_tag
        self.locks_dir = ensure_locks_dir(locks_dir)
        self.slot_index: int | None = None
        self._handle: _FlockHandle | None = None

    @property
    def acquired(self) -> bool:
        return self._handle is not None and self._handle.acquired

    def try_acquire(self) -> bool:
        if self.acquired:
            return True
        for idx in range(self.max_slots):
            h = _FlockHandle(
                self.locks_dir / f"browser_slot_{idx:02d}.lock",
                metadata={"slot": idx, "owner": self.owner_tag},
            )
            if h.try_acquire():
                self._handle = h
                self.slot_index = idx
                return True
        return False

    def acquire(self, timeout: float = 120.0, poll_interval: float = 0.5) -> bool:
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            if self.try_acquire():
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(min(poll_interval, max(0.05, deadline - time.monotonic())))

    def release(self) -> None:
        if self._handle is not None:
            self._handle.release()
            self._handle = None
        self.slot_index = None

    def __enter__(self) -> GlobalBrowserSlot:
        if not self.acquire():
            raise TimeoutError(f"All {self.max_slots} global Chrome browser slots busy")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.release()


class JobExecutionLock(_FlockHandle):
    """Exclusive cross-process lock ensuring a `job_id` is never executed twice concurrently."""

    def __init__(self, job_id: str, locks_dir: Path | None = None):
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", job_id.strip()) or "default_job"
        base = ensure_locks_dir(locks_dir)
        self.job_id = job_id
        super().__init__(
            base / f"job_{safe_id}.lock",
            metadata={"job_id": job_id},
        )
