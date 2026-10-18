"""Cross-process runtime claims with durable ownership for uncertain requests."""

from __future__ import annotations

import fcntl
import json
import os
import time
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Iterator

from account_budget import Budgets

from .protocol import stamp

PENDING = {"submitted", "ambiguous"}


class PoolUnavailable(RuntimeError):
    """No safe runtime could be claimed before the queue deadline."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except FileNotFoundError:
        return {}


class RuntimeScheduler:
    def __init__(self, root: Path, *, store: Path | None = None, lock_dir: Path | None = None):
        self.root = Path(root)
        self.store = Path(store or Path.home() / ".config/video-pilot/management")
        self.directory = self.store / "colab-dispatch"
        self.locks = Path(lock_dir or Path.home() / ".cache/video-pilot-colab")

    def identity(self, account: str) -> str:
        mapped = Budgets(self.store).read()["aliases"].get("colab:" + account)
        health = read_json(self.store / "colab-health.json")
        item = next((x for x in health.get("accounts", []) if x["id"] == account), {})
        observed = item.get("server_assignment", {})
        if observed.get("verified") and observed.get("identity"):
            if mapped and mapped != observed["identity"]:
                raise PoolUnavailable("COLAB_IDENTITY_MISMATCH: verified account differs from the saved budget owner")
            return observed["identity"]
        return mapped or "account:" + account

    def allocation_turn(self, minimum_interval: float = 3.0) -> None:
        """Stagger allocation starts across independent controllers and accounts."""
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (self.directory / "allocation.lock").open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            path = self.directory / "allocation-start.json"
            previous = read_json(path).get("started_at", 0)
            delay = max(0, minimum_interval - (time.time() - previous))
            if delay:
                time.sleep(delay)
            self._write(path, {"started_at": time.time()})

    def pending(self, account: str, request: str, journal: Path) -> list[Path]:
        """Import old journals too; an exited runner never frees an unknown remote send."""
        identity = self.identity(account)
        paths = set((self.root / "runs").glob("*/cache/colab-*/*/state.json"))
        for record in self.directory.glob("*.json"):
            saved = read_json(record)
            if saved.get("journal"):
                if (
                    saved.get("phase") in PENDING
                    and self.identity(saved["account"]) == identity
                    and (saved.get("request_id") != request or Path(saved['journal']).resolve() != journal.resolve())
                    and not Path(saved["journal"]).is_file()
                ):
                    blocked_path = Path(saved["journal"])
                    return [blocked_path]  # Missing evidence never proves remote termination.
                paths.add(Path(saved["journal"]))
        blocked = []
        for path in paths:
            state = read_json(path)
            owner = state.get("account")
            if (
                state.get("phase") in PENDING
                and owner
                and self.identity(owner) == identity
                and (state.get("request_id") != request or path.resolve() != journal.resolve())
            ):
                blocked.append(path)
        return blocked

    def _eligible(self, account: str, *, exact: bool) -> bool:
        if exact:
            return True  # Collection of the pinned request remains possible during a service block.
        snapshot = Budgets(self.store).snapshot("colab:" + account)
        if (
            snapshot["uncertain"]
            or snapshot["blocks"].get("colab")
            or snapshot["available_seconds"] <= 0
            or snapshot["needs_service_recheck"]
        ):
            return False
        health = read_json(self.store / "colab-health.json")
        if time.time() - health.get("checked_at", 0) < 300:
            item = next((x for x in health.get("accounts", []) if x["id"] == account), None)
            if item and item["state"] not in {"authenticated_idle", "t4_ready", "active_kernel_not_tested"}:
                return False
            if item and item["state"] == "authenticated_idle" and snapshot["allocated_sessions"]:
                return False  # Reconcile a stale allocation journal before starting another runtime.
        return True

    @contextmanager
    def claim(
        self, candidates: list[str], *, session: str, request: str, journal: Path, exact: bool, wait_seconds: float = 15
    ) -> Iterator[str]:
        """Select and lock together; no gap exists between choosing and reserving an account."""
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.locks.mkdir(parents=True, exist_ok=True, mode=0o700)
        deadline = time.monotonic() + max(0, wait_seconds)
        while True:
            for account in candidates:
                if not self._eligible(account, exact=exact):
                    continue
                key = stamp(self.identity(account))
                with ExitStack() as held:
                    try:
                        for path in [
                            self.locks / ("identity-" + key + ".lock"),
                            self.locks / (stamp([account, session]) + ".lock"),
                        ]:
                            handle = held.enter_context(path.open("a"))
                            os.chmod(path, 0o600)
                            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        continue
                    if self.pending(account, request, journal):
                        continue
                    record = self.directory / (key + ".json")
                    value = {
                        "account": account,
                        "session": session,
                        "request_id": request,
                        "journal": str(journal.resolve()),
                        "pid": os.getpid(),
                        "phase": "claimed",
                        "updated_at": time.time(),
                    }
                    self._write(record, value)
                    try:
                        yield account
                    finally:
                        state = read_json(journal)
                        self._write(
                            record,
                            {
                                **value,
                                "pid": None,
                                "updated_at": time.time(),
                                "phase": state.get("phase", "not_submitted"),
                            },
                        )
                    return
            if time.monotonic() >= deadline:
                raise PoolUnavailable(
                    "COLAB_POOL_WAIT: selected runtimes are busy, unhealthy or own pending requests; reconcile before retry"
                )
            time.sleep(min(0.2, max(0, deadline - time.monotonic())))

    @staticmethod
    def _write(path: Path, value: dict[str, Any]) -> None:
        tmp = path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(json.dumps(value, indent=2) + "\n")
        tmp.replace(path)
