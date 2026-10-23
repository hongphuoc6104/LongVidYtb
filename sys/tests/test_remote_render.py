"""Remote boundaries; fixtures are not live Colab/MP4 proof."""

import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(Path(p).read_text())


def write(p, x):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(x, ensure_ascii=False, indent=2))
    tmp.replace(p)


class Blocked(Exception):
    pass


from colab_bridge.client import Client, ColabError
from colab_bridge.job_protocol import build_render_request, bundle, extract, validate_render_result
from colab_bridge.protocol import file_hash


def result(folder, req):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "video.mp4").write_bytes(b"\0\0\0\x18ftypisom" + b"fixture")
    write(folder / "layout.json", {"passed": True})
    write(folder / "editorial-audit.json", {"quality_approval": False})
    plans = req["brief"]["outputs"]
    write(
        folder / "props.json",
        {
            "outputs": plans,
            "aspect_ratio": req["brief"]["aspect_ratio"],
            "primary_language": plans[0]["language"],
            "tracks": {
                lang: {
                    "audioSrc": lang + ".wav",
                    "duration": req["audio"]["tracks"][lang]["duration"],
                    "cues": [],
                    "scenesByAspect": {plan["aspect_ratio"]: [] for plan in plans if plan["language"] == lang},
                }
                for lang in dict.fromkeys(plan["language"] for plan in plans)
            },
        },
    )
    report = {
        "request_id": req["request_id"],
        "operation": "render",
        "processing_location": "colab",
        "device": "fixture Tesla T4",
        "outputs": [
            dict(
                req["brief"]["outputs"][0],
                file="video.mp4",
                width=1080,
                height=1920,
                duration=5.0,
                video_codec="h264",
                audio_codec="aac",
            )
        ],
        "files": {p.name: {"sha256": file_hash(p), "size": p.stat().st_size} for p in folder.iterdir()},
    }
    write(folder / "render-result.json", report)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cfg = read(ROOT / "config.json")
        self.brief = {
            "aspect_ratio": "9:16",
            "outputs": [
                {"aspect_ratio": "9:16", "language": "en", "subtitles": True, "voice": "VietNarrator", "speed": 1.0}
            ],
        }
        (self.root / "image.png").write_bytes(b"imagefixture")
        (self.root / "en.wav").write_bytes(b"audiofixture")
        self.images = {"items": [{"scene_id": "SC01", "image_id": "IM01", "ratio": "9:16", "path": "image.png"}]}
        self.audio = {
            "wav": "en.wav",
            "language": "en",
            "tracks": {"en": {"wav": "en.wav", "duration": 5.0, "segments": []}},
        }
        self.req = build_render_request(
            ROOT, self.brief, {"scenes": []}, self.images, self.audio, lambda x: self.root / x
        )
        with patch("colab_bridge.client.cli", return_value="/bin/true"):
            self.client = Client(self.root, self.cfg)
        self.client.account = None
        self.client.cfg["management_store"] = str(self.root / "management")
        self.addCleanup(patch.stopall)
        patch.object(self.client, "_ready").start()
        patch.object(self.client, "_reserve").start()
        patch.object(self.client, "_settle").start()

    def test_bundle_keeps_fixed_sources_and_referenced_assets(self):
        write(self.root / "token.json", {"secret": "not-uploaded"})
        target = self.root / "input.zip"
        bundle(self.req, target)
        with zipfile.ZipFile(target) as z:
            self.assertNotIn("token.json", z.namelist())
            manifest = json.loads(z.read("request.json"))
            self.assertTrue(all("local_path" not in x for x in manifest["files"]))
            self.assertEqual(manifest["brief"]["outputs"][0]["speed"], 1.0)
            self.assertIn("source/renderer/outputs.mjs", z.namelist())
            self.assertIn("source/renderer/srt.mjs", z.namelist())
            self.assertEqual(z.read("source/renderer/captions.mjs"), (ROOT / "renderer/captions.mjs").read_bytes())
            self.assertEqual(z.read("source/renderer/srt.mjs"), (ROOT / "renderer/srt.mjs").read_bytes())
            self.assertEqual(z.read("source/renderer/index.tsx"), (ROOT / "renderer/index.tsx").read_bytes())
        (self.root / "image.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed"):
            bundle(self.req, self.root / "changed.zip")

    def test_wrong_stream_contract_hash_duration_rejected(self):
        for key, value in [("language", "vi"), ("width", 1920), ("duration", 20.0), ("audio_codec", "none")]:
            folder = self.root / key
            result(folder, self.req)
            meta = read(folder / "render-result.json")
            meta["outputs"][0][key] = value
            write(folder / "render-result.json", meta)
            with self.assertRaises(ValueError):
                validate_render_result(folder, self.req)
        folder = self.root / "valid"
        result(folder, self.req)
        validate_render_result(folder, self.req)
        (folder / "video.mp4").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed"):
            validate_render_result(folder, self.req)

    def test_rehashed_wrong_render_props_are_rejected(self):
        for defect in ("primary", "extra_track", "audio", "duration", "captions", "aspect"):
            folder = self.root / defect
            result(folder, self.req)
            props = read(folder / "props.json")
            if defect == "primary":
                props["primary_language"] = "vi"
            elif defect == "extra_track":
                props["tracks"]["vi"] = props["tracks"]["en"]
            elif defect == "audio":
                props["tracks"]["en"]["audioSrc"] = "vi.wav"
            elif defect == "duration":
                props["tracks"]["en"]["duration"] = 1.0
            elif defect == "captions":
                props["tracks"]["en"]["cues"] = [{"text": "Wrong narration", "start": 0, "end": 1}]
            else:
                props["tracks"]["en"]["scenesByAspect"] = {"16:9": []}
            write(folder / "props.json", props)
            report = read(folder / "render-result.json")
            report["files"]["props.json"] = {
                "size": (folder / "props.json").stat().st_size,
                "sha256": file_hash(folder / "props.json"),
            }
            write(folder / "render-result.json", report)
            with self.subTest(defect=defect):
                with self.assertRaisesRegex(ValueError, "props"):
                    validate_render_result(folder, self.req)

    def test_zip_traversal_bounds_rejected(self):
        for name in ("../escape", "/escape", "a\\escape"):
            archive = self.root / "bad.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr(name, b"x")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                extract(archive, self.root / "extract")
        with zipfile.ZipFile(self.root / "large.zip", "w") as z:
            z.writestr("file", b"12345")
        with self.assertRaisesRegex(ValueError, "bounds"):
            extract(self.root / "large.zip", self.root / "extract", limit=4)

    def test_timeout_pins_original_session_only_collects(self):
        calls = []
        self.client.session = "original-session"

        def call(*args, **kwargs):
            calls.append(args)
            if args[0] == "exec" and "m.run(" in kwargs.get("code", ""):
                raise ColabError("COLAB_TIMEOUT")
            if args[0] == "download":
                raise ColabError("not available")
            m = re.search(r"VP_EXEC_OK_[0-9a-f]+", kwargs.get("code", ""))
            return m.group() if m else ""

        with patch.object(self.client, "ensure_authenticated"), patch.object(self.client, "call", side_effect=call):
            with self.assertRaisesRegex(ColabError, "TIMEOUT"):
                self.client.render(self.req, self.root / "out", self.root / "cache")
            self.client.session = "new-default"
            calls.clear()
            with self.assertRaisesRegex(ColabError, "not available"):
                self.client.render(
                    self.req,
                    self.root / "out",
                    self.root / "cache",
                    before_submit=lambda: self.fail("Stopped collection must not submit"),
                )
            self.assertEqual(self.client.session, "original-session")
            self.assertEqual([c[0] for c in calls], ["download"])

    def test_stop_blocks_execution_cache_never_submits(self):
        with patch.object(self.client, "ensure_authenticated"), patch.object(self.client, "call") as call:
            with self.assertRaisesRegex(Blocked, "stopped"):
                self.client.render(
                    self.req,
                    self.root / "out",
                    self.root / "cache",
                    before_submit=lambda: (_ for _ in ()).throw(Blocked("stopped")),
                )
            call.assert_not_called()
        result(self.root / "cache" / self.req["request_id"] / "result", self.req)
        with patch.object(self.client, "call") as call:
            self.client.render(
                self.req, self.root / "out", self.root / "cache", before_submit=lambda: self.fail("No submit on cache")
            )
            call.assert_not_called()
            self.assertTrue((self.root / "out/video.mp4").exists())

    def test_collection_recovery_has_durable_limit(self):
        cache = self.root / "cache"
        folder = cache / self.req["request_id"]
        folder.mkdir(parents=True)
        write(
            folder / "state.json",
            {
                "phase": "ambiguous",
                "account": None,
                "session": "old",
                "remote": "/remote",
                "request_id": self.req["request_id"],
            },
        )
        with (
            patch.object(self.client, "ensure_authenticated"),
            patch.object(self.client, "call", side_effect=ColabError("download unavailable")) as call,
        ):
            for _ in range(3):
                with self.assertRaisesRegex(ColabError, "download unavailable"):
                    self.client.render(self.req, self.root / "out", cache)
            with self.assertRaisesRegex(ColabError, "RECOVERY_LIMIT"):
                self.client.render(self.req, self.root / "out", cache)
            self.assertEqual(call.call_count, 3)
        self.assertEqual(read(folder / "state.json")["collection_attempts"], 3)


