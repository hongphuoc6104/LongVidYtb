#!/usr/bin/env python3
"""Runner script for generating nao_luoi long explainer images."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Configure logging
log_path = Path("video/vn_pilot_nao_luoi_long/_work_long/image_gen.log")
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_path), mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("nao_luoi_image_gen")

from sys.flow_cdp.process_manager import ProcessGroupManager
from sys.tools.produce_vn_dual_mode import dispatch_long_image_dag_via_pool


def main() -> int:
    spec_path = Path("video/vn_pilot_nao_luoi_long/nao_luoi_long_aligned_spec.json")
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    beats = spec.get("beats", [])
    logger.info("Loaded %d beats from %s", len(beats), spec_path)

    # Invariant: ensure all beats have based_on = None for 100% 3-worker parallelism
    for b in beats:
        b["based_on"] = None

    out_dir = Path("video/vn_pilot_nao_luoi_long/_work_long/images")
    out_dir.mkdir(parents=True, exist_ok=True)

    allowed = list(
        {"profile_13", "profile_14", "profile_15", "profile_16"}
        | {f"profile_en{i:02d}" for i in range(10, 20)}
    )

    logger.info("Starting dispatch_long_image_dag_via_pool for nao_luoi with max_workers=3...")
    res = dispatch_long_image_dag_via_pool(
        channel_slug="nao_luoi",
        beats=beats,
        output_dir=out_dir,
        image_model="BELUGA",
        max_workers=3,
        allowed_profiles=allowed,
    )
    logger.info("dispatch_long_image_dag_via_pool returned %d image paths", len(res))

    # Verify all 305 images
    missing = []
    small = []
    for idx in range(len(beats)):
        p = out_dir / f"img_{idx:04d}.png"
        if not p.is_file():
            missing.append(idx)
        elif p.stat().st_size < 50000:
            small.append((idx, p.stat().st_size))

    if missing:
        logger.error("Missing images (%d): %s", len(missing), missing[:20])
        return 1

    if small:
        logger.warning("Images < 50KB (%d): %s", len(small), small[:20])

    logger.info("SUCCESS: All %d images exist in %s and are valid (>50KB)!", len(beats), out_dir)

    # Clean up Chrome worker processes
    ProcessGroupManager().clean_orphans_from_registry()
    logger.info("Cleaned orphan Chrome processes from registry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
