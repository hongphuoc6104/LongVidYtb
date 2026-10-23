"""Tests for Autonomous Image Generation Micro-Pipeline."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from flow_prompts import PromptError
from image_pipeline import run_autonomous_image_pipeline
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAutonomousImagePipeline(unittest.TestCase):
    def setUp(self):
        self.sample_content = {
            "schema_version": "3.0",
            "topic": "Học sâu và Tư duy phản biện",
            "aspect_ratio": "16:9",
            "style": "Minh hoạ biên tập 2D tối giản, văn phòng hiện đại",
            "characters": [
                {
                    "id": "CH01",
                    "name": "Nghiên cứu sinh",
                    "appearance": "Người que đầu tròn viền đen",
                    "outfit": "Áo sơ mi tối giản",
                }
            ],
            "scenes": [
                {
                    "id": "SC01",
                    "title": "Mở đầu",
                    "setting": "Bàn học lúc nửa đêm",
                    "action": "Ngồi đọc tài liệu nghiên cứu",
                    "purpose": "Nhận diện vấn đề",
                    "character_ids": ["CH01"],
                    "images": [
                        {
                            "id": "SC01_I1",
                            "description": "Bàn học lúc nửa đêm. Ngồi đọc tài liệu nghiên cứu.",
                            "based_on": None,
                            "shot_type": "full_scene",
                            "preserve": "",
                            "change": "Thiết lập cảnh ban đầu",
                            "character_ids": ["CH01"],
                            "visible_text": [],
                        }
                    ],
                },
                {
                    "id": "SC02",
                    "title": "Biến đổi",
                    "setting": "Bàn học lúc nửa đêm",
                    "action": "Ghi chú vào sổ tay",
                    "purpose": "Hành động giải pháp",
                    "character_ids": ["CH01"],
                    "images": [
                        {
                            "id": "SC02_I1",
                            "description": "Bàn học lúc nửa đêm. Ghi chú vào sổ tay.",
                            "based_on": "SC01_I1",
                            "shot_type": "variation",
                            "preserve": "Giữ nguyên góc máy bàn học và ánh đèn vàng ấm.",
                            "change": "Chuyển tay cầm bút ghi chú vào sổ.",
                            "character_ids": ["CH01"],
                            "visible_text": [],
                        }
                    ],
                },
            ],
        }

    def test_autonomous_pipeline_api_execution(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            result = run_autonomous_image_pipeline(
                content_input=self.sample_content,
                output_dir=out_dir,
                ratio="16:9",
                mock=True,
            )

            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["total_images"], 2)

            # 1. Standard images exist and have valid resolution
            for img_name in ("SC01.png", "SC01_I1.png", "SC02.png", "SC02_I1.png"):
                img_path = out_dir / img_name
                self.assertTrue(img_path.is_file(), f"Missing image: {img_name}")
                with Image.open(img_path) as im:
                    self.assertEqual(im.size, (1280, 720))

            # 2. Metadata sidecars exist and are valid JSON
            for sidecar_name in ("SC01.json", "SC01_I1.json", "SC02.json", "SC02_I1.json"):
                sidecar_path = out_dir / sidecar_name
                self.assertTrue(sidecar_path.is_file(), f"Missing sidecar: {sidecar_name}")
                sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
                self.assertIn("prompt", sidecar)
                self.assertIn("sha256", sidecar)
                self.assertEqual(sidecar["width"], 1280)
                self.assertEqual(sidecar["height"], 720)

            # 3. manifest.json
            manifest_path = out_dir / "manifest.json"
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["total_images"], 2)
            self.assertEqual(manifest["aspect_ratio"], "16:9")
            self.assertEqual(len(manifest["images"]), 2)

            # 4. budgets.json
            budgets_path = out_dir / "budgets.json"
            self.assertTrue(budgets_path.is_file())
            budgets = json.loads(budgets_path.read_text(encoding="utf-8"))
            self.assertEqual(budgets["total_images"], 2)
            self.assertEqual(budgets["status"], "completed")

    def test_autonomous_pipeline_cli_invocation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            content_file = tmp_path / "content.json"
            content_file.write_text(json.dumps(self.sample_content, ensure_ascii=False), encoding="utf-8")
            out_dir = tmp_path / "images_out"

            cmd = [
                sys.executable,
                "-m",
                "sys.image_pipeline",
                "--content",
                str(content_file),
                "--out",
                str(out_dir),
                "--ratio",
                "16:9",
                "--mock",
            ]
            res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"CLI invocation failed: {res.stderr}\n{res.stdout}")
            self.assertIn("Successfully generated 2 images", res.stdout)
            self.assertTrue((out_dir / "manifest.json").is_file())
            self.assertTrue((out_dir / "budgets.json").is_file())
            self.assertTrue((out_dir / "SC01.png").is_file())
            self.assertTrue((out_dir / "SC02.png").is_file())

    def test_early_visual_cliche_gate_rejection(self):
        bad_content = json.loads(json.dumps(self.sample_content))
        bad_content["scenes"][0]["setting"] = "Phòng làm việc với màn hình chia đôi split screen"

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            with self.assertRaises(PromptError) as ctx:
                run_autonomous_image_pipeline(bad_content, out_dir, mock=True)
            self.assertIn("FLOW_CLICHE_FORBIDDEN", str(ctx.exception))
            self.assertIn("split screen", str(ctx.exception).lower())

    def test_aspect_ratio_9x16_resolution(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            result = run_autonomous_image_pipeline(
                content_input=self.sample_content,
                output_dir=out_dir,
                ratio="9:16",
                mock=True,
            )
            self.assertEqual(result["status"], "completed")
            with Image.open(out_dir / "SC01.png") as im:
                self.assertEqual(im.size, (720, 1280))

    def test_dag_dependency_chain_in_sidecars(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            run_autonomous_image_pipeline(
                content_input=self.sample_content,
                output_dir=out_dir,
                ratio="16:9",
                mock=True,
            )
            sc02_sidecar = json.loads((out_dir / "SC02_I1.json").read_text(encoding="utf-8"))
            self.assertEqual(sc02_sidecar["based_on"], "SC01_I1")
            self.assertEqual(sc02_sidecar["shot_type"], "variation")
            self.assertIn("A Base scene reference is declared", sc02_sidecar["prompt"])

    def test_scenes_visual_spec_and_directory_input(self):
        """Verify R2 compliance: content with scenes[].visual format loaded from a directory."""
        visual_content = {
            "schema_version": "3.0",
            "topic": "Nghiên cứu khoa học và Trực giác",
            "aspect_ratio": "16:9",
            "scenes": [
                {
                    "id": "SC01",
                    "shot_type": "full_scene",
                    "visual": {
                        "setting": "Phòng nghiên cứu sinh học chuẩn",
                        "action": "Nhà khoa học kiểm tra kính hiển vi",
                        "preserve": "",
                        "change": "",
                        "camera": "eye_level_static",
                    },
                },
                {
                    "id": "SC02",
                    "shot_type": "variation",
                    "based_on": "SC01",
                    "visual": {
                        "setting": "Phòng nghiên cứu sinh học chuẩn",
                        "action": "Nhà khoa học ghi chép kết quả thí nghiệm",
                        "preserve": "Giữ nguyên bàn kính hiển vi và áo blouse trắng.",
                        "change": "Cầm bút ghi chép kết quả vào sổ thực nghiệm.",
                        "camera": "medium_close_up",
                    },
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            blueprint_dir = Path(tmp_dir) / "blueprint"
            blueprint_dir.mkdir()
            (blueprint_dir / "content.json").write_text(
                json.dumps(visual_content, ensure_ascii=False), encoding="utf-8"
            )
            out_dir = Path(tmp_dir) / "images_out"

            # Pass the directory path as content_input
            result = run_autonomous_image_pipeline(
                content_input=blueprint_dir,
                output_dir=out_dir,
                ratio="16:9",
                mock=True,
            )
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["total_images"], 2)

            # SC01 and SC02 files created
            self.assertTrue((out_dir / "SC01.png").is_file())
            self.assertTrue((out_dir / "SC02.png").is_file())

            # SC02 sidecar properly links based_on SC01 and preserves visual contract
            sc02_sidecar = json.loads((out_dir / "SC02.json").read_text(encoding="utf-8"))
            self.assertEqual(sc02_sidecar["based_on"], "SC01")
            self.assertEqual(sc02_sidecar["shot_type"], "variation")
            self.assertIn("A Base scene reference is declared", sc02_sidecar["prompt"])

    def test_visual_field_cliche_gate_rejection(self):
        """Verify clichés inside scenes[].visual fields (setting, action, change) are blocked."""
        bad_visual_content = {
            "schema_version": "3.0",
            "topic": "Thử nghiệm cliché",
            "aspect_ratio": "16:9",
            "scenes": [
                {
                    "id": "SC01",
                    "visual": {
                        "setting": "Phòng thực nghiệm với pipe valve áp suất cao",
                        "action": "Thao tác van áp",
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            with self.assertRaises(PromptError) as ctx:
                run_autonomous_image_pipeline(bad_visual_content, out_dir, mock=True)
            self.assertIn("FLOW_CLICHE_FORBIDDEN", str(ctx.exception))
            self.assertIn("pipe valve", str(ctx.exception).lower())

    def test_mock_false_dispatches_to_flow_cdp_batch(self):
        """Verify that when mock=False, the pipeline dispatches to flow_cdp.bridge.generate_cdp_batch."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            dummy_img = Path(tmp_dir) / "dummy.png"
            Image.new("RGB", (1280, 720)).save(dummy_img)

            fake_results = [
                {
                    "request_id": "SC01_I1",
                    "path": str(dummy_img),
                    "sha256": "abcdef1234567890",
                    "media_id": "forge-media-001",
                },
                {
                    "request_id": "SC02_I1",
                    "path": str(dummy_img),
                    "sha256": "abcdef1234567891",
                    "media_id": "forge-media-002",
                },
            ]

            with patch("flow_cdp.bridge.generate_cdp_batch", side_effect=[[fake_results[0]], [fake_results[1]]]) as mock_batch:
                res = run_autonomous_image_pipeline(
                    content_input=self.sample_content,
                    output_dir=out_dir,
                    ratio="16:9",
                    mock=False,
                )
                self.assertEqual(res["status"], "completed")
                self.assertEqual(mock_batch.call_count, 2)
                # Verify 5-tier rampup timeout was passed (120.0s for 2 images)
                self.assertEqual(mock_batch.call_args.kwargs.get("timeout"), 120.0)
                # Verify sidecar contains the media_id returned from CDP
                sc01_sidecar = json.loads((out_dir / "SC01.json").read_text(encoding="utf-8"))
                self.assertEqual(sc01_sidecar["media_id"], "forge-media-001")

    def test_default_watermark_healing_invoked_on_images(self):
        """Verify Requirement R4: apply_editorial_overlay is invoked by default on downloaded images."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output"
            with patch("tools.editorial_compositor.apply_editorial_overlay") as mock_heal:
                res = run_autonomous_image_pipeline(
                    content_input=self.sample_content,
                    output_dir=out_dir,
                    ratio="16:9",
                    mock=True,
                )
                self.assertEqual(res["status"], "completed")
                # Both generated images should have watermark healing applied
                self.assertEqual(mock_heal.call_count, 2)
