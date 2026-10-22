"""Empirical stress and adversarial verification suite for Milestone M1.

Tests PatchPartitioner boundary conditions, dangling merges, chain chunking,
and MultiProfileDispatcher DAG concurrency across complex synthetic graphs.
"""
from __future__ import annotations

import concurrent.futures
import threading
import time
import unittest
from typing import Any

from flow_cdp.multi_profile_manager import (
    ChromeProfileWorker,
    MultiProfileDispatcher,
    MultiProfileManager,
)
from flow_cdp.patch_partitioner import Patch, PatchPartitioner


class TestPatchPartitionerStress(unittest.TestCase):
    """Adversarial stress tests for PatchPartitioner."""

    def setUp(self):
        self.partitioner = PatchPartitioner(target_size=3, min_size=2, max_size=4)

    def test_01_empty_input(self):
        """Empty input must produce empty patch list."""
        patches = self.partitioner.partition([])
        self.assertEqual(patches, [])

    def test_02_single_item(self):
        """1 item input must produce exactly 1 patch containing that item."""
        items = [{"testCase": "item-0", "prompt": "P0"}]
        patches = self.partitioner.partition(items)
        self.assertEqual(len(patches), 1)
        self.assertEqual(len(patches[0].items), 1)
        self.assertEqual(patches[0].items[0]["testCase"], "item-0")

    def test_03_two_items(self):
        """2 items input must produce exactly 1 patch containing 2 items."""
        items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(2)]
        patches = self.partitioner.partition(items)
        self.assertEqual(len(patches), 1)
        self.assertEqual(len(patches[0].items), 2)

    def test_04_three_items(self):
        """3 items input must produce exactly 1 patch containing 3 items (target_size)."""
        items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(3)]
        patches = self.partitioner.partition(items)
        self.assertEqual(len(patches), 1)
        self.assertEqual(len(patches[0].items), 3)

    def test_05_four_items_merges_dangling(self):
        """4 items: target_size=3, leftover 1 item MUST be merged into 1 patch of 4 items."""
        items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(4)]
        patches = self.partitioner.partition(items)
        self.assertEqual(len(patches), 1, "4 items should merge into 1 patch of 4 instead of [3, 1]")
        self.assertEqual(len(patches[0].items), 4)

    def test_06_five_items(self):
        """5 items: should partition into [3, 2] patches (no dangling 1-item patch)."""
        items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(5)]
        patches = self.partitioner.partition(items)
        self.assertEqual(len(patches), 2)
        sizes = [len(p.items) for p in patches]
        self.assertEqual(sorted(sizes), [2, 3])
        self.assertEqual(sum(sizes), 5)

    def test_07_seven_items_merges_dangling(self):
        """7 items: should partition into [3, 4] patches without any dangling 1-item patch."""
        items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(7)]
        patches = self.partitioner.partition(items)
        sizes = [len(p.items) for p in patches]
        self.assertEqual(sorted(sizes), [3, 4])
        self.assertEqual(sum(sizes), 7)
        for p in patches:
            self.assertGreaterEqual(len(p.items), 2)
            self.assertLessEqual(len(p.items), 4)

    def test_08_eight_and_ten_items_dangling_merges(self):
        """8 items -> [3, 3, 2], 10 items -> [3, 3, 4].

        No patch should have 1 item.
        """
        for n, expected_sizes in [(8, [3, 3, 2]), (10, [3, 3, 4])]:
            items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(n)]
            patches = self.partitioner.partition(items)
            sizes = [len(p.items) for p in patches]
            self.assertEqual(sorted(sizes), sorted(expected_sizes), f"Failed for {n} items")
            self.assertTrue(all(len(p.items) >= 2 for p in patches))

    def test_09_one_hundred_items_stress(self):
        """100 independent items: must all partition cleanly into sizes between 2 and 4."""
        items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(100)]
        patches = self.partitioner.partition(items)
        total_items = sum(len(p.items) for p in patches)
        self.assertEqual(total_items, 100)
        # 100 items with target 3, max 4 -> 33 patches (32 patches of 3, 1 patch of 4)
        for idx, p in enumerate(patches):
            self.assertGreaterEqual(
                len(p.items), 2, f"Patch {idx} has fewer than min_size=2 items: {len(p.items)}"
            )
            self.assertLessEqual(
                len(p.items), 4, f"Patch {idx} has more than max_size=4 items: {len(p.items)}"
            )

    def test_10_long_chain_chunking_and_dag_linking(self):
        """Long sequential chain of 10 items (> max_size=4).

        Must chunk into sequential patches linked by depends_on_patch_id and dependency_group_id.
        """
        items = [{"testCase": f"seq-{i}", "prompt": f"P{i}"} for i in range(10)]
        for i in range(1, 10):
            items[i]["based_on"] = f"seq-{i-1}"
        patches = self.partitioner.partition(items)
        total = sum(len(p.items) for p in patches)
        self.assertEqual(total, 10)

        # All patches must share the same dependency_group_id
        dep_group = patches[0].dependency_group_id
        self.assertIsNotNone(dep_group)
        for p in patches:
            self.assertEqual(p.dependency_group_id, dep_group)

        # Patches must be chained sequentially via depends_on_patch_id
        self.assertIsNone(patches[0].depends_on_patch_id)
        for i in range(1, len(patches)):
            self.assertEqual(patches[i].depends_on_patch_id, patches[i - 1].patch_id)

    def test_11_long_chain_chunk_sizes_behavior(self):
        """Empirically document long chain partitioning behavior for chains of size 5, 6, 7, 8, 9, 11."""
        for n in [5, 6, 7, 8, 9, 11]:
            items = [{"testCase": f"item-{i}", "prompt": f"P{i}"} for i in range(n)]
            for i in range(1, n):
                items[i]["based_on"] = f"item-{i-1}"
            patches = self.partitioner.partition(items)
            self.assertEqual(sum(len(p.items) for p in patches), n)
            for p in patches:
                self.assertLessEqual(len(p.items), self.partitioner.max_size)

    def test_12_profile_conflict_prevents_dangling_merge(self):
        """A dangling 1-item patch must NOT be merged if profile conflicts with previous patch."""
        items = [
            {"testCase": "item-0", "prompt": "P0", "profile_id": "profile_1"},
            {"testCase": "item-1", "prompt": "P1", "profile_id": "profile_1"},
            {"testCase": "item-2", "prompt": "P2", "profile_id": "profile_1"},
            {"testCase": "item-3", "prompt": "P3", "profile_id": "profile_2"},
        ]
        patches = self.partitioner.partition(items)
        self.assertEqual(len(patches), 2)
        self.assertEqual(len(patches[0].items), 3)
        self.assertEqual(patches[0].pinned_profile, "profile_1")
        self.assertEqual(len(patches[1].items), 1)
        self.assertEqual(patches[1].pinned_profile, "profile_2")

    def test_13_dependency_group_prevents_dangling_merge(self):
        """A dangling 1-item independent shot must NOT merge into a dependency group patch."""
        # 5 items in a chain -> split into 2 patches with dependency_group_id
        chain_items = [{"testCase": f"c-{i}", "prompt": f"C{i}"} for i in range(5)]
        for i in range(1, 5):
            chain_items[i]["based_on"] = f"c-{i-1}"
        # Followed by 1 independent shot
        indep_item = [{"testCase": "indep-0", "prompt": "Indep"}]
        all_items = chain_items + indep_item

        patches = self.partitioner.partition(all_items)
        # The independent item must NOT merge into patches[-2] or patches[-1] because of dependency_group_id
        self.assertEqual(patches[-1].items[0]["testCase"], "indep-0")
        self.assertIsNone(patches[-1].dependency_group_id)

    def test_14_branching_tree_dependencies(self):
        """Root with 4 direct dependent children (Tree). All belong to same component."""
        items = [
            {"testCase": "root", "prompt": "Root"},
            {"testCase": "child-1", "prompt": "C1", "based_on": "root"},
            {"testCase": "child-2", "prompt": "C2", "based_on": "root"},
            {"testCase": "child-3", "prompt": "C3", "based_on": "root"},
            {"testCase": "child-4", "prompt": "C4", "based_on": "root"},
        ]
        patches = self.partitioner.partition(items)
        total = sum(len(p.items) for p in patches)
        self.assertEqual(total, 5)
        # Root must appear in the first patch
        first_patch_ids = [it["testCase"] for it in patches[0].items]
        self.assertIn("root", first_patch_ids)

    def test_15_cyclic_input_items_broken_gracefully(self):
        """Cyclic items (A->B->C->A) must not infinite loop and must produce acyclic patches."""
        items = [
            {"testCase": "s-a", "prompt": "A", "based_on": "s-b"},
            {"testCase": "s-b", "prompt": "B", "based_on": "s-c"},
            {"testCase": "s-c", "prompt": "C", "based_on": "s-a"},
        ]
        patches = self.partitioner.partition(items)
        self.assertEqual(sum(len(p.items) for p in patches), 3)
        # Patches must not have circular depends_on_patch_id
        for p in patches:
            self.assertNotEqual(p.depends_on_patch_id, p.patch_id)


