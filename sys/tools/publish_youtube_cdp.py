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

try:
    from tools.review_queue_manager import check_publish_permission, set_review_decision
except ImportError:
    from sys.tools.review_queue_manager import check_publish_permission, set_review_decision

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("publish_youtube_cdp")


def verify_short_live(short_url_or_id: str) -> dict[str, Any]:
    """Verify whether a YouTube Short displays the native Related Video pill live via Innertube HTML."""
    vid = short_url_or_id.strip().rstrip("/").split("/")[-1].split("?")[0]
    req = urllib.request.Request(
        f"https://www.youtube.com/shorts/{vid}",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return {"video_id": vid, "has_pill": False, "verified_live": False, "error": str(e)}

    linked_title = None
    m = re.search(r"var ytInitialData = ({.*?});</script>", html)
    if not m:
        m = re.search(r"ytInitialData\s*=\s*({.+?});</script>", html)

    if m:
        data_str = m.group(1)
        chunks = data_str.split("id.reel_multi_format_link")
        if len(chunks) > 1:
            for c in chunks[1:]:
                tm = re.search(r'"content":\s*"([^"]+)"', c[:400])
                if tm:
                    linked_title = tm.group(1)
                    break

    if not linked_title and "reel_multi_format_link" in html:
        rm = re.search(r'"accessibilityId":\s*"id\.reel_multi_format_link".*?"content":\s*"([^"]+)"', html)
        if rm:
            linked_title = rm.group(1)

    has_pill = "reel_multi_format_link" in html
    return {
        "video_id": vid,
        "has_pill": has_pill,
        "verified_live": bool(linked_title or has_pill),
        "linked_title": linked_title,
    }


def fetch_youtube_title(video_url_or_id: str) -> Optional[str]:
    """Fetch video title using local youtube_channel_map.json or YouTube oEmbed."""
    if not video_url_or_id:
        return None
    vid = video_url_or_id.strip().rstrip("/").split("/")[-1].split("?")[0]
    if not vid:
        return None

    # 1. Quick check against youtube_channel_map.json
    try:
        map_path = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
        if map_path.exists():
            data = json.loads(map_path.read_text(encoding="utf-8"))
            for ch in data.get("channels", {}).values():
                for v in ch.get("published_videos", []):
                    u = v.get("video_url", "")
                    if vid in u and v.get("title"):
                        return v.get("title")
    except Exception:
        pass

    # 2. Network check via oEmbed
    req = urllib.request.Request(
        f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            info = json.loads(resp.read().decode("utf-8", errors="ignore"))
            return info.get("title")
    except Exception:
        return None


class YouTubeCDPClient:
    """Direct CDP Controller for YouTube Studio."""

    def __init__(
        self,
        profile_cfg: dict[str, Any],
        headless: bool = True,
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
        self._is_hardening = False

    def ensure_browser(self) -> bool:
        """Launch Chrome profile if not already running."""
        if not self._port_lock.acquire(timeout=120.0):
            raise TimeoutError(f"CDP port {self.port} locked by another process after 120s timeout")
        if is_port_listening(self.port):
            logger.info("Chrome is already listening on port %d", self.port)
            return True
        logger.info("Launching Chrome profile on port %d (headless=%s)...", self.port, self.headless)
        extra_args = ["--window-size=1920,1080"] if self.headless else None
        return self.pm.launch(
            self.profile_cfg,
            url="https://studio.youtube.com",
            headless=self.headless,
            startup_timeout=self.startup_timeout,
            extra_args=extra_args,
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

    async def configure_headless_hardening(self) -> None:
        """Apply Anti-Interstitial User-Agent override and 1080p Emulation metrics."""
        clean_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        try:
            ver = await self.call("Browser.getVersion")
            ua = ver.get("userAgent", "")
            if ua:
                clean_ua = ua.replace("HeadlessChrome/", "Chrome/")
        except Exception as e:
            logger.debug("Browser.getVersion fallback: %s", e)

        try:
            await self.call("Network.setUserAgentOverride", {"userAgent": clean_ua})
            logger.info("Configured Network.setUserAgentOverride: %s", clean_ua)
        except Exception as e:
            logger.warning("Failed to set Network.setUserAgentOverride: %s", e)

        try:
            await self.call(
                "Emulation.setDeviceMetricsOverride",
                {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False},
            )
            logger.debug("Configured Emulation.setDeviceMetricsOverride: 1920x1080")
        except Exception as e:
            logger.warning("Failed to set Emulation.setDeviceMetricsOverride: %s", e)

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
            await self.call("Network.enable")
        except Exception:
            pass

        await self.configure_headless_hardening()

        try:
            await self.call("DOM.getDocument", {"depth": -1, "pierce": True})
        except Exception:
            pass

        try:
            await self.dismiss_studio_interstitials()
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
        if method == "Page.navigate" and not getattr(self, "_is_hardening", False):
            self._is_hardening = True
            try:
                await self.configure_headless_hardening()
            except Exception:
                pass
            finally:
                self._is_hardening = False
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
        await self.dismiss_studio_interstitials()
        await asyncio.sleep(1.0)

        click_js = r"""
            (() => {
                if (document.querySelector('ytcp-uploads-dialog input[type="file"]')) return 'ALREADY_OPEN';
                let btn = document.querySelector('#upload-icon') ||
                          document.querySelector('ytcp-icon-button#upload-icon') ||
                          document.querySelector('ytcp-button#upload-icon') ||
                          document.querySelector('#create-icon') ||
                          document.querySelector('ytcp-button#create-icon') ||
                          document.querySelector('ytcp-icon-button#create-icon') ||
                          document.querySelector('button#create-icon') ||
                          document.querySelector('button[aria-label*="Create"]') ||
                          document.querySelector('button[aria-label*="Upload"]') ||
                          document.querySelector('ytcp-button[aria-label*="Create"]') ||
                          document.querySelector('ytcp-button[aria-label*="Upload"]') ||
                          document.querySelector('[aria-label*="Create"]') ||
                          document.querySelector('[aria-label*="Upload"]');
                if (!btn) {
                    btn = Array.from(document.querySelectorAll('ytcp-button, button, [role="button"]')).find(
                        el => {
                            const txt = (el.innerText || el.getAttribute('aria-label') || '').trim();
                            return /^(Create|Tạo|Upload|Tải lên)$/i.test(txt) || /(Create|Tạo)\s*(video)?/i.test(txt);
                        }
                    );
                }
                if (btn) {
                    btn.click();
                    return 'CLICKED';
                }
                return null;
            })()
        """
        clicked = await self.evaluate(click_js)
        if not clicked:
            logger.info("Upload button not immediately found; navigating to /videos/upload?d=ud fallback...")
            await self.evaluate("""
                (() => {
                    const m = window.location.href.match(/(https:\\/\\/studio\\.youtube\\.com\\/channel\\/[^\\/\\?#]+)/);
                    const base = m ? m[1] : 'https://studio.youtube.com';
                    window.location.href = base + '/videos/upload?d=ud';
                })()
            """)
            await asyncio.sleep(7.0)
            await self.dismiss_studio_interstitials()
            await asyncio.sleep(2.0)
            clicked = await self.evaluate(click_js)
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

            # Check for verification or blocking modal
            has_verify = await self.evaluate("""
                (() => {
                    const d = document.querySelector('ytcp-feature-eligibility-dialog, yt-trust-tiers-wizard-dialog');
                    if (d && d.offsetParent !== null) return true;
                    const errModal = document.querySelector('ytcp-permanent-operational-error-manager tp-yt-paper-dialog[aria-hidden="false"]');
                    if (errModal && errModal.offsetParent !== null) return true;
                    const activeDialogs = Array.from(document.querySelectorAll('tp-yt-paper-dialog[aria-hidden="false"], ytcp-dialog')).filter(diag => {
                        const text = (diag.innerText || '').toLowerCase();
                        return diag.offsetParent !== null && (text.includes('xác minh') || text.includes('verify') || text.includes('số điện thoại') || text.includes('phone'));
                    });
                    return activeDialogs.length > 0;
                })()
            """)
            if has_verify:
                logger.warning("Custom thumbnail requires verification or encountered modal; dismissing prompt to continue.")
                await self.evaluate("""
                    (() => {
                        const cancel = document.querySelector('tp-yt-paper-dialog #close-button') ||
                                       document.querySelector('tp-yt-paper-dialog #cancel-button') ||
                                       document.querySelector('tp-yt-paper-dialog ytcp-button') ||
                                       document.querySelector('#cancel-button') ||
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

    async def attach_subtitles(self, subtitles_path: str | Path) -> bool:
        """Attach subtitles (.srt) file in YouTube Studio dialog if accessible."""
        sub_path = Path(subtitles_path).resolve()
        if not sub_path.is_file():
            logger.warning("Subtitles file not found: %s", sub_path)
            return False
        logger.info("Attempting to attach subtitles from %s...", sub_path)
        try:
            has_input = await self.evaluate("""
                Boolean(
                    document.querySelector('input[type="file"][accept*=".srt"]') ||
                    Array.from(document.querySelectorAll('input[type="file"]')).find(i => (i.accept || '').includes('.srt') || (i.name || '').includes('sub'))
                )
            """)
            if has_input:
                doc = await self.call("DOM.getDocument", {"depth": -1, "pierce": True})
                root_id = doc.get("root", {}).get("nodeId", 1)
                sub_node = await self.call("DOM.querySelector", {
                    "nodeId": root_id,
                    "selector": 'input[type="file"][accept*=".srt"], input[type="file"]',
                })
                node_id = sub_node.get("nodeId", 0)
                if node_id > 0:
                    await self.call("DOM.setFileInputFiles", {
                        "nodeId": node_id,
                        "files": [str(sub_path)],
                    })
                    logger.info("Attached subtitles file (%s) to file input successfully.", sub_path.name)
                    return True
            logger.info("Subtitle file input not directly exposed in current wizard step; logged for reference.")
            return False
        except Exception as e:
            logger.warning("Subtitle attachment encountered non-fatal error: %s", e)
            return False

    async def dismiss_studio_interstitials(self) -> bool:
        """Dismiss Studio unsupported browser interstitial banner or proceed button if present."""
        clicked = await self.evaluate("""
            (() => {
                const proceed = document.querySelector('#proceed-link');
                if (proceed) {
                    proceed.click();
                    return true;
                }
                const btn = Array.from(document.querySelectorAll('a, button, ytcp-button, [role="button"], #proceed-link')).find(el => {
                    if (el.id === 'proceed-link') return true;
                    const txt = (el.innerText || '').toLowerCase();
                    return txt.includes('skip to youtube studio') ||
                           txt.includes('chuyển thẳng đến youtube studio') ||
                           txt.includes('continue to youtube studio') ||
                           txt.includes('tiếp tục truy cập youtube studio') ||
                           txt.includes('tiếp tục chuyển đến youtube studio');
                });
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        if clicked:
            logger.info("Dismissed YouTube Studio unsupported browser / proceed interstitial.")
            await asyncio.sleep(2.0)
        return bool(clicked)

    def resolve_channel_handle(self, short_id: Optional[str] = None) -> Optional[str]:
        """Resolve channel @handle from profile_cfg, youtube_channel_map.json, or short_id."""
        if self.profile_cfg.get("handle"):
            return self.profile_cfg["handle"]

        map_path = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
        if map_path.exists():
            try:
                data = json.loads(map_path.read_text(encoding="utf-8"))
                channels = data.get("channels", {})
                if short_id:
                    for ch in channels.values():
                        for v in ch.get("published_videos", []):
                            if short_id in v.get("video_url", ""):
                                if ch.get("handle"):
                                    return ch["handle"]
                pid = self.profile_cfg.get("id") or self.profile_cfg.get("profile_id")
                if pid:
                    for ch in channels.values():
                        if ch.get("profile_id") == pid:
                            return ch.get("handle")
                port = self.port
                if port:
                    for ch in channels.values():
                        if ch.get("cdp_port") == port:
                            return ch.get("handle")
                udd = self.profile_cfg.get("user_data_dir")
                if udd:
                    for ch in channels.values():
                        if ch.get("user_data_dir") == udd:
                            return ch.get("handle")
            except Exception as e:
                logger.warning("Error reading youtube_channel_map.json: %s", e)
        return None

    async def check_trust_tiers_dialog(self) -> dict[str, Any]:
        """Detect if YouTube Studio popped up yt-trust-tiers-wizard-dialog or Tier 3 verification."""
        res = await self.evaluate("""
            (() => {
                const trustDialog = document.querySelector('yt-trust-tiers-wizard-dialog');
                if (trustDialog) {
                    const style = window.getComputedStyle(trustDialog);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        return {
                            detected: true,
                            source: 'tag:yt-trust-tiers-wizard-dialog',
                            text: (trustDialog.innerText || '').substring(0, 300)
                        };
                    }
                }

                const dialogs = Array.from(document.querySelectorAll(
                    'ytcp-dialog, tp-yt-paper-dialog, [role="dialog"], yt-dialog'
                ));
                for (const d of dialogs) {
                    const style = window.getComputedStyle(d);
                    if (style.display === 'none' || style.visibility === 'hidden') continue;
                    const txt = (d.innerText || '').toLowerCase();
                    if (
                        txt.includes('one-time verification') ||
                        txt.includes('xác minh một lần') ||
                        txt.includes('xác minh 1 lần') ||
                        txt.includes('trust-tiers') ||
                        txt.includes('intermediate features') ||
                        txt.includes('advanced features') ||
                        txt.includes('tính năng nâng cao')
                    ) {
                        return {
                            detected: true,
                            source: 'dialog_text',
                            text: d.innerText.substring(0, 300)
                        };
                    }
                }
                return { detected: false };
            })()
        """)
        return res or {"detected": False}

    async def dismiss_trust_tiers_dialog(self) -> bool:
        """Dismiss yt-trust-tiers-wizard-dialog cleanly."""
        dismissed = await self.evaluate("""
            (() => {
                const trustDialog = document.querySelector('yt-trust-tiers-wizard-dialog');
                const dialogs = trustDialog
                    ? [trustDialog]
                    : Array.from(document.querySelectorAll('ytcp-dialog, tp-yt-paper-dialog, [role="dialog"]'));
                for (const d of dialogs) {
                    const closeBtn = d.querySelector(
                        '#close-button, #cancel-button, ytcp-button#close-button, ytcp-button#cancel-button, ' +
                        '[aria-label="Đóng"], [aria-label="Close"], [aria-label="Hủy"], [aria-label="Cancel"], .close-button'
                    );
                    if (closeBtn) {
                        const btn = closeBtn.querySelector('button') || closeBtn;
                        btn.click();
                        return true;
                    }
                }
                return false;
            })()
        """)
        try:
            await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
            await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
        except Exception:
            pass
        await asyncio.sleep(1.5)
        return bool(dismissed)

    async def apply_clickable_handle_fallback(
        self,
        target_title: str,
        handle: str,
        channel_name: str = "",
    ) -> bool:
        """Apply Tier-1/2 Clickable Channel Fallback in YouTube Studio video edit page.

        1. Prepends clickable @<Handle> callout to Description:
           - English: 👉 Tap @<Handle> to watch the full-length video: "<Target Long Title>"!
           - Vietnamese: 👉 Bấm ngay vào tên kênh @<Handle> để vào kênh xem trọn vẹn video bản dài: "<Target Long Title>" nhé!
        2. Keeps updated_title = title.strip()[:55] (never inflates with @<Handle>).
        3. Saves changes via Studio #save button and waits for persistence.
        """
        clean_handle = handle.strip()
        if not clean_handle.startswith("@"):
            clean_handle = f"@{clean_handle}"

        # Detect if channel/text is English
        ch_meta = f"{channel_name} {self.profile_cfg.get('name', '')} {self.profile_cfg.get('channel_id', '')} {self.profile_cfg.get('slug', '')} {self.profile_cfg.get('id', '')}".lower()
        vn_pattern = r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]"
        has_vn = bool(re.search(vn_pattern, f"{target_title} {channel_name}".lower()))
        is_en = (
            any(marker in ch_meta for marker in ("en_", "en-", "english", "lazy_brain", "wallet_anatomy"))
            or clean_handle.lower().startswith(("@en_", "@en-", "en_", "en-"))
            or not has_vn
        )

        if is_en:
            callout = f'👉 Tap {clean_handle} to watch the full-length video: "{target_title}"!'
        else:
            callout = f'👉 Bấm ngay vào tên kênh {clean_handle} để vào kênh xem trọn vẹn video bản dài: "{target_title}" nhé!'

        logger.info("Applying clickable handle fallback (is_en=%s) for %s with callout: '%s'", is_en, clean_handle, callout)

        # 1. Update Description
        desc_res = await self.evaluate(f"""
            (() => {{
                const descEl = document.querySelector('#description-textarea #textbox') ||
                               document.querySelector('ytcp-mention-textbox#description-textarea #textbox') ||
                               document.querySelector('#description-container #textbox');
                if (!descEl) return {{ ok: false, error: 'no_desc_el' }};

                const callout = {json.dumps(callout)};
                let desc = descEl.innerText || '';

                if (desc.startsWith(callout)) {{
                    return {{ ok: true, changed: false, desc: desc.substring(0, 100) }};
                }}

                let newDesc = '';
                if (desc.startsWith('👉 Bấm ngay vào tên kênh') || desc.startsWith('👉 Tap ')) {{
                    const lines = desc.split('\\n');
                    lines[0] = callout;
                    newDesc = lines.join('\\n');
                }} else {{
                    newDesc = desc.trim() ? (callout + '\\n\\n' + desc.trim()) : callout;
                }}

                descEl.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, newDesc);
                descEl.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                descEl.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                return {{ ok: true, changed: true, desc: newDesc.substring(0, 100) }};
            }})()
        """)
        logger.info("Description fallback update result: %s", desc_res)

        # 2. Update Title: keep updated_title = title.strip()[:55] (never append @Handle)
        title_res = await self.evaluate("""
            (() => {
                const titleEl = document.querySelector('#title-textarea #textbox') ||
                                document.querySelector('ytcp-mention-textbox#title-textarea #textbox');
                if (!titleEl) return { ok: false, error: 'no_title_el' };

                let title = (titleEl.innerText || '').trim();
                const updated_title = title.substring(0, 55).trim();
                if (title === updated_title) {
                    return { ok: true, changed: false, title: title };
                }

                titleEl.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, updated_title);
                titleEl.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                titleEl.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                return { ok: true, changed: true, title: updated_title };
            })()
        """)
        logger.info("Title fallback update result: %s", title_res)

        # 3. Click Save button and wait for persistence
        saved = False
        for i in range(12):
            await asyncio.sleep(0.5)
            save_info = await self.evaluate("""
                (() => {
                    const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                    if (!saveBtn) return { found: false };
                    const isAriaDisabled = saveBtn.getAttribute('aria-disabled') === 'true';
                    const inner = saveBtn.querySelector('button') || saveBtn;
                    if (!isAriaDisabled && !inner.disabled) {
                        inner.click();
                        return { found: true, clicked: true };
                    }
                    return { found: true, clicked: false, ariaDisabled: isAriaDisabled };
                })()
            """)
            if save_info and save_info.get("clicked"):
                logger.info("Save button clicked after applying fallback (%.1fs).", (i + 1) * 0.5)
                saved = True
                break

        if not saved:
            if desc_res and not desc_res.get("changed") and title_res and not title_res.get("changed"):
                logger.info("Fallback was already applied previously and form is clean.")
                return True
            logger.warning("Could not click save button after applying fallback.")
            return False

        # Wait for Save RPC to complete
        for j in range(15):
            await asyncio.sleep(1.0)
            st = await self.evaluate("""
                (() => {
                    const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                    return saveBtn ? saveBtn.getAttribute('aria-disabled') : null;
                })()
            """)
            if st == "true":
                logger.info("Save RPC completed and persisted after %ds.", j + 1)
                break
        await asyncio.sleep(2.0)
        return True

    async def link_related_video(self, related_url_or_id: str, target_title: Optional[str] = None) -> bool:
        """For Shorts: Link related video in the Studio dialog or video edit page."""
        if not related_url_or_id:
            return False
        raw_target = related_url_or_id.strip()
        vid_id = raw_target.rstrip("/").split("/")[-1].split("?")[0]
        logger.info("Attempting to configure related video: %s (vid_id=%s, target_title=%s)", raw_target, vid_id, target_title)
        # Search for related video trigger in upload dialog or video details page
        res = await self.evaluate("""
            (() => {
                const selectors = [
                    'ytcp-video-metadata-editor-advanced #related-video-picker',
                    'ytcp-video-metadata-editor-sidepanel #related-video',
                    '#linked-video-editor-link',
                    'ytcp-shorts-content-links-picker',
                    'ytcp-linked-video-editor',
                    'ytcp-video-elements-dialog #related-video-button'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        el.scrollIntoView({ behavior: 'instant', block: 'center' });
                        const btn = el.querySelector('.container, ytcp-button, button, #trigger, .edit-button') || el;
                        btn.click();
                        return true;
                    }
                }
                const fallbackBtn = Array.from(document.querySelectorAll('ytcp-button, button, div[role="button"], ytcp-form-select')).find(b => {
                    const txt = (b.innerText || b.getAttribute('aria-label') || '').toLowerCase();
                    return txt.includes('video liên quan') || txt.includes('related video');
                });
                if (fallbackBtn) {
                    fallbackBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
                    fallbackBtn.click();
                    return true;
                }
                return false;
            })()
        """)
        if res:
            await asyncio.sleep(2.5)
            # Check if trust tiers dialog appeared
            diag = await self.check_trust_tiers_dialog()
            if diag.get("detected"):
                logger.warning("Detected Tier 3 verification dialog during upload wizard. Dismissing dialog...")
                await self.dismiss_trust_tiers_dialog()
                return False
            # Try typing into search input inside ytcp-entity-picker-dialog / ytcp-video-pick-dialog if present
            await self.evaluate(f"""
                (() => {{
                    const q = {json.dumps(vid_id)};
                    const dialog = document.querySelector('ytcp-entity-picker-dialog, ytcp-video-pick-dialog');
                    if (!dialog) return;
                    const input = dialog.querySelector('input');
                    if (input) {{
                        input.focus();
                        input.value = q;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }})()
            """)
            await asyncio.sleep(2.0)
            picked = await self.evaluate(f"""
                (() => {{
                    const q_id = {json.dumps(vid_id)};
                    const q_title = {json.dumps((target_title or "").lower())};
                    const full = {json.dumps(raw_target)};
                    const items = Array.from(document.querySelectorAll(
                        'ytcp-video-pick-dialog ytcp-entity-card, ytcp-entity-card, ytcp-entity-picker-dialog ytcp-entity-picker-item, ytcp-video-pick-dialog ytcp-video-row'
                    ));
                    let match = items.find(it => {{
                        const html = it.innerHTML || '';
                        const txt = (it.innerText || '').toLowerCase();
                        const aria = (it.getAttribute('aria-label') || '').toLowerCase();
                        return (q_id && html.includes(q_id)) ||
                               (q_title && (txt.includes(q_title) || aria.includes(q_title))) ||
                               (full.length > 5 && txt.includes(full.substring(0, 15).toLowerCase()));
                    }});
                    if (!match && items.length > 0) {{
                        // Pick the first non-Short (16:9 Long) video on the channel if ID isn't in innerHTML
                        match = items.find(it => !((it.innerText || '').toLowerCase().includes('#shorts'))) || items[0];
                    }}
                    if (match) {{
                        match.click();
                        return true;
                    }}
                    return false;
                }})()
            """)
            if picked:
                await asyncio.sleep(1.5)
                logger.info("Linked related video successfully (%s).", vid_id)
                return True
        logger.info("Related video picker not visible at current step.")
        return False

    async def link_related_video_post_publish(
        self,
        short_url_or_id: str,
        related_url_or_id: str,
        target_title: Optional[str] = None,
        handle: Optional[str] = None,
    ) -> dict[str, Any]:
        """Navigate to Studio video edit page for the Short and attach Related video + Save.

        If YouTube Tier 3 verification (yt-trust-tiers-wizard-dialog) is required, cleanly dismisses
        the dialog and applies Tier-1/2 Clickable Channel Fallback with @Handle callout in Description & Title.
        """
        if not short_url_or_id or not related_url_or_id:
            return {
                "linked_via_cdp": False,
                "tier3_verification_required": False,
                "clickable_handle_fallback_applied": False,
                "handle": None,
            }
        short_id = short_url_or_id.strip().rstrip("/").split("/")[-1].split("?")[0]
        raw_target = related_url_or_id.strip()
        vid_id = raw_target.rstrip("/").split("/")[-1].split("?")[0]

        resolved_handle = handle or self.resolve_channel_handle(short_id) or ""
        if resolved_handle and not resolved_handle.startswith("@"):
            resolved_handle = f"@{resolved_handle}"

        if not target_title:
            target_title = fetch_youtube_title(vid_id)

        edit_url = f"https://studio.youtube.com/video/{short_id}/edit"
        logger.info(
            "Navigating to Short edit page for Related Video binding: %s (target=%s, title=%s, handle=%s)",
            edit_url,
            vid_id,
            target_title,
            resolved_handle,
        )
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(4.0)

        # 1. Dismiss interstitial if present
        for _ in range(4):
            d = await self.dismiss_studio_interstitials()
            if d:
                logger.info("Dismissed Studio interstitial banner.")
                await asyncio.sleep(4.0)
                break
            await asyncio.sleep(1.0)

        # Wait up to 15s for the edit page / picker to load
        for _ in range(15):
            has_editor = await self.evaluate("""
                Boolean(document.querySelector('#linked-video-editor-link, ytcp-shorts-content-links-picker, #description-textarea'))
            """)
            if has_editor:
                break
            # Also check if banner reappeared
            await self.dismiss_studio_interstitials()
            await asyncio.sleep(1.0)

        # 2. Check if already correctly linked AND verified live on YouTube
        current_linked = await self.evaluate("""
            (() => {
                const el = document.querySelector('#linked-video-editor-link .dropdown-trigger-text');
                return el ? el.innerText.trim() : null;
            })()
        """)
        logger.info("Current linked title in Studio for %s: '%s'", short_id, current_linked)

        live_check = verify_short_live(short_id)
        is_live = live_check.get("has_pill", False)
        logger.info("Current live check for %s: has_pill=%s", short_id, is_live)

        if current_linked and current_linked not in ('Không có', 'None', ''):
            matches_target = False
            if target_title and (
                target_title.lower() in current_linked.lower()
                or current_linked.lower() in target_title.lower()
            ):
                matches_target = True
            elif vid_id and vid_id in current_linked:
                matches_target = True

            if matches_target and is_live:
                logger.info(
                    "Short %s is already correctly linked to '%s' and verified live on YouTube.",
                    short_id,
                    current_linked,
                )
                return {
                    "linked_via_cdp": True,
                    "tier3_verification_required": False,
                    "clickable_handle_fallback_applied": False,
                    "handle": resolved_handle,
                }

            # If it matches in Studio but is NOT live, or if it does not match target:
            # Clear existing link so Studio marks the form dirty and allows picking & re-saving
            reason = "not live on YouTube" if matches_target else "does not match target"
            logger.info("Existing link '%s' (%s). Clearing to re-link...", current_linked, reason)
            await self.evaluate("""
                (() => {
                    const clearBtn = document.querySelector(
                        '#linked-video-editor-link #right-icon, ytcp-shorts-content-links-picker #right-icon'
                    );
                    if (clearBtn) clearBtn.click();
                })()
            """)
            await asyncio.sleep(2.0)

        # 3. Open picker & monitor for Tier 3 verification modal
        opened = False
        tier3_detected = False

        # Pre-check if trust tiers dialog is already open
        initial_diag = await self.check_trust_tiers_dialog()
        if initial_diag.get("detected"):
            logger.warning(
                "Tier 3 verification dialog already visible upon loading edit page: %s",
                initial_diag.get("text", "")[:100],
            )
            tier3_detected = True

        if not tier3_detected:
            for attempt in range(5):
                await self.evaluate("""
                    (() => {
                        const el = document.querySelector('#linked-video-editor-link, ytcp-shorts-content-links-picker');
                        if (el) {
                            el.scrollIntoView({ behavior: 'instant', block: 'center' });
                            const btn = el.querySelector('.container, #trigger, button') || el;
                            btn.click();
                        }
                    })()
                """)
                await asyncio.sleep(2.0)

                # Check if trust tiers dialog appeared
                diag = await self.check_trust_tiers_dialog()
                if diag.get("detected"):
                    logger.warning(
                        "Detected YouTube Tier 3 verification dialog on attempt %d: '%s'",
                        attempt + 1,
                        diag.get("text", "")[:100],
                    )
                    tier3_detected = True
                    break

                card_count = await self.evaluate("""
                    document.querySelectorAll(
                        'ytcp-video-pick-dialog ytcp-entity-card, ytcp-entity-card, ' +
                        'ytcp-entity-picker-dialog ytcp-entity-picker-item, ytcp-video-pick-dialog ytcp-video-row'
                    ).length
                """)
                if card_count > 0:
                    opened = True
                    logger.info("Picker open with %d cards on attempt %d.", card_count, attempt + 1)
                    break

        if not opened and not tier3_detected:
            # Final check for dialog
            diag = await self.check_trust_tiers_dialog()
            if diag.get("detected"):
                tier3_detected = True

        if tier3_detected:
            logger.info("Dismissing Tier 3 verification dialog cleanly...")
            await self.dismiss_trust_tiers_dialog()
            logger.info("Applying Tier-1/2 Clickable Channel Fallback (%s) on Short edit page...", resolved_handle)
            applied = await self.apply_clickable_handle_fallback(
                target_title=target_title or "Video chính trên kênh",
                handle=resolved_handle,
            )
            return {
                "linked_via_cdp": False,
                "tier3_verification_required": True,
                "clickable_handle_fallback_applied": applied,
                "handle": resolved_handle,
            }

        if not opened:
            logger.warning("Failed to open related video picker dialog for Short %s.", short_id)
            return {
                "linked_via_cdp": False,
                "tier3_verification_required": False,
                "clickable_handle_fallback_applied": False,
                "handle": resolved_handle,
            }

        # 4. Pick matching card (robust matching for 1 or 2 Long videos on channel)
        picked = await self.evaluate(f"""
            (() => {{
                const cards = Array.from(document.querySelectorAll(
                    'ytcp-video-pick-dialog ytcp-entity-card, ytcp-entity-card, ' +
                    'ytcp-entity-picker-dialog ytcp-entity-picker-item, ytcp-video-pick-dialog ytcp-video-row'
                ));
                if (cards.length === 0) return {{ ok: false, error: 'no_cards' }};

                const q_id = {json.dumps(vid_id)};
                const current_short = {json.dumps(short_id)};
                const q_title = {json.dumps((target_title or "").lower().strip())};
                const title_prefix = q_title ? q_title.split(/[:,-]/)[0].trim() : '';

                // Exclude the Short video itself from selection candidates
                const candidate_cards = cards.filter(c => {{
                    const html = c.innerHTML || '';
                    const txt = (c.innerText || '').toLowerCase();
                    if (current_short && (html.includes(current_short) || txt.includes(current_short))) {{
                        return false;
                    }}
                    return true;
                }});

                const pool = candidate_cards.length > 0 ? candidate_cards : cards;

                // Priority 1: Match by exact video ID in HTML (thumbnail src or link) or aria-label
                let match = null;
                if (q_id) {{
                    match = pool.find(c => {{
                        const html = c.innerHTML || '';
                        const aria = (c.getAttribute('aria-label') || '');
                        return html.includes(q_id) || aria.includes(q_id);
                    }});
                }}

                // Priority 2: Match by exact target title
                if (!match && q_title) {{
                    match = pool.find(c => {{
                        const txt = (c.innerText || '').toLowerCase();
                        const aria = (c.getAttribute('aria-label') || '').toLowerCase();
                        return txt.includes(q_title) || aria.includes(q_title) || q_title.includes(txt.trim());
                    }});
                }}

                // Priority 3: Match by title prefix (first segment before colon)
                if (!match && title_prefix && title_prefix.length >= 6) {{
                    match = pool.find(c => {{
                        const txt = (c.innerText || '').toLowerCase();
                        const aria = (c.getAttribute('aria-label') || '').toLowerCase();
                        return txt.includes(title_prefix) || aria.includes(title_prefix);
                    }});
                }}

                // Priority 4 (Channel with 1 or 2 Long videos):
                // Filter out any other Short videos (marked #shorts) and pick the matching Long video
                if (!match) {{
                    match = pool.find(c => {{
                        const txt = (c.innerText || '').toLowerCase();
                        return !txt.includes('#shorts') && !txt.includes('/shorts/');
                    }}) || pool[0];
                }}

                if (match) {{
                    match.click();
                    return {{
                        ok: true,
                        text: (match.innerText || '').trim().replace(/\\s+/g, ' ').substring(0, 100)
                    }};
                }}
                return {{ ok: false }};
            }})()
        """)
        logger.info("Picked card result: %s", picked)
        await asyncio.sleep(2.0)

        # 5. Wait for save button enabled and click
        saved = False
        for i in range(12):
            await asyncio.sleep(0.5)
            save_info = await self.evaluate("""
                (() => {
                    const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                    if (!saveBtn) return { found: false };
                    const isAriaDisabled = saveBtn.getAttribute('aria-disabled') === 'true';
                    const inner = saveBtn.querySelector('button') || saveBtn;
                    if (!isAriaDisabled && !inner.disabled) {
                        inner.click();
                        return { found: true, clicked: true };
                    }
                    return { found: true, clicked: false, ariaDisabled: isAriaDisabled };
                })()
            """)
            if save_info and save_info.get("clicked"):
                logger.info("Save button clicked after %.1fs.", (i + 1) * 0.5)
                saved = True
                break

        if saved:
            for j in range(15):
                await asyncio.sleep(1.0)
                st = await self.evaluate("""
                    (() => {
                        const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                        return saveBtn ? saveBtn.getAttribute('aria-disabled') : null;
                    })()
                """)
                if st == "true":
                    logger.info("Save RPC completed and persisted after %ds.", j + 1)
                    break
            await asyncio.sleep(2.0)
            return {
                "linked_via_cdp": True,
                "tier3_verification_required": False,
                "clickable_handle_fallback_applied": False,
                "handle": resolved_handle,
            }

        logger.warning("Could not click save button or save was not enabled.")
        return {
            "linked_via_cdp": False,
            "tier3_verification_required": False,
            "clickable_handle_fallback_applied": False,
            "handle": resolved_handle,
        }

    async def update_video_thumbnail_post_publish(
        self,
        video_url_or_id: str,
        thumbnail_path: str | Path,
    ) -> dict[str, Any]:
        """Navigate to Studio video edit page, upload custom thumbnail, click #save, and persist."""
        path_str = str(Path(thumbnail_path).resolve())
        if not os.path.isfile(path_str):
            raise FileNotFoundError(f"Thumbnail not found: {path_str}")

        vid_id = video_url_or_id.strip().rstrip("/").split("/")[-1].split("?")[0]
        edit_url = f"https://studio.youtube.com/video/{vid_id}/edit"
        logger.info("Navigating to Video edit page for custom thumbnail update: %s", edit_url)
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(4.0)

        # 1. Dismiss interstitials
        for _ in range(4):
            d = await self.dismiss_studio_interstitials()
            if d:
                logger.info("Dismissed Studio interstitial banner.")
                await asyncio.sleep(3.0)
                break
            await asyncio.sleep(1.0)

        # Wait up to 15s for the editor page to load
        for _ in range(15):
            has_editor = await self.evaluate("""
                Boolean(document.querySelector('input#file-loader, ytcp-thumbnails-compact-editor, ytcp-video-thumbnail-editor, ytcp-video-metadata-editor'))
            """)
            if has_editor:
                break
            await self.dismiss_studio_interstitials()
            await asyncio.sleep(1.0)

        # 2. Upload thumbnail via upload_thumbnail (DOM.setFileInputFiles)
        uploaded = await self.upload_thumbnail(path_str)
        if not uploaded:
            logger.warning("Failed to attach custom thumbnail on edit page for %s", vid_id)
            return {"success": False, "video_id": vid_id, "error": "upload_failed"}

        # 3. Wait for save button to become enabled and click save
        saved = False
        for i in range(30):
            await asyncio.sleep(1.0)
            save_info = await self.evaluate("""
                (() => {
                    const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                    if (!saveBtn) return { found: false };
                    const isAriaDisabled = saveBtn.getAttribute('aria-disabled') === 'true';
                    const inner = saveBtn.querySelector('button') || saveBtn;
                    if (!isAriaDisabled && !inner.disabled) {
                        inner.click();
                        return { found: true, clicked: true };
                    }
                    return { found: true, clicked: false, ariaDisabled: isAriaDisabled };
                })()
            """)
            if save_info and save_info.get("clicked"):
                logger.info("Save button clicked after %ds.", i + 1)
                saved = True
                break
            if (i + 1) % 5 == 0:
                logger.info("Waiting for Save button to become enabled (%ds/30s)...", i + 1)

        if saved:
            for j in range(15):
                await asyncio.sleep(1.0)
                st = await self.evaluate("""
                    (() => {
                        const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                        return saveBtn ? saveBtn.getAttribute('aria-disabled') : null;
                    })()
                """)
                if st == "true":
                    logger.info("Thumbnail save RPC persisted after %ds.", j + 1)
                    break
            await asyncio.sleep(2.0)
            return {"success": True, "video_id": vid_id, "thumbnail_path": path_str}

        logger.warning("Could not click save button for thumbnail or save was not enabled.")
        return {"success": False, "video_id": vid_id, "error": "save_button_not_clicked"}

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

        # Wait for share confirmation dialog (and click 'Vẫn xuất bản' / 'Publish anyway' if checks warning modal appears)
        logger.info("Waiting for publication confirmation dialog...")
        confirmed_url = None
        for _ in range(25):
            await asyncio.sleep(1.0)
            # Check if YouTube popped up 'Chúng tôi vẫn đang kiểm tra nội dung của bạn' -> click 'Vẫn xuất bản' / 'Publish anyway'
            clicked_publish_anyway = await self.evaluate("""
                (() => {
                    const dialogs = Array.from(document.querySelectorAll('ytcp-confirmation-dialog, tp-yt-paper-dialog, ytcp-dialog'));
                    for (const dlg of dialogs) {
                        if (dlg.offsetParent === null) continue;
                        const btns = Array.from(dlg.querySelectorAll('ytcp-button, button, #secondary-action-button, #confirm-button'));
                        for (const b of btns) {
                            const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                            if (txt === 'vẫn xuất bản' || txt === 'publish anyway') {
                                b.click();
                                const inner = b.querySelector('button');
                                if (inner) inner.click();
                                return txt;
                            }
                        }
                    }
                    return null;
                })()
            """)
            if clicked_publish_anyway:
                logger.info("Clicked warning confirmation dialog button: %s", clicked_publish_anyway)
                await asyncio.sleep(2.0)

            confirmed = await self.evaluate("""
                (() => {
                    const shareDialog = document.querySelector('ytcp-video-share-dialog');
                    if (!shareDialog || shareDialog.offsetParent === null) return { found: false };
                    const link = shareDialog.querySelector('a')?.href || null;
                    const title = shareDialog.querySelector('#dialog-title')?.innerText?.trim() || null;
                    return { found: true, link, title };
                })()
            """)
            if confirmed and confirmed.get("found") and confirmed.get("link"):
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
    headless: bool = True,
    job_id: Optional[str] = None,
    bypass_review_gate: bool = False,
) -> dict[str, Any]:
    """Execute end-to-end publish flow for a single video."""
    # Mandatory Video Review & Approval Gate
    effective_job_id = job_id
    if not effective_job_id and video_path:
        p = Path(video_path)
        if p.parent.name and p.parent.name not in ("video", "runs", "sys", "Desktop", ""):
            effective_job_id = p.parent.name
        else:
            effective_job_id = p.stem

    if not bypass_review_gate and effective_job_id:
        allowed, reason = check_publish_permission(effective_job_id)
        if not allowed:
            raise RuntimeError(
                f"PUBLISH_BLOCKED_BY_REVIEW_GATE: Job '{effective_job_id}' is not APPROVED (status={reason}). "
                "Please approve in the Review Dashboard first."
            )

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
        yt_chid = profile_cfg.get("youtube_channel_id") or profile_cfg.get("channel_id")
        target_studio_url = f"https://studio.youtube.com/channel/{yt_chid}" if yt_chid and str(yt_chid).startswith("UC") else "https://studio.youtube.com"
        if "studio.youtube.com" not in curr_url or (yt_chid and str(yt_chid).startswith("UC") and str(yt_chid) not in curr_url):
            logger.info("Navigating to %s...", target_studio_url)
            await client.call("Page.navigate", {"url": target_studio_url})
            await asyncio.sleep(6.0)

        await client.dismiss_studio_interstitials()
        await asyncio.sleep(2.0)

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

        # Step 6: Custom Thumbnail (Long 16:9) or Related Video (Short 9:16)
        thumbnail_status = False
        if thumbnail_path and not is_short:
            thumbnail_status = await client.upload_thumbnail(thumbnail_path)

        # Step 6b: Subtitles (.srt) handling if provided and exists
        subtitles_status = False
        if subtitles_path:
            sub_file = Path(subtitles_path).resolve()
            if sub_file.is_file():
                logger.info("Handling subtitles attachment from %s (%d bytes)...", sub_file, sub_file.stat().st_size)
                if hasattr(client, "attach_subtitles"):
                    try:
                        subtitles_status = await client.attach_subtitles(sub_file)
                    except Exception as sub_err:
                        logger.warning("Could not attach subtitles via CDP (continuing publish): %s", sub_err)
            else:
                logger.warning("Subtitles path provided but file not found: %s", subtitles_path)

        related_linked = False
        if is_short and related_video_url:
            related_linked = await client.link_related_video(related_video_url)

        # Step 7: Advance through wizard to Step 4 (Visibility)
        await client.advance_to_visibility_step()

        # Step 8: Set Visibility to PUBLIC
        await client.set_visibility(visibility)

        # Step 9: Wait for upload completion
        await client.wait_for_upload_complete()

        # Step 10: Finalize Publication & QA Screenshot
        final_url = await client.publish_and_finish(screenshot_path=screenshot_path)
        resolved_url = final_url or dialog_video_url

        if visibility.upper() == "PUBLIC":
            if not resolved_url:
                raise RuntimeError(
                    "PUBLIC_VERIFICATION_FAILED: No video URL resolved from YouTube Studio dialog."
                )
            if resolved_url and Path(video_path).exists():
                vid_id = resolved_url.strip().rstrip("/").split("/")[-1].split("?")[0]
                oembed_ok = False
                if vid_id:
                    oembed_endpoint = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json"
                    for attempt in range(1, 8):
                        await asyncio.sleep(2.5)
                        try:
                            req = urllib.request.Request(
                                oembed_endpoint,
                                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/136.0.0.0"},
                            )
                            with urllib.request.urlopen(req, timeout=8) as resp:
                                if resp.status == 200:
                                    oembed_ok = True
                                    logger.info("Verified live PUBLIC oEmbed HTTP 200 for %s on attempt %d", vid_id, attempt)
                                    break
                        except Exception as exc:
                            logger.warning("oEmbed PUBLIC check attempt %d/7 for %s not yet 200: %s", attempt, vid_id, exc)
                if not oembed_ok:
                    raise RuntimeError(
                        f"PUBLIC_VERIFICATION_FAILED: Video '{resolved_url}' did not return HTTP 200 on public oEmbed! "
                        "It is still Private/Draft in YouTube Studio."
                    )

        live_status: dict[str, Any] = {}
        if is_short and related_video_url and resolved_url:
            # YouTube takes 2-4 seconds after publish to expose the short page
            await asyncio.sleep(3.0)
            live_status = verify_short_live(resolved_url)
            logger.info("Post-publish Short live check for %s: has_pill=%s", resolved_url, live_status.get("has_pill"))

            # If has_pill is False (even if related_linked was True during wizard),
            # run link_related_video_post_publish up to 2 times until verified
            if not live_status.get("has_pill"):
                logger.warning(
                    "Short %s missing Related Video pill live (wizard selection dropped). "
                    "Running link_related_video_post_publish repair loop (max 2 attempts)...",
                    resolved_url,
                )
                for attempt in range(1, 3):
                    logger.info("Attempt %d/2 to link related video post-publish for %s", attempt, resolved_url)
                    post_res = await client.link_related_video_post_publish(
                        resolved_url,
                        related_video_url,
                        target_title=title,
                        handle=profile_cfg.get("handle") if profile_cfg else None,
                    )
                    post_ok = post_res.get("linked_via_cdp", False)
                    if post_res.get("tier3_verification_required"):
                        logger.warning(
                            "Channel requires Tier 3 verification; applied clickable handle fallback (%s).",
                            post_res.get("handle"),
                        )
                        break
                    await asyncio.sleep(3.0)
                    live_status = verify_short_live(resolved_url)
                    if live_status.get("has_pill"):
                        logger.info(
                            "Confirmed Related Video pill live on attempt %d: '%s'",
                            attempt,
                            live_status.get("linked_title"),
                        )
                        related_linked = True
                        break
                    else:
                        logger.warning(
                            "Attempt %d finished (cdp_saved=%s), but live has_pill still False.",
                            attempt,
                            post_ok,
                        )
            else:
                related_linked = True

        if effective_job_id and resolved_url:
            try:
                set_review_decision(effective_job_id, "PUBLISHED", published_url=resolved_url)
                logger.info("Updated review queue for %s to PUBLISHED (%s)", effective_job_id, resolved_url)
            except Exception as e:
                logger.warning("Could not update review queue status for %s: %s", effective_job_id, e)

        return {
            "status": "PUBLISHED",
            "channel_name": channel_info.get("channelName", "Sticker Vocabulary"),
            "channel_id": channel_info.get("channelId"),
            "video_url": resolved_url,
            "title": title,
            "visibility": visibility,
            "thumbnail_uploaded": thumbnail_status,
            "subtitles_path": str(subtitles_path) if subtitles_path else None,
            "subtitles_uploaded": bool(subtitles_status),
            "related_video_linked": bool(related_linked),
            "live_verified": bool(live_status.get("has_pill", False)),
            "live_title": live_status.get("linked_title"),
            "screenshot_path": str(screenshot_path) if screenshot_path else None,
        }
    finally:
        await client.close()
        client.terminate_browser()


publish_to_youtube_studio = publish_single_video


def parse_metadata_file(md_path: str | Path) -> dict[str, str]:
    """Parse title, description, and tags from markdown publication kit."""
    text = Path(md_path).read_text(encoding="utf-8")
    title = ""
    description = ""
    tags = ""

    # Title extraction
    m_title = re.search(r"## 1\. (?:Tiêu đề|Title)[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
    if not m_title:
        m_title = re.search(r"## 1\. (?:Tiêu đề|Title)[^\n]*\n([^\n#]+)", text)
    if m_title:
        title = m_title.group(1).strip()

    # Description extraction
    m_desc = re.search(r"## 2\. (?:Mô tả|Description)[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
    if not m_desc:
        m_desc = re.search(r"## 2\. (?:Mô tả|Description)[^\n]*\n([^\n#]+)", text)
    if m_desc:
        description = m_desc.group(1).strip()

    # Tags extraction
    m_tags = re.search(r"## 3\.\s*(?:Thẻ từ khóa|Tags)[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
    if not m_tags:
        m_tags = re.search(r"## 3\.\s*(?:Thẻ từ khóa|Tags)[^\n]*\n([^\n#]+)", text)
    if m_tags:
        tags = m_tags.group(1).strip()

    return {"title": title, "description": description, "tags": tags}


def main():
    parser = argparse.ArgumentParser(description="Automated YouTube CDP Publisher for Video Pilot")
    parser.add_argument("--video", "--video-file", dest="video", required=False, help="Path to MP4 video file")
    parser.add_argument("--channel", help="Channel ID (e.g., co_the_ke, ai_binh_dan) to resolve profile")
    parser.add_argument("--job-id", help="Job ID")
    parser.add_argument("--profile", help="Explicit Chrome profile ID (e.g. profile_1)")
    parser.add_argument("--cdp-port", type=int, help="CDP port override")
    parser.add_argument("--title", help="Video title (overrides metadata file)")
    parser.add_argument("--description", help="Video description (overrides metadata file)")
    parser.add_argument("--metadata", help="Path to markdown metadata file (youtube_long.md / youtube_shorts.md)")
    parser.add_argument("--thumbnail", help="Path to thumbnail image file (for 16:9)")
    parser.add_argument("--update-thumbnail", help="Retroactively upload thumbnail to an existing video (requires --video-url or --video-id and --channel)")
    parser.add_argument("--video-url", help="Existing video URL")
    parser.add_argument("--video-id", help="Existing video ID")
    parser.add_argument("--subtitles", help="Path to subtitles SRT file")
    parser.add_argument("--visibility", "--privacy", dest="visibility", default="PUBLIC", choices=["PUBLIC", "UNLISTED", "PRIVATE"])
    parser.add_argument("--short", action="store_true", help="Mark as Short (9:16)")
    parser.add_argument("--related-video", help="Related video URL or ID (for Shorts)")
    parser.add_argument("--screenshot", help="Output path for verification screenshot")
    parser.add_argument("--headless", action="store_true", default=True, help="Run Chrome in headless mode (default True)")
    parser.add_argument("--no-headless", "--headed", dest="headless", action="store_false", help="Run Chrome with GUI")
    parser.add_argument("--bypass-review-gate", action="store_true", help="Bypass mandatory review approval gate")

    args = parser.parse_args()

    title = args.title
    description = args.description

    if args.metadata:
        meta = parse_metadata_file(args.metadata)
        if not title:
            title = meta.get("title")
        if not description:
            description = meta.get("description")

    if not title and not args.update_thumbnail:
        parser.error("Title must be specified via --title or --metadata")
    if not args.update_thumbnail and not args.video:
        parser.error("--video is required when publishing a video")
    if not description:
        description = ""

    # Check Review Gate before launching upload process
    job_id = args.job_id
    if not job_id and args.video:
        p = Path(args.video)
        if p.parent.name and p.parent.name not in ("video", "runs", "sys", "Desktop", ""):
            job_id = p.parent.name
        else:
            job_id = p.stem

    if not args.bypass_review_gate and job_id and not args.update_thumbnail:
        allowed, reason = check_publish_permission(job_id)
        if not allowed:
            raise RuntimeError(
                f"PUBLISH_BLOCKED_BY_REVIEW_GATE: Job '{job_id}' is not APPROVED (status={reason}). "
                "Please approve in the Review Dashboard first."
            )

    profile_cfg = None
    map_file = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
    if args.channel and map_file.exists():
        ch_map = json.loads(map_file.read_text(encoding="utf-8"))
        ch_key = args.channel if args.channel in ch_map.get("channels", {}) else args.channel.replace("-", "_")
        if ch_key in ch_map.get("channels", {}):
            entry = ch_map["channels"][ch_key]
            profile_cfg = {
                "id": entry["profile_id"],
                "port": args.cdp_port or entry["cdp_port"],
                "directory": entry["directory"],
                "user_data_dir": entry["user_data_dir"],
                "email": entry["email"],
                "handle": entry.get("handle"),
                "youtube_channel_id": entry.get("youtube_channel_id"),
            }
    elif args.profile:
        flow_profiles_file = Path.home() / ".config/video-pilot/flow/profiles.json"
        if flow_profiles_file.exists():
            data = json.loads(flow_profiles_file.read_text(encoding="utf-8"))
            for p in data.get("profiles", []):
                if p["id"] == args.profile:
                    profile_cfg = p
                    if args.cdp_port:
                        profile_cfg["port"] = args.cdp_port
                    break

    if args.update_thumbnail:
        target_video = args.video_url or args.video_id
        if not target_video:
            parser.error("--update-thumbnail requires --video-url or --video-id")
        if not profile_cfg:
            parser.error("--update-thumbnail requires a valid --channel or --profile")

        async def _run_update():
            c = YouTubeCDPClient(profile_cfg, headless=args.headless)
            try:
                await c.connect()
                res = await c.update_video_thumbnail_post_publish(target_video, args.update_thumbnail)
                return res
            finally:
                await c.close()

        update_res = asyncio.run(_run_update())
        print(json.dumps(update_res, indent=2))
        sys.exit(0 if update_res.get("success") else 1)

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
            job_id=job_id,
            bypass_review_gate=args.bypass_review_gate,
        )
    )

    if args.channel and result.get("video_url") and map_file.exists():
        try:
            import fcntl
            lock_path = map_file.with_suffix(".lock")
            with open(lock_path, "w", encoding="utf-8") as lock_fh:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
                try:
                    ch_map = json.loads(map_file.read_text(encoding="utf-8"))
                    ch_key = args.channel if args.channel in ch_map.get("channels", {}) else args.channel.replace("-", "_")
                    if ch_key in ch_map.get("channels", {}):
                        entry = ch_map["channels"][ch_key]
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
                finally:
                    fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.warning("Failed to update youtube_channel_map.json: %s", e)

    print("\n=== PUBLISH REPORT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
