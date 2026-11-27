"""Unit tests for V12 Long-Form Deep Audit YouTube Studio CDP Fixes.

Covers:
1. `--no-notify-subscribers` (`YouTubeCDPClient.set_notify_subscribers(False)` & `expand_show_more_details()`).
2. Automated Playlist selection & creation (`ensure_and_select_playlist("Sử Kể Lại — Hồ Sơ Chiến Dịch & Bí Ẩn Đại Việt")`).
3. End Screen 2-element template attachment (`attach_endscreen_template()`).
4. Retroactive Short `Related Video` linker (`attach_related_video_existing_short()`).
5. In-place `/video/<VID>/edit` updater (`update_existing_video_studio_settings()`) and dead Private link cleaner (`clean_dead_links_from_description()`).
6. Turnkey batch operator `sys/scratch/studio_rescue_v12_ops.py` dry-run, Short-to-Long bridge resolution, and `--pin-due-comments` target detection.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.scratch.studio_rescue_v12_ops import (  # noqa: E402
    find_due_pinned_comment_targets,
    resolve_short_to_long_links,
    run_studio_rescue_v12_ops,
)
from sys.tools.publish_youtube_cdp import (  # noqa: E402
    DEAD_PRIVATE_VIDEO_IDS,
    DEFAULT_SU_KE_LAI_PLAYLIST,
    YouTubeCDPClient,
    clean_dead_links_from_description,
    is_short_related_video_disabled,
    publish_single_video,
)


def test_clean_dead_links_from_description_purges_private_v1_ids():
    """Verify clean_dead_links_from_description removes y5VeObQ7u1E, o_3FRlZ87wE, CbeJM6jT4ag while keeping valid links."""
    sample_desc = (
        "Quang Trung đại phá 29 vạn quân Thanh.\n\n"
        "🎬 Xem thêm các hồ sơ quân sự trên kênh Sử Kể Lại (@SuKeLaiVN):\n"
        "- Hành Quân Thần Tốc 1789: Bí Mật Ba Người Một Cáng — https://youtu.be/CbeJM6jT4ag\n"
        "- Tượng Binh & Hỏa Hổ Tây Sơn: Vũ Khí Nghiền Nát Kỵ Binh — https://youtube.com/shorts/0lSQgjgo-RA\n"
        "- Điện Biên Phủ — https://youtu.be/o_3FRlZ87wE\n"
        "- Trận Bạch Đằng 938: Giải Mã Bẫy Cọc Và Con Nước Tử Thần — https://youtu.be/y5VeObQ7u1E\n"
        "- Phòng Tuyến Như Nguyệt 1077: Chặn 10 Vạn Quân Tống — https://youtu.be/7ht-AqW1ZmU\n\n"
        "#SuKeLai #QuangTrung"
    )
    cleaned, removed = clean_dead_links_from_description(sample_desc, DEAD_PRIVATE_VIDEO_IDS)
    assert set(removed) == {"CbeJM6jT4ag", "o_3FRlZ87wE", "y5VeObQ7u1E"}
    for dead_id in DEAD_PRIVATE_VIDEO_IDS:
        assert dead_id not in cleaned
    assert "0lSQgjgo-RA" in cleaned
    assert "7ht-AqW1ZmU" in cleaned
    assert "#SuKeLai #QuangTrung" in cleaned


def test_set_notify_subscribers_unchecks_and_handles_locked_state():
    """Verify YouTubeCDPClient.set_notify_subscribers expands Show More and toggles checkbox state."""
    client = YouTubeCDPClient({"id": "profile_5", "port": 9226}, headless=True)
    calls: list[str] = []

    async def fake_eval(expr: str, await_promise: bool = True, timeout: float = 60.0):
        if "#toggle-button" in expr and "ALREADY_EXPANDED" in expr:
            calls.append("expand_show_more")
            return "TOGGLED"
        if "notify_subscribers_checkbox_not_found" in expr:
            calls.append("toggle_notify")
            if "const TARGET = false" in expr:
                return {
                    "applied": True,
                    "changed": True,
                    "previous": True,
                    "checked": False,
                    "target": False,
                    "locked": False,
                    "matched_by": "direct_id",
                }
            return {
                "applied": True,
                "changed": False,
                "previous": True,
                "checked": True,
                "target": True,
                "locked": False,
                "matched_by": "direct_id",
            }
        return None

    client.evaluate = AsyncMock(side_effect=fake_eval)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res_uncheck = asyncio.run(client.set_notify_subscribers(False))
        res_check = asyncio.run(client.set_notify_subscribers(True))

    assert "expand_show_more" in calls
    assert "toggle_notify" in calls
    assert res_uncheck["applied"] is True
    assert res_uncheck["changed"] is True
    assert res_uncheck["checked"] is False
    assert res_check["applied"] is True
    assert res_check["checked"] is True


def test_ensure_and_select_playlist_existing_and_create_new():
    """Verify ensure_and_select_playlist selects existing playlist or creates it when missing."""
    client = YouTubeCDPClient({"id": "profile_5", "port": 9226}, headless=True)

    # Case 1: Playlist already exists in ytcp-playlist-dialog
    async def fake_eval_existing(expr: str, await_promise: bool = True, timeout: float = 60.0):
        if "playlists_component_not_found" in expr:
            return {"opened": True, "already_selected": False, "trigger_text": "Chọn"}
        if "was_checked" in expr:
            return {"found": True, "was_checked": False, "matched_text": DEFAULT_SU_KE_LAI_PLAYLIST.lower()}
        if "ytcp-playlist-dialog" in expr and "Boolean(" in expr:
            return True
        return True

    client.evaluate = AsyncMock(side_effect=fake_eval_existing)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res1 = asyncio.run(client.ensure_and_select_playlist(DEFAULT_SU_KE_LAI_PLAYLIST))
    assert res1["applied"] is True
    assert res1["created"] is False
    assert res1["playlist_title"] == DEFAULT_SU_KE_LAI_PLAYLIST

    # Case 2: Playlist does not exist -> creates new playlist and selects it
    search_calls = {"n": 0}

    async def fake_eval_create(expr: str, await_promise: bool = True, timeout: float = 60.0):
        if "playlists_component_not_found" in expr:
            return {"opened": True, "already_selected": False, "trigger_text": "Chọn"}
        if "was_checked" in expr:
            search_calls["n"] += 1
            if search_calls["n"] == 1:
                return {"found": False, "item_count": 0}
            return {"found": True, "was_checked": True, "matched_text": DEFAULT_SU_KE_LAI_PLAYLIST.lower()}
        if "ytcp-playlist-dialog" in expr and "Boolean(" in expr:
            return True
        if "#new-playlist-button" in expr:
            return True
        if "no_create_dialog" in expr:
            return {"created": True}
        return True

    client.evaluate = AsyncMock(side_effect=fake_eval_create)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res2 = asyncio.run(client.ensure_and_select_playlist(DEFAULT_SU_KE_LAI_PLAYLIST))
    assert res2["applied"] is True
    assert res2["created"] is True
    assert search_calls["n"] == 2


def test_attach_endscreen_template_applies_two_element_template():
    """Verify attach_endscreen_template opens #endscreens-button, picks 2-element template, and clicks #save-button."""
    client = YouTubeCDPClient({"id": "profile_5", "port": 9226}, headless=True)
    client.call = AsyncMock(return_value={})
    client.dismiss_studio_interstitials = AsyncMock(return_value=False)

    async def fake_eval(expr: str, await_promise: bool = True, timeout: float = 60.0):
        if "window.location.href" in expr:
            return "https://studio.youtube.com/video/JdYxkBVpFuY/edit"
        if "#endscreens-button" in expr and "esRow" in expr:
            return True
        if "Boolean(" in expr and "ytve-endscreen-editor-modal" in expr:
            return True
        if "template_card" in expr:
            return {"method": "template_card", "label": "2 video: Phù hợp nhất với người xem + Tải lên gần đây nhất"}
        if "BEST_FOR_VIEWER" in expr:
            return True
        if "already_saved_or_unchanged" in expr:
            return {"clicked": True}
        if "still_open" in expr or "getBoundingClientRect" in expr:
            return False
        return None

    client.evaluate = AsyncMock(side_effect=fake_eval)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = asyncio.run(client.attach_endscreen_template("JdYxkBVpFuY"))

    assert res["applied"] is True
    assert res["saved"] is True
    assert res["template"]["method"] == "template_card"


