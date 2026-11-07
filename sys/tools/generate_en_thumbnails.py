#!/usr/bin/env python3
"""High-CTR 16:9 YouTube Thumbnail Generator for English Batch 1 Fleet.

Requirements:
- Generates eye-catching, vibrant, high-contrast 16:9 thumbnails (1280x720, < 2 MB).
- Saves to BOTH:
    1. video/<job_id>/thumbnail.png
    2. sys/runs/en_batch1_prod/<job_id>/thumbnail.png
- Uses Flow CDP BELUGA (0 credits) on profile_4 (or an idle profile with ProfilePortLock)
  with the visual_hook + bold hand-lettered allowed_text (2-4 uppercase words in upper third,
  high contrast, zero programmatic UI card overlays per AGENTS.md §6).
- Includes deterministic high-contrast visual fallback from the job's anchor keyframe (S01_start.png)
  or extracted 16:9 video frame if Flow CDP ports are busy/offline, ensuring thumbnail.png is ALWAYS
  guaranteed to be created before Step 4 finishes in produce_en_flow_dynamic_demo.py.
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_cdp.cdp_direct_client import PROFILES
from sys.flow_cdp.resource_locks import ProfilePortLock, is_port_locked_by_another_process
from sys.flow_video.sparkle_unblend import clean_beluga_sparkle_pil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("generate_en_thumbnails")

BATCH1_SPECS_DIR = SYS_DIR / "channels" / "en_batch1_specs"
BATCH1_RUNS_DIR = SYS_DIR / "runs" / "en_batch1_prod"
VIDEO_DIR = REPO_ROOT / "video"
SYSTEM_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
    "/usr/share/fonts/fonts-go/Go-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def resolve_bold_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Find available bold system TTF font, fallback to default."""
    for p in SYSTEM_FONT_CANDIDATES:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, font_size)
            except Exception:
                pass
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def overlay_hand_lettered_text(
    im: Image.Image,
    allowed_text: str,
    target_width: int = 1280,
    target_height: int = 720,
) -> Image.Image:
    """Render bold hand-lettered uppercase text in the upper third (<=10% height, zero card overlays).

    Per AGENTS.md §6:
    - Upper third, <=10% height, 1-4 uppercase words in Flow image (zero overlays).
    - Bold outlined typography directly integrated onto canvas.
    - Yellow (#FFE600) with solid black (#000000) stroke and subtle shadow.
    """
    clean_text = " ".join(allowed_text.strip().upper().split())
    if not clean_text:
        return im

    # Work in RGB or RGBA
    out = im.convert("RGBA") if im.mode != "RGBA" else im.copy()
    draw = ImageDraw.Draw(out)

    max_h = int(target_height * 0.10)  # Max 10% height (72px for 720p)
    max_w = int(target_width * 0.82)   # Max 82% width
    font_size = 64
    stroke_w = 6

    font = resolve_bold_font(font_size)
    bbox = draw.textbbox((0, 0), clean_text, font=font, stroke_width=stroke_w)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # Dynamically scale down font if text overflows bounds
    while (tw > max_w or th > max_h) and font_size > 26:
        font_size -= 2
        font = resolve_bold_font(font_size)
        bbox = draw.textbbox((0, 0), clean_text, font=font, stroke_width=stroke_w)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

    # Upper third positioning: y ~ 11% to 14% of canvas height
    x = (target_width - tw) // 2 - bbox[0]
    y = int(target_height * 0.11) - bbox[1]

    # Subtle drop shadow for 3D depth on light backgrounds
    shadow_offset = 3
    draw.text(
        (x + shadow_offset, y + shadow_offset),
        clean_text,
        font=font,
        fill="#000000",
        stroke_width=stroke_w,
        stroke_fill="#000000",
    )

    # Ultra-vibrant primary hand-lettered text: #FFE600 (Kinetic Yellow) with thick black stroke
    draw.text(
        (x, y),
        clean_text,
        font=font,
        fill="#FFE600",
        stroke_width=stroke_w,
        stroke_fill="#000000",
    )

    return out.convert("RGB")


