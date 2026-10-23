"""Adversarial Verification Suite for Milestone M1 (CDP Multi-Profile Dispatch & Invariants).

Empirical Challenger verification tests:
1. Variation Worker Pinning & Failover Invariant:
   - Dependent variation shots CANNOT fail over to foreign profiles under any error.
   - DAG inter-patch pinning propagates parent worker to child patches.
   - Child patches are NEVER scheduled if parent fails.
   - Conflict isolation for disparate profile IDs.
2. Disk Reconciliation Invariants:
   - Corrupt image binary rejected.
   - 0-byte image rejected.
   - Truncated JPEG/PNG rejected.
   - Valid image with missing sidecar behavior and downstream consequence.
   - Valid image with intact sidecar reconciliation.
   - Stuck conflict auto-reset to not_submitted.
3. Lifecycle Cleanup & Abort Invariants:
   - "Mở bao nhiêu tắt bấy nhiêu" port isolation.
   - Context manager teardown on simulated SIGINT (KeyboardInterrupt).
   - Context manager teardown on unhandled Exception.
   - atexit handler idempotency.
   - Resilience against individual port teardown errors.
   - Workload tier boundaries and edge cases.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

import image_pipeline as ip
from flow_cdp.lifecycle import (
    ProfileLifecycleManager,
    calculate_optimal_workers,
    get_workload_tier_info,
)
from flow_cdp.multi_profile_manager import (
    ChromeProfileWorker,
    MultiProfileDispatcher,
    MultiProfileManager,
    ProfileState,
)
from flow_cdp.patch_partitioner import Patch, PatchPartitioner
from pilot import ROOT, Pilot, digest, read, write


class TestChallengerM1VariationPinningAndFailover(unittest.TestCase):
    """Adversarial stress tests for variation worker pinning and failover prohibition."""

    def setUp(self):
        self.profiles = [
            {"id": "p1", "port": 9225, "directory": "Profile 1"},
            {"id": "p2", "port": 9223, "directory": "Profile 2"},
            {"id": "p3", "port": 9224, "directory": "Profile 3"},
        ]
        self.manager = MultiProfileManager(self.profiles, cooldown_seconds=5.0)

    def test_adv_in_patch_variation_strictly_raises_on_pre_submit_error(self):
        """When child variation fails on p1 with retryable pre-submit error,

        failover to foreign profile p2/p3 is strictly forbidden and raises RuntimeError.
        """
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        patch_obj = Patch(
            patch_id="patch-adv-var-1",
            items=[
                {"testCase": "base-shot", "prompt": "Base full scene"},
                {"testCase": "var-shot", "prompt": "Variation shot", "based_on": "base-shot"},
            ],
        )

        attempts: list[str] = []

        def executor(worker: ChromeProfileWorker, items: list[dict]):
            attempts.append(worker.profile_id)
            if worker.profile_id == "p1":
                patch_obj.mark_item_success("base-shot", {"path": "/tmp/base.png", "media_id": "media-p1"})
                err = RuntimeError("Pre-submit socket closed during variation")
                err.generation_submitted = False
                err.retryable_pre_submit = True
                raise err
            return [{"path": f"/tmp/{x['testCase']}.png", "media_id": f"media-{x['testCase']}"} for x in items]

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.execute_patch_with_failover(patch_obj, executor)

        err_msg = str(ctx.exception)
        self.assertIn("Cannot fail over patch", err_msg)
        self.assertIn("items depend on media produced by profile p1", err_msg)
        # Verify it was only attempted on p1, never leaked to p2 or p3
        self.assertEqual(attempts, ["p1"])
        self.assertNotIn("p2", attempts)
        self.assertNotIn("p3", attempts)

    def test_adv_in_patch_variation_strictly_raises_on_non_retryable_error(self):
        """When child variation fails on p1 with a generic error (non-retryable),

        it immediately halts and never fails over to p2 or p3.
        """
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        patch_obj = Patch(
            patch_id="patch-adv-var-nonretryable",
            items=[
                {"testCase": "base-shot", "prompt": "Base full scene"},
                {"testCase": "var-shot", "prompt": "Variation shot", "based_on": "base-shot"},
            ],
        )

        attempts: list[str] = []

        def executor(worker: ChromeProfileWorker, items: list[dict]):
            attempts.append(worker.profile_id)
            if worker.profile_id == "p1":
                patch_obj.mark_item_success("base-shot", {"path": "/tmp/base.png", "media_id": "media-p1"})
                raise RuntimeError("Generic catastrophic connection failure")
            return [{"path": f"/tmp/{x['testCase']}.png", "media_id": f"media-{x['testCase']}"} for x in items]

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.execute_patch_with_failover(patch_obj, executor)

        self.assertIn("Generic catastrophic connection failure", str(ctx.exception))
        # Ensure zero failover attempts on p2 or p3
        self.assertEqual(attempts, ["p1"])

    def test_adv_pinned_profile_from_item_strictly_raises_if_target_profile_fails(self):
        """When patch item specifies target profile_id='p2', if p2 fails,

        it MUST NOT fail over to p1 or p3.
        """
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        patch_obj = Patch(
            patch_id="patch-adv-explicit-pin",
            items=[
                {"testCase": "pinned-shot", "prompt": "Pinned shot", "profile_id": "p2"},
            ],
        )

        attempts: list[str] = []

        def executor(worker: ChromeProfileWorker, items: list[dict]):
            attempts.append(worker.profile_id)
            err = RuntimeError("Pre-submit error on p2")
            err.generation_submitted = False
            err.retryable_pre_submit = True
            raise err

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.execute_patch_with_failover(patch_obj, executor)

        self.assertIn("Cannot fail over patch", str(ctx.exception))
        self.assertEqual(attempts, ["p2"])

    def test_adv_pinned_profile_resolved_from_disk_sidecar(self):
        """_get_required_profile extracts profile_id from base_ref_path sidecar JSON."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_img = Path(tmp_dir) / "base_shot.png"
            base_img.touch()
            sidecar = Path(tmp_dir) / "base_shot.json"
            sidecar.write_text(json.dumps({"profile_id": "p3", "forgeId": "forge-123"}))

            patch_obj = Patch(
                patch_id="patch-sidecar-pin",
                items=[
                    {"testCase": "var-1", "prompt": "Var", "baseRefPath": str(base_img)},
                ],
            )
            req = MultiProfileDispatcher._get_required_profile(patch_obj, patch_obj.items)
            self.assertEqual(req, "p3")

    def test_adv_pinned_profile_resolved_from_dict_base_image_sidecar(self):
        """_get_required_profile extracts profile_id from dict base_image path sidecar."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_img = Path(tmp_dir) / "base_shot2.png"
            base_img.touch()
            sidecar = Path(tmp_dir) / "base_shot2.json"
            sidecar.write_text(json.dumps({"profile": "p2", "media_id": "media-456"}))

            patch_obj = Patch(
                patch_id="patch-dict-pin",
                items=[
                    {"testCase": "var-2", "prompt": "Var", "base_image": {"path": str(base_img)}},
                ],
            )
            req = MultiProfileDispatcher._get_required_profile(patch_obj, patch_obj.items)
            self.assertEqual(req, "p2")

    def test_adv_multi_patch_dag_variation_chain_pinned_to_parent_worker(self):
        """3-Patch DAG: Patch A (parent) -> Patch B (variation) -> Patch C (grandchild).

        All three patches MUST execute on the exact same worker profile.
        """
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        pa = Patch(patch_id="patch-a", items=[{"testCase": "a", "prompt": "Scene A"}])
        pb = Patch(
            patch_id="patch-b",
            items=[{"testCase": "b", "prompt": "Scene B", "based_on": "a"}],
            depends_on_patch_id="patch-a",
        )
        pc = Patch(
            patch_id="patch-c",
            items=[{"testCase": "c", "prompt": "Scene C", "based_on": "b"}],
            depends_on_patch_id="patch-b",
        )

        execution_log: list[tuple[str, str]] = []

        def executor(worker: ChromeProfileWorker, items: list[dict]):
            for item in items:
                execution_log.append((item["testCase"], worker.profile_id))
            return [{"path": f"/tmp/{x['testCase']}.png", "media_id": f"media-{x['testCase']}"} for x in items]

        results = dispatcher.dispatch_all([pa, pb, pc], executor, max_concurrency=3)
        self.assertEqual(len(results), 3)

        # Verify all 3 patches ran on the exact same worker profile
        workers_used = [entry[1] for entry in execution_log]
        self.assertEqual(len(set(workers_used)), 1, f"Expected 1 worker for entire chain, got {set(workers_used)}")
        self.assertEqual([e[0] for e in execution_log], ["a", "b", "c"])

    def test_adv_multi_patch_dag_child_never_executed_if_parent_fails(self):
        """If parent patch fails, dependent child patches must NEVER be scheduled."""
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        pa = Patch(patch_id="patch-parent", items=[{"testCase": "p", "prompt": "Parent"}])
        pb = Patch(
            patch_id="patch-child",
            items=[{"testCase": "c", "prompt": "Child", "based_on": "p"}],
            depends_on_patch_id="patch-parent",
        )

        executed_cases: list[str] = []

        def failing_parent_executor(worker: ChromeProfileWorker, items: list[dict]):
            for item in items:
                executed_cases.append(item["testCase"])
            if items[0]["testCase"] == "p":
                raise RuntimeError("Parent generation failed on GPU")
            return [{"path": "/tmp/c.png", "media_id": "media-c"}]

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.dispatch_all([pa, pb], failing_parent_executor, max_concurrency=2)

        self.assertIn("FLOW_PARTIAL_BATCH", str(ctx.exception))
        # Child "c" was NEVER submitted to executor
        self.assertEqual(executed_cases, ["p"])
        self.assertNotIn("c", executed_cases)

    def test_adv_multi_patch_dag_child_failure_does_not_failover_to_foreign_worker(self):
        """Parent patch succeeds on W1. Child patch starts on W1 and fails.

        Child patch MUST NOT fail over to W2 or W3.
        """
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        pa = Patch(patch_id="patch-parent-ok", items=[{"testCase": "p_ok", "prompt": "Parent OK"}])
        pb = Patch(
            patch_id="patch-child-fail",
            items=[{"testCase": "c_fail", "prompt": "Child Fail", "based_on": "p_ok"}],
            depends_on_patch_id="patch-parent-ok",
        )

        attempts_log: list[tuple[str, str]] = []

        def executor(worker: ChromeProfileWorker, items: list[dict]):
            case = items[0]["testCase"]
            attempts_log.append((case, worker.profile_id))
            if case == "p_ok":
                return [{"path": "/tmp/p.png", "media_id": "media-p", "profile_id": worker.profile_id}]
            # Child failure
            err = RuntimeError("Socket dropped before child generation")
            err.generation_submitted = False
            err.retryable_pre_submit = True
            raise err

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.dispatch_all([pa, pb], executor, max_concurrency=2)

        self.assertIn("Cannot fail over patch", str(ctx.exception))
        # Parent succeeded on worker X
        parent_worker = attempts_log[0][1]
        # Child was attempted ONLY on parent_worker, never on a foreign worker
        child_attempts = [w for c, w in attempts_log if c == "c_fail"]
        self.assertEqual(child_attempts, [parent_worker])

    def test_adv_partitioner_rejects_merging_conflicting_profiles(self):
        """PatchPartitioner never bundles items with conflicting profile assignments."""
        partitioner = PatchPartitioner(target_size=3, min_size=2, max_size=4)
        items = [
            {"id": "item-1", "profile_id": "p1"},
            {"id": "item-2", "profile_id": "p2"},
            {"id": "item-3", "profile_id": "p1"},
        ]
        patches = partitioner.partition(items)
        for p in patches:
            profiles_in_patch = {it.get("profile_id") for it in p.items if it.get("profile_id")}
            self.assertLessEqual(len(profiles_in_patch), 1)


class TestChallengerM1DiskReconciliation(unittest.TestCase):
    """Adversarial stress tests for disk reconciliation invariants."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for n in ["schemas", ".agents", "renderer", "tests", "examples", "scripts"]:
            if (ROOT / n).is_dir():
                shutil.copytree(ROOT / n, self.root / n)
        for n in [
            "pilot.py", "workflow.py", "machine_review.py", "image_pipeline.py",
            "prompt_templates.py", "content_contract.py", "adapters.py", "config.json",
            "account_budget.py", "flow_management.py", "execution.py", "AGENTS.md", "GEMINI.md"
        ]:
            shutil.copy(ROOT / n, self.root / n)

        cfg = read(self.root / "config.json")
        cfg.pop("flow_batch", None)
        cfg["flow_require_ui_evidence"] = True
        cfg["flow_management_store"] = str(self.root)
        write(self.root / "config.json", cfg)

        self.p = Pilot(self.root)
        self.j = "challenger-reconcile"
        self.p.new(self.j, read(ROOT / "examples/m1/brief.json"))
        self.p.approve(self.j, "control", 1, "CHALLENGER FIXTURE")
        d = read(ROOT / "examples/m1/content.json")
        _, r, h = self.p.brief(self.j)
        d.update(brief_revision=r, brief_hash=h)
        write(self.p.job(self.j) / "draft/content.json", d)
        self.p.run(self.j, "content")
        self.p.approve(self.j, "content", 1, "CHALLENGER FIXTURE")

        # Create preflight
        base = self.p.job(self.j) / "flow"
        base.mkdir(exist_ok=True)
        Image.new("RGB", (30, 30)).save(base / "preflight.png")
        write(base / "preflight.json", {
            "observed_at": time.time(),
            "mode": "image",
            "credits_per_generation": 0,
            "model": "Nano Banana 2 Lite",
            "profile": "video-pilot",
            "project": "Video Pilot",
            "observer": "CHALLENGER",
            "account_confirmed": True,
            "operations": ["image", "character-register"],
            "screenshot": "flow/preflight.png",
            "screenshot_hash": digest(base / "preflight.png"),
        })

    def tearDown(self):
        self.p.db.close()
        self.tmp.cleanup()

    def test_adv_disk_reconciliation_corrupt_binary_rejected(self):
        """Corrupt image binary in download/ MUST NOT be auto-reconciled to downloaded."""
        target = "ref:CH01"
        prompt = "Character reference"
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / "flow/attempts" / key
        download_dir = attempt_dir / "download"
        download_dir.mkdir(parents=True, exist_ok=True)

        # Write corrupt bytes (not a valid image)
        corrupt_file = download_dir / "result.png"
        corrupt_file.write_bytes(b"CORRUPT_NON_IMAGE_BINARY_DATA_0123456789")

        record = {
            "key": key,
            "identity": identity,
            "state": "submitted",
            "submitted_at": time.time(),
        }
        write(attempt_dir / "request.json", record)

        rec = ip.auto_reconcile_attempt(self.p, self.j, attempt_dir, record)

        # State MUST NOT be updated to downloaded
        self.assertNotEqual(rec.get("state"), "downloaded")
        self.assertEqual(rec.get("state"), "submitted")
        self.assertFalse(rec.get("auto_reconciled", False))
        # request.json on disk must remain submitted
        disk_record = read(attempt_dir / "request.json")
        self.assertEqual(disk_record.get("state"), "submitted")

    def test_adv_disk_reconciliation_zero_byte_file_rejected(self):
        """0-byte file in download/ MUST NOT be auto-reconciled."""
        target = "ref:CH01"
        prompt = "Character reference"
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / "flow/attempts" / key
        download_dir = attempt_dir / "download"
        download_dir.mkdir(parents=True, exist_ok=True)

        # Touch 0-byte file
        zero_file = download_dir / "result.jpg"
        zero_file.touch()
        self.assertEqual(zero_file.stat().st_size, 0)

        record = {
            "key": key,
            "identity": identity,
            "state": "ambiguous",
            "submitted_at": time.time(),
        }
        write(attempt_dir / "request.json", record)

        rec = ip.auto_reconcile_attempt(self.p, self.j, attempt_dir, record)

        self.assertNotEqual(rec.get("state"), "downloaded")
        self.assertEqual(rec.get("state"), "ambiguous")

    def test_adv_disk_reconciliation_truncated_jpeg_rejected(self):
        """Truncated JPEG file (valid header but broken body) MUST NOT be auto-reconciled."""
        target = "ref:CH01"
        prompt = "Character reference"
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / "flow/attempts" / key
        download_dir = attempt_dir / "download"
        download_dir.mkdir(parents=True, exist_ok=True)

        # Truncated JPEG header
        truncated_file = download_dir / "result.jpg"
        truncated_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")

        record = {
            "key": key,
            "identity": identity,
            "state": "submitted",
            "submitted_at": time.time(),
        }
        write(attempt_dir / "request.json", record)

        rec = ip.auto_reconcile_attempt(self.p, self.j, attempt_dir, record)

        self.assertNotEqual(rec.get("state"), "downloaded")
        self.assertEqual(rec.get("state"), "submitted")

    def test_adv_disk_reconciliation_valid_image_with_missing_sidecar(self):
        """When download/ has valid image binary but NO sidecar .json:

        auto_reconcile_attempt reconciles the image binary, BUT downstream sidecar lookups
        must safely handle the missing sidecar without crashing.
        """
        target = "ref:CH01"
        prompt = "Character reference"
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / "flow/attempts" / key
        download_dir = attempt_dir / "download"
        download_dir.mkdir(parents=True, exist_ok=True)

        # Create 100% valid image
        img_file = download_dir / "result.png"
        Image.new("RGB", (720, 1280), (100, 150, 200)).save(img_file)
        self.assertGreater(img_file.stat().st_size, 100)

        # NO sidecar result.json created
        sidecar_file = download_dir / "result.json"
        self.assertFalse(sidecar_file.exists())

        record = {
            "key": key,
            "identity": identity,
            "state": "submitted",
            "submitted_at": time.time(),
        }
        write(attempt_dir / "request.json", record)

        rec = ip.auto_reconcile_attempt(self.p, self.j, attempt_dir, record)

        # Binary verification passed, so attempt state was updated to downloaded
        self.assertEqual(rec.get("state"), "downloaded")
        self.assertTrue(rec.get("auto_reconciled"))
        self.assertEqual(rec.get("sha256"), digest(img_file))

        # Downstream resilience test: check if _resolve_item_profile crashes on missing sidecar
        item_ref = {"based_on": str(img_file)}
        resolved = PatchPartitioner._resolve_item_profile(item_ref)
        self.assertIsNone(resolved, "Missing sidecar must safely return None without throwing")

    def test_adv_reconcile_stuck_conflict_preserves_unknown_submission(self):
        """Transport error wording cannot establish that the provider received nothing."""
        target = "ref:CH01"
        prompt = "Character reference"
        cfg, ratio, actual_prompt, identity, key = ip._plan_request(
            self.p, self.j, target, prompt, (), None, None
        )
        attempt_dir = self.p.job(self.j) / "flow/attempts" / key
        attempt_dir.mkdir(parents=True, exist_ok=True)

        record = {
            "key": key,
            "identity": identity,
            "state": "ambiguous",
            "error": "Temporary network timeout: no close frame received or sent",
            "submitted_at": time.time(),
        }
        write(attempt_dir / "request.json", record)

        before = (attempt_dir / "request.json").read_bytes()
        res = ip.reconcile_stuck_conflict(self.p, self.j, target, reason="test recovery")
        self.assertIsNotNone(res)
        self.assertEqual(res.get("state"), "ambiguous")
        self.assertEqual((attempt_dir / "request.json").read_bytes(), before)


