"""Unit tests for Flow CDP Credit & Quota Ledger and DynamicProfilePool integration."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest
from flow_cdp.credit_ledger import (
    MIN_VIDEO_CREDITS,
    TIER_ROLE_AUTH_EXPIRED,
    TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT,
    TIER_ROLE_VIDEO_AND_IMAGE,
    CreditLedger,
    compute_tier_role,
    get_credit_ledger,
)
from flow_cdp.persistent_pool import DynamicProfilePool


@pytest.fixture
def tmp_ledger_path(tmp_path: Path) -> Path:
    """Provide isolated path for credit ledger store."""
    return tmp_path / "test_credits.json"


@pytest.fixture
def ledger(tmp_ledger_path: Path) -> CreditLedger:
    """Create isolated CreditLedger instance."""
    return CreditLedger(path=tmp_ledger_path)


def test_register_profile_new_and_idempotent(ledger: CreditLedger) -> None:
    """Verify profile registration initializes default schema and is idempotent."""
    entry = ledger.register_profile("profile_1", initial_credits=1000)
    assert entry["credits_remaining"] == 1000
    assert entry["subscription_credits"] == 1000
    assert entry["status"] == "active"
    assert entry["expiry_epoch"] is None
    assert entry["last_synced_at"] > 0

    # Idempotent call does not overwrite modified balance
    ledger.deduct_credits("profile_1", amount=100)
    second_call = ledger.register_profile("profile_1", initial_credits=1000)
    assert second_call["credits_remaining"] == 900
    assert second_call["status"] == "active"


def test_sync_balance_active_and_exhausted(ledger: CreditLedger) -> None:
    """Verify live balance sync marks profile active or exhausted according to balance."""
    # Active sync
    res_active = ledger.sync_balance(
        profile_id="profile_active",
        remaining=750,
        subscription_credits=1000,
        expiry_epoch=1893456000,
        paygate_tier=1,
    )
    assert res_active["credits_remaining"] == 750
    assert res_active["subscription_credits"] == 1000
    assert res_active["status"] == "active"
    assert res_active["exhausted_reason"] is None
    assert res_active["paygate_tier"] == 1
    assert res_active["expiry_epoch"] == 1893456000

    # Exhausted sync when remaining is 0
    res_exhausted = ledger.sync_balance(
        profile_id="profile_zero",
        remaining=0,
        subscription_credits=1000,
    )
    assert res_exhausted["credits_remaining"] == 0
    assert res_exhausted["status"] == "exhausted"
    assert res_exhausted["exhausted_reason"] == "quota_exceeded"


def test_get_balance_unregistered_and_existing(ledger: CreditLedger) -> None:
    """Verify get_balance registers unknown profile with default credits and returns balance."""
    bal_new = ledger.get_balance("profile_unknown", default_credits=500)
    assert bal_new == 500

    bal_existing = ledger.get_balance("profile_unknown")
    assert bal_existing == 500


def test_get_balance_auto_resets_on_expired_subscription(ledger: CreditLedger) -> None:
    """Verify automatic quota reset when expiry_epoch is in the past."""
    # Setup profile with past expiry epoch and 0 credits
    past_epoch = int(time.time()) - 3600
    ledger.register_profile("profile_expired", initial_credits=1000)
    ledger.mark_exhausted("profile_expired", expiry_epoch=past_epoch, reason="quota_exceeded")

    assert ledger.is_eligible("profile_expired", min_credits=10) is True  # triggers auto-reset
    bal_after = ledger.get_balance("profile_expired")
    assert bal_after == 1000

    summary_entry = ledger.summary(["profile_expired"])["profiles"]["profile_expired"]
    assert summary_entry["status"] == "active"
    assert summary_entry["exhausted_reason"] is None
    assert summary_entry["expiry_epoch"] is None


def test_get_balance_does_not_reset_when_expiry_in_future(ledger: CreditLedger) -> None:
    """Verify quota is not reset when expiry_epoch is in the future."""
    future_epoch = int(time.time()) + 3600
    ledger.register_profile("profile_future", initial_credits=1000)
    ledger.mark_exhausted("profile_future", expiry_epoch=future_epoch, reason="rate_limited")

    assert ledger.is_eligible("profile_future", min_credits=10) is False
    bal = ledger.get_balance("profile_future")
    assert bal == 0


def test_deduct_credits_normal_and_exhaustion(ledger: CreditLedger) -> None:
    """Verify credit deduction decrements balance and transitions to exhausted at 0."""
    ledger.register_profile("profile_deduct", initial_credits=30)

    # First deduction: 30 - 20 = 10
    rem1 = ledger.deduct_credits("profile_deduct", amount=20, reason="video_generation")
    assert rem1 == 10
    assert ledger.is_eligible("profile_deduct", min_credits=10) is True

    # Second deduction: 10 - 20 = 0 (bounded at 0)
    rem2 = ledger.deduct_credits("profile_deduct", amount=20, reason="video_generation")
    assert rem2 == 0
    assert ledger.is_eligible("profile_deduct", min_credits=10) is False

    summary_entry = ledger.summary(["profile_deduct"])["profiles"]["profile_deduct"]
    assert summary_entry["status"] == "exhausted"
    assert summary_entry["exhausted_reason"] == "video_generation"
    assert summary_entry["last_used_at"] > 0


def test_mark_exhausted(ledger: CreditLedger) -> None:
    """Verify mark_exhausted zeroes credits and sets reason and expiry."""
    ledger.register_profile("profile_mark", initial_credits=500)
    expiry = int(time.time()) + 7200
    ledger.mark_exhausted("profile_mark", expiry_epoch=expiry, reason="unusual_activity")

    assert ledger.get_balance("profile_mark") == 0
    assert ledger.is_eligible("profile_mark", min_credits=1) is False

    entry = ledger.summary(["profile_mark"])["profiles"]["profile_mark"]
    assert entry["status"] == "exhausted"
    assert entry["exhausted_reason"] == "unusual_activity"
    assert entry["expiry_epoch"] == expiry


def test_is_eligible_criteria(ledger: CreditLedger) -> None:
    """Verify is_eligible checks both balance threshold and exhausted status."""
    ledger.register_profile("p_ok", initial_credits=50)
    ledger.register_profile("p_low", initial_credits=5)
    ledger.register_profile("p_exh", initial_credits=50)
    ledger.mark_exhausted("p_exh", reason="manual")

    assert ledger.is_eligible("p_ok", min_credits=10) is True
    assert ledger.is_eligible("p_low", min_credits=10) is False
    assert ledger.is_eligible("p_exh", min_credits=10) is False


def test_select_eligible_profiles_filtering_and_sorting(ledger: CreditLedger) -> None:
    """Verify select_eligible_profiles sorts by highest balance and LRU tie-breaker."""
    # Setup 4 profiles
    ledger.register_profile("prof_a", initial_credits=800)
    ledger.register_profile("prof_b", initial_credits=400)
    ledger.register_profile("prof_c", initial_credits=800)
    ledger.register_profile("prof_d", initial_credits=5)  # below 10

    # Adjust last_used_at for tie breaking between prof_a and prof_c
    ledger.deduct_credits("prof_a", amount=10)  # last_used_at = now
    time.sleep(0.01)
    ledger.deduct_credits("prof_c", amount=10)  # last_used_at is newer than prof_a

    profiles_input = [
        {"id": "prof_d", "port": 9225},
        {"id": "prof_b", "port": 9223},
        {"id": "prof_c", "port": 9224},
        {"id": "prof_a", "port": 9222},
        {"id": "", "port": 9999},  # invalid empty id
    ]

    selected = ledger.select_eligible_profiles(profiles_input, min_credits=10)
    selected_ids = [p["id"] for p in selected]

    # prof_d is excluded because balance 5 < 10
    assert "prof_d" not in selected_ids
    # prof_a and prof_c have remaining 790, prof_b has 400
    # prof_a was used earlier than prof_c, so prof_a should precede prof_c in LRU
    assert selected_ids == ["prof_a", "prof_c", "prof_b"]


def test_summary_all_and_filtered(ledger: CreditLedger) -> None:
    """Verify summary returns diagnostics across entire fleet or filtered list."""
    ledger.register_profile("p1", initial_credits=100)
    ledger.register_profile("p2", initial_credits=0)
    ledger.mark_exhausted("p2", reason="empty")

    sum_all = ledger.summary()
    assert sum_all["total_profiles"] == 2
    assert sum_all["active_profiles"] == 1
    assert sum_all["exhausted_profiles"] == 1
    assert sum_all["total_credits_remaining"] == 100
    assert "p1" in sum_all["profiles"]
    assert "p2" in sum_all["profiles"]

    sum_filtered = ledger.summary(["p1"])
    assert sum_filtered["total_profiles"] == 1
    assert sum_filtered["active_profiles"] == 1
    assert sum_filtered["total_credits_remaining"] == 100
    assert "p2" not in sum_filtered["profiles"]


def test_get_credit_ledger_singleton_and_custom(tmp_path: Path) -> None:
    """Verify get_credit_ledger creates custom path instance or singleton."""
    custom_file = tmp_path / "custom_credits.json"
    inst1 = get_credit_ledger(custom_file)
    inst2 = get_credit_ledger(custom_file)
    assert inst1.path == custom_file.resolve()
    assert inst2.path == custom_file.resolve()


def test_ledger_corrupted_file_recovery(tmp_ledger_path: Path) -> None:
    """Verify corrupted JSON file on disk is safely re-initialized."""
    tmp_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_ledger_path.write_text("NOT_VALID_JSON{{{", encoding="utf-8")

    ledger = CreditLedger(path=tmp_ledger_path)
    bal = ledger.get_balance("recovery_prof", default_credits=1000)
    assert bal == 1000

    content = json.loads(tmp_ledger_path.read_text(encoding="utf-8"))
    assert "profiles" in content
    assert "recovery_prof" in content["profiles"]


def test_dynamic_profile_pool_skips_exhausted_profiles(ledger: CreditLedger) -> None:
    """Verify DynamicProfilePool with min_credits_required skips exhausted profiles."""
    profiles: list[dict[str, Any]] = [
        {"name": "profile_rich", "port": 9222},
        {"name": "profile_poor", "port": 9223},
        {"name": "profile_exhausted", "port": 9224},
    ]

    ledger.register_profile("profile_rich", initial_credits=500)
    ledger.register_profile("profile_poor", initial_credits=5)  # < 10
    ledger.register_profile("profile_exhausted", initial_credits=100)
    ledger.mark_exhausted("profile_exhausted", reason="quota_exceeded")

    pool = DynamicProfilePool(
        profiles=profiles,
        cooldown_seconds=60.0,
        enforce_os_locks=False,
        min_credits_required=10,
        credit_ledger=ledger,
    )

    # First acquisition should choose profile_rich (the only eligible one)
    acquired = pool.acquire()
    assert acquired is not None
    assert acquired["name"] == "profile_rich"

    # Next acquisition has no more eligible profiles (poor < 10, exhausted is exhausted, rich in use)
    assert pool.acquire() is None

    # Requesting poor or exhausted specifically should fail
    assert pool.acquire(required_name="profile_poor") is None
    assert pool.acquire(required_name="profile_exhausted") is None

    # Release profile_rich and re-acquire
    pool.release(acquired)
    re_acquired = pool.acquire(required_name="profile_rich")
    assert re_acquired is not None
    assert re_acquired["name"] == "profile_rich"


def test_pick_and_reserve_commit_rollback(tmp_path: Path) -> None:
    """Verify pick_and_reserve, commit, and rollback methods on CreditLedger."""
    ledger = CreditLedger(path=tmp_path / "reserve_credits.json")
    ledger.sync_balance("p_rich", 100)
    ledger.sync_balance("p_poor", 5)

    profiles = [
        {"name": "p_poor", "cdp_port": 9222},
        {"name": "p_rich", "cdp_port": 9223},
    ]

    # Reserve with cost=10 should pick p_rich (p_poor only has 5)
    chosen = ledger.pick_and_reserve(profiles=profiles, cost=10)
    assert chosen is not None
    assert chosen["name"] == "p_rich"

    # Specific profile reservation check
    assert ledger.pick_and_reserve(profile_id="p_poor", cost=10) is None
    assert ledger.pick_and_reserve(profile_id="p_poor", cost=5) == "p_poor"
    assert ledger.pick_and_reserve(profile_id="p_rich", cost=10) == "p_rich"

    # Rollback does not alter balance
    ledger.rollback("p_rich", cost=10)
    assert ledger.get_balance("p_rich") == 100

    # Commit deducts credits
    new_bal = ledger.commit("p_rich", cost=12, reason="video")
    assert new_bal == 88
    assert ledger.get_balance("p_rich") == 88


def test_compute_tier_role_logic() -> None:
    """Verify tier role classification based on credit thresholds and account status."""
    assert MIN_VIDEO_CREDITS == 7
    # >= 7 credits -> video_and_image
    assert compute_tier_role(1000, "active") == TIER_ROLE_VIDEO_AND_IMAGE
    assert compute_tier_role(7, "active") == TIER_ROLE_VIDEO_AND_IMAGE
    # 0 <= credits < 7 -> image_only_zero_credit
    assert compute_tier_role(6, "active") == TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT
    assert compute_tier_role(0, "active") == TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT
    assert compute_tier_role(0, "exhausted") == TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT
    # auth_expired -> auth_expired
    assert compute_tier_role(1000, "auth_expired") == TIER_ROLE_AUTH_EXPIRED
    assert compute_tier_role(0, "auth_expired") == TIER_ROLE_AUTH_EXPIRED


def test_pick_for_image_task_prioritizes_zero_and_low_credits(ledger: CreditLedger) -> None:
    """Verify pick_for_image_task selects 0-credit/low-credit accounts before high-credit accounts."""
    ledger.set_credits("p_1000", 1000)
    ledger.set_credits("p_50", 50)
    ledger.set_credits("p_3", 3)
    ledger.set_credits("p_0_recent", 0)
    ledger.set_credits("p_0_old", 0)
    ledger.set_credits("p_expired", 0, status="auth_expired")

    # Set last_used_at timestamps: p_0_old used earlier than p_0_recent
    ledger.touch_used("p_0_recent")
    # p_0_old last_used_at remains 0.0 (older)

    profiles = [
        {"id": "p_1000", "port": 9222},
        {"id": "p_50", "port": 9223},
        {"id": "p_3", "port": 9224},
        {"id": "p_0_recent", "port": 9225},
        {"id": "p_0_old", "port": 9226},
        {"id": "p_expired", "port": 9227},
    ]

    # 1. Should pick 0-credit account with oldest last_used_at (p_0_old)
    picked_1 = ledger.pick_for_image_task(profiles)
    assert picked_1 is not None
    assert picked_1["id"] == "p_0_old"

    # 2. When p_0_old is absent, picks next 0-credit account (p_0_recent)
    profiles_no_p0_old = [p for p in profiles if p["id"] != "p_0_old"]
    picked_2 = ledger.pick_for_image_task(profiles_no_p0_old)
    assert picked_2 is not None
    assert picked_2["id"] == "p_0_recent"

    # 3. When 0-credit accounts are absent, picks lowest credit account (p_3 with 3 credits < 7)
    profiles_no_zeros = [p for p in profiles if p["id"] not in ("p_0_old", "p_0_recent")]
    picked_3 = ledger.pick_for_image_task(profiles_no_zeros)
    assert picked_3 is not None
    assert picked_3["id"] == "p_3"

    # 4. Fallback to video_and_image accounts: picks p_50 (50 credits) over p_1000 (1000 credits)
    # to preserve 1,000-credit accounts for video clips!
    profiles_video_only = [{"id": "p_1000", "port": 9222}, {"id": "p_50", "port": 9223}]
    picked_4 = ledger.pick_for_image_task(profiles_video_only)
    assert picked_4 is not None
    assert picked_4["id"] == "p_50"

    # 5. Skips auth_expired account
    profiles_expired = [{"id": "p_expired", "port": 9227}]
    assert ledger.pick_for_image_task(profiles_expired) is None


def test_pick_for_video_task_requires_sufficient_credits_and_skips_low_credits(ledger: CreditLedger) -> None:
    """Verify pick_for_video_task selects >= cost accounts and skips < 7 credit accounts."""
    ledger.set_credits("p_0", 0)
    ledger.set_credits("p_5", 5)
    ledger.set_credits("p_7", 7)
    ledger.set_credits("p_100", 100)
    ledger.set_credits("p_1000", 1000)
    ledger.set_credits("p_auth_exp", 500, status="auth_expired")

    profiles = [
        {"id": "p_0", "port": 9222},
        {"id": "p_5", "port": 9223},
        {"id": "p_7", "port": 9224},
        {"id": "p_100", "port": 9225},
        {"id": "p_1000", "port": 9226},
        {"id": "p_auth_exp", "port": 9227},
    ]

    # For 7-credit clip (Omni 1.1 Flash 4s):
    # Should pick p_1000 (highest available credits)
    picked_omni4s = ledger.pick_for_video_task(profiles, cost=7, min_credits=7)
    assert picked_omni4s is not None
    assert picked_omni4s["id"] == "p_1000"

    # When p_1000 is excluded, should pick p_100
    profiles_no_1000 = [p for p in profiles if p["id"] != "p_1000"]
    picked_omni4s_sub = ledger.pick_for_video_task(profiles_no_1000, cost=7, min_credits=7)
    assert picked_omni4s_sub is not None
    assert picked_omni4s_sub["id"] == "p_100"

    # When only p_7, p_5, p_0 remain:
    profiles_low = [p for p in profiles if p["id"] in ("p_7", "p_5", "p_0")]
    picked_p7 = ledger.pick_for_video_task(profiles_low, cost=7, min_credits=7)
    assert picked_p7 is not None
    assert picked_p7["id"] == "p_7"

    # For 10-credit clip (Omni 1.1 Flash 6s), p_7 (7 credits < 10) is skipped
    picked_omni6s = ledger.pick_for_video_task(profiles_low, cost=10, min_credits=7)
    assert picked_omni6s is None

    # When all profiles have < 7 credits, returns None
    profiles_sub7 = [{"id": "p_5", "port": 9223}, {"id": "p_0", "port": 9222}]
    assert ledger.pick_for_video_task(profiles_sub7, cost=7, min_credits=7) is None


def test_tier_role_auto_transition_on_commit(ledger: CreditLedger) -> None:
    """Verify transition from video_and_image to image_only_zero_credit when credits drop 10 -> 3."""
    # 1. Initialize account with 10 credits
    entry = ledger.set_credits("prof_transition", 10)
    assert entry["credits_remaining"] == 10
    assert entry["status"] == "active"
    assert entry["tier_role"] == TIER_ROLE_VIDEO_AND_IMAGE

    # 2. Commit a 7-credit Omni 1.1 Flash 4s clip: 10 - 7 = 3 credits
    new_bal = ledger.commit("prof_transition", cost=7, reason="omni_1.1_flash_4s")
    assert new_bal == 3

    # Check that tier_role automatically transitioned to image_only_zero_credit
    summary_entry = ledger.summary(["prof_transition"])["profiles"]["prof_transition"]
    assert summary_entry["credits_remaining"] == 3
    assert summary_entry["status"] == "active"
    assert summary_entry["tier_role"] == TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT

    # Profile cannot be picked for 7-credit video clip anymore
    assert ledger.pick_for_video_task([{"id": "prof_transition"}], cost=7, min_credits=7) is None

    # But profile is still immediately active and eligible for zero-credit image tasks!
    image_pick = ledger.pick_for_image_task([{"id": "prof_transition"}])
    assert image_pick is not None
    assert image_pick["id"] == "prof_transition"

    # 3. Deduct remaining 3 credits to 0: status becomes exhausted, tier_role remains image_only_zero_credit
    bal_zero = ledger.commit("prof_transition", cost=3, reason="final_spend")
    assert bal_zero == 0
    zero_entry = ledger.summary(["prof_transition"])["profiles"]["prof_transition"]
    assert zero_entry["status"] == "exhausted"
    assert zero_entry["tier_role"] == TIER_ROLE_IMAGE_ONLY_ZERO_CREDIT

    # 4. Top-up / reset back to 100 credits: automatically transitions back to video_and_image
    topup_entry = ledger.set_credits("prof_transition", 100)
    assert topup_entry["status"] == "active"
    assert topup_entry["tier_role"] == TIER_ROLE_VIDEO_AND_IMAGE


def test_get_pool_summary_accuracy(ledger: CreditLedger) -> None:
    """Verify get_pool_summary metrics, clip estimates, and unlimited zero-credit capacity."""
    # Setup fleet:
    # 3 video_and_image profiles (>= 7 credits): 1000 + 50 + 7 = 1057 credits
    # 3 image_only_zero_credit profiles (< 7 credits): 6 + 0 + 0 = 6 credits
    # Total available: 1063 credits
    ledger.set_credits("p_v1", 1000)
    ledger.set_credits("p_v2", 50)
    ledger.set_credits("p_v3", 7)
    ledger.set_credits("p_z1", 6)
    ledger.set_credits("p_z2", 0)
    ledger.set_credits("p_z3", 0, status="exhausted")

    summary = ledger.get_pool_summary()

    assert summary["total_profiles"] == 6
    assert summary["video_ready_count"] == 3
    assert summary["image_only_zero_credit_count"] == 3
    assert summary["total_available_credits"] == 1063

    # Video clip estimates
    assert summary["estimated_omni_4s_clips"] == 1063 // 7  # 151
    assert summary["estimated_omni_6s_clips"] == 1063 // 10  # 106
    assert summary["estimated_omni_8s_clips"] == 1063 // 12  # 88

    # Zero-credit image capacity invariant
    assert summary["zero_credit_image_capacity"] == "unlimited"

    # Test filtering to specific profiles
    sub_summary = ledger.get_pool_summary(profiles=[{"id": "p_v1"}, {"id": "p_z1"}])
    assert sub_summary["total_profiles"] == 2
    assert sub_summary["video_ready_count"] == 1
    assert sub_summary["image_only_zero_credit_count"] == 1
    assert sub_summary["total_available_credits"] == 1006
    assert sub_summary["estimated_omni_4s_clips"] == 1006 // 7