def find_spec_for_job(job_id_or_slug: str) -> tuple[str, str, Dict[str, Any]]:
    """Return (job_id, slug, spec_dict) matching given job_id or slug."""
    clean = job_id_or_slug.strip().replace("_", "-")
    slug = clean.replace("-batch1-16x9", "").replace("-batch1-9x16", "")
    job_id = f"{slug}-batch1-16x9"

    candidate_spec_names = [
        f"{slug}_long_16x9.json",
        f"{slug.replace('-', '_')}_long_16x9.json",
    ]
    spec_path: Optional[Path] = None
    for name in candidate_spec_names:
        p = BATCH1_SPECS_DIR / name
        if p.is_file():
            spec_path = p
            break

    if not spec_path:
        # Search all specs in BATCH1_SPECS_DIR
        for p in BATCH1_SPECS_DIR.glob("*_long_16x9.json"):
            if slug in p.name:
                spec_path = p
                break

    if not spec_path or not spec_path.is_file():
        raise FileNotFoundError(f"Could not find long_16x9 spec JSON for slug '{slug}' in {BATCH1_SPECS_DIR}")

    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)

    return job_id, slug, spec_data


def generate_fallback_thumbnail_from_assets(
    job_id: str,
    slug: str,
    allowed_text: str,
    target_width: int = 1280,
    target_height: int = 720,
) -> Image.Image:
    """Deterministic high-contrast visual fallback from anchor keyframes or final MP4."""
    base_img: Optional[Image.Image] = None

    # Priority 1: Extract 16:9 frame at 3s from rendered Long MP4 if available
    long_mp4 = VIDEO_DIR / job_id / f"{job_id}.mp4"
    if long_mp4.is_file() and long_mp4.stat().st_size > 1_000_000:
        try:
            tmp_png = tempfile.mktemp(suffix=".png")
            cmd = [
                "ffmpeg",
                "-y",
                "-ss",
                "00:00:03",
                "-i",
                str(long_mp4),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                tmp_png,
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=10)
            if os.path.isfile(tmp_png) and os.path.getsize(tmp_png) > 10_000:
                base_img = Image.open(tmp_png).convert("RGB")
                os.remove(tmp_png)
        except Exception as e:
            logger.debug("[%s] Failed to extract frame from MP4: %s", job_id, e)

    # Priority 2: 16:9 anchor keyframe S01_start.png in flow_chain/frames
    if base_img is None:
        kf_16 = BATCH1_RUNS_DIR / job_id / "flow_chain" / "frames" / "S01_start.png"
        if kf_16.is_file() and kf_16.stat().st_size > 10_000:
            try:
                base_img = Image.open(kf_16).convert("RGB")
            except Exception:
                base_img = None

    # Priority 3: Any valid 16:9 keyframe from flow_chain/frames/*.png
    if base_img is None:
        any_kfs_16 = sorted(glob.glob(str(BATCH1_RUNS_DIR / job_id / "flow_chain" / "frames" / "*.png")))
        for cand in any_kfs_16:
            if os.path.getsize(cand) > 10_000:
                try:
                    base_img = Image.open(cand).convert("RGB")
                    break
                except Exception:
                    continue

    # Priority 4: 9:16 Short anchor keyframe cropped/zoomed to full-bleed 16:9 widescreen
    if base_img is None:
        cand_9_paths = [
            BATCH1_RUNS_DIR / f"{slug}-batch1-9x16" / "flow_chain" / "frames" / "S01_start.png",
        ]
        any_kfs_9 = sorted(glob.glob(str(BATCH1_RUNS_DIR / f"{slug}-batch1-9x16" / "flow_chain" / "frames" / "*.png")))
        cand_9_paths.extend([Path(p) for p in any_kfs_9 if Path(p) not in cand_9_paths])
        for kf_9 in cand_9_paths:
            if kf_9.is_file() and kf_9.stat().st_size > 10_000:
                try:
                    src_9 = Image.open(kf_9).convert("RGB")
                    w, h = src_9.size
                    # Crop a clean full-bleed 16:9 widescreen horizontal slice centered on the
                    # upper-middle focal area (y from 18% to 50% of source height).
                    # Eliminates all blurred sidebars so the subject fills 100% of the 16:9 frame.
                    slice_h = int(round(w * (target_height / target_width)))
                    crop_y1 = int(round(h * 0.18))
                    if crop_y1 + slice_h > h:
                        crop_y1 = max(0, h - slice_h)
                    crop_y2 = min(h, crop_y1 + slice_h)

                    cropped = src_9.crop((0, crop_y1, w, crop_y2))
                    base_img = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    # Contrast and sharpness enhancement on the cropped slice
                    base_img = ImageEnhance.Contrast(base_img).enhance(1.10)
                    base_img = ImageEnhance.Sharpness(base_img).enhance(1.18)
                    break
                except Exception as e:
                    logger.debug("[%s] Failed to crop/zoom 9:16 keyframe %s: %s", job_id, kf_9, e)

    # Priority 5: Fallback clean gradient canvas
    if base_img is None:
        logger.warning("[%s] No keyframe assets found, generating stylized gradient canvas...", job_id)
        base_img = Image.new("RGB", (target_width, target_height), (22, 27, 34))
        draw_bg = ImageDraw.Draw(base_img)
        # Deep blue/slate subtle radial atmosphere
        for r in range(400, 0, -20):
            alpha_color = (25 + int(r * 0.05), 35 + int(r * 0.08), 55 + int(r * 0.12))
            draw_bg.ellipse(
                (target_width // 2 - r * 2, target_height // 2 - r, target_width // 2 + r * 2, target_height // 2 + r),
                fill=alpha_color,
            )

    # Standardize to target 1280x720 aspect ratio
    if base_img.size != (target_width, target_height):
        bw, bh = base_img.size
        # Center crop to 16:9 if aspect doesn't match
        target_aspect = target_width / target_height
        curr_aspect = bw / bh
        if abs(curr_aspect - target_aspect) > 0.02:
            if curr_aspect > target_aspect:
                new_w = int(bh * target_aspect)
                left = (bw - new_w) // 2
                base_img = base_img.crop((left, 0, left + new_w, bh))
            else:
                new_h = int(bw / target_aspect)
                top = (bh - new_h) // 2
                base_img = base_img.crop((0, top, bw, top + new_h))
        base_img = base_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Contrast & Color Vibrancy Boost (high-CTR thumbnail standard)
    enhanced = ImageEnhance.Contrast(base_img).enhance(1.22)
    enhanced = ImageEnhance.Color(enhanced).enhance(1.18)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.25)

    # Overlay bold hand-lettered uppercase text in upper third
    final_thumb = overlay_hand_lettered_text(
        enhanced,
        allowed_text=allowed_text,
        target_width=target_width,
        target_height=target_height,
    )
    return final_thumb


