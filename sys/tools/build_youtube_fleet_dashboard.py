#!/usr/bin/env python3
"""Build Super-Clean High-Density YouTube Fleet Dashboard (sys/tools/build_youtube_fleet_dashboard.py).

Generates an executive, scannable, high-density dashboard for the 18 English channels (Batch 1),
with zero clutter, zero redundant buttons, and real-time live progress tracking of Long 16:9 renders.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import html
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Root paths
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
CHANNELS_DIR = SYS_DIR / "channels"
BATCH1_RUNS_DIR = SYS_DIR / "runs" / "en_batch1_prod"
VIDEO_DIR = REPO_ROOT / "video"

CHANNEL_MAP_PATH = CHANNELS_DIR / "youtube_channel_map.json"
METRICS_PATH = CHANNELS_DIR / "dashboard_metrics.json"

DEFAULT_BRAIN_EXPORT_PATH = Path(
    "/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/youtube_fleet_dashboard.html"
)
DEFAULT_BATCH_EXPORT_PATH = BATCH1_RUNS_DIR / "youtube_fleet_dashboard.html"
DEFAULT_DESKTOP_EXPORT_PATH = Path("/home/hongphuoc6104/Desktop/YOUTUBE_FLEET_DASHBOARD.html")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("build_youtube_fleet_dashboard")


def get_video_duration_formatted(video_path: Path) -> str:
    """Extract video duration using ffprobe formatted as MM:SS."""
    if not video_path.exists():
        return ""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        raw_dur = float(res.stdout.strip()) if res.stdout.strip() else 0.0
        m, s = divmod(int(raw_dur), 60)
        return f"{m:02d}:{s:02d}"
    except Exception:
        return ""


def load_channel_map() -> Dict[str, Any]:
    """Load youtube_channel_map.json."""
    if not CHANNEL_MAP_PATH.exists():
        logger.warning(f"Channel map not found at {CHANNEL_MAP_PATH}")
        return {}
    try:
        with open(CHANNEL_MAP_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("channels", {})
    except Exception as e:
        logger.error(f"Error loading channel map: {e}")
        return {}


def load_metrics_avatars() -> Dict[str, str]:
    """Load cached avatar URLs from dashboard_metrics.json."""
    avatars: Dict[str, str] = {}
    if not METRICS_PATH.exists():
        return avatars
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in data.get("channels", []):
                cid = c.get("channel_id")
                avatar = c.get("avatar_url")
                if cid and avatar:
                    avatars[cid] = avatar
                    # Also map slug version
                    slug = c.get("slug")
                    if slug:
                        avatars[slug] = avatar
    except Exception as e:
        logger.debug(f"Error reading avatars from metrics: {e}")
    return avatars


def scan_batch1_fleet() -> List[Dict[str, Any]]:
    """Scan 18 English channels in en_batch1_prod."""
    channels_map = load_channel_map()
    avatars = load_metrics_avatars()

    if not BATCH1_RUNS_DIR.exists():
        logger.warning(f"Batch dir not found: {BATCH1_RUNS_DIR}")
        return []

    # Get all 16x9 directories
    job_dirs = sorted(
        [d.name for d in BATCH1_RUNS_DIR.iterdir() if d.is_dir() and d.name.endswith("-16x9")]
    )

    channels: List[Dict[str, Any]] = []

    for index, j16 in enumerate(job_dirs, 1):
        slug = j16.replace("-batch1-16x9", "")
        j9 = f"{slug}-batch1-9x16"

        # Lookup channel in map
        ch_info: Optional[Dict[str, Any]] = None
        for k, v in channels_map.items():
            if v.get("slug") == slug or k == slug.replace("-", "_"):
                ch_info = v
                break

        channel_name = ch_info.get("channel_name", slug.replace("-", " ").title()) if ch_info else slug
        handle = ch_info.get("handle", f"@{slug.replace('-', '')}") if ch_info else ""
        email = ch_info.get("email", "") if ch_info else ""
        port = ch_info.get("cdp_port", "") if ch_info else ""
        channel_url = (
            ch_info.get("youtube_channel_url")
            or (f"https://www.youtube.com/{handle}" if handle else "")
            if ch_info
            else ""
        )
        avatar_url = (
            avatars.get(slug)
            or avatars.get(slug.replace("-", "_"))
            or (ch_info.get("avatar_url") if ch_info else "")
            or ""
        )

        # Check Short 9:16
        short_video_url = ch_info.get("short_video_url") if ch_info else None
        mp4_9_path = VIDEO_DIR / j9 / f"{j9}.mp4"
        has_mp4_9 = mp4_9_path.exists() and mp4_9_path.stat().st_size > 500000

        # Check Long 16:9
        long_video_url = ch_info.get("long_video_url") if ch_info else None
        mp4_16_path = VIDEO_DIR / j16 / f"{j16}.mp4"
        has_mp4_16 = mp4_16_path.exists() and mp4_16_path.stat().st_size > 1000000
        thumb_path = VIDEO_DIR / j16 / "thumbnail.png"
        has_thumbnail = thumb_path.exists() and thumb_path.stat().st_size > 10000
        duration_16 = ""
        if has_mp4_16:
            duration_16 = get_video_duration_formatted(mp4_16_path)

        # Live scan flow_chain progress
        kf_glob = glob.glob(f"{BATCH1_RUNS_DIR}/{j16}/flow_chain/*/*.png")
        valid_kfs = [p for p in kf_glob if os.path.getsize(p) > 10000]
        kf_count = len(valid_kfs)

        clips_glob = glob.glob(f"{BATCH1_RUNS_DIR}/{j16}/flow_chain/clips/*.mp4")
        valid_clips = [p for p in clips_glob if os.path.getsize(p) > 50000]
        clip_count = len(valid_clips)

        # Status classification
        # Short status: 'published', 'awaiting_login', 'pending'
        if short_video_url:
            short_status = "published"
        elif has_mp4_9:
            short_status = "awaiting_login"
        else:
            short_status = "pending"

        # Long status: 'published', 'rendering', 'queued'
        if long_video_url:
            long_status = "published"
        elif kf_count > 0 or clip_count > 0:
            long_status = "rendering"
        else:
            long_status = "queued"

        # Primary filter category
        # - 'published': either short or long published
        # - 'rendering': long is rendering
        # - 'awaiting_login': short ready but not published (login needed)
        filter_tags = ["all"]
        if short_status == "published" or long_status == "published":
            filter_tags.append("published")
        if long_status == "rendering":
            filter_tags.append("rendering")
        if short_status == "awaiting_login":
            filter_tags.append("awaiting_login")

        channels.append(
            {
                "index": index,
                "slug": slug,
                "name": channel_name,
                "handle": handle,
                "email": email,
                "port": port,
                "channel_url": channel_url,
                "avatar_url": avatar_url,
                "short_status": short_status,
                "short_url": short_video_url,
                "has_mp4_9": has_mp4_9,
                "long_status": long_status,
                "long_url": long_video_url,
                "has_mp4_16": has_mp4_16,
                "has_thumbnail": has_thumbnail,
                "duration_16": duration_16,
                "kf_count": kf_count,
                "clip_count": clip_count,
                "kf_target": 80,
                "clip_target": 64,
                "filter_tags": " ".join(filter_tags),
            }
        )

    return channels


def render_dashboard_html(channels: List[Dict[str, Any]]) -> str:
    """Generate high-density, ultra-clean HTML dashboard."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_channels = len(channels)
    shorts_published = sum(1 for c in channels if c["short_status"] == "published")
    shorts_rendered = sum(1 for c in channels if c["has_mp4_9"] or c["short_status"] == "published")
    shorts_awaiting_login = sum(1 for c in channels if c["short_status"] == "awaiting_login")

    long_published = sum(1 for c in channels if c["long_status"] == "published")
    long_rendering = sum(1 for c in channels if c["long_status"] == "rendering")
    long_queued = sum(1 for c in channels if c["long_status"] == "queued")
    thumbs_ready = sum(1 for c in channels if c.get("has_thumbnail"))

    # In-flight active render details for KPI 4
    rendering_channels = [c for c in channels if c["long_status"] == "rendering"]

    # Build KPI 4 mini progress items
    live_items_html = ""
    if rendering_channels:
        for rc in rendering_channels:
            kf_pct = min(100, int((rc["kf_count"] / rc["kf_target"]) * 100))
            cl_pct = min(100, int((rc["clip_count"] / rc["clip_target"]) * 100))
            overall_pct = int((kf_pct * 0.4) + (cl_pct * 0.6))
            live_items_html += f"""
            <div class="kpi-live-channel">
              <div class="kpi-live-row">
                <span class="kpi-live-name">{html.escape(rc['name'])}</span>
                <span class="kpi-live-pct">{overall_pct}%</span>
              </div>
              <div class="kpi-bar-track">
                <div class="kpi-bar-fill" style="width: {overall_pct}%"></div>
              </div>
              <div class="kpi-live-sub">
                <span>KF: <b>{rc['kf_count']}/{rc['kf_target']}</b></span>
                <span>Clips: <b>{rc['clip_count']}/{rc['clip_target']}</b></span>
              </div>
            </div>
            """
    else:
        live_items_html = "<div class='text-muted'>Không có tác vụ render nào đang chạy.</div>"

    # Build table rows
    rows_html = ""
    for c in channels:
        idx_str = f"{c['index']:02d}"
        avatar_img = ""
        initials = "".join([part[0] for part in c["name"].split()[:2]]).upper()
        if c["avatar_url"]:
            avatar_img = f"""<img class="ch-avatar" src="{html.escape(c['avatar_url'])}" alt="{html.escape(c['name'])}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
            <div class="ch-avatar-fallback" style="display:none;">{initials}</div>"""
        else:
            avatar_img = f"""<div class="ch-avatar-fallback">{initials}</div>"""

        # Column 2: Short 9:16
        if c["short_status"] == "published":
            col_short = f"""
            <div class="status-cell">
              <span class="badge badge-success"><span class="dot dot-success"></span> ĐÃ ĐĂNG</span>
              <a href="{html.escape(c['short_url'])}" target="_blank" rel="noopener noreferrer" class="btn-yt-short">
                <svg viewBox="0 0 24 24" class="btn-icon"><path fill="currentColor" d="M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z"/></svg>
                Xem Shorts ↗
              </a>
            </div>
            """
        elif c["short_status"] == "awaiting_login":
            col_short = """
            <div class="status-cell">
              <span class="badge badge-warning"><span class="dot dot-warning"></span> CHỜ LOGIN</span>
              <span class="text-note">Sẵn sàng MP4 (video/)</span>
            </div>
            """
        else:
            col_short = """
            <div class="status-cell">
              <span class="badge badge-neutral">Chưa có MP4</span>
            </div>
            """

        thumb_badge = '<span class="badge" style="background:rgba(251,191,36,0.12);color:#fbbf24;border:1px solid rgba(251,191,36,0.3);font-size:10.5px;padding:2px 6px;border-radius:4px;margin-top:4px;display:inline-block;">🖼️ Thumbnail 16:9</span>' if c.get("has_thumbnail") else ''

        # Column 3: Long 16:9
        if c["long_status"] == "published":
            dur_display = f" • {c['duration_16']}" if c["duration_16"] else ""
            col_long = f"""
            <div class="status-cell">
              <span class="badge badge-success"><span class="dot dot-success"></span> ĐÃ ĐĂNG{dur_display}</span>
              <a href="{html.escape(c['long_url'])}" target="_blank" rel="noopener noreferrer" class="btn-yt-long">
                <svg viewBox="0 0 24 24" class="btn-icon"><path fill="currentColor" d="M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z"/></svg>
                Xem 16:9 ↗
              </a>
              {thumb_badge}
            </div>
            """
        elif c["long_status"] == "rendering":
            kf_pct = min(100, int((c["kf_count"] / c["kf_target"]) * 100))
            cl_pct = min(100, int((c["clip_count"] / c["clip_target"]) * 100))
            total_pct = int((kf_pct * 0.4) + (cl_pct * 0.6))
            col_long = f"""
            <div class="render-progress-box">
              <div class="render-progress-header">
                <span class="badge badge-info pulse"><span class="dot dot-info"></span> ĐANG RENDER ({total_pct}%)</span>
                <span class="render-progress-counts"><b>{c['kf_count']}</b>/80 KF • <b>{c['clip_count']}</b>/64 Clips</span>
              </div>
              <div class="progress-bar-track">
                <div class="progress-bar-fill animated-glow" style="width: {total_pct}%"></div>
              </div>
              {thumb_badge}
            </div>
            """
        else:
            col_long = f"""
            <div class="status-cell">
              <span class="badge badge-muted">⏳ Chờ render</span>
              <span class="text-note">Hàng đợi (0/80 KF)</span>
              {thumb_badge}
            </div>
            """

        # Column 4: Studio & Channel
        col_channel = f"""
        <div class="channel-actions-cell">
          <a href="{html.escape(c['channel_url'])}" target="_blank" rel="noopener noreferrer" class="btn-channel-link">
            Mở Kênh ↗
          </a>
          <span class="port-tag" title="CDP Debug Port">Port {c['port']}</span>
        </div>
        """

        rows_html += f"""
        <tr class="ch-row" data-tags="{c['filter_tags']}" data-search="{c['name'].lower()} {c['handle'].lower()} {c['email'].lower()} {c['port']} {c['slug']}">
          <td class="col-id">{idx_str}</td>
          <td class="col-channel">
            <div class="ch-meta">
              <div class="ch-avatar-wrap">
                {avatar_img}
              </div>
              <div class="ch-info">
                <div class="ch-name-line">
                  <span class="ch-name">{html.escape(c['name'])}</span>
                  <span class="ch-handle">{html.escape(c['handle'])}</span>
                </div>
                <div class="ch-sub-line">
                  <span class="ch-email">{html.escape(c['email'])}</span>
                  <span class="ch-sep">•</span>
                  <span class="ch-port">Cổng: <b>{c['port']}</b></span>
                </div>
              </div>
            </div>
          </td>
          <td class="col-short">{col_short}</td>
          <td class="col-long">{col_long}</td>
          <td class="col-actions">{col_channel}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YouTube Fleet Command Center • 18 Kênh English Batch 1</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2306b6d4'><polygon points='5 3 19 12 5 21 5 3'/></svg>" type="image/svg+xml">
<style>
  :root {{
    --bg-main: #070a12;
    --bg-surface: #0f172a;
    --bg-card: rgba(18, 26, 44, 0.7);
    --bg-card-hover: rgba(26, 38, 64, 0.85);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-active: rgba(6, 182, 212, 0.4);

    --primary: #06b6d4;
    --primary-light: #22d3ee;
    --primary-glow: rgba(6, 182, 212, 0.25);

    --success: #10b981;
    --success-bg: rgba(16, 185, 129, 0.12);
    --success-border: rgba(16, 185, 129, 0.3);

    --warning: #f59e0b;
    --warning-bg: rgba(245, 158, 11, 0.12);
    --warning-border: rgba(245, 158, 11, 0.3);

    --info: #38bdf8;
    --info-bg: rgba(56, 189, 248, 0.12);
    --info-border: rgba(56, 189, 248, 0.3);

    --danger: #ef4444;

    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --text-dim: #64748b;

    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background-color: var(--bg-main);
    background-image:
      radial-gradient(circle at 15% 15%, rgba(6, 182, 212, 0.05), transparent 40%),
      radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.05), transparent 40%);
    background-attachment: fixed;
    color: var(--text-main);
    font-family: var(--font);
    font-size: 13.5px;
    line-height: 1.5;
    padding: 24px;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }}

  .container {{
    max-width: 1460px;
    margin: 0 auto;
  }}

  /* Top Command Header */
  .header-card {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
  }}

  .brand-area {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}

  .brand-logo {{
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 16px var(--primary-glow);
  }}

  .brand-logo svg {{
    width: 24px;
    height: 24px;
    fill: #ffffff;
  }}

  .brand-titles h1 {{
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .brand-tag {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    background: rgba(6, 182, 212, 0.15);
    color: var(--primary-light);
    border: 1px solid rgba(6, 182, 212, 0.3);
    padding: 2px 8px;
    border-radius: 6px;
  }}

  .brand-titles p {{
    font-size: 12.5px;
    color: var(--text-muted);
    margin-top: 2px;
  }}

  .header-right {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .timestamp-badge {{
    font-size: 12px;
    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.04);
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
  }}

  .btn-refresh {{
    background: rgba(6, 182, 212, 0.12);
    color: var(--primary-light);
    border: 1px solid rgba(6, 182, 212, 0.35);
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}

  .btn-refresh:hover {{
    background: var(--primary);
    color: #000000;
    box-shadow: 0 0 12px var(--primary-glow);
  }}

  /* Top 4 KPI Grid */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 22px;
  }}

  @media (max-width: 1080px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
  }}
  @media (max-width: 640px) {{
    .kpi-grid {{ grid-template-columns: 1fr; }}
  }}

  .kpi-card {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    position: relative;
    overflow: hidden;
  }}

  .kpi-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
  }}
  .kpi-total::before {{ background: #06b6d4; }}
  .kpi-shorts::before {{ background: #10b981; }}
  .kpi-longs::before {{ background: #8b5cf6; }}
  .kpi-live::before {{ background: #f59e0b; }}

  .kpi-label {{
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-muted);
    margin-bottom: 6px;
  }}

  .kpi-val {{
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 4px;
  }}

  .kpi-val-small {{
    font-size: 17px;
    font-weight: 700;
  }}

  .kpi-sub {{
    font-size: 12px;
    color: var(--text-dim);
  }}

  /* KPI 4 Live Rendering list */
  .kpi-live-channel {{
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }}
  .kpi-live-channel:first-child {{
    margin-top: 4px;
    padding-top: 0;
    border-top: none;
  }}
  .kpi-live-row {{
    display: flex;
    justify-content: space-between;
    font-size: 11.5px;
    margin-bottom: 3px;
  }}
  .kpi-live-name {{
    font-weight: 600;
    color: #e2e8f0;
  }}
  .kpi-live-pct {{
    font-weight: 700;
    color: var(--primary-light);
  }}
  .kpi-bar-track {{
    height: 4px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 3px;
  }}
  .kpi-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #06b6d4, #10b981);
    border-radius: 4px;
  }}
  .kpi-live-sub {{
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: var(--text-dim);
  }}

  /* Filter & Search Bar */
  .toolbar-card {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }}

  .filter-tabs {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}

  .filter-tab {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }}

  .filter-tab:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
  }}

  .filter-tab.active {{
    background: var(--primary);
    border-color: var(--primary);
    color: #000000;
    box-shadow: 0 0 10px var(--primary-glow);
  }}

  .search-wrap {{
    position: relative;
    min-width: 280px;
  }}

  .search-input {{
    width: 100%;
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 7px 12px 7px 34px;
    color: #ffffff;
    font-size: 12.5px;
    outline: none;
    transition: border-color 0.2s;
  }}

  .search-input:focus {{
    border-color: var(--primary);
    box-shadow: 0 0 8px var(--primary-glow);
  }}

  .search-icon {{
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 15px;
    height: 15px;
    fill: var(--text-dim);
  }}

  /* Management Table */
  .table-card {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }}

  table.fleet-table {{
    width: 100%;
    border-collapse: collapse;
    text-align: left;
  }}

  table.fleet-table thead th {{
    background: rgba(15, 23, 42, 0.95);
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
  }}

  table.fleet-table tbody tr {{
    border-bottom: 1px solid var(--border-color);
    transition: background 0.15s ease;
  }}

  table.fleet-table tbody tr:hover {{
    background: var(--bg-card-hover);
  }}

  table.fleet-table tbody td {{
    padding: 12px 16px;
    vertical-align: middle;
  }}

  /* Columns */
  .col-id {{
    width: 44px;
    color: var(--text-dim);
    font-weight: 700;
    font-size: 12px;
  }}

  .col-channel {{
    min-width: 320px;
  }}

  .ch-meta {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .ch-avatar-wrap {{
    position: relative;
    width: 42px;
    height: 42px;
    flex-shrink: 0;
  }}

  .ch-avatar {{
    width: 42px;
    height: 42px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.12);
  }}

  .ch-avatar-fallback {{
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1e293b, #334155);
    color: var(--primary-light);
    font-weight: 700;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border-color);
  }}

  .ch-info {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .ch-name-line {{
    display: flex;
    align-items: baseline;
    gap: 8px;
  }}

  .ch-name {{
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
  }}

  .ch-handle {{
    font-size: 12px;
    color: var(--primary-light);
    font-family: monospace;
  }}

  .ch-sub-line {{
    font-size: 11.5px;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .ch-sep {{
    color: rgba(255, 255, 255, 0.15);
  }}

  .ch-port b {{
    color: #cbd5e1;
  }}

  /* Status Cells */
  .col-short, .col-long {{
    min-width: 240px;
  }}

  .status-cell {{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }}

  /* Badges */
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }}

  .badge-success {{
    background: var(--success-bg);
    color: #34d399;
    border: 1px solid var(--success-border);
  }}

  .badge-warning {{
    background: var(--warning-bg);
    color: #fbbf24;
    border: 1px solid var(--warning-border);
  }}

  .badge-info {{
    background: var(--info-bg);
    color: #38bdf8;
    border: 1px solid var(--info-border);
  }}

  .badge-muted {{
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-dim);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }}

  .badge-neutral {{
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-muted);
  }}

  .dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }}
  .dot-success {{ background: var(--success); }}
  .dot-warning {{ background: var(--warning); }}
  .dot-info {{ background: var(--info); }}

  .pulse {{
    animation: pulse 1.8s infinite;
  }}
  @keyframes pulse {{
    0% {{ opacity: 1; }}
    50% {{ opacity: 0.6; }}
    100% {{ opacity: 1; }}
  }}

  .text-note {{
    font-size: 11.5px;
    color: var(--text-dim);
  }}

  /* Buttons */
  .btn-yt-short, .btn-yt-long {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.15s ease;
  }}

  .btn-yt-short:hover, .btn-yt-long:hover {{
    background: #dc2626;
    color: #ffffff;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
  }}

  .btn-icon {{
    width: 14px;
    height: 14px;
  }}

  /* Render Progress Box */
  .render-progress-box {{
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 220px;
  }}

  .render-progress-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }}

  .render-progress-counts {{
    font-size: 11.5px;
    color: var(--text-muted);
    font-family: monospace;
  }}
  .render-progress-counts b {{
    color: var(--primary-light);
  }}

  .progress-bar-track {{
    height: 7px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    overflow: hidden;
  }}

  .progress-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #06b6d4, #10b981);
    border-radius: 6px;
    transition: width 0.3s ease;
  }}

  .animated-glow {{
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.6);
  }}

  /* Channel Actions Column */
  .col-actions {{
    min-width: 150px;
  }}

  .channel-actions-cell {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .btn-channel-link {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
    border: 1px solid var(--border-color);
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.15s ease;
  }}

  .btn-channel-link:hover {{
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.25);
  }}

  .port-tag {{
    font-size: 11px;
    font-family: monospace;
    color: var(--text-dim);
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 3px 6px;
    border-radius: 5px;
  }}

  /* Footer Note */
  .footer-note {{
    text-align: center;
    margin-top: 24px;
    font-size: 12px;
    color: var(--text-dim);
  }}
  .footer-note code {{
    background: rgba(255, 255, 255, 0.06);
    padding: 2px 6px;
    border-radius: 4px;
    color: var(--primary-light);
  }}
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <header class="header-card">
    <div class="brand-area">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      </div>
      <div class="brand-titles">
        <h1>
          Video Pilot Fleet Command
          <span class="brand-tag">Batch 1 • 18 Kênh EN</span>
        </h1>
        <p>Bảng điều khiển tinh gọn • Giám sát trực tiếp tiến độ Render và Trạng thái phát hành</p>
      </div>
    </div>
    <div class="header-right">
      <span class="timestamp-badge">Cập nhật: {now_str}</span>
      <button class="btn-refresh" onclick="location.reload();">
        <svg style="width:14px;height:14px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
        Làm mới
      </button>
    </div>
  </header>

  <!-- 4 Compact KPI Cards -->
  <section class="kpi-grid">
    <!-- KPI 1 -->
    <div class="kpi-card kpi-total">
      <div>
        <div class="kpi-label">Tổng Kênh Fleet</div>
        <div class="kpi-val">{total_channels} <span style="font-size:16px;font-weight:600;color:var(--text-muted);">Kênh</span></div>
      </div>
      <div class="kpi-sub">English Explainer Batch 1</div>
    </div>

    <!-- KPI 2 -->
    <div class="kpi-card kpi-shorts">
      <div>
        <div class="kpi-label">Short 9:16</div>
        <div class="kpi-val">{shorts_published} / {total_channels} <span style="font-size:16px;font-weight:600;color:#34d399;">Đã đăng</span></div>
      </div>
      <div class="kpi-sub"><b>{shorts_rendered}/{total_channels}</b> Render MP4 • <b>{shorts_awaiting_login}</b> Chờ login</div>
    </div>

    <!-- KPI 3 -->
    <div class="kpi-card kpi-longs">
      <div>
        <div class="kpi-label">Long 16:9 & Thumbnails</div>
        <div class="kpi-val kpi-val-small">
          <span style="color:#a78bfa;">{long_published} Đã đăng</span>
          <span style="color:var(--text-dim);font-weight:400;margin:0 4px;">•</span>
          <span style="color:#38bdf8;">{long_rendering} Đang chạy</span>
        </div>
      </div>
      <div class="kpi-sub">{long_queued} chờ • <b style="color:#fbbf24;">{thumbs_ready}/{total_channels} Thumbnails</b></div>
    </div>

    <!-- KPI 4 -->
    <div class="kpi-card kpi-live">
      <div>
        <div class="kpi-label">Tiến Độ Render Trực Tiếp (Flow+Veo)</div>
        <div>
          {live_items_html}
        </div>
      </div>
    </div>
  </section>

  <!-- Toolbar: 1-Click Filter Tabs + Instant Search -->
  <div class="toolbar-card">
    <div class="filter-tabs">
      <button class="filter-tab active" data-filter="all" onclick="setFilter('all', this)">Tất cả ({total_channels})</button>
      <button class="filter-tab" data-filter="published" onclick="setFilter('published', this)">Đã lên sóng ({shorts_published})</button>
      <button class="filter-tab" data-filter="rendering" onclick="setFilter('rendering', this)">Đang render Long ({long_rendering})</button>
      <button class="filter-tab" data-filter="awaiting_login" onclick="setFilter('awaiting_login', this)">Chờ đăng nhập ({shorts_awaiting_login})</button>
    </div>
    <div class="search-wrap">
      <svg class="search-icon" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
      <input type="text" id="searchInput" class="search-input" placeholder="Tìm kiếm kênh, @handle, email, port..." oninput="filterTable()">
    </div>
  </div>

  <!-- Main Management Table -->
  <main class="table-card">
    <table class="fleet-table" id="fleetTable">
      <thead>
        <tr>
          <th>#</th>
          <th>Kênh & Tài Khoản</th>
          <th>Short 9:16</th>
          <th>Long 16:9</th>
          <th>Kênh YouTube</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        {rows_html}
      </tbody>
    </table>
  </main>

  <footer class="footer-note">
    Tự động cập nhật bằng lệnh <code>python3 sys/tools/build_youtube_fleet_dashboard.py</code> • Video Pilot Enterprise Core
  </footer>

</div>

<script>
  let currentFilter = 'all';

  function setFilter(filter, btn) {{
    currentFilter = filter;
    document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    filterTable();
  }}

  function filterTable() {{
    const query = (document.getElementById('searchInput').value || '').trim().toLowerCase();
    const rows = document.querySelectorAll('#tableBody tr');

    rows.forEach(row => {{
      const tags = row.getAttribute('data-tags') || '';
      const searchData = row.getAttribute('data-search') || '';

      const matchFilter = (currentFilter === 'all') || tags.includes(currentFilter);
      const matchSearch = (!query) || searchData.includes(query);

      if (matchFilter && matchSearch) {{
        row.style.display = '';
      }} else {{
        row.style.display = 'none';
      }}
    }});
  }}
</script>

</body>
</html>
"""
    return html_content


def main() -> int:
    parser = argparse.ArgumentParser(description="Build YouTube Fleet Clean Dashboard")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Custom output HTML path",
    )
    args = parser.parse_args()

    logger.info("Scanning English Batch 1 Fleet (18 channels)...")
    channels = scan_batch1_fleet()
    if not channels:
        logger.error("No channels found in en_batch1_prod.")
        return 1

    logger.info(f"Loaded {len(channels)} channels. Rendering HTML...")
    html_content = render_dashboard_html(channels)

    output_paths = [
        DEFAULT_BRAIN_EXPORT_PATH,
        DEFAULT_BATCH_EXPORT_PATH,
        DEFAULT_DESKTOP_EXPORT_PATH,
    ]
    if args.output:
        output_paths.append(args.output)

    for p in output_paths:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Wrote dashboard ({len(html_content):,} bytes) -> {p}")
        except Exception as e:
            logger.warning(f"Could not write to {p}: {e}")

    print("\n✓ Dashboard generation complete.")
    print(f"  Brain Path: {DEFAULT_BRAIN_EXPORT_PATH}")
    print(f"  Batch Path: {DEFAULT_BATCH_EXPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
