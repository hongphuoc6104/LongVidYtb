"""Unit tests for flow_cdp.bridge module."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flow_cdp.bridge import (
    ensure_connected,
    generate_cdp_batch,
    generate_cdp_image,
    query_status,
    require_queue_acceptance,
)

from pilot import Blocked


class FlowCdpBridgeTests(unittest.TestCase):
    def test_require_queue_acceptance_respects_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.json").write_text(json.dumps({"flow_queue_trial_enabled": True}))
            (root / "acceptance.json").write_text(json.dumps({"production_ready": False}))

            with patch("flow_cdp.bridge._config", return_value={"flow_queue_trial_enabled": True}):
                # Should not raise when flow_queue_trial_enabled is True
                require_queue_acceptance()

            with patch("flow_cdp.bridge._config", return_value={"flow_queue_trial_enabled": False}), \
                 patch("flow_cdp.bridge.MODULE_ROOT", root), \
                 patch("flow_cdp.bridge.SYS_ROOT", root):
                with self.assertRaises(Blocked):
                    require_queue_acceptance()

    def test_query_status_and_ensure_connected(self):
        with patch("flow_cdp.bridge.send_raw_command", return_value={"status": "connected"}):
            status = query_status()
            self.assertEqual(status["status"], "connected")

            connected = ensure_connected()
            self.assertEqual(connected["status"], "connected")

    def test_generate_cdp_image_invokes_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            dummy_img = out_dir / "shot.png"
            dummy_img.write_text("fake binary")

            fake_batch_result = [
                {
                    "request_id": "shot-01",
                    "path": str(dummy_img),
                    "media_id": "forge-123",
                    "sha256": "abc123hash",
                }
            ]

            with patch("flow_cdp.bridge.require_queue_acceptance"), \
                 patch("flow_cdp.bridge.ensure_connected"), \
                 patch("flow_cdp.bridge.generate_cdp_batch", return_value=fake_batch_result) as batch:
                res = generate_cdp_image(
                    prompt="A test stick figure",
                    ratio="16:9",
                    test_case="shot-01",
                    job_id="real-production-job",
                    out_dir=out_dir,
                )
                self.assertEqual(res["request_id"], "shot-01")
                self.assertEqual(res["media_id"], "forge-123")
                self.assertEqual(batch.call_args.args[0][0]["jobId"], "real-production-job")
                self.assertEqual(batch.call_args.args[0][0]["testCase"], "shot-01")

    def test_generate_cdp_image_inherits_profile_from_base_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            base_img = work_dir / "base.png"
            base_img.write_text("base binary")
            base_sidecar = work_dir / "base.json"
            base_sidecar.write_text(json.dumps({
                "jobId": "base-job",
                "forgeId": "forge-base-999",
                "profile_id": "profile_2",
            }))

            fake_res = [{
                "request_id": "child-01",
                "path": str(work_dir / "child.png"),
                "forge_id": "forge-child-100",
                "profile_id": "profile_2",
            }]

            with patch("flow_cdp.bridge.require_queue_acceptance"), \
                 patch("flow_cdp.bridge.ensure_connected"), \
                 patch("flow_cdp.bridge.generate_cdp_batch", return_value=fake_res) as batch_mock:
                res = generate_cdp_image(
                    prompt="Variation shot",
                    ratio="16:9",
                    base_ref_path=base_img,
                    test_case="child-01",
                    out_dir=work_dir,
                )
                self.assertEqual(res["request_id"], "child-01")
                # Verify profile_id="profile_2" was passed to generate_cdp_batch
                self.assertEqual(batch_mock.call_args.kwargs.get("profile_id"), "profile_2")
                self.assertEqual(batch_mock.call_args.args[0][0].get("profile_id"), "profile_2")

    def test_generate_cdp_batch_pins_to_target_profile(self):
        specs = [
            {"testCase": "shot-1", "prompt": "P1", "profile_id": "profile_3"},
            {"testCase": "shot-2", "prompt": "P2", "profile_id": "profile_3"},
        ]
        with patch("flow_cdp.bridge._config", return_value={
            "patch_size": 3,
            "flow_cdp_profiles": [
                {"id": "profile_1", "port": 9225, "directory": "Profile 1"},
                {"id": "profile_2", "port": 9223, "directory": "Profile 2"},
                {"id": "profile_3", "port": 9224, "directory": "Profile 3"},
            ],
        }), patch("flow_cdp.bridge._execute_sub_batch") as exec_sub_mock:
            exec_sub_mock.return_value = [
                {"request_id": "shot-1", "path": "/tmp/1.png", "forge_id": "f1", "profile_id": "profile_3"},
                {"request_id": "shot-2", "path": "/tmp/2.png", "forge_id": "f2", "profile_id": "profile_3"},
            ]
            results = generate_cdp_batch(specs)
            self.assertEqual(len(results), 2)
            # The worker passed to _execute_sub_batch must be profile_3
            worker = exec_sub_mock.call_args.kwargs.get("worker")
            self.assertIsNotNone(worker)
            self.assertEqual(worker.profile_id, "profile_3")

    def test_generate_cdp_batch_pins_target_profile_with_mixed_specs(self):
        # First spec has no profile_id (independent), second spec has profile_3
        specs = [
            {"testCase": "shot-indep", "prompt": "P1"},
            {"testCase": "shot-dep", "prompt": "P2", "profile_id": "profile_3"},
        ]
        with patch("flow_cdp.bridge._config", return_value={
            "patch_size": 3,
            "flow_cdp_profiles": [
                {"id": "profile_1", "port": 9225, "directory": "Profile 1"},
                {"id": "profile_2", "port": 9223, "directory": "Profile 2"},
                {"id": "profile_3", "port": 9224, "directory": "Profile 3"},
            ],
        }), patch("flow_cdp.bridge._execute_sub_batch") as exec_sub_mock:
            exec_sub_mock.return_value = [
                {"request_id": "shot-indep", "path": "/tmp/1.png", "forge_id": "f1", "profile_id": "profile_3"},
                {"request_id": "shot-dep", "path": "/tmp/2.png", "forge_id": "f2", "profile_id": "profile_3"},
            ]
            results = generate_cdp_batch(specs)
            self.assertEqual(len(results), 2)
            worker = exec_sub_mock.call_args.kwargs.get("worker")
            self.assertIsNotNone(worker)
            self.assertEqual(worker.profile_id, "profile_3")


    def test_generate_cdp_batch_calculates_5_tier_timeout_and_workers(self):
        specs_small = [{"testCase": f"shot-{i}", "prompt": f"P{i}", "profile_id": "profile_1"} for i in range(2)]
        with patch("flow_cdp.bridge._config", return_value={"patch_size": 3, "flow_cdp_profiles": [{"id": "profile_1", "port": 9225}]}), \
             patch("flow_cdp.bridge._execute_sub_batch") as exec_sub_mock:
            exec_sub_mock.return_value = [{"request_id": f"shot-{i}", "path": f"/tmp/{i}.png", "profile_id": "profile_1"} for i in range(2)]
            generate_cdp_batch(specs_small)
            self.assertEqual(exec_sub_mock.call_args.kwargs.get("timeout"), 120.0)

        specs_bulk = [{"testCase": f"shot-{i}", "prompt": f"P{i}"} for i in range(105)]
        with patch("flow_cdp.bridge._config", return_value={"patch_size": 3, "flow_cdp_profiles": [{"id": f"profile_{i}", "port": 9220 + i} for i in range(1, 15)]}), \
             patch("flow_cdp.bridge._execute_sub_batch") as exec_sub_mock, \
             patch("flow_cdp.bridge.MultiProfileDispatcher.dispatch_all") as dispatch_mock:
            dispatch_mock.return_value = [{"request_id": f"shot-{i}", "path": f"/tmp/{i}.png"} for i in range(105)]
            generate_cdp_batch(specs_bulk)
            # Concurrency passed to dispatch_all should be 12 (max tier 5 cap)
            self.assertEqual(dispatch_mock.call_args.kwargs.get("max_concurrency"), 12)


if __name__ == "__main__":
    unittest.main()


