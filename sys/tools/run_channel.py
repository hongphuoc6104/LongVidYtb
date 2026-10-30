#!/usr/bin/env python3
"""Convenience alias for sys/tools/run_channel_video.py."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runner = Path(__file__).resolve().parent / "run_channel_video.py"
    runpy.run_path(str(runner), run_name="__main__")
