#!/usr/bin/env python3
"""SIM Verification & Tier-2/Tier-3 Channel Unlock Manager.

SSOT CLI and automation module for managing YouTube Studio phone verifications,
tier unlocking (Tier 2 Custom Thumbnail / >15m video, Tier 3 Advanced Features &
Related Video linking), cooldown enforcement across 4 physical SIM cards, and
Zero-SIM fallback automation.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sim_verification_manager")

# Invariants & SSOT Constants
MANDATORY_COOLDOWN_SECONDS: int = 20 * 60  # Mandatory >= 20 minute cooldown between verifications on the same SIM
SMS_TIMEOUT_GROUP_B_SECONDS: int = 60      # Auto-fallback to Voice Call after 60s SMS timeout for Vietnamobile/Reddi
SMS_TIMEOUT_GROUP_A_SECONDS: int = 120     # Standard timeout for MobiFone / Viettel

DEFAULT_LEDGER_PATH = Path("sys/.state/sim_verification_ledger.json")
DEFAULT_CHANNEL_MAP_PATH = Path("sys/channels/youtube_channel_map.json")
DEFAULT_PUBLISH_REPORT_PATH = Path("sys/runs/en_batch1_prod/youtube_publish_report.json")
DEFAULT_METRICS_PATH = Path("sys/channels/dashboard_metrics.json")

# 4 Phone numbers & carrier specifications
PHONE_MOBIFONE_A = "0794999539"
PHONE_VIETTEL_A = "0398658115"
PHONE_VIETNAMOBILE_B1 = "0559745970"
PHONE_VIETNAMOBILE_B2 = "0559238139"

ALL_PHONE_NUMBERS = [
    PHONE_MOBIFONE_A,
    PHONE_VIETTEL_A,
    PHONE_VIETNAMOBILE_B1,
    PHONE_VIETNAMOBILE_B2,
]

# Static Slot Matrix Specifications (4 slots per SIM: 2 SMS + 2 Voice Call = 16 total slots)
RAW_SLOT_ASSIGNMENT_MATRIX: Dict[str, Dict[str, Any]] = {
    PHONE_MOBIFONE_A: {
        "carrier": "MobiFone",
        "group": "Group A",
        "reliability": "High Reliability",
        "auto_fallback_to_voice": False,
        "sms_timeout_seconds": SMS_TIMEOUT_GROUP_A_SECONDS,
        "slots": [
            {
                "slot_id": 1,
                "method": "sms",
                "assigned_channel": "en_macro_gears",
                "profile_id": "profile_en07",
                "notes": "Slot 1 (en_macro_gears / profile_en07 or existing VN)",
            },
            {
                "slot_id": 2,
                "method": "sms",
                "assigned_channel": "en_inside_vessel",
                "profile_id": "profile_en11",
                "notes": "Slot 2 (en_inside_vessel / profile_en11)",
            },
            {
                "slot_id": 3,
                "method": "voice_call",
                "assigned_channel": "en_root_and_canopy",
                "profile_id": "profile_en12",
                "notes": "Slot 3 Voice (en_root_and_canopy / profile_en12)",
            },
            {
                "slot_id": 4,
                "method": "voice_call",
                "assigned_channel": "ban_do_quyen_luc",
                "profile_id": "profile_12",
                "notes": "Slot 4 Voice (ban_do_quyen_luc / profile_12)",
            },
        ],
    },
    PHONE_VIETTEL_A: {
        "carrier": "Viettel",
        "group": "Group A",
        "reliability": "High Reliability",
        "auto_fallback_to_voice": False,
        "sms_timeout_seconds": SMS_TIMEOUT_GROUP_A_SECONDS,
        "slots": [
            {
                "slot_id": 1,
                "method": "sms",
                "assigned_channel": "en_cold_case_ink",
                "profile_id": "profile_en14",
                "notes": "Slot 1 (en_cold_case_ink / profile_en14 or existing VN)",
            },
            {
                "slot_id": 2,
                "method": "sms",
                "assigned_channel": "en_fine_print",
                "profile_id": "profile_en10",
                "notes": "Slot 2 (en_fine_print / profile_en10)",
            },
            {
                "slot_id": 3,
                "method": "voice_call",
                "assigned_channel": "en_choke_point",
                "profile_id": "profile_en15",
                "notes": "Slot 3 Voice (en_choke_point / profile_en15)",
            },
            {
                "slot_id": 4,
                "method": "voice_call",
                "assigned_channel": "en_first_principles",
                "profile_id": "profile_en05",
                "notes": "Slot 4 Voice (en_first_principles / profile_en05)",
            },
        ],
    },
    PHONE_VIETNAMOBILE_B1: {
        "carrier": "Vietnamobile/Reddi",
        "group": "Group B",
        "reliability": "Group B (Auto-fallback to Voice Call after 60s SMS timeout)",
        "auto_fallback_to_voice": True,
        "sms_timeout_seconds": SMS_TIMEOUT_GROUP_B_SECONDS,
        "slots": [
            {
                "slot_id": 1,
                "method": "sms",
                "assigned_channel": "en_lazy_brain",
                "profile_id": "profile_en01",
                "notes": "Slot 1 (en_lazy_brain / profile_en01)",
            },
            {
                "slot_id": 2,
                "method": "sms",
                "assigned_channel": "en_wallet_anatomy",
                "profile_id": "profile_en06",
                "notes": "Slot 2 (en_wallet_anatomy / profile_en06)",
            },
            {
                "slot_id": 3,
                "method": "voice_call",
                "assigned_channel": "en_scale_and_bone",
                "profile_id": "profile_en08",
                "notes": "Slot 3 Voice (en_scale_and_bone / profile_en08)",
            },
            {
                "slot_id": 4,
                "method": "voice_call",
                "assigned_channel": "en_pocket_cosmos",
                "profile_id": "profile_en16",
                "notes": "Slot 4 Voice (en_pocket_cosmos / profile_en16)",
            },
        ],
    },
    PHONE_VIETNAMOBILE_B2: {
        "carrier": "Vietnamobile/Reddi",
        "group": "Group B",
        "reliability": "Group B (Auto-fallback to Voice Call after 60s SMS timeout)",
        "auto_fallback_to_voice": True,
        "sms_timeout_seconds": SMS_TIMEOUT_GROUP_B_SECONDS,
        "slots": [
            {
                "slot_id": 1,
                "method": "sms",
                "assigned_channel": "en_second_arrow",
                "profile_id": "profile_en17",
                "notes": "Slot 1 (en_second_arrow / profile_en17)",
            },
            {
                "slot_id": 2,
                "method": "sms",
                "assigned_channel": "en_career_leverage",
                "profile_id": "profile_en09",
                "notes": "Slot 2 (en_career_leverage / profile_en09)",
            },
            {
                "slot_id": 3,
                "method": "voice_call",
                "assigned_channel": None,
                "profile_id": None,
                "is_dynamic_reserve": True,
                "reserve_type": "VN_PIVOT_GT_500",
                "candidate_channels": ["tui_tien", "la_ban_hoc_thuat", "luat_doi_thuong"],
                "threshold_views": 500,
                "notes": "Slot 3 Voice (Dynamic Reserve #1: first VN Pivot channel tui_tien/la_ban_hoc_thuat/luat_doi_thuong hitting >500 views)",
            },
            {
                "slot_id": 4,
                "method": "voice_call",
                "assigned_channel": None,
                "profile_id": None,
                "is_dynamic_reserve": True,
                "reserve_type": "EN_SECONDARY_GT_200",
                "candidate_channels": ["en_crowd_strings", "en_bamboo_marble", "en_spawn_to_apex"],
                "threshold_views": 200,
                "notes": "Slot 4 Voice (Dynamic Reserve #2: first EN secondary channel en_crowd_strings/en_bamboo_marble/en_spawn_to_apex hitting >200 views)",
            },
        ],
    },
}


class CooldownActiveError(Exception):
    """Raised when an operation violates the mandatory 20-minute SIM cooldown."""
    pass


@dataclass
class SimSlot:
    slot_id: int
    method: str  # 'sms' or 'voice_call'
    status: str = "ASSIGNED"  # 'ASSIGNED', 'VERIFIED', 'AVAILABLE', 'RESERVED', 'FAILED'
    assigned_channel: Optional[str] = None
    profile_id: Optional[str] = None
    verified_at: Optional[str] = None
    notes: str = ""
    is_dynamic_reserve: bool = False
    reserve_type: Optional[str] = None
    candidate_channels: List[str] = field(default_factory=list)
    threshold_views: int = 0


@dataclass
class SimCard:
    phone: str
    carrier: str
    group: str
    reliability: str
    auto_fallback_to_voice: bool
    sms_timeout_seconds: int
    last_verification_at: Optional[str] = None
    slots: List[SimSlot] = field(default_factory=list)

    def is_cooling_down(self, now: Optional[datetime] = None) -> bool:
        return self.cooldown_seconds_remaining(now=now) > 0.0

    def cooldown_seconds_remaining(self, now: Optional[datetime] = None) -> float:
        if not self.last_verification_at:
            return 0.0
        now_dt = now or datetime.now(timezone.utc)
        try:
            last_dt = datetime.fromisoformat(self.last_verification_at)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            elapsed = (now_dt - last_dt).total_seconds()
            remaining = MANDATORY_COOLDOWN_SECONDS - elapsed
            return max(0.0, remaining)
        except Exception as e:
            logger.warning("Failed to parse last_verification_at '%s': %s", self.last_verification_at, e)
            return 0.0


@dataclass
class ChannelAuditResult:
    channel_id: str
    profile_id: Optional[str]
    channel_name: str
    email: Optional[str]
    tier2_unlocked: bool
    tier3_unlocked: bool
    hit_feature_eligibility_dialog: bool
    hit_verify_its_you_gate: bool
    long_video_published: bool
    short_video_published: bool
    related_video_linked: bool
    classification: str
    assigned_sim_phone: Optional[str] = None
    assigned_sim_slot: Optional[int] = None
    assigned_sim_method: Optional[str] = None
    notes: str = ""


class SimVerificationLedger:
    """Manages the 16-slot SIM verification ledger and cooldown safety invariants."""

    def __init__(self, ledger_path: Path = DEFAULT_LEDGER_PATH):
        self.ledger_path = Path(ledger_path)
        self.version = "1.0.0"
        self.updated_at: str = datetime.now(timezone.utc).isoformat()
        self.sims: Dict[str, SimCard] = {}
        self.history: List[Dict[str, Any]] = []
        self._initialize_default_matrix()

    def _initialize_default_matrix(self) -> None:
        """Populate defaults from RAW_SLOT_ASSIGNMENT_MATRIX."""
        for phone, meta in RAW_SLOT_ASSIGNMENT_MATRIX.items():
            slots: List[SimSlot] = []
            for slot_dict in meta["slots"]:
                status = "RESERVED" if slot_dict.get("is_dynamic_reserve") else "ASSIGNED"
                slot = SimSlot(
                    slot_id=slot_dict["slot_id"],
                    method=slot_dict["method"],
                    status=status,
                    assigned_channel=slot_dict.get("assigned_channel"),
                    profile_id=slot_dict.get("profile_id"),
                    verified_at=None,
                    notes=slot_dict.get("notes", ""),
                    is_dynamic_reserve=slot_dict.get("is_dynamic_reserve", False),
                    reserve_type=slot_dict.get("reserve_type"),
                    candidate_channels=slot_dict.get("candidate_channels", []),
                    threshold_views=slot_dict.get("threshold_views", 0),
                )
                slots.append(slot)
            self.sims[phone] = SimCard(
                phone=phone,
                carrier=meta["carrier"],
                group=meta["group"],
                reliability=meta["reliability"],
                auto_fallback_to_voice=meta["auto_fallback_to_voice"],
                sms_timeout_seconds=meta["sms_timeout_seconds"],
                last_verification_at=None,
                slots=slots,
            )

    @classmethod
    def load(cls, ledger_path: Path = DEFAULT_LEDGER_PATH) -> SimVerificationLedger:
        ledger = cls(ledger_path=ledger_path)
        if not ledger_path.is_file():
            logger.info("Ledger not found at %s. Initialized new default ledger.", ledger_path)
            return ledger

        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ledger.version = data.get("version", "1.0.0")
            ledger.updated_at = data.get("updated_at", datetime.now(timezone.utc).isoformat())
            ledger.history = data.get("history", [])

            sims_data = data.get("sims", {})
            for phone, sdata in sims_data.items():
                if phone in ledger.sims:
                    card = ledger.sims[phone]
                    card.last_verification_at = sdata.get("last_verification_at")
                    existing_slots_by_id = {s["slot_id"]: s for s in sdata.get("slots", [])}
                    for slot in card.slots:
                        if slot.slot_id in existing_slots_by_id:
                            saved = existing_slots_by_id[slot.slot_id]
                            slot.status = saved.get("status", slot.status)
                            slot.assigned_channel = saved.get("assigned_channel", slot.assigned_channel)
                            slot.profile_id = saved.get("profile_id", slot.profile_id)
                            slot.verified_at = saved.get("verified_at")
                            if "notes" in saved:
                                slot.notes = saved["notes"]
            logger.debug("Successfully loaded ledger from %s", ledger_path)
        except Exception as e:
            logger.error("Failed to parse ledger %s: %s. Reverting to default matrix.", ledger_path, e)
        return ledger

    def save(self, ledger_path: Optional[Path] = None) -> None:
        target_path = Path(ledger_path or self.ledger_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now(timezone.utc).isoformat()

        payload = {
            "version": self.version,
            "updated_at": self.updated_at,
            "sims": {},
            "history": self.history,
        }
        for phone, card in self.sims.items():
            payload["sims"][phone] = {
                "phone": card.phone,
                "carrier": card.carrier,
                "group": card.group,
                "reliability": card.reliability,
                "auto_fallback_to_voice": card.auto_fallback_to_voice,
                "sms_timeout_seconds": card.sms_timeout_seconds,
                "last_verification_at": card.last_verification_at,
                "slots": [asdict(slot) for slot in card.slots],
            }

        tmp_path = target_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        tmp_path.replace(target_path)
        logger.debug("Saved verification ledger to %s", target_path)

    def check_cooldown(self, phone: str, now: Optional[datetime] = None) -> Tuple[bool, float]:
        """Check cooldown status for a phone number. Returns (is_cooling_down, remaining_seconds)."""
        card = self.sims.get(phone)
        if not card:
            raise KeyError(f"Unknown SIM phone number: {phone}")
        remaining = card.cooldown_seconds_remaining(now=now)
        return (remaining > 0.0, remaining)

    def check_all_cooldowns(self, now: Optional[datetime] = None) -> Dict[str, Dict[str, Any]]:
        """Return status and remaining cooldown seconds across all managed SIMs."""
        res = {}
        for phone, card in self.sims.items():
            cooling, rem = self.check_cooldown(phone, now=now)
            res[phone] = {
                "carrier": card.carrier,
                "group": card.group,
                "is_cooling_down": cooling,
                "remaining_seconds": round(rem, 1),
                "remaining_minutes": round(rem / 60.0, 1),
                "last_verification_at": card.last_verification_at,
            }
        return res

    def record_verification(
        self,
        phone: str,
        slot_id: int,
        channel_id: str,
        method: Optional[str] = None,
        status: str = "VERIFIED",
        notes: str = "",
        force: bool = False,
        now: Optional[datetime] = None,
    ) -> SimSlot:
        """Record verification attempt. Enforces mandatory 20-min cooldown unless forced."""
        card = self.sims.get(phone)
        if not card:
            raise KeyError(f"Unknown SIM phone number: {phone}")

        slot = next((s for s in card.slots if s.slot_id == slot_id), None)
        if not slot:
            raise IndexError(f"Slot {slot_id} not found on SIM {phone}")

        now_dt = now or datetime.now(timezone.utc)
        cooling, rem = self.check_cooldown(phone, now=now_dt)
        if cooling and not force:
            rem_min = rem / 60.0
            raise CooldownActiveError(
                f"Phone {phone} is cooling down for {rem:.0f}s ({rem_min:.1f}m remaining). "
                f"Mandatory {MANDATORY_COOLDOWN_SECONDS // 60}m cooldown between verifications on the same SIM."
            )

        # Update slot
        slot.status = status
        slot.assigned_channel = channel_id
        if method:
            slot.method = method
        iso_now = now_dt.isoformat()
        slot.verified_at = iso_now
        if notes:
            slot.notes = f"{slot.notes} | {notes}".strip(" |")

        # Update card cooldown
        card.last_verification_at = iso_now

        # Append to audit history
        self.history.append({
            "timestamp": iso_now,
            "phone": phone,
            "carrier": card.carrier,
            "slot_id": slot_id,
            "channel_id": channel_id,
            "method": slot.method,
            "status": status,
            "notes": notes,
        })
        self.save()
        logger.info(
            "Recorded verification on %s [Slot %d] for %s (%s). New cooldown active until +20m.",
            phone, slot_id, channel_id, slot.method
        )
        return slot

    def allocate_dynamic_reserves(
        self,
        metrics_source: Optional[Dict[str, Any] | Path] = None,
    ) -> Dict[str, Any]:
        """Inspect view counts and dynamically allocate Dynamic Reserve Slots 3 & 4 on 0559238139.

        Slot 3: First VN Pivot channel ('tui_tien', 'la_ban_hoc_thuat', 'luat_doi_thuong') hitting >500 views.
        Slot 4: First EN secondary channel ('en_crowd_strings', 'en_bamboo_marble', 'en_spawn_to_apex') hitting >200 views.
        """
        metrics = self._load_metrics(metrics_source)
        res_card = self.sims.get(PHONE_VIETNAMOBILE_B2)
        if not res_card:
            return {"status": "error", "message": "Reserve card not configured"}

        results = {}

        # Slot 3: VN Pivot
        slot3 = next((s for s in res_card.slots if s.slot_id == 3), None)
        if slot3 and slot3.is_dynamic_reserve:
            vn_winner, vn_views = self._find_first_eligible(
                slot3.candidate_channels,
                slot3.threshold_views,
                metrics,
            )
            if vn_winner:
                slot3.assigned_channel = vn_winner
                slot3.status = "ASSIGNED"
                slot3.notes = f"Allocated: {vn_winner} surpassed {slot3.threshold_views} views ({vn_views} views)"
                results["slot_3"] = {"allocated": True, "channel": vn_winner, "views": vn_views}
            else:
                top_candidate, top_views = self._get_highest_view_candidate(slot3.candidate_channels, metrics)
                slot3.status = "RESERVED"
                slot3.notes = (
                    f"Waiting for VN Pivot channel to hit >{slot3.threshold_views} views. "
                    f"Current leader: {top_candidate} ({top_views}/{slot3.threshold_views} views)"
                )
                results["slot_3"] = {"allocated": False, "leader": top_candidate, "views": top_views}

        # Slot 4: EN Secondary
        slot4 = next((s for s in res_card.slots if s.slot_id == 4), None)
        if slot4 and slot4.is_dynamic_reserve:
            en_winner, en_views = self._find_first_eligible(
                slot4.candidate_channels,
                slot4.threshold_views,
                metrics,
            )
            if en_winner:
                slot4.assigned_channel = en_winner
                slot4.status = "ASSIGNED"
                slot4.notes = f"Allocated: {en_winner} surpassed {slot4.threshold_views} views ({en_views} views)"
                results["slot_4"] = {"allocated": True, "channel": en_winner, "views": en_views}
            else:
                top_candidate, top_views = self._get_highest_view_candidate(slot4.candidate_channels, metrics)
                slot4.status = "RESERVED"
                slot4.notes = (
                    f"Waiting for EN secondary channel to hit >{slot4.threshold_views} views. "
                    f"Current leader: {top_candidate} ({top_views}/{slot4.threshold_views} views)"
                )
                results["slot_4"] = {"allocated": False, "leader": top_candidate, "views": top_views}

        self.save()
        return results

    def _load_metrics(self, source: Optional[Dict[str, Any] | Path]) -> Dict[str, int]:
        """Extract channel_views dict mapping channel_id -> view_count."""
        data = None
        if isinstance(source, dict):
            data = source
        else:
            path = Path(source or DEFAULT_METRICS_PATH)
            if path.is_file():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    logger.warning("Could not read metrics from %s: %s", path, e)

        views_map: Dict[str, int] = {}
        if not data:
            return views_map

        # Check if already a flat map {channel_id: views}
        if isinstance(data, dict) and "channels" not in data and all(isinstance(v, (int, float)) for v in data.values()):
            return {k: int(v) for k, v in data.items()}

        # Check 'channels' list or dict
        channels_raw = data.get("channels", [])
        if isinstance(channels_raw, list):
            for ch in channels_raw:
                cid = ch.get("channel_id") or ch.get("slug")
                if cid:
                    views_map[cid] = ch.get("channel_views", ch.get("total_views", ch.get("views", 0))) or 0
        elif isinstance(channels_raw, dict):
            for cid, ch in channels_raw.items():
                if isinstance(ch, dict):
                    views_map[cid] = ch.get("channel_views", ch.get("total_views", ch.get("views", 0))) or 0
                elif isinstance(ch, (int, float)):
                    views_map[cid] = int(ch)
        return views_map

    def _find_first_eligible(
        self,
        candidates: List[str],
        threshold: int,
        metrics: Dict[str, int],
    ) -> Tuple[Optional[str], int]:
        for cid in candidates:
            v = metrics.get(cid, 0)
            if v > threshold:
                return cid, v
        return None, 0

    def _get_highest_view_candidate(
        self,
        candidates: List[str],
        metrics: Dict[str, int],
    ) -> Tuple[str, int]:
        best_cid = candidates[0] if candidates else "none"
        best_views = 0
        for cid in candidates:
            v = metrics.get(cid, 0)
            if v > best_views:
                best_views = v
                best_cid = cid
        return best_cid, best_views


class ZeroSimFallbackHelper:
    """Automates Step 3 Zero-SIM Fallback for channels without an active SIM slot.

    Includes:
    - in_video_auto_frame_thumbnail: Selects the 25% or 50% hand-lettered keyframe in YouTube Studio.
    - tier3_build_channel_history: Selects 'Build channel history' under YouTube Studio Settings -> Feature eligibility.
    """

    @staticmethod
    def get_fallback_config(channel_id: str) -> Dict[str, Any]:
        return {
            "channel_id": channel_id,
            "strategy": "ZERO_SIM_STEP3_FALLBACK",
            "tier2_fallback": {
                "mode": "in_video_auto_frame_thumbnail",
                "recommended_keyframe": "25% or 50% hand-lettered doodle frame",
                "frame_index": 1,  # 0-indexed: index 1 is middle frame (approx 25%-50% timestamp)
                "selector_cdp": ZeroSimFallbackHelper.generate_in_video_auto_frame_js(frame_index=1),
            },
            "tier3_fallback": {
                "mode": "build_channel_history",
                "settings_url": "https://studio.youtube.com/channel/SETTINGS/features",
                "option_name": "Build channel history",
                "selector_cdp": ZeroSimFallbackHelper.generate_build_channel_history_js(),
            },
        }

    @staticmethod
    def generate_in_video_auto_frame_js(frame_index: int = 1) -> str:
        """CDP JavaScript evaluating and clicking the 25%/50% auto-generated video frame."""
        return f"""(() => {{
    // Select YouTube Studio auto-generated video thumbnail frame #{frame_index} (25%-50% doodle keyframe)
    const options = Array.from(document.querySelectorAll(
        'ytcp-video-thumbnail-editor [role="radio"], ' +
        'ytcp-thumbnails-compact-editor-uploader [role="radio"], ' +
        'tp-yt-paper-radio-button[name="auto-generated-thumbnail"], ' +
        '#auto-generated-thumbnails ytcp-thumbnail-selection-item'
    ));
    if (options.length > {frame_index}) {{
        const target = options[{frame_index}];
        target.scrollIntoView({{ behavior: 'instant', block: 'center' }});
        target.click();
        return {{ success: true, selected_index: {frame_index}, element: target.tagName }};
    }}
    // Fallback: look for non-custom thumbnail clickable blocks
    const thumbs = Array.from(document.querySelectorAll('ytcp-thumbnail-area #thumbnail-container, ytcp-thumbnail-selection-item'));
    if (thumbs.length > {frame_index}) {{
        thumbs[{frame_index}].click();
        return {{ success: true, selected_index: {frame_index}, note: 'fallback thumbnail clicked' }};
    }}
    return {{ success: false, reason: 'Auto-frame thumbnail option not found in DOM' }};
}})()"""

    @staticmethod
    def generate_build_channel_history_js() -> str:
        """CDP JavaScript to navigate Settings -> Channel -> Feature Eligibility and select 'Build channel history'."""
        return """(() => {
    // 1. Expand Tier 3 Advanced Features section
    const tier3Item = document.querySelector('ytcp-feature-eligibility-item#advanced-features, ytcp-feature-eligibility-item[feature-tier="3"]');
    if (tier3Item) {
        const expandBtn = tier3Item.querySelector('#expansion-panel-summary, #arrow-icon, button');
        if (expandBtn) expandBtn.click();
    }
    // 2. Click 'Access features' button if present
    const accessBtn = Array.from(document.querySelectorAll('ytcp-button, button')).find(b => {
        const txt = (b.innerText || '').toLowerCase();
        return txt.includes('access features') || txt.includes('truy cập tính năng');
    });
    if (accessBtn) accessBtn.click();

    // 3. In the selection modal, pick 'Build channel history' radio button
    setTimeout(() => {
        const historyRadio = Array.from(document.querySelectorAll('tp-yt-paper-radio-button, div[role="radio"]')).find(r => {
            const txt = (r.innerText || '').toLowerCase();
            return txt.includes('channel history') || txt.includes('lịch sử kênh') || txt.includes('build channel history');
        });
        if (historyRadio) {
            historyRadio.click();
            const nextOrDone = document.querySelector('#next-button, #done-button, ytcp-button#confirm-button');
            if (nextOrDone) nextOrDone.click();
        }
    }, 1000);
    return { success: true, action: 'initiated_build_channel_history_selection' };
})()"""


class ChannelFleetAuditor:
    """Audits existing channel states across channel map, publish reports, and logs."""

    def __init__(
        self,
        channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH,
        publish_report_path: Path = DEFAULT_PUBLISH_REPORT_PATH,
        metrics_path: Path = DEFAULT_METRICS_PATH,
    ):
        self.channel_map_path = Path(channel_map_path)
        self.publish_report_path = Path(publish_report_path)
        self.metrics_path = Path(metrics_path)

    def audit_fleet(self, ledger: Optional[SimVerificationLedger] = None) -> List[ChannelAuditResult]:
        channels_map = self._load_channel_map()
        pub_report = self._load_publish_report()
        ledger = ledger or SimVerificationLedger.load()

        # Build reverse lookup for SIM allocations
        sim_lookup: Dict[str, Tuple[str, int, str]] = {}  # channel_id -> (phone, slot_id, method)
        for phone, card in ledger.sims.items():
            for slot in card.slots:
                if slot.assigned_channel:
                    sim_lookup[slot.assigned_channel] = (phone, slot.slot_id, slot.method)

        results: List[ChannelAuditResult] = []

        for cid, cinfo in sorted(channels_map.items()):
            profile_id = cinfo.get("profile_id")
            channel_name = cinfo.get("channel_name", cid)
            email = cinfo.get("email")

            pubs = cinfo.get("published_videos", [])
            has_long_pub = any(
                p.get("format") == "long_16x9" or ("youtu.be" in str(p.get("video_url", "")) and "shorts" not in str(p.get("video_url", "")))
                for p in pubs
            )
            has_short_pub = any(
                p.get("format") == "short_9x16" or ("shorts" in str(p.get("video_url", "")))
                for p in pubs
            )
            has_related_link = any(bool(p.get("related_video_url")) for p in pubs)

            # Check publish report notes for gate hit
            report_item = next((r for r in pub_report if r.get("channel_id") == cid or r.get("slug") == cinfo.get("slug")), None)
            hit_reauth = False
            hit_dialog = False
            notes = ""

            if report_item:
                if report_item.get("auth_status") == "NEEDS_REAUTH_VERIFY_ITS_YOU" or "Verify Its You" in str(report_item.get("notes", "")):
                    hit_reauth = True
                    notes = report_item.get("notes", "Hit Google Verify Its You gate")
                if not report_item.get("long_url") and not has_long_pub and has_short_pub:
                    # Shorts published but long video could not publish / skipped custom thumbnail
                    hit_dialog = True
                    if not notes:
                        notes = "Hit ytcp-feature-eligibility-dialog (Tier 2 verification gate on long/thumbnail)"

            # Tier 2 unlocked: has custom thumbnail uploaded or long video verified
            tier2_unlocked = has_long_pub
            # Tier 3 unlocked: has related video link successfully bound
            tier3_unlocked = has_related_link

            # Classification
            if hit_reauth:
                classification = "BLOCKED_REAUTH_VERIFY_ITS_YOU"
            elif tier2_unlocked and tier3_unlocked:
                classification = "TIER2_TIER3_UNLOCKED"
            elif tier2_unlocked and not tier3_unlocked:
                classification = "TIER2_ONLY_UNLOCKED"
            elif hit_dialog or (not tier2_unlocked and has_short_pub):
                classification = "NEEDS_TIER2_SIM_VERIFY"
            elif not has_short_pub and not has_long_pub:
                classification = "ZERO_VIDEOS_STANDBY"
            else:
                classification = "STANDARD_TIER1"

            sim_info = sim_lookup.get(cid)
            sim_phone = sim_info[0] if sim_info else None
            sim_slot = sim_info[1] if sim_info else None
            sim_method = sim_info[2] if sim_info else None

            results.append(ChannelAuditResult(
                channel_id=cid,
                profile_id=profile_id,
                channel_name=channel_name,
                email=email,
                tier2_unlocked=tier2_unlocked,
                tier3_unlocked=tier3_unlocked,
                hit_feature_eligibility_dialog=hit_dialog,
                hit_verify_its_you_gate=hit_reauth,
                long_video_published=has_long_pub,
                short_video_published=has_short_pub,
                related_video_linked=has_related_link,
                classification=classification,
                assigned_sim_phone=sim_phone,
                assigned_sim_slot=sim_slot,
                assigned_sim_method=sim_method,
                notes=notes,
            ))

        return results

    def _load_channel_map(self) -> Dict[str, Any]:
        if not self.channel_map_path.is_file():
            logger.warning("Channel map not found at %s", self.channel_map_path)
            return {}
        try:
            with open(self.channel_map_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("channels", {})
        except Exception as e:
            logger.error("Error reading channel map: %s", e)
            return {}

    def _load_publish_report(self) -> List[Dict[str, Any]]:
        if not self.publish_report_path.is_file():
            return []
        try:
            with open(self.publish_report_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Error reading publish report: %s", e)
            return []


# CLI Renderers & Formatters
def render_plan(ledger: SimVerificationLedger) -> str:
    lines = [
        "=" * 85,
        "4-SIM VERIFICATION & TIER-2/TIER-3 CHANNEL UNLOCK PLAN (16 SLOTS SSOT)",
        "=" * 85,
        f"Updated At: {ledger.updated_at}",
        f"Cooldown Rule: Mandatory >= {MANDATORY_COOLDOWN_SECONDS // 60} minutes between verifications on same phone number.",
        "-" * 85,
    ]

    for phone, card in ledger.sims.items():
        cooling, rem = ledger.check_cooldown(phone)
        status_str = f"COOLING DOWN ({rem:.0f}s left)" if cooling else "READY"
        lines.append(f"Phone: {phone} | Carrier: {card.carrier:<16} | Group: {card.group:<8} | Cooldown: {status_str}")
        lines.append(f"Reliability: {card.reliability}")
        lines.append("  Slots (2 SMS + 2 Voice Call):")
        for s in card.slots:
            target = s.assigned_channel or "[RESERVED - Awaiting Trigger]"
            prof = f"({s.profile_id})" if s.profile_id else ""
            method_badge = s.method.upper()
            lines.append(
                f"    Slot {s.slot_id} [{method_badge:<10}] : {s.status:<9} | {target:<22} {prof:<14} | {s.notes}"
            )
        lines.append("-" * 85)

    return "\n".join(lines)


def render_status(ledger: SimVerificationLedger, audit_results: List[ChannelAuditResult]) -> str:
    lines = [
        "=" * 85,
        "FLEET TIER-2/TIER-3 UNLOCK AUDIT & SIM VERIFICATION STATUS",
        "=" * 85,
    ]

    unlocked_t2_t3 = [r for r in audit_results if r.tier2_unlocked and r.tier3_unlocked]
    tier2_only = [r for r in audit_results if r.tier2_unlocked and not r.tier3_unlocked]
    needs_sim = [r for r in audit_results if r.hit_feature_eligibility_dialog or r.classification == "NEEDS_TIER2_SIM_VERIFY"]
    reauth_gate = [r for r in audit_results if r.hit_verify_its_you_gate]
    standby = [r for r in audit_results if r.classification == "ZERO_VIDEOS_STANDBY"]

    lines.append(f"Total Fleet Channels: {len(audit_results)}")
    lines.append(f"  ✓ Tier 2 & Tier 3 Unlocked: {len(unlocked_t2_t3)} channels (20 VN + 4 EN)")
    lines.append(f"  ▲ Tier 2 Only Unlocked:     {len(tier2_only)} channels (en_bamboo_marble)")
    lines.append(f"  ⚠ Needs SIM (Hit Dialog):   {len(needs_sim)} channels (EN batch 1 pending Tier 2)")
    lines.append(f"  ⛔ Reauth Blocked:           {len(reauth_gate)} channel(s): {[r.channel_id for r in reauth_gate]}")
    lines.append(f"  ⏳ Zero-Video Standby:       {len(standby)} channels")
    lines.append("-" * 85)
    lines.append(f"{'Channel ID':<22} | {'Profile':<12} | {'T2 Unlocked':<11} | {'T3 Link':<8} | {'SIM Allocation':<24}")
    lines.append("-" * 85)

    for r in audit_results:
        t2 = "YES" if r.tier2_unlocked else "NO"
        t3 = "YES" if r.tier3_unlocked else "NO"
        sim_desc = f"{r.assigned_sim_phone} S{r.assigned_sim_slot} ({r.assigned_sim_method})" if r.assigned_sim_phone else "Zero-SIM Fallback"
        lines.append(f"{r.channel_id:<22} | {str(r.profile_id):<12} | {t2:<11} | {t3:<8} | {sim_desc:<24}")

    lines.append("=" * 85)
    return "\n".join(lines)


def render_cooldown(ledger: SimVerificationLedger) -> str:
    lines = [
        "=" * 70,
        "SIM COOLDOWN STATUS (MANDATORY >= 20 MINUTE INTERVAL)",
        "=" * 70,
    ]
    status_map = ledger.check_all_cooldowns()
    for phone, info in status_map.items():
        if info["is_cooling_down"]:
            cd_str = f"COOLING DOWN: {info['remaining_seconds']}s remaining ({info['remaining_minutes']}m)"
        else:
            cd_str = "READY FOR NEXT VERIFICATION"
        lines.append(f"Phone {phone} ({info['carrier']}, {info['group']}): {cd_str}")
        lines.append(f"  Last Verification: {info['last_verification_at'] or 'None recorded'}")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Video Pilot 4-SIM Verification & Channel Unlock Manager")
    parser.add_argument("--status", action="store_true", help="Audit channel fleet unlock status & gate blockers")
    parser.add_argument("--plan", action="store_true", help="Display the 16-slot SIM assignment matrix and rules")
    parser.add_argument("--allocate", action="store_true", help="Reconcile and allocate dynamic reserve slots based on metrics")
    parser.add_argument("--cooldown-check", action="store_true", help="Check cooldown timers across all 4 SIMs")
    parser.add_argument("--phone", type=str, help="Filter or specify phone number (e.g. 0794999539)")
    parser.add_argument("--slot", type=int, choices=[1, 2, 3, 4], help="Slot index (1-4)")
    parser.add_argument("--channel", type=str, help="Channel ID for verification or fallback lookup")
    parser.add_argument("--record-verification", action="store_true", help="Record a verification completion in the ledger")
    parser.add_argument("--method", choices=["sms", "voice_call"], default=None, help="Verification method used")
    parser.add_argument("--force", action="store_true", help="Bypass cooldown check (emergency/testing override)")
    parser.add_argument("--fallback-config", type=str, help="Output Step 3 Zero-SIM fallback config & CDP script for channel")
    parser.add_argument("--json", action="store_true", help="Output responses in JSON format")
    parser.add_argument("--ledger-path", type=Path, default=DEFAULT_LEDGER_PATH, help="Path to sim ledger JSON file")

    args = parser.parse_args()

    ledger = SimVerificationLedger.load(args.ledger_path)
    auditor = ChannelFleetAuditor()

    # Step 3 Fallback config command
    if args.fallback_config:
        cfg = ZeroSimFallbackHelper.get_fallback_config(args.fallback_config)
        if args.json:
            print(json.dumps(cfg, indent=2))
        else:
            print("=" * 70)
            print(f"STEP 3 ZERO-SIM FALLBACK CONFIGURATION FOR: {args.fallback_config}")
            print("=" * 70)
            print(f"Tier 2 Mode: {cfg['tier2_fallback']['mode']}")
            print(f"Recommended Keyframe: {cfg['tier2_fallback']['recommended_keyframe']}")
            print(f"Tier 3 Mode: {cfg['tier3_fallback']['mode']}")
            print(f"Settings URL: {cfg['tier3_fallback']['settings_url']}")
            print("\n[CDP SCRIPT: Auto-Frame Thumbnail Selector]")
            print(cfg["tier2_fallback"]["selector_cdp"])
            print("\n[CDP SCRIPT: Build Channel History]")
            print(cfg["tier3_fallback"]["selector_cdp"])
        return 0

    # Cooldown check command
    if args.cooldown_check:
        if args.json:
            print(json.dumps(ledger.check_all_cooldowns(), indent=2))
        else:
            print(render_cooldown(ledger))
        return 0

    # Dynamic Reserve Allocation command
    if args.allocate:
        alloc_res = ledger.allocate_dynamic_reserves()
        if args.json:
            print(json.dumps(alloc_res, indent=2))
        else:
            print("Allocated dynamic reserve slots:")
            print(json.dumps(alloc_res, indent=2))
            print(render_plan(ledger))
        return 0

    # Record verification command
    if args.record_verification:
        if not args.phone or not args.slot or not args.channel:
            print("Error: --record-verification requires --phone, --slot, and --channel", file=sys.stderr)
            return 1
        try:
            slot = ledger.record_verification(
                phone=args.phone,
                slot_id=args.slot,
                channel_id=args.channel,
                method=args.method,
                status="VERIFIED",
                force=args.force,
            )
            if args.json:
                print(json.dumps(asdict(slot), indent=2))
            else:
                print(f"Successfully recorded verification on {args.phone} Slot {args.slot} for {args.channel}!")
                print(render_cooldown(ledger))
            return 0
        except CooldownActiveError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    # Status audit command
    if args.status:
        audit_results = auditor.audit_fleet(ledger)
        if args.json:
            print(json.dumps([asdict(r) for r in audit_results], indent=2))
        else:
            print(render_status(ledger, audit_results))
        return 0

    # Default action: Plan
    if args.json:
        payload = {
            "updated_at": ledger.updated_at,
            "sims": {phone: asdict(card) for phone, card in ledger.sims.items()},
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_plan(ledger))

    return 0


if __name__ == "__main__":
    sys.exit(main())
