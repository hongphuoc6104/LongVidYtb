"""Multi-account Colab T4 session pool manager and parallel task dispatcher.

Manages multiple Google Colab accounts simultaneously (1 account = 1 isolated T4 GPU VM),
supports role-based routing ('any', 'tts', 'render'), staggered T4 allocation,
and work-stealing failover across accounts so TTS and multi-chapter renders
execute in parallel without waiting on a single shared session.
"""
from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from enum import Enum
import json
import logging
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
from typing import Any, Callable

from . import accounts

logger = logging.getLogger("colab_bridge.pool_manager")

HARD_BLOCK_PATTERNS = [
    re.compile(r"quota.{0,24}(exceed|exhaust)|resource.{0,24}limit", re.IGNORECASE),
    re.compile(r"unusual[\s_-]?activity|automated requests|abuse detected", re.IGNORECASE),
    re.compile(r"captcha", re.IGNORECASE),
    re.compile(r"invalid_grant|token.{0,24}(expired|revoked)|login required|sign.?in required", re.IGNORECASE),
    re.compile(r"\b429\b|rate[\s_-]?limit", re.IGNORECASE),
    re.compile(r"\b503\b", re.IGNORECASE),
]


class ColabWorkerState(str, Enum):
    HEALTHY = "healthy"
    BUSY = "busy"
    COOLDOWN = "cooldown"
    BLOCKED = "blocked"


@dataclass
class ColabAccountWorker:
    account_id: str
    session_name: str = "video-pilot-tts"
    role: str = "any"
    state: ColabWorkerState = ColabWorkerState.HEALTHY
    cooldown_until: float = 0.0
    last_error: str | None = None
    success_count: int = 0
    failure_count: int = 0
    assigned_task_id: str | None = None
    t4_confirmed: bool = False
    render_runtime_ready: bool = False
    tts_runtime_ready: bool = False

    def is_available(self, now: float | None = None, lock_dir: Path | None = None) -> bool:
        now = time.time() if now is None else now
        if self.state == ColabWorkerState.BLOCKED:
            return False
        if self.state == ColabWorkerState.COOLDOWN:
            if now >= self.cooldown_until:
                self.state = ColabWorkerState.HEALTHY
                self.last_error = None
            else:
                return False
        if self.state != ColabWorkerState.HEALTHY:
            return False
        if accounts.is_session_busy(self.account_id, self.session_name, lock_dir=lock_dir):
            return False
        return True

    def matches_role(self, requested_role: str | None = None) -> bool:
        if not requested_role or requested_role == "any":
            return True
        return self.role in ("any", requested_role)

    def mark_busy(self, task_id: str | None = None) -> None:
        self.state = ColabWorkerState.BUSY
        self.assigned_task_id = task_id

    def mark_success(self) -> None:
        self.state = ColabWorkerState.HEALTHY
        self.assigned_task_id = None
        self.success_count += 1

    def mark_error(self, error: str, cooldown_seconds: float = 60.0) -> None:
        self.last_error = error
        self.failure_count += 1
        self.assigned_task_id = None
        is_hard_block = any(p.search(error) for p in HARD_BLOCK_PATTERNS)
        if is_hard_block:
            self.state = ColabWorkerState.BLOCKED
            self.cooldown_until = time.time() + (cooldown_seconds * 5)
            logger.warning(
                "Colab account %s blocked/quota-exhausted: %s",
                self.account_id,
                error,
            )
        else:
            self.state = ColabWorkerState.COOLDOWN
            self.cooldown_until = time.time() + (cooldown_seconds / 2)
            self.t4_confirmed = False
            self.render_runtime_ready = False