def test_attach_related_video_existing_short_links_parent_long():
    """Verify attach_related_video_existing_short opens /video/<SHORT_VID>/edit, selects parent Long in ytcp-video-metadata-related-video, and saves."""
    client = YouTubeCDPClient({"id": "profile_5", "port": 9226}, headless=True)
    client.call = AsyncMock(return_value={})
    client.dismiss_studio_interstitials = AsyncMock(return_value=False)
    client.check_trust_tiers_dialog = AsyncMock(return_value={"detected": False})
    trigger_reads = {"n": 0}

    async def fake_eval(expr: str, await_promise: bool = True, timeout: float = 60.0):
        if "window.location.href" in expr:
            return "https://studio.youtube.com/channel/UCrLlAXwHQlxkDPFN3aW66PA"
        if "Boolean(" in expr and "ytcp-video-metadata-related-video" in expr:
            return True
        if ".dropdown-trigger-text" in expr:
            trigger_reads["n"] += 1
            if trigger_reads["n"] == 1:
                return "Không có"
            return "Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?"
        if "text_fallback" in expr and "ytcp-video-metadata-related-video" in expr:
            return {"clicked": True, "selector": "ytcp-video-metadata-related-video"}
        if "Boolean(" in expr and "ytcp-video-pick-dialog" in expr:
            return True
        if "matched_text" in expr and "ytcp-entity-card" in expr:
            return {"ok": True, "matched_text": "Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?"}
        if "ytcp-button#save" in expr and "clicked: true" in expr:
            return {"found": True, "clicked": True}
        if "ytcp-button#save" in expr and "aria-disabled" in expr:
            return True
        return None

    client.evaluate = AsyncMock(side_effect=fake_eval)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = asyncio.run(
            client.attach_related_video_existing_short(
                "t8rEbXya5P0",
                "JdYxkBVpFuY",
                target_title="Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?",
            )
        )

    assert res["success"] is True
    assert res["linked_via_cdp"] is True
    assert res["short_id"] == "t8rEbXya5P0"
    assert res["target_id"] == "JdYxkBVpFuY"
    assert res["saved"] is True
    assert "Đêm Lệ Chi Viên 1442" in res["selected_text"]

    # Case 2: Already linked to target title -> returns idempotent success without re-saving
    with patch("asyncio.sleep", new_callable=AsyncMock):
        res_idempotent = asyncio.run(
            client.attach_related_video_existing_short(
                "t8rEbXya5P0",
                "JdYxkBVpFuY",
                target_title="Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?",
            )
        )
    assert res_idempotent["success"] is True
    assert res_idempotent["already_linked"] is True
    assert res_idempotent["saved"] is False


