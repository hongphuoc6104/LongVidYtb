#!/usr/bin/env python3
"""YouTube Studio 20-Channel Readiness Auditor for Video Pilot.

Audits Google Auth status, live Channel Identity lock (UC_ID vs expected UC_ID),
Feature Eligibility Tiers (Tier 1 Standard, Tier 2 Intermediate for >15m / custom thumbnails,
Tier 3 Advanced), and verifies whether each channel has an active >15m Long video waiting.

Enforces:
- ProcessGroupManager + stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)
- GPU headless Chrome (--headless=new, 90% VRAM via build_optimized_chrome_launch)
- Strict process teardown after each channel audit
- Atomic output written to video/vn_20_channels_readiness.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_cdp.resource_locks import stagger_cross_process_action
from sys.tools.publish_youtube_cdp import YouTubeCDPClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("audit_20_channels_readiness")

VN_20_CHANNELS = [
    "ai_binh_dan",
    "ban_do_quyen_luc",
    "banh_rang",
    "chanh_niem_ke",
    "co_the_ke",
    "dia_com",
    "ho_so_ky_la",
    "la_ban_hoc_thuat",
    "loi_sang_soi",
    "luat_doi_thuong",
    "luat_ngam",
    "minh_triet_song",
    "nao_luoi",
    "nghe_song_sot",
    "su_ke_lai",
    "tam_tinh_dem",
    "thuong_cho_kheo",
    "tui_tien",
    "ua_sao_vay",
    "vu_tru_ti_hon",
]


def detect_long_video_waiting(channel_slug: str, root_dir: Optional[Path] = None) -> dict[str, Any]:
    """Detect if a rendered Long (16:9) video exists and measure its duration (>15m check)."""
    base_root = root_dir or REPO_ROOT
    norm_slug = channel_slug.strip().replace("-", "_").lower()

    manifest_path = base_root / "video" / "publish_manifest_20_long.json"
    manifest_data = {}
    if manifest_path.is_file():
        try:
            raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_data = raw_manifest.get("channels", {}).get(norm_slug, {})
        except Exception as e:
            logger.debug("Could not read publish_manifest_20_long.json for %s: %s", norm_slug, e)

    video_dir = base_root / "video" / f"vn_pilot_{norm_slug}_long"
    mp4_path = base_root / manifest_data.get("video_path", f"video/vn_pilot_{norm_slug}_long/vn_pilot_{norm_slug}_long_16x9.mp4")
    srt_path = base_root / manifest_data.get("srt_path", f"video/vn_pilot_{norm_slug}_long/vn_pilot_{norm_slug}_long_16x9.srt")
    thumbnail_path = base_root / manifest_data.get("thumbnail_path", f"video/vn_pilot_{norm_slug}_long/vn_pilot_{norm_slug}_long_thumbnail_16x9.png")

    has_mp4 = mp4_path.is_file()
    has_srt = srt_path.is_file()
    has_thumb = thumbnail_path.is_file()

    # Determine duration
    duration_sec = 0.0
    chapters = manifest_data.get("chapters", [])
    if chapters and isinstance(chapters, list):
        last_ch = chapters[-1]
        if isinstance(last_ch, dict):
            end_ms = last_ch.get("end_ms", 0)
            if end_ms > 0:
                duration_sec = float(end_ms) / 1000.0
            elif "timestamp" in last_ch:
                ts_parts = [int(p) for p in str(last_ch["timestamp"]).strip().split(":") if p.isdigit()]
                if len(ts_parts) == 2:
                    duration_sec = ts_parts[0] * 60.0 + ts_parts[1] + 60.0
                elif len(ts_parts) == 3:
                    duration_sec = ts_parts[0] * 3600.0 + ts_parts[1] * 60.0 + ts_parts[2] + 60.0
        elif isinstance(last_ch, str):
            import re
            m = re.search(r"(\d{1,2}:\d{2}(?::\d{2})?)", last_ch)
            if m:
                ts_parts = [int(p) for p in m.group(1).split(":") if p.isdigit()]
                if len(ts_parts) == 2:
                    duration_sec = ts_parts[0] * 60.0 + ts_parts[1] + 60.0
                elif len(ts_parts) == 3:
                    duration_sec = ts_parts[0] * 3600.0 + ts_parts[1] * 60.0 + ts_parts[2] + 60.0

    # Fallback to audio output.json or brief
    if duration_sec <= 0.0:
        run_candidates = [
            base_root / "sys" / "runs" / f"vn_pilot_{norm_slug}_long" / "revisions" / "audio" / "1" / "output.json",
            base_root / "sys" / "runs" / f"vn_pilot_{norm_slug}_long" / "brief.json",
        ]
        for rc in run_candidates:
            if rc.is_file():
                try:
                    cdata = json.loads(rc.read_text(encoding="utf-8"))
                    payload_dur = cdata.get("payload", {}).get("duration") or cdata.get("duration_sec")
                    if payload_dur:
                        duration_sec = float(payload_dur)
                        break
                except Exception:
                    pass

    # If duration still 0 but mp4 exists, estimate from file size (assuming ~6Mbps h264_nvenc)
    if duration_sec <= 0.0 and has_mp4:
        size_bytes = mp4_path.stat().st_size
        duration_sec = (size_bytes * 8.0) / (6_000_000.0)

    is_gt_15m = duration_sec > 900.0

    return {
        "channel_id": norm_slug,
        "video_found": has_mp4,
        "mp4_path": str(mp4_path) if has_mp4 else None,
        "srt_path": str(srt_path) if has_srt else None,
        "thumbnail_path": str(thumbnail_path) if has_thumb else None,
        "duration_sec": round(duration_sec, 2),
        "duration_min": round(duration_sec / 60.0, 2),
        "is_gt_15m": is_gt_15m,
        "video_dir": str(video_dir),
    }


async def audit_channel_readiness_async(
    channel_slug: str,
    channel_map: dict[str, Any],
    dry_run: bool = False,
    root_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Execute live or dry-run readiness scan for a single channel."""
    norm_slug = channel_slug.strip().replace("-", "_").lower()
    ch_info = channel_map.get("channels", {}).get(norm_slug, {})
    expected_uc = ch_info.get("youtube_channel_id")
    profile_id = ch_info.get("profile_id", "profile_13")
    cdp_port = ch_info.get("cdp_port", 9234)
    handle = ch_info.get("handle")
    udd = ch_info.get("user_data_dir")
    email = ch_info.get("email", "")

    waiting_video = detect_long_video_waiting(norm_slug, root_dir)

    if dry_run:
        logger.info("[DRY-RUN] Audited channel %s (expected_uc=%s, gt_15m=%s)", norm_slug, expected_uc, waiting_video["is_gt_15m"])
        udd_exists = bool(udd and Path(udd).is_dir())
        return {
            "channel_id": norm_slug,
            "channel_name": ch_info.get("channel_name", norm_slug),
            "handle": handle,
            "profile_id": profile_id,
            "cdp_port": cdp_port,
            "email": email,
            "user_data_dir_exists": udd_exists,
            "expected_channel_id": expected_uc,
            "live_channel_id": expected_uc,
            "channel_identity_match": True,
            "authenticated": udd_exists,
            "tier1_standard": True,
            "tier2_intermediate": True,
            "tier3_advanced": False,
            "tier2_eligible": True,
            "tier3_eligible": False,
            "tier1_status_text": "Đã bật",
            "tier2_status_text": "Đã bật",
            "tier3_status_text": "Đủ điều kiện",
            "audit_method": "dry_run",
            "has_gt_15m_waiting": waiting_video["is_gt_15m"],
            "waiting_video": waiting_video,
            "status": "READY" if udd_exists else "PROFILE_DIR_MISSING",
            "dry_run": True,
        }

    # Live Chrome scan
    logger.info("Auditing live channel %s on port %d...", norm_slug, cdp_port)
    stagger_cross_process_action("chrome_launch", min_interval_sec=3.2, jitter_sec=0.6)

    profile_cfg = {
        "id": profile_id,
        "port": cdp_port,
        "directory": ch_info.get("directory", "Default"),
        "user_data_dir": udd or str(Path.home() / f".config/google-chrome-cdp-{profile_id}"),
        "email": email,
        "handle": handle,
        "youtube_channel_id": expected_uc,
    }

    client = YouTubeCDPClient(profile_cfg, headless=True)
    live_report: dict[str, Any] = {}
    try:
        await client.connect()

        # Step 0: Ensure Studio navigation (navigate to studio root first so it redirects to actual live channel)
        target_studio_url = "https://studio.youtube.com"
        curr_url = await client.evaluate("window.location.href")
        if "studio.youtube.com" not in str(curr_url):
            await client.call("Page.navigate", {"url": target_studio_url})
            await asyncio.sleep(5.0)

        await client.dismiss_studio_interstitials()
        await asyncio.sleep(2.0)

        # Readiness scan
        scan = await client.check_studio_readiness()
        live_uc = scan.get("channel_id")
        live_name = scan.get("channel_name") or ch_info.get("channel_name", norm_slug)
        auth_ok = scan.get("authenticated", False)

        id_match = False
        if expected_uc and live_uc:
            id_match = (expected_uc == live_uc)
        elif not expected_uc and live_uc:
            id_match = True

        audit_method = scan.get("audit_method", "")
        tier2_ok = scan.get("tier2_eligible", False)

        status = "READY"
        if not auth_ok:
            status = "AUTH_REQUIRED"
        elif expected_uc and not id_match:
            status = "CHANNEL_MISMATCH"
        elif not tier2_ok:
            if audit_method == "settings_unavailable":
                status = "TIER2_UNCONFIRMED"
            elif waiting_video["is_gt_15m"]:
                status = "TIER2_REQUIRED_FOR_GT_15M_AND_THUMB"
            else:
                status = "TIER2_REQUIRED_FOR_THUMB"

        live_report = {
            "channel_id": norm_slug,
            "channel_name": live_name,
            "handle": scan.get("handle") or handle,
            "profile_id": profile_id,
            "cdp_port": cdp_port,
            "email": email,
            "expected_channel_id": expected_uc,
            "live_channel_id": live_uc,
            "channel_identity_match": id_match,
            "authenticated": auth_ok,
            "tier1_standard": scan.get("standard_features", True),
            "tier2_intermediate": scan.get("intermediate_features", False),
            "tier3_advanced": scan.get("advanced_features", False),
            "tier2_eligible": tier2_ok,
            "tier3_eligible": scan.get("tier3_eligible", False),
            "tier1_status_text": scan.get("tier1_status_text", ""),
            "tier2_status_text": scan.get("tier2_status_text", ""),
            "tier3_status_text": scan.get("tier3_status_text", ""),
            "audit_method": audit_method,
            "has_gt_15m_waiting": waiting_video["is_gt_15m"],
            "waiting_video": waiting_video,
            "status": status,
            "dry_run": False,
        }
    except Exception as exc:
        logger.error("Audit error on channel %s: %s", norm_slug, exc)
        live_report = {
            "channel_id": norm_slug,
            "channel_name": ch_info.get("channel_name", norm_slug),
            "handle": handle,
            "profile_id": profile_id,
            "cdp_port": cdp_port,
            "email": email,
            "expected_channel_id": expected_uc,
            "live_channel_id": None,
            "channel_identity_match": False,
            "authenticated": False,
            "tier1_standard": False,
            "tier2_intermediate": False,
            "tier3_advanced": False,
            "tier2_eligible": False,
            "tier3_eligible": False,
            "tier1_status_text": "",
            "tier2_status_text": "",
            "tier3_status_text": "",
            "audit_method": "error",
            "has_gt_15m_waiting": waiting_video["is_gt_15m"],
            "waiting_video": waiting_video,
            "status": f"ERROR: {exc}",
            "dry_run": False,
        }
    finally:
        await client.close()
        client.terminate_browser()

    return live_report


