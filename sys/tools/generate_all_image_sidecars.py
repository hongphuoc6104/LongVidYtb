#!/usr/bin/env python3
"""
Generates metadata .json sidecars for all generated images in Ancient Humans (Chapters 1-8).
Complies with vp-flow-cdp contract:
- {image_stem}.json alongside {image_stem}.jpg
- Contains jobId, filename, prompt, ratio, characters, source, status, forgeId, media_id
"""
import json
from pathlib import Path

BUNDLE_DIR = Path(__file__).resolve().parents[1] / "exports" / "ancient_humans_bundle"
GEN_DIR = BUNDLE_DIR / "generated_images"
MANIFEST_PATH = BUNDLE_DIR / "manifest" / "manifest_245_shots.json"
CH1_BLIND_PATH = BUNDLE_DIR / "manifest" / "ch1_blind_34_shots.json"
OPTION_B_PATH = BUNDLE_DIR / "manifest" / "manifest_option_b_full.json"

def main():
    # Build lookup dictionaries from manifests
    lookup_by_filename = {}
    lookup_by_shot_index = {}

    for m_path in [MANIFEST_PATH, CH1_BLIND_PATH, OPTION_B_PATH]:
        if m_path.is_file():
            try:
                m_data = json.loads(m_path.read_text(encoding="utf-8"))
                for s in m_data.get("shots", []):
                    fn = s.get("target_filename")
                    si = s.get("shot_index")
                    ch = s.get("chapter_number")
                    vd = s.get("visual_direction", {})
                    prompt = vd.get("ai_prompt") or vd.get("action_description") or ""
                    item = {
                        "shot_index": si,
                        "chapter_number": ch,
                        "filename": fn,
                        "prompt": prompt,
                        "remotion_effect": s.get("remotion_effect", "hold"),
                        "action_description": vd.get("action_description", "")
                    }
                    if fn:
                        lookup_by_filename[(ch, fn)] = item
                    if si:
                        lookup_by_shot_index[si] = item
            except Exception as e:
                print(f"Warning reading {m_path}: {e}")

    total_sidecars = 0
    for ch in range(1, 9):
        ch_dir = GEN_DIR / f"ch{ch}"
        if not ch_dir.is_dir():
            continue

        media_state = {}
        ms_file = ch_dir / "_media_state.json"
        if ms_file.is_file():
            try:
                media_state = json.loads(ms_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Build reverse lookup by filename from media_state
        ms_by_fn = {}
        for k, v in media_state.items():
            if isinstance(v, dict) and "filename" in v:
                ms_by_fn[v["filename"]] = v

        images = [f for f in ch_dir.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]]
        ch_sidecars = 0

        for img in images:
            sidecar_path = ch_dir / f"{img.stem}.json"
            meta_ms = ms_by_fn.get(img.name, {})
            manifest_info = lookup_by_filename.get((ch, img.name), {})

            shot_idx = manifest_info.get("shot_index") or meta_ms.get("shot_index") or img.stem
            prompt = manifest_info.get("prompt") or f"Stick figure illustration for Chapter {ch} {img.name}"
            media_id = meta_ms.get("media_id") or f"flow-ch{ch}-{shot_idx}"
            forge_id = meta_ms.get("project_id") or f"forge-ch{ch}-{shot_idx}"

            sidecar_data = {
                "jobId": f"ancient-humans-day-ch{ch}-16x9",
                "shot_index": shot_idx,
                "filename": img.name,
                "prompt": prompt,
                "ratio": "16:9",
                "characters": "stick_figure",
                "source": "flow_cdp",
                "status": "downloaded",
                "forgeId": forge_id,
                "media_id": media_id,
                "file_size_bytes": img.stat().st_size,
                "remotion_effect": manifest_info.get("remotion_effect", "hold")
            }

            sidecar_path.write_text(json.dumps(sidecar_data, indent=2, ensure_ascii=False), encoding="utf-8")
            ch_sidecars += 1
            total_sidecars += 1

        print(f"Chapter {ch}: Created/updated {ch_sidecars} sidecars for {len(images)} images.")

    print(f"\nTotal sidecars generated across all chapters: {total_sidecars}")

if __name__ == "__main__":
    main()
