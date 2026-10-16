#!/usr/bin/env python3
"""Test Suite: Verification of Tooling Stack and System Readiness."""

import re
import shutil
import subprocess
import sys
from pathlib import Path


def test_python_and_venv_runtime():
    """Verify that Python 3.11+ is active and sys/.venv exists."""
    assert sys.version_info >= (3, 11), f"Python version must be >= 3.11, got {sys.version_info}"
    repo_root = Path(__file__).resolve().parents[2]
    venv_dir = repo_root / "sys/.venv"
    assert venv_dir.is_dir(), f"Expected virtual environment at {venv_dir}"
    venv_python = venv_dir / "bin/python"
    assert venv_python.is_file(), f"Expected python binary inside venv at {venv_python}"


def test_ruff_linter_availability():
    """Verify that ruff linter is accessible and executable."""
    repo_root = Path(__file__).resolve().parents[2]
    venv_ruff = repo_root / "sys/.venv/bin/ruff"
    ruff_bin = str(venv_ruff) if venv_ruff.is_file() else shutil.which("ruff")
    assert ruff_bin is not None, "ruff executable not found in venv or system PATH"

    res = subprocess.run([ruff_bin, "--version"], capture_output=True, text=True)
    assert res.returncode == 0, f"ruff --version failed: {res.stderr}"
    assert "ruff" in res.stdout.lower(), f"Unexpected output from ruff: {res.stdout}"


def test_pytest_availability():
    """Verify that pytest is available in the current environment."""
    pytest_bin = shutil.which("pytest")
    assert pytest_bin is not None, "pytest binary not found in PATH"
    res = subprocess.run([pytest_bin, "--version"], capture_output=True, text=True)
    assert res.returncode == 0, f"pytest --version failed: {res.stderr}"
    assert "pytest" in res.stdout.lower(), f"Unexpected pytest output: {res.stdout}"


def test_git_vcs_and_remote():
    """Verify git executable and clean repository setup."""
    git_bin = shutil.which("git")
    assert git_bin is not None, "git executable not found in PATH"
    repo_root = Path(__file__).resolve().parents[2]
    res = subprocess.run([git_bin, "status"], cwd=str(repo_root), capture_output=True, text=True)
    assert res.returncode == 0, f"git status failed: {res.stderr}"


def test_media_tools_readiness():
    """Verify that ffprobe, ffmpeg, and node are installed."""
    for tool in ["ffmpeg", "ffprobe", "node"]:
        tool_bin = shutil.which(tool)
        assert tool_bin is not None, f"Tool '{tool}' not found in PATH"
        res = subprocess.run([tool_bin, "-version" if "ff" in tool else "--version"], capture_output=True, text=True)
        assert res.returncode == 0, f"{tool} version check failed: {res.stderr}"


def test_treehouse_and_axi_tools_readiness():
    """Verify treehouse, gh-axi, and lavish-axi binaries and configuration."""
    repo_root = Path(__file__).resolve().parents[2]
    th_cfg = repo_root / "treehouse.json"
    assert th_cfg.is_file(), f"treehouse.json configuration missing at {th_cfg}"

    for axi_tool in ["treehouse", "gh-axi", "lavish-axi"]:
        tool_bin = shutil.which(axi_tool)
        assert tool_bin is not None, f"Expected {axi_tool} binary in PATH"
        res = subprocess.run([tool_bin, "--version"], capture_output=True, text=True)
        assert res.returncode == 0, f"{axi_tool} version check failed: {res.stderr}"


def test_core_directory_and_doc_invariants():
    """Verify existence of mandatory files and layout single source of truth."""
    repo_root = Path(__file__).resolve().parents[2]
    for required_file in ["AGENTS.md", "PLAYBOOK.md", "pyproject.toml", "treehouse.json", "pipeline", "pilot.py"]:
        p = repo_root / required_file
        assert p.is_file(), f"Required file missing: {required_file}"

    for required_dir in ["sys", "sys/runs", "sys/logs/issues", "sys/tests", "sys/conveyor"]:
        d = repo_root / required_dir
        assert d.is_dir(), f"Required directory missing: {required_dir}"


def test_topic_to_video_skill_chain_and_token_budget():
    """Verify Topic-to-Video 6-skill orchestration chain, link integrity, and AGENTS.md token budget."""
    repo_root = Path(__file__).resolve().parents[2]
    agents_md = repo_root / "AGENTS.md"
    index_md = repo_root / "INDEX.md"
    prod_skill_md = repo_root / ".agents/skills/vp-production/SKILL.md"

    agents_text = agents_md.read_text(encoding="utf-8")
    agents_lines = agents_text.splitlines()
    assert len(agents_lines) <= 45, f"AGENTS.md exceeded compact line budget (got {len(agents_lines)} lines)"
    assert len(agents_text.encode("utf-8")) <= 4096, "AGENTS.md exceeded 4KB token-economy budget"

    core_skills = (
        "vp-research-architect",
        "vp-scriptwriting",
        "vp-production",
        "vp-flow-cdp",
        "vp-colab-bridge",
    )
    for skill_name in core_skills:
        assert skill_name in agents_text, f"AGENTS.md missing core skill in chain: {skill_name}"
        assert (repo_root / ".agents/skills" / skill_name / "SKILL.md").is_file(), f"Missing {skill_name}/SKILL.md"

    assert "outline -> dialogue -> audio -> images -> video" in agents_text
    assert "13m Explainer Blueprint" in agents_text

    prod_text = prod_skill_md.read_text(encoding="utf-8")
    for upstream_or_downstream in (
        "../vp-research-architect/SKILL.md",
        "../vp-scriptwriting/SKILL.md",
        "../vp-flow-cdp/SKILL.md",
        "../vp-colab-bridge/SKILL.md",
        "vocab/bank.py start",
    ):
        assert upstream_or_downstream in prod_text, f"vp-production/SKILL.md missing '{upstream_or_downstream}'"

    index_text = index_md.read_text(encoding="utf-8")
    for skill_name in core_skills:
        assert skill_name in index_text, f"INDEX.md missing routing entry for {skill_name}"
    assert "vp-layered-motion" not in agents_text
    assert "vp-layered-motion" not in index_text

    for md_path in (index_md, prod_skill_md):
        content = md_path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            clean = target.strip("<>").split("#", 1)[0]
            if not clean or re.match(r"^[A-Za-z]+:", clean):
                continue
            resolved = (md_path.parent / clean).resolve()
            assert resolved.exists(), f"Broken link in {md_path.name}: {target} -> {resolved}"
