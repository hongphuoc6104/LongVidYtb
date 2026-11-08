"""Process Group Lifecycle & Zero-Orphan Management for Flow CDP Chrome Workers.

Guarantees:
1. Process Group Isolation: Launches Chrome with start_new_session=True so the leader's
   PID equals the process group ID (PGID). All internal Chrome child processes
   (zygote, GPU process, utility services, renderers, crashpad handler) inherit this PGID.
2. Lock-Protected Shared Registry: Atomically maintains ~/.cache/video-pilot/chrome_pids_global.json
   under `fcntl.flock` with per-port `owner_pid` tracking so concurrent channel jobs never
   overwrite each other's registry entries or kill sibling channels' active browsers.
3. Two-Stage Teardown: Sends SIGTERM to the entire process group (os.killpg), waits for
   graceful exit, and follows with SIGKILL to guarantee zero orphan processes.
4. Dead-Owner Orphan Reaper: Automatically detects and reaps Chrome instances whose parent
   Python `owner_pid` terminated unexpectedly (e.g. SIGKILL) without disturbing live jobs.
5. Singleton Lock Cleanup: Automatically unlinks SingletonLock, SingletonCookie, and SingletonSocket
   to eliminate browser lock conflicts on subsequent launches.
"""
from __future__ import annotations

import atexit
import fcntl
import json
import logging
import os
import shutil
import signal
import socket
import subprocess
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .resource_locks import (
    build_optimized_chrome_launch,
    is_port_locked_by_another_process,
    stagger_cross_process_action,
)

logger = logging.getLogger("flow_cdp.process_manager")

DEFAULT_REGISTRY_FILE = Path.home() / ".cache/video-pilot/chrome_pids_global.json"
CHROME_EXE_NAMES = frozenset({
    "chrome",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
})


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
    """Check if process with given PID exists and is not a zombie."""
    if pid is None or pid <= 1:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    stat_path = Path(f"/proc/{pid}/stat")
    try:
        if stat_path.is_file():
            content = stat_path.read_text(encoding="utf-8", errors="ignore")
            rparen = content.rfind(")")
            if rparen != -1 and len(content) > rparen + 2:
                state_char = content[rparen + 2]
                if state_char == "Z":
                    return False
    except OSError:
        pass
    return True


def is_chrome_pid(pid: int) -> bool:
    """Check if PID is alive and its executable argv[0] is Chrome/Chromium."""
    if not is_pid_alive(pid):
        return False
    cmdline_file = Path(f"/proc/{pid}/cmdline")
    try:
        if cmdline_file.is_file():
            parts = cmdline_file.read_bytes().decode("utf-8", errors="ignore").split("\x00")
            exe_name = Path(parts[0]).name.lower() if parts and parts[0] else ""
            return exe_name in CHROME_EXE_NAMES
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


def _collect_open_tmp_prefixes(tmp_root: Path, my_uid: int) -> set[str]:
    """Return resolved directory prefixes under `tmp_root` currently held open by user processes."""
    open_prefixes: set[str] = set()
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return open_prefixes
    tmp_prefix = str(tmp_root) + os.sep
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid != my_uid:
                continue
            fd_dir = entry / "fd"
            if not fd_dir.is_dir():
                continue
            for fd in fd_dir.iterdir():
                try:
                    target = os.readlink(fd)
                except OSError:
                    continue
                if target.startswith(tmp_prefix):
                    rel = target[len(tmp_prefix) :].split(os.sep, 1)[0]
                    if rel:
                        open_prefixes.add(str(tmp_root / rel))
        except OSError:
            continue
    return open_prefixes


def clean_stale_chrome_tmp_artifacts(
    tmp_dir: str | Path = "/tmp",
    min_age_seconds: float = 600.0,
) -> list[str]:
    """Sweep stale owned `/tmp/url_fetcher_*` directories abandoned by terminated Chrome sessions.

    Protects active sessions by requiring:
    1. Exact prefix `url_fetcher_` inside `tmp_dir` (never follows symlinks).
    2. Owned by `os.getuid()`.
    3. `mtime` older than `min_age_seconds`.
    4. Zero open file descriptors from any live user process in `/proc/<pid>/fd`.
    """
    cleaned: list[str] = []
    root = Path(tmp_dir)
    if root.is_symlink() or not root.is_dir():
        return cleaned
    root_resolved = root.resolve()
    my_uid = os.getuid()
    cutoff = time.time() - max(0.0, min_age_seconds)

    candidates: list[Path] = []
    try:
        for item in root_resolved.iterdir():
            if not item.name.startswith("url_fetcher_"):
                continue
            if item.is_symlink() or not item.is_dir():
                continue
            try:
                st = item.lstat()
            except OSError:
                continue
            if st.st_uid != my_uid or st.st_mtime >= cutoff:
                continue
            candidates.append(item)
    except OSError:
        return cleaned

    if not candidates:
        return cleaned

    open_prefixes = _collect_open_tmp_prefixes(root_resolved, my_uid)
    for cand in candidates:
        cand_str = str(cand)
        if cand_str in open_prefixes:
            continue
        try:
            shutil.rmtree(cand)
            cleaned.append(cand_str)
        except OSError:
            continue
    return cleaned


