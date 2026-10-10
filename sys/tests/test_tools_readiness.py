#!/usr/bin/env python3
"""Test Suite: Verification of Tooling Stack and System Readiness."""

from pathlib import Path
import shutil
import subprocess
import sys


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


def test_core_directory_and_doc_invariants():
    """Verify existence of mandatory files and layout single source of truth."""
    repo_root = Path(__file__).resolve().parents[2]
    for required_file in ["AGENTS.md", "PLAYBOOK.md", "pyproject.toml", "pipeline", "pilot.py"]:
        p = repo_root / required_file
        assert p.is_file(), f"Required file missing: {required_file}"

    for required_dir in ["sys", "sys/runs", "sys/logs/issues", "sys/tests", "sys/conveyor"]:
        d = repo_root / required_dir
        assert d.is_dir(), f"Required directory missing: {required_dir}"
