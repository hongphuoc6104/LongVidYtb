#!/usr/bin/env python3
"""Runner script to generate FHD+ 1080p Explainer images for banh_rang via Flow CDP pool."""
import json
import logging
import os
from pathlib import Path
import sys
import time

from sys.flow_cdp.process_manager import ProcessGroupManager
from sys.tools.produce_vn_dual_mode import dispatch_long_image_dag_via_pool

# Set up logging to file and console
work_long = Path("video/vn_pilot_banh_rang_long/_work_long")
log_file = work_long / "generate_images.log"
status_file = work_long / "generate_status.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("generate_banh_rang")

def update_status(status: str, extra: dict | None = None):
    data = {
        "status": status,
        "timestamp": time.time(),
        "time_str": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if extra:
        data.update(extra)
    status_file.write_text(json.dumps(data, indent=2))

def main():
    spec_path = Path("video/vn_pilot_banh_rang_long/banh_rang_long_aligned_spec.json")
    if not spec_path.is_file():
        logger.error(f"Spec file not found: {spec_path}")
        update_status("failed", {"error": f"Spec not found: {spec_path}"})
        sys.exit(1)

    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    beats = spec_data["beats"] if isinstance(spec_data, dict) else spec_data
    total_beats = len(beats)
    output_dir = work_long / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    allowed = {"profile_6", "profile_7", "profile_8", "profile_10", "profile_11", "profile_12"} | {f"profile_en{i:02d}" for i in range(10, 20)}
    allowed_profiles = sorted(list(allowed))
    
    # Check existing images
    existing_pngs = [p for p in output_dir.glob("img_*.png") if p.stat().st_size > 5000]
    logger.info(
        f"Starting Explainer image generation for banh_rang: {len(existing_pngs)}/{total_beats} already exist on disk."
    )
    update_status("running", {
        "total_beats": total_beats,
        "existing_on_disk": len(existing_pngs),
        "target_new": total_beats - len(existing_pngs),
        "allowed_profiles": allowed_profiles,
    })

    start_time = time.time()
    try:
        paths = dispatch_long_image_dag_via_pool(
            channel_slug="banh_rang",
            beats=beats,
            output_dir=output_dir,
            image_model="BELUGA",
            max_workers=3,
            allowed_profiles=allowed_profiles,
        )
        elapsed = time.time() - start_time
        final_pngs = [p for p in output_dir.glob("img_*.png") if p.stat().st_size > 5000]
        logger.info(
            f"Image generation finished in {elapsed:.1f}s. Total valid images: {len(final_pngs)}/{total_beats}"
        )
        update_status("completed", {
            "total_beats": total_beats,
            "final_count": len(final_pngs),
            "elapsed_seconds": elapsed,
        })
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"Error during image generation: {e}")
        update_status("failed", {
            "error": str(e),
            "elapsed_seconds": elapsed,
        })
        raise
    finally:
        logger.info("Cleaning up any remaining Chrome processes...")
        try:
            ProcessGroupManager().clean_orphans_from_registry()
        except Exception as exc:
            logger.warning(f"Error during clean_orphans_from_registry: {exc}")

if __name__ == "__main__":
    main()
