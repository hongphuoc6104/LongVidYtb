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



    def test_weyl_cinematic_camera_vectors_non_repeating_and_bounded(self):
        cmd = [
            "node",
            "--input-type=module",
            "-e",
            """
import {selectSemanticCameraEffect, computeCinematicCameraVector} from './renderer/camera.mjs';
const seen = new Set();
let prevEff = '';
for (let i = 0; i < 48; i++) {
  const sc = {
    id: `SC${String(i + 1).padStart(2, '0')}`,
    title: `Scene ${i + 1}`,
    start: i * 14,
    end: (i + 1) * 14,
    tone: i % 3 === 0 ? 'reflective_slow' : (i % 3 === 1 ? 'analytical_crisp' : 'narrative_warm')
  };
  const eff = selectSemanticCameraEffect({effect: 'auto'}, sc, i);
  if (i > 0 && eff === prevEff) {
    process.exit(2);
  }
  prevEff = eff;
  const vec = computeCinematicCameraVector(eff, sc, i);
  const sig = JSON.stringify(vec);
  if (seen.has(sig)) process.exit(3);
  seen.add(sig);
  if (vec.scaleStart < 1.0 || vec.scaleEnd > 1.08 || Math.abs(vec.txStart) > 1.5 || Math.abs(vec.txEnd) > 1.5) {
    process.exit(4);
  }
}
console.log('WEYL_48_OK');
"""
        ]
        result = subprocess.run(cmd, cwd=str(ROOT / "sys"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Weyl vector test failed: {result.stderr}")
        self.assertIn("WEYL_48_OK", result.stdout)



    def test_aspect_adaptive_camera_focus_and_anchor_group_continuity(self):
        cmd = [
            "node",
            "--input-type=module",
            "-e",
            """
import {
  selectSemanticCameraEffect,
  computeCinematicCameraVector,
  resolveCameraAnchorGroup,
  resolveBeatFocus,
  isContinuousCameraBeat
} from './renderer/camera.mjs';

const sc = { id: 'SC01', title: 'Hook', start: 0, end: 12, tone: 'narrative_warm' };
const vec16x9 = computeCinematicCameraVector('pan_right', sc, 0, false);
const vec9x16 = computeCinematicCameraVector('pan_right', sc, 0, true);

// 1. 9:16 tightens horizontal pan swing compared to 16:9
const span16 = Math.abs(vec16x9.txEnd - vec16x9.txStart);
const span9 = Math.abs(vec9x16.txEnd - vec9x16.txStart);
if (!(span9 < span16)) process.exit(10);

// 2. Focus resolution: default {0.5, 0.5} maps to 44% on 16:9 and 40% on 9:16; explicit beat focus is honored on Beat 2+
const defaultBeat = { focus: { x: 0.5, y: 0.5 } };
const customBeat = { focus: { x: 0.38, y: 0.36 } };
const f16 = resolveBeatFocus(defaultBeat, defaultBeat, false);
const f9 = resolveBeatFocus(defaultBeat, defaultBeat, true);
const fCustom = resolveBeatFocus(customBeat, defaultBeat, true);
if (f16.focusY !== 44 || f9.focusY !== 40) process.exit(11);
if (fCustom.focusX !== 38 || fCustom.focusY !== 36) process.exit(12);

// 3. Anchor-group continuity: full_scene + variations share one continuous group; macro_prop and white_card isolate cleanly
const beats = [
  { id: 'B1', at: 0.0, shot_type: 'macro_prop', effect: 'punch_in', focus: { x: 0.5, y: 0.5 } },
  { id: 'B2', at: 2.2, shot_type: 'full_scene', effect: 'zoom_in', focus: { x: 0.5, y: 0.5 } },
  { id: 'B3', at: 5.0, shot_type: 'variation', based_on: 'SC01_I2', effect: 'pan_right', focus: { x: 0.5, y: 0.5 } },
  { id: 'B4', at: 8.2, shot_type: 'variation', based_on: 'SC01_I2', effect: 'zoom_out', focus: { x: 0.5, y: 0.5 } },
  { id: 'B5', at: 11.0, shot_type: 'white_card', effect: 'hold', focus: { x: 0.5, y: 0.5 } }
];
const g0 = resolveCameraAnchorGroup(beats, 0, 14.0);
const g1 = resolveCameraAnchorGroup(beats, 1, 14.0);
const g2 = resolveCameraAnchorGroup(beats, 2, 14.0);
const g3 = resolveCameraAnchorGroup(beats, 3, 14.0);
const g4 = resolveCameraAnchorGroup(beats, 4, 14.0);

if (g0.startIndex !== 0 || g0.endIndex !== 0 || Math.abs(g0.span - 2.2) > 1e-4) process.exit(13);
if (g1.startIndex !== 1 || g1.endIndex !== 3 || Math.abs(g1.span - 8.8) > 1e-4) process.exit(14);
if (g2.startIndex !== 1 || g3.startIndex !== 1) process.exit(15);
if (g4.startIndex !== 4 || g4.endIndex !== 4 || selectSemanticCameraEffect(beats[4], sc, 4) !== 'hold') process.exit(16);
if (isContinuousCameraBeat(beats[3], beats[4])) process.exit(17);

console.log('ASPECT_AND_ANCHOR_OK');
"""
        ]
        result = subprocess.run(cmd, cwd=str(ROOT / "sys"), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Aspect/Anchor test failed (code {result.returncode}): {result.stderr}")
        self.assertIn("ASPECT_AND_ANCHOR_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
