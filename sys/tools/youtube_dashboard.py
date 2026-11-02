#!/usr/bin/env python3
"""YouTube 8-Channel Management & Analytics Dashboard (V3 Scalable).

Fast, modular parallel scraper and lightweight dashboard server for managing
the Video Pilot 8-channel YouTube fleet across N batches (Week 1, Batch 2, Batch 3...)
with zero Chrome overhead during scraping, CORS support, and standalone HTML export.
"""
from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repository root and sys directory are on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tools.dashboard_catalog_engine as dashboard_catalog_engine
import tools.dashboard_ui_template as dashboard_ui_template
import tools.review_queue_manager as review_queue_manager
from flow_cdp.resource_locks import build_optimized_chrome_launch
from tools.dashboard_catalog_engine import (
    DEFAULT_CHANNEL_MAP_PATH,
    DEFAULT_HISTORY_PATH,
    DEFAULT_METRICS_PATH,
    collect_scalable_dashboard_metrics,
    extract_video_id,
    fetch_url,
    format_duration,
    parse_numeric_count,
    scrape_channel_metrics,
    scrape_channel_tabs_bulk,
    scrape_video_metrics_resilient,
    sync_discovered_videos_to_channel_map,
    verify_channel_actual_video_count,
)
from tools.dashboard_ui_template import get_dashboard_html
from tools.review_queue_manager import load_review_queue

__all__ = [
    "extract_video_id",
    "parse_numeric_count",
    "format_duration",
    "fetch_url",
    "scrape_video_metrics",
    "scrape_channel_metrics",
    "scrape_channel_tabs_bulk",
    "verify_channel_actual_video_count",
    "collect_dashboard_metrics",
    "render_ascii_table",
    "launch_channel_chrome_studio",
    "export_standalone_html",
    "DashboardHTTPHandler",
    "run_server",
    "main",
    "DASHBOARD_HTML",
]

