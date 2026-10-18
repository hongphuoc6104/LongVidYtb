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
    {"id": "profile_1", "port": 9225, "directory": "Profile 1", "user_data_dir": "~/.config/google-chrome-cdp-p1"},
    {"id": "profile_2", "port": 9223, "directory": "Profile 2", "user_data_dir": "~/.config/google-chrome-cdp-p2"},
    {"id": "profile_3", "port": 9224, "directory": "Profile 3", "user_data_dir": "~/.config/google-chrome-cdp-p3"},
    {"id": "profile_4", "port": 9222, "directory": "Profile 4", "user_data_dir": "~/.config/google-chrome-cdp-profile4"},
    {"id": "profile_5", "port": 9226, "directory": "Default", "user_data_dir": "~/.config/google-chrome-cdp-profile5"},
    {"id": "profile_6", "port": 9227, "directory": "Profile 7", "user_data_dir": "~/.config/google-chrome-cdp-profile7"},
]


class MultiProfileManager:
    """Manages Chrome profile workers, dynamic job leasing, and handles failover / cooldown."""

    def __init__(
        self,
        profiles_config: list[dict[str, Any]] | None = None,
        cooldown_seconds: float = 5.0,
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
                max_profiles_per_job=max(self.max_workers_per_job, len(self.pool_profiles)),
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
        """Release leased profiles owned by this manager instance."""
        if self.lease_manager and self.job_id:
            for prof_id in list(self.workers.keys()):
                self.lease_manager.release_profile(self.job_id, prof_id)

    def refresh_workers(self, timeout: float = 30.0) -> int:
        """Attempt to re-acquire leased profiles if workers pool is empty or degraded."""
        if not self.lease_manager or not self.job_id:
            return len(self.workers)

        with self._lock:
            needed = max(1, self.max_workers_per_job - len(self.workers))
            if needed > 0:
                active = self.lease_manager.lease_profiles(
                    job_id=self.job_id,
                    pool_profiles=self.pool_profiles,
                    count=self.max_workers_per_job,
                    max_profiles_per_job=max(self.max_workers_per_job, len(self.pool_profiles)),
                    timeout=timeout,
                )
                for p in active:
                    prof_id = p["id"]
                    if prof_id not in self.workers:
                        w = ChromeProfileWorker(
                            profile_id=prof_id,
                            port=int(p.get("port", 9222)),
                            directory=p.get("directory", "Default"),
                            user_data_dir=p.get("user_data_dir", "~/.config/google-chrome"),
                        )
                        self.workers[prof_id] = w
            return len(self.workers)

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

    def acquire_healthy_worker(
        self,
        exclude_ids: set[str] | None = None,
        target_profile_id: str | None = None,
    ) -> ChromeProfileWorker | None:
        """Acquire the next available healthy worker, optionally targeting a specific profile or excluding certain profiles."""
        exclude = exclude_ids or set()
        with self._lock:
            if target_profile_id:
                worker = self.workers.get(target_profile_id)
                if worker and worker.profile_id not in exclude and worker.is_available:
                    worker.mark_busy()
                    return worker
                return None
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

    @staticmethod
    def _get_required_profile(patch: Any, pending_items: list[dict[str, Any]]) -> str | None:
        """Identify if this patch must be pinned to a specific worker profile."""
        if getattr(patch, "pinned_profile", None):
            return str(patch.pinned_profile)
        for it in pending_items:
            p_id = it.get("profile_id") or it.get("profile")
            if p_id:
                return str(p_id)
            base_ref = it.get("baseRefPath") or it.get("base_ref_path") or it.get("base_image")
            if base_ref:
                try:
                    sc = Path(str(base_ref)).with_suffix(".json")
                    if sc.is_file():
                        sc_data = json.loads(sc.read_text(encoding="utf-8"))
                        cand = sc_data.get("profile_id") or sc_data.get("profile")
                        if cand:
                            return str(cand)
                except Exception:
                    pass
        # Check if pending items depend on items completed earlier in this patch
        assigned = getattr(patch, "assigned_profile", None)
        completed = getattr(patch, "completed_items", None)
        if assigned and completed:
            completed_ids = set(completed.keys())
            for it in pending_items:
                parent_id = it.get("based_on") or it.get("base_shot") or it.get("parent_id")
                if parent_id and str(parent_id) in completed_ids:
                    return str(assigned)
        return None

    def execute_patch_with_failover(
        self,
        patch: Any,
        executor_func: Callable[[ChromeProfileWorker, list[dict[str, Any]]], list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Fail over only after an explicitly retryable, proven pre-send transport failure.
        Only uncompleted items in the patch are retried.
        Dependent items (based_on) completed on a worker profile MUST NOT fail over to a different profile.
        """
        excluded_workers: set[str] = set()

        last_exc: Exception | None = None
        while not patch.is_completed and patch.retry_count <= self.max_retries_per_patch:
            pending_items = patch.get_pending_items()
            if not pending_items:
                patch.status = "completed"
                break

            required_profile = self._get_required_profile(patch, pending_items)
            if required_profile:
                patch.pinned_profile = required_profile

            if required_profile:
                if required_profile in excluded_workers:
                    raise RuntimeError(
                        f"Cannot fail over patch {patch.patch_id} with dependency items to a different profile. "
                        f"Target profile {required_profile} encountered error and ownership is pinned."
                    )
                worker = self.manager.acquire_healthy_worker(
                    exclude_ids=excluded_workers,
                    target_profile_id=required_profile,
                )
            else:
                worker = self.manager.acquire_healthy_worker(exclude_ids=excluded_workers)

            if not worker:
                # If worker unavailable or in cooldown, wait up to 65s for worker/cooldown to pass
                wait_start = time.time()
                while not worker and (time.time() - wait_start < 65.0):
                    time.sleep(0.5)
                    if required_profile:
                        if required_profile in excluded_workers:
                            break
                        worker = self.manager.acquire_healthy_worker(
                            exclude_ids=excluded_workers,
                            target_profile_id=required_profile,
                        )
                    else:
                        worker = self.manager.acquire_healthy_worker(exclude_ids=excluded_workers)
                        if not worker and (time.time() - wait_start > 30.0):
                            worker = self.manager.acquire_healthy_worker()
                if not worker:
                    if last_exc is not None:
                        raise last_exc
                    raise RuntimeError(
                        f"All Chrome profiles (required: {required_profile or 'any'}) in cooldown or blocked: {self.manager.get_status()}"
                    )

            patch.assigned_profile = worker.profile_id
            patch.status = "running"
            try:
                logger.info(
                    "Executing patch %s (%d items) on profile %s (port %d)",
                    patch.patch_id, len(pending_items), worker.profile_id, worker.port
                )
                results = executor_func(worker, pending_items)
                if len(results) != len(pending_items):
                    raise RuntimeError('FLOW_PARTIAL_RESULTS: preserve requests and reconcile missing results')
                for item, res in zip(pending_items, results, strict=False):
                    item_id = str(item.get("testCase") or item.get("id") or "")
                    if "profile_id" not in res or not res["profile_id"]:
                        res["profile_id"] = worker.profile_id
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
                # Unknown or provider-blocked submissions must retain their owner.
                # A retry requires explicit evidence that no generation was sent.
                proven_unsent = getattr(ex, "generation_submitted", None) is False
                retryable = getattr(ex, "retryable_pre_submit", False) is True
                hard_stop = bool(re.search(r"captcha|unusual.activity|\b(?:401|403|429|503)\b|quota|bot.detect|provider.blocked|unauthorized|authentication|login", error_str, re.I))
                if hard_stop or not proven_unsent or not retryable:
                    raise
                # Check if pending items have dependency on items completed on this worker
                has_dep_on_completed = False
                if getattr(patch, "completed_items", None):
                    c_ids = set(patch.completed_items.keys())
                    for it in pending_items:
                        p_id = it.get("based_on") or it.get("base_shot") or it.get("parent_id")
                        if p_id and str(p_id) in c_ids:
                            has_dep_on_completed = True
                            break

                if has_dep_on_completed or required_profile:
                    excluded_workers.add(worker.profile_id)
                    patch.retry_count += 1
                    for item in pending_items:
                        item_id = str(item.get("testCase") or item.get("id") or item.get("job_id") or item.get("request_id") or "")
                        if item_id not in patch.completed_items:
                            patch.mark_item_failure(item_id, f"Cannot fail over dependent shot to foreign profile: {error_str}")
                    raise RuntimeError(
                        f"Cannot fail over patch {patch.patch_id} to a different profile: "
                        f"items depend on media produced by profile {worker.profile_id} ({error_str})"
                    ) from ex
                if getattr(self.manager, "job_id", None):
                    self.manager.replace_worker_for_job(worker, reason=error_str)
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
        """Dispatch all patches in parallel across up to max_concurrency workers, respecting inter-patch dependencies."""
        if not patches:
            return []

        if not self.manager.workers:
            if hasattr(self.manager, "refresh_workers"):
                self.manager.refresh_workers(timeout=5.0)

        if not self.manager.workers:
            job_name = getattr(self.manager, 'job_id', 'unknown')
            pool = getattr(self.manager, "pool_profiles", [])
            lm = getattr(self.manager, "lease_manager", None)
            diag = [
                f"{p.get('id', 'unknown')}(port={p.get('port')}, busy={lm.is_profile_busy(p.get('id', '')) if lm else 'unknown'})"
                for p in pool
            ]
            active_leases = lm.list_active_leases() if lm else []
            exc = RuntimeError(
                f"No Chrome profile workers available for job {job_name}. "
                f"Configured profiles: [{', '.join(diag)}]. "
                f"Active leases: {active_leases}. "
                f"Ensure profiles are running and not locked."
            )
            exc.generation_submitted = False
            raise exc

        all_results: list[dict[str, Any]] = []
        errors: list[Exception] = []

        # Build inter-patch dependency DAG
        patch_by_id = {p.patch_id: p for p in patches}
        dependents: dict[str, list[Any]] = {}
        in_degree: dict[str, int] = {}

        for p in patches:
            parent_id = getattr(p, "depends_on_patch_id", None)
            if parent_id and parent_id in patch_by_id:
                in_degree[p.patch_id] = in_degree.get(p.patch_id, 0) + 1
                dependents.setdefault(parent_id, []).append(p)
            else:
                in_degree[p.patch_id] = 0

        ready_queue: list[Any] = [p for p in patches if in_degree[p.patch_id] == 0]
        max_workers = max(1, min(max_concurrency, len(self.manager.workers)))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures: dict[concurrent.futures.Future, Any] = {}

            def fill_capacity() -> None:
                while len(futures) < max_workers and ready_queue:
                    next_patch = ready_queue.pop(0)
                    future = pool.submit(self.execute_patch_with_failover, next_patch, executor_func)
                    futures[future] = next_patch

            fill_capacity()
            while futures:
                done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    completed_patch = futures.pop(future)
                    try:
                        res = future.result()
                        all_results.extend(res)
                        for child in dependents.get(completed_patch.patch_id, []):
                            if completed_patch.assigned_profile:
                                child.pinned_profile = completed_patch.assigned_profile
                            in_degree[child.patch_id] -= 1
                            if in_degree[child.patch_id] == 0:
                                ready_queue.append(child)
                    except Exception as ex:
                        errors.append(ex)
                if not errors:
                    fill_capacity()

        if errors:
            if not all_results and all(getattr(error, 'generation_submitted', None) is False for error in errors):
                raise errors[0]
            raise RuntimeError(
                'FLOW_PARTIAL_BATCH: stopped queued work; preserve original ownership '
                f'and reconcile every unresolved request. First failure: {errors[0]}'
            ) from errors[0]

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


