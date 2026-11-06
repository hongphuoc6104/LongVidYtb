#!/usr/bin/env python3
"""Build and validate full script specs for W-Prep-Squad-6 (Channels 16-18 Batch 1).

Channels:
16. en-lazy-brain:
    - Long 16:9: sys/channels/en_batch1_specs/en-lazy-brain_long_16x9.json
    - Short 9:16: sys/channels/en_batch1_specs/en-lazy-brain_short_9x16.json
17. en-career-leverage:
    - Long 16:9: sys/channels/en_batch1_specs/en-career-leverage_long_16x9.json
    - Short 9:16: sys/channels/en_batch1_specs/en-career-leverage_short_9x16.json
18. en-wallet-anatomy:
    - Long 16:9: sys/channels/en_batch1_specs/en-wallet-anatomy_long_16x9.json
    - Short 9:16: sys/channels/en_batch1_specs/en-wallet-anatomy_short_9x16.json
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

# Ensure sys directory is in python path
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from tools.data_en_batch1_lazy_brain import (
    get_lazy_brain_long_shots,
    get_lazy_brain_short_shots,
)
from tools.data_en_batch1_career_leverage import (
    get_career_leverage_long_shots,
    get_career_leverage_short_shots,
)
from tools.data_en_batch1_wallet_anatomy import (
    get_wallet_anatomy_long_shots,
    get_wallet_anatomy_short_shots,
)

SPECS_DIR = SYS_DIR / "channels/en_batch1_specs"
SPECS_DIR.mkdir(parents=True, exist_ok=True)


def build_all_specs() -> list[Path]:
    written_files: list[Path] = []

    # 1. en-lazy-brain
    lazy_long_shots = get_lazy_brain_long_shots()
    for s in lazy_long_shots:
        s["speech_rate"] = "+12%"

    lazy_long = {
        "job_id": "en-lazy-brain-batch1-16x9",
        "channel_slug": "en-lazy-brain",
        "aspect": "16:9",
        "voice": "en-US-AndrewNeural",
        "title": "The Dopamine Baseline Paradox: Why Your Brain Procrastinates on High-Value Goals (And How to Reset It)",
        "youtube_title": "Why Your Brain Loves to Procrastinate",
        "thumbnail_spec": {
            "visual_hook": "Vivid flat-shaded neuroscience diagram of a dopamine balance scale tipped down by glowing notification icons against a blank work desk",
            "allowed_text": "DOPAMINE TRAP",
            "overlay_card": False,
        },
        "shots": lazy_long_shots,
    }
    p_lazy_long = SPECS_DIR / "en-lazy-brain_long_16x9.json"
    p_lazy_long.write_text(json.dumps(lazy_long, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written_files.append(p_lazy_long)

    lazy_short = {
        "job_id": "en-lazy-brain-batch1-9x16",
        "parent_long_id": "en-lazy-brain-batch1-16x9",
        "channel_slug": "en-lazy-brain",
        "aspect": "9:16",
        "voice": "en-US-AndrewNeural",
        "title": "Cheap Dopamine First: Why Checking Your Phone for 3 Minutes Wrecks 3 Hours of Focus",
        "youtube_title": "How 3 Minutes of Scrolling Wrecks Focus",
        "shots": get_lazy_brain_short_shots(),
    }
    p_lazy_short = SPECS_DIR / "en-lazy-brain_short_9x16.json"
    p_lazy_short.write_text(json.dumps(lazy_short, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written_files.append(p_lazy_short)

    # 2. en-career-leverage
    career_long_shots = get_career_leverage_long_shots()
    for s in career_long_shots:
        s["speech_rate"] = "+18%"

    career_long = {
        "job_id": "en-career-leverage-batch1-16x9",
        "channel_slug": "en-career-leverage",
        "aspect": "16:9",
        "voice": "en-US-RogerNeural",
        "title": "The Peter Principle & Asymmetric Leverage: Why the Hardest Worker Rarely Gets Promoted",
        "youtube_title": "Why the Hardest Worker Rarely Gets Promoted",
        "thumbnail_spec": {
            "visual_hook": "Architectural corporate strategy diagram showing an overloaded brass gear at the bottom while a tiny fulcrum lever lifts the top executive platform",
            "allowed_text": "WORK VS LEVERAGE",
            "overlay_card": False,
        },
        "shots": career_long_shots,
    }
    p_career_long = SPECS_DIR / "en-career-leverage_long_16x9.json"
    p_career_long.write_text(json.dumps(career_long, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written_files.append(p_career_long)

    career_short_shots = get_career_leverage_short_shots()
    for s in career_short_shots:
        s["speech_rate"] = "+10%"

    career_short = {
        "job_id": "en-career-leverage-batch1-9x16",
        "parent_long_id": "en-career-leverage-batch1-16x9",
        "channel_slug": "en-career-leverage",
        "aspect": "9:16",
        "voice": "en-US-RogerNeural",
        "title": "Output vs. Visibility: The Quiet Reason High Performers Get Passed Over for Promotion",
        "youtube_title": "Why High Performers Get Passed Over",
        "shots": career_short_shots,
    }
    p_career_short = SPECS_DIR / "en-career-leverage_short_9x16.json"
    p_career_short.write_text(json.dumps(career_short, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written_files.append(p_career_short)

    # 3. en-wallet-anatomy
    wallet_long_shots = get_wallet_anatomy_long_shots()
    for s in wallet_long_shots:
        s["speech_rate"] = "+10%"

    wallet_long = {
        "job_id": "en-wallet-anatomy-batch1-16x9",
        "channel_slug": "en-wallet-anatomy",
        "aspect": "16:9",
        "voice": "en-US-AndrewNeural",
        "title": "The Diderot Spiral & Frictionless Debt: Why Earning More Money Rarely Makes You Wealthy",
        "youtube_title": "Why Earning More Rarely Makes You Rich",
        "thumbnail_spec": {
            "visual_hook": "Tactile studio mechanical brass cash register spiraling upward into a domino chain of luxury tags draining a glass vault",
            "allowed_text": "THE INCOME TRAP",
            "overlay_card": False,
        },
        "shots": wallet_long_shots,
    }
    p_wallet_long = SPECS_DIR / "en-wallet-anatomy_long_16x9.json"
    p_wallet_long.write_text(json.dumps(wallet_long, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written_files.append(p_wallet_long)

    wallet_short = {
        "job_id": "en-wallet-anatomy-batch1-9x16",
        "parent_long_id": "en-wallet-anatomy-batch1-16x9",
        "channel_slug": "en-wallet-anatomy",
        "aspect": "9:16",
        "voice": "en-US-AndrewNeural",
        "title": "Pain of Paying: How Tap-to-Pay Quietly Disables Your Brain's Spending Brake",
        "youtube_title": "How Tap-to-Pay Turns Off Your Spending Brake",
        "shots": get_wallet_anatomy_short_shots(),
    }
    p_wallet_short = SPECS_DIR / "en-wallet-anatomy_short_9x16.json"
    p_wallet_short.write_text(json.dumps(wallet_short, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written_files.append(p_wallet_short)

    for p in written_files:
        print(f"[✓] Written {p} ({p.stat().st_size} bytes)")

    return written_files


if __name__ == "__main__":
    build_all_specs()
