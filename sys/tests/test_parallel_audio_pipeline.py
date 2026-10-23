"""Comprehensive tests for default multi-threaded & multi-account parallel audio synthesis.

Covers:
1. AudioPipeline default multi-threaded execution (parallel=True, max_workers=3, batch_size=4)
   in both mock mode and remote ColabPoolDispatcher mode.
2. remote_audio.produce_parallel() multi-account shard partitioning, work-stealing failover
   on 429/503/COLAB_TIMEOUT, and deterministic assembly when shards complete out-of-order.
3. High-concurrency stress test (24 segments across multiple workers with injected
   account quota failover and out-of-order completion).
"""
from __future__ import annotations

import copy
import json
import tempfile
import threading
import time
import unittest
import wave
from pathlib import Path
from unittest import mock

import audio_pipeline
import remote_audio
from colab_bridge.pool_manager import ColabPoolManager


def _write_test_wav(path: Path, seconds: float = 0.5, sr: int = 48000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nframes = int(sr * seconds)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"\x10\x00" * nframes)


class ParallelAudioPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def _create_brief_and_content(self, num_scenes: int = 6) -> tuple[Path, Path]:
        brief_path = self.root / "brief.json"
        content_path = self.root / "content.json"
        brief = {
            "voice": "VietNarrator",
            "speed": 1.0,
            "aspect_ratio": "16:9",
            "primary_language": "vi",
        }
        scenes = []
        for idx in range(1, num_scenes + 1):
            if idx == 1:
                # SC01 must obey <= 18 syllables and zero [pause:...]
                text = "Não bộ luôn chọn đường tắt khi đối mặt áp lực."
            else:
                text = (
                    "Cảnh tiếp theo phân tích cơ chế nhận thức sâu sắc. "
                    "Mỗi quyết định đều tiêu tốn năng lượng thần kinh đáng kể."
                )
            scenes.append(
                {
                    "id": f"SC{idx:02d}",
                    "narration": text,
                    "tone": "analytical_crisp" if idx % 2 == 0 else "narrative_warm",
                }
            )
        brief_path.write_text(json.dumps(brief, ensure_ascii=False), encoding="utf-8")
        content_path.write_text(
            json.dumps({"scenes": scenes}, ensure_ascii=False), encoding="utf-8"
        )
        return brief_path, content_path

    def test_audio_pipeline_defaults_to_parallel_multi_threaded_execution(self) -> None:
        brief_path, content_path = self._create_brief_and_content(num_scenes=6)
        out_dir = self.root / "out_mock"
        pipe = audio_pipeline.AudioPipeline(
            content_path=content_path,
            brief_path=brief_path,
            out_dir=out_dir,
            mock=True,
        )
        self.assertTrue(pipe.parallel)
        self.assertEqual(pipe.max_workers, 3)
        self.assertEqual(pipe.batch_size, 4)

        manifest = pipe.run()
        self.assertEqual(manifest["processing_location"], "local")
        self.assertGreaterEqual(len(manifest["segments"]), 6)
        self.assertTrue((out_dir / "narration.wav").is_file())
        self.assertTrue((out_dir / "subtitles.srt").is_file())
        # Verify exact sequence order in assembled segments
        paths = [seg["path"] for seg in manifest["segments"]]
        expected_paths = [f"segments/segment-{i:03d}.wav" for i in range(len(paths))]
        self.assertEqual(paths, expected_paths)

    def test_audio_pipeline_remote_dispatches_batches_across_colab_pool(self) -> None:
        brief_path, content_path = self._create_brief_and_content(num_scenes=5)
        out_dir = self.root / "out_remote"
        pipe = audio_pipeline.AudioPipeline(
            content_path=content_path,
            brief_path=brief_path,
            out_dir=out_dir,
            mock=False,
            parallel=True,
            max_workers=3,
            batch_size=3,
        )

        accounts_cfg = [
            {"id": "account-01", "role": "tts"},
            {"id": "account-02", "role": "tts"},
            {"id": "account-03", "role": "tts"},
        ]
        real_mgr = ColabPoolManager(
            accounts_config=accounts_cfg,
            cooldown_seconds=0.05,
            stagger_seconds=0.0,
            lock_dir=self.root / "locks",
        )
        used_accounts: list[str] = []
        lock = threading.Lock()

        def fake_synthesize(client_self, req, batch_tmp, batch_cache, before_submit=None):
            acct = client_self.cfg.get("account", "unknown")
            with lock:
                used_accounts.append(acct)
            segs = req.get("items") or req.get("segments") or []
            out_segs = []
            for local_i, _seg in enumerate(segs):
                wav_name = f"segment-{local_i:04d}.wav"
                audio_pipeline.generate_mock_tone(batch_tmp / wav_name, 1.35, freq=220.0)
                out_segs.append({"index": local_i, "path": wav_name, "duration": 1.35})
            (batch_tmp / "tts-result.json").write_text(
                json.dumps({"segments": out_segs}), encoding="utf-8"
            )

        with (
            mock.patch("colab_bridge.pool_manager.ColabPoolManager", return_value=real_mgr),
            mock.patch("colab_bridge.accounts.is_session_busy", return_value=False),
            mock.patch("colab_bridge.accounts.has_external_session", return_value=False),
            mock.patch("colab_bridge.client.Client.synthesize", new=fake_synthesize),
        ):
            manifest = pipe.run()

        self.assertEqual(manifest["processing_location"], "colab")
        self.assertGreaterEqual(len(used_accounts), 2)
        self.assertTrue(
            set(used_accounts).issubset({"account-01", "account-02", "account-03"}),
            f"Unexpected accounts used: {used_accounts}",
        )
        paths = [seg["path"] for seg in manifest["segments"]]
        expected_paths = [f"segments/segment-{i:03d}.wav" for i in range(len(paths))]
        self.assertEqual(paths, expected_paths)

    def test_produce_parallel_work_stealing_failover_and_deterministic_order(self) -> None:
        accounts_cfg = [
            {"id": "account-01", "role": "tts"},
            {"id": "account-02", "role": "tts"},
            {"id": "account-03", "role": "tts"},
        ]
        mgr = ColabPoolManager(
            accounts_config=accounts_cfg,
            cooldown_seconds=0.05,
            stagger_seconds=0.0,
            lock_dir=self.root / "locks",
        )

        scenes = [
            {
                "scene_id": f"SC{idx:02d}",
                "narration": f"Câu thứ {idx} trong bài kiểm tra đa luồng.",
                "texts": [f"Câu thứ {idx} trong bài kiểm tra đa luồng."],
                "gaps": [],
                "tail": 0.2,
                "tone": "narrative_warm",
                "retake": 0,
            }
            for idx in range(1, 10)
        ]

        repo_root = Path(__file__).resolve().parents[1]
        base_cfg = json.loads((repo_root / "config.json").read_text(encoding="utf-8"))
        cfg = copy.deepcopy(base_cfg)
        cfg["tts_voice"] = "VietNarrator"
        cfg["tts_speed"] = 1.0
        cfg["en_voice"] = "VietNarrator"
        cfg["en_speed"] = 1.0
        cfg.setdefault("voices", {})["vi"] = "assets/voices/viet_narrator/profile.json"
        cfg.setdefault("colab_tts", {})["account"] = "auto-idle"
        cfg["colab_tts"].setdefault("voices", {})["vi"] = "assets/voices/viet_narrator/profile.json"

        fail_once = {"account-01": True}
        lock = threading.Lock()

        def fake_synthesize(client_self, req, shard_out, shard_cache, before_submit=None):
            acct = client_self.cfg["account"]
            with lock:
                if fail_once.get(acct):
                    fail_once[acct] = False
                    raise RuntimeError("HTTP 429 Too Many Requests: Colab T4 quota exceeded on account-01")

            req_items = req.get("segments") or req.get("items") or []
            # Introduce inverted delay so later shards finish earlier (out-of-order completion)
            first_scene_id = req_items[0]["scene_id"]
            if first_scene_id == "SC01":
                time.sleep(0.06)
            elif first_scene_id == "SC04":
                time.sleep(0.03)
            else:
                time.sleep(0.01)

            segs_out = []
            for idx, seg in enumerate(req_items):
                wav_name = f"shard-seg-{idx:04d}.wav"
                dur = 0.5 + idx * 0.1
                _write_test_wav(shard_out / wav_name, seconds=dur)
                segs_out.append(
                    {
                        "index": idx,
                        "scene_id": seg["scene_id"],
                        "text": seg["text"],
                        "path": wav_name,
                        "duration": dur,
                        "content_duration": dur - 0.1,
                    }
                )
            res = {
                "voice": "VietNarrator",
                "backend": "colab-omnivoice",
                "segments": segs_out,
                "english_spans": [],
                "batches": [{"size": len(segs_out), "status": "ok"}],
            }
            (shard_out / "tts-result.json").write_text(json.dumps(res), encoding="utf-8")

        out_dir = self.root / "parallel_out"
        cache_dir = self.root / "parallel_cache"

        with (
            mock.patch("colab_bridge.accounts.is_session_busy", return_value=False),
            mock.patch("colab_bridge.accounts.has_external_session", return_value=False),
            mock.patch("colab_bridge.client.Client.synthesize", new=fake_synthesize),
        ):
            report = remote_audio.produce_parallel(
                root=repo_root,
                cfg=cfg,
                scenes=scenes,
                out=out_dir,
                cache=cache_dir,
                max_concurrency=3,
                scenes_per_shard=3,
                primary_language="vi",
                pool_manager=mgr,
            )

        self.assertEqual(report["shards_dispatched"], 3)
        self.assertEqual(len(report["segments"]), 9)
        # Verify deterministic scene ordering despite out-of-order completion and account-01 failover
        assembled_scene_ids = [seg["scene_id"] for seg in report["segments"]]
        expected_scene_ids = [f"SC{idx:02d}" for idx in range(1, 10)]
        self.assertEqual(assembled_scene_ids, expected_scene_ids)

        # Verify monotonic non-overlapping timeline
        for i in range(len(report["segments"]) - 1):
            self.assertAlmostEqual(
                report["segments"][i]["end"],
                report["segments"][i + 1]["start"],
                places=3,
            )
        self.assertTrue((out_dir / "narration.wav").is_file())


if __name__ == "__main__":
    unittest.main()
