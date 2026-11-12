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


def format_and_truncate_tags(tags: Optional[str | list[str]], max_chars: int = 480) -> list[str]:
    """Parse comma/newline separated tags and truncate cleanly under max_chars total length.

    YouTube imposes a strict 500-character cap on total tags. Keeping under 480 chars
    safely avoids any rejected input.
    """
    if not tags:
        return []
    if isinstance(tags, str):
        raw_list = re.split(r"[,\n]+", tags)
    else:
        raw_list = list(tags)

    cleaned: list[str] = []
    seen = set()
    for t in raw_list:
        clean_tag = str(t).strip().lstrip("#").strip()
        if clean_tag and clean_tag.lower() not in seen:
            seen.add(clean_tag.lower())
            cleaned.append(clean_tag)

    selected: list[str] = []
    curr_len = 0
    for tag in cleaned:
        cost = len(tag) + (1 if selected else 0)
        if curr_len + cost <= max_chars:
            selected.append(tag)
            curr_len += cost
        else:
            break
    return selected


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
        self._last_publish_accepted = False

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
                let channelId = m ? m[1] : null;

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
                if (!channelId && window.ytcfg && typeof window.ytcfg.get === 'function') {
                    channelId = window.ytcfg.get('CHANNEL_ID') || null;
                }
                return { title, url, channelId, channelName: name };
            })()
        """)
        curr_url = (info or {}).get("url", "")
        if "accounts.google.com/v3/signin" in curr_url or "confirmidentifier" in curr_url or "accounts.google.com" in curr_url:
            raise RuntimeError(f"GOOGLE_AUTH_REQUIRED: {curr_url}")
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
        tags: Optional[str | list[str]] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
    ) -> None:
        """Set title, description, audience settings, tags, language, and category."""
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

        # Expand 'Hiển thị thêm' / 'Show more' if tags, language, or category need to be set
        clean_tags = format_and_truncate_tags(tags, max_chars=480)
        if clean_tags or language or category:
            await self.evaluate("""
                (() => {
                    const tagBox = document.querySelector('#tags-container') || document.querySelector('input#text-input[aria-label*="Tags"]');
                    if (tagBox && tagBox.offsetParent !== null) return 'ALREADY_EXPANDED';
                    const toggleBtn = document.querySelector('ytcp-uploads-video-details #toggle-button') ||
                                      document.querySelector('#toggle-button') ||
                                      document.querySelector('ytcp-button#toggle-button') ||
                                      Array.from(document.querySelectorAll('ytcp-button, button')).find(b => {
                                          const txt = (b.innerText || '').toLowerCase();
                                          return txt.includes('hiển thị thêm') || txt.includes('show more');
                                      });
                    if (toggleBtn) {
                        toggleBtn.click();
                        return 'TOGGLED';
                    }
                    return null;
                })()
            """)
            await asyncio.sleep(1.0)

        # Tags handling
        if clean_tags:
            logger.info("Filling %d tags (total chars=%d)...", len(clean_tags), sum(len(t) for t in clean_tags) + max(0, len(clean_tags) - 1))
            tags_csv = ",".join(clean_tags) + ","
            tags_res = await self.evaluate(f"""
                (() => {{
                    const container = document.querySelector('#tags-container') ||
                                      document.querySelector('ytcp-form-input-container#tags-container') ||
                                      document.querySelector('ytcp-chip-bar');
                    if (!container) return {{ success: false, reason: 'no_tags_container' }};
                    container.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                    const input = container.querySelector('input#text-input') ||
                                  container.querySelector('input') ||
                                  document.querySelector('#tags-container input');
                    if (!input) return {{ success: false, reason: 'no_input' }};

                    input.focus();
                    document.execCommand('insertText', false, {json.dumps(tags_csv)});
                    input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    return {{ success: true }};
                }})()
            """)
            await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"})
            await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"})
            await asyncio.sleep(0.5)

            # Check chip count; if 0, fallback to inserting each tag individually with CDP Enter
            chip_count_res = await self.evaluate("""
                (() => {
                    const chips = document.querySelectorAll('#tags-container ytcp-chip');
                    return chips.length;
                })()
            """)
            chip_count = int(chip_count_res or 0)
            if chip_count == 0:
                logger.info("Tags CSV insertion produced 0 chips; falling back to individual tag insertion...")
                for tag in clean_tags:
                    await self.evaluate(f"""
                        (() => {{
                            const input = document.querySelector('#tags-container input#text-input') ||
                                          document.querySelector('#tags-container input');
                            if (!input) return;
                            input.focus();
                            document.execCommand('insertText', false, {json.dumps(tag)});
                            input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                        }})()
                    """)
                    await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"})
                    await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"})
                    await asyncio.sleep(0.1)

            final_chips = await self.evaluate("""
                (() => {
                    const chips = document.querySelectorAll('#tags-container ytcp-chip');
                    return chips.length;
                })()
            """) or 0
            logger.info("Tags filled result: %s, final chip count: %d", tags_res, final_chips)
            await asyncio.sleep(0.5)

        # Video Language
        if language:
            lang_candidates = [
                '#language-input',
                'ytcp-form-language-input',
                'ytcp-text-dropdown-select#language-input',
                '#language-and-close-captioning #language-input',
            ]
            await self._select_studio_dropdown_option(lang_candidates, language)

        # Category
        if category:
            cat_candidates = [
                '#category',
                'ytcp-video-metadata-category',
                'ytcp-text-dropdown-select#category',
                '#category-dropdown',
            ]
            await self._select_studio_dropdown_option(cat_candidates, category)

    async def _select_studio_dropdown_option(
        self,
        selector_candidates: list[str],
        target_value: str,
    ) -> bool:
        """Select an option in a YouTube Studio custom dropdown (e.g. Language, Category)."""
        if not target_value:
            return False

        logger.info("Selecting dropdown option for '%s'...", target_value)
        val_lower = target_value.strip().lower()
        synonyms = [val_lower]
        if "tiếng việt" in val_lower or "vietnamese" in val_lower:
            synonyms.extend(["tiếng việt", "vietnamese"])
        elif "giáo dục" in val_lower or "education" in val_lower:
            synonyms.extend(["giáo dục", "education"])
        elif "khoa học" in val_lower or "science" in val_lower or "công nghệ" in val_lower:
            synonyms.extend([
                "khoa học và công nghệ",
                "khoa học & công nghệ",
                "science & technology",
                "science and technology",
            ])
        elif "mọi người" in val_lower or "blog" in val_lower:
            synonyms.extend([
                "mọi người và blog",
                "mọi người & blog",
                "people & blogs",
                "people and blogs",
            ])

        try:
            clicked_trigger = await self.evaluate(f"""
                (() => {{
                    const candidates = {json.dumps(selector_candidates)};
                    let container = null;
                    for (const sel of candidates) {{
                        const el = document.querySelector(sel);
                        if (el && el.offsetParent !== null) {{
                            container = el;
                            break;
                        }}
                    }}
                    if (!container) return false;
                    container.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                    const trigger = container.querySelector('#trigger') ||
                                    container.querySelector('ytcp-dropdown-trigger') ||
                                    container.querySelector('.dropdown-trigger') ||
                                    container.querySelector('[role="button"]') ||
                                    container;
                    trigger.click();
                    return true;
                }})()
            """)
            if not clicked_trigger:
                logger.warning("Could not find dropdown container for %s from candidates %s", target_value, selector_candidates)
                return False

            await asyncio.sleep(0.8)

            selected = await self.evaluate(f"""
                (() => {{
                    const synonyms = {json.dumps(synonyms)};
                    const menus = Array.from(document.querySelectorAll(
                        'tp-yt-paper-listbox, ytcp-text-menu, tp-yt-iron-dropdown, ytcp-dropdown-select-item-list'
                    )).filter(m => m.offsetParent !== null && window.getComputedStyle(m).display !== 'none');

                    const items = [];
                    for (const m of menus) {{
                        items.push(...Array.from(m.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, [role="option"]')));
                    }}
                    if (items.length === 0) {{
                        items.push(...Array.from(document.querySelectorAll('tp-yt-paper-item, [role="option"]')).filter(el => el.offsetParent !== null));
                    }}

                    for (const item of items) {{
                        const text = (item.innerText || item.textContent || '').trim().toLowerCase();
                        for (const syn of synonyms) {{
                            if (text === syn || text.includes(syn)) {{
                                item.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                                item.click();
                                return {{ success: true, matched_text: text }};
                            }}
                        }}
                    }}
                    return {{ success: false, items_count: items.length }};
                }})()
            """)

            if selected and selected.get("success"):
                logger.info("Successfully selected '%s' in dropdown (matched: %s)", target_value, selected.get("matched_text"))
                await asyncio.sleep(0.5)
                return True
            else:
                logger.warning("Could not find matching option for '%s' in dropdown items: %s", target_value, selected)
                await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
                await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
                return False
        except Exception as e:
            logger.warning("Dropdown selection for '%s' encountered error: %s", target_value, e)
            return False

    async def upload_thumbnail(
        self,
        thumbnail_path: str | Path,
        strict_thumbnail: bool = False,
    ) -> bool:
        """Upload custom thumbnail if provided and supported."""
        path_str = str(Path(thumbnail_path).resolve())
        if not os.path.isfile(path_str):
            logger.warning("Thumbnail file does not exist: %s", path_str)
            if strict_thumbnail:
                raise RuntimeError(f"CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED: File not found: {path_str}")
            return False

        logger.info("Uploading custom thumbnail: %s (strict=%s)", path_str, strict_thumbnail)
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
            if strict_thumbnail:
                raise RuntimeError("CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED: Thumbnail file input not found")
            return False

        try:
            await self.call("DOM.setFileInputFiles", {
                "files": [path_str],
                "objectId": obj_id,
            })
            logger.info("Thumbnail attached successfully. Verifying preview...")
            await asyncio.sleep(2.5)

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
                if strict_thumbnail:
                    raise RuntimeError("CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED")
                return False

            # Verify custom thumbnail preview appeared
            thumb_ok = await self.evaluate("""
                (() => {
                    const uploader = document.querySelector('ytcp-thumbnail-uploader');
                    if (uploader) {
                        const img = uploader.querySelector('img[src]');
                        if (img && img.src && !img.src.includes('placeholder')) return true;
                    }
                    const customTile = document.querySelector('ytcp-thumbnails-compact-editor-uploader #still-1') ||
                                       document.querySelector('#still-1[selected]') ||
                                       document.querySelector('ytcp-thumbnail-area [selected]');
                    if (customTile) return true;
                    const selectedThumb = document.querySelector('ytcp-thumbnail[selected], ytcp-thumbnail-pill[selected]');
                    if (selectedThumb) return true;
                    return false;
                })()
            """)
            if thumb_ok:
                logger.info("Custom thumbnail preview verified successfully.")
                return True
            else:
                logger.warning("Custom thumbnail attached but preview not explicitly confirmed.")
                if strict_thumbnail:
                    raise RuntimeError("CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED")
                return True
        except Exception as e:
            if "CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED" in str(e):
                raise
            logger.warning("Thumbnail upload encountered exception: %s", e)
            if strict_thumbnail:
                raise RuntimeError(f"CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED: {e}") from e
            return False

    async def _close_captions_modal(self) -> None:
        """Safely close any open captions dialog so the main Upload Wizard is not blocked."""
        try:
            await self.evaluate("""
                (() => {
                    const dlgs = Array.from(document.querySelectorAll(
                        'ytve-captions-editor-modal, ytve-captions-editor-upload-dialog, ytcp-captions-upload-dialog, ytcp-timedtext-editor-dialog, tp-yt-paper-dialog, ytcp-dialog'
                    )).filter(d => {
                        if (d.matches('ytcp-uploads-dialog')) return false;
                        if (d.contains(document.querySelector('ytcp-uploads-video-details'))) return false;
                        if (d.offsetParent === null) return false;
                        return true;
                    });
                    if (dlgs.length > 0) {
                        const topDlg = dlgs[dlgs.length - 1];
                        const closeBtn = topDlg.querySelector('#close-button') ||
                                         topDlg.querySelector('#cancel-button') ||
                                         topDlg.querySelector('ytcp-button#close-button') ||
                                         topDlg.querySelector('ytcp-button#cancel-button') ||
                                         topDlg.querySelector('button[aria-label*="Đóng"]') ||
                                         topDlg.querySelector('button[aria-label*="Close"]');
                        if (closeBtn) closeBtn.click();
                    }
                })()
            """)
            await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
            await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
        except Exception:
            pass

    async def _upload_srt_inside_open_captions_modal(self, sub_path: Path) -> bool:
        """Upload SRT file inside open Studio captions editor modal (ytve-captions-editor-modal / dialog)."""
        logger.info("Executing SRT upload sequence inside captions modal from %s...", sub_path)
        try:
            # 1. Poll up to 8.0s for modal upload options or 3-dot #more-actions-menu to mount
            action_res = None
            for _ in range(16):
                await asyncio.sleep(0.5)
                action_res = await self.evaluate("""
                    (() => {
                        const findDirect = () => {
                            const items = Array.from(document.querySelectorAll(
                                'tp-yt-paper-item[test-id="upload"], tp-yt-paper-item, ytcp-button, button, [role="button"], [role="menuitem"]'
                            ));
                            return items.find(b => {
                                if (b.offsetParent === null) return false;
                                const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                return t.includes('tải tệp lên') || t.includes('upload file') || b.getAttribute('test-id') === 'upload';
                            });
                        };

                        let btn = findDirect();
                        if (btn) {
                            btn.click();
                            return { action: 'direct_upload_clicked' };
                        }

                        const moreBtn = document.querySelector('ytve-captions-editor-modal #more-actions-menu') ||
                                        document.querySelector('#more-actions-menu') ||
                                        document.querySelector('ytcp-icon-button#more-actions-menu') ||
                                        document.querySelector('ytve-captions-editor-modal ytcp-icon-button[icon*="more"]');
                        if (moreBtn && moreBtn.offsetParent !== null) {
                            moreBtn.click();
                            return { action: 'more_menu_clicked' };
                        }
                        return { action: 'none_found' };
                    })()
                """)
                if action_res and action_res.get("action") in ("direct_upload_clicked", "more_menu_clicked"):
                    break
            logger.info("Captions upload initial action: %s", action_res)

            if action_res and action_res.get("action") == "more_menu_clicked":
                await asyncio.sleep(1.0)
                # Click upload option from opened dropdown
                clicked_menu = await self.evaluate("""
                    (() => {
                        const items = Array.from(document.querySelectorAll(
                            'tp-yt-paper-item[test-id="upload"], tp-yt-paper-item, [role="menuitem"], ytcp-text-menu-item'
                        ));
                        const btn = items.find(b => {
                            if (b.offsetParent === null) return false;
                            const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                            return t.includes('tải tệp lên') || t.includes('upload file') || b.getAttribute('test-id') === 'upload';
                        });
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        return false;
                    })()
                """)
                logger.info("Clicked upload from more-actions menu: %s", clicked_menu)

            await asyncio.sleep(1.5)

            # 3. Handle upload dialog: select 'With timing' and click #confirm-button / Continue
            await self.evaluate("""
                (() => {
                    const dlg = document.querySelector('ytve-captions-editor-upload-dialog') ||
                                document.querySelector('ytcp-captions-upload-dialog') ||
                                document.querySelector('tp-yt-paper-dialog') ||
                                document;
                    const radios = Array.from(dlg.querySelectorAll('tp-yt-paper-radio-button, input[type="radio"]'));
                    const withTiming = radios.find(r => {
                        const t = (r.innerText || r.textContent || '').toLowerCase();
                        return t.includes('có thông tin thời gian') || t.includes('with timing') || r.getAttribute('name') === 'with-timing';
                    });
                    if (withTiming) withTiming.click();

                    const confirmBtn = dlg.querySelector('#confirm-button button') ||
                                       dlg.querySelector('#confirm-button') ||
                                       Array.from(dlg.querySelectorAll('ytcp-button, button')).find(b => {
                                           if (b.id === 'next-button') return false;
                                           const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                           return t === 'tiếp tục' || t === 'continue' || t.includes('tiếp tục');
                                       });
                    if (confirmBtn) confirmBtn.click();
                })()
            """)

            # 4. Critical: Poll up to 6s (every 0.3s) for input#captions-file-loader
            obj_id = None
            for _ in range(20):
                await asyncio.sleep(0.3)
                input_obj = await self.get_remote_object("""
                    (() => {
                        const loader = document.querySelector('#captions-file-loader') ||
                                       document.querySelector('input[type="file"]#captions-file-loader') ||
                                       document.querySelector('ytve-captions-editor-upload-dialog input[type="file"]') ||
                                       document.querySelector('ytcp-captions-upload-dialog input[type="file"]');
                        if (loader) return loader;
                        const allInputs = Array.from(document.querySelectorAll('input[type="file"]')).filter(
                            i => !i.closest('ytcp-thumbnail-uploader') && !i.closest('ytcp-thumbnails-compact-editor-uploader')
                        );
                        return allInputs.find(i => (i.accept || '').includes('.srt') || (i.name || '').includes('sub') || (i.id || '').includes('captions')) || allInputs[0] || null;
                    })()
                """)
                if input_obj and input_obj.get("objectId"):
                    obj_id = input_obj["objectId"]
                    break

            if not obj_id:
                logger.warning("Could not resolve objectId for captions file input.")
                await self._close_captions_modal()
                return False

            await self.call("DOM.setFileInputFiles", {
                "files": [str(sub_path)],
                "objectId": obj_id,
            })
            logger.info("Subtitles file injected via CDP. Waiting 3.5s for Studio parsing & timeline population...")
            await asyncio.sleep(3.5)

            # 5. Click Done / Publish / Save in captions editor modal
            saved = await self.evaluate("""
                (() => {
                    const finishBtn = document.querySelector('ytve-captions-editor-modal #publish-button button') ||
                                      document.querySelector('ytve-captions-editor-modal #publish-button') ||
                                      document.querySelector('ytcp-dialog #publish-button') ||
                                      document.querySelector('ytve-captions-editor-modal #save-button') ||
                                      Array.from(document.querySelectorAll('ytve-captions-editor-modal ytcp-button, ytve-captions-editor-modal button, ytcp-dialog button, ytcp-dialog ytcp-button')).find(b => {
                                          if (b.id === 'next-button') return false;
                                          const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                          return t === 'xong' || t === 'done' || t === 'xuất bản' || t === 'publish' || t === 'lưu' || t === 'save';
                                      });
                    if (finishBtn && finishBtn.getAttribute('aria-disabled') !== 'true') {
                        finishBtn.click();
                        return true;
                    }
                    return false;
                })()
            """)
            logger.info("Captions editor finish button clicked: %s", saved)

            # 6. Wait up to 8s for ytve-captions-editor-modal and dialogs to close
            closed = False
            for _ in range(16):
                await asyncio.sleep(0.5)
                is_open = await self.evaluate("""
                    (() => {
                        const modal = document.querySelector('ytve-captions-editor-modal');
                        if (modal && modal.offsetParent !== null && modal.getAttribute('aria-hidden') !== 'true') return true;
                        const subDlg = document.querySelector('ytve-captions-editor-upload-dialog, ytcp-captions-upload-dialog');
                        if (subDlg && subDlg.offsetParent !== null && subDlg.getAttribute('aria-hidden') !== 'true') return true;
                        return false;
                    })()
                """)
                if not is_open:
                    closed = True
                    break

            if not closed:
                logger.warning("Captions editor modal did not close within 8s; closing modal safely.")
                await self._close_captions_modal()
                return False

            logger.info("Subtitles successfully uploaded and captions modal closed cleanly.")
            return True
        except Exception as e:
            logger.warning("Subtitles upload inside modal encountered error: %s", e)
            await self._close_captions_modal()
            return False

    async def attach_subtitles_on_elements_step(self, subtitles_path: str | Path) -> bool:
        """Attach subtitles (.srt) file during Step 2 (Video Elements / Thành phần video)."""
        sub_path = Path(subtitles_path).resolve()
        if not sub_path.is_file():
            logger.warning("Subtitles file not found: %s", sub_path)
            return False

        logger.info("Attempting to attach subtitles on Elements step from %s...", sub_path)
        try:
            clicked_btn = await self.evaluate("""
                (() => {
                    let btn = document.querySelector('#subtitles-button') ||
                              document.querySelector('ytcp-button#subtitles-button') ||
                              document.querySelector('button#subtitles-button') ||
                              document.querySelector('button[aria-label*="Phụ đề"]') ||
                              document.querySelector('button[aria-label*="Subtitles"]') ||
                              document.querySelector('ytcp-button[aria-label*="Phụ đề"]') ||
                              document.querySelector('ytcp-button[aria-label*="Subtitles"]');
                    if (!btn) {
                        const rows = Array.from(document.querySelectorAll('ytcp-video-elements-row, ytcp-elements-row, [role="row"], .element-row'));
                        const subRow = rows.find(r => {
                            const t = (r.innerText || '').toLowerCase();
                            return t.includes('phụ đề') || t.includes('subtitles');
                        });
                        if (subRow) {
                            btn = subRow.querySelector('ytcp-button, button, #add-button');
                        }
                    }
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                })()
            """)
            if not clicked_btn:
                logger.warning("Subtitles Add button not found on Video Elements step.")
                return False

            return await self._upload_srt_inside_open_captions_modal(sub_path)
        except Exception as e:
            logger.warning("Subtitles attachment on Elements step encountered error: %s", e)
            await self._close_captions_modal()
            return False

    async def attach_subtitles_post_publish(self, video_url_or_id: str, subtitles_path: str | Path) -> bool:
        """Attach subtitles (.srt) via Studio /video/<id>/edit page post-publication."""
        sub_path = Path(subtitles_path).resolve()
        if not sub_path.is_file():
            logger.warning("Subtitles file not found for post-publish attachment: %s", sub_path)
            return False

        vid_id = str(video_url_or_id).strip()
        if "/" in vid_id:
            vid_id = vid_id.split("/")[-1].split("?")[0]
        if "v=" in vid_id:
            vid_id = vid_id.split("v=")[1].split("&")[0]

        edit_url = f"https://studio.youtube.com/video/{vid_id}/edit"
        logger.info("Navigating to %s for post-publish subtitles attachment...", edit_url)
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(3.5)
        await self.dismiss_studio_interstitials()

        # Poll up to 8s for #subtitles-editor-link or #subtitles-button on /edit page and click
        clicked_sub_link = False
        for _ in range(16):
            clicked_sub_link = await self.evaluate("""
                (() => {
                    const link = document.querySelector('#subtitles-editor-link') ||
                                 document.querySelector('a#subtitles-editor-link') ||
                                 document.querySelector('#subtitles-button') ||
                                 document.querySelector('ytcp-button#subtitles-button') ||
                                 Array.from(document.querySelectorAll('a, button, ytcp-button')).find(el => {
                                     const t = (el.innerText || el.textContent || '').trim().toLowerCase();
                                     return t === 'phụ đề' || t === 'subtitles' || (el.getAttribute('aria-label') || '').toLowerCase().includes('phụ đề');
                                 });
                    if (link && link.offsetParent !== null) {
                        link.click();
                        return true;
                    }
                    return false;
                })()
            """)
            if clicked_sub_link:
                break
            await asyncio.sleep(0.5)
        if not clicked_sub_link:
            logger.warning("Could not find subtitles link on /edit page for %s", vid_id)
            return False

        return await self._upload_srt_inside_open_captions_modal(sub_path)

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

    async def check_studio_readiness(self) -> dict[str, Any]:
        """Verify Studio Auth, live Channel Identity, and inspect Feature Eligibility (Tiers 1/2/3)."""
        curr_url = await self.evaluate("window.location.href")
        if not curr_url or "accounts.google.com" in curr_url or "confirmidentifier" in curr_url:
            return {
                "authenticated": False,
                "auth_url": curr_url or "",
                "channel_id": None,
                "channel_name": None,
                "handle": None,
                "standard_features": False,
                "intermediate_features": False,
                "advanced_features": False,
                "tier2_eligible": False,
                "tier3_eligible": False,
                "tier1_status_text": "",
                "tier2_status_text": "",
                "tier3_status_text": "",
                "audit_method": "auth_required",
                "error": f"GOOGLE_AUTH_REQUIRED: {curr_url}",
            }

        channel_info = await self.get_channel_info()
        channel_id = channel_info.get("channelId")
        channel_name = channel_info.get("channelName")
        handle = self.resolve_channel_handle()

        # Step: Inspect Studio Settings -> Channel -> Feature Eligibility
        audit_method = "settings_unavailable"
        tier1_text = ""
        tier2_text = ""
        tier3_text = ""

        try:
            # 1. Open Settings Dialog
            opened = await self.evaluate("""
                (() => {
                    const settingsBtn = document.querySelector('#settings-item') ||
                                        document.querySelector('ytcp-navigation-item#settings-item') ||
                                        document.querySelector('#settings-button') ||
                                        document.querySelector('button[aria-label*="Cài đặt"]') ||
                                        document.querySelector('button[aria-label*="Settings"]') ||
                                        Array.from(document.querySelectorAll('ytcp-navigation-item, button, a')).find(el => {
                                            const t = (el.innerText || '').trim().toLowerCase();
                                            return t === 'cài đặt' || t === 'settings';
                                        });
                    if (settingsBtn) {
                        settingsBtn.click();
                        return true;
                    }
                    return false;
                })()
            """)

            if opened:
                # Wait up to 6s for settings dialog
                dlg_ready = False
                for _ in range(12):
                    await asyncio.sleep(0.5)
                    is_visible = await self.evaluate("""
                        (() => {
                            const dlg = document.querySelector('ytcp-settings-dialog') ||
                                        document.querySelector('ytcp-dialog[dialog-type="settings"]') ||
                                        document.querySelector('tp-yt-paper-dialog.ytcp-settings-dialog');
                            return Boolean(dlg && dlg.offsetParent !== null && dlg.getAttribute('aria-hidden') !== 'true');
                        })()
                    """)
                    if is_visible:
                        dlg_ready = True
                        break

                if dlg_ready:
                    # 2. Click Channel / Kênh nav tab
                    await self.evaluate("""
                        (() => {
                            const dlg = document.querySelector('ytcp-settings-dialog') || document;
                            const tabs = Array.from(dlg.querySelectorAll('tp-yt-paper-tab, ytcp-navigation-item, .navigation-item, [role="tab"], tp-yt-paper-item'));
                            const channelTab = tabs.find(t => {
                                const text = (t.innerText || '').trim().toLowerCase();
                                return text === 'kênh' || text === 'channel';
                            });
                            if (channelTab) channelTab.click();
                        })()
                    """)
                    await asyncio.sleep(0.6)

                    # 3. Click Feature eligibility / Điều kiện sử dụng tính năng tab
                    await self.evaluate("""
                        (() => {
                            const dlg = document.querySelector('ytcp-settings-dialog') || document;
                            const tabs = Array.from(dlg.querySelectorAll('tp-yt-paper-tab, [role="tab"], .tab-header, button'));
                            const featTab = tabs.find(t => {
                                const text = (t.innerText || '').trim().toLowerCase();
                                return text.includes('điều kiện') || text.includes('tính năng') || text.includes('feature eligibility');
                            });
                            if (featTab) featTab.click();
                        })()
                    """)
                    await asyncio.sleep(0.8)

                    # 4. Inspect Tier Rows
                    tier_res = await self.evaluate("""
                        (() => {
                            const dlg = document.querySelector('ytcp-settings-dialog') || document;
                            function getStatus(section) {
                                if (!section) return '';
                                const badge = section.querySelector('.status, .badge, ytcp-chip, .feature-status, [class*="status"], [class*="badge"]');
                                if (badge && badge.innerText) return badge.innerText.trim();
                                const lines = (section.innerText || '').split('\\n').map(l => l.trim()).filter(Boolean);
                                for (const line of lines) {
                                    const l = line.toLowerCase();
                                    if (l === 'đã bật' || l === 'enabled' || l === 'đủ điều kiện' || l === 'eligible' || l === 'bị tắt' || l === 'disabled') {
                                        return line;
                                    }
                                }
                                return '';
                            }

                            const sections = Array.from(dlg.querySelectorAll('ytcp-feature-eligibility-section, .feature-section, ytcp-settings-section, tp-yt-paper-item, div[role="region"], .tier-container, .section'));
                            let t1 = '';
                            let t2 = '';
                            let t3 = '';

                            for (const s of sections) {
                                const t = (s.innerText || '').toLowerCase();
                                if ((t.includes('chuẩn') || t.includes('standard')) && !t1) {
                                    t1 = getStatus(s);
                                }
                                if ((t.includes('bậc trung') || t.includes('intermediate') || t.includes('15 phút') || t.includes('15 minutes')) && !t2) {
                                    t2 = getStatus(s);
                                }
                                if ((t.includes('nâng cao') || t.includes('advanced')) && !t3) {
                                    t3 = getStatus(s);
                                }
                            }

                            const bodyText = (dlg.innerText || '').toLowerCase();
                            if (!t1 && (bodyText.includes('tính năng chuẩn') || bodyText.includes('standard features'))) {
                                t1 = (bodyText.includes('chuẩn') && bodyText.includes('đã bật')) ? 'Đã bật' : (bodyText.includes('standard') && bodyText.includes('enabled') ? 'Enabled' : '');
                            }
                            if (!t2 && (bodyText.includes('tính năng bậc trung') || bodyText.includes('intermediate features'))) {
                                t2 = (bodyText.includes('bậc trung') && bodyText.includes('đã bật')) ? 'Đã bật' : (bodyText.includes('đủ điều kiện') ? 'Đủ điều kiện' : (bodyText.includes('intermediate') && bodyText.includes('enabled') ? 'Enabled' : ''));
                            }
                            if (!t3 && (bodyText.includes('tính năng nâng cao') || bodyText.includes('advanced features'))) {
                                t3 = (bodyText.includes('nâng cao') && bodyText.includes('đã bật')) ? 'Đã bật' : (bodyText.includes('đủ điều kiện') ? 'Đủ điều kiện' : (bodyText.includes('advanced') && bodyText.includes('enabled') ? 'Enabled' : ''));
                            }

                            return { t1, t2, t3 };
                        })()
                    """)

                    if isinstance(tier_res, dict):
                        tier1_text = tier_res.get("t1", "")
                        tier2_text = tier_res.get("t2", "")
                        tier3_text = tier_res.get("t3", "")
                        if tier1_text or tier2_text or tier3_text:
                            audit_method = "settings_feature_eligibility"

                    # 5. Cleanly close dialog
                    await self.evaluate("""
                        (() => {
                            const dlg = document.querySelector('ytcp-settings-dialog');
                            if (!dlg) return;
                            const closeBtn = dlg.querySelector('#close-button') ||
                                             dlg.querySelector('ytcp-button#close-button') ||
                                             dlg.querySelector('#cancel-button') ||
                                             dlg.querySelector('button[aria-label*="Đóng"]') ||
                                             dlg.querySelector('button[aria-label*="Close"]');
                            if (closeBtn) closeBtn.click();
                        })()
                    """)
                    await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
                    await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
                    await asyncio.sleep(0.5)
        except Exception as err:
            logger.warning("Feature eligibility inspection error (falling back): %s", err)

        # Determine enabled ONLY when status text explicitly contains 'đã bật' or 'enabled'
        t1_enabled = "đã bật" in tier1_text.lower() or "enabled" in tier1_text.lower()
        t2_enabled = "đã bật" in tier2_text.lower() or "enabled" in tier2_text.lower()
        t3_enabled = "đã bật" in tier3_text.lower() or "enabled" in tier3_text.lower()

        # Default standard to True if channel is authenticated and active
        if not t1_enabled and not tier1_text:
            t1_enabled = True
            tier1_text = "Đã bật"

        return {
            "authenticated": True,
            "auth_url": curr_url,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "handle": handle,
            "standard_features": t1_enabled,
            "intermediate_features": t2_enabled,
            "advanced_features": t3_enabled,
            "tier2_eligible": t2_enabled,
            "tier3_eligible": t3_enabled,
            "tier1_status_text": tier1_text,
            "tier2_status_text": tier2_text,
            "tier3_status_text": tier3_text,
            "audit_method": audit_method,
            "details": {
                "tier1_status": tier1_text,
                "tier2_status": tier2_text,
                "tier3_status": tier3_text,
            },
        }

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
                    const errorEl = document.querySelector('ytcp-video-upload-progress .error-short, .error-area, ytcp-uploads-dialog .error-short, ytcp-badge[type="BADGE_STYLE_TYPE_RED"], #error-message');
                    const doneBtn = document.querySelector('#done-button');
                    const text = statusEl ? statusEl.innerText.trim() : '';
                    const errText = errorEl ? errorEl.innerText.trim() : '';
                    const doneDisabled = doneBtn ? (doneBtn.hasAttribute('disabled') || doneBtn.getAttribute('aria-disabled') === 'true') : true;
                    return { text, errText, doneDisabled };
                })()
            """)
            text = (state or {}).get("text", "")
            err_text = (state or {}).get("errText", "")
            done_disabled = (state or {}).get("doneDisabled", True)

            # Check for Tier-2 >15m triggers or verification required
            combined_err = f"{err_text} {text}".strip()
            comb_lower = combined_err.lower()
            tier2_triggers = (
                "hơn 15 phút",
                "longer than 15 minutes",
                "video quá dài",
                "quá trình xử lý bị hủy",
                "processing abandoned",
                "cần xác minh",
                "verify your account",
            )
            if done_disabled and any(trig in comb_lower for trig in tier2_triggers):
                fatal_msg = err_text or text or "Video longer than 15 minutes / account verification required"
                logger.error("Upload aborted due to Tier-2 duration or verification requirement: %s", fatal_msg)
                raise RuntimeError(f"TIER2_DURATION_OR_VERIFICATION_REQUIRED: {fatal_msg}")

            now = time.time()
            if now - last_log > 5.0:
                logger.info("Upload status: %r (Publish button ready: %s)", text, not done_disabled)
                last_log = now

            t_lower = text.lower()
            has_active_percent = (
                "%" in text
                and "100%" not in text
                and "đang xử lý" not in t_lower
                and "processing" not in t_lower
            )
            is_uploading = (
                has_active_percent
                or "còn " in t_lower
                or "left" in t_lower
                or "remaining" in t_lower
                or "đang tải" in t_lower
                or "uploading" in t_lower
            )
            is_processed = (
                bool(text.strip())
                and (
                    "100%" in text
                    or "đã xử lý" in t_lower
                    or "đang xử lý" in t_lower
                    or "quá trình xử lý" in t_lower
                    or "đã tải lên" in t_lower
                    or "uploaded" in t_lower
                    or "đã hoàn tất" in t_lower
                    or "đã kiểm tra" in t_lower
                    or "kiểm tra hoàn tất" in t_lower
                    or "không tìm thấy vấn đề" in t_lower
                    or "không phát hiện vấn đề" in t_lower
                    or "no issues found" in t_lower
                    or "checks complete" in t_lower
                    or "processing" in t_lower
                )
                and not is_uploading
            )

            # NEVER exit waiting with True unless upload is 100%/processed AND #done-button is enabled AND not actively uploading
            if not done_disabled and is_processed and not is_uploading:
                logger.info("Upload complete and verified ready for publication (Done button enabled).")
                return True

            await asyncio.sleep(2.0)

        logger.warning("Upload wait timed out after %.0fs; done button or processing incomplete.", max_wait_sec)
        return False

    async def publish_and_finish(self, screenshot_path: Optional[str | Path] = None) -> Optional[str]:
        """Click the Publish/Done button, capture share/processing dialog, and extract confirmed URL."""
        self._last_publish_accepted = False
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

        # Wait for share confirmation dialog or processing modal
        logger.info("Waiting for publication confirmation dialog...")
        confirmed_url = None
        for _ in range(25):
            await asyncio.sleep(1.0)
            # 1. Check if YouTube popped up 'Chúng tôi vẫn đang kiểm tra nội dung của bạn' -> click 'Vẫn xuất bản' / 'Publish anyway'
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

            # 2. Check for ytcp-video-share-dialog
            confirmed = await self.evaluate("""
                (() => {
                    const shareDialog = document.querySelector('ytcp-video-share-dialog');
                    if (!shareDialog || shareDialog.offsetParent === null) return { found: false };
                    const links = Array.from(shareDialog.querySelectorAll('a')).map(a => a.href).filter(Boolean);
                    const ytLink = links.find(l => l.includes('youtu.be/') || l.includes('youtube.com/watch?v='));
                    const title = shareDialog.querySelector('#dialog-title')?.innerText?.trim() || null;
                    return { found: true, link: ytLink || null, title };
                })()
            """)
            if confirmed and confirmed.get("found"):
                self._last_publish_accepted = True
                if confirmed.get("link"):
                    confirmed_url = confirmed["link"]
                    logger.info("Publication confirmed via share dialog: %s (Title: %s)", confirmed_url, confirmed.get("title"))
                    break

            # 3. Check for the processing modal ('Xử lý video' / 'Video processing' / 'Độ nét chuẩn' / 'Standard definition')
            proc_dlg = await self.evaluate("""
                (() => {
                    const dlgs = Array.from(document.querySelectorAll(
                        'ytcp-video-processing-dialog, ytcp-dialog, tp-yt-paper-dialog'
                    ));
                    for (const d of dlgs) {
                        if (d.offsetParent === null || d.getAttribute('aria-hidden') === 'true') continue;
                        const txt = (d.innerText || d.textContent || '').toLowerCase();
                        if (
                            txt.includes('xử lý video') ||
                            txt.includes('video processing') ||
                            txt.includes('độ nét chuẩn') ||
                            txt.includes('standard definition')
                        ) {
                            const links = Array.from(d.querySelectorAll('a'));
                            let link = null;
                            for (const a of links) {
                                const h = a.href || '';
                                if (h.includes('youtu.be/') || h.includes('watch?v=') || h.includes('/video/')) {
                                    link = h;
                                    break;
                                }
                            }
                            return { detected: true, link };
                        }
                    }
                    return { detected: false };
                })()
            """)
            if proc_dlg and proc_dlg.get("detected"):
                self._last_publish_accepted = True
                p_link = proc_dlg.get("link")
                if p_link and ("youtu.be" in p_link or "watch?v=" in p_link):
                    confirmed_url = p_link
                logger.info("Publication confirmed via processing modal ('Xử lý video').")
                if screenshot_path:
                    try:
                        await self.capture_screenshot(screenshot_path)
                    except Exception as s_err:
                        logger.warning("Could not capture screenshot of processing dialog: %s", s_err)
                # Click Close button inside processing dialog
                await self.evaluate("""
                    (() => {
                        const dlgs = Array.from(document.querySelectorAll(
                            'ytcp-video-processing-dialog, ytcp-dialog, tp-yt-paper-dialog'
                        ));
                        for (const d of dlgs) {
                            if (d.offsetParent === null) continue;
                            const txt = (d.innerText || d.textContent || '').toLowerCase();
                            if (
                                txt.includes('xử lý video') ||
                                txt.includes('video processing') ||
                                txt.includes('độ nét chuẩn') ||
                                txt.includes('standard definition')
                            ) {
                                const closeBtn = d.querySelector('#close-button') ||
                                                 d.querySelector('ytcp-button#close-button') ||
                                                 Array.from(d.querySelectorAll('ytcp-button, button')).find(b => {
                                                     const bt = (b.innerText || '').trim().toLowerCase();
                                                     return bt === 'đóng' || bt === 'close';
                                                 });
                                if (closeBtn) closeBtn.click();
                                break;
                            }
                        }
                    })()
                """)
                await asyncio.sleep(1.0)
                break

        if screenshot_path and not Path(screenshot_path).is_file():
            try:
                await self.capture_screenshot(screenshot_path)
            except Exception:
                pass

        # Close share modal if still present
        await self.evaluate("""
            (() => {
                const closeBtn = document.querySelector('ytcp-video-share-dialog #close-button') ||
                                 document.querySelector('#close-button');
                if (closeBtn) closeBtn.click();
            })()
        """)
        await asyncio.sleep(2.0)
        return confirmed_url

    async def verify_video_edit_page(
        self,
        video_url_or_id: str,
        screenshot_path: Optional[str | Path] = None,
    ) -> dict[str, Any]:
        """Navigate to studio.youtube.com/video/<vid_id>/edit, expose details, take screenshot, and return live summary."""
        vid_id = str(video_url_or_id).strip()
        if "/" in vid_id:
            vid_id = vid_id.split("/")[-1].split("?")[0]
        if "v=" in vid_id:
            vid_id = vid_id.split("v=")[1].split("&")[0]

        edit_url = f"https://studio.youtube.com/video/{vid_id}/edit"
        logger.info("Navigating to video edit page: %s...", edit_url)
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(3.0)
        await self.dismiss_studio_interstitials()

        # Wait up to 10s for title editor
        for _ in range(20):
            has_title = await self.evaluate("Boolean(document.querySelector('#title-textarea #textbox'))")
            if has_title:
                break
            await asyncio.sleep(0.5)

        # Click #toggle-button (Show more / Hiển thị thêm) if collapsed
        await self.evaluate("""
            (() => {
                const tagBox = document.querySelector('#tags-container');
                if (tagBox && tagBox.offsetParent !== null) return 'ALREADY_EXPANDED';
                const toggleBtn = document.querySelector('#toggle-button') ||
                                  document.querySelector('ytcp-button#toggle-button') ||
                                  Array.from(document.querySelectorAll('ytcp-button, button')).find(b => {
                                      const txt = (b.innerText || '').toLowerCase();
                                      return txt.includes('hiển thị thêm') || txt.includes('show more');
                                  });
                if (toggleBtn) toggleBtn.click();
            })()
        """)
        await asyncio.sleep(1.0)

        if screenshot_path:
            p = Path(screenshot_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            try:
                await self.capture_screenshot(p)
                logger.info("Captured edit verification screenshot to %s", p)
            except Exception as sc_err:
                logger.warning("Could not capture edit verification screenshot: %s", sc_err)

            try:
                await self.evaluate("""
                    (() => {
                        const el = document.querySelector('#tags-container') ||
                                   document.querySelector('ytcp-form-input-container#tags-container');
                        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
                    })()
                """)
                await asyncio.sleep(0.5)
                bottom_p = p.with_name(f"{p.stem}_bottom{p.suffix}")
                await self.capture_screenshot(bottom_p)
                logger.info("Captured edit verification bottom screenshot to %s", bottom_p)
            except Exception as sc_bottom_err:
                logger.warning("Could not capture edit verification bottom screenshot: %s", sc_bottom_err)

        summary = await self.evaluate("""
            (() => {
                const titleEl = document.querySelector('#title-textarea #textbox') ||
                                document.querySelector('#textbox[contenteditable="true"]');
                const descEl = document.querySelector('#description-textarea #textbox');
                const descText = descEl ? (descEl.innerText || '') : '';

                const live_title = titleEl ? (titleEl.innerText || '').trim() : '';
                const description_length = descText.length;
                const has_chapters_00_00 = descText.includes('00:00');

                // Custom thumbnail check
                const thumbUploader = document.querySelector('ytcp-thumbnail-uploader img[src]') ||
                                      document.querySelector('#still-1[selected]') ||
                                      document.querySelector('ytcp-thumbnails-compact-editor-uploader img[src]');
                const has_custom_thumbnail = Boolean(thumbUploader);

                // Tags chips
                const chips = Array.from(document.querySelectorAll('#tags-container ytcp-chip'));
                const tags_chip_count = chips.length;
                const tags_sample = chips.slice(0, 5).map(c => (c.innerText || c.textContent || '').trim()).filter(Boolean);

                // Subtitles
                const subBtn = document.querySelector('#subtitles-button') ||
                               document.querySelector('#subtitles-editor-link') ||
                               document.querySelector('ytcp-video-elements-row');
                const subText = subBtn ? (subBtn.innerText || subBtn.textContent || '').trim() : '';
                const subLower = subText.toLowerCase();
                const subtitles_present = (
                    subLower.includes('đã thêm') ||
                    subLower.includes('added') ||
                    (subText.length > 0 && !subLower.includes('thêm') && !subLower.includes('add'))
                );

                // Language & Category
                const langEl = document.querySelector('#language-input') ||
                               document.querySelector('ytcp-text-dropdown-select#language-input') ||
                               document.querySelector('#language-and-close-captioning #language-input');
                const language_text = langEl ? (langEl.innerText || langEl.textContent || '').trim() : '';

                const catEl = document.querySelector('#category') ||
                              document.querySelector('ytcp-text-dropdown-select#category') ||
                              document.querySelector('#category-dropdown');
                const category_text = catEl ? (catEl.innerText || catEl.textContent || '').trim() : '';

                // Visibility
                const visBtn = document.querySelector('#visibility-button') ||
                               document.querySelector('#visibility') ||
                               document.querySelector('ytcp-video-metadata-visibility') ||
                               document.querySelector('.visibility-label');
                const visibility_text = visBtn ? (visBtn.innerText || visBtn.textContent || '').trim() : '';

                return {
                    live_title,
                    description_length,
                    has_chapters_00_00,
                    has_custom_thumbnail,
                    tags_chip_count,
                    tags_sample,
                    subtitles_present,
                    subtitles_status: subText,
                    language_text,
                    category_text,
                    visibility_text,
                };
            })()
        """)
        res = dict(summary) if isinstance(summary, dict) else {}
        v_low = (res.get("visibility_text") or "").lower()
        is_draft_or_private = (
            "bản nháp" in v_low
            or "draft" in v_low
            or "riêng tư" in v_low
            or "private" in v_low
        )
        res["is_draft_or_private"] = is_draft_or_private
        res["video_id"] = vid_id
        res["edit_url"] = edit_url
        logger.info(
            "Studio edit page verified for %s: title='%s', vis='%s', chips=%s, draft=%s",
            vid_id,
            res.get("live_title"),
            res.get("visibility_text"),
            res.get("tags_chip_count"),
            is_draft_or_private,
        )
        return res


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
    tags: Optional[str | list[str]] = None,
    language: Optional[str] = None,
    category: Optional[str] = None,
    strict_thumbnail: bool = False,
    expected_channel_id: Optional[str] = None,
    max_wait_sec: Optional[float] = None,
    edit_screenshot_path: Optional[str | Path] = None,
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

    target_expected_channel_id = expected_channel_id
    if target_expected_channel_id is None and profile_cfg:
        target_expected_channel_id = profile_cfg.get("youtube_channel_id") or profile_cfg.get("channel_id")

    client = YouTubeCDPClient(profile_cfg, headless=headless)
    try:
        await client.connect()

        # Step 0: Ensure browser is at YouTube Studio dashboard
        curr_url = await client.evaluate("window.location.href")
        if curr_url and ("accounts.google.com/v3/signin" in str(curr_url) or "confirmidentifier" in str(curr_url) or "accounts.google.com" in str(curr_url)):
            raise RuntimeError(f"GOOGLE_AUTH_REQUIRED: {curr_url}")

        yt_chid = profile_cfg.get("youtube_channel_id") or profile_cfg.get("channel_id")
        target_studio_url = f"https://studio.youtube.com/channel/{yt_chid}" if yt_chid and str(yt_chid).startswith("UC") else "https://studio.youtube.com"
        if "studio.youtube.com" not in str(curr_url) or (yt_chid and str(yt_chid).startswith("UC") and str(yt_chid) not in str(curr_url)):
            logger.info("Navigating to %s...", target_studio_url)
            await client.call("Page.navigate", {"url": target_studio_url})
            await asyncio.sleep(6.0)

        await client.dismiss_studio_interstitials()
        await asyncio.sleep(2.0)

        # Step 1: Channel Info Verification & Channel Identity Lock
        await asyncio.sleep(4.0)
        channel_info = await client.get_channel_info()
        logger.info("Channel info: %s", channel_info)

        curr_url = channel_info.get("url", "")
        if "accounts.google.com/v3/signin" in curr_url or "confirmidentifier" in curr_url or "accounts.google.com" in curr_url:
            raise RuntimeError(f"GOOGLE_AUTH_REQUIRED: {curr_url}")

        if target_expected_channel_id and str(target_expected_channel_id).startswith("UC"):
            live_chid = channel_info.get("channelId")
            if live_chid != target_expected_channel_id:
                raise RuntimeError(
                    f"CHANNEL_IDENTITY_MISMATCH: expected={target_expected_channel_id}, got={channel_info}"
                )

        # Step 2: Open Upload Dialog
        await client.open_upload_dialog()

        # Step 3: Attach Video File
        await client.attach_video(video_path)

        # Step 4: Extract Video URL from Dialog
        dialog_video_url = await client.extract_video_url()
        logger.info("Assigned video URL in dialog: %s", dialog_video_url)

        # Step 5: Fill Metadata (Title, Description, MFK, Tags, Language, Category)
        await client.fill_details(
            title=title,
            description=description,
            is_kids=False,
            tags=tags,
            language=language,
            category=category,
        )

        # Step 6: Custom Thumbnail (Long 16:9 & Short 9:16)
        thumbnail_status = False
        if thumbnail_path:
            thumbnail_status = await client.upload_thumbnail(
                thumbnail_path,
                strict_thumbnail=strict_thumbnail,
            )

        # Advance to Step 2 (Video Elements)
        await client.evaluate("""
            (() => {
                const btn = document.querySelector('#next-button');
                if (btn && btn.getAttribute('aria-disabled') !== 'true') btn.click();
            })()
        """)
        # Wait up to 8s until Step 2 Video Elements renders
        for _ in range(16):
            has_elements = await client.evaluate("""
                Boolean(
                    document.querySelector('#subtitles-button') ||
                    document.querySelector('#cards-button') ||
                    document.querySelector('#endscreens-button') ||
                    document.querySelector('ytcp-video-elements-row') ||
                    document.querySelector('ytcp-uploads-video-elements')
                )
            """)
            if has_elements:
                break
            await asyncio.sleep(0.5)

        # Step 6b: Subtitles (.srt) handling on Elements step if provided and exists
        subtitles_status = False
        if subtitles_path:
            sub_file = Path(subtitles_path).resolve()
            if sub_file.is_file():
                logger.info("Handling subtitles attachment from %s (%d bytes)...", sub_file, sub_file.stat().st_size)
                try:
                    subtitles_status = await client.attach_subtitles_on_elements_step(sub_file)
                except Exception as sub_err:
                    logger.warning("Could not attach subtitles on elements step (continuing publish): %s", sub_err)
            else:
                logger.warning("Subtitles path provided but file not found: %s", subtitles_path)

        related_linked = False
        if is_short and related_video_url:
            related_linked = await client.link_related_video(related_video_url)

        # Step 7: Advance through wizard to Step 4 (Visibility)
        await client.advance_to_visibility_step()

        # Step 8: Set Visibility to PUBLIC
        await client.set_visibility(visibility)

        # Step 9: Wait for upload completion (Dynamic timeout)
        if max_wait_sec is None:
            try:
                p = Path(video_path)
                file_mb = p.stat().st_size / (1024 * 1024) if p.is_file() else 300.0
                effective_max_wait = max(600.0, file_mb * 1.6)
            except Exception:
                effective_max_wait = 600.0
        else:
            effective_max_wait = max_wait_sec

        logger.info("Upload completion max wait timeout: %.1fs", effective_max_wait)
        await client.wait_for_upload_complete(max_wait_sec=effective_max_wait)

        # Step 10: Finalize Publication & QA Screenshot
        final_url = await client.publish_and_finish(screenshot_path=screenshot_path)
        resolved_url = final_url or dialog_video_url

        # Step 10b: Automatic post-publish subtitles fallback if wizard attachment failed
        if subtitles_path and not subtitles_status and resolved_url:
            sub_file = Path(subtitles_path).resolve()
            if sub_file.is_file():
                logger.info(
                    "Subtitles not attached during wizard; running post-publish subtitles fallback on /edit for %s...",
                    resolved_url,
                )
                try:
                    subtitles_status = await client.attach_subtitles_post_publish(resolved_url, sub_file)
                    logger.info("attach_subtitles_post_publish result: %s", subtitles_status)
                except Exception as sub_post_err:
                    logger.warning("Could not attach subtitles post-publish (continuing): %s", sub_post_err)

        oembed_ok = False
        oembed_pending = False
        edit_verification: Optional[dict[str, Any]] = None

        if visibility.upper() == "PUBLIC":
            if not resolved_url:
                raise RuntimeError(
                    "PUBLIC_VERIFICATION_FAILED: No video URL resolved from YouTube Studio dialog."
                )
            if resolved_url and Path(video_path).exists():
                vid_id = resolved_url.strip().rstrip("/").split("/")[-1].split("?")[0]
                if vid_id:
                    oembed_endpoint = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json"
                    max_attempts = 7 if is_short else 18
                    sleep_between = 2.5 if is_short else 5.0
                    total_wait = max_attempts * sleep_between
                    logger.info(
                        "Verifying live PUBLIC status via YouTube oEmbed for %s (%d attempts, max %.0fs)...",
                        vid_id,
                        max_attempts,
                        total_wait,
                    )
                    for attempt in range(1, max_attempts + 1):
                        await asyncio.sleep(sleep_between)
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
                            logger.warning(
                                "oEmbed PUBLIC check attempt %d/%d for %s not yet 200: %s",
                                attempt,
                                max_attempts,
                                vid_id,
                                exc,
                            )

                    if not oembed_ok:
                        if not is_short:
                            logger.info(
                                "Long video %s did not return oEmbed 200 after %.0fs; running Studio edit verification fallback...",
                                vid_id,
                                total_wait,
                            )
                            if hasattr(client, "verify_video_edit_page"):
                                edit_verification = await client.verify_video_edit_page(
                                    vid_id,
                                    screenshot_path=edit_screenshot_path,
                                )

                            is_draft = edit_verification.get("is_draft_or_private", False) if edit_verification else False
                            accepted = getattr(client, "_last_publish_accepted", False)

                            if not is_draft or accepted:
                                logger.warning(
                                    "Video %s confirmed queued/processing or publish accepted (not draft). "
                                    "Marking as PUBLISHED with oembed_pending_processing=True.",
                                    vid_id,
                                )
                                oembed_pending = True
                            else:
                                raise RuntimeError(
                                    f"PUBLIC_VERIFICATION_FAILED: Video '{resolved_url}' confirmed as Draft/Private in YouTube Studio "
                                    f"(visibility={edit_verification.get('visibility_text') if edit_verification else 'unknown'})."
                                )
                        else:
                            raise RuntimeError(
                                f"PUBLIC_VERIFICATION_FAILED: Video '{resolved_url}' did not return HTTP 200 on public oEmbed! "
                                "It is still Private/Draft in YouTube Studio."
                            )
                    else:
                        if edit_screenshot_path and hasattr(client, "verify_video_edit_page"):
                            try:
                                edit_verification = await client.verify_video_edit_page(
                                    vid_id,
                                    screenshot_path=edit_screenshot_path,
                                )
                            except Exception as ev_err:
                                logger.warning("Could not capture edit verification for %s: %s", vid_id, ev_err)

        if edit_screenshot_path and edit_verification is None and resolved_url and hasattr(client, "verify_video_edit_page"):
            vid_id = resolved_url.strip().rstrip("/").split("/")[-1].split("?")[0]
            try:
                edit_verification = await client.verify_video_edit_page(
                    vid_id,
                    screenshot_path=edit_screenshot_path,
                )
            except Exception as ev_err:
                logger.warning("Could not capture edit verification for %s: %s", vid_id, ev_err)

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

        if effective_job_id and resolved_url and not bypass_review_gate:
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
            "edit_screenshot_path": str(edit_screenshot_path) if edit_screenshot_path else None,
            "oembed_ok": oembed_ok,
            "oembed_pending_processing": oembed_pending,
            "edit_verification": edit_verification,
        }
    finally:
        await client.close()
        client.terminate_browser()


publish_to_youtube_studio = publish_single_video


def parse_metadata_file(md_path: str | Path) -> dict[str, str]:
    """Parse title, description, tags, language, and category from markdown publication kit."""
    text = Path(md_path).read_text(encoding="utf-8")
    title = ""
    description = ""
    tags = ""
    language = "Tiếng Việt"
    category = "Giáo dục"
    pinned_comment = ""

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

    # Language extraction (support bullet format under ## 4. and header blocks)
    m_bullet_lang = re.search(r"-\s*\*\*Ngôn ngữ video(?:\s*\([^)]*\))?\*\*:\s*([^\n\r]+)", text, re.IGNORECASE)
    if m_bullet_lang:
        language = m_bullet_lang.group(1).strip()
    else:
        m_lang = re.search(r"##\s*(?:Ngôn ngữ|Language)[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
        if not m_lang:
            m_lang = re.search(r"##\s*(?:Ngôn ngữ|Language)[^\n]*\n([^\n#]+)", text)
        if m_lang:
            language = m_lang.group(1).strip()

    # Category extraction (support bullet format under ## 4. and header blocks)
    m_bullet_cat = re.search(r"-\s*\*\*Danh mục(?:\s*\([^)]*\))?\*\*:\s*([^\n\r]+)", text, re.IGNORECASE)
    if m_bullet_cat:
        category = m_bullet_cat.group(1).strip()
    else:
        m_cat = re.search(r"##\s*(?:Danh mục|Category)[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL)
        if not m_cat:
            m_cat = re.search(r"##\s*(?:Danh mục|Category)[^\n]*\n([^\n#]+)", text)
        if m_cat:
            category = m_cat.group(1).strip()

    # Pinned comment extraction (supports ## 5. or ## 6. or ## Pinned Comment)
    m_pin = re.search(r"##\s*(?:\d+\.)?\s*(?:Bình luận ghim|Pinned Comment)[^\n]*\n```(?:text)?\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
    if not m_pin:
        m_pin = re.search(r"##\s*(?:\d+\.)?\s*(?:Bình luận ghim|Pinned Comment)[^\n]*\n([^\n#]+)", text, re.IGNORECASE)
    if m_pin:
        pinned_comment = m_pin.group(1).strip()

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "language": language,
        "category": category,
        "pinned_comment": pinned_comment,
    }


def main():
    parser = argparse.ArgumentParser(description="Automated YouTube CDP Publisher for Video Pilot")
    parser.add_argument("--video", "--video-file", dest="video", required=False, help="Path to MP4 video file")
    parser.add_argument("--channel", help="Channel ID (e.g., co_the_ke, ai_binh_dan) to resolve profile")
    parser.add_argument("--job-id", help="Job ID")
    parser.add_argument("--profile", help="Explicit Chrome profile ID (e.g. profile_1)")
    parser.add_argument("--cdp-port", type=int, help="CDP port override")
    parser.add_argument("--title", help="Video title (overrides metadata file)")
    parser.add_argument("--description", help="Video description (overrides metadata file)")
    parser.add_argument("--tags", help="Comma-separated tags (overrides metadata file)")
    parser.add_argument("--language", default=None, help="Video language (e.g. Tiếng Việt)")
    parser.add_argument("--category", default=None, help="Video category (e.g. Giáo dục)")
    parser.add_argument("--metadata", help="Path to markdown metadata file (youtube_long.md / youtube_shorts.md)")
    parser.add_argument("--thumbnail", help="Path to thumbnail image file (for 16:9)")
    parser.add_argument("--strict-thumbnail", action="store_true", help="Raise error if custom thumbnail is rejected")
    parser.add_argument("--expected-channel-id", help="Expected channel ID (e.g. UC...) to assert before upload")
    parser.add_argument("--update-thumbnail", help="Retroactively upload thumbnail to an existing video (requires --video-url or --video-id and --channel)")
    parser.add_argument("--video-url", help="Existing video URL")
    parser.add_argument("--video-id", help="Existing video ID")
    parser.add_argument("--subtitles", help="Path to subtitles SRT file")
    parser.add_argument("--visibility", "--privacy", dest="visibility", default="PUBLIC", choices=["PUBLIC", "UNLISTED", "PRIVATE"])
    parser.add_argument("--short", action="store_true", help="Mark as Short (9:16)")
    parser.add_argument("--related-video", help="Related video URL or ID (for Shorts)")
    parser.add_argument("--screenshot", help="Output path for verification screenshot")
    parser.add_argument("--edit-screenshot", help="Output path for post-publish Studio /edit verification screenshot")
    parser.add_argument("--headless", action="store_true", default=True, help="Run Chrome in headless mode (default True)")
    parser.add_argument("--no-headless", "--headed", dest="headless", action="store_false", help="Run Chrome with GUI")
    parser.add_argument("--bypass-review-gate", action="store_true", help="Bypass mandatory review approval gate")

    args = parser.parse_args()

    title = args.title
    description = args.description
    tags = args.tags
    language = args.language
    category = args.category

    if args.metadata:
        meta = parse_metadata_file(args.metadata)
        if not title:
            title = meta.get("title")
        if not description:
            description = meta.get("description")
        if not tags:
            tags = meta.get("tags")
        if not language:
            language = meta.get("language")
        if not category:
            category = meta.get("category")

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
        sys.exit(0 if (isinstance(update_res, dict) and update_res.get("success")) else 1)

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
            tags=tags,
            language=language,
            category=category,
            strict_thumbnail=args.strict_thumbnail,
            expected_channel_id=args.expected_channel_id,
            edit_screenshot_path=getattr(args, "edit_screenshot", None),
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
