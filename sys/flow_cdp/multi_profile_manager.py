"""Multi-profile manager and failover router for Chrome DevTools Protocol (CDP).

Manages 3 simultaneous Chrome profiles (e.g. Profile 1, Profile 2, Profile 3),
routes patches in parallel, detects abnormal activity/blocks (e.g. PUBLIC_ERROR_UNUSUAL_ACTIVITY,
CAPTCHA, timeouts, disconnects), puts failed profiles into cooldown, and fails over to
healthy profiles while executing only the remaining failed shots.
"""
from __future__ import annotations

import concurrent.futures
import json
import logging
import re
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger("flow_cdp.multi_profile")

UNUSUAL_ACTIVITY_PATTERNS = [
    re.compile(r"public_error_unusual_activity", re.IGNORECASE),
    re.compile(r"unusual[\s_-]?activity", re.IGNORECASE),
    re.compile(r"captcha", re.IGNORECASE),
    re.compile(r"bot[\s_-]?detect", re.IGNORECASE),
    re.compile(r"rate[\s_-]?limit", re.IGNORECASE),
    re.compile(r"\b429\b"),
    re.compile(r"\b503\b"),
    re.compile(r"quota[\s_-]?exceeded", re.IGNORECASE),
    re.compile(r"econnrefused", re.IGNORECASE),
    re.compile(r"target[\s_-]?closed", re.IGNORECASE),
    re.compile(r"disconnected", re.IGNORECASE),
    re.compile(r"session[\s_-]?closed", re.IGNORECASE),
    re.compile(r"timed?[\s_-]?out", re.IGNORECASE),
]


class ProfileState(str, Enum):
    HEALTHY = "healthy"
    BUSY = "busy"
    COOLDOWN = "cooldown"
    BLOCKED = "blocked"


