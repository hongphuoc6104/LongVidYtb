"""Cross-process Profile Lease & Concurrency Lock Manager for Flow CDP.

Enforces multi-job profile quota and safe parallel execution without conflict:
- A single job is restricted to a maximum number of concurrent profiles (e.g., 2 profiles).
- Profiles must be registered and claimed via OS-level atomic file locks (fcntl.flock).
- Dynamic replacement: A job can swap a degraded/cooldown profile for an idle pool profile
  during execution, with automatic registration.
- Prevents cross-job race conditions and collisions when multiple jobs run in parallel.
"""
from __future__ import annotations

import fcntl
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("flow_cdp.lease_manager")

DEFAULT_LOCK_DIR = Path.home() / ".cache/video-pilot/flow_locks"
DEFAULT_MAX_PROFILES_PER_JOB = 6


def is_pid_alive(pid: int | None) -> bool:
    """Check if process with given PID is alive."""
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _open_lock_file(path: Path) -> Any:
    """Open a lock file with FD_CLOEXEC set atomically to prevent FD leaks into child processes."""
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    fd = os.open(str(path), flags, 0o600)
    handle = os.fdopen(fd, "a")
    try:
        cur_flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, cur_flags | fcntl.FD_CLOEXEC)
    except OSError:
        pass
    return handle


