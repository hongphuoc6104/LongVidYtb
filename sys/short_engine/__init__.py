"""Modular Turbo Serialized Short Engine (`sys/short_engine/`)."""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if not hasattr(sys, "__path__"):
    sys.__path__ = [str(SYS_DIR)]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from colab_bridge import accounts as colab_accounts  # noqa: E402
from colab_bridge.client import Client  # noqa: E402
from colab_bridge.pool_manager import ColabPoolManager  # noqa: E402
from colab_bridge.protocol import stamp  # noqa: E402

logger = logging.getLogger("produce_serialized_short")

FPS = 30
WIDTH = 1440
HEIGHT = 2560
SCALE_W = 1512
SCALE_H = 2688
POSTER_FRAMES = 4
HUD_MAX_WIDTH = 1140
TARGET_SR = 48000

VIETSUB_FONT_SIZE = 132
MIN_OVERLAY_FONT_SIZE = 132
MAX_OVERLAY_WORDS = 4


def text_tail(txt: str, limit: int = 600) -> str:
    """Return trailing characters of long log output for concise error messages."""
    return txt[-limit:] if len(txt) > limit else txt


def ffprobe_json(path: Path) -> dict[str, Any]:
    """Run ffprobe returning parsed stream and format metadata."""
    res = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,pix_fmt,nb_frames,sample_rate,channels",
            "-show_entries",
            "format=duration,size,bit_rate",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(res.stdout)


def measure_ebur128(path: Path) -> dict[str, float]:
    """Measure integrated LUFS and true peak (dBTP) using FFmpeg ebur128."""
    res = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    txt = (res.stdout or "") + "\n" + (res.stderr or "")
    summary = txt.rsplit("Summary:", 1)[-1]
    mi = re.search(r"I:\s+(-?\d+\.\d+)\s+LUFS", summary)
    mtp = re.search(r"Peak:\s+(-?\d+\.\d+)\s+dBFS", summary)
    if not mi or not mtp:
        raise RuntimeError(f"Could not parse ebur128 summary from {path}:\n{text_tail(txt)}")
    return {"integrated_lufs": float(mi.group(1)), "true_peak_dbtp": float(mtp.group(1))}


def select_idle_colab_accounts(
    session_name: str,
    *,
    max_accounts: int = 4,
    min_seconds: float = 450.0,
) -> list[str]:
    """Return genuinely idle, healthy, budget-verified Colab T4 accounts ordered by fast boot reliability."""
    pm = ColabPoolManager()
    st = pm.get_status(probe_server=False)
    probe_client = Client(SYS_DIR, {"colab_tts": {}})
    budgets = probe_client._budgets()
    aliases = budgets.read().get("aliases", {})
    excluded = {x.strip() for x in os.environ.get("VP_COLAB_EXCLUDE", "").split(",") if x.strip()}

    idle: list[str] = []
    for w in st["workers"]:
        acc = w["id"]
        if acc in excluded or w["state"] != "healthy" or w["external_lock_busy"] or w["local_sessions"]:
            continue
        alias = f"colab:{acc}"
        snap = budgets.snapshot(alias)
        ident = aliases.get(alias)
        j_path = budgets.path.parent / f"allocation-{stamp(ident)}.json" if ident else None
        j_phase = json.loads(j_path.read_text(encoding="utf-8")).get("phase") if (j_path and j_path.is_file()) else None
        budget_ok = (
            snap["identity_configured"]
            and not snap["blocks"].get("colab")
            and not snap["allocated_sessions"]
            and not snap["uncertain"]
            and not snap.get("needs_service_recheck")
            and float(snap["available_seconds"]) >= min_seconds
            and j_phase not in ("submitted", "ambiguous", "allocated")
        )
        if budget_ok:
            idle.append(acc)

    preferred_order = {
        "account-12": 0,
        "account-01": 1,
        "account-02": 2,
        "account-18": 3,
        "account-19": 4,
        "account-13": 5,
        "account-17": 6,
    }
    idle.sort(key=lambda a: (preferred_order.get(a, 50), a))

    verified: list[str] = []
    binary = pm.binary
    for acc in idle:
        try:
            asgn = colab_accounts.assignment_state(binary, acc, session_name, refresh_auth=True)
            if asgn.get("verified") is True and int(asgn.get("assignment_count", 1)) == 0:
                verified.append(acc)
        except Exception as err:
            logger.warning("[%s] Colab assignment probe skipped: %s", acc, err)
        if len(verified) >= max_accounts:
            break
    return verified[:max_accounts]
