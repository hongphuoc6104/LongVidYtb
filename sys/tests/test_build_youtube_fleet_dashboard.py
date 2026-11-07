"""Unit tests for sys/tools/build_youtube_fleet_dashboard.py."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for p in (str(REPO_ROOT), str(SYS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from tools.build_youtube_fleet_dashboard import (
    main,
    render_dashboard_html,
    scan_batch1_fleet,
)


def test_scan_batch1_fleet_returns_18_channels():
    channels = scan_batch1_fleet()
    assert len(channels) == 18
    slugs = [c["slug"] for c in channels]
    assert "en-bamboo-marble" in slugs
    assert "en-lazy-brain" in slugs
    assert "en-crowd-strings" in slugs


def test_render_dashboard_html_contains_required_kpis_and_filters():
    channels = scan_batch1_fleet()
    html_out = render_dashboard_html(channels)

    # 4 KPIs
    assert "Tổng Kênh Fleet" in html_out
    assert "Short 9:16" in html_out
    assert "Long 16:9" in html_out
    assert "Tiến Độ Render Trực Tiếp (Flow+Veo)" in html_out

    # Filter tabs
    assert 'data-filter="all"' in html_out
    assert 'data-filter="published"' in html_out
    assert 'data-filter="rendering"' in html_out
    assert 'data-filter="awaiting_login"' in html_out

    # Search & Table
    assert 'id="searchInput"' in html_out
    assert 'id="fleetTable"' in html_out
    assert 'class="fleet-table"' in html_out
    assert len(channels) == 18


def test_cli_main_generates_files(tmp_path):
    custom_out = tmp_path / "custom_dashboard.html"
    sys.argv = ["build_youtube_fleet_dashboard.py", "--output", str(custom_out)]
    code = main()
    assert code == 0
    assert custom_out.exists()
    assert custom_out.stat().st_size > 10000
