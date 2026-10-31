#!/usr/bin/env python3
"""Channel Customization & Branding Tool for Video Pilot (sys/tools/setup_channel_branding.py).

Configures Channel Name, Handle, Description, Avatar, and Banner in YouTube Studio
via Chrome DevTools Protocol (CDP).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sys.tools.publish_youtube_cdp import YouTubeCDPClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("setup_channel_branding")


async def switch_customization_tab(client: YouTubeCDPClient, keyword: str) -> bool:
    """Switch between Layout, Branding, and Basic info tabs in Customization."""
    res = await client.evaluate(f"""
        (() => {{
            const tabs = Array.from(document.querySelectorAll('tp-yt-paper-tab, [role="tab"], .tab-header'));
            const target = tabs.find(t => t.innerText && t.innerText.toLowerCase().includes({json.dumps(keyword.lower())}));
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }})()
    """)
    await asyncio.sleep(2.5)
    return bool(res)


async def setup_channel_branding(
    channel_name: str,
    handle_candidates: list[str],
    description: str,
    avatar_path: str | Path,
    banner_path: str | Path,
    profile_cfg: dict,
    screenshot_path: str | Path,
) -> dict:
    client = YouTubeCDPClient(profile_cfg, headless=False)
    await client.connect()

    try:
        # Get channel ID or navigate to editing
        await asyncio.sleep(4.0)
        channel_info = await client.get_channel_info()
        cid = channel_info.get("channelId")
        if not cid:
            await client.call("Page.navigate", {"url": "https://studio.youtube.com"})
            await asyncio.sleep(4.0)
            channel_info = await client.get_channel_info()
            cid = channel_info.get("channelId")

        editing_url = f"https://studio.youtube.com/channel/{cid}/editing"
        logger.info("Navigating to Customization editing page: %s", editing_url)
        await client.call("Page.navigate", {"url": editing_url})
        await asyncio.sleep(6.0)

        # Switch to Basic Info tab ("Thông tin cơ bản")
        logger.info("Switching to 'Thông tin cơ bản' (Basic Info) tab...")
        await switch_customization_tab(client, "cơ bản")

        # 1. Update Channel Name
        logger.info("Setting Channel Name to: %s", channel_name)
        await client.evaluate(f"""
            (() => {{
                const input = document.querySelector('input.ytcpChannelEditingChannelNameFormInput') ||
                              document.querySelector('input[placeholder*="tên kênh"]');
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

        # 2. Update Handle (using native input typing pipeline)
        accepted_handle = None
        for candidate in handle_candidates:
            clean = candidate.lstrip("@")
            logger.info("Attempting handle: %s", clean)
            await client.evaluate("""
                (() => {
                    const input = document.querySelector('input.YtcpChannelEditingChannelHandleHandleInput') ||
                                  document.querySelector('input[placeholder*="tên người dùng"]');
                    if (input) {
                        input.focus();
                        input.select();
                        document.execCommand('selectAll', false, null);
                        document.execCommand('delete', false, null);
                    }
                })()
            """)
            await asyncio.sleep(0.5)
            await client.call("Input.insertText", {"text": clean})
            await asyncio.sleep(2.0)
            await client.evaluate("""
                (() => {
                    const input = document.querySelector('input.YtcpChannelEditingChannelHandleHandleInput');
                    if (input) {
                        input.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                    }
                })()
            """)
            await asyncio.sleep(2.0)

            # Check if error message appeared
            has_error = await client.evaluate("""
                (() => {
                    const err = document.querySelector('ytcp-form-error-message') ||
                                document.querySelector('.error-message');
                    return Boolean(err && err.innerText.trim());
                })()
            """)
            if not has_error:
                accepted_handle = clean
                logger.info("Handle @%s accepted without error!", clean)
                break
            logger.warning("Handle @%s is unavailable or invalid, trying next...", clean)

        # 3. Update Description
        logger.info("Setting Channel Description (%d chars)...", len(description))
        await client.evaluate(f"""
            (() => {{
                const box = document.querySelector('ytcp-social-suggestions-textbox #textbox') ||
                            document.querySelector('#textbox[contenteditable="true"]');
                if (!box) return false;
                box.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(description)});
                box.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                box.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                return true;
            }})()
        """)
        await asyncio.sleep(1.0)

        # Switch to Branding tab ("Xây dựng thương hiệu")
        logger.info("Switching to 'Xây dựng thương hiệu' (Branding) tab...")
        await switch_customization_tab(client, "thương hiệu")

        # 4. Upload Avatar
        av_str = str(Path(avatar_path).resolve())
        if os.path.isfile(av_str):
            logger.info("Uploading Avatar: %s", av_str)
            avatar_obj = await client.get_remote_object("""
                (() => {
                    const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                    return inputs.find(i => i.closest && i.closest('ytcp-profile-image-upload')) || inputs[1];
                })()
            """)
            a_obj_id = avatar_obj.get("objectId")
            if a_obj_id:
                try:
                    await client.call("DOM.setFileInputFiles", {
                        "files": [av_str],
                        "objectId": a_obj_id,
                    })
                    logger.info("Avatar set. Waiting for crop dialog...")
                    await asyncio.sleep(3.0)
                    await client.evaluate("""
                        (() => {
                            const btn = document.querySelector('#done-button') ||
                                        Array.from(document.querySelectorAll('ytcp-button, button')).find(b => b.innerText === 'Xong' || b.innerText === 'Done');
                            if (btn) btn.click();
                        })()
                    """)
                    logger.info("Avatar crop confirmed.")
                    await asyncio.sleep(2.0)
                except Exception as e:
                    logger.warning("Avatar upload exception: %s", e)

        # 5. Upload Banner
        ban_str = str(Path(banner_path).resolve())
        if os.path.isfile(ban_str):
            logger.info("Uploading Banner: %s", ban_str)
            banner_obj = await client.get_remote_object("""
                (() => {
                    const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                    return inputs.find(i => i.closest && (i.closest('.ytcpBannerUploadInstructions') || i.closest('ytcp-banner-image-upload'))) || inputs[0];
                })()
            """)
            b_obj_id = banner_obj.get("objectId")
            if b_obj_id:
                try:
                    await client.call("DOM.setFileInputFiles", {
                        "files": [ban_str],
                        "objectId": b_obj_id,
                    })
                    logger.info("Banner set. Waiting for crop dialog...")
                    await asyncio.sleep(3.0)
                    await client.evaluate("""
                        (() => {
                            const btn = document.querySelector('#done-button') ||
                                        Array.from(document.querySelectorAll('ytcp-button, button')).find(b => b.innerText === 'Xong' || b.innerText === 'Done');
                            if (btn) btn.click();
                        })()
                    """)
                    logger.info("Banner crop confirmed.")
                    await asyncio.sleep(2.0)
                except Exception as e:
                    logger.warning("Banner upload exception: %s", e)

        # 6. Publish Changes
        logger.info("Clicking Publish button to apply customization...")
        pub_res = await client.evaluate("""
            (() => {
                const btn = document.querySelector('#publish-button') ||
                            Array.from(document.querySelectorAll('ytcp-button, button')).find(b => b.innerText.includes('Xuất bản') || b.innerText.includes('Publish'));
                if (!btn) return false;
                const disabled = btn.getAttribute('aria-disabled') === 'true' || btn.hasAttribute('disabled');
                if (!disabled) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        logger.info("Publish clicked: %s", pub_res)
        await asyncio.sleep(8.0)

        # 7. Verification Screenshot
        if screenshot_path:
            await client.capture_screenshot(screenshot_path)
            logger.info("Saved QA screenshot to: %s", screenshot_path)

        # 8. Check Saved Info
        saved_info = await client.evaluate("""
            (() => {
                const name = document.querySelector('input.ytcpChannelEditingChannelNameFormInput')?.value;
                const handle = document.querySelector('input.YtcpChannelEditingChannelHandleHandleInput')?.value;
                const desc = document.querySelector('ytcp-social-suggestions-textbox #textbox')?.innerText;
                return { name, handle, desc: desc ? desc.substring(0, 100) : '' };
            })()
        """)

        return {
            "channel_id": cid,
            "channel_name": (saved_info or {}).get("name") or channel_name,
            "handle": f"@{(saved_info or {}).get('handle') or accepted_handle}",
            "description": description,
            "screenshot": str(screenshot_path) if screenshot_path else None,
        }
    finally:
        await client.close()
        client.terminate_browser()


def main():
    parser = argparse.ArgumentParser(description="YouTube Channel Customization Tool")
    parser.add_argument("--channel", help="Channel identifier (e.g. ua_sao_vay, ai_binh_dan)")
    parser.add_argument("--name", help="Channel Name")
    parser.add_argument("--handles", nargs="+", help="Handle candidate options")
    parser.add_argument("--description", help="Channel Description")
    parser.add_argument("--avatar", help="Path to avatar image (800x800)")
    parser.add_argument("--banner", help="Path to banner image (2048x1152)")
    parser.add_argument("--port", type=int, help="Chrome CDP Port")
    parser.add_argument("--profile-dir", help="Chrome Profile Directory")
    parser.add_argument("--user-data-dir", help="Chrome User Data Dir")
    parser.add_argument("--email", help="Account Email")
    parser.add_argument("--screenshot", help="Output path for QA screenshot")

    args = parser.parse_args()

    channel_name = args.name
    handle_candidates = args.handles
    description = args.description
    avatar_path = args.avatar
    banner_path = args.banner
    port = args.port
    profile_dir = args.profile_dir
    user_data_dir = args.user_data_dir
    email = args.email
    screenshot = args.screenshot

    map_file = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
    if args.channel:
        spec_file = REPO_ROOT / "sys" / "channels" / args.channel / "assets" / "channel_setup_spec.json"
        if spec_file.exists():
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
            if not channel_name:
                channel_name = spec.get("youtube_name")
            if not handle_candidates:
                handle_candidates = spec.get("handle_candidates", [])
            if not description:
                description = spec.get("description", "")
            assets = spec.get("assets", {})
            if not avatar_path:
                avatar_path = assets.get("avatar_800x800")
            if not banner_path:
                banner_path = assets.get("banner_2048x1152")

        if map_file.exists():
            ch_map = json.loads(map_file.read_text(encoding="utf-8"))
            if args.channel in ch_map.get("channels", {}):
                entry = ch_map["channels"][args.channel]
                if port is None:
                    port = entry.get("cdp_port")
                if profile_dir is None:
                    profile_dir = entry.get("directory")
                if user_data_dir is None:
                    user_data_dir = entry.get("user_data_dir")
                if email is None:
                    email = entry.get("email")

        if not screenshot:
            screenshot = str(REPO_ROOT / "sys/reports" / f"channel_setup_{args.channel}.png")

    if not channel_name:
        parser.error("Channel name must be provided via --name or --channel")
    if not handle_candidates:
        parser.error("Handle candidates must be provided via --handles or --channel")
    if not description:
        description = ""
    if port is None:
        port = 9230
    if profile_dir is None:
        profile_dir = "Profile 15"
    if user_data_dir is None:
        user_data_dir = str(Path.home() / ".config/google-chrome-cdp-p15")
    if email is None:
        email = ""

    profile_cfg = {
        "id": args.channel or "custom",
        "port": port,
        "directory": profile_dir,
        "user_data_dir": user_data_dir,
        "email": email,
    }

    result = asyncio.run(
        setup_channel_branding(
            channel_name=channel_name,
            handle_candidates=handle_candidates,
            description=description,
            avatar_path=avatar_path,
            banner_path=banner_path,
            profile_cfg=profile_cfg,
            screenshot_path=screenshot,
        )
    )

    if args.channel and map_file.exists() and result.get("channel_id"):
        try:
            ch_map = json.loads(map_file.read_text(encoding="utf-8"))
            if args.channel in ch_map.get("channels", {}):
                entry = ch_map["channels"][args.channel]
                entry["youtube_channel_id"] = result["channel_id"]
                entry["youtube_channel_url"] = f"https://www.youtube.com/channel/{result['channel_id']}"
                if result.get("handle"):
                    entry["handle"] = result["handle"]
                if result.get("channel_name"):
                    entry["channel_name"] = result["channel_name"]
                map_file.write_text(json.dumps(ch_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                logger.info("Updated youtube_channel_map.json with channel info for %s", args.channel)
        except Exception as e:
            logger.warning("Could not update youtube_channel_map.json: %s", e)

    print("\n=== CHANNEL SETUP RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
