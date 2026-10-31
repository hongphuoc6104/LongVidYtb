#!/usr/bin/env python3
"""Comprehensive Unit Tests for Video Pilot YouTube Fleet Dashboard (V3).

Tests:
1. extract_video_id, parse_numeric_count, format_duration utility functions.
2. Private & unlisted video detection logic.
3. Scalability with 160 videos across 20 batches and 8 channels (funnel matrix aggregation & HTML embedding).
4. Terminal ASCII table rendering with multi-batch breakdown.
5. Standalone HTML dashboard export.
6. Dashboard HTTP handler (CORS preflight, GET /, GET /api/metrics, GET /api/history, POST /api/refresh, POST /api/sync-map, POST /api/open-studio).
"""
from __future__ import annotations

import json
import threading
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

# Ensure sys directory is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"

from tools.dashboard_catalog_engine import (
    collect_scalable_dashboard_metrics,
    extract_video_id,
    format_duration,
    parse_numeric_count,
)
from tools.dashboard_ui_template import get_dashboard_html
from tools.youtube_dashboard import (
    DashboardHTTPHandler,
    export_standalone_html,
    render_ascii_table,
    scrape_video_metrics,
)


# ==============================================================================
# 1. Video ID, Numeric Count & Duration Utility Tests
# ==============================================================================
def test_extract_video_id():
    """Verify standard, shorts, youtu.be, and malformed URL ID extraction."""
    # Standard watch URL
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    # Shorts URL
    assert extract_video_id("https://youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    # Shortened youtu.be URL
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    # URL with parameters
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ?si=abcdef123456") == "dQw4w9WgXcQ"
    # Whitespace trimming
    assert extract_video_id("   https://youtu.be/dQw4w9WgXcQ   ") == "dQw4w9WgXcQ"
    # None, empty or non-YouTube
    assert extract_video_id("") == ""
    assert extract_video_id(None) == ""
    assert extract_video_id("https://example.com/not_youtube") == ""


def test_parse_numeric_count():
    """Verify integer parsing for various YouTube count formats."""
    # Plain numbers
    assert parse_numeric_count("150") == 150
    assert parse_numeric_count("1,450") == 1450
    assert parse_numeric_count("28,912") == 28912

    # Suffixes
    assert parse_numeric_count("1.2K") == 1200
    assert parse_numeric_count("3.5M") == 3500000
    assert parse_numeric_count("1.5B") == 1500000000

    # With contextual words
    assert parse_numeric_count("7 subscribers") == 7
    assert parse_numeric_count("992 views") == 992
    assert parse_numeric_count("1.2K views") == 1200
    assert parse_numeric_count("25 likes") == 25

    # Edge cases
    assert parse_numeric_count("") == 0
    assert parse_numeric_count(None) == 0
    assert parse_numeric_count("No views yet") == 0


def test_format_duration():
    """Verify duration formatting into mm:ss and hh:mm:ss."""
    # Zero and negative
    assert format_duration(0) == "00:00"
    assert format_duration(-10) == "00:00"

    # Seconds only
    assert format_duration(5) == "00:05"
    assert format_duration(59) == "00:59"

    # Minutes and seconds
    assert format_duration(65) == "01:05"
    assert format_duration(599) == "09:59"
    assert format_duration(600) == "10:00"

    # Hours, minutes and seconds
    assert format_duration(3600) == "1:00:00"
    assert format_duration(3665) == "1:01:05"
    assert format_duration(7325) == "2:02:05"


# ==============================================================================
# 2. Private & Unlisted Video Detection Tests
# ==============================================================================
def test_private_video_detection():
    """Verify playabilityStatus.status == LOGIN_REQUIRED sets is_public to False."""
    private_html = """
    <!DOCTYPE html>
    <html>
    <script>
    var ytInitialPlayerResponse = {
        "playabilityStatus": {
            "status": "LOGIN_REQUIRED",
            "reason": "This is a private video. Sign in if you have been granted access."
        },
        "videoDetails": {
            "videoId": "privTest123",
            "title": "Private Test Video",
            "isPrivate": true
        }
    };
    </script>
    </html>
    """

    with patch("tools.dashboard_catalog_engine.fetch_url", return_value=private_html):
        metrics = scrape_video_metrics("privTest123", is_short=False)
        assert metrics["video_id"] == "privTest123"
        assert metrics["is_public"] is False


def test_unlisted_video_detection():
    """Verify playerMicroformatRenderer.isUnlisted sets is_public to False."""
    unlisted_html = """
    <!DOCTYPE html>
    <html>
    <script>
    var ytInitialPlayerResponse = {
        "playabilityStatus": {
            "status": "OK"
        },
        "videoDetails": {
            "videoId": "unlistTest1",
            "title": "Unlisted Video",
            "viewCount": "120"
        },
        "microformat": {
            "playerMicroformatRenderer": {
                "isUnlisted": true,
                "publishDate": "2026-10-25"
            }
        }
    };
    </script>
    </html>
    """

    with patch("tools.dashboard_catalog_engine.fetch_url", return_value=unlisted_html):
        metrics = scrape_video_metrics("unlistTest1", is_short=True)
        assert metrics["video_id"] == "unlistTest1"
        assert metrics["is_public"] is False
        assert metrics["view_count"] == 120


def test_public_video_scrape():
    """Verify public video parsing parses title, views, likes, and length properly."""
    public_html = """
    <!DOCTYPE html>
    <html>
    <script>
    var ytInitialPlayerResponse = {
        "playabilityStatus": {
            "status": "OK"
        },
        "videoDetails": {
            "videoId": "pubTest1234",
            "title": "Public Explainer Video",
            "viewCount": "1250",
            "lengthSeconds": "185"
        },
        "microformat": {
            "playerMicroformatRenderer": {
                "likeCount": "95",
                "publishDate": "2026-10-30"
            }
        }
    };
    var ytInitialData = {};
    </script>
    </html>
    """

    with patch("tools.dashboard_catalog_engine.fetch_url", return_value=public_html):
        metrics = scrape_video_metrics("pubTest1234", is_short=False)
        assert metrics["video_id"] == "pubTest1234"
        assert metrics["is_public"] is True
        assert metrics["title"] == "Public Explainer Video"
        assert metrics["view_count"] == 1250
        assert metrics["like_count"] == 95
        assert metrics["length_seconds"] == 185


def test_scrape_channel_tabs_prioritizes_channel_id_and_rejects_foreign_external_id():
    """Verify scrape_channel_tabs_bulk prioritizes channel_id over handle and rejects foreign externalId."""
    from tools.dashboard_catalog_engine import scrape_channel_tabs_bulk, verify_channel_actual_video_count

    requested_urls: list[str] = []

    matching_tab_html = """
    <html><body>
    <script>
    var ytInitialData = {
        "metadata": {
            "channelMetadataRenderer": {
                "externalId": "UCEWZEZJTFpNCbURgtNLHA1A"
            }
        },
        "contents": {
            "twoColumnBrowseResultsRenderer": {
                "tabs": [
                    {
                        "tabRenderer": {
                            "selected": true,
                            "content": {
                                "richGridRenderer": {
                                    "contents": [
                                        {
                                            "richItemRenderer": {
                                                "content": {
                                                    "lockupViewModel": {
                                                        "rendererContext": {
                                                            "commandContext": {
                                                                "onTap": {
                                                                    "innertubeCommand": {
                                                                        "watchEndpoint": {
                                                                            "videoId": "gjx2Gv0GhS0"
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "metadata": {
                                                            "lockupMetadataViewModel": {
                                                                "title": {
                                                                    "content": "Valid Fleet Video"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
    };
    </script></body></html>
    """

    foreign_tab_html = """
    <html><body>
    <script>
    var ytInitialData = {
        "metadata": {
            "channelMetadataRenderer": {
                "externalId": "UCfdNYvMxrVsG_daZyXR7pqA"
            }
        },
        "contents": {
            "twoColumnBrowseResultsRenderer": {
                "tabs": [
                    {
                        "tabRenderer": {
                            "selected": true,
                            "content": {
                                "richGridRenderer": {
                                    "contents": [
                                        {
                                            "richItemRenderer": {
                                                "content": {
                                                    "lockupViewModel": {
                                                        "rendererContext": {
                                                            "commandContext": {
                                                                "onTap": {
                                                                    "innertubeCommand": {
                                                                        "watchEndpoint": {
                                                                            "videoId": "foreign12345"
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "metadata": {
                                                            "lockupMetadataViewModel": {
                                                                "title": {
                                                                    "content": "Foreign Video"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
    };
    </script></body></html>
    """

    def mock_fetch(url: str, timeout: float = 10.0) -> str:
        requested_urls.append(url)
        return matching_tab_html

    with patch("tools.dashboard_catalog_engine.fetch_url", side_effect=mock_fetch):
        # 1. When channel_id is provided, request canonical /channel/{channel_id}/videos and /shorts (not @handle)
        requested_urls.clear()
        res = scrape_channel_tabs_bulk(
            handle="@HoSoKyLaVN",
            channel_id="UCEWZEZJTFpNCbURgtNLHA1A",
        )
        assert len(requested_urls) == 2
        for url in requested_urls:
            assert "https://www.youtube.com/channel/UCEWZEZJTFpNCbURgtNLHA1A/" in url
            assert "@HoSoKyLaVN" not in url
        assert "gjx2Gv0GhS0" in res

        # 2. verify_channel_actual_video_count also prioritizes channel_id
        v_res = verify_channel_actual_video_count(
            handle="@HoSoKyLaVN",
            channel_id="UCEWZEZJTFpNCbURgtNLHA1A",
        )
        assert v_res["channel_id"] == "UCEWZEZJTFpNCbURgtNLHA1A"
        assert v_res["total_count"] == 1
        assert "gjx2Gv0GhS0" in v_res["video_ids"]

    # 3. When externalId does not match channel_id, reject and discard results
    def mock_fetch_foreign(url: str, timeout: float = 10.0) -> str:
        return foreign_tab_html

    with patch("tools.dashboard_catalog_engine.fetch_url", side_effect=mock_fetch_foreign):
        res_rejected = scrape_channel_tabs_bulk(
            handle="@HoSoKyLaVN",
            channel_id="UCEWZEZJTFpNCbURgtNLHA1A",
        )
        assert res_rejected == {}
        assert "foreign12345" not in res_rejected

    # 4. Fallback to handle only when channel_id is empty
    requested_urls.clear()
    with patch("tools.dashboard_catalog_engine.fetch_url", side_effect=mock_fetch):
        _ = scrape_channel_tabs_bulk(handle="@AIBinhDanVN", channel_id="")
        assert len(requested_urls) == 2
        for url in requested_urls:
            assert "https://www.youtube.com/@AIBinhDanVN/" in url


# ==============================================================================
# 3. Scalability with 160 Videos (20 Batches x 8 Channels)
# ==============================================================================
def test_scalability_160_videos_20_batches(tmp_path: Path):
    """Verify scalability engine aggregates 160 videos across 20 batches and 8 channels.

    Structure:
    - 8 channels: ch_01 to ch_08
    - 20 batches: batch1 to batch20
    - 8 videos per batch (4 longs + 4 shorts), linked 1:1 via related_video_url
    - Total: 20 batches * 8 = 160 videos, 80 longs, 80 shorts, 80 funnel pairs.
    """
    channel_keys = [f"ch_{i:02d}" for i in range(1, 9)]
    batch_ids = [f"batch{b}" for b in range(1, 21)]

    channels_data: Dict[str, Any] = {}
    for k in channel_keys:
        channels_data[k] = {
            "channel_id": k,
            "channel_name": f"Channel {k.upper()}",
            "handle": f"@{k}VN",
            "slug": k.replace("_", "-"),
            "youtube_channel_id": f"UC_{k}_id",
            "published_videos": [],
        }

    # Generate 160 videos (20 batches * 4 pairs = 80 pairs = 160 videos)
    # YouTube video IDs must be exactly 11 characters (e.g. LVid01P0001)
    expected_funnel_pairs = 80

    for b_idx, b_id in enumerate(batch_ids, start=1):
        # Distribute 4 pairs across the 8 channels in round-robin fashion
        for pair_idx in range(4):
            ch_k = channel_keys[(b_idx * 4 + pair_idx) % 8]
            long_vid = f"LVid{b_idx:02d}P{pair_idx:02d}01"
            short_vid = f"SVid{b_idx:02d}P{pair_idx:02d}01"

            long_url = f"https://youtu.be/{long_vid}"
            short_url = f"https://youtube.com/shorts/{short_vid}"

            # Long entry
            channels_data[ch_k]["published_videos"].append({
                "video_url": long_url,
                "title": f"Explainer Long {b_id} on {ch_k}",
                "format": "long_16x9",
                "batch": b_id,
                "related_video_url": None,
                "published_at": f"2026-10-{b_idx:02d}T10:00:00Z",
            })

            # Short entry linked to the long entry
            channels_data[ch_k]["published_videos"].append({
                "video_url": short_url,
                "title": f"Teaser Short {b_id} on {ch_k}",
                "format": "short_9x16",
                "batch": b_id,
                "related_video_url": long_url,
                "published_at": f"2026-10-{b_idx:02d}T10:05:00Z",
            })

    channel_map_file = tmp_path / "youtube_channel_map_160.json"
    metrics_file = tmp_path / "dashboard_metrics_160.json"
    history_file = tmp_path / "dashboard_history_160.jsonl"
    channel_map_file.write_text(
        json.dumps({"version": 1, "channels": channels_data}, indent=2),
        encoding="utf-8",
    )

    # Mock tab bulk scraper and resilient watch scrape so test runs purely in-memory
    def mock_scrape_channel_tabs_bulk(handle: str, channel_id: str = "", timeout: float = 10.0):
        return {}

    def mock_scrape_video_metrics_resilient(
        video_id: str,
        is_short: bool = False,
        bulk_tab_info=None,
        channel_map_entry=None,
        cached_metrics=None,
        timeout: float = 8.0,
        allow_watch_scrape: bool = True,
    ):
        return {
            "video_id": video_id,
            "video_url": f"https://youtube.com/shorts/{video_id}" if is_short else f"https://youtu.be/{video_id}",
            "title": f"Title for {video_id}",
            "view_count": 250 if is_short else 500,
            "like_count": 20 if is_short else 45,
            "comment_count_text": "5",
            "length_seconds": 45 if is_short else 300,
            "publish_date": "2026-10-31",
            "is_public": True,
            "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "scraped_at": "2026-10-31T14:00:00Z",
        }

    def mock_scrape_channel_metrics(channel_key: str, channel_id: str, handle: str, cached_channel=None, timeout=12.0):
        return {
            "channel_key": channel_key,
            "subscriber_count_text": "100 subscribers",
            "subscriber_count": 100,
            "videos_count_text": "20 videos",
            "videos_count": 20,
            "avatar_url": "",
            "description_snippet": "Test channel snippet",
            "header_badge_lag": False,
            "raw_videos_count_text": "20 videos",
            "verified_video_ids": [],
            "scraped_at": "2026-10-31T14:00:00Z",
        }

    with patch("tools.dashboard_catalog_engine.scrape_channel_tabs_bulk", side_effect=mock_scrape_channel_tabs_bulk), \
         patch("tools.dashboard_catalog_engine.scrape_video_metrics_resilient", side_effect=mock_scrape_video_metrics_resilient), \
         patch("tools.dashboard_catalog_engine.scrape_channel_metrics", side_effect=mock_scrape_channel_metrics):

        snapshot = collect_scalable_dashboard_metrics(
            channel_map_path=channel_map_file,
            output_path=metrics_file,
            history_path=history_file,
            incremental=False,
            force_full=True,
            max_workers=16,
        )

    # 1. Verify Video & Batch Totals
    totals = snapshot["totals"]
    assert totals["total_channels"] == 8
    assert totals["total_videos"] == 160
    assert totals["total_long_videos"] == 80
    assert totals["total_short_videos"] == 80
    assert len(snapshot["all_videos"]) == 160
    assert len(snapshot["batches"]) == 20
    assert len(snapshot["funnel_matrix"]) == expected_funnel_pairs

    # 2. Verify Funnel Compliance
    assert totals["funnel_linked_shorts"] == 80
    assert totals["funnel_total_shorts"] == 80
    assert totals["funnel_compliance_pct"] == 100.0

    # 3. Verify Batch Performance Rows
    for b in snapshot["batches"]:
        assert b["videos_count"] == 8
        assert b["long_count"] == 4
        assert b["short_count"] == 4
        assert b["views"] > 0
        assert b["likes"] > 0

    # 4. Verify ASCII Table Rendering
    ascii_table = render_ascii_table(snapshot)
    assert "YOUTUBE FLEET SCALABLE ANALYTICS & CATALOG DASHBOARD (V3)" in ascii_table
    assert "BATCH PERFORMANCE BREAKDOWN" in ascii_table
    for b_id in batch_ids:
        # Check formatted batch labels (e.g. "Batch 1" .. "Batch 20")
        b_num = b_id.replace("batch", "")
        assert f"Batch {b_num}" in ascii_table

    # 5. Verify Standalone HTML Generation & Embedding
    html_output = get_dashboard_html(embedded_data=snapshot)
    assert "<!DOCTYPE html>" in html_output
    assert 'id="__INITIAL_DATA__"' in html_output
    assert "window.__INITIAL_DASHBOARD_DATA__" in html_output
    # Check that all 20 batch names and sample video IDs are embedded in the HTML
    for b_id in batch_ids:
        assert b_id in html_output
    assert "LVid01P0001" in html_output
    assert "SVid20P0301" in html_output

    # 6. Verify export_standalone_html
    standalone_html_path = tmp_path / "standalone_dashboard_160.html"
    exported_path = export_standalone_html(snapshot, standalone_html_path)
    assert exported_path.exists()
    assert exported_path.stat().st_size > 50_000


# ==============================================================================
# 4. ASCII Table & HTML Standalone Export Unit Tests
# ==============================================================================
def test_render_ascii_table_minimal():
    """Verify render_ascii_table handles minimal or legacy snapshot shapes."""
    minimal_data = {
        "schema_version": "3.0",
        "generated_at": "2026-10-31T12:00:00Z",
        "scrape_duration_seconds": 1.25,
        "totals": {
            "total_channels": 1,
            "total_videos": 2,
            "total_views": 1500,
            "total_likes": 80,
            "total_subscribers": 15,
            "funnel_linked_shorts": 1,
            "funnel_total_shorts": 1,
            "funnel_compliance_pct": 100.0,
            "views_delta": 25,
        },
        "batches": [
            {
                "batch_id": "batch2",
                "batch_label": "Batch 2",
                "videos_count": 2,
                "long_count": 1,
                "short_count": 1,
                "views": 1500,
                "likes": 80,
                "avg_views": 750.0,
            }
        ],
        "channels": [
            {
                "channel_id": "ai_binh_dan",
                "channel_name": "AI Bình Dân",
                "handle": "@AIBinhDanVN",
                "subscriber_count": 15,
                "videos_count": 2,
                "channel_views": 1500,
                "channel_likes": 80,
                "videos": [
                    {
                        "video_id": "vidLong1",
                        "format": "long_16x9",
                        "batch": "batch2",
                        "view_count": 1000,
                        "like_count": 60,
                    },
                    {
                        "video_id": "vidShort1",
                        "format": "short_9x16",
                        "batch": "batch2",
                        "view_count": 500,
                        "like_count": 20,
                    },
                ],
                "funnel_pairs": [{"is_linked": True}],
            }
        ],
    }

    table_str = render_ascii_table(minimal_data)
    assert "@AIBinhDanVN" in table_str
    assert "Batch 2" in table_str
    assert "1,500 Views" in table_str
    assert "✓ 1/1 Linked" in table_str


def test_export_standalone_html_creates_directories(tmp_path: Path):
    """Verify export_standalone_html automatically creates nested directories."""
    nested_dir = tmp_path / "deep" / "nested" / "path"
    target_html = nested_dir / "exported_dashboard.html"
    sample_data = {"test_key": "test_value", "totals": {}}

    result_path = export_standalone_html(sample_data, target_html)
    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "test_key" in content
    assert "<!DOCTYPE html>" in content


# ==============================================================================
# 5. Dashboard HTTP Server & CORS Preflight Tests
# ==============================================================================
@pytest.fixture
def dashboard_server(tmp_path: Path):
    """Spin up an ephemeral ThreadingHTTPServer on an OS-assigned free port."""
    channel_map_file = tmp_path / "test_channel_map.json"
    metrics_file = tmp_path / "test_metrics.json"
    history_file = tmp_path / "test_history.jsonl"

    channel_map_file.write_text(json.dumps({"channels": {}}), encoding="utf-8")
    sample_metrics = {
        "schema_version": "3.0",
        "generated_at": "2026-10-31T14:00:00Z",
        "scrape_duration_seconds": 0.5,
        "totals": {
            "total_channels": 8,
            "total_videos": 16,
            "total_views": 10000,
            "total_likes": 500,
            "total_subscribers": 50,
        },
        "batches": [],
        "channels": [],
        "all_videos": [],
    }
    metrics_file.write_text(json.dumps(sample_metrics), encoding="utf-8")

    history_row = {"timestamp": "2026-10-31T14:00:00Z", "total_videos": 16, "total_views": 10000}
    history_file.write_text(json.dumps(history_row) + "\n", encoding="utf-8")

    DashboardHTTPHandler.channel_map_path = channel_map_file
    DashboardHTTPHandler.metrics_path = metrics_file
    DashboardHTTPHandler.history_path = history_file
    DashboardHTTPHandler.export_paths = [tmp_path / "auto_export.html"]

    server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardHTTPHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    server.shutdown()
    server.server_close()


def test_http_options_cors_preflight(dashboard_server):
    """Verify OPTIONS request returns 204 or 200 with permissive CORS headers."""
    req = urllib.request.Request(
        f"{dashboard_server}/api/refresh",
        headers={"Origin": "null"},
        method="OPTIONS",
    )
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status in (200, 204)
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"
        assert "POST" in resp.headers.get("Access-Control-Allow-Methods", "")


def test_http_get_index(dashboard_server):
    """Verify GET / serves HTML with CORS headers and embedded metrics."""
    req = urllib.request.Request(f"{dashboard_server}/", headers={"Origin": "null"})
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"
        body = resp.read().decode("utf-8")
        assert "<!DOCTYPE html>" in body
        assert "Video Pilot" in body


def test_http_get_api_metrics(dashboard_server):
    """Verify GET /api/metrics returns valid JSON snapshot with CORS header."""
    req = urllib.request.Request(f"{dashboard_server}/api/metrics")
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"
        data = json.loads(resp.read().decode("utf-8"))
        assert data["schema_version"] == "3.0"
        assert data["totals"]["total_views"] == 10000


def test_http_get_api_history(dashboard_server):
    """Verify GET /api/history returns trend entries list with CORS header."""
    req = urllib.request.Request(f"{dashboard_server}/api/history")
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        assert resp.status == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"
        history = json.loads(resp.read().decode("utf-8"))
        assert isinstance(history, list)
        assert len(history) == 1
        assert history[0]["total_views"] == 10000


def test_http_post_refresh(dashboard_server):
    """Verify POST /api/refresh triggers metrics collection and returns updated snapshot."""
    mock_snapshot = {
        "schema_version": "3.0",
        "generated_at": "2026-10-31T14:15:00Z",
        "scrape_duration_seconds": 0.8,
        "totals": {"total_views": 10500},
        "batches": [],
        "channels": [],
        "all_videos": [],
    }

    with patch("tools.youtube_dashboard.collect_dashboard_metrics", return_value=mock_snapshot):
        req = urllib.request.Request(
            f"{dashboard_server}/api/refresh",
            data=json.dumps({"force_full": True}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            assert resp.status == 200
            assert resp.headers.get("Access-Control-Allow-Origin") == "*"
            data = json.loads(resp.read().decode("utf-8"))
            assert data["totals"]["total_views"] == 10500


def test_http_post_sync_map(dashboard_server):
    """Verify POST /api/sync-map syncs map, refreshes metrics, and returns summary."""
    mock_snapshot = {
        "schema_version": "3.0",
        "totals": {"total_videos": 18},
    }

    with patch("tools.youtube_dashboard.sync_discovered_videos_to_channel_map", return_value=2), \
         patch("tools.youtube_dashboard.collect_dashboard_metrics", return_value=mock_snapshot):
        req = urllib.request.Request(
            f"{dashboard_server}/api/sync-map",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            assert resp.status == 200
            assert resp.headers.get("Access-Control-Allow-Origin") == "*"
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "ok"
            assert data["synced_count"] == 2
            assert data["metrics"]["totals"]["total_videos"] == 18


def test_http_post_open_studio(dashboard_server):
    """Verify POST /api/open-studio invokes launch_channel_chrome_studio."""
    with patch(
        "tools.youtube_dashboard.launch_channel_chrome_studio",
        return_value={"status": "ok", "message": "Launched", "port": 9234},
    ):
        req = urllib.request.Request(
            f"{dashboard_server}/api/open-studio",
            data=json.dumps({"channel_id": "ai_binh_dan"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "ok"
            assert data["port"] == 9234


# ==============================================================================
# 7. Metadata Enrichment & Dashboard V3 UI Upgrade Tests
# ==============================================================================
def test_channel_metadata_enrichment_from_registry(tmp_path: Path):
    """Verify channels are enriched with email, wave, niche, promise, persona, references, seed_topics, and hook_formulas."""
    channel_map_file = tmp_path / "test_channel_map.json"
    metrics_file = tmp_path / "test_metrics.json"

    channel_map_data = {
        "version": 1,
        "channels": {
            "nao_luoi": {
                "channel_name": "Não Lười",
                "handle": "@NaoLuoiVN",
                "email": "naoluoi.channel@example.com",
                "profile_id": "profile_10",
                "cdp_port": 9232,
                "youtube_channel_id": "UC_nao_luoi_id",
                "published_videos": [
                    {
                        "video_url": "https://youtu.be/nlTestLong01",
                        "title": "Long Test Nao Luoi",
                        "format": "long_16x9",
                        "batch": "week1",
                        "published_at": "2026-10-31T09:00:00Z",
                    }
                ],
            },
            "custom_unknown_channel": {
                "channel_name": "Unknown Channel",
                "handle": "@UnknownVN",
                "email": "unknown@example.com",
                "profile_id": "profile_99",
                "cdp_port": 9299,
                "youtube_channel_id": "UC_unknown_id",
                "wave": 3,
                "niche": "Tâm linh ứng dụng",
                "published_videos": [],
            },
        },
    }
    channel_map_file.write_text(json.dumps(channel_map_data, indent=2), encoding="utf-8")

    def mock_tabs(handle: str, channel_id: str = "", timeout: float = 10.0):
        return {}

    def mock_video_metrics(video_id: str, **kwargs):
        return {
            "video_id": video_id,
            "title": f"Title {video_id}",
            "view_count": 300,
            "like_count": 25,
            "length_seconds": 120,
            "is_public": True,
            "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "scraped_at": "2026-10-31T14:00:00Z",
        }

    def mock_channel_metrics(channel_key: str, channel_id: str, handle: str, cached_channel=None, **kwargs):
        return {
            "channel_key": channel_key,
            "subscriber_count": 50,
            "videos_count": 1,
        }

    with patch("tools.dashboard_catalog_engine.scrape_channel_tabs_bulk", side_effect=mock_tabs), \
         patch("tools.dashboard_catalog_engine.scrape_video_metrics_resilient", side_effect=mock_video_metrics), \
         patch("tools.dashboard_catalog_engine.scrape_channel_metrics", side_effect=mock_channel_metrics):

        snapshot = collect_scalable_dashboard_metrics(
            channel_map_path=channel_map_file,
            output_path=metrics_file,
            incremental=False,
            force_full=True,
            max_workers=4,
        )

    channels = {c["channel_id"]: c for c in snapshot["channels"]}

    # Verify nao_luoi enriched from sys/channels/registry.py
    nl = channels["nao_luoi"]
    assert nl["email"] == "naoluoi.channel@example.com"
    assert nl["profile_id"] == "profile_10"
    assert nl["cdp_port"] == 9232
    assert nl["wave"] == 1
    assert nl["language"] == "vi"
    assert "niche" in nl and len(nl["niche"]) > 0
    assert "promise" in nl and len(nl["promise"]) > 0
    assert "persona" in nl and len(nl["persona"]) > 0
    assert isinstance(nl["references"], list)
    assert len(nl["references"]) >= 2
    for r in nl["references"]:
        assert "name" in r
        assert "platform" in r
        assert "format" in r
        assert "learn" in r
    assert isinstance(nl["seed_topics"], list)
    assert len(nl["seed_topics"]) >= 5
    assert isinstance(nl["hook_formulas"], list)
    assert len(nl["hook_formulas"]) >= 1
    assert nl["visual_profile_id"] == "handdrawn_2d_explainer"
    assert nl["visual_archetype_id"] == "stickman_doodle"
    assert nl["visual_archetype_label"] == "1. Indie Doodle Stickman"
    assert isinstance(nl["visual_palette"], list)
    assert len(nl["visual_palette"]) > 0

    # Verify video enrichment
    vid = snapshot["all_videos"][0]
    assert vid["email"] == "naoluoi.channel@example.com"
    assert vid["profile_id"] == "profile_10"
    assert vid["cdp_port"] == 9232
    assert vid["wave"] == 1
    assert vid["language"] == "vi"

    # Verify custom_unknown_channel graceful fallback
    unk = channels["custom_unknown_channel"]
    assert unk["email"] == "unknown@example.com"
    assert unk["wave"] == 3
    assert unk["niche"] == "Tâm linh ứng dụng"
    assert unk["references"] == []
    assert unk["seed_topics"] == []
    assert unk["hook_formulas"] == []


def test_foreign_video_blacklist_and_stale_discovered_purged(tmp_path: Path):
    """Verify that foreign blacklisted videos and unverified discovered videos are purged."""
    channel_map_file = tmp_path / "test_channel_map_blacklist.json"
    metrics_file = tmp_path / "test_metrics_blacklist.json"

    # Includes one valid video, one blacklisted foreign video, and one stale discovered video
    channel_map_data = {
        "version": 1,
        "channels": {
            "ho_so_ky_la": {
                "channel_name": "Hồ Sơ Kỳ Lạ",
                "handle": "@HoSoKyLaVN",
                "email": "hosokyla@example.com",
                "profile_id": "profile_13",
                "cdp_port": 9235,
                "youtube_channel_id": "UCEWZEZJTFpNCbURgtNLHA1A",
                "published_videos": [
                    {
                        "video_url": "https://youtu.be/validVid1234",
                        "title": "Valid Video",
                        "format": "long_16x9",
                        "batch": "week1",
                        "published_at": "2026-10-31T09:00:00Z",
                    },
                    {
                        "video_url": "https://youtu.be/bB2kjiltY1I",  # Foreign blacklist ID
                        "title": "Foreign Video",
                        "format": "long_16x9",
                        "batch": "discovered",
                        "published_at": "2026-10-31T09:00:00Z",
                    },
                    {
                        "video_url": "https://youtu.be/staleDisc999",  # Stale discovered not in tab_vids
                        "title": "Stale Discovered",
                        "format": "short_9x16",
                        "batch": "discovered",
                        "published_at": "2026-10-31T09:00:00Z",
                    },
                ],
            }
        },
    }
    channel_map_file.write_text(json.dumps(channel_map_data, indent=2), encoding="utf-8")

    def mock_tabs(handle: str, channel_id: str = "", timeout: float = 10.0):
        # Only validVid1234 is in verified tab discovery
        return {
            "validVid1234": {"title": "Valid Video", "is_short": False}
        }

    with patch("tools.dashboard_catalog_engine.scrape_channel_tabs_bulk", side_effect=mock_tabs), \
         patch("tools.dashboard_catalog_engine.scrape_video_metrics_resilient", return_value={"title": "V", "view_count": 10, "is_public": True}), \
         patch("tools.dashboard_catalog_engine.scrape_channel_metrics", return_value={"subscriber_count": 10, "videos_count": 1}):

        snapshot = collect_scalable_dashboard_metrics(
            channel_map_path=channel_map_file,
            output_path=metrics_file,
            incremental=False,
            force_full=True,
            max_workers=2,
        )

    all_vids = [v["video_id"] for v in snapshot["all_videos"]]
    assert "validVid1234" in all_vids
    assert "bB2kjiltY1I" not in all_vids
    assert "staleDisc999" not in all_vids


def test_dashboard_ui_html_v3_elements():
    """Verify HTML template contains Wave filter, Tab 5, dynamic headers, account strip, and reference drawer."""
    mock_snapshot = {
        "schema_version": "3.0",
        "generated_at": "2026-10-31T15:00:00Z",
        "scrape_duration_seconds": 0.5,
        "totals": {
            "total_channels": 16,
            "total_videos": 32,
            "total_long_videos": 16,
            "total_short_videos": 16,
            "total_views": 50000,
            "long_views": 25000,
            "short_views": 25000,
            "total_likes": 3000,
            "total_subscribers": 1500,
            "avg_views_per_video": 1562.5,
            "avg_views_per_channel": 3125.0,
            "funnel_linked_shorts": 16,
            "funnel_total_shorts": 16,
            "funnel_compliance_pct": 100.0,
        },
        "batches": [
            {"batch_id": "week1", "batch_label": "Đợt 1 (Week 1)", "videos_count": 16, "views": 25000, "likes": 1500}
        ],
        "channels": [
            {
                "channel_id": "nao_luoi",
                "channel_name": "Não Lười",
                "handle": "@NaoLuoiVN",
                "youtube_channel_url": "https://www.youtube.com/channel/UC_nao_luoi",
                "studio_url": "https://studio.youtube.com/channel/UC_nao_luoi",
                "analytics_url": "https://studio.youtube.com/channel/UC_nao_luoi/analytics",
                "email": "naoluoi.channel@example.com",
                "profile_id": "profile_10",
                "cdp_port": 9232,
                "wave": 1,
                "niche": "Tâm lý học hành vi",
                "persona": "Người bạn đồng hành khoa học",
                "promise": "Hiểu bộ não để bớt lười",
                "channel_views": 15000,
                "channel_likes": 1200,
                "subscriber_count": 500,
                "references": [
                    {
                        "name": "Better Ideas",
                        "platform": "YouTube",
                        "format": "long",
                        "learn": "Pacing & storytelling",
                    }
                ],
                "seed_topics": ["Tại sao chúng ta trì hoãn?", "Hiệu ứng Zeigarnik"],
                "hook_formulas": ["Bạn không lười, bộ não bạn chỉ đang..."],
                "videos": [],
            }
        ],
        "all_videos": [],
        "funnel_matrix": [],
        "history": [],
    }

    html = get_dashboard_html(embedded_data=mock_snapshot)

    # 1. Navigation & Dynamic Headers
    assert "btn-tab-fleet" in html
    assert "btn-tab-catalog" in html
    assert "btn-tab-funnel" in html
    assert "btn-tab-ops" in html
    assert "btn-tab-refs" in html
    assert "1. Tổng Quan Hệ Thống Kênh" in html
    assert "5. Kho Kênh Mẫu, Email & Đề Tài Gợi Ý" in html

    # 2. Wave Filter Dropdown
    assert 'id="filter-wave"' in html
    assert "Wave 1 — 8 Kênh Gốc" in html
    assert "Wave 2 — 8 Kênh Mở Rộng" in html
    assert "Wave 3 — 4 Kênh Tâm Linh & Minh Triết" in html
    assert "Wave 4 — 19 Kênh Tiếng Anh Quốc Tế" in html

    # 2b. Language Filter Dropdown
    assert 'id="filter-lang"' in html
    assert "🌐 Tất cả ngôn ngữ" in html
    assert "🇻🇳 Tiếng Việt (VN)" in html
    assert "🇺🇸 Tiếng Anh Quốc Tế (EN)" in html

    # 2c. Visual Archetype Style Filter Dropdown
    assert 'id="filter-style"' in html
    assert "🎨 Tất cả 10 Hệ Mỹ Thuật" in html
    assert "1. Indie Doodle Stickman" in html
    assert "2. 2D Noir & Red-String Dossier" in html
    assert "3. Kawaii Mascots & Sticker-Pop" in html
    assert "10. Woodblock Print & Night Gouache" in html

    # 3. Tab 5 Pane Structure
    assert 'id="tab-refs"' in html
    assert 'id="references-table-body"' in html
    assert "Tài Khoản Google & CDP" in html
    assert "Kênh & Đợt (Wave)" in html
    assert "Định Vị, Persona & Lời Hứa" in html
    assert "Kênh Mẫu & Nguồn Tham Khảo" in html

    # 4. CSS Classes
    assert ".channel-account-strip" in html
    assert ".btn-copy-mini" in html
    assert ".badge-wave" in html
    assert ".badge-wave-1" in html
    assert ".badge-wave-2" in html
    assert ".badge-wave-3" in html
    assert ".badge-wave-4" in html
    assert ".badge-lang" in html
    assert ".new-channel-badge" in html
    assert ".channel-ref-drawer-wrap" in html
    assert ".btn-ref-toggle" in html
    assert ".style-badge-swatch-wrap" in html
    assert ".swatch-dot" in html

    # 5. JavaScript functions
    assert "function renderReferencesTab()" in html
    assert "function toggleReferencesExpand(" in html
    assert "getLangBadgeHtml" in html
    assert "getStyleBadgeAndSwatchesHtml" in html
    assert "state.waveFilter" in html
    assert "state.langFilter" in html
    assert "state.styleFilter" in html