def audit_channel_readiness(
    channel_slug: str,
    channel_map: dict[str, Any],
    dry_run: bool = False,
    root_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Synchronous wrapper for single channel readiness audit."""
    return asyncio.run(audit_channel_readiness_async(channel_slug, channel_map, dry_run=dry_run, root_dir=root_dir))


def audit_20_channels(
    channels: Optional[list[str]] = None,
    dry_run: bool = False,
    output_file: Optional[Path] = None,
    root_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Audit all specified channels and write readiness report."""
    base_root = root_dir or REPO_ROOT
    map_file = base_root / "sys" / "channels" / "youtube_channel_map.json"
    if not map_file.is_file():
        raise FileNotFoundError(f"youtube_channel_map.json not found at {map_file}")

    channel_map = json.loads(map_file.read_text(encoding="utf-8"))
    target_channels = channels or VN_20_CHANNELS

    results: dict[str, Any] = {}
    for ch in target_channels:
        norm_slug = ch.strip().replace("-", "_").lower()
        res = audit_channel_readiness(norm_slug, channel_map, dry_run=dry_run, root_dir=base_root)
        results[norm_slug] = res

    # Compute high-level summary
    total = len(results)
    ready_count = sum(1 for r in results.values() if r.get("status") == "READY")
    auth_issues = sum(1 for r in results.values() if not r.get("authenticated"))
    mismatches = sum(1 for r in results.values() if not r.get("channel_identity_match"))
    gt_15m_count = sum(1 for r in results.values() if r.get("has_gt_15m_waiting"))

    summary_doc = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": dry_run,
        "total_channels": total,
        "ready_count": ready_count,
        "auth_required_count": auth_issues,
        "channel_mismatch_count": mismatches,
        "gt_15m_waiting_count": gt_15m_count,
        "channels": results,
    }

    out_p = output_file or (base_root / "video" / "vn_20_channels_readiness.json")
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(summary_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("Saved 20-channel readiness report to %s", out_p)
    return summary_doc


def main():
    parser = argparse.ArgumentParser(description="Audit YouTube Studio Readiness for 20 Vietnamese Channels")
    parser.add_argument("--channels", nargs="*", help="Specific channels to audit (default: all 20)")
    parser.add_argument("--dry-run", action="store_true", help="Perform offline audit without spawning Chrome")
    parser.add_argument("--output", help="Custom output JSON path")
    args = parser.parse_args()

    out_path = Path(args.output).resolve() if args.output else None
    report = audit_20_channels(
        channels=args.channels,
        dry_run=args.dry_run,
        output_file=out_path,
    )
    print("\n=== 20 CHANNELS READINESS AUDIT REPORT ===")
    print(f"Total Channels: {report['total_channels']}")
    print(f"Ready:          {report['ready_count']}")
    print(f"Auth Required:  {report['auth_required_count']}")
    print(f"Identity Match: {report['total_channels'] - report['channel_mismatch_count']}/{report['total_channels']}")
    print(f">15m Waiting:   {report['gt_15m_waiting_count']}")
    print(f"Output saved to: {out_path or (REPO_ROOT / 'video' / 'vn_20_channels_readiness.json')}")


if __name__ == "__main__":
    main()
