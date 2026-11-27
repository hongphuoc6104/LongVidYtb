"""Unit tests for V12 BELUGA zero-credit specialist routing on CreditLedger."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from flow_cdp.credit_ledger import (
    CreditLedger,
    select_beluga_zero_credit_specialists,
)
from flow_cdp.resource_locks import mark_profile_unauthenticated


def _seed_profile(
    ledger: CreditLedger,
    profile_id: str,
    *,
    credits: int,
    paygate_tier: int = 0,
    last_used_at: float = 1000.0,
    status: str | None = None,
    cooldown_sec: float = 0.0,
) -> None:
    """Seed a profile entry directly with deterministic metadata for routing tests."""
    st = status if status is not None else ("active" if credits > 0 else "exhausted")
    ledger.set_credits(profile_id, credits, status=st)
    with ledger._locked_store() as data:
        entry = data["profiles"][profile_id]
        entry["paygate_tier"] = paygate_tier
        entry["last_used_at"] = last_used_at
        if cooldown_sec > 0.0:
            entry["cooldown_until"] = time.time() + cooldown_sec
        elif cooldown_sec < 0.0:
            entry["cooldown_until"] = time.time() + cooldown_sec


def test_v12_beluga_specialist_tier_ordering_matches_fleet_plan(tmp_path: Path) -> None:
    """Zero/low-credit specialists come FIRST, regular pool SECOND, paygate_tier==2 Ultra LAST."""
    credits_path = tmp_path / "credits.json"
    unauth_path = tmp_path / "unauthenticated_profiles.json"
    unauth_path.write_text(
        json.dumps({"profiles": ["profile_1", "profile_4", "profile_13", "profile_2"]}),
        encoding="utf-8",
    )

    ledger = CreditLedger(path=credits_path)

    # Tier 0: 7 authenticated low/zero-credit BELUGA specialists (0 <= credits <= 9)
    _seed_profile(ledger, "profile_5", credits=0, paygate_tier=1, last_used_at=100.0)
    _seed_profile(ledger, "profile_8", credits=0, paygate_tier=1, last_used_at=200.0, cooldown_sec=-60.0)
    _seed_profile(ledger, "profile_10", credits=0, paygate_tier=1, last_used_at=300.0)
    _seed_profile(ledger, "profile_en05", credits=2, paygate_tier=0, last_used_at=150.0)
    _seed_profile(ledger, "profile_en16", credits=4, paygate_tier=0, last_used_at=160.0)
    _seed_profile(ledger, "profile_en07", credits=6, paygate_tier=1, last_used_at=170.0)
    _seed_profile(ledger, "profile_en13", credits=6, paygate_tier=0, last_used_at=180.0)

    # Tier 1: regular pool profiles (> 9 credits, paygate_tier != 2, including tier=3)
    _seed_profile(ledger, "profile_en11", credits=11, paygate_tier=0, last_used_at=400.0)
    _seed_profile(ledger, "profile_16", credits=50, paygate_tier=3, last_used_at=410.0)
    _seed_profile(ledger, "profile_en18", credits=1544, paygate_tier=1, last_used_at=420.0)

    # Tier 2: Ultra profiles (paygate_tier == 2) — must be strictly LAST
    _seed_profile(ledger, "profile_en03", credits=24518, paygate_tier=2, last_used_at=500.0)
    _seed_profile(ledger, "profile_18", credits=24849, paygate_tier=2, last_used_at=510.0)
    _seed_profile(ledger, "profile_22", credits=25459, paygate_tier=2, last_used_at=520.0)

    # Excluded profiles:
    # - unauthenticated_profiles.json (even if 0/2c and last_used_at > 0)
    _seed_profile(ledger, "profile_1", credits=0, paygate_tier=0, last_used_at=50.0)
    _seed_profile(ledger, "profile_4", credits=0, paygate_tier=0, last_used_at=60.0)
    _seed_profile(ledger, "profile_13", credits=2, paygate_tier=0, last_used_at=70.0)
    _seed_profile(ledger, "profile_2", credits=1050, paygate_tier=1, last_used_at=80.0)
    # - last_used_at == 0.0 (unverified/never-used)
    _seed_profile(ledger, "profile_en04", credits=0, paygate_tier=0, last_used_at=0.0)
    _seed_profile(ledger, "profile_en01", credits=25050, paygate_tier=2, last_used_at=0.0, cooldown_sec=3600.0)
    # - active cooldown
    _seed_profile(ledger, "profile_en09", credits=3, paygate_tier=1, last_used_at=90.0, cooldown_sec=600.0)
    # - auth_expired
    _seed_profile(ledger, "profile_expired", credits=0, paygate_tier=0, last_used_at=95.0, status="auth_expired")

    ordered = ledger.select_beluga_zero_credit_specialists(max_credit_threshold=9)

    assert ordered == [
        # Tier 0: 0c LRU first, then 2c, 4c, 6c LRU
        "profile_5",
        "profile_8",
        "profile_10",
        "profile_en05",
        "profile_en16",
        "profile_en07",
        "profile_en13",
        # Tier 1: regular pool lowest balance first
        "profile_en11",
        "profile_16",
        "profile_en18",
        # Tier 2: Ultra (paygate_tier == 2) strictly LAST
        "profile_en03",
        "profile_18",
        "profile_22",
    ]


def test_select_beluga_respects_threshold_and_ultra_stays_last(tmp_path: Path) -> None:
    """Verify max_credit_threshold boundary and that paygate_tier==2 stays LAST even at low balance."""
    ledger = CreditLedger(path=tmp_path / "credits.json")
    _seed_profile(ledger, "p_zero", credits=0, paygate_tier=0, last_used_at=100.0)
    _seed_profile(ledger, "p_nine", credits=9, paygate_tier=1, last_used_at=100.0)
    _seed_profile(ledger, "p_ten", credits=10, paygate_tier=1, last_used_at=100.0)
    _seed_profile(ledger, "p_ultra_low", credits=5, paygate_tier=2, last_used_at=100.0)

    default_order = ledger.select_beluga_zero_credit_specialists()
    assert default_order == ["p_zero", "p_nine", "p_ten", "p_ultra_low"]

    # With threshold=0, p_nine moves to regular fallback tier (Tier 1) behind p_zero,
    # still ahead of p_ultra_low (Tier 2).
    strict_zero_order = ledger.select_beluga_zero_credit_specialists(max_credit_threshold=0)
    assert strict_zero_order == ["p_zero", "p_nine", "p_ten", "p_ultra_low"]


def test_select_beluga_respects_locks_dir_ttl_and_profiles_filter(tmp_path: Path) -> None:
    """Verify locks_dir TTL unauthenticated entries, profiles subset filtering, and convenience helper."""
    credits_path = tmp_path / "credits.json"
    locks_dir = tmp_path / "locks"
    ledger = CreditLedger(path=credits_path)

    _seed_profile(ledger, "p_spec_a", credits=0, paygate_tier=0, last_used_at=100.0)
    _seed_profile(ledger, "p_spec_b", credits=4, paygate_tier=0, last_used_at=100.0)
    _seed_profile(ledger, "p_disabled", credits=0, paygate_tier=0, last_used_at=50.0)
    _seed_profile(ledger, "p_pool", credits=100, paygate_tier=1, last_used_at=200.0)
    _seed_profile(ledger, "p_ultra", credits=25000, paygate_tier=2, last_used_at=300.0)

    # Mark p_spec_a unauthenticated with active TTL, and p_spec_b with already-expired TTL
    mark_profile_unauthenticated("p_spec_a", ttl_sec=3600.0, locks_dir=locks_dir)
    mark_profile_unauthenticated("p_spec_b", ttl_sec=-10.0, locks_dir=locks_dir)

    configured_profiles: list[dict[str, Any]] = [
        {"id": "p_ultra", "port": 9270},
        {"id": "p_pool", "port": 9230},
        {"id": "p_disabled", "port": 9228, "enabled": False},
        {"id": "p_spec_a", "port": 9226},
        {"id": "p_spec_b", "port": 9255},
        {"id": "p_unknown", "port": 9299},
    ]

    selected = select_beluga_zero_credit_specialists(
        max_credit_threshold=9,
        ledger_path=credits_path,
        profiles=configured_profiles,
        locks_dir=locks_dir,
    )
    assert selected == ["p_spec_b", "p_pool", "p_ultra"]
    # Unknown profile from input list must not be auto-created in credits store
    assert "p_unknown" not in ledger.summary()["profiles"]