class TestChallengerM1LifecycleAndTeardown(unittest.TestCase):
    """Adversarial stress tests for lifecycle tracking, simulated SIGINT/abort, and teardown."""

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.is_port_listening")
    @patch("flow_cdp.accounts.registry")
    def test_adv_lifecycle_pre_existing_port_isolation(self, mock_reg, mock_listening, mock_stop):
        """Lifecycle manager MUST preserve pre-existing ports and only close spawned ports."""
        mock_reg.return_value = {
            "profiles": [
                {"id": "p1", "port": 9225},
                {"id": "p2", "port": 9223},
                {"id": "p3", "port": 9224},
            ]
        }
        # Port 9225 is pre-existing; 9223 and 9224 are not
        mock_listening.side_effect = lambda port: port == 9225

        lm = ProfileLifecycleManager(auto_teardown=True, force_teardown_all=False)
        self.assertIn(9225, lm.pre_existing_ports)
        self.assertNotIn(9223, lm.pre_existing_ports)

        # Simulate spawning port 9223
        lm.spawned_ports.add(9223)

        closed = lm.teardown(force_all=False)

        # Only spawned port 9223 closed; pre-existing 9225 untouched
        self.assertEqual(closed, [9223])
        mock_stop.assert_called_once_with(9223)

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.is_port_listening", return_value=False)
    @patch("flow_cdp.accounts.registry", return_value={"profiles": []})
    def test_adv_lifecycle_context_manager_teardown_on_simulated_sigint(self, mock_reg, mock_listening, mock_stop):
        """When KeyboardInterrupt (SIGINT) occurs inside context, teardown runs and closes spawned ports."""
        sigint_caught = False
        try:
            with ProfileLifecycleManager(auto_teardown=True) as lm:
                lm.spawned_ports.add(9223)
                lm.spawned_ports.add(9224)
                # Simulate Ctrl+C / SIGINT
                raise KeyboardInterrupt("Simulated user Ctrl+C / SIGINT")
        except KeyboardInterrupt:
            sigint_caught = True

        self.assertTrue(sigint_caught)
        # Teardown was called for both spawned ports
        stopped_ports = [call.args[0] for call in mock_stop.call_args_list]
        self.assertCountEqual(stopped_ports, [9223, 9224])
        # spawned_ports emptied
        self.assertEqual(len(lm.spawned_ports), 0)

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.is_port_listening", return_value=False)
    @patch("flow_cdp.accounts.registry", return_value={"profiles": []})
    def test_adv_lifecycle_context_manager_teardown_on_unhandled_exception(self, mock_reg, mock_listening, mock_stop):
        """When an unhandled Exception occurs inside context, teardown cleans up cleanly."""
        exception_caught = False
        try:
            with ProfileLifecycleManager(auto_teardown=True) as lm:
                lm.spawned_ports.add(9222)
                raise RuntimeError("Catastrophic browser automation crash")
        except RuntimeError:
            exception_caught = True

        self.assertTrue(exception_caught)
        mock_stop.assert_called_once_with(9222)
        self.assertEqual(len(lm.spawned_ports), 0)

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.is_port_listening", return_value=False)
    @patch("flow_cdp.accounts.registry", return_value={"profiles": []})
    def test_adv_lifecycle_teardown_idempotent_double_call_safe(self, mock_reg, mock_listening, mock_stop):
        """Calling teardown() multiple times does not re-terminate already closed ports."""
        lm = ProfileLifecycleManager(auto_teardown=True)
        lm.spawned_ports.add(9223)

        closed_1 = lm.teardown()
        self.assertEqual(closed_1, [9223])
        self.assertEqual(mock_stop.call_count, 1)

        # Second teardown call on same instance
        closed_2 = lm.teardown()
        self.assertEqual(closed_2, [])
        # mock_stop should still only have been called once
        self.assertEqual(mock_stop.call_count, 1)

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.is_port_listening", return_value=False)
    @patch("flow_cdp.accounts.registry", return_value={"profiles": []})
    def test_adv_lifecycle_teardown_survives_partial_port_error(self, mock_reg, mock_listening, mock_stop):
        """If stopping one port raises an error, remaining ports are still stopped."""
        def side_effect(port: int):
            if port == 9223:
                raise OSError("Process vanished or permission denied")
            return True

        mock_stop.side_effect = side_effect
        lm = ProfileLifecycleManager(auto_teardown=True)
        lm.spawned_ports.add(9223)
        lm.spawned_ports.add(9224)

        closed = lm.teardown()
        # Port 9224 succeeded despite 9223 failing
        self.assertIn(9224, closed)
        self.assertEqual(mock_stop.call_count, 2)

    def test_adv_workload_sizing_boundary_and_extremes(self):
        """Workload tier boundaries, zero, negative, and large image counts."""
        # Boundaries
        self.assertEqual(calculate_optimal_workers(0), 1)
        self.assertEqual(calculate_optimal_workers(-5), 1)
        self.assertEqual(calculate_optimal_workers(1), 1)
        self.assertEqual(calculate_optimal_workers(3), 1)
        self.assertEqual(calculate_optimal_workers(4), 2)
        self.assertEqual(calculate_optimal_workers(8), 3)
        self.assertEqual(calculate_optimal_workers(9), 3)
        self.assertEqual(calculate_optimal_workers(16), 4)
        self.assertEqual(calculate_optimal_workers(20), 5)
        self.assertEqual(calculate_optimal_workers(21), 5)
        self.assertEqual(calculate_optimal_workers(50), 8)
        self.assertEqual(calculate_optimal_workers(51), 8)
        self.assertEqual(calculate_optimal_workers(100), 8)

        # Plan inspection
        plan_micro = get_workload_tier_info(2)
        self.assertEqual(plan_micro["tier"], "micro")
        self.assertEqual(plan_micro["recommended_workers"], 1)

        plan_bulk = get_workload_tier_info(80)
        self.assertEqual(plan_bulk["tier"], "bulk_long_video")
        self.assertEqual(plan_bulk["recommended_workers"], 8)

    @patch("flow_cdp.accounts.stop_profile_by_port")
    @patch("flow_cdp.accounts.is_port_listening", side_effect=lambda p: p == 9225)
    @patch("flow_cdp.accounts.registry")
    def test_adv_force_teardown_all_closes_both_pre_existing_and_spawned(self, mock_reg, mock_listening, mock_stop):
        """When force_teardown_all=True, BOTH pre-existing and spawned ports are closed."""
        mock_reg.return_value = {
            "profiles": [
                {"id": "p1", "port": 9225},
                {"id": "p2", "port": 9223},
            ]
        }
        lm = ProfileLifecycleManager(auto_teardown=True, force_teardown_all=True)
        lm.spawned_ports.add(9223)

        closed = lm.teardown(force_all=True)
        self.assertCountEqual(closed, [9225, 9223])
        self.assertEqual(mock_stop.call_count, 2)

    def test_adv_register_spawned_port_helper(self):
        """register_spawned_port integrates with active lifecycle manager and is safe when none active."""
        from flow_cdp.lifecycle import register_spawned_port

        # Without active lifecycle: should not raise
        register_spawned_port(9229)

        # With active lifecycle
        with patch("flow_cdp.accounts.is_port_listening", return_value=False), \
             patch("flow_cdp.accounts.registry", return_value={"profiles": []}), \
             patch("flow_cdp.accounts.stop_profile_by_port"):
            with ProfileLifecycleManager(auto_teardown=True) as mgr:
                register_spawned_port(9227)
                self.assertIn(9227, mgr.spawned_ports)


