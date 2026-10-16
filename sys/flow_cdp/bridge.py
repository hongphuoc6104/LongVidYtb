"""Standardized Python bridge for Flow CDP (formerly B-2 Illustrator / CDP).

Provides direct communication over Unix domain socket / CDP, multi-profile
parallel patch dispatching (across 3 Chrome profiles), failover upon abnormal activity,
and clean result mapping without mandatory UI screenshot proofs.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import socket
import stat
import struct
import tempfile
import time
from pathlib import Path
from typing import Any

from pilot import Blocked, digest

from .multi_profile_manager import ChromeProfileWorker, MultiProfileDispatcher, MultiProfileManager
from .patch_partitioner import PatchPartitioner

logger = logging.getLogger("flow_cdp.bridge")

SYS_ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = Path(__file__).resolve().parent
ROOT = SYS_ROOT  # Backward compatibility with b2_bridge


def session_socket_path(root: Path = SYS_ROOT, profile_id: str = "") -> Path:
    suffix = os.environ.get("VP_SESSION_KEY", "") + (f"-{profile_id}" if profile_id else "")
    key = hashlib.sha256((str(Path(root).resolve()) + suffix).encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / ("video-pilot-" + str(os.getuid())) / ("flow-" + key + ".sock")


SOCKET_PATH = session_socket_path()


def get_socket_path(profile_id: str = "") -> Path:
    if profile_id:
        return session_socket_path(SYS_ROOT, profile_id)
    return SOCKET_PATH


def _config() -> dict[str, Any]:
    try:
        return json.loads((ROOT / "config.json").read_text())
    except Exception:
        return {}


def _mark_not_submitted(exc: Blocked) -> Blocked:
    """Tag a pre-submission failure so it is never treated as an ambiguous Flow submission."""
    if getattr(exc, "generation_submitted", None) is None:
        exc.generation_submitted = False
    return exc


def send_raw_command(command: str, timeout: float = 120.0, sock_path: Path | None = None) -> dict[str, Any]:
    target_sock = sock_path or get_socket_path()
    if not target_sock.exists():
        raise Blocked(
            f"Flow CDP session socket not found at {target_sock}. "
            "Ensure flow-cdp session service is running."
        )
    try:
        parent = target_sock.parent.lstat()
        endpoint = target_sock.lstat()
        if (stat.S_ISLNK(parent.st_mode) or not stat.S_ISDIR(parent.st_mode)
                or parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700
                or not stat.S_ISSOCK(endpoint.st_mode) or endpoint.st_uid != os.getuid()
                or stat.S_IMODE(endpoint.st_mode) != 0o600):
            raise _mark_not_submitted(Blocked("UNSAFE_FLOW_SOCKET: private owned directory and socket required"))
    except OSError as error:
        raise _mark_not_submitted(Blocked("UNSAFE_FLOW_SOCKET: endpoint ownership unavailable")) from error

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(str(target_sock))
        if hasattr(socket, "SO_PEERCRED"):
            _, peer_uid, _ = struct.unpack("3i", client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i")))
            if peer_uid != os.getuid():
                raise _mark_not_submitted(Blocked("UNSAFE_FLOW_SOCKET: peer user differs from runtime owner"))
        payload = (command.strip() + "\n").encode("utf-8")
        client.sendall(payload)

        response_chunks = []
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            response_chunks.append(chunk)
            if b"\n" in chunk:
                break

        response_text = b"".join(response_chunks).decode("utf-8").strip()
        if not response_text:
            raise _mark_not_submitted(Blocked("Empty response from Flow CDP session socket"))
        return json.loads(response_text)
    except socket.timeout:
        exc = Blocked(f"Flow CDP session command timed out after {timeout}s: {command[:50]}")
        if not command.startswith("tool-snapshot:queue:"):
            exc = _mark_not_submitted(exc)
        raise exc from exc
    except (json.JSONDecodeError, OSError) as exc:
        err = Blocked(f"Flow CDP session communication error: {exc}")
        if not command.startswith("tool-snapshot:queue:"):
            err = _mark_not_submitted(err)
        raise err from exc
    finally:
        client.close()


def query_status(timeout: float | None = None, sock_path: Path | None = None) -> dict[str, Any]:
    cfg = _config()
    timeout = timeout if timeout is not None else cfg.get("flow_status_timeout_seconds", 30.0)
    retries = cfg.get("flow_status_retries", 2)
    backoff = cfg.get("flow_status_backoff_seconds", 2.0)
    last_exc: Blocked | None = None
    for attempt in range(retries + 1):
        try:
            if sock_path is not None and sock_path != get_socket_path():
                return send_raw_command("status", timeout=timeout, sock_path=sock_path)
            return send_raw_command("status", timeout=timeout)
        except Blocked as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
    if last_exc:
        from .cdp_direct_client import PROFILES, is_port_open
        if any(is_port_open(p["cdp_port"]) for p in PROFILES):
            return {
                "status": "connected",
                "identity": {
                    "observedProfile": str(Path(PROFILES[0]["user_data_dir"]).expanduser() / PROFILES[0]["profile_dir"]),
                    "toolUrl": PROFILES[0]["url"],
                }
            }
        raise last_exc
    return {"status": "not_connected"}


def ensure_connected(sock_path: Path | None = None) -> dict[str, Any]:
    target_sock = sock_path if (sock_path is not None and sock_path != get_socket_path()) else None
    if is_session_available(target_sock):
        return query_status(sock_path=target_sock)
    from .cdp_direct_client import PROFILES, ensure_chrome_profiles_launched, is_port_open
    if any(is_port_open(p["cdp_port"]) for p in PROFILES):
        return {
            "status": "connected",
            "identity": {
                "observedProfile": str(Path(PROFILES[0]["user_data_dir"]).expanduser() / PROFILES[0]["profile_dir"]),
                "toolUrl": PROFILES[0]["url"],
            }
        }
    if target_sock is not None:
        result = send_raw_command("connect", timeout=75.0, sock_path=target_sock)
    else:
        try:
            result = send_raw_command("connect", timeout=75.0)
        except Exception:
            ensure_chrome_profiles_launched()
            return {
                "status": "connected",
                "identity": {
                    "observedProfile": str(Path(PROFILES[0]["user_data_dir"]).expanduser() / PROFILES[0]["profile_dir"]),
                    "toolUrl": PROFILES[0]["url"],
                }
            }
    if result.get("status") != "connected":
        raise Blocked(f"Flow CDP connection blocked: {result.get('reason', 'not connected')}")
    return result


def is_session_available(sock_path: Path | None = None) -> bool:
    target_sock = sock_path or get_socket_path()
    if not target_sock.exists():
        return False
    try:
        res = query_status(sock_path=target_sock)
        return res.get("status") == "connected"
    except Exception:
        return False


def require_queue_acceptance() -> None:
    acceptance_file = ROOT / "experiments/b2_illustrator/acceptance.json"
    if not acceptance_file.exists():
        acceptance_file = MODULE_ROOT / "acceptance.json"
    record = json.loads(acceptance_file.read_text()) if acceptance_file.exists() else {}
    config = _config()
    if record.get("production_ready") is not True and config.get("flow_queue_trial_enabled") is not True:
        raise Blocked("B2_QUEUE_NOT_ACCEPTED: Flow CDP queue not accepted for production")


def _execute_via_cdp_direct(specs: list[dict[str, Any]], timeout: float = 240.0, worker: Any = None) -> list[dict[str, Any]]:
    import asyncio
    import urllib.request

    from PIL import Image

    from .cdp_direct_client import PROFILES, DirectCDPProfileSession, ensure_chrome_profiles_launched, is_port_open

    worker_id = getattr(worker, "profile_id", "")
    worker_port = getattr(worker, "port", None)
    selected_cfg = None
    if worker_id or worker_port:
        selected_cfg = next((p for p in PROFILES if (worker_id and p["name"] == worker_id) or (worker_port and p["cdp_port"] == worker_port)), None)
    if not selected_cfg:
        for p in PROFILES:
            if is_port_open(p["cdp_port"]):
                selected_cfg = p
                break
    if not selected_cfg:
        selected_cfg = PROFILES[0]

    # Only launch the specifically assigned profile to avoid high RAM/CPU usage and lag
    ensure_chrome_profiles_launched([selected_cfg])

    async def _run():
        sess = DirectCDPProfileSession(selected_cfg)
        await sess.connect()
        await sess._wait_for_flow_ready(timeout=15.0)
        items = []
        try:
            for spec in specs:
                start_t = time.time()
                prompt = spec["prompt"]
                aspect = spec.get("ratio", "9:16")
                base_media_id = spec.get("baseMediaId")
                ref_media_ids = [spec["charMediaId"]] if spec.get("charMediaId") else None
                model = "BELUGA"

                res = await sess.generate_image(
                    prompt=prompt,
                    aspect=aspect,
                    model=model,
                    base_media_id=base_media_id,
                    ref_media_ids=ref_media_ids,
                )
                out_dir = Path(spec["outDir"]).resolve()
                out_dir.mkdir(parents=True, exist_ok=True)
                dest_img = out_dir / "result.jpg"

                req = urllib.request.Request(res["url"], headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                if len(data) < 5000:
                    raise RuntimeError(f"Downloaded image too small ({len(data)} bytes)")
                dest_img.write_bytes(data)
                with Image.open(dest_img) as im:
                    im.verify()

                latency = round(time.time() - start_t, 2)
                items.append({
                    "request_id": spec["testCase"],
                    "path": str(dest_img),
                    "forge_id": res["media_id"],
                    "latency": latency,
                    "sha256": digest(dest_img),
                })
        finally:
            if sess.ws is not None:
                await sess.ws.close()
        return items

    return asyncio.run(_run())


def _execute_sub_batch(specs: list[dict[str, Any]], timeout: float = 240.0, sock_path: Path | None = None, before_submit=None, worker: Any = None) -> list[dict[str, Any]]:
    """Submit 1 to 4 requests directly over CDP socket or direct CDP client."""
    target_sock = sock_path if (sock_path is not None and sock_path != get_socket_path()) else None
    try:
        require_queue_acceptance()
        connection = ensure_connected(sock_path=target_sock)
        if not 1 <= len(specs) <= 4:
            raise Blocked(f"Flow CDP queue requires 1 to 4 requests per batch, got {len(specs)}")

        for spec in specs:
            if spec.get("characterRefPath") and not spec.get("charMediaId"):
                raise Blocked("REFERENCE_MEDIA_ID_REQUIRED: characterRefPath thiếu charMediaId tương ứng")
            if spec.get("baseRefPath") and not spec.get("baseMediaId"):
                raise Blocked("REFERENCE_MEDIA_ID_REQUIRED: baseRefPath thiếu baseMediaId (thiếu sidecar .json chứa forgeId)")

        folder = SYS_ROOT / "experiments/b2_illustrator/results/controller"
        folder.mkdir(parents=True, exist_ok=True)
        import uuid
        manifest = folder / f"queue-{uuid.uuid4().hex}.json"
        manifest.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")

        if before_submit is not None:
            before_submit(connection)
    except Blocked as exc:
        _mark_not_submitted(exc)
        raise

    try:
        if target_sock is not None and target_sock.exists():
            result = send_raw_command(f"tool-snapshot:queue:{manifest}", timeout=max(timeout, 240), sock_path=target_sock)
        else:
            result = send_raw_command(f"tool-snapshot:queue:{manifest}", timeout=max(timeout, 240))
    except Blocked as exc:
        if "session socket not found" in str(exc).lower():
            return _execute_via_cdp_direct(specs, timeout=timeout, worker=worker)
        raise


    if result.get("status") == "blocked":
        error = Blocked(result.get("reason", "Flow CDP queue blocked"))
        error.generation_submitted = result.get("generationSubmitted", True)
        error.collection_only = result.get("collectionOnly", False)
        error.attempt_states = result.get("attemptStates", [])
        raise error

    items = result.get("items", [])
    if len(items) != len(specs):
        raise Blocked("Flow CDP incomplete batch; reconcile before retry")

    for spec, item in zip(specs, items, strict=False):
        if item.get("request_id") != spec["testCase"] or not Path(item["path"]).is_file():
            raise Blocked("Flow CDP result mapping failed")
        item["sha256"] = digest(Path(item["path"]))
    return items


def generate_cdp_image(
    prompt: str,
    ratio: str = "16:9",
    base_ref_path: str | Path | None = None,
    char_ref_path: str | Path | None = None,
    base_media_id: str | None = None,
    char_media_id: str | None = None,
    preserve: str = "",
    change: str = "",
    literal_text: str = "",
    out_dir: str | Path | None = None,
    test_case: str = "SCENE",
    timeout: float = 120.0,
    collection_only: bool = False,
    before_submit=None,
    model=None,
    project=None,
    tool_url=None,
    use_character_ref: bool = True,
    profile_id: str = "",
) -> dict[str, Any]:
    """Generate a single image via Flow CDP."""
    try:
        require_queue_acceptance()
        if profile_id:
            ensure_connected(sock_path=get_socket_path(profile_id))
        else:
            ensure_connected()
    except Blocked as exc:
        _mark_not_submitted(exc)
        raise

    canonical_mascot = (SYS_ROOT / "assets/characters/channel-mascot/reference-v1.png").resolve()
    if use_character_ref and char_ref_path is None and canonical_mascot.exists():
        char_ref_path = canonical_mascot
        char_media_id = char_media_id or "de94a39b-155f-4afe-acbb-d9d4b59ad532"

    target_dir = Path(out_dir).resolve() if out_dir else (SYS_ROOT / "experiments/b2_illustrator/results/controller").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    spec = {
        "testCase": test_case,
        "testName": f"Pipeline CDP Generation: {test_case}",
        "prompt": prompt,
        "collectionOnly": collection_only,
        "preserve": preserve,
        "change": change,
        "literalText": literal_text,
        "ratio": ratio,
        "outDir": str(target_dir),
        "baseRefPath": str(Path(base_ref_path).resolve()) if base_ref_path else None,
        "characterRefPath": str(Path(char_ref_path).resolve()) if char_ref_path else None,
        "baseMediaId": base_media_id,
        "charMediaId": char_media_id,
    }
    if not use_character_ref and char_ref_path is None:
        spec["useCharacterRef"] = False
    if model is not None:
        spec.update(model=model, project=project, toolUrl=tool_url, managementContract=1)

    spec_file = target_dir / f".spec-{test_case}-{int(time.time() * 1000)}.json"
    spec_file.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    return generate_cdp_batch([spec], timeout=timeout, before_submit=before_submit, profile_id=profile_id)[0]


def generate_cdp_batch(
    specs: list[dict[str, Any]],
    timeout: float = 240.0,
    before_submit=None,
    profile_id: str = "",
    use_multi_profile: bool = True,
) -> list[dict[str, Any]]:
    """Submit batch through Flow CDP with automatic patch partitioning and multi-profile failover."""
    cfg = _config()
    patch_size = cfg.get("patch_size", 3)
    profiles_cfg = cfg.get("flow_cdp_profiles", None)

    # If small batch (1-4) and single profile specified, or socket is already active for this single profile
    if len(specs) <= 4 and (not use_multi_profile or not profiles_cfg or len(profiles_cfg) <= 1):
        sock = get_socket_path(profile_id)
        return _execute_sub_batch(specs, timeout=timeout, sock_path=sock, before_submit=before_submit)

    # Multi-patch & multi-profile parallel execution
    partitioner = PatchPartitioner(target_size=patch_size, min_size=2, max_size=4)
    patches = partitioner.partition(specs)

    job_id = None
    if specs and isinstance(specs[0], dict):
        job_id = specs[0].get("job_id") or specs[0].get("jobId") or specs[0].get("testCase")

    if profiles_cfg and job_id:
        try:
            from execution import is_job, settings

            from pilot import Pilot
            p_obj = Pilot()
            if is_job(p_obj, job_id):
                binding = settings(p_obj, job_id).get("management_session", {}).get("runtime_bindings", {}).get("flow", {})
                target_path = binding.get("target", {}).get("profile_path")
                if target_path:
                    target_resolved = Path(target_path).resolve()
                    matched = [
                        prof for prof in profiles_cfg
                        if (Path(prof.get("user_data_dir", "")).expanduser() / prof.get("directory", "")).resolve() == target_resolved
                    ]
                    if matched:
                        profiles_cfg = matched
        except Exception:
            pass

    workers_needed = max(1, min(len(patches), len(profiles_cfg))) if patches else 1
    manager = MultiProfileManager(profiles_config=profiles_cfg, job_id=job_id, max_workers_per_job=workers_needed)
    try:
        dispatcher = MultiProfileDispatcher(profile_manager=manager)

        def worker_executor(worker: ChromeProfileWorker, patch_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
            sock = get_socket_path(worker.profile_id)
            # If per-worker socket doesn't exist, fall back to default socket
            if not sock.exists() and get_socket_path().exists():
                sock = get_socket_path()
            return _execute_sub_batch(patch_items, timeout=timeout, sock_path=sock, before_submit=before_submit, worker=worker)

        return dispatcher.dispatch_all(patches, worker_executor, max_concurrency=max(1, len(manager.workers)))
    finally:
        manager.close()


# Backward compatibility aliases for B-2 Illustrator
generate_b2_image = generate_cdp_image
generate_b2_batch = generate_cdp_batch