class ColabPoolManager:
    """Manages a pool of Google Colab accounts for concurrent T4 GPU sessions."""

    def __init__(
        self,
        accounts_config: list[dict[str, Any]] | None = None,
        *,
        session_name: str = "video-pilot-tts",
        cooldown_seconds: float = 60.0,
        stagger_seconds: float = 3.0,
        lock_dir: Path | None = None,
        binary: str | Path | None = None,
    ):
        self.session_name = session_name
        self.cooldown_seconds = cooldown_seconds
        self.stagger_seconds = stagger_seconds
        self.lock_dir = lock_dir
        self.binary = str(binary or shutil.which("colab") or (Path.home() / ".local/bin/colab"))
        self._lock = threading.Lock()
        self._allocation_lock = threading.Lock()
        self._last_allocation_at = 0.0

        self.workers: dict[str, ColabAccountWorker] = {}
        if accounts_config is not None:
            raw_entries = accounts_config
        else:
            reg = accounts.registry()
            raw_entries = [
                x for x in reg.get("accounts", [])
                if x.get("enabled", True) and (accounts.folder(x["id"]) / "token.json").is_file()
            ]
        for item in raw_entries:
            acc_id = item["id"]
            worker = ColabAccountWorker(
                account_id=acc_id,
                session_name=item.get("session", self.session_name),
                role=item.get("role", "any"),
            )
            self.workers[acc_id] = worker

    def get_status(self, probe_server: bool = False) -> dict[str, Any]:
        """Return live pool status across all configured Colab workers."""
        with self._lock:
            now = time.time()
            worker_list = []
            available_count = 0
            for w in self.workers.values():
                ext_busy = accounts.is_session_busy(w.account_id, w.session_name, lock_dir=self.lock_dir)
                avail = w.is_available(now=now, lock_dir=self.lock_dir)
                if avail:
                    available_count += 1
                effective_state = w.state.value
                if w.state == ColabWorkerState.COOLDOWN and now >= w.cooldown_until:
                    effective_state = ColabWorkerState.HEALTHY.value
                elif ext_busy and effective_state == ColabWorkerState.HEALTHY.value:
                    effective_state = ColabWorkerState.BUSY.value

                entry: dict[str, Any] = {
                    "id": w.account_id,
                    "session": w.session_name,
                    "role": w.role,
                    "state": effective_state,
                    "external_lock_busy": ext_busy,
                    "t4_confirmed": w.t4_confirmed,
                    "render_runtime_ready": w.render_runtime_ready,
                    "tts_runtime_ready": w.tts_runtime_ready,
                    "assigned_task_id": w.assigned_task_id,
                    "cooldown_remaining": max(0.0, round(w.cooldown_until - now, 1))
                    if w.state == ColabWorkerState.COOLDOWN
                    else 0.0,
                    "success_count": w.success_count,
                    "failure_count": w.failure_count,
                    "last_error": w.last_error,
                    "local_sessions": accounts.local_sessions(w.account_id),
                }
                if probe_server and Path(self.binary).is_file():
                    entry["server_assignment"] = accounts.assignment_state(
                        self.binary, w.account_id, w.session_name
                    )
                worker_list.append(entry)

            return {
                "total_workers": len(self.workers),
                "available_workers": available_count,
                "session_name": self.session_name,
                "workers": worker_list,
            }

    def acquire_healthy_worker(
        self,
        *,
        role: str | None = None,
        exclude_ids: set[str] | None = None,
        task_id: str | None = None,
    ) -> ColabAccountWorker | None:
        """Acquire the best available idle Colab account worker."""
        exclude = exclude_ids or set()
        with self._lock:
            now = time.time()
            candidates = [
                w for w in self.workers.values()
                if w.account_id not in exclude
                and w.matches_role(role)
                and w.is_available(now=now, lock_dir=self.lock_dir)
            ]
            if not candidates:
                return None
            # Sort: exact role match first, T4 already confirmed second, fewest failures third, most successes fourth
            candidates.sort(
                key=lambda w: (
                    0 if (role and w.role == role) else 1,
                    0 if w.t4_confirmed else 1,
                    w.failure_count,
                    -w.success_count,
                )
            )
            chosen = candidates[0]
            chosen.mark_busy(task_id=task_id)
            return chosen

    def release_worker(
        self,
        worker: ColabAccountWorker,
        *,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        with self._lock:
            if success:
                worker.mark_success()
            else:
                worker.mark_error(error or "Unknown error", self.cooldown_seconds)

    def run_account_cmd(
        self,
        account_id: str,
        args: list[str],
        *,
        timeout: int = 180,
        input_text: str | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Execute an isolated colab-cli command under a specific account profile."""
        argv = accounts.command(self.binary, account_id, args)
        return subprocess.run(
            argv,
            input=input_text,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )

    def ensure_t4_session(
        self,
        worker: ColabAccountWorker,
        *,
        force_new: bool = False,
    ) -> dict[str, Any]:
        """Ensure an active T4 GPU session exists on the worker's account (with staggered allocation)."""
        acc = worker.account_id
        sess = worker.session_name
        reused = False
        if not force_new:
            res = self.run_account_cmd(acc, ["sessions"], timeout=60, check=False)
            out = (res.stdout or "") + "\n" + (res.stderr or "")
            if sess in out and "No active sessions" not in out and res.returncode == 0:
                reused = True

        if not reused:
            with self._allocation_lock:
                elapsed = time.time() - self._last_allocation_at
                if elapsed < self.stagger_seconds and self._last_allocation_at > 0:
                    time.sleep(self.stagger_seconds - elapsed)
                self._last_allocation_at = time.time()
            self.run_account_cmd(acc, ["new", "-s", sess, "--gpu", "T4"], timeout=180, check=True)
            worker.render_runtime_ready = False
            worker.tts_runtime_ready = False

        gpu_code = (
            "import subprocess, json\n"
            "gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], text=True).strip()\n"
            "print('VP_POOL_GPU=' + json.dumps(gpu))\n"
        )
        p = self.run_account_cmd(
            acc,
            ["exec", "-s", sess, "--timeout", "45"],
            timeout=60,
            input_text=gpu_code,
            check=True,
        )
        matches = [line for line in p.stdout.splitlines() if line.startswith("VP_POOL_GPU=")]
        gpu_name = json.loads(matches[-1].split("=", 1)[1]) if matches else ""
        if "T4" not in gpu_name:
            raise RuntimeError(f"[{acc}] Expected T4 GPU on session {sess!r}, got {gpu_name!r}")
        worker.t4_confirmed = True
        return {
            "account": acc,
            "session": sess,
            "gpu": gpu_name,
            "reused": reused,
        }

    def start_pool(
        self,
        account_ids: list[str] | None = None,
        *,
        max_workers: int = 3,
    ) -> dict[str, Any]:
        """Start or verify T4 sessions across multiple accounts in parallel."""
        targets = [
            w for w in self.workers.values()
            if (account_ids is None or w.account_id in account_ids)
        ][:max_workers]
        started: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(targets))) as pool:
            fut_map = {pool.submit(self.ensure_t4_session, w): w for w in targets}
            for fut in concurrent.futures.as_completed(fut_map):
                w = fut_map[fut]
                try:
                    info = fut.result()
                    started.append(info)
                except Exception as exc:
                    w.mark_error(str(exc), self.cooldown_seconds)
                    failed.append({"account": w.account_id, "session": w.session_name, "error": str(exc)})

        return {
            "started_count": len(started),
            "failed_count": len(failed),
            "started": sorted(started, key=lambda x: x["account"]),
            "failed": sorted(failed, key=lambda x: x["account"]),
        }

    def stop_pool(self, account_ids: list[str] | None = None) -> dict[str, Any]:
        """Stop active T4 sessions across selected or all pool accounts."""
        targets = [
            w for w in self.workers.values()
            if (account_ids is None or w.account_id in account_ids)
        ]
        stopped: list[str] = []
        errors: list[dict[str, str]] = []
        for w in targets:
            res = self.run_account_cmd(w.account_id, ["stop", "-s", w.session_name], timeout=60, check=False)
            w.t4_confirmed = False
            w.render_runtime_ready = False
            w.tts_runtime_ready = False
            if res.returncode == 0:
                stopped.append(w.account_id)
            else:
                errors.append({"account": w.account_id, "stderr": (res.stderr or res.stdout or "").strip()})
        return {"stopped": stopped, "errors": errors}


