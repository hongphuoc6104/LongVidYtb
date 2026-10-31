#!/usr/bin/env python3
"""Video Pilot YouTube Fleet Dashboard Catalog & Bulk Scraper Engine.

Scalable, high-performance catalog engine designed to monitor and aggregate
metrics for the 8-channel YouTube fleet across N batches (week1, batch2, batch3...).
Provides 2-call bulk tab discovery per channel, resilient per-video metric enrichment,
incremental smart caching, funnel link verification, historical tracking, and
auto-sync with youtube_channel_map.json.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import logging
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root and sys directory are on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from channels.registry import channels as get_registry_channels
    from channels.registry import get_visual_archetype
except Exception:
    try:
        from sys.channels.registry import channels as get_registry_channels
        from sys.channels.registry import get_visual_archetype
    except Exception:
        get_registry_channels = None
        get_visual_archetype = None

DEFAULT_CHANNEL_MAP_PATH = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
DEFAULT_METRICS_PATH = REPO_ROOT / "sys" / "channels" / "dashboard_metrics.json"
DEFAULT_HISTORY_PATH = REPO_ROOT / "sys" / "channels" / "dashboard_history.jsonl"

FOREIGN_VIDEO_BLACKLIST = {
    "upsIwIjtjYQ",
    "OJD6Wkpi3pE",
    "V8QVHvNw450",
    "bB2kjiltY1I",
    "tg3mucW5htA",
    "NWXxjIpRMnE",
    "oabbkRLvtXU",
    "_A-d_sCcCx8",
    "TwiHZSXKvDw",
    "_u4BUza-2lw",
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("dashboard_catalog_engine")


def extract_video_id(url: Optional[str]) -> str:
    """Extract standard 11-char YouTube video ID from various URL patterns."""
    if not url:
        return ""
    url = url.strip()
    match = re.search(r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else ""


def parse_numeric_count(text: Optional[str]) -> int:
    """Parse subscriber or view count strings like '1.2K', '3.5M', '992 views' into integer."""
    if not text:
        return 0
    cleaned = text.strip().lower().replace(",", "")
    match = re.search(r"([\d\.]+)\s*([kmb])?", cleaned)
    if not match:
        return 0
    try:
        val = float(match.group(1))
        unit = match.group(2)
        mult = 1
        if unit == "k":
            mult = 1_000
        elif unit == "m":
            mult = 1_000_000
        elif unit == "b":
            mult = 1_000_000_000
        return int(val * mult)
    except (ValueError, TypeError):
        return 0


def format_duration(seconds: int) -> str:
    """Format duration seconds into mm:ss or hh:mm:ss."""
    if seconds <= 0:
        return "00:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_duration_to_seconds(text: Optional[str]) -> int:
    """Parse duration string like '3:26', '1:02:15' or '3 minutes, 26 seconds' into total seconds."""
    if not text:
        return 0
    cleaned = text.strip()
    # Check colon formatted HH:MM:SS or MM:SS
    m_hms = re.search(r"(?:(\d+):)?(\d+):(\d+)", cleaned)
    if m_hms:
        h = int(m_hms.group(1)) if m_hms.group(1) else 0
        m = int(m_hms.group(2))
        s = int(m_hms.group(3))
        return h * 3600 + m * 60 + s
    # Check words formatted: e.g. "3 hours, 26 minutes, 15 seconds"
    h_m = re.search(r"(\d+)\s*(?:hours?|hrs?|h\b)", cleaned, re.IGNORECASE)
    m_m = re.search(r"(\d+)\s*(?:minutes?|mins?|m\b)", cleaned, re.IGNORECASE)
    s_m = re.search(r"(\d+)\s*(?:seconds?|secs?|s\b)", cleaned, re.IGNORECASE)
    if h_m or m_m or s_m:
        h = int(h_m.group(1)) if h_m else 0
        m = int(m_m.group(1)) if m_m else 0
        s = int(s_m.group(1)) if s_m else 0
        return h * 3600 + m * 60 + s
    return 0


def format_batch_label(batch: Optional[str]) -> str:
    """Format batch identifier into human-readable label."""
    if not batch:
        return "Unknown"
    b_low = batch.lower().strip()
    if b_low.startswith("batch") and b_low[5:].isdigit():
        return f"Batch {b_low[5:]}"
    if b_low.startswith("week") and b_low[4:].isdigit():
        return f"Week {b_low[4:]}"
    if b_low == "discovered":
        return "Discovered"
    return batch.replace("_", " ").title()


def fetch_url(url: str, timeout: float = 10.0) -> str:
    """Fetch URL with desktop User-Agent and English locale."""
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def fetch_oembed_title(video_id: str, timeout: float = 4.0) -> str:
    """Fetch video title from YouTube oEmbed endpoint."""
    if not video_id:
        return ""
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        raw = fetch_url(oembed_url, timeout=timeout)
        data = json.loads(raw)
        return data.get("title", "").strip()
    except Exception:
        return ""


def parse_tab_initial_data(
    html: str, is_short: bool, expected_channel_id: str = ""
) -> Dict[str, Dict[str, Any]]:
    """Parse ytInitialData from a channel /videos or /shorts tab."""
    results: Dict[str, Dict[str, Any]] = {}
    p_marker = "ytInitialData = "
    p_idx = html.find(p_marker)
    if p_idx == -1:
        return results

    try:
        start_pos = p_idx + len(p_marker)
        data, _ = json.JSONDecoder().raw_decode(html[start_pos:])
    except Exception as exc:
        logger.debug("Failed parsing tab ytInitialData JSON: %s", exc)
        return results

    # Channel ID ground-truth verification:
    # If expected_channel_id is provided and metadata contains externalId,
    # reject responses from foreign channels to prevent fleet pollution.
    external_id = data.get("metadata", {}).get("channelMetadataRenderer", {}).get("externalId", "")
    if expected_channel_id and external_id and external_id != expected_channel_id:
        logger.warning(
            "Foreign channel externalId mismatch! expected=%s, got=%s. Discarding tab results.",
            expected_channel_id,
            external_id,
        )
        return {}

    tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
    selected_content: Optional[Dict[str, Any]] = None
    for t in tabs:
        if not t.get("tabRenderer", {}).get("selected"):
            continue
        content = t.get("tabRenderer", {}).get("content", {})
        selected_content = content
        grid_items = content.get("richGridRenderer", {}).get("contents", [])
        if not grid_items:
            grid_items = content.get("sectionListRenderer", {}).get("contents", [])

        for c in grid_items:
            rfm = c.get("richItemRenderer", {}).get("content", {})
            if not rfm:
                rfm = c

            # 1. lockupViewModel (/videos tab modern)
            if "lockupViewModel" in rfm:
                lvm = rfm["lockupViewModel"]
                vid = ""
                tap = lvm.get("rendererContext", {}).get("commandContext", {}).get("onTap", {})
                vid = tap.get("innertubeCommand", {}).get("watchEndpoint", {}).get("videoId", "")
                if not vid:
                    for ol in lvm.get("contentImage", {}).get("thumbnailViewModel", {}).get("overlays", []):
                        for b in ol.get("thumbnailBottomOverlayViewModel", {}).get("badges", []):
                            target = b.get("thumbnailBadgeViewModel", {}).get("animationActivationTargetId")
                            if target and len(target) == 11:
                                vid = target
                                break
                        if vid:
                            break
                if not vid:
                    m = re.search(r'\"videoId\":\s*\"([a-zA-Z0-9_-]{11})\"', json.dumps(lvm))
                    if m:
                        vid = m.group(1)

                if vid:
                    meta = lvm.get("metadata", {}).get("lockupMetadataViewModel", {})
                    title = meta.get("title", {}).get("content", "").strip()
                    if not title:
                        a11y_label = lvm.get("rendererContext", {}).get("accessibilityContext", {}).get("label", "")
                        title = re.sub(r"\s+\d+\s+(?:minutes?|seconds?|hours?).*", "", a11y_label).strip()

                    views = 0
                    pub_text = ""
                    for row in meta.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", []):
                        for part in row.get("metadataParts", []):
                            txt = part.get("text", {}).get("content", "")
                            a11y = part.get("accessibilityLabel", "")
                            if "view" in a11y.lower():
                                views = parse_numeric_count(a11y)
                            elif "view" in txt.lower():
                                views = parse_numeric_count(txt)
                            elif part.get("leadingIcon", {}).get("name") == "PLAY_ARROW_OUTLINED":
                                views = parse_numeric_count(txt)
                            if "ago" in a11y.lower():
                                pub_text = a11y
                            elif "ago" in txt.lower():
                                pub_text = txt

                    sec = 0
                    for ol in lvm.get("contentImage", {}).get("thumbnailViewModel", {}).get("overlays", []):
                        for b in ol.get("thumbnailBottomOverlayViewModel", {}).get("badges", []):
                            tbvm = b.get("thumbnailBadgeViewModel", {})
                            if tbvm.get("text"):
                                sec = parse_duration_to_seconds(tbvm.get("text"))
                                break
                        if sec > 0:
                            break

                    thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    sources = (
                        lvm.get("contentImage", {})
                        .get("thumbnailViewModel", {})
                        .get("image", {})
                        .get("sources", [])
                    )
                    if sources:
                        thumb = sources[-1].get("url", thumb)

                    results[vid] = {
                        "video_id": vid,
                        "title": title,
                        "view_count": views,
                        "length_seconds": sec,
                        "published_time_text": pub_text,
                        "thumbnail_url": thumb,
                        "is_short": is_short,
                    }

            # 2. videoRenderer (/videos tab classic)
            elif "videoRenderer" in rfm:
                vr = rfm["videoRenderer"]
                vid = vr.get("videoId", "")
                if vid:
                    title_runs = vr.get("title", {}).get("runs", [])
                    title = title_runs[0].get("text", "") if title_runs else vr.get("title", {}).get("simpleText", "")
                    if not title:
                        title = vr.get("title", {}).get("accessibility", {}).get("accessibilityData", {}).get("label", "")
                    v_text = vr.get("viewCountText", {}).get("simpleText", "") or vr.get("shortViewCountText", {}).get("simpleText", "")
                    views = parse_numeric_count(v_text)
                    sec = parse_duration_to_seconds(vr.get("lengthText", {}).get("simpleText", ""))
                    pub_text = vr.get("publishedTimeText", {}).get("simpleText", "")
                    thumbs = vr.get("thumbnail", {}).get("thumbnails", [])
                    thumb = thumbs[-1].get("url", f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg") if thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    results[vid] = {
                        "video_id": vid,
                        "title": title.strip(),
                        "view_count": views,
                        "length_seconds": sec,
                        "published_time_text": pub_text,
                        "thumbnail_url": thumb,
                        "is_short": False,
                    }

            # 3. shortsLockupViewModel (/shorts tab modern)
            elif "shortsLockupViewModel" in rfm:
                slvm = rfm["shortsLockupViewModel"]
                vid = slvm.get("onTap", {}).get("innertubeCommand", {}).get("reelWatchEndpoint", {}).get("videoId", "")
                if not vid and slvm.get("entityId"):
                    cand = slvm["entityId"].replace("shorts-shelf-item-", "")
                    if len(cand) == 11:
                        vid = cand
                if not vid:
                    m = re.search(r'\"videoId\":\s*\"([a-zA-Z0-9_-]{11})\"', json.dumps(slvm))
                    if m:
                        vid = m.group(1)

                if vid:
                    title = slvm.get("overlayMetadata", {}).get("primaryText", {}).get("content", "").strip()
                    if not title and slvm.get("accessibilityText"):
                        title = re.sub(r",\s*\d+.*views.*", "", slvm.get("accessibilityText", "")).strip()
                    v_str = slvm.get("overlayMetadata", {}).get("secondaryText", {}).get("content", "")
                    views = parse_numeric_count(v_str)

                    thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    sources = slvm.get("thumbnailViewModel", {}).get("image", {}).get("sources", [])
                    if sources:
                        thumb = sources[-1].get("url", thumb)

                    results[vid] = {
                        "video_id": vid,
                        "title": title,
                        "view_count": views,
                        "length_seconds": 0,
                        "published_time_text": "",
                        "thumbnail_url": thumb,
                        "is_short": True,
                    }

            # 4. reelItemRenderer (/shorts tab classic)
            elif "reelItemRenderer" in rfm:
                rr = rfm["reelItemRenderer"]
                vid = rr.get("videoId", "")
                if vid:
                    headline = rr.get("headline", {}).get("simpleText", "")
                    if not headline:
                        h_runs = rr.get("headline", {}).get("runs", [])
                        headline = h_runs[0].get("text", "") if h_runs else ""
                    v_text = rr.get("viewCountText", {}).get("simpleText", "")
                    views = parse_numeric_count(v_text)
                    thumbs = rr.get("thumbnail", {}).get("thumbnails", [])
                    thumb = thumbs[-1].get("url", f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg") if thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    results[vid] = {
                        "video_id": vid,
                        "title": headline.strip(),
                        "view_count": views,
                        "length_seconds": 0,
                        "published_time_text": "",
                        "thumbnail_url": thumb,
                        "is_short": True,
                    }

    # 5. Regex-scan fallback: ONLY if structured tab parsing yielded NO videos,
    # and restrict exclusively to the selected tabRenderer content when channel ID matches.
    # Never perform blind regex scanning across entire ytInitialData when structured parsing succeeded!
    if not results and selected_content:
        channel_matches = True
        if expected_channel_id and external_id:
            channel_matches = (external_id == expected_channel_id)

        if channel_matches:
            content_str = json.dumps(selected_content)
            matched_ids = re.findall(
                r'(?:\"videoId\":\s*\"|/watch\?v=|/shorts/)([a-zA-Z0-9_-]{11})', content_str
            )
            for vid in matched_ids:
                if vid not in results and len(vid) == 11 and vid not in ("watch_later", "playlist_wl"):
                    results[vid] = {
                        "video_id": vid,
                        "title": "",
                        "view_count": 0,
                        "length_seconds": 0,
                        "published_time_text": "",
                        "thumbnail_url": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                        "is_short": is_short,
                    }

    return results


def scrape_channel_tabs_bulk(
    handle: str, channel_id: str = "", timeout: float = 10.0
) -> Dict[str, Dict[str, Any]]:
    """Scrape public /videos and /shorts tabs for a channel (only 2 HTTP requests).

    Returns a combined dictionary mapping video_id -> bulk video details.
    ALWAYS prioritizes channel_id over handle whenever channel_id is non-empty.
    """
    clean_cid = channel_id.strip() if channel_id else ""
    clean_handle = handle.strip() if handle else ""
    if clean_handle and not clean_handle.startswith("@"):
        clean_handle = f"@{clean_handle}"

    # Ground-truth: ALWAYS prioritize channel_id over handle whenever channel_id is non-empty!
    if clean_cid:
        base_url = f"https://www.youtube.com/channel/{clean_cid}"
    elif clean_handle:
        base_url = f"https://www.youtube.com/{clean_handle}"
    else:
        return {}

    videos_url = f"{base_url}/videos"
    shorts_url = f"{base_url}/shorts"

    def _fetch_tab(url: str, is_short: bool) -> Dict[str, Dict[str, Any]]:
        try:
            html = fetch_url(url, timeout=timeout)
            return parse_tab_initial_data(html, is_short=is_short, expected_channel_id=clean_cid)
        except Exception as exc:
            logger.debug("Failed fetching tab %s: %s", url, exc)
            return {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f_videos = pool.submit(_fetch_tab, videos_url, False)
        f_shorts = pool.submit(_fetch_tab, shorts_url, True)
        videos_dict = f_videos.result()
        shorts_dict = f_shorts.result()

    combined: Dict[str, Dict[str, Any]] = {}
    combined.update(videos_dict)
    combined.update(shorts_dict)
    return combined


def verify_channel_actual_video_count(
    handle: str = "", channel_id: str = "", timeout: float = 10.0
) -> Dict[str, Any]:
    """Verify actual public video count and list for a channel prioritizing canonical ID."""
    clean_cid = channel_id.strip() if channel_id else ""
    clean_handle = handle.strip() if handle else ""
    tab_items = scrape_channel_tabs_bulk(handle=clean_handle, channel_id=clean_cid, timeout=timeout)
    long_count = sum(1 for v in tab_items.values() if not v.get("is_short"))
    short_count = sum(1 for v in tab_items.values() if v.get("is_short"))
    return {
        "channel_id": clean_cid,
        "handle": clean_handle,
        "total_count": len(tab_items),
        "long_count": long_count,
        "short_count": short_count,
        "video_ids": list(tab_items.keys()),
        "videos": tab_items,
    }


def scrape_video_metrics_resilient(
    video_id: str,
    is_short: bool = False,
    bulk_tab_info: Optional[Dict[str, Any]] = None,
    channel_map_entry: Optional[Dict[str, Any]] = None,
    cached_metrics: Optional[Dict[str, Any]] = None,
    timeout: float = 8.0,
    allow_watch_scrape: bool = True,
) -> Dict[str, Any]:
    """Scrape video metrics from YouTube watch page with resilient multi-tier fallbacks."""
    metrics: Dict[str, Any] = {
        "video_id": video_id,
        "video_url": f"https://youtube.com/shorts/{video_id}" if is_short else f"https://youtu.be/{video_id}",
        "title": "",
        "view_count": 0,
        "like_count": 0,
        "comment_count_text": "0",
        "length_seconds": 0,
        "publish_date": "",
        "is_public": True,
        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
        "scraped_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if not video_id:
        return metrics

    # 1. Direct watch page scrape if allowed
    if allow_watch_scrape:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            html = fetch_url(watch_url, timeout=timeout)
            # Check ytInitialPlayerResponse
            p_marker = "ytInitialPlayerResponse = "
            p_idx = html.find(p_marker)
            if p_idx != -1:
                try:
                    start_pos = p_idx + len(p_marker)
                    player_data, _ = json.JSONDecoder().raw_decode(html[start_pos:])

                    # Playability / Private status check
                    play_status = player_data.get("playabilityStatus", {})
                    status_code = play_status.get("status", "")
                    reason = play_status.get("reason", "").lower()
                    if status_code in ("LOGIN_REQUIRED", "ERROR") and "private" in reason:
                        metrics["is_public"] = False

                    vd = player_data.get("videoDetails", {})
                    if vd:
                        metrics["title"] = vd.get("title", "").strip()
                        metrics["view_count"] = int(vd.get("viewCount", 0) or 0)
                        metrics["length_seconds"] = int(vd.get("lengthSeconds", 0) or 0)
                        if vd.get("isPrivate"):
                            metrics["is_public"] = False

                    micro = player_data.get("microformat", {}).get("playerMicroformatRenderer", {})
                    if micro:
                        metrics["publish_date"] = micro.get("publishDate") or micro.get("uploadDate") or ""
                        if micro.get("isUnlisted"):
                            metrics["is_public"] = False
                        if "likeCount" in micro:
                            metrics["like_count"] = parse_numeric_count(str(micro.get("likeCount", 0)))
                        thumbs = micro.get("thumbnail", {}).get("thumbnails", [])
                        if not thumbs and vd:
                            thumbs = vd.get("thumbnail", {}).get("thumbnails", [])
                        if thumbs:
                            metrics["thumbnail_url"] = thumbs[-1].get("url", metrics["thumbnail_url"])
                except Exception as exc:
                    logger.debug("Error parsing ytInitialPlayerResponse for %s: %s", video_id, exc)

            # Check ytInitialData for likes and comments
            d_marker = "ytInitialData = "
            d_idx = html.find(d_marker)
            if d_idx != -1:
                try:
                    start_pos = d_idx + len(d_marker)
                    data, _ = json.JSONDecoder().raw_decode(html[start_pos:])
                    d_str = json.dumps(data)

                    if metrics["like_count"] == 0:
                        like_match = re.search(
                            r'\"segmentedLikeDislikeButtonViewModel\":\{\"likeButtonViewModel\":\{\"likeButtonViewModel\":\{\"toggleButtonViewModel\":\{\"toggleButtonViewModel\":\{\"defaultButtonViewModel\":\{\"buttonViewModel\":\{\"iconName\":\"LIKE\",\"title\":\"([^\"]+)\"',
                            d_str,
                        )
                        if like_match:
                            metrics["like_count"] = parse_numeric_count(like_match.group(1))

                    comm_match = re.search(
                        r'\"commentsHeaderRenderer\":\{\"countText\":\{\"runs\":\[\{\"text\":\"([^\"]+)\"\}',
                        d_str,
                    )
                    if comm_match:
                        c_text = comm_match.group(1).strip()
                        if c_text.lower() != "comments":
                            metrics["comment_count_text"] = c_text
                except Exception as exc:
                    logger.debug("Error parsing ytInitialData for %s: %s", video_id, exc)
        except Exception as exc:
            logger.debug("Failed watch scrape for %s: %s", video_id, exc)

    # 2. Resilient Fallbacks
    # (a) Title fallback
    if not metrics["title"]:
        if bulk_tab_info and bulk_tab_info.get("title"):
            metrics["title"] = bulk_tab_info["title"].strip()
        elif channel_map_entry and channel_map_entry.get("title"):
            metrics["title"] = channel_map_entry["title"].strip()
        elif cached_metrics and cached_metrics.get("title"):
            metrics["title"] = cached_metrics["title"].strip()
        else:
            oe_title = fetch_oembed_title(video_id)
            if oe_title:
                metrics["title"] = oe_title

    # (b) View count fallback
    bulk_views = bulk_tab_info.get("view_count", 0) if bulk_tab_info else 0
    cached_views = cached_metrics.get("view_count", 0) if cached_metrics else 0
    metrics["view_count"] = max(metrics["view_count"], bulk_views, cached_views)

    # (c) Like count fallback
    if metrics["like_count"] == 0 and cached_metrics and cached_metrics.get("like_count", 0) > 0:
        metrics["like_count"] = cached_metrics.get("like_count", 0)

    # (d) Length seconds fallback
    if metrics["length_seconds"] == 0:
        bulk_len = bulk_tab_info.get("length_seconds", 0) if bulk_tab_info else 0
        cached_len = cached_metrics.get("length_seconds", 0) if cached_metrics else 0
        metrics["length_seconds"] = max(bulk_len, cached_len)

    # (e) Publish date fallback
    if not metrics["publish_date"]:
        if channel_map_entry and channel_map_entry.get("published_at"):
            metrics["publish_date"] = channel_map_entry["published_at"]
        elif cached_metrics and cached_metrics.get("publish_date"):
            metrics["publish_date"] = cached_metrics["publish_date"]

    # (f) Thumbnail URL fallback
    if not metrics["thumbnail_url"] or metrics["thumbnail_url"].endswith("/hqdefault.jpg"):
        if bulk_tab_info and bulk_tab_info.get("thumbnail_url"):
            metrics["thumbnail_url"] = bulk_tab_info["thumbnail_url"]
        elif cached_metrics and cached_metrics.get("thumbnail_url"):
            metrics["thumbnail_url"] = cached_metrics["thumbnail_url"]

    # (g) Is public verification
    if bulk_tab_info and (bulk_tab_info.get("view_count", 0) > 0 or bulk_tab_info.get("title")):
        metrics["is_public"] = True

    return metrics


def scrape_channel_metrics(
    channel_key: str,
    channel_id: str,
    handle: str,
    cached_channel: Optional[Dict[str, Any]] = None,
    timeout: float = 12.0,
) -> Dict[str, Any]:
    """Scrape live subscriber count, video count, avatar and snippet from YouTube channel."""
    url = f"https://www.youtube.com/channel/{channel_id}" if channel_id else f"https://www.youtube.com/{handle}"
    metrics: Dict[str, Any] = {
        "channel_key": channel_key,
        "subscriber_count_text": "0 subscribers",
        "subscriber_count": 0,
        "videos_count_text": "0 videos",
        "videos_count": 0,
        "avatar_url": "",
        "description_snippet": "",
        "header_badge_lag": False,
        "raw_videos_count_text": "0 videos",
        "verified_video_ids": [],
        "scraped_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if not channel_id and not handle:
        return metrics

    try:
        html = fetch_url(url, timeout=timeout)
        d_marker = "ytInitialData = "
        d_idx = html.find(d_marker)
        if d_idx != -1:
            start_pos = d_idx + len(d_marker)
            data, _ = json.JSONDecoder().raw_decode(html[start_pos:])

            ph = data.get("header", {}).get("pageHeaderRenderer", {})
            model = ph.get("content", {}).get("pageHeaderViewModel", {})
            meta_rows = model.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", [])
            parts: List[str] = []
            for row in meta_rows:
                for part in row.get("metadataParts", []):
                    c = part.get("text", {}).get("content", "").strip()
                    if c:
                        parts.append(c)

            for p in parts:
                low = p.lower()
                if "subscriber" in low:
                    metrics["subscriber_count_text"] = p
                    metrics["subscriber_count"] = parse_numeric_count(p)
                elif "video" in low:
                    metrics["videos_count_text"] = p
                    metrics["videos_count"] = parse_numeric_count(p)

            avatar_sources = (
                model.get("image", {})
                .get("decoratedAvatarViewModel", {})
                .get("avatar", {})
                .get("avatarViewModel", {})
                .get("image", {})
                .get("sources", [])
            )
            if avatar_sources:
                metrics["avatar_url"] = avatar_sources[-1].get("url", "")

            desc = (
                model.get("description", {})
                .get("descriptionPreviewViewModel", {})
                .get("description", {})
                .get("content", "")
            )
            if not desc:
                desc = data.get("microformat", {}).get("microformatDataRenderer", {}).get("description", "")
            metrics["description_snippet"] = desc.strip()
    except Exception as exc:
        logger.debug("Failed parsing channel ytInitialData for %s: %s", channel_key, exc)

    # Fallback to cached metrics if live channel scrape hit consent/rate-limit
    if cached_channel:
        if metrics["subscriber_count"] == 0 and cached_channel.get("subscriber_count", 0) > 0:
            metrics["subscriber_count"] = cached_channel["subscriber_count"]
            metrics["subscriber_count_text"] = cached_channel.get(
                "subscriber_count_text", f"{cached_channel['subscriber_count']} subscribers"
            )
        if not metrics["avatar_url"] and cached_channel.get("avatar_url"):
            metrics["avatar_url"] = cached_channel["avatar_url"]
        if not metrics["description_snippet"] and cached_channel.get("description_snippet"):
            metrics["description_snippet"] = cached_channel["description_snippet"]

    metrics["raw_videos_count_text"] = metrics["videos_count_text"]
    return metrics


def find_local_deliverable(
    channel_key: str, batch: str, format_profile: str, repo_root: Path = REPO_ROOT
) -> Tuple[str, str]:
    """Find local job_id and mp4_relpath from channel release locks."""
    ch_dir = repo_root / "sys" / "channels" / channel_key
    for lock_name in (f"{batch}_v2_release_lock.json", f"{batch}_release_lock.json"):
        lock_p = ch_dir / lock_name
        if lock_p.exists():
            try:
                data = json.loads(lock_p.read_text(encoding="utf-8"))
                deliv = data.get("deliverables", {}).get(format_profile, {})
                if deliv.get("job_id"):
                    return deliv.get("job_id", ""), deliv.get("mp4_relpath", "")
            except Exception:
                pass
    return "", ""


def append_and_load_history(
    history_path: Path, current_totals: Dict[str, Any], batches_count: int, max_entries: int = 30
) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
    """Store compact history entry in JSONL and compute deltas from previous snapshot."""
    history_entries: List[Dict[str, Any]] = []
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        history_entries.append(json.loads(line))
        except Exception as exc:
            logger.warning("Failed reading history from %s: %s", history_path, exc)

    prev_entry = history_entries[-1] if history_entries else None
    current_views = current_totals.get("total_views", 0)
    current_likes = current_totals.get("total_likes", 0)
    current_subs = current_totals.get("total_subscribers", 0)

    deltas = {
        "views_delta": (current_views - prev_entry.get("total_views", 0)) if prev_entry else 0,
        "likes_delta": (current_likes - prev_entry.get("total_likes", 0)) if prev_entry else 0,
        "subs_delta": (current_subs - prev_entry.get("total_subscribers", 0)) if prev_entry else 0,
    }

    new_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_videos": current_totals.get("total_videos", 0),
        "total_views": current_views,
        "total_likes": current_likes,
        "total_subscribers": current_subs,
        "batches_count": batches_count,
    }

    history_entries.append(new_entry)
    try:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(new_entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.warning("Failed writing history entry to %s: %s", history_path, exc)

    return deltas, history_entries[-max_entries:]


def sync_discovered_videos_to_channel_map(
    channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH,
    discovered_by_channel: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
) -> int:
    """Sync newly discovered public channel videos back to youtube_channel_map.json."""
    if not channel_map_path.exists():
        return 0

    try:
        raw_map = json.loads(channel_map_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error("Failed loading channel map for sync: %s", exc)
        return 0

    channels_dict = raw_map.get("channels", {})
    if discovered_by_channel is None:
        discovered_by_channel = {}
        for key, info in channels_dict.items():
            discovered_by_channel[key] = scrape_channel_tabs_bulk(
                info.get("handle", ""), info.get("youtube_channel_id", "")
            )

    added_count = 0
    purged_count = 0
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for key, info in channels_dict.items():
        tab_vids = discovered_by_channel.get(key, {})

        # Defensive cleanup: purge any foreign blacklist videos or stale discovered videos
        if "published_videos" in info:
            cleaned_pubs = []
            for pv in info["published_videos"]:
                p_vid = extract_video_id(pv.get("video_url"))
                if p_vid in FOREIGN_VIDEO_BLACKLIST:
                    purged_count += 1
                    continue
                if pv.get("batch") == "discovered" and p_vid not in tab_vids:
                    purged_count += 1
                    continue
                cleaned_pubs.append(pv)
            info["published_videos"] = cleaned_pubs

        existing_vids = {
            extract_video_id(pv.get("video_url")) for pv in info.get("published_videos", [])
        }

        for vid, item in tab_vids.items():
            if vid and vid not in existing_vids and vid not in FOREIGN_VIDEO_BLACKLIST:
                is_short = bool(item.get("is_short", False))
                new_entry = {
                    "video_url": f"https://youtube.com/shorts/{vid}" if is_short else f"https://youtu.be/{vid}",
                    "title": item.get("title", ""),
                    "format": "short_9x16" if is_short else "long_16x9",
                    "batch": "discovered",
                    "related_video_url": None,
                    "published_at": now_iso,
                }
                if "published_videos" not in info:
                    info["published_videos"] = []
                info["published_videos"].append(new_entry)
                existing_vids.add(vid)
                added_count += 1
                logger.info("Synced new discovered video %s to %s", vid, key)

    if added_count > 0 or purged_count > 0:
        try:
            channel_map_path.write_text(json.dumps(raw_map, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info("Saved %d newly discovered videos to %s", added_count, channel_map_path)
        except Exception as exc:
            logger.error("Failed saving updated channel map: %s", exc)

    return added_count


def collect_scalable_dashboard_metrics(
    channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH,
    output_path: Optional[Path] = DEFAULT_METRICS_PATH,
    history_path: Optional[Path] = DEFAULT_HISTORY_PATH,
    incremental: bool = False,
    force_full: bool = False,
    auto_sync_map: bool = False,
    cache_ttl_seconds: float = 180.0,
    max_workers: int = 32,
) -> Dict[str, Any]:
    """Scrape and aggregate fleet metrics scaling from 32 to 100-1,000+ videos.

    Combines 2-call bulk tab discovery, resilient watch page enrichment,
    funnel matrix verification, and historical trend tracking.
    """
    if not channel_map_path.exists():
        raise FileNotFoundError(f"Missing channel map file at {channel_map_path}")

    raw_map = json.loads(channel_map_path.read_text(encoding="utf-8"))
    channels_dict = raw_map.get("channels", {})
    channel_keys = list(channels_dict.keys())

    # Load existing cached metrics if present
    cached_videos_by_id: Dict[str, Dict[str, Any]] = {}
    cached_channels_by_id: Dict[str, Dict[str, Any]] = {}
    if output_path and output_path.exists():
        try:
            prev_snapshot = json.loads(output_path.read_text(encoding="utf-8"))
            for v in prev_snapshot.get("all_videos", []):
                if v.get("video_id"):
                    cached_videos_by_id[v["video_id"]] = v
            for c in prev_snapshot.get("channels", []):
                if c.get("channel_id"):
                    cached_channels_by_id[c["channel_id"]] = c
        except Exception as exc:
            logger.debug("Failed reading existing metrics from %s: %s", output_path, exc)

    t0 = time.time()
    logger.info("Initiating scalable fleet discovery for %d channels...", len(channel_keys))

    # Phase 1: Parallel bulk tab discovery & channel header scrape (16 tab calls + 8 channel calls)
    bulk_tabs_by_channel: Dict[str, Dict[str, Dict[str, Any]]] = {}
    channel_headers: Dict[str, Dict[str, Any]] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        tab_futures = {
            key: pool.submit(
                scrape_channel_tabs_bulk,
                channels_dict[key].get("handle", ""),
                channels_dict[key].get("youtube_channel_id", ""),
            )
            for key in channel_keys
        }
        header_futures = {
            key: pool.submit(
                scrape_channel_metrics,
                key,
                channels_dict[key].get("youtube_channel_id", ""),
                channels_dict[key].get("handle", ""),
                cached_channels_by_id.get(key),
            )
            for key in channel_keys
        }

        for key in channel_keys:
            bulk_tabs_by_channel[key] = tab_futures[key].result()
            channel_headers[key] = header_futures[key].result()

    tab_elapsed = time.time() - t0
    logger.info("Bulk tab discovery completed in %.2f seconds.", tab_elapsed)

    # Auto-sync discovered videos if requested
    if auto_sync_map:
        sync_discovered_videos_to_channel_map(channel_map_path, bulk_tabs_by_channel)

    # Load registry channels metadata (SSOT)
    reg_map: Dict[str, Any] = {}
    if get_registry_channels is not None:
        try:
            reg_map = get_registry_channels()
        except Exception as exc:
            logger.debug("Failed loading registry channels: %s", exc)

    # Phase 2: Compile complete video catalog per channel
    # Merge mapped published_videos with any extra discovered videos
    video_tasks: List[Dict[str, Any]] = []

    for key in channel_keys:
        info = channels_dict[key]
        ch_reg = reg_map.get(key)
        ch_name = info.get("channel_name", key)
        handle = info.get("handle", "")
        ch_email = info.get("email", "") or (getattr(ch_reg, "email", "") if ch_reg else "")
        ch_prof = info.get("profile_id", "")
        ch_port = info.get("cdp_port", 0)
        ch_wave = getattr(ch_reg, "wave", 1) if ch_reg else info.get("wave", 1)
        ch_lang = getattr(ch_reg, "language", "en" if key.startswith("en_") else "vi")
        pub_list = info.get("published_videos", [])
        tab_vids = bulk_tabs_by_channel.get(key, {})
        mapped_vids: set[str] = set()

        for pv in pub_list:
            v_url = pv.get("video_url", "")
            vid = extract_video_id(v_url)
            if not vid or vid in FOREIGN_VIDEO_BLACKLIST:
                continue
            if pv.get("batch") == "discovered" and vid not in tab_vids:
                continue
            mapped_vids.add(vid)
            is_sh = pv.get("format") == "short_9x16"
            video_tasks.append({
                "video_id": vid,
                "channel_key": key,
                "channel_name": ch_name,
                "handle": handle,
                "email": ch_email,
                "profile_id": ch_prof,
                "cdp_port": ch_port,
                "wave": ch_wave,
                "language": ch_lang,
                "is_short": is_sh,
                "format": pv.get("format", "short_9x16" if is_sh else "long_16x9"),
                "batch": pv.get("batch", "week1"),
                "published_at": pv.get("published_at", ""),
                "related_video_url": pv.get("related_video_url"),
                "map_entry": pv,
                "bulk_tab_info": tab_vids.get(vid),
            })

        # Extra discovered public videos
        for vid, b_item in tab_vids.items():
            if vid not in mapped_vids and vid not in FOREIGN_VIDEO_BLACKLIST:
                is_sh = bool(b_item.get("is_short", False))
                video_tasks.append({
                    "video_id": vid,
                    "channel_key": key,
                    "channel_name": ch_name,
                    "handle": handle,
                    "email": ch_email,
                    "profile_id": ch_prof,
                    "cdp_port": ch_port,
                    "wave": ch_wave,
                    "language": ch_lang,
                    "is_short": is_sh,
                    "format": "short_9x16" if is_sh else "long_16x9",
                    "batch": "discovered",
                    "published_at": "",
                    "related_video_url": None,
                    "map_entry": None,
                    "bulk_tab_info": b_item,
                })

    total_catalog_videos = len(video_tasks)
    logger.info("Found %d total videos across %d channels. Commencing enrichment...", total_catalog_videos, len(channel_keys))

    # Phase 3: Parallel Per-Video Enrichment with Smart Caching
    now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
    enriched_by_id: Dict[str, Dict[str, Any]] = {}

    def _enrich_task(task: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        vid = task["video_id"]
        is_sh = task["is_short"]
        bulk_info = task["bulk_tab_info"]
        map_entry = task["map_entry"]
        cached = cached_videos_by_id.get(vid)

        # Smart Caching evaluation
        allow_watch = True
        if incremental and not force_full and total_catalog_videos > 40 and cached:
            scraped_iso = cached.get("scraped_at", "")
            if scraped_iso:
                try:
                    s_dt = datetime.datetime.fromisoformat(scraped_iso)
                    age = now_ts - s_dt.timestamp()
                    if age < cache_ttl_seconds and bulk_info and bulk_info.get("title"):
                        allow_watch = False
                except Exception:
                    pass

        raw_enriched = scrape_video_metrics_resilient(
            video_id=vid,
            is_short=is_sh,
            bulk_tab_info=bulk_info,
            channel_map_entry=map_entry,
            cached_metrics=cached,
            timeout=8.0,
            allow_watch_scrape=allow_watch,
        )
        return vid, raw_enriched

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        enrich_futs = [pool.submit(_enrich_task, t) for t in video_tasks]
        for f in concurrent.futures.as_completed(enrich_futs):
            vid, res = f.result()
            enriched_by_id[vid] = res

    # Phase 4: Construct Canonical Video Dictionaries & Link Funnel Matrix
    all_videos: List[Dict[str, Any]] = []
    videos_by_channel: Dict[str, List[Dict[str, Any]]] = {k: [] for k in channel_keys}

    # Map of all short related_video_ids for funnel lookup
    funnel_target_ids: set[str] = set()
    for task in video_tasks:
        rel_url = task.get("related_video_url")
        if rel_url:
            target_id = extract_video_id(rel_url)
            if target_id:
                funnel_target_ids.add(target_id)

    for task in video_tasks:
        vid = task["video_id"]
        ch_k = task["channel_key"]
        enr = enriched_by_id.get(vid, {})
        rel_url = task.get("related_video_url")
        rel_vid = extract_video_id(rel_url) if rel_url else ""
        fmt = task["format"]
        is_sh = task["is_short"]
        b_id = task["batch"]

        # Funnel linkage rule:
        # For Short: True if valid related_video_id exists
        # For Long: True if long video_id is targeted by any short
        if is_sh:
            has_funnel = bool(rel_vid)
        else:
            has_funnel = vid in funnel_target_ids

        v_count = enr.get("view_count", 0)
        l_count = enr.get("like_count", 0)
        eng_rate = round(l_count / v_count * 100, 2) if v_count > 0 else 0.0

        pub_at = task.get("published_at") or enr.get("publish_date", "")
        pub_date = enr.get("publish_date") or (pub_at[:10] if len(pub_at) >= 10 else "")

        job_id, local_mp4 = find_local_deliverable(ch_k, b_id, fmt)

        canon_video = {
            "video_id": vid,
            "video_url": f"https://youtube.com/shorts/{vid}" if is_sh else f"https://youtu.be/{vid}",
            "channel_id": ch_k,
            "channel_name": task["channel_name"],
            "handle": task["handle"],
            "email": task.get("email", ""),
            "profile_id": task.get("profile_id", ""),
            "cdp_port": task.get("cdp_port", 0),
            "wave": task.get("wave", 1),
            "language": task.get("language", "en" if ch_k.startswith("en_") else "vi"),
            "title": enr.get("title", ""),
            "format": fmt,
            "is_short": is_sh,
            "batch": b_id,
            "batch_label": format_batch_label(b_id),
            "published_at": pub_at,
            "publish_date": pub_date,
            "view_count": v_count,
            "like_count": l_count,
            "engagement_rate": eng_rate,
            "comment_count_text": enr.get("comment_count_text", "0"),
            "length_seconds": enr.get("length_seconds", 0),
            "duration_formatted": format_duration(enr.get("length_seconds", 0)),
            "is_public": enr.get("is_public", True),
            "related_video_url": rel_url,
            "related_video_id": rel_vid,
            "has_funnel_link": has_funnel,
            "thumbnail_url": enr.get("thumbnail_url", f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"),
            "job_id": job_id,
            "local_mp4_relpath": local_mp4,
            "scraped_at": enr.get("scraped_at", datetime.datetime.now(datetime.timezone.utc).isoformat()),
        }
        all_videos.append(canon_video)
        videos_by_channel[ch_k].append(canon_video)

    # Sort each channel's videos: newest published first, then Long before Short
    def _video_sort_key(v: Dict[str, Any]) -> Tuple[int, str, int]:
        batch_rank = 10
        b_low = v["batch"].lower()
        if b_low.startswith("batch") and b_low[5:].isdigit():
            batch_rank = int(b_low[5:]) * 10
        elif b_low == "week1":
            batch_rank = 1
        elif b_low == "discovered":
            batch_rank = 0
        pub_str = v.get("published_at") or v.get("publish_date") or ""
        format_order = 0 if v["format"] == "long_16x9" else 1
        return (batch_rank, pub_str, -format_order)

    for ch_k in channel_keys:
        videos_by_channel[ch_k].sort(key=_video_sort_key, reverse=True)

    # Phase 5: Build Batches Breakdown & Funnel Matrix
    batches_map: Dict[str, Dict[str, Any]] = {}
    funnel_matrix: List[Dict[str, Any]] = []

    for v in all_videos:
        b_id = v["batch"]
        if b_id not in batches_map:
            batches_map[b_id] = {
                "batch_id": b_id,
                "batch_label": format_batch_label(b_id),
                "videos_count": 0,
                "long_count": 0,
                "short_count": 0,
                "views": 0,
                "likes": 0,
                "avg_views": 0.0,
                "_max_published": "",
            }
        b_obj = batches_map[b_id]
        b_obj["videos_count"] += 1
        if v["format"] == "long_16x9":
            b_obj["long_count"] += 1
        else:
            b_obj["short_count"] += 1
        b_obj["views"] += v["view_count"]
        b_obj["likes"] += v["like_count"]
        if v["published_at"] > b_obj["_max_published"]:
            b_obj["_max_published"] = v["published_at"]

    for b_obj in batches_map.values():
        cnt = b_obj["videos_count"]
        b_obj["avg_views"] = round(b_obj["views"] / cnt, 1) if cnt > 0 else 0.0

    # Sort batches newest first
    sorted_batches = sorted(
        batches_map.values(),
        key=lambda b: (b["_max_published"], b["batch_id"]),
        reverse=True,
    )
    for b in sorted_batches:
        b.pop("_max_published", None)

    # Phase 6: Build Per-Channel Objects & Fleet Totals
    channels_list: List[Dict[str, Any]] = []
    fleet_total_views = sum(v["view_count"] for v in all_videos)
    fleet_total_likes = sum(v["like_count"] for v in all_videos)
    fleet_total_subs = 0
    total_long_vids = sum(1 for v in all_videos if v["format"] == "long_16x9")
    total_short_vids = sum(1 for v in all_videos if v["format"] == "short_9x16")
    long_views = sum(v["view_count"] for v in all_videos if v["format"] == "long_16x9")
    short_views = sum(v["view_count"] for v in all_videos if v["format"] == "short_9x16")
    funnel_linked_shorts = sum(1 for v in all_videos if v["format"] == "short_9x16" and v["has_funnel_link"])

    for key in channel_keys:
        info = channels_dict[key]
        header = channel_headers[key]
        vids = videos_by_channel[key]

        ch_subs = header.get("subscriber_count", 0)
        fleet_total_subs += ch_subs
        ch_views = sum(v["view_count"] for v in vids)
        ch_likes = sum(v["like_count"] for v in vids)

        # Find latest long and short
        long_vids = [v for v in vids if v["format"] == "long_16x9"]
        short_vids = [v for v in vids if v["format"] == "short_9x16"]
        latest_long = long_vids[0] if long_vids else {}
        latest_short = short_vids[0] if short_vids else {}

        # Find week1 long and short
        week1_long = next((v for v in long_vids if v["batch"] == "week1"), None)
        week1_short = next((v for v in short_vids if v["batch"] == "week1"), None)

        # Channel batches breakdown & funnel pairs
        ch_batches_map: Dict[str, Dict[str, Any]] = {}
        for v in vids:
            bid = v["batch"]
            if bid not in ch_batches_map:
                ch_batches_map[bid] = {"videos_count": 0, "views": 0, "likes": 0}
            ch_batches_map[bid]["videos_count"] += 1
            ch_batches_map[bid]["views"] += v["view_count"]
            ch_batches_map[bid]["likes"] += v["like_count"]

        # Funnel pairs per batch
        funnel_pairs: List[Dict[str, Any]] = []
        batch_ids = sorted(list({v["batch"] for v in vids}), reverse=True)
        for bid in batch_ids:
            batch_longs = [v for v in long_vids if v["batch"] == bid]
            batch_shorts = [v for v in short_vids if v["batch"] == bid]

            # Match shorts to longs
            for s_item in batch_shorts:
                rel_v = s_item.get("related_video_id")
                matching_long = next((lv for lv in batch_longs if lv["video_id"] == rel_v), None)
                if not matching_long and batch_longs:
                    matching_long = batch_longs[0]

                is_link = bool(matching_long and rel_v == matching_long["video_id"])
                l_v = matching_long["view_count"] if matching_long else 0
                s_v = s_item["view_count"]
                ratio = round(s_v / l_v, 2) if l_v > 0 else 0.0

                pair_obj = {
                    "batch": bid,
                    "batch_label": format_batch_label(bid),
                    "long_video": matching_long,
                    "short_video": s_item,
                    "is_linked": is_link,
                    "funnel_view_ratio": ratio,
                }
                funnel_pairs.append(pair_obj)

                funnel_matrix.append({
                    "channel_id": key,
                    "channel_name": info.get("channel_name", key),
                    "handle": info.get("handle", ""),
                    "batch": bid,
                    "batch_label": format_batch_label(bid),
                    "long_video_id": matching_long.get("video_id") if matching_long else "",
                    "long_title": matching_long.get("title") if matching_long else "",
                    "long_views": l_v,
                    "long_likes": matching_long.get("like_count", 0) if matching_long else 0,
                    "short_video_id": s_item.get("video_id", ""),
                    "short_title": s_item.get("title", ""),
                    "short_views": s_v,
                    "short_likes": s_item.get("like_count", 0),
                    "is_linked": is_link,
                    "funnel_view_ratio": ratio,
                })

        # Avatar fallback
        avatar_final = header.get("avatar_url", "")
        if not avatar_final:
            local_avatar = REPO_ROOT / "sys" / "channels" / key / "assets" / "avatar_800x800.png"
            if local_avatar.exists():
                avatar_final = f"/assets/{key}/avatar_800x800.png"

        # Public count verification
        public_vids_count = sum(1 for v in vids if v.get("is_public"))
        verified_ids = [v["video_id"] for v in vids if v.get("is_public")]
        badge_lag = header.get("videos_count", 0) > public_vids_count

        yt_id = info.get("youtube_channel_id", "")
        ch_reg = reg_map.get(key)
        niche = getattr(ch_reg, "niche", "") if ch_reg else info.get("niche", "")
        promise = getattr(ch_reg, "promise", "") if ch_reg else info.get("promise", "")
        persona = getattr(ch_reg, "persona", "") if ch_reg else info.get("persona", "")
        wave = getattr(ch_reg, "wave", 1) if ch_reg else info.get("wave", 1)
        email = info.get("email", "") or (getattr(ch_reg, "email", "") if ch_reg else "")

        references: List[Dict[str, str]] = []
        if ch_reg and hasattr(ch_reg, "references"):
            for r in ch_reg.references:
                references.append({
                    "name": getattr(r, "name", ""),
                    "platform": getattr(r, "platform", ""),
                    "format": getattr(r, "format", ""),
                    "learn": getattr(r, "learn", ""),
                })
        elif "references" in info:
            references = info.get("references", [])

        seed_topics = list(getattr(ch_reg, "seed_topics", ())) if ch_reg else list(info.get("seed_topics", []))
        hook_formulas = list(getattr(ch_reg, "hook_formulas", ())) if ch_reg else list(info.get("hook_formulas", []))

        arch = get_visual_archetype(key) if get_visual_archetype else {"id": "unknown", "label": "Unknown"}
        vis = getattr(ch_reg, "visual", None)
        vis_profile_id = getattr(vis, "profile_id", "") if vis else ""
        vis_label = getattr(vis, "label", "") if vis else ""
        vis_palette = list(getattr(vis, "palette", ())) if vis else []

        channel_obj = {
            "channel_id": key,
            "channel_name": info.get("channel_name", key),
            "handle": info.get("handle", ""),
            "slug": info.get("slug", key),
            "youtube_channel_id": yt_id,
            "youtube_channel_url": f"https://www.youtube.com/channel/{yt_id}",
            "studio_url": f"https://studio.youtube.com/channel/{yt_id}",
            "analytics_url": f"https://studio.youtube.com/channel/{yt_id}/analytics",
            "email": email,
            "profile_id": info.get("profile_id", ""),
            "visual_profile_id": vis_profile_id,
            "visual_label": vis_label,
            "visual_archetype_id": arch["id"],
            "visual_archetype_label": arch["label"],
            "visual_palette": vis_palette,
            "cdp_port": info.get("cdp_port", 0),
            "directory": info.get("directory", ""),
            "user_data_dir": info.get("user_data_dir", ""),
            "avatar_url": avatar_final,
            "niche": niche,
            "promise": promise,
            "persona": persona,
            "wave": wave,
            "language": getattr(ch_reg, "language", "en" if key.startswith("en_") else "vi"),
            "references": references,
            "seed_topics": seed_topics,
            "hook_formulas": hook_formulas,
            "description_snippet": header.get("description_snippet", ""),
            "subscriber_count_text": header.get("subscriber_count_text", "0 subscribers"),
            "subscriber_count": ch_subs,
            "videos_count_text": f"{public_vids_count} videos",
            "videos_count": public_vids_count,
            "header_badge_lag": badge_lag,
            "raw_videos_count_text": header.get("videos_count_text", f"{public_vids_count} videos"),
            "verified_video_ids": verified_ids,
            "is_clean_2_videos": (public_vids_count <= 2) and bool(latest_long and latest_short),
            "channel_views": ch_views,
            "channel_likes": ch_likes,
            "release_status": "LOCKED_RELEASE_READY",
            "long_video": latest_long,
            "short_video": latest_short,
            "week1_long_video": week1_long,
            "week1_short_video": week1_short,
            "videos": vids,
            "batches_breakdown": ch_batches_map,
            "funnel_pairs": funnel_pairs,
        }
        channels_list.append(channel_obj)

    elapsed_total = time.time() - t0
    funnel_compliance_pct = (
        round(funnel_linked_shorts / total_short_vids * 100, 1) if total_short_vids > 0 else 0.0
    )
    all_clean = all(c["videos_count"] >= 2 for c in channels_list) and (funnel_compliance_pct >= 100.0)

    # Totals structure
    totals = {
        "total_channels": len(channels_list),
        "total_videos": len(all_videos),
        "total_long_videos": total_long_vids,
        "total_short_videos": total_short_vids,
        "total_views": fleet_total_views,
        "long_views": long_views,
        "short_views": short_views,
        "total_likes": fleet_total_likes,
        "total_subscribers": fleet_total_subs,
        "avg_views_per_video": round(fleet_total_views / len(all_videos), 1) if all_videos else 0.0,
        "avg_views_per_channel": round(fleet_total_views / len(channels_list), 1) if channels_list else 0.0,
        "funnel_linked_shorts": funnel_linked_shorts,
        "funnel_total_shorts": total_short_vids,
        "funnel_compliance_pct": funnel_compliance_pct,
        "views_delta": 0,
        "likes_delta": 0,
        "subs_delta": 0,
        "all_channels_clean_2_videos": all_clean,
    }

    # Phase 7: History tracking & deltas
    history_list: List[Dict[str, Any]] = []
    if history_path:
        deltas, history_list = append_and_load_history(
            history_path, totals, batches_count=len(sorted_batches)
        )
        totals.update(deltas)

    dashboard_snapshot = {
        "schema_version": "3.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scrape_duration_seconds": round(elapsed_total, 2),
        "totals": totals,
        "batches": sorted_batches,
        "channels": channels_list,
        "all_videos": all_videos,
        "funnel_matrix": funnel_matrix,
        "history": history_list,
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(dashboard_snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Saved scalable snapshot (v3.0) to %s in %.2fs", output_path, elapsed_total)

    return dashboard_snapshot


def collect_dashboard_metrics(
    channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH,
    output_path: Optional[Path] = DEFAULT_METRICS_PATH,
    history_path: Optional[Path] = DEFAULT_HISTORY_PATH,
    incremental: bool = False,
    force_full: bool = False,
    auto_sync_map: bool = False,
    cache_ttl_seconds: float = 180.0,
    max_workers: int = 32,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Backward-compatible entry point for youtube_dashboard server."""
    return collect_scalable_dashboard_metrics(
        channel_map_path=channel_map_path,
        output_path=output_path,
        history_path=history_path,
        incremental=incremental,
        force_full=force_full,
        auto_sync_map=auto_sync_map,
        cache_ttl_seconds=cache_ttl_seconds,
        max_workers=max_workers,
    )


