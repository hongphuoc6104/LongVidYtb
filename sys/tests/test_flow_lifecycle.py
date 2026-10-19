"""Unit tests for flow_cdp.lifecycle module."""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from flow_cdp.lifecycle import (
    ProfileLifecycleManager,
    calculate_optimal_workers,
    get_workload_tier_info,
)


class TestFlowLifecycle(unittest.TestCase):
    def test_calculate_optimal_workers_tiers(self):
        # 1-3 images: 1 worker
        self.assertEqual(calculate_optimal_workers(1), 1)
        self.assertEqual(calculate_optimal_workers(2), 1)
        self.assertEqual(calculate_optimal_workers(3), 1)

        # 4-8 images: 2-3 workers
        self.assertEqual(calculate_optimal_workers(5), 2)
        self.assertEqual(calculate_optimal_workers(8), 3)

        # 9-20 images: 3-5 workers
        self.assertEqual(calculate_optimal_workers(12), 3)
        self.assertEqual(calculate_optimal_workers(16), 4)
        self.assertEqual(calculate_optimal_workers(20), 5)

        # 21-50 images: 5-7 workers
        self.assertEqual(calculate_optimal_workers(25), 5)
        self.assertEqual(calculate_optimal_workers(48), 7)

        # Bulk > 50 images: 8-10 workers
        self.assertEqual(calculate_optimal_workers(75), 8)
        self.assertEqual(calculate_optimal_workers(300), 10)

    def test_get_workload_tier_info(self):
        info_micro = get_workload_tier_info(2)
        self.assertEqual(info_micro["tier"], "micro")
        self.assertEqual(info_micro["actual_workers"], 1)

        info_short = get_workload_tier_info(5)
        self.assertEqual(info_short["tier"], "short")
        self.assertEqual(info_short["actual_workers"], 2)

        info_bulk = get_workload_tier_info(300)
        self.assertEqual(info_bulk["tier"], "bulk_long_video")
        self.assertEqual(info_bulk["actual_workers"], 10)

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.launch_profile", return_value=True)
    @patch("flow_cdp.accounts.is_port_listening", side_effect=[False, False, True])
    @patch("flow_cdp.accounts.registry", return_value={"profiles": []})
    def test_lifecycle_manager_spawns_and_teardowns_exact_opened(
        self, mock_reg, mock_listening, mock_launch, mock_stop
    ):
        with ProfileLifecycleManager(auto_teardown=True) as mgr:
            prof = {"cdp_port": 9225, "user_data_dir": "/tmp/p1", "profile_dir": "Profile 1"}
            ok = mgr.launch_profile(prof)
            self.assertTrue(ok)
            self.assertIn(9225, mgr.spawned_ports)

        # When exiting with block, teardown must be called on 9225
        mock_stop.assert_called_with(9225)


if __name__ == "__main__":
    unittest.main()
