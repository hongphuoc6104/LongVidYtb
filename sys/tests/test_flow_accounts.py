"""Unit tests for Flow CDP profile and account management."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flow_cdp.accounts import (
    detect_chrome_binary,
    is_port_listening,
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


if __name__ == "__main__":
    unittest.main()
