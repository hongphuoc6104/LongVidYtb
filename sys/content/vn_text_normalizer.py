"""Forwarding module for vn_text_normalizer living in sys/tools/."""
from __future__ import annotations

import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))
TOOLS_DIR = SYS_DIR / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from tools.vn_text_normalizer import *  # noqa: F401, F403
from tools.vn_text_normalizer import (  # noqa: F401
    FOREIGN_NAMES_MAP,
    detect_unnormalized_tokens,
    enforce_tts_normalization_gate,
    normalize_for_tts,
    num_to_vn_words,
    split_utterances_by_pause,
)
