#!/usr/bin/env python3
"""Automated YouTube Channel Setup Tool via Chrome DevTools Protocol (CDP).

Sets up or customizes a YouTube channel:
1. Launches persistent signed-in Chrome profile.
2. Navigates to studio.youtube.com and handles initial channel creation if needed.
3. Customizes Channel Name, Handle, Description.
4. Uploads Avatar (avatar_800x800.png) & Banner (banner_2048x1152.png).
5. Publishes changes and extracts live Channel ID & Handle.
6. Updates sys/channels/youtube_channel_map.json and captures QA screenshot.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "sys") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "sys"))

from sys.tools.publish_youtube_cdp import YouTubeCDPClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("setup_youtube_channel_cdp")

MAP_PATH = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
QA_DIR = Path("/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/qa")


def load_channel_map() -> Dict[str, Any]:
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"Missing {MAP_PATH}")
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def save_channel_map(data: Dict[str, Any]) -> None:
    MAP_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Updated channel map saved to %s", MAP_PATH)


class YouTubeChannelSetupClient(YouTubeCDPClient):
    """CDP Client extension for YouTube channel creation and branding customization."""

    async def check_and_handle_creation_dialog(self, channel_name: str, handle_candidates: List[str]) -> bool:
        """Handle initial 'Create channel' modal if user has never created a channel."""
        logger.info("Checking for initial channel creation dialog...")
        is_dialog = await self.evaluate("""
            (() => {
                const dlg = document.querySelector('ytd-channel-creation-dialog-renderer') ||
                            document.querySelector('ytcp-channel-creation-dialog') ||
                            document.querySelector('#channel-creation-dialog');
                if (dlg && dlg.offsetParent !== null) return true;
                const text = document.body ? document.body.innerText : '';
                return text.includes('Tạo kênh') && (text.includes('Tên người dùng') || text.includes('Cách bạn sẽ xuất hiện'));
            })()
        """)

        if not is_dialog:
            logger.info("No channel creation dialog found. Channel already exists or studio loaded directly.")
            return False

        logger.info("Channel creation dialog detected! Filling initial channel details...")

        # 1. Fill Name
        await self.evaluate(f"""
            (() => {{
                const dlg = document.querySelector('ytd-channel-creation-dialog-renderer');
                const input = (dlg ? dlg.querySelectorAll('input')[0] : null) ||
                              document.querySelector('ytd-channel-creation-dialog-renderer input#name') ||
                              document.querySelector('ytcp-channel-creation-dialog input#name') ||
                              document.querySelector('input[placeholder*="tên"]') ||
                              document.querySelector('input[name="name"]');
                if (!input) return false;
                input.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(channel_name)});
                input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                return input.value;
            }})()
        """)
        await asyncio.sleep(1.0)

        # 2. Fill Handle
        for candidate in handle_candidates:
            clean_handle = candidate.lstrip("@")
            logger.info("Trying initial handle: %s", clean_handle)
            await self.evaluate(f"""
                (() => {{
                    const dlg = document.querySelector('ytd-channel-creation-dialog-renderer');
                    const input = (dlg ? dlg.querySelectorAll('input')[1] : null) ||
                                  document.querySelector('ytd-channel-creation-dialog-renderer input#handle') ||
                                  document.querySelector('ytcp-channel-creation-dialog input#handle') ||
                                  document.querySelector('input[placeholder*="người dùng"]') ||
                                  document.querySelector('input[name="handle"]');
                    if (!input) return false;
                    input.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, {json.dumps(clean_handle)});
                    input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                    return input.value;
                }})()
            """)
            await asyncio.sleep(2.0)

            has_error = await self.evaluate("""
                (() => {
                    const err = document.querySelector('ytd-channel-creation-dialog-renderer .error-message') ||
                                document.querySelector('.error-message');
                    return Boolean(err && err.innerText.trim());
                })()
            """)
            if not has_error:
                logger.info("Initial handle accepted: %s", clean_handle)
                break

        # 3. Click Create Channel button
        logger.info("Clicking 'Create Channel / Tạo kênh' button...")
        clicked = await self.evaluate("""
            (() => {
                const dlg = document.querySelector('ytd-channel-creation-dialog-renderer');
                const btn = (dlg ? Array.from(dlg.querySelectorAll('button')).find(b => b.innerText.includes('Tạo kênh') || b.innerText.includes('Create channel')) : null) ||
                            document.querySelector('#create-channel-button') ||
                            Array.from(document.querySelectorAll('ytcp-button, ytd-button-renderer, button')).find(
                                b => b.innerText.includes('Tạo kênh') || b.innerText.includes('Create channel')
                            );
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        logger.info("Create channel button clicked: %s. Waiting 10s for channel initialization...", clicked)
        await asyncio.sleep(10.0)
        return True

    async def switch_customization_tab(self, tab_labels: str | List[str]) -> bool:
        """Switch between 'Xây dựng thương hiệu' (Branding), 'Thông tin cơ bản' (Basic info), or 'Hồ sơ' (Profile)."""
        labels = [tab_labels] if isinstance(tab_labels, str) else list(tab_labels)
        logger.info("Switching customization tab to one of: %s", labels)
        switched = await self.evaluate(f"""
            (() => {{
                const candidates = {json.dumps([lbl.lower() for lbl in labels])};
                const tabs = Array.from(document.querySelectorAll('tp-yt-paper-tab, .paper-tab, ytcp-tab, [role="tab"]'));
                for (const kw of candidates) {{
                    const target = tabs.find(t => t.innerText && t.innerText.toLowerCase().includes(kw));
                    if (target) {{
                        target.click();
                        return target.innerText.trim();
                    }}
                }}
                return false;
            }})()
        """)
        await asyncio.sleep(2.5)
        return bool(switched)

    async def set_channel_name(self, channel_name: str) -> Optional[str]:
        """Update Channel Name field."""
        logger.info("Setting Channel Name to: %s", channel_name)
        res = await self.evaluate(f"""
            (() => {{
                const input = document.querySelector('input.ytcpChannelEditingChannelNameFormInput') ||
                              document.querySelector('ytcp-channel-editing-channel-name input') ||
                              document.querySelector('input[placeholder*="tên kênh" i]') ||
                              document.querySelector('input[placeholder*="channel name" i]');
                if (!input) return null;
                if (input.value && input.value.trim() === {json.dumps(channel_name)}) {{
                    return input.value.trim();
                }}
                input.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(channel_name)});
                input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                return input.value;
            }})()
        """)
        logger.info("Channel Name set result: %s", res)
        return res

    async def set_handle(self, handle_candidates: List[str]) -> Optional[str]:
        """Try handle candidates in order until accepted."""
        cur_handle = await self.evaluate("""
            (() => {
                const input = document.querySelector('input.YtcpChannelEditingChannelHandleHandleInput') ||
                              document.querySelector('ytcp-channel-editing-channel-handle input') ||
                              document.querySelector('input[placeholder*="tên người dùng" i]') ||
                              document.querySelector('input[placeholder*="handle" i]');
                return input ? (input.value || '').trim().replace(/^@/, '') : '';
            })()
        """)
        if cur_handle:
            for candidate in handle_candidates:
                if cur_handle.lower() == candidate.lstrip("@").lower():
                    logger.info("Channel handle already matches target candidate: @%s", cur_handle)
                    return f"@{cur_handle}"

        for candidate in handle_candidates:
            clean_handle = candidate.lstrip("@")
            logger.info("Testing handle candidate: %s", clean_handle)
            await self.evaluate(f"""
                (() => {{
                    const input = document.querySelector('input.YtcpChannelEditingChannelHandleHandleInput') ||
                                  document.querySelector('ytcp-channel-editing-channel-handle input') ||
                                  document.querySelector('input[placeholder*="tên người dùng" i]') ||
                                  document.querySelector('input[placeholder*="handle" i]');
                    if (!input) return false;
                    input.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, {json.dumps(clean_handle)});
                    input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                    return input.value;
                }})()
            """)
            await asyncio.sleep(2.5)

            has_error = await self.evaluate("""
                (() => {
                    const err = document.querySelector('ytcp-form-input-container[invalid]') ||
                                document.querySelector('.error-message') ||
                                document.querySelector('ytcp-form-error-message');
                    return Boolean(err && err.innerText.trim());
                })()
            """)
            if not has_error:
                accepted_handle = f"@{clean_handle}"
                logger.info("Handle accepted: %s", accepted_handle)
                return accepted_handle
            logger.warning("Handle @%s is unavailable or invalid, trying next...", clean_handle)

        return f"@{cur_handle}" if cur_handle else None

    async def set_description(self, description: str) -> Optional[str]:
        """Update Channel Description textbox."""
        logger.info("Setting Channel Description (%d chars)...", len(description))
        res = await self.evaluate(f"""
            (() => {{
                const box = document.querySelector('ytcp-social-suggestions-textbox #textbox') ||
                            document.querySelector('#textbox[contenteditable="true"]');
                if (!box) return null;
                box.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(description)});
                box.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                box.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                box.blur();
                window.scrollTo(0, 0);
                return box.innerText ? box.innerText.substring(0, 80) : '';
            }})()
        """)
        logger.info("Description set preview: %s...", res)
        return res

    async def upload_avatar(self, avatar_path: str | Path) -> bool:
        """Upload Avatar and confirm crop modal."""
        path = str(Path(avatar_path).resolve())
        logger.info("Attaching Avatar image: %s", path)
        avatar_input_obj = await self.get_remote_object("""
            (() => {
                const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                return inputs.find(i => i.closest && i.closest('ytcp-profile-image-upload')) || inputs[1];
            })()
        """)
        obj_id = avatar_input_obj.get("objectId")
        if not obj_id:
            logger.warning("Could not find Avatar file input element")
            return False

        try:
            await self.call("DOM.setFileInputFiles", {
                "files": [path],
                "objectId": obj_id
            })
            logger.info("Avatar attached. Waiting for crop modal...")
            await asyncio.sleep(3.5)

            # Confirm Done / Xong button in crop dialog
            confirmed = await self.evaluate("""
                (() => {
                    const btn = document.querySelector('#done-button') ||
                                Array.from(document.querySelectorAll('ytcp-button, button')).find(
                                    b => b.innerText.trim() === 'Xong' || b.innerText.trim() === 'Done'
                                );
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                })()
            """)
            logger.info("Avatar crop confirmed: %s", confirmed)
            await asyncio.sleep(2.0)
            return bool(confirmed)
        except Exception as e:
            logger.warning("Avatar upload exception: %s", e)
            return False

    async def upload_banner(self, banner_path: str | Path) -> bool:
        """Upload Banner and confirm crop modal."""
        path = str(Path(banner_path).resolve())
        logger.info("Attaching Banner image: %s", path)
        banner_input_obj = await self.get_remote_object("""
            (() => {
                const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                return inputs.find(i => i.closest && (i.closest('.ytcpBannerUploadInstructions') || i.closest('ytcp-banner-image-upload'))) || inputs[0];
            })()
        """)
        obj_id = banner_input_obj.get("objectId")
        if not obj_id:
            logger.warning("Could not find Banner file input element")
            return False

        try:
            await self.call("DOM.setFileInputFiles", {
                "files": [path],
                "objectId": obj_id
            })
            logger.info("Banner attached. Waiting for crop modal...")
            await asyncio.sleep(3.5)

            confirmed = await self.evaluate("""
                (() => {
                    const btn = document.querySelector('#done-button') ||
                                Array.from(document.querySelectorAll('ytcp-button, button')).find(
                                    b => b.innerText.trim() === 'Xong' || b.innerText.trim() === 'Done'
                                );
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                })()
            """)
            logger.info("Banner crop confirmed: %s", confirmed)
            await asyncio.sleep(2.0)
            return bool(confirmed)
        except Exception as e:
            logger.warning("Banner upload exception: %s", e)
            return False

    async def publish_customization(self) -> bool:
        """Click Publish button to persist changes."""
        logger.info("Clicking Publish / Xuất bản button...")
        pub_info = await self.evaluate("""
            (() => {
                const btn = document.querySelector('#publish-button') ||
                            Array.from(document.querySelectorAll('ytcp-button, button')).find(
                                b => b.innerText.includes('Xuất bản') || b.innerText.includes('Publish')
                            );
                if (!btn) return { found: false };
                const disabled = btn.getAttribute('aria-disabled') === 'true' || btn.hasAttribute('disabled');
                if (!disabled) {
                    btn.click();
                    return { found: true, clicked: true, text: btn.innerText.trim() };
                }
                return { found: true, clicked: false, text: btn.innerText.trim(), disabled: true };
            })()
        """)
        logger.info("Publish action: %s", pub_info)
        await asyncio.sleep(8.0)
        return bool(pub_info.get("clicked"))


async def setup_youtube_channel(
    channel_id: str,
    profile_id: Optional[str] = None,
    headless: bool = False,
) -> Dict[str, Any]:
    """Execute end-to-end YouTube Channel Setup."""
    ch_map_data = load_channel_map()
    if channel_id not in ch_map_data["channels"]:
        raise ValueError(f"Channel '{channel_id}' not found in youtube_channel_map.json")

    ch_entry = ch_map_data["channels"][channel_id]
    slug = ch_entry["slug"]

    # Profile config
    profile_cfg = {
        "id": ch_entry["profile_id"] if not profile_id else profile_id,
        "port": ch_entry["cdp_port"],
        "directory": ch_entry["directory"],
        "user_data_dir": ch_entry["user_data_dir"],
        "email": ch_entry["email"],
    }

    # Spec data
    spec_path = REPO_ROOT / "sys" / "channels" / channel_id / "assets" / "channel_setup_spec.json"
    if not spec_path.exists():
        raise FileNotFoundError(f"Missing spec file: {spec_path}. Run generate_channel_branding.py first!")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    logger.info("Starting YouTube Channel Setup for '%s' (%s) on Profile %s (port %d)...",
                spec["youtube_name"], channel_id, profile_cfg["id"], profile_cfg["port"])

    client = YouTubeChannelSetupClient(profile_cfg, headless=headless)
    await client.connect()

    try:
        # Step 1: Wait for initial studio navigation and check creation dialog
        await asyncio.sleep(5.0)
        cur_url = await client.evaluate("window.location.href")
        if "studio.youtube.com" not in (cur_url or ""):
            logger.info("Redirected away from Studio (%s), navigating to create_channel...", cur_url)
            await client.call("Page.navigate", {"url": "https://www.youtube.com/create_channel"})
            await asyncio.sleep(5.0)
            await client.check_and_handle_creation_dialog(spec["youtube_name"], spec["handle_candidates"])
        else:
            await client.check_and_handle_creation_dialog(spec["youtube_name"], spec["handle_candidates"])

        # Step 2: Extract current channel ID
        info = await client.get_channel_info()
        logger.info("Initial Studio state: %s", info)
        cur_url = await client.evaluate("window.location.href")
        m = re.search(r"/channel/(UC[a-zA-Z0-9_-]+)", cur_url or "")
        cid_found = m.group(1) if m else (info.get("channelId") or ch_entry.get("youtube_channel_id"))

        # Step 3: Navigate to Customization page
        if cid_found:
            custom_url = f"https://studio.youtube.com/channel/{cid_found}/editing"
        else:
            custom_url = "https://studio.youtube.com/channel/editing"

        logger.info("Navigating to Channel Customization: %s", custom_url)
        await client.call("Page.navigate", {"url": custom_url})
        await asyncio.sleep(7.0)

        # Also click Customization sidebar item if still not on /editing
        cur_url = await client.evaluate("window.location.href")
        if "/editing" not in (cur_url or ""):
            await client.evaluate("""
                (() => {
                    const link = document.querySelector('a[href*="/editing"]') ||
                                 Array.from(document.querySelectorAll('a, tp-yt-paper-icon-item')).find(
                                     el => el.innerText && (
                                         el.innerText.toLowerCase().includes('customization') ||
                                         el.innerText.toLowerCase().includes('tùy chỉnh')
                                     )
                                 );
                    if (link) link.click();
                })()
            """)
            await asyncio.sleep(5.0)
            cur_url = await client.evaluate("window.location.href")

        # Refresh channel ID from current location if not previously captured
        m = re.search(r"/channel/(UC[a-zA-Z0-9_-]+)", cur_url or "")
        if m:
            cid_found = m.group(1)

        # Step 4: Basic Info Tab (Name, Handle, Description)
        # Try switching to 'Thông tin cơ bản' / 'Basic info' / 'Profile' tab
        await client.switch_customization_tab(["Thông tin cơ bản", "Basic info", "Hồ sơ", "Profile"])
        await client.set_channel_name(spec["youtube_name"])
        accepted_handle = await client.set_handle(spec["handle_candidates"])
        await client.set_description(spec["description"])

        # Step 5: Branding Tab (Avatar, Banner)
        await client.switch_customization_tab(["Xây dựng thương hiệu", "Branding", "Hồ sơ", "Profile"])
        avatar_uploaded = await client.upload_avatar(spec["assets"]["avatar_800x800"])
        banner_uploaded = await client.upload_banner(spec["assets"]["banner_2048x1152"])

        # Step 6: Publish changes
        pub_success = await client.publish_customization()

        # Step 7: QA Screenshot
        QA_DIR.mkdir(parents=True, exist_ok=True)
        shot_path = QA_DIR / f"channel_setup_{slug}.png"
        await client.capture_screenshot(shot_path)
        logger.info("QA screenshot captured at: %s", shot_path)

        # Step 8: Update channel map under flock
        import fcntl
        lock_path = MAP_PATH.with_suffix(".lock")
        channel_url = f"https://www.youtube.com/channel/{cid_found}" if cid_found else None
        with open(lock_path, "w", encoding="utf-8") as lock_fh:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
            try:
                latest_map = load_channel_map()
                cur_entry = latest_map["channels"].get(channel_id, ch_entry)
                cur_entry["channel_name"] = spec["youtube_name"]
                if cid_found:
                    cur_entry["youtube_channel_id"] = cid_found
                    cur_entry["youtube_channel_url"] = channel_url
                if accepted_handle:
                    cur_entry["handle"] = accepted_handle
                latest_map["channels"][channel_id] = cur_entry
                save_channel_map(latest_map)
            finally:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)

        report = {
            "status": "SETUP_COMPLETED",
            "channel_id": channel_id,
            "slug": slug,
            "youtube_name": spec["youtube_name"],
            "youtube_channel_id": cid_found,
            "youtube_channel_url": channel_url,
            "handle": accepted_handle,
            "avatar_uploaded": avatar_uploaded,
            "banner_uploaded": banner_uploaded,
            "published": pub_success,
            "screenshot": str(shot_path),
        }
        logger.info("Channel Setup Summary:\n%s", json.dumps(report, indent=2, ensure_ascii=False))
        return report

    finally:
        await client.close()
        client.terminate_browser()


def main():
    parser = argparse.ArgumentParser(description="Automated YouTube Channel Setup via CDP")
    parser.add_argument("--channel", required=True, help="Channel ID (e.g., co_the_ke, ai_binh_dan)")
    parser.add_argument("--profile", help="Override Chrome profile ID")
    parser.add_argument("--headless", action="store_true", help="Run Chrome headless")

    args = parser.parse_args()
    report = asyncio.run(setup_youtube_channel(channel_id=args.channel, profile_id=args.profile, headless=args.headless))
    print("\n=== FINAL SETUP REPORT ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
