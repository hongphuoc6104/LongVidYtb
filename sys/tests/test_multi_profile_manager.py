"""Unit tests for MultiProfileManager and failover dispatcher."""
import time
import unittest

from flow_cdp.multi_profile_manager import (
    ChromeProfileWorker,
    MultiProfileDispatcher,
    MultiProfileManager,
    ProfileState,
)
from flow_cdp.patch_partitioner import Patch


class TestMultiProfileManager(unittest.TestCase):
    def setUp(self):
        self.profiles = [
            {"id": "p1", "port": 9222, "directory": "Profile 1"},
            {"id": "p2", "port": 9223, "directory": "Profile 2"},
            {"id": "p3", "port": 9224, "directory": "Profile 3"},
        ]
        self.manager = MultiProfileManager(self.profiles, cooldown_seconds=2.0)

    def test_initial_pool_status(self):
        status = self.manager.get_status()
        self.assertEqual(status["active_workers"], 3)
        self.assertTrue(all(p["state"] == "healthy" for p in status["profiles"]))

    def test_worker_acquisition_and_release(self):
        w1 = self.manager.acquire_healthy_worker()
        self.assertIsNotNone(w1)
        self.assertEqual(w1.state, ProfileState.BUSY)

        w2 = self.manager.acquire_healthy_worker()
        self.assertIsNotNone(w2)
        self.assertNotEqual(w1.profile_id, w2.profile_id)

        # Release w1 with success
        self.manager.release_worker(w1, success=True)
        self.assertEqual(w1.state, ProfileState.HEALTHY)
        self.assertEqual(w1.success_count, 1)

    def test_error_triggers_cooldown(self):
        w = self.manager.acquire_healthy_worker()
        self.manager.release_worker(w, success=False, error="PUBLIC_ERROR_UNUSUAL_ACTIVITY detected")
        self.assertEqual(w.state, ProfileState.COOLDOWN)
        self.assertGreater(w.cooldown_until, time.time())

        # An acquired worker should NOT be w
        next_w = self.manager.acquire_healthy_worker()
        self.assertNotEqual(next_w.profile_id, w.profile_id)

    def test_dispatcher_failover_on_unusual_activity(self):
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=3)
        patch = Patch(
            patch_id="patch-failover-1",
            items=[
                {"testCase": "shot-1", "prompt": "Shot 1"},
                {"testCase": "shot-2", "prompt": "Shot 2"},
            ],
        )

        attempts = []

        def mock_executor(worker: ChromeProfileWorker, items: list[dict]):
            attempts.append((worker.profile_id, [x["testCase"] for x in items]))
            if worker.profile_id == "p1":
                # p1 succeeds on shot-1 then fails on shot-2 with unusual activity
                patch.mark_item_success("shot-1", {"path": "/tmp/1.png", "media_id": "m1"})
                raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY: Account blocked temporarily")
            # Other workers succeed on whatever items they are given
            return [{"path": f"/tmp/{x['testCase']}.png", "media_id": f"m-{x['testCase']}"} for x in items]

        results = dispatcher.execute_patch_with_failover(patch, mock_executor)

        # Verify p1 was tried first, then another worker took over only the remaining items (shot-2)
        self.assertGreaterEqual(len(attempts), 2)
        self.assertEqual(attempts[0][0], "p1")
        self.assertIn("shot-1", attempts[0][1])

        # Second attempt should NOT be p1, and only needs shot-2
        self.assertNotEqual(attempts[1][0], "p1")
        self.assertEqual(attempts[1][1], ["shot-2"])

        # Final result should be completed with 2 items
        self.assertTrue(patch.is_completed)
        self.assertEqual(len(results), 2)

    def test_parallel_dispatch_across_workers(self):
        dispatcher = MultiProfileDispatcher(self.manager)
        patches = [
            Patch(patch_id=f"patch-{i}", items=[{"testCase": f"shot-{i}-1", "prompt": "p"}])
            for i in range(3)
        ]

        assigned_profiles = set()

        def slow_executor(worker: ChromeProfileWorker, items: list[dict]):
            assigned_profiles.add(worker.profile_id)
            time.sleep(0.05)
            return [{"path": f"/tmp/{items[0]['testCase']}.png", "media_id": "ok"}]

        results = dispatcher.dispatch_all(patches, slow_executor, max_concurrency=3)
        self.assertEqual(len(results), 3)
        # Should have utilized multiple distinct profiles in parallel
        self.assertGreater(len(assigned_profiles), 1)

    def test_probe_status_includes_port_listening(self):
        status = self.manager.get_status(probe_ports=True)
        self.assertIn("port_listening", status["profiles"][0])
        self.assertIsInstance(status["profiles"][0]["port_listening"], bool)

    def test_all_workers_blocked_raises_error(self):
        dispatcher = MultiProfileDispatcher(self.manager, max_retries_per_patch=1)
        patch = Patch(patch_id="p-fail-all", items=[{"testCase": "t-1"}])

        def always_fail(worker: ChromeProfileWorker, items: list[dict]):
            raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY")

        with self.assertRaises(RuntimeError) as ctx:
            dispatcher.execute_patch_with_failover(patch, always_fail)
        self.assertIn("failed after", str(ctx.exception).lower())

    def test_default_profiles_sync_with_config_and_cdp_client(self):
        import json
        from pathlib import Path

        from flow_cdp.cdp_direct_client import PROFILES
        from flow_cdp.multi_profile_manager import DEFAULT_PROFILES

        cfg_path = Path(__file__).resolve().parents[1] / "config.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg_profiles = cfg["flow_cdp_profiles"]

        self.assertEqual(len(cfg_profiles), 3)
        self.assertEqual(len(DEFAULT_PROFILES), 3)
        self.assertEqual(len(PROFILES), 3)

        expected_ports = [9225, 9223, 9224]
        self.assertEqual([p["port"] for p in cfg_profiles], expected_ports)
        self.assertEqual([p["port"] for p in DEFAULT_PROFILES], expected_ports)
        self.assertEqual([p["cdp_port"] for p in PROFILES], expected_ports)

    def test_direct_cdp_connect_skips_reload_when_untrapped_and_polls_on_reload(self):
        import asyncio
        from unittest.mock import AsyncMock, patch

        from flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession

        session = DirectCDPProfileSession(PROFILES[1])
        called_methods = []

        async def fake_call(method: str, params: dict | None = None, timeout: float = 60.0):
            called_methods.append(method)
            if method == "Network.getAllCookies":
                return {"cookies": [{"name": "_GRECAPTCHA", "domain": "flow.google.com", "path": "/"}]}
            return {}

        eval_states = [
            False,  # initial typeof window.mintCaptcha === 'function'
            None,   # evaluate CDP_RECAPTCHA_GUARD_JS
            {       # _wait_for_flow_ready probe
                "readyState": "complete",
                "hasAt": True,
                "hasPristine": True,
                "hasExec": True,
                "trapped": False,
                "hasMint": True,
            },
            True,   # final typeof window.mintCaptcha === 'function'
        ]

        async def fake_eval(expr: str, await_promise: bool = True, timeout: float = 120.0):
            return eval_states.pop(0) if eval_states else True

        class DummyWS:
            async def close(self):
                pass
            def __aiter__(self):
                return self
            async def __anext__(self):
                raise StopAsyncIteration

        with patch("flow_cdp.cdp_direct_client.get_flow_target", return_value={
            "webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/page/1",
            "url": PROFILES[1]["url"],
        }), patch("flow_cdp.cdp_direct_client.websockets.connect", new=AsyncMock(return_value=DummyWS())):
            session.call = fake_call
            session.evaluate = fake_eval
            asyncio.run(session.connect(reload_for_guard=False))
            asyncio.run(session.close())

        self.assertNotIn("Page.reload", called_methods)
        self.assertNotIn("Storage.clearDataForOrigin", called_methods)


if __name__ == "__main__":
    unittest.main()