class ProcessGroupManager:
    """Manages Chrome process lifecycle with cross-process lock-safe registry and two-stage teardown."""

    def __init__(
        self,
        registry_file: Path | str | None = None,
        auto_cleanup_on_exit: bool = True,
        headless: bool = True,
        **kwargs: Any,
    ):
        self.registry_file = Path(registry_file or DEFAULT_REGISTRY_FILE).expanduser().resolve()
        self.registry_lock_file = self.registry_file.with_suffix(".lock")
        self.active_processes: dict[int, dict[str, Any]] = {}
        self.default_headless = headless
        self._lock = threading.RLock()
        self._ensure_registry_initialized()
        if auto_cleanup_on_exit:
            atexit.register(self._atexit_cleanup)

    def _atexit_cleanup(self) -> None:
        """Hook called when Python process terminates: shut down only instances owned by this process."""
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

    @contextmanager
    def _locked_registry(self) -> Iterator[dict[str, Any]]:
        """Acquire both thread RLock and OS file lock around read-modify-write of registry JSON."""
        with self._lock:
            self._ensure_registry_dir()
            with open(self.registry_lock_file, "a+", encoding="utf-8") as lf:
                fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
                try:
                    data = self._read_registry_unlocked()
                    yield data
                    self._write_registry_unlocked(data)
                finally:
                    try:
                        fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
                    except OSError:
                        pass

    def _read_registry_unlocked(self) -> dict[str, Any]:
        if not self.registry_file.is_file():
            return {"updated_at": time.time(), "processes": {}}
        try:
            parsed = json.loads(self.registry_file.read_text(encoding="utf-8"))
            if isinstance(parsed, dict) and isinstance(parsed.get("processes"), dict):
                return parsed
        except Exception:
            pass
        return {"updated_at": time.time(), "processes": {}}

    def _write_registry_unlocked(self, data: dict[str, Any]) -> None:
        data["updated_at"] = time.time()
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

    def _ensure_registry_initialized(self) -> None:
        """Ensure registry JSON file exists on disk without clobbering existing entries."""
        with self._locked_registry() as data:
            data.setdefault("processes", {})

    def _load_registry_data(self) -> dict[str, Any]:
        """Load registry snapshot safely under lock."""
        with self._lock:
            self._ensure_registry_dir()
            if not self.registry_file.is_file():
                return {"updated_at": time.time(), "processes": {}}
            with open(self.registry_lock_file, "a+", encoding="utf-8") as lf:
                fcntl.flock(lf.fileno(), fcntl.LOCK_SH)
                try:
                    return self._read_registry_unlocked()
                finally:
                    try:
                        fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
                    except OSError:
                        pass

    def _save_registry(self) -> None:
        """Merge active_processes of this manager into on-disk registry atomically."""
        my_pid = os.getpid()
        with self._locked_registry() as data:
            procs = data.setdefault("processes", {})
            for port, info in self.active_processes.items():
                procs[str(port)] = {
                    "port": info["port"],
                    "pid": info["pid"],
                    "pgid": info["pgid"],
                    "owner_pid": info.get("owner_pid", my_pid),
                    "user_data_dir": str(info.get("user_data_dir", "")),
                    "profile_dir": info.get("profile_dir", ""),
                    "started_at": info.get("started_at", time.time()),
                    "headless": info.get("headless", True),
                }

    def _remove_from_registry(self, port: int) -> None:
        """Remove a single port entry from on-disk registry atomically."""
        with self._locked_registry() as data:
            procs = data.get("processes", {})
            procs.pop(str(port), None)

    def _find_pids_by_port(self, port: int) -> list[int]:
        """Find Chrome/Chromium PIDs whose argv contains `--remote-debugging-port={port}`."""
        pids: list[int] = []
        proc_dir = Path("/proc")
        if not proc_dir.is_dir():
            return pids
        port_flag = f"--remote-debugging-port={port}"
        skip_pids = {os.getpid(), os.getppid()}
        for entry in proc_dir.iterdir():
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            if pid in skip_pids:
                continue
            try:
                cmdline_path = entry / "cmdline"
                if cmdline_path.is_file():
                    parts = cmdline_path.read_bytes().decode("utf-8", errors="ignore").split("\x00")
                    exe_name = Path(parts[0]).name.lower() if parts and parts[0] else ""
                    if exe_name in CHROME_EXE_NAMES and any(a == port_flag for a in parts):
                        pids.append(pid)
            except (OSError, PermissionError):
                continue
        return pids

    def _kill_group(self, pgid: int | None, pid: int | None, sig: signal.Signals) -> bool:
        """Send signal to process group and individual pid safely."""
        killed_any = False
        skip = {0, 1, os.getpid(), os.getppid(), os.getpgrp()}
        if pgid is not None and pgid not in skip and pgid > 1:
            try:
                os.killpg(pgid, sig)
                killed_any = True
            except (ProcessLookupError, PermissionError, OSError):
                pass

        if pid is not None and pid not in skip and pid > 1:
            try:
                os.kill(pid, sig)
                killed_any = True
            except (ProcessLookupError, PermissionError, OSError):
                pass
        return killed_any

    @staticmethod
    def _is_entry_owned_by_live_foreign_process(info: dict[str, Any], port: int) -> bool:
        """Return True if registry entry belongs to another live Python process."""
        owner_pid = info.get("owner_pid")
        my_pid = os.getpid()
        if owner_pid is not None and int(owner_pid) != my_pid and is_pid_alive(int(owner_pid)):
            return True
        if is_port_locked_by_another_process(port):
            return True
        return False

    def clean_orphans_from_registry(self, force_all: bool = False) -> int:
        """Scan registry for stale/dead-owner Chrome processes and reap them safely."""
        data = self._load_registry_data()
        processes = data.get("processes", {})
        reaped_count = 0

        for port_str, info in list(processes.items()):
            try:
                port = int(port_str)
                with self._lock:
                    if port in self.active_processes and not force_all:
                        continue
                if not force_all and self._is_entry_owned_by_live_foreign_process(info, port):
                    continue

                pgid = info.get("pgid")
                pid = info.get("pid")
                user_data_dir = info.get("user_data_dir")
                profile_dir = info.get("profile_dir")

                port_listening = is_port_listening(port)
                alive = (pid is not None and is_pid_alive(pid)) or port_listening

                if alive:
                    logger.info(
                        "ProcessGroupManager: Reaping orphan Chrome instance on port %d (PID %s, PGID %s, dead owner %s)",
                        port,
                        pid,
                        pgid,
                        info.get("owner_pid"),
                    )
                    self._kill_group(pgid, pid, signal.SIGTERM)
                    time.sleep(0.4)
                    self._kill_group(pgid, pid, signal.SIGKILL)
                    for l_pid in self._find_pids_by_port(port):
                        self._kill_group(None, l_pid, signal.SIGKILL)
                    reaped_count += 1

                if user_data_dir:
                    clean_singleton_locks(user_data_dir, profile_dir)
                self._remove_from_registry(port)
            except Exception as e:
                logger.warning("Error cleaning orphan port %s: %s", port_str, e)

        try:
            clean_stale_chrome_tmp_artifacts()
        except Exception:
            pass
        return reaped_count

    def launch(
        self,
        profile_cfg: dict[str, Any],
        url: str = "https://flow.google.com/",
        headless: bool = True,
        chrome_bin: str | None = None,
        startup_timeout: float = 20.0,
        extra_args: list[str] | None = None,
    ) -> bool:
        """Launch Chrome with hardware acceleration, RAM /dev/shm IPC, and process group isolation."""
        port = int(profile_cfg.get("port") or profile_cfg.get("cdp_port", 0))
        if port <= 0:
            logger.error("ProcessGroupManager: Invalid port %d", port)
            return False

        # Reap any crashed dead-owner orphans before launching new browsers
        try:
            self.clean_orphans_from_registry(force_all=False)
        except Exception:
            pass

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

        # Clean stale locks before launch and stagger cross-process browser spawns by >= 3.2s + jitter
        clean_singleton_locks(target_dir, prof_name)
        stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)

        merged_extra_args: list[str] = []
        if profile_cfg.get("extra_args"):
            merged_extra_args.extend(profile_cfg["extra_args"])
        if profile_cfg.get("window_size"):
            merged_extra_args.append(f"--window-size={profile_cfg['window_size']}")
        if extra_args:
            merged_extra_args.extend(extra_args)

        cmd, env = build_optimized_chrome_launch(
            binary=binary,
            user_data_dir=target_dir,
            profile_dir=prof_name,
            port=port,
            url=url,
            headless=headless,
            extra_args=merged_extra_args or None,
        )

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
                "owner_pid": os.getpid(),
                "user_data_dir": str(target_dir),
                "profile_dir": prof_name,
                "port": port,
                "headless": headless,
                "started_at": time.time(),
                "process": proc,
            }
        self._save_registry()

        deadline = time.time() + startup_timeout
        while time.time() < deadline:
            if is_port_listening(port):
                try:
                    from .lifecycle import register_spawned_port
                    register_spawned_port(port)
                except Exception:
                    pass
                logger.info(
                    "ProcessGroupManager: Launched GPU-accelerated Chrome on port %d (PID %d, PGID %d)",
                    port,
                    proc.pid,
                    proc.pid,
                )
                return True
            time.sleep(0.2)

        logger.error("ProcessGroupManager: Port %d unready after %.1fs, terminating", port, startup_timeout)
        self.terminate_by_port(port)
        return False

    def terminate_by_port(self, port: int, wait_interval: float = 1.0) -> bool:
        """Two-stage process group termination (SIGTERM -> wait -> SIGKILL) and lock cleanup."""
        with self._lock:
            info = self.active_processes.pop(port, None)

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

        logger.debug("ProcessGroupManager: Stage 1 SIGTERM to port %d (PGID %s, PID %s)", port, pgid, pid)
        self._kill_group(pgid, pid, signal.SIGTERM)

        time.sleep(wait_interval)

        still_alive = is_port_listening(port) or (pid is not None and is_pid_alive(pid))
        if still_alive:
            logger.debug("ProcessGroupManager: Stage 2 SIGKILL to port %d (PGID %s, PID %s)", port, pgid, pid)
            self._kill_group(pgid, pid, signal.SIGKILL)

        if proc is not None:
            try:
                proc.poll()
                proc.wait(timeout=0.2)
            except Exception:
                pass

        lingering = self._find_pids_by_port(port)
        for l_pid in lingering:
            if l_pid > 1:
                try:
                    l_pgid = os.getpgid(l_pid)
                    if l_pgid > 1 and l_pgid != os.getpgrp():
                        os.killpg(l_pgid, signal.SIGKILL)
                except OSError:
                    pass
                try:
                    os.kill(l_pid, signal.SIGKILL)
                except OSError:
                    pass

        if is_port_listening(port):
            time.sleep(0.2)
            for l_pid in self._find_pids_by_port(port):
                self._kill_group(None, l_pid, signal.SIGKILL)

        if user_data_dir:
            clean_singleton_locks(user_data_dir, profile_dir)

        try:
            clean_stale_chrome_tmp_artifacts()
        except Exception:
            pass

        self._remove_from_registry(port)

        port_closed = not is_port_listening(port)
        if port_closed:
            logger.info("ProcessGroupManager: Port %d successfully terminated and cleaned", port)
        else:
            logger.warning("ProcessGroupManager: Port %d still listening after two-stage teardown", port)
        return port_closed

    def terminate_owned(self) -> list[int]:
        """Shut down only Chrome instances spawned by this ProcessGroupManager."""
        with self._lock:
            owned_ports = sorted(self.active_processes.keys())
        closed_ports = []
        for port in owned_ports:
            if self.terminate_by_port(port):
                closed_ports.append(port)
        return closed_ports

    def terminate_all(self, include_foreign_live_owners: bool = False) -> list[int]:
        """Shut down instances owned by this process plus any dead-owner orphans.

        Never kills Chrome instances actively owned by another live Python process unless
        `include_foreign_live_owners=True` is explicitly requested.
        """
        with self._lock:
            active_ports = set(self.active_processes.keys())

        data = self._load_registry_data()
        reapable_registry_ports: set[int] = set()
        for port_str, info in data.get("processes", {}).items():
            try:
                p = int(port_str)
            except ValueError:
                continue
            if p in active_ports or include_foreign_live_owners:
                reapable_registry_ports.add(p)
            elif not self._is_entry_owned_by_live_foreign_process(info, p):
                reapable_registry_ports.add(p)

        target_ports = sorted(active_ports | reapable_registry_ports)
        closed_ports = []
        for port in target_ports:
            if self.terminate_by_port(port):
                closed_ports.append(port)

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


def launch_chrome(
    profile_cfg: dict[str, Any],
    url: str = "https://flow.google.com/",
    headless: bool = True,
    chrome_bin: str | None = None,
    startup_timeout: float = 20.0,
    extra_args: list[str] | None = None,
) -> bool:
    """Launch Chrome using ProcessGroupManager with optional extra args and window sizing."""
    return get_process_manager().launch(
        profile_cfg=profile_cfg,
        url=url,
        headless=headless,
        chrome_bin=chrome_bin,
        startup_timeout=startup_timeout,
        extra_args=extra_args,
    )


ProcessManager = ProcessGroupManager


