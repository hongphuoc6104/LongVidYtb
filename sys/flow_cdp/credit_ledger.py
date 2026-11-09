"""Google Flow CDP Multi-Profile Credit & Quota Ledger.

Provides a thread-safe and multiprocess-safe (fcntl.flock) persistence ledger for
tracking 1,000-credit balances, live RPC quota balances, expiry epochs, deduction
accounting, and least-recently-used rotation across all Chrome profiles.
"""
from __future__ import annotations

import fcntl
import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

logger = logging.getLogger("flow_cdp.credit_ledger")

MIN_VIDEO_CREDITS = 7
TIER_ROLE_VIDEO_AND_IMAGE = "video_and_image"
TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT = "image_only_zero_credit"
TIER_ROLE_AUTH_EXPIRED = "auth_expired"


def compute_tier_role(credits: int, status: str = "active") -> str:
    """Calculate 2-tier role based on credit balance and account status.

    - If status == "auth_expired": "auth_expired"
    - If status == "exhausted" or 0 <= credits < MIN_VIDEO_CREDITS: "image_only_zero_credit"
      (active for Nano Banana Pro / 2.1 / 2 Lite, 2K Upsample, and Gemini TTS zero-credit tasks)
    - If credits >= MIN_VIDEO_CREDITS and status != "auth_expired": "video_and_image"
    """
    if status == "auth_expired":
        return TIER_ROLE_AUTH_EXPIRED
    if status == "exhausted" or 0 <= int(credits) < MIN_VIDEO_CREDITS:
        return TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT
    if int(credits) >= MIN_VIDEO_CREDITS:
        return TIER_ROLE_VIDEO_AND_IMAGE
    return TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT


DEFAULT_CREDITS_PATH = Path(
    os.environ.get(
        "VP_FLOW_CREDITS_PATH",
        str(Path.home() / ".config/video-pilot/flow/credits.json"),
    )
)


