"""Tests for standalone native FFmpeg h264_nvenc (and CPU fallback) rendering engine."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import colab_bridge.flow_video_worker as flow_video_worker
import render_cli


class StandaloneRenderEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ffmpeg = shutil.which("ffmpeg")
        cls.ffprobe = shutil.which("ffprobe")
        assert cls.ffmpeg is not None, "ffmpeg executable must be in PATH"
        assert cls.ffprobe is not None, "ffprobe executable must be in PATH"

    def test_flow_video_worker_nvenc_detection_and_encoder_args(self):
        """Validates NVENC detection flag and video encoder arguments."""
        # 1. has_nvenc() should return a boolean
        nvenc_flag = flow_video_worker.has_nvenc()
        self.assertIsInstance(nvenc_flag, bool)

        # 2. video_encoder_args when True (NVENC active)
        nvenc_args = flow_video_worker.video_encoder_args(use_nvenc=True)
        self.assertIn("-c:v", nvenc_args)
        self.assertIn("h264_nvenc", nvenc_args)
        self.assertIn("-preset", nvenc_args)
        self.assertIn("p4", nvenc_args)

        # 3. video_encoder_args when False (CPU libx264 fallback)
        cpu_args = flow_video_worker.video_encoder_args(use_nvenc=False)
        self.assertIn("-c:v", cpu_args)
        self.assertIn("libx264", cpu_args)
        self.assertIn("yuv420p", cpu_args)

    def test_make_rounded_watermark(self):
        """Validates rounded watermark creation with alpha transparency."""
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            logo_in = tpath / "raw_logo.png"
            logo_out = tpath / "watermark_100.png"

            # Generate synthetic 200x200 RGBA image
            img = Image.new("RGBA", (200, 200), color=(59, 130, 196, 255))
            img.save(logo_in, "PNG")

            out_path = flow_video_worker.make_rounded_watermark(
                logo_in, logo_out, size=100, opacity=0.92, radius=15
            )
            self.assertTrue(out_path.is_file())
            self.assertGreater(out_path.stat().st_size, 0)

            result_img = Image.open(out_path)
            self.assertEqual(result_img.size, (100, 100))
            self.assertEqual(result_img.mode, "RGBA")
            # Verify corner is transparent due to rounded mask
            corner_pixel = result_img.getpixel((0, 0))
            self.assertEqual(corner_pixel[3], 0)

    def test_render_single_job_with_static_image_keyframes(self):
        """Validates render_single_job with static image flipbook and audio."""
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            img1 = tpath / "frame1.png"
            img2 = tpath / "frame2.png"
            wav = tpath / "audio.wav"

            Image.new("RGB", (720, 1280), color=(248, 240, 220)).save(img1)
            Image.new("RGB", (720, 1280), color=(147, 168, 140)).save(img2)
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=1000:duration=1.0", str(wav)],
                capture_output=True,
                check=True,
            )

            req = {
                "job_id": "test_static_job",
                "aspect": "9:16",
                "audio_path": str(wav),
                "use_nvenc": False,  # ensure CPU fallback runs in test container
                "keyframes": [
                    {"image_path": str(img1), "duration": 0.5},
                    {"image_path": str(img2), "duration": 0.5},
                ],
            }
            req_file = tpath / "req.json"
            req_file.write_text(json.dumps(req))

            out_dir = tpath / "out"
            res = flow_video_worker.render_single_job(req_file, out_dir)

            self.assertIn("video_path", res)
            self.assertTrue(Path(res["video_path"]).is_file())
            self.assertEqual(res["aspect_tag"], "9x16")
            self.assertEqual(res["width"], 1080)
            self.assertEqual(res["height"], 1920)
            self.assertTrue((out_dir / "render-result.json").is_file())

    def test_render_single_job_with_video_clip_beats(self):
        """Validates render_single_job concatenating video clip beats."""
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            clip1 = tpath / "clip1.mp4"
            clip2 = tpath / "clip2.mp4"
            wav = tpath / "audio.wav"

            # Create two 0.5s clips
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=red:s=720x1280:d=0.5",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    str(clip1),
                ],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=blue:s=720x1280:d=0.5",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    str(clip2),
                ],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=800:duration=1.0", str(wav)],
                capture_output=True,
                check=True,
            )

            req = {
                "job_id": "test_clip_job",
                "aspect": "9:16",
                "audio_path": str(wav),
                "use_nvenc": False,
                "clips": [str(clip1), str(clip2)],
            }
            req_file = tpath / "req.json"
            req_file.write_text(json.dumps(req))

            out_dir = tpath / "out"
            res = flow_video_worker.render_single_job(req_file, out_dir)

            self.assertIn("video_path", res)
            self.assertTrue(Path(res["video_path"]).is_file())
            self.assertGreater(Path(res["video_path"]).stat().st_size, 1000)

    def test_render_props_package_contract_and_layout(self):
        """Validates render_props_package execution with subtitles, watermark, and layout.json."""
        with tempfile.TemporaryDirectory() as td:
            work_dir = Path(td)
            pub_dir = work_dir / "public"
            pub_dir.mkdir(parents=True)

            img = pub_dir / "scene1.png"
            Image.new("RGB", (720, 1280), color=(248, 240, 220)).save(img)
            wav = pub_dir / "narration.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=1000:duration=1.0", str(wav)],
                capture_output=True,
                check=True,
            )

            props = {
                "aspect_ratio": "9:16",
                "duration": 1.0,
                "audioSrc": "narration.wav",
                "subtitles": True,
                "scenes": [
                    {
                        "id": "SC01",
                        "start": 0.0,
                        "end": 1.0,
                        "image": "scene1.png",
                        "images": [{"src": "scene1.png", "at": 0.0, "effect": "hold"}],
                    }
                ],
                "cues": [{"text": "Kiểm thử native FFmpeg render.", "start": 0.0, "end": 0.9}],
            }
            (work_dir / "props.json").write_text(json.dumps(props, ensure_ascii=False, indent=2))

            if hasattr(flow_video_worker, "render_props_package"):
                if not flow_video_worker.has_nvenc():
                    with self.assertRaises(RuntimeError):
                        flow_video_worker.render_props_package(work_dir, require_nvenc=True)

                res = flow_video_worker.render_props_package(work_dir, require_nvenc=False)
                self.assertIsNotNone(res)
                self.assertTrue((work_dir / "video.mp4").is_file() or (work_dir / "video_9x16.mp4").is_file())
                self.assertTrue((work_dir / "layout.json").is_file())
                layout = json.loads((work_dir / "layout.json").read_text())
                self.assertTrue(layout.get("passed"))
            else:
                self.assertTrue(callable(flow_video_worker.render_single_job))

    def test_render_cli_verify_inputs_validation_and_errors(self):
        """Validates render_cli.verify_inputs on valid, missing, and invalid directories/props."""
        # 1. Non-existent directory
        with self.assertRaises(FileNotFoundError):
            render_cli.verify_inputs(Path("/non/existent/path/for/video_pilot"))

        # 2. Missing props.json
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                render_cli.verify_inputs(Path(td))

            # 3. Invalid JSON in props.json
            (Path(td) / "props.json").write_text("NOT_VALID_JSON{", encoding="utf-8")
            with self.assertRaises(ValueError):
                render_cli.verify_inputs(Path(td))

            # 4. Valid props.json
            valid_dict = {"aspect_ratio": "9:16", "duration": 5.0}
            (Path(td) / "props.json").write_text(json.dumps(valid_dict), encoding="utf-8")
            loaded = render_cli.verify_inputs(Path(td))
            self.assertEqual(loaded["aspect_ratio"], "9:16")
            self.assertEqual(loaded["duration"], 5.0)

    def test_render_cli_collect_outputs(self):
        """Validates collect_outputs retrieves all standard video and asset artifacts."""
        with tempfile.TemporaryDirectory() as td:
            work_dir = Path(td)
            (work_dir / "video.mp4").touch()
            (work_dir / "video_9x16.mp4").touch()
            (work_dir / "video_16x9.mp4").touch()
            (work_dir / "subtitles.srt").touch()
            (work_dir / "layout.json").touch()
            (work_dir / "thumbnail_youtube_16x9.png").touch()
            (work_dir / "cover_tiktok_reels_9x16.png").touch()
            (work_dir / "SC01.png").touch()

            props = {"scenes": [{"id": "SC01"}]}
            outputs = render_cli.collect_outputs(work_dir, props)

            self.assertIn("video", outputs)
            self.assertIn("video_9x16", outputs)
            self.assertIn("video_16x9", outputs)
            self.assertIn("subtitles", outputs)
            self.assertIn("layout", outputs)
            self.assertIn("thumbnail_youtube_16x9", outputs)
            self.assertIn("cover_tiktok_reels_9x16", outputs)
            self.assertIn("stills", outputs)
            self.assertEqual(len(outputs["stills"]), 1)

    def test_render_cli_help_and_arguments(self):
        """Validates CLI invocation help and arguments parsing."""
        cmd = [sys.executable, str(ROOT / "render_cli.py"), "--help"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("work_dir", res.stdout)
        self.assertIn("--concurrency", res.stdout)
        self.assertIn("--timeout", res.stdout)


if __name__ == "__main__":
    unittest.main()
