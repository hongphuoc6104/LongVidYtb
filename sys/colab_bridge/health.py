"""Bounded account audit. Auth, server assignment and kernel health stay separate."""

from __future__ import annotations

import concurrent.futures
import fcntl
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from session_store import locked_json

from . import accounts
from .protocol import stamp


def kernel_health(binary: str | Path, name: str, session: str, timeout: int = 25,
                  *, identity: str | None = None, lock_dir: Path | None = None) -> dict[str, Any]:
    """Run only a device/readiness observation; never allocate, install or generate."""
    code = (
        "import json, subprocess, importlib.util\n"
        "gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True,timeout=5).strip()\n"
        "print('VP_HEALTH='+json.dumps({'gpu':gpu,'tts_installed':importlib.util.find_spec('omnivoice') is not None}),flush=True)\n"
    )
    if identity is not None:
        from contextlib import ExitStack
        base = Path(lock_dir or Path.home()/'.cache/video-pilot-colab')
        base.mkdir(parents=True, exist_ok=True, mode=0o700)
        with ExitStack() as held:
            try:
                for path in [base/('identity-'+stamp(identity)+'.lock'), base/(stamp([name, session])+'.lock')]:
                    handle = held.enter_context(path.open('a'))
                    fcntl.flock(handle, fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                return {'verified': False, 'reason': 'busy'}
            return kernel_health(binary, name, session, timeout)
    try:
        result = subprocess.run(
            accounts.command(binary, name, ["exec", "-s", session, "--timeout", "10"]),
            input=code,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        values = [line[10:] for line in result.stdout.splitlines() if line.startswith("VP_HEALTH=")]
        if result.returncode or not values:
            return {"verified": False, "reason": "kernel_unconfirmed"}
        value = json.loads(values[-1])
        return {"verified": True, "t4": "T4" in value["gpu"], "tts_installed": value["tts_installed"] is True}
    except subprocess.TimeoutExpired:
        return {"verified": False, "reason": "kernel_timeout"}
    except (OSError, ValueError, KeyError):
        return {"verified": False, "reason": "kernel_unconfirmed"}


def audit(
    *,
    session: str = "video-pilot-tts",
    refresh_auth: bool = False,
    check_kernels: bool = False,
    binary: str | Path | None = None,
    workers: int = 4,
    store: Path | None = None,
) -> dict[str, Any]:
    """Inspect accounts concurrently; refreshing existing credentials is explicit opt-in."""
    binary = binary or shutil.which("colab") or Path.home() / ".local/bin/colab"

    def inspect(item: dict[str, Any]) -> dict[str, Any]:
        name = item["id"]
        entry = {
            "id": name,
            "enabled": item.get("enabled", True),
            "role": item.get("role", "any"),
            "session": session,
            "session_busy": accounts.is_session_busy(name, session),
            "external_session": accounts.has_external_session(name),
        }
        observed = accounts.assignment_state(binary, name, session, timeout=30, refresh_auth=refresh_auth)
        entry["server_assignment"] = observed
        entry["state"] = observed.get("reason", "unknown")
        if observed.get("verified"):
            entry["state"] = "authenticated_idle" if observed["assignment_count"] == 0 else "assignment_unmapped"
            if observed.get("named_assignment_active"):
                entry["state"] = "active_kernel_not_tested"
                if check_kernels and not entry["session_busy"] and not entry["external_session"]:
                    kernel = kernel_health(binary, name, session, identity=observed.get('identity'))
                    entry["kernel"] = kernel
                    entry["state"] = (
                        ("t4_ready" if kernel.get("t4") else "non_t4") if kernel["verified"] else kernel["reason"]
                    )
        if entry["external_session"]:
            entry["state"] = "external_session_protected"
        elif entry["session_busy"]:
            entry["state"] = "busy"
        return entry

    entries = accounts.registry()["accounts"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 8))) as pool:
        rows = list(pool.map(inspect, entries))
    identities = {}
    for item in rows:
        observed = item["server_assignment"]
        identity = observed.get("identity")
        if observed.get("verified") and identity:
            if identity in identities:
                item["duplicate_of"] = identities[identity]["id"]
            else:
                identities[identity] = item
    assignments = {
        identity: max(
            x["server_assignment"].get("assignment_count", 0)
            for x in rows
            if x["server_assignment"].get("identity") == identity
        )
        for identity in identities
    }
    report = {
        "checked_at": time.time(),
        "session": session,
        "refresh_auth": refresh_auth,
        "accounts": rows,
        "total_accounts": len(rows),
        "verified_identities": len(identities),
        "authenticated_accounts": sum(x["server_assignment"].get("verified") is True for x in rows),
        "active_assignments": sum(assignments.values()),
        "unique_authenticated_idle": sum(assignments[identity] == 0 for identity in identities),
        "t4_ready": sum(x["state"] == "t4_ready" for x in rows),
        "authenticated_idle": sum(x["state"] == "authenticated_idle" for x in rows),
        "provider_gpu_capacity": "not_tested",
    }
    path = Path(store or Path.home() / ".config/video-pilot/management") / "colab-health.json"
    with locked_json(path, dict) as data:
        data.clear()
        data.update(report)
    return report