class ColabPoolDispatcher:
    """Dispatches tasks concurrently across multiple Colab T4 accounts with work-stealing failover."""

    def __init__(
        self,
        pool_manager: ColabPoolManager | None = None,
        *,
        max_retries_per_task: int = 3,
        poll_interval_seconds: float = 0.5,
        max_wait_for_worker_seconds: float = 1800.0,
    ):
        self.manager = pool_manager or ColabPoolManager()
        self.max_retries_per_task = max_retries_per_task
        self.poll_interval_seconds = poll_interval_seconds
        self.max_wait_for_worker_seconds = max_wait_for_worker_seconds

    def _wait_for_worker(
        self,
        *,
        role: str | None = None,
        exclude_ids: set[str] | None = None,
        task_id: str | None = None,
    ) -> ColabAccountWorker | None:
        deadline = time.time() + self.max_wait_for_worker_seconds
        while time.time() <= deadline:
            worker = self.manager.acquire_healthy_worker(
                role=role,
                exclude_ids=exclude_ids,
                task_id=task_id,
            )
            if worker is not None:
                return worker
            # Check if any non-excluded worker is merely BUSY (meaning it will free up) or in COOLDOWN
            with self.manager._lock:
                viable = [
                    w for w in self.manager.workers.values()
                    if (exclude_ids is None or w.account_id not in exclude_ids)
                    and w.matches_role(role)
                    and w.state != ColabWorkerState.BLOCKED
                ]
            if not viable:
                return None
            time.sleep(self.poll_interval_seconds)
        return None

    def execute_task_with_failover(
        self,
        task: dict[str, Any],
        executor_func: Callable[[ColabAccountWorker, dict[str, Any]], Any],
        *,
        role: str | None = None,
    ) -> Any:
        """Execute a single task on an available T4 worker, failing over to another account on error."""
        task_id = str(task.get("id") or task.get("chapter") or task.get("request_id") or "task")
        task_role = task.get("role") or role
        excluded_workers: set[str] = set()
        attempts = 0
        last_error: Exception | None = None

        while attempts < self.max_retries_per_task:
            worker = self._wait_for_worker(role=task_role, exclude_ids=excluded_workers, task_id=task_id)
            if worker is None and excluded_workers:
                # Clear exclusions if all other accounts were tried and some might have recovered from cooldown
                excluded_workers.clear()
                worker = self._wait_for_worker(role=task_role, task_id=task_id)
            if worker is None:
                raise RuntimeError(
                    f"No healthy Colab T4 accounts available for task {task_id!r} "
                    f"(last_error={last_error}): {self.manager.get_status()}"
                )

            attempts += 1
            try:
                logger.info(
                    "Executing task %s on Colab account %s (session %s, attempt %d/%d)",
                    task_id,
                    worker.account_id,
                    worker.session_name,
                    attempts,
                    self.max_retries_per_task,
                )
                result = executor_func(worker, task)
                self.manager.release_worker(worker, success=True)
                return result
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Task %s failed on Colab account %s (attempt %d/%d): %s",
                    task_id,
                    worker.account_id,
                    attempts,
                    self.max_retries_per_task,
                    exc,
                )
                self.manager.release_worker(worker, success=False, error=str(exc))
                excluded_workers.add(worker.account_id)

        raise RuntimeError(
            f"Task {task_id!r} failed after {attempts} attempts across Colab pool: {last_error}"
        ) from last_error

    def dispatch_all(
        self,
        tasks: list[dict[str, Any]],
        executor_func: Callable[[ColabAccountWorker, dict[str, Any]], Any],
        *,
        max_concurrency: int = 3,
        role: str | None = None,
    ) -> list[Any]:
        """Dispatch tasks in parallel across up to max_concurrency T4 accounts."""
        if not tasks:
            return []

        worker_count = max(1, min(max_concurrency, max(1, len(self.manager.workers))))
        results_by_idx: dict[int, Any] = {}
        errors: list[Exception] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as pool:
            future_to_idx = {
                pool.submit(
                    self.execute_task_with_failover,
                    task,
                    executor_func,
                    role=role,
                ): idx
                for idx, task in enumerate(tasks)
            }
            for fut in concurrent.futures.as_completed(future_to_idx):
                idx = future_to_idx[fut]
                try:
                    results_by_idx[idx] = fut.result()
                except Exception as exc:
                    errors.append(exc)

        if errors:
            raise RuntimeError(f"Colab pool dispatch failed with {len(errors)} error(s): {errors[0]}") from errors[0]

        return [results_by_idx[i] for i in range(len(tasks))]
