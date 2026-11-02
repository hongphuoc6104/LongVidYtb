#!/usr/bin/env python3
"""CLI tool for managing Google Flow Applets and exporting VP Omni Chain Studio V2.

Supports:
  - `--export-v2-tsx <path>`: Exports complete App.tsx + creation prompt for VP Omni Chain Studio V2.
  - `--build-state-json`: Outputs structured VP_OMNI_STUDIO_V2_STATE JSON.
  - `--list-applets --profile <id>`: Lists personal, Google, and community applets via tRARke.
  - `--fork-applet <share_id> --profile <id>`: Forks a shared tool into the target profile via CSvxid.

All CDP operations guarantee strict teardown of opened Chrome instances.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sys.flow_cdp.accounts import registry
from sys.flow_cdp.applet_manager import (
    RPC_FORK_APPLET,
    RPC_LIST_APPLETS,
    build_fork_applet_request,
    build_list_applets_request,
    build_vp_omni_studio_v2_state,
    generate_vp_omni_studio_v2_tsx,
    parse_applets_list,
)
from sys.flow_cdp.cdp_direct_client import DirectCDPProfileSession
from sys.flow_cdp.process_manager import ProcessGroupManager

logger = logging.getLogger("manage_flow_applets")


def get_profile_cfg(profile_arg: str) -> dict[str, Any]:
    """Resolve profile configuration by id or port."""
    reg = registry()
    profiles = reg.get("profiles", [])
    target = profile_arg.strip()

    for p in profiles:
        if p.get("id") == target:
            return p
        if str(p.get("port")) == target:
            return p

    available = [f"{p.get('id')} (port {p.get('port')})" for p in profiles]
    raise ValueError(
        f"Profile '{profile_arg}' not found in browser-profiles.json. Available: {', '.join(available)}"
    )


async def cmd_list_applets(profile_id: str, as_json: bool = False) -> None:
    """Execute tRARke RPC on target profile and list all applets."""
    profile_cfg = get_profile_cfg(profile_id)
    port = int(profile_cfg.get("port", 9222))
    pm = ProcessGroupManager()
    session: Optional[DirectCDPProfileSession] = None

    print(f"[*] Launching headless Chrome on {profile_cfg.get('id')} (port {port})...")
    try:
        pm.launch(profile_cfg, headless=True)
        session = DirectCDPProfileSession(profile_cfg)
        await session.connect(reload_for_guard=False)

        print("[*] Calling RPC tRARke (List Applets)...")
        envelope = build_list_applets_request()
        res = await session._post_batchexecute(
            rpcid=RPC_LIST_APPLETS,
            freq=envelope,
            captcha_action=None,
            timeout=30.0,
        )

        applets = parse_applets_list(res.get("text", ""))

        if as_json:
            print(json.dumps(applets, indent=2, ensure_ascii=False))
            return

        user_tools = [a for a in applets if a["kind"] == "USER"]
        google_tools = [a for a in applets if a["kind"] == "GOOGLE"]
        community_tools = [a for a in applets if a["kind"] == "COMMUNITY"]

        print("\n=======================================================")
        print(f" Google Flow Applets ({len(applets)} Total)")
        print("=======================================================")

        if user_tools:
            print(f"\n[+] Personal / Owned Applets ({len(user_tools)}):")
            for u in user_tools:
                pin_mark = " [PINNED]" if u.get("is_pinned") else ""
                print(f"  • {u['name']} (ID: {u['applet_id']}){pin_mark}")
                if u.get("description"):
                    print(f"    Desc: {u['description']}")
                if u.get("share_id"):
                    print(f"    Share: https://flow.google.com/shared/tool/{u['share_id']}")

        if google_tools:
            print(f"\n[+] Google First-Party Tools ({len(google_tools)}):")
            for g in google_tools:
                print(f"  • {g['name']} (Runs: {g['run_count']}) — {g['description']}")
                if g.get("share_id"):
                    print(f"    Share: https://flow.google.com/shared/tool/{g['share_id']}")

        if community_tools:
            print(f"\n[+] Featured Community Tools ({len(community_tools)}):")
            for c in community_tools[:10]:
                auth = f" by {c['author']}" if c.get("author") else ""
                print(f"  • {c['name']}{auth} (Runs: {c['run_count']})")
                if c.get("description"):
                    print(f"    Desc: {c['description']}")

        print(f"\n[*] Listed {len(applets)} tools successfully.")

    finally:
        if session:
            try:
                await session.close()
            except Exception:
                pass
        pm.terminate_by_port(port)
        print(f"[*] Port {port} cleanly torn down.")


async def cmd_fork_applet(share_id: str, profile_id: str) -> None:
    """Execute CSvxid RPC on target profile to fork a shared tool."""
    profile_cfg = get_profile_cfg(profile_id)
    port = int(profile_cfg.get("port", 9222))
    pm = ProcessGroupManager()
    session: Optional[DirectCDPProfileSession] = None

    print(f"[*] Launching headless Chrome on {profile_cfg.get('id')} (port {port})...")
    try:
        pm.launch(profile_cfg, headless=True)
        session = DirectCDPProfileSession(profile_cfg)
        await session.connect(reload_for_guard=False)

        print(f"[*] Forking shared applet share_id={share_id} via CSvxid...")
        envelope = build_fork_applet_request(share_id)
        res = await session._post_batchexecute(
            rpcid=RPC_FORK_APPLET,
            freq=envelope,
            captcha_action=None,
            timeout=30.0,
        )

        print("[*] Fork RPC Response received:")
        raw_text = res.get("text", "")
        print(raw_text[:2000] if len(raw_text) > 2000 else raw_text)

    finally:
        if session:
            try:
                await session.close()
            except Exception:
                pass
        pm.terminate_by_port(port)
        print(f"[*] Port {port} cleanly torn down.")


def cmd_export_v2_tsx(output_path: Optional[str] = None) -> None:
    """Export complete App.tsx and companion creation prompt."""
    out_file = (
        Path(output_path).resolve()
        if output_path
        else REPO_ROOT / "sys" / "flow_cdp" / "applets" / "vp_omni_studio_v2" / "App.tsx"
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)

    tsx_code = generate_vp_omni_studio_v2_tsx()
    out_file.write_text(tsx_code, encoding="utf-8")
    print(f"[+] Wrote App.tsx to: {out_file} ({len(tsx_code):,} bytes)")

    # Companion Vibe-Coding Prompt
    prompt_file = out_file.parent / "CREATION_PROMPT.md"
    prompt_content = f"""# VP Omni Chain Studio V2 — Applet Prompt for Google Flow (/create-tool)

