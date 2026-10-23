"""Unit tests for PersistentWorkerPool."""
from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

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


if __name__ == "__main__":
    unittest.main()
