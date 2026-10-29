"""Durable management selections and request pinning, with process-safe writes."""

import fcntl
import json
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def locked_json(path, default):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.with_suffix(".lock").open("a") as lock:
        os.chmod(lock.name, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        value = json.loads(path.read_text()) if path.exists() else default()
        yield value
        tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(path)


class Sessions:
    def __init__(self, system_root):
        self.path = Path(system_root) / ".state/management-session.json"

    def read(self):
        return (
            json.loads(self.path.read_text())
            if self.path.exists()
            else {
                "version": 1,
                "session_id": None,
                "pool": [],
                "defaults": {},
                "pins": {},
                "selection": "specified",
                "preset": "remote-t4",
            }
        )

    def select(self, pool, defaults, *, selection="specified", preset="remote-t4", known=None):
        if selection not in ("specified", "auto") or preset != "remote-t4":
            raise ValueError("Supported selection/preset required")
        if not isinstance(pool, list) or any(not isinstance(x, str) for x in pool) or len(pool) != len(set(pool)):
            raise ValueError("Unique account IDs required")
        if (
            not isinstance(defaults, dict)
            or set(defaults) - {"colab", "flow"}
            or any(x not in pool for x in defaults.values())
        ):
            raise ValueError("Defaults must belong to selected pool")
        if known is not None:
            by_id = {x["id"]: x for x in known}
            if any(x not in by_id for x in pool) or any(
                by_id[x]["service"] != service for service, x in defaults.items()
            ):
                raise ValueError("Unknown account or wrong service")
        with locked_json(self.path, self.read) as state:
            state.setdefault("session_id", None)
            if state["session_id"] is None:
                state["session_id"] = uuid.uuid4().hex
            state.update(pool=pool, defaults=defaults, selection=selection, preset=preset, updated_at=time.time())
            if selection == "auto":
                previous = state.get("runtime_bindings", {}).pop("colab", None)
                if previous:
                    state.setdefault("runtime_binding_history", []).append(
                        {"job": None, "binding": previous, "reason": "automatic_pool_selection", "at": time.time()}
                    )
        return self.read()

    def snapshot(self, job=None):
        state = self.read()
        snapshot = {key: state.get(key) for key in ("version", "session_id", "pool", "defaults", "selection", "preset")}
        snapshot["runtime_bindings"] = {
            **state.get("runtime_bindings", {}),
            **state.get("job_runtime_bindings", {}).get(job, {}),
        }
        return snapshot

    def pin(self, request, *, job, service, account, session, identity=None):
        if not all(isinstance(x, str) and x for x in (request, job, service, account, session)) or service not in (
            "colab",
            "flow",
        ):
            raise ValueError("Exact request ownership required")
        record = {"job": job, "service": service, "account": account, "session": session, "identity": identity}
        with locked_json(self.path, self.read) as state:
            existing = state.setdefault("pins", {}).get(request)
            if existing and existing != record:
                raise ValueError("Pinned request ownership cannot be changed")
            state["pins"][request] = record
        return record

    def unpin(self, request):
        with locked_json(self.path, self.read) as state:
            state.setdefault("pins", {}).pop(request, None)