Copy and paste the prompt below into Google Flow's Applet Creator Agent:

---

```
Build a durable, high-performance web applet called "VP Omni Chain Studio V2".

Features:
1. Dual-Engine Switch:
   - Mode 1 (Hybrid Video Chain): High-density keyframes using Nano Banana 2.1 (0 credits) connected by Omni 1.1 Flash video generation with automatic duration selection (4s, 6s, 8s, 10s).
   - Mode 2 (Zero-Credit Flipbook): 100% Free 0-credit storyboard engine that generates all keyframes with Nano Banana 2.1, exports them to the Project Media Grid via Flow.save, and downloads a JSON storyboard manifest via Flow.download.
2. AI Script Splitter:
   - Uses Flow.generate.text (0 credits) to automatically decompose user narration scripts into visual 2D Doodle Feynman beats with estimated durations and minimal doodle prompts.
3. Reference Identity & Style Lock:
   - Uses Flow.media.select to lock stickman character and handdrawn style reference image media IDs.
4. Batch Keyframe Generator:
   - Uses Flow.generate.image with "🍌 Nano Banana 2.1" and 16:9 / 9:16 aspect ratio.
5. Atomic State Persistence:
   - Saves and restores state automatically using Flow.storage with key "VP_OMNI_STUDIO_V2_STATE".
```

---
*Generated by Video Pilot Flow CDP Suite ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})*
"""
    prompt_file.write_text(prompt_content, encoding="utf-8")
    print(f"[+] Wrote Creation Prompt to: {prompt_file}")


def cmd_build_state_json(spec_path: Optional[str] = None, output_path: Optional[str] = None) -> None:
    """Build VP_OMNI_STUDIO_V2_STATE JSON from spec file or defaults."""
    spec_data: dict[str, Any] = {}
    if spec_path:
        spec_file = Path(spec_path).resolve()
        if spec_file.exists():
            spec_data = json.loads(spec_file.read_text(encoding="utf-8"))
        else:
            print(f"[-] Spec file {spec_file} not found, using default state.")

    state = build_vp_omni_studio_v2_state(spec_data)
    json_str = json.dumps(state, indent=2, ensure_ascii=False)

    if output_path:
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json_str, encoding="utf-8")
        print(f"[+] Wrote state JSON to: {out_p}")
    else:
        print(json_str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Google Flow Applets & VP Omni Studio V2")
    parser.add_argument("--export-v2-tsx", nargs="?", const="", help="Export VP Omni Studio V2 App.tsx [path]")
    parser.add_argument("--build-state-json", action="store_true", help="Build VP_OMNI_STUDIO_V2_STATE JSON")
    parser.add_argument("--spec", help="Path to input spec JSON for --build-state-json")
    parser.add_argument("--output", help="Path to output file for state JSON")
    parser.add_argument("--list-applets", action="store_true", help="List Flow Applets on profile")
    parser.add_argument("--fork-applet", help="Fork shared applet share_id")
    parser.add_argument("--profile", default="profile_6", help="Target profile id or port (default: profile_6)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON for commands")

    args = parser.parse_args()

    if args.export_v2_tsx is not None:
        cmd_export_v2_tsx(args.export_v2_tsx or None)
        return

    if args.build_state_json:
        cmd_build_state_json(args.spec, args.output)
        return

    if args.list_applets:
        asyncio.run(cmd_list_applets(args.profile, as_json=args.json))
        return

    if args.fork_applet:
        asyncio.run(cmd_fork_applet(args.fork_applet, args.profile))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
