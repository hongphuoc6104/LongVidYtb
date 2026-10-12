"""Unit tests for Multi-Account Colab T4 Pool Manager and Parallel Dispatcher."""
import fcntl
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from colab_bridge import accounts
from colab_bridge.pool_manager import (
    ColabAccountWorker,
    ColabPoolDispatcher,
    ColabPoolManager,
    ColabWorkerState,
)
from colab_bridge.protocol import stamp


class ColabPoolManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store_patch = patch.object(accounts, "STORE", self.root / "store")
        self.store_patch.start()
        self.addCleanup(self.store_patch.stop)

        self.lock_dir = self.root / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "token.json").write_text('{"test": true}')
        (self.source / "sessions.json").write_text("{}")

        for acc_id, role in (("account-01", "any"), ("account-02", "render"), ("account-03", "tts")):
            accounts.add(acc_id, self.source, role=role)

    def test_acquire_respects_roles_and_external_locks(self) -> None:
        manager = ColabPoolManager(lock_dir=self.lock_dir)
        self.assertEqual(manager.get_status()["available_workers"], 3)

        # Requesting 'render' prioritizes exact role match ('account-02') over 'any' ('account-01')
        w_render = manager.acquire_healthy_worker(role="render", task_id="ch1")
        self.assertIsNotNone(w_render)
        self.assertEqual(w_render.account_id, "account-02")

        # Next 'render' request picks 'account-01' (role='any' matches 'render')
        w_render2 = manager.acquire_healthy_worker(role="render", task_id="ch2")
        self.assertIsNotNone(w_render2)
        self.assertEqual(w_render2.account_id, "account-01")

        # 'account-03' has role='tts', so it will not be acquired for 'render'
        self.assertIsNone(manager.acquire_healthy_worker(role="render", task_id="ch3"))

        # Requesting 'tts' acquires 'account-03'
        w_tts = manager.acquire_healthy_worker(role="tts", task_id="tts-batch-1")
        self.assertIsNotNone(w_tts)
        self.assertEqual(w_tts.account_id, "account-03")

        manager.release_worker(w_render, success=True)
        manager.release_worker(w_render2, success=True)
        manager.release_worker(w_tts, success=True)

        # Hold an external session lock on account-02 and verify it is skipped
        lock_file = self.lock_dir / (stamp(["account-02", "video-pilot-tts"]) + ".lock")
        with lock_file.open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            chosen = manager.acquire_healthy_worker(role="render")
            self.assertIsNotNone(chosen)
            self.assertEqual(chosen.account_id, "account-01")
            manager.release_worker(chosen, success=True)
            fcntl.flock(handle, fcntl.LOCK_UN)

    def test_parallel_dispatch_and_work_stealing_failover(self) -> None:
        pool_cfg = [
            {"id": "account-01", "role": "any"},
            {"id": "account-02", "role": "any"},
            {"id": "account-03", "role": "any"},
        ]
        manager = ColabPoolManager(
            accounts_config=pool_cfg,
            cooldown_seconds=10.0,
            lock_dir=self.lock_dir,
        )
        dispatcher = ColabPoolDispatcher(
            pool_manager=manager,
            max_retries_per_task=3,
            poll_interval_seconds=0.05,
        )

        tasks = [{"id": f"ch{i}", "chapter": i} for i in range(1, 7)]
        active_accounts: set[str] = set()
        max_simultaneous = 0
        lock = threading.Lock()
        failed_once = False

        def execute_fn(worker: ColabAccountWorker, task: dict) -> dict:
            nonlocal max_simultaneous, failed_once
            with lock:
                active_accounts.add(worker.account_id)
                max_simultaneous = max(max_simultaneous, len(active_accounts))
            try:
                time.sleep(0.08)
                if worker.account_id == "account-01" and not failed_once:
                    failed_once = True
                    raise RuntimeError("Colab GPU quota exceeded on account-01")
                return {"chapter": task["chapter"], "account": worker.account_id}
            finally:
                with lock:
                    active_accounts.discard(worker.account_id)

        results = dispatcher.dispatch_all(tasks, execute_fn, max_concurrency=3)
        self.assertEqual(len(results), 6)
        self.assertEqual([r["chapter"] for r in results], [1, 2, 3, 4, 5, 6])
        self.assertGreaterEqual(max_simultaneous, 2)
        # account-01 hit a hard quota block and must be marked BLOCKED, while 02 and 03 finished all 6 chapters
        self.assertEqual(manager.workers["account-01"].state, ColabWorkerState.BLOCKED)
        self.assertTrue(all(r["account"] in ("account-02", "account-03") for r in results))

    def test_start_pool_and_stop_pool_with_staggered_t4_verification(self) -> None:
        pool_cfg = [
            {"id": "account-01", "role": "any"},
            {"id": "account-02", "role": "any"},
        ]
        manager = ColabPoolManager(
            accounts_config=pool_cfg,
            stagger_seconds=0.05,
            lock_dir=self.lock_dir,
        )
        calls: list[tuple[str, list[str]]] = []

        def fake_run(account_id: str, args: list[str], **kwargs):
            calls.append((account_id, list(args)))
            if args == ["sessions"]:
                return subprocess.CompletedProcess(args, 0, stdout="No active sessions found on server\n", stderr="")
            if args[:1] == ["new"]:
                return subprocess.CompletedProcess(args, 0, stdout="Allocated T4\n", stderr="")
            if args[:1] == ["exec"]:
                return subprocess.CompletedProcess(args, 0, stdout='VP_POOL_GPU="Tesla T4"\n', stderr="")
            if args[:1] == ["stop"]:
                return subprocess.CompletedProcess(args, 0, stdout="Stopped\n", stderr="")
            raise AssertionError(f"Unexpected args: {args}")

        with patch.object(manager, "run_account_cmd", side_effect=fake_run):
            started = manager.start_pool(max_workers=2)
            self.assertEqual(started["started_count"], 2)
            self.assertEqual(started["failed_count"], 0)
            self.assertTrue(manager.workers["account-01"].t4_confirmed)
            self.assertTrue(manager.workers["account-02"].t4_confirmed)

            stopped = manager.stop_pool()
            self.assertEqual(sorted(stopped["stopped"]), ["account-01", "account-02"])
            self.assertFalse(manager.workers["account-01"].t4_confirmed)

    def test_stop_pool_reconciles_tmp_profiles_and_teardown_closes_chrome(self) -> None:
        tmp_profiles = self.root / "tmp_vp_colab_profiles"
        acc2_tmp = tmp_profiles / "account-02"
        acc2_tmp.mkdir(parents=True, exist_ok=True)
        (acc2_tmp / "sessions.json").write_text(
            '{"video-pilot-tts": {"endpoint": "ep-test-02", "accelerator": "T4"}}'
        )

        manager = ColabPoolManager(
            accounts_config=[{"id": "account-02", "role": "render"}],
            lock_dir=self.lock_dir,
        )

        def fake_run(account_id: str, args: list[str], **kwargs):
            return subprocess.CompletedProcess(args, 0, stdout="Stopped\n", stderr="")

        with patch.object(manager, "run_account_cmd", side_effect=fake_run):
            res = manager.teardown_job_resources(
                ["account-02"],
                close_chrome=True,
                tmp_profiles_dir=tmp_profiles,
            )
            self.assertEqual(res["colab"]["stopped"], ["account-02"])
            self.assertIn("stopped_profiles", res["chrome_cdp"])
            # Both canonical and /tmp sessions.json must have 'video-pilot-tts' cleared
            self.assertEqual((acc2_tmp / "sessions.json").read_text().strip(), "{}")
            canon_sess = accounts.folder("account-02") / "sessions.json"
            self.assertEqual(canon_sess.read_text().strip(), "{}")


if __name__ == "__main__":
    unittest.main()