def try_flow_cdp_generation(
    job_id: str,
    slug: str,
    visual_hook: str,
    allowed_text: str,
    target_width: int = 1280,
    target_height: int = 720,
    preferred_profile: str = "profile_4",
    timeout_sec: float = 60.0,
) -> Optional[Image.Image]:
    """Attempt Flow CDP BELUGA image generation on profile_4 or first unlocked profile."""
    # Find candidate profile
    target_prof = next((p for p in PROFILES if p.get("name") == preferred_profile), None)
    if not target_prof or is_port_locked_by_another_process(target_prof.get("cdp_port", 0)):
        # Fallback to any unlocked profile
        for p in PROFILES:
            port = p.get("cdp_port", 0)
            if port and not is_port_locked_by_another_process(port):
                target_prof = p
                break

    if not target_prof:
        logger.info("[%s] All Flow CDP ports are currently busy/locked; using deterministic fallback.", job_id)
        return None

    port = int(target_prof.get("cdp_port", 0))
    port_lock = ProfilePortLock(port, owner_tag=f"thumb_{slug}")
    if not port_lock.try_acquire():
        logger.info("[%s] Port %d was locked during acquire; using deterministic fallback.", job_id, port)
        return None

    work_dir = Path(tempfile.mkdtemp(prefix=f"thumb_{slug}_"))
    try:
        from sys.flow_cdp.persistent_pool import PersistentWorkerPool

        flow_prompt = (
            f"Horizontal 16:9 YouTube video thumbnail, cinematic widescreen composition, dramatic lighting, "
            f"vibrant saturated colors, clean negative space. Visual scene: {visual_hook}. "
            f"Zero rectangular text cards, zero dark vignette, full bleed, 8k resolution."
        )

        raw_filename = f"{slug}_thumb_raw.png"
        task = {
            "id": f"thumb_{slug}",
            "jobId": f"thumb_{slug}",
            "prompt": flow_prompt,
            "ratio": "16:9",
            "aspect": "16:9",
            "model": "BELUGA",
            "filename": raw_filename,
            "out_dir": str(work_dir),
            "credit_cost": 0,
            "credit_reason": "image",
            "editorial_overlay": {"enabled": False},
        }

        logger.info("[%s] Submitting Flow CDP BELUGA image task on %s (port %d)...", job_id, target_prof.get("name"), port)
        pool = PersistentWorkerPool(
            target_workers=1,
            profiles=[target_prof],
            cooldown_seconds=15.0,
            pacing_seconds=1.0,
            stagger_seconds=1.0,
            headless=True,
            min_credits_required=0,
            enforce_os_locks=False,  # Already locked above
        )
        try:
            pool.start()
            pool.submit_task(task)
            pool.wait_completion(timeout=timeout_sec)
        finally:
            pool.shutdown()

        raw_path = work_dir / raw_filename
        if raw_path.is_file() and raw_path.stat().st_size > 10_000:
            with Image.open(raw_path) as raw_im:
                rgba = clean_beluga_sparkle_pil(raw_im.convert("RGBA"))
                # Resize to target
                resized = rgba.resize((target_width, target_height), Image.Resampling.LANCZOS)
                # Overlay crisp bold hand-lettered text in upper third
                final_im = overlay_hand_lettered_text(
                    resized.convert("RGB"),
                    allowed_text=allowed_text,
                    target_width=target_width,
                    target_height=target_height,
                )
                logger.info("[✓] [%s] Generated native Flow CDP thumbnail (%d bytes)", job_id, raw_path.stat().st_size)
                return final_im
    except Exception as ex:
        logger.warning("[%s] Flow CDP generation encountered error (%s); falling back to anchor keyframe.", job_id, ex)
    finally:
        port_lock.release()
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass

    return None


