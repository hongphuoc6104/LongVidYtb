"""Unit tests for flow_cdp.lifecycle module."""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from pathlib import Path
import tempfile
from PIL import Image

from flow_cdp.lifecycle import (
    RAMPUP_BATCH_TIERS,
    ProfileLifecycleManager,
    calculate_optimal_workers,
    calculate_rampup_timeout,
    calculate_rampup_workers,
    get_workload_tier_info,
)
from tools.editorial_compositor import apply_editorial_overlay, build_editorial_task_spec


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

    def test_calculate_rampup_workers_and_timeouts_5_tiers(self):
        # Tier 1: <= 10 images -> 4 workers, 120.0s timeout
        self.assertEqual(calculate_rampup_workers(1), 4)
        self.assertEqual(calculate_rampup_workers(5), 4)
        self.assertEqual(calculate_rampup_workers(10), 4)
        self.assertEqual(calculate_rampup_timeout(1), 120.0)
        self.assertEqual(calculate_rampup_timeout(10), 120.0)

        # Tier 2: <= 30 images -> 6 workers, 210.0s timeout
        self.assertEqual(calculate_rampup_workers(11), 6)
        self.assertEqual(calculate_rampup_workers(30), 6)
        self.assertEqual(calculate_rampup_timeout(11), 210.0)
        self.assertEqual(calculate_rampup_timeout(30), 210.0)

        # Tier 3: <= 60 images -> 9 workers, 300.0s timeout
        self.assertEqual(calculate_rampup_workers(31), 9)
        self.assertEqual(calculate_rampup_workers(60), 9)
        self.assertEqual(calculate_rampup_timeout(31), 300.0)
        self.assertEqual(calculate_rampup_timeout(60), 300.0)

        # Tier 4: <= 90 images -> 11 workers, 390.0s timeout
        self.assertEqual(calculate_rampup_workers(61), 11)
        self.assertEqual(calculate_rampup_workers(90), 11)
        self.assertEqual(calculate_rampup_timeout(61), 390.0)
        self.assertEqual(calculate_rampup_timeout(90), 390.0)

        # Tier 5: > 90 images (e.g. 110) -> 12 workers, 480.0s timeout
        self.assertEqual(calculate_rampup_workers(91), 12)
        self.assertEqual(calculate_rampup_workers(110), 12)
        self.assertEqual(calculate_rampup_workers(300), 12)
        self.assertEqual(calculate_rampup_timeout(91), 480.0)
        self.assertEqual(calculate_rampup_timeout(110), 480.0)
        self.assertEqual(len(RAMPUP_BATCH_TIERS), 5)

    def test_apply_editorial_overlay_default_healing_png_and_jpeg(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            png_path = tmp_dir / "test.png"
            Image.new("RGB", (1280, 720), (255, 255, 255)).save(png_path, format="PNG")
            res_png = apply_editorial_overlay(png_path)
            self.assertEqual(Path(res_png), png_path)
            with Image.open(png_path) as im:
                im.verify()
                self.assertEqual(im.format, "PNG")

            jpg_path = tmp_dir / "test.jpg"
            Image.new("RGB", (1920, 1080), (200, 200, 200)).save(jpg_path, format="JPEG")
            res_jpg = apply_editorial_overlay(jpg_path)
            self.assertEqual(Path(res_jpg), jpg_path)
            with Image.open(jpg_path) as im:
                im.verify()
                self.assertEqual(im.format, "JPEG")

    def test_editorial_compositor_preserves_dimensions_and_compiles_170(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            spec = build_editorial_task_spec(1, 1, tmp_dir)
            self.assertEqual(spec["ratio"], "16:9")
            self.assertTrue(spec["editorial_overlay"]["enabled"])
            self.assertNotIn("Scene 001", spec["prompt"])

            img_path = tmp_dir / "SC001.jpg"
            Image.new("RGB", (1920, 1080), (255, 255, 255)).save(img_path, format="JPEG")
            apply_editorial_overlay(img_path, spec["editorial_overlay"])
            with Image.open(img_path) as out_im:
                out_im.verify()
            with Image.open(img_path) as out_im:
                self.assertEqual(out_im.size, (1920, 1080))

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

