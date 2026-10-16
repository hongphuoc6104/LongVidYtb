"""Contract tests for the vp-colab-bridge skill and its progressive disclosure references."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / ".agents" / "skills" / "vp-colab-bridge"


class ColabBridgeSkillTests(unittest.TestCase):
    def test_skill_and_reference_files_exist(self) -> None:
        skill_md = SKILL_DIR / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "vp-colab-bridge/SKILL.md must exist")

        expected_refs = (
            "cli-and-accounts.md",
            "tts-omnivoice-worker.md",
            "remote-remotion-render.md",
            "error-recovery-matrix.md",
        )
        for ref_name in expected_refs:
            ref_path = SKILL_DIR / "references" / ref_name
            self.assertTrue(ref_path.is_file(), f"Missing reference file: {ref_name}")
            self.assertGreater(ref_path.stat().st_size, 500, f"Reference file too short: {ref_name}")

    def test_skill_frontmatter_and_mandatory_invariants(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: vp-colab-bridge\ndescription:"))

        mandatory_tokens = (
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--run-all-compositor-stages-before-draw",
            "--disable-gpu-rasterization",
            "DISABLE_FROM_SURFACE=true",
            "VP_CHROME_PATH",
            "chrome-wrapper.sh",
            "vn_text_normalizer.py",
            "line_boil",
            "reconcile",
            "collect",
            "reconcile-render-failure",
            "pool_manager.py",
            "pool-status",
            "pool-start",
            "pool-stop",
            "status-all",
            "select-idle",
            "auto-idle",
            "ERR-20261009-01",
            "ERR-20261009-02",
            "ERR-20261010-08",
            "ERR-20261010-10",
            "ERR-20261011-02",
        )
        for token in mandatory_tokens:
            self.assertIn(token, text, f"Missing mandatory token in SKILL.md: {token}")

    def test_error_recovery_matrix_covers_all_colab_error_codes(self) -> None:
        matrix_text = (SKILL_DIR / "references" / "error-recovery-matrix.md").read_text(encoding="utf-8")
        expected_error_codes = (
            "COLAB_CLI_MISSING",
            "COLAB_LOGIN_REQUIRED",
            "COLAB_SESSION_NOT_FOUND",
            "COLAB_ALLOCATION_PENDING",
            "COLAB_ASSIGNMENT_UNVERIFIED",
            "COLAB_LOCAL_SESSION_MAPPING_MISSING",
            "COLAB_RUNTIME_BINDING_INVALID",
            "COLAB_VERIFIED_SETUP_REQUIRED",
            "COLAB_PROVIDER_BLOCKED",
            "COLAB_TIMEOUT",
            "COLAB_EXEC_UNCONFIRMED",
            "COLAB_PENDING_OTHER_REQUEST",
            "COLAB_RECOVERY_LIMIT",
            "COLAB_FAILURE_UNVERIFIED",
            "COLAB_GPU_REQUIRED",
            "COLAB_T4_NOT_CONFIRMED",
            "Colab reference does not match current",
            "COLAB_GPU_OOM",
        )
        for code in expected_error_codes:
            self.assertIn(code, matrix_text, f"Error code missing from error-recovery-matrix.md: {code}")

    def test_all_relative_markdown_links_in_skill_resolve(self) -> None:
        for md_path in SKILL_DIR.rglob("*.md"):
            content = md_path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", content):
                clean = target.strip("<>").split("#", 1)[0]
                if not clean or re.match(r"^[A-Za-z]+:", clean):
                    continue
                resolved = (md_path.parent / clean).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"Broken link in {md_path.relative_to(ROOT)}: {target} -> {resolved}",
                )


if __name__ == "__main__":
    unittest.main()
