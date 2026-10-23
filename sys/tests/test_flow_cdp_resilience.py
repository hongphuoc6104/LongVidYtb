"""Resilience tests for Flow CDP socket recovery, anti-tab-discarding, and WebSocket reconnection."""
import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import b2_bridge
import flow_cdp.bridge as flow_bridge
from flow_cdp.cdp_direct_client import (
    PROFILES,
    DirectCDPProfileSession,
    ensure_chrome_profiles_launched,
)
from flow_cdp.multi_profile_manager import (
    ChromeProfileWorker,
    MultiProfileDispatcher,
    MultiProfileManager,
)
from flow_cdp.patch_partitioner import Patch
from websockets.exceptions import ConnectionClosedError


class TestFlowCdpResilience(unittest.TestCase):
    def test_chrome_launch_flags_include_anti_discard_and_memory_saver(self):
        """Chrome launch arguments must disable tab discarding, memory saver and background throttling."""
        launched_cmd = []
        launched_env = {}

        def fake_popen(cmd, env=None, **kwargs):
            launched_cmd.extend(cmd)
            if env:
                launched_env.update(env)
            proc = MagicMock()
            proc.poll.return_value = None
            return proc

        target_cfg = [dict(PROFILES[0], cdp_port=19225)]
        with patch("flow_cdp.cdp_direct_client.is_port_open", side_effect=[False, True]), \
             patch("flow_cdp.cdp_direct_client.subprocess.Popen", side_effect=fake_popen), \
             patch("flow_cdp.cdp_direct_client.time.sleep"):
            ensure_chrome_profiles_launched(target_cfg, headless=True)

        cmd_str = " ".join(launched_cmd)
        self.assertIn("--headless=new", cmd_str)
        self.assertNotIn("DISPLAY", launched_env)
        self.assertIn("AutomaticTabDiscarding", cmd_str)
        self.assertIn("MemorySaverMode", cmd_str)
        self.assertIn("--disable-background-timer-throttling", cmd_str)
        self.assertIn("--disable-backgrounding-occluded-windows", cmd_str)
        self.assertIn("--disable-renderer-backgrounding", cmd_str)
        self.assertIn("--disable-dev-shm-usage", cmd_str)
        self.assertIn("--disable-hang-monitor", cmd_str)

    def test_chrome_launch_headed_mode_sets_display(self):
        """When headless=False is requested, DISPLAY must be retained and --headless=new omitted."""
        launched_cmd = []
        launched_env = {}

        def fake_popen(cmd, env=None, **kwargs):
            launched_cmd.extend(cmd)
            if env:
                launched_env.update(env)
            proc = MagicMock()
            proc.poll.return_value = None
            return proc

        target_cfg = [dict(PROFILES[0], cdp_port=19226)]
        with patch("flow_cdp.cdp_direct_client.is_port_open", side_effect=[False, True]), \
             patch("flow_cdp.cdp_direct_client.subprocess.Popen", side_effect=fake_popen), \
             patch("flow_cdp.cdp_direct_client.time.sleep"):
            ensure_chrome_profiles_launched(target_cfg, headless=False)

        cmd_str = " ".join(launched_cmd)
        self.assertNotIn("--headless=new", cmd_str)
        self.assertIn("DISPLAY", launched_env)

    def test_b2_bridge_ensure_connected_does_not_crash_when_socket_missing(self):
        """When socket is missing and CDP ports are closed, ensure_connected must launch Chrome without raising socket not found."""
        nonexistent_sock = Path("/tmp/video-pilot-test-nonexistent/flow-dummy.sock")

        with patch("flow_cdp.cdp_direct_client.is_port_open", return_value=False), \
             patch("flow_cdp.cdp_direct_client.ensure_chrome_profiles_launched") as mock_launch, \
             patch("b2_bridge.SOCKET_PATH", nonexistent_sock):
            status = b2_bridge.ensure_connected(sock_path=nonexistent_sock)
            self.assertEqual(status.get("status"), "connected")
            mock_launch.assert_called_once()

    def test_flow_bridge_ensure_connected_does_not_crash_when_socket_missing(self):
        """In flow_cdp.bridge, ensure_connected launches Chrome directly if neither port nor socket is active."""
        nonexistent_sock = Path("/tmp/video-pilot-test-nonexistent/flow-dummy.sock")

        with patch("flow_cdp.cdp_direct_client.is_port_open", return_value=False), \
             patch("flow_cdp.cdp_direct_client.ensure_chrome_profiles_launched") as mock_launch, \
             patch.object(flow_bridge, "SOCKET_PATH", nonexistent_sock), \
             patch.object(flow_bridge, "get_socket_path", return_value=nonexistent_sock):
            status = flow_bridge.ensure_connected(sock_path=nonexistent_sock)
            self.assertEqual(status.get("status"), "connected")
            mock_launch.assert_called_once()

    def test_direct_cdp_websocket_ping_interval_disabled(self):
        """WebSocket connection must set ping_interval=None to avoid false drops during heavy browser RPCs."""
        session = DirectCDPProfileSession(PROFILES[0])
        connect_kwargs = {}

        async def fake_connect(url, **kwargs):
            connect_kwargs.update(kwargs)
            ws = MagicMock()
            ws.closed = False
            async def fake_close():
                pass
            ws.close = fake_close
            ws.__aiter__ = MagicMock(return_value=iter([]))
            return ws

        with patch("flow_cdp.cdp_direct_client.get_flow_target", return_value={
            "webSocketDebuggerUrl": "ws://127.0.0.1:9225/devtools/page/test",
            "url": PROFILES[0]["url"],
        }), patch("flow_cdp.cdp_direct_client.websockets.connect", side_effect=fake_connect):
            session.call = AsyncMock(return_value={})
            session.evaluate = AsyncMock(return_value={"hasAt": True, "hasPristine": True})
            asyncio.run(session.connect(reload_for_guard=False))
            asyncio.run(session.close())

        self.assertIsNone(connect_kwargs.get("ping_interval"))

    def test_evaluate_reconnects_and_recovers_on_no_close_frame(self):
        session = DirectCDPProfileSession(PROFILES[0])
        reconnected = []
        mock_ws = MagicMock()
        mock_ws.closed = False
        async def fake_close():
            pass
        mock_ws.close = fake_close
        session.ws = mock_ws

        async def fake_reconnect():
            reconnected.append(True)
            new_ws = MagicMock()
            new_ws.closed = False
            new_ws.close = fake_close
            session.ws = new_ws

        session.reconnect = fake_reconnect

        # 1st call raises ConnectionClosedError ('no close frame received or sent')
        # 2nd call returns valid result
        close_error = ConnectionClosedError(rcvd=None, sent=None)
        mock_call = AsyncMock(side_effect=[close_error, {"result": {"value": "recovered_value"}}])
        session.call = mock_call

        res = asyncio.run(session.evaluate("window.__test_probe", await_promise=False))
        self.assertEqual(res, "recovered_value")
        self.assertEqual(len(reconnected), 1)

    def test_dispatcher_fails_over_on_websocket_pre_submit_closure(self):
        """A pre-submission WebSocket closure fails over cleanly to another worker without aborting the batch."""
        profiles = [
            {"id": "worker-1", "port": 9222, "directory": "P1"},
            {"id": "worker-2", "port": 9223, "directory": "P2"},
        ]
        manager = MultiProfileManager(profiles, cooldown_seconds=0.1)
        dispatcher = MultiProfileDispatcher(manager, max_retries_per_patch=2)

        patch_obj = Patch(
            patch_id="patch-resilience-1",
            items=[{"testCase": "shot-1", "prompt": "Prompt 1"}],
        )

        attempts = []

        def executor(worker: ChromeProfileWorker, items: list[dict]):
            attempts.append(worker.profile_id)
            if worker.profile_id == "worker-1":
                exc = RuntimeError("CDP_TRANSPORT_CLOSED: no close frame received or sent")
                exc.generation_submitted = False
                exc.retryable_pre_submit = True
                raise exc
            return [{"request_id": items[0]["testCase"], "path": "/tmp/shot-1.png", "media_id": "m1"}]

        results = dispatcher.execute_patch_with_failover(patch_obj, executor)
        self.assertTrue(patch_obj.is_completed)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["media_id"], "m1")
        self.assertIn("worker-1", attempts)
        self.assertIn("worker-2", attempts)


if __name__ == "__main__":
    unittest.main()
