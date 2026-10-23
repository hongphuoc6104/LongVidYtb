"""Unit tests for Flow CDP profile and account management."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from flow_cdp.accounts import (
    detect_chrome_binary,
    is_port_listening,
    launch_profile,
    probe_profile,
    registry,
    save_registry,
    scan_system_chrome_profiles,
    setup_profile_dir,
)


class TestFlowAccounts(unittest.TestCase):
    def test_detect_chrome_binary_finds_system_or_fallback(self):
        binary = detect_chrome_binary()
        self.assertIsInstance(binary, str)
        self.assertTrue(len(binary) > 0)

    def test_scan_system_chrome_profiles_reads_local_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            local_state = tmppath / "Local State"
            local_state.write_text(
                '{"profile": {"info_cache": {"Profile 1": {"name": "Test1", "user_name": "test@gmail.com"}}}}',
                encoding="utf-8",
            )
            profiles = scan_system_chrome_profiles(source_dir=tmppath)
            self.assertEqual(len(profiles), 1)
            self.assertEqual(profiles[0]["directory"], "Profile 1")
            self.assertEqual(profiles[0]["email"], "test@gmail.com")

    def test_setup_profile_dir_cleans_singleton_locks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target_profile"
            target.mkdir()
            (target / "SingletonLock").touch()
            (target / "SingletonCookie").touch()
            setup_profile_dir(target, source_profile_name="Profile 1")
            self.assertFalse((target / "SingletonLock").exists())
            self.assertFalse((target / "SingletonCookie").exists())

    def test_is_port_listening_handles_closed_port(self):
        # Port 59999 is almost certainly closed
        self.assertFalse(is_port_listening(59999, timeout=0.1))

    @patch("flow_cdp.accounts.is_port_listening", return_value=False)
    def test_probe_profile_closed_port(self, mock_listening):
        res = probe_profile(9225)
        self.assertFalse(res["listening"])
        self.assertIsNone(res["version"])
        self.assertFalse(res["flow_open"])

    def test_registry_and_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_store = Path(tmpdir) / "flow"
            with patch("flow_cdp.accounts.STORE", custom_store):
                reg = registry()
                self.assertIn("profiles", reg)
                self.assertGreaterEqual(len(reg["profiles"]), 3)

                reg["preferred"] = "profile_custom"
                save_registry(reg)

                loaded = registry()
                self.assertEqual(loaded["preferred"], "profile_custom")

    def setUp(self):
        from flow_cdp.process_manager import reset_process_manager
        reset_process_manager()

    def tearDown(self):
        from flow_cdp.process_manager import reset_process_manager
        reset_process_manager()

    @patch("subprocess.Popen")
    def test_launch_profile_headless_mode_strips_display_and_adds_flag(self, mock_popen):
        fake_proc = MagicMock()
        fake_proc.pid = 9991
        mock_popen.return_value = fake_proc

        with tempfile.TemporaryDirectory() as tmpdir:
            reg_file = Path(tmpdir) / "chrome_pids.json"
            entry = {"port": 19228, "user_data_dir": str(Path(tmpdir) / "prof"), "directory": "Profile 1"}
            with patch("flow_cdp.process_manager.DEFAULT_REGISTRY_FILE", reg_file), \
                 patch("flow_cdp.process_manager.is_port_listening", side_effect=[False, True]):
                ok = launch_profile(entry, headless=True)
                self.assertTrue(ok)

            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            cmd = args[0]
            env = kwargs.get("env", {})
            cmd_str = " ".join(cmd)
            self.assertIn("--headless=new", cmd_str)
            self.assertNotIn("DISPLAY", env)
            self.assertIn("AutomaticTabDiscarding", cmd_str)
            self.assertIn("--disable-dev-shm-usage", cmd_str)

    @patch("subprocess.Popen")
    def test_launch_profile_headed_mode_sets_display(self, mock_popen):
        fake_proc = MagicMock()
        fake_proc.pid = 9992
        mock_popen.return_value = fake_proc

        with tempfile.TemporaryDirectory() as tmpdir:
            reg_file = Path(tmpdir) / "chrome_pids.json"
            entry = {"port": 19229, "user_data_dir": str(Path(tmpdir) / "prof"), "directory": "Profile 1"}
            with patch("flow_cdp.process_manager.DEFAULT_REGISTRY_FILE", reg_file), \
                 patch("flow_cdp.process_manager.is_port_listening", side_effect=[False, True]):
                ok = launch_profile(entry, headless=False)
                self.assertTrue(ok)

            mock_popen.assert_called_once()
            args, kwargs = mock_popen.call_args
            cmd = args[0]
            env = kwargs.get("env", {})
            cmd_str = " ".join(cmd)
            self.assertNotIn("--headless=new", cmd_str)
            self.assertIn("DISPLAY", env)


if __name__ == "__main__":
    unittest.main()