if __name__ == "__main__":
    unittest.main()


class WorkerRoutingTests(unittest.TestCase):
    def test_worker_prepares_english_portrait_timeline_captions_and_stream_manifest(self):
        from colab_bridge.job_worker import run

        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "image.png").write_bytes(b"fixture")
            (folder / "audio.wav").write_bytes(b"fixture")
            brief = {
                "aspect_ratio": "9:16",
                "outputs": [
                    {"aspect_ratio": "9:16", "language": "en", "subtitles": True, "voice": "VietNarrator", "speed": 1.0}
                ],
            }
            content = {
                "schema_version": "3.0",
                "scenes": [
                    {
                        "id": "SC01",
                        "title": "A question",
                        "narration_en": "I see a predator.",
                        "beats": [
                            {
                                "id": "BT01",
                                "image_id": "IM01",
                                "anchor": {"en": {"quote": "I", "occurrence": 1}},
                                "effect": "hold",
                                "focus": {"x": 0.5, "y": 0.5},
                            }
                        ],
                    }
                ],
            }
            images = {"items": [{"scene_id": "SC01", "image_id": "IM01", "ratio": "9:16", "path": "image.png"}]}
            track = {
                "language": "en",
                "voice": "VietNarrator",
                "speed": 1.0,
                "wav": "audio.wav",
                "duration": 5.0,
                "segments": [
                    {
                        "scene_id": "SC01",
                        "text": "I see a predator.",
                        "start": 0.0,
                        "end": 5.0,
                        "content_end": 4.5,
                        "path": "audio.wav",
                    }
                ],
            }
            audio = dict(track, tracks={"en": track})
            req = build_render_request(ROOT, brief, content, images, audio, lambda x: folder / x)
            target = folder / "input.zip"
            bundle(req, target)
            chrome = folder / "chrome"
            chrome.touch()
            actions = []

            def remote_run(argv, **kwargs):
                actions.append(argv)
                if argv[0] == "node":
                    out = Path(argv[-1])
                    (out / "video.mp4").write_bytes(b"\0\0\0\x18ftypisom" + b"fixture")
                    write(out / "layout.json", {"passed": True})
                    (out / "SC01.png").write_bytes(b"stillfixture")

            def probe(argv, **kwargs):
                if argv[0] == "node":
                    return str(chrome) + "\n"
                if argv[0] == "nvidia-smi":
                    return "fixture Tesla T4\n"
                return json.dumps(
                    {
                        "format": {"duration": "5.0"},
                        "streams": [
                            {"codec_type": "video", "codec_name": "h264", "width": 1080, "height": 1920},
                            {"codec_type": "audio", "codec_name": "aac"},
                        ],
                    }
                )

            with (
                patch("colab_bridge.job_worker.subprocess.run", side_effect=remote_run),
                patch("colab_bridge.job_worker.subprocess.check_output", side_effect=probe),
            ):
                report = run(target, folder / "output", req["request_id"], req["worker_sha256"])
            props = read(folder / "output/props.json")
            self.assertEqual(props["tracks"]["en"]["audioSrc"], "en.wav")
            self.assertEqual(props["tracks"]["en"]["scenesByAspect"]["9:16"][0]["images"][0]["effect"], "hold")
            self.assertEqual(props["tracks"]["en"]["cues"][0]["text"], "I see a predator.")
            self.assertEqual(props["tracks"]["en"]["scenesByAspect"]["9:16"][0]["end"], 5.0)
            self.assertTrue(props["modern_style"])
            self.assertFalse(report["quality_approval"])
            validate_render_result(folder / "output", req)
            self.assertTrue((folder / "output/subtitles_en.srt").exists())


