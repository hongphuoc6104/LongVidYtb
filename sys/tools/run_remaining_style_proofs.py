#!/usr/bin/env python3
"""Run style proof generation for the 8 missing channels."""

import subprocess
import sys
from pathlib import Path

MISSING_CHANNELS = [
    ("en-first-principles", "0,1,2,3"),
    ("en-scale-and-bone", "4,5,6,7"),
    ("en-pocket-cosmos", "8,9,10,11"),
    ("en-deep-time-strata", "12,13,14,15"),
    ("en-inside-vessel", "16,17,18,19"),
    ("en-macro-gears", "20,21,22,23"),
    ("en-fine-print", "24,25,26,27"),
    ("en-wallet-anatomy", "28,29,30,31"),
]

BASE_DIR = Path("/home/hongphuoc6104/Desktop/vp-agent-core")
SPECS_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/style_proofs/specs")

def run_channel(channel: str, profiles: str):
    spec_file = SPECS_DIR / f"{channel}.json"
    if not spec_file.exists():
        print(f"Spec file not found: {spec_file}")
        return False
    cmd = [
        sys.executable,
        str(BASE_DIR / "sys/tools/channel_style_proof_worker.py"),
        "--channel", channel,
        "--profiles", profiles,
        "--spec-file", str(spec_file),
    ]
    print(f"Starting {channel} with profiles {profiles}...")
    res = subprocess.run(cmd, env={"PYTHONPATH": str(BASE_DIR / "sys")})
    return res.returncode == 0

if __name__ == "__main__":
    import concurrent.futures
    # Run with modest concurrency (2-3 channels at a time to prevent IP burst rate-limiting)
    print("Launching style proof generation for 8 remaining channels...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_channel, ch, prof): ch for ch, prof in MISSING_CHANNELS}
        for future in concurrent.futures.as_completed(futures):
            ch = futures[future]
            try:
                success = future.result()
                print(f"Finished {ch}: {'SUCCESS' if success else 'FAILED'}")
            except Exception as e:
                print(f"Error on {ch}: {e}")