def generate_thumbnail_for_job(
    job_id_or_slug: str | None = None,
    *,
    job_id: str | None = None,
    force: bool = False,
    use_flow_cdp: bool = True,
) -> Path:
    """Generate high-CTR 16:9 thumbnail for a single job and save to BOTH video/ and sys/runs/."""
    target_id = job_id or job_id_or_slug
    if not target_id:
        raise ValueError("Must provide job_id or job_id_or_slug")
    job_id, slug, spec_data = find_spec_for_job(target_id)

    video_thumb = VIDEO_DIR / job_id / "thumbnail.png"
    run_thumb = BATCH1_RUNS_DIR / job_id / "thumbnail.png"

    # If both already exist and are valid (< 2 MB and > 20 KB), return video_thumb unless forced
    if (
        not force
        and video_thumb.is_file()
        and run_thumb.is_file()
        and 20_000 < video_thumb.stat().st_size < 2_000_000
        and 20_000 < run_thumb.stat().st_size < 2_000_000
    ):
        logger.info("[%s] Reusing valid existing thumbnail (%d bytes) -> %s", job_id, video_thumb.stat().st_size, video_thumb)
        return video_thumb

    thumb_spec = spec_data.get("thumbnail_spec", {})
    visual_hook = thumb_spec.get("visual_hook") or spec_data.get("title", "")
    allowed_text = thumb_spec.get("allowed_text") or "WATCH NOW"

    logger.info("[%s] Generating 16:9 thumbnail (hook=%r, text=%r)...", job_id, visual_hook[:40], allowed_text)

    thumb_img: Optional[Image.Image] = None

    # Step 1: Attempt Flow CDP if enabled
    if use_flow_cdp:
        thumb_img = try_flow_cdp_generation(
            job_id=job_id,
            slug=slug,
            visual_hook=visual_hook,
            allowed_text=allowed_text,
            target_width=1280,
            target_height=720,
            preferred_profile="profile_4",
            timeout_sec=25.0,
        )

    # Step 2: Deterministic fallback if Flow CDP didn't produce image
    if thumb_img is None:
        thumb_img = generate_fallback_thumbnail_from_assets(
            job_id=job_id,
            slug=slug,
            allowed_text=allowed_text,
            target_width=1280,
            target_height=720,
        )

    # Step 3: Save to BOTH destinations atomically
    video_thumb.parent.mkdir(parents=True, exist_ok=True)
    run_thumb.parent.mkdir(parents=True, exist_ok=True)

    tmp_out = video_thumb.with_suffix(".tmp.png")
    thumb_img.save(tmp_out, format="PNG", optimize=True)

    file_size = tmp_out.stat().st_size
    if file_size > 2_000_000:
        # If over 2MB, re-save with slight compression / JPEG fallback inside PNG or optimize
        logger.warning("[%s] Thumbnail size %d exceeds 2MB; re-encoding...", job_id, file_size)
        thumb_img.save(tmp_out, format="PNG", optimize=True, compress_level=9)
        file_size = tmp_out.stat().st_size

    # Move atomically to video_thumb and copy to run_thumb
    shutil.move(str(tmp_out), str(video_thumb))
    shutil.copy2(str(video_thumb), str(run_thumb))

    # Also save metadata sidecar
    sidecar = {
        "job_id": job_id,
        "slug": slug,
        "aspect": "16:9",
        "width": thumb_img.width,
        "height": thumb_img.height,
        "size_bytes": file_size,
        "allowed_text": allowed_text,
        "visual_hook": visual_hook,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    video_thumb.with_suffix(".json").write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    run_thumb.with_suffix(".json").write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")

    logger.info(
        "[✓] [%s] Thumbnail saved successfully (%dx%d, %d bytes) -> %s",
        job_id,
        thumb_img.width,
        thumb_img.height,
        file_size,
        video_thumb,
    )
    return video_thumb


def generate_all_batch1_thumbnails(force: bool = False, use_flow_cdp: bool = True) -> Dict[str, Any]:
    """Generate thumbnails for all 18 Batch 1 English Long 16:9 channels."""
    specs = sorted(BATCH1_SPECS_DIR.glob("*_long_16x9.json"))
    logger.info("Found %d Long 16:9 specs in %s", len(specs), BATCH1_SPECS_DIR)

    results: Dict[str, Any] = {}
    for spec_path in specs:
        slug = spec_path.stem.replace("_long_16x9", "").replace("-long-16x9", "")
        job_id = f"{slug}-batch1-16x9"
        try:
            path = generate_thumbnail_for_job(job_id=job_id, force=force, use_flow_cdp=use_flow_cdp)
            results[job_id] = {
                "status": "success",
                "path": str(path),
                "size_bytes": path.stat().st_size,
            }
        except Exception as e:
            logger.error("[%s] Thumbnail generation failed: %s", job_id, e, exc_info=True)
            results[job_id] = {"status": "error", "error": str(e)}

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate 16:9 YouTube Thumbnails for English Batch 1")
    parser.add_argument("--all", action="store_true", help="Generate thumbnails for all 18 Long 16:9 channels")
    parser.add_argument("--job-id", type=str, help="Generate thumbnail for a specific job_id or slug")
    parser.add_argument("--force", action="store_true", help="Force regenerate existing thumbnails")
    parser.add_argument("--no-flow", action="store_true", help="Skip Flow CDP and use deterministic visual fallback")
    args = parser.parse_args()

    use_flow = not args.no_flow

    if args.job_id:
        generate_thumbnail_for_job(args.job_id, force=args.force, use_flow_cdp=use_flow)
    else:
        results = generate_all_batch1_thumbnails(force=args.force, use_flow_cdp=use_flow)
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        logger.info("Completed thumbnail generation: %d/%d successful.", success_count, len(results))

    return 0


if __name__ == "__main__":
    sys.exit(main())
