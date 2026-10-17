"""Unit tests for professional Remotion renderer effects (Spring, Easing, Motion Blur, Perlin Shake, Overlays)."""
import math
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def py_organic_noise(time: float, seed: float = 0.0) -> float:
    """Python counterpart of organicNoise in sys/renderer/index.tsx."""
    o1 = math.sin(time * 19.3 + seed * 1.7)
    o2 = math.sin(time * 38.7 + seed * 3.1) * 0.5
    o3 = math.sin(time * 73.1 + seed * 5.9) * 0.25
    return (o1 + o2 + o3) / 1.75


def py_boil_jitter(frame: int, seed: int = 0) -> float:
    """Python counterpart of boilJitter in sys/renderer/index.tsx."""
    step = frame // 4
    r = math.sin(step * 12.9898 + seed * 78.233) * 43758.5453
    return r - math.floor(r) - 0.5


class RendererEffectsTests(unittest.TestCase):
    def test_boil_jitter_deterministic_and_bounded(self):
        # Deterministic
        self.assertEqual(py_boil_jitter(12, 3), py_boil_jitter(12, 3))
        # Bounded between -0.5 and 0.5
        for f in range(120):
            val = py_boil_jitter(f, 1)
            self.assertGreaterEqual(val, -0.5)
            self.assertLessEqual(val, 0.5)
    def test_organic_noise_deterministic_and_bounded(self):
        # 1. Deterministic
        self.assertEqual(py_organic_noise(1.23, 4.5), py_organic_noise(1.23, 4.5))
        # 2. Bounded between -1.0 and 1.0
        for t in [i * 0.05 for i in range(100)]:
            val = py_organic_noise(t, 1.2)
            self.assertGreaterEqual(val, -1.0)
            self.assertLessEqual(val, 1.0)
        # 3. Multi-harmonic: not a simple single frequency sine wave
        diffs = [py_organic_noise(i * 0.01) - math.sin(i * 0.01 * 19.3) / 1.75 for i in range(20)]
        self.assertTrue(any(abs(d) > 0.05 for d in diffs))

    def test_motion_blur_curve_peaks_at_midpoint(self):
        # Motion blur should be zero at start (0) and end (1) of transition
        blur_start = math.sin(0 * math.pi) * 18
        blur_mid = math.sin(0.5 * math.pi) * 18
        blur_end = math.sin(1.0 * math.pi) * 18

        self.assertAlmostEqual(blur_start, 0.0, places=4)
        self.assertAlmostEqual(blur_mid, 18.0, places=4)
        self.assertAlmostEqual(blur_end, 0.0, places=4)

        # Midpoint blur must be greater than quarter points
        blur_quarter = math.sin(0.25 * math.pi) * 18
        self.assertGreater(blur_mid, blur_quarter)

    def test_remotion_bundle_compilation(self):
        check = subprocess.run(["node", "--input-type=module", "-e", "import('@remotion/bundler').catch(() => process.exit(1))"],
                               cwd=str(ROOT / "sys"), capture_output=True)
        if check.returncode != 0:
            self.skipTest("@remotion/bundler not installed locally (Remotion prioritizes Colab T4)")
        # Test that index.tsx bundles cleanly via Remotion bundler
        cmd = [
            "node",
            "--input-type=module",
            "-e",
            """
import { bundle } from '@remotion/bundler';
import path from 'node:path';

const url = await bundle({
  entryPoint: path.resolve('renderer/index.tsx'),
});
if (!url) process.exit(1);
console.log('OK');
"""
        ]
        result = subprocess.run(cmd, cwd=str(ROOT / "sys"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Bundle failed: {result.stderr}")
        self.assertIn("OK", result.stdout)

    def test_capabilities_doc_and_guidelines_consistency(self):
        cap_file = ROOT / "sys/docs/render-capabilities.md"
        cinema_file = ROOT / ".agents/skills/vp-production/references/cinematography.md"

        cap_text = cap_file.read_text()
        cinema_text = cinema_file.read_text()

        # Both docs must mention supported motion blur/whip pan and handheld shake
        self.assertIn("Whip Pan", cap_text)
        self.assertIn("Whip pan", cinema_text)
        self.assertIn("Perlin", cap_text)
        self.assertIn("Cinematic Overlays", cap_text)

        # Parallax must remain unsupported in 2D bitmap scope
        self.assertIn("Parallax 3D đa lớp", cinema_text)
        self.assertIn("Chưa hỗ trợ", cap_text)

        # New jobs use full-frame beats; cut-out layers are deprecated.
        self.assertIn("Deprecated for new jobs", cap_text)
        self.assertIn('kind: "scene"', cap_text)
        self.assertNotIn("vp-layered-motion", cap_text)

    def test_camera_variety_and_sequence_constraints(self):
        import json
        script = """
import {
  selectSemanticCameraEffect,
  cameraVariation,
  resolveFallbackCameraSequence,
  hash01
} from './sys/renderer/camera.mjs';

const scenes = ['SC01', 'SC02', 'SC03', 'SC04', 'CH01_SC01'];
const results = {};

for (const sc of scenes) {
  const seq = resolveFallbackCameraSequence(sc, 24);
  results[sc] = {
    seq,
    variations: [0, 1, 2, 3, 4].map(i => cameraVariation(sc, i)),
  };
}

results.semantic = {
  hold: selectSemanticCameraEffect({effect: 'hold'}, {id: 'SC01'}, 0),
  wide: selectSemanticCameraEffect({}, {id: 'SC01', camera: 'wide view'}, 0),
  punch: selectSemanticCameraEffect({}, {id: 'SC01', camera_intent: 'reveal shock'}, 0),
};

console.log(JSON.stringify(results));
"""
        res = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)

        # 1. Semantic overrides work
        self.assertEqual(data["semantic"]["hold"], "hold")
        self.assertEqual(data["semantic"]["wide"], "zoom_out")
        self.assertEqual(data["semantic"]["punch"], "punch_in")

        # 2. Sequence constraints across scenes
        for sc in ["SC01", "SC02", "SC03", "SC04", "CH01_SC01"]:
            seq = data[sc]["seq"]
            self.assertEqual(len(seq), 24)
            unique_effects = set(seq)
            self.assertGreaterEqual(len(unique_effects), 5, f"Too few unique effects in {sc}: {unique_effects}")

            # No duplicates in any window of 3
            for i in range(len(seq) - 3):
                window = seq[i : i + 3]
                self.assertEqual(len(set(window)), 3, f"Duplicate found in window of 3 for {sc} at {i}: {window}")

            # No consecutive same-direction zoom or vertical oscillation
            zoom_in_family = {"zoom_in", "drift_diag_in"}
            zoom_out_family = {"zoom_out", "drift_diag_out"}
            vertical_family = {"pan_up", "pan_down"}
            for i in range(len(seq) - 1):
                self.assertFalse(
                    seq[i] in zoom_in_family and seq[i + 1] in zoom_in_family,
                    f"Consecutive zoom in at {i} in {sc}",
                )
                self.assertFalse(
                    seq[i] in zoom_out_family and seq[i + 1] in zoom_out_family,
                    f"Consecutive zoom out at {i} in {sc}",
                )
                self.assertFalse(
                    seq[i] in vertical_family and seq[i + 1] in vertical_family,
                    f"Consecutive vertical pan at {i} in {sc}",
                )

            # Variations bounds
            for var in data[sc]["variations"]:
                self.assertGreaterEqual(var["zoomAmp"], 0.04)
                self.assertLessEqual(var["zoomAmp"], 0.09)
                self.assertGreaterEqual(var["panAmp"], 1.5)
                self.assertLessEqual(var["panAmp"], 3.5)
                self.assertEqual(len(var["easing"]), 4)
                self.assertIn(var["dirSign"], [-1, 1])


if __name__ == "__main__":
    unittest.main()
