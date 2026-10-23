#!/usr/bin/env python3
"""Direct 3-Profile Chrome CDP Client for Google Flow Image Generation (vp-flow-cdp).

Connects directly to the 3 signed-in Chrome CDP profiles (ports 9225/9222, 9223, 9224),
arms the document_start reCAPTCHA Enterprise guard via Page.addScriptToEvaluateOnNewDocument,
and executes batchexecute image generation RPCs directly inside the browser tabs
without any external daemon or extension.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import socket
import subprocess
import time
import urllib.request
from typing import Any, Optional

import websockets

from . import flow_rpc

logger = logging.getLogger("flow_cdp.direct_client")

SITE_KEY = "6LdsFiUsAAAAAIjVDZcuLhaHiDn5nnHVXVRQGeMV"

CDP_RECAPTCHA_GUARD_JS = r"""
(function () {
  'use strict';
  let _pristineExecute = null;
  let _capturedTrapped = false;
  let _captureSource = null;

  function savePristine(fn, enterprise, source) {
    if (_pristineExecute || typeof fn !== 'function') return false;
    try {
      const src = fn.toString();
      if (src.includes('extension_hijack_detected')) {
        _capturedTrapped = true;
        return false;
      }
    } catch (e) {}
    _pristineExecute = fn.bind(enterprise);
    _captureSource = source;
    Promise.resolve().then(cleanAllTraps);
    return true;
  }

  function cleanTrap(obj, prop) {
    try {
      const desc = Object.getOwnPropertyDescriptor(obj, prop);
      if (!desc || (!desc.get && !desc.set)) return;
      Object.defineProperty(obj, prop, {
        value: desc.get ? desc.get() : undefined,
        writable: true,
        configurable: true,
        enumerable: true,
      });
    } catch (e) {}
  }

  let _cleanedUp = false;
  function cleanAllTraps() {
    if (_cleanedUp) return;
    _cleanedUp = true;
    try {
      const gc = window.grecaptcha;
      if (gc) {
        const ent = gc.enterprise;
        if (ent) cleanTrap(ent, 'execute');
        cleanTrap(gc, 'enterprise');
      }
      cleanTrap(window, 'grecaptcha');
    } catch (e) {}
  }

  function watchExecute(enterprise) {
    let _val = enterprise.execute;
    if (typeof _val === 'function' && savePristine(_val, enterprise, 'L3-immediate')) return;
    try {
      Object.defineProperty(enterprise, 'execute', {
        get() { return _val; },
        set(fn) { _val = fn; savePristine(fn, enterprise, 'L3-setter'); },
        configurable: true,
        enumerable: true,
      });
    } catch (e) {}
  }

  function watchEnterprise(grecaptcha) {
    let _val = grecaptcha.enterprise;
    if (_val && typeof _val === 'object') watchExecute(_val);
    try {
      Object.defineProperty(grecaptcha, 'enterprise', {
        get() { return _val; },
        set(obj) { _val = obj; if (obj && typeof obj === 'object') watchExecute(obj); },
        configurable: true,
        enumerable: true,
      });
    } catch (e) {}
  }

  function installCapture() {
    let _val = window.grecaptcha;
    if (_val && typeof _val === 'object') watchEnterprise(_val);
    try {
      Object.defineProperty(window, 'grecaptcha', {
        get() { return _val; },
        set(obj) { _val = obj; if (obj && typeof obj === 'object') watchEnterprise(obj); },
        configurable: true,
        enumerable: true,
      });
    } catch (e) {}

    const pollId = setInterval(() => {
      if (_pristineExecute) { clearInterval(pollId); return; }
      try {
        const exec = window.grecaptcha?.enterprise?.execute;
        if (typeof exec === 'function') {
          savePristine(exec, window.grecaptcha.enterprise, 'poll-2ms');
          if (_pristineExecute) clearInterval(pollId);
        }
      } catch (e) {}
    }, 2);
    setTimeout(() => clearInterval(pollId), 30000);
  }

  installCapture();

  try {
    if (!window.__vp_cdp_hijack) {
      Object.defineProperty(window, '__vp_cdp_hijack', {
        value: Object.freeze({
          get pristine() { return _pristineExecute; },
          get trapped() { return _capturedTrapped; },
          get source()  { return _captureSource; },
        }),
        writable: true,
        configurable: true,
        enumerable: false,
      });
    }
  } catch (e) {
    try {
      if (!window.__vp_cdp_hijack) {
        window.__vp_cdp_hijack = {
          get pristine() { return _pristineExecute; },
          get trapped() { return _capturedTrapped; },
          get source()  { return _captureSource; },
        };
      }
    } catch (err) {}
  }

  const SITE_KEY_FALLBACK = '6LdsFiUsAAAAAIjVDZcuLhaHiDn5nnHVXVRQGeMV';
  const _realObjectAssign = Object.assign;
  let captchaMintTail = Promise.resolve();

  function resolveSitekey() {
    try {
      const clients = (window.___grecaptcha_cfg || {}).clients || {};
      for (const k of Object.keys(clients)) {
        if (clients[k] && clients[k].sitekey) return clients[k].sitekey;
      }
    } catch (e) {}
    return SITE_KEY_FALLBACK;
  }

  function waitReady(timeout = 5000) {
    return new Promise((resolve) => {
      let done = false;
      const fin = () => { if (!done) { done = true; resolve(); } };
      try { window.grecaptcha?.enterprise?.ready?.(fin); } catch (e) {}
      setTimeout(fin, timeout);
    });
  }

  async function executeWithAssignNeuter(sitekey, action) {
    const targetAction = action;
    Object.assign = function (target, ...sources) {
      const result = _realObjectAssign.call(this, target, ...sources);
      if (result && typeof result === 'object' && result.action === 'extension_hijack_detected') {
        result.action = targetAction;
      }
      return result;
    };
    try {
      await waitReady(2500);
      const fn = window.__vp_cdp_hijack?.pristine || window.grecaptcha?.enterprise?.execute;
      if (typeof fn !== 'function') throw new Error('grecaptcha_not_ready');
      const token = await Promise.race([
        fn(sitekey, { action }),
        new Promise((_, rej) => setTimeout(() => rej(new Error('execute_hang')), 8000)),
      ]);
      return token ? String(token) : null;
    } finally {
      Object.assign = _realObjectAssign;
    }
  }

  window.mintCaptcha = async function (pageAction) {
    const previous = captchaMintTail.catch(() => {});
    let release;
    captchaMintTail = new Promise((resolve) => { release = resolve; });
    await previous;
    try {
      let lastErr = null;
      for (let i = 0; i < 2; i++) {
        try {
          const token = await executeWithAssignNeuter(resolveSitekey(), pageAction);
          if (token) return token;
        } catch (e) {
          lastErr = e;
        }
        await new Promise((r) => setTimeout(r, 100));
      }
      throw lastErr || new Error('captcha_mint_failed');
    } finally {
      release();
    }
  };
})();
"""

PROFILES = [
    {
        "name": "profile_1",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-p1"),
        "profile_dir": "Profile 1",
        "cdp_port": 9225,
        "url": "https://flow.google.com/project/3cc9a378-4801-4a5e-b984-4370e0c3d2aa",
        "project_id": "3cc9a378-4801-4a5e-b984-4370e0c3d2aa",
    },
    {
        "name": "profile_2",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-p2"),
        "profile_dir": "Profile 2",
        "cdp_port": 9223,
        "url": "https://flow.google.com/project/917085b1-ed75-4d4e-aa3e-dad16f6ee7b4",
        "project_id": "917085b1-ed75-4d4e-aa3e-dad16f6ee7b4",
    },
    {
        "name": "profile_3",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-p3"),
        "profile_dir": "Profile 3",
        "cdp_port": 9224,
        "url": "https://flow.google.com/project/afc36132-bdc0-4d3c-9440-a4a63d8cdfbf",
        "project_id": "afc36132-bdc0-4d3c-9440-a4a63d8cdfbf",
    },
    {
        "name": "profile_4",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile4"),
        "profile_dir": "Profile 4",
        "cdp_port": 9222,
        "url": "https://flow.google.com/project/45f66f11-b15f-4fc5-bcfc-fa46f874f57f",
        "project_id": "45f66f11-b15f-4fc5-bcfc-fa46f874f57f",
    },
    {
        "name": "profile_5",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile5"),
        "profile_dir": "Default",
        "cdp_port": 9226,
        "url": "https://flow.google.com/project/ecc61241-f9a6-40f4-bc63-8a50c8f94672",
        "project_id": "ecc61241-f9a6-40f4-bc63-8a50c8f94672",
    },
    {
        "name": "profile_6",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile7"),
        "profile_dir": "Profile 7",
        "cdp_port": 9227,
        "url": "https://flow.google.com/project/8cc6cb2b-8a51-4f86-8772-63f31b1947df",
        "project_id": "8cc6cb2b-8a51-4f86-8772-63f31b1947df",
    },
    {
        "name": "profile_7",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile11"),
        "profile_dir": "Profile 11",
        "cdp_port": 9228,
        "url": "https://flow.google.com/project/d17a7e81-7c91-4c28-98e4-b77873a11007",
        "project_id": "d17a7e81-7c91-4c28-98e4-b77873a11007",
    },
    {
        "name": "profile_8",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-p5"),
        "profile_dir": "Profile 5",
        "cdp_port": 9229,
        "url": "https://flow.google.com/project/e28b8f92-8da2-4d39-a9f5-c88984b22008",
        "project_id": "e28b8f92-8da2-4d39-a9f5-c88984b22008",
    },
    {
        "name": "profile_9",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-p15"),
        "profile_dir": "Profile 15",
        "cdp_port": 9230,
        "url": "https://flow.google.com/project/f39c90a3-9eb3-4e4a-ba06-d99a95c33009",
        "project_id": "f39c90a3-9eb3-4e4a-ba06-d99a95c33009",
    },
    {
        "name": "profile_10",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile6"),
        "profile_dir": "Profile 6",
        "cdp_port": 9231,
        "url": "https://flow.google.com/project/a40d01b4-0fc4-4f5b-cb17-ea0ba6d44010",
        "project_id": "a40d01b4-0fc4-4f5b-cb17-ea0ba6d44010",
    },
    {
        "name": "profile_11",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile12"),
        "profile_dir": "Profile 12",
        "cdp_port": 9232,
        "url": "https://flow.google.com/project/b51e02c5-1fd5-4a6c-dc28-fb1cb7e55011",
        "project_id": "b51e02c5-1fd5-4a6c-dc28-fb1cb7e55011",
    },
    {
        "name": "profile_12",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile13"),
        "profile_dir": "Profile 13",
        "cdp_port": 9233,
        "url": "https://flow.google.com/project/c62f13d6-2ae6-4b7d-ed39-ac2dc8f66012",
        "project_id": "c62f13d6-2ae6-4b7d-ed39-ac2dc8f66012",
    },
    {
        "name": "profile_13",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile14"),
        "profile_dir": "Profile 14",
        "cdp_port": 9234,
        "url": "https://flow.google.com/project/d73a24e7-3bf7-4c8e-fe4a-bd3ed9a77013",
        "project_id": "d73a24e7-3bf7-4c8e-fe4a-bd3ed9a77013",
    },
    {
        "name": "profile_14",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile16"),
        "profile_dir": "Profile 16",
        "cdp_port": 9235,
        "url": "https://flow.google.com/project/e84b35f8-4ca8-4d9f-af5b-ce4feab88014",
        "project_id": "e84b35f8-4ca8-4d9f-af5b-ce4feab88014",
    },
    {
        "name": "profile_15",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile17"),
        "profile_dir": "Profile 17",
        "cdp_port": 9236,
        "url": "https://flow.google.com/project/f95c46a9-5db9-4eaf-ba6c-df5afbc99015",
        "project_id": "f95c46a9-5db9-4eaf-ba6c-df5afbc99015",
    },
    {
        "name": "profile_16",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile18"),
        "profile_dir": "Profile 18",
        "cdp_port": 9237,
        "url": "https://flow.google.com/project/0a6d57ba-6eca-4fba-cb7d-ea6bacda0016",
        "project_id": "0a6d57ba-6eca-4fba-cb7d-ea6bacda0016",
    },
    {
        "name": "profile_17",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile19"),
        "profile_dir": "Profile 19",
        "cdp_port": 9238,
        "url": "https://flow.google.com/project/1b7e68cb-7fdb-4acb-dc8e-fb7cbdeb1017",
        "project_id": "1b7e68cb-7fdb-4acb-dc8e-fb7cbdeb1017",
    },
    {
        "name": "profile_18",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile22"),
        "profile_dir": "Profile 22",
        "cdp_port": 9239,
        "url": "https://flow.google.com/project/2c8f79dc-8aec-4bdc-ed9f-ac8dcefc2018",
        "project_id": "2c8f79dc-8aec-4bdc-ed9f-ac8dcefc2018",
    },
    {
        "name": "profile_19",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile23"),
        "profile_dir": "Profile 23",
        "cdp_port": 9240,
        "url": "https://flow.google.com/project/3d9a8aed-9bfd-4ced-fe0a-bd9edafd3019",
        "project_id": "3d9a8aed-9bfd-4ced-fe0a-bd9edafd3019",
    },
    {
        "name": "profile_20",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile8"),
        "profile_dir": "Profile 8",
        "cdp_port": 9241,
        "url": "https://flow.google.com/project/4ea09bfe-ac0e-4dfe-af1b-ce0faefe4020",
        "project_id": "4ea09bfe-ac0e-4dfe-af1b-ce0faefe4020",
    },
]


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def ensure_chrome_profiles_launched(
    profiles: list[dict[str, Any]] | None = None,
    headless: bool = True,
) -> None:
    # Safe default: only launch primary profile if not explicitly specified, preventing RAM exhaustion
    target_profiles = profiles if profiles is not None else [PROFILES[0]]
    env = dict(os.environ)
    if headless:
        env.pop("DISPLAY", None)
    else:
        env["DISPLAY"] = os.environ.get("DISPLAY", ":0")

    try:
        from .accounts import detect_chrome_binary
        chrome_bin = detect_chrome_binary()
    except Exception:
        chrome_bin = "/opt/google/chrome/chrome"

    for p in target_profiles:
        port = p["cdp_port"]
        if is_port_open(port):
            continue
        udir = p["user_data_dir"]
        for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            lp = os.path.join(udir, lock_name)
            if os.path.lexists(lp):
                try:
                    os.unlink(lp)
                except OSError:
                    pass
        cmd = [
            chrome_bin,
            f"--user-data-dir={udir}",
            f"--profile-directory={p['profile_dir']}",
            f"--remote-debugging-port={port}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,AutomaticTabDiscarding,MemorySaverMode",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            "--disable-hang-monitor",
        ]
        if headless:
            cmd.insert(1, "--headless=new")
        cmd.append(p["url"])

        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            from .process_manager import get_process_manager
            pm = get_process_manager()
            with pm._lock:
                pm.active_processes[port] = {
                    "pid": proc.pid,
                    "pgid": proc.pid,
                    "user_data_dir": udir,
                    "profile_dir": p["profile_dir"],
                    "port": port,
                    "headless": headless,
                    "started_at": time.time(),
                    "process": proc,
                }
                pm._save_registry()
        except Exception:
            pass
        try:
            from .lifecycle import register_spawned_port
            register_spawned_port(port)
        except Exception:
            pass
        time.sleep(0.3)

    for p in target_profiles:
        port = p["cdp_port"]
        for _ in range(30):
            if is_port_open(port):
                break
            time.sleep(0.5)


def get_flow_target(cdp_port: int) -> dict[str, Any]:
    req = urllib.request.Request(f"http://127.0.0.1:{cdp_port}/json")
    with urllib.request.urlopen(req, timeout=5) as resp:
        targets = json.loads(resp.read().decode("utf-8"))
    pages = [t for t in targets if t.get("type") == "page"]
    for t in pages:
        u = t.get("url", "")
        if "flow.google.com" in u or "labs.google" in u:
            return t
    if pages:
        return pages[0]
    raise RuntimeError(f"No page target found on CDP port {cdp_port}")


class DirectCDPProfileSession:
    """Direct CDP connection to a single Chrome profile's Google Flow tab."""

    def __init__(self, profile_cfg: dict[str, Any]):
        self.profile_cfg = profile_cfg
        self.name = profile_cfg["name"]
        self.cdp_port = int(profile_cfg["cdp_port"])
        self.default_url = profile_cfg["url"]
        self.project_id = profile_cfg.get("project_id") or self._extract_project_id(self.default_url)
        self.ws = None
        self.msg_id = 0
        self.pending: dict[int, asyncio.Future] = {}
        self._reader_task = None

    @staticmethod
    def _extract_project_id(url: str) -> str:
        m = re.search(r"/project/([0-9a-fA-F-]{36})", url or "")
        return m.group(1) if m else ""

    async def _wait_for_flow_ready(self, timeout: float = 25.0) -> dict[str, Any]:
        """Actively poll the Flow tab until document, WIZ CSRF token, and reCAPTCHA Enterprise are ready."""
        deadline = time.monotonic() + timeout
        probe_js = """
        (() => {
            const readyState = document.readyState;
            const wiz = globalThis.WIZ_global_data || {};
            const hasAt = Boolean(wiz.SNlM0e);
            const hasPristine = Boolean(window.__vp_cdp_hijack?.pristine);
            const execFn = window.grecaptcha?.enterprise?.execute;
            const hasExec = typeof execFn === 'function';
            let trapped = Boolean(window.__vp_cdp_hijack?.trapped);
            if (hasExec && !hasPristine) {
                try {
                    if (String(execFn).includes('extension_hijack_detected')) trapped = true;
                } catch (e) {}
            }
            return {
                readyState,
                hasAt,
                hasPristine,
                hasExec,
                trapped,
                hasMint: typeof window.mintCaptcha === 'function'
            };
        })()
        """
        last_state: dict[str, Any] = {}
        while time.monotonic() < deadline:
            try:
                state = await self.evaluate(probe_js, await_promise=False, timeout=5.0)
                if isinstance(state, dict):
                    last_state = state
                    if (
                        state.get("readyState") == "complete"
                        and state.get("hasAt")
                        and (state.get("hasPristine") or (state.get("hasExec") and not state.get("trapped")))
                    ):
                        return state
            except Exception:
                pass
            await asyncio.sleep(0.5)
        return last_state

    async def connect(self, reload_for_guard: bool = False) -> None:
        target = get_flow_target(self.cdp_port)
        ws_url = target["webSocketDebuggerUrl"]
        cur_url = target.get("url") or self.default_url
        pid = self._extract_project_id(cur_url)
        if pid:
            self.project_id = pid
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
        await self.call("Page.addScriptToEvaluateOnNewDocument", {"source": CDP_RECAPTCHA_GUARD_JS})

        if "/project/" not in str(cur_url) and "/project/" in self.default_url:
            await self.call("Page.navigate", {"url": self.default_url})
            cur_url = self.default_url
            pid = self._extract_project_id(cur_url)
            if pid:
                self.project_id = pid
            await asyncio.sleep(1.0)

        need_reload = reload_for_guard
        if not need_reload:
            has_mint = await self.evaluate("typeof window.mintCaptcha === 'function'", await_promise=False)
            if not has_mint:
                await self.evaluate(CDP_RECAPTCHA_GUARD_JS, await_promise=False)
            state = await self._wait_for_flow_ready(timeout=8.0)
            if state.get("trapped") or not (state.get("hasPristine") or state.get("hasExec")):
                need_reload = True

        if need_reload:
            try:
                await self.call(
                    "Storage.clearDataForOrigin",
                    {
                        "origin": "https://flow.google.com",
                        "storageTypes": "appcache,cache_storage,file_systems,indexeddb,local_storage,service_workers,shader_cache,websql",
                    },
                )
                all_cookies = (await self.call("Network.getAllCookies")).get("cookies", [])
                for c in all_cookies:
                    if "GRECAPTCHA" in c["name"] or c["name"].startswith("_ga"):
                        await self.call(
                            "Network.deleteCookies",
                            {"name": c["name"], "domain": c["domain"], "path": c.get("path", "/")},
                        )
            except Exception:
                pass
            await self.call("Page.reload", {"ignoreCache": False})
            await self._wait_for_flow_ready(timeout=25.0)

        has_mint = await self.evaluate("typeof window.mintCaptcha === 'function'", await_promise=False)
        if not has_mint:
            await self.evaluate(CDP_RECAPTCHA_GUARD_JS, await_promise=False)

    async def reconnect(self) -> None:
        """Re-acquire flow target and re-establish CDP websocket connection."""
        if getattr(self, "_reconnecting", False):
            return
        self._reconnecting = True
        try:
            if self._reader_task and not self._reader_task.done():
                self._reader_task.cancel()
            if self.ws:
                try:
                    await self.ws.close()
                except Exception:
                    pass
                self.ws = None
            target = get_flow_target(self.cdp_port)
            ws_url = target["webSocketDebuggerUrl"]
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
            await self.call("Page.addScriptToEvaluateOnNewDocument", {"source": CDP_RECAPTCHA_GUARD_JS})
            await self.evaluate(CDP_RECAPTCHA_GUARD_JS, await_promise=False)
        finally:
            self._reconnecting = False

    async def close(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
        if self.ws:
            await self.ws.close()

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

    def _is_closed(self) -> bool:
        if self.ws is None:
            return True
        if hasattr(self.ws, "closed"):
            return bool(self.ws.closed)
        if hasattr(self.ws, "state"):
            return getattr(self.ws.state, "name", "") != "OPEN"
        return False

    async def call(self, method: str, params: dict | None = None, timeout: float = 60.0) -> dict:
        if not getattr(self, "_reconnecting", False) and self._is_closed():
            await self.reconnect()
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

    async def evaluate(self, expression: str, await_promise: bool = True, timeout: float = 120.0) -> Any:
        for attempt in range(3):
            try:
                if not getattr(self, "_reconnecting", False) and self._is_closed():
                    await self.reconnect()
                res = await self.call(
                    "Runtime.evaluate",
                    {"expression": expression, "awaitPromise": await_promise, "returnByValue": True},
                    timeout=timeout,
                )
                if "exceptionDetails" in res:
                    exc = res["exceptionDetails"]
                    raise RuntimeError(f"JS exception: {exc.get('text')} {exc.get('exception', {}).get('description', '')}")
                return res.get("result", {}).get("value")
            except (RuntimeError, websockets.exceptions.ConnectionClosed, OSError) as err:
                err_str = str(err).lower()
                is_recoverable = (
                    "navigated or closed" in err_str
                    or "no close frame" in err_str
                    or "connectionclosed" in err_str
                    or isinstance(err, (websockets.exceptions.ConnectionClosed, OSError))
                )
                if is_recoverable and attempt < 2:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    if self.ws:
                        try:
                            await self.ws.close()
                        except Exception:
                            pass
                        self.ws = None
                    continue
                if isinstance(err, (websockets.exceptions.ConnectionClosed, OSError)) or "no close frame" in err_str:
                    err_wrap = RuntimeError(f"CDP_TRANSPORT_CLOSED: {err}")
                    err_wrap.generation_submitted = False
                    err_wrap.retryable_pre_submit = True
                    raise err_wrap from err
                raise

    async def generate_image(
        self,
        prompt: str,
        aspect: str = "16:9",
        model: str = "BELUGA",
        base_media_id: Optional[str] = None,
        ref_media_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        last_unsafe_exc = None
        for attempt_idx in range(3):
            effective_prompt = prompt if attempt_idx == 0 else (prompt + f"\n(Clean educational 2D diagram illustration #{attempt_idx})")
            freq = flow_rpc.image_request(
                prompt=effective_prompt,
                project_id=self.project_id,
                count=1,
                aspect=aspect,
                model=model,
                base_media_id=base_media_id,
                ref_media_ids=ref_media_ids,
            )
            js_code = f"""
            (async () => {{
                let submissionAttempted = false;
                try {{
                    let freqStr = {json.dumps(freq)};
                    const token = await window.mintCaptcha("IMAGE_GENERATION");
                    if (!token) return {{ error: "CAPTCHA_FAILED: empty token", submitted: false }};
                    freqStr = freqStr.split("__CAPTCHA__").join(token);
                    const wiz = globalThis.WIZ_global_data || {{}};
                    const at = wiz.SNlM0e;
                    const sid = wiz.FdrFJe;
                    const bl = wiz.cfb2h;
                    if (!at) return {{ error: "NO_AT_TOKEN", submitted: false }};
                    const reqid = Math.floor(Math.random() * 900000) + 100000;
                    const sourcePath = location.pathname || "/";
                    const hl = (document.documentElement.lang || navigator.language || "en").split("-")[0];
                    const url = `/_/AiSandboxAngularFrontend/data/batchexecute?rpcids=ogiZ0b&source-path=${{encodeURIComponent(sourcePath)}}&bl=${{encodeURIComponent(bl || "")}}&f.sid=${{encodeURIComponent(sid || "")}}&hl=${{encodeURIComponent(hl)}}&_reqid=${{reqid}}&rt=c`;
                    submissionAttempted = true;
                    const resp = await fetch(url, {{
                        method: "POST",
                        credentials: "include",
                        headers: {{
                            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                            "x-same-domain": "1"
                        }},
                        body: new URLSearchParams({{ "f.req": freqStr, at }})
                    }});
                    const text = await resp.text();
                    return {{ status: resp.status, text: text.slice(0, 32000000) }};
                }} catch (err) {{
                    return {{ error: err.message || String(err), submitted: submissionAttempted }};
                }}
            }})()
            """
            out = await self.evaluate(js_code, await_promise=True, timeout=180.0)
            if not isinstance(out, dict) or out.get("error"):
                err_msg = out.get("error") if isinstance(out, dict) else "NO_CDP_RESPONSE"
                err = RuntimeError(str(err_msg))
                if isinstance(out, dict) and out.get("submitted") is False:
                    err.generation_submitted = False
                raise err
            raw_text = out.get("text", "")
            try:
                payload = flow_rpc.first_payload(raw_text, flow_rpc.RPC_GEN_IMAGE)
            except Exception as ex:
                if "PUBLIC_ERROR_UNSAFE_GENERATION" in str(ex) and attempt_idx < 2:
                    last_unsafe_exc = ex
                    await asyncio.sleep(1.5)
                    continue
                if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in str(ex) or "CAPTCHA" in str(ex):
                    raise RuntimeError("FLOW_PROVIDER_BLOCKED: preserve the original session and reconcile; do not resubmit") from ex
                raise
            images = flow_rpc.read_images(payload)
            if not images:
                raise RuntimeError(f"No generated image URL in response (HTTP {out.get('status')})")
            return {
                "media_id": images[0].media_id,
                "url": images[0].url,
                "profile": self.name,
                "project_id": self.project_id,
            }
        raise last_unsafe_exc or RuntimeError("PUBLIC_ERROR_UNSAFE_GENERATION")

    async def generate_images_batch(
        self,
        prompts: list[str],
        aspect: str = "16:9",
        model: str = "BELUGA",
        base_media_id: Optional[str] = None,
        ref_media_ids: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        if not prompts or len(prompts) > 4:
            raise ValueError("prompts must contain 1 to 4 prompt strings")
        freq = flow_rpc.image_request(
            prompt=prompts[0],
            prompts=prompts,
            project_id=self.project_id,
            count=len(prompts),
            aspect=aspect,
            model=model,
            base_media_id=base_media_id,
            ref_media_ids=ref_media_ids,
        )
        js_code = f"""
        (async () => {{
            try {{
                let freqStr = {json.dumps(freq)};
                const token = await window.mintCaptcha("IMAGE_GENERATION");
                if (!token) return {{ error: "CAPTCHA_FAILED: empty token" }};
                freqStr = freqStr.split("__CAPTCHA__").join(token);
                const wiz = globalThis.WIZ_global_data || {{}};
                const at = wiz.SNlM0e;
                const sid = wiz.FdrFJe;
                const bl = wiz.cfb2h;
                if (!at) return {{ error: "NO_AT_TOKEN" }};
                const reqid = Math.floor(Math.random() * 900000) + 100000;
                const sourcePath = location.pathname || "/";
                const hl = (document.documentElement.lang || navigator.language || "en").split("-")[0];
                const url = `/_/AiSandboxAngularFrontend/data/batchexecute?rpcids=ogiZ0b&source-path=${{encodeURIComponent(sourcePath)}}&bl=${{encodeURIComponent(bl || "")}}&f.sid=${{encodeURIComponent(sid || "")}}&hl=${{encodeURIComponent(hl)}}&_reqid=${{reqid}}&rt=c`;
                const resp = await fetch(url, {{
                    method: "POST",
                    credentials: "include",
                    headers: {{
                        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                        "x-same-domain": "1"
                    }},
                    body: new URLSearchParams({{ "f.req": freqStr, at }})
                }});
                const text = await resp.text();
                return {{ status: resp.status, text: text.slice(0, 32000000) }};
            }} catch (err) {{
                return {{ error: err.message || String(err) }};
            }}
        }})()
        """
        out = await self.evaluate(js_code, await_promise=True, timeout=180.0)
        if not isinstance(out, dict) or out.get("error"):
            err_msg = out.get("error") if isinstance(out, dict) else "NO_CDP_RESPONSE"
            err = RuntimeError(str(err_msg))
            if isinstance(out, dict) and out.get("submitted") is False:
                err.generation_submitted = False
            elif any(pat in str(err_msg) for pat in ("CAPTCHA_FAILED", "NO_AT_TOKEN", "CDP_TRANSPORT_CLOSED", "Failed to fetch")):
                err.generation_submitted = False
            raise err
        raw_text = out.get("text", "")
        try:
            payload = flow_rpc.first_payload(raw_text, flow_rpc.RPC_GEN_IMAGE)
        except Exception as ex:
            if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in str(ex) or "CAPTCHA" in str(ex):
                raise RuntimeError("FLOW_PROVIDER_BLOCKED: preserve the original session and reconcile; do not resubmit") from ex
            raise
        images = flow_rpc.read_images(payload)
        if not images:
            raise RuntimeError(f"No generated image URL in response (HTTP {out.get('status')})")
        return [
            {
                "media_id": im.media_id,
                "url": im.url,
                "profile": self.name,
                "project_id": self.project_id,
            }
            for im in images
        ]

