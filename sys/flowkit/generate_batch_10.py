#!/usr/bin/env python3
"""Generate the first 10 images for analytical-charlie-gordon-9x16-001 using Flow Kit."""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "analytical-charlie-gordon-9x16-001"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ITEMS = [
    {
        "id": "01_BG_SC01_9x16",
        "prompt": "Empty minimalist clinic consultation room with clean wooden desk and window light, pale cream walls, open floor space, no people, safe lower third for captions. Hand-drawn 2D marker-pen look, clean black outlines, flat soft colors.",
        "skip_if_exists": True
    },
    {
        "id": "02_STK_CHARLIE_HOPEFUL_9x16",
        "prompt": "One anonymous adult stick figure Charlie with large round white head, dot eyes, gentle hopeful smile, single stick torso, simple blue sweater, standing on pure white background with continuous closed black outline. Hand-drawn 2D marker-pen look, centered with generous margin, no shadow, no background scenery."
    },
    {
        "id": "03_STK_THOUGHT_FRIENDS_9x16",
        "prompt": "One small thought bubble containing two stick figures smiling and waving friendly hands, on pure white background with continuous closed black outline. Hand-drawn 2D marker-pen look, isolated graphic, no background."
    },
    {
        "id": "04_BG_SC02_9x16",
        "prompt": "Empty minimalist study room with tall tidy bookshelves, soft amber lighting, pale wood desk, open central floor, no people, safe lower third for captions. Hand-drawn 2D marker-pen look, clean black outlines, flat soft colors."
    },
    {
        "id": "05_STK_CHARLIE_STUDY_9x16",
        "prompt": "One anonymous adult stick figure Charlie wearing small spectacles, reading an open thick book with focused expression, round white head, stick torso, blue sweater, on pure white background with continuous closed black outline. Hand-drawn 2D marker-pen look."
    },
    {
        "id": "06_STK_BRAIN_GLOW_9x16",
        "prompt": "One radiant lightbulb brain icon with glowing energy rays pointing outward, on pure white background with continuous closed black outline. Hand-drawn 2D marker-pen look, vibrant yellow energy lines, isolated cut-out."
    },
    {
        "id": "07_BG_SC03_9x16",
        "prompt": "Empty industrial bakery workshop with clean marker outlines, pale gray-blue machines, flour sacks on floor, open space, no people, safe lower third for captions. Hand-drawn 2D marker-pen look, muted flat colors."
    },
    {
        "id": "08_STK_COWORKERS_MOCK_9x16",
        "prompt": "Group of two anonymous stick figures pointing fingers and laughing mockingly with open mouths, round white heads, work aprons, on pure white background with continuous closed black outline. Hand-drawn 2D marker-pen look."
    },
    {
        "id": "09_STK_CHARLIE_HURT_9x16",
        "prompt": "One anonymous stick figure Charlie with round white head looking down in shock and hurt realization, hand clutching chest, blue sweater, on pure white background with continuous closed black outline. Hand-drawn 2D marker-pen look."
    },
    {
        "id": "10_BG_SC04_9x16",
        "prompt": "Split composition empty city street: warm glowing shop windows on the right, cold twilight pavement on the left, clear vertical divide, no people, safe lower third for captions. Hand-drawn 2D marker-pen look, muted flat colors."
    }
]


def download_file(url: str, dest_path: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        dest_path.write_bytes(data)
        return len(data)


def main():
    print(f"=== Starting generation of {len(ITEMS)} images ===")
    manifest = []
    
    for i, item in enumerate(ITEMS, 1):
        target_id = item["id"]
        img_path = OUTPUT_DIR / f"{target_id}.jpg"
        meta_path = OUTPUT_DIR / f"{target_id}.json"
        
        if item.get("skip_if_exists") and img_path.is_file():
            print(f"[{i}/{len(ITEMS)}] {target_id}: Already exists ({img_path.stat().st_size} bytes). Skipping generation.")
            manifest.append({"id": target_id, "path": str(img_path), "status": "existing"})
            continue
            
        print(f"\n[{i}/{len(ITEMS)}] Generating {target_id}...")
        req_data = {
            "prompt": item["prompt"],
            "aspect_ratio": "IMAGE_ASPECT_RATIO_PORTRAIT",
            "image_model": "NANO_BANANA_2_LITE",
            "count": 1
        }
        
        req = urllib.request.Request(
            "http://127.0.0.1:8100/api/flow/generate-image",
            data=json.dumps(req_data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                dt = time.time() - t0
                
                media = (res.get("media") or [{}])[0]
                img_data = media.get("image", {}).get("generatedImage", {})
                media_id = img_data.get("mediaId")
                fife_url = img_data.get("fifeUrl")
                
                if fife_url:
                    bytes_len = download_file(fife_url, img_path)
                    meta_path.write_text(json.dumps({
                        "target_id": target_id,
                        "prompt": item["prompt"],
                        "media_id": media_id,
                        "fife_url": fife_url,
                        "file_size": bytes_len,
                        "latency_s": dt,
                        "timestamp": time.time()
                    }, indent=2), encoding="utf-8")
                    print(f"  ✓ SUCCESS in {dt:.2f}s! Saved {target_id}.jpg ({bytes_len} bytes, mediaId: {media_id})")
                    manifest.append({"id": target_id, "media_id": media_id, "path": str(img_path), "status": "ok"})
                else:
                    print(f"  ✗ Warning: No fifeUrl in response: {res}")
                    manifest.append({"id": target_id, "status": "no_url"})
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            print(f"  ✗ HTTP Error {e.code}: {err}")
            manifest.append({"id": target_id, "status": "error", "error": err})
            # If hit rate limit or cooldown, break to prevent cascading failures
            if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in err:
                print("  [ALERT] Hit PUBLIC_ERROR_UNUSUAL_ACTIVITY. Halting batch safely.")
                break
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            manifest.append({"id": target_id, "status": "exception", "error": str(e)})

        # Polite interval between generations
        if i < len(ITEMS):
            print("  Waiting 4.0s before next request...")
            time.sleep(4.0)

    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n=== Batch complete. Generated {len([m for m in manifest if m.get('status') in ('ok', 'existing')])}/{len(ITEMS)} images ===")


if __name__ == "__main__":
    main()