def test_is_short_related_video_disabled_respects_overview_playbook():
    """Verify is_short_related_video_disabled returns False for su_ke_lai now that overview.md has short_attach_related_video: true."""
    assert is_short_related_video_disabled("su_ke_lai") is False


def test_update_existing_video_studio_settings_in_place(tmp_path: Path):
    """Verify update_existing_video_studio_settings updates title, description, notify_subscribers, playlist, endscreen, and saves."""
    client = YouTubeCDPClient({"id": "profile_5", "port": 9226}, headless=True)
    client.call = AsyncMock(return_value={})
    client.dismiss_studio_interstitials = AsyncMock(return_value=False)
    client.upload_thumbnail = AsyncMock(return_value=True)
    client.ensure_and_select_playlist = AsyncMock(
        return_value={"applied": True, "created": False, "playlist_title": DEFAULT_SU_KE_LAI_PLAYLIST}
    )
    client.expand_show_more_details = AsyncMock(return_value=True)
    client.set_notify_subscribers = AsyncMock(
        return_value={"applied": True, "changed": True, "checked": False}
    )
    client.set_altered_content_disclosure = AsyncMock(return_value={"applied": True, "value": "yes"})
    client._select_studio_dropdown_option = AsyncMock(return_value=True)
    client.attach_subtitles_post_publish = AsyncMock(return_value=True)
    client.attach_endscreen_template = AsyncMock(
        return_value={"applied": True, "saved": True}
    )
    client._click_editor_save_and_wait = AsyncMock(return_value=True)

    tags_injected = {"done": False}

    async def fake_eval(expr: str, await_promise: bool = True, timeout: float = 60.0):
        if "Boolean(el)" in expr:
            return True
        if "no_title_textbox" in expr:
            return {"updated": True, "title": "Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?"}
        if "no_description_textbox" in expr:
            return {"updated": True, "length": 420}
        if "#tags-container ytcp-chip" in expr:
            return 2 if tags_injected["done"] else 0
        if "insertText" in expr and "#tags-container" in expr:
            tags_injected["done"] = True
            return True
        if "#language-input" in expr:
            return "chọn"
        if "#category" in expr:
            return "giáo dục"
        return None

    client.evaluate = AsyncMock(side_effect=fake_eval)
    thumb = tmp_path / "thumb.png"
    thumb.write_bytes(b"PNG" * 100)
    srt = tmp_path / "captions.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nĐêm Lệ Chi Viên\n", encoding="utf-8")

    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = asyncio.run(
            client.update_existing_video_studio_settings(
                "JdYxkBVpFuY",
                notify_subscribers=False,
                title="Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?",
                description="Mô tả hợp lệ.\n- Link chết: https://youtu.be/CbeJM6jT4ag\n- Link sống: https://youtu.be/7ht-AqW1ZmU",
                clean_dead_links=DEAD_PRIVATE_VIDEO_IDS,
                thumbnail_path=thumb,
                playlist_name=DEFAULT_SU_KE_LAI_PLAYLIST,
                tags=["Lệ Chi Viên", "Nguyễn Trãi"],
                language="Tiếng Việt",
                category="Giáo dục",
                altered_content="yes",
                subtitles_path=srt,
                attach_endscreen=True,
            )
        )

    assert res["success"] is True
    assert res["saved"] is True
    assert res["changes"]["title"]["updated"] is True
    assert res["changes"]["description"]["removed_dead_ids"] == ["CbeJM6jT4ag"]
    assert res["changes"]["thumbnail_uploaded"] is True
    assert res["changes"]["playlist"]["applied"] is True
    assert res["changes"]["notify_subscribers"]["checked"] is False
    assert res["changes"]["tags_chip_count"] == 2
    assert res["changes"]["language_selected"] is True
    assert res["changes"]["altered_content"]["value"] == "yes"
    assert res["changes"]["subtitles_uploaded"] is True
    assert res["changes"]["endscreen"]["applied"] is True
    client.set_notify_subscribers.assert_awaited_once_with(False)
    client.ensure_and_select_playlist.assert_awaited_once_with(DEFAULT_SU_KE_LAI_PLAYLIST)
    client.set_altered_content_disclosure.assert_awaited_once_with("yes")
    client._select_studio_dropdown_option.assert_awaited_once()
    client.attach_subtitles_post_publish.assert_awaited_once_with("JdYxkBVpFuY", srt.resolve())
    client.attach_endscreen_template.assert_awaited_once()


