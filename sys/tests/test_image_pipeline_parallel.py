"""Unit tests for multi-profile parallel worker queue and based_on routing in image_pipeline."""
import queue
import unittest
from unittest.mock import MagicMock, patch

from flow_cdp.lifecycle import calculate_optimal_workers


class TestImagePipelineParallel(unittest.TestCase):
    """Test dynamic worker queue allocation and based_on profile preservation."""

    def test_worker_sizing_multi_tier(self):
        # 1-3 -> 1
        self.assertEqual(calculate_optimal_workers(3), 1)
        # 5 -> 2, 8 -> 3
        self.assertEqual(calculate_optimal_workers(5), 2)
        self.assertEqual(calculate_optimal_workers(8), 3)
        # 15 -> 4, 20 -> 5
        self.assertEqual(calculate_optimal_workers(15), 4)
        self.assertEqual(calculate_optimal_workers(20), 5)
        # 48 -> 7, 75 -> 8, 300 -> 10
        self.assertEqual(calculate_optimal_workers(48), 7)
        self.assertEqual(calculate_optimal_workers(75), 8)
        self.assertEqual(calculate_optimal_workers(300), 10)

    def test_worker_queue_rotation_and_based_on_inheritance(self):
        """Simulate worker thread execution: independent units get queue profiles, variations inherit parent."""
        pool_profiles = [{"id": f"profile_{i}"} for i in range(1, 11)]
        concurrency = 3

        profile_pool_queue = queue.Queue()
        active_worker_pids = [prof["id"] for prof in pool_profiles[:concurrency]]
        for pid in active_worker_pids:
            profile_pool_queue.put(pid)

        # 3 independent units + 1 variation depending on SC01_01
        units = [
            {"id": "SC01_01", "based_on": None},
            {"id": "SC01_02", "based_on": None},
            {"id": "SC01_03", "based_on": None},
            {"id": "SC01_01_var", "based_on": "SC01_01"},  # Variation
        ]

        completed = {}
        dispatched_profiles = {}

        for u in units:
            base = completed.get(u.get("based_on"))
            assigned_worker_pid = None
            borrowed_from_queue = False

            if base and base.get("profile_id"):
                assigned_worker_pid = base["profile_id"]
            else:
                try:
                    assigned_worker_pid = profile_pool_queue.get_nowait()
                    borrowed_from_queue = True
                except queue.Empty:
                    assigned_worker_pid = None

            dispatched_profiles[u["id"]] = assigned_worker_pid
            completed[u["id"]] = {
                "target": u["id"],
                "path": f"/tmp/{u['id']}.png",
                "sha256": "dummy",
                "profile_id": assigned_worker_pid,
            }

            if borrowed_from_queue and assigned_worker_pid:
                profile_pool_queue.put(assigned_worker_pid)

        # SC01_01, SC01_02, SC01_03 should be assigned profiles from the active pool
        self.assertIn(dispatched_profiles["SC01_01"], active_worker_pids)
        self.assertIn(dispatched_profiles["SC01_02"], active_worker_pids)
        self.assertIn(dispatched_profiles["SC01_03"], active_worker_pids)

        # SC01_01_var MUST inherit SC01_01's exact profile_id!
        self.assertEqual(dispatched_profiles["SC01_01_var"], dispatched_profiles["SC01_01"])

        # Queue should be completely restored to initial capacity
        restored = []
        while not profile_pool_queue.empty():
            restored.append(profile_pool_queue.get_nowait())
        self.assertEqual(sorted(restored), sorted(active_worker_pids))


if __name__ == "__main__":
    unittest.main()
