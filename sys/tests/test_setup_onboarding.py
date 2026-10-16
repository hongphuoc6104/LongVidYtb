"""Unit tests for unified setup onboarding wizard."""
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.setup_onboarding import ensure_colab_cli, step_bootstrap_env


class TestSetupOnboarding(unittest.TestCase):
    @patch("shutil.which")
    def test_ensure_colab_cli_finds_existing_binary(self, mock_which):
        mock_which.return_value = "/usr/local/bin/colab"
        with patch("pathlib.Path.is_file", return_value=True), patch("os.access", return_value=True):
            binary = ensure_colab_cli()
            self.assertEqual(binary, "/usr/local/bin/colab")

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_ensure_colab_cli_installs_when_missing(self, mock_run, mock_which):
        with patch("pathlib.Path.is_file", side_effect=[False, True, True]), patch("os.access", return_value=True):
            mock_run.return_value.returncode = 0
            binary = ensure_colab_cli()
            self.assertIn("colab", binary)
            mock_run.assert_called()

    def test_step_bootstrap_creates_directories(self):
        step_bootstrap_env()
        repo_root = Path(__file__).resolve().parents[2]
        self.assertTrue((repo_root / "sys/runs").is_dir())
        self.assertTrue((repo_root / "video").is_dir())


if __name__ == "__main__":
    unittest.main()
