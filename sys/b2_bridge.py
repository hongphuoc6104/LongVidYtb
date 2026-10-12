"""Backward compatibility bridge for B-2 Illustrator delegating to flow_cdp."""
import time
from pathlib import Path
from typing import Any

import flow_cdp.bridge as _cdp

ROOT = _cdp.ROOT
SOCKET_PATH = _cdp.SOCKET_PATH
session_socket_path = _cdp.session_socket_path
get_socket_path = _cdp.get_socket_path
is_session_available = _cdp.is_session_available
_mark_not_submitted = _cdp._mark_not_submitted
_config = _cdp._config
Blocked = _cdp.Blocked
digest = _cdp.digest

_real_send_raw_command = _cdp.send_raw_command
_real_require_queue_acceptance = _cdp.require_queue_acceptance
_real_query_status = _cdp.query_status
_real_ensure_connected = _cdp.ensure_connected


def send_raw_command(command: str, timeout: float = 120.0, **kwargs) -> dict[str, Any]:
    if kwargs.get("sock_path") is not None and kwargs["sock_path"] != get_socket_path():
        return _real_send_raw_command(command, timeout=timeout, sock_path=kwargs["sock_path"])
    return _real_send_raw_command(command, timeout=timeout)


def require_queue_acceptance():
    _cdp.ROOT = ROOT
    return _real_require_queue_acceptance()


def query_status(timeout: float | None = None, sock_path: Path | None = None) -> dict[str, Any]:
    _cdp.ROOT = ROOT
    cfg = _config()
    timeout = timeout if timeout is not None else cfg.get("flow_status_timeout_seconds", 30.0)
    retries = cfg.get("flow_status_retries", 2)
    backoff = cfg.get("flow_status_backoff_seconds", 2.0)
    last_exc: Blocked | None = None
    for attempt in range(retries + 1):
        try:
            return send_raw_command("status", timeout=timeout)
        except Blocked as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
    if last_exc:
        raise last_exc
    return {"status": "not_connected"}


def ensure_connected(sock_path: Path | None = None) -> dict[str, Any]:
    _cdp.ROOT = ROOT
    status = query_status(sock_path=sock_path)
    if status.get("status") == "connected":
        return status
    result = send_raw_command("connect", timeout=75.0)
    if result.get("status") != "connected":
        raise Blocked(f"Flow connection blocked: {result.get('reason', 'not connected')}")
    return result


def generate_b2_image(*args, **kwargs) -> dict[str, Any]:
    _cdp.ROOT = ROOT
    orig_send = _cdp.send_raw_command
    orig_conn = _cdp.ensure_connected
    orig_status = _cdp.query_status
    orig_accept = _cdp.require_queue_acceptance
    _cdp.send_raw_command = send_raw_command
    _cdp.ensure_connected = ensure_connected
    _cdp.query_status = query_status
    _cdp.require_queue_acceptance = require_queue_acceptance
    try:
        return _cdp.generate_cdp_image(*args, **kwargs)
    finally:
        _cdp.send_raw_command = orig_send
        _cdp.ensure_connected = orig_conn
        _cdp.query_status = orig_status
        _cdp.require_queue_acceptance = orig_accept


def generate_b2_batch(*args, **kwargs) -> list[dict[str, Any]]:
    _cdp.ROOT = ROOT
    orig_send = _cdp.send_raw_command
    orig_conn = _cdp.ensure_connected
    orig_status = _cdp.query_status
    orig_accept = _cdp.require_queue_acceptance
    _cdp.send_raw_command = send_raw_command
    _cdp.ensure_connected = ensure_connected
    _cdp.query_status = query_status
    _cdp.require_queue_acceptance = require_queue_acceptance
    try:
        return _cdp.generate_cdp_batch(*args, **kwargs)
    finally:
        _cdp.send_raw_command = orig_send
        _cdp.ensure_connected = orig_conn
        _cdp.query_status = orig_status
        _cdp.require_queue_acceptance = orig_accept


generate_cdp_image = generate_b2_image
generate_cdp_batch = generate_b2_batch
