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
import random
import re
import subprocess
import time
from pathlib import Path
from typing import IO, Any

LOCKS_DIR = Path.home() / ".cache/video-pilot/locks"
MIN_DEV_SHM_FREE_MB = 512
UNAUTHENTICATED_FILE_NAME = "unauthenticated_profiles.json"


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


def get_gpu_vram_mb(budget_ratio: float = 0.90) -> int | None:
    """Detect total local NVIDIA GPU VRAM in MiB and return the budgeted amount (default 90%)."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0,
        ).strip()
        lines = [line.strip() for line in out.splitlines() if line.strip().isdigit()]
        if lines:
            total_mb = int(lines[0])
            if total_mb > 0:
                return max(256, int(total_mb * budget_ratio))
    except Exception:
        pass
    return None


def get_host_ram_total_mb() -> int | None:
    """Return total host system RAM in MiB from `/proc/meminfo`, or None if unavailable."""
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        return max(256, int(parts[1]) // 1024)
    except OSError:
        pass
    return None


def get_host_ram_available_mb() -> int | None:
    """Return currently available host RAM (`MemAvailable`) in MiB from `/proc/meminfo`."""
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        return max(0, int(parts[1]) // 1024)
    except OSError:
        pass
    return None


def compute_optimal_browser_slots(
    budget_ratio: float = 0.90,
    per_browser_vram_mb: int = 110,
    xorg_reserve_mb: int = 180,
    ram_total_mb: int | None = None,
    cpu_threads: int | None = None,
) -> int:
    """Compute optimal concurrency slots bounded by GPU VRAM, host RAM, and CPU threads."""
    env_max = os.environ.get("VP_MAX_CHROME_INSTANCES")
    if env_max is not None and env_max.strip() != "":
        try:
            return max(1, int(env_max))
        except ValueError:
            pass

    vram_mb = get_gpu_vram_mb(budget_ratio=budget_ratio)
    if vram_mb is not None:
        vram_slots = max(8, min(16, (vram_mb - xorg_reserve_mb) // per_browser_vram_mb))
    else:
        vram_slots = 8

    eff_ram = ram_total_mb if ram_total_mb is not None else get_host_ram_total_mb()
    if eff_ram is not None:
        ram_budget_slots = max(2, (eff_ram - 7168) // 900)
        if eff_ram <= 16800:
            ram_cap = 4
        elif eff_ram <= 32768:
            ram_cap = 6
        else:
            ram_cap = 16
        ram_slots = min(ram_cap, ram_budget_slots)
    else:
        ram_slots = 16

    eff_cpu = cpu_threads if cpu_threads is not None else os.cpu_count()
    if eff_cpu is not None:
        if eff_cpu <= 8:
            cpu_slots = 4
        elif eff_cpu <= 16:
            cpu_slots = 6
        else:
            cpu_slots = 16
    else:
        cpu_slots = 16

    return max(2, min(vram_slots, ram_slots, cpu_slots))


DEFAULT_MAX_GLOBAL_BROWSERS = compute_optimal_browser_slots()
DEFAULT_MAX_BROWSER_SLOTS = DEFAULT_MAX_GLOBAL_BROWSERS


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
            else:
                try:
                    uid = os.getuid()
                    gdm_auth = f"/run/user/{uid}/gdm/Xauthority"
                    if os.path.exists(gdm_auth):
                        base_env["XAUTHORITY"] = gdm_auth
                except Exception:
                    pass
        base_env.setdefault("__NV_PRIME_RENDER_OFFLOAD", "1")
        base_env.setdefault("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
    base_env.setdefault("MALLOC_ARENA_MAX", "2")
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
        "--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode,OptimizationGuideModelDownloading,OptimizationGuideOnDeviceModel,OptimizationHints,OptimizationHintsFetching,OptimizationTargetPrediction,Translate,AudioServiceOutOfProcess,SpareRendererForSitePerProcess,BackForwardCache,Prerender2,MediaRouter,DialMediaRouteProvider,AutofillServerCommunication,CertificateTransparencyComponentUpdater,InterestFeedContentSuggestions",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-hang-monitor",
        "--disable-background-networking",
        "--disable-breakpad",
        "--disable-domain-reliability",
        "--disable-client-side-phishing-detection",
        "--no-pings",
        "--metrics-recording-only",
        "--safebrowsing-disable-auto-update",
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
            "--disable-software-rasterizer",
            "--use-gl=angle",
            "--use-angle=gl",
        ])
        vram_mb = get_gpu_vram_mb(0.90)
        if vram_mb:
            cmd.append(f"--force-gpu-mem-available-mb={vram_mb}")

    if headless:
        cmd.extend([
            "--headless=new",
            "--hide-scrollbars",
            "--mute-audio",
            "--alsa-output-device=null",
            "--renderer-process-limit=2",
            "--js-flags=--max-old-space-size=384",
        ])
        if has_display:
            cmd.append("--ozone-platform=x11")

    if extra_args:
        custom_window = next((a for a in extra_args if a.startswith("--window-size=")), None)
        if custom_window:
            cmd = [c for c in cmd if not c.startswith("--window-size=")]
        custom_vram = next((a for a in extra_args if a.startswith("--force-gpu-mem-available-mb=")), None)
        if custom_vram:
            cmd = [c for c in cmd if not c.startswith("--force-gpu-mem-available-mb=")]
        custom_ozone = next((a for a in extra_args if a.startswith("--ozone-platform=")), None)
        if custom_ozone:
            cmd = [c for c in cmd if not c.startswith("--ozone-platform=")]
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


class GlobalFlowProductionLock(_FlockHandle):
    """Host-wide counting lock capping concurrent Flow Chrome pools while `GlobalBrowserSlot` caps total browsers."""

    LOCK_FILENAME = "global_flow_production.lock"
    ENV_OWNER_KEY = "VP_FLOW_LOCK_OWNER_PID"
    ENV_MAX_SLOTS_KEY = "VP_FLOW_LOCK_SLOTS"
    MAX_SLOTS = 6

    def __init__(
        self,
        job_id: str = "",
        stage: str = "",
        locks_dir: Path | None = None,
        max_slots: int | None = None,
    ):
        base = ensure_locks_dir(locks_dir)
        self.base_dir = base
        self.job_id = job_id
        self.stage = stage
        env_slots = os.environ.get(self.ENV_MAX_SLOTS_KEY, "").strip()
        default_slots = int(env_slots) if env_slots.isdigit() else self.MAX_SLOTS
        self.max_slots = max(1, int(max_slots if max_slots is not None else default_slots))
        self.slot_index: int | None = None
        self._reentrant_noop = False
        super().__init__(
            base / self.LOCK_FILENAME,
            metadata={"job_id": job_id, "stage": stage},
        )

    def _slot_path(self, idx: int) -> Path:
        if idx <= 0:
            return self.base_dir / self.LOCK_FILENAME
        stem = self.LOCK_FILENAME[:-5] if self.LOCK_FILENAME.endswith(".lock") else self.LOCK_FILENAME
        return self.base_dir / f"{stem}_slot_{idx:02d}.lock"

    def read_holder(self) -> dict[str, Any]:
        """Non-destructively read metadata of the process holding slot 0 (or active slot)."""
        target = self.lock_path if self._fh is not None else self._slot_path(0)
        if not target.is_file():
            return {}
        try:
            raw = target.read_text(encoding="utf-8").strip()
            if raw:
                parsed = json.loads(raw.splitlines()[0])
                if isinstance(parsed, dict):
                    return parsed
        except Exception:
            pass
        return {}

    def try_acquire(self) -> bool:
        my_pid = str(os.getpid())
        if os.environ.get(self.ENV_OWNER_KEY) == my_pid and self._fh is None:
            self._reentrant_noop = True
            return True
        for idx in range(self.max_slots):
            self.lock_path = self._slot_path(idx)
            if super().try_acquire():
                self.slot_index = idx
                os.environ[self.ENV_OWNER_KEY] = my_pid
                return True
        self.lock_path = self._slot_path(0)
        return False

    def acquire_patiently(
        self,
        timeout: float = 7200.0,
        poll_interval: float = 4.0,
        on_wait: Any = None,
    ) -> bool:
        """Wait until any slot becomes free, invoking `on_wait(holder_dict, waited_sec)`."""
        t0 = time.monotonic()
        deadline = t0 + max(0.0, timeout)
        last_notify = -999.0
        while True:
            if self.try_acquire():
                return True
            now = time.monotonic()
            if now >= deadline:
                return False
            waited = now - t0
            if on_wait is not None and (waited - last_notify) >= 12.0:
                last_notify = waited
                try:
                    on_wait(self.read_holder(), round(waited, 1))
                except Exception:
                    pass
            time.sleep(min(poll_interval, max(0.05, deadline - now)))

    def release(self) -> None:
        if self._reentrant_noop:
            self._reentrant_noop = False
            return
        had_fh = self._fh is not None
        super().release()
        self.slot_index = None
        if had_fh and os.environ.get(self.ENV_OWNER_KEY) == str(os.getpid()):
            os.environ.pop(self.ENV_OWNER_KEY, None)

    def __enter__(self) -> GlobalFlowProductionLock:
        if not self.acquire_patiently():
            raise TimeoutError(f"Timed out waiting for {self.__class__.__name__} ({self.lock_path})")
        return self


class GlobalRenderIoLock(GlobalFlowProductionLock):
    """Host-wide exclusive lock serializing Colab T4 chunk download & FFmpeg disk muxing to prevent SATA I/O thrash."""

    LOCK_FILENAME = "global_render_io.lock"
    ENV_OWNER_KEY = "VP_RENDER_LOCK_OWNER_PID"
    MAX_SLOTS = 1


DEFAULT_MAX_LOCAL_CPU_ENCODE_SLOTS = 1
DEFAULT_LOCAL_CPU_THREADS = 2


def apply_low_priority_cpu_clamp(max_threads: int = DEFAULT_LOCAL_CPU_THREADS) -> None:
    """Clamp OpenMP/BLAS/OpenCV thread pools and lower OS scheduling priority to prevent UI lag."""
    t_str = str(max(1, int(max_threads)))
    for env_key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(env_key, t_str)
    try:
        import cv2  # type: ignore

        cv2.setNumThreads(max(1, int(max_threads)))
    except Exception:
        pass
    if hasattr(os, "nice"):
        try:
            cur_nice = os.nice(0)
            if cur_nice < 10:
                os.nice(10 - cur_nice)
        except OSError:
            pass


def _nice_child_15() -> None:
    """`preexec_fn` helper setting background nice=15 on local auxiliary FFmpeg subprocesses."""
    if hasattr(os, "nice"):
        try:
            cur = os.nice(0)
            if cur < 15:
                os.nice(15 - cur)
        except OSError:
            pass


class LocalCpuEncodeSlot:
    """Cross-process kernel semaphore capping concurrent local CPU video/map/rig pre-bakers.

    Prevents multi-agent / `ProcessPoolExecutor` `libx264` storms (`load average > 70` on 8T hosts)
    by serializing local auxiliary pre-bakes (`max_slots=1` default, override via
    `VP_MAX_LOCAL_CPU_ENCODE_SLOTS`) and clamping thread pools to `<= 2` threads (`< 25%` CPU).
    """

    def __init__(
        self,
        max_slots: int | None = None,
        owner_tag: str = "",
        locks_dir: Path | None = None,
    ):
        env_max = os.environ.get("VP_MAX_LOCAL_CPU_ENCODE_SLOTS")
        resolved_max = int(env_max) if (env_max and env_max.isdigit()) else DEFAULT_MAX_LOCAL_CPU_ENCODE_SLOTS
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
                self.locks_dir / f"local_cpu_encode_slot_{idx:02d}.lock",
                metadata={"slot": idx, "owner": self.owner_tag},
            )
            if h.try_acquire():
                self._handle = h
                self.slot_index = idx
                return True
        return False

    def acquire(self, timeout: float = 1800.0, poll_interval: float = 0.5) -> bool:
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

    def __enter__(self) -> LocalCpuEncodeSlot:
        if not self.acquire():
            raise TimeoutError(f"Timed out waiting for LocalCpuEncodeSlot ({self.max_slots} slots)")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.release()


def stagger_cross_process_action(
    action_name: str,
    min_interval_sec: float = 2.0,
    jitter_sec: float = 0.0,
    locks_dir: Path | None = None,
) -> float:
    """Enforce a minimum time gap between cross-process actions (e.g., Chrome launch or RPC submit).

    Prevents simultaneous multi-browser burst spikes from the same host IP or 4C/8T CPU.
    """
    if isinstance(jitter_sec, (Path, str)):
        locks_dir = Path(jitter_sec)
        jitter_sec = 0.0

    if min_interval_sec <= 0 and jitter_sec <= 0:
        return 0.0

    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", action_name.strip()) or "default"
    # Use /dev/shm if available and no custom locks_dir is provided to eliminate disk I/O contention
    if locks_dir is not None:
        base = ensure_locks_dir(locks_dir)
    elif Path("/dev/shm").is_dir() and os.access("/dev/shm", os.W_OK):
        shm_locks = Path("/dev/shm/video-pilot-locks")
        try:
            shm_locks.mkdir(parents=True, exist_ok=True, mode=0o700)
            base = shm_locks
        except OSError:
            base = ensure_locks_dir()
    else:
        base = ensure_locks_dir()

    stamp_path = base / f"stagger_{safe_name}.lock"
    slept_sec = 0.0
    try:
        with open(stamp_path, "a+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                fh.seek(0)
                raw = fh.read().strip()
                last_ts = float(raw) if raw else 0.0
            except ValueError:
                last_ts = 0.0

            effective_interval = min_interval_sec
            if jitter_sec > 0:
                effective_interval += random.uniform(0.0, jitter_sec)

            now = time.time()
            wait_sec = (last_ts + effective_interval) - now
            max_wait = 15.0 if locks_dir is not None else 90.0
            if 0.0 < wait_sec <= max_wait:
                time.sleep(wait_sec)
                slept_sec = wait_sec

            new_ts = time.time()
            fh.seek(0)
            fh.truncate()
            fh.write(f"{new_ts:.6f}\n")
            fh.flush()
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    return slept_sec


def trigger_cross_process_ip_cooldown(
    action_name: str = "flow_rpc_submit",
    cooldown_sec: float = 62.0,
    locks_dir: Path | None = None,
) -> None:
    """Advance the cross-process stagger timestamp into the future to enforce a host-wide quiet window."""
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", action_name.strip()) or "default"
    if locks_dir is not None:
        base = ensure_locks_dir(locks_dir)
    elif Path("/dev/shm").is_dir() and os.access("/dev/shm", os.W_OK):
        shm_locks = Path("/dev/shm/video-pilot-locks")
        try:
            shm_locks.mkdir(parents=True, exist_ok=True, mode=0o700)
            base = shm_locks
        except OSError:
            base = ensure_locks_dir()
    else:
        base = ensure_locks_dir()

    stamp_path = base / f"stagger_{safe_name}.lock"
    try:
        with open(stamp_path, "a+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                fh.seek(0)
                raw = fh.read().strip()
                last_ts = float(raw) if raw else 0.0
            except ValueError:
                last_ts = 0.0
            now = time.time()
            # Idempotent across in-flight waves: only push forward if not already in a future cooldown
            if last_ts < now + 10.0:
                target_ts = now + float(cooldown_sec)
                fh.seek(0)
                fh.truncate()
                fh.write(f"{target_ts:.6f}\n")
                fh.flush()
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


def mark_profile_unauthenticated(
    profile_name: str,
    ttl_sec: float = 86400.0,
    locks_dir: Path | None = None,
) -> None:
    """Record a profile as unauthenticated (e.g. NO_AT_TOKEN / hasAt=False) with a TTL."""
    if not profile_name:
        return
    base = ensure_locks_dir(locks_dir)
    target_file = base / UNAUTHENTICATED_FILE_NAME
    lock_file = base / f"{UNAUTHENTICATED_FILE_NAME}.lock"
    try:
        with open(lock_file, "a+", encoding="utf-8") as lfh:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
            data: dict[str, Any] = {}
            if target_file.is_file():
                try:
                    data = json.loads(target_file.read_text(encoding="utf-8"))
                except Exception:
                    data = {}
            data[str(profile_name)] = {
                "marked_at": time.time(),
                "ttl_sec": float(ttl_sec),
            }
            tmp_p = target_file.with_suffix(".tmp")
            tmp_p.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp_p.replace(target_file)
            fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


def clear_profile_unauthenticated(
    profile_name: str,
    locks_dir: Path | None = None,
) -> None:
    """Clear a stale unauthenticated cache entry after live RPC/session verification succeeds."""
    if not profile_name:
        return
    base = ensure_locks_dir(locks_dir)
    target_file = base / UNAUTHENTICATED_FILE_NAME
    if not target_file.is_file():
        return
    lock_file = base / f"{UNAUTHENTICATED_FILE_NAME}.lock"
    try:
        with open(lock_file, "a+", encoding="utf-8") as lfh:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_EX)
            try:
                data = json.loads(target_file.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            if isinstance(data, dict) and str(profile_name) in data:
                data.pop(str(profile_name), None)
                tmp_p = target_file.with_suffix(".tmp")
                tmp_p.write_text(json.dumps(data, indent=2), encoding="utf-8")
                tmp_p.replace(target_file)
            fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


def is_profile_unauthenticated(
    profile_name: str,
    locks_dir: Path | None = None,
) -> bool:
    """Check if profile is marked unauthenticated and within its TTL."""
    if not profile_name:
        return False
    base = ensure_locks_dir(locks_dir)
    target_file = base / UNAUTHENTICATED_FILE_NAME
    if not target_file.is_file():
        return False
    lock_file = base / f"{UNAUTHENTICATED_FILE_NAME}.lock"
    try:
        with open(lock_file, "a+", encoding="utf-8") as lfh:
            fcntl.flock(lfh.fileno(), fcntl.LOCK_SH)
            try:
                data = json.loads(target_file.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            finally:
                fcntl.flock(lfh.fileno(), fcntl.LOCK_UN)
        entry = data.get(str(profile_name))
        if not entry or not isinstance(entry, dict):
            return False
        marked_at = float(entry.get("marked_at", 0.0))
        ttl_sec = float(entry.get("ttl_sec", 86400.0))
        if time.time() < marked_at + ttl_sec:
            return True
        return False
    except OSError:
        return False

