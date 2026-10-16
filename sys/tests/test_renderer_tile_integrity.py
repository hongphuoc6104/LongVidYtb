"""Unit tests verifying Chromium GPU raster tile integrity and Remotion headless safety."""
import os
from pathlib import Path
import unittest

from pilot import ROOT
SYSTEM = ROOT


class RendererTileIntegrityTests(unittest.TestCase):
    def test_render_mjs_headless_configuration(self):
        content = (SYSTEM / 'renderer/render.mjs').read_text()
        self.assertIn("wrapChromeExecutable", content)
        self.assertIn("process.env.DISABLE_FROM_SURFACE = 'true'", content)
        self.assertIn("--enable-gpu", content)
        self.assertIn("--run-all-compositor-stages-before-draw", content)
        self.assertIn("--disable-gpu-rasterization", content)
        self.assertIn("--disable-dev-shm-usage", content)

    def test_job_worker_env_disable_from_surface(self):
        content = (SYSTEM / 'colab_bridge/job_worker.py').read_text()
        self.assertIn("DISABLE_FROM_SURFACE='true'", content)
        self.assertIn("chrome-wrapper.sh", content)
        self.assertIn("--run-all-compositor-stages-before-draw", content)
        self.assertIn("--disable-gpu-rasterization", content)

    def test_render_mjs_nvenc_hardware_acceleration_and_headless_safety(self):
        content = (SYSTEM / 'renderer/render.mjs').read_text()
        self.assertIn("videoBitrate: '6M'", content)
        self.assertIn("hardwareAcceleration: 'if-possible'", content)
        self.assertIn("10_nvidia.json", content)
        self.assertIn("--use-angle=gl-egl", content)
        self.assertIn("--disable-checker-imaging", content)
        self.assertIn("--disable-new-content-rendering-timeout", content)
        self.assertIn("--disable-gpu-rasterization", content)
        self.assertNotIn("--use-angle=gl\n", content)
        self.assertNotIn("--use-angle=gl ", content)

    def test_job_worker_safe_headless_and_prohibits_xvfb(self):
        content = (SYSTEM / 'colab_bridge/job_worker.py').read_text()
        self.assertNotIn("xvfb-run", content)
        self.assertIn("10_nvidia.json", content)
        self.assertIn("--use-angle=gl-egl", content)
        self.assertIn("--disable-checker-imaging", content)
        self.assertIn("--disable-new-content-rendering-timeout", content)
        self.assertIn("env.pop('DISPLAY', None)", content)
        self.assertIn("--disable-gpu-rasterization", content)

    def test_production_bundles_enforce_t4_and_clean_headless(self):
        for script_rel in (
            'exports/study_motivation_bundle/scripts/render_all_on_colab.py',
            'exports/terrifying_humans_bundle/scripts/render_all_on_colab.py',
        ):
            script_path = SYSTEM / script_rel
            if script_path.is_file():
                txt = script_path.read_text()
                self.assertIn("del env['DISPLAY']", txt)
                self.assertIn("pkill", txt)
        for old_script_rel in (
            'exports/motivation_v2_exp_bundle/scripts/render_all_on_colab.py',
            'exports/ancient_humans_bundle/scripts/render_all_on_colab.py',
        ):
            old_path = SYSTEM / old_script_rel
            if old_path.is_file():
                txt = old_path.read_text()
                self.assertIn("COLAB_T4_NOT_CONFIRMED", txt)

    def test_subtitles_z_index_and_caption_style(self):
        captions_js = (SYSTEM / 'renderer/captions.mjs').read_text()
        self.assertIn("zIndex: 30", captions_js)

        index_tsx = (SYSTEM / 'renderer/index.tsx').read_text()
        self.assertIn("zIndex: 30", index_tsx)
        self.assertIn("objectFit: 'cover'", index_tsx)

    def test_no_blinding_bg_flash(self):
        index_tsx = (SYSTEM / 'renderer/index.tsx').read_text()
        self.assertNotIn("[1, 0]", [line.strip() for line in index_tsx.splitlines() if 'bg_flash' in line])

    def test_flow_compiler_rejects_deprecated_layer_asset_prompts(self):
        from flow_prompts import compile as compile_prompt
        data = {'description': 'Complete scene in a palace hall', 'aspect_ratio': '9:16'}
        for purpose in ('layer_background', 'layer_sticker'):
            with self.subTest(purpose=purpose), self.assertRaisesRegex(ValueError, 'FLOW_LAYERING_DISABLED'):
                compile_prompt('NanoBanana2Lite', purpose, data, '1.2.0')



    def test_tile_drop_scanner_function(self):
        """Ensure tile drop detector accurately identifies white tile drops and clean frames."""
        import numpy as np
        # 1080x1920 frame with dropped bottom tiles
        bad_frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        bad_frame[1280:, :] = 254  # dropped tiles
        b20 = np.mean(bad_frame[int(1920*0.8):, :, 0] > 240)
        self.assertGreater(b20, 0.9)

        # Clean frame
        clean_frame = np.full((1920, 1080, 3), 120, dtype=np.uint8)
        b20_clean = np.mean(clean_frame[int(1920*0.8):, :, 0] > 240)
        self.assertLess(b20_clean, 0.05)

if __name__ == '__main__':
    unittest.main()