@dataclass
class ChromeProfileWorker:
    profile_id: str
    port: int
    directory: str
    user_data_dir: str = "~/.config/google-chrome"
    state: ProfileState = ProfileState.HEALTHY
    cooldown_until: float = 0.0
    last_error: str | None = None
    success_count: int = 0
    failure_count: int = 0
    assigned_patch_id: str | None = None

    @property
    def is_available(self) -> bool:
        if self.state == ProfileState.HEALTHY:
            return True
        if self.state == ProfileState.COOLDOWN and time.time() >= self.cooldown_until:
            self.state = ProfileState.HEALTHY
            self.last_error = None
            return True
        return False

    def is_port_open(self, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
        """Probe if this worker's remote debugging port is actively listening."""
        import socket
        try:
            with socket.create_connection((host, self.port), timeout=timeout):
                return True
        except OSError:
            return False

    def mark_busy(self, patch_id: str | None = None) -> None:
        self.state = ProfileState.BUSY
        self.assigned_patch_id = patch_id

    def mark_success(self) -> None:
        self.state = ProfileState.HEALTHY
        self.assigned_patch_id = None
        self.success_count += 1

    def mark_error(self, error: str, cooldown_seconds: float = 60.0) -> None:
        self.last_error = error
        self.failure_count += 1
        self.assigned_patch_id = None
        # Check if error matches unusual activity/bot/rate-limit patterns
        is_unusual = any(p.search(error) for p in UNUSUAL_ACTIVITY_PATTERNS)
        if is_unusual:
            self.state = ProfileState.COOLDOWN
            self.cooldown_until = time.time() + cooldown_seconds
            logger.warning(
                "Profile %s triggered abnormal activity / cooldown: %s (cooldown for %ss)",
                self.profile_id, error, cooldown_seconds
            )
        else:
            # Fatal or general error
            self.state = ProfileState.COOLDOWN
            self.cooldown_until = time.time() + (cooldown_seconds / 2)


DEFAULT_PROFILES = [
    {"id": "profile_1", "port": 9225, "directory": "Profile 106", "user_data_dir": "~/.config/google-chrome-cdp-p1"},
    {"id": "profile_2", "port": 9223, "directory": "Profile 127", "user_data_dir": "~/.config/google-chrome-cdp-p2"},
    {"id": "profile_3", "port": 9224, "directory": "Profile 13", "user_data_dir": "~/.config/google-chrome-cdp-p3"},
    {"id": "profile_4", "port": 9222, "directory": "Profile 130", "user_data_dir": "~/.config/google-chrome-cdp-p4"},
    {"id": "profile_5", "port": 9226, "directory": "Profile 102", "user_data_dir": "~/.config/google-chrome-cdp-p5"},
    {"id": "profile_6", "port": 9227, "directory": "Profile 98", "user_data_dir": "~/.config/google-chrome-cdp-p6"},
]


class MultiProfileManager:
    """Manages Chrome profile workers, dynamic job leasing, and handles failover / cooldown."""

    def __init__(
        self,
        profiles_config: list[dict[str, Any]] | None = None,
        cooldown_seconds: float = 15.0,
        job_id: str | None = None,
        max_workers_per_job: int = 6,
        lock_dir: Path | None = None,
    ):
        raw_profiles = profiles_config
        if raw_profiles is None:
            try:
                from .accounts import registry
                reg = registry()
                raw_profiles = reg.get("profiles", DEFAULT_PROFILES)
            except Exception:
                raw_profiles = DEFAULT_PROFILES

        self.pool_profiles = list(raw_profiles)
        self.cooldown_seconds = cooldown_seconds
        self.job_id = job_id
        self.max_workers_per_job = max_workers_per_job
        self._lock = threading.Lock()

        # Job lease management
        self.lease_manager = None
        if self.job_id:
            try:
                from .lease_manager import FlowJobLeaseManager
            except ImportError:
                from lease_manager import FlowJobLeaseManager
            self.lease_manager = FlowJobLeaseManager(lock_dir=lock_dir)
            active_profiles = self.lease_manager.lease_profiles(
                job_id=self.job_id,
                pool_profiles=self.pool_profiles,
                count=self.max_workers_per_job,
                max_profiles_per_job=self.max_workers_per_job,
            )
        else:
            active_profiles = self.pool_profiles

        self.workers: dict[str, ChromeProfileWorker] = {}
        for p in active_profiles:
            w = ChromeProfileWorker(
                profile_id=p["id"],
                port=int(p.get("port", 9222)),
                directory=p.get("directory", "Default"),
                user_data_dir=p.get("user_data_dir", "~/.config/google-chrome"),
            )
            self.workers[w.profile_id] = w

    def __enter__(self) -> MultiProfileManager:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Release all leased profiles for this job."""
        if self.lease_manager and self.job_id:
            self.lease_manager.release_all_for_job(self.job_id)

    def replace_worker_for_job(
        self,
        failed_worker: ChromeProfileWorker,
        reason: str = "",
    ) -> ChromeProfileWorker | None:
        """Dynamically replace a degraded profile worker with a registered healthy idle pool profile."""
        if not self.lease_manager or not self.job_id:
            return None

        with self._lock:
            replacement_meta = self.lease_manager.replace_profile(
                job_id=self.job_id,
                failed_profile_id=failed_worker.profile_id,
                pool_profiles=self.pool_profiles,
                reason=reason,
            )
            if not replacement_meta:
                return None

            # Remove failed worker from active job pool
            self.workers.pop(failed_worker.profile_id, None)

            # Register new worker
            new_worker = ChromeProfileWorker(
                profile_id=replacement_meta["id"],
                port=int(replacement_meta.get("port", 9222)),
                directory=replacement_meta.get("directory", "Default"),
                user_data_dir=replacement_meta.get("user_data_dir", "~/.config/google-chrome"),
            )
            self.workers[new_worker.profile_id] = new_worker
            return new_worker

    def get_status(self, probe_ports: bool = False) -> dict[str, Any]:
        """Return diagnostic status of all profiles."""
        with self._lock:
            now = time.time()
            return {
                "active_workers": len(self.workers),
                "profiles": [
                    {
                        "id": w.profile_id,
                        "port": w.port,
                        "directory": w.directory,
                        "port_listening": w.is_port_open() if probe_ports else None,
                        "state": w.state.value if not (w.state == ProfileState.COOLDOWN and now >= w.cooldown_until) else ProfileState.HEALTHY.value,
                        "cooldown_remaining": max(0.0, round(w.cooldown_until - now, 1)) if w.state == ProfileState.COOLDOWN else 0.0,
                        "success_count": w.success_count,
                        "failure_count": w.failure_count,
                        "last_error": w.last_error,
                    }
                    for w in self.workers.values()
                ],
            }

    def acquire_healthy_worker(self, exclude_ids: set[str] | None = None) -> ChromeProfileWorker | None:
        """Acquire the next available healthy worker, optionally excluding certain profiles."""
        exclude = exclude_ids or set()
        with self._lock:
            # Check for available workers
            candidates = [w for w in self.workers.values() if w.profile_id not in exclude and w.is_available]
            if not candidates:
                return None
            # Prioritize worker with lowest failure count, then highest success
            candidates.sort(key=lambda w: (w.failure_count, -w.success_count))
            chosen = candidates[0]
            chosen.mark_busy()
            return chosen

    def release_worker(self, worker: ChromeProfileWorker, success: bool = True, error: str | None = None) -> None:
        with self._lock:
            if success:
                worker.mark_success()
            else:
                worker.mark_error(error or "Unknown error", self.cooldown_seconds)

    def stop_all_profiles(self) -> dict[str, Any]:
        """Terminate all isolated Chrome CDP profile instances and clean Singleton locks."""
        import subprocess

        stopped_profiles: list[str] = []
        cleaned_locks: list[str] = []
        with self._lock:
            for w in self.workers.values():
                user_dir = Path(w.user_data_dir).expanduser()
                if "google-chrome-cdp" in str(user_dir):
                    subprocess.run(
                        ["pkill", "-f", "--", f"user-data-dir={user_dir}"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                subprocess.run(
                    ["pkill", "-f", "--", f"remote-debugging-port={w.port}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                    for candidate in (user_dir / lock_name, user_dir / w.directory / lock_name):
                        if candidate.exists() or candidate.is_symlink():
                            try:
                                candidate.unlink()
                                cleaned_locks.append(str(candidate))
                            except OSError:
                                pass
                w.state = ProfileState.HEALTHY
                w.assigned_patch_id = None
                stopped_profiles.append(w.profile_id)

        subprocess.run(["pkill", "-f", "--", "port_forwarder.py"], capture_output=True, text=True, check=False)
        for _ in range(10):
            if not any(w.is_port_open(timeout=0.15) for w in self.workers.values()):
                break
            time.sleep(0.2)
        ports_still_open = [w.port for w in self.workers.values() if w.is_port_open(timeout=0.2)]
        return {
            "stopped_profiles": stopped_profiles,
            "cleaned_locks_count": len(cleaned_locks),
            "ports_still_open": ports_still_open,
        }


class MultiProfileDispatcher:
    """Dispatches patches across the multi-profile pool in parallel with auto-failover."""

    def __init__(
        self,
        profile_manager: MultiProfileManager | None = None,
        max_retries_per_patch: int = 3,
    ):
        self.manager = profile_manager or MultiProfileManager()
        self.max_retries_per_patch = max_retries_per_patch

    def execute_patch_with_failover(
        self,
        patch: Any,
        executor_func: Callable[[ChromeProfileWorker, list[dict[str, Any]]], list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Execute a single patch, failing over to another profile if abnormal activity occurs.
        Only uncompleted items in the patch are retried.
        """
        excluded_workers: set[str] = set()

        last_exc: Exception | None = None
        while not patch.is_completed and patch.retry_count <= self.max_retries_per_patch:
            pending_items = patch.get_pending_items()
            if not pending_items:
                patch.status = "completed"
                break

            worker = self.manager.acquire_healthy_worker(exclude_ids=excluded_workers)
            if not worker:
                # If all excluded or in cooldown, wait up to 65s for worker/cooldown to pass
                wait_start = time.time()
                while not worker and (time.time() - wait_start < 65.0):
                    time.sleep(2.0)
                    worker = self.manager.acquire_healthy_worker(exclude_ids=excluded_workers)
                    if not worker and (time.time() - wait_start > 30.0):
                        worker = self.manager.acquire_healthy_worker()
                if not worker:
                    if last_exc is not None:
                        raise last_exc
                    raise RuntimeError(
                        f"All Chrome profiles in cooldown or blocked: {self.manager.get_status()}"
                    )

            patch.assigned_profile = worker.profile_id
            patch.status = "running"
            try:
                logger.info(
                    "Executing patch %s (%d items) on profile %s (port %d)",
                    patch.patch_id, len(pending_items), worker.profile_id, worker.port
                )
                results = executor_func(worker, pending_items)
                for item, res in zip(pending_items, results, strict=False):
                    item_id = str(item.get("testCase") or item.get("id") or "")
                    patch.mark_item_success(item_id, res)

                self.manager.release_worker(worker, success=True)
                break
            except Exception as ex:
                last_exc = ex
                error_str = str(ex)
                logger.warning(
                    "Patch %s encountered error on profile %s: %s",
                    patch.patch_id, worker.profile_id, error_str
                )
                self.manager.release_worker(worker, success=False, error=error_str)
                # If managed under a specific job, dynamically lease a replacement from pool
                if getattr(self.manager, "job_id", None):
                    self.manager.replace_worker_for_job(worker, reason=error_str)
                # If the failure is a fundamental pre-submission contract violation, fail immediately
                if getattr(ex, "generation_submitted", None) is False:
                    raise ex
                excluded_workers.add(worker.profile_id)
                patch.retry_count += 1
                # Mark individual failed item if identified, leaving completed items intact
                for item in pending_items:
                    item_id = str(item.get("testCase") or item.get("id") or item.get("job_id") or item.get("request_id") or "")
                    if item_id not in patch.completed_items:
                        patch.mark_item_failure(item_id, error_str)

        if not patch.is_completed:
            raise RuntimeError(
                f"Patch {patch.patch_id} failed after {patch.retry_count} attempts: {patch.error or last_exc}"
            ) from last_exc

        return list(patch.completed_items.values())

    def dispatch_all(
        self,
        patches: list[Any],
        executor_func: Callable[[ChromeProfileWorker, list[dict[str, Any]]], list[dict[str, Any]]],
        max_concurrency: int = 6,
    ) -> list[dict[str, Any]]:
        """Dispatch all patches in parallel across up to max_concurrency workers."""
        if not patches:
            return []

        if not self.manager.workers:
            raise RuntimeError(
                f"No Chrome profile workers available for job {getattr(self.manager, 'job_id', 'unknown')}. "
                f"Ensure profiles are running and not locked."
            )

        all_results: list[dict[str, Any]] = []
        errors: list[Exception] = []

        max_workers = max(1, min(max_concurrency, len(self.manager.workers)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(self.execute_patch_with_failover, patch, executor_func): patch
                for patch in patches
            }
            for fut in concurrent.futures.as_completed(futures):
                try:
                    patch_res = fut.result()
                    all_results.extend(patch_res)
                except Exception as ex:
                    errors.append(ex)

        if errors:
            if len(errors) == 1:
                raise errors[0]
            for err in errors:
                if getattr(err, "generation_submitted", None) is False:
                    raise err
            raise errors[0]

        return all_results


if __name__ == "__main__":
    import sys
    cfg_file = Path(__file__).resolve().parents[1] / "config.json"
    cfg = json.loads(cfg_file.read_text()) if cfg_file.is_file() else {}
    profiles = cfg.get("flow_cdp_profiles", DEFAULT_PROFILES)
    manager = MultiProfileManager(profiles_config=profiles)
    if "stop" in sys.argv or "--stop" in sys.argv:
        print(json.dumps(manager.stop_all_profiles(), indent=2))
    else:
        probe = "--probe" in sys.argv or "status" in sys.argv or "-p" in sys.argv
        print(json.dumps(manager.get_status(probe_ports=probe), indent=2))


