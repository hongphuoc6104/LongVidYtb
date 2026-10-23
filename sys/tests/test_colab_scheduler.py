"""Unit and high-concurrency stress tests for RuntimeScheduler and Budgets ledger."""
from __future__ import annotations

import concurrent.futures
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from account_budget import Budgets
from colab_bridge.scheduler import PoolUnavailable, RuntimeScheduler


class ColabSchedulerAndBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "management"
        self.lock_dir = self.root / "locks"
        self.budgets = Budgets(self.store)
        self.scheduler = RuntimeScheduler(self.root, store=self.store, lock_dir=self.lock_dir)

    def test_identity_binding_prevents_duplicate_google_account_collision(self) -> None:
        # Bind account-01 and account-09 to the SAME underlying Google identity
        self.budgets.bind_identity("colab:account-01", "google:shared-user-01", "ev-1")
        self.budgets.bind_identity("colab:account-09", "google:shared-user-01", "ev-9")
        self.budgets.bind_identity("colab:account-02", "google:distinct-user-02", "ev-2")

        j1 = self.root / "runs/job1/cache/colab-tts/req1/state.json"
        j2 = self.root / "runs/job2/cache/colab-tts/req2/state.json"
        j1.parent.mkdir(parents=True, exist_ok=True)
        j2.parent.mkdir(parents=True, exist_ok=True)

        # Hold claim on account-01; attempting to claim account-09 (same identity) must skip to account-02
        with self.scheduler.claim(
            ["account-01"],
            session="video-pilot-tts",
            request="req-1",
            journal=j1,
            exact=False,
            wait_seconds=0.5,
        ) as claimed_1:
            self.assertEqual(claimed_1, "account-01")
            with self.scheduler.claim(
                ["account-09", "account-02"],
                session="video-pilot-tts",
                request="req-2",
                journal=j2,
                exact=False,
                wait_seconds=0.5,
            ) as claimed_2:
                self.assertEqual(claimed_2, "account-02")

    def test_pending_ambiguous_request_blocks_new_work_on_same_identity(self) -> None:
        self.budgets.bind_identity("colab:account-01", "google:user-01", "ev-1")
        j1 = self.root / "runs/job1/cache/colab-tts/req1/state.json"
        j2 = self.root / "runs/job2/cache/colab-tts/req2/state.json"
        j1.parent.mkdir(parents=True, exist_ok=True)
        j2.parent.mkdir(parents=True, exist_ok=True)

        with self.scheduler.claim(
            ["account-01"],
            session="video-pilot-tts",
            request="req-1",
            journal=j1,
            exact=False,
            wait_seconds=0.2,
        ):
            j1.write_text(json.dumps({"account": "account-01", "request_id": "req-1", "phase": "ambiguous"}))

        # Now j1 is in 'ambiguous' state; a new request req-2 on account-01 must be rejected
        with self.assertRaisesRegex(PoolUnavailable, "COLAB_POOL_WAIT"):
            with self.scheduler.claim(
                ["account-01"],
                session="video-pilot-tts",
                request="req-2",
                journal=j2,
                exact=False,
                wait_seconds=0.1,
            ):
                pass

        # Collection-only recovery for the original pinned request req-1 is still permitted
        with self.scheduler.claim(
            ["account-01"],
            session="video-pilot-tts",
            request="req-1",
            journal=j1,
            exact=True,
            wait_seconds=0.2,
            collection_only=True,
        ) as collected_acc:
            self.assertEqual(collected_acc, "account-01")

    def test_24h_budget_ledger_lifecycle_and_hard_stop_blocks(self) -> None:
        alias = "colab:account-01"
        self.budgets.bind_identity(alias, "google:user-01", "ev-init")
        t0 = time.time()
        self.budgets.allocated(alias, "video-pilot-tts", device="T4", at=t0, evidence="ev-alloc")

        # Cannot allocate a second concurrent GPU on the same identity
        with self.assertRaisesRegex(ValueError, "one allocated GPU runtime"):
            self.budgets.allocated(alias, "video-pilot-tts-2", device="T4", at=t0 + 1, evidence="ev-alloc2")

        # Reserve and settle hold
        self.budgets.reserve(alias, "req-audio-1", 600, now=t0 + 10)
        snap = self.budgets.snapshot(alias, now=t0 + 10)
        self.assertEqual(snap["held_seconds"], 600)
        self.budgets.settle(alias, "req-audio-1")
        self.assertEqual(self.budgets.snapshot(alias, now=t0 + 10)["held_seconds"], 0)

        # Release session
        self.budgets.released(alias, "video-pilot-tts", at=t0 + 120, evidence="ev-rel")
        snap_after = self.budgets.snapshot(alias, now=t0 + 120)
        self.assertEqual(snap_after["allocated_sessions"], [])
        self.assertAlmostEqual(snap_after["used_seconds"], 120, places=1)

        # Hard stop block (e.g., 429) raises Recovery blocked and marks account ineligible
        with self.assertRaisesRegex(ValueError, "Recovery blocked"):
            self.budgets.recover(
                alias,
                "colab",
                "command:exec",
                action="reconcile",
                error="429",
                submit_state="unknown",
                evidence="ev-429",
            )
        self.assertFalse(self.scheduler._eligible("account-01", exact=False))

    def test_high_concurrency_atomic_claim_no_double_assignment(self) -> None:
        candidates = [f"account-{i:02d}" for i in range(1, 7)]
        for acc in candidates:
            self.budgets.bind_identity(f"colab:{acc}", f"google:id-{acc}", "ev")

        active_accounts: set[str] = set()
        overlap_detected = False
        lock = threading.Lock()
        claimed_history: list[str] = []

        def worker_claim(task_idx: int) -> str:
            nonlocal overlap_detected
            journal = self.root / f"runs/j{task_idx}/cache/colab-tts/r{task_idx}/state.json"
            journal.parent.mkdir(parents=True, exist_ok=True)
            with self.scheduler.claim(
                candidates,
                session="video-pilot-tts",
                request=f"req-{task_idx}",
                journal=journal,
                exact=False,
                wait_seconds=5.0,
            ) as acc:
                with lock:
                    if acc in active_accounts:
                        overlap_detected = True
                    active_accounts.add(acc)
                    claimed_history.append(acc)
                time.sleep(0.03)
                journal.write_text(json.dumps({"account": acc, "request_id": f"req-{task_idx}", "phase": "complete"}))
                with lock:
                    active_accounts.discard(acc)
                return acc

        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(worker_claim, range(18)))

        self.assertFalse(overlap_detected, "Concurrent threads claimed the same account simultaneously!")
        self.assertEqual(len(results), 18)


if __name__ == "__main__":
    unittest.main()
