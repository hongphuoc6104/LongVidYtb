"""Compatibility re-export shim for the canonical scripts.visual_quality module."""
from __future__ import annotations

import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from scripts.visual_quality import *  # noqa: E402, F401, F403
from scripts.visual_quality import (  # noqa: E402, F401
    _NARRATIVE_PHASE_PATTERNS,
    _PHASE_NAME_INDEX,
    _SETTING_ALIASES,
)
