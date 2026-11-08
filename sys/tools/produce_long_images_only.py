#!/usr/bin/env python3
"""Dedicated runner to pre-generate 240-350 BELUGA 16:9 images via Flow CDP pool without running TTS or NVENC."""
import argparse
import json
import logging
from pathlib import Path
from sys.tools.produce_vn_dual_mode import (
    dispatch_long_image_dag_via_pool,
    resolve_beat_transition,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_long_images")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--channel", default="ho-so-ky-la")
    parser.add_argument("--profiles", default=None)
    parser.add_argument("--max-workers", type=int, default=6)
    args = parser.parse_args()

    spec_data = json.loads(args.spec.read_text(encoding="utf-8"))
    raw_beats = spec_data.get("beats", [])
    beats = []
    for idx, b in enumerate(raw_beats):
        beats.append({
            "beat_id": b.get("beat_id") or b.get("id", f"B{idx:03d}"),
            "based_on": b.get("based_on"),
            "prompt": b.get("prompt") or b.get("prompt_spec", ""),
            "duration": float(b.get("duration") or b.get("hold") or 2.6),
            "camera_motion": b.get("camera_motion") or b.get("camera_move", "push_in"),
            "transition": resolve_beat_transition(b, idx),
            "narration": b.get("narration", f"Phân đoạn {idx + 1}"),
            "chapter_index": b.get("chapter_index", (idx // 30) + 1),
            "event_kind": b.get("event_kind", "ANCHOR_ESTABLISH"),
        })

    profiles = [p.strip() for p in args.profiles.split(",") if p.strip()] if args.profiles else None
    images_dir = args.out_dir / "_work_long" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Dispatching {len(beats)} images to {images_dir} with {args.max_workers} workers...")
    paths = dispatch_long_image_dag_via_pool(
        channel_slug=args.channel,
        beats=beats,
        output_dir=images_dir,
        image_model="BELUGA",
        max_workers=args.max_workers,
        allowed_profiles=profiles,
    )
    logger.info(f"Done! {len(paths)} images produced.")


if __name__ == "__main__":
    main()
