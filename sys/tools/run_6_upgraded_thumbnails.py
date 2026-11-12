#!/usr/bin/env python3
"""Targeted runner to generate fresh Flow Native Thumbnails for the 6 upgraded channels."""

import logging
import sys
from pathlib import Path

# Add sys directory to sys.path
sys_dir = Path(__file__).resolve().parent.parent
if str(sys_dir) not in sys.path:
    sys.path.insert(0, str(sys_dir))

from tools.generate_sensational_thumbnails import generate_flow_native_thumbnails

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("run_6_upgraded")

TARGET_CHANNELS = [
    "co_the_ke",
    "ua_sao_vay",
    "banh_rang",
    "minh_triet_song",
    "loi_sang_soi",
    "tam_tinh_dem",
]

def main() -> None:
    logger.info(f"Starting regeneration of Flow Native Thumbnails for {len(TARGET_CHANNELS)} channels: {TARGET_CHANNELS}")
    results = generate_flow_native_thumbnails(
        channels=TARGET_CHANNELS,
        aspect="both",
        max_workers=2,
        force=True,
    )
    logger.info(f"Successfully generated {len(results)} thumbnails:")
    for k, p in sorted(results.items()):
        sz_kb = p.stat().st_size / 1024 if p.exists() else 0.0
        logger.info(f"  ✓ {k:30} -> {p} [{sz_kb:.1f} KB]")

if __name__ == "__main__":
    main()
