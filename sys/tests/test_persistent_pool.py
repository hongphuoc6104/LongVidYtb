"""Unit tests for PersistentWorkerPool."""
from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

SYS_DIR = Path(__file__).resolve().parent.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from flow_cdp.persistent_pool import (
    PersistentWorkerPool,
)


class MockCDPSession:
    """Mock CDP profile session tracking connect calls and executions."""

    def __init__(self, prof_cfg: dict[str, Any]):
        self.prof_cfg = prof_cfg
        self.name = prof_cfg.get("name") or prof_cfg.get("id")
        self.connect_count = 0
        self.close_count = 0
        self.generate_calls: list[dict[str, Any]] = []
        self.should_fail_rate_limit = False
        self.should_fail_transient = False
        self.recaptcha_refreshed = False

    async def _refresh_recaptcha_session(self):
        self.recaptcha_refreshed = True

    async def connect(self):
        self.connect_count += 1
        return self

    async def close(self):
        self.close_count += 1

    async def call(self, method: str, params: dict | None = None, timeout: float = 60.0):
        return {}

    async def generate_image(
        self,
        prompt: str,
        aspect: str = "16:9",
        model: str = "BELUGA",
        base_media_id: str | None = None,
        ref_media_ids: list[str] | None = None,
    ):
        self.generate_calls.append({
            "prompt": prompt,
            "aspect": aspect,
            "base_media_id": base_media_id,
            "profile": self.name,
            "timestamp": time.time(),
        })
        if self.should_fail_rate_limit:
            self.should_fail_rate_limit = False
            raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY: Bot detected, rate limited")
        if self.should_fail_transient:
            self.should_fail_transient = False
            raise RuntimeError("Transient transport socket drop")

        return {
            "media_id": f"media-{self.name}-{len(self.generate_calls)}",
            "url": None,
            "profile": self.name,
        }


class MockBatchCDPSession(MockCDPSession):
    """Mock CDP profile session supporting generate_images_batch."""

    def __init__(self, prof_cfg: dict[str, Any]):
        super().__init__(prof_cfg)
        self.generate_batch_calls: list[dict[str, Any]] = []

    async def generate_images_batch(
        self,
        prompts: list[str],
        aspect: str = "16:9",
        model: str = "BELUGA",
        base_media_id: str | None = None,
        ref_media_ids: list[str] | None = None,
    ):
        self.generate_batch_calls.append({
            "prompts": prompts,
            "aspect": aspect,
            "model": model,
            "profile": self.name,
            "timestamp": time.time(),
        })
        return [
            {
                "media_id": f"batch-media-{self.name}-{i}",
                "url": None,
                "profile": self.name,
            }
            for i, p in enumerate(prompts)
        ]


