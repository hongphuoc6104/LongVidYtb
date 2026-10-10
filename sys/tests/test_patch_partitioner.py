"""Unit tests for Flow CDP patch partitioner."""
import unittest
from flow_cdp.patch_partitioner import PatchPartitioner, Patch


class TestPatchPartitioner(unittest.TestCase):
    def setUp(self):
        self.partitioner = PatchPartitioner(target_size=3, min_size=2, max_size=4)

    def test_empty_items(self):
        self.assertEqual(self.partitioner.partition([]), [])

    def test_independent_shots_partitioning(self):
        items = [{"testCase": f"shot-{i}", "prompt": f"prompt {i}", "ratio": "16:9"} for i in range(7)]
        patches = self.partitioner.partition(items)
        
        # 7 items with target_size=3, max_size=4 should divide into ~2-3 patches
        self.assertGreaterEqual(len(patches), 2)
        total_items = sum(len(p.items) for p in patches)
        self.assertEqual(total_items, 7)
        for p in patches:
            self.assertGreaterEqual(len(p.items), 2)
            self.assertLessEqual(len(p.items), 4)

    def test_dependency_chain_kept_in_same_patch(self):
        items = [
            {"testCase": "scene-01", "prompt": "establishing"},
            {"testCase": "scene-02", "prompt": "variation 1", "based_on": "scene-01"},
            {"testCase": "scene-03", "prompt": "variation 2", "based_on": "scene-02"},
            {"testCase": "scene-04", "prompt": "independent"},
            {"testCase": "scene-05", "prompt": "independent 2"},
        ]
        patches = self.partitioner.partition(items)
        
        # Find patch containing scene-01
        p_with_01 = next(p for p in patches if any(x["testCase"] == "scene-01" for x in p.items))
        shot_ids = [x["testCase"] for x in p_with_01.items]
        
        # scene-01, scene-02, scene-03 must be in the same patch in sequential order
        self.assertIn("scene-02", shot_ids)
        self.assertIn("scene-03", shot_ids)
        self.assertLess(shot_ids.index("scene-01"), shot_ids.index("scene-02"))
        self.assertLess(shot_ids.index("scene-02"), shot_ids.index("scene-03"))

    def test_patch_item_tracking_and_partial_retry(self):
        items = [
            {"testCase": "shot-a", "prompt": "A"},
            {"testCase": "shot-b", "prompt": "B"},
            {"testCase": "shot-c", "prompt": "C"},
        ]
        patch = Patch(patch_id="patch-1", items=items)
        self.assertEqual(patch.pending_count, 3)
        self.assertFalse(patch.is_completed)

        # Mark shot-a successful
        patch.mark_item_success("shot-a", {"path": "/tmp/a.png", "media_id": "m-a"})
        self.assertEqual(patch.pending_count, 2)
        pending = patch.get_pending_items()
        self.assertEqual([x["testCase"] for x in pending], ["shot-b", "shot-c"])

        # Mark shot-b failed
        patch.mark_item_failure("shot-b", "PUBLIC_ERROR_UNUSUAL_ACTIVITY")
        self.assertEqual(patch.status, "failed")
        self.assertEqual(patch.error, "PUBLIC_ERROR_UNUSUAL_ACTIVITY")

        # Retrying only processes pending items (shot-b and shot-c)
        pending_retry = patch.get_pending_items()
        self.assertEqual(len(pending_retry), 2)
        self.assertNotIn("shot-a", [x["testCase"] for x in pending_retry])

        # Complete shot-b and shot-c
        patch.mark_item_success("shot-b", {"path": "/tmp/b.png", "media_id": "m-b"})
        patch.mark_item_success("shot-c", {"path": "/tmp/c.png", "media_id": "m-c"})
        self.assertTrue(patch.is_completed)
        self.assertEqual(patch.status, "completed")
    def test_circular_dependency_does_not_infinite_loop(self):
        # A depends on B, B depends on A
        items = [
            {"testCase": "cycle-a", "prompt": "A", "based_on": "cycle-b"},
            {"testCase": "cycle-b", "prompt": "B", "based_on": "cycle-a"},
        ]
        # Must terminate and produce valid patches without infinite loop
        patches = self.partitioner.partition(items)
        self.assertEqual(sum(len(p.items) for p in patches), 2)

    def test_long_dependency_chain_chunked_cleanly(self):
        # 6 items in sequential dependency chain with max_size=4
        items = [{"testCase": f"seq-{i}", "prompt": f"P{i}"} for i in range(6)]
        for i in range(1, 6):
            items[i]["based_on"] = f"seq-{i-1}"
        patches = self.partitioner.partition(items)
        self.assertEqual(sum(len(p.items) for p in patches), 6)
        for p in patches:
            self.assertLessEqual(len(p.items), self.partitioner.max_size)

    def test_already_completed_item_not_marked_failed(self):
        items = [{"testCase": "item-1"}, {"testCase": "item-2"}]
        patch = Patch(patch_id="p-test", items=items)
        patch.mark_item_success("item-1", {"ok": True})
        patch.mark_item_failure("item-1", "Late error")
        # Completed items must take precedence
        self.assertIn("item-1", patch.completed_items)
        self.assertNotIn("item-1", patch.failed_items)


if __name__ == "__main__":
    unittest.main()

