"""Unit and concurrency tests for ColabPoolManager, ColabPoolDispatcher, and CLI sync."""
from __future__ import annotations

import fcntl
import json
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from colab_bridge import accounts
from colab_bridge.pool_manager import (
    ColabAccountWorker,
    ColabPoolDispatcher,
    ColabPoolManager,
    ColabWorkerState,
)
from colab_bridge.protocol import stamp


class ColabPoolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "store"
        self.lock_dir = self.root / "locks"
        self.tmp_profiles = self.root / "tmp_profiles"
        self.patch_store = patch.object(accounts, "STORE", self.store)
        self.patch_store.start()
        self.addCleanup(self.patch_store.stop)

        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "token.json").write_text('{"refresh_token": "tok-123"}')
        (self.source / "sessions.json").write_text("{}")

        for idx in range(1, 5):
            role = "tts" if idx in (1, 2) else ("render" if idx == 3 else "any")
            accounts.add(f"account-0{idx}", self.source, role=role)

    def test_acquire_healthy_worker_prioritizes_exact_role_and_t4_confirmed(self) -> None:
        mgr = ColabPoolManager(lock_dir=self.lock_dir, cooldown_seconds=10.0)
        mgr.workers["account-02"].t4_confirmed = True

        w1 = mgr.acquire_healthy_worker(role="tts", task_id="t1")
        self.assertIsNotNone(w1)
        assert w1 is not None
        self.assertEqual(w1.account_id, "account-02")
        self.assertEqual(w1.state, ColabWorkerState.BUSY)

        w2 = mgr.acquire_healthy_worker(role="tts", task_id="t2")
        self.assertIsNotNone(w2)
        assert w2 is not None
        self.assertEqual(w2.account_id, "account-01")

        # Next TTS acquisition falls back to 'any' (account-04), skipping 'render' (account-03)
        w3 = mgr.acquire_healthy_worker(role="tts", task_id="t3")
        self.assertIsNotNone(w3)
        assert w3 is not None
        self.assertEqual(w3.account_id, "account-04")

        # No more TTS/any workers free
        self.assertIsNone(mgr.acquire_healthy_worker(role="tts", task_id="t4"))

    def test_external_session_lock_prevents_worker_acquisition(self) -> None:
        mgr = ColabPoolManager(lock_dir=self.lock_dir)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = self.lock_dir / (stamp(["account-01", "video-pilot-tts"]) + ".lock")
        with lock_file.open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            status = mgr.get_status()
            acc1 = next(x for x in status["workers"] if x["id"] == "account-01")
            self.assertTrue(acc1["external_lock_busy"])
            self.assertEqual(acc1["state"], "busy")
            w = mgr.acquire_healthy_worker(role="tts", exclude_ids={"account-02", "account-04"})
            self.assertIsNone(w)
            fcntl.flock(handle, fcntl.LOCK_UN)

    def test_hard_block_vs_transient_cooldown_classification(self) -> None:
        w = ColabAccountWorker(account_id="account-01")
        w.mark_error("Transient WebSocket timeout", cooldown_seconds=20.0)
        self.assertEqual(w.state, ColabWorkerState.COOLDOWN)
        self.assertFalse(w.is_available(now=time.time()))
        self.assertTrue(w.is_available(now=time.time() + 15.0))

        w.mark_error("HTTP 429 rate limit exceeded", cooldown_seconds=20.0)
        self.assertEqual(w.state, ColabWorkerState.BLOCKED)
        self.assertFalse(w.is_available(now=time.time() + 15.0))

        w2 = ColabAccountWorker(account_id="account-02")
        w2.mark_error("Colab resource quota exhausted", cooldown_seconds=20.0)
        self.assertEqual(w2.state, ColabWorkerState.BLOCKED)

    def test_staggered_t4_session_allocation_enforces_minimum_interval(self) -> None:
        mgr = ColabPoolManager(
            accounts_config=[
                {"id": "account-01", "role": "tts"},
                {"id": "account-02", "role": "tts"},
                {"id": "account-03", "role": "tts"},
            ],
            stagger_seconds=0.18,
            lock_dir=self.lock_dir,
        )
        new_timestamps: list[float] = []
        ts_lock = threading.Lock()

        def fake_run_cmd(account_id: str, args: list[str], **kwargs):
            if args[0] == "sessions":
                return subprocess.CompletedProcess(args, 0, stdout="No active sessions\n", stderr="")
            if args[0] == "new":
                with ts_lock:
                    new_timestamps.append(time.monotonic())
                return subprocess.CompletedProcess(args, 0, stdout="Created\n", stderr="")
            if args[0] == "exec":
                return subprocess.CompletedProcess(args, 0, stdout='VP_POOL_GPU="Tesla T4"\n', stderr="")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

        with patch.object(mgr, "run_account_cmd", side_effect=fake_run_cmd):
            res = mgr.start_pool(max_workers=3)

        self.assertEqual(res["started_count"], 3)
        self.assertEqual(res["failed_count"], 0)
        self.assertEqual(len(new_timestamps), 3)
        new_timestamps.sort()
        self.assertGreaterEqual(new_timestamps[1] - new_timestamps[0], 0.15)
        self.assertGreaterEqual(new_timestamps[2] - new_timestamps[1], 0.15)

    def test_work_stealing_failover_across_accounts_preserves_exact_order(self) -> None:
        mgr = ColabPoolManager(
            accounts_config=[
                {"id": "account-01", "role": "tts"},
                {"id": "account-02", "role": "tts"},
                {"id": "account-03", "role": "tts"},
            ],
            cooldown_seconds=5.0,
            lock_dir=self.lock_dir,
        )
        dispatcher = ColabPoolDispatcher(mgr, max_retries_per_task=3, poll_interval_seconds=0.02)
        tasks = [{"id": f"task-{i}", "idx": i} for i in range(12)]
        attempts_by_account: dict[str, int] = {"account-01": 0, "account-02": 0, "account-03": 0}
        lock = threading.Lock()

        def executor(worker: ColabAccountWorker, task: dict) -> dict:
            with lock:
                attempts_by_account[worker.account_id] += 1
            if worker.account_id == "account-01":
                raise RuntimeError("HTTP 429 rate limit on account-01")
            time.sleep(0.01)
            return {"idx": task["idx"], "handled_by": worker.account_id}

        results = dispatcher.dispatch_all(tasks, executor, max_concurrency=3, role="tts")
        self.assertEqual([r["idx"] for r in results], list(range(12)))
        self.assertTrue(all(r["handled_by"] in ("account-02", "account-03") for r in results))
        self.assertEqual(mgr.workers["account-01"].state, ColabWorkerState.BLOCKED)

    def test_stop_pool_and_teardown_reconciles_tmp_sessions_and_protects_external_endpoints(self) -> None:
        mgr = ColabPoolManager(
            accounts_config=[{"id": "account-01", "role": "tts"}],
            lock_dir=self.lock_dir,
        )
        # Write session endpoint in /tmp/vp_colab_profiles to test split-cache reconciliation
        tmp_acc = self.tmp_profiles / "account-01"
        tmp_acc.mkdir(parents=True, exist_ok=True)
        (tmp_acc / "sessions.json").write_text(
            json.dumps({"video-pilot-tts": {"endpoint": "ep-vp-tts-001"}})
        )
        unassigned_calls: list[tuple[str, list[str]]] = []

        def fake_unassign(acc_id: str, target_endpoints=None):
            eps = list(target_endpoints or [])
            unassigned_calls.append((acc_id, eps))
            return eps

        with patch.object(
            mgr,
            "run_account_cmd",
            return_value=subprocess.CompletedProcess(["stop"], 0, stdout="Stopped\n", stderr=""),
        ), patch.object(mgr, "_unassign_server_endpoints", side_effect=fake_unassign):
            res = mgr.teardown_job_resources(
                ["account-01"],
                close_chrome=False,
                tmp_profiles_dir=self.tmp_profiles,
            )

        self.assertEqual(res["colab"]["stopped"], ["account-01"])
        self.assertEqual(unassigned_calls, [("account-01", ["ep-vp-tts-001"])])
        # Verify both canonical and tmp sessions.json cleared 'video-pilot-tts'
        canon_sess = json.loads((accounts.folder("account-01") / "sessions.json").read_text())
        tmp_sess = json.loads((tmp_acc / "sessions.json").read_text())
        self.assertNotIn("video-pilot-tts", canon_sess)
        self.assertNotIn("video-pilot-tts", tmp_sess)

    def test_conveyor_colab_cli_supports_pool_subcommands(self) -> None:
        from scripts import conveyor

        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as mock_run, \
             patch.object(sys := __import__("sys"), "exit"):
            args = type(
                "Args",
                (),
                {
                    "colab_action": "pool-status",
                    "probe": True,
                    "refresh_auth": False,
                    "check_kernels": False,
                    "accounts": "account-01,account-02",
                    "max_workers": 3,
                    "account": "auto",
                },
            )()
            conveyor.cmd_colab(args)
            called_cmd = mock_run.call_args[0][0]
            self.assertIn("colab_bridge", called_cmd)
            self.assertIn("pool-status", called_cmd)
            self.assertIn("--probe", called_cmd)
            self.assertIn("account-01,account-02", called_cmd)
            self.assertIsNotNone(sys)


if __name__ == "__main__":
    unittest.main()
