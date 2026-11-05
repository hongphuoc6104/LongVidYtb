"""Orchestrator for multi-account Flow Video generation and seamless stitching."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone

logger = logging.getLogger("flow_video.orchestrator")
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SYS_DIR = _REPO_ROOT / "sys"
for _p in (str(_REPO_ROOT), str(_SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_cdp.process_manager import get_process_manager
from sys.flow_cdp.resource_locks import GlobalBrowserSlot, ProfilePortLock
from sys.flow_video.chain_planner import (
    build_chain_tasks,
    export_remotion_beats,
)
from sys.flow_video.models import (
    ChainMode,
    VideoChainSpec,
    VideoClipTask,
)
from sys.flow_video.stitcher import (
    ASPECT_RESOLUTIONS,
    probe_video_clip,
    render_flipbook_segment,
    stitch_video_chain,
)
from typing import Any

from PIL import Image

# Resilient import of upstream profiles
try:
    from sys.flow_cdp.cdp_direct_client import (
        DirectCDPProfileSession,
        get_all_configured_profiles,
    )
except ImportError:
    try:
        from sys.flow_cdp.cdp_direct_client import PROFILES, DirectCDPProfileSession

        def get_all_configured_profiles() -> list[dict[str, Any]]:
            return [dict(p) for p in PROFILES]
    except ImportError:
        DirectCDPProfileSession = None  # type: ignore

        def get_all_configured_profiles() -> list[dict[str, Any]]:
            return []

# Resilient import of CreditLedger
try:
    from sys.flow_cdp.credit_ledger import CreditLedger
except ImportError:

    class CreditLedger:  # type: ignore
        """Fallback ledger conforming to upstream credit ledger contract."""

        def __init__(self, ledger_path: Path | str | None = None) -> None:
            self.balances: dict[str, int] = {}
            self.exhausted: set[str] = set()

        def sync_balance(self, profile_id: str, balance: int) -> None:
            self.balances[profile_id] = int(balance)

        def get_balance(self, profile_id: str) -> int:
            return self.balances.get(profile_id, 100)

        def is_eligible(self, profile_id: str, min_credits: int = 10) -> bool:
            if profile_id in self.exhausted:
                return False
            return self.get_balance(profile_id) >= min_credits

        def select_eligible_profiles(
            self, profiles: list[dict[str, Any]], min_credits: int = 10
        ) -> list[dict[str, Any]]:
            return [
                p
                for p in profiles
                if self.is_eligible(
                    str(p.get("name") or p.get("profile_dir", "")),
                    min_credits=min_credits,
                )
            ]

        def deduct_credits(
            self, profile_id: str, amount: int, reason: str = "video"
        ) -> None:
            curr = self.get_balance(profile_id)
            self.balances[profile_id] = max(0, curr - amount)

        def mark_exhausted(
            self,
            profile_id: str,
            expiry_epoch: int | None = None,
            reason: str = "quota",
        ) -> None:
            self.exhausted.add(profile_id)

        def pick_and_reserve(
            self,
            profiles: list[dict[str, Any]] | None = None,
            cost: int = 10,
            min_credits: int | None = None,
            profile_id: str | None = None,
        ) -> dict[str, Any] | str | None:
            threshold = cost if min_credits is None else min_credits
            if profile_id:
                return profile_id if self.is_eligible(profile_id, min_credits=threshold) else None
            if profiles:
                eligible = self.select_eligible_profiles(profiles, min_credits=threshold)
                if eligible:
                    return eligible[0]
            return None

        def pick_for_image_task(
            self, profiles: list[dict[str, Any]]
        ) -> dict[str, Any] | None:
            if not profiles:
                return None
            sorted_p = sorted(
                profiles,
                key=lambda p: self.get_balance(str(p.get("name") or p.get("profile_dir", ""))),
            )
            return sorted_p[0]

        def pick_profile(
            self, profiles: list[dict[str, Any]], min_credits: int = 0
        ) -> dict[str, Any] | None:
            return self.pick_for_image_task(profiles)

        def commit(self, profile_id: str, cost: int = 10, reason: str = "video") -> int:
            self.deduct_credits(profile_id, cost, reason=reason)
            return self.get_balance(profile_id)

        def rollback(self, profile_id: str, cost: int = 10) -> None:
            pass


class FlowVideoChainOrchestrator:
    """End-to-end orchestrator for multi-account Flow Video pipelines."""

    def __init__(
        self,
        spec: VideoChainSpec,
        work_dir: str | Path | None = None,
        output_mp4_path: str | Path | None = None,
        max_workers: int = 6,
        headless: bool = True,
        resume: bool = True,
        dry_run: bool = False,
        max_retries_per_clip: int = 20,
        skip_stitch: bool = False,
    ) -> None:
        self.spec = spec
        base_dir = (
            Path(work_dir)
            if work_dir
            else Path(f"sys/runs/flow_video_{spec.job_id}")
        )
        self.work_dir = base_dir.resolve()
        self.frames_dir = self.work_dir / "frames"
        self.clips_dir = self.work_dir / "clips"
        self.out_dir = self.work_dir / "output"

        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.output_mp4_path = (
            Path(output_mp4_path).resolve()
            if output_mp4_path
            else self.out_dir / f"{spec.job_id}_final.mp4"
        )
        self.manifest_path = self.work_dir / "chain_manifest.json"
        self.remotion_beats_path = self.work_dir / "remotion_beats.json"
        self.chain_report_path = self.work_dir / "chain_report.json"

        self.max_workers = max(1, int(max_workers))
        self.headless = bool(headless)
        self.resume = bool(resume)
        self.dry_run = bool(dry_run)
        self.max_retries = max(1, int(max_retries_per_clip))
        self.skip_stitch = bool(skip_stitch)

        self.credit_ledger = CreditLedger()
        self._launched_ports: set[int] = set()
        self._profiles_used: set[str] = set()
        self._credits_deducted: dict[str, int] = {}
        self._profile_cooldowns: dict[str, float] = {}
        self._lock = asyncio.Lock()

    # Proven high-success video profiles ordered by empirical completion rate;
    # 0%-success flagged profiles are pushed to the back as last-resort fallback.
    PROVEN_VIDEO_PROFILES: tuple[str, ...] = (
        "profile_13",
        "profile_en16",
        "profile_en01",
        "profile_18",
        "profile_9",
        "profile_4",
        "profile_en13",
        "profile_en03",
        "profile_1",
        "profile_en07",
        "profile_en11",
        "profile_19",
        "profile_6",
        "profile_en10",
    )
    KNOWN_BLOCKED_VIDEO_PROFILES: frozenset[str] = frozenset({
        "profile_2", "profile_3", "profile_7", "profile_12", "profile_14",
        "profile_15", "profile_17", "profile_20", "profile_21",
        "profile_en09", "profile_en12",
    })

    def _get_channel_profiles(self) -> list[dict[str, Any]]:
        """Return profiles ordered by proven video health and rotated per job_id to prevent port collisions."""
        import hashlib
        import os

        all_profiles = get_all_configured_profiles()
        explicit_raw = os.environ.get("VP_FLOW_PROFILES", "").strip()
        explicit_names = [x.strip() for x in explicit_raw.split(",") if x.strip()] if explicit_raw else []
        if explicit_names:
            explicit_primary = [
                p for p in all_profiles
                if p.get("name") in explicit_names or p.get("id") in explicit_names
            ]
            rest = [
                p for p in all_profiles
                if p not in explicit_primary and p.get("name") != "profile_11"
            ]
            if explicit_primary:
                return explicit_primary + rest

        if len(all_profiles) <= 4:
            return all_profiles

        by_name = {str(p.get("name") or p.get("id")): p for p in all_profiles}
        tier1_healthy = [by_name[n] for n in self.PROVEN_VIDEO_PROFILES if n in by_name]
        tier2_secondary = [
            p for p in all_profiles
            if p not in tier1_healthy
            and str(p.get("name") or p.get("id")) not in self.KNOWN_BLOCKED_VIDEO_PROFILES
        ]
        tier3_blocked = [
            p for p in all_profiles
            if p not in tier1_healthy and p not in tier2_secondary
        ]

        # Rotate tier1 and tier2 deterministically by job_id so concurrent jobs spread across ports
        job_seed = str(getattr(self.spec, "job_id", "") or getattr(self.spec, "channel_id", "") or "default")
        offset = int(hashlib.md5(job_seed.encode("utf-8")).hexdigest()[:8], 16)
        if len(tier1_healthy) > 1:
            rot1 = offset % len(tier1_healthy)
            tier1_healthy = tier1_healthy[rot1:] + tier1_healthy[:rot1]
        if len(tier2_secondary) > 1:
            rot2 = offset % len(tier2_secondary)
            tier2_secondary = tier2_secondary[rot2:] + tier2_secondary[:rot2]

        return tier1_healthy + tier2_secondary + tier3_blocked

    def run(self) -> dict[str, Any]:
        """Synchronous convenience wrapper to execute pipeline."""
        return asyncio.run(self.run_async())

    async def run_async(self) -> dict[str, Any]:
        """Main async orchestration lifecycle."""
        try:
            # Step 1: Ensure all keyframe / scene pair images exist on disk
            await self._ensure_keyframes()

            # Step 2: Check zero-credit flipbook mode or auto-fallback
            is_flipbook = (
                self.spec.mode == ChainMode.ZERO_CREDIT_FLIPBOOK
                or str(self.spec.mode).lower() == "zero_credit_flipbook"
            )

            if not is_flipbook and getattr(self.spec, "auto_fallback_zero_credit", True):
                all_profiles = self._get_channel_profiles()
                initial_tasks = self._plan_tasks()
                min_cost = min(
                    (
                        getattr(t, "credit_cost", 0)
                        or self._credit_cost_for_model(self.spec.video_model, int(round(t.duration_sec)))
                        for t in initial_tasks
                    ),
                    default=7,
                )
                eligible = self.credit_ledger.select_eligible_profiles(all_profiles, min_credits=min_cost)
                if not eligible:
                    is_flipbook = True
                    self.spec.mode = ChainMode.ZERO_CREDIT_FLIPBOOK

            # Step 3: Build clip tasks
            tasks = self._plan_tasks()

            # Step 4: Reconcile with existing manifest if resume is enabled
            tasks = self._reconcile_manifest(tasks)

            # Step 5: Generation across accounts or local zero-credit flipbook
            if is_flipbook:
                await self._generate_flipbook_clips(tasks)
            else:
                await self._generate_clips_parallel(tasks)

            # Step 6: Stitch final seamless video (skip when Remotion composites raw clips directly)
            if self.skip_stitch:
                stitch_report = {
                    "skipped": True,
                    "duration": round(sum(float(t.duration_sec or 0.0) for t in tasks), 2),
                }
            else:
                stitch_report = self._stitch_final(tasks)

            # Step 7: Export Remotion beats and summary report
            report = self._finalize_reports(tasks, stitch_report)
            return report

        finally:
            # STRICT TEARDOWN: Ensure 0 leaked Chrome processes!
            self._teardown_all_chrome_processes()

    # -------------------------------------------------------------------------
    # Step 1: Keyframe Resolution
    # -------------------------------------------------------------------------
    async def _ensure_keyframes(self) -> None:
        """Verify image paths exist on disk or generate them via Flow CDP."""
        items_to_check: list[tuple[str, str | None, str | None, Any]] = []

        if self.spec.keyframes:
            for kf in self.spec.keyframes:
                items_to_check.append(
                    (kf.id, kf.image_path, kf.image_prompt, kf)
                )
        else:
            for sp in self.spec.scene_pairs:
                items_to_check.append(
                    (f"{sp.id}_start", sp.start_image_path, sp.start_image_prompt, (sp, "start"))
                )
                if sp.end_image_path or sp.end_image_prompt:
                    items_to_check.append(
                        (f"{sp.id}_end", sp.end_image_path, sp.end_image_prompt, (sp, "end"))
                    )

        for item_id, img_path, prompt, ref_obj in items_to_check:
            if img_path and Path(img_path).is_file():
                continue

            # Need to generate missing frame
            dest_file = self.frames_dir / f"{item_id}.png"
            if self.resume and dest_file.is_file() and dest_file.stat().st_size > 0:
                self._update_ref_path(ref_obj, str(dest_file.resolve()))
                continue

            if self.dry_run:
                self._create_dummy_image(dest_file, self.spec.aspect)
                self._update_ref_path(ref_obj, str(dest_file.resolve()))
                continue

            if not prompt:
                raise ValueError(
                    f"Frame {item_id} has neither an existing image_path nor an image_prompt"
                )

            # Generate via Flow CDP
            await self._generate_single_image(prompt, dest_file)
            self._update_ref_path(ref_obj, str(dest_file.resolve()))

    def _update_ref_path(self, ref_obj: Any, path_str: str) -> None:
        if isinstance(ref_obj, tuple):
            sp, side = ref_obj
            if side == "start":
                sp.start_image_path = path_str
            else:
                sp.end_image_path = path_str
        else:
            ref_obj.image_path = path_str

    def _create_dummy_image(self, dest_path: Path, aspect: str) -> None:
        tw, th = ASPECT_RESOLUTIONS.get(aspect, (1920, 1080))
        img = Image.new("RGB", (tw, th), color=(46, 67, 97))
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest_path)

    async def _generate_single_image(self, prompt: str, dest_file: Path) -> None:
        """Generate a single image frame using an eligible Chrome profile with automatic failover."""
        profiles = self._get_channel_profiles()
        eligible: list[dict[str, Any]] = []

        if hasattr(self.credit_ledger, "pick_for_image_task"):
            picked = self.credit_ledger.pick_for_image_task(profiles)
            if picked:
                eligible = [picked] if isinstance(picked, dict) else [p for p in profiles if (p.get("id") or p.get("name")) == picked]
        elif hasattr(self.credit_ledger, "pick_profile"):
            picked = self.credit_ledger.pick_profile(profiles)
            if picked:
                eligible = [picked] if isinstance(picked, dict) else [p for p in profiles if (p.get("id") or p.get("name")) == picked]

        if not eligible:
            eligible = self.credit_ledger.select_eligible_profiles(profiles, min_credits=0)
            if not eligible:
                eligible = self.credit_ledger.select_eligible_profiles(profiles, min_credits=10)
            if not eligible:
                eligible = list(profiles)

        if not eligible:
            raise RuntimeError("No eligible Chrome profiles with credits available for image generation")

        last_exc: Exception | None = None
        for profile_cfg in eligible:
            port = int(profile_cfg.get("cdp_port", 9222))
            profile_name = str(profile_cfg.get("name") or f"profile_{port}")

            port_lock = ProfilePortLock(port, owner_tag=f"img_{dest_file.stem}")
            browser_slot = GlobalBrowserSlot(owner_tag=f"img_{dest_file.stem}")

            if not browser_slot.acquire(timeout=60.0):
                continue

            try:
                if not port_lock.acquire(timeout=30.0):
                    continue
                try:
                    pm = get_process_manager()
                    launched = pm.launch(profile_cfg, headless=self.headless)
                    if not launched:
                        continue
                    self._launched_ports.add(port)

                    session = DirectCDPProfileSession(profile_cfg)
                    await session.connect()
                    try:
                        res = await session.generate_image(
                            prompt=prompt,
                            aspect=self.spec.aspect,
                            model="BELUGA",
                        )
                        url = res.get("url")
                        if not url:
                            raise RuntimeError(f"Image generation returned no URL: {res}")

                        await self._download_binary(session, url, dest_file)

                        # Validate with PIL
                        with Image.open(dest_file) as im:
                            im.verify()

                        sidecar_file = dest_file.with_suffix(".json")
                        sidecar_data = {
                            "media_id": res.get("media_id"),
                            "url": url,
                            "profile": profile_name,
                            "prompt": prompt,
                            "aspect": self.spec.aspect,
                            "model": "BELUGA",
                            "generated_at": datetime.now(timezone.utc).isoformat(),
                        }
                        sidecar_file.write_text(
                            json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8",
                        )

                        self.credit_ledger.deduct_credits(profile_name, 10, reason="image")
                        self._profiles_used.add(profile_name)
                        return
                    finally:
                        await session.close()
                        pm.terminate_by_port(port)
                        self._launched_ports.discard(port)
                finally:
                    port_lock.release()
            except Exception as exc:
                last_exc = exc
                try:
                    get_process_manager().terminate_by_port(port)
                    self._launched_ports.discard(port)
                except Exception:
                    pass
                if "INSUFFICIENT_CREDITS" in str(exc) or "PUBLIC_ERROR_QUOTA" in str(exc):
                    self.credit_ledger.mark_exhausted(profile_name, reason=str(exc))
                continue
            finally:
                browser_slot.release()

        raise RuntimeError(f"Failed to generate image frame {dest_file.name}: {last_exc}")

    async def _download_binary(self, session: Any, url: str, dest_file: Path) -> int:
        if hasattr(session, "download_authenticated_binary"):
            return await session.download_authenticated_binary(url, str(dest_file))

        # Fallback via CDP JavaScript evaluate
        js = f"""
        (async () => {{
            const resp = await fetch({json.dumps(url)});
            if (!resp.ok) throw new Error("HTTP " + resp.status);
            const blob = await resp.blob();
            return new Promise((resolve, reject) => {{
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result.split(',')[1]);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            }});
        }})()
        """
        b64_str = await session.evaluate(js, await_promise=True, timeout=90.0)
        raw_bytes = base64.b64decode(b64_str)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_bytes(raw_bytes)
        return len(raw_bytes)

    # -------------------------------------------------------------------------
    # Step 2: Task Planning & Manifest Reconciliation
    # -------------------------------------------------------------------------
    def _plan_tasks(self) -> list[VideoClipTask]:
        return build_chain_tasks(self.spec, work_dir=self.work_dir)

    def _credit_cost_for_model(self, model: str, duration_sec: int = 6) -> int:
        norm = (model or "").lower().strip()
        if "flipbook" in norm or "zero_credit" in norm:
            return 0
        elif "omni" in norm or "abra" in norm:
            credit_map = {4: 7, 6: 10, 8: 12, 10: 15}
            return credit_map.get(duration_sec, 10)
        elif "lite" in norm:
            return 10
        elif "quality" in norm:
            return 100
        elif "fast" in norm:
            return 20
        return 10

    def _reconcile_manifest(self, tasks: list[VideoClipTask]) -> list[VideoClipTask]:
        """Check existing manifest on disk to avoid re-generating finished clips."""
        if not self.resume or not self.manifest_path.is_file():
            self._save_manifest(tasks)
            return tasks

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            saved_clips = {c["clip_id"]: c for c in saved.get("tasks", [])}
        except Exception:
            self._save_manifest(tasks)
            return tasks

        for t in tasks:
            if t.clip_id in saved_clips:
                cached = saved_clips[t.clip_id]
                out_p = Path(cached.get("output_mp4_path", t.output_mp4_path))
                if (
                    cached.get("status") == "completed"
                    and out_p.is_file()
                    and out_p.stat().st_size > 0
                ):
                    try:
                        probe_video_clip(out_p)
                        t.status = "completed"
                        t.output_mp4_path = str(out_p.resolve())
                        t.profile_used = cached.get("profile_used")
                        t.generation_seconds = float(cached.get("generation_seconds", 0.0))
                    except Exception:
                        t.status = "pending"

        self._save_manifest(tasks)
        return tasks

    def _save_manifest(self, tasks: list[VideoClipTask]) -> None:
        payload = {
            "job_id": self.spec.job_id,
            "mode": self.spec.mode.value if isinstance(self.spec.mode, ChainMode) else str(self.spec.mode),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "tasks": [t.to_dict() for t in tasks],
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    async def _generate_flipbook_clips(self, tasks: list[VideoClipTask]) -> None:
        """Render all clip segments locally via render_flipbook_segment (0 credits, 0 RPC calls)."""
        tw, th = ASPECT_RESOLUTIONS.get(self.spec.aspect, (1920, 1080))
        for task in tasks:
            if task.status == "completed":
                continue

            out_p = Path(task.output_mp4_path)
            if self.resume and out_p.is_file() and out_p.stat().st_size > 0:
                try:
                    probe_video_clip(out_p)
                    task.status = "completed"
                    task.credit_cost = 0
                    task.profile_used = "local_zero_credit_flipbook"
                    continue
                except Exception:
                    pass

            target_dur = float(task.target_duration or task.duration_sec)
            start_t = time.monotonic()
            if self.dry_run:
                if Path(task.start_frame_path).is_file():
                    render_flipbook_segment(
                        start_image=task.start_frame_path,
                        end_image=task.end_frame_path if task.end_frame_path and Path(task.end_frame_path).is_file() else None,
                        output_mp4=task.output_mp4_path,
                        duration_sec=target_dur,
                        width=tw,
                        height=th,
                        fps=self.spec.target_fps,
                    )
                else:
                    self._generate_dummy_clip(task)
            else:
                render_flipbook_segment(
                    start_image=task.start_frame_path,
                    end_image=task.end_frame_path,
                    output_mp4=task.output_mp4_path,
                    duration_sec=target_dur,
                    width=tw,
                    height=th,
                    fps=self.spec.target_fps,
                )

            elapsed = time.monotonic() - start_t
            task.generation_seconds = round(elapsed, 2)
            task.status = "completed"
            task.credit_cost = 0
            task.profile_used = "local_zero_credit_flipbook"
            self._save_manifest(tasks)

    # -------------------------------------------------------------------------
    # Step 3: Parallel Clip Generation Across Multi-Account Pool
    # -------------------------------------------------------------------------
    async def _generate_clips_parallel(self, tasks: list[VideoClipTask]) -> None:
        pending = [t for t in tasks if t.status != "completed"]
        if not pending:
            return

        if self.dry_run:
            for t in pending:
                self._generate_dummy_clip(t)
                t.status = "completed"
                t.profile_used = "dry_run_mock"
                self._save_manifest(tasks)
            return

        all_profiles = self._get_channel_profiles()
        min_cost = min(
            (
                getattr(t, "credit_cost", 0)
                or self._credit_cost_for_model(self.spec.video_model, int(round(t.duration_sec)))
                for t in pending
            ),
            default=10,
        )
        eligible_profiles = self.credit_ledger.select_eligible_profiles(
            all_profiles, min_credits=min_cost
        )
        if not eligible_profiles:
            raise RuntimeError(
                f"No eligible Chrome profiles with >= {min_cost} credits found"
            )

        num_workers = min(len(pending), self.max_workers, len(eligible_profiles))
        worker_queue: asyncio.Queue[VideoClipTask] = asyncio.Queue()
        for t in pending:
            worker_queue.put_nowait(t)

        available_profiles: list[dict[str, Any]] = list(eligible_profiles)

        async def worker_loop(worker_idx: int) -> None:
            if worker_idx > 0:
                await asyncio.sleep(min(worker_idx * 0.75, 5.0))
            while not worker_queue.empty():
                try:
                    task = worker_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                clip_cost = getattr(task, "credit_cost", 0) or self._credit_cost_for_model(
                    self.spec.video_model, int(round(task.duration_sec))
                )
                success = False
                attempts = 0
                port_skips = 0

                while not success and attempts < self.max_retries:
                    attempts += 1
                    profile_cfg = None
                    wait_sec = 0.0

                    async with self._lock:
                        now = time.time()
                        # Find profile eligible for this specific clip_cost and not on cooldown
                        def is_candidate(p: dict[str, Any], cost: int = clip_cost, cur_now: float = now) -> bool:
                            pname = str(p.get("name") or p.get("profile_dir", ""))
                            return self.credit_ledger.is_eligible(pname, min_credits=cost) and self._profile_cooldowns.get(pname, 0.0) <= cur_now

                        eligible_candidates = [p for p in available_profiles if is_candidate(p)]
                        if not eligible_candidates:
                            # Re-check eligible from pool
                            fresh = self.credit_ledger.select_eligible_profiles(all_profiles, min_credits=clip_cost)
                            for fp in fresh:
                                if fp not in available_profiles:
                                    available_profiles.append(fp)
                            eligible_candidates = [p for p in available_profiles if is_candidate(p)]

                        if not eligible_candidates:
                            # All eligible profiles might be in cooldown
                            cooldown_times = [
                                self._profile_cooldowns.get(str(p.get("name") or p.get("profile_dir", "")), 0.0)
                                for p in available_profiles
                                if self.credit_ledger.is_eligible(str(p.get("name") or p.get("profile_dir", "")), min_credits=clip_cost)
                            ]
                            active_cooldowns = [t for t in cooldown_times if t > now]
                            if active_cooldowns:
                                wait_sec = max(2.0, min(30.0, min(active_cooldowns) - now))
                                attempts = max(0, attempts - 1)  # Do not burn attempt budget while waiting for cooldown
                            else:
                                task.status = "failed"
                                task.error = f"All profiles exhausted or insufficient credits (needed {clip_cost})"
                                self._save_manifest(tasks)
                                worker_queue.task_done()
                                return
                        else:
                            profile_cfg = eligible_candidates[0]
                            available_profiles.remove(profile_cfg)

                    if wait_sec > 0:
                        logger.info(f"All eligible profiles in cooldown. Waiting {wait_sec:.1f}s before retrying task {task.clip_id}...")
                        await asyncio.sleep(wait_sec)
                        continue

                    p_name = str(profile_cfg.get("name") or f"profile_{profile_cfg.get('cdp_port')}")
                    try:
                        await self._generate_single_clip(task, profile_cfg=profile_cfg)
                        task.status = "completed"
                        task.profile_used = p_name
                        success = True
                        async with self._lock:
                            available_profiles.append(profile_cfg)
                            self._profiles_used.add(p_name)
                            self._save_manifest(tasks)
                    except Exception as exc:
                        task.error = str(exc)
                        now_exc = time.time()
                        is_port_busy = "Chrome port" in str(exc) and "busy" in str(exc)
                        if is_port_busy:
                            port_skips += 1
                            attempts = max(0, attempts - 1)
                        async with self._lock:
                            # Check if real credit exhausted
                            if "INSUFFICIENT_CREDITS" in str(exc) or "PUBLIC_ERROR_QUOTA" in str(exc):
                                self.credit_ledger.mark_exhausted(p_name, reason=str(exc))
                            elif "FLOW_PROVIDER_BLOCKED" in str(exc) or "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in str(exc):
                                self._profile_cooldowns[p_name] = now_exc + 1800.0
                                available_profiles.append(profile_cfg)
                                attempts = max(0, attempts - 1)  # Do not burn attempt budget on temporary provider rate limit
                            elif is_port_busy:
                                # Port busy from another worker; retry this profile after brief 3s stagger
                                self._profile_cooldowns[p_name] = now_exc + 3.0
                                available_profiles.append(profile_cfg)
                            else:
                                # Put failed profile on 45s cooldown to rotate across other profiles
                                self._profile_cooldowns[p_name] = now_exc + 45.0
                                available_profiles.append(profile_cfg)
                            self._save_manifest(tasks)
                        # Rotate immediately to next healthy profile with brief jitter instead of blocking worker for 45s
                        if "TOO_MUCH_TRAFFIC" in str(exc) or "FLOW_PROVIDER_BLOCKED" in str(exc) or "PUBLIC_ERROR_UNUSUAL_ACTIVITY" in str(exc):
                            logger.warning(f"[RATE_LIMIT_ROTATE] Profile {p_name} rate-limited at clip {task.clip_id}. Cooldown 1800s; rotating in 2.5s...")
                            await asyncio.sleep(2.5)
                        else:
                            # Brief backoff before rotating to next profile
                            await asyncio.sleep(min(5.0, 1.0 * attempts))

                if not success:
                    task.status = "failed"
                    self._save_manifest(tasks)

                worker_queue.task_done()

        workers = [asyncio.create_task(worker_loop(i)) for i in range(num_workers)]
        await asyncio.gather(*workers)

        # Check if any tasks failed
        failed = [t for t in tasks if t.status == "failed"]
        if failed:
            err_details = "; ".join(f"{t.clip_id}: {t.error}" for t in failed)
            raise RuntimeError(f"Generation failed for {len(failed)} clips: {err_details}")

    async def _generate_single_clip(
        self, clip: VideoClipTask, profile_cfg: dict[str, Any] | None = None
    ) -> None:
        """Launch headless Chrome, query credits, and synthesize video clip via DirectCDP."""
        clip_cost = getattr(clip, "credit_cost", 0) or self._credit_cost_for_model(
            self.spec.video_model, int(round(clip.duration_sec))
        )

        all_profiles = self._get_channel_profiles()
        if profile_cfg is None:
            if hasattr(self.credit_ledger, "pick_and_reserve"):
                reserved = self.credit_ledger.pick_and_reserve(profiles=all_profiles, cost=clip_cost)
                if isinstance(reserved, dict):
                    profile_cfg = reserved
            if profile_cfg is None:
                eligible = self.credit_ledger.select_eligible_profiles(all_profiles, min_credits=clip_cost)
                if not eligible:
                    raise RuntimeError(f"No eligible Chrome profiles with >= {clip_cost} credits found")
                profile_cfg = eligible[0]

        port = int(profile_cfg.get("cdp_port", 9222))
        p_name = str(profile_cfg.get("name") or f"profile_{port}")

        if hasattr(self.credit_ledger, "pick_and_reserve"):
            self.credit_ledger.pick_and_reserve(profile_id=p_name, cost=clip_cost)

        port_lock = ProfilePortLock(port, owner_tag=f"clip_{clip.clip_id}")
        browser_slot = GlobalBrowserSlot(owner_tag=f"clip_{clip.clip_id}")

        if not browser_slot.acquire(timeout=60.0):
            if hasattr(self.credit_ledger, "rollback"):
                self.credit_ledger.rollback(p_name, clip_cost)
            raise TimeoutError("All global browser slots busy")

        try:
            if not port_lock.acquire(timeout=1.5):
                if hasattr(self.credit_ledger, "rollback"):
                    self.credit_ledger.rollback(p_name, clip_cost)
                raise TimeoutError(f"Chrome port {port} busy")
            try:
                pm = get_process_manager()
                launched = pm.launch(profile_cfg, headless=self.headless)
                if not launched:
                    if hasattr(self.credit_ledger, "rollback"):
                        self.credit_ledger.rollback(p_name, clip_cost)
                    raise RuntimeError(f"Failed to launch Chrome on port {port}")
                self._launched_ports.add(port)

                session = DirectCDPProfileSession(profile_cfg)
                await session.connect()
                try:
                    # Verify live credits
                    if hasattr(session, "query_credits"):
                        credits_info = await session.query_credits()
                        rem = int(credits_info.get("remaining", 0))
                        self.credit_ledger.sync_balance(p_name, rem)
                        if rem < clip_cost:
                            if hasattr(self.credit_ledger, "rollback"):
                                self.credit_ledger.rollback(p_name, clip_cost)
                            self.credit_ledger.mark_exhausted(p_name, reason="INSUFFICIENT_CREDITS")
                            raise RuntimeError(
                                f"Live credits ({rem}) below required cost ({clip_cost}) for {p_name}"
                            )

                    # Synthesize video clip with exact duration_seconds
                    start_t = time.monotonic()
                    if hasattr(session, "generate_video_from_frames"):
                        await session.generate_video_from_frames(
                            prompt=clip.motion_prompt,
                            first_frame_path_or_id=clip.start_frame_path,
                            last_frame_path_or_id=clip.end_frame_path,
                            output_mp4_path=clip.output_mp4_path,
                            aspect=clip.aspect,
                            model=clip.video_model,
                            duration_seconds=int(round(clip.duration_sec)),
                            seed=clip.seed,
                        )
                    else:
                        raise NotImplementedError(
                            "session.generate_video_from_frames not available in cdp_direct_client"
                        )

                    elapsed = time.monotonic() - start_t
                    clip.generation_seconds = round(elapsed, 2)

                    # Verify output clip
                    probe_video_clip(clip.output_mp4_path)

                    # Commit credits
                    if hasattr(self.credit_ledger, "commit"):
                        self.credit_ledger.commit(p_name, clip_cost)
                    else:
                        self.credit_ledger.deduct_credits(p_name, clip_cost, reason="video")

                    curr_ded = self._credits_deducted.get(p_name, 0)
                    self._credits_deducted[p_name] = curr_ded + clip_cost
                finally:
                    await session.close()
                    pm.terminate_by_port(port)
                    self._launched_ports.discard(port)
            except Exception:
                if hasattr(self.credit_ledger, "rollback"):
                    self.credit_ledger.rollback(p_name, clip_cost)
                try:
                    get_process_manager().terminate_by_port(port)
                    self._launched_ports.discard(port)
                except Exception:
                    pass
                raise
            finally:
                port_lock.release()
        finally:
            browser_slot.release()

    async def _execute_clip_on_profile(
        self, task: VideoClipTask, profile_cfg: dict[str, Any], cost: int
    ) -> None:
        task.credit_cost = cost
        await self._generate_single_clip(task, profile_cfg=profile_cfg)

    def _generate_dummy_clip(self, task: VideoClipTask) -> None:
        """Create a lightweight synthetic test clip for dry runs."""
        tw, th = ASPECT_RESOLUTIONS.get(task.aspect, (1920, 1080))
        dur = max(1, int(round(task.duration_sec)))
        out_p = Path(task.output_mp4_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"testsrc=duration={dur}:size={tw}x{th}:rate=30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "ultrafast",
            str(out_p.resolve()),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        task.generation_seconds = 0.5

    # -------------------------------------------------------------------------
    # Step 4: Final Stitching & Reporting
    # -------------------------------------------------------------------------
    def _stitch_final(self, tasks: list[VideoClipTask]) -> dict[str, Any]:
        return stitch_video_chain(
            clips=tasks,
            output_mp4_path=self.output_mp4_path,
            mode=self.spec.mode,
            aspect=self.spec.aspect,
            fps=self.spec.target_fps,
            audio_path=self.spec.audio_path,
            normalize_audio_lufs=self.spec.normalize_audio_lufs,
            keep_veo_audio=self.spec.keep_veo_audio,
            veo_audio_mix_weight=getattr(self.spec, "veo_audio_mix_weight", 0.45),
        )

    def _finalize_reports(
        self, tasks: list[VideoClipTask], stitch_report: dict[str, Any]
    ) -> dict[str, Any]:
        # Remotion beats export
        beats = export_remotion_beats(tasks, mode=self.spec.mode, fps=self.spec.target_fps)
        with open(self.remotion_beats_path, "w", encoding="utf-8") as f:
            json.dump(beats, f, indent=2)

        clips_summary = [
            {
                "clip_id": t.clip_id,
                "index": t.index,
                "duration_sec": t.duration_sec,
                "target_duration_sec": t.target_duration_sec,
                "credit_cost": getattr(t, "credit_cost", 0),
                "output_mp4_path": t.output_mp4_path,
                "status": t.status,
            }
            for t in tasks
        ]
        total_credit_cost = sum(c["credit_cost"] for c in clips_summary)

        # Full chain report
        report = {
            "job_id": self.spec.job_id,
            "mode": self.spec.mode.value if isinstance(self.spec.mode, ChainMode) else str(self.spec.mode),
            "aspect": self.spec.aspect,
            "video_model": self.spec.video_model,
            "duration_seconds": stitch_report.get("duration", 0.0),
            "nb_clips": len(tasks),
            "total_credit_cost": total_credit_cost,
            "clips": clips_summary,
            "tasks": [t.to_dict() for t in tasks],
            "stitched_video": stitch_report,
            "output_path": str(self.output_mp4_path),
            "profiles_used": list(self._profiles_used),
            "credits_deducted": self._credits_deducted,
            "dry_run": self.dry_run,
            "remotion_beats_file": str(self.remotion_beats_path),
            "manifest_file": str(self.manifest_path),
            "success": True,
        }

        with open(self.chain_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def _teardown_all_chrome_processes(self) -> None:
        """Strictly stop and clean up any Chrome processes launched by this run."""
        pm = get_process_manager()
        for port in list(self._launched_ports):
            try:
                pm.terminate_by_port(port)
            except Exception:
                pass
        self._launched_ports.clear()
