#!/usr/bin/env python3
"""Direct 3-Profile Chrome CDP Client for Google Flow Image Generation (vp-flow-cdp).

Connects directly to the 3 signed-in Chrome CDP profiles (ports 9225/9222, 9223, 9224),
arms the document_start reCAPTCHA Enterprise guard via Page.addScriptToEvaluateOnNewDocument,
and executes batchexecute image generation RPCs directly inside the browser tabs
without any external daemon or extension.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import re
import shutil
import socket
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import websockets
import websockets.exceptions

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
      for (let i = 0; i < 15; i++) {
        try {
          const token = await executeWithAssignNeuter(resolveSitekey(), pageAction);
          if (token) return token;
        } catch (e) {
          lastErr = e;
        }
        await new Promise((r) => setTimeout(r, 500));
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
        "url": "https://flow.google.com/project/d85cc9de-8aa3-48a0-bf98-c92521056dc0",
        "project_id": "d85cc9de-8aa3-48a0-bf98-c92521056dc0",
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
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile24"),
        "profile_dir": "Profile 24",
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
        "url": "https://flow.google.com/project/6e65cdc4-1063-4941-b66a-13ea3b13b984",
        "project_id": "6e65cdc4-1063-4941-b66a-13ea3b13b984",
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
        "url": "https://flow.google.com/project/2bdb755e-e212-4e1e-b72e-502607f4e111",
        "project_id": "2bdb755e-e212-4e1e-b72e-502607f4e111",
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
        "url": "https://flow.google.com/project/bde97c7e-487f-4eb7-b262-11960860e57c",
        "project_id": "bde97c7e-487f-4eb7-b262-11960860e57c",
    },
    {
        "name": "profile_21",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-profile25"),
        "profile_dir": "Profile 25",
        "cdp_port": 9242,
        "url": "https://flow.google.com/project/5fb1ac0f-bd1f-4eff-bf2c-df1abfff5021",
        "project_id": "5fb1ac0f-bd1f-4eff-bf2c-df1abfff5021",
    },
    {
        "name": "profile_en01",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en01"),
        "profile_dir": "Default",
        "cdp_port": 9251,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en02",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en02"),
        "profile_dir": "Profile 9",
        "cdp_port": 9252,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en03",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en03"),
        "profile_dir": "Profile 12",
        "cdp_port": 9253,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en05",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en05"),
        "profile_dir": "Profile 27",
        "cdp_port": 9255,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en06",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en06"),
        "profile_dir": "Profile 28",
        "cdp_port": 9256,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en07",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en07"),
        "profile_dir": "Profile 29",
        "cdp_port": 9257,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en08",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en08"),
        "profile_dir": "Profile 30",
        "cdp_port": 9258,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en09",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en09"),
        "profile_dir": "Profile 31",
        "cdp_port": 9259,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en10",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en10"),
        "profile_dir": "Profile 32",
        "cdp_port": 9260,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en11",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en11"),
        "profile_dir": "Profile 33",
        "cdp_port": 9261,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en12",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en12"),
        "profile_dir": "Profile 34",
        "cdp_port": 9262,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en13",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en13"),
        "profile_dir": "Profile 35",
        "cdp_port": 9263,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en14",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en14"),
        "profile_dir": "Profile 36",
        "cdp_port": 9264,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en15",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en15"),
        "profile_dir": "Profile 37",
        "cdp_port": 9265,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en16",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en16"),
        "profile_dir": "Profile 38",
        "cdp_port": 9266,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en17",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en17"),
        "profile_dir": "Profile 39",
        "cdp_port": 9267,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en18",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en18"),
        "profile_dir": "Profile 40",
        "cdp_port": 9268,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
    {
        "name": "profile_en19",
        "user_data_dir": os.path.expanduser("~/.config/google-chrome-cdp-en19"),
        "profile_dir": "Profile 41",
        "cdp_port": 9269,
        "url": "https://flow.google.com/",
        "project_id": "",
    },
]


def _normalize_profile_dict(raw: dict[str, Any]) -> dict[str, Any]:
    name = str(raw.get("name") or raw.get("id") or f"profile_{raw.get('cdp_port') or raw.get('port')}")
    port = int(raw.get("cdp_port") or raw.get("port") or 9225)
    profile_dir = str(raw.get("profile_dir") or raw.get("directory") or "Default")
    user_data_dir = os.path.expanduser(str(raw.get("user_data_dir") or ""))
    url = "https://flow.google.com/"
    project_id = str(raw.get("project_id") or "")
    if re.search(r"[0-9]0(0[789]|1[0-9]|2[01])$", project_id):
        project_id = ""
    return {
        "name": name,
        "id": name,
        "user_data_dir": user_data_dir,
        "profile_dir": profile_dir,
        "directory": profile_dir,
        "cdp_port": port,
        "port": port,
        "url": url,
        "project_id": project_id,
    }


def get_all_configured_profiles() -> list[dict[str, Any]]:
    """Return all 39 configured Chrome CDP profiles (plus any onboarded profiles in registry)."""
    results: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for p in PROFILES:
        norm = _normalize_profile_dict(p)
        if norm["name"] == "profile_en04":
            continue
        results.append(norm)
        seen_names.add(norm["name"])

    reg_path = Path.home() / ".config/video-pilot/flow/profiles.json"
    if reg_path.is_file():
        try:
            data = json.loads(reg_path.read_text(encoding="utf-8"))
            for p in data.get("profiles", []):
                if not p.get("enabled", True):
                    continue
                norm = _normalize_profile_dict(p)
                if norm["name"] == "profile_en04" or norm["name"] in seen_names:
                    continue
                results.append(norm)
                seen_names.add(norm["name"])
        except Exception:
            pass
    return results


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
    from .process_manager import get_process_manager

    pm = get_process_manager()
    for p in target_profiles:
        port = int(p["cdp_port"])
        if is_port_open(port):
            continue
        launch_cfg = {
            "id": p.get("name", f"port_{port}"),
            "port": port,
            "cdp_port": port,
            "user_data_dir": p["user_data_dir"],
            "profile_dir": p.get("profile_dir", "Default"),
            "directory": p.get("profile_dir", "Default"),
        }
        # Launch lightweight Flow root shell to avoid 404 project redirects & heavy timeline WebGL overhead
        pm.launch(launch_cfg, url="https://flow.google.com/", headless=headless)
        time.sleep(0.25)

    for p in target_profiles:
        port = int(p["cdp_port"])
        for _ in range(30):
            if is_port_open(port):
                break
            time.sleep(0.5)


def get_flow_target(cdp_port: int, retries: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(f"http://127.0.0.1:{cdp_port}/json")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                targets = json.loads(resp.read().decode("utf-8"))
            pages = [t for t in targets if t.get("type") == "page"]
            for t in pages:
                u = t.get("url", "")
                if u and ("flow.google.com" in u or "labs.google" in u):
                    return t
            if pages and attempt > 10:
                return pages[0]
        except Exception:
            pass
        time.sleep(0.5)
    try:
        new_req = urllib.request.Request(f"http://127.0.0.1:{cdp_port}/json/new?https://flow.google.com", method="PUT")
        with urllib.request.urlopen(new_req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass
    raise RuntimeError(f"No page target found on CDP port {cdp_port}")


class DirectCDPProfileSession:
    """Direct CDP connection to a single Chrome profile's Google Flow tab."""

    def __init__(self, profile_cfg: dict[str, Any]):
        self.profile_cfg = profile_cfg
        self.name = str(
            profile_cfg.get("name")
            or profile_cfg.get("id")
            or f"profile_{profile_cfg.get('cdp_port') or profile_cfg.get('port')}"
        )
        self.cdp_port = int(profile_cfg.get("cdp_port") or profile_cfg.get("port") or 9225)
        self.default_url = str(profile_cfg.get("url") or "https://flow.google.com/")
        self.project_id = profile_cfg.get("project_id") or self._extract_project_id(self.default_url)
        self.ws = None
        self.msg_id = 0
        self.pending: dict[int, asyncio.Future] = {}
        self._reader_task = None
        self._model_catalog: Optional[list[dict[str, Any]]] = None

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
        target = None
        last_exc = None
        for _ in range(15):
            try:
                target = await asyncio.to_thread(get_flow_target, self.cdp_port, 4)
                if target and target.get("webSocketDebuggerUrl"):
                    break
            except Exception as e:
                last_exc = e
                await asyncio.sleep(0.5)
        if not target:
            if last_exc:
                raise last_exc
            raise RuntimeError(f"Could not resolve flow target on port {self.cdp_port}")
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
            open_timeout=30,
        )
        self._reader_task = asyncio.create_task(self._reader())
        await self.call("Page.enable")
        await self.call("Runtime.enable")
        await self.call("Page.addScriptToEvaluateOnNewDocument", {"source": CDP_RECAPTCHA_GUARD_JS})

        # Prune any extra duplicate page tabs on this browser to keep memory/renderer count strictly 1 tab
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.cdp_port}/json")
            with urllib.request.urlopen(req, timeout=3) as resp:
                all_targets = json.loads(resp.read().decode("utf-8"))
            active_tid = target.get("id")
            for other in all_targets:
                if other.get("type") == "page" and other.get("id") and other.get("id") != active_tid:
                    try:
                        close_req = urllib.request.Request(
                            f"http://127.0.0.1:{self.cdp_port}/json/close/{other['id']}"
                        )
                        urllib.request.urlopen(close_req, timeout=2).read()
                    except Exception:
                        pass
        except Exception:
            pass

        cur_url_str = str(cur_url or "")
        # Avoid 404 project redirects and heavy timeline WebGL canvas: use lightweight https://flow.google.com/
        if (
            "flow.google.com" not in cur_url_str
            or "/404" in cur_url_str
            or "reason=project" in cur_url_str
        ):
            await self.call("Page.navigate", {"url": "https://flow.google.com/"})
            cur_url = "https://flow.google.com/"
            await asyncio.sleep(0.8)

        need_reload = reload_for_guard
        has_mint = await self.evaluate("typeof window.mintCaptcha === 'function'", await_promise=False)
        if not has_mint:
            await self.evaluate(CDP_RECAPTCHA_GUARD_JS, await_promise=False)
        state = await self._wait_for_flow_ready(timeout=18.0)
        if state.get("trapped"):
            need_reload = True

        if need_reload:
            await self.call("Page.reload", {"ignoreCache": False})
            await self._wait_for_flow_ready(timeout=25.0)

        has_mint = await self.evaluate("typeof window.mintCaptcha === 'function'", await_promise=False)
        if not has_mint:
            await self.evaluate(CDP_RECAPTCHA_GUARD_JS, await_promise=False)
        await asyncio.sleep(2.0)

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
                    or "cannot find default execution context" in err_str
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

    async def _ensure_mint_captcha_guard(self) -> None:
        has_mint = await self.evaluate("typeof window.mintCaptcha === 'function'", await_promise=False)
        if not has_mint:
            await self.evaluate(CDP_RECAPTCHA_GUARD_JS, await_promise=False)

    async def _refresh_recaptcha_session(self) -> None:
        """Refresh reCAPTCHA session in-place without reloading the tab or wiping _GRECAPTCHA trust cookies."""
        try:
            await self._ensure_mint_captcha_guard()
            for x, y in ((210, 210), (460, 330), (640, 420), (350, 280)):
                await self.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
                await asyncio.sleep(0.12)
            await asyncio.sleep(1.5)
        except Exception:
            pass

    async def generate_image(
        self,
        prompt: str,
        aspect: str = "16:9",
        model: str = "BELUGA",
        base_media_id: Optional[str] = None,
        ref_media_ids: Optional[list[str]] = None,
        reference_media_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        await self.ensure_project_id()
        await self._ensure_mint_captcha_guard()
        effective_refs = reference_media_ids if reference_media_ids is not None else ref_media_ids
        for attempt in range(5):
            freq = flow_rpc.image_request(
                prompt=prompt,
                project_id=self.project_id,
                count=1,
                aspect=aspect,
                model=model,
                base_media_id=base_media_id,
                reference_media_ids=effective_refs,
            )
            source_path_override = f"/project/{self.project_id}" if self.project_id else "/"
            js_code = f"""
            (async () => {{
                let submissionAttempted = false;
                try {{
                    let freqStr = {json.dumps(freq)};
                    const token = await window.mintCaptcha({json.dumps(flow_rpc.CAPTCHA_IMAGE)});
                    if (!token) return {{ error: "CAPTCHA_FAILED: empty token", submitted: false }};
                    freqStr = freqStr.split("__CAPTCHA__").join(token);
                    let wiz = globalThis.WIZ_global_data || {{}};
                    let at = wiz.SNlM0e;
                    if (!at) {{
                        for (let w = 0; w < 30; w++) {{
                            await new Promise(r => setTimeout(r, 500));
                            wiz = globalThis.WIZ_global_data || {{}};
                            at = wiz.SNlM0e;
                            if (at) break;
                        }}
                    }}
                    const sid = wiz.FdrFJe;
                    const bl = wiz.cfb2h;
                    if (!at) return {{ error: "NO_AT_TOKEN", submitted: false }};
                    const reqid = Math.floor(Math.random() * 900000) + 100000;
                    const sourcePath = {json.dumps(source_path_override)} || location.pathname || "/";
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
            from .resource_locks import stagger_cross_process_action

            await asyncio.to_thread(stagger_cross_process_action, "flow_rpc_submit", 2.5, 0.4)
            out = await self.evaluate(js_code, await_promise=True, timeout=180.0)
            if not isinstance(out, dict) or out.get("error"):
                err_msg = str(out.get("error") if isinstance(out, dict) else "NO_CDP_RESPONSE")
                if "NO_AT_TOKEN" in err_msg:
                    from .resource_locks import mark_profile_unauthenticated

                    mark_profile_unauthenticated(self.name)
                    err = RuntimeError(err_msg)
                    err.generation_submitted = False
                    raise err
                if attempt < 2 and "CAPTCHA_FAILED" in err_msg:
                    await self._refresh_recaptcha_session()
                    continue
                err = RuntimeError(err_msg)
                if isinstance(out, dict) and out.get("submitted") is False:
                    err.generation_submitted = False
                raise err
            raw_text = out.get("text", "")
            try:
                payload = flow_rpc.first_payload(raw_text, flow_rpc.RPC_GEN_IMAGE)
                break
            except Exception as ex:
                ex_str = str(ex)
                if attempt == 0 and ("NOT_FOUND" in ex_str or "5" in ex_str):
                    await self.ensure_project_id(force_new=True)
                    await self._ensure_mint_captcha_guard()
                    continue
                if "NO_AT_TOKEN" in ex_str:
                    from .resource_locks import mark_profile_unauthenticated

                    mark_profile_unauthenticated(self.name)
                    err_block = RuntimeError(f"FLOW_PROVIDER_BLOCKED: unauthenticated session ({ex})")
                    err_block.generation_submitted = False
                    raise err_block from ex
                if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in ex_str or "TOO_MUCH_TRAFFIC" in ex_str:
                    self._recaptcha_refreshed = True
                    try:
                        await self._refresh_recaptcha_session()
                    except Exception:
                        pass
                    err_block = RuntimeError(
                        f"FLOW_PROVIDER_BLOCKED: preserve the original session and reconcile; do not resubmit ({ex})"
                    )
                    err_block.generation_submitted = False
                    raise err_block from ex
                if "CAPTCHA" in ex_str:
                    if attempt == 0:
                        self._recaptcha_refreshed = True
                        await asyncio.sleep(2.5)
                        await self._refresh_recaptcha_session()
                        continue
                    err_block = RuntimeError(f"FLOW_PROVIDER_BLOCKED: captcha failed ({ex})")
                    err_block.generation_submitted = False
                    raise err_block from ex
                raise
        else:
            raise RuntimeError(f"Image generation failed after retries on {self.name}")
        images = flow_rpc.read_images(payload)
        if not images:
            raise RuntimeError(f"No generated image URL in response (HTTP {out.get('status')})")
        return {
            "media_id": images[0].media_id,
            "url": images[0].url,
            "profile": self.name,
            "project_id": self.project_id,
        }

    async def generate_images_batch(
        self,
        prompts: list[str],
        aspect: str = "16:9",
        model: str = "BELUGA",
        base_media_id: Optional[str] = None,
        ref_media_ids: Optional[list[str]] = None,
        reference_media_ids: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        if not prompts or len(prompts) > 4:
            raise ValueError("prompts must contain 1 to 4 prompt strings")
        await self.ensure_project_id()
        await self._ensure_mint_captcha_guard()
        effective_refs = reference_media_ids if reference_media_ids is not None else ref_media_ids
        freq = flow_rpc.image_request(
            prompt=prompts[0],
            prompts=prompts,
            project_id=self.project_id,
            count=len(prompts),
            aspect=aspect,
            model=model,
            base_media_id=base_media_id,
            reference_media_ids=effective_refs,
        )
        source_path_override = f"/project/{self.project_id}" if self.project_id else "/"
        js_code = f"""
        (async () => {{
            try {{
                let freqStr = {json.dumps(freq)};
                const token = await window.mintCaptcha({json.dumps(flow_rpc.CAPTCHA_IMAGE)});
                if (!token) return {{ error: "CAPTCHA_FAILED: empty token" }};
                freqStr = freqStr.split("__CAPTCHA__").join(token);
                let wiz = globalThis.WIZ_global_data || {{}};
                let at = wiz.SNlM0e;
                if (!at) {{
                    for (let w = 0; w < 30; w++) {{
                        await new Promise(r => setTimeout(r, 500));
                        wiz = globalThis.WIZ_global_data || {{}};
                        at = wiz.SNlM0e;
                        if (at) break;
                    }}
                }}
                const sid = wiz.FdrFJe;
                const bl = wiz.cfb2h;
                if (!at) return {{ error: "NO_AT_TOKEN" }};
                const reqid = Math.floor(Math.random() * 900000) + 100000;
                const sourcePath = {json.dumps(source_path_override)} || location.pathname || "/";
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
        if "PYTEST_CURRENT_TEST" not in os.environ:
            from .resource_locks import stagger_cross_process_action

            await asyncio.to_thread(stagger_cross_process_action, "flow_rpc_submit", 2.5, 0.4)
        out = await self.evaluate(js_code, await_promise=True, timeout=180.0)
        if not isinstance(out, dict) or out.get("error"):
            err_msg = out.get("error") if isinstance(out, dict) else "NO_CDP_RESPONSE"
            if "NO_AT_TOKEN" in str(err_msg):
                from .resource_locks import mark_profile_unauthenticated

                mark_profile_unauthenticated(self.name)
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
            if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in str(ex) or "TOO_MUCH_TRAFFIC" in str(ex) or "CAPTCHA" in str(ex):
                self._recaptcha_refreshed = True
                try:
                    await self._refresh_recaptcha_session()
                except Exception:
                    pass
                err_block = RuntimeError(
                    f"FLOW_PROVIDER_BLOCKED: preserve the original session and reconcile; do not resubmit ({ex})"
                )
                err_block.generation_submitted = False
                raise err_block from ex
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

    async def _post_batchexecute(
        self,
        rpcid: str,
        freq: str,
        captcha_action: Optional[str] = None,
        timeout: float = 180.0,
    ) -> dict[str, Any]:
        """Execute a signed-in batchexecute POST inside the active Flow tab."""
        if captcha_action:
            from .resource_locks import stagger_cross_process_action

            await self._ensure_mint_captcha_guard()
            await asyncio.to_thread(stagger_cross_process_action, "flow_rpc_submit", 2.5, 0.4)
        source_path_override = f"/project/{self.project_id}" if self.project_id else "/"
        js_code = f"""
        (async () => {{
            let submissionAttempted = false;
            try {{
                let freqStr = {json.dumps(freq)};
                const captchaAction = {json.dumps(captcha_action)};
                if (captchaAction) {{
                    const token = await window.mintCaptcha(captchaAction);
                    if (!token) return {{ error: "CAPTCHA_FAILED: empty token", submitted: false }};
                    freqStr = freqStr.split("__CAPTCHA__").join(token);
                }}
                let wiz = globalThis.WIZ_global_data || {{}};
                let at = wiz.SNlM0e;
                if (!at) {{
                    for (let w = 0; w < 30; w++) {{
                        await new Promise(r => setTimeout(r, 500));
                        wiz = globalThis.WIZ_global_data || {{}};
                        at = wiz.SNlM0e;
                        if (at) break;
                    }}
                }}
                const sid = wiz.FdrFJe;
                const bl = wiz.cfb2h;
                if (!at) return {{ error: "NO_AT_TOKEN", submitted: false }};
                const reqid = Math.floor(Math.random() * 900000) + 100000;
                const sourcePath = {json.dumps(source_path_override)} || location.pathname || "/";
                const hl = (document.documentElement.lang || navigator.language || "en").split("-")[0];
                const url = `/_/AiSandboxAngularFrontend/data/batchexecute?rpcids=${{encodeURIComponent({json.dumps(rpcid)})}}&source-path=${{encodeURIComponent(sourcePath)}}&bl=${{encodeURIComponent(bl || "")}}&f.sid=${{encodeURIComponent(sid || "")}}&hl=${{encodeURIComponent(hl)}}&_reqid=${{reqid}}&rt=c`;
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
                return {{ status: resp.status, text: text.slice(0, 32000000), submitted: true }};
            }} catch (err) {{
                return {{ error: err.message || String(err), submitted: submissionAttempted }};
            }}
        }})()
        """
        out = await self.evaluate(js_code, await_promise=True, timeout=timeout)
        if not isinstance(out, dict) or out.get("error"):
            err_msg = out.get("error") if isinstance(out, dict) else "NO_CDP_RESPONSE"
            err = RuntimeError(str(err_msg))
            if isinstance(out, dict) and out.get("submitted") is False:
                err.generation_submitted = False
            raise err
        return out

    async def query_credits(self) -> dict[str, Any]:
        """Query live Flow credit balance via `nzlxg` batchexecute RPC (0 credits cost)."""
        out = await self._post_batchexecute(
            rpcid=flow_rpc.RPC_CREDITS,
            freq=flow_rpc.credits_request(),
            captcha_action=None,
            timeout=60.0,
        )
        payload = flow_rpc.first_payload(out.get("text", ""), flow_rpc.RPC_CREDITS)
        info = flow_rpc.read_credits(payload)
        info["profile"] = self.name
        return info

    async def ensure_project_id(self, title: str = "Video Pilot", force_new: bool = False) -> str:
        """Return existing `project_id` or create a new project via `jHPbke` (0 credits cost)."""
        if self.project_id and not force_new:
            pid = self.project_id
        else:
            out = await self._post_batchexecute(
                rpcid=flow_rpc.RPC_CREATE_PROJECT,
                freq=flow_rpc.create_project_request(title=title),
                captcha_action=None,
                timeout=60.0,
            )
            payload = flow_rpc.first_payload(out.get("text", ""), flow_rpc.RPC_CREATE_PROJECT)
            pid = flow_rpc.read_project_id(payload)
            self.project_id = pid
            self.profile_cfg["project_id"] = pid

        # Enforce valid /project/<pid> workspace path for batchexecute source-path integrity & document_start guard
        did_navigate = False
        try:
            curr_url = await self.evaluate("location.href", await_promise=False)
            target_prefix = f"https://flow.google.com/project/{pid}"
            if not str(curr_url).startswith(target_prefix):
                await self.call("Page.navigate", {"url": target_prefix})
                did_navigate = True
                await self._wait_for_flow_ready(timeout=15.0)
                after_url = await self.evaluate("location.href", await_promise=False)
                if not str(after_url).startswith(target_prefix) and not force_new:
                    return await self.ensure_project_id(title=title, force_new=True)
        except Exception as nav_err:
            logger.debug("Project workspace navigation check: %s", nav_err)

        await self._ensure_mint_captcha_guard()
        if (did_navigate or not getattr(self, "_mouse_warmed", False)) and "PYTEST_CURRENT_TEST" not in os.environ:
            self._mouse_warmed = True
            for mx, my in ((210, 210), (460, 330), (640, 420)):
                try:
                    await self.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": mx, "y": my})
                except Exception:
                    pass
                await asyncio.sleep(0.35)
            await asyncio.sleep(2.5)
        return pid

    @staticmethod
    def _detect_mime_type(raw_bytes: bytes, file_path: Path) -> str:
        if len(raw_bytes) >= 3 and raw_bytes[:3] == b"\xff\xd8\xff":
            return "image/jpeg"
        if len(raw_bytes) >= 4 and raw_bytes[:4] == b"\x89PNG":
            return "image/png"
        if len(raw_bytes) >= 12 and raw_bytes[:4] == b"RIFF" and raw_bytes[8:12] == b"WEBP":
            return "image/webp"
        if len(raw_bytes) >= 4 and raw_bytes[:4] == b"GIF8":
            return "image/gif"
        ext = file_path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            return "image/jpeg"
        if ext == ".webp":
            return "image/webp"
        if ext == ".gif":
            return "image/gif"
        return "image/png"

    async def upload_image_file(
        self,
        image_path: str | os.PathLike[str],
        asset_id: Optional[str] = None,
        is_hidden: bool = False,
    ) -> dict[str, Any]:
        """Upload a local image file to Google Flow via `maseQ` (`Q9a`/`T9a`) and return its `media_id`."""
        path_obj = Path(image_path).expanduser().resolve()
        if not path_obj.is_file():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        raw_bytes = path_obj.read_bytes()
        if not raw_bytes:
            raise ValueError(f"Image file is empty (0 bytes): {image_path}")

        mime_type = self._detect_mime_type(raw_bytes, path_obj)
        b64_data = base64.b64encode(raw_bytes).decode("ascii")
        await self.ensure_project_id()

        for attempt in range(2):
            freq = flow_rpc.upload_image_request(
                image_b64=b64_data,
                mime_type=mime_type,
                project_id=self.project_id,
                file_name=path_obj.name,
                asset_id=asset_id,
                is_hidden=is_hidden,
            )
            out = await self._post_batchexecute(
                rpcid=flow_rpc.RPC_UPLOAD_IMAGE,
                freq=freq,
                captcha_action=flow_rpc.CAPTCHA_UPLOAD_IMAGE,
                timeout=120.0,
            )
            try:
                payload = flow_rpc.first_payload(out.get("text", ""), flow_rpc.RPC_UPLOAD_IMAGE)
                break
            except Exception as ex:
                if attempt == 0 and ("NOT_FOUND" in str(ex) or "5" in str(ex)):
                    await self.ensure_project_id(force_new=True)
                    continue
                raise

        uploaded = flow_rpc.read_uploaded_image(payload)
        sidecar = path_obj.with_suffix(".json")
        if sidecar.is_file() and uploaded.media_id and self.name:
            try:
                sdata = json.loads(sidecar.read_text(encoding="utf-8"))
                if isinstance(sdata, dict):
                    pmap = sdata.get("profile_media_ids")
                    if not isinstance(pmap, dict):
                        pmap = {}
                    pmap[self.name] = str(uploaded.media_id)
                    if self.project_id:
                        pmap[f"{self.name}:{self.project_id}"] = str(uploaded.media_id)
                    sdata["profile_media_ids"] = pmap
                    sidecar.write_text(json.dumps(sdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception:
                pass
        return {
            "media_id": uploaded.media_id,
            "url": uploaded.url,
            "profile": self.name,
            "project_id": self.project_id,
            "file_name": path_obj.name,
            "mime_type": mime_type,
        }

    async def download_authenticated_binary(
        self,
        url: str,
        output_path: Optional[str | os.PathLike[str]] = None,
        timeout: float = 120.0,
    ) -> int | bytes:
        """Download binary asset (image or MP4 video) from `flow-content.google` or signed GCS URL."""
        if not url:
            raise ValueError("Cannot download empty URL")

        js_fetch = f"""
        (async () => {{
            const targetUrl = {json.dumps(url)};
            let resp = null;
            try {{
                resp = await fetch(targetUrl, {{ credentials: "include" }});
            }} catch (e) {{
                resp = await fetch(targetUrl);
            }}
            if (!resp || !resp.ok) {{
                resp = await fetch(targetUrl);
            }}
            if (!resp.ok) throw new Error("HTTP " + resp.status);
            const blob = await resp.blob();
            return await new Promise((resolve, reject) => {{
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result.split(",")[1]);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            }});
        }})()
        """
        raw_bytes: Optional[bytes] = None
        try:
            b64_str = await self.evaluate(js_fetch, await_promise=True, timeout=timeout)
            if isinstance(b64_str, str) and b64_str:
                raw_bytes = base64.b64decode(b64_str)
        except Exception:
            raw_bytes = None

        if not raw_bytes:
            # Fallback: fetch in Python using cookies from the browser session
            cookies_res = await self.call("Network.getAllCookies")
            cookies = cookies_res.get("cookies", [])
            cookie_hdr = "; ".join(
                f"{c['name']}={c['value']}"
                for c in cookies
                if any(dom in c.get("domain", "") for dom in ("google.com", "flow-content.google", "labs.google"))
            )
            headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/136.0.0.0 Safari/537.36"}
            if cookie_hdr and "storage.googleapis.com" not in url:
                headers["Cookie"] = cookie_hdr
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw_bytes = resp.read()

        if not raw_bytes:
            raise RuntimeError(f"Downloaded 0 bytes from {url}")

        if output_path is not None:
            dest = Path(output_path).expanduser().resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw_bytes)
            return len(raw_bytes)
        return raw_bytes

    async def _get_model_catalog(self) -> list[dict[str, Any]]:
        if self._model_catalog is not None:
            return self._model_catalog
        try:
            out = await self._post_batchexecute(
                rpcid=flow_rpc.RPC_MODEL_CATALOG,
                freq=flow_rpc.model_catalog_request(),
                captcha_action=None,
                timeout=30.0,
            )
            payload = flow_rpc.first_payload(out.get("text", ""), flow_rpc.RPC_MODEL_CATALOG)
            self._model_catalog = flow_rpc.read_model_catalog(payload)
        except Exception:
            self._model_catalog = []
        return self._model_catalog

    @staticmethod
    def _verify_mp4_with_ffprobe(mp4_path: Path) -> dict[str, Any]:
        if not mp4_path.is_file() or mp4_path.stat().st_size == 0:
            raise RuntimeError(f"Output MP4 missing or empty: {mp4_path}")
        ffprobe_bin = shutil.which("ffprobe") or "ffprobe"
        cmd = [
            ffprobe_bin,
            "-v",
            "error",
            "-show_entries",
            "stream=width,height,codec_name,codec_type,duration,nb_frames",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(mp4_path.resolve()),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"ffprobe validation failed on {mp4_path}: {res.stderr.strip()}")
        data = json.loads(res.stdout or "{}")
        streams = data.get("streams", [])
        vstream = next((s for s in streams if s.get("codec_type") == "video"), None)
        if not vstream:
            raise RuntimeError(f"No video stream in {mp4_path}")
        width = int(vstream.get("width") or 0)
        height = int(vstream.get("height") or 0)
        dur = float(vstream.get("duration") or data.get("format", {}).get("duration") or 0.0)
        if width <= 0 or height <= 0 or dur <= 0.0:
            raise RuntimeError(f"Invalid video stream in {mp4_path}: {width}x{height}, duration={dur}s")
        return {
            "width": width,
            "height": height,
            "duration": round(dur, 4),
            "codec_name": vstream.get("codec_name", ""),
            "size_bytes": mp4_path.stat().st_size,
        }

    async def generate_video_from_frames(
        self,
        prompt: str,
        first_frame_path_or_id: str | os.PathLike[str],
        last_frame_path_or_id: Optional[str | os.PathLike[str]] = None,
        output_mp4_path: Optional[str | os.PathLike[str]] = None,
        aspect: str = "16:9",
        model: str = "veo_3_1_fast",
        duration_seconds: int = 5,
        seed: Optional[int] = None,
        poll_interval: float = 4.5,
        poll_timeout: float = 360.0,
    ) -> dict[str, Any]:
        """Generate a Veo video clip from a start frame (and optional end frame) via Flow CDP.

        Automatically uploads local frame files (`maseQ`), submits `eb1hJf` (`START_FRAME`)
        or `nprQif` (`START_END_FRAMES`), polls `jwpduf`/`as29s` until completion, downloads
        the MP4, validates with `ffprobe`, and writes a `{stem}.json` provenance sidecar.
        """
        await self.ensure_project_id()

        first_str = str(first_frame_path_or_id)
        did_upload = False
        if Path(first_str).expanduser().is_file():
            up1 = await self.upload_image_file(first_str)
            first_media_id = up1["media_id"]
            did_upload = True
        else:
            first_media_id = first_str

        last_media_id: Optional[str] = None
        if last_frame_path_or_id:
            last_str = str(last_frame_path_or_id)
            if Path(last_str).expanduser().is_file():
                if Path(last_str).expanduser().resolve() == Path(first_str).expanduser().resolve():
                    last_media_id = first_media_id
                else:
                    if did_upload:
                        await asyncio.sleep(3.0)
                    up2 = await self.upload_image_file(last_str)
                    last_media_id = up2["media_id"]
                    did_upload = True
            else:
                last_media_id = last_str

        await asyncio.sleep(2.5 if did_upload else 1.2)
        if did_upload and "PYTEST_CURRENT_TEST" not in os.environ:
            for mx, my in ((240, 260), (510, 340), (680, 410)):
                try:
                    await self.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": mx, "y": my})
                except Exception:
                    pass
                await asyncio.sleep(0.25)
            await asyncio.sleep(6.0)
        catalog = await self._get_model_catalog()
        resolved_model = flow_rpc.resolve_video_model(
            model,
            aspect=aspect,
            has_start_frame=True,
            has_end_frame=bool(last_media_id),
            catalog=catalog,
            duration_seconds=duration_seconds,
        )
        rpcid, freq = flow_rpc.video_frames_request(
            prompt=prompt,
            project_id=self.project_id,
            first_frame_media_id=first_media_id,
            last_frame_media_id=last_media_id,
            aspect=aspect,
            model=resolved_model,
            count=1,
            catalog=catalog,
            duration_seconds=duration_seconds,
        )

        sub_payload = None
        for vid_attempt in range(3):
            try:
                out = await self._post_batchexecute(
                    rpcid=rpcid,
                    freq=freq,
                    captcha_action=flow_rpc.CAPTCHA_VIDEO,
                    timeout=180.0,
                )
                sub_payload = flow_rpc.first_payload(out.get("text", ""), rpcid)
                break
            except Exception as ex:
                ex_s = str(ex)
                if "NO_AT_TOKEN" in ex_s:
                    from .resource_locks import mark_profile_unauthenticated

                    mark_profile_unauthenticated(self.name)
                    err_block = RuntimeError(f"FLOW_PROVIDER_BLOCKED: unauthenticated session ({ex})")
                    err_block.generation_submitted = False
                    raise err_block from ex
                if "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in ex_s or "TOO_MUCH_TRAFFIC" in ex_s:
                    self._recaptcha_refreshed = True
                    try:
                        await self._refresh_recaptcha_session()
                    except Exception:
                        pass
                    err_block = RuntimeError(
                        f"FLOW_PROVIDER_BLOCKED: preserve the original session and reconcile; do not resubmit ({ex})"
                    )
                    err_block.generation_submitted = False
                    raise err_block from ex
                if "CAPTCHA_FAILED" in ex_s or "CAPTCHA" in ex_s:
                    if vid_attempt == 0:
                        self._recaptcha_refreshed = True
                        await asyncio.sleep(2.5)
                        await self._refresh_recaptcha_session()
                        continue
                    err_block = RuntimeError(f"FLOW_PROVIDER_BLOCKED: captcha failed ({ex})")
                    err_block.generation_submitted = False
                    raise err_block from ex
                raise

        sub_info = flow_rpc.read_video_submission(sub_payload)
        media_id = sub_info["media_id"]
        video_url = sub_info.get("url") or ""

        deadline = time.monotonic() + poll_timeout
        poll_count = 0
        while not video_url and time.monotonic() < deadline:
            await asyncio.sleep(poll_interval)
            poll_count += 1
            poll_out = await self._post_batchexecute(
                rpcid=flow_rpc.RPC_OPERATION,
                freq=flow_rpc.operation_request([media_id]),
                captcha_action=None,
                timeout=60.0,
            )
            poll_payload = flow_rpc.first_payload(poll_out.get("text", ""), flow_rpc.RPC_OPERATION)
            poll_info = flow_rpc.read_video_poll(poll_payload, target_media_id=media_id)
            if poll_info["status"] == "failed":
                raise RuntimeError(poll_info.get("error") or f"Video generation failed for {media_id}")
            if poll_info.get("url"):
                video_url = poll_info["url"]
                break

            # Secondary check via as29s if jwpduf returned done without URL or periodically
            if (poll_info["status"] == "completed" or poll_count % 2 == 0) and not video_url:
                try:
                    media_out = await self._post_batchexecute(
                        rpcid=flow_rpc.RPC_MEDIA,
                        freq=flow_rpc.media_request(media_id),
                        captcha_action=None,
                        timeout=60.0,
                    )
                    media_payload = flow_rpc.first_payload(media_out.get("text", ""), flow_rpc.RPC_MEDIA)
                    media_info = flow_rpc.read_video_poll(media_payload, target_media_id=media_id)
                    if media_info.get("url"):
                        video_url = media_info["url"]
                        break
                except Exception:
                    pass

        if not video_url:
            raise TimeoutError(f"Timed out after {poll_timeout}s waiting for video {media_id}")

        result: dict[str, Any] = {
            "media_id": media_id,
            "url": video_url,
            "profile": self.name,
            "project_id": self.project_id,
            "model": model,
            "resolved_model": resolved_model,
            "aspect": aspect,
            "first_frame_media_id": first_media_id,
            "last_frame_media_id": last_media_id,
            "duration_seconds": duration_seconds,
            "seed": seed,
        }

        if output_mp4_path is not None:
            out_path = Path(output_mp4_path).expanduser().resolve()
            await self.download_authenticated_binary(video_url, out_path, timeout=180.0)
            probe_info = self._verify_mp4_with_ffprobe(out_path)
            sidecar_path = out_path.with_suffix(".json")
            result["output_mp4_path"] = str(out_path)
            result["sidecar_path"] = str(sidecar_path)
            result["ffprobe"] = probe_info
            sidecar_data = {
                **result,
                "prompt": prompt,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            sidecar_path.write_text(
                json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        return result

