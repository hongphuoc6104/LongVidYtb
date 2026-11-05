#!/usr/bin/env python3
"""Build and validate Batch 3 packages for dia_com (dia-com-batch3-16x9 and dia-com-batch3-9x16)."""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from channels.registry import get_channel, channel_cast, channel_profile_stamp
from content.research_story_architect import compute_brief_hash
from tools.editorial_value_linter import lint_editorial_and_narrative_quality
from tools.script_diversity_linter import check_ai_cliche_phrases, check_intra_video_repetitions, lint_script
from tools.cta_tone_linter import lint_cta
from visual_pacing import audit_narrative_visual_density
from content_contract import validate_content, schema_errors