DEFAULT_BRAIN_EXPORT_PATH = Path(
    "/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/youtube_fleet_dashboard.html"
)
DEFAULT_DESKTOP_EXPORT_PATH = Path(
    "/home/hongphuoc6104/Desktop/YOUTUBE_FLEET_DASHBOARD.html"
)
DEFAULT_EXPORT_HTML_PATHS: List[Path] = [
    DEFAULT_BRAIN_EXPORT_PATH,
    DEFAULT_DESKTOP_EXPORT_PATH,
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("youtube_dashboard")

# Expose default HTML string for backward compatibility
DASHBOARD_HTML: str = get_dashboard_html()


def scrape_video_metrics(video_id: str, is_short: bool = False, timeout: float = 12.0) -> Dict[str, Any]:
    """Scrape real-time video metrics from YouTube watch page with resilient fallbacks."""
    return scrape_video_metrics_resilient(video_id=video_id, is_short=is_short, timeout=timeout)


def collect_dashboard_metrics(
    channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH,
    output_path: Optional[Path] = DEFAULT_METRICS_PATH,
    max_workers: int = 16,
    force_full: bool = False,
    incremental: bool = False,
    auto_sync_map: bool = False,
) -> Dict[str, Any]:
    """Scrape and aggregate live metrics for all YouTube channels in parallel across N batches."""
    return collect_scalable_dashboard_metrics(
        channel_map_path=channel_map_path,
        output_path=output_path,
        history_path=DEFAULT_HISTORY_PATH,
        incremental=incremental,
        force_full=force_full,
        auto_sync_map=auto_sync_map,
        max_workers=max_workers,
    )


def _populate_review_queue_media_mtime(q_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure updated_at / media_mtime is populated from video disk mtime to bust browser cache."""
    if not isinstance(q_data, dict):
        return q_data
    items = q_data.get("items")
    if not isinstance(items, dict):
        return q_data
    video_root = (REPO_ROOT / "video").resolve()
    for it in items.values():
        if not isinstance(it, dict):
            continue
        vpath = it.get("video_path") or it.get("mp4_path")
        if not vpath and it.get("job_id"):
            cand = video_root / it["job_id"] / f"{it['job_id']}.mp4"
            if cand.is_file():
                vpath = str(cand)
        if vpath and Path(vpath).is_file():
            mtime = int(Path(vpath).stat().st_mtime)
            it["media_mtime"] = mtime
            if not it.get("updated_at"):
                it["updated_at"] = str(mtime)
    return q_data


def export_standalone_html(data: Dict[str, Any], output_html_path: Path) -> Path:
    """Generate and export a standalone self-contained HTML dashboard file."""
    enriched = dict(data) if data else {}
    try:
        enriched["review_queue"] = _populate_review_queue_media_mtime(load_review_queue())
    except Exception as exc:
        logger.debug("Could not load review_queue for export: %s", exc)
    html_content = dashboard_ui_template.get_dashboard_html(embedded_data=enriched)
    out_p = Path(output_html_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(html_content, encoding="utf-8")
    logger.info("Exported standalone HTML dashboard to %s (%d bytes)", out_p, len(html_content))
    return out_p


def export_all_standalone_dashboards(
    data: Dict[str, Any], extra_paths: Optional[List[Path]] = None
) -> List[Path]:
    """Export standalone HTML dashboard to standard brain/desktop paths plus any extra paths."""
    targets: List[Path] = []
    seen: set[str] = set()
    for p in DEFAULT_EXPORT_HTML_PATHS:
        targets.append(p)
        seen.add(str(p.resolve()))

    if extra_paths:
        for ep in extra_paths:
            if ep and str(ep.resolve()) not in seen:
                targets.append(ep)
                seen.add(str(ep.resolve()))

    exported: List[Path] = []
    for p in targets:
        try:
            export_standalone_html(data, p)
            exported.append(p)
        except Exception as exc:
            logger.warning("Failed exporting standalone HTML to %s: %s", p, exc)
    return exported


def render_ascii_table(data: Dict[str, Any]) -> str:
    """Format metrics into a clean terminal ASCII/Markdown table."""
    totals = data.get("totals", {})
    channels = data.get("channels", [])
    batches = data.get("batches", [])

    lines = [
        "=" * 122,
        "  YOUTUBE FLEET SCALABLE ANALYTICS & CATALOG DASHBOARD (V3)",
        f"  Generated at: {data.get('generated_at', 'N/A')}  |  Scrape Time: {data.get('scrape_duration_seconds', 0)}s  |  Schema: {data.get('schema_version', '3.0')}",
        "=" * 122,
        f"{'Channel':<18} | {'Handle':<16} | {'Subs':>5} | {'Public Vids':<13} | {'Latest (B2) V/L':<18} | {'All-Time V/L':<18} | {'Funnel Status':<16}",
        "-" * 122,
    ]

    for c in channels:
        ch_name = str(c.get("channel_name", ""))[:17]
        handle = str(c.get("handle", ""))[:15]
        subs = str(c.get("subscriber_count", 0))

        vids_list = c.get("videos", [])
        if vids_list:
            long_cnt = sum(1 for v in vids_list if v.get("format") == "long_16x9")
            short_cnt = sum(1 for v in vids_list if v.get("format") == "short_9x16")
            pub_cnt = c.get("videos_count", len(vids_list))
            vids_summary = f"{pub_cnt} ({long_cnt}L+{short_cnt}S)"
        else:
            pub_cnt = c.get("videos_count", 2)
            vids_summary = f"{pub_cnt} vids"

        # Latest Batch (B2) Views / Likes
        b2_vids = [v for v in vids_list if str(v.get("batch", "")).lower() in ("batch2", "b2")]
        if not b2_vids and vids_list:
            latest_batch_id = vids_list[0].get("batch")
            b2_vids = [v for v in vids_list if v.get("batch") == latest_batch_id]

        if b2_vids:
            b2_views = sum(v.get("view_count", 0) for v in b2_vids)
            b2_likes = sum(v.get("like_count", 0) for v in b2_vids)
            b2_summary = f"{b2_views:,} v / {b2_likes} l"
        else:
            lv = c.get("long_video", {})
            sv = c.get("short_video", {})
            b_views = lv.get("view_count", 0) + sv.get("view_count", 0)
            b_likes = lv.get("like_count", 0) + sv.get("like_count", 0)
            b2_summary = f"{b_views:,} v / {b_likes} l"

        tot_views = c.get("channel_views", 0)
        tot_likes = c.get("channel_likes", 0)
        all_time_summary = f"{tot_views:,} v / {tot_likes} l"

        # Funnel status
        funnel_pairs = c.get("funnel_pairs", [])
        if funnel_pairs:
            linked_cnt = sum(1 for fp in funnel_pairs if fp.get("is_linked"))
            tot_fp = len(funnel_pairs)
            if linked_cnt == tot_fp:
                funnel_status = f"✓ {linked_cnt}/{tot_fp} Linked"
            else:
                funnel_status = f"! {linked_cnt}/{tot_fp} Linked"
        else:
            sv = c.get("short_video", {})
            if sv.get("has_funnel_link") or sv.get("related_video_url"):
                funnel_status = "✓ 1/1 Linked"
            else:
                funnel_status = "N/A"

        line = f"{ch_name:<18} | {handle:<16} | {subs:>5} | {vids_summary:<13} | {b2_summary:<18} | {all_time_summary:<18} | {funnel_status:<16}"
        lines.append(line)

    lines.append("-" * 122)

    # Batch Summary Table
    if batches:
        lines.append("")
        lines.append("  BATCH PERFORMANCE BREAKDOWN")
        lines.append("  " + "-" * 105)
        lines.append(f"  {'Batch':<16} | {'Videos':>7} | {'Longs':>6} | {'Shorts':>7} | {'Total Views':>14} | {'Total Likes':>12} | {'Avg Views/Vid':>14}")
        lines.append("  " + "-" * 105)
        for b in batches:
            b_lbl = str(b.get("batch_label", b.get("batch_id", "")))[:15]
            v_cnt = str(b.get("videos_count", 0))
            l_cnt = str(b.get("long_count", 0))
            s_cnt = str(b.get("short_count", 0))
            b_v = f"{b.get('views', 0):,}"
            b_l = f"{b.get('likes', 0):,}"
            avg_v = f"{b.get('avg_views', 0.0):.1f}"
            lines.append(f"  {b_lbl:<16} | {v_cnt:>7} | {l_cnt:>6} | {s_cnt:>7} | {b_v:>14} | {b_l:>12} | {avg_v:>14}")
        lines.append("  " + "-" * 105)

    tot_ch = totals.get("total_channels", len(channels))
    tot_vids = totals.get("total_videos", len(data.get("all_videos", [])))
    tot_views = totals.get("total_views", 0)
    tot_likes = totals.get("total_likes", 0)
    tot_subs = totals.get("total_subscribers", 0)
    v_delta = totals.get("views_delta", 0)
    v_delta_str = f" (+{v_delta:,})" if v_delta > 0 else ""
    f_comp = totals.get("funnel_compliance_pct", 0.0)
    f_linked = totals.get("funnel_linked_shorts", 0)
    f_tot = totals.get("funnel_total_shorts", 0)

    lines.append(
        f"TOTALS: {tot_ch} Channels | {tot_vids} Videos | {tot_views:,} Views{v_delta_str} | "
        f"{tot_likes:,} Likes | {tot_subs} Subscribers | Funnel: {f_linked}/{f_tot} ({f_comp}%)"
    )
    lines.append("=" * 122)
    return "\n".join(lines)


def launch_channel_chrome_studio(channel_id: str, channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH) -> Dict[str, Any]:
    """Launch dedicated Chrome CDP profile for a channel directly into YouTube Studio."""
    raw_map = json.loads(channel_map_path.read_text(encoding="utf-8"))
    channels = raw_map.get("channels", {})
    if channel_id not in channels:
        return {"status": "error", "message": f"Channel '{channel_id}' not found in map"}

    cfg = channels[channel_id]
    user_data_dir = cfg.get("user_data_dir")
    cdp_port = cfg.get("cdp_port", 9222)
    yt_channel_id = cfg.get("youtube_channel_id", "")
    target_url = f"https://studio.youtube.com/channel/{yt_channel_id}"

    chrome_bin = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or "/usr/bin/google-chrome"
    if not os.path.exists(chrome_bin):
        return {"status": "error", "message": f"Chrome binary not found at {chrome_bin}"}

    cmd, env = build_optimized_chrome_launch(
        binary=chrome_bin,
        user_data_dir=user_data_dir,
        profile_dir=cfg.get("directory"),
        port=int(cdp_port),
        url=target_url,
        headless=False,
    )
    try:
        subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return {
            "status": "ok",
            "message": f"Launched Chrome Studio for {cfg.get('channel_name', channel_id)} on port {cdp_port}",
            "channel_id": channel_id,
            "port": cdp_port,
            "studio_url": target_url,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Failed to spawn Chrome: {exc}"}


class DashboardHTTPHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for the local YouTube Fleet Dashboard (V3)."""

    channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH
    metrics_path: Path = DEFAULT_METRICS_PATH
    history_path: Path = DEFAULT_HISTORY_PATH
    export_paths: List[Path] = DEFAULT_EXPORT_HTML_PATHS

    def log_message(self, format: str, *args: Any) -> None:
        """Custom logger for clean terminal logs."""
        logger.info("%s - - [%s] %s", self.address_string(), self.log_date_time_string(), format % args)

    def _send_cors_headers(self) -> None:
        """Attach permissive CORS headers for local file:// and web access."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests cleanly."""
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle dashboard HTML and metrics API calls."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path in ("/", "/index.html"):
            try:
                importlib.reload(dashboard_catalog_engine)
                importlib.reload(dashboard_ui_template)
                importlib.reload(review_queue_manager)
            except Exception as exc:
                logger.debug("Failed reloading modules in do_GET: %s", exc)

            if self.metrics_path.exists():
                try:
                    data = json.loads(self.metrics_path.read_text(encoding="utf-8"))
                except Exception:
                    data = collect_dashboard_metrics(self.channel_map_path, self.metrics_path)
            else:
                data = collect_dashboard_metrics(self.channel_map_path, self.metrics_path)

            try:
                data["review_queue"] = _populate_review_queue_media_mtime(review_queue_manager.load_review_queue())
            except Exception as exc:
                logger.warning("Failed loading review queue in do_GET: %s", exc)

            html = dashboard_ui_template.get_dashboard_html(embedded_data=data)
            content = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self._send_cors_headers()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/api/review-queue":
            try:
                q_data = _populate_review_queue_media_mtime(review_queue_manager.load_review_queue())
            except Exception as exc:
                q_data = {"schema_version": "1.0", "items": {}, "error": str(exc)}
            content = json.dumps(q_data, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path.startswith("/media/"):
            # Safe local media serving from video/<job_id>/
            rel = urllib.parse.unquote(parsed.path[len("/media/"):]).lstrip("/")
            video_root = (REPO_ROOT / "video").resolve()
            target_file = (video_root / rel).resolve()
            if not str(target_file).startswith(str(video_root)) or not target_file.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Media file not found")
                return

            ext = target_file.suffix.lower()
            mime_map = {
                ".mp4": "video/mp4",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".srt": "text/plain; charset=utf-8",
            }
            ctype = mime_map.get(ext, "application/octet-stream")
            file_size = target_file.stat().st_size
            range_header = self.headers.get("Range")

            if range_header and range_header.startswith("bytes="):
                try:
                    byte_range = range_header.split("=", 1)[1].split(",")
                    start_str, end_str = byte_range[0].split("-", 1)
                    start = int(start_str) if start_str else 0
                    end = int(end_str) if end_str else file_size - 1
                    end = min(end, file_size - 1)
                    length = max(0, end - start + 1)
                    with open(target_file, "rb") as f:
                        f.seek(start)
                        chunk = f.read(length)
                    self.send_response(HTTPStatus.PARTIAL_CONTENT)
                    self._send_cors_headers()
                    self.send_header("Content-Type", ctype)
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(len(chunk)))
                    self.end_headers()
                    self.wfile.write(chunk)
                    return
                except Exception:
                    pass

            data_bytes = target_file.read_bytes()
            self.send_response(HTTPStatus.OK)
            self._send_cors_headers()
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(len(data_bytes)))
            self.end_headers()
            self.wfile.write(data_bytes)
            return

        if parsed.path == "/api/metrics":
            try:
                importlib.reload(dashboard_catalog_engine)
            except Exception as exc:
                logger.debug("Failed reloading dashboard_catalog_engine in /api/metrics: %s", exc)

            if self.metrics_path.exists():
                try:
                    data = json.loads(self.metrics_path.read_text(encoding="utf-8"))
                except Exception:
                    data = collect_dashboard_metrics(self.channel_map_path, self.metrics_path)
            else:
                data = collect_dashboard_metrics(self.channel_map_path, self.metrics_path)

            try:
                data["review_queue"] = _populate_review_queue_media_mtime(review_queue_manager.load_review_queue())
            except Exception:
                pass
            content = json.dumps(data, ensure_ascii=False).encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/api/history":
            history_rows: List[Dict[str, Any]] = []
            if self.history_path.exists():
                try:
                    with open(self.history_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                history_rows.append(json.loads(line))
                except Exception as exc:
                    logger.warning("Error reading history: %s", exc)

            content = json.dumps(history_rows, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    def do_POST(self) -> None:
        """Handle refresh, sync-map, and Chrome Studio launch actions."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/refresh":
            try:
                importlib.reload(dashboard_catalog_engine)
                importlib.reload(dashboard_ui_template)
            except Exception as exc:
                logger.debug("Failed reloading modules in do_POST /api/refresh: %s", exc)

            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
            except Exception:
                payload = {}

            force_full = bool(payload.get("force_full", False))
            try:
                data = collect_dashboard_metrics(
                    channel_map_path=self.channel_map_path,
                    output_path=self.metrics_path,
                    force_full=force_full,
                )
                export_all_standalone_dashboards(data, self.export_paths)
                content = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as exc:
                logger.error("Refresh error: %s", exc)
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                content = json.dumps({"error": str(exc)}).encode("utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            return

        if parsed.path == "/api/sync-map":
            try:
                importlib.reload(dashboard_catalog_engine)
                importlib.reload(dashboard_ui_template)
            except Exception as exc:
                logger.debug("Failed reloading modules in do_POST /api/sync-map: %s", exc)

            try:
                added_count = sync_discovered_videos_to_channel_map(self.channel_map_path)
                data = collect_dashboard_metrics(
                    channel_map_path=self.channel_map_path,
                    output_path=self.metrics_path,
                    force_full=True,
                )
                export_all_standalone_dashboards(data, self.export_paths)
                res = {
                    "status": "ok",
                    "synced_count": added_count,
                    "message": f"Successfully synced {added_count} discovered videos to channel map",
                    "metrics": data,
                }
                content = json.dumps(res, ensure_ascii=False).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as exc:
                logger.error("Sync map error: %s", exc)
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self._send_cors_headers()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                content = json.dumps({"error": str(exc)}).encode("utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            return

        if parsed.path == "/api/open-studio":
            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
            except Exception:
                payload = {}

            channel_id = payload.get("channel_id", "")
            if not channel_id:
                query_params = urllib.parse.parse_qs(parsed.query)
                channel_id = query_params.get("channel", [""])[0]

            res = launch_channel_chrome_studio(channel_id, self.channel_map_path)
            status_code = HTTPStatus.OK if res.get("status") == "ok" else HTTPStatus.BAD_REQUEST

            self.send_response(status_code)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            content = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if parsed.path == "/api/review-decision":
            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length) if length > 0 else b"{}"
            try:
                payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
            except Exception:
                payload = {}

            try:
                q_data = review_queue_manager.load_review_queue()
                items = q_data.setdefault("items", {})
                from datetime import datetime, timezone

                now_iso = datetime.now(timezone.utc).isoformat()
                updated_ids: List[str] = []

                if "decisions" in payload and isinstance(payload["decisions"], dict):
                    for jid, dec in payload["decisions"].items():
                        if jid in items and isinstance(dec, dict):
                            st = str(dec.get("status", items[jid].get("status", "PENDING_REVIEW"))).upper()
                            if st in review_queue_manager.VALID_STATUSES:
                                items[jid]["status"] = st
                                items[jid]["reviewed_at"] = now_iso if st in ("APPROVED", "REJECTED") else None
                            if "review_notes" in dec:
                                items[jid]["review_notes"] = str(dec.get("review_notes") or "")
                            updated_ids.append(jid)
                else:
                    jid = str(payload.get("job_id", "")).strip()
                    if not jid or jid not in items:
                        raise KeyError(f"Job '{jid}' not found in review queue")
                    st = str(payload.get("status", items[jid].get("status", "PENDING_REVIEW"))).upper()
                    if st in review_queue_manager.VALID_STATUSES:
                        items[jid]["status"] = st
                        items[jid]["reviewed_at"] = now_iso if st in ("APPROVED", "REJECTED") else None
                    if "review_notes" in payload:
                        items[jid]["review_notes"] = str(payload.get("review_notes") or "")
                    updated_ids.append(jid)

                review_queue_manager.save_review_queue(q_data)
                res = {
                    "status": "ok",
                    "updated": updated_ids,
                    "review_queue": q_data,
                }
                status_code = HTTPStatus.OK
            except Exception as exc:
                logger.error("Review decision update error: %s", exc)
                res = {"status": "error", "message": str(exc)}
                status_code = HTTPStatus.BAD_REQUEST

            self.send_response(status_code)
            self._send_cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            content = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Action not found")


def run_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    history_path: Path = DEFAULT_HISTORY_PATH,
    export_paths: Optional[List[Path]] = None,
) -> None:
    """Start local dashboard web server."""
    DashboardHTTPHandler.channel_map_path = channel_map_path
    DashboardHTTPHandler.metrics_path = metrics_path
    DashboardHTTPHandler.history_path = history_path
    if export_paths is not None:
        DashboardHTTPHandler.export_paths = export_paths

    # Ensure metrics exist before serving
    if not metrics_path.exists():
        logger.info("Initializing baseline metrics snapshot...")
        collect_dashboard_metrics(channel_map_path, metrics_path)

    server = ThreadingHTTPServer((host, port), DashboardHTTPHandler)
    logger.info("=" * 70)
    logger.info("  🚀 Video Pilot YouTube Fleet Dashboard Server (V3) Running!")
    logger.info("  Dashboard URL : http://%s:%d", host, port)
    logger.info("  Metrics API   : http://%s:%d/api/metrics", host, port)
    logger.info("  Press Ctrl+C to terminate.")
    logger.info("=" * 70)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Dashboard server shutting down gracefully.")
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="YouTube Fleet Analytics & Management Dashboard (V3)")
    parser.add_argument("--channel-map", type=Path, default=DEFAULT_CHANNEL_MAP_PATH, help="Path to channel map SSOT")
    parser.add_argument("--output", type=Path, default=DEFAULT_METRICS_PATH, help="Path to output metrics JSON")
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY_PATH, help="Path to dashboard history JSONL")
    parser.add_argument("--export-html", type=Path, default=None, help="Export standalone HTML dashboard to custom path")
    parser.add_argument("--sync-map", action="store_true", help="Sync discovered public videos into channel map")
    parser.add_argument("--force-full", action="store_true", help="Force full watch-page scrape bypassing incremental cache")
    parser.add_argument("--workers", type=int, default=32, help="Concurrent HTTP worker threads")
    parser.add_argument("--serve", action="store_true", help="Launch local dashboard web server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Dashboard server host")
    parser.add_argument("--port", type=int, default=8765, help="Dashboard server port")
    parser.add_argument("--open-studio", type=str, help="Launch dedicated Chrome Studio profile for channel")

    args = parser.parse_args()

    if args.open_studio:
        res = launch_channel_chrome_studio(args.open_studio, args.channel_map)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("status") == "ok" else 1

    extra_export_paths = [args.export_html] if args.export_html else []

    if args.sync_map:
        synced = sync_discovered_videos_to_channel_map(args.channel_map)
        logger.info("CLI sync-map completed: %d new videos added to channel map.", synced)

    if args.serve:
        run_server(
            host=args.host,
            port=args.port,
            channel_map_path=args.channel_map,
            metrics_path=args.output,
            history_path=args.history,
            export_paths=extra_export_paths,
        )
        return 0

    # Default CLI mode: Fetch live metrics, export standalone HTML & print ASCII table
    data = collect_dashboard_metrics(
        channel_map_path=args.channel_map,
        output_path=args.output,
        max_workers=args.workers,
        force_full=args.force_full,
    )
    export_all_standalone_dashboards(data, extra_export_paths)
    table_str = render_ascii_table(data)
    print("\n" + table_str + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