class TestPersistentWorkerPool(unittest.TestCase):
    def setUp(self):
        self.test_profiles = [
            {"name": "p1", "cdp_port": 9221, "user_data_dir": "/tmp/p1", "profile_dir": "P1"},
            {"name": "p2", "cdp_port": 9222, "user_data_dir": "/tmp/p2", "profile_dir": "P2"},
            {"name": "p3", "cdp_port": 9223, "user_data_dir": "/tmp/p3", "profile_dir": "P3"},
            {"name": "p4", "cdp_port": 9224, "user_data_dir": "/tmp/p4", "profile_dir": "P4"},
        ]
        self.sessions: dict[str, MockCDPSession] = {}

    def session_factory(self, prof_cfg: dict[str, Any]) -> MockCDPSession:
        name = prof_cfg["name"]
        sess = MockCDPSession(prof_cfg)
        self.sessions[name] = sess
        return sess

    def test_pool_lifecycle_and_shutdown(self):
        """Worker threads launch staggered, run, and cleanly shut down."""
        mock_proc_mgr = MagicMock()
        pool = PersistentWorkerPool(
            target_workers=2,
            stagger_seconds=0.05,
            pacing_seconds=0.05,
            profiles=self.test_profiles,
            proc_mgr=mock_proc_mgr,
            session_factory=self.session_factory,
        )
        self.assertFalse(pool.is_running)
        pool.start()
        self.assertTrue(pool.is_running)
        self.assertEqual(len(pool.workers), 2)
        self.assertTrue(all(t.is_alive() for t in pool.workers))

        pool.shutdown()
        self.assertFalse(pool.is_running)
        self.assertEqual(len(pool.workers), 0)
        mock_proc_mgr.terminate_all.assert_called_once()

    def test_session_reuse_across_multiple_tasks(self):
        """Session connect() is called ONCE per worker, held open across tasks."""
        pool = PersistentWorkerPool(
            target_workers=1,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles[:1],
            proc_mgr=MagicMock(),
            session_factory=self.session_factory,
        )
        with pool:
            # Submit 5 tasks
            for i in range(1, 6):
                pool.submit_task({"id": f"shot_{i}", "prompt": f"Prompt {i}"})
            finished = pool.wait_completion(timeout=5.0)
            self.assertTrue(finished)

        # Single worker leased 'p1'
        self.assertIn("p1", self.sessions)
        sess = self.sessions["p1"]
        self.assertEqual(sess.connect_count, 1)  # EXACTLY ONCE!
        self.assertEqual(len(sess.generate_calls), 5)  # All 5 executed on same session
        self.assertEqual(sess.close_count, 1)  # Closed on pool exit

    def test_priority_queue_dispatch_order(self):
        """Priority 0 (retry) is picked up before Priority 10 (standard)."""
        pool = PersistentWorkerPool(
            target_workers=1,
            stagger_seconds=0.0,
            pacing_seconds=0.05,
            profiles=self.test_profiles[:1],
            proc_mgr=MagicMock(),
            session_factory=self.session_factory,
        )
        # Populate queue BEFORE starting workers to verify dispatch order
        pool.submit_task({"id": "std_1", "prompt": "Std 1"}, priority=10)
        pool.submit_task({"id": "std_2", "prompt": "Std 2"}, priority=10)
        pool.submit_task({"id": "retry_high", "prompt": "Retry High"}, priority=0)

        with pool:
            pool.wait_completion(timeout=5.0)

        sess = self.sessions["p1"]
        prompts_order = [c["prompt"] for c in sess.generate_calls]
        # retry_high must have executed first!
        self.assertEqual(prompts_order[0], "Retry High")
        self.assertEqual(prompts_order[1:], ["Std 1", "Std 2"])

    def test_pacing_gap_enforcement(self):
        """Sequential requests on the same profile respect calibrated pacing gap."""
        pacing = 0.2  # 200ms
        pool = PersistentWorkerPool(
            target_workers=1,
            stagger_seconds=0.0,
            pacing_seconds=pacing,
            profiles=self.test_profiles[:1],
            proc_mgr=MagicMock(),
            session_factory=self.session_factory,
        )
        t_start = time.time()
        with pool:
            pool.submit_task({"id": "shot_1", "prompt": "Shot 1"})
            pool.submit_task({"id": "shot_2", "prompt": "Shot 2"})
            pool.submit_task({"id": "shot_3", "prompt": "Shot 3"})
            pool.wait_completion(timeout=5.0)
        t_total = time.time() - t_start
        self.assertGreaterEqual(t_total, pacing * 1.8)

        sess = self.sessions["p1"]
        timestamps = [c["timestamp"] for c in sess.generate_calls]
        self.assertEqual(len(timestamps), 3)
        gap1 = timestamps[1] - timestamps[0]
        gap2 = timestamps[2] - timestamps[1]
        self.assertGreaterEqual(gap1, pacing * 0.9)
        self.assertGreaterEqual(gap2, pacing * 0.9)

    def test_rate_limit_error_7_triggers_cooldown_and_standby_swap(self):
        """Error 7 triggers 10-min quarantine, remediation, and standby profile swap."""
        mock_proc = MagicMock()

        def custom_factory(prof_cfg: dict[str, Any]) -> MockCDPSession:
            sess = self.session_factory(prof_cfg)
            if prof_cfg["name"] == "p1":
                sess.should_fail_rate_limit = True
            return sess

        pool = PersistentWorkerPool(
            target_workers=1,
            cooldown_seconds=600.0,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles,  # p1, p2, p3, p4
            proc_mgr=mock_proc,
            session_factory=custom_factory,
        )

        with pool:
            pool.submit_task({"id": "shot_fail", "prompt": "Shot to trigger failover"})
            pool.wait_completion(timeout=5.0)

        # p1 should now be in cooldown!
        self.assertIn("p1", pool.profile_pool.cooldowns)
        self.assertGreater(pool.profile_pool.cooldowns["p1"], time.time() + 500.0)

        # p2 should have been swapped in to complete the retried task!
        self.assertIn("p2", self.sessions)
        p2_sess = self.sessions["p2"]
        self.assertTrue(any(c["prompt"] == "Shot to trigger failover" for c in p2_sess.generate_calls))

        # Results should be successfully recorded
        self.assertIn("shot_fail", pool.results)
        self.assertEqual(pool.results["shot_fail"]["profile_id"], "p2")

    def test_dag_variation_pinning(self):
        """Variation shots with based_on stay strictly pinned to parent profile."""
        pool = PersistentWorkerPool(
            target_workers=3,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles[:3],  # p1, p2, p3
            proc_mgr=MagicMock(),
            session_factory=self.session_factory,
        )

        with pool:
            # Base shot SC01
            pool.submit_task({"id": "SC01", "prompt": "Base shot SC01"})
            # Variations SC01_var1, SC01_var2
            pool.submit_task({"id": "SC01_var1", "based_on": "SC01", "prompt": "Variation 1"})
            pool.submit_task({"id": "SC01_var2", "based_on": "SC01", "prompt": "Variation 2"})
            # Independent shot SC02
            pool.submit_task({"id": "SC02", "prompt": "Independent SC02"})

            pool.wait_completion(timeout=5.0)

        # Retrieve parent profile
        sc01_prof = pool.results["SC01"]["profile_id"]
        var1_prof = pool.results["SC01_var1"]["profile_id"]
        var2_prof = pool.results["SC01_var2"]["profile_id"]

        # MUST be identical!
        self.assertEqual(var1_prof, sc01_prof)
        self.assertEqual(var2_prof, sc01_prof)

        # Base media ID must have been passed to variations
        sc01_media = pool.results["SC01"]["media_id"]
        parent_sess = self.sessions[sc01_prof]
        var_calls = [c for c in parent_sess.generate_calls if "Variation" in c["prompt"]]
        self.assertEqual(len(var_calls), 2)
        for vc in var_calls:
            self.assertEqual(vc["base_media_id"], sc01_media)

    def test_unrecoverable_parent_aborts_deferred_dependents(self):
        """If parent fails permanently, deferred dependent tasks abort cleanly without deadlock."""
        def failing_factory(prof_cfg: dict[str, Any]) -> MockCDPSession:
            sess = self.session_factory(prof_cfg)
            # Permanent failure
            sess.should_fail_transient = True
            return sess

        callback_errors = {}
        def cb(task, res, err):
            if err:
                callback_errors[task["id"]] = str(err)

        pool = PersistentWorkerPool(
            target_workers=1,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles[:1],
            proc_mgr=MagicMock(),
            session_factory=failing_factory,
        )

        with pool:
            # Base shot SC_bad has max_retries=1 so it fails permanently quickly
            pool.submit_task({"id": "SC_bad", "prompt": "Fail prompt", "max_retries": 0, "callback": cb})
            # Dependent shot waiting for SC_bad
            pool.submit_task({"id": "SC_bad_var", "based_on": "SC_bad", "prompt": "Var prompt", "callback": cb})

            finished = pool.wait_completion(timeout=3.0)
            self.assertTrue(finished)

        # Both parent and child must have aborted cleanly
        self.assertIn("SC_bad", callback_errors)
        self.assertIn("SC_bad_var", callback_errors)
        self.assertIn("failed permanently", callback_errors["SC_bad_var"])

    def test_pinned_dependent_tasks_migrated_on_standby_swap(self):
        """When a profile with pinned dependent tasks swaps, all pinned tasks migrate without deadlock."""
        def custom_factory(prof_cfg: dict[str, Any]) -> MockCDPSession:
            sess = self.session_factory(prof_cfg)
            # p1 succeeds on SC_P, then fails rate limit on SC_trigger
            if prof_cfg["name"] == "p1":
                orig_gen = sess.generate_image
                def gen_with_failover(prompt, *args, **kwargs):
                    if "Trigger failover" in prompt:
                        raise RuntimeError("FLOW_PROVIDER_BLOCKED: rate_limit_error_7")
                    return orig_gen(prompt, *args, **kwargs)
                sess.generate_image = gen_with_failover
            return sess

        pool = PersistentWorkerPool(
            target_workers=1,
            cooldown_seconds=600.0,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles,  # p1, p2, p3, p4
            proc_mgr=MagicMock(),
            session_factory=custom_factory,
        )

        with pool:
            # 1. Parent shot succeeds on p1
            pool.submit_task({"id": "SC_P", "prompt": "Parent shot"})
            # 2. Dependent shots wait for SC_P
            pool.submit_task({"id": "SC_D1", "based_on": "SC_P", "prompt": "Child 1"})
            pool.submit_task({"id": "SC_D2", "based_on": "SC_P", "prompt": "Child 2"})
            # 3. Intermediate shot triggers rate limit on p1
            pool.submit_task({"id": "SC_trigger", "prompt": "Trigger failover"})

            # Must complete cleanly without deadlocking on timeout!
            finished = pool.wait_completion(timeout=6.0)
            self.assertTrue(finished, "Pool deadlocked when migrating pinned dependent tasks!")

        # All 4 tasks must have succeeded (SC_P on p1, others completed on p2)
        self.assertIn("SC_P", pool.results)
        self.assertIn("SC_D1", pool.results)
        self.assertIn("SC_D2", pool.results)
        self.assertIn("SC_trigger", pool.results)

    def test_zero_credit_image_tasks_do_not_deduct_credits(self):
        """0-credit BELUGA/image tasks do NOT deduct credits, but touch_used is called."""
        mock_ledger = MagicMock()
        mock_ledger.is_eligible.return_value = True

        pool = PersistentWorkerPool(
            target_workers=1,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles[:1],
            proc_mgr=MagicMock(),
            session_factory=self.session_factory,
            credit_ledger=mock_ledger,
        )

        with pool:
            # 1. Image task with BELUGA model -> 0 credits deducted
            pool.submit_task({"id": "img_01", "prompt": "An image task", "type": "image", "model": "BELUGA"})
            # 2. Video task with credit_cost=10 -> 10 credits deducted
            pool.submit_task({"id": "vid_01", "prompt": "A video task", "type": "video", "credit_cost": 10})
            finished = pool.wait_completion(timeout=5.0)
            self.assertTrue(finished)

        # deduct_credits should only have been called ONCE for vid_01!
        self.assertEqual(mock_ledger.deduct_credits.call_count, 1)
        args, kwargs = mock_ledger.deduct_credits.call_args
        self.assertEqual(args[0], "p1")
        amount_passed = kwargs.get("amount") if "amount" in kwargs else (args[1] if len(args) > 1 else None)
        self.assertEqual(amount_passed, 10)

        # touch_used should have been called for img_01
        self.assertGreaterEqual(mock_ledger.touch_used.call_count, 1)
        mock_ledger.touch_used.assert_called_with("p1")

    def test_work_stealing_steals_overloaded_pinned_tasks_onto_idle_workers(self):
        """enable_work_stealing=True allows idle worker to steal tasks from overloaded pinned queue."""
        pool = PersistentWorkerPool(
            target_workers=2,
            stagger_seconds=0.0,
            pacing_seconds=0.05,
            profiles=self.test_profiles[:2],  # p1 and p2
            proc_mgr=MagicMock(),
            session_factory=self.session_factory,
            enable_work_stealing=True,
            work_steal_threshold=1,
        )

        # Populate p1's pinned queue with 4 tasks before workers run
        for i in range(1, 5):
            pool.pinned_queues["p1"].put(
                (10, i, {"id": f"pinned_p1_{i}", "prompt": f"Task {i}", "pinned_profile": "p1"})
            )
        with pool._tasks_lock:
            pool._pending_tasks += 4

        with pool:
            finished = pool.wait_completion(timeout=5.0)
            self.assertTrue(finished)

        # Both p1 and p2 should have processed at least 1 task because of work stealing!
        self.assertIn("p1", self.sessions)
        self.assertIn("p2", self.sessions)
        p1_calls = self.sessions["p1"].generate_calls
        p2_calls = self.sessions["p2"].generate_calls
        self.assertGreater(len(p1_calls), 0)
        self.assertGreater(len(p2_calls), 0)
        self.assertEqual(len(p1_calls) + len(p2_calls), 4)

    def test_configurable_cooldown_seconds_on_error_7(self):
        """Custom cooldown_seconds=90.0 sets ~90s cooldown on Error 7 instead of 600s."""
        def custom_factory(prof_cfg: dict[str, Any]) -> MockCDPSession:
            sess = self.session_factory(prof_cfg)
            if prof_cfg["name"] == "p1":
                sess.should_fail_rate_limit = True
            return sess

        pool = PersistentWorkerPool(
            target_workers=1,
            cooldown_seconds=90.0,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles,
            proc_mgr=MagicMock(),
            session_factory=custom_factory,
        )

        t_before = time.time()
        with pool:
            pool.submit_task({"id": "shot_fast_cd", "prompt": "Fast cooldown task"})
            pool.wait_completion(timeout=5.0)

        self.assertIn("p1", pool.profile_pool.cooldowns)
        cd_expiry = pool.profile_pool.cooldowns["p1"]
        # Quarantined for ~90s from error occurrence
        self.assertGreater(cd_expiry, t_before + 70.0)
        self.assertLess(cd_expiry, t_before + 110.0)

    def test_warm_session_preservation_on_error_7(self):
        """Browser session is kept warm in warm_sessions on Error 7 (not terminated), and closed on shutdown."""
        mock_proc = MagicMock()

        def custom_factory(prof_cfg: dict[str, Any]) -> MockCDPSession:
            sess = self.session_factory(prof_cfg)
            if prof_cfg["name"] == "p1":
                sess.should_fail_rate_limit = True
            return sess

        pool = PersistentWorkerPool(
            target_workers=1,
            cooldown_seconds=600.0,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles,
            proc_mgr=mock_proc,
            session_factory=custom_factory,
            enforce_os_locks=True,
            max_global_browsers=8,
        )

        with pool:
            pool.submit_task({"id": "shot_err7", "prompt": "Trigger Error 7"})
            pool.wait_completion(timeout=5.0)

            # p1 should be preserved in warm_sessions!
            self.assertIn("p1", pool.warm_sessions)
            p1_sess = pool.warm_sessions["p1"]
            # p1 browser session was NOT closed while kept warm
            self.assertEqual(p1_sess.close_count, 0)
            # p1 was not terminated by port
            self.assertNotIn(9221, [call[0][0] for call in mock_proc.terminate_by_port.call_args_list if call[0]])

        # After pool shutdown, warm session must be cleanly closed
        self.assertEqual(p1_sess.close_count, 1)
        self.assertEqual(len(pool.warm_sessions), 0)

    def test_multi_prompt_batching_independent_anchor_tasks(self):
        """Multiple independent anchor tasks (no based_on / baseMediaId) are batched via generate_images_batch."""
        batch_sessions: dict[str, MockBatchCDPSession] = {}

        def batch_factory(prof_cfg: dict[str, Any]) -> MockBatchCDPSession:
            sess = MockBatchCDPSession(prof_cfg)
            batch_sessions[prof_cfg["name"]] = sess
            return sess

        pool = PersistentWorkerPool(
            target_workers=1,
            stagger_seconds=0.0,
            pacing_seconds=0.01,
            profiles=self.test_profiles[:1],
            proc_mgr=MagicMock(),
            session_factory=batch_factory,
            enable_rpc_batching=True,
            max_rpc_batch_size=4,
        )
        # Queue 4 independent anchor tasks before starting
        for i in range(1, 5):
            pool.submit_task({"id": f"anchor_{i}", "prompt": f"Anchor Prompt {i}", "aspect": "16:9", "model": "BELUGA"})

        with pool:
            finished = pool.wait_completion(timeout=5.0)
            self.assertTrue(finished)

        sess = batch_sessions["p1"]
        # generate_images_batch was called with 4 prompts in a single round-trip!
        self.assertEqual(len(sess.generate_batch_calls), 1)
        batch_call = sess.generate_batch_calls[0]
        self.assertEqual(len(batch_call["prompts"]), 4)
        self.assertEqual(batch_call["prompts"], [f"Anchor Prompt {i}" for i in range(1, 5)])
        # All 4 results recorded
        for i in range(1, 5):
            self.assertIn(f"anchor_{i}", pool.results)

    def test_is_profile_unauthenticated_filtering(self):
        """Unauthenticated profile is excluded from DynamicProfilePool.acquire."""
        import tempfile

        from flow_cdp.resource_locks import (
            is_profile_unauthenticated,
            mark_profile_unauthenticated,
        )

        with tempfile.TemporaryDirectory() as td:
            locks_dir = Path(td)
            self.assertFalse(is_profile_unauthenticated("p1", locks_dir=locks_dir))
            mark_profile_unauthenticated("p1", ttl_sec=3600.0, locks_dir=locks_dir)
            self.assertTrue(is_profile_unauthenticated("p1", locks_dir=locks_dir))

            # DynamicProfilePool respects unauthenticated status
            with patch("flow_cdp.persistent_pool.is_profile_unauthenticated", side_effect=lambda name: name == "p1"):
                pool = PersistentWorkerPool(
                    target_workers=1,
                    profiles=self.test_profiles,
                    session_factory=self.session_factory,
                )
                acquired = pool.profile_pool.acquire()
                # p1 should be skipped, so p2 is acquired!
                self.assertIsNotNone(acquired)
                self.assertEqual(acquired["name"], "p2")


if __name__ == "__main__":
    unittest.main()
