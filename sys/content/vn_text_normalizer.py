"""Forwarding module for vn_text_normalizer living in sys/tools/."""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from vn_text_normalizer import *  # noqa: F401, F403
from vn_text_normalizer import (  # noqa: F401
    FOREIGN_NAMES_MAP,
    detect_unnormalized_tokens,
    enforce_tts_normalization_gate,
    normalize_for_tts,
    num_to_vn_words,
    split_utterances_by_pause,
)
