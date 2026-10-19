"""Flow CDP Lifecycle & Dynamic Workload Manager.

Guarantees:
1. Adaptive Tab Sizing: Automatically calculates optimal parallel Chrome workers
   based on workload size (e.g. 1 tab for micro tasks, 2-3 for shorts, 8-10 for bulk)
   to eliminate RAM waste.
2. Accurate Lifecycle Tracking: Distinguishes between pre-existing user Chrome instances
   and newly spawned instances ("mở bao nhiêu thì tắt bấy nhiêu").
3. Guaranteed Teardown: Shuts down spawned browser instances upon task completion, error,
   or unexpected exit (via context manager & atexit hooks) to ensure zero RAM leakage.
"""
from __future__ import annotations

import atexit
import logging
import math
import os
import signal
import sys
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("flow_cdp.lifecycle")

# Workload Tiers Definition
WORKLOAD_TIERS = [
    {
        "tier": "micro",
        "min_images": 1,
        "max_images": 3,
        "recommended_workers": 1,
        "description": "Thumbnail, Scene Retake, hoặc Test Prompt",
        "estimated_ram_mb": 600,
    },
    {
        "tier": "short",
        "min_images": 4,
        "max_images": 8,
        "recommended_workers": 2,
        "description": "TikTok / Reels / Shorts 9:16 (5 cảnh độc lập SC01..SC05)",
        "estimated_ram_mb": 1400,
    },
    {
        "tier": "chapter",
        "min_images": 9,
        "max_images": 20,
        "recommended_workers": 4,
        "description": "Một Chapter đơn lẻ hoặc Explainer ngắn 3-5 phút",
        "estimated_ram_mb": 2600,
    },
    {
        "tier": "standard_explainer",
        "min_images": 21,
        "max_images": 50,
        "recommended_workers": 6,
        "description": "Video full_frame_v1 tiêu chuẩn (5-8 phút, 30-45 cảnh)",
        "estimated_ram_mb": 4200,
    },
    {
        "tier": "bulk_long_video",
        "min_images": 51,
        "max_images": 999999,
        "recommended_workers": 8,
        "description": "Video dài long_16x9 (11-13 phút, 8 chapters, 48 scenes) hoặc Batch lớn",
        "estimated_ram_mb": 6500,
    },
]


def calculate_optimal_workers(num_images: int, max_cap: int = 10, min_cap: int = 1) -> int:
    """Calculate the optimal number of parallel workers for a given image count.

    Strategy:
    - 1-3 images:   1 tab  (Startup overhead of multiple tabs is not justified)
    - 4-8 images:   2-3 tabs (Shorts 9:16 finishes in ~60-80s without wasting RAM)
    - 9-20 images:  4-5 tabs (Medium chapter, finishes in ~1.5-2.5m)
    - 21-50 images: 6-7 tabs (Standard full explainer)
    - >50 images:   8-10 tabs (Large batch, capped at RAM safety limit)
    """
    if num_images <= 0:
        return min_cap
    if num_images <= 3:
        target = 1
    elif num_images <= 8:
        target = max(2, math.ceil(num_images / 3))
    elif num_images <= 20:
        target = max(3, math.ceil(num_images / 4))
    elif num_images <= 50:
        target = max(5, math.ceil(num_images / 7))
    else:
        target = min(max_cap, max(8, math.ceil(num_images / 15)))

    return max(min_cap, min(max_cap, target))


def get_workload_tier_info(num_images: int) -> dict[str, Any]:
    """Return descriptive metadata about the workload tier and resource profile."""
    for t in WORKLOAD_TIERS:
        if t["min_images"] <= num_images <= t["max_images"]:
            info = dict(t)
            info["actual_workers"] = calculate_optimal_workers(num_images)
            return info
    return {
        "tier": "custom",
        "min_images": num_images,
        "max_images": num_images,
        "recommended_workers": calculate_optimal_workers(num_images),
        "actual_workers": calculate_optimal_workers(num_images),
        "description": "Tùy biến",
        "estimated_ram_mb": calculate_optimal_workers(num_images) * 700,
    }


