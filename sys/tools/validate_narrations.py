#!/usr/bin/env python3
"""Draft and validate refreshed narrations for the 48 scenes."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sys"))
sys.path.insert(0, str(ROOT / "sys" / "tools"))

from script_cadence_checker import ScriptCadenceChecker, count_syllables, extract_pauses
from script_diversity_linter import lint_script
from build_study_motivation_history_13m import get_academic_sources

# Expected cue counts
EXPECTED_CUE_COUNTS = {
    'SC01': 5, 'SC02': 4, 'SC03': 4, 'SC04': 3, 'SC05': 3, 'SC06': 3,
    'SC07': 3, 'SC08': 3, 'SC09': 4, 'SC10': 3, 'SC11': 4, 'SC12': 2,
    'SC13': 4, 'SC14': 4, 'SC15': 3, 'SC16': 4, 'SC17': 4, 'SC18': 3,
    'SC19': 3, 'SC20': 3, 'SC21': 4, 'SC22': 3, 'SC23': 4, 'SC24': 3,
    'SC25': 3, 'SC26': 3, 'SC27': 4, 'SC28': 4, 'SC29': 3, 'SC30': 3,
    'SC31': 3, 'SC32': 3, 'SC33': 4, 'SC34': 3, 'SC35': 3, 'SC36': 3,
    'SC37': 3, 'SC38': 2, 'SC39': 3, 'SC40': 3, 'SC41': 4, 'SC42': 4,
    'SC43': 3, 'SC44': 4, 'SC45': 3, 'SC46': 3, 'SC47': 3, 'SC48': 3
}

TARGET_SYLLABLES = {
    # Ch1 (15.0s)
    'SC01': 54, 'SC02': 54, 'SC03': 54, 'SC04': 54, 'SC05': 54, 'SC06': 54,
    # Ch2 (17.5s)
    'SC07': 64, 'SC08': 64, 'SC09': 64, 'SC10': 64, 'SC11': 64, 'SC12': 64,
    # Ch3 (17.5s)
    'SC13': 64, 'SC14': 64, 'SC15': 64, 'SC16': 64, 'SC17': 64, 'SC18': 64,
    # Ch4 (17.5s)
    'SC19': 64, 'SC20': 64, 'SC21': 64, 'SC22': 64, 'SC23': 64, 'SC24': 64,
    # Ch5 (17.5s)
    'SC25': 64, 'SC26': 64, 'SC27': 64, 'SC28': 64, 'SC29': 64, 'SC30': 64,
    # Ch6 (17.5s)
    'SC31': 64, 'SC32': 64, 'SC33': 64, 'SC34': 64, 'SC35': 64, 'SC36': 64,
    # Ch7 (15.0s)
    'SC37': 54, 'SC38': 54, 'SC39': 54, 'SC40': 54, 'SC41': 54, 'SC42': 54,
    # Ch8 (12.5s)
    'SC43': 44, 'SC44': 44, 'SC45': 44, 'SC46': 44, 'SC47': 44, 'SC48': 45
}

def split_cues(text: str):
    import re
    cleaned = re.sub(r"\[pause:[^\]]+\]", " ", text)
    parts = [s.strip() for s in re.split(r"[.!?…]+", cleaned) if s.strip()]
    return parts

print("Validator module ready.")
