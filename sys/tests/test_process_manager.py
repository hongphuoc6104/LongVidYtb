"""Unit and integration tests for ProcessGroupManager and zero-orphan teardown."""
from __future__ import annotations

import json
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

sys_dir = str(Path(__file__).resolve().parent.parent)
if sys_dir not in sys.path:
    sys.path.insert(0, sys_dir)

from flow_cdp.process_manager import (
    ProcessGroupManager,
    clean_singleton_locks,
)


class TestProcessGroupManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.registry_file = self.root / "cache/video-pilot/chrome_pids.json"
        self.manager = ProcessGroupManager(registry_file=self.registry_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_singleton_locks(self):
        user_dir = self.root / "chrome-profile"
        prof_dir = user_dir / "Profile 1"
        prof_dir.mkdir(parents=True)

        # Create lock files and symlinks
        for base in (user_dir, prof_dir):
            (base / "SingletonLock").symlink_to(base / "nonexistent-target")
            (base / "SingletonCookie").write_text("cookie")
            (base / "SingletonSocket").write_text("socket")

        cleaned = clean_singleton_locks(user_dir, "Profile 1")
        self.assertEqual(len(cleaned), 6)
        for base in (user_dir, prof_dir):
            for name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                self.assertFalse((base / name).exists())
                self.assertFalse((base / name).is_symlink())

    @patch("subprocess.Popen")
    @patch("flow_cdp.process_manager.is_port_listening", side_effect=[False, False, True])
    def test_launch_records_pgid_in_registry(self, mock_listening, mock_popen):
        fake_proc = MagicMock()
        fake_proc.pid = 8888
        mock_popen.return_value = fake_proc

        cfg = {
            "port": 9225,
            "user_data_dir": str(self.root / "user_data"),
            "directory": "Profile 1",
        }

        ok = self.manager.launch(cfg, url="https://flow.google.com/", headless=True)
        self.assertTrue(ok)

        # Verify Popen called with start_new_session=True
        mock_popen.assert_called_once()
        _, kwargs = mock_popen.call_args
        self.assertTrue(kwargs.get("start_new_session"))
        self.assertNotIn("DISPLAY", kwargs.get("env", {}))

        # Verify recorded in active_processes
        tracked = self.manager.get_tracked_process(9225)
        self.assertIsNotNone(tracked)
        self.assertEqual(tracked["pid"], 8888)
        self.assertEqual(tracked["pgid"], 8888)

        # Verify persisted on disk
        data = json.loads(self.registry_file.read_text(encoding="utf-8"))
        self.assertIn("9225", data["processes"])
        self.assertEqual(data["processes"]["9225"]["pid"], 8888)
        self.assertEqual(data["processes"]["9225"]["pgid"], 8888)

    @patch("flow_cdp.process_manager.is_port_listening", return_value=False)
    @patch("os.killpg")
    @patch("os.kill")
    def test_two_stage_teardown_kills_process_group(self, mock_kill, mock_killpg, mock_listening):
        # Setup active process entry
        self.manager.active_processes[9225] = {
            "port": 9225,
            "pid": 8888,
            "pgid": 8888,
            "user_data_dir": str(self.root / "user_data"),
            "profile_dir": "Profile 1",
        }
        self.manager._save_registry()

        closed = self.manager.terminate_by_port(9225, wait_interval=0.01)
        self.assertTrue(closed)

        # Verify Stage 1 SIGTERM sent to pgid 8888
        mock_killpg.assert_has_calls([call(8888, signal.SIGTERM)], any_order=True)

        # Verify removed from registry
        self.assertNotIn(9225, self.manager.active_processes)
        data = json.loads(self.registry_file.read_text(encoding="utf-8"))
        self.assertNotIn("9225", data["processes"])

    @patch("os.killpg")
    @patch("os.kill")
    def test_safety_guard_never_signals_pgid_le_1(self, mock_kill, mock_killpg):
        """Must NEVER send signal to PGID <= 1 (e.g. init or current group 0)."""
        # Test with pgid=0, pgid=1, pgid=-1, None
        for bad_id in (0, 1, -1, None):
            self.manager._kill_group(bad_id, bad_id, signal.SIGTERM)
            self.manager._kill_group(bad_id, bad_id, signal.SIGKILL)

        mock_killpg.assert_not_called()
        mock_kill.assert_not_called()

    @patch("flow_cdp.process_manager.is_pid_alive", return_value=True)
    @patch("os.killpg")
    def test_clean_orphans_from_registry_reaps_stale_processes(self, mock_killpg, mock_alive):
        """Stale records in registry from crashed runs must be reaped on startup."""
        stale_data = {
            "updated_at": 1000.0,
            "processes": {
                "9225": {"port": 9225, "pid": 7777, "pgid": 7777, "user_data_dir": str(self.root / "p1")},
                "9223": {"port": 9223, "pid": 7778, "pgid": 7778, "user_data_dir": str(self.root / "p2")},
            },
        }
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.registry_file.write_text(json.dumps(stale_data), encoding="utf-8")

        mgr = ProcessGroupManager(registry_file=self.registry_file)
        self.assertEqual(len(mgr.active_processes), 0)

        # Verify SIGTERM and SIGKILL were sent to both stale PGIDs
        mock_killpg.assert_has_calls([
            call(7777, signal.SIGTERM),
            call(7777, signal.SIGKILL),
            call(7778, signal.SIGTERM),
            call(7778, signal.SIGKILL),
        ], any_order=True)

        # Verify registry file cleared
        clean_data = json.loads(self.registry_file.read_text(encoding="utf-8"))
        self.assertEqual(clean_data["processes"], {})


if __name__ == "__main__":
    unittest.main()
