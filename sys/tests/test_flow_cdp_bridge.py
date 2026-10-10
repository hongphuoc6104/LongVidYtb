"""Unit tests for flow_cdp.bridge module."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import flow_cdp
from flow_cdp.bridge import (
    generate_cdp_image,
    generate_cdp_batch,
    query_status,
    ensure_connected,
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
                 patch("flow_cdp.bridge.generate_cdp_batch", return_value=fake_batch_result):
                res = generate_cdp_image(
                    prompt="A test stick figure",
                    ratio="16:9",
                    test_case="shot-01",
                    out_dir=out_dir,
                )
                self.assertEqual(res["request_id"], "shot-01")
                self.assertEqual(res["media_id"], "forge-123")


if __name__ == "__main__":
    unittest.main()
