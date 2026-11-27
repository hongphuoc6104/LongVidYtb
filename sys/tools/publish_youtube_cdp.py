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

try:
    from flow_cdp.process_manager import ProcessGroupManager, is_port_listening
    from flow_cdp.resource_locks import ProfilePortLock
except ImportError:
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

SISTER_CHANNEL_FORBIDDEN_TOKENS: tuple[str, ...] = (
    "@firstprinciplesink",
    "@luatngamdamdongvn",
    "firstprinciplesink",
    "luatngamdamdongvn",
    "luật ngầm đám đông",
    "first principles ink",
)

DEFAULT_SU_KE_LAI_PLAYLIST: str = "Sử Kể Lại — Hồ Sơ Chiến Dịch & Bí Ẩn Đại Việt"
DEAD_PRIVATE_VIDEO_IDS: tuple[str, ...] = (
    "y5VeObQ7u1E",
    "o_3FRlZ87wE",
    "CbeJM6jT4ag",
)


def clean_dead_links_from_description(
    description: str,
    dead_ids: tuple[str, ...] | list[str] = DEAD_PRIVATE_VIDEO_IDS,
) -> tuple[str, list[str]]:
    """Remove lines or inline URLs referencing dead/Private video IDs from a YouTube description."""
    raw = str(description or "")
    if not raw:
        return "", []
    targets = [str(d).strip() for d in dead_ids if str(d).strip()]
    removed: list[str] = []
    kept_lines: list[str] = []
    for line in raw.splitlines():
        matched_ids = [did for did in targets if did in line]
        if matched_ids:
            for did in matched_ids:
                if did not in removed:
                    removed.append(did)
            continue
        kept_lines.append(line)
    cleaned = "\n".join(kept_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned, removed


def validate_no_sister_channel_leak(channel_id: str | None, *texts: str | None) -> None:
    """Reject cross-channel sister-account handles/mentions on su_ke_lai to prevent sockpuppet detection."""
    ch_norm = str(channel_id or "").strip().lower().replace("-", "_")
    if ch_norm and ch_norm != "su_ke_lai":
        return
    for txt in texts:
        low = str(txt or "").lower()
        for tok in SISTER_CHANNEL_FORBIDDEN_TOKENS:
            if tok in low:
                raise ValueError(f"SISTER_CHANNEL_COMMENT_FORBIDDEN: found {tok!r} in channel={channel_id!r} payload")


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
        altered_content: str = "unset",
        notify_subscribers: Optional[bool] = None,
        playlist_name: Optional[str] = None,
    ) -> None:
        """Set title, description, playlist, audience settings, altered-content disclosure, notify-subscribers, tags, language, and category."""
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

        if playlist_name:
            try:
                await self.ensure_and_select_playlist(playlist_name)
            except Exception as pl_err:
                logger.warning("Playlist assignment (%s) encountered error: %s", playlist_name, pl_err)

        logger.info("Setting audience: Not made for kids (MFK=False)...")
        radio_name = "VIDEO_MADE_FOR_KIDS_MFK" if is_kids else "VIDEO_MADE_FOR_KIDS_NOT_MFK"
        await self.evaluate(f"""
            (() => {{
                const radio = document.querySelector('tp-yt-paper-radio-button[name="{radio_name}"]');
                if (radio) radio.click();
            }})()
        """)
        await asyncio.sleep(1.0)

        # Expand 'Hiển thị thêm' / 'Hiện thêm' / 'Show more' if tags, language, category, altered content, or notify_subscribers need to be set
        clean_tags = format_and_truncate_tags(tags, max_chars=480)
        if clean_tags or language or category or altered_content in ("yes", "no") or notify_subscribers is not None:
            await self.expand_show_more_details()

        if altered_content in ("yes", "no"):
            await self.set_altered_content_disclosure(altered_content)

        if notify_subscribers is not None:
            await self.set_notify_subscribers(bool(notify_subscribers))

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

    async def set_altered_content_disclosure(self, mode: str) -> dict[str, Any]:
        """Set YouTube Studio Altered/Synthetic Content radio (`yes` or `no`)."""
        norm = str(mode or "unset").strip().lower()
        if norm not in ("yes", "no"):
            return {"applied": False, "mode": norm}
        radio_name = "VIDEO_HAS_ALTERED_CONTENT_YES" if norm == "yes" else "VIDEO_HAS_ALTERED_CONTENT_NO"
        res = await self.evaluate(f"""
            (() => {{
                const radio = document.querySelector('tp-yt-paper-radio-button[name="{radio_name}"]') ||
                              document.querySelector('[name="{radio_name}"]');
                if (!radio) return {{ applied: false, reason: 'altered_radio_not_found' }};
                radio.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                radio.click();
                return {{ applied: true, radio: '{radio_name}' }};
            }})()
        """)
        logger.info("Altered content disclosure (%s): %s", norm, res)
        await asyncio.sleep(0.5)
        return res if isinstance(res, dict) else {"applied": False}

    async def expand_show_more_details(self) -> bool:
        """Expand 'Show more' / 'Hiện thêm' / 'Hiển thị thêm' (#toggle-button) in Details or /edit."""
        res = await self.evaluate("""
            (() => {
                const tagBox = document.querySelector('#tags-container') ||
                               document.querySelector('#notify-subscribers') ||
                               document.querySelector('ytcp-checkbox-lit#notify-subscribers') ||
                               document.querySelector('input#text-input[aria-label*="Tags"]');
                if (tagBox) {
                    const r = tagBox.getBoundingClientRect ? tagBox.getBoundingClientRect() : null;
                    if (tagBox.offsetParent !== null || (r && r.width > 0 && r.height > 0)) {
                        return 'ALREADY_EXPANDED';
                    }
                }
                const nodes = [];
                function walk(root, depth = 0) {
                    if (!root || depth > 28) return;
                    if (root.nodeType === 1) {
                        nodes.push(root);
                        if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                    }
                    for (const c of root.children || []) walk(c, depth + 1);
                }
                walk(document.body);

                let toggleBtn = document.querySelector('ytcp-uploads-video-details #toggle-button') ||
                                document.querySelector('ytcp-video-metadata-editor #toggle-button') ||
                                document.querySelector('#toggle-button') ||
                                document.querySelector('ytcp-button#toggle-button');
                if (!toggleBtn) {
                    toggleBtn = nodes.find(b => {
                        if (!b.matches || !b.matches('ytcp-button, button, [role="button"], #toggle-button')) return false;
                        const raw = (b.innerText || b.textContent || b.getAttribute('aria-label') || '');
                        const txt = (raw.normalize ? raw.normalize('NFC') : raw).trim().toLowerCase();
                        if (txt.includes('ẩn bớt') || txt.includes('hiển thị bớt') || txt.includes('show less')) return false;
                        return b.id === 'toggle-button' ||
                               txt.includes('hiển thị thêm') ||
                               txt.includes('hiện thêm') ||
                               txt.includes('show more');
                    });
                }
                if (toggleBtn) {
                    toggleBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
                    toggleBtn.click();
                    return 'TOGGLED';
                }
                return null;
            })()
        """)
        if res == "TOGGLED":
            await asyncio.sleep(1.0)
        return bool(res)

    async def set_notify_subscribers(self, enabled: bool = False) -> dict[str, Any]:
        """Set 'Publish to subscriptions feed and notify subscribers' checkbox state (True=checked, False=unchecked)."""
        target_state = bool(enabled)
        await self.expand_show_more_details()
        target_js = "true" if target_state else "false"
        res = await self.evaluate(f"""
            (() => {{
                const TARGET = {target_js};
                const phrases = [
                    'publish to subscriptions feed and notify subscribers',
                    'notify subscribers',
                    'xuất bản lên nguồn cấp dữ liệu nội dung đăng ký và thông báo cho người đăng ký',
                    'thông báo cho người đăng ký',
                    'nguồn cấp dữ liệu nội dung đăng ký'
                ];
                const norm = (s) => ((s || '').normalize ? (s || '').normalize('NFC') : (s || ''))
                    .replace(/\\s+/g, ' ').trim().toLowerCase();

                const nodes = [];
                function walk(root, depth = 0) {{
                    if (!root || depth > 36) return;
                    if (root.nodeType === 1) {{
                        nodes.push(root);
                        if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                    }}
                    for (const c of root.children || []) walk(c, depth + 1);
                }}
                walk(document.body);

                function resolveCheckboxHost(el) {{
                    if (!el) return null;
                    const tag = (el.tagName || '').toUpperCase();
                    if (tag === 'YTCP-CHECKBOX-LIT' || tag === 'TP-YT-PAPER-CHECKBOX' || el.getAttribute('role') === 'checkbox' || (tag === 'INPUT' && el.type === 'checkbox')) {{
                        return el;
                    }}
                    const inner = el.querySelector && el.querySelector('ytcp-checkbox-lit, tp-yt-paper-checkbox, [role="checkbox"], input[type="checkbox"]');
                    if (inner) return inner;
                    if (el.shadowRoot) {{
                        const sInner = el.shadowRoot.querySelector('ytcp-checkbox-lit, tp-yt-paper-checkbox, [role="checkbox"], input[type="checkbox"]');
                        if (sInner) return sInner;
                    }}
                    return el;
                }}

                function readChecked(cb) {{
                    if (!cb) return null;
                    if (typeof cb.checked === 'boolean') return cb.checked;
                    const aria = cb.getAttribute && cb.getAttribute('aria-checked');
                    if (aria === 'true') return true;
                    if (aria === 'false') return false;
                    if (cb.hasAttribute && cb.hasAttribute('checked')) return true;
                    const roots = [cb, cb.shadowRoot].filter(Boolean);
                    for (const r of roots) {{
                        if (!r.querySelector) continue;
                        const innerChecked = r.querySelector('[aria-checked="true"], input[type="checkbox"]:checked, #checkbox.checked, div.checked');
                        if (innerChecked) return true;
                        const innerUnchecked = r.querySelector('[aria-checked="false"], #checkbox:not(.checked)');
                        if (innerUnchecked) {{
                            const inp = r.querySelector('input[type="checkbox"]');
                            if (inp && typeof inp.checked === 'boolean') return inp.checked;
                            return false;
                        }}
                    }}
                    return false;
                }}

                function readDisabled(cb) {{
                    if (!cb) return false;
                    if (cb.disabled === true) return true;
                    if (cb.hasAttribute && cb.hasAttribute('disabled')) return true;
                    if (cb.getAttribute && cb.getAttribute('aria-disabled') === 'true') return true;
                    const roots = [cb, cb.shadowRoot].filter(Boolean);
                    for (const r of roots) {{
                        if (!r.querySelector) continue;
                        const d = r.querySelector('[aria-disabled="true"], input:disabled, #checkbox[disabled]');
                        if (d) return true;
                    }}
                    return false;
                }}

                let matchedEl = document.querySelector('ytcp-checkbox-lit#notify-subscribers') ||
                                document.querySelector('tp-yt-paper-checkbox#notify-subscribers') ||
                                document.querySelector('#notify-subscribers ytcp-checkbox-lit') ||
                                document.querySelector('#notify-subscribers tp-yt-paper-checkbox') ||
                                document.querySelector('#notify-subscribers');
                let matchedBy = matchedEl ? 'direct_id' : null;

                if (!matchedEl) {{
                    matchedEl = nodes.find(el => {{
                        const id = (el.id || '').toLowerCase();
                        return id === 'notify-subscribers' || id.includes('notify-subscribers');
                    }});
                    if (matchedEl) matchedBy = 'shadow_id';
                }}

                if (!matchedEl) {{
                    for (const el of nodes) {{
                        if (!el.matches || !el.matches('ytcp-checkbox-lit, tp-yt-paper-checkbox, [role="checkbox"], ytcp-form-checkbox, label, .checkbox-container')) {{
                            continue;
                        }}
                        const ownTxt = norm(el.innerText || el.textContent || el.getAttribute('aria-label') || '');
                        const parentTxt = el.parentElement ? norm(el.parentElement.innerText || el.parentElement.textContent || '') : '';
                        const combined = ownTxt + ' ' + parentTxt;
                        if (phrases.some(p => combined.includes(p)) && combined.length < 450) {{
                            matchedEl = el;
                            matchedBy = 'text_match';
                            break;
                        }}
                    }}
                }}

                const cb = resolveCheckboxHost(matchedEl);
                if (!cb) {{
                    return {{ applied: false, changed: false, reason: 'notify_subscribers_checkbox_not_found' }};
                }}

                cb.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                const beforeChecked = Boolean(readChecked(cb));
                const isDisabled = readDisabled(cb) || readDisabled(matchedEl);

                if (beforeChecked === TARGET) {{
                    return {{
                        applied: true,
                        changed: false,
                        previous: beforeChecked,
                        checked: beforeChecked,
                        target: TARGET,
                        locked: isDisabled,
                        matched_by: matchedBy,
                    }};
                }}

                if (isDisabled) {{
                    return {{
                        applied: false,
                        changed: false,
                        previous: beforeChecked,
                        checked: beforeChecked,
                        target: TARGET,
                        locked: true,
                        reason: 'checkbox_disabled_or_already_published',
                        matched_by: matchedBy,
                    }};
                }}

                const clickCandidates = [];
                if (cb.shadowRoot) {{
                    const sTarget = cb.shadowRoot.querySelector('#checkbox, [role="checkbox"], input[type="checkbox"], .checkbox');
                    if (sTarget) clickCandidates.push(sTarget);
                }}
                if (cb.querySelector) {{
                    const lTarget = cb.querySelector('#checkbox, [role="checkbox"], input[type="checkbox"], .checkbox');
                    if (lTarget) clickCandidates.push(lTarget);
                }}
                clickCandidates.push(cb);
                if (matchedEl && matchedEl !== cb) clickCandidates.push(matchedEl);

                let afterChecked = beforeChecked;
                for (const targetNode of clickCandidates) {{
                    try {{
                        targetNode.click();
                    }} catch (e) {{}}
                    afterChecked = Boolean(readChecked(cb));
                    if (afterChecked === TARGET) break;
                }}

                return {{
                    applied: afterChecked === TARGET,
                    changed: afterChecked !== beforeChecked,
                    previous: beforeChecked,
                    checked: afterChecked,
                    target: TARGET,
                    locked: false,
                    matched_by: matchedBy,
                }};
            }})()
        """)
        logger.info("set_notify_subscribers(enabled=%s) -> %s", target_state, res)
        await asyncio.sleep(0.5)
        return res if isinstance(res, dict) else {"applied": False, "changed": False}

    async def ensure_and_select_playlist(
        self,
        playlist_title: str = DEFAULT_SU_KE_LAI_PLAYLIST,
    ) -> dict[str, Any]:
        """Select playlist in Details (ytcp-video-metadata-playlists), creating it in Studio if missing."""
        target_name = str(playlist_title or DEFAULT_SU_KE_LAI_PLAYLIST).strip()
        if not target_name:
            return {"applied": False, "reason": "empty_playlist_title"}

        logger.info("Ensuring & selecting playlist: %r...", target_name)
        target_json = json.dumps(target_name, ensure_ascii=False)

        # 1. Check if already selected on trigger and click trigger to open ytcp-playlist-dialog
        open_res = await self.evaluate(f"""
            (() => {{
                const TARGET = {target_json};
                const norm = (s) => ((s || '').normalize ? (s || '').normalize('NFC') : (s || ''))
                    .replace(/\\s+/g, ' ').trim().toLowerCase();
                const tNorm = norm(TARGET);
                const comp = document.querySelector('ytcp-video-metadata-playlists') ||
                             document.querySelector('#playlists') ||
                             document.querySelector('[id*="playlist"]');
                if (!comp) return {{ opened: false, reason: 'playlists_component_not_found' }};
                comp.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                const currentTxt = norm(comp.innerText || comp.textContent || '');
                const alreadySelected = Boolean(tNorm && currentTxt.includes(tNorm));
                const trigger = comp.querySelector('#select-button, ytcp-text-dropdown-trigger, ytcp-dropdown-trigger, #trigger, [role="button"], button') || comp;
                trigger.click();
                return {{ opened: true, already_selected: alreadySelected, trigger_text: (comp.innerText || '').trim().slice(0, 120) }};
            }})()
        """)
        if not (isinstance(open_res, dict) and open_res.get("opened")):
            logger.warning("Could not open playlist dropdown: %s", open_res)
            return {"applied": False, "created": False, "playlist_title": target_name, "detail": open_res}

        # Wait up to 4.5s for ytcp-playlist-dialog to render
        for _ in range(9):
            await asyncio.sleep(0.5)
            dlg_open = await self.evaluate("""
                Boolean(
                    document.querySelector('ytcp-playlist-dialog') ||
                    document.querySelector('tp-yt-paper-dialog ytcp-checkbox-group') ||
                    document.querySelector('#new-playlist-button')
                )
            """)
            if dlg_open:
                break

        # 2. Search for matching playlist checkbox inside ytcp-playlist-dialog
        select_js = f"""
            (() => {{
                const TARGET = {target_json};
                const norm = (s) => ((s || '').normalize ? (s || '').normalize('NFC') : (s || ''))
                    .replace(/\\s+/g, ' ').trim().toLowerCase();
                const tNorm = norm(TARGET);
                const tPrefix = tNorm.split(/[—–-]/)[0].trim();

                const dlg = document.querySelector('ytcp-playlist-dialog') ||
                            Array.from(document.querySelectorAll('tp-yt-paper-dialog, ytcp-dialog')).find(d => {{
                                const txt = norm(d.innerText || '');
                                return txt.includes('danh sách phát') || txt.includes('playlist');
                            }}) || document;

                const items = Array.from(dlg.querySelectorAll(
                    'ytcp-ve, li, label, ytcp-checkbox-lit, tp-yt-paper-checkbox, .playlist-item'
                ));
                for (const item of items) {{
                    const txt = norm(item.innerText || item.textContent || '');
                    if (!txt || txt.length > 180) continue;
                    if (txt === tNorm || txt.includes(tNorm) || (tPrefix.length >= 10 && txt.includes(tPrefix))) {{
                        const cb = (item.matches && item.matches('ytcp-checkbox-lit, tp-yt-paper-checkbox, [role="checkbox"]'))
                            ? item
                            : (item.querySelector('ytcp-checkbox-lit, tp-yt-paper-checkbox, [role="checkbox"], input[type="checkbox"]') || item);
                        const isChecked = cb.checked === true ||
                                          cb.getAttribute('aria-checked') === 'true' ||
                                          cb.hasAttribute('checked') ||
                                          Boolean(cb.querySelector && cb.querySelector('[aria-checked="true"], input:checked, #checkbox.checked')) ||
                                          Boolean(cb.shadowRoot && cb.shadowRoot.querySelector('[aria-checked="true"], input:checked, #checkbox.checked'));
                        if (!isChecked) {{
                            const clickTarget = (cb.shadowRoot && cb.shadowRoot.querySelector('#checkbox, [role="checkbox"], input')) ||
                                                (cb.querySelector && cb.querySelector('#checkbox, [role="checkbox"], input')) ||
                                                cb;
                            clickTarget.click();
                        }}
                        return {{ found: true, was_checked: isChecked, matched_text: txt.slice(0, 120) }};
                    }}
                }}
                return {{ found: false, item_count: items.length }};
            }})()
        """
        pick_res = await self.evaluate(select_js)
        created = False

        if not (isinstance(pick_res, dict) and pick_res.get("found")):
            logger.info("Playlist %r not found in dialog (%s); creating new playlist in Studio...", target_name, pick_res)
            clicked_new = await self.evaluate("""
                (() => {
                    const dlg = document.querySelector('ytcp-playlist-dialog') || document;
                    const newBtn = dlg.querySelector('#new-playlist-button') ||
                                   dlg.querySelector('ytcp-button#new-playlist-button') ||
                                   Array.from(dlg.querySelectorAll('ytcp-button, button, tp-yt-paper-item')).find(b => {
                                       const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                       return t.includes('danh sách phát mới') || t.includes('new playlist');
                                   });
                    if (newBtn) {
                        newBtn.click();
                        return true;
                    }
                    return false;
                })()
            """)
            if clicked_new:
                await asyncio.sleep(1.0)
                # Click dropdown submenu item "Danh sách phát mới" / "New playlist" if a paper-menu opened
                await self.evaluate("""
                    (() => {
                        const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, [role="menuitem"]'));
                        const match = items.find(it => {
                            const r = it.getBoundingClientRect ? it.getBoundingClientRect() : null;
                            if (!r || r.width <= 0 || r.height <= 0) return false;
                            const t = (it.innerText || it.textContent || '').trim().toLowerCase();
                            return t.includes('danh sách phát mới') || t.includes('new playlist');
                        });
                        if (match) match.click();
                    })()
                """)
                await asyncio.sleep(1.2)

                # Fill playlist title in creation dialog/form and click Create / Tạo
                create_res = await self.evaluate(f"""
                    (() => {{
                        const TITLE = {target_json};
                        const createDlg = document.querySelector('ytcp-playlist-creation-dialog') ||
                                          document.querySelector('ytcp-create-playlist-dialog') ||
                                          document.querySelector('#create-playlist-form') ||
                                          Array.from(document.querySelectorAll('tp-yt-paper-dialog, ytcp-dialog')).find(d => {{
                                              const t = (d.innerText || '').toLowerCase();
                                              return (t.includes('tạo danh sách phát') || t.includes('create playlist') || t.includes('danh sách phát mới')) &&
                                                     !d.matches('ytcp-uploads-dialog');
                                          }}) ||
                                          document.querySelector('ytcp-playlist-dialog');
                        if (!createDlg) return {{ created: false, reason: 'no_create_dialog' }};

                        const box = createDlg.querySelector('#title-textarea #textbox') ||
                                    createDlg.querySelector('#create-playlist-form #textbox') ||
                                    createDlg.querySelector('#textbox[contenteditable="true"]') ||
                                    createDlg.querySelector('input#text-input, input[type="text"], textarea');
                        if (!box) return {{ created: false, reason: 'no_title_input' }};

                        box.focus();
                        try {{
                            document.execCommand('selectAll', false, null);
                            document.execCommand('delete', false, null);
                            document.execCommand('insertText', false, TITLE);
                        }} catch (e) {{}}
                        if (box.value !== undefined && box.value !== TITLE) {{
                            box.value = TITLE;
                        }} else if (box.isContentEditable && !(box.innerText || '').trim()) {{
                            box.textContent = TITLE;
                        }}
                        box.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                        box.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));

                        const createBtn = createDlg.querySelector('#create-button') ||
                                          createDlg.querySelector('ytcp-button#create-button') ||
                                          Array.from(createDlg.querySelectorAll('ytcp-button, button')).find(b => {{
                                              const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                              return t === 'tạo' || t === 'create';
                                          }});
                        if (createBtn) {{
                            createBtn.click();
                            return {{ created: true }};
                        }}
                        return {{ created: false, reason: 'no_create_button' }};
                    }})()
                """)
                logger.info("Create playlist dialog result: %s", create_res)
                if isinstance(create_res, dict) and create_res.get("created"):
                    created = True
                    await asyncio.sleep(2.2)
                    pick_res = await self.evaluate(select_js)

        # 3. Click Done / Xong on ytcp-playlist-dialog
        await self.evaluate("""
            (() => {
                const dlg = document.querySelector('ytcp-playlist-dialog') || document;
                const doneBtn = dlg.querySelector('ytcp-playlist-dialog #done-button') ||
                                dlg.querySelector('ytcp-button#done-button') ||
                                Array.from(dlg.querySelectorAll('ytcp-button, button')).find(b => {
                                    const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                    return t === 'xong' || t === 'done';
                                });
                if (doneBtn) {
                    doneBtn.click();
                }
            })()
        """)
        await asyncio.sleep(0.8)
        applied = bool((isinstance(pick_res, dict) and pick_res.get("found")) or created or open_res.get("already_selected"))
        return {
            "applied": applied,
            "created": created,
            "playlist_title": target_name,
            "pick_result": pick_res,
        }

    select_or_create_playlist = ensure_and_select_playlist

    async def attach_endscreen_template(
        self,
        video_url_or_id: Optional[str] = None,
        template_preference: str = "two_elements",
    ) -> dict[str, Any]:
        """Attach 2-element End Screen template (Best for viewer + Most recent upload / Subscribe) in Video Elements or /video/<VID>/edit."""
        if video_url_or_id:
            vid_id = str(video_url_or_id).strip()
            if "v=" in vid_id:
                vid_id = vid_id.split("v=")[1].split("&")[0]
            elif "/" in vid_id:
                vid_id = vid_id.rstrip("/").split("/")[-1].split("?")[0]
            cur_url = str(await self.evaluate("window.location.href") or "")
            if vid_id and f"/video/{vid_id}/edit" not in cur_url:
                edit_url = f"https://studio.youtube.com/video/{vid_id}/edit"
                logger.info("Navigating to %s for End Screen attachment...", edit_url)
                await self.call("Page.navigate", {"url": edit_url})
                await asyncio.sleep(3.5)
                await self.dismiss_studio_interstitials()

        # 1. Click #endscreens-button / #endscreen-editor-link on Video Elements or /edit right rail
        clicked_open = await self.evaluate("""
            (() => {
                let btn = document.querySelector('#endscreens-button') ||
                          document.querySelector('ytcp-button#endscreens-button') ||
                          document.querySelector('#endscreen-editor-link') ||
                          document.querySelector('a#endscreen-editor-link') ||
                          document.querySelector('[test-id="endscreens-button"]');
                if (!btn) {
                    const rows = Array.from(document.querySelectorAll(
                        'ytcp-video-elements-row, ytcp-elements-row, .element-row, ytcp-form-select, [role="row"]'
                    ));
                    const esRow = rows.find(r => {
                        const t = (r.innerText || r.textContent || '').toLowerCase();
                        return t.includes('màn hình kết thúc') || t.includes('end screen');
                    });
                    if (esRow) {
                        btn = esRow.querySelector('#endscreens-button, #add-button, #edit-button, ytcp-button, button, a') || esRow;
                    }
                }
                if (!btn) {
                    btn = Array.from(document.querySelectorAll('ytcp-button, button, a, [role="button"]')).find(el => {
                        const t = (el.innerText || el.textContent || el.getAttribute('aria-label') || '').trim().toLowerCase();
                        return t === 'màn hình kết thúc' || t === 'end screen' || t.includes('màn hình kết thúc');
                    });
                }
                if (btn) {
                    btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        if not clicked_open:
            logger.warning("End Screen trigger button (#endscreens-button) not found.")
            return {"applied": False, "saved": False, "reason": "endscreens_button_not_found"}

        # 2. Wait up to 8s for ytve-endscreen-editor-modal to mount
        modal_ready = False
        for _ in range(16):
            await asyncio.sleep(0.5)
            modal_ready = bool(
                await self.evaluate("""
                    Boolean(
                        document.querySelector('ytve-endscreen-editor-modal') ||
                        document.querySelector('ytve-endscreen-template-picker') ||
                        document.querySelector('ytve-endscreen-editor-options-panel') ||
                        document.querySelector('ytve-modal-host #save-button')
                    )
                """)
            )
            if modal_ready:
                break

        if not modal_ready:
            logger.warning("End Screen editor modal did not open within 8s.")
            return {"applied": False, "saved": False, "reason": "endscreen_modal_not_opened"}

        await asyncio.sleep(1.0)

        # 3. Apply 2-element template (2 videos: Best for viewer + Most recent upload, or 1 video + 1 subscribe)
        template_res = await self.evaluate("""
            (() => {
                const modal = document.querySelector('ytve-endscreen-editor-modal') ||
                              document.querySelector('ytve-modal-host') ||
                              document;
                const nodes = [];
                function walk(root, depth = 0) {
                    if (!root || depth > 28) return;
                    if (root.nodeType === 1) {
                        nodes.push(root);
                        if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                    }
                    for (const c of root.children || []) walk(c, depth + 1);
                }
                walk(modal);

                // Prefer 2-video or 1-video+1-subscribe template cards inside ytve-endscreen-template-picker
                // Strictly exclude 'Import from video' / 'Nhập từ video' buttons!
                const cards = nodes.filter(el => {
                    if (!el.matches) return false;
                    if (el.matches('ytve-endscreen-template-preview, .template-preview, .card, [role="button"]')) {
                        const txt = (el.innerText || el.textContent || el.getAttribute('aria-label') || '').trim().toLowerCase();
                        if (txt.includes('nhập') || txt.includes('import')) return false;
                        return txt.includes('2 video') ||
                               txt.includes('1 video') ||
                               (el.closest('ytve-endscreen-template-picker') !== null && !el.matches('ytcp-button, button'));
                    }
                    return false;
                });

                const oneVidSubCard = cards.find(c => {
                    const t = (c.innerText || c.textContent || c.getAttribute('aria-label') || '').toLowerCase();
                    return t.includes('1 video') && (t.includes('đăng ký') || t.includes('subscribe'));
                });
                const twoVidCard = cards.find(c => {
                    const t = (c.innerText || c.textContent || c.getAttribute('aria-label') || '').toLowerCase();
                    return t.includes('2 video');
                });
                const chosenCard = twoVidCard || oneVidSubCard || cards[0] || null;
                if (chosenCard) {
                    chosenCard.scrollIntoView({ behavior: 'instant', block: 'center' });
                    const inner = chosenCard.querySelector('.template-preview, button, [role="button"]') || chosenCard;
                    inner.click();
                    return { method: 'template_card', label: (chosenCard.innerText || chosenCard.getAttribute('aria-label') || 'template').trim().slice(0, 80) };
                }

                // Fallback: click + Element / + Thành phần (#add-element-button) and pick Video
                const addBtn = nodes.find(el => {
                    if (!el.matches || !el.matches('ytcp-button, button, #add-element-button')) return false;
                    const t = (el.innerText || el.textContent || el.getAttribute('aria-label') || '').toLowerCase();
                    return el.id === 'add-element-button' || t.includes('thành phần') || t.includes('element');
                });
                if (addBtn) {
                    addBtn.click();
                    return { method: 'add_element_button_clicked' };
                }
                return { method: 'existing_or_none', card_count: cards.length };
            })()
        """)
        logger.info("End screen template selection step: %s", template_res)
        await asyncio.sleep(1.0)

        if isinstance(template_res, dict) and template_res.get("method") == "add_element_button_clicked":
            # Select 'Video' from the element menu
            await self.evaluate("""
                (() => {
                    const items = Array.from(document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu-item, [role="menuitem"]'));
                    const vidItem = items.find(it => {
                        const t = (it.innerText || it.textContent || '').trim().toLowerCase();
                        return t === 'video' || t.startsWith('video') || it.getAttribute('test-id') === 'VIDEO';
                    });
                    if (vidItem) vidItem.click();
                })()
            """)
            await asyncio.sleep(1.0)

        # Ensure every video element on the endscreen canvas has a valid auto-resolved video type (BEST_FOR_VIEWER or MOST_RECENT_UPLOAD)
        # so no element is left in the invalid empty "Choose specific video" state
        await self.evaluate("""
            (() => {
                const modal = document.querySelector('ytve-endscreen-editor-modal') || document;
                const elBoxes = Array.from(modal.querySelectorAll(
                    'ytve-endscreen-element-box, .endscreen-element, ytve-endscreen-editor-timeline-row'
                ));
                const pickRadio = (preferMostRecent) => {
                    const radios = Array.from(modal.querySelectorAll('tp-yt-paper-radio-button, [role="radio"]'));
                    const best = radios.find(r => {
                        const t = (r.innerText || r.textContent || '').toLowerCase();
                        return r.getAttribute('name') === 'BEST_FOR_VIEWER' ||
                               t.includes('phù hợp nhất với người xem') ||
                               t.includes('best for viewer');
                    });
                    const recent = radios.find(r => {
                        const t = (r.innerText || r.textContent || '').toLowerCase();
                        return r.getAttribute('name') === 'MOST_RECENT_UPLOAD' ||
                               t.includes('tải lên gần đây nhất') ||
                               t.includes('most recent upload');
                    });
                    const target = preferMostRecent ? (recent || best) : (best || recent);
                    if (target && target.getAttribute('aria-checked') !== 'true') {
                        target.click();
                    }
                };
                if (elBoxes.length > 0) {
                    elBoxes.forEach((box, idx) => {
                        try { box.click(); } catch (e) {}
                        pickRadio(idx % 2 === 1);
                    });
                } else {
                    pickRadio(false);
                }
            })()
        """)
        await asyncio.sleep(0.8)

        # 4. Click #save-button inside ytve-endscreen-editor-modal (verifying >= 1 element exists if disabled)
        save_res = await self.evaluate("""
            (() => {
                const modal = document.querySelector('ytve-endscreen-editor-modal') ||
                              document.querySelector('ytve-modal-host') ||
                              document.querySelector('ytcp-dialog') ||
                              document;
                const elCount = modal.querySelectorAll(
                    'ytve-endscreen-element-box, .endscreen-element, ytve-endscreen-editor-timeline-row, [test-id*="element"]'
                ).length;
                const saveBtn = modal.querySelector('ytve-endscreen-editor-modal #save-button') ||
                                modal.querySelector('ytve-modal-host #save-button') ||
                                modal.querySelector('#save-button') ||
                                Array.from(modal.querySelectorAll('ytcp-button, button')).find(b => {
                                    if (b.id === 'next-button' || b.id === 'save') return false;
                                    const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                    return t === 'lưu' || t === 'save';
                                });
                if (!saveBtn) return { clicked: false, reason: 'no_save_button', element_count: elCount };
                const disabled = saveBtn.hasAttribute('disabled') || saveBtn.getAttribute('aria-disabled') === 'true';
                if (disabled) {
                    return {
                        clicked: false,
                        disabled: true,
                        has_elements: elCount >= 1,
                        element_count: elCount,
                        reason: elCount >= 1 ? 'already_saved_or_unchanged' : 'disabled_with_zero_elements',
                    };
                }
                saveBtn.click();
                return { clicked: true, element_count: elCount };
            })()
        """)
        logger.info("End screen #save-button result: %s", save_res)
        saved = bool(isinstance(save_res, dict) and save_res.get("clicked"))
        already_saved = bool(
            isinstance(save_res, dict)
            and save_res.get("disabled")
            and (save_res.get("has_elements") or (isinstance(template_res, dict) and template_res.get("method") == "template_card"))
        )

        # Wait up to 6s for modal to close; if still open (e.g. already_saved), close cleanly via #discard-button / #close-button
        for _ in range(12):
            await asyncio.sleep(0.5)
            still_open = await self.evaluate("""
                (() => {
                    const m = document.querySelector('ytve-endscreen-editor-modal');
                    if (!m) return false;
                    const r = m.getBoundingClientRect ? m.getBoundingClientRect() : null;
                    return Boolean(m.offsetParent !== null || (r && r.width > 0 && r.height > 0));
                })()
            """)
            if not still_open:
                break
        else:
            await self.evaluate("""
                (() => {
                    const m = document.querySelector('ytve-endscreen-editor-modal') || document;
                    const closeBtn = m.querySelector('#discard-button, #close-button, #cancel-button, button[aria-label*="Đóng"], button[aria-label*="Close"]');
                    if (closeBtn) {
                        const inner = closeBtn.querySelector('button') || closeBtn;
                        inner.click();
                        if (inner !== closeBtn) closeBtn.click();
                    }
                })()
            """)
            await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
            await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 27, "key": "Escape", "code": "Escape"})
            await asyncio.sleep(0.5)

        return {
            "applied": bool(saved or already_saved),
            "saved": saved,
            "already_saved": already_saved,
            "template": template_res,
            "preference": template_preference,
        }

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

        thumb_bytes = os.path.getsize(path_str)
        if thumb_bytes > 2 * 1024 * 1024:
            logger.error(
                "Thumbnail exceeds YouTube 2MB limit (%d bytes > 2097152 bytes): %s",
                thumb_bytes,
                path_str,
            )
            if strict_thumbnail:
                raise RuntimeError(
                    f"CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED: Thumbnail exceeds 2MB limit ({thumb_bytes} bytes): {path_str}"
                )
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
            logger.info("Thumbnail attached via file input. Polling preview & Tier-2 state...")
            await asyncio.sleep(1.0)

            has_verify = False
            thumb_state: dict[str, Any] = {"ok": False, "reason": "not_checked"}
            for _ in range(10):
                # Check for verification or blocking modal first
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
                    break

                # Inspect real preview state inside ytcp-thumbnail-uploader (never match hidden /edit placeholder or auto stills)
                thumb_state = await self.evaluate("""
                    (() => {
                        const uploader = document.querySelector('ytcp-thumbnail-uploader');
                        if (!uploader) {
                            return { ok: false, reason: 'no_uploader' };
                        }
                        const tooltipIcon = uploader.querySelector('#select-tooltip-icon, [icon="yt-sys-icons:help"]');
                        const tooltipVisible = Boolean(tooltipIcon && tooltipIcon.offsetParent !== null);
                        const previewBtn = uploader.querySelector('#preview-button');
                        const previewVisible = Boolean(previewBtn && previewBtn.offsetParent !== null);
                        const selectBtn = uploader.querySelector('#select-button');
                        const selectVisible = Boolean(selectBtn && selectBtn.offsetParent !== null);
                        const hasSelectedAttr = uploader.hasAttribute('selected');

                        const imgs = Array.from(uploader.querySelectorAll('img[src]'));
                        const validImg = imgs.find(img => {
                            const src = (img.getAttribute('src') || img.src || '').trim();
                            if (!src) return false;
                            if (
                                src.includes('placeholder') ||
                                src.includes('/edit') ||
                                src.includes('/upload') ||
                                src.includes('studio.youtube.com/channel')
                            ) {
                                return false;
                            }
                            const visible = img.offsetParent !== null;
                            const loaded = (img.naturalWidth || 0) > 0;
                            const isCustomSrc = (
                                src.startsWith('blob:') ||
                                src.startsWith('data:image/') ||
                                src.includes('ytimg.com') ||
                                src.includes('googleusercontent.com')
                            );
                            return visible && loaded && isCustomSrc;
                        });

                        const ok = Boolean(
                            validImg &&
                            !tooltipVisible &&
                            (hasSelectedAttr || previewVisible || !selectVisible)
                        );
                        return {
                            ok,
                            tooltipVisible,
                            previewVisible,
                            selectVisible,
                            hasSelectedAttr,
                            matchedSrc: validImg ? (validImg.getAttribute('src') || validImg.src || '').slice(0, 120) : null,
                        };
                    })()
                """) or {"ok": False, "reason": "eval_none"}

                if thumb_state.get("ok"):
                    break
                if thumb_state.get("tooltipVisible") and not thumb_state.get("previewVisible"):
                    logger.warning("Tier-2 tooltip icon (?) visible on thumbnail uploader: %s", thumb_state)
                    break
                await asyncio.sleep(0.8)

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

            if thumb_state and thumb_state.get("ok"):
                logger.info("Custom thumbnail preview verified successfully: %s", thumb_state.get("matchedSrc"))
                return True

            logger.warning("Custom thumbnail preview NOT confirmed (state=%s).", thumb_state)
            if strict_thumbnail:
                raise RuntimeError(f"CUSTOM_THUMBNAIL_REJECTED_OR_TIER2_REQUIRED: {thumb_state}")
            return False
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
                                        Array.from(document.querySelectorAll('ytcp-navigation-item, tp-yt-paper-icon-item, button, a')).find(el => {
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
                    # 2. Wait up to 5s for Channel / Kênh nav item inside lazy-mounted dialog and click it
                    for _ in range(10):
                        await asyncio.sleep(0.5)
                        ch_clicked = await self.evaluate("""
                            (() => {
                                const dlg = document.querySelector('ytcp-settings-dialog') || document;
                                const allEls = [];
                                function walk(root, depth = 0) {
                                    if (!root || depth > 14) return;
                                    if (root.nodeType === 1) {
                                        allEls.push(root);
                                        if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                                    }
                                    for (const c of root.children || []) walk(c, depth + 1);
                                }
                                walk(dlg);
                                const channelTab =
                                    allEls.find(el => (el.matches && el.matches('li#channel, [role="menuitem"]#channel')) && ((el.innerText || '').trim().toLowerCase() === 'kênh' || (el.innerText || '').trim().toLowerCase() === 'channel')) ||
                                    allEls.find(el => {
                                        if (!el.matches || !el.matches('li, [role="menuitem"], tp-yt-paper-tab, ytcp-navigation-item, .navigation-item, [role="tab"], tp-yt-paper-item, span.title-text')) return false;
                                        const text = (el.innerText || '').trim().toLowerCase();
                                        return text === 'kênh' || text === 'channel';
                                    });
                                if (channelTab) {
                                    const clickable = (channelTab.closest && channelTab.closest('li, [role="menuitem"], ytcp-navigation-item, tp-yt-paper-tab')) || channelTab;
                                    clickable.click();
                                    if (clickable !== channelTab) channelTab.click();
                                    return true;
                                }
                                return false;
                            })()
                        """)
                        if ch_clicked:
                            break

                    # 3. Wait up to 3.5s for Feature eligibility / Điều kiện sử dụng tính năng tab and click it
                    for _ in range(7):
                        await asyncio.sleep(0.5)
                        feat_clicked = await self.evaluate("""
                            (() => {
                                const dlg = document.querySelector('ytcp-settings-dialog') || document;
                                const allEls = [];
                                function walk(root, depth = 0) {
                                    if (!root || depth > 14) return;
                                    if (root.nodeType === 1) {
                                        allEls.push(root);
                                        if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                                    }
                                    for (const c of root.children || []) walk(c, depth + 1);
                                }
                                walk(dlg);
                                const featTab = allEls.find(t => {
                                    if (!t.matches || !t.matches('tp-yt-paper-tab, [role="tab"], .tab-header, button')) return false;
                                    const text = (t.innerText || '').trim().toLowerCase();
                                    return text === 'điều kiện sử dụng tính năng' ||
                                           text === 'feature eligibility' ||
                                           text.includes('điều kiện sử dụng tính năng') ||
                                           text.includes('feature eligibility');
                                });
                                if (featTab) {
                                    featTab.click();
                                    return true;
                                }
                                return false;
                            })()
                        """)
                        if feat_clicked:
                            break

                    # Wait up to 3.5s for tier cards/text to render inside dialog
                    for _ in range(7):
                        await asyncio.sleep(0.5)
                        tiers_mounted = await self.evaluate("""
                            (() => {
                                const dlg = document.querySelector('ytcp-settings-dialog') || document;
                                const txt = (dlg.innerText || '').toLowerCase();
                                return txt.includes('tính năng bậc trung') || txt.includes('intermediate features') || txt.includes('tính năng cơ bản') || txt.includes('standard features');
                            })()
                        """)
                        if tiers_mounted:
                            break

                    # 4. Inspect Tier Rows (Shadow-DOM + TrustTiers classes + bounded line parser)
                    tier_res = await self.evaluate("""
                        (() => {
                            const dlg = document.querySelector('ytcp-settings-dialog') || document;
                            const STATUS_TOKENS = [
                                'đã bật', 'enabled',
                                'đủ điều kiện', 'eligible',
                                'đang chờ xử lý', 'pending',
                                'bị tắt', 'disabled',
                                'chưa đủ điều kiện', 'ineligible',
                                'tạm thời không dùng được', 'temporarily unavailable'
                            ];
                            function matchStatusLine(line) {
                                const l = (line || '').trim().toLowerCase();
                                if (!l) return '';
                                if (STATUS_TOKENS.includes(l)) return line.trim();
                                return '';
                            }
                            function getStatus(section) {
                                if (!section) return '';
                                const badges = section.querySelectorAll('.ytTrustTiersHomeLevelFeatureLevelStatusBar .label, .ytTrustTiersHomeLevelFeatureLevelStatusBar ytcp-badge, .ytTrustTiersHomeLevelFeatureLevelStatusBar, .status, .badge, ytcp-chip, ytcp-badge .label, ytcp-badge, .feature-status, [class*="status"], [class*="badge"]');
                                for (const badge of badges) {
                                    const bt = (badge.innerText || '').trim();
                                    if (matchStatusLine(bt)) return matchStatusLine(bt);
                                }
                                const lines = (section.innerText || '').split('\\n').map(l => l.trim()).filter(Boolean);
                                for (const line of lines) {
                                    const m = matchStatusLine(line);
                                    if (m) return m;
                                }
                                return '';
                            }

                            const allEls = [];
                            function walk(root, depth = 0) {
                                if (!root || depth > 14) return;
                                if (root.nodeType === 1) {
                                    allEls.push(root);
                                    if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                                }
                                for (const c of root.children || []) walk(c, depth + 1);
                            }
                            walk(dlg);

                            let t1 = '';
                            let t2 = '';
                            let t3 = '';

                            // Primary selector: modern YouTube Trust Tiers components (.ytTrustTiersHomeLevelFeatureLevelName)
                            const levelHeaders = allEls.filter(el =>
                                el.classList && el.classList.contains('ytTrustTiersHomeLevelFeatureLevelName')
                            );
                            for (const hdr of levelHeaders) {
                                const htxt = (hdr.innerText || '').trim().toLowerCase();
                                let container = hdr.parentElement;
                                let statusFound = '';
                                for (let step = 0; step < 4 && container; step++) {
                                    statusFound = getStatus(container);
                                    if (statusFound) break;
                                    container = container.parentElement;
                                }
                                if ((htxt.includes('cơ bản') || htxt.includes('chuẩn') || htxt.includes('standard')) && !t1) {
                                    t1 = statusFound;
                                } else if ((htxt.includes('bậc trung') || htxt.includes('intermediate')) && !t2) {
                                    t2 = statusFound;
                                } else if ((htxt.includes('nâng cao') || htxt.includes('advanced')) && !t3) {
                                    t3 = statusFound;
                                }
                            }

                            // Secondary selector: legacy feature sections
                            const sections = allEls.filter(el =>
                                el.matches && el.matches('ytcp-feature-eligibility-section, .feature-section, ytcp-settings-section, tp-yt-paper-item, div[role="region"], .tier-container, .section')
                            );
                            for (const s of sections) {
                                const t = (s.innerText || '').toLowerCase();
                                if ((t.includes('cơ bản') || t.includes('chuẩn') || t.includes('standard')) && !t1) {
                                    t1 = getStatus(s);
                                }
                                if ((t.includes('bậc trung') || t.includes('intermediate') || t.includes('15 phút') || t.includes('15 minutes')) && !t2) {
                                    t2 = getStatus(s);
                                }
                                if ((t.includes('nâng cao') || t.includes('advanced')) && !t3) {
                                    t3 = getStatus(s);
                                }
                            }

                            // Fallback: bounded line-by-line parser over dlg.innerText (never bleeds Tier 1 status into Tier 2)
                            const rawLines = (dlg.innerText || '').split('\\n').map(l => l.trim()).filter(Boolean);
                            let currentTier = 0;
                            for (const line of rawLines) {
                                const low = line.toLowerCase();
                                if (/^1\\./.test(low) && (low.includes('cơ bản') || low.includes('chuẩn') || low.includes('standard'))) {
                                    currentTier = 1;
                                    continue;
                                }
                                if (/^2\\./.test(low) && (low.includes('bậc trung') || low.includes('intermediate'))) {
                                    currentTier = 2;
                                    continue;
                                }
                                if (/^3\\./.test(low) && (low.includes('nâng cao') || low.includes('advanced'))) {
                                    currentTier = 3;
                                    continue;
                                }
                                if (low === 'đóng' || low === 'close' || low === 'lưu' || low === 'save') {
                                    currentTier = 0;
                                    continue;
                                }
                                const matched = matchStatusLine(line);
                                if (matched) {
                                    if (currentTier === 1 && !t1) t1 = matched;
                                    else if (currentTier === 2 && !t2) t2 = matched;
                                    else if (currentTier === 3 && !t3) t3 = matched;
                                }
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
                    'ytcp-video-metadata-related-video',
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
                        const btn = el.querySelector('.container, ytcp-button, button, #trigger, .dropdown-trigger, .edit-button') || el;
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

    async def clear_related_video_post_publish(
        self,
        short_url_or_id: str,
        *,
        edit_screenshot_path: Optional[str | Path] = None,
    ) -> dict[str, Any]:
        """Navigate to Studio video edit page for a Short, remove the linked Related Video, and Save."""
        short_id = short_url_or_id.strip().rstrip("/").split("/")[-1].split("?")[0]
        edit_url = f"https://studio.youtube.com/video/{short_id}/edit"
        logger.info("Navigating to Short edit page to clear Related Video: %s", edit_url)
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(4.0)

        for _ in range(4):
            d = await self.dismiss_studio_interstitials()
            if d:
                logger.info("Dismissed Studio interstitial banner.")
                await asyncio.sleep(3.0)
                break
            await asyncio.sleep(1.0)

        for _ in range(15):
            has_editor = await self.evaluate("""
                Boolean(document.querySelector('#linked-video-editor-link, ytcp-shorts-content-links-picker, #description-textarea'))
            """)
            if has_editor:
                break
            await self.dismiss_studio_interstitials()
            await asyncio.sleep(1.0)

        before_title = await self.evaluate("""
            (() => {
                const el = document.querySelector('#linked-video-editor-link .dropdown-trigger-text, ytcp-shorts-content-links-picker .dropdown-trigger-text');
                return el ? el.innerText.trim() : null;
            })()
        """)
        logger.info("Related video before clear for %s: %r", short_id, before_title)

        clicked_delete = await self.evaluate("""
            (() => {
                const clearBtn = document.querySelector(
                    '#linked-video-editor-link #right-icon, ytcp-shorts-content-links-picker #right-icon'
                );
                if (clearBtn) {
                    clearBtn.scrollIntoView({ behavior: 'instant', block: 'center' });
                    clearBtn.click();
                    return { found: true, clicked: true, selector: '#right-icon' };
                }
                return { found: false, clicked: false, reason: 'no_right_icon_found' };
            })()
        """)
        logger.info("Clear related video click result for %s: %s", short_id, clicked_delete)

        saved = False
        if clicked_delete and clicked_delete.get("clicked"):
            await asyncio.sleep(1.5)
            for i in range(20):
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
                    logger.info("Clicked Save after clearing Related Video (%ds).", i + 1)
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
                        logger.info("Clear Related Video save persisted after %ds.", j + 1)
                        break
                await asyncio.sleep(2.0)

        # Reload edit page and verify Related Video is empty
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(4.5)
        after_title = await self.evaluate("""
            (() => {
                const el = document.querySelector('#linked-video-editor-link .dropdown-trigger-text, ytcp-shorts-content-links-picker .dropdown-trigger-text');
                return el ? el.innerText.trim() : null;
            })()
        """)
        if edit_screenshot_path:
            out_p = Path(edit_screenshot_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            await self.capture_screenshot(out_p)

        cleared_ok = (not after_title) or (after_title in ("Không có", "None", ""))
        live_check = verify_short_live(short_id)
        return {
            "success": bool(cleared_ok),
            "video_id": short_id,
            "before_title": before_title,
            "after_title": after_title,
            "clicked_delete": clicked_delete,
            "saved": saved,
            "live_has_pill": bool(live_check.get("has_pill", False)),
            "screenshot": str(edit_screenshot_path) if edit_screenshot_path else None,
        }

    async def update_video_thumbnail_post_publish(
        self,
        video_url_or_id: str,
        thumbnail_path: str | Path,
        *,
        edit_screenshot_path: Optional[str | Path] = None,
        strict_thumbnail: bool = False,
    ) -> dict[str, Any]:
        """Navigate to Studio video edit page, upload custom thumbnail, click #save, and verify reload."""
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
        uploaded = await self.upload_thumbnail(path_str, strict_thumbnail=strict_thumbnail)
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
            edit_verify = await self.verify_video_edit_page(
                vid_id,
                screenshot_path=edit_screenshot_path,
            )
            has_custom = bool(edit_verify.get("has_custom_thumbnail"))
            logger.info("Post-save reload check for %s: has_custom_thumbnail=%s", vid_id, has_custom)
            if strict_thumbnail and not has_custom:
                return {
                    "success": False,
                    "video_id": vid_id,
                    "thumbnail_path": path_str,
                    "error": "custom_thumbnail_not_persisted_on_reload",
                    "edit_verification": edit_verify,
                }
            return {
                "success": True,
                "video_id": vid_id,
                "thumbnail_path": path_str,
                "has_custom_thumbnail": has_custom,
                "edit_verification": edit_verify,
            }

        logger.warning("Could not click save button for thumbnail or save was not enabled.")
        return {"success": False, "video_id": vid_id, "error": "save_button_not_clicked"}

    async def _click_editor_save_and_wait(self, max_wait_sec: float = 20.0) -> bool:
        """Click #save on /video/<VID>/edit, dismiss any precheck confirmation dialog, and wait for persistence."""
        clicked = False
        steps = max(4, int(max_wait_sec * 2))
        for _ in range(steps):
            save_info = await self.evaluate("""
                (() => {
                    const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                    if (!saveBtn) return { found: false };
                    const disabled = saveBtn.hasAttribute('disabled') || saveBtn.getAttribute('aria-disabled') === 'true';
                    const inner = saveBtn.querySelector('button') || saveBtn;
                    if (!disabled && !inner.disabled) {
                        inner.click();
                        return { found: true, clicked: true };
                    }
                    return { found: true, clicked: false, disabled: true };
                })()
            """)
            if isinstance(save_info, dict) and save_info.get("clicked"):
                clicked = True
                break
            await asyncio.sleep(0.5)

        if not clicked:
            return False

        for _ in range(int(max_wait_sec)):
            await asyncio.sleep(1.0)
            # Click any precheck / confirmation dialog ('Vẫn lưu', 'Save anyway', 'Vẫn lên lịch')
            await self.evaluate("""
                (() => {
                    const targets = ['vẫn lưu', 'save anyway', 'vẫn lên lịch', 'schedule anyway', 'vẫn xuất bản', 'publish anyway'];
                    const dlgs = Array.from(document.querySelectorAll('ytcp-confirmation-dialog, ytcp-prechecks-warning-dialog, tp-yt-paper-dialog, ytcp-dialog'));
                    for (const d of dlgs) {
                        const r = d.getBoundingClientRect ? d.getBoundingClientRect() : null;
                        if (!r || r.width <= 0 || r.height <= 0) continue;
                        const btns = Array.from(d.querySelectorAll('ytcp-button, button, #confirm-button, #secondary-action-button'));
                        for (const b of btns) {
                            const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                            if (targets.includes(txt) || b.id === 'confirm-button') {
                                const inner = b.querySelector('button') || b;
                                inner.click();
                                if (inner !== b) b.click();
                                return true;
                            }
                        }
                    }
                    return false;
                })()
            """)
            is_clean = await self.evaluate("""
                (() => {
                    const saveBtn = document.querySelector('ytcp-button#save, #save-button, ytcp-video-metadata-editor #save');
                    return saveBtn ? (saveBtn.hasAttribute('disabled') || saveBtn.getAttribute('aria-disabled') === 'true') : true;
                })()
            """)
            if is_clean:
                break
        await asyncio.sleep(1.0)
        return True

    async def attach_related_video_existing_short(
        self,
        short_vid: str,
        target_long_vid_or_title: str,
        *,
        target_title: Optional[str] = None,
        navigate_if_needed: bool = True,
        save_changes: bool = True,
        screenshot_path: Optional[str | Path] = None,
    ) -> dict[str, Any]:
        """Open /video/<SHORT_VID>/edit on an existing Scheduled/Public Short and link ytcp-video-metadata-related-video to parent Long."""
        short_id = str(short_vid or "").strip().rstrip("/").split("/")[-1].split("?")[0]
        if "v=" in short_id:
            short_id = short_id.split("v=")[1].split("&")[0]
        raw_target = str(target_long_vid_or_title or "").strip()
        if not short_id or not raw_target:
            return {"success": False, "linked_via_cdp": False, "short_id": short_id, "reason": "missing_short_or_target"}

        # Extract 11-char video ID if raw_target is a URL or ID
        target_id = raw_target.rstrip("/").split("/")[-1].split("?")[0]
        if "v=" in target_id:
            target_id = target_id.split("v=")[1].split("&")[0]
        is_vid_id = bool(re.match(r"^[A-Za-z0-9_-]{11}$", target_id))
        resolved_title = target_title or (fetch_youtube_title(target_id) if is_vid_id else raw_target)
        if not resolved_title and not is_vid_id:
            resolved_title = raw_target

        edit_url = f"https://studio.youtube.com/video/{short_id}/edit"
        if navigate_if_needed:
            cur_url = str(await self.evaluate("window.location.href") or "")
            if f"/video/{short_id}/edit" not in cur_url:
                logger.info("Navigating to Short /edit for Related Video linking: %s (target=%r, title=%r)", edit_url, raw_target, resolved_title)
                await self.call("Page.navigate", {"url": edit_url})
                await asyncio.sleep(3.5)
                await self.dismiss_studio_interstitials()

        # Wait up to 12s for Short metadata editor to hydrate
        for _ in range(24):
            has_editor = await self.evaluate("""
                Boolean(
                    document.querySelector('ytcp-video-metadata-related-video') ||
                    document.querySelector('#linked-video-editor-link') ||
                    document.querySelector('ytcp-shorts-content-links-picker') ||
                    document.querySelector('#title-textarea #textbox')
                )
            """)
            if has_editor:
                break
            await asyncio.sleep(0.5)

        # Pre-check existing linked related video text for idempotency or re-link clearing
        existing_link_text = str(
            await self.evaluate("""
                (() => {
                    const el = document.querySelector('ytcp-video-metadata-related-video .dropdown-trigger-text') ||
                               document.querySelector('#linked-video-editor-link .dropdown-trigger-text') ||
                               document.querySelector('ytcp-shorts-content-links-picker .dropdown-trigger-text');
                    return el ? (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim() : '';
                })()
            """)
            or ""
        )
        if existing_link_text and existing_link_text.lower() not in ("không có", "none", "chọn", "select"):
            rt_low = (resolved_title or "").lower().strip()
            rt_prefix = rt_low.split(":")[0].strip() if rt_low else ""
            ex_low = existing_link_text.lower()
            already_matches = bool(
                (rt_low and (rt_low in ex_low or ex_low in rt_low))
                or (rt_prefix and len(rt_prefix) >= 6 and rt_prefix in ex_low)
                or (is_vid_id and target_id.lower() in ex_low)
            )
            if already_matches:
                logger.info("Short %s is already linked to %r; returning idempotent success.", short_id, existing_link_text)
                if screenshot_path:
                    await self.capture_screenshot(screenshot_path)
                return {
                    "success": True,
                    "linked_via_cdp": True,
                    "already_linked": True,
                    "short_id": short_id,
                    "target_id": target_id if is_vid_id else None,
                    "target_title": resolved_title,
                    "selected_text": existing_link_text,
                    "saved": False,
                    "screenshot_path": str(screenshot_path) if screenshot_path else None,
                }
            # Different video currently linked -> click clear (#right-icon) or edit (#edit-icon) first
            logger.info("Short %s currently linked to different video %r; clearing before re-linking...", short_id, existing_link_text)
            await self.evaluate("""
                (() => {
                    const clearBtn = document.querySelector(
                        'ytcp-video-metadata-related-video #right-icon, #linked-video-editor-link #right-icon, ytcp-shorts-content-links-picker #right-icon'
                    );
                    if (clearBtn) clearBtn.click();
                })()
            """)
            await asyncio.sleep(1.2)

        # Open Related Video picker (ytcp-video-metadata-related-video / Video liên quan)
        opened = False
        tier3_detected = False
        for _ in range(4):
            click_open = await self.evaluate("""
                (() => {
                    const selectors = [
                        'ytcp-video-metadata-related-video',
                        '#linked-video-editor-link',
                        'ytcp-shorts-content-links-picker',
                        'ytcp-linked-video-editor',
                        'ytcp-video-metadata-editor-sidepanel #related-video',
                        'ytcp-video-metadata-editor-advanced #related-video-picker',
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            el.scrollIntoView({ behavior: 'instant', block: 'center' });
                            const btn = el.querySelector('#select-button, .dropdown-trigger, #trigger, .container, ytcp-button, button, #edit-icon') || el;
                            btn.click();
                            return { clicked: true, selector: sel };
                        }
                    }
                    const fallback = Array.from(document.querySelectorAll('ytcp-button, button, div[role="button"], ytcp-form-select')).find(b => {
                        const t = (b.innerText || b.textContent || b.getAttribute('aria-label') || '').toLowerCase();
                        return t.includes('video liên quan') || t.includes('related video');
                    });
                    if (fallback) {
                        fallback.scrollIntoView({ behavior: 'instant', block: 'center' });
                        fallback.click();
                        return { clicked: true, selector: 'text_fallback' };
                    }
                    return { clicked: false };
                })()
            """)
            await asyncio.sleep(1.8)
            diag = await self.check_trust_tiers_dialog()
            if diag.get("detected"):
                tier3_detected = True
                break
            dlg_ready = await self.evaluate("""
                Boolean(
                    document.querySelector('ytcp-video-pick-dialog') ||
                    document.querySelector('ytcp-entity-picker-dialog') ||
                    document.querySelectorAll('ytcp-video-pick-dialog ytcp-entity-card, ytcp-entity-card, ytcp-video-row').length > 0
                )
            """)
            if dlg_ready or (isinstance(click_open, dict) and click_open.get("clicked")):
                opened = True
                if dlg_ready:
                    break

        if tier3_detected:
            await self.dismiss_trust_tiers_dialog()
            handle = self.resolve_channel_handle(short_id) or "@SuKeLaiVN"
            applied = await self.apply_clickable_handle_fallback(
                target_title=resolved_title or "Video chính trên kênh",
                handle=handle,
            )
            return {
                "success": False,
                "linked_via_cdp": False,
                "tier3_verification_required": True,
                "clickable_handle_fallback_applied": applied,
                "short_id": short_id,
                "target": raw_target,
            }

        if not opened:
            return {
                "success": False,
                "linked_via_cdp": False,
                "short_id": short_id,
                "target": raw_target,
                "reason": "related_video_picker_not_found",
            }

        # Type search query if resolved_title is available, then select matching card
        search_queries = []
        if resolved_title:
            search_queries.append(resolved_title.split(":")[0].strip())
        if is_vid_id:
            search_queries.append(target_id)
        search_queries.append("")  # fallback to unfiltered card list

        picked_res: dict[str, Any] = {"ok": False}
        for sq in search_queries:
            if sq:
                await self.evaluate(f"""
                    (() => {{
                        const q = {json.dumps(sq, ensure_ascii=False)};
                        const dlg = document.querySelector('ytcp-video-pick-dialog, ytcp-entity-picker-dialog') || document;
                        const inp = dlg.querySelector('input#search-input, input[type="text"], input');
                        if (inp) {{
                            inp.focus();
                            inp.value = '';
                            inp.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                            inp.value = q;
                            inp.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                            inp.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                        }}
                    }})()
                """)
                await asyncio.sleep(1.5)
            else:
                await self.evaluate("""
                    (() => {
                        const dlg = document.querySelector('ytcp-video-pick-dialog, ytcp-entity-picker-dialog');
                        const inp = dlg ? dlg.querySelector('input#search-input, input[type="text"], input') : null;
                        if (inp && inp.value) {
                            inp.focus();
                            inp.value = '';
                            inp.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                        }
                    })()
                """)
                await asyncio.sleep(1.0)

            picked_res = await self.evaluate(f"""
                (() => {{
                    const qId = {json.dumps(target_id if is_vid_id else "", ensure_ascii=False)};
                    const curShort = {json.dumps(short_id, ensure_ascii=False)};
                    const qTitle = {json.dumps((resolved_title or "").lower().strip(), ensure_ascii=False)};
                    const qPrefix = qTitle ? qTitle.split(/[:,-]/)[0].trim() : '';

                    const cards = Array.from(document.querySelectorAll(
                        'ytcp-video-pick-dialog ytcp-entity-card, ytcp-entity-card, ' +
                        'ytcp-entity-picker-dialog ytcp-entity-picker-item, ytcp-video-pick-dialog ytcp-video-row'
                    ));
                    if (cards.length === 0) return {{ ok: false, reason: 'no_cards' }};

                    const pool = cards.filter(c => {{
                        const h = c.innerHTML || '';
                        const t = (c.innerText || '').toLowerCase();
                        return !(curShort && (h.includes(curShort) || t.includes(curShort)));
                    }});
                    const candidates = pool.length > 0 ? pool : cards;

                    let match = null;
                    if (qId) {{
                        match = candidates.find(c => (c.innerHTML || '').includes(qId) || (c.getAttribute('aria-label') || '').includes(qId));
                    }}
                    if (!match && qTitle) {{
                        match = candidates.find(c => {{
                            const t = (c.innerText || '').toLowerCase();
                            const a = (c.getAttribute('aria-label') || '').toLowerCase();
                            return t.includes(qTitle) || a.includes(qTitle);
                        }});
                    }}
                    if (!match && qPrefix && qPrefix.length >= 5) {{
                        match = candidates.find(c => {{
                            const t = (c.innerText || '').toLowerCase();
                            const a = (c.getAttribute('aria-label') || '').toLowerCase();
                            return t.includes(qPrefix) || a.includes(qPrefix);
                        }});
                    }}
                    if (!match && !qId && !qTitle) {{
                        match = candidates.find(c => !((c.innerText || '').toLowerCase().includes('#shorts'))) || candidates[0];
                    }}
                    if (match) {{
                        match.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                        match.click();
                        return {{ ok: true, matched_text: (match.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 120) }};
                    }}
                    return {{ ok: false, card_count: candidates.length }};
                }})()
            """) or {"ok": False}
            if picked_res.get("ok"):
                break

        await asyncio.sleep(1.2)
        saved = False
        if picked_res.get("ok") and save_changes:
            saved = await self._click_editor_save_and_wait()

        after_linked = await self.evaluate("""
            (() => {
                const el = document.querySelector('ytcp-video-metadata-related-video .dropdown-trigger-text') ||
                           document.querySelector('#linked-video-editor-link .dropdown-trigger-text') ||
                           document.querySelector('ytcp-shorts-content-links-picker .dropdown-trigger-text') ||
                           document.querySelector('ytcp-video-metadata-related-video');
                return el ? (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim() : '';
            })()
        """)
        if screenshot_path:
            await self.capture_screenshot(screenshot_path)

        ok = bool(picked_res.get("ok") and (saved or not save_changes))
        return {
            "success": ok,
            "linked_via_cdp": ok,
            "short_id": short_id,
            "target_id": target_id if is_vid_id else None,
            "target_title": resolved_title,
            "picked": picked_res,
            "selected_text": after_linked,
            "saved": saved,
            "screenshot_path": str(screenshot_path) if screenshot_path else None,
        }

    async def update_existing_video_studio_settings(
        self,
        video_url_or_id: str,
        *,
        notify_subscribers: Optional[bool] = False,
        title: Optional[str] = None,
        description: Optional[str] = None,
        clean_dead_links: Optional[list[str] | tuple[str, ...]] = None,
        thumbnail_path: Optional[str | Path] = None,
        strict_thumbnail: bool = False,
        playlist_name: Optional[str] = None,
        attach_endscreen: bool = False,
        related_video: Optional[str] = None,
        visibility: Optional[str] = None,
        tags: Optional[str | list[str]] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
        altered_content: str = "unset",
        subtitles_path: Optional[str | Path] = None,
        screenshot_path: Optional[str | Path] = None,
    ) -> dict[str, Any]:
        """In-place /video/<VID>/edit updater: expands Show More (#toggle-button), unchecks Notify Subscribers, updates title/desc/thumb/playlist/endscreen/related-video/visibility, and clicks #save."""
        vid_id = str(video_url_or_id or "").strip()
        if "v=" in vid_id:
            vid_id = vid_id.split("v=")[1].split("&")[0]
        elif "/" in vid_id:
            vid_id = vid_id.rstrip("/").split("/")[-1].split("?")[0]
        if not vid_id:
            raise ValueError(f"Invalid video_url_or_id: {video_url_or_id!r}")

        edit_url = f"https://studio.youtube.com/video/{vid_id}/edit"
        logger.info("Navigating to %s for in-place Studio settings update...", edit_url)
        await self.call("Page.navigate", {"url": edit_url})
        await asyncio.sleep(3.5)
        await self.dismiss_studio_interstitials()

        # Wait up to 15s for editor hydration
        for _ in range(30):
            has_editor = await self.evaluate("""
                (() => {
                    const el = document.querySelector('#title-textarea #textbox') ||
                               document.querySelector('ytcp-video-metadata-editor');
                    return Boolean(el);
                })()
            """)
            if has_editor:
                break
            await asyncio.sleep(0.5)

        report: dict[str, Any] = {
            "video_id": vid_id,
            "edit_url": edit_url,
            "changes": {},
        }

        # 1. Title update
        if title is not None and str(title).strip():
            clean_title = str(title).strip()
            if len(clean_title) > 55:
                raise ValueError(f"TITLE_EXCEEDS_55_CHARS: len={len(clean_title)} title={clean_title!r}")
            t_res = await self.evaluate(f"""
                (() => {{
                    const el = document.querySelector('#title-textarea #textbox') ||
                               document.querySelector('#textbox[contenteditable="true"]');
                    if (!el) return {{ updated: false, reason: 'no_title_textbox' }};
                    const cur = (el.innerText || '').trim();
                    if (cur === {json.dumps(clean_title, ensure_ascii=False)}) {{
                        return {{ updated: false, unchanged: true, title: cur }};
                    }}
                    el.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, {json.dumps(clean_title, ensure_ascii=False)});
                    el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                    return {{ updated: true, previous: cur, title: (el.innerText || '').trim() }};
                }})()
            """)
            report["changes"]["title"] = t_res

        # 2. Description update and/or dead Private link cleaning
        if description is not None or clean_dead_links:
            current_desc = description
            if current_desc is None:
                current_desc = str(
                    await self.evaluate("""
                        (() => {
                            const el = document.querySelector('#description-textarea #textbox');
                            return el ? (el.innerText || '') : '';
                        })()
                    """)
                    or ""
                )
            removed_dead_ids: list[str] = []
            if clean_dead_links:
                current_desc, removed_dead_ids = clean_dead_links_from_description(current_desc, clean_dead_links)
            d_res = await self.evaluate(f"""
                (() => {{
                    const el = document.querySelector('#description-textarea #textbox');
                    if (!el) return {{ updated: false, reason: 'no_description_textbox' }};
                    const targetDesc = {json.dumps(current_desc, ensure_ascii=False)};
                    const cur = (el.innerText || '').trim();
                    if (cur === targetDesc.trim()) {{
                        return {{ updated: false, unchanged: true, length: cur.length }};
                    }}
                    el.focus();
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
                    document.execCommand('insertText', false, targetDesc);
                    el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                    return {{ updated: true, length: (el.innerText || '').length }};
                }})()
            """)
            if isinstance(d_res, dict):
                d_res["removed_dead_ids"] = removed_dead_ids
            report["changes"]["description"] = d_res

        # 3. Custom Thumbnail (< 2MB)
        if thumbnail_path:
            thumb_ok = await self.upload_thumbnail(thumbnail_path, strict_thumbnail=strict_thumbnail)
            report["changes"]["thumbnail_uploaded"] = thumb_ok

        # 4. Playlist selection / creation
        if playlist_name:
            pl_res = await self.ensure_and_select_playlist(playlist_name)
            report["changes"]["playlist"] = pl_res

        # 5. Notify subscribers checkbox + tags/language/altered_content (inside Show more / #toggle-button)
        if notify_subscribers is not None or tags or language or category or altered_content in ("yes", "no"):
            await self.expand_show_more_details()
        if notify_subscribers is not None:
            notify_res = await self.set_notify_subscribers(bool(notify_subscribers))
            report["changes"]["notify_subscribers"] = notify_res
        if altered_content in ("yes", "no"):
            alt_res = await self.set_altered_content_disclosure(altered_content)
            report["changes"]["altered_content"] = alt_res
        if tags:
            clean_tags = format_and_truncate_tags(tags, max_chars=480)
            existing_chips = int(
                await self.evaluate("document.querySelectorAll('#tags-container ytcp-chip').length") or 0
            )
            if clean_tags and existing_chips == 0:
                tags_csv = ",".join(clean_tags) + ","
                await self.evaluate(f"""
                    (() => {{
                        const container = document.querySelector('#tags-container') ||
                                          document.querySelector('ytcp-form-input-container#tags-container');
                        if (!container) return false;
                        container.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                        const input = container.querySelector('input#text-input, input');
                        if (!input) return false;
                        input.focus();
                        document.execCommand('insertText', false, {json.dumps(tags_csv, ensure_ascii=False)});
                        input.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                        return true;
                    }})()
                """)
                await self.call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"})
                await self.call("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"})
                await asyncio.sleep(0.5)
                after_chips = int(
                    await self.evaluate("document.querySelectorAll('#tags-container ytcp-chip').length") or 0
                )
                report["changes"]["tags_chip_count"] = after_chips
        if language:
            cur_lang = str(
                await self.evaluate("""
                    (() => {
                        const el = document.querySelector('#language-input') ||
                                   document.querySelector('ytcp-text-dropdown-select#language-input');
                        return el ? (el.innerText || el.textContent || '').trim().toLowerCase() : '';
                    })()
                """)
                or ""
            )
            if not cur_lang or "chọn" in cur_lang or "select" in cur_lang:
                lang_ok = await self._select_studio_dropdown_option(
                    ['#language-input', 'ytcp-form-language-input', 'ytcp-text-dropdown-select#language-input'],
                    language,
                )
                report["changes"]["language_selected"] = lang_ok
        if category:
            cur_cat = str(
                await self.evaluate("""
                    (() => {
                        const el = document.querySelector('#category') ||
                                   document.querySelector('ytcp-text-dropdown-select#category');
                        return el ? (el.innerText || el.textContent || '').trim().toLowerCase() : '';
                    })()
                """)
                or ""
            )
            if not cur_cat or "chọn" in cur_cat or "select" in cur_cat:
                cat_ok = await self._select_studio_dropdown_option(
                    ['#category', 'ytcp-video-metadata-category', 'ytcp-text-dropdown-select#category'],
                    category,
                )
                report["changes"]["category_selected"] = cat_ok

        # 6. Short Related Video (if requested)
        if related_video:
            rel_res = await self.attach_related_video_existing_short(
                vid_id,
                related_video,
                navigate_if_needed=False,
                save_changes=False,
            )
            report["changes"]["related_video"] = rel_res

        # 7. Visibility switch (PRIVATE / UNLISTED / PUBLIC) if requested
        if visibility:
            vis_norm = visibility.strip().upper()
            vis_res = await self.evaluate("""
                (() => {
                    const trigger = document.querySelector('ytcp-video-metadata-visibility #select-button') ||
                                    document.querySelector('#visibility-button') ||
                                    document.querySelector('ytcp-video-metadata-visibility ytcp-dropdown-trigger') ||
                                    document.querySelector('ytcp-video-metadata-visibility #trigger') ||
                                    document.querySelector('ytcp-video-metadata-visibility');
                    if (!trigger) return { opened: false };
                    trigger.scrollIntoView({ behavior: 'instant', block: 'center' });
                    const btn = trigger.querySelector('#select-button, button, #trigger, .dropdown-trigger') || trigger;
                    btn.click();
                    return { opened: true };
                })()
            """)
            if isinstance(vis_res, dict) and vis_res.get("opened"):
                await asyncio.sleep(1.0)
                await self.evaluate("""
                    (() => {
                        const firstExpand = document.querySelector('#first-container-expand-button') ||
                                            document.querySelector('#first-container tp-yt-paper-radio-button') ||
                                            document.querySelector('tp-yt-paper-radio-button[name="FIRST_CONTAINER"]');
                        if (firstExpand) firstExpand.click();
                    })()
                """)
                await asyncio.sleep(0.6)
                set_r = await self.evaluate(f"""
                    (() => {{
                        const radio = document.querySelector('tp-yt-paper-radio-button[name="{vis_norm}"]');
                        if (!radio) return {{ ok: false, reason: 'radio_not_found' }};
                        radio.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                        radio.click();
                        const inner = radio.querySelector('#radioContainer, #offRadio');
                        if (inner) inner.click();
                        return {{ ok: true, visibility: '{vis_norm}' }};
                    }})()
                """)
                if not (isinstance(set_r, dict) and set_r.get("ok")):
                    await asyncio.sleep(0.6)
                    set_r = await self.evaluate(f"""
                        (() => {{
                            const radio = document.querySelector('tp-yt-paper-radio-button[name="{vis_norm}"]');
                            if (!radio) return {{ ok: false, reason: 'radio_still_not_found' }};
                            radio.click();
                            const inner = radio.querySelector('#radioContainer, #offRadio');
                            if (inner) inner.click();
                            return {{ ok: true, visibility: '{vis_norm}' }};
                        }})()
                    """)
                await asyncio.sleep(0.5)
                await self.evaluate("""
                    (() => {
                        const popup = document.querySelector('ytcp-video-visibility-edit-popup') ||
                                      document.querySelector('tp-yt-iron-dropdown[aria-hidden="false"]') ||
                                      document;
                        const doneBtn = popup.querySelector('#save-button, ytcp-button#save-button') ||
                                        Array.from(popup.querySelectorAll('ytcp-button, button')).find(b => {
                                            const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                                            return t === 'xong' || t === 'done';
                                        });
                        if (doneBtn) {
                            doneBtn.click();
                        }
                    })()
                """)
                await asyncio.sleep(1.0)
                report["changes"]["visibility"] = set_r

        # 8. Save dirty /edit Details BEFORE opening End Screen modal so Studio never drops unsaved edits
        saved_details = await self._click_editor_save_and_wait()

        # 9. Attach subtitles if missing and subtitles_path provided
        if subtitles_path and Path(subtitles_path).is_file():
            sub_ok = await self.attach_subtitles_post_publish(vid_id, Path(subtitles_path).resolve())
            report["changes"]["subtitles_uploaded"] = sub_ok

        # 10. Attach 2-element End Screen template (saves inside its own modal)
        if attach_endscreen:
            es_res = await self.attach_endscreen_template(video_url_or_id=None)
            report["changes"]["endscreen"] = es_res

        # 10. Click main editor #save again if any post-modal state is dirty
        saved_after = await self._click_editor_save_and_wait(max_wait_sec=4.0) if not saved_details else False
        saved = bool(saved_details or saved_after)
        report["saved"] = saved

        if screenshot_path:
            await self.capture_screenshot(screenshot_path)
            report["screenshot_path"] = str(screenshot_path)

        report["success"] = True
        return report

    async def post_and_pin_comment(
        self,
        video_url_or_id: str,
        comment_text: str,
        screenshot_path: Optional[str | Path] = None,
    ) -> dict[str, Any]:
        """Post a comment on a live PUBLIC video/Short watch page and pin it as the creator."""
        raw_target = str(video_url_or_id or "").strip()
        vid_id = raw_target
        if "v=" in vid_id:
            vid_id = vid_id.split("v=")[1].split("&")[0]
        elif "/" in vid_id:
            vid_id = vid_id.rstrip("/").split("/")[-1].split("?")[0]

        clean_comment = str(comment_text or "").strip()
        if not vid_id or not clean_comment:
            return {
                "success": False,
                "video_id": vid_id,
                "posted": False,
                "pinned": False,
                "error": "missing_video_id_or_comment",
            }

        watch_url = f"https://www.youtube.com/watch?v={vid_id}"
        target_json = json.dumps(clean_comment, ensure_ascii=False)

        async def _open_comments_panel() -> dict[str, Any]:
            await self.evaluate(
                """
                (() => {
                    document.querySelectorAll('video').forEach(v => {
                        try { v.pause(); } catch (e) {}
                    });
                })()
                """
            )
            cur_url = str(await self.evaluate("window.location.href") or "")
            is_shorts = "/shorts/" in cur_url
            if is_shorts:
                opened = await self.evaluate(
                    """
                    (() => {
                        const existingBox = document.querySelector('ytd-commentbox #contenteditable-root, ytd-comment-thread-renderer, #simplebox-placeholder');
                        if (existingBox) {
                            const r = existingBox.getBoundingClientRect();
                            if (r.width > 0 && r.height > 0) return { is_shorts: true, already_open: true };
                        }
                        const selectors = [
                            'ytd-reel-player-overlay-renderer #comments-button button',
                            '#comments-button button',
                            '#comments-button yt-button-shape button',
                            'button[aria-label*="Bình luận"]',
                            'button[aria-label*="Comments"]',
                            'button[aria-label*="comments"]'
                        ];
                        for (const sel of selectors) {
                            const btns = Array.from(document.querySelectorAll(sel));
                            for (const btn of btns) {
                                const r = btn.getBoundingClientRect();
                                if (r.width > 0 && r.height > 0) {
                                    btn.click();
                                    return { is_shorts: true, clicked: sel };
                                }
                            }
                        }
                        return { is_shorts: true, clicked: null };
                    })()
                    """
                )
                await asyncio.sleep(2.0)
                return opened if isinstance(opened, dict) else {"is_shorts": True}

            await self.evaluate("window.scrollTo(0, 520);")
            await asyncio.sleep(1.2)
            await self.evaluate(
                """
                (() => {
                    window.scrollTo(0, 920);
                    document.querySelectorAll('video').forEach(v => {
                        try { v.pause(); } catch (e) {}
                    });
                })()
                """
            )
            await asyncio.sleep(1.5)
            return {"is_shorts": False, "scrolled": True}

        async def _find_matching_thread() -> dict[str, Any]:
            js = """
                (() => {
                    const TARGET = __TARGET_COMMENT__;
                    const norm = s => (s || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                    const prefix = norm(TARGET).slice(0, 42);
                    const threads = Array.from(document.querySelectorAll('ytd-comment-thread-renderer'));
                    for (let i = 0; i < threads.length; i++) {
                        const t = threads[i];
                        const contentEl = t.querySelector('#comment #content-text, ytd-comment-view-model #content-text, #content-text');
                        const txt = norm(contentEl ? (contentEl.innerText || contentEl.textContent) : '');
                        const badgeEl = t.querySelector('#pinned-comment-badge, ytd-pinned-comment-badge-renderer, #pinned-comment-badge-renderer');
                        const badgeText = (badgeEl ? (badgeEl.innerText || badgeEl.textContent || '') : '').replace(/\\s+/g, ' ').trim();
                        const hasPinnedWord = badgeText.toLowerCase().includes('ghim') || badgeText.toLowerCase().includes('pinned');
                        if (prefix && txt.includes(prefix)) {
                            return {
                                found: true,
                                index: i,
                                pinned: Boolean(badgeEl && (hasPinnedWord || badgeEl.getBoundingClientRect().height > 0)),
                                badge_text: badgeText,
                                text: (contentEl ? (contentEl.innerText || contentEl.textContent || '') : '').trim().slice(0, 160),
                                total_threads: threads.length,
                            };
                        }
                    }
                    const firstBadge = document.querySelector('ytd-comment-thread-renderer #pinned-comment-badge, ytd-comment-thread-renderer ytd-pinned-comment-badge-renderer');
                    return {
                        found: false,
                        total_threads: threads.length,
                        any_pinned_badge: Boolean(firstBadge),
                    };
                })()
            """.replace("__TARGET_COMMENT__", target_json)
            res = await self.evaluate(js)
            return res if isinstance(res, dict) else {"found": False}

        logger.info("Navigating to %s to post & pin comment...", watch_url)
        await self.call("Page.navigate", {"url": watch_url})
        await asyncio.sleep(4.5)
        await _open_comments_panel()

        # Wait up to 15s for comments section (either comment box or thread list)
        comments_ready = False
        for _ in range(30):
            comments_ready = bool(
                await self.evaluate(
                    """
                    Boolean(
                        document.querySelector('#simplebox-placeholder, ytd-comment-simplebox-renderer #placeholder-area, ytd-commentbox #contenteditable-root, ytd-comment-thread-renderer')
                    )
                    """
                )
            )
            if comments_ready:
                break
            await asyncio.sleep(0.5)

        if not comments_ready:
            # Retry opening panel once more in case page hydrated late
            await _open_comments_panel()
            await asyncio.sleep(2.0)

        existing = await _find_matching_thread()
        posted = False
        already_present = bool(existing.get("found"))
        already_pinned = bool(existing.get("found") and existing.get("pinned"))

        if already_pinned:
            logger.info("Comment on %s is already posted and pinned.", vid_id)
            if screenshot_path:
                await self.capture_screenshot(screenshot_path)
            return {
                "success": True,
                "video_id": vid_id,
                "watch_url": watch_url,
                "posted": False,
                "already_pinned": True,
                "pinned": True,
                "pinned_badge_text": existing.get("badge_text", ""),
                "matched_comment_preview": existing.get("text", ""),
                "screenshot_path": str(screenshot_path) if screenshot_path else None,
            }

        if not already_present:
            # Click placeholder to reveal editable comment box if collapsed
            await self.evaluate(
                """
                (() => {
                    const ph = document.querySelector('#simplebox-placeholder') ||
                               document.querySelector('ytd-comment-simplebox-renderer #placeholder-area') ||
                               document.querySelector('#placeholder-area');
                    if (ph) {
                        ph.scrollIntoView({ block: 'center' });
                        ph.click();
                        return true;
                    }
                    return false;
                })()
                """
            )
            await asyncio.sleep(1.2)

            typed_ok = False
            for _ in range(12):
                js_type = """
                    (() => {
                        const TARGET = __TARGET_COMMENT__;
                        const boxes = Array.from(document.querySelectorAll('ytd-commentbox #contenteditable-root'));
                        const ce = boxes.find(el => {
                            const r = el.getBoundingClientRect();
                            return r.width > 0 && r.height > 0;
                        });
                        if (!ce) return { ok: false, reason: 'no_contenteditable' };
                        ce.scrollIntoView({ block: 'center' });
                        ce.focus();
                        ce.click();
                        try {
                            const sel = window.getSelection();
                            const range = document.createRange();
                            range.selectNodeContents(ce);
                            sel.removeAllRanges();
                            sel.addRange(range);
                            document.execCommand('delete', false, null);
                        } catch (e) {}
                        let inserted = false;
                        try {
                            inserted = document.execCommand('insertText', false, TARGET);
                        } catch (e) {}
                        if (!inserted || !ce.innerText.trim()) {
                            ce.textContent = TARGET;
                        }
                        ce.dispatchEvent(new InputEvent('input', { bubbles: true, data: TARGET, inputType: 'insertText' }));
                        ce.dispatchEvent(new Event('change', { bubbles: true }));
                        return {
                            ok: ce.innerText.trim().length >= Math.min(8, TARGET.length),
                            len: ce.innerText.trim().length,
                        };
                    })()
                """.replace("__TARGET_COMMENT__", target_json)
                type_res = await self.evaluate(js_type)
                if isinstance(type_res, dict) and type_res.get("ok"):
                    typed_ok = True
                    break
                await asyncio.sleep(0.5)

            if not typed_ok:
                if screenshot_path:
                    await self.capture_screenshot(screenshot_path)
                return {
                    "success": False,
                    "video_id": vid_id,
                    "watch_url": watch_url,
                    "posted": False,
                    "pinned": False,
                    "error": "comment_input_not_found_or_uneditable",
                    "screenshot_path": str(screenshot_path) if screenshot_path else None,
                }

            await asyncio.sleep(0.6)
            submitted = await self.evaluate(
                """
                (() => {
                    const boxes = Array.from(document.querySelectorAll('ytd-commentbox #contenteditable-root'));
                    const ce = boxes.find(el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0;
                    });
                    const root = ce ? ce.closest('ytd-commentbox') : document.querySelector('ytd-commentbox');
                    if (!root) return { clicked: false, reason: 'no_commentbox' };
                    const btn = root.querySelector('#submit-button button, #submit-button #button, ytd-button-renderer#submit-button button, #submit-button');
                    if (!btn) return { clicked: false, reason: 'no_submit_button' };
                    const disabled = btn.disabled || btn.getAttribute('aria-disabled') === 'true';
                    if (disabled) return { clicked: false, reason: 'submit_disabled' };
                    btn.click();
                    return { clicked: true };
                })()
                """
            )
            if not (isinstance(submitted, dict) and submitted.get("clicked")):
                if screenshot_path:
                    await self.capture_screenshot(screenshot_path)
                return {
                    "success": False,
                    "video_id": vid_id,
                    "watch_url": watch_url,
                    "posted": False,
                    "pinned": False,
                    "error": f"comment_submit_failed:{submitted}",
                    "screenshot_path": str(screenshot_path) if screenshot_path else None,
                }

            # Poll up to 15s for the posted thread to render
            for _ in range(30):
                await asyncio.sleep(0.5)
                chk = await _find_matching_thread()
                if chk.get("found"):
                    posted = True
                    existing = chk
                    break
            if not posted:
                logger.warning("Submitted comment on %s did not appear in DOM within 15s.", vid_id)
                if screenshot_path:
                    await self.capture_screenshot(screenshot_path)
                return {
                    "success": False,
                    "video_id": vid_id,
                    "watch_url": watch_url,
                    "posted": False,
                    "pinned": False,
                    "error": "posted_comment_not_visible_after_submit",
                    "screenshot_path": str(screenshot_path) if screenshot_path else None,
                }

        # Open three-dot action menu on the matching thread and pin it
        logger.info("Pinning comment thread (index=%s) on %s...", existing.get("index"), vid_id)
        menu_opened = await self.evaluate(
            """
            (() => {
                const TARGET = __TARGET_COMMENT__;
                const norm = s => (s || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                const prefix = norm(TARGET).slice(0, 42);
                const threads = Array.from(document.querySelectorAll('ytd-comment-thread-renderer'));
                const targetThread = threads.find(t => {
                    const el = t.querySelector('#comment #content-text, ytd-comment-view-model #content-text, #content-text');
                    return el && norm(el.innerText || el.textContent).includes(prefix);
                });
                if (!targetThread) return { ok: false, reason: 'thread_not_found' };
                targetThread.scrollIntoView({ block: 'center' });
                targetThread.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
                const commentNode = targetThread.querySelector('#comment, ytd-comment-view-model') || targetThread;
                commentNode.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
                const btn = commentNode.querySelector('#action-menu button, #action-menu yt-icon-button button, button[aria-label*="Thao tác"], button[aria-label*="Action menu"], ytd-menu-renderer button');
                if (!btn) return { ok: false, reason: 'action_menu_btn_not_found' };
                btn.click();
                return { ok: true };
            })()
            """.replace("__TARGET_COMMENT__", target_json)
        )
        if not (isinstance(menu_opened, dict) and menu_opened.get("ok")):
            if screenshot_path:
                await self.capture_screenshot(screenshot_path)
            return {
                "success": False,
                "video_id": vid_id,
                "watch_url": watch_url,
                "posted": posted or already_present,
                "pinned": False,
                "error": f"pin_menu_open_failed:{menu_opened}",
                "screenshot_path": str(screenshot_path) if screenshot_path else None,
            }

        await asyncio.sleep(0.8)
        pin_clicked = False
        for _ in range(10):
            pin_res = await self.evaluate(
                """
                (() => {
                    const containers = Array.from(document.querySelectorAll('ytd-popup-container, tp-yt-iron-dropdown'));
                    const pool = [];
                    containers.forEach(c => {
                        c.querySelectorAll('tp-yt-paper-item, ytd-menu-service-item-renderer, yt-list-item-view-model, [role="menuitem"]').forEach(el => pool.push(el));
                    });
                    for (const item of pool) {
                        const r = item.getBoundingClientRect();
                        if (r.width <= 0 || r.height <= 0) continue;
                        const txt = (item.innerText || item.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                        if (!txt || txt.includes('bỏ ghim') || txt.includes('unpin')) continue;
                        if (txt === 'ghim' || txt === 'pin' || txt.startsWith('ghim ') || txt.startsWith('pin ')) {
                            const innerClick = item.querySelector('tp-yt-paper-item, button, a, [role="menuitem"]') || item;
                            innerClick.click();
                            return { clicked: true, label: txt, tag: innerClick.tagName };
                        }
                    }
                    return { clicked: false };
                })()
                """
            )
            if isinstance(pin_res, dict) and pin_res.get("clicked"):
                pin_clicked = True
                logger.info("Clicked pin menu item (%s, tag=%s) for %s", pin_res.get("label"), pin_res.get("tag"), vid_id)
                break
            await asyncio.sleep(0.4)

        if not pin_clicked:
            if screenshot_path:
                await self.capture_screenshot(screenshot_path)
            return {
                "success": False,
                "video_id": vid_id,
                "watch_url": watch_url,
                "posted": posted or already_present,
                "pinned": False,
                "error": "pin_menu_item_not_found",
                "screenshot_path": str(screenshot_path) if screenshot_path else None,
            }

        await asyncio.sleep(0.8)
        confirm_clicked = False
        last_dialog_debug: Any = None
        for _ in range(15):
            conf_res = await self.evaluate(
                """
                (() => {
                    const dialogs = [];
                    const collectDialogs = (root) => {
                        if (!root) return;
                        root.querySelectorAll('tp-yt-paper-dialog, yt-confirm-dialog-renderer, yt-dialog-view-model, [role="dialog"]').forEach(d => {
                            const r = d.getBoundingClientRect();
                            if (r.width > 0 && r.height > 0) dialogs.push(d);
                        });
                    };
                    collectDialogs(document);
                    const btnDebug = [];
                    const searchRoots = dialogs.length > 0 ? dialogs : Array.from(document.querySelectorAll('ytd-popup-container, body > tp-yt-iron-overlay-backdrop, body'));
                    const seen = new Set();
                    for (const root of searchRoots) {
                        const btns = Array.from(root.querySelectorAll('button, tp-yt-paper-button, yt-button-shape button, [role="button"]'));
                        for (const b of btns) {
                            if (seen.has(b)) continue;
                            seen.add(b);
                            const r = b.getBoundingClientRect();
                            if (r.width <= 0 || r.height <= 0) continue;
                            const txt = (b.innerText || b.textContent || b.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                            btnDebug.push({ txt, id: b.id || (b.closest('[id]') ? b.closest('[id]').id : ''), tag: b.tagName });
                            if (!txt || txt.includes('hủy') || txt.includes('cancel') || txt.includes('đóng') || txt.includes('close')) continue;
                            const inConfirm = Boolean(b.closest('#confirm-button'));
                            if (inConfirm || txt === 'ghim' || txt === 'pin' || txt === 'ghim bình luận' || txt === 'pin comment') {
                                b.click();
                                return { confirmed: true, text: txt, inConfirm };
                            }
                        }
                    }
                    return { confirmed: false, dialogCount: dialogs.length, btns: btnDebug.slice(0, 12) };
                })()
                """
            )
            last_dialog_debug = conf_res
            if isinstance(conf_res, dict) and conf_res.get("confirmed"):
                confirm_clicked = True
                logger.info("Confirmed pin dialog (%s) for %s", conf_res.get("text"), vid_id)
                break
            await asyncio.sleep(0.4)

        if not confirm_clicked:
            logger.warning("Pin confirmation button did not appear or wasn't clicked for %s (debug=%s); checking state after reload.", vid_id, last_dialog_debug)

        await asyncio.sleep(2.5)

        # Reload watch URL cleanly and verify #pinned-comment-badge persisted
        logger.info("Reloading %s to verify pinned comment badge...", watch_url)
        await self.call("Page.navigate", {"url": watch_url})
        await asyncio.sleep(4.5)
        await _open_comments_panel()

        verified: dict[str, Any] = {}
        for _ in range(24):
            verified = await _find_matching_thread()
            if verified.get("found") and verified.get("pinned"):
                break
            await asyncio.sleep(0.5)

        pinned_ok = bool(verified.get("found") and verified.get("pinned"))
        if screenshot_path:
            await self.capture_screenshot(screenshot_path)

        return {
            "success": pinned_ok,
            "video_id": vid_id,
            "watch_url": watch_url,
            "posted": posted or already_present,
            "pinned": pinned_ok,
            "confirm_clicked": confirm_clicked,
            "pinned_badge_text": verified.get("badge_text", ""),
            "matched_comment_preview": verified.get("text", ""),
            "screenshot_path": str(screenshot_path) if screenshot_path else None,
        }

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
                    const inner = btn.querySelector('button');
                    if (inner) inner.click();
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
            # Walks light + Shadow DOM (depth <= 48) and checks bounding rects so position:fixed / slotted dialogs are handled reliably.
            clicked_publish_anyway = await self.evaluate("""
                (() => {
                    const targets = ['vẫn xuất bản', 'publish anyway'];
                    const dialogTags = new Set([
                        'YTCP-CONFIRMATION-DIALOG',
                        'YTCP-PRECHECKS-WARNING-DIALOG',
                        'YTCP-UPLOADS-STILL-CHECKING-DIALOG',
                        'TP-YT-PAPER-DIALOG',
                        'YTCP-DIALOG'
                    ]);
                    const nodes = [];
                    function walk(root, depth = 0) {
                        if (!root || depth > 48) return;
                        if (root.nodeType === 1) {
                            nodes.push(root);
                            if (root.shadowRoot) walk(root.shadowRoot, depth + 1);
                        }
                        for (const c of root.children || []) walk(c, depth + 1);
                    }
                    walk(document.body);

                    function insideDialog(el) {
                        let cur = el;
                        let steps = 0;
                        while (cur && steps < 48) {
                            steps++;
                            if (cur.nodeType === 1) {
                                const tag = (cur.tagName || '').toUpperCase();
                                const role = (cur.getAttribute && cur.getAttribute('role')) || '';
                                if (dialogTags.has(tag) || tag.includes('DIALOG') || role === 'dialog' || role === 'alertdialog') {
                                    return true;
                                }
                            }
                            cur = cur.parentElement || (cur.getRootNode && cur.getRootNode().host) || null;
                        }
                        return false;
                    }

                    // Keep selector hint 'ytcp-confirmation-dialog' for DOM queries/tests
                    const fallbackConfirm = document.querySelectorAll('ytcp-confirmation-dialog');
                    for (const el of nodes) {
                        if (!el.matches || !el.matches('ytcp-button, ytcp-button-shape, button, [role="button"], #secondary-action-button, #confirm-button')) {
                            continue;
                        }
                        const rect = el.getBoundingClientRect ? el.getBoundingClientRect() : null;
                        if (!rect || rect.width <= 0 || rect.height <= 0) continue;
                        const style = window.getComputedStyle(el);
                        if (style.visibility === 'hidden' || style.display === 'none') continue;
                        const rawTxt = (el.innerText || el.textContent || el.getAttribute('aria-label') || '');
                        const txt = (rawTxt.normalize ? rawTxt.normalize('NFC') : rawTxt).replace(/\\s+/g, ' ').trim().toLowerCase();
                        const isPrecheckSecondary = Boolean(
                            el.id === 'secondary-action-button' &&
                            el.closest && el.closest('ytcp-prechecks-warning-dialog, ytcp-uploads-still-checking-dialog')
                        );
                        if ((targets.includes(txt) || isPrecheckSecondary) && (insideDialog(el) || fallbackConfirm.length > 0)) {
                            const innerBtn = (el.shadowRoot && el.shadowRoot.querySelector('button')) || el.querySelector('button') || el;
                            innerBtn.click();
                            if (innerBtn !== el) el.click();
                            return txt || 'secondary-action-button';
                        }
                    }
                    return null;
                })()
            """)
            if clicked_publish_anyway:
                logger.info("Clicked warning confirmation dialog button: %s", clicked_publish_anyway)
                self._last_publish_accepted = True
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
                        if (d.closest('ytcp-uploads-dialog') || d.querySelector('#done-button, ytcp-video-visibility-select')) continue;
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
                            if (d.closest('ytcp-uploads-dialog') || d.querySelector('#done-button, ytcp-video-visibility-select')) continue;
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

        # Wait up to 15s for hydrated title text inside editor
        for _ in range(30):
            has_title = await self.evaluate("""
                (() => {
                    const el = document.querySelector('#title-textarea #textbox');
                    return Boolean(el && ((el.innerText || '').trim().length > 0));
                })()
            """)
            if has_title:
                break
            await asyncio.sleep(0.5)

        # Click #toggle-button (Show more / Hiển thị thêm) if collapsed and wait for #tags-container visibility
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
        for _ in range(6):
            await asyncio.sleep(0.5)
            tags_vis = await self.evaluate("""
                (() => {
                    const tb = document.querySelector('#tags-container');
                    return Boolean(tb && tb.offsetParent !== null);
                })()
            """)
            if tags_vis:
                break

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

                // Custom thumbnail check (exclude hidden /edit fallback img and Tier-2 help tooltip lock)
                const up = document.querySelector('ytcp-thumbnail-uploader');
                let has_custom_thumbnail = false;
                if (up) {
                    const tip = up.querySelector('#select-tooltip-icon, [icon="yt-sys-icons:help"]');
                    const tipVis = Boolean(tip && tip.offsetParent !== null);
                    const pb = up.querySelector('#preview-button');
                    const pbVis = Boolean(pb && pb.offsetParent !== null);
                    const sb = up.querySelector('#select-button');
                    const sbVis = Boolean(sb && sb.offsetParent !== null);
                    const hasSel = up.hasAttribute('selected');
                    const validThumbImg = Array.from(up.querySelectorAll('img[src]')).find(img => {
                        const src = (img.getAttribute('src') || img.src || '').trim();
                        if (!src || src.includes('placeholder') || src.includes('/edit') || src.includes('/upload')) {
                            return false;
                        }
                        const isCustomSrc = (
                            src.startsWith('blob:') ||
                            src.startsWith('data:image/') ||
                            src.includes('ytimg.com') ||
                            src.includes('googleusercontent.com')
                        );
                        return img.offsetParent !== null && (img.naturalWidth || 0) > 0 && isCustomSrc;
                    });
                    has_custom_thumbnail = !tipVis && (Boolean(validThumbImg) || (hasSel && pbVis && !sbVis));
                }

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

                // Visibility + active draft notice banner check (piercing Shadow DOM)
                const visBtn = document.querySelector('#visibility-button') ||
                               document.querySelector('#visibility') ||
                               document.querySelector('ytcp-video-metadata-visibility') ||
                               document.querySelector('#visibility-container') ||
                               document.querySelector('.visibility-label');
                const visibility_text = visBtn ? (visBtn.innerText || visBtn.textContent || '').trim() : '';

                let draft_banner_detected = false;
                let draft_banner_text = '';
                const draftPhrases = [
                    'trạng thái nháp',
                    'chỉnh sửa bản nháp',
                    'currently a draft',
                    'video is a draft',
                    'edit draft',
                ];
                function scanDraftNodes(root, depth = 0) {
                    if (!root || depth > 10 || draft_banner_detected) return;
                    if (root.nodeType === 1) {
                        const tag = (root.tagName || '').toUpperCase();
                        const cls = typeof root.className === 'string' ? root.className : '';
                        if (!cls.includes('closing') && (tag === 'YTCP-BANNER' || tag === 'YTCP-TOP-BANNER' || tag === 'YTCP-BUTTON' || tag === 'BUTTON')) {
                            const rect = root.getBoundingClientRect ? root.getBoundingClientRect() : null;
                            const style = window.getComputedStyle(root);
                            if (rect && rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden') {
                                const txt = (root.innerText || root.textContent || '').trim().replace(/\\s+/g, ' ');
                                const low = txt.toLowerCase();
                                if (txt.length <= 250 && draftPhrases.some(p => low.includes(p))) {
                                    draft_banner_detected = true;
                                    draft_banner_text = txt;
                                    return;
                                }
                            }
                        }
                        if (root.shadowRoot) scanDraftNodes(root.shadowRoot, depth + 1);
                    }
                    for (const c of root.children || []) scanDraftNodes(c, depth + 1);
                }
                scanDraftNodes(document.body);

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
                    draft_banner_detected,
                    draft_banner_text,
                };
            })()
        """)
        res = dict(summary) if isinstance(summary, dict) else {}
        v_low = (res.get("visibility_text") or "").lower()
        is_draft_or_private = (
            bool(res.get("draft_banner_detected"))
            or "bản nháp" in v_low
            or "trạng thái nháp" in v_low
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


def is_short_related_video_disabled(channel_id: Optional[str]) -> bool:
    """Return True if channel playbook, production lock, or channel map disables Short Related Video links.

    Precedence: `sys/channels/<ch>/playbook/overview.md` > `channel_v2_production_lock.json` > `youtube_channel_map.json`.
    """
    if not channel_id:
        return False
    ch_norm = str(channel_id).strip().replace("-", "_")
    overview_file = REPO_ROOT / "sys" / "channels" / ch_norm / "playbook" / "overview.md"
    if overview_file.exists():
        try:
            ov_text = overview_file.read_text(encoding="utf-8")
            if re.search(r"short_attach_related_video\s*:\s*true\b", ov_text, re.IGNORECASE):
                return False
            if re.search(r"short_attach_related_video\s*:\s*false\b", ov_text, re.IGNORECASE):
                return True
        except Exception as exc:
            logger.warning("Could not read publish_policy from %s: %s", overview_file, exc)
    lock_file = REPO_ROOT / "sys" / "channels" / ch_norm / "channel_v2_production_lock.json"
    if lock_file.exists():
        try:
            lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
            policy = lock_data.get("publish_policy") or {}
            if policy.get("short_attach_related_video") is False:
                return True
        except Exception as exc:
            logger.warning("Could not read publish_policy from %s: %s", lock_file, exc)
    map_file = REPO_ROOT / "sys" / "channels" / "youtube_channel_map.json"
    if map_file.exists():
        try:
            ch_map = json.loads(map_file.read_text(encoding="utf-8"))
            entry = (ch_map.get("channels") or {}).get(ch_norm) or {}
            if entry.get("disable_short_related_video") is True:
                return True
        except Exception as exc:
            logger.warning("Could not read disable_short_related_video from %s: %s", map_file, exc)
    return False


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
    pinned_comment: Optional[str] = None,
    comment_screenshot_path: Optional[str | Path] = None,
    altered_content: str = "unset",
    notify_subscribers: Optional[bool] = None,
    no_notify_subscribers: bool = False,
    playlist_name: Optional[str] = None,
    attach_endscreen: bool = False,
) -> dict[str, Any]:
    """Execute end-to-end publish flow for a single video."""
    effective_notify_subscribers: Optional[bool] = (
        False if no_notify_subscribers else notify_subscribers
    )
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

        # Step 5: Fill Metadata (Title, Description, MFK, Altered Content, Tags, Language, Category)
        await client.fill_details(
            title=title,
            description=description,
            is_kids=False,
            tags=tags,
            language=language,
            category=category,
            altered_content=altered_content,
        )

        playlist_result: Optional[dict[str, Any]] = None
        if playlist_name:
            try:
                playlist_result = await client.ensure_and_select_playlist(playlist_name)
            except Exception as pl_err:
                logger.warning("Playlist assignment (%s) failed during wizard: %s", playlist_name, pl_err)

        notify_result: Optional[dict[str, Any]] = None
        if effective_notify_subscribers is not None:
            try:
                notify_result = await client.set_notify_subscribers(bool(effective_notify_subscribers))
            except Exception as ns_err:
                logger.warning("set_notify_subscribers(%s) failed during wizard: %s", effective_notify_subscribers, ns_err)

        # Step 6: Custom Thumbnail (Long 16:9 & Short 9:16)
        thumbnail_status = False
        if thumbnail_path:
            thumbnail_status = await client.upload_thumbnail(
                thumbnail_path,
                strict_thumbnail=strict_thumbnail,
            )
        elif is_short:
            logger.warning(
                "Short upload called without --thumbnail! On Tier-2+ channels YouTube will pick an arbitrary body frame instead of custom 9:16 cover."
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

        endscreen_result: Optional[dict[str, Any]] = None
        if attach_endscreen and not is_short:
            try:
                endscreen_result = await client.attach_endscreen_template(video_url_or_id=None)
            except Exception as es_err:
                logger.warning("Could not attach endscreen on elements step (continuing publish): %s", es_err)

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
                            vis_low = (edit_verification.get("visibility_text") or "").strip().lower() if edit_verification else ""
                            has_pub_or_pending_vis = any(
                                kw in vis_low
                                for kw in (
                                    "công khai",
                                    "public",
                                    "đang chờ xử lý",
                                    "pending",
                                    "đang xử lý",
                                    "processing",
                                    "đã lên lịch",
                                    "scheduled",
                                )
                            )
                            accepted = getattr(client, "_last_publish_accepted", False)

                            if not is_draft and (accepted or has_pub_or_pending_vis):
                                logger.warning(
                                    "Video %s confirmed queued/processing or publish accepted (not draft, vis=%r). "
                                    "Marking as PUBLISHED with oembed_pending_processing=True.",
                                    vid_id,
                                    vis_low,
                                )
                                oembed_pending = True
                            else:
                                raise RuntimeError(
                                    f"PUBLIC_VERIFICATION_FAILED: Video '{resolved_url}' confirmed as Draft/Private or unconfirmed in YouTube Studio "
                                    f"(is_draft={is_draft}, accepted={accepted}, visibility={edit_verification.get('visibility_text') if edit_verification else 'unknown'}, "
                                    f"draft_banner={edit_verification.get('draft_banner_text') if edit_verification else ''})."
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
                        target_title=None,
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

        pinned_comment_result: Optional[dict[str, Any]] = None
        if (
            pinned_comment
            and str(pinned_comment).strip()
            and visibility.upper() in ("PUBLIC", "UNLISTED")
            and resolved_url
            and hasattr(client, "post_and_pin_comment")
        ):
            try:
                await asyncio.sleep(2.0)
                pinned_comment_result = await client.post_and_pin_comment(
                    resolved_url,
                    str(pinned_comment).strip(),
                    screenshot_path=comment_screenshot_path,
                )
                logger.info("Post-publish pinned comment result: %s", pinned_comment_result)
            except Exception as pin_err:
                logger.warning("Could not post/pin comment for %s: %s", resolved_url, pin_err)
                pinned_comment_result = {
                    "success": False,
                    "posted": False,
                    "pinned": False,
                    "error": str(pin_err),
                }

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
            "pinned_comment": pinned_comment_result,
            "notify_subscribers": effective_notify_subscribers,
            "notify_subscribers_result": notify_result,
            "playlist_result": playlist_result,
            "endscreen_result": endscreen_result,
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
    altered_content = "unset"

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

    m_altered = re.search(r"-\s*\*\*Nội dung đã chỉnh sửa(?:\s*\([^)]*\))?\*\*:\s*([^\n\r]+)", text, re.IGNORECASE)
    if m_altered:
        raw_alt = m_altered.group(1).strip().lower()
        if any(tok in raw_alt for tok in ("có", "yes", "true")):
            altered_content = "yes"
        elif any(tok in raw_alt for tok in ("không", "no", "false")):
            altered_content = "no"

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "language": language,
        "category": category,
        "pinned_comment": pinned_comment,
        "altered_content": altered_content,
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
    parser.add_argument("--attach-subtitles", help="Retroactively attach .srt subtitles to an existing video (requires --video-url or --video-id and --channel)")
    parser.add_argument("--post-pinned-comment", action="store_true", help="Retroactively post & pin comment on an existing PUBLIC video (requires --video-url or --video-id, --channel, and --pinned-comment or --metadata)")
    parser.add_argument("--pinned-comment", help="Comment text to post & pin (defaults to ## 5. Binh luan ghim in --metadata)")
    parser.add_argument("--no-pin-comment", action="store_true", help="Do not post/pin comment even if present in --metadata")
    parser.add_argument("--comment-screenshot", help="Output path for pinned comment verification screenshot")
    parser.add_argument("--video-url", help="Existing video URL")
    parser.add_argument("--video-id", help="Existing video ID")
    parser.add_argument("--subtitles", help="Path to subtitles SRT file")
    parser.add_argument("--visibility", "--privacy", dest="visibility", default="PUBLIC", choices=["PUBLIC", "UNLISTED", "PRIVATE"])
    parser.add_argument("--short", action="store_true", help="Mark as Short (9:16)")
    parser.add_argument("--related-video", help="Related video URL or ID (for Shorts)")
    parser.add_argument("--clear-related-video", action="store_true", help="Retroactively clear Related Video from an existing Short (requires --video-url or --video-id and --channel)")
    parser.add_argument("--screenshot", help="Output path for verification screenshot")
    parser.add_argument("--edit-screenshot", help="Output path for post-publish Studio /edit verification screenshot")
    parser.add_argument("--headless", action="store_true", default=True, help="Run Chrome in headless mode (default True)")
    parser.add_argument("--no-headless", "--headed", dest="headless", action="store_false", help="Run Chrome with GUI")
    parser.add_argument("--bypass-review-gate", action="store_true", help="Bypass mandatory review approval gate")
    parser.add_argument(
        "--altered-content",
        choices=["unset", "yes", "no"],
        default="unset",
        help="YouTube Studio altered/synthetic content disclosure radio (`yes` for AI/35mm channels, `no`, or `unset`).",
    )
    parser.add_argument(
        "--no-notify-subscribers",
        action="store_true",
        help="Uncheck 'Publish to subscriptions feed and notify subscribers' (automatically unchecked for long_16x9 uploads when passed or in-place via --video-id).",
    )
    parser.add_argument(
        "--notify-subscribers",
        action="store_true",
        help="Explicitly keep 'Publish to subscriptions feed and notify subscribers' checked.",
    )
    parser.add_argument(
        "--playlist",
        default=None,
        help="Assign video to playlist in Details (creates playlist if missing; e.g. 'Sử Kể Lại — Hồ Sơ Chiến Dịch & Bí Ẩn Đại Việt').",
    )
    parser.add_argument(
        "--attach-endscreen",
        action="store_true",
        help="Attach 2-element End Screen template (Best for viewer + Most recent upload / Subscribe) on Long videos.",
    )
    parser.add_argument(
        "--set-related-video",
        default=None,
        help="Retroactively link Related Video on an existing Short (/video/<SHORT_VID>/edit) to parent Long video ID or title.",
    )
    parser.add_argument(
        "--update-studio-settings",
        action="store_true",
        help="Run in-place /video/<VID>/edit settings update (--no-notify-subscribers, --playlist, --attach-endscreen, --title, --description, --clean-dead-links).",
    )
    parser.add_argument(
        "--clean-dead-links",
        action="store_true",
        help="Remove dead Private video links (y5VeObQ7u1E, o_3FRlZ87wE, CbeJM6jT4ag) from video description.",
    )

    args = parser.parse_args()

    title = args.title
    description = args.description
    tags = args.tags
    language = args.language
    category = args.category
    pinned_comment = args.pinned_comment
    altered_content = args.altered_content

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
        if not pinned_comment:
            pinned_comment = meta.get("pinned_comment")
        if altered_content == "unset" and meta.get("altered_content") in ("yes", "no"):
            altered_content = meta["altered_content"]

    if args.no_pin_comment:
        pinned_comment = None

    if args.clean_dead_links and description:
        description, _ = clean_dead_links_from_description(description)

    validate_no_sister_channel_leak(args.channel, description, pinned_comment)

    in_place_edit_requested = bool(
        args.update_studio_settings
        or args.set_related_video
        or (
            not args.video
            and (args.video_url or args.video_id)
            and (
                args.no_notify_subscribers
                or args.notify_subscribers
                or args.playlist
                or args.attach_endscreen
                or args.clean_dead_links
                or args.title
                or args.description
                or args.metadata
            )
        )
    )

    retroactive_mode = bool(
        args.update_thumbnail
        or args.attach_subtitles
        or args.post_pinned_comment
        or args.clear_related_video
        or in_place_edit_requested
    )

    if not title and not retroactive_mode:
        parser.error("Title must be specified via --title or --metadata")
    if not retroactive_mode and not args.video:
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

    if not args.bypass_review_gate and job_id and not retroactive_mode:
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
                res = await c.update_video_thumbnail_post_publish(
                    target_video,
                    args.update_thumbnail,
                    edit_screenshot_path=getattr(args, "edit_screenshot", None),
                    strict_thumbnail=args.strict_thumbnail,
                )
                return res
            finally:
                await c.close()
                c.terminate_browser()

        update_res = asyncio.run(_run_update())
        print(json.dumps(update_res, indent=2, ensure_ascii=False))
        sys.exit(0 if (isinstance(update_res, dict) and update_res.get("success")) else 1)

    if args.attach_subtitles:
        target_video = args.video_url or args.video_id
        if not target_video:
            parser.error("--attach-subtitles requires --video-url or --video-id")
        if not profile_cfg:
            parser.error("--attach-subtitles requires a valid --channel or --profile")

        async def _run_subtitles():
            c = YouTubeCDPClient(profile_cfg, headless=args.headless)
            try:
                await c.connect()
                ok = await c.attach_subtitles_post_publish(target_video, args.attach_subtitles)
                return {"success": bool(ok), "video": target_video, "subtitles_path": str(args.attach_subtitles)}
            finally:
                await c.close()
                c.terminate_browser()

        sub_res = asyncio.run(_run_subtitles())
        print(json.dumps(sub_res, indent=2, ensure_ascii=False))
        sys.exit(0 if sub_res.get("success") else 1)

    if args.post_pinned_comment:
        target_video = args.video_url or args.video_id
        if not target_video:
            parser.error("--post-pinned-comment requires --video-url or --video-id")
        if not profile_cfg:
            parser.error("--post-pinned-comment requires a valid --channel or --profile")
        if not pinned_comment or not str(pinned_comment).strip():
            parser.error("--post-pinned-comment requires --pinned-comment or --metadata containing ## 5. Binh luan ghim")

        async def _run_pin_comment():
            c = YouTubeCDPClient(profile_cfg, headless=args.headless)
            try:
                await c.connect()
                res = await c.post_and_pin_comment(
                    target_video,
                    str(pinned_comment).strip(),
                    screenshot_path=getattr(args, "comment_screenshot", None) or args.screenshot,
                )
                return res
            finally:
                await c.close()
                c.terminate_browser()

        pin_res = asyncio.run(_run_pin_comment())
        print(json.dumps(pin_res, indent=2, ensure_ascii=False))
        sys.exit(0 if (isinstance(pin_res, dict) and pin_res.get("success")) else 1)

    if args.clear_related_video:
        target_video = args.video_url or args.video_id
        if not target_video:
            parser.error("--clear-related-video requires --video-url or --video-id")
        if not profile_cfg:
            parser.error("--clear-related-video requires a valid --channel or --profile")

        async def _run_clear_related():
            c = YouTubeCDPClient(profile_cfg, headless=args.headless)
            try:
                await c.connect()
                res = await c.clear_related_video_post_publish(
                    target_video,
                    edit_screenshot_path=getattr(args, "edit_screenshot", None) or args.screenshot,
                )
                return res
            finally:
                await c.close()
                c.terminate_browser()

        clr_res = asyncio.run(_run_clear_related())
        print(json.dumps(clr_res, indent=2, ensure_ascii=False))
        sys.exit(0 if (isinstance(clr_res, dict) and clr_res.get("success")) else 1)

    if args.set_related_video and not args.update_studio_settings:
        target_video = args.video_url or args.video_id
        if not target_video:
            parser.error("--set-related-video requires --video-url or --video-id")
        if not profile_cfg:
            parser.error("--set-related-video requires a valid --channel or --profile")

        async def _run_set_related():
            c = YouTubeCDPClient(profile_cfg, headless=args.headless)
            try:
                await c.connect()
                res = await c.attach_related_video_existing_short(
                    target_video,
                    args.set_related_video,
                    screenshot_path=getattr(args, "edit_screenshot", None) or args.screenshot,
                )
                return res
            finally:
                await c.close()
                c.terminate_browser()

        rel_res = asyncio.run(_run_set_related())
        print(json.dumps(rel_res, indent=2, ensure_ascii=False))
        sys.exit(0 if (isinstance(rel_res, dict) and rel_res.get("success")) else 1)

    if in_place_edit_requested:
        target_video = args.video_url or args.video_id
        if not target_video:
            parser.error("In-place Studio settings update requires --video-url or --video-id")
        if not profile_cfg:
            parser.error("In-place Studio settings update requires a valid --channel or --profile")

        notify_opt: Optional[bool] = None
        if args.no_notify_subscribers:
            notify_opt = False
        elif args.notify_subscribers:
            notify_opt = True

        async def _run_in_place_settings():
            c = YouTubeCDPClient(profile_cfg, headless=args.headless)
            try:
                await c.connect()
                res = await c.update_existing_video_studio_settings(
                    target_video,
                    notify_subscribers=notify_opt,
                    title=title if (args.title or args.metadata) else None,
                    description=description if (args.description or args.metadata) else None,
                    clean_dead_links=DEAD_PRIVATE_VIDEO_IDS if args.clean_dead_links else None,
                    thumbnail_path=args.thumbnail,
                    strict_thumbnail=args.strict_thumbnail,
                    playlist_name=args.playlist,
                    attach_endscreen=args.attach_endscreen,
                    related_video=args.set_related_video or args.related_video,
                    screenshot_path=getattr(args, "edit_screenshot", None) or args.screenshot,
                )
                return res
            finally:
                await c.close()
                c.terminate_browser()

        settings_res = asyncio.run(_run_in_place_settings())
        print(json.dumps(settings_res, indent=2, ensure_ascii=False))
        sys.exit(0 if (isinstance(settings_res, dict) and settings_res.get("success")) else 1)

    effective_related_video = args.related_video
    if args.short and args.channel and is_short_related_video_disabled(args.channel):
        if effective_related_video:
            logger.info(
                "Channel '%s' has short_attach_related_video disabled — ignoring --related-video=%s.",
                args.channel,
                effective_related_video,
            )
        effective_related_video = None

    # For long_16x9 uploads, default notify_subscribers to False when --no-notify-subscribers is passed
    upload_notify_subscribers: Optional[bool] = None
    if args.no_notify_subscribers:
        upload_notify_subscribers = False
    elif args.notify_subscribers:
        upload_notify_subscribers = True
    elif not args.short and str(args.channel or "").strip().replace("-", "_") == "su_ke_lai":
        upload_notify_subscribers = False

    upload_playlist = args.playlist
    if not upload_playlist and not args.short and str(args.channel or "").strip().replace("-", "_") == "su_ke_lai":
        upload_playlist = DEFAULT_SU_KE_LAI_PLAYLIST

    result = asyncio.run(
        publish_single_video(
            video_path=args.video,
            title=title,
            description=description,
            thumbnail_path=args.thumbnail,
            subtitles_path=args.subtitles,
            visibility=args.visibility,
            is_short=args.short,
            related_video_url=effective_related_video,
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
            pinned_comment=pinned_comment,
            comment_screenshot_path=getattr(args, "comment_screenshot", None),
            altered_content=altered_content,
            notify_subscribers=upload_notify_subscribers,
            no_notify_subscribers=bool(args.no_notify_subscribers),
            playlist_name=upload_playlist,
            attach_endscreen=bool(args.attach_endscreen or (not args.short and str(args.channel or "").strip().replace("-", "_") == "su_ke_lai")),
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
                                "related_video_url": effective_related_video,
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