class TestMultiProfileDispatcherDAGStress(unittest.TestCase):
    """Stress tests for MultiProfileDispatcher DAG execution, concurrency, and worker pinning."""

    def setUp(self):
        self.profiles = [
            {"id": "p1", "port": 9225, "directory": "Profile 1"},
            {"id": "p2", "port": 9223, "directory": "Profile 2"},
            {"id": "p3", "port": 9224, "directory": "Profile 3"},
            {"id": "p4", "port": 9222, "directory": "Profile 4"},
        ]
        self.manager = MultiProfileManager(self.profiles, cooldown_seconds=1.0)
        self.dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=2)

    def test_01_deep_linear_dag_execution_order_and_worker_pinning(self):
        """A linear chain of 8 patches (P0 -> P1 -> ... -> P7).

        Must execute sequentially in strict order, with all patches pinned to the same worker profile.
        """
        patches = []
        prev_id = None
        for i in range(8):
            pid = f"lin-patch-{i}"
            p = Patch(
                patch_id=pid,
                items=[{"testCase": f"shot-{i}", "prompt": f"P{i}"}],
                dependency_group_id="deep-lin-group",
                depends_on_patch_id=prev_id,
            )
            patches.append(p)
            prev_id = pid

        execution_order = []
        lock = threading.Lock()

        def mock_executor(worker: ChromeProfileWorker, items: list[dict]):
            with lock:
                execution_order.append((worker.profile_id, items[0]["testCase"], time.time()))
            time.sleep(0.01)
            return [{"path": f"/tmp/{items[0]['testCase']}.png", "media_id": f"m-{items[0]['testCase']}"}]

        results = self.dispatcher.dispatch_all(patches, mock_executor, max_concurrency=4)
        self.assertEqual(len(results), 8)
        self.assertEqual(len(execution_order), 8)

        # Verify strict topological ordering
        for i in range(8):
            self.assertEqual(execution_order[i][1], f"shot-{i}")
            if i > 0:
                self.assertLess(execution_order[i - 1][2], execution_order[i][2])

        # Verify all patches ran on the exact same worker profile
        first_worker = execution_order[0][0]
        for entry in execution_order:
            self.assertEqual(entry[0], first_worker, "All chained patches must pin to the same profile")

    def test_02_wide_fan_out_tree_dag(self):
        """Root patch P0 with 6 child patches (P1..P6) all depending on P0.

        P0 must finish first. Then all 6 children must run on P0's worker profile without deadlocking.
        """
        p0 = Patch(patch_id="tree-root", items=[{"testCase": "root-shot", "prompt": "Root"}])
        children = [
            Patch(
                patch_id=f"tree-child-{i}",
                items=[{"testCase": f"child-{i}-shot", "prompt": f"C{i}"}],
                depends_on_patch_id="tree-root",
            )
            for i in range(6)
        ]
        all_patches = [p0] + children

        exec_events = []
        lock = threading.Lock()

        def mock_executor(worker: ChromeProfileWorker, items: list[dict]):
            with lock:
                exec_events.append((worker.profile_id, items[0]["testCase"], time.time()))
            time.sleep(0.02)
            return [{"path": f"/tmp/{items[0]['testCase']}.png", "media_id": f"m-{items[0]['testCase']}"}]

        results = self.dispatcher.dispatch_all(all_patches, mock_executor, max_concurrency=4)
        self.assertEqual(len(results), 7)
        self.assertEqual(len(exec_events), 7)

        # Root must be first
        self.assertEqual(exec_events[0][1], "root-shot")
        root_worker = exec_events[0][0]
        root_time = exec_events[0][2]

        # All children must execute after root and use root's worker profile
        for child_event in exec_events[1:]:
            self.assertEqual(child_event[0], root_worker, "Child must pin to root's profile")
            self.assertGreaterEqual(child_event[2], root_time, "Child must start after root")

    def test_03_forest_multi_tree_concurrency(self):
        """Forest of 3 independent trees running concurrently across 4 workers.

        Tree A: A0 -> A1 -> A2
        Tree B: B0 -> B1 -> B2
        Tree C: C0 -> C1 -> C2
        Verify that trees utilize distinct worker profiles concurrently, while within each tree
        the worker pinning is strictly preserved.
        """
        trees_patches = []
        for prefix in ["A", "B", "C"]:
            p0 = Patch(patch_id=f"{prefix}-0", items=[{"testCase": f"{prefix}-shot-0"}], dependency_group_id=f"g-{prefix}")
            p1 = Patch(patch_id=f"{prefix}-1", items=[{"testCase": f"{prefix}-shot-1"}], dependency_group_id=f"g-{prefix}", depends_on_patch_id=f"{prefix}-0")
            p2 = Patch(patch_id=f"{prefix}-2", items=[{"testCase": f"{prefix}-shot-2"}], dependency_group_id=f"g-{prefix}", depends_on_patch_id=f"{prefix}-1")
            trees_patches.extend([p0, p1, p2])

        events = []
        lock = threading.Lock()

        def slow_executor(worker: ChromeProfileWorker, items: list[dict]):
            t_start = time.time()
            time.sleep(0.04)
            t_end = time.time()
            with lock:
                events.append({
                    "profile": worker.profile_id,
                    "shot": items[0]["testCase"],
                    "start": t_start,
                    "end": t_end,
                })
            return [{"path": f"/tmp/{items[0]['testCase']}.png", "media_id": f"m-{items[0]['testCase']}"}]

        results = self.dispatcher.dispatch_all(trees_patches, slow_executor, max_concurrency=4)
        self.assertEqual(len(results), 9)

        # Verify worker pinning within each tree
        tree_workers = {}
        for prefix in ["A", "B", "C"]:
            prefix_events = [e for e in events if e["shot"].startswith(prefix)]
            self.assertEqual(len(prefix_events), 3)
            # Order within tree
            shots_order = [e["shot"] for e in prefix_events]
            self.assertEqual(shots_order, [f"{prefix}-shot-0", f"{prefix}-shot-1", f"{prefix}-shot-2"])
            # All shots in this tree share the same worker
            worker_ids = {e["profile"] for e in prefix_events}
            self.assertEqual(len(worker_ids), 1, f"Tree {prefix} violated worker pinning: {worker_ids}")
            tree_workers[prefix] = worker_ids.pop()

        # Concurrency verification: different trees should ideally run on different workers
        self.assertGreater(len(set(tree_workers.values())), 1, "Trees should be distributed across multiple workers")

    def test_04_high_volume_stress_50_patches(self):
        """Stress test with 50 independent patches dispatched across 4 workers."""
        patches = [
            Patch(patch_id=f"p-vol-{i}", items=[{"testCase": f"shot-vol-{i}-{j}"} for j in range(2)])
            for i in range(50)
        ]

        def fast_executor(worker: ChromeProfileWorker, items: list[dict]):
            time.sleep(0.002)
            return [{"path": f"/tmp/{x['testCase']}.png", "media_id": f"m-{x['testCase']}"} for x in items]

        results = self.dispatcher.dispatch_all(patches, fast_executor, max_concurrency=4)
        self.assertEqual(len(results), 100)
        self.assertTrue(all(p.is_completed for p in patches))

    def test_05_failed_parent_aborts_dependents(self):
        """If parent patch fails, child patch must not execute and dispatch_all raises."""
        p0 = Patch(patch_id="fail-parent", items=[{"testCase": "fail-p-shot"}])
        p1 = Patch(patch_id="child-p", items=[{"testCase": "child-p-shot"}], depends_on_patch_id="fail-parent")

        child_executed = False

        def failing_executor(worker: ChromeProfileWorker, items: list[dict]):
            nonlocal child_executed
            shot = items[0]["testCase"]
            if shot == "fail-p-shot":
                raise RuntimeError("Parent hardware error")
            if shot == "child-p-shot":
                child_executed = True
            return [{"path": f"/tmp/{shot}.png"}]

        with self.assertRaises(RuntimeError) as ctx:
            self.dispatcher.dispatch_all([p0, p1], failing_executor, max_concurrency=2)

        self.assertFalse(child_executed, "Child must NOT execute if parent failed")

    def test_06_dangling_dependency_id_handled_gracefully(self):
        """If depends_on_patch_id references a non-existent patch, it executes as root."""
        p = Patch(
            patch_id="orphan-p",
            items=[{"testCase": "orphan-shot"}],
            depends_on_patch_id="non-existent-parent",
        )
        results = self.dispatcher.dispatch_all(
            [p],
            lambda w, it: [{"path": "/tmp/ok.png"}],
            max_concurrency=2,
        )
        self.assertEqual(len(results), 1)

    def test_07_empty_patch_list(self):
        """Dispatch empty patches list returns empty list."""
        results = self.dispatcher.dispatch_all([], lambda w, it: [], max_concurrency=4)
        self.assertEqual(results, [])

    def test_08_worker_thread_safety_under_race_conditions(self):
        """Empirically stress-test acquire_healthy_worker and release_worker under 20 concurrent threads.

        Verifies that no two threads ever hold the same worker simultaneously.
        """
        active_holders: dict[str, int] = {}
        race_violations = 0
        lock = threading.Lock()

        def worker_task(task_id: int):
            nonlocal race_violations
            for _ in range(25):
                w = self.manager.acquire_healthy_worker()
                if not w:
                    time.sleep(0.005)
                    continue
                with lock:
                    active_holders[w.profile_id] = active_holders.get(w.profile_id, 0) + 1
                    if active_holders[w.profile_id] > 1:
                        race_violations += 1
                # Simulate work
                time.sleep(0.002)
                with lock:
                    active_holders[w.profile_id] -= 1
                self.manager.release_worker(w, success=True)

        threads = [threading.Thread(target=worker_task, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(race_violations, 0, "Race condition detected: same worker held by multiple threads!")

    def test_09_hard_stop_error_fails_immediately_without_retries(self):
        """Hard-stop errors (bot detect, unusual activity) must raise immediately without retry loops."""
        p = Patch(patch_id="p-hardstop", items=[{"testCase": "t-hardstop"}])
        call_count = 0

        def hard_stop_executor(worker: ChromeProfileWorker, items: list[dict]):
            nonlocal call_count
            call_count += 1
            raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY detected by bot detector")

        with self.assertRaises(RuntimeError) as ctx:
            self.dispatcher.execute_patch_with_failover(p, hard_stop_executor)

        self.assertIn("UNUSUAL_ACTIVITY", str(ctx.exception))
        self.assertEqual(call_count, 1, "Hard-stop error should fail immediately on first attempt")

    def test_10_foreign_profile_failover_prohibited_for_variation(self):
        """Variation beat with based_on must NOT fail over to another profile on pre-send transport error."""
        p = Patch(
            patch_id="p-var-dep",
            items=[
                {"testCase": "shot-parent", "prompt": "parent"},
                {"testCase": "shot-child", "prompt": "child", "based_on": "shot-parent"},
            ],
        )
        attempt_workers = []

        def failing_child_executor(worker: ChromeProfileWorker, items: list[dict]):
            attempt_workers.append(worker.profile_id)
            if worker.profile_id == "p1":
                p.mark_item_success("shot-parent", {"path": "/tmp/parent.png", "media_id": "m-p1"})
                err = RuntimeError("Socket lost before child submission")
                err.generation_submitted = False
                err.retryable_pre_submit = True
                raise err
            return [{"path": f"/tmp/{it['testCase']}.png"} for it in items]

        with self.assertRaises(RuntimeError) as ctx:
            self.dispatcher.execute_patch_with_failover(p, failing_child_executor)

        self.assertIn("Cannot fail over patch", str(ctx.exception))
        self.assertIn("depend on media produced by profile p1", str(ctx.exception))
        self.assertEqual(attempt_workers, ["p1"], "Must not attempt foreign worker failover")


if __name__ == "__main__":
    unittest.main()
