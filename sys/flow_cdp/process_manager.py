"""Process Group Lifecycle & Zero-Orphan Management for Flow CDP Chrome Workers.

Guarantees:
1. Process Group Isolation: Launches Chrome with start_new_session=True so the leader's
   PID equals the process group ID (PGID). All internal Chrome child processes
   (zygote, GPU process, utility services, renderers, crashpad handler) inherit this PGID.
2. Persistent Registry: Atomically maintains ~/.cache/video-pilot/chrome_pids.json to track
   active browser sessions across script invocations and enable recovery after unhandled crashes.
3. Two-Stage Teardown: Sends SIGTERM to the entire process group (os.killpg), waits 1.0s for
   graceful exit, and follows with SIGKILL to guarantee zero orphan processes.
4. Singleton Lock Cleanup: Automatically unlinks SingletonLock, SingletonCookie, and SingletonSocket
   to eliminate browser lock conflicts on subsequent launches.
"""
from __future__ import annotations

import atexit
import json
import logging
import os
import shutil
import signal
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("flow_cdp.process_manager")

import hashlib
_WORKSPACE_TAG = hashlib.sha256(str(Path(__file__).resolve().parents[2]).encode("utf-8")).hexdigest()[:8]
DEFAULT_REGISTRY_FILE = Path.home() / f".cache/video-pilot/chrome_pids_{_WORKSPACE_TAG}.json"


