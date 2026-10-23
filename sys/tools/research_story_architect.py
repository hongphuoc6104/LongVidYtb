"""Compatibility re-export shim for content.research_story_architect."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from content.research_story_architect import *  # noqa: F401, F403

if __name__ == "__main__":
    runpy.run_module("content.research_story_architect", run_name="__main__")
