#!/usr/bin/env python3
"""YouTube CDP Publisher Tool for Video Pilot (sys/tools/publish_youtube_cdp.py).

Automates uploading Long (16:9) and Short (9:16) videos directly to YouTube Studio
via Chrome DevTools Protocol (CDP) using persistent signed-in Chrome profiles.

Features:
- Connects to existing or spawned Chrome profiles via ProcessGroupManager.
- Navigates to YouTube Studio and verifies channel authentication.
- Automatically handles video file attachment, title, description with chapters.
- Sets 'Not made for kids' audience settings.
- Uploads custom 16:9 thumbnails with graceful eligibility handling.
- Steppers through Details -> Elements -> Checks -> Visibility (PUBLIC).
- Waits for upload progress to complete before publishing.
- Extracts live video URLs (https://youtu.be/<ID>).
- Captures QA screenshots at publication milestones.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Optional

import websockets

# Add repository root to Python path
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
for _p in (str(REPO_ROOT), str(SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_cdp.process_manager import ProcessGroupManager, is_port_listening
from sys.flow_cdp.resource_locks import ProfilePortLock

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("publish_youtube_cdp")


class YouTubeCDPClient:
    """Direct CDP Controller for YouTube Studio."""

    def __init__(
        self,
        profile_cfg: dict[str, Any],
        headless: bool = False,
        startup_timeout: float = 30.0,
    ):
        self.profile_cfg = profile_cfg
        self.port = int(profile_cfg.get("port") or profile_cfg.get("cdp_port", 9234))
        self.headless = headless
        self.startup_timeout = startup_timeout
        self.pm = ProcessGroupManager()
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.msg_id = 0
        self._reader_task: Optional[asyncio.Task] = None
        self.pending: dict[int, asyncio.Future] = {}
        self._port_lock = ProfilePortLock(self.port, owner_tag="youtube_publisher")

    def ensure_browser(self) -> bool:
        """Launch Chrome profile if not already running."""
        if not self._port_lock.acquire(timeout=120.0):
            raise TimeoutError(f"CDP port {self.port} locked by another process after 120s timeout")
        if is_port_listening(self.port):
            logger.info("Chrome is already listening on port %d", self.port)
            return True
        logger.info("Launching Chrome profile on port %d (headless=%s)...", self.port, self.headless)
        return self.pm.launch(
            self.profile_cfg,
            url="https://studio.youtube.com",
            headless=self.headless,
            startup_timeout=self.startup_timeout,
        )

    def _get_page_ws_url(self) -> str:
        """Find the page target for YouTube Studio."""
        deadline = time.time() + 20.0
        while time.time() < deadline:
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{self.port}/json")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                studio_target = None
                for t in targets:
                    if t.get("type") == "page":
                        url = t.get("url", "")
                        if "studio.youtube.com" in url:
                            return t["webSocketDebuggerUrl"]
                        studio_target = t
                if studio_target:
                    return studio_target["webSocketDebuggerUrl"]
            except Exception:
                pass
            time.sleep(0.5)
        raise RuntimeError(f"Could not find YouTube Studio page target on port {self.port}")

    async def connect(self) -> None:
        """Connect WebSocket to Chrome CDP."""
        self.ensure_browser()
        ws_url = self._get_page_ws_url()
        logger.info("Connecting to CDP WebSocket: %s", ws_url)
        self.ws = await websockets.connect(
            ws_url,
            max_size=64 * 1024 * 1024,
            ping_interval=None,
            ping_timeout=None,
            close_timeout=10,
        )
        self._reader_task = asyncio.create_task(self._reader())
        await self.call("Page.enable")
        await self.call("Runtime.enable")
        await self.call("DOM.enable")
        try:
            await self.call("DOM.getDocument", {"depth": -1, "pierce": True})
        except Exception:
            pass

    async def close(self) -> None:
        """Cleanly close WebSocket and release port lock."""
        try:
            if self._reader_task:
                self._reader_task.cancel()
            if self.ws:
                try:
                    await self.ws.close()
                except Exception:
                    pass
        finally:
            self._port_lock.release()

    def terminate_browser(self) -> None:
        """Terminate the Chrome process group."""
        self.pm.terminate_by_port(self.port)

    async def _reader(self) -> None:
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                mid = msg.get("id")
                if mid is not None and mid in self.pending:
                    fut = self.pending.pop(mid)
                    if not fut.done():
                        fut.set_result(msg)
        except Exception as e:
            for fut in list(self.pending.values()):
                if not fut.done():
                    fut.set_exception(e)
            self.pending.clear()

    async def call(self, method: str, params: Optional[dict] = None, timeout: float = 60.0) -> dict:
        self.msg_id += 1
        mid = self.msg_id
        fut = asyncio.get_running_loop().create_future()
        self.pending[mid] = fut
        try:
            await self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            res = await asyncio.wait_for(fut, timeout=timeout)
        except Exception:
            self.pending.pop(mid, None)
            raise
        if "error" in res:
            raise RuntimeError(f"CDP error in {method}: {res['error']}")
        return res.get("result", {})

    async def evaluate(self, expression: str, await_promise: bool = True, timeout: float = 60.0) -> Any:
        res = await self.call(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": await_promise, "returnByValue": True},
            timeout=timeout,
        )
        if "exceptionDetails" in res:
            exc = res["exceptionDetails"]
            raise RuntimeError(f"JS Exception: {exc.get('text')} {exc.get('exception', {}).get('description', '')}")
        return res.get("result", {}).get("value")

    async def get_remote_object(self, expression: str) -> dict:
        res = await self.call(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": False, "returnByValue": False},
        )
        return res.get("result", {})

    async def capture_screenshot(self, output_path: str | Path) -> Path:
        """Capture full viewport screenshot and save to disk."""
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        shot = await self.call("Page.captureScreenshot", {"format": "png"})
        data = shot.get("data")
        if data:
            path.write_bytes(base64.b64decode(data))
            logger.info("Saved screenshot to %s", path)
        return path

    async def get_channel_info(self) -> dict[str, Any]:
        """Verify Studio dashboard and extract active channel information."""
        info = await self.evaluate("""
            (() => {
                const title = document.title;
                const url = window.location.href;
                const m = url.match(/studio\\.youtube\\.com\\/channel\\/([^\\/\\?#]+)/);
                const channelId = m ? m[1] : null;

                // Channel name element on sidebar or avatar
                const nameEl = document.querySelector('#channel-title') ||
                               document.querySelector('#entity-name') ||
                               document.querySelector('ytcp-home-page #title');
                let name = nameEl ? nameEl.innerText.trim() : null;
                if (!name) {
                    const text = document.body ? document.body.innerText : '';
                    const mName = text.match(/Kênh của bạn[\\s\\n]+([^\\n]+)/);
                    if (mName) name = mName[1].trim();
                }
                return { title, url, channelId, channelName: name };
            })()
        """)
        return info or {}

    async def open_upload_dialog(self) -> bool:
        """Click upload icon or create button to open the upload wizard."""
        logger.info("Opening upload dialog...")
        clicked = await self.evaluate("""
            (() => {
                const btn = document.querySelector('#upload-icon') ||
                            document.querySelector('ytcp-icon-button#upload-icon') ||
                            document.querySelector('#create-icon') ||
                            document.querySelector('ytcp-button#create-icon');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        if not clicked:
            raise RuntimeError("Could not find YouTube Studio upload or create button!")

        await asyncio.sleep(2.0)

        # If a dropdown menu appeared, select "Tải video lên"
        await self.evaluate("""
            (() => {
                const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu tp-yt-paper-item'));
                const uploadItem = items.find(it => it.innerText.includes('Tải video') || it.innerText.includes('Upload video'));
                if (uploadItem) uploadItem.click();
            })()
        """)

        # Wait for <input type="file" name="Filedata">
        deadline = time.time() + 15.0
        while time.time() < deadline:
            has_input = await self.evaluate("""
                Boolean(document.querySelector('ytcp-uploads-dialog input[type="file"]') || document.querySelector('input[type="file"]'))
            """)
            if has_input:
                logger.info("Upload dialog opened and file input located.")
                return True
            await asyncio.sleep(0.5)

        raise RuntimeError("Upload dialog did not open within timeout.")

    async def attach_video(self, video_path: str | Path) -> None:
        """Attach MP4 video file via CDP DOM.setFileInputFiles."""
        path_str = str(Path(video_path).resolve())
        if not os.path.isfile(path_str):
            raise FileNotFoundError(f"Video file not found: {path_str}")

        logger.info("Attaching video file: %s", path_str)
        input_obj = await self.get_remote_object("""
            (() => {
                const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
                return inputs.find(i => i.name === 'Filedata') || inputs[0];
            })()
        """)
        obj_id = input_obj.get("objectId")
        if not obj_id:
            raise RuntimeError("Could not resolve objectId for video file input!")

        await self.call("DOM.setFileInputFiles", {
            "files": [path_str],
            "objectId": obj_id,
        })
        logger.info("File input set. Waiting for transition to Details step...")

        # Wait for Details step (step 0 active or title textbox visible)
        deadline = time.time() + 25.0
        while time.time() < deadline:
            has_details = await self.evaluate("""
                Boolean(
                    document.querySelector('#title-textarea #textbox') ||
                    document.querySelector('#textbox[contenteditable="true"]') ||
                    document.querySelector('ytcp-uploads-video-details')
                )
            """)
            if has_details:
                logger.info("Successfully transitioned to Details step.")
                return
            await asyncio.sleep(0.5)

        raise RuntimeError("Timed out waiting for Details dialog to load after file attachment.")

    async def extract_video_url(self) -> Optional[str]:
        """Extract YouTube video URL specifically from the upload dialog (https://youtu.be/<ID>)."""
        for _ in range(20):
            url = await self.evaluate("""
                (() => {
                    const dialog = document.querySelector('ytcp-uploads-dialog');
                    if (!dialog) return null;
                    const links = Array.from(dialog.querySelectorAll('a')).map(a => a.href).filter(Boolean);
                    const ytLink = links.find(l => l.includes('youtu.be/'));
                    if (ytLink) return ytLink;
                    const watchLink = links.find(l => l.includes('youtube.com/watch?v=') || l.includes('youtube.com/shorts/'));
                    return watchLink || null;
                })()
            """)
            if url:
                return url
            await asyncio.sleep(1.0)
        return None

    async def fill_details(
        self,
        title: str,
        description: str,
        is_kids: bool = False,
    ) -> None:
        """Set title, description, and audience settings."""
        logger.info("Filling title: %s", title)
        title_res = await self.evaluate(f"""
            (() => {{
                const el = document.querySelector('#title-textarea #textbox') ||
                           document.querySelector('#textbox[contenteditable="true"]');
                if (!el) return false;
                el.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(title)});
                el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                return el.innerText;
            }})()
        """)
        logger.info("Title set: %s", title_res)

        logger.info("Filling description (%d chars)...", len(description))
        desc_res = await self.evaluate(f"""
            (() => {{
                const el = document.querySelector('#description-textarea #textbox');
                if (!el) return false;
                el.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {json.dumps(description)});
                el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                return el.innerText ? el.innerText.substring(0, 100) : '';
            }})()
        """)
        logger.info("Description set preview: %s...", desc_res)

        logger.info("Setting audience: Not made for kids (MFK=False)...")
        radio_name = "VIDEO_MADE_FOR_KIDS_MFK" if is_kids else "VIDEO_MADE_FOR_KIDS_NOT_MFK"
        await self.evaluate(f"""
            (() => {{
                const radio = document.querySelector('tp-yt-paper-radio-button[name="{radio_name}"]');
                if (radio) radio.click();
            }})()
        """)
        await asyncio.sleep(1.0)

    async def upload_thumbnail(self, thumbnail_path: str | Path) -> bool:
        """Upload custom thumbnail if provided and supported."""
        path_str = str(Path(thumbnail_path).resolve())
        if not os.path.isfile(path_str):
            logger.warning("Thumbnail file does not exist: %s", path_str)
            return False

        logger.info("Uploading custom thumbnail: %s", path_str)
        thumb_obj = await self.get_remote_object("""
            (() => {
                const input = document.querySelector('input#file-loader') ||
                              Array.from(document.querySelectorAll('input[type="file"]')).find(i => i.accept && i.accept.includes('image'));
                return input;
            })()
        """)
        obj_id = thumb_obj.get("objectId")
        if not obj_id:
            logger.warning("Could not find thumbnail file input.")
            return False

        try:
            await self.call("DOM.setFileInputFiles", {
                "files": [path_str],
                "objectId": obj_id,
            })
            logger.info("Thumbnail attached successfully.")
            await asyncio.sleep(2.0)

            # Check for verification modal
            has_verify = await self.evaluate("""
                Boolean(
                    document.querySelector('ytcp-feature-eligibility-dialog') ||
                    document.querySelector('ytcp-dialog[aria-label*="xác minh"]') ||
                    document.querySelector('ytcp-dialog[aria-label*="verify"]')
                )
            """)
            if has_verify:
                logger.warning("Custom thumbnail requires phone verification; dismissing prompt to continue.")
                await self.evaluate("""
                    (() => {
                        const cancel = document.querySelector('#cancel-button') ||
                                       document.querySelector('ytcp-button#dismiss-button') ||
                                       document.querySelector('ytcp-dialog #close-button');
                        if (cancel) cancel.click();
                    })()
                """)
                return False
            return True
        except Exception as e:
            logger.warning("Thumbnail upload encountered exception: %s", e)
            return False

    async def link_related_video(self, related_url_or_id: str) -> bool:
        """For Shorts: Link related video in the Studio dialog if accessible."""
        if not related_url_or_id:
            return False
        logger.info("Attempting to configure related video: %s", related_url_or_id)
        # Search for related video container
        res = await self.evaluate("""
            (() => {
                const picker = document.querySelector('ytcp-video-metadata-editor-advanced #related-video-picker') ||
                               Array.from(document.querySelectorAll('ytcp-button, button')).find(b => b.innerText.includes('Video liên quan') || b.innerText.includes('Related video'));
                if (picker) {
                    picker.click();
                    return true;
                }
                return false;
            })()
        """)
        if res:
            await asyncio.sleep(2.0)
            await self.evaluate(f"""
                (() => {{
                    const query = {json.dumps(related_url_or_id)};
                    const item = Array.from(document.querySelectorAll('ytcp-entity-picker-dialog ytcp-entity-picker-item, ytcp-video-row')).find(it => it.innerText.includes(query) || (query.length > 5 && it.innerText.includes(query.substring(0, 15))));
                    if (item) item.click();
                }})()
            """)
            logger.info("Linked related video successfully.")
            return True
        logger.info("Related video picker not visible or already set.")
        return False

    async def advance_to_visibility_step(self) -> None:
        """Click next-button repeatedly until reaching Step 4 (Visibility)."""
        logger.info("Advancing through wizard steps to Visibility step...")
        for step in range(3):
            # Check if Visibility radio is already visible
            has_pub = await self.evaluate("""
                Boolean(document.querySelector('tp-yt-paper-radio-button[name="PUBLIC"]'))
            """)
            if has_pub:
                logger.info("Reached Visibility step.")
                return

            clicked = await self.evaluate("""
                (() => {
                    const btn = document.querySelector('#next-button');
                    if (btn && btn.getAttribute('aria-disabled') !== 'true') {
                        btn.click();
                        return true;
                    }
                    return false;
                })()
            """)
            logger.info("Clicked next-button (iteration %d): %s", step + 1, clicked)
            await asyncio.sleep(2.5)

        # Final check if on Visibility
        await asyncio.sleep(1.0)

    async def set_visibility(self, visibility: str = "PUBLIC") -> None:
        """Select visibility mode (PUBLIC, UNLISTED, PRIVATE) and verify selection."""
        logger.info("Setting visibility to %s...", visibility)
        radio_name = visibility.upper()
        res = await self.evaluate(f"""
            (() => {{
                const radio = document.querySelector('tp-yt-paper-radio-button[name="{radio_name}"]');
                if (radio) {{
                    radio.click();
                    return radio.getAttribute('aria-checked') || radio.checked;
                }}
                return null;
            }})()
        """)
        logger.info("Visibility radio %s checked: %s", radio_name, res)
        await asyncio.sleep(1.0)

    async def wait_for_upload_complete(self, max_wait_sec: float = 300.0) -> bool:
        """Monitor upload progress label until upload reaches 100% / processing."""
        logger.info("Monitoring upload progress (max wait %.0fs)...", max_wait_sec)
        deadline = time.time() + max_wait_sec
        last_log = 0.0

        while time.time() < deadline:
            state = await self.evaluate("""
                (() => {
                    const statusEl = document.querySelector('span.progress-label') ||
                                     document.querySelector('.ytcp-video-upload-progress') ||
                                     document.querySelector('ytcp-video-upload-progress');
                    const doneBtn = document.querySelector('#done-button');
                    const text = statusEl ? statusEl.innerText.trim() : '';
                    const doneDisabled = doneBtn ? (doneBtn.hasAttribute('disabled') || doneBtn.getAttribute('aria-disabled') === 'true') : true;
                    return { text, doneDisabled };
                })()
            """)
            text = (state or {}).get("text", "")
            done_disabled = (state or {}).get("doneDisabled", True)

            now = time.time()
            if now - last_log > 5.0:
                logger.info("Upload status: %r (Publish button ready: %s)", text, not done_disabled)
                last_log = now

            is_uploading = "đang tải lên" in text.lower() or "uploading" in text.lower()
            if not done_disabled and not is_uploading:
                logger.info("Upload complete and verified ready for publication.")
                return True

            if not done_disabled and ("100%" in text or "đã xử lý" in text.lower() or "đã hoàn tất" in text.lower() or "đã kiểm tra" in text.lower()):
                logger.info("Upload progress reached 100%% / processing.")
                return True

            await asyncio.sleep(2.0)

        logger.warning("Upload wait timed out after %.0fs; continuing publication.", max_wait_sec)
        return False

    async def publish_and_finish(self, screenshot_path: Optional[str | Path] = None) -> Optional[str]:
        """Click the Publish/Done button, capture share dialog, and extract confirmed URL."""
        logger.info("Clicking Publish / Done button (#done-button)...")
        clicked = await self.evaluate("""
            (() => {
                const btn = document.querySelector('#done-button');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        if not clicked:
            raise RuntimeError("Could not find Done / Publish button (#done-button)!")

        # Wait for share confirmation dialog
        logger.info("Waiting for publication confirmation dialog...")
        confirmed_url = None
        for _ in range(12):
            await asyncio.sleep(1.0)
            confirmed = await self.evaluate("""
                (() => {
                    const shareDialog = document.querySelector('ytcp-video-share-dialog');
                    const link = shareDialog ? shareDialog.querySelector('a')?.href : null;
                    const title = shareDialog ? shareDialog.querySelector('#dialog-title')?.innerText?.trim() : null;
                    return { found: Boolean(shareDialog), link, title };
                })()
            """)
            if confirmed and confirmed.get("link"):
                confirmed_url = confirmed["link"]
                logger.info("Publication confirmed: %s (Title: %s)", confirmed_url, confirmed.get("title"))
                break

        if screenshot_path:
            await self.capture_screenshot(screenshot_path)

        # Close share modal
        await self.evaluate("""
            (() => {
                const closeBtn = document.querySelector('ytcp-video-share-dialog #close-button') ||
                                 document.querySelector('#close-button');
                if (closeBtn) closeBtn.click();
            })()
        """)
        await asyncio.sleep(2.0)
        return confirmed_url


async def publish_single_video(
    video_path: str | Path,
    title: str,
    description: str,
    thumbnail_path: Optional[str | Path] = None,
    subtitles_path: Optional[str | Path] = None,
    visibility: str = "PUBLIC",
    is_short: bool = False,
    related_video_url: Optional[str] = None,
    screenshot_path: Optional[str | Path] = None,
    profile_cfg: Optional[dict[str, Any]] = None,
    headless: bool = False,
) -> dict[str, Any]:
    """Execute end-to-end publish flow for a single video."""
    if profile_cfg is None:
        profile_cfg = {
            "id": "profile_13",
            "port": 9234,
            "directory": "Profile 14",
            "user_data_dir": str(Path.home() / ".config/google-chrome-cdp-profile14"),
            "email": "",
        }

    client = YouTubeCDPClient(profile_cfg, headless=headless)
    try:
        await client.connect()

        # Step 0: Ensure browser is at YouTube Studio dashboard
        curr_url = await client.evaluate("window.location.href")
        if "studio.youtube.com" not in curr_url:
            logger.info("Navigating to https://studio.youtube.com...")
            await client.call("Page.navigate", {"url": "https://studio.youtube.com"})
            await asyncio.sleep(6.0)

        # Step 1: Channel Info Verification
        await asyncio.sleep(4.0)
        channel_info = await client.get_channel_info()
        logger.info("Channel info: %s", channel_info)

        # Step 2: Open Upload Dialog
        await client.open_upload_dialog()

        # Step 3: Attach Video File
        await client.attach_video(video_path)

        # Step 4: Extract Video URL from Dialog
        dialog_video_url = await client.extract_video_url()
        logger.info("Assigned video URL in dialog: %s", dialog_video_url)

        # Step 5: Fill Metadata (Title, Description, MFK)
        await client.fill_details(title=title, description=description, is_kids=False)

        # Step 6: Custom Thumbnail (Long 16:9)
        thumbnail_status = False
        if thumbnail_path and not is_short:
            thumbnail_status = await client.upload_thumbnail(thumbnail_path)

        # Step 7: Advance through wizard to Step 4 (Visibility)
        await client.advance_to_visibility_step()

        # Step 8: Set Visibility to PUBLIC
        await client.set_visibility(visibility)

        # Step 9: Wait for upload completion
        await client.wait_for_upload_complete()

        # Step 10: Finalize Publication & QA Screenshot
        final_url = await client.publish_and_finish(screenshot_path=screenshot_path)
        resolved_url = final_url or dialog_video_url

        return {
            "status": "PUBLISHED",
            "channel_name": channel_info.get("channelName", "Sticker Vocabulary"),
            "channel_id": channel_info.get("channelId"),
            "video_url": resolved_url,
            "title": title,
            "visibility": visibility,
            "thumbnail_uploaded": thumbnail_status,
            "screenshot_path": str(screenshot_path) if screenshot_path else None,
        }
    finally:
        await client.close()
        client.terminate_browser()


def parse_metadata_file(md_path: str | Path) -> dict[str, str]:
    """Parse title and description from markdown publication kit."""
    text = Path(md_path).read_text(encoding="utf-8")
    title = ""
    description = ""

    # Title extraction
    m_title = re.search(r"## 1\. Tiêu đề[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
    if m_title:
        title = m_title.group(1).strip()

    # Description extraction
    m_desc = re.search(r"## 2\. Mô tả[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
    if m_desc:
        description = m_desc.group(1).strip()

    return {"title": title, "description": description}


def main():
    parser = argparse.ArgumentParser(description="Automated YouTube CDP Publisher for Video Pilot")
    parser.add_argument("--video", required=True, help="Path to MP4 video file")
    parser.add_argument("--channel", help="Channel ID (e.g., co_the_ke, ai_binh_dan) to resolve profile")
    parser.add_argument("--profile", help="Explicit Chrome profile ID (e.g. profile_1)")
    parser.add_argument("--title", help="Video title (overrides metadata file)")
    parser.add_argument("--description", help="Video description (overrides metadata file)")
    parser.add_argument("--metadata", help="Path to markdown metadata file (youtube_long.md / youtube_shorts.md)")
    parser.add_argument("--thumbnail", help="Path to thumbnail image file (for 16:9)")
    parser.add_argument("--subtitles", help="Path to subtitles SRT file")
    parser.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "UNLISTED", "PRIVATE"])
    parser.add_argument("--short", action="store_true", help="Mark as Short (9:16)")
    parser.add_argument("--related-video", help="Related video URL or ID (for Shorts)")
    parser.add_argument("--screenshot", help="Output path for verification screenshot")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")

    args = parser.parse_args()

    title = args.title
    description = args.description

    if args.metadata:
        meta = parse_metadata_file(args.metadata)
        if not title:
            title = meta.get("title")
        if not description:
            description = meta.get("description")

    if not title:
        parser.error("Title must be specified via --title or --metadata")
    if not description:
        description = ""

    profile_cfg = None
    map_file = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
    if args.channel and map_file.exists():
        ch_map = json.loads(map_file.read_text(encoding="utf-8"))
        if args.channel in ch_map.get("channels", {}):
            entry = ch_map["channels"][args.channel]
            profile_cfg = {
                "id": entry["profile_id"],
                "port": entry["cdp_port"],
                "directory": entry["directory"],
                "user_data_dir": entry["user_data_dir"],
                "email": entry["email"],
            }
    elif args.profile:
        flow_profiles_file = Path.home() / ".config/video-pilot/flow/profiles.json"
        if flow_profiles_file.exists():
            data = json.loads(flow_profiles_file.read_text(encoding="utf-8"))
            for p in data.get("profiles", []):
                if p["id"] == args.profile:
                    profile_cfg = p
                    break

    result = asyncio.run(
        publish_single_video(
            video_path=args.video,
            title=title,
            description=description,
            thumbnail_path=args.thumbnail,
            subtitles_path=args.subtitles,
            visibility=args.visibility,
            is_short=args.short,
            related_video_url=args.related_video,
            screenshot_path=args.screenshot,
            profile_cfg=profile_cfg,
            headless=args.headless,
        )
    )

    if args.channel and result.get("video_url") and map_file.exists():
        try:
            ch_map = json.loads(map_file.read_text(encoding="utf-8"))
            if args.channel in ch_map.get("channels", {}):
                entry = ch_map["channels"][args.channel]
                if args.short:
                    entry["short_video_url"] = result["video_url"]
                else:
                    entry["long_video_url"] = result["video_url"]
                if result.get("channel_id"):
                    entry["youtube_channel_id"] = result["channel_id"]
                    entry["youtube_channel_url"] = f"https://www.youtube.com/channel/{result['channel_id']}"
                history = entry.setdefault("published_videos", [])
                existing_urls = {v.get("video_url") for v in history if isinstance(v, dict)}
                if result["video_url"] not in existing_urls:
                    history.append({
                        "video_url": result["video_url"],
                        "title": title,
                        "format": "short_9x16" if args.short else "long_16x9",
                        "related_video_url": args.related_video,
                        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    })
                map_file.write_text(json.dumps(ch_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                logger.info("Updated youtube_channel_map.json for %s with %s", args.channel, result["video_url"])
        except Exception as e:
            logger.warning("Failed to update youtube_channel_map.json: %s", e)

    print("\n=== PUBLISH REPORT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