def test_publish_single_video_wires_no_notify_playlist_and_endscreen(tmp_path: Path):
    """Verify publish_single_video wires no_notify_subscribers=True, playlist_name, and attach_endscreen=True."""
    dummy_mp4 = tmp_path / "long_v12.mp4"
    dummy_mp4.write_bytes(b"\x00" * 1024)

    with patch("sys.tools.publish_youtube_cdp.YouTubeCDPClient") as mock_client_cls, \
         patch("urllib.request.urlopen") as mock_urlopen, \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        mc = AsyncMock()
        mc.terminate_browser = MagicMock()
        mc.evaluate.return_value = "https://studio.youtube.com/channel/UCrLlAXwHQlxkDPFN3aW66PA"
        mc.get_channel_info.return_value = {
            "channelId": "UCrLlAXwHQlxkDPFN3aW66PA",
            "channelName": "Sử Kể Lại",
        }
        mc.ensure_and_select_playlist.return_value = {"applied": True, "playlist_title": DEFAULT_SU_KE_LAI_PLAYLIST}
        mc.set_notify_subscribers.return_value = {"applied": True, "checked": False}
        mc.attach_endscreen_template.return_value = {"applied": True, "saved": True}
        mc.publish_and_finish.return_value = "https://youtu.be/JdYxkBVpFuY"
        mock_client_cls.return_value = mc

        res = asyncio.run(
            publish_single_video(
                video_path=dummy_mp4,
                title="Đêm Lệ Chi Viên 1442: Ai Đứng Sau Án Tru Di?",
                description="00:00 Mở đầu",
                bypass_review_gate=True,
                is_short=False,
                no_notify_subscribers=True,
                playlist_name=DEFAULT_SU_KE_LAI_PLAYLIST,
                attach_endscreen=True,
            )
        )

    assert res["status"] == "PUBLISHED"
    assert res["notify_subscribers"] is False
    assert res["notify_subscribers_result"]["checked"] is False
    assert res["playlist_result"]["applied"] is True
    assert res["endscreen_result"]["applied"] is True
    mc.set_notify_subscribers.assert_awaited_once_with(False)
    mc.ensure_and_select_playlist.assert_awaited_once_with(DEFAULT_SU_KE_LAI_PLAYLIST)
    mc.attach_endscreen_template.assert_awaited_once()


