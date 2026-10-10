#!/usr/bin/env python3
"""Flow Kit Backend Manager for Video Pilot project.

Commands:
    python3 run.py start    - Start Flow Kit backend as a daemon process
    python3 run.py stop     - Stop Flow Kit backend cleanly
    python3 run.py restart  - Restart Flow Kit backend
    python3 run.py status   - Check health, listening ports and extension status
    python3 run.py logs     - View recent logs
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

os.environ["no_proxy"] = "127.0.0.1,localhost"
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

DIR = Path(__file__).resolve().parent
REPO = DIR / "repo"
VENV_PYTHON = DIR / ".venv" / "bin" / "python"
RUNTIME = DIR / "runtime"
LOGS = DIR / "logs"
PID_FILE = RUNTIME / "flowkit.pid"
LOG_FILE = LOGS / "flowkit.log"
CONFIG_FILE = DIR / "config.json"


def load_config() -> dict:
    if CONFIG_FILE.is_file():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "api_host": "127.0.0.1",
        "api_port": 8100,
        "ws_host": "127.0.0.1",
        "ws_port": 9222,
        "flow_project_id": "",
        "media_provider": "flow",
        "default_provider": "flow",
        "flow_allow_degraded": "0",
    }


def is_port_listening(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def get_pid() -> int | None:
    if PID_FILE.is_file():
        try:
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            # Check if process is still alive
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError):
            PID_FILE.unlink(missing_ok=True)
    try:
        res = subprocess.run(
            ["pgrep", "-f", "agent.main"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.returncode == 0 and res.stdout.strip():
            first_pid = int(res.stdout.strip().splitlines()[0])
            os.kill(first_pid, 0)
            return first_pid
    except Exception:
        pass
    return None


def fetch_json(url: str, timeout: float = 2.0) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FlowKit-Manager/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def start_backend():
    cfg = load_config()
    host = cfg.get("api_host", "127.0.0.1")
    port = int(cfg.get("api_port", 8100))
    ws_port = int(cfg.get("ws_port", 9222))

    existing_pid = get_pid()
    if existing_pid:
        print(f"Flow Kit backend is already running (PID: {existing_pid}).")
        status_backend()
        return 0

    if is_port_listening(host, port) or is_port_listening(host, ws_port):
        print(f"ERROR: Port {port} or {ws_port} is already in use by another process.")
        return 1

    RUNTIME.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.update(
        FLOW_AGENT_DIR=str(RUNTIME),
        API_HOST=host,
        API_PORT=str(port),
        WS_HOST=cfg.get("ws_host", "127.0.0.1"),
        WS_PORT=str(ws_port),
        FLOW_PROJECT_ID=cfg.get("flow_project_id", ""),
        MEDIA_PROVIDER=cfg.get("media_provider", "flow"),
        DEFAULT_PROVIDER=cfg.get("default_provider", "flow"),
        FLOW_ALLOW_DEGRADED=cfg.get("flow_allow_degraded", "0"),
    )

    log_fd = open(LOG_FILE, "a", encoding="utf-8")
    proc = subprocess.Popen(
        [str(VENV_PYTHON), "-m", "agent.main"],
        cwd=REPO,
        env=env,
        stdout=log_fd,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    print(f"Starting Flow Kit backend (PID: {proc.pid})...")

    # Wait for server to become healthy
    deadline = time.time() + 10.0
    healthy = False
    while time.time() < deadline:
        if proc.poll() is not None:
            print(f"ERROR: Process exited prematurely with code {proc.returncode}.")
            PID_FILE.unlink(missing_ok=True)
            return 1
        data = fetch_json(f"http://{host}:{port}/health", timeout=1.0)
        if data and data.get("status") == "ok":
            healthy = True
            break
        time.sleep(0.5)

    if healthy:
        print(f"Flow Kit backend is UP and HEALTHY at http://{host}:{port}")
        print(f"WebSocket listening at ws://{host}:{ws_port}")
        print(f"Extension directory: {DIR / 'extension'}")
        return 0
    else:
        print(f"WARNING: Server did not respond with healthy status within 10s. Check {LOG_FILE}.")
        return 1


def stop_backend():
    pid = get_pid()
    if not pid:
        print("Flow Kit backend is not running.")
        PID_FILE.unlink(missing_ok=True)
        return 0

    print(f"Stopping Flow Kit backend (PID: {pid})...")
    try:
        # SIGINT allows graceful shutdown of Uvicorn and WebSocket servers
        os.kill(pid, signal.SIGINT)
        deadline = time.time() + 6.0
        while time.time() < deadline:
            time.sleep(0.5)
            try:
                os.kill(pid, 0)
            except OSError:
                break
        else:
            print("Process did not exit after SIGINT, sending SIGTERM...")
            os.kill(pid, signal.SIGTERM)
            time.sleep(2.0)
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    except OSError as err:
        print(f"Notice during shutdown: {err}")

    PID_FILE.unlink(missing_ok=True)
    cfg = load_config()
    host = cfg.get("api_host", "127.0.0.1")
    port = int(cfg.get("api_port", 8100))
    ws_port = int(cfg.get("ws_port", 9222))
    time.sleep(0.5)
    print(f"Stopped. Ports {port} and {ws_port} free: {not is_port_listening(host, port) and not is_port_listening(host, ws_port)}")
    return 0


def status_backend():
    cfg = load_config()
    host = cfg.get("api_host", "127.0.0.1")
    port = int(cfg.get("api_port", 8100))
    ws_port = int(cfg.get("ws_port", 9222))

    pid = get_pid()
    port_8100 = is_port_listening(host, port)
    port_9222 = is_port_listening(host, ws_port)

    health_data = fetch_json(f"http://{host}:{port}/health")
    flow_status = fetch_json(f"http://{host}:{port}/api/flow/status")
    prov_status = fetch_json(f"http://{host}:{port}/api/providers/status")

    print("=========================================")
    print("  Flow Kit Backend — Status")
    print("=========================================")
    print(f"Process PID:        {pid or 'NOT RUNNING'}")
    print(f"HTTP Port ({port}):   {'LISTENING' if port_8100 else 'CLOSED'}")
    print(f"WS Port   ({ws_port}):   {'LISTENING' if port_9222 else 'CLOSED'}")
    print(f"Base URL:           http://{host}:{port}")
    print(f"Extension Folder:   {DIR / 'extension'}")
    print("-----------------------------------------")

    if health_data:
        print(f"API Health:         {health_data.get('status', 'unknown')}")
        print(f"Flowkit Version:    {health_data.get('version', 'unknown')}")
        ext_conn = health_data.get("extension_connected", False)
        print(f"Extension Status:   {'CONNECTED' if ext_conn else 'NOT CONNECTED (Waiting for Chrome extension)'}")
    else:
        print("API Health:         UNREACHABLE")

    if flow_status:
        print(f"Flow Project ID:    {flow_status.get('flow_project_id') or '(None / Not configured)'}")
        print(f"Transport:          {flow_status.get('transport', 'batch')}")

    if prov_status:
        providers = [p.get('name') for p in prov_status.get('providers', []) if p.get('available')]
        print(f"Available Providers: {', '.join(providers) if providers else 'None'}")
    print("=========================================")
    return 0 if (pid and health_data) else 1


def show_logs(lines: int = 50):
    if not LOG_FILE.is_file():
        print(f"No log file found at {LOG_FILE}")
        return 0
    content = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = content[-lines:] if len(content) > lines else content
    print(f"--- Last {len(tail)} lines of {LOG_FILE} ---")
    print("\n".join(tail))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Flow Kit Backend Manager")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "logs"], help="Command to execute")
    parser.add_argument("-n", "--lines", type=int, default=50, help="Number of log lines to show")
    args = parser.parse_args()

    if args.command == "start":
        sys.exit(start_backend())
    elif args.command == "stop":
        sys.exit(stop_backend())
    elif args.command == "restart":
        stop_backend()
        time.sleep(1)
        sys.exit(start_backend())
    elif args.command == "status":
        sys.exit(status_backend())
    elif args.command == "logs":
        sys.exit(show_logs(args.lines))


if __name__ == "__main__":
    main()