class CreditLedger:
    """Multiprocess-safe and thread-safe credit ledger for Flow CDP profiles."""

    def __init__(self, path: Path | str | None = None):
        if path is not None:
            self.path = Path(path).expanduser().resolve()
        else:
            env_path = os.environ.get("VP_FLOW_CREDITS_PATH")
            if env_path:
                self.path = Path(env_path).expanduser().resolve()
            else:
                self.path = (Path.home() / ".config/video-pilot/flow/credits.json").resolve()

        self._thread_lock = threading.RLock()
        self._lock_path = self.path.with_name(self.path.name + ".lock")

    @contextmanager
    def _locked_store(self) -> Generator[dict[str, Any], None, None]:
        """Atomically lock file and yield mutable store dictionary with save on exit."""
        with self._thread_lock:
            self._lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(str(self._lock_path), os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                data = self._read_data()
                yield data
                self._write_data(data)
            finally:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
                os.close(fd)

    def _read_data(self) -> dict[str, Any]:
        """Read data from disk or return fresh schema."""
        if self.path.is_file():
            try:
                content = self.path.read_text(encoding="utf-8")
                data = json.loads(content)
                if isinstance(data, dict) and "profiles" in data:
                    return data
            except Exception as e:
                logger.warning("Failed to parse credit ledger %s: %s; recreating.", self.path, e)

        return {
            "version": 1,
            "updated_at": time.time(),
            "profiles": {},
        }

    def _write_data(self, data: dict[str, Any]) -> None:
        """Write data atomically via temporary file."""
        data["updated_at"] = time.time()
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        tmp.replace(self.path)

    def register_profile(
        self,
        profile_id: str,
        initial_credits: int = 1000,
    ) -> dict[str, Any]:
        """Register a profile with initial credit balance if not present."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            if profile_id in profiles:
                entry = profiles[profile_id]
                if "tier_role" not in entry:
                    entry["tier_role"] = compute_tier_role(
                        int(entry.get("credits_remaining", 0)),
                        entry.get("status", "active"),
                    )
                return dict(entry)

            now = time.time()
            status = "active" if initial_credits > 0 else "exhausted"
            entry = {
                "credits_remaining": initial_credits,
                "subscription_credits": initial_credits,
                "expiry_epoch": None,
                "paygate_tier": 0,
                "status": status,
                "exhausted_reason": None,
                "last_used_at": 0.0,
                "last_synced_at": now,
                "tier_role": compute_tier_role(initial_credits, status),
                "cooldown_until": 0.0,
                "cooldown_reason": None,
            }
            profiles[profile_id] = entry
            return dict(entry)

    def sync_balance(
        self,
        profile_id: str,
        remaining: int,
        subscription_credits: int = 1000,
        expiry_epoch: int | None = None,
        paygate_tier: int = 0,
    ) -> dict[str, Any]:
        """Sync live balance obtained via CDP RPC query."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            entry = profiles.get(profile_id, {})
            now = time.time()

            entry["credits_remaining"] = remaining
            entry["subscription_credits"] = subscription_credits
            entry["expiry_epoch"] = expiry_epoch
            entry["paygate_tier"] = paygate_tier
            entry["last_synced_at"] = now

            if remaining > 0:
                entry["status"] = "active"
                entry["exhausted_reason"] = None
            else:
                entry["status"] = "exhausted"
                entry["exhausted_reason"] = "quota_exceeded"

            entry["tier_role"] = compute_tier_role(remaining, entry["status"])
            profiles[profile_id] = entry
            return dict(entry)

    def get_balance(self, profile_id: str, default_credits: int = 1000) -> int:
        """Get remaining credits for a profile, auto-resetting if subscription expiry passed."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            now = time.time()

            if profile_id not in profiles:
                status = "active" if default_credits > 0 else "exhausted"
                entry = {
                    "credits_remaining": default_credits,
                    "subscription_credits": default_credits,
                    "expiry_epoch": None,
                    "paygate_tier": 0,
                    "status": status,
                    "exhausted_reason": None,
                    "last_used_at": 0.0,
                    "last_synced_at": now,
                    "tier_role": compute_tier_role(default_credits, status),
                    "cooldown_until": 0.0,
                    "cooldown_reason": None,
                }
                profiles[profile_id] = entry
                return default_credits

            entry = profiles[profile_id]
            expiry = entry.get("expiry_epoch")
            if expiry is not None and now >= expiry:
                sub_credits = entry.get("subscription_credits") or default_credits
                entry["credits_remaining"] = sub_credits
                entry["status"] = "active"
                entry["exhausted_reason"] = None
                entry["expiry_epoch"] = None
                entry["tier_role"] = compute_tier_role(sub_credits, "active")
                logger.info(
                    "Profile %s subscription reset triggered at %s (balance reset to %d)",
                    profile_id,
                    now,
                    sub_credits,
                )

            return int(entry.get("credits_remaining", 0))

    def is_eligible(self, profile_id: str, min_credits: int = 10) -> bool:
        """Check if profile has enough remaining credits, is not exhausted, and is not on cooldown."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            now = time.time()
            if profile_id not in profiles:
                status = "active" if 1000 > 0 else "exhausted"
                entry = {
                    "credits_remaining": 1000,
                    "subscription_credits": 1000,
                    "expiry_epoch": None,
                    "paygate_tier": 0,
                    "status": status,
                    "exhausted_reason": None,
                    "last_used_at": 0.0,
                    "last_synced_at": now,
                    "tier_role": compute_tier_role(1000, status),
                    "cooldown_until": 0.0,
                    "cooldown_reason": None,
                }
                profiles[profile_id] = entry
                return 1000 >= min_credits

            entry = profiles[profile_id]
            if float(entry.get("cooldown_until") or 0.0) > now:
                return False

            expiry = entry.get("expiry_epoch")
            if expiry is not None and now >= expiry:
                sub_credits = entry.get("subscription_credits") or 1000
                entry["credits_remaining"] = sub_credits
                entry["status"] = "active"
                entry["exhausted_reason"] = None
                entry["expiry_epoch"] = None
                entry["tier_role"] = compute_tier_role(sub_credits, "active")

            bal = int(entry.get("credits_remaining", 0))
            status = entry.get("status", "active")
            return bal >= min_credits and status not in ("exhausted", "auth_expired")

    def set_credits(
        self,
        profile_id: str,
        credits: int,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Explicitly set credits for profile, auto-updating tier_role and exhaustion status."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            now = time.time()
            new_bal = max(0, int(credits))

            if profile_id not in profiles:
                st = status if status is not None else ("active" if new_bal > 0 else "exhausted")
                entry = {
                    "credits_remaining": new_bal,
                    "subscription_credits": 1000,
                    "expiry_epoch": None,
                    "paygate_tier": 0,
                    "status": st,
                    "exhausted_reason": None,
                    "last_used_at": 0.0,
                    "last_synced_at": now,
                    "tier_role": compute_tier_role(new_bal, st),
                    "cooldown_until": 0.0,
                    "cooldown_reason": None,
                }
                profiles[profile_id] = entry
                return dict(entry)

            entry = profiles[profile_id]
            entry["credits_remaining"] = new_bal

            if status is not None:
                entry["status"] = status
            elif new_bal <= 0:
                entry["status"] = "exhausted"
                entry["exhausted_reason"] = entry.get("exhausted_reason") or "quota_exceeded"
            elif entry.get("status") == "exhausted" and new_bal > 0:
                entry["status"] = "active"
                entry["exhausted_reason"] = None

            entry["tier_role"] = compute_tier_role(new_bal, entry.get("status", "active"))
            profiles[profile_id] = entry
            return dict(entry)

    def select_eligible_profiles(
        self,
        profiles: list[dict[str, Any]],
        min_credits: int = 10,
    ) -> list[dict[str, Any]]:
        """Filter and sort eligible profiles, preferring tested profiles (last_used > 0), higher credits, and LRU."""
        eligible_items: list[tuple[int, int, float, dict[str, Any]]] = []

        for p in profiles:
            pid = p.get("id") or p.get("name")
            if not pid:
                continue
            if not self.is_eligible(pid, min_credits=min_credits):
                continue

            with self._locked_store() as data:
                entry = data.get("profiles", {}).get(pid, {})
                remaining = int(entry.get("credits_remaining", 0))
                last_used = float(entry.get("last_used_at", 0.0))

            # Sort key: (-remaining, last_used) to prioritize accounts with highest credits
            eligible_items.append((0, remaining, last_used, p))

        eligible_items.sort(key=lambda x: (-x[1], x[2]))
        return [item[3] for item in eligible_items]

    def pick_for_image_task(
        self,
        profiles: list[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Pick optimal profile for zero-credit image/TTS generation.

        Prioritizes image_only_zero_credit accounts (0 <= available < 7) FIRST
        (sorted by lowest available credits first, then oldest last_used_at).
        Falls back to video_and_image accounts (sorted by lowest available credits first,
        then oldest last_used_at) to preserve high-credit accounts for video generation!
        """
        if not profiles:
            return None

        zero_credit_candidates: list[tuple[int, float, dict[str, Any]]] = []
        video_candidates: list[tuple[int, float, dict[str, Any]]] = []

        with self._locked_store() as data:
            store_profiles = data.setdefault("profiles", {})
            now = time.time()

            for p in profiles:
                pid = p.get("id") or p.get("name")
                if not pid:
                    continue
                if p.get("enabled") is False:
                    continue

                if pid not in store_profiles:
                    entry = {
                        "credits_remaining": 1000,
                        "subscription_credits": 1000,
                        "expiry_epoch": None,
                        "paygate_tier": 0,
                        "status": "active",
                        "exhausted_reason": None,
                        "last_used_at": 0.0,
                        "last_synced_at": now,
                        "tier_role": TIER_ROLE_VIDEO_AND_IMAGE,
                        "cooldown_until": 0.0,
                        "cooldown_reason": None,
                    }
                    store_profiles[pid] = entry
                else:
                    entry = store_profiles[pid]

                if float(entry.get("cooldown_until") or 0.0) > now:
                    continue

                status = entry.get("status", "active")
                if status == "auth_expired":
                    continue

                # Auto-reset if subscription expiry passed
                expiry = entry.get("expiry_epoch")
                if expiry is not None and now >= expiry:
                    sub_credits = entry.get("subscription_credits") or 1000
                    entry["credits_remaining"] = sub_credits
                    entry["status"] = "active"
                    entry["exhausted_reason"] = None
                    entry["expiry_epoch"] = None
                    entry["tier_role"] = compute_tier_role(sub_credits, "active")
                    status = "active"

                available = int(entry.get("credits_remaining", 0))
                last_used = float(entry.get("last_used_at", 0.0))
                role = entry.get("tier_role") or compute_tier_role(available, status)

                if role == TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT or (0 <= available < MIN_VIDEO_CREDITS) or status == "exhausted":
                    zero_credit_candidates.append((available, last_used, p))
                else:
                    video_candidates.append((available, last_used, p))

        if zero_credit_candidates:
            # Sort by lowest available credits first, then oldest last_used_at
            zero_credit_candidates.sort(key=lambda x: (x[0], x[1]))
            return zero_credit_candidates[0][2]

        if video_candidates:
            # Fall back to video_and_image accounts with lowest credits first
            video_candidates.sort(key=lambda x: (x[0], x[1]))
            return video_candidates[0][2]

        return None

    def pick_for_video_task(
        self,
        profiles: list[dict[str, Any]],
        cost: int = 7,
        min_credits: int = 7,
    ) -> Optional[dict[str, Any]]:
        """Pick optimal profile for video generation clip.

        Picks from video_and_image accounts where available >= max(cost, min_credits),
        sorted by highest available credits first, then oldest last_used_at.
        Skips accounts with < MIN_VIDEO_CREDITS (7) or exhausted/auth_expired status.
        """
        if not profiles:
            return None

        threshold = max(cost, min_credits)
        candidates: list[tuple[int, float, dict[str, Any]]] = []

        with self._locked_store() as data:
            store_profiles = data.setdefault("profiles", {})
            now = time.time()

            for p in profiles:
                pid = p.get("id") or p.get("name")
                if not pid:
                    continue
                if p.get("enabled") is False:
                    continue

                if pid not in store_profiles:
                    entry = {
                        "credits_remaining": 1000,
                        "subscription_credits": 1000,
                        "expiry_epoch": None,
                        "paygate_tier": 0,
                        "status": "active",
                        "exhausted_reason": None,
                        "last_used_at": 0.0,
                        "last_synced_at": now,
                        "tier_role": TIER_ROLE_VIDEO_AND_IMAGE,
                        "cooldown_until": 0.0,
                        "cooldown_reason": None,
                    }
                    store_profiles[pid] = entry
                else:
                    entry = store_profiles[pid]

                if float(entry.get("cooldown_until") or 0.0) > now:
                    continue

                status = entry.get("status", "active")
                if status in ("auth_expired", "exhausted"):
                    continue

                # Auto-reset if subscription expiry passed
                expiry = entry.get("expiry_epoch")
                if expiry is not None and now >= expiry:
                    sub_credits = entry.get("subscription_credits") or 1000
                    entry["credits_remaining"] = sub_credits
                    entry["status"] = "active"
                    entry["exhausted_reason"] = None
                    entry["expiry_epoch"] = None
                    entry["tier_role"] = compute_tier_role(sub_credits, "active")
                    status = "active"

                available = int(entry.get("credits_remaining", 0))
                last_used = float(entry.get("last_used_at", 0.0))
                role = entry.get("tier_role") or compute_tier_role(available, status)

                if role != TIER_ROLE_VIDEO_AND_IMAGE:
                    continue
                if available < threshold:
                    continue

                candidates.append((available, last_used, p))

        if not candidates:
            return None

        # Highest available credits first (-x[0]), then oldest last_used_at (x[1])
        candidates.sort(key=lambda x: (-x[0], x[1]))
        return candidates[0][2]

    def deduct_credits(
        self,
        profile_id: str,
        amount: int = 10,
        reason: str = "video",
    ) -> int:
        """Deduct credits upon successful generation."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            now = time.time()
            if profile_id not in profiles:
                profiles[profile_id] = {
                    "credits_remaining": 1000,
                    "subscription_credits": 1000,
                    "expiry_epoch": None,
                    "paygate_tier": 0,
                    "status": "active",
                    "exhausted_reason": None,
                    "last_used_at": 0.0,
                    "last_synced_at": now,
                    "tier_role": TIER_ROLE_VIDEO_AND_IMAGE,
                    "cooldown_until": 0.0,
                    "cooldown_reason": None,
                }

            entry = profiles[profile_id]
            curr = int(entry.get("credits_remaining", 1000))
            new_bal = max(0, curr - amount)
            entry["credits_remaining"] = new_bal
            entry["last_used_at"] = now

            if float(entry.get("cooldown_until") or 0.0) <= now:
                entry["cooldown_until"] = 0.0
                entry["cooldown_reason"] = None

            if new_bal <= 0:
                entry["status"] = "exhausted"
                entry["exhausted_reason"] = reason

            entry["tier_role"] = compute_tier_role(new_bal, entry.get("status", "active"))

            profiles[profile_id] = entry
            logger.debug(
                "Profile %s deducted %d credits (reason: %s); new balance: %d, tier: %s",
                profile_id,
                amount,
                reason,
                new_bal,
                entry["tier_role"],
            )
            return new_bal

    def pick_and_reserve(
        self,
        profiles: list[dict[str, Any]] | None = None,
        cost: int = 10,
        min_credits: int | None = None,
        profile_id: str | None = None,
    ) -> dict[str, Any] | str | None:
        """Pick an eligible profile with sufficient balance and reserve the task."""
        threshold = cost if min_credits is None else min_credits
        if profile_id:
            if self.is_eligible(profile_id, min_credits=threshold):
                return profile_id
            return None

        if profiles:
            eligible = self.select_eligible_profiles(profiles, min_credits=threshold)
            if eligible:
                return eligible[0]
        return None

    def commit(
        self,
        profile_id: str,
        cost: int = 7,
        reason: str = "video",
    ) -> int:
        """Commit credit deduction upon successful clip generation."""
        return self.deduct_credits(profile_id, amount=cost, reason=reason)

    def rollback(
        self,
        profile_id: str,
        cost: int = 10,
    ) -> None:
        """Release reservation or handle rollback on failure."""
        logger.debug("Rollback called for profile %s with cost %d", profile_id, cost)

    def touch_used(self, profile_id: str) -> None:
        """Update last_used_at timestamp without modifying credit balance, clearing expired cooldown."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            if profile_id in profiles:
                entry = profiles[profile_id]
                now = time.time()
                entry["last_used_at"] = now
                if float(entry.get("cooldown_until") or 0.0) <= now:
                    entry["cooldown_until"] = 0.0
                    entry["cooldown_reason"] = None

    def mark_cooldown(
        self,
        profile_id: str,
        seconds: float = 900.0,
        reason: str = "rate_limit",
    ) -> None:
        """Mark profile in cooldown until timestamp to avoid reuse on rate limits or errors."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            entry = profiles.setdefault(
                profile_id,
                {
                    "credits_remaining": 1000,
                    "subscription_credits": 1000,
                    "expiry_epoch": None,
                    "paygate_tier": 0,
                    "status": "active",
                    "exhausted_reason": None,
                    "last_used_at": 0.0,
                    "last_synced_at": time.time(),
                    "tier_role": compute_tier_role(1000, "active"),
                    "cooldown_until": 0.0,
                    "cooldown_reason": None,
                },
            )
            entry["cooldown_until"] = time.time() + max(0.0, float(seconds))
            entry["cooldown_reason"] = str(reason)[:200]
            logger.warning(
                "Profile %s marked in cooldown for %.1fs (until %s): %s",
                profile_id,
                seconds,
                entry["cooldown_until"],
                entry["cooldown_reason"],
            )

    def clear_cooldown(self, profile_id: str) -> None:
        """Clear active cooldown for profile."""
        with self._locked_store() as data:
            profiles = data.get("profiles", {})
            if profile_id in profiles:
                entry = profiles[profile_id]
                entry["cooldown_until"] = 0.0
                entry["cooldown_reason"] = None

    def is_on_cooldown(self, profile_id: str) -> bool:
        """Check if profile is currently on cooldown."""
        with self._locked_store() as data:
            entry = data.get("profiles", {}).get(profile_id, {})
            return float(entry.get("cooldown_until") or 0.0) > time.time()

    def mark_exhausted(
        self,
        profile_id: str,
        expiry_epoch: int | None = None,
        reason: str = "quota_exceeded",
    ) -> None:
        """Mark profile as exhausted until reset or quota renewal."""
        with self._locked_store() as data:
            profiles = data.setdefault("profiles", {})
            entry = profiles.setdefault(
                profile_id,
                {
                    "subscription_credits": 1000,
                    "last_used_at": 0.0,
                    "last_synced_at": time.time(),
                },
            )
            entry["credits_remaining"] = 0
            entry["status"] = "exhausted"
            entry["exhausted_reason"] = reason
            entry["expiry_epoch"] = expiry_epoch
            entry["tier_role"] = compute_tier_role(0, "exhausted")
            logger.warning("Profile %s marked exhausted: %s (expiry: %s)", profile_id, reason, expiry_epoch)

    def get_pool_summary(
        self,
        profiles: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Return smart 2-tier credit summary across all or specified profiles."""
        with self._locked_store() as data:
            store_profiles = data.get("profiles", {})
            now = time.time()

            if profiles is not None:
                eval_list: list[tuple[str, dict[str, Any] | None]] = []
                for p in profiles:
                    pid = p.get("id") or p.get("name") if isinstance(p, dict) else str(p)
                    if pid:
                        eval_list.append((pid, store_profiles.get(pid)))
            else:
                eval_list = [(pid, store_profiles.get(pid)) for pid in store_profiles.keys()]

            total_profiles = len(eval_list)
            video_ready_count = 0
            image_only_zero_credit_count = 0
            total_available_credits = 0

            for _pid, entry in eval_list:
                if entry is None:
                    credits_rem = 1000
                    status = "active"
                else:
                    expiry = entry.get("expiry_epoch")
                    if expiry is not None and now >= expiry:
                        sub_credits = entry.get("subscription_credits") or 1000
                        entry["credits_remaining"] = sub_credits
                        entry["status"] = "active"
                        entry["exhausted_reason"] = None
                        entry["expiry_epoch"] = None
                        entry["tier_role"] = compute_tier_role(sub_credits, "active")

                    credits_rem = int(entry.get("credits_remaining", 0))
                    status = str(entry.get("status", "active"))

                if status == "auth_expired":
                    continue

                total_available_credits += max(0, credits_rem)

                if credits_rem >= MIN_VIDEO_CREDITS and status != "exhausted":
                    video_ready_count += 1
                elif (0 <= credits_rem < MIN_VIDEO_CREDITS) or status == "exhausted":
                    image_only_zero_credit_count += 1

            return {
                "total_profiles": total_profiles,
                "video_ready_count": video_ready_count,
                "image_only_zero_credit_count": image_only_zero_credit_count,
                "total_available_credits": total_available_credits,
                "estimated_omni_4s_clips": total_available_credits // 7,
                "estimated_omni_6s_clips": total_available_credits // 10,
                "estimated_omni_8s_clips": total_available_credits // 12,
                "zero_credit_image_capacity": "unlimited",
            }

    def summary(self, profile_ids: list[str] | None = None) -> dict[str, Any]:
        """Return diagnostic overview of credits across fleet or target profiles."""
        with self._locked_store() as data:
            all_profiles = data.get("profiles", {})
            target_ids = profile_ids or list(all_profiles.keys())

            filtered: dict[str, Any] = {}
            total_remaining = 0
            active_count = 0
            exhausted_count = 0

            for pid in target_ids:
                entry = all_profiles.get(pid)
                if not entry:
                    continue
                if "tier_role" not in entry:
                    entry["tier_role"] = compute_tier_role(
                        int(entry.get("credits_remaining", 0)),
                        entry.get("status", "active"),
                    )
                filtered[pid] = dict(entry)
                credits_rem = int(entry.get("credits_remaining", 0))
                total_remaining += credits_rem
                if entry.get("status") == "exhausted" or credits_rem <= 0:
                    exhausted_count += 1
                else:
                    active_count += 1

            return {
                "store_path": str(self.path),
                "total_profiles": len(filtered),
                "active_profiles": active_count,
                "exhausted_profiles": exhausted_count,
                "total_credits_remaining": total_remaining,
                "profiles": filtered,
            }


_DEFAULT_LEDGER: Optional[CreditLedger] = None
_DEFAULT_LEDGER_LOCK = threading.Lock()


def get_credit_ledger(path: Path | str | None = None) -> CreditLedger:
    """Get or create singleton CreditLedger instance."""
    global _DEFAULT_LEDGER
    if path is not None:
        return CreditLedger(path=path)
    with _DEFAULT_LEDGER_LOCK:
        if _DEFAULT_LEDGER is None:
            _DEFAULT_LEDGER = CreditLedger()
        return _DEFAULT_LEDGER
