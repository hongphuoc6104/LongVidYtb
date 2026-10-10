"""Tests verifying that mandatory UI screenshots (ui-proof.json / before-submit.png)
are no longer required to accept valid downloaded image assets.
"""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image

import adapters
from pilot import ROOT, Blocked


class EvidenceRelaxationTests(unittest.TestCase):
    def test_copy_optional_flow_screenshot_does_not_raise_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "screenshot.png"
            # Should not raise even when required=True was passed in older code
            adapters.copy_optional_flow_screenshot(None, dest, required=True)
            self.assertFalse(dest.exists())
            
            non_existent = Path(tmp) / "non-existent.png"
            adapters.copy_optional_flow_screenshot(non_existent, dest, required=True)
            self.assertFalse(dest.exists())

    def test_copy_optional_flow_screenshot_copies_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "real.png"
            dest = Path(tmp) / "copied.png"
            Image.new("RGB", (10, 10)).save(src)
            adapters.copy_optional_flow_screenshot(src, dest, required=False)
            self.assertTrue(dest.exists())

    def test_gflow_image_accepted_without_ui_proof(self):
        """Verify gflow single image generation completes cleanly without requiring ui-proof.json."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_dir = root / "download"
            out_dir.mkdir(parents=True)
            
            img_file = out_dir / "result.png"
            Image.new("RGB", (160, 90), color="blue").save(img_file)
            
            p = SimpleNamespace(root=root, brief=lambda j: [{"aspect_ratio": "16:9"}])
            
            fake_cdp_res = {
                "path": str(img_file),
                "forge_id": "media-test-456",
                "latency": 0.2,
                # No before_submit screenshot provided
                "before_submit": None,
            }
            
            with patch("b2_bridge.generate_b2_image", return_value=fake_cdp_res):
                res = adapters.gflow(
                    p, "image", "--id", "test-req", "--prompt", "A test prompt",
                    "--ratio", "16:9", "--out", str(out_dir)
                )
                self.assertEqual(res.returncode, 0)
                self.assertTrue(img_file.is_file())
                # Metadata sidecar was written
                meta = json.loads(img_file.with_suffix(".json").read_text())
                self.assertEqual(meta["forgeId"], "media-test-456")
                self.assertEqual(meta["status"], "downloaded")


if __name__ == "__main__":
    unittest.main()