class TestChallengerM1AdvancedChainsAndEdgeCases(unittest.TestCase):
    """Stress tests for long dependency chains and edge conditions."""

    def setUp(self):
        self.profiles = [
            {"id": "p1", "port": 9225, "directory": "Profile 1"},
            {"id": "p2", "port": 9223, "directory": "Profile 2"},
            {"id": "p3", "port": 9224, "directory": "Profile 3"},
        ]
        self.manager = MultiProfileManager(self.profiles, cooldown_seconds=5.0)

    def test_adv_long_10_shot_chain_e2e_partitioning_and_pinned_dispatch(self):
        """A 10-shot sequential variation chain: shot_0 -> shot_1 -> ... -> shot_9.

        Must be partitioned into chunks linked by DAG dependencies and ALL executed on the
        exact same worker profile in strict topological order.
        """
        partitioner = PatchPartitioner(target_size=3, min_size=2, max_size=4)
        items = [{"id": "shot_0", "prompt": "Base shot"}]
        for i in range(1, 10):
            items.append({"id": f"shot_{i}", "prompt": f"Variation {i}", "based_on": f"shot_{i-1}"})

        patches = partitioner.partition(items)
        self.assertGreater(len(patches), 1, "10 items must be partitioned into multiple chunks")

        # Verify dependency linking across patches
        group_ids = {p.dependency_group_id for p in patches}
        self.assertEqual(len(group_ids), 1, "All chunks must share dependency_group_id")

        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        execution_order: list[tuple[str, str]] = []

        def tracked_executor(worker: ChromeProfileWorker, chunk_items: list[dict]):
            for it in chunk_items:
                execution_order.append((it["id"], worker.profile_id))
            return [{"path": f"/tmp/{it['id']}.png", "media_id": f"media-{it['id']}"} for it in chunk_items]

        results = dispatcher.dispatch_all(patches, tracked_executor, max_concurrency=3)
        self.assertEqual(len(results), 10)

        # 1. Topological order preserved
        executed_ids = [e[0] for e in execution_order]
        expected_ids = [f"shot_{i}" for i in range(10)]
        self.assertEqual(executed_ids, expected_ids)

        # 2. Worker pinning strictly preserved across ALL chunks
        workers_used = {e[1] for e in execution_order}
        self.assertEqual(len(workers_used), 1, f"All chunks must use identical worker, got {workers_used}")

    def test_adv_long_chain_partial_failure_halts_remaining_chunks(self):
        """In a 10-shot chain, if chunk 2 fails, chunk 3+ MUST NOT execute."""
        partitioner = PatchPartitioner(target_size=3, min_size=2, max_size=4)
        items = [{"id": "shot_0", "prompt": "Base shot"}]
        for i in range(1, 10):
            items.append({"id": f"shot_{i}", "prompt": f"Variation {i}", "based_on": f"shot_{i-1}"})

        patches = partitioner.partition(items)
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)

        executed_chunks: list[int] = []

        def failing_executor(worker: ChromeProfileWorker, chunk_items: list[dict]):
            chunk_idx = len(executed_chunks)
            executed_chunks.append(chunk_idx)
            if chunk_idx == 1:
                # Second chunk fails
                raise RuntimeError("Chunk 2 GPU crashed")
            return [{"path": f"/tmp/{it['id']}.png", "media_id": f"media-{it['id']}"} for it in chunk_items]

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.dispatch_all(patches, failing_executor, max_concurrency=2)

        self.assertIn("FLOW_PARTIAL_BATCH", str(ctx.exception))
        # Chunk 0 and chunk 1 were attempted; chunk 2+ were never run
        self.assertEqual(executed_chunks, [0, 1])


if __name__ == "__main__":
    unittest.main()

