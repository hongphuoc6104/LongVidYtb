#!/usr/bin/env python3
"""Clean proof generator using verified active profiles."""

import json
import logging
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flow_cdp.persistent_pool import PersistentWorkerPool
from flow_cdp.cdp_direct_client import PROFILES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("clean_proofs")

TARGET_SIZE = (1080, 1920)
BASE_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f")
SPECS_DIR = BASE_DIR / "style_proofs/specs"
PROOFS_DIR = BASE_DIR / "style_proofs"

MISSING_CHANNELS = [
    "en-first-principles", "en-scale-and-bone", "en-pocket-cosmos", 
    "en-deep-time-strata", "en-inside-vessel", "en-macro-gears", 
    "en-fine-print", "en-wallet-anatomy"
]

# Verified authenticated profiles
ACTIVE_PROFILE_NAMES = [
    "profile_1", "profile_4", "profile_5", "profile_6", "profile_8",
    "profile_11", "profile_12", "profile_14", "profile_18", "profile_19"
]
active_profiles = [p for p in PROFILES if p["name"] in ACTIVE_PROFILE_NAMES]

def update_gallery():
    """Update selection gallery markdown."""
    out_path = BASE_DIR / "style_proofs_selection_gallery.md"
    channels_order = [
        "en-bamboo-marble", "en-career-leverage", "en-choke-point", "en-cold-case-ink",
        "en-crowd-strings", "en-kindred-sketch", "en-lazy-brain", "en-root-and-canopy",
        "en-second-arrow", "en-spawn-to-apex", "en-first-principles", "en-scale-and-bone",
        "en-pocket-cosmos", "en-deep-time-strata", "en-inside-vessel", "en-macro-gears",
        "en-fine-print", "en-wallet-anatomy"
    ]
    lines = [
        "# Bảng Thư Viện Lựa Chọn Phong Cách 18 Kênh (Đối Thủ Thực Tế Trên YouTube)",
        "",
        "> [!IMPORTANT]",
        "> **HƯỚNG DẪN CHỌN PHONG CÁCH CHO TỪNG KÊNH**:",
        "> - Mỗi kênh đều được thiết kế **4 phong cách trực quan ứng với 4 kênh đối thủ lớn nhất trên YouTube**.",
        "> - Hình ảnh hiển thị dưới đây là **ảnh thật được tạo trực tiếp từ Google Flow CDP** (tỷ lệ 9:16 dọc full-bleed).",
        "> - Bạn chỉ cần xem carousel và chọn phong cách bạn ưng ý nhất cho từng kênh (Ví dụ: `en-bamboo-marble: Style 1`, `en-choke-point: Style 1 (RealLifeLore)`, v.v.).",
        "",
    ]
    for idx, ch in enumerate(channels_order, 1):
        spec_file = SPECS_DIR / f"{ch}.json"
        if not spec_file.exists(): continue
        with open(spec_file) as f: spec = json.load(f)
        niche = spec.get("niche", "")
        scene_desc = spec.get("scene_description", "")
        styles = spec.get("styles", {})
        ch_proofs_dir = PROOFS_DIR / ch
        lines.append("---")
        lines.append(f"## {idx}. `{ch}` — {niche}")
        lines.append(f"**📖 Kịch bản cảnh mẫu**: *{scene_desc}*")
        lines.append("")
        existing_images = []
        for sk in ["style_1", "style_2", "style_3", "style_4"]:
            img_path = ch_proofs_dir / f"proof_{sk}.jpg"
            if img_path.exists() and img_path.stat().st_size > 2000:
                sinfo = styles.get(sk, {})
                cname = sinfo.get("competitor", sk)
                sname = sinfo.get("style_name", "")
                existing_images.append((img_path, f"{cname} — {sname}"))
        if existing_images:
            lines.append("### 📸 Ảnh Thật Tạo Từ Flow CDP (4 Phong Cách Ứng Cử Viên):")
            lines.append("")
            lines.append("````carousel")
            for i, (ip, cap) in enumerate(existing_images):
                if i > 0: lines.append("<!-- slide -->")
                lines.append(f"![Style {i+1}: {cap}]({ip})")
            lines.append("````")
            lines.append("")
        else:
            lines.append("*(Đang tiến hành kết xuất ảnh Flow cho các phong cách ứng viên...)*")
            lines.append("")
        lines.append("### 🎨 Chi Tiết 4 Phong Cách Đối Thủ Đề Xuất:")
        lines.append("")
        lines.append("| Lựa chọn | Kênh Đối Thủ Tham Chiếu | Tên Phong Cách Thẩm Mỹ |")
        lines.append("| :---: | :--- | :--- |")
        for sk_idx, sk in enumerate(["style_1", "style_2", "style_3", "style_4"], 1):
            sinfo = styles.get(sk, {})
            cname = sinfo.get("competitor", "")
            sname = sinfo.get("style_name", "")
            lines.append(f"| **Style {sk_idx}** | **{cname}** | {sname} |")
        lines.append("")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

def main():
    pool = PersistentWorkerPool(
        target_workers=3,
        headless=True,
        profiles=active_profiles,
        cooldown_seconds=30.0,
        pacing_seconds=4.0
    )
    
    tasks = []
    task_map = {}
    for ch in MISSING_CHANNELS:
        spec_file = SPECS_DIR / f"{ch}.json"
        if not spec_file.exists(): continue
        with open(spec_file) as f: spec = json.load(f)
        ch_dir = PROOFS_DIR / ch
        ch_dir.mkdir(parents=True, exist_ok=True)
        for sk, sval in spec.get("styles", {}).items():
            dest_jpg = ch_dir / f"proof_{sk}.jpg"
            if dest_jpg.exists() and dest_jpg.stat().st_size > 2000:
                continue
            tid = f"{ch}_{sk}"
            t = {
                "id": tid,
                "jobId": tid,
                "prompt": sval["prompt"],
                "ratio": "9:16",
                "aspect": "9:16",
                "model": "BELUGA",
                "filename": f"proof_{sk}.png",
                "out_dir": str(ch_dir),
                "credit_cost": 1,
                "credit_reason": "image",
                "editorial_overlay": {"enabled": False}
            }
            tasks.append(t)
            task_map[tid] = (ch, sk, dest_jpg, ch_dir / f"proof_{sk}.png")
            
    logger.info(f"Total missing proof tasks to generate: {len(tasks)}")
    if not tasks:
        logger.info("All proof images already generated!")
        update_gallery()
        return

    logger.info(f"Starting pool with {len(active_profiles)} active profiles...")
    pool.start()
    # Submit tasks and wait
    for t in tasks:
        pool.submit_task(t)
        
    logger.info("Tasks submitted. Waiting for completion...")
    pool.wait_completion(timeout=600.0)
    pool.shutdown()
    # Final pass conversion
    for tid, (ch, sk, dest_jpg, png_p) in task_map.items():
        if png_p.exists() and not dest_jpg.exists():
            try:
                with Image.open(png_p) as im:
                    rgb = im.convert("RGB")
                    resized = rgb.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                    resized.save(dest_jpg, format="JPEG", quality=95)
            except Exception as e:
                pass
    update_gallery()
    logger.info("Done generating remaining style proofs!")

if __name__ == "__main__":
    main()
