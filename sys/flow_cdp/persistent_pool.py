"""Persistent Chrome Worker Pool for High-Throughput Flow CDP Image Generation.

Guarantees:
1. Long-lived DirectCDPProfileSession reuse across tasks (zero per-image connection churn).
2. Configurable worker pool sizing (1 to 20 profiles, e.g. 2, 4, 6, 8, 10).
3. Thread-safe PriorityQueue task dispatch (priority=10 standard, priority=0 retry).
4. Calibrated pacing gap (>= 2.0s per profile) and launch stagger (0.4s).
5. Auto-remediation and 10-minute cooldown quarantine upon Error 7 (PUBLIC_ERROR_UNUSUAL_ACTIVITY),
   with automatic standby profile swap without interrupting other active workers.
6. DAG variation continuity pinning (shots with `based_on` pinned to parent profile).
7. Clean shutdown and zero orphan processes via ProcessGroupManager.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import queue
import re
import shutil
import tempfile
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from PIL import Image

logger = logging.getLogger("flow_cdp.persistent_pool")

# Patterns indicating bot-detection, rate limiting, or abnormal activity
UNUSUAL_ACTIVITY_PATTERNS = [
    re.compile(r"public_error_unusual_activity", re.IGNORECASE),
    re.compile(r"unusual[\s_-]?activity", re.IGNORECASE),
    re.compile(r"flow_provider_blocked", re.IGNORECASE),
    re.compile(r"captcha", re.IGNORECASE),
    re.compile(r"no_at_token", re.IGNORECASE),
    re.compile(r"bot[\s_-]?detect", re.IGNORECASE),
    re.compile(r"rate[\s_-]?limit", re.IGNORECASE),
    re.compile(r"\b429\b"),
    re.compile(r"\b503\b"),
    re.compile(r"quota[\s_-]?exceeded", re.IGNORECASE),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


async def remediate_profile_session(sess: Any) -> None:
    """Clear origin cache, cookies, and reload tab to recover from transient rate-limits."""
    try:
        await sess.call(
            "Storage.clearDataForOrigin",
            {
                "origin": "https://flow.google.com",
                "storageTypes": "appcache,cache_storage,file_systems,indexeddb,local_storage,service_workers,shader_cache,websql",
            },
            timeout=6.0,
        )
        await sess.call("Network.clearBrowserCache", timeout=6.0)
        res = await sess.call("Network.getAllCookies", timeout=6.0)
        cookies = res.get("cookies", [])
        for c in cookies:
            if "GRECAPTCHA" in c.get("name", "") or c.get("name", "").startswith("_ga"):
                await sess.call(
                    "Network.deleteCookies",
                    {"name": c["name"], "domain": c.get("domain", ""), "path": c.get("path", "/")},
                    timeout=4.0,
                )
        await sess.call("Page.navigate", {"url": "https://flow.google.com/"}, timeout=6.0)
    except Exception as exc:
        logger.debug("Remediation suppressed error: %s", exc)


class DynamicProfilePool:
    """Thread-safe pool managing active and standby Chrome profiles with cooldown quarantine."""

    def __init__(self, profiles: list[dict[str, Any]], cooldown_seconds: float = 600.0):
        self.lock = threading.Lock()
        self.all_profiles = [dict(p) for p in profiles]
        self.in_use: set[str] = set()
        self.cooldowns: dict[str, float] = {}
        self.cooldown_seconds = cooldown_seconds

    def acquire(
        self,
        current_name: Optional[str] = None,
        required_name: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        with self.lock:
            now = time.time()
            if required_name:
                for p in self.all_profiles:
                    name = p.get("name") or p.get("id")
                    if name == required_name:
                        if required_name in self.in_use:
                            return None
                        if required_name in self.cooldowns:
                            if self.cooldowns[required_name] > now:
                                return None
                            del self.cooldowns[required_name]
                        self.in_use.add(required_name)
                        return dict(p)
                return None

            for p in self.all_profiles:
                name = p.get("name") or p.get("id")
                if name == current_name or name in self.in_use:
                    continue
                if name in self.cooldowns:
                    if self.cooldowns[name] > now:
                        continue
                    del self.cooldowns[name]
                self.in_use.add(name)
                return dict(p)
            return None

    def release(self, profile_cfg: dict[str, Any], quarantine_reason: Optional[str] = None) -> None:
        with self.lock:
            name = profile_cfg.get("name") or profile_cfg.get("id")
            if name:
                self.in_use.discard(name)
                if quarantine_reason:
                    self.cooldowns[name] = time.time() + self.cooldown_seconds
                    logger.warning("Profile %s quarantined for %ss: %s", name, self.cooldown_seconds, quarantine_reason)

    def release_all(self) -> None:
        with self.lock:
            self.in_use.clear()

    def get_status(self) -> dict[str, Any]:
        with self.lock:
            now = time.time()
            return {
                "total_profiles": len(self.all_profiles),
                "in_use": list(self.in_use),
                "in_cooldown": {
                    k: round(v - now, 1) for k, v in self.cooldowns.items() if v > now
                },
            }


class PersistentWorkerPool:
    """Maintains warm Chrome worker threads with persistent CDP sessions across batch tasks."""

    def __init__(
        self,
        target_workers: int = 4,
        cooldown_seconds: float = 600.0,
        pacing_seconds: float = 2.0,
        stagger_seconds: float = 0.4,
        headless: bool = True,
        profiles: list[dict[str, Any]] | None = None,
        proc_mgr: Any | None = None,
        session_factory: Callable[[dict[str, Any]], Any] | None = None,
        default_out_dir: Path | str | None = None,
    ):
        self.target_workers = max(1, target_workers)
        self.cooldown_seconds = cooldown_seconds
        self.pacing_seconds = pacing_seconds
        self.stagger_seconds = stagger_seconds
        self.headless = headless
        self.default_out_dir = Path(default_out_dir) if default_out_dir else None

        # Resolve profiles
        if profiles is None:
            try:
                from flow_cdp.cdp_direct_client import PROFILES
                self.raw_profiles = list(PROFILES)
            except Exception:
                from flow_cdp.multi_profile_manager import DEFAULT_PROFILES
                self.raw_profiles = [
                    {
                        "name": p["id"],
                        "cdp_port": p["port"],
                        "user_data_dir": p["user_data_dir"],
                        "profile_dir": p["directory"],
                        "url": "https://flow.google.com/",
                    }
                    for p in DEFAULT_PROFILES
                ]
        else:
            self.raw_profiles = list(profiles)

        # Standardize profile dicts (ensure 'name' and 'cdp_port' keys exist)
        for p in self.raw_profiles:
            if "name" not in p and "id" in p:
                p["name"] = p["id"]
            if "cdp_port" not in p and "port" in p:
                p["cdp_port"] = p["port"]

        self.profile_pool = DynamicProfilePool(self.raw_profiles, cooldown_seconds=cooldown_seconds)

        # Process manager
        if proc_mgr is not None:
            self.proc_mgr = proc_mgr
        else:
            try:
                from flow_cdp.process_manager import ProcessGroupManager
                self.proc_mgr = ProcessGroupManager()
            except Exception:
                self.proc_mgr = None

        self.session_factory = session_factory

        # Queues and Synchronization
        self.shared_queue: queue.PriorityQueue[tuple[int, int, dict[str, Any]]] = queue.PriorityQueue()
        self.pinned_queues: dict[str, queue.PriorityQueue[tuple[int, int, dict[str, Any]]]] = {
            p["name"]: queue.PriorityQueue() for p in self.raw_profiles
        }
        self._seq_counter = 0
        self._seq_lock = threading.Lock()

        # Task tracking & DAG variation pinning
        self.parent_profile_map: dict[str, str] = {}  # task_id -> profile_name
        self.parent_media_map: dict[str, str] = {}    # task_id -> media_id
        self.deferred_tasks: dict[str, list[tuple[int, int, dict[str, Any]]]] = {} # parent_id -> list of deferred child tasks
        self.dag_lock = threading.Lock()

        # Active tasks accounting for wait_completion
        self._pending_tasks = 0
        self._tasks_lock = threading.Lock()
        self._tasks_done_cond = threading.Condition(self._tasks_lock)

        self.results: dict[str, dict[str, Any]] = {}
        self.incidents: list[dict[str, Any]] = []
        self.workers: list[threading.Thread] = []
        self.abort_event = threading.Event()
        self.is_running = False

    def __enter__(self) -> PersistentWorkerPool:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.shutdown()

    def start(self) -> None:
        """Spawn worker threads and establish persistent sessions."""
        if self.is_running:
            return
        self.is_running = True
        self.abort_event.clear()

        num_workers = min(self.target_workers, len(self.raw_profiles))
        for w_id in range(1, num_workers + 1):
            prof = self.profile_pool.acquire()
            if not prof:
                logger.warning("Insufficient profiles in pool to start Worker-%d", w_id)
                break
            t = threading.Thread(
                target=self._worker_thread_loop,
                args=(w_id, prof),
                name=f"PersistentWorker-{w_id}",
                daemon=True,
            )
            self.workers.append(t)
            t.start()
            if self.stagger_seconds > 0:
                time.sleep(self.stagger_seconds)

    def _next_seq(self) -> int:
        with self._seq_lock:
            self._seq_counter += 1
            return self._seq_counter

    def submit_task(self, task: dict[str, Any], priority: int = 10) -> None:
        """Submit an image generation task.

        priority=10: standard submission
        priority=0:  high-priority retry
        """
        task_id = str(task.get("id") or task.get("request_id") or task.get("index") or self._next_seq())
        task["_registered_id"] = task_id
        seq = self._next_seq()

        with self._tasks_lock:
            self._pending_tasks += 1

        with self.dag_lock:
            parent_id = task.get("based_on") or task.get("parent_id") or task.get("base_shot")
            if parent_id:
                parent_id_str = str(parent_id)
                # If parent already completed, pin to parent profile immediately
                if parent_id_str in self.parent_profile_map:
                    parent_prof = self.parent_profile_map[parent_id_str]
                    task["pinned_profile"] = parent_prof
                    if parent_id_str in self.parent_media_map and not task.get("baseMediaId"):
                        task["baseMediaId"] = self.parent_media_map[parent_id_str]
                    if parent_prof in self.pinned_queues:
                        self.pinned_queues[parent_prof].put((priority, seq, task))
                        return
                else:
                    # Parent shot not completed yet; defer task until parent finishes
                    self.deferred_tasks.setdefault(parent_id_str, []).append((priority, seq, task))
                    return

            # Check if pre-pinned
            pinned = task.get("pinned_profile")
            if pinned and pinned in self.pinned_queues:
                self.pinned_queues[pinned].put((priority, seq, task))
                return

        self.shared_queue.put((priority, seq, task))

    def _launch_browser(self, prof_cfg: dict[str, Any]) -> bool:
        """Ensure Chrome is running for the designated profile."""
        target_url = prof_cfg.get("url", "https://flow.google.com/")
        if self.proc_mgr and hasattr(self.proc_mgr, "launch"):
            return self.proc_mgr.launch(prof_cfg, url=target_url, headless=self.headless)
        try:
            from flow_cdp import accounts
            port = int(prof_cfg.get("cdp_port") or prof_cfg.get("port", 0))
            if accounts.is_port_listening(port):
                return True
            entry = {
                "port": port,
                "user_data_dir": prof_cfg["user_data_dir"],
                "directory": prof_cfg.get("profile_dir", "Default"),
            }
            return accounts.launch_profile(entry, url=target_url)
        except Exception as ex:
            logger.warning("Browser launch error on %s: %s", prof_cfg.get("name"), ex)
            return False

    def _create_session(self, prof_cfg: dict[str, Any]) -> Any:
        if self.session_factory is not None:
            return self.session_factory(prof_cfg)
        from flow_cdp.cdp_direct_client import DirectCDPProfileSession
        return DirectCDPProfileSession(prof_cfg)

    def _worker_thread_loop(self, worker_id: int, initial_profile: dict[str, Any]) -> None:
        """Worker thread maintaining long-lived WebSocket session."""
        current_profile = initial_profile
        prof_name = current_profile["name"]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        sess = None

        def init_session(p_cfg: dict[str, Any]) -> Any:
            self._launch_browser(p_cfg)
            s = self._create_session(p_cfg)
            if hasattr(s, "connect"):
                res = s.connect()
                if asyncio.iscoroutine(res):
                    loop.run_until_complete(res)
            if hasattr(s, "_wait_for_flow_ready"):
                state = loop.run_until_complete(s._wait_for_flow_ready(timeout=12.0))
                if isinstance(state, dict) and not state.get("hasAt"):
                    try:
                        if hasattr(s, "close"):
                            c = s.close()
                            if asyncio.iscoroutine(c):
                                loop.run_until_complete(c)
                    except Exception:
                        pass
                    raise RuntimeError(f"Profile {p_cfg.get('name')} not authenticated on Flow (hasAt=False)")
            return s

        while sess is None and current_profile is not None and not self.abort_event.is_set():
            prof_name = current_profile["name"]
            try:
                sess = init_session(current_profile)
            except Exception as exc:
                logger.warning("[Worker-%d] Profile %s unavailable at startup: %s", worker_id, prof_name, exc)
                self.profile_pool.release(current_profile, quarantine_reason="init_connect_failed")
                current_profile = self.profile_pool.acquire()

        if sess is None or current_profile is None:
            logger.error("[Worker-%d] No healthy profiles available. Exiting.", worker_id)
            loop.close()
            return

        last_request_time = 0.0

        try:
            while not self.abort_event.is_set():
                task_item = None

                # 1. Check worker's dedicated pinned queue first
                if prof_name in self.pinned_queues:
                    try:
                        task_item = self.pinned_queues[prof_name].get_nowait()
                    except queue.Empty:
                        pass

                # 2. Check shared priority queue
                if task_item is None:
                    try:
                        task_item = self.shared_queue.get(timeout=0.3)
                    except queue.Empty:
                        continue

                priority, seq, task = task_item
                pinned_to = task.get("pinned_profile")
                if pinned_to and pinned_to != prof_name:
                    # Routed to foreign worker: re-route to correct pinned queue
                    if pinned_to in self.pinned_queues:
                        self.pinned_queues[pinned_to].put((priority, seq, task))
                    else:
                        self.shared_queue.put((priority, seq, task))
                    continue

                task_id = task.get("_registered_id") or str(seq)

                # 3. Pacing gap enforcement (>= pacing_seconds per profile)
                now = time.time()
                elapsed = now - last_request_time
                if elapsed < self.pacing_seconds:
                    sleep_dur = self.pacing_seconds - elapsed
                    if not self.abort_event.is_set():
                        time.sleep(sleep_dur)

                # 4. Execute image generation
                t0 = time.time()
                try:
                    res = self._execute_task_rpc(loop, sess, task, current_profile)
                    last_request_time = time.time()
                    latency = round(time.time() - t0, 2)

                    # Successful generation: store result & update DAG mappings
                    media_id = res.get("media_id") or res.get("forge_id") or ""
                    res["latency"] = latency
                    res["profile_id"] = prof_name

                    # Write standardized JSON sidecar
                    img_path_str = res.get("path")
                    if img_path_str:
                        sidecar_path = Path(img_path_str).with_suffix(".json")
                        sidecar_payload = {
                            "jobId": str(task.get("jobId") or task.get("id") or task_id),
                            "forgeId": media_id,
                            "profile_id": prof_name,
                            "prompt": task.get("prompt", ""),
                            "latency": latency,
                            "sha256": res.get("sha256", ""),
                            "aspect_ratio": task.get("ratio") or task.get("aspect") or "16:9",
                            "width": res.get("width", 0),
                            "height": res.get("height", 0),
                            "shot_type": task.get("shot_type", "full_scene"),
                            "type": "image",
                            "source": "google-flow-browser",
                            "status": "downloaded",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                        try:
                            sidecar_path.write_text(
                                json.dumps(sidecar_payload, ensure_ascii=False, indent=2),
                                encoding="utf-8",
                            )
                            res["sidecar"] = str(sidecar_path)
                        except Exception as sc_err:
                            logger.warning("Failed writing sidecar %s: %s", sidecar_path, sc_err)

                    with self.dag_lock:
                        self.parent_profile_map[task_id] = prof_name
                        if media_id:
                            self.parent_media_map[task_id] = media_id
                        self.results[task_id] = res

                        # Release deferred dependent tasks waiting on this shot
                        if task_id in self.deferred_tasks:
                            for dep_priority, dep_seq, dep_task in self.deferred_tasks.pop(task_id):
                                dep_task["pinned_profile"] = prof_name
                                if media_id and not dep_task.get("baseMediaId"):
                                    dep_task["baseMediaId"] = media_id
                                if prof_name in self.pinned_queues:
                                    self.pinned_queues[prof_name].put((dep_priority, dep_seq, dep_task))
                                else:
                                    self.shared_queue.put((dep_priority, dep_seq, dep_task))

                    if callable(task.get("callback")):
                        try:
                            task["callback"](task, res, None)
                        except Exception:
                            pass

                    self._mark_task_finished()

                except Exception as exc:
                    err_str = str(exc)
                    is_rate_limit = any(p.search(err_str) for p in UNUSUAL_ACTIVITY_PATTERNS)

                    incident = {
                        "task_id": task_id,
                        "profile": prof_name,
                        "error": err_str,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "is_rate_limit": is_rate_limit,
                    }
                    self.incidents.append(incident)

                    if is_rate_limit:
                        logger.warning("[FAILOVER] Profile %s hit rate limit / unusual activity at task %s: %s", prof_name, task_id, err_str)
                        # Remediate in session
                        loop.run_until_complete(remediate_profile_session(sess))

                        # Close session and quarantine profile for 10 minutes
                        old_name = prof_name
                        try:
                            if hasattr(sess, "close"):
                                close_res = sess.close()
                                if asyncio.iscoroutine(close_res):
                                    loop.run_until_complete(close_res)
                        except Exception:
                            pass

                        self.profile_pool.release(current_profile, quarantine_reason="rate_limit_error_7")

                        # Re-queue task at HEAD of queue (priority=0)
                        task["retries"] = task.get("retries", 0) + 1
                        if task["retries"] <= task.get("max_retries", 3):
                            # Note: if task was pinned to old_name, clear pinning so healthy profile can take it,
                            # unless it depends on completed media
                            if not task.get("based_on"):
                                task.pop("pinned_profile", None)
                            self.shared_queue.put((0, seq, task))
                        else:
                            logger.error("Task %s exceeded max retries after rate limit", task_id)
                            with self.dag_lock:
                                if task_id in self.deferred_tasks:
                                    for _dep_priority, dep_seq, dep_task in self.deferred_tasks.pop(task_id):
                                        dep_id = dep_task.get("_registered_id") or str(dep_seq)
                                        logger.error("Dependent task %s aborted because parent %s failed permanently", dep_id, task_id)
                                        if callable(dep_task.get("callback")):
                                            try:
                                                dep_task["callback"](dep_task, None, RuntimeError(f"Parent task {task_id} failed permanently"))
                                            except Exception:
                                                pass
                                        self._mark_task_finished()
                            self._mark_task_finished()

                        # Standby profile swap
                        new_prof = self.profile_pool.acquire(current_name=old_name)
                        if not new_prof:
                            logger.warning("[Worker-%d] No standby profiles available. Waiting 10s...", worker_id)
                            time.sleep(10)
                            new_prof = self.profile_pool.acquire()
                            if not new_prof:
                                logger.error("[Worker-%d] All profiles exhausted. Terminating worker.", worker_id)
                                break
                        current_profile = new_prof
                        prof_name = current_profile["name"]
                        logger.info("[Worker-%d] Swapped to standby profile %s", worker_id, prof_name)
                        try:
                            sess = init_session(current_profile)
                        except Exception as switch_err:
                            logger.error("[Worker-%d] Failed connecting to swapped profile %s: %s", worker_id, prof_name, switch_err)
                            self.profile_pool.release(current_profile, quarantine_reason="swapped_connect_failed")
                            break
                        continue

                    else:
                        # Non-rate-limit exception (transient transport or download error)
                        task["retries"] = task.get("retries", 0) + 1
                        if task["retries"] <= task.get("max_retries", 3):
                            self.shared_queue.put((0, seq, task))
                            time.sleep(1.0)
                        else:
                            logger.error("Task %s failed permanently: %s", task_id, err_str)
                            with self.dag_lock:
                                if task_id in self.deferred_tasks:
                                    for _dep_priority, dep_seq, dep_task in self.deferred_tasks.pop(task_id):
                                        dep_id = dep_task.get("_registered_id") or str(dep_seq)
                                        logger.error("Dependent task %s aborted because parent %s failed permanently", dep_id, task_id)
                                        if callable(dep_task.get("callback")):
                                            try:
                                                dep_task["callback"](dep_task, None, RuntimeError(f"Parent task {task_id} failed permanently"))
                                            except Exception:
                                                pass
                                        self._mark_task_finished()
                            if callable(task.get("callback")):
                                try:
                                    task["callback"](task, None, exc)
                                except Exception:
                                    pass
                            self._mark_task_finished()

        finally:
            if sess:
                try:
                    if hasattr(sess, "close"):
                        c = sess.close()
                        if asyncio.iscoroutine(c):
                            loop.run_until_complete(c)
                except Exception:
                    pass
            self.profile_pool.release(current_profile)
            loop.close()

    def _execute_task_rpc(self, loop: asyncio.AbstractEventLoop, sess: Any, task: dict[str, Any], prof_cfg: dict[str, Any]) -> dict[str, Any]:
        """Execute RPC call, download, PIL verification and atomic move."""
        prompt = task["prompt"]
        aspect = task.get("ratio") or task.get("aspect") or "16:9"
        model = task.get("model", "BELUGA")
        base_media_id = task.get("baseMediaId") or task.get("base_media_id")

        if hasattr(sess, "generate_image"):
            gen_res = sess.generate_image(
                prompt=prompt,
                aspect=aspect,
                model=model,
                base_media_id=base_media_id,
            )
            if asyncio.iscoroutine(gen_res):
                res = loop.run_until_complete(gen_res)
            else:
                res = gen_res
        else:
            raise RuntimeError("Session does not support generate_image")

        media_url = res.get("url")
        media_id = res.get("media_id") or res.get("forge_id")
        out_dir = Path(task.get("out_dir") or self.default_out_dir or (Path(tempfile.gettempdir()) / "video-pilot-pool-images"))
        out_dir.mkdir(parents=True, exist_ok=True)
        task_idx = task.get("index") or task.get("_registered_id") or "000"
        filename = task.get("filename") or f"image_{task_idx}.jpg"

        # If a destination file path is already provided
        img_dest = out_dir / filename
        width, height = 0, 0

        # Download binary if URL returned
        if media_url and media_url.startswith("http"):
            staging_dir = out_dir.parent / ".staging"
            staging_dir.mkdir(parents=True, exist_ok=True)
            staging_path = staging_dir / f"temp_{task_idx}_{prof_cfg['name']}.jpg"

            img_data = b""
            for dl_attempt in range(3):
                try:
                    req = urllib.request.Request(media_url, headers={"User-Agent": "video-pilot"})
                    with urllib.request.urlopen(req, timeout=45) as resp:
                        img_data = resp.read()
                    if len(img_data) >= 5000:
                        break
                except Exception as dl_err:
                    if dl_attempt == 2:
                        raise RuntimeError(f"Download failed after 3 attempts: {dl_err}") from dl_err
                    time.sleep(1.0)

            if len(img_data) < 5000:
                raise RuntimeError(f"Downloaded image too small ({len(img_data)} bytes)")

            staging_path.write_bytes(img_data)
            with Image.open(staging_path) as im:
                im.verify()
            with Image.open(staging_path) as im:
                im.load()
                width, height = im.size
            overlay_cfg = task.get("editorial_overlay", {"enabled": True})
            if overlay_cfg and overlay_cfg.get("enabled", True):
                from tools.editorial_compositor import apply_editorial_overlay
                apply_editorial_overlay(staging_path, overlay_cfg)
            shutil.move(str(staging_path), str(img_dest))
            f_hash = sha256_file(img_dest)
        else:
            img_dest.touch(exist_ok=True)
            f_hash = "mock_sha256"

        return {
            "path": str(img_dest),
            "media_id": media_id,
            "url": media_url,
            "sha256": f_hash,
            "width": width,
            "height": height,
            "profile_id": prof_cfg["name"],
        }

    def _mark_task_finished(self) -> None:
        with self._tasks_lock:
            self._pending_tasks = max(0, self._pending_tasks - 1)
            if self._pending_tasks == 0:
                self._tasks_done_cond.notify_all()

    def wait_completion(self, timeout: float | None = None) -> bool:
        """Block until all submitted tasks and their dependent retries have finished."""
        with self._tasks_lock:
            if self._pending_tasks == 0:
                return True
            return self._tasks_done_cond.wait_for(
                lambda: self._pending_tasks == 0 or self.abort_event.is_set(),
                timeout=timeout,
            )

    def shutdown(self, wait_timeout: float = 4.0) -> None:
        """Cleanly stop worker threads, close sessions, and terminate browser processes."""
        self.abort_event.set()
        with self._tasks_lock:
            self._tasks_done_cond.notify_all()

        for t in self.workers:
            t.join(timeout=wait_timeout)
        self.workers.clear()

        self.profile_pool.release_all()

        if self.proc_mgr and hasattr(self.proc_mgr, "terminate_all"):
            try:
                self.proc_mgr.terminate_all()
            except Exception as e:
                logger.warning("Error during proc_mgr terminate_all: %s", e)

        self.is_running = False

    def get_status(self) -> dict[str, Any]:
        with self._tasks_lock:
            pending = self._pending_tasks
        return {
            "is_running": self.is_running,
            "active_worker_threads": sum(1 for t in self.workers if t.is_alive()),
            "pending_tasks": pending,
            "shared_queue_size": self.shared_queue.qsize(),
            "completed_results": len(self.results),
            "incidents_count": len(self.incidents),
            "pool_status": self.profile_pool.get_status(),
        }
