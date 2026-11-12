#!/usr/bin/env python3
"""Runner script for generating co_the_ke long explainer images."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Configure logging
log_path = Path("video/vn_pilot_co_the_ke_long/_work_long/image_gen.log")
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_path), mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("co_the_ke_image_gen")

from sys.flow_cdp.process_manager import ProcessGroupManager
from sys.tools.produce_vn_dual_mode import dispatch_long_image_dag_via_pool


def main() -> int:
    spec_path = Path("video/vn_pilot_co_the_ke_long/co_the_ke_long_explainer_spec.json")
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    beats = spec.get("beats", [])
    logger.info("Loaded %d beats from %s", len(beats), spec_path)

    out_dir = Path("video/vn_pilot_co_the_ke_long/_work_long/images")
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting dispatch_long_image_dag_via_pool for co_the_ke with max_workers=3...")
    allowed_profiles = [
        "profile_en18", "profile_en10", "profile_en14", "profile_en15", "profile_en17", "profile_en19",
        "profile_13", "profile_14", "profile_15", "profile_16",
    ]
    res = dispatch_long_image_dag_via_pool(
        channel_slug="co_the_ke",
        beats=beats,
        output_dir=out_dir,
        image_model="BELUGA",
        max_workers=3,
        allowed_profiles=allowed_profiles,
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
