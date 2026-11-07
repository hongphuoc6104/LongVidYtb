"""Unit tests for SIM Verification & Tier-2/Tier-3 Channel Unlock Manager."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sys.tools.sim_verification_manager import (
    ALL_PHONE_NUMBERS,
    PHONE_MOBIFONE_A,
    PHONE_VIETNAMOBILE_B1,
    PHONE_VIETNAMOBILE_B2,
    PHONE_VIETTEL_A,
    RAW_SLOT_ASSIGNMENT_MATRIX,
    SMS_TIMEOUT_GROUP_B_SECONDS,
    ChannelFleetAuditor,
    CooldownActiveError,
    SimVerificationLedger,
    ZeroSimFallbackHelper,
    main,
    render_cooldown,
    render_plan,
    render_status,
)

import pytest


def test_sim_matrix_invariants():
    """Verify exact 4 phone numbers, carrier groups, and 16 total slots."""
    assert len(ALL_PHONE_NUMBERS) == 4
    assert PHONE_MOBIFONE_A == "0794999539"
    assert PHONE_VIETTEL_A == "0398658115"
    assert PHONE_VIETNAMOBILE_B1 == "0559745970"
    assert PHONE_VIETNAMOBILE_B2 == "0559238139"

    total_slots = 0
    total_sms = 0
    total_voice = 0

    for phone in ALL_PHONE_NUMBERS:
        meta = RAW_SLOT_ASSIGNMENT_MATRIX[phone]
        slots = meta["slots"]
        assert len(slots) == 4
        total_slots += len(slots)
        sms_count = sum(1 for s in slots if s["method"] == "sms")
        voice_count = sum(1 for s in slots if s["method"] == "voice_call")
        assert sms_count == 2
        assert voice_count == 2
        total_sms += sms_count
        total_voice += voice_count

    assert total_slots == 16
    assert total_sms == 8
    assert total_voice == 8


def test_carrier_reliability_and_group_b_fallback():
    """Group A should be high reliability; Group B must auto-fallback to Voice Call after 60s."""
    mobifone = RAW_SLOT_ASSIGNMENT_MATRIX[PHONE_MOBIFONE_A]
    viettel = RAW_SLOT_ASSIGNMENT_MATRIX[PHONE_VIETTEL_A]
    vm_b1 = RAW_SLOT_ASSIGNMENT_MATRIX[PHONE_VIETNAMOBILE_B1]
    vm_b2 = RAW_SLOT_ASSIGNMENT_MATRIX[PHONE_VIETNAMOBILE_B2]

    assert mobifone["group"] == "Group A"
    assert mobifone["auto_fallback_to_voice"] is False
    assert viettel["group"] == "Group A"
    assert viettel["auto_fallback_to_voice"] is False

    assert vm_b1["group"] == "Group B"
    assert vm_b1["auto_fallback_to_voice"] is True
    assert vm_b1["sms_timeout_seconds"] == SMS_TIMEOUT_GROUP_B_SECONDS == 60

    assert vm_b2["group"] == "Group B"
    assert vm_b2["auto_fallback_to_voice"] is True
    assert vm_b2["sms_timeout_seconds"] == SMS_TIMEOUT_GROUP_B_SECONDS == 60


def test_exact_slot_assignments():
    """Check exact channel assignments for each of the 4 SIMs."""
    ledger = SimVerificationLedger()

    # MobiFone 0794999539
    card1 = ledger.sims[PHONE_MOBIFONE_A]
    assert card1.slots[0].assigned_channel == "en_macro_gears"
    assert card1.slots[0].profile_id == "profile_en07"
    assert card1.slots[1].assigned_channel == "en_inside_vessel"
    assert card1.slots[1].profile_id == "profile_en11"
    assert card1.slots[2].assigned_channel == "en_root_and_canopy"
    assert card1.slots[2].method == "voice_call"
    assert card1.slots[3].assigned_channel == "ban_do_quyen_luc"
    assert card1.slots[3].method == "voice_call"

    # Viettel 0398658115
    card2 = ledger.sims[PHONE_VIETTEL_A]
    assert card2.slots[0].assigned_channel == "en_cold_case_ink"
    assert card2.slots[0].profile_id == "profile_en14"
    assert card2.slots[1].assigned_channel == "en_fine_print"
    assert card2.slots[1].profile_id == "profile_en10"
    assert card2.slots[2].assigned_channel == "en_choke_point"
    assert card2.slots[2].method == "voice_call"
    assert card2.slots[3].assigned_channel == "en_first_principles"
    assert card2.slots[3].method == "voice_call"

    # Vietnamobile 0559745970
    card3 = ledger.sims[PHONE_VIETNAMOBILE_B1]
    assert card3.slots[0].assigned_channel == "en_lazy_brain"
    assert card3.slots[0].profile_id == "profile_en01"
    assert card3.slots[1].assigned_channel == "en_wallet_anatomy"
    assert card3.slots[1].profile_id == "profile_en06"
    assert card3.slots[2].assigned_channel == "en_scale_and_bone"
    assert card3.slots[2].method == "voice_call"
    assert card3.slots[3].assigned_channel == "en_pocket_cosmos"
    assert card3.slots[3].method == "voice_call"

    # Vietnamobile 0559238139
    card4 = ledger.sims[PHONE_VIETNAMOBILE_B2]
    assert card4.slots[0].assigned_channel == "en_second_arrow"
    assert card4.slots[0].profile_id == "profile_en17"
    assert card4.slots[1].assigned_channel == "en_career_leverage"
    assert card4.slots[1].profile_id == "profile_en09"
    # Dynamic reserves
    assert card4.slots[2].is_dynamic_reserve is True
    assert card4.slots[2].candidate_channels == ["tui_tien", "la_ban_hoc_thuat", "luat_doi_thuong"]
    assert card4.slots[2].threshold_views == 500
    assert card4.slots[3].is_dynamic_reserve is True
    assert card4.slots[3].candidate_channels == ["en_crowd_strings", "en_bamboo_marble", "en_spawn_to_apex"]
    assert card4.slots[3].threshold_views == 200


def test_cooldown_enforcement(tmp_path: Path):
    """Ensure mandatory >= 20 min cooldown is strictly enforced per phone number."""
    test_ledger_file = tmp_path / "test_ledger.json"
    ledger = SimVerificationLedger(test_ledger_file)

    phone = PHONE_MOBIFONE_A
    assert not ledger.check_cooldown(phone)[0]

    t0 = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)
    slot = ledger.record_verification(
        phone=phone,
        slot_id=1,
        channel_id="en_macro_gears",
        method="sms",
        status="VERIFIED",
        now=t0,
    )
    assert slot.status == "VERIFIED"
    assert slot.verified_at == t0.isoformat()

    # Immediate next attempt at t0 + 5 minutes should fail with CooldownActiveError
    t_5m = t0 + timedelta(minutes=5)
    is_cooling, remaining = ledger.check_cooldown(phone, now=t_5m)
    assert is_cooling is True
    assert remaining == pytest.approx(15 * 60, rel=1e-2)

    with pytest.raises(CooldownActiveError) as exc_info:
        ledger.record_verification(
            phone=phone,
            slot_id=2,
            channel_id="en_inside_vessel",
            now=t_5m,
        )
    assert "is cooling down" in str(exc_info.value)
    assert "20m cooldown" in str(exc_info.value)

    # Force flag allows emergency override
    forced_slot = ledger.record_verification(
        phone=phone,
        slot_id=2,
        channel_id="en_inside_vessel",
        force=True,
        now=t_5m,
    )
    assert forced_slot.status == "VERIFIED"

    # At t0 + 21 minutes, cooldown has expired naturally
    t_21m = t0 + timedelta(minutes=21)
    is_cooling_21, remaining_21 = ledger.check_cooldown(phone, now=t_21m)
    # Note: because t_5m reset last_verification_at, let's test relative to t_5m + 21m
    t_post = t_5m + timedelta(minutes=21)
    is_cooling_post, remaining_post = ledger.check_cooldown(phone, now=t_post)
    assert is_cooling_post is False
    assert remaining_post == 0.0

    # Another verification now succeeds without force
    slot3 = ledger.record_verification(
        phone=phone,
        slot_id=3,
        channel_id="en_root_and_canopy",
        now=t_post,
    )
    assert slot3.status == "VERIFIED"


def test_dynamic_reserve_allocation(tmp_path: Path):
    """Test dynamic allocation triggers for VN Pivot (>500 views) and EN Secondary (>200 views)."""
    test_ledger_file = tmp_path / "test_ledger.json"
    ledger = SimVerificationLedger(test_ledger_file)

    # Case 1: Views below threshold
    low_metrics = {
        "tui_tien": 450,
        "la_ban_hoc_thuat": 120,
        "luat_doi_thuong": 300,
        "en_crowd_strings": 150,
        "en_bamboo_marble": 80,
        "en_spawn_to_apex": 190,
    }
    res1 = ledger.allocate_dynamic_reserves(metrics_source=low_metrics)
    assert res1["slot_3"]["allocated"] is False
    assert res1["slot_3"]["leader"] == "tui_tien"
    assert res1["slot_3"]["views"] == 450
    assert res1["slot_4"]["allocated"] is False
    assert res1["slot_4"]["leader"] == "en_spawn_to_apex"
    assert res1["slot_4"]["views"] == 190

    slot3 = ledger.sims[PHONE_VIETNAMOBILE_B2].slots[2]
    slot4 = ledger.sims[PHONE_VIETNAMOBILE_B2].slots[3]
    assert slot3.status == "RESERVED"
    assert slot4.status == "RESERVED"

    # Case 2: la_ban_hoc_thuat hits 550 (>500) and en_bamboo_marble hits 210 (>200)
    high_metrics = {
        "tui_tien": 450,
        "la_ban_hoc_thuat": 550,
        "luat_doi_thuong": 300,
        "en_crowd_strings": 150,
        "en_bamboo_marble": 210,
        "en_spawn_to_apex": 190,
    }
    res2 = ledger.allocate_dynamic_reserves(metrics_source=high_metrics)
    assert res2["slot_3"]["allocated"] is True
    assert res2["slot_3"]["channel"] == "la_ban_hoc_thuat"
    assert res2["slot_3"]["views"] == 550

    assert res2["slot_4"]["allocated"] is True
    assert res2["slot_4"]["channel"] == "en_bamboo_marble"
    assert res2["slot_4"]["views"] == 210

    assert slot3.status == "ASSIGNED"
    assert slot3.assigned_channel == "la_ban_hoc_thuat"
    assert slot4.status == "ASSIGNED"
    assert slot4.assigned_channel == "en_bamboo_marble"


def test_zero_sim_fallback_helper():
    """Verify Step 3 fallback configuration, selectors, and scripts."""
    config = ZeroSimFallbackHelper.get_fallback_config("en_deep_time_strata")
    assert config["channel_id"] == "en_deep_time_strata"
    assert config["strategy"] == "ZERO_SIM_STEP3_FALLBACK"

    t2 = config["tier2_fallback"]
    assert t2["mode"] == "in_video_auto_frame_thumbnail"
    assert t2["frame_index"] == 1
    assert "ytcp-video-thumbnail-editor" in t2["selector_cdp"]
    assert "selected_index: 1" in t2["selector_cdp"]

    t3 = config["tier3_fallback"]
    assert t3["mode"] == "build_channel_history"
    assert "advanced-features" in t3["selector_cdp"]
    assert "Build channel history" in t3["option_name"]


def test_fleet_auditor_live_data():
    """Audit actual repo channel map and publish report."""
    auditor = ChannelFleetAuditor()
    ledger = SimVerificationLedger()
    results = auditor.audit_fleet(ledger)

    assert len(results) >= 38  # 42 in channel map

    # 20 VN channels + 4 EN channels should have both Tier 2 and Tier 3 unlocked
    unlocked = [r for r in results if r.tier2_unlocked and r.tier3_unlocked]
    assert len(unlocked) == 24

    # Verify en_root_and_canopy is correctly flagged with Verify Its You gate
    reauth = next((r for r in results if r.channel_id == "en_root_and_canopy"), None)
    assert reauth is not None
    assert reauth.hit_verify_its_you_gate is True
    assert reauth.classification == "BLOCKED_REAUTH_VERIFY_ITS_YOU"

    # Verify en_macro_gears has both Tier 2 & Tier 3 unlocked
    macro = next((r for r in results if r.channel_id == "en_macro_gears"), None)
    assert macro is not None
    assert macro.tier2_unlocked is True
    assert macro.tier3_unlocked is True
    assert macro.assigned_sim_phone == PHONE_MOBIFONE_A
    assert macro.assigned_sim_slot == 1


def test_cli_renderers(tmp_path: Path):
    """Test string renderers for CLI output."""
    ledger = SimVerificationLedger(tmp_path / "ledger.json")
    auditor = ChannelFleetAuditor()
    audit_results = auditor.audit_fleet(ledger)

    plan_str = render_plan(ledger)
    assert "4-SIM VERIFICATION & TIER-2/TIER-3 CHANNEL UNLOCK PLAN" in plan_str
    assert "0794999539" in plan_str
    assert "0398658115" in plan_str
    assert "0559745970" in plan_str
    assert "0559238139" in plan_str

    status_str = render_status(ledger, audit_results)
    assert "FLEET TIER-2/TIER-3 UNLOCK AUDIT" in status_str
    assert "Total Fleet Channels: 42" in status_str

    cooldown_str = render_cooldown(ledger)
    assert "SIM COOLDOWN STATUS" in cooldown_str
    assert "READY FOR NEXT VERIFICATION" in cooldown_str


def test_cli_execution_flags(monkeypatch, tmp_path: Path, capsys):
    """Test CLI commands execution via main()."""
    test_ledger = tmp_path / "cli_ledger.json"

    # 1. --plan
    monkeypatch.setattr("sys.argv", ["sim_verification_manager.py", "--plan", "--ledger-path", str(test_ledger)])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "4-SIM VERIFICATION & TIER-2/TIER-3 CHANNEL UNLOCK PLAN" in captured.out

    # 2. --cooldown-check
    monkeypatch.setattr("sys.argv", ["sim_verification_manager.py", "--cooldown-check", "--ledger-path", str(test_ledger)])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "SIM COOLDOWN STATUS" in captured.out

    # 3. --fallback-config
    monkeypatch.setattr("sys.argv", ["sim_verification_manager.py", "--fallback-config", "en_kindred_sketch", "--ledger-path", str(test_ledger)])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "STEP 3 ZERO-SIM FALLBACK CONFIGURATION FOR: en_kindred_sketch" in captured.out

    # 4. --status --json
    monkeypatch.setattr("sys.argv", ["sim_verification_manager.py", "--status", "--json", "--ledger-path", str(test_ledger)])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert any(c["channel_id"] == "ai_binh_dan" for c in data)