def main() -> None:
    """CLI runner for testing and manual snapshot refreshes."""
    parser = argparse.ArgumentParser(description="YouTube Fleet Catalog & Metrics Engine")
    parser.add_argument("--channel-map", type=Path, default=DEFAULT_CHANNEL_MAP_PATH, help="Path to channel map JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_METRICS_PATH, help="Path to output metrics JSON")
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY_PATH, help="Path to history JSONL")
    parser.add_argument("--force-full", action="store_true", help="Force full watch scrape bypassing cache")
    parser.add_argument("--incremental", action="store_true", default=True, help="Enable smart incremental caching")
    parser.add_argument("--sync", action="store_true", help="Auto-sync newly discovered videos to channel map")
    parser.add_argument("--workers", type=int, default=32, help="Max parallel scraping threads")
    parser.add_argument("--json", action="store_true", help="Output full JSON snapshot to stdout")

    args = parser.parse_args()
    snapshot = collect_scalable_dashboard_metrics(
        channel_map_path=args.channel_map,
        output_path=args.output,
        history_path=args.history,
        incremental=args.incremental,
        force_full=args.force_full,
        auto_sync_map=args.sync,
        max_workers=args.workers,
    )

    totals = snapshot["totals"]
    print(f"Scraped {totals['total_videos']} videos across {totals['total_channels']} channels in {snapshot['scrape_duration_seconds']}s")
    print(f"Total Views: {totals['total_views']} (Long: {totals['long_views']}, Short: {totals['short_views']}) | Likes: {totals['total_likes']} | Subs: {totals['total_subscribers']}")
    print(f"Batches: {len(snapshot['batches'])} | Funnel Compliance: {totals['funnel_compliance_pct']}% ({totals['funnel_linked_shorts']}/{totals['funnel_total_shorts']})")
    print(f"Deltas -> Views: +{totals['views_delta']} | Likes: +{totals['likes_delta']} | Subs: +{totals['subs_delta']}")

    if args.json:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