def detect_chrome_binary() -> str:
    """Find available Chrome or Chromium binary on the host system."""
    candidates = [
        "/opt/google/chrome/google-chrome",
        "/opt/google/chrome/chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    found = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    if found:
        return found
    return "/opt/google/chrome/google-chrome"


def is_port_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Check if TCP port is accepting connections."""
    if port <= 0 or port > 65535:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_pid_alive(pid: int) -> bool:
    """Check if process with given PID exists."""
    if pid <= 1:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def is_chrome_pid(pid: int) -> bool:
    """Check if PID is alive and is actually a Chrome/Chromium process."""
    if not is_pid_alive(pid):
        return False
    cmdline_file = Path(f"/proc/{pid}/cmdline")
    try:
        if cmdline_file.is_file():
            cmdline = cmdline_file.read_bytes().decode("utf-8", errors="ignore").lower()
            return "chrome" in cmdline or "chromium" in cmdline
    except (OSError, PermissionError):
        pass
    return False


def clean_singleton_locks(user_data_dir: str | Path, profile_dir: str | None = None) -> list[str]:
    """Clean SingletonLock, SingletonCookie, and SingletonSocket files/symlinks."""
    cleaned = []
    target_dir = Path(user_data_dir).expanduser().resolve()
    candidate_dirs = [target_dir]
    if profile_dir:
        candidate_dirs.append(target_dir / profile_dir)

    for cdir in candidate_dirs:
        for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            lock_path = cdir / lock_name
            if lock_path.exists() or lock_path.is_symlink():
                try:
                    lock_path.unlink()
                    cleaned.append(str(lock_path))
                except OSError:
                    pass
    return cleaned


class ProcessGroupManager:
    """Manages Chrome process lifecycle with process group tracking and guaranteed two-stage teardown."""

    def __init__(self, registry_file: Path | str | None = None, auto_cleanup_on_exit: bool = True):
        self.registry_file = Path(registry_file or DEFAULT_REGISTRY_FILE).expanduser().resolve()
        self.active_processes: dict[int, dict[str, Any]] = {}  # port -> {pid, pgid, user_data_dir, profile_dir, ...}
        self._lock = threading.RLock()
        self._ensure_registry_dir()
        if auto_cleanup_on_exit:
            atexit.register(self._atexit_cleanup)

    def _atexit_cleanup(self) -> None:
        """Hook called when Python process terminates: shut down all spawned instances."""
        with self._lock:
            ports = list(self.active_processes.keys())
        for port in ports:
            try:
                self.terminate_by_port(port, wait_interval=0.2)
            except Exception:
                pass

    def _ensure_registry_dir(self) -> None:
        """Create parent directory with secure permissions."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    def _load_registry_data(self) -> dict[str, Any]:
        """Load registry from disk safely."""
        if not self.registry_file.is_file():
            return {"updated_at": time.time(), "processes": {}}
        try:
            return json.loads(self.registry_file.read_text(encoding="utf-8"))
        except Exception:
            return {"updated_at": time.time(), "processes": {}}

    def _save_registry(self) -> None:
        """Save registry to disk atomically."""
        with self._lock:
            self._ensure_registry_dir()
            data = {
                "updated_at": time.time(),
                "processes": {
                    str(port): {
                        "port": info["port"],
                        "pid": info["pid"],
                        "pgid": info["pgid"],
                        "user_data_dir": str(info.get("user_data_dir", "")),
                        "profile_dir": info.get("profile_dir", ""),
                        "started_at": info.get("started_at", time.time()),
                        "headless": info.get("headless", True),
                    }
                    for port, info in self.active_processes.items()
                },
            }
            tmp = self.registry_file.with_suffix(f".tmp.{os.getpid()}.{threading.get_ident()}")
            try:
                tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                os.chmod(tmp, 0o600)
                tmp.replace(self.registry_file)
            except Exception as e:
                logger.warning("Failed to save PID registry to %s: %s", self.registry_file, e)
                if tmp.is_file():
                    try:
                        tmp.unlink()
                    except OSError:
                        pass

    def _remove_from_registry(self, port: int) -> None:
        """Remove port entry from on-disk registry file."""
        with self._lock:
            data = self._load_registry_data()
            processes = data.get("processes", {})
            if str(port) in processes:
                del processes[str(port)]
                data["processes"] = processes
                data["updated_at"] = time.time()
                tmp = self.registry_file.with_suffix(f".tmp.{os.getpid()}.{threading.get_ident()}")
                try:
                    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                    tmp.replace(self.registry_file)
                except Exception:
                    pass

    def _clear_registry(self) -> None:
        """Wipe all entries in on-disk registry."""
        with self._lock:
            self._ensure_registry_dir()
            data = {"updated_at": time.time(), "processes": {}}
            try:
                self.registry_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            except Exception:
                pass

    def _find_pids_by_port(self, port: int) -> list[int]:
        """Find PIDs whose cmdline contains remote-debugging-port={port}."""
        pids = []
        proc_dir = Path("/proc")
        if not proc_dir.is_dir():
            return pids
        port_flag = f"--remote-debugging-port={port}"
        for entry in proc_dir.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                cmdline_path = entry / "cmdline"
                if cmdline_path.is_file():
                    cmdline = cmdline_path.read_bytes().decode("utf-8", errors="ignore")
                    if port_flag in cmdline and ("chrome" in cmdline.lower() or "chromium" in cmdline.lower()):
                        pids.append(int(entry.name))
            except (OSError, PermissionError):
                continue
        return pids

    def _kill_group(self, pgid: int | None, pid: int | None, sig: signal.Signals) -> bool:
        """Send signal to process group and individual pid safely."""
        killed_any = False
        if pgid is not None and pgid > 1:
            try:
                os.killpg(pgid, sig)
                killed_any = True
            except (ProcessLookupError, PermissionError, OSError):
                pass

        if pid is not None and pid > 1:
            try:
                os.kill(pid, sig)
                killed_any = True
            except (ProcessLookupError, PermissionError, OSError):
                pass
        return killed_any

    def clean_orphans_from_registry(self) -> int:
        """Scan registry for stale or leaked Chrome processes and reap them."""
        with self._lock:
            data = self._load_registry_data()
            processes = data.get("processes", {})
            reaped_count = 0

            for port_str, info in list(processes.items()):
                try:
                    port = int(port_str)
                    pgid = info.get("pgid")
                    pid = info.get("pid")
                    user_data_dir = info.get("user_data_dir")
                    profile_dir = info.get("profile_dir")

                    # Check if port is listening or pid is still alive
                    port_listening = is_port_listening(port)
                    alive = (pid is not None and is_pid_alive(pid)) or port_listening

                    if alive:
                        logger.info("ProcessGroupManager: Reaping orphan Chrome instance on port %d (PID %s, PGID %s)", port, pid, pgid)
                        self._kill_group(pgid, pid, signal.SIGTERM)
                        time.sleep(0.5)
                        self._kill_group(pgid, pid, signal.SIGKILL)
                        reaped_count += 1

                    if user_data_dir:
                        clean_singleton_locks(user_data_dir, profile_dir)
                except Exception as e:
                    logger.warning("Error cleaning orphan port %s: %s", port_str, e)

            # Clear cleaned entries
            self._clear_registry()
            return reaped_count

    def launch(
        self,
        profile_cfg: dict[str, Any],
        url: str = "https://flow.google.com/",
        headless: bool = True,
        chrome_bin: str | None = None,
        startup_timeout: float = 6.0,
    ) -> bool:
        """Launch Chrome with process group isolation, record PID/PGID, and wait for CDP readiness."""
        port = int(profile_cfg.get("port") or profile_cfg.get("cdp_port", 0))
        if port <= 0:
            logger.error("ProcessGroupManager: Invalid port %d", port)
            return False

        if is_port_listening(port):
            logger.debug("ProcessGroupManager: Port %d already listening", port)
            return True

        user_data_dir = profile_cfg.get("user_data_dir")
        if not user_data_dir:
            logger.error("ProcessGroupManager: Missing user_data_dir for profile %s", profile_cfg.get("id"))
            return False

        target_dir = Path(user_data_dir).expanduser().resolve()
        prof_name = profile_cfg.get("directory") or profile_cfg.get("profile_dir", "Profile 1")
        binary = chrome_bin or detect_chrome_binary()

        # Clean stale locks before launch
        clean_singleton_locks(target_dir, prof_name)

        # Environment display isolation
        env = dict(os.environ)
        if headless:
            env.pop("DISPLAY", None)
            env.pop("XAUTHORITY", None)
        else:
            env["DISPLAY"] = os.environ.get("DISPLAY", ":0")

        cmd = [
            binary,
            f"--user-data-dir={target_dir}",
            f"--profile-directory={prof_name}",
            f"--remote-debugging-port={port}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-component-update",
            "--host-resolver-rules=MAP edgedl.me.gvt1.com ~NOTFOUND, MAP *.gvt1.com ~NOTFOUND",
            "--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode,OptimizationGuideModelDownloading,OptimizationGuideOnDeviceModel,OptimizationHints",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            "--disable-hang-monitor",
        ]
        if headless:
            cmd.extend([
                "--headless=new",
                "--hide-scrollbars",
                "--mute-audio",
            ])
        cmd.append(url)

        # Spawn Chrome as process group leader (start_new_session=True)
        try:
            proc = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Crucial: PGID == PID
            )
        except Exception as e:
            logger.error("ProcessGroupManager: Failed to spawn Chrome on port %d: %s", port, e)
            return False

        with self._lock:
            self.active_processes[port] = {
                "pid": proc.pid,
                "pgid": proc.pid,
                "user_data_dir": str(target_dir),
                "profile_dir": prof_name,
                "port": port,
                "headless": headless,
                "started_at": time.time(),
                "process": proc,
            }
            self._save_registry()

        # Poll port readiness
        deadline = time.time() + startup_timeout
        while time.time() < deadline:
            if is_port_listening(port):
                try:
                    from .lifecycle import register_spawned_port
                    register_spawned_port(port)
                except Exception:
                    pass
                logger.info("ProcessGroupManager: Successfully launched Chrome on port %d (PID %d, PGID %d)", port, proc.pid, proc.pid)
                return True
            time.sleep(0.2)

        # Timeout: terminate unready instance to prevent orphan leak
        logger.error("ProcessGroupManager: Port %d unready after %.1fs, terminating", port, startup_timeout)
        self.terminate_by_port(port)
        return False

    def terminate_by_port(self, port: int, wait_interval: float = 1.0) -> bool:
        """Two-stage process group termination (SIGTERM -> wait 1.0s -> SIGKILL) and lock cleanup."""
        with self._lock:
            info = self.active_processes.pop(port, None)

        # Fallback to registry if not in memory
        if not info:
            data = self._load_registry_data()
            info = data.get("processes", {}).get(str(port))

        if not info and not is_port_listening(port):
            lingering = self._find_pids_by_port(port)
            if not lingering:
                self._remove_from_registry(port)
                return True

        pgid = info.get("pgid") if info else None
        pid = info.get("pid") if info else None
        user_data_dir = info.get("user_data_dir") if info else None
        profile_dir = info.get("profile_dir") if info else None
        proc = info.get("process") if info else None

        # Stage 1: Graceful SIGTERM to process group
        logger.debug("ProcessGroupManager: Stage 1 SIGTERM to port %d (PGID %s, PID %s)", port, pgid, pid)
        self._kill_group(pgid, pid, signal.SIGTERM)

        # Wait for graceful exit
        time.sleep(wait_interval)

        # Stage 2: Forceful SIGKILL to process group if still alive
        still_alive = is_port_listening(port) or (pid is not None and is_pid_alive(pid))
        if still_alive:
            logger.debug("ProcessGroupManager: Stage 2 SIGKILL to port %d (PGID %s, PID %s)", port, pgid, pid)
            self._kill_group(pgid, pid, signal.SIGKILL)

        # Reap zombie if spawned by current process
        if proc is not None:
            try:
                proc.poll()
                proc.wait(timeout=0.2)
            except Exception:
                pass

        # Scan for any lingering processes holding this port
        lingering = self._find_pids_by_port(port)
        for l_pid in lingering:
            if l_pid > 1:
                try:
                    l_pgid = os.getpgid(l_pid)
                    if l_pgid > 1:
                        os.killpg(l_pgid, signal.SIGKILL)
                except OSError:
                    pass
                try:
                    os.kill(l_pid, signal.SIGKILL)
                except OSError:
                    pass

        # Fallback safety net
        if is_port_listening(port):
            subprocess.run(
                ["pkill", "-9", "-f", f"remote-debugging-port={port}"],
                capture_output=True,
                check=False,
            )
            time.sleep(0.2)

        # Clean singleton locks
        if user_data_dir:
            clean_singleton_locks(user_data_dir, profile_dir)

        # Remove from persistent registry
        self._remove_from_registry(port)

        port_closed = not is_port_listening(port)
        if port_closed:
            logger.info("ProcessGroupManager: Port %d successfully terminated and cleaned", port)
        else:
            logger.warning("ProcessGroupManager: Port %d still listening after two-stage teardown", port)
        return port_closed

    def terminate_all(self) -> list[int]:
        """Shut down all tracked instances and verify zero lingering ports."""
        with self._lock:
            active_ports = list(self.active_processes.keys())
            data = self._load_registry_data()
            registry_ports = [int(p) for p in data.get("processes", {}).keys()]
            all_ports = sorted(list(set(active_ports + registry_ports)))

        closed_ports = []
        for port in all_ports:
            if self.terminate_by_port(port):
                closed_ports.append(port)

        self._clear_registry()
        return closed_ports

    def get_tracked_process(self, port: int) -> dict[str, Any] | None:
        """Return metadata of active tracked process by port."""
        with self._lock:
            return self.active_processes.get(port)

    def list_active_ports(self) -> list[int]:
        """Return list of currently tracked active ports."""
        with self._lock:
            return list(self.active_processes.keys())


_GLOBAL_PROCESS_MANAGER: ProcessGroupManager | None = None
_GLOBAL_LOCK = threading.Lock()


def get_process_manager() -> ProcessGroupManager:
    """Return singleton ProcessGroupManager instance."""
    global _GLOBAL_PROCESS_MANAGER
    with _GLOBAL_LOCK:
        if _GLOBAL_PROCESS_MANAGER is None:
            _GLOBAL_PROCESS_MANAGER = ProcessGroupManager()
        return _GLOBAL_PROCESS_MANAGER


def reset_process_manager() -> None:
    """Reset global ProcessGroupManager singleton (useful for test isolation)."""
    global _GLOBAL_PROCESS_MANAGER
    with _GLOBAL_LOCK:
        _GLOBAL_PROCESS_MANAGER = None
