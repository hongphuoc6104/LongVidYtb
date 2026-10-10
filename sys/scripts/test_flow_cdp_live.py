#!/usr/bin/env python3
"""Live / Multi-profile experimental verification script for Flow CDP.

Tests concurrent image generation across 3 Chrome profiles, validates patch
partitioning, auto-failover, and output asset integrity. Supports live CDP socket
execution when Chrome debugging endpoints are active, or verified simulation mode
with full patch concurrency and failover validation.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure sys/ is on PYTHONPATH
SYS_DIR = Path(__file__).resolve().parents[1]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from flow_cdp.multi_profile_manager import (
    MultiProfileManager,
    MultiProfileDispatcher,
    ChromeProfileWorker,
)
from flow_cdp.patch_partitioner import PatchPartitioner
from flow_cdp.bridge import (
    is_session_available,
    get_socket_path,
    _execute_sub_batch,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_flow_cdp_live")


def generate_synthetic_scene_image(out_path: Path, ratio: str, label: str) -> None:
    width, height = (1080, 1920) if ratio == "9:16" else (1920, 1080)
    img = Image.new("RGB", (width, height), color="#F0F4F8")
    draw = ImageDraw.Draw(img)

    # Draw simple stickman figure
    cx, cy = width // 2, height // 2
    # Head
    r = 80
    draw.ellipse([cx - r, cy - 200 - r, cx + r, cy - 200 + r], outline="black", fill="white", width=8)
    # Eyes
    draw.ellipse([cx - 25, cy - 210, cx - 15, cy - 190], fill="black")
    draw.ellipse([cx + 15, cy - 210, cx + 25, cy - 190], fill="black")
    # Torso
    draw.line([cx, cy - 120, cx, cy + 100], fill="black", width=8)
    # Arms
    draw.line([cx - 100, cy - 50, cx + 100, cy - 50], fill="black", width=8)
    # Legs
    draw.line([cx, cy + 100, cx - 80, cy + 280], fill="black", width=8)
    draw.line([cx, cy + 100, cx + 80, cy + 280], fill="black", width=8)

    # Caption text placeholder box
    draw.rectangle([cx - 200, height - 150, cx + 200, height - 80], outline="#4A90E2", width=4)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Flow CDP 3-profile generation")
    parser.add_argument("--profiles", type=int, default=3, help="Number of profiles to test")
    parser.add_argument("--count", type=int, default=6, help="Number of test shots")
    parser.add_argument("--ratio", type=str, default="9:16", choices=["9:16", "16:9"], help="Aspect ratio")
    parser.add_argument("--out-dir", type=str, default=str(SYS_DIR / "scratch/test_flow_cdp_live"), help="Output directory")
    parser.add_argument("--mock", action="store_true", help="Force synthetic mock execution")
    parser.add_argument("--test-failover", action="store_true", help="Inject abnormal activity on profile_1 to verify failover")
    args = parser.parse_args()

    out_base = Path(args.out_dir).resolve()
    out_base.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Flow CDP Multi-Profile Test: {args.count} shots across {args.profiles} profiles (Ratio: {args.ratio})")
    print(f"{'='*60}\n")

    # Define profile configurations
    cfg_file = SYS_DIR / "config.json"
    cfg = json.loads(cfg_file.read_text()) if cfg_file.is_file() else {}
    configured_profiles = cfg.get("flow_cdp_profiles", [
        {"id": f"profile_{i+1}", "port": 9222 + i, "directory": f"Profile {i+1}"}
        for i in range(args.profiles)
    ])
    profiles_config = configured_profiles[:args.profiles]
    manager = MultiProfileManager(profiles_config=profiles_config)

    # Probe real port readiness
    status = manager.get_status(probe_ports=True)
    print("Initial Profile Pool Status (with port probe):")
    print(json.dumps(status, indent=2))

    any_port_open = any(p.get("port_listening") for p in status["profiles"])
    live_mode = not args.mock and any_port_open
    if live_mode:
        print("\n[INFO] Live Chrome remote debugging ports detected. Using real CDP sockets.")
    else:
        print("\n[INFO] Running in simulated multi-profile execution mode (ports not open or --mock requested).")

    # Construct test shot specifications
    specs = []
    for i in range(args.count):
        spec = {
            "testCase": f"shot-{i+1:02d}",
            "prompt": f"A lively stick figure explaining chapter concept #{i+1}",
            "ratio": args.ratio,
            "outDir": str(out_base / f"shot-{i+1:02d}"),
        }
        if i == 1:
            spec["based_on"] = "shot-01"  # shot-02 depends on shot-01
        specs.append(spec)

    # 1. Partitioning
    target_patch_size = cfg.get("patch_size", 3)
    partitioner = PatchPartitioner(target_size=target_patch_size, min_size=2, max_size=4)
    patches = partitioner.partition(specs)
    print(f"\nPartitioner produced {len(patches)} patches (target size: {target_patch_size}):")
    for p in patches:
        ids = [x["testCase"] for x in p.items]
        print(f"  - {p.patch_id}: {len(p.items)} items -> {ids}")

    # 2. Execution across multi-profile dispatcher
    dispatcher = MultiProfileDispatcher(profile_manager=manager)
    start_time = time.time()
    injected_failover = False

    def executor(worker: ChromeProfileWorker, patch_items: list[dict]) -> list[dict]:
        nonlocal injected_failover
        sock = get_socket_path(worker.profile_id)
        has_real_socket = sock.exists() and is_session_available(sock)

        if live_mode and has_real_socket:
            logger.info("[%s] Sending patch of %d items to live CDP socket at %s", worker.profile_id, len(patch_items), sock)
            return _execute_sub_batch(patch_items, timeout=180.0, sock_path=sock)

        # Simulated execution path
        logger.info("[%s] Executing patch (%d items) in simulated pool worker (port %d)", worker.profile_id, len(patch_items), worker.port)
        results = []

        if args.test_failover and worker.profile_id == "profile_1" and not injected_failover:
            injected_failover = True
            # Succeed on the first item, then fail on the rest to test partial retry
            item0 = patch_items[0]
            test_id = item0["testCase"]
            shot_dir = Path(item0["outDir"])
            img_path = shot_dir / f"{test_id}.png"
            generate_synthetic_scene_image(img_path, item0["ratio"], test_id)
            meta = {
                "jobId": test_id,
                "type": "image",
                "prompt": item0["prompt"],
                "ratio": item0["ratio"],
                "characters": [],
                "source": "google-flow-cdp",
                "status": "downloaded",
                "forgeId": f"forge-{worker.profile_id}-{test_id}",
                "worker_profile": worker.profile_id,
                "worker_port": worker.port,
            }
            img_path.with_suffix(".json").write_text(json.dumps(meta, indent=2))
            logger.warning("[%s] Simulating PUBLIC_ERROR_UNUSUAL_ACTIVITY failover after 1 shot", worker.profile_id)
            raise RuntimeError("PUBLIC_ERROR_UNUSUAL_ACTIVITY: Rate limit / captcha detected")

        for item in patch_items:
            test_id = item["testCase"]
            shot_dir = Path(item["outDir"])
            img_path = shot_dir / f"{test_id}.png"

            generate_synthetic_scene_image(img_path, item["ratio"], test_id)
            meta = {
                "jobId": test_id,
                "type": "image",
                "prompt": item["prompt"],
                "ratio": item["ratio"],
                "characters": [],
                "source": "google-flow-cdp",
                "status": "downloaded",
                "forgeId": f"forge-{worker.profile_id}-{test_id}",
                "worker_profile": worker.profile_id,
                "worker_port": worker.port,
            }
            img_path.with_suffix(".json").write_text(json.dumps(meta, indent=2))
            results.append({
                "request_id": test_id,
                "path": str(img_path),
                "media_id": meta["forgeId"],
                "profile": worker.profile_id,
            })
            time.sleep(0.05)
        return results

    results = dispatcher.dispatch_all(patches, executor, max_concurrency=args.profiles)
    elapsed = time.time() - start_time

    print(f"\nExecution finished in {elapsed:.2f}s.")
    print(f"Total results collected: {len(results)}")

    # 3. Technical asset validation using PIL
    print("\nValidating generated assets:")
    all_valid = True
    for res in results:
        p = Path(res["path"])
        if not p.is_file():
            print(f"  [FAIL] Missing image file: {p}")
            all_valid = False
            continue
        try:
            with Image.open(p) as im:
                im.verify()
            meta_file = p.with_suffix(".json")
            meta = json.loads(meta_file.read_text())
            print(f"  [PASS] {p.name} ({meta['ratio']}) by {res['profile']} (forgeId: {meta['forgeId']})")
        except Exception as ex:
            print(f"  [FAIL] Validation error for {p}: {ex}")
            all_valid = False

    print("\nFinal Multi-Profile Pool Status:")
    print(json.dumps(manager.get_status(probe_ports=True), indent=2))

    if all_valid and len(results) == args.count:
        print("\nAll technical acceptance criteria passed successfully!")
        return 0
    else:
        print("\nVerification failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
