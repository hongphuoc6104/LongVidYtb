"""End-to-end regression and contract tests for standalone Remotion rendering."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "sample_render_package"


class StandaloneRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        cls.ffprobe = shutil.which("ffprobe")

    def test_native_srt_generator_logic(self):
        """Validates formatSrtTimestamp and generateSrt in sys/renderer/srt.mjs."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        script = """
import { formatSrtTimestamp, generateSrt } from './renderer/srt.mjs';

const t0 = formatSrtTimestamp(0);
const t1 = formatSrtTimestamp(2.5);
const t2 = formatSrtTimestamp(65.123);
const t3 = formatSrtTimestamp(3665.045);

const cues = [
  { start: 0.0, end: 2.5, text: '  Xin chào đây là bản dựng video độc lập.  ' },
  { start: 2.5, end: 5.1, text: 'Phụ đề thứ hai.' }
];

const srt = generateSrt(cues);
const emptySrt = generateSrt([]);
const nullSrt = generateSrt(null);

console.log(JSON.stringify({ t0, t1, t2, t3, srt, emptySrt, nullSrt }));
"""
        res = subprocess.run(
            [self.node, "--input-type=module", "-e", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)

        self.assertEqual(data["t0"], "00:00:00,000")
        self.assertEqual(data["t1"], "00:00:02,500")
        self.assertEqual(data["t2"], "00:01:05,123")
        self.assertEqual(data["t3"], "01:01:05,045")

        expected_srt = (
            "1\n00:00:00,000 --> 00:00:02,500\nXin chào đây là bản dựng video độc lập.\n\n"
            "2\n00:00:02,500 --> 00:00:05,100\nPhụ đề thứ hai.\n"
        )
        self.assertEqual(data["srt"], expected_srt)
        self.assertEqual(data["emptySrt"], "")
        self.assertEqual(data["nullSrt"], "")

    def test_standalone_fixture_renders_cleanly(self):
        """Verifies strict I/O contract execution against standalone sample package."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        self.assertTrue(FIXTURE_DIR.is_dir(), f"Fixture directory missing: {FIXTURE_DIR}")
        props_file = FIXTURE_DIR / "props.json"
        self.assertTrue(props_file.is_file(), "props.json missing in fixture")

        # Execute node render.mjs directly
        cmd = [self.node, str(ROOT / "renderer" / "render.mjs"), str(FIXTURE_DIR)]
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Render command failed:\n{res.stderr}\n{res.stdout}")

        # 1. Output MP4 verification
        video_file = FIXTURE_DIR / "video.mp4"
        video_9x16_file = FIXTURE_DIR / "video_9x16.mp4"
        self.assertTrue(video_file.is_file(), "video.mp4 was not produced")
        self.assertTrue(video_9x16_file.is_file(), "video_9x16.mp4 was not produced")
        self.assertGreater(video_file.stat().st_size, 50000, "video.mp4 is suspiciously small")

        if self.ffprobe:
            probe_raw = subprocess.check_output(
                [self.ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video_file)],
                text=True,
            )
            probe = json.loads(probe_raw)
            video_stream = next((s for s in probe["streams"] if s["codec_type"] == "video"), None)
            audio_stream = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)

            self.assertIsNotNone(video_stream, "No video stream in video.mp4")
            self.assertIsNotNone(audio_stream, "No audio stream in video.mp4")
            self.assertEqual(video_stream["codec_name"], "h264")
            self.assertEqual(audio_stream["codec_name"], "aac")
            self.assertEqual(video_stream["width"], 1080)
            self.assertEqual(video_stream["height"], 1920)

        # 2. Output Subtitles SRT verification
        srt_file = FIXTURE_DIR / "subtitles.srt"
        self.assertTrue(srt_file.is_file(), "subtitles.srt was not produced")
        srt_text = srt_file.read_text(encoding="utf-8")
        self.assertIn("1\n00:00:00,500 --> 00:00:02,500", srt_text)
        self.assertIn("Thử nghiệm hệ thống render Remotion độc lập.", srt_text)

        # 3. Output Layout Safety Audit
        layout_file = FIXTURE_DIR / "layout.json"
        self.assertTrue(layout_file.is_file(), "layout.json was not produced")
        layout_data = json.loads(layout_file.read_text(encoding="utf-8"))
        self.assertTrue(layout_data.get("passed"), f"Layout check failed: {layout_data}")
        self.assertEqual(len(layout_data.get("failures", [])), 0)

        # 4. Output Scene Preview Stills
        still_file = FIXTURE_DIR / "SC01.png"
        self.assertTrue(still_file.is_file(), "Representative still SC01.png was not produced")
        self.assertGreater(still_file.stat().st_size, 10000, "SC01.png is suspiciously small")
        if self.ffprobe:
            dim = subprocess.check_output(
                [
                    self.ffprobe,
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "csv=s=x:p=0",
                    str(still_file),
                ],
                text=True,
            ).strip()
            self.assertEqual(dim, "1080x1920")

        # 5. Output Thumbnail/Cover Stills
        cover_file = FIXTURE_DIR / "cover_tiktok_reels_9x16.png"
        self.assertTrue(cover_file.is_file(), "cover_tiktok_reels_9x16.png was not produced")
        self.assertGreater(cover_file.stat().st_size, 10000, "cover_tiktok_reels_9x16.png is suspiciously small")
        if self.ffprobe:
            dim = subprocess.check_output(
                [
                    self.ffprobe,
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "csv=s=x:p=0",
                    str(cover_file),
                ],
                text=True,
            ).strip()
            self.assertEqual(dim, "1080x1920")

    def test_python_render_cli_wrappers(self):
        """Verifies sys/render_cli.py and python -m sys.renderer interfaces."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        # 1. Test CLI help & argument parsing: python3 sys/render_cli.py --help
        cmd_cli = [sys.executable, str(ROOT / "render_cli.py"), "--help"]
        res_cli = subprocess.run(cmd_cli, cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(res_cli.returncode, 0, f"render_cli.py --help failed: {res_cli.stderr}")
        self.assertIn("--concurrency", res_cli.stdout)

        # 2. Test Module invocation E2E: python3 -m sys.renderer <work_dir> --concurrency 4
        cmd_mod = [sys.executable, "-m", "sys.renderer", str(FIXTURE_DIR), "--concurrency", "4"]
        res_mod = subprocess.run(cmd_mod, cwd=str(ROOT.parent), capture_output=True, text=True)
        self.assertEqual(res_mod.returncode, 0, f"python -m sys.renderer failed: {res_mod.stderr}")
        self.assertIn("Render successful", res_mod.stdout)

        # 3. Verify programmatic collect_outputs contract
        from sys.render_cli import collect_outputs, verify_inputs

        props = verify_inputs(FIXTURE_DIR)
        outputs = collect_outputs(FIXTURE_DIR, props)
        self.assertIn("video", outputs)
        self.assertIn("subtitles", outputs)
        self.assertIn("layout", outputs)
        self.assertIn("cover_tiktok_reels_9x16", outputs)

    def test_standalone_16x9_rendering_and_thumbnails(self):
        """Verifies 16:9 standalone render and thumbnail_youtube_16x9.png output."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir)
            pub_dir = work_dir / "public"
            pub_dir.mkdir(parents=True)

            # Copy sample assets into public/
            shutil.copy2(FIXTURE_DIR / "public" / "scene1.png", pub_dir / "scene1.png")
            shutil.copy2(FIXTURE_DIR / "public" / "narration.wav", pub_dir / "narration.wav")

            props_16x9 = {
                "aspect_ratio": "16:9",
                "duration": 2.0,
                "fps": 30,
                "width": 1920,
                "height": 1080,
                "audioSrc": "narration.wav",
                "scenes": [
                    {
                        "id": "SC_LAND",
                        "start": 0.0,
                        "end": 2.0,
                        "image": "scene1.png",
                        "title": "Landscape Scene",
                        "images": [{"src": "scene1.png", "at": 0.0, "shot_type": "full_scene", "effect": "zoom_in"}],
                    }
                ],
                "cues": [{"text": "Kiểm thử render tỷ lệ 16:9 độc lập.", "start": 0.0, "end": 1.8}],
                "thumbnail_spec": {"title": "BẢN DỰNG 16:9 ĐỘC LẬP", "badge": "HD YOUTUBE"},
            }

            (work_dir / "props.json").write_text(json.dumps(props_16x9, ensure_ascii=False, indent=2), encoding="utf-8")

            # Render 16:9 package
            from sys.render_cli import render_standalone

            outputs = render_standalone(work_dir, check_outputs=True)
            self.assertIn("video", outputs)
            self.assertIn("thumbnail_youtube_16x9", outputs)

            # Verify files
            self.assertTrue((work_dir / "video.mp4").is_file())
            self.assertTrue((work_dir / "video_16x9.mp4").is_file())
            self.assertTrue((work_dir / "subtitles.srt").is_file())
            self.assertTrue((work_dir / "layout.json").is_file())
            self.assertTrue((work_dir / "SC_LAND.png").is_file())

            thumb_yt = work_dir / "thumbnail_youtube_16x9.png"
            self.assertTrue(thumb_yt.is_file(), "thumbnail_youtube_16x9.png was not generated")
            self.assertGreater(thumb_yt.stat().st_size, 10000)

            if self.ffprobe:
                dim = subprocess.check_output(
                    [
                        self.ffprobe,
                        "-v",
                        "error",
                        "-select_streams",
                        "v:0",
                        "-show_entries",
                        "stream=width,height",
                        "-of",
                        "csv=s=x:p=0",
                        str(thumb_yt),
                    ],
                    text=True,
                ).strip()
                self.assertEqual(dim, "1920x1080")

    def test_render_cli_validation_and_errors(self):
        """Verifies validation and error handling in render_cli."""
        from sys.render_cli import verify_inputs

        # Non-existent dir
        with self.assertRaises(FileNotFoundError):
            verify_inputs(Path("/non/existent/path/xyz"))

        # Missing props.json
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                verify_inputs(Path(tmpdir))

            # Invalid props.json
            (Path(tmpdir) / "props.json").write_text("invalid json", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_inputs(Path(tmpdir))

    def test_default_multithreading_and_colab_t4_concurrency(self):
        """Verifies renderConcurrency Colab T4 GPU acceleration and runParallelPool multi-threading."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        script = """
import { renderConcurrency, runParallelPool } from './renderer/outputs.mjs';

// 1. Colab T4 environment: 2 vCPUs + GPU EGL enabled -> should NOT throttle to 2
delete process.env.VP_RENDER_CONCURRENCY;
const colabAuto = renderConcurrency(null, 2, true);
const colabRequested4 = renderConcurrency(4, 2, true);
const colabRequested8 = renderConcurrency(8, 2, true);

// 2. Environment variable override (VP_RENDER_CONCURRENCY)
process.env.VP_RENDER_CONCURRENCY = '6';
const envOverride = renderConcurrency(4, 2, false);
delete process.env.VP_RENDER_CONCURRENCY;

// 3. Explicit props.render_concurrency on 2-core container without GPU flag
const explicit4On2Cores = renderConcurrency(4, 2, false);

// 4. Parallel pool execution test
const activeCounts = [];
let currentActive = 0;
const items = [1, 2, 3, 4, 5, 6];
const results = await runParallelPool(items, 4, async (item) => {
  currentActive++;
  activeCounts.push(currentActive);
  await new Promise((r) => setTimeout(r, 40));
  currentActive--;
  return item * 10;
});

console.log(JSON.stringify({
  colabAuto,
  colabRequested4,
  colabRequested8,
  envOverride,
  explicit4On2Cores,
  maxActive: Math.max(...activeCounts),
  results
}));
"""
        res = subprocess.run(
            [self.node, "--input-type=module", "-e", script],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)
        self.assertEqual(data["colabAuto"], 6)
        self.assertEqual(data["colabRequested4"], 4)
        self.assertEqual(data["colabRequested8"], 8)
        self.assertEqual(data["envOverride"], 6)
        self.assertEqual(data["explicit4On2Cores"], 4)
        self.assertEqual(data["maxActive"], 4)
        self.assertEqual(data["results"], [10, 20, 30, 40, 50, 60])

    def test_dual_mode_parallel_rendering(self):
        """Verifies aspect_ratio='dual' renders both 9:16 and 16:9 videos, thumbnails, and stills in parallel."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir)
            pub_dir = work_dir / "public"
            pub_dir.mkdir(parents=True)

            shutil.copy2(FIXTURE_DIR / "public" / "scene1.png", pub_dir / "scene1.png")
            shutil.copy2(FIXTURE_DIR / "public" / "narration.wav", pub_dir / "narration.wav")

            props_dual = {
                "aspect_ratio": "dual",
                "render_concurrency": 4,
                "duration": 2.0,
                "fps": 30,
                "audioSrc": "narration.wav",
                "scenes": [
                    {
                        "id": "SC_DUAL_01",
                        "start": 0.0,
                        "end": 1.0,
                        "image": "scene1.png",
                        "images": [{"src": "scene1.png", "at": 0.0, "shot_type": "full_scene", "effect": "zoom_in"}],
                    },
                    {
                        "id": "SC_DUAL_02",
                        "start": 1.0,
                        "end": 2.0,
                        "image": "scene1.png",
                        "images": [{"src": "scene1.png", "at": 1.0, "shot_type": "full_scene", "effect": "pan_left"}],
                    },
                ],
                "cues": [
                    {"text": "Kiểm thử xuất bản kép.", "start": 0.0, "end": 0.9},
                    {"text": "Chạy đa luồng mặc định.", "start": 1.0, "end": 1.9},
                ],
                "thumbnail_spec": {"title": "XUẤT BẢN KÉP ĐA LUỒNG", "badge": "DUAL ENGINE"},
            }
            (work_dir / "props.json").write_text(json.dumps(props_dual, ensure_ascii=False, indent=2), encoding="utf-8")

            from sys.render_cli import render_standalone

            outputs = render_standalone(work_dir, concurrency=4, check_outputs=True)

            self.assertTrue((work_dir / "video.mp4").is_file())
            self.assertTrue((work_dir / "video_9x16.mp4").is_file())
            self.assertTrue((work_dir / "video_16x9.mp4").is_file())
            self.assertTrue((work_dir / "thumbnail_youtube_16x9.png").is_file())
            self.assertTrue((work_dir / "cover_tiktok_reels_9x16.png").is_file())
            self.assertTrue((work_dir / "SC_DUAL_01.png").is_file())
            self.assertTrue((work_dir / "SC_DUAL_02.png").is_file())
            self.assertIn("video_16x9", outputs)

            layout = json.loads((work_dir / "layout.json").read_text(encoding="utf-8"))
            self.assertTrue(layout.get("passed"))
            self.assertEqual(layout.get("execution_mode"), "multi_threaded_batch")
            self.assertGreaterEqual(layout.get("concurrency", 0), 4)

    def test_caption_text_overflow_safety_guard(self):
        """Verifies that batch DOM caption safety check catches overflowing cues and aborts rendering."""
        if not self.node:
            self.skipTest("Node.js runtime required")

        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir)
            pub_dir = work_dir / "public"
            pub_dir.mkdir(parents=True)

            shutil.copy2(FIXTURE_DIR / "public" / "scene1.png", pub_dir / "scene1.png")
            shutil.copy2(FIXTURE_DIR / "public" / "narration.wav", pub_dir / "narration.wav")

            # Unbreakable super-long token guaranteed to overflow the single-line/two-line caption box
            overflow_token = "SIÊU_CHUỖI_KHÔNG_NGẮT_DÒNG_" * 25
            props_overflow = {
                "aspect_ratio": "9:16",
                "duration": 2.0,
                "fps": 30,
                "audioSrc": "narration.wav",
                "scenes": [
                    {
                        "id": "SC_OVERFLOW",
                        "start": 0.0,
                        "end": 2.0,
                        "image": "scene1.png",
                        "images": [{"src": "scene1.png", "at": 0.0, "shot_type": "full_scene"}],
                    }
                ],
                "cues": [{"text": overflow_token, "start": 0.2, "end": 1.8}],
            }
            (work_dir / "props.json").write_text(
                json.dumps(props_overflow, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            cmd = [self.node, str(ROOT / "renderer" / "render.mjs"), str(work_dir)]
            res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

            self.assertNotEqual(res.returncode, 0, "Render should fail when caption overflows")
            self.assertIn("Text overflow", res.stderr + res.stdout)

            layout_file = work_dir / "layout.json"
            self.assertTrue(layout_file.is_file(), "layout.json must be written even on caption failure")
            layout = json.loads(layout_file.read_text(encoding="utf-8"))
            self.assertFalse(layout.get("passed"))
            self.assertGreater(len(layout.get("failures", [])), 0)
            self.assertFalse(
                (work_dir / "video.mp4").exists(), "video.mp4 should not be produced after caption overflow failure"
            )


if __name__ == "__main__":
    unittest.main()