_ACTIVE_LIFECYCLE: ProfileLifecycleManager | None = None


def get_current_lifecycle() -> ProfileLifecycleManager | None:
    return _ACTIVE_LIFECYCLE


def register_spawned_port(port: int) -> None:
    """Register a newly spawned Chrome debug port with the active lifecycle manager."""
    global _ACTIVE_LIFECYCLE
    if _ACTIVE_LIFECYCLE is not None:
        _ACTIVE_LIFECYCLE.spawned_ports.add(port)


class ProfileLifecycleManager:
    """Manages spawning, tracking, and clean teardown of Chrome profile instances.

    Ensures that only profiles spawned during the current session are closed upon exit,
    preserving pre-existing user browser windows.
    """

    def __init__(self, auto_teardown: bool = True, force_teardown_all: bool = False):
        from . import accounts
        self.accounts = accounts
        self.auto_teardown = auto_teardown
        self.force_teardown_all = force_teardown_all

        # Record pre-existing open ports before launching any new instances
        self.pre_existing_ports: set[int] = set()
        self.spawned_ports: set[int] = set()
        self.active_sessions: list[Any] = []
        self._record_pre_existing()

        # Register exit hook for emergency cleanup
        if self.auto_teardown:
            atexit.register(self._atexit_handler)

    def _record_pre_existing(self) -> None:
        """Scan which profile ports are already listening."""
        reg = self.accounts.registry()
        for p in reg.get("profiles", []):
            port = int(p["port"])
            if self.accounts.is_port_listening(port):
                self.pre_existing_ports.add(port)

    def launch_profile(self, profile_cfg: dict[str, Any], url: str = "https://flow.google.com/") -> bool:
        """Launch a profile if not running, and track it if newly spawned."""
        port = int(profile_cfg.get("port") or profile_cfg.get("cdp_port", 0))
        if port == 0:
            return False

        if self.accounts.is_port_listening(port):
            # Port was already open
            return True

        entry = {
            "port": port,
            "user_data_dir": profile_cfg["user_data_dir"],
            "directory": profile_cfg.get("directory") or profile_cfg.get("profile_dir", "Default"),
        }
        ok = self.accounts.launch_profile(entry, url=url)
        if ok:
            self.spawned_ports.add(port)
            logger.info("Lifecycle: Spawned new Chrome instance on port %d", port)
        return ok

    def teardown(self, force_all: bool | None = None) -> list[int]:
        """Shut down Chrome instances and free system memory.

        If force_all is True: closes all profiles used.
        Otherwise: strictly closes instances spawned by this run ('mở bao nhiêu tắt bấy nhiêu').
        """
        do_force = self.force_teardown_all if force_all is None else force_all
        closed_ports = []

        if do_force:
            target_ports = set(self.pre_existing_ports).union(self.spawned_ports)
        else:
            target_ports = set(self.spawned_ports)

        for port in list(target_ports):
            try:
                self.accounts.stop_profile_by_port(port)
                closed_ports.append(port)
                self.spawned_ports.discard(port)
            except Exception as e:
                logger.warning("Error stopping profile on port %d: %s", port, e)

        return closed_ports

    def _atexit_handler(self) -> None:
        """Hook called when Python process terminates."""
        if self.spawned_ports:
            self.teardown(force_all=self.force_teardown_all)

    def __enter__(self) -> ProfileLifecycleManager:
        global _ACTIVE_LIFECYCLE
        self._prev_active = _ACTIVE_LIFECYCLE
        _ACTIVE_LIFECYCLE = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        global _ACTIVE_LIFECYCLE
        _ACTIVE_LIFECYCLE = self._prev_active
        if self.auto_teardown:
            self.teardown(force_all=self.force_teardown_all)