class FlowJobLeaseManager:
    """Manages cross-process lease locks for Chrome CDP profiles."""

    def __init__(self, lock_dir: Path | None = None):
        self.lock_dir = Path(lock_dir or DEFAULT_LOCK_DIR)
        self.lock_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._open_handles: dict[str, Any] = {}
        self.clean_stale_leases()

    def clean_stale_leases(self) -> list[str]:
        """Remove any .lease files that are not actively held by an OS flock or living PID."""
        cleaned = []
        for meta_file in self.lock_dir.glob("*.lease"):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                prof_id = data.get("profile_id")
                pid = data.get("pid")
                pid_dead = pid is not None and not is_pid_alive(pid)
                if prof_id and (pid_dead or not self.is_profile_busy(prof_id)):
                    meta_file.unlink(missing_ok=True)
                    cleaned.append(prof_id)
            except Exception:
                pass
        return cleaned

    def _lock_file_path(self, profile_id: str) -> Path:
        return self.lock_dir / f"{profile_id}.lock"

    def _lease_meta_path(self, profile_id: str) -> Path:
        return self.lock_dir / f"{profile_id}.lease"

    def is_profile_busy(self, profile_id: str, exclude_job_id: str | None = None) -> bool:
        """Check if profile is currently locked and leased by another process/job."""
        lock_path = self._lock_file_path(profile_id)
        if not lock_path.is_file():
            return False

        meta_path = self._lease_meta_path(profile_id)
        current_job = None
        current_pid = None
        if meta_path.is_file():
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                current_job = data.get("job_id")
                current_pid = data.get("pid")
            except Exception:
                pass

        if exclude_job_id and current_job == exclude_job_id:
            return False

        # If recorded PID is dead, this profile is not legitimately busy
        if current_pid is not None and not is_pid_alive(current_pid):
            return False

        # Test OS flock
        try:
            handle = _open_lock_file(lock_path)
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                handle.close()
                return True
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)
                handle.close()
                return False
        except OSError:
            return False

    def get_job_leases(self, job_id: str) -> list[str]:
        """Return list of profile IDs currently leased to the specified job_id."""
        leased: list[str] = []
        for meta_file in self.lock_dir.glob("*.lease"):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                prof_id = data.get("profile_id")
                if data.get("job_id") == job_id and prof_id:
                    # Verify lock is still held or valid
                    if prof_id in self._open_handles or self.is_profile_busy(prof_id):
                        leased.append(prof_id)
            except Exception:
                continue
        return sorted(leased)

    def lease_profiles(
        self,
        job_id: str,
        pool_profiles: list[dict[str, Any]],
        count: int = 2,
        max_profiles_per_job: int = DEFAULT_MAX_PROFILES_PER_JOB,
        timeout: float = 180.0,
    ) -> list[dict[str, Any]]:
        """Atomically claim and lease up to 'count' idle profiles for a job, adhering to quota."""
        self.clean_stale_leases()
        start_time = time.time()
        enabled_candidates = [p for p in pool_profiles if p.get("enabled", True)]
        effective_quota = min(count, max_profiles_per_job, len(enabled_candidates))
        if effective_quota <= 0:
            return []
        while True:
            current_held = self.get_job_leases(job_id)
            granted: list[dict[str, Any]] = []

            # Re-verify already held profiles by this job in this instance
            for prof_id in list(self._open_handles.keys()):
                if prof_id in current_held:
                    p = next((x for x in pool_profiles if x["id"] == prof_id), None)
                    if p and p not in granted:
                        granted.append(p)

            allowed_new = max_profiles_per_job - len(current_held)
            new_acquired = 0
            if allowed_new > 0 and len(granted) < effective_quota:
                for p in pool_profiles:
                    if len(granted) >= effective_quota or new_acquired >= allowed_new:
                        break
                    prof_id = p["id"]
                    if prof_id in current_held or not p.get("enabled", True):
                        continue
                    if any(g["id"] == prof_id for g in granted):
                        continue
                    if self.is_profile_busy(prof_id):
                        continue
                    if self._try_acquire_lock(prof_id, job_id, p):
                        granted.append(p)
                        new_acquired += 1

            if len(granted) >= effective_quota or (allowed_new <= 0 and len(granted) > 0) or timeout <= 0 or (time.time() - start_time >= timeout):
                break
            if len(granted) > 0 and new_acquired == 0:
                break
            time.sleep(0.5)

        return granted

    def _try_acquire_lock(self, profile_id: str, job_id: str, profile_info: dict[str, Any]) -> bool:
        """Atomically acquire flock and write lease metadata."""
        lock_path = self._lock_file_path(profile_id)
        meta_path = self._lease_meta_path(profile_id)
        try:
            handle = _open_lock_file(lock_path)
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            return False

        meta = {
            "job_id": job_id,
            "profile_id": profile_id,
            "port": profile_info.get("port"),
            "directory": profile_info.get("directory"),
            "pid": os.getpid(),
            "leased_at": time.time(),
        }
        try:
            meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            self._open_handles[profile_id] = handle
            logger.info("Job %s successfully leased profile %s (port %s)", job_id, profile_id, profile_info.get("port"))
            return True
        except Exception as e:
            try:
                fcntl.flock(handle, fcntl.LOCK_UN)
                handle.close()
            except OSError:
                pass
            logger.error("Failed to write lease metadata for %s: %s", profile_id, e)
            return False

    def replace_profile(
        self,
        job_id: str,
        failed_profile_id: str,
        pool_profiles: list[dict[str, Any]],
        reason: str = "",
    ) -> dict[str, Any] | None:
        """Release a degraded profile and atomically lease a healthy idle replacement from the pool."""
        logger.warning(
            "Job %s requesting replacement for failed profile %s. Reason: %s",
            job_id, failed_profile_id, reason or "unspecified"
        )
        candidates = [
            p for p in pool_profiles
            if p["id"] != failed_profile_id and p.get("enabled", True) and not self.is_profile_busy(p["id"])
        ]
        if not candidates:
            logger.warning(
                "Job %s: No available idle profile in pool to replace %s. Retaining lease.",
                job_id, failed_profile_id
            )
            return None

        # Release the failed profile first to free quota
        self.release_profile(job_id, failed_profile_id)

        # Find replacement from candidates
        for p in candidates:
            prof_id = p["id"]
            if not self.is_profile_busy(prof_id):
                if self._try_acquire_lock(prof_id, job_id, p):
                    logger.info("Job %s replaced %s with %s", job_id, failed_profile_id, prof_id)
                    return p

        # If candidates failed to acquire, attempt to re-acquire original profile
        orig = next((p for p in pool_profiles if p["id"] == failed_profile_id), None)
        if orig and self._try_acquire_lock(failed_profile_id, job_id, orig):
            logger.info("Job %s re-acquired original profile %s after replacement failed", job_id, failed_profile_id)

        logger.error("Job %s: No available idle profile in pool to replace %s", job_id, failed_profile_id)
        return None

    def release_profile(self, job_id: str, profile_id: str) -> bool:
        """Release lease lock for a single profile."""
        meta_path = self._lease_meta_path(profile_id)
        if meta_path.is_file():
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                if data.get("job_id") != job_id:
                    logger.warning("Job %s cannot release profile %s owned by %s", job_id, profile_id, data.get("job_id"))
                    return False
            except Exception:
                pass

        if profile_id in self._open_handles:
            handle = self._open_handles.pop(profile_id)
            try:
                fcntl.flock(handle, fcntl.LOCK_UN)
                handle.close()
            except OSError:
                pass

        if meta_path.is_file():
            try:
                meta_path.unlink()
            except OSError:
                pass

        logger.info("Job %s released profile %s", job_id, profile_id)
        return True

    def release_all_for_job(self, job_id: str) -> list[str]:
        """Release all profile leases held by the specified job."""
        released: list[str] = []
        for meta_file in list(self.lock_dir.glob("*.lease")):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                if data.get("job_id") == job_id:
                    prof_id = data.get("profile_id")
                    if prof_id and self.release_profile(job_id, prof_id):
                        released.append(prof_id)
            except Exception:
                continue
        return released

    def list_active_leases(self) -> list[dict[str, Any]]:
        """List all currently active leases across all jobs in the system."""
        leases: list[dict[str, Any]] = []
        for meta_file in sorted(self.lock_dir.glob("*.lease")):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                prof_id = data.get("profile_id")
                # Verify lock is still active
                if self.is_profile_busy(prof_id):
                    leases.append(data)
                else:
                    # Clean stale metadata
                    meta_file.unlink(missing_ok=True)
            except Exception:
                continue
        return leases