def test_studio_rescue_v12_ops_dry_run_and_pin_due_comments(tmp_path: Path):
    """Verify studio_rescue_v12_ops dry-run validates Longs, Short->Long bridges, dead link purge, and due pinned comments."""
    summary = asyncio.run(
        run_studio_rescue_v12_ops(
            dry_run=True,
        )
    )
    assert summary["dry_run"] is True
    assert summary["playlist_name"] == DEFAULT_SU_KE_LAI_PLAYLIST
    assert len(summary["longs_processed"]) >= 6

    # L02 must be first in priority order and must uncheck notify_subscribers
    first_long = summary["longs_processed"][0]
    assert first_long["code"] == "L02"
    assert first_long["video_id"] == "JdYxkBVpFuY"
    assert first_long["will_uncheck_notify_subscribers"] is True
    assert first_long["will_assign_playlist"] is True
    assert first_long["will_attach_endscreen"] is True
    assert first_long["title_len"] <= 55

    # ln8E1Lsg_gI dead links must be identified for removal
    ln8_info = summary["ln8e1_dead_links_cleaned"]
    assert ln8_info["video_id"] == "ln8E1Lsg_gI"
    assert "CbeJM6jT4ag" in ln8_info["removed_dead_ids"]
    assert "y5VeObQ7u1E" in ln8_info["removed_dead_ids"]

    # Stale XoHxxT3KrwA -> PRIVATE and legacy dead-hour gGLHk-UsKak / wo4lyBAeqvI -> UNLISTED
    vis_map = {item["video_id"]: item["target_visibility"] for item in summary["visibility_switched"]}
    assert vis_map["XoHxxT3KrwA"] == "PRIVATE"
    assert vis_map["gGLHk-UsKak"] == "UNLISTED"
    assert vis_map["wo4lyBAeqvI"] == "UNLISTED"

    # Short -> Long bridges must resolve S01 -> L02 (JdYxkBVpFuY) and Wave Shorts (e.g. ep13 -> L05 BoSkNTNIOGc)
    short_links = resolve_short_to_long_links()
    by_code = {s["code"]: s for s in short_links}
    assert by_code["S01"]["parent_long_video_id"] == "JdYxkBVpFuY"
    assert by_code["S04"]["parent_long_video_id"] == "Zx3X-CfcA74"
    assert by_code["S07"]["parent_long_video_id"] == "BoSkNTNIOGc"
    assert by_code["S10"]["parent_long_video_id"] == "66kNPYHhXHs"
    assert by_code["ep13"]["parent_long_video_id"] == "BoSkNTNIOGc"
    assert by_code["ep16"]["parent_long_video_id"] == "JdYxkBVpFuY"

    # S01 (11:30 today) is already past due and unpinned -> must appear in find_due_pinned_comment_targets
    tz_vn = timezone(timedelta(hours=7))
    due = find_due_pinned_comment_targets(
        now_vn=datetime(2026, 11, 27, 12, 30, tzinfo=tz_vn),
        check_live_oembed=False,
    )
    due_codes = {d["code"] for d in due}
    assert "S01" in due_codes