class ColabBudgetIntegrationTests(unittest.TestCase):
    def setUp(self):
        from account_budget import Budgets

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cfg = read(ROOT / "config.json")
        self.cfg["colab_tts"]["management_store"] = str(self.root / "management")
        with patch("colab_bridge.client.cli", return_value="/bin/true"):
            self.client = Client(self.root, self.cfg)
        self.client.account = "fixture-account"
        self.client.session = "fixture-session"
        self.budget = Budgets(self.root / "management")

    def test_dispatch_requires_confirmed_identity_and_t4_ledger(self):
        with self.assertRaisesRegex(ColabError, "VERIFIED_SETUP_REQUIRED"):
            self.client._reserve("request", "audio")
        self.budget.bind_identity(
            "colab:fixture-account", "fixture-provider-subject", "synthetic isolated identity evidence"
        )
        with self.assertRaisesRegex(ColabError, "VERIFIED_SETUP_REQUIRED"):
            self.client._reserve("request", "audio")
        self.budget.allocated(
            "colab:fixture-account", "fixture-session", device="T4", evidence="synthetic isolated allocation evidence"
        )
        self.client._reserve("request", "audio")
        self.client._reserve("request", "audio")
        status = self.budget.snapshot("colab:fixture-account")
        self.assertEqual(status["held_seconds"], 600)
        pin = self.client.management.read()["pins"]["request"]
        self.assertEqual(pin["identity"], "fixture-provider-subject")
        self.client._settle("request")
        self.assertEqual(self.budget.snapshot("colab:fixture-account")["held_seconds"], 0)
        self.budget.uncertain("colab:fixture-account", "fixture-session", "synthetic disconnect evidence")
        with self.assertRaisesRegex(ColabError, "VERIFIED_SETUP_REQUIRED"):
            self.client._reserve("other", "render")

    def test_lifecycle_tracks_actual_observed_gpu_and_confirmed_release_only(self):
        self.budget.bind_identity("colab:fixture-account", "fixture-provider-subject", "synthetic identity evidence")
        with (
            patch.object(self.client, "ensure_authenticated"),
            patch.object(self.client, "call", return_value="fixture command confirmed"),
            patch.object(self.client, "exec", return_value='VP_GPU="Tesla T4"\n'),
        ):
            self.client.start()
            allocated = self.budget.snapshot("colab:fixture-account")["allocated_sessions"]
            self.assertEqual(len(allocated), 1)
            self.assertTrue(Path(allocated[0]["evidence"]).is_file())
            self.client.stop()
            self.assertEqual(self.budget.snapshot("colab:fixture-account")["allocated_sessions"], [])

    def test_unknown_allocation_cannot_allocate_again_and_reconciles_saved_session(self):
        self.budget.bind_identity("colab:fixture-account", "fixture-provider-subject", "synthetic identity evidence")
        with (
            patch.object(self.client, "ensure_authenticated"),
            patch.object(self.client, "call", side_effect=ColabError("COLAB_TIMEOUT")) as call,
        ):
            with self.assertRaisesRegex(ColabError, "TIMEOUT"):
                self.client.start()
            with self.assertRaisesRegex(ColabError, "ALLOCATION_PENDING"):
                self.client.start()
            self.budget.bind_identity(
                "colab:other-alias", "fixture-provider-subject", "synthetic same-identity evidence"
            )
            self.client.account = "other-alias"
            with self.assertRaisesRegex(ColabError, "ALLOCATION_PENDING"):
                self.client.start()
            self.assertEqual(call.call_count, 1)
        self.client.account = "fixture-account"
        self.client.session = "changed-default"
        with (
            patch.object(
                self.client,
                "_assignment_state",
                return_value={
                    "verified": True,
                    "identity": "fixture-provider-subject",
                    "assignment_count": 1,
                    "named_assignment_active": True,
                },
            ),
            patch.object(self.client, "ensure_authenticated"),
            patch.object(self.client, "exec", return_value='VP_GPU="Tesla T4"\n'),
        ):
            self.client.reconcile()
        self.assertEqual(self.client.session, "fixture-session")
        self.assertEqual(
            self.budget.snapshot("colab:fixture-account")["allocated_sessions"][0]["session"], "fixture-session"
        )

    def test_provider_quota_error_blocks_future_work_without_leaking_output(self):
        from types import SimpleNamespace

        self.budget.bind_identity("colab:fixture-account", "fixture-provider-subject", "synthetic identity evidence")
        self.budget.allocated(
            "colab:fixture-account", "fixture-session", device="T4", evidence="synthetic allocation evidence"
        )
        response = SimpleNamespace(
            returncode=1, stdout="private-token-secret", stderr="Quota exceeded: GPU unavailable"
        )
        with (
            patch("colab_bridge.accounts.command", return_value=["fixture-cli"]),
            patch("colab_bridge.client.subprocess.run", return_value=response),
        ):
            with self.assertRaisesRegex(ColabError, "PROVIDER_BLOCKED: quota"):
                self.client.call("exec")
        self.assertEqual(self.budget.snapshot("colab:fixture-account")["blocks"]["colab"]["error"], "quota")
        self.assertNotIn(
            "private-token-secret", "".join(p.read_text() for p in (self.root / ".state/colab-observations").iterdir())
        )
        with self.assertRaisesRegex(ColabError, "VERIFIED_SETUP_REQUIRED"):
            self.client._reserve("new", "audio")
        self.assertEqual(self.client.account, "fixture-account")

    def test_new_budget_window_requires_actual_session_recheck(self):
        from account_budget import HOUR, WINDOW

        self.budget.bind_identity("colab:fixture-account", "fixture-provider-subject", "synthetic identity evidence")
        with (
            patch("account_budget.time.time", return_value=100),
            patch("colab_bridge.client.time.time", return_value=100),
            patch.object(self.client, "ensure_authenticated"),
            patch.object(self.client, "call", return_value="fixture"),
            patch.object(self.client, "exec", return_value='VP_GPU="Tesla T4"\n'),
        ):
            self.client.start()
        later = 100 + WINDOW + HOUR
        with (
            patch("account_budget.time.time", return_value=later),
            patch("colab_bridge.client.time.time", return_value=later),
        ):
            with self.assertRaisesRegex(ColabError, "SERVICE_RECHECK_REQUIRED"):
                self.client._ready()
            with self.assertRaisesRegex(ColabError, "SERVICE_RECHECK_REQUIRED"):
                self.client._reserve("new", "audio")
            with (
                patch.object(
                    self.client,
                    "_assignment_state",
                    return_value={
                        "verified": True,
                        "identity": "fixture-provider-subject",
                        "assignment_count": 1,
                        "named_assignment_active": True,
                    },
                ),
                patch.object(self.client, "ensure_authenticated"),
                patch.object(self.client, "exec", return_value='VP_GPU="A100"\n'),
            ):
                with self.assertRaisesRegex(ColabError, "T4_NOT_CONFIRMED"):
                    self.client.reconcile()
            self.assertTrue(self.budget.snapshot("colab:fixture-account")["needs_service_recheck"])
            with (
                patch.object(
                    self.client,
                    "_assignment_state",
                    return_value={
                        "verified": True,
                        "identity": "fixture-provider-subject",
                        "assignment_count": 1,
                        "named_assignment_active": True,
                    },
                ),
                patch.object(self.client, "ensure_authenticated"),
                patch.object(self.client, "exec", return_value='VP_GPU="Tesla T4"\n'),
            ):
                self.client.reconcile()
            self.assertFalse(self.budget.snapshot("colab:fixture-account")["needs_service_recheck"])
            self.client._reserve("new", "audio")
            self.assertEqual(self.budget.snapshot("colab:fixture-account")["held_seconds"], 600)

    def test_budget_exhaustion_does_not_rotate_account(self):
        import time

        self.budget.bind_identity("colab:fixture-account", "fixture-provider-subject", "synthetic identity evidence")
        self.budget.allocated(
            "colab:fixture-account",
            "fixture-session",
            device="T4",
            at=time.time() - 5 * 3600,
            evidence="synthetic allocation evidence",
        )
        with self.assertRaisesRegex(ColabError, "BUDGET_BLOCKED"):
            self.client._reserve("new", "render")
        self.assertEqual(self.client.account, "fixture-account")
        self.assertEqual(self.client.session, "fixture-session")

    def test_multi_t4_pool_parallel_dispatch_default(self):
        import threading
        import time

        from colab_bridge.pool_manager import ColabPoolDispatcher, ColabPoolManager

        accounts_cfg = [{"id": f"colab_t4_{i}", "role": "render", "session": "video-pilot-tts"} for i in range(1, 5)]
        manager = ColabPoolManager(accounts_cfg, lock_dir=self.root / "locks")
        dispatcher = ColabPoolDispatcher(manager, poll_interval_seconds=0.02)
        active = 0
        peak_active = 0
        lock = threading.Lock()

        def run_render_on_t4(worker, task):
            nonlocal active, peak_active
            with lock:
                active += 1
                peak_active = max(peak_active, active)
            time.sleep(0.08)
            with lock:
                active -= 1
            return {"task_id": task["id"], "account": worker.account_id}

        tasks = [{"id": f"render_ch_{i}", "role": "render"} for i in range(4)]
        with (
            patch("colab_bridge.accounts.is_session_busy", return_value=False),
            patch("colab_bridge.accounts.has_external_session", return_value=False),
        ):
            results = dispatcher.dispatch_all(tasks, run_render_on_t4, role="render")

        self.assertEqual(len(results), 4)
        self.assertEqual([r["task_id"] for r in results], ["render_ch_0", "render_ch_1", "render_ch_2", "render_ch_3"])
        self.assertEqual(len({r["account"] for r in results}), 4)
        self.assertGreaterEqual(peak_active, 2, "Expected default multi-threaded parallel dispatch across T4 workers")
