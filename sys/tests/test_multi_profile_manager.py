"""Unit tests for MultiProfileManager and failover dispatcher."""
import time
import unittest
from flow_cdp.multi_profile_manager import (
    MultiProfileManager,
    MultiProfileDispatcher,
    ProfileState,
    ChromeProfileWorker,
)
from flow_cdp.patch_partitioner import Patch


class TestMultiProfileManager(unittest.TestCase):
    def setUp(self):
        self.profiles = [
            {"id": "p1", "port": 9222, "directory": "Profile 1"},
            {"id": "p2", "port": 9223, "directory": "Profile 2"},
            {"id": "p3", "port": 9224, "directory": "Profile 3"},
        ]
        self.manager = MultiProfileManager(self.profiles, cooldown_seconds=2.0)

    def test_initial_pool_status(self):
        status = self.manager.get_status()
        self.assertEqual(status["active_workers"], 3)
        self.assertTrue(all(p["state"] == "healthy" for p in status["profiles"]))

    def test_worker_acquisition_and_release(self):
        w1 = self.manager.acquire_healthy_worker()
        self.assertIsNotNone(w1)
        self.assertEqual(w1.state, ProfileState.BUSY)

        w2 = self.manager.acquire_healthy_worker()
        self.assertIsNotNone(w2)
        self.assertNotEqual(w1.profile_id, w2.profile_id)

        # Release w1 with success
        self.manager.release_worker(w1, success=True)
        self.assertEqual(w1.state, ProfileState.HEALTHY)
        self.assertEqual(w1.success_count, 1)

    def test_error_triggers_cooldown(self):
        w = self.manager.acquire_healthy_worker()
        self.manager.release_worker(w, success=False, error="PUBLIC_ERROR_UNUSUAL_ACTIVITY detected")
        self.assertEqual(w.state, ProfileState.COOLDOWN)
        self.assertGreater(w.cooldown_until, time.time())

        # An acquired worker should NOT be w
        next_w = self.manager.acquire_healthy_worker()
        self.assertNotEqual(next_w.profile_id, w.profile_id)

    def test_dispatcher_failover_on_unusual_activity(self):
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        patch = Patch(
            patch_id="patch-failover-1",
            items=[
                {"testCase": "shot-1", "prompt": "Shot 1"},
                {"testCase": "shot-2", "prompt": "Shot 2"},
            ],
        )

        attempts = []

        def mock_executor(worker: ChromeProfileWorker, items: list[dict]):
            attempts.append((worker.profile_id, [x["testCase"] for x in items]))
            if worker.profile_id == "p1":
                # p1 succeeds on shot-1 then fails on shot-2 with unusual activity
                patch.mark_item_success("shot-1", {"path": "/tmp/1.png", "media_id": "m1"})
                raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY: Account blocked temporarily")
            # Other workers succeed on whatever items they are given
            return [{"path": f"/tmp/{x['testCase']}.png", "media_id": f"m-{x['testCase']}"} for x in items]

        results = dispatcher.execute_patch_with_failover(patch, mock_executor)
        
        # Verify p1 was tried first, then another worker took over only the remaining items (shot-2)
        self.assertGreaterEqual(len(attempts), 2)
        self.assertEqual(attempts[0][0], "p1")
        self.assertIn("shot-1", attempts[0][1])
        
        # Second attempt should NOT be p1, and only needs shot-2
        self.assertNotEqual(attempts[1][0], "p1")
        self.assertEqual(attempts[1][1], ["shot-2"])
        
        # Final result should be completed with 2 items
        self.assertTrue(patch.is_completed)
        self.assertEqual(len(results), 2)

    def test_parallel_dispatch_across_workers(self):
        dispatcher = MultiProfileDispatcher(self.manager)
        patches = [
            Patch(patch_id=f"patch-{i}", items=[{"testCase": f"shot-{i}-1", "prompt": "p"}])
            for i in range(3)
        ]

        assigned_profiles = set()

        def slow_executor(worker: ChromeProfileWorker, items: list[dict]):
            assigned_profiles.add(worker.profile_id)
            time.sleep(0.05)
            return [{"path": f"/tmp/{items[0]['testCase']}.png", "media_id": "ok"}]

        results = dispatcher.dispatch_all(patches, slow_executor, max_concurrency=3)
        self.assertEqual(len(results), 3)
        # Should have utilized multiple distinct profiles in parallel
        self.assertGreater(len(assigned_profiles), 1)

    def test_probe_status_includes_port_listening(self):
        status = self.manager.get_status(probe_ports=True)
        self.assertIn("port_listening", status["profiles"][0])
        self.assertIsInstance(status["profiles"][0]["port_listening"], bool)

    def test_all_workers_blocked_raises_error(self):
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=1)
        patch = Patch(patch_id="p-fail-all", items=[{"testCase": "t-1"}])
        
        def always_fail(worker: ChromeProfileWorker, items: list[dict]):
            raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY")

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.execute_patch_with_failover(patch, always_fail)
        self.assertIn("failed after", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
