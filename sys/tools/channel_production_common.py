#!/usr/bin/env python3
"""Video Pilot — Common Production Helpers for Channel Videos (Short & Long).

SSOT shared production library supporting both short_9x16 and long_16x9:
- Multi-channel resource slicing & account routing (contract §1)
- Voice profile resolution and clause-level cadence splitting
- Flow CDP image compilation (1.7.0 doodle + custom channel visual identities)
- Support for image reuse (reuse_from), variations (based_on), emphasis lettering,
  channel endcards, and focus-crop beats
- Colab T4 OmniVoice TTS synthesis & PCM16 WAV assembly with trailing silence padding
- Remote Colab Tesla T4 Native FFmpeg h264_nvenc rendering (30 fps, external SRT for long)
- FFprobe validation & deliverable packaging
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import audio_processing as ap  # noqa: E402
from channels.registry import get_channel  # noqa: E402
from colab_bridge.client import Client, ColabError  # noqa: E402

ColabBridgeError = ColabError
from colab_bridge.job_protocol import build_render_request  # noqa: E402
from colab_bridge.protocol import build_request  # noqa: E402
from flow_prompts import compile as compile_flow_prompt  # noqa: E402
from flow_prompts.compiler import CHARACTER_FREE_DIRECTIVE  # noqa: E402
from scripts.subtitles import audit_cues, subtitle_cues  # noqa: E402
from tools.vn_text_normalizer import normalize_for_tts  # noqa: E402

logger = logging.getLogger("channel_production_common")

REVERSE_DISPLAY_MAP: Dict[str, str] = {
    "Diu-túp": "YouTube",
    "Diu túp": "YouTube",
    "Tích-tốc": "TikTok",
    "Tích tốc": "TikTok",
    "Phây-sờ-búc": "Facebook",
    "Phây sờ búc": "Facebook",
    "Phây-bút": "Facebook",
    "Phây-xơ-búc": "Facebook",
    "Gúc-gồ": "Google",
    "Gúc gồ": "Google",
    "Sóp-pi": "Shopee",
    "Xóp-pi": "Shopee",
    "vi-đê-ô": "video",
    "i-meo": "email",
    "oai-phai": "wifi",
    "in-tơ-nét": "internet",
    "láp-tóp": "laptop",
    "đét-lai": "deadline",
    "xờ-lai": "slide",
    "hai-lai": "highlight",
    "Guốc": "Word",
    "Ếch-xen": "Excel",
    "bờ-lốc": "blog",
    "pót-cát": "podcast",
    "Ri-chát Phây-man": "Richard Feynman",
    "Ri-chát": "Richard",
    "Phây-man": "Feynman",
    "Hô-mô sa-pi-en": "Homo sapiens",
    "Nê-an-đơ-than": "Neanderthal",
    "Cô-vít": "Covid",
    "Cô-vít mười chín": "Covid-19",
}


def restore_display_text(text: str) -> str:
    """Restore written Latin/brand terms in display captions, SRT and on-screen text."""
    if not text:
        return text
    for phonetic, written in REVERSE_DISPLAY_MAP.items():
        text = re.sub(rf"(?i)\b{re.escape(phonetic)}\b", written, text)
    return text

# Contract §1 Unified Zero-Contention SSOT Resource Partitioning:
# - 100% mutually disjoint across all 8 channels (zero Flow profile overlap, zero Colab overlap).
# - Uses only the 11 verified unique Google identities with healthy quota.
# - Excludes unauthenticated `profile_11` and disabled `account-02`.
# - Places each channel's own YouTube Studio profile LAST as cold-standby fallback so primary
#   Flow generation never touches any YouTube Studio session (even within the same channel).
CHANNEL_RESOURCE_PARTITIONS: Dict[str, Dict[str, Any]] = {
    "nao_luoi": {
        "slug": "nao-luoi",
        "youtube_profile": "profile_4",
        "flow_profiles": ["profile_2", "profile_4"],
        "colab_accounts": ["account-01", "account-13"],
        "session": "vp-nao-luoi",
    },
    "tui_tien": {
        "slug": "tui-tien",
        "youtube_profile": "profile_10",
        "flow_profiles": ["profile_7", "profile_10"],
        "colab_accounts": ["account-04"],
        "session": "vp-tui-tien",
    },
    "ua_sao_vay": {
        "slug": "ua-sao-vay",
        "youtube_profile": "profile_9",
        "flow_profiles": ["profile_8", "profile_9"],
        "colab_accounts": ["account-06", "account-17"],
        "session": "vp-ua-sao-vay",
    },
    "su_ke_lai": {
        "slug": "su-ke-lai",
        "youtube_profile": "profile_5",
        "flow_profiles": ["profile_12", "profile_5"],
        "colab_accounts": ["account-10"],
        "session": "vp-su-ke-lai",
    },
    "thuong_cho_kheo": {
        "slug": "thuong-cho-kheo",
        "youtube_profile": "profile_6",
        "flow_profiles": ["profile_14", "profile_6"],
        "colab_accounts": ["account-11"],
        "session": "vp-thuong-cho-kheo",
    },
    "ho_so_ky_la": {
        "slug": "ho-so-ky-la",
        "youtube_profile": "profile_3",
        "flow_profiles": ["profile_15", "profile_16", "profile_3"],
        "colab_accounts": ["account-15"],
        "session": "vp-ho-so-ky-la",
    },
    "co_the_ke": {
        "slug": "co-the-ke",
        "youtube_profile": "profile_1",
        "flow_profiles": ["profile_17", "profile_18", "profile_1"],
        "colab_accounts": ["account-16"],
        "session": "vp-co-the-ke",
    },
    "ai_binh_dan": {
        "slug": "ai-binh-dan",
        "youtube_profile": "profile_13",
        "flow_profiles": ["profile_19", "profile_20", "profile_13"],
        "colab_accounts": ["account-20", "account-18"],
        "session": "vp-ai-binh-dan",
    },
    "luat_ngam": {
        "slug": "luat-ngam",
        "youtube_profile": "profile_2",
        "flow_profiles": ["profile_7", "profile_2"],
        "colab_accounts": ["account-01", "account-03"],
        "session": "vp-luat-ngam",
    },
    "ban_do_quyen_luc": {
        "slug": "ban-do-quyen-luc",
        "youtube_profile": "profile_19",
        "flow_profiles": ["profile_12", "profile_19"],
        "colab_accounts": ["account-04", "account-05"],
        "session": "vp-ban-do-quyen-luc",
    },
    "dia_com": {
        "slug": "dia-com",
        "youtube_profile": "profile_14",
        "flow_profiles": ["profile_8", "profile_14"],
        "colab_accounts": ["account-06", "account-07"],
        "session": "vp-dia-com",
    },
    "luat_doi_thuong": {
        "slug": "luat-doi-thuong",
        "youtube_profile": "profile_15",
        "flow_profiles": ["profile_3", "profile_15"],
        "colab_accounts": ["account-08", "account-10"],
        "session": "vp-luat-doi-thuong",
    },
    "banh_rang": {
        "slug": "banh-rang",
        "youtube_profile": "profile_16",
        "flow_profiles": ["profile_4", "profile_16"],
        "colab_accounts": ["account-11", "account-12"],
        "session": "vp-banh-rang",
    },
    "vu_tru_ti_hon": {
        "slug": "vu-tru-ti-hon",
        "youtube_profile": "profile_17",
        "flow_profiles": ["profile_1", "profile_17"],
        "colab_accounts": ["account-13", "account-14"],
        "session": "vp-vu-tru-ti-hon",
    },
    "nghe_song_sot": {
        "slug": "nghe-song-sot",
        "youtube_profile": "profile_18",
        "flow_profiles": ["profile_5", "profile_18"],
        "colab_accounts": ["account-15", "account-16"],
        "session": "vp-nghe-song-sot",
    },
    "la_ban_hoc_thuat": {
        "slug": "la-ban-hoc-thuat",
        "youtube_profile": "profile_20",
        "flow_profiles": ["profile_6", "profile_20"],
        "colab_accounts": ["account-17", "account-20"],
        "session": "vp-la-ban-hoc-thuat",
    },
    "chanh_niem_ke": {
        "slug": "chanh-niem-ke",
        "youtube_profile": "profile_7",
        "flow_profiles": ["profile_8", "profile_13", "profile_10"],
        "colab_accounts": ["account-01", "account-04"],
        "session": "vp-chanh-niem-ke",
    },
    "loi_sang_soi": {
        "slug": "loi-sang-soi",
        "youtube_profile": "profile_12",
        "flow_profiles": ["profile_16", "profile_18", "profile_19"],
        "colab_accounts": ["account-06", "account-10"],
        "session": "vp-loi-sang-soi",
    },
    "minh_triet_song": {
        "slug": "minh-triet-song",
        "youtube_profile": "profile_11",
        "flow_profiles": ["profile_4", "profile_9"],
        "colab_accounts": ["account-11", "account-15"],
        "session": "vp-minh-triet-song",
    },
    "tam_tinh_dem": {
        "slug": "tam-tinh-dem",
        "youtube_profile": "profile_21",
        "flow_profiles": ["profile_5", "profile_6"],
        "colab_accounts": ["account-16", "account-20"],
        "session": "vp-tam-tinh-dem",
    },
    "en_lazy_brain": {
        "slug": "en-lazy-brain",
        "youtube_profile": "profile_en01",
        "flow_profiles": ["profile_1", "profile_2"],
        "colab_accounts": ["account-01", "account-03"],
        "session": "vp-en-lazy-brain",
    },
    "en_crowd_strings": {
        "slug": "en-crowd-strings",
        "youtube_profile": "profile_en02",
        "flow_profiles": ["profile_2", "profile_3"],
        "colab_accounts": ["account-04", "account-05"],
        "session": "vp-en-crowd-strings",
    },
    "en_kindred_sketch": {
        "slug": "en-kindred-sketch",
        "youtube_profile": "profile_en03",
        "flow_profiles": ["profile_3", "profile_4"],
        "colab_accounts": ["account-06", "account-07"],
        "session": "vp-en-kindred-sketch",
    },
    "en_first_principles": {
        "slug": "en-first-principles",
        "youtube_profile": "profile_en05",
        "flow_profiles": ["profile_5", "profile_6"],
        "colab_accounts": ["account-11", "account-12"],
        "session": "vp-en-first-principles",
    },
    "en_wallet_anatomy": {
        "slug": "en-wallet-anatomy",
        "youtube_profile": "profile_en06",
        "flow_profiles": ["profile_6", "profile_7"],
        "colab_accounts": ["account-13", "account-14"],
        "session": "vp-en-wallet-anatomy",
    },
    "en_macro_gears": {
        "slug": "en-macro-gears",
        "youtube_profile": "profile_en07",
        "flow_profiles": ["profile_7", "profile_8"],
        "colab_accounts": ["account-15", "account-16"],
        "session": "vp-en-macro-gears",
    },
    "en_plain_sight_ai": {
        "slug": "en-plain-sight-ai",
        "youtube_profile": "profile_en08",
        "flow_profiles": ["profile_8", "profile_9"],
        "colab_accounts": ["account-17", "account-18"],
        "session": "vp-en-plain-sight-ai",
    },
    "en_career_leverage": {
        "slug": "en-career-leverage",
        "youtube_profile": "profile_en09",
        "flow_profiles": ["profile_9", "profile_10"],
        "colab_accounts": ["account-19", "account-20"],
        "session": "vp-en-career-leverage",
    },
    "en_fine_print": {
        "slug": "en-fine-print",
        "youtube_profile": "profile_en10",
        "flow_profiles": ["profile_10", "profile_12"],
        "colab_accounts": ["account-01", "account-04"],
        "session": "vp-en-fine-print",
    },
    "en_inside_vessel": {
        "slug": "en-inside-vessel",
        "youtube_profile": "profile_en11",
        "flow_profiles": ["profile_20", "profile_1"],
        "colab_accounts": ["account-05", "account-06"],
        "session": "vp-en-inside-vessel",
    },
    "en_kitchen_molecules": {
        "slug": "en-kitchen-molecules",
        "youtube_profile": "profile_en12",
        "flow_profiles": ["profile_12", "profile_13"],
        "colab_accounts": ["account-07", "account-08"],
        "session": "vp-en-kitchen-molecules",
    },
    "en_wait_how": {
        "slug": "en-wait-how",
        "youtube_profile": "profile_en13",
        "flow_profiles": ["profile_13", "profile_14"],
        "colab_accounts": ["account-10", "account-11"],
        "session": "vp-en-wait-how",
    },
    "en_cold_case_ink": {
        "slug": "en-cold-case-ink",
        "youtube_profile": "profile_en14",
        "flow_profiles": ["profile_14", "profile_15"],
        "colab_accounts": ["account-12", "account-13"],
        "session": "vp-en-cold-case-ink",
    },
    "en_choke_point": {
        "slug": "en-choke-point",
        "youtube_profile": "profile_en15",
        "flow_profiles": ["profile_15", "profile_16"],
        "colab_accounts": ["account-14", "account-15"],
        "session": "vp-en-choke-point",
    },
    "en_pocket_cosmos": {
        "slug": "en-pocket-cosmos",
        "youtube_profile": "profile_en16",
        "flow_profiles": ["profile_16", "profile_17"],
        "colab_accounts": ["account-16", "account-17"],
        "session": "vp-en-pocket-cosmos",
    },
    "en_second_arrow": {
        "slug": "en-second-arrow",
        "youtube_profile": "profile_en17",
        "flow_profiles": ["profile_17", "profile_18"],
        "colab_accounts": ["account-18", "account-19"],
        "session": "vp-en-second-arrow",
    },
    "en_parable_lamp": {
        "slug": "en-parable-lamp",
        "youtube_profile": "profile_en18",
        "flow_profiles": ["profile_18", "profile_19"],
        "colab_accounts": ["account-20", "account-01"],
        "session": "vp-en-parable-lamp",
    },
    "en_bamboo_marble": {
        "slug": "en-bamboo-marble",
        "youtube_profile": "profile_en19",
        "flow_profiles": ["profile_19", "profile_20"],
        "colab_accounts": ["account-03", "account-05"],
        "session": "vp-en-bamboo-marble",
    },
}

DEFAULT_WORKERS_PER_JOB = int(os.environ.get("VP_WORKERS_PER_JOB", "2"))
DEFAULT_FLOW_PACING_SECONDS = float(os.environ.get("VP_FLOW_PACING_SECONDS", "1.0"))

DEFAULT_CANDIDATE_ACCOUNTS: List[str] = [
    f"account-{i:02d}" for i in range(1, 21) if i != 2  # account-02 disabled by default
]

VERIFIED_COLAB_ACCOUNTS: List[str] = [
    "account-10",
    "account-13",
    "account-18",
    "account-19",
    "account-20",
    "account-01",
    "account-03",
    "account-04",
    "account-05",
    "account-06",
    "account-11",
    "account-15",
    "account-16",
    "account-17",
]


class _AccountBudgetProxy:
    def __init__(self, budgets_mgr: Any, account_id: str, data: dict[str, Any], identity: str):
        self._budgets_mgr = budgets_mgr
        self.account_id = account_id
        self._identity = identity
        self._data = data
        acct_entry = data.get("accounts", {}).get(identity, {})
        self.intervals = acct_entry.get("intervals", [])
        self.allocated_sessions: List[str] = [
            str(it.get("session")) for it in self.intervals if it.get("end") is None and it.get("session")
        ]
        self.uncertain_allocations: List[str] = [
            str(it.get("session")) for it in self.intervals if it.get("uncertain") and it.get("session")
        ]

    def clear_uncertain(self) -> None:
        self.uncertain_allocations.clear()
        for it in self.intervals:
            it["uncertain"] = False


class _BudgetsProxy:
    def __init__(self, budgets_mgr: Any):
        self._budgets = budgets_mgr
        self.path = getattr(budgets_mgr, "path", None)

    def read(self) -> dict[str, Any]:
        return self._budgets.read()

    def snapshot(self, alias: str) -> dict[str, Any]:
        return self._budgets.snapshot(alias)

    def load_account(self, account_id: str) -> _AccountBudgetProxy:
        data = self._budgets.read()
        alias = f"colab:{account_id}" if not account_id.startswith("colab:") else account_id
        identity = data.get("aliases", {}).get(alias, "")
        return _AccountBudgetProxy(self._budgets, account_id, data, identity)

    def record_stop(self, account_id: str, session_name: str, reason: str = "stale_cleanup") -> None:
        alias = f"colab:{account_id}" if not account_id.startswith("colab:") else account_id
        now = time.time()
        try:
            self._budgets.released(alias, session_name, at=now, evidence=reason)
        except Exception:
            try:
                from session_store import locked_json

                with locked_json(self._budgets.path, self._budgets.read) as data:
                    identity = data.get("aliases", {}).get(alias)
                    if identity and identity in data.get("accounts", {}):
                        for it in data["accounts"][identity].get("intervals", []):
                            if it.get("session") == session_name and it.get("end") is None:
                                start_t = float(it.get("start") or now)
                                it["end"] = max(now, start_t + 1.0)
                                it["release_evidence"] = reason
                                it["uncertain"] = False
            except Exception:
                pass

    def save_account(self, acct_budget: _AccountBudgetProxy) -> None:
        try:
            from session_store import locked_json

            with locked_json(self._budgets.path, self._budgets.read) as data:
                identity = acct_budget._identity
                if identity and identity in data.get("accounts", {}):
                    for it in data["accounts"][identity].get("intervals", []):
                        if not acct_budget.uncertain_allocations:
                            it["uncertain"] = False
        except Exception:
            pass


class _SchedulerProxy:
    def __init__(self, client: Any):
        self._client = client

    def clear_session_journal(self, account_id: str, identity_key: str) -> None:
        try:
            from colab_bridge.protocol import stamp

            budgets = self._client._budgets()
            store_dir = budgets.path.parent
            if identity_key:
                alloc_file = store_dir / f"allocation-{stamp(identity_key)}.json"
                if alloc_file.is_file():
                    lock_file = alloc_file.with_suffix(".lock")
                    try:
                        with lock_file.open("a") as lk:
                            try:
                                fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
                                try:
                                    data = json.loads(alloc_file.read_text(encoding="utf-8"))
                                    data["phase"] = "released"
                                    data["release_reason"] = "stale_cleanup"
                                    data["updated_at"] = time.time()
                                    alloc_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                                except Exception:
                                    alloc_file.unlink(missing_ok=True)
                                fcntl.flock(lk, fcntl.LOCK_UN)
                            except BlockingIOError:
                                pass
                    except Exception:
                        pass
            dispatch_dir = store_dir / "colab-dispatch"
            if dispatch_dir.is_dir():
                for rec in dispatch_dir.glob("*.json"):
                    try:
                        d = json.loads(rec.read_text(encoding="utf-8"))
                        if d.get("account") == account_id:
                            rec.unlink(missing_ok=True)
                    except Exception:
                        pass
        except Exception:
            pass


def _identity_key(client: Any, account_id: str) -> str:
    alias = f"colab:{account_id}" if not account_id.startswith("colab:") else account_id
    budgets = client._budgets()
    return budgets.read().get("aliases", {}).get(alias, "")


def ensure_client_failover_helpers(client: Any) -> None:
    if not hasattr(client, "budgets"):
        client.budgets = _BudgetsProxy(client._budgets())
    if not hasattr(client, "scheduler"):
        client.scheduler = _SchedulerProxy(client)
    if not hasattr(client, "_identity_key"):
        client._identity_key = lambda cand_account: _identity_key(client, cand_account)


def cleanup_stale_colab_state(client: Client, cand_account: str, desired_session: str) -> None:
    """Clear stale allocated sessions, uncertain flags, and journals when assignment_count == 0."""
    ensure_client_failover_helpers(client)
    try:
        obs = client._assignment_state()
        assignment_count = obs.get("assignment_count", 0) if obs.get("verified") else 0
    except Exception:
        assignment_count = 0

    if assignment_count == 0:
        logger.info(f"Account {cand_account} has 0 active Colab assignments; clearing stale allocation state.")
        acct_budget = client.budgets.load_account(cand_account)
        for old_sess in list(acct_budget.allocated_sessions):
            client.budgets.record_stop(cand_account, old_sess, "stale_cleanup")
        acct_budget.uncertain_allocations.clear()
        client.budgets.save_account(acct_budget)
        client.scheduler.clear_session_journal(cand_account, client._identity_key(cand_account))
    else:
        logger.warning(
            f"Account {cand_account} has {assignment_count} active assignments; skipping destructive state clear."
        )

SENTENCE_RE = re.compile(r'(?<=[.!?…;])\s+|(?<=[.!?…;]["\'”’])\s+')
SENTENCE_END_CHARS = ('.', '!', '?', '…', ';', ':', '”', '"', '’', "'")


def resolve_channel_ids(raw_id: str) -> Tuple[str, str]:
    """Normalize user channel identifier into (channel_id, channel_slug)."""
    clean = raw_id.strip()
    if clean.startswith("channel-"):
        clean = clean[len("channel-"):]
    if clean.startswith("ch_"):
        clean = clean[len("ch_"):]
    channel_id = clean.replace("-", "_")
    channel_slug = clean.replace("_", "-")
    return channel_id, channel_slug


def get_channel_slice(channel_id: str) -> Tuple[List[str], List[str], str]:
    """Return (flow_profiles, colab_accounts, session_name) for a channel from contract §1."""
    part = CHANNEL_RESOURCE_PARTITIONS.get(channel_id)
    if part:
        return (
            list(part["flow_profiles"]),
            list(part["colab_accounts"]),
            part["session"],
        )
    slug = channel_id.replace("_", "-")
    return (
        ["profile_1", "profile_3", "profile_4"],
        ["account-01"],
        f"vp-{slug}",
    )


def resolve_asset_path(candidate: str | Path, sys_dir: Path, root_dir: Path) -> Optional[Path]:
    """Resolve an asset path against multiple potential root directories."""
    p = Path(candidate)
    if p.is_file():
        return p
    for base in [root_dir, sys_dir, Path("/home/hongphuoc6104/Desktop/vp-agent-core")]:
        cand = base / p
        if cand.is_file():
            return cand
    return None


def find_voice_profile(sys_dir: Path, channel_id: str, channel_slug: str) -> Tuple[Path, Dict[str, Any]]:
    """Locate channel voice profile and ensure local presence inside sys_dir/assets/voices/ch_<channel_id>."""
    target_dir = sys_dir / f"assets/voices/ch_{channel_id}"
    local_profile = target_dir / "profile.json"
    if local_profile.is_file() and (target_dir / "reference.wav").is_file():
        return local_profile, json.loads(local_profile.read_text(encoding="utf-8"))

    candidates = [
        sys_dir / f"assets/voices/ch_{channel_id}/profile.json",
        sys_dir / f"assets/voices/{channel_id}/profile.json",
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/ch_{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/voices/{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/voices/ch_{channel_id}/profile.json"),
        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/voices/{channel_id}/profile.json"),
    ]
    found_profile: Optional[Path] = None
    for p in candidates:
        if p.is_file():
            found_profile = p
            break

    if not found_profile:
        fallback = sys_dir / "assets/voices/viet_narrator/profile.json"
        if not fallback.is_file():
            fallback = Path("/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/voices/viet_narrator/profile.json")
        found_profile = fallback

    profile_data = json.loads(found_profile.read_text(encoding="utf-8"))
    ref_name = profile_data.get("reference_wav", "reference.wav")
    src_ref = found_profile.parent / ref_name

    target_dir.mkdir(parents=True, exist_ok=True)
    if found_profile.resolve() != local_profile.resolve():
        shutil.copy2(found_profile, local_profile)
    if src_ref.is_file() and not (target_dir / ref_name).is_file():
        shutil.copy2(src_ref, target_dir / ref_name)

    return local_profile, profile_data


def split_long_sentence_at_middle_comma(sentence: str) -> List[str]:
    """If sentence has > 18 words and contains commas, split at the comma closest to the middle."""
    words = sentence.split()
    if len(words) <= 18 or "," not in sentence:
        return [sentence]

    comma_indices = [m.start() for m in re.finditer(r",", sentence)]
    if not comma_indices:
        return [sentence]

    target_mid = len(words) / 2.0
    best_idx = -1
    best_diff = float("inf")

    for idx in comma_indices:
        before = sentence[:idx].strip()
        after = sentence[idx + 1:].strip()
        w1 = len(before.split())
        w2 = len(after.split())
        if w1 == 0 or w2 == 0:
            continue
        diff = abs(w1 - target_mid)
        if diff < best_diff:
            best_diff = diff
            best_idx = idx

    if best_idx == -1:
        return [sentence]

    part1 = sentence[:best_idx].strip()
    part2 = sentence[best_idx + 1:].strip()

    res = [part1]
    if len(part2.split()) > 18 and "," in part2:
        res.extend(split_long_sentence_at_middle_comma(part2))
    else:
        res.append(part2)

    return res


def split_into_clauses(text: str) -> List[str]:
    """Split narration into natural spoken clauses/sentences for OmniVoice."""
    clean = text.strip()
    if not clean:
        return []

    raw_sentences = [s.strip() for s in SENTENCE_RE.split(clean) if s.strip()]
    clauses: List[str] = []
    for s in raw_sentences:
        clauses.extend(split_long_sentence_at_middle_comma(s))

    return [c for c in clauses if c]


def concat_mono_pcm16_wavs(wav_paths: List[Path], out_wav: Path) -> None:
    """Concatenate 48kHz mono PCM16 WAV files without transcoding loss."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as outfile:
        outfile.setnchannels(1)
        outfile.setsampwidth(2)
        outfile.setframerate(48000)
        for p in wav_paths:
            with wave.open(str(p), "rb") as infile:
                if (infile.getnchannels(), infile.getsampwidth(), infile.getframerate()) != (1, 2, 48000):
                    tmp_conv = p.with_name(f"conv_{p.name}")
                    cmd = [
                        "ffmpeg", "-y", "-i", str(p),
                        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
                        str(tmp_conv),
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    with wave.open(str(tmp_conv), "rb") as cin:
                        outfile.writeframes(cin.readframes(cin.getnframes()))
                    tmp_conv.unlink(missing_ok=True)
                else:
                    outfile.writeframes(infile.readframes(infile.getnframes()))


def append_silence_to_wav(wav_path: Path, silence_seconds: float = 1.2) -> None:
    """Append uncompressed zero-PCM16 frames to WAV file to pad endcard hold duration."""
    with wave.open(str(wav_path), "rb") as r:
        nchannels = r.getnchannels()
        sampwidth = r.getsampwidth()
        framerate = r.getframerate()
        frames = r.readframes(r.getnframes())

    num_silence_frames = int(framerate * silence_seconds)
    silence_bytes = b"\x00" * (num_silence_frames * nchannels * sampwidth)

    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(nchannels)
        w.setsampwidth(sampwidth)
        w.setframerate(framerate)
        w.writeframes(frames + silence_bytes)


_STICKMAN_LEAK_RE = re.compile(
    r"\b(?:bald\s+circle\s+stickman|circle\s+stickman|stickman\s+character|stickman\s+protagonist|stick\s+figure|stickman|người\s+que)\b",
    re.IGNORECASE,
)
_WHITE_CANVAS_LEAK_RE = re.compile(
    r"\b(?:on\s+pure\s+white\s+#FFFFFF\s+canvas|on\s+pure\s+white\s+canvas|on\s+clean\s+white\s+canvas|on\s+flat\s+white\s+canvas|on\s+pure\s+white\s+background)\b",
    re.IGNORECASE,
)


def _sanitize_non_stickman_text(text: str, ch: Any) -> str:
    """Strip leaked stickman or pure-white-canvas tokens when channel is non-stickman."""
    if not text:
        return ""
    profile_id = getattr(getattr(ch, "visual", None), "profile_id", "") or ""
    if profile_id in ("ch_stickman_doodle", "handdrawn_2d_explainer", "1.7.0"):
        return text
    cast_app = getattr(getattr(ch, "visual", None), "cast_appearance", "") or ""
    is_char_free = "Character-free" in cast_app
    replacement_actor = "focal subject" if is_char_free else "expressive protagonist"
    cleaned = _STICKMAN_LEAK_RE.sub(replacement_actor, text)
    palette = getattr(getattr(ch, "visual", None), "palette", None) or ["#F5EFE0"]
    bg_hex = palette[0] if palette else "#F5EFE0"
    cleaned = _WHITE_CANVAS_LEAK_RE.sub(f"on textured {bg_hex} art surface", cleaned)
    return cleaned


def compile_channel_scene_prompt(
    ch: Any,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    sc: Dict[str, Any],
    img: Dict[str, Any],
    aspect_ratio: str = "9:16",
) -> str:
    """Compile custom channel scene prompt adhering to each channel's distinct visual identity."""
    orient = "vertical" if aspect_ratio == "9:16" else "horizontal widescreen"
    s1 = (
        f"Requested aspect ratio: {aspect_ratio}. Render a complete 100% full-bleed {orient} {aspect_ratio} "
        "2D illustration extending continuously to all four edges with zero letterbox bars, zero subtitle boxes, "
        "zero UI chrome, and zero dark vignette."
    )
    palette_str = ", ".join(ch.visual.palette) if hasattr(ch.visual, "palette") else "#FFFFFF"
    s2 = f"Visual Style ({ch.visual.profile_id}): {brief.get('style') or ch.visual.style_description} Palette: {palette_str}."

    has_char = bool(img.get("has_character", True))
    if not has_char:
        s3 = CHARACTER_FREE_DIRECTIVE
    elif "Character-free" in getattr(ch.visual, "cast_appearance", ""):
        s3 = f"Visual Elements: {ch.visual.cast_appearance}."
    else:
        char_map = {c["id"]: c for c in content.get("characters", [])}
        cids = img.get("character_ids") or sc.get("character_ids") or []
        char_descs = []
        for cid in cids:
            c = char_map.get(cid)
            if c:
                app_txt = _sanitize_non_stickman_text(c.get("appearance", ""), ch)
                out_txt = _sanitize_non_stickman_text(c.get("outfit", ""), ch)
                char_descs.append(
                    f"Character {c.get('name', cid)}: {app_txt}. Outfit: {out_txt}."
                )
        if char_descs:
            s3 = " ".join(char_descs)
        else:
            s3 = f"Character: {ch.visual.cast_appearance}. Outfit: {ch.visual.outfit}."

    # Variation / based_on handling
    based_on = img.get("based_on")
    if based_on:
        preserve_txt = _sanitize_non_stickman_text(
            img.get("preserve", "same character design, stage lighting and palette"), ch
        )
        change_txt = _sanitize_non_stickman_text(img.get("change", img.get("description", "")), ch)
        s4 = (
            f"Variation Shot (based on {based_on}): Maintain continuous visual continuity with the established scene. "
            f"Preserve strictly: {preserve_txt}. Visible change: {change_txt}."
        )
    else:
        desc_txt = _sanitize_non_stickman_text(img.get("description", ""), ch)
        s4 = f"Scene Composition & Action: {desc_txt}"

    # Lettering & emphasis text handling
    emphasis_text = img.get("emphasis_text")
    visible_text = img.get("visible_text") or []
    lang_label = "English" if getattr(ch, "language", "vi") == "en" else "Vietnamese"

    if emphasis_text:
        s5 = (
            f"Emphasis lettering instruction: render exact uppercase {lang_label} hand-lettered text in the upper third "
            f"of the frame (strictly <= 10% frame height, 1-4 uppercase words, native hand-lettering integrated directly "
            f"onto the flat canvas, strictly zero rectangular text cards, banners, or gradient overlays covering artwork): \"{emphasis_text}\"."
        )
        if visible_text:
            text_labels = ", ".join(
                f'"{t}"' if isinstance(t, str) else f'"{t.get("text", "")}"'
                for t in visible_text
                if (isinstance(t, str) and t != emphasis_text) or (isinstance(t, dict) and t.get("text") != emphasis_text)
            )
            if text_labels:
                s5 += f" Additional compact labels (< 5% frame height): {text_labels}."
    elif visible_text:
        text_labels = ", ".join(
            f'"{t}"' if isinstance(t, str) else f'"{t.get("text", "")}"' for t in visible_text
        )
        s5 = f"Render concise uppercase {lang_label} hand-lettered labels (< 5% frame height) for exact text: {text_labels}."
    else:
        s5 = "Strict zero-text policy: render zero words, letters, numbers, speech bubbles, or watermarks anywhere in the frame."

    return f"{s1}\n\n{s2}\n\n{s3}\n\n{s4}\n\n{s5}"


def compile_channel_thumb_prompt(
    ch: Any,
    brief: Dict[str, Any],
    thumb_prompt: str,
    thumb_text: str,
    aspect_ratio: str = "9:16",
) -> str:
    """Compile high-CTR 60/40 poster thumbnail prompt with extreme focal scale and bold outlined typography."""
    orient = "vertical" if aspect_ratio == "9:16" else "horizontal widescreen"
    s1 = (
        f"Requested aspect ratio: {aspect_ratio}. Render a complete 100% full-bleed {orient} {aspect_ratio} "
        "high-impact YouTube poster thumbnail illustration extending continuously to all four edges with zero letterbox bars, "
        "zero UI chrome, and zero dark vignette."
    )
    palette = list(ch.visual.palette) if hasattr(ch.visual, "palette") and ch.visual.palette else ["#1E293B", "#FACC15", "#EF4444"]
    palette_str = ", ".join(palette)
    s2 = f"Visual Style ({ch.visual.profile_id}): {ch.visual.style_description} High-Contrast Poster Palette: {palette_str}."
    s3 = f"Character Cast: {ch.visual.cast_appearance}. Outfit: {ch.visual.outfit}."
    clean_thumb_scene = _sanitize_non_stickman_text(thumb_prompt, ch)
    s4 = (
        f"High-CTR 60/40 Poster Composition ({ch.visual.thumbnail_rule}): "
        f"Extreme close-up focal subject and dramatic visual contrast occupying 60% of the frame with immediate mobile readability "
        f"(never tiny objects lost in empty white space). Visual Scene: {clean_thumb_scene}"
    )
    s5 = (
        f"Bold Poster Typography (~25-30% of frame in upper or left high-contrast zone): render massive, ultra-legible "
        f"hand-lettered uppercase hook text in high-contrast bright yellow (#FACC15) or crisp white (#FFFFFF) with a thick black (#000000) "
        f"stroke integrated directly onto the canvas (strictly zero rectangular text cards, banners, or extra filler words): \"{thumb_text}\""
    )
    return f"{s1}\n\n{s2}\n\n{s3}\n\n{s4}\n\n{s5}"


def stage_a_images(
    sys_dir: Path,
    job_dir: Path,
    channel_id: str,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    format_profile: str = "short_9x16",
    flow_profiles_arg: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute Stage A: Flow CDP Full-Frame Images + Native Thumbnail.

    Handles:
    - reuse_from: copies existing image & sidecar JSON without regenerating
    - is_endcard: copies channel asset endcard_{aspect}
    - based_on: compiles variation prompt & wires parent DAG dependency
    - focus-crop beats: skips generation (crop is performed at render time)
    - emphasis_text: complies with <=10% lettering constraint
    """
    aspect_ratio = "16:9" if format_profile == "long_16x9" else "9:16"
    target_size = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
    aspect_tag = "16x9" if aspect_ratio == "16:9" else "9x16"

    logger.info(
        f"[*] GIAI ĐOẠN A: Kiểm tra và chuẩn bị ảnh Flow CDP cho {job_dir.name} "
        f"(kênh: {channel_id}, định dạng: {aspect_ratio})..."
    )
    img_rev_dir = job_dir / "revisions/images/1"
    img_rev_dir.mkdir(parents=True, exist_ok=True)

    is_nao_luoi = (channel_id == "nao_luoi")
    ch_profile = None if is_nao_luoi else get_channel(channel_id)
    root_dir = sys_dir.parent
    channel_slug = channel_id.replace("_", "-")

    items_to_generate: List[Dict[str, Any]] = []

    for sc in content.get("scenes", []):
        for img in sc.get("images", []):
            req_id = img["id"]
            shot = img.get("shot_type", "full_scene")
            target_jpg = img_rev_dir / f"{req_id}_{aspect_tag}.jpg"
            target_json = img_rev_dir / f"{req_id}_{aspect_tag}.json"

            # 1. Skip focus-crop beats
            spec_str = str(img.get("spec", ""))
            if spec_str.startswith("crop:") or img.get("is_crop"):
                logger.info(f"  [>] Visual {req_id} là focus-crop beat ({spec_str}) -> Bỏ qua sinh ảnh Flow.")
                continue

            # 2. Check is_endcard
            if img.get("is_endcard") or spec_str == "endcard":
                endcard_asset_jpg = sys_dir / f"channels/{channel_id}/assets/endcard_{aspect_tag}.jpg"
                endcard_asset_json = sys_dir / f"channels/{channel_id}/assets/endcard_{aspect_tag}.json"
                if not endcard_asset_jpg.is_file():
                    for alt_base in [
                        sys_dir / f"assets/channels/{channel_id}",
                        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/channels/{channel_id}/assets"),
                        Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/assets/channels/{channel_id}"),
                        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/channels/{channel_id}/assets"),
                        Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/assets/channels/{channel_id}"),
                    ]:
                        alt_jpg = alt_base / f"endcard_{aspect_tag}.jpg"
                        if alt_jpg.is_file():
                            endcard_asset_jpg = alt_jpg
                            alt_json = alt_base / f"endcard_{aspect_tag}.json"
                            if alt_json.is_file():
                                endcard_asset_json = alt_json
                            break
                if endcard_asset_jpg.is_file():
                    shutil.copy2(endcard_asset_jpg, target_jpg)
                    if endcard_asset_json.is_file():
                        shutil.copy2(endcard_asset_json, target_json)
                    else:
                        sidecar = {
                            "jobId": req_id,
                            "forgeId": f"channel-endcard-{channel_id}-{aspect_tag}",
                            "aspect_ratio": aspect_ratio,
                            "prompt": f"Endcard for {channel_id}",
                            "status": "verified",
                        }
                        target_json.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    logger.info(f"  [✓] Visual {req_id} (Endcard) sao chép từ channel asset: {endcard_asset_jpg}")
                    items_to_generate.append({
                        "id": req_id,
                        "scene_id": sc["id"],
                        "prompt": f"Endcard for {channel_id}",
                        "target_jpg": target_jpg,
                        "target_json": target_json,
                        "aspect": aspect_ratio,
                        "is_thumb": False,
                        "based_on": None,
                        "base_media_id": None,
                        "shot_type": "full_scene",
                    })
                    continue
                else:
                    logger.warning(f"Endcard asset chưa tồn tại tại {endcard_asset_jpg}, sẽ tạo mới qua Flow.")

            # 3. Check reuse_from
            reuse_ref = img.get("reuse_from")
            if reuse_ref:
                src_path = resolve_asset_path(reuse_ref, sys_dir, root_dir)
                if src_path and src_path.is_file():
                    shutil.copy2(src_path, target_jpg)
                    src_json = src_path.with_suffix(".json")
                    if src_json.is_file():
                        shutil.copy2(src_json, target_json)
                        # Ensure forgeId / media_id exists in sidecar
                        try:
                            meta = json.loads(target_json.read_text(encoding="utf-8"))
                            if not meta.get("forgeId") and not meta.get("media_id"):
                                meta["forgeId"] = f"reused-{src_path.stem}"
                                target_json.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                        except Exception:
                            pass
                    else:
                        sidecar = {
                            "jobId": req_id,
                            "forgeId": f"reused-{src_path.stem}",
                            "aspect_ratio": aspect_ratio,
                            "prompt": f"Reused from {reuse_ref}",
                            "status": "verified",
                        }
                        target_json.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    logger.info(f"  [✓] Visual {req_id} (reuse_from) sao chép từ {src_path}")
                    items_to_generate.append({
                        "id": req_id,
                        "scene_id": sc["id"],
                        "prompt": f"Reused from {reuse_ref}",
                        "target_jpg": target_jpg,
                        "target_json": target_json,
                        "aspect": aspect_ratio,
                        "is_thumb": False,
                        "based_on": None,
                        "base_media_id": None,
                        "shot_type": shot,
                    })
                    continue
                else:
                    logger.warning(f"reuse_from không tìm thấy file tại '{reuse_ref}', sẽ tạo mới qua Flow.")

            # 4. Compile prompt for new generation
            shot = img.get("shot_type", "full_scene")
            emphasis_text = img.get("emphasis_text")
            allowed_text = list(img.get("visible_text") or [])
            if emphasis_text and not any(
                (isinstance(t, str) and t == emphasis_text) or (isinstance(t, dict) and t.get("text") == emphasis_text)
                for t in allowed_text
            ):
                allowed_text.append({
                    "text": emphasis_text,
                    "is_emphasis": True,
                    "placement": "upper-third",
                    "max_height": 0.10,
                })

            if is_nao_luoi:
                effective_shot = "full_scene" if shot == "variation" else (
                    shot if shot in (
                        "full_scene",
                        "macro_prop",
                        "white_card",
                        "white_isolated",
                        "concept_metaphor",
                        "visual_diagram",
                        "cutaway_detail",
                        "still_life",
                        "environment",
                    ) else "full_scene"
                )
                flow_data: Dict[str, Any] = {
                    "description": img["description"],
                    "aspect_ratio": aspect_ratio,
                    "allowed_text": allowed_text,
                    "shot_type": effective_shot,
                    "has_character": img.get("has_character", True),
                    "character_free": not img.get("has_character", True),
                }
                if emphasis_text:
                    flow_data["emphasis_text"] = emphasis_text
                if img.get("preserve") and flow_data.get("base_reference"):
                    flow_data["preserve"] = [img["preserve"]] if isinstance(img["preserve"], str) else img["preserve"]
                if img.get("change") and flow_data.get("base_reference"):
                    flow_data["change"] = [img["change"]] if isinstance(img["change"], str) else img["change"]

                compiled = compile_flow_prompt(
                    "NanoBanana2Lite",
                    "scene",
                    flow_data,
                    version="1.7.0",
                )
                final_prompt = compiled["prompt"]
            else:
                final_prompt = compile_channel_scene_prompt(
                    ch_profile, brief, content, sc, img, aspect_ratio=aspect_ratio
                )

            # Optional Google First-Party Tools integration (Shot Explorer & Story Sketch)
            try:
                from flow_video.google_first_party_tools import ShotExplorerEngine, StorySketchEngine

                if img.get("camera_preset"):
                    angle_directive = ShotExplorerEngine.build_camera_angle_prompt(str(img["camera_preset"]))
                    final_prompt = f"{angle_directive}. {final_prompt}"
                if img.get("based_on") and img.get("story_sketch_chain"):
                    final_prompt = StorySketchEngine.build_shot_prompt(
                        final_prompt, parent_media_id=str(img["based_on"])
                    )
            except Exception:
                pass

            # Check if parent image sidecar has forgeId / media_id for based_on
            parent_base_media_id = None
            if img.get("based_on"):
                parent_id = img["based_on"]
                parent_json = img_rev_dir / f"{parent_id}_{aspect_tag}.json"
                if parent_json.is_file():
                    try:
                        p_meta = json.loads(parent_json.read_text(encoding="utf-8"))
                        parent_base_media_id = p_meta.get("forgeId") or p_meta.get("media_id")
                    except Exception:
                        pass
                else:
                    # Check if parent_id actually exists in job scenes
                    parent_exists_in_job = any(
                        im.get("id") == parent_id
                        for sc_check in content.get("scenes", [])
                        for im in sc_check.get("images", [])
                    )
                    if not parent_exists_in_job:
                        logger.warning(
                            f"  [!] Visual {req_id} có based_on='{parent_id}' không tồn tại trong job -> hủy based_on."
                        )
                        img["based_on"] = None

            items_to_generate.append({
                "id": req_id,
                "scene_id": sc["id"],
                "prompt": final_prompt,
                "target_jpg": target_jpg,
                "target_json": target_json,
                "aspect": aspect_ratio,
                "is_thumb": False,
                "based_on": img.get("based_on"),
                "base_media_id": parent_base_media_id,
                "reference_media_ids": img.get("reference_media_ids") or ([parent_base_media_id] if parent_base_media_id else None),
                "camera_preset": img.get("camera_preset"),
                "story_sketch_chain": img.get("story_sketch_chain"),
                "shot_type": shot,
            })

    # Native Thumbnail item
    thumb_id = f"THUMBNAIL_{aspect_tag}"
    thumb_jpg = img_rev_dir / f"{thumb_id}.jpg"
    thumb_json = img_rev_dir / f"{thumb_id}.json"
    thumb_spec = brief.get("packaging", {}).get("thumbnail_spec", {})
    thumb_prompt = thumb_spec.get("thumbnail_prompt") or thumb_spec.get("visual_hook", "Minimal flat doodle canvas.")
    thumb_text = thumb_spec.get("text_overlay", "VIDEO PILOT")

    if is_nao_luoi:
        thumb_compiled = compile_flow_prompt(
            "NanoBanana2Lite",
            "scene",
            {
                "description": thumb_prompt,
                "aspect_ratio": aspect_ratio,
                "allowed_text": [thumb_text] if thumb_text else [],
                "shot_type": "full_scene",
                "has_character": True,
                "character_free": False,
            },
            version="1.7.0",
        )
        final_thumb_prompt = thumb_compiled["prompt"]
    else:
        final_thumb_prompt = compile_channel_thumb_prompt(
            ch_profile, brief, thumb_prompt, thumb_text, aspect_ratio=aspect_ratio
        )

    items_to_generate.append({
        "id": thumb_id,
        "scene_id": "THUMBNAIL",
        "prompt": final_thumb_prompt,
        "target_jpg": thumb_jpg,
        "target_json": thumb_json,
        "aspect": aspect_ratio,
        "is_thumb": True,
        "based_on": None,
        "base_media_id": None,
        "shot_type": "full_scene",
    })

    # Filter items that already exist on disk and pass verification
    pending_items: List[Dict[str, Any]] = []
    for it in items_to_generate:
        jpg = it["target_jpg"]
        js = it["target_json"]
        if jpg.is_file() and js.is_file() and jpg.stat().st_size > 5000:
            try:
                with Image.open(jpg) as im:
                    im.verify()
                meta = json.loads(js.read_text(encoding="utf-8"))
                if meta.get("forgeId") or meta.get("media_id"):
                    continue
            except Exception:
                pass
        pending_items.append(it)

    if not pending_items:
        logger.info(f"  [✓] Toàn bộ {len(items_to_generate)} ảnh cảnh và Thumbnail đã tồn tại hợp lệ. Bỏ qua Flow CDP!")
    else:
        logger.info(f"  [+] Cần sinh mới trên Flow CDP: {len(pending_items)}/{len(items_to_generate)} ảnh...")
        from flow_cdp.cdp_direct_client import PROFILES
        from flow_cdp.persistent_pool import PersistentWorkerPool

        # Resolve assigned profiles (prioritize matched, then append all healthy VN standby profiles)
        matched: List[Dict[str, Any]] = []
        if flow_profiles_arg:
            allowed_set = {p.strip() for p in flow_profiles_arg.split(",") if p.strip()}
            matched = [p for p in PROFILES if p.get("name") in allowed_set or p.get("id") in allowed_set]
            if not matched:
                logger.warning(f"No profiles matched '{flow_profiles_arg}', using available profiles.")
        else:
            part_profiles, _, _ = get_channel_slice(channel_id)
            matched = [p for p in PROFILES if p.get("name") in part_profiles or p.get("id") in part_profiles]

        standby_vn_profiles = [
            p
            for p in PROFILES
            if p not in matched
            and not str(p.get("name", "")).startswith("profile_en")
            and p.get("name") != "profile_11"
        ]
        try:
            from flow_cdp.credit_ledger import CreditLedger

            _ledger = CreditLedger()
            standby_vn_profiles.sort(
                key=lambda p: _ledger.get_balance(str(p.get("name") or p.get("id") or ""))
            )
        except Exception:
            pass
        assigned_profiles = matched + standby_vn_profiles

        from flow_cdp.lifecycle import calculate_optimal_workers

        env_workers = os.environ.get("VP_WORKERS_PER_JOB", "").strip()
        if env_workers:
            req_workers = int(env_workers)
            pool_cap = len(matched) if (flow_profiles_arg and matched) else len(assigned_profiles)
        else:
            req_workers = calculate_optimal_workers(len(pending_items), max_cap=10, min_cap=1)
            pool_cap = len(matched) if (flow_profiles_arg and matched) else len(assigned_profiles)
        pacing_sec = float(os.environ.get("VP_FLOW_PACING_SECONDS", str(DEFAULT_FLOW_PACING_SECONDS)))
        workers_count = max(1, min(pool_cap, req_workers))
        logger.info(
            f"  [+] Khởi tạo PersistentWorkerPool ({workers_count} active / {len(assigned_profiles)} slice profiles: "
            f"{[p['name'] for p in assigned_profiles]}, pacing={pacing_sec:.1f}s)..."
        )
        pool = PersistentWorkerPool(
            target_workers=workers_count,
            profiles=assigned_profiles,
            cooldown_seconds=float(os.environ.get("VP_FLOW_COOLDOWN_SECONDS", "45.0")),
            pacing_seconds=pacing_sec,
            stagger_seconds=1.0,
            headless=True,
            default_out_dir=img_rev_dir,
        )
        with pool:
            for it in pending_items:
                task_spec = {
                    "id": it["id"],
                    "prompt": it["prompt"],
                    "ratio": it["aspect"],
                    "filename": it["target_jpg"].name,
                    "out_dir": str(img_rev_dir),
                    "editorial_overlay": {"enabled": False},
                    "shot_type": it.get("shot_type", "full_scene"),
                }
                if it.get("is_thumb"):
                    task_spec["model"] = "GEM_PIX_2"
                if it.get("based_on"):
                    task_spec["based_on"] = it["based_on"]
                if it.get("base_media_id"):
                    task_spec["baseMediaId"] = it["base_media_id"]
                if it.get("reference_media_ids"):
                    task_spec["reference_media_ids"] = it["reference_media_ids"]
                if it.get("camera_preset"):
                    task_spec["camera_preset"] = it["camera_preset"]
                if it.get("story_sketch_chain"):
                    task_spec["story_sketch_chain"] = it["story_sketch_chain"]

                pool.submit_task(task_spec)

            timeout_sec = max(300.0, len(pending_items) * 75.0)
            completed = pool.wait_completion(timeout=timeout_sec)
            if not completed or pool.shared_queue.qsize() > 0:
                raise RuntimeError(f"Flow pool timeout hoặc chưa hoàn tất: {pool.get_status()}")

    # Verify and ensure resolution with PIL
    for it in items_to_generate:
        jpg = it["target_jpg"]
        if not jpg.is_file():
            raise FileNotFoundError(f"Missing output image file: {jpg}")
        with Image.open(jpg) as im:
            if im.size != target_size:
                im_resized = im.resize(target_size, Image.Resampling.LANCZOS)
                im_resized.save(jpg, format="JPEG", quality=95)
            else:
                im.verify()

        js = it["target_json"]
        if not js.is_file():
            sidecar_data = {
                "jobId": it["id"],
                "forgeId": f"local-{it['id']}",
                "aspect_ratio": it["aspect"],
                "prompt": it["prompt"],
                "status": "verified",
            }
            js.write_text(json.dumps(sidecar_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Copy thumbnail to job_dir root
    dest_thumb = job_dir / f"thumbnail_{aspect_tag}.jpg"
    if thumb_jpg.is_file():
        shutil.copy2(thumb_jpg, dest_thumb)

    # Build output manifest
    manifest_items = []
    files_list = []
    for it in items_to_generate:
        files_list.append(f"revisions/images/1/{it['target_jpg'].name}")
        files_list.append(f"revisions/images/1/{it['target_json'].name}")
        if not it["is_thumb"]:
            sha = hashlib.sha256(it["target_jpg"].read_bytes()).hexdigest()
            manifest_items.append({
                "image_id": it["id"],
                "scene_id": it["scene_id"],
                "path": f"revisions/images/1/{it['target_jpg'].name}",
                "prompt": it["prompt"],
                "sha256": sha,
                "ratio": it["aspect"],
            })

    images_output = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "images",
        "revision": 1,
        "files": files_list,
        "items": manifest_items,
        "payload": {
            "items": manifest_items,
            "thumbnail": f"revisions/images/1/THUMBNAIL_{aspect_tag}.jpg",
            "format": aspect_ratio,
        },
        "checks": {"passed": True, "errors": []},
    }
    (img_rev_dir / "output.json").write_text(json.dumps(images_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    images_manifest = {"checkpoint": "final", "items": manifest_items}
    (img_rev_dir / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (job_dir / "images.json").write_text(json.dumps(images_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(f"  [✓] Giai đoạn A hoàn tất: {len(manifest_items)} ảnh cảnh + 1 Thumbnail ({aspect_ratio})")
    return images_output


def stage_b_audio(
    sys_dir: Path,
    job_dir: Path,
    channel_id: str,
    channel_slug: str,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    format_profile: str = "short_9x16",
    colab_account: Optional[str] = None,
    session_name: Optional[str] = None,
    force_audio: bool = False,
) -> Tuple[Dict[str, Any], Optional[Client], Optional[str]]:
    """Execute Stage B: OmniVoice TTS synthesis on Colab T4 with trailing silence for endcards."""
    aspect_ratio = "16:9" if format_profile == "long_16x9" else "9:16"
    logger.info(f"[*] GIAI ĐOẠN B: Tổng hợp giọng kể OmniVoice cho {job_dir.name} ({format_profile})...")
    audio_rev_dir = job_dir / "revisions/audio/1"
    audio_rev_dir.mkdir(parents=True, exist_ok=True)

    narration_wav = audio_rev_dir / "narration.wav"
    audio_out_json = audio_rev_dir / "output.json"
    subtitles_srt = audio_rev_dir / "subtitles.srt"

    # Reuse if already valid and force_audio is False
    if not force_audio and narration_wav.is_file() and audio_out_json.is_file() and subtitles_srt.is_file():
        try:
            saved = json.loads(audio_out_json.read_text(encoding="utf-8"))
            payload = saved.get("payload", saved)
            if payload.get("duration") and payload.get("segments") and payload.get("tracks"):
                logger.info(
                    f"  [✓] Âm thanh đã tồn tại hợp lệ ({payload['duration']:.2f}s). "
                    "Bỏ qua tái tổng hợp (dùng --force-audio nếu muốn tạo lại)."
                )
                return payload, None, payload.get("account_used")
        except Exception:
            pass

    # Pre-TTS lint check before synthesizing NEW audio on Colab
    try:
        from tools import editorial_value_linter, script_diversity_linter

        strict_anti_ai = os.environ.get("VP_STRICT_ANTI_AI", "0") in ("1", "true", "True")
        brief_file = job_dir / "brief.json"
        brief_data = (
            json.loads(brief_file.read_text(encoding="utf-8"))
            if brief_file.is_file()
            else {"format_profile": format_profile}
        )

        ed_report = editorial_value_linter.lint_editorial_and_narrative_quality(brief_data, content)
        if not ed_report.get("passed", True):
            err_msgs = "; ".join(ed_report.get("errors", []))
            msg = f"Pre-TTS Editorial Lint Failed: {err_msgs}"
            if strict_anti_ai:
                raise ValueError(msg)
            logger.warning(f"  [!] CẢNH BÁO PRE-TTS (Editorial): {msg}")

        scenes = content.get("scenes", [])
        div_report = script_diversity_linter.lint_script(scenes)
        if div_report.get("status") == "FAILED" or div_report.get("total_violations", 0) > 0:
            viols = [
                f"{v.get('type')}: {v.get('matched_text') or v.get('keyword') or v.get('message') or ''}"
                for v in div_report.get("violations", [])[:5]
            ]
            msg = f"Pre-TTS Script Diversity Violations ({div_report.get('total_violations')}): {'; '.join(viols)}"
            if strict_anti_ai:
                raise ValueError(msg)
            logger.warning(f"  [!] CẢNH BÁO PRE-TTS (Diversity/AI Cliché): {msg}")
    except ValueError:
        raise
    except Exception as exc:
        logger.warning(f"  [!] Pre-TTS lint check bypassed due to exception: {exc}")

    # Resolve voice profile
    profile_path, profile = find_voice_profile(sys_dir, channel_id, channel_slug)
    voice_name = profile.get("voice", f"VietNarrator_{channel_slug}")
    rel_profile = str(profile_path.relative_to(sys_dir))

    tts_speed = float(profile.get("recommended_speed", profile.get("source_speed", 1.0)))
    target_lufs = float(profile.get("audio_lufs", -14.0))
    target_peak = float(profile.get("audio_peak_db", -1.5))
    voice_chain = profile.get("audio_voice_chain") or ap.VOICE_CHAIN

    # Build scenes plan with natural human breathing jitter and situation-aware prosody
    scenes = content.get("scenes", [])
    scenes_plan: List[Dict[str, Any]] = []
    default_tone = profile.get("default_tone") or "narrative_warm"
    for sc_idx, sc in enumerate(scenes):
        narration = sc.get("narration", "").strip()
        norm_narration = normalize_for_tts(narration)
        clauses = split_into_clauses(norm_narration)
        if not clauses:
            clauses = [norm_narration]
        sc_sit = str(sc.get("narrative_situation") or sc.get("narrative_role") or "")
        sc_tone = sc.get("tone") or (
            "reflective_slow" if sc_sit in ("slow_reflective", "editorial_commentary", "closing_takeaway")
            else ("analytical_crisp" if sc_sit in ("hook_shock", "rapid_examples", "causal_chain") else default_tone)
        )
        base_comma = 0.07 if sc_sit in ("hook_shock", "rapid_examples") else (0.10 if sc_sit in ("slow_reflective", "editorial_commentary") else 0.08)
        base_sent = 0.14 if sc_sit in ("hook_shock", "rapid_examples") else (0.19 if sc_sit in ("slow_reflective", "editorial_commentary") else 0.16)
        gaps = []
        for c_idx, c in enumerate(clauses[:-1]):
            jitter = (((sc_idx * 7 + c_idx * 13) % 7) - 3) * 0.008
            is_end = c.endswith(SENTENCE_END_CHARS)
            g = round(max(0.06, (base_sent if is_end else base_comma) + jitter), 3)
            gaps.append(g)
        tail_base = 0.21 if sc_sit in ("slow_reflective", "editorial_commentary", "closing_takeaway") else (0.15 if sc_sit == "hook_shock" else 0.18)
        tail_jitter = (((sc_idx * 11) % 5) - 2) * 0.012
        scenes_plan.append({
            "scene_id": sc["id"],
            "texts": clauses,
            "gaps": gaps,
            "tail": round(max(0.12, tail_base + tail_jitter), 3),
            "tone": sc_tone,
        })

    # Resource slice & account selection
    _, part_accounts, default_session = get_channel_slice(channel_id)
    target_account = colab_account or part_accounts[0]
    target_session = session_name or default_session

    base_cfg_path = sys_dir / "config.json"
    cfg: Dict[str, Any] = json.loads(base_cfg_path.read_text(encoding="utf-8")) if base_cfg_path.is_file() else {}
    cfg["voices"] = {"vi": rel_profile, "en": rel_profile}
    cfg["tts_voice"] = voice_name
    cfg["en_voice"] = voice_name
    cfg["tts_speed"] = tts_speed
    cfg["audio_lufs"] = target_lufs
    cfg["audio_peak_db"] = target_peak
    cfg["audio_voice_chain"] = voice_chain

    cfg.setdefault("colab_tts", {})
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["batch_size"] = 1
    cfg["colab_tts"]["num_step"] = 32
    cfg["colab_tts"]["timeout_seconds"] = 3600 if format_profile == "long_16x9" else 1800
    cfg["colab_tts"]["models"] = {
        "vi": {
            "id": "kjanh/KhanhTTS-OmniVoice",
            "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84",
        },
        "en": {
            "id": "kjanh/KhanhTTS-OmniVoice",
            "revision": "20d056b8ea5d8d578b4cbaf1f703012fa3798a84",
        },
    }

    request = build_request(sys_dir, cfg, scenes_plan, assemble=False)
    logger.info(f"Built Colab TTS request ID: {request['request_id']} with {len(request.get('items', []))} items")

    # Prioritize warm T4 accounts first (rotated across jobs), then target channel slice accounts, then verified pool
    warm_pool = ["account-01", "account-10", "account-13"]
    rot = sum(ord(ch) for ch in job_dir.name) % len(warm_pool)
    rotated_warm = warm_pool[rot:] + warm_pool[:rot]
    raw_accounts = (
        ([colab_account] if colab_account else [])
        + rotated_warm
        + [target_account]
        + [a for a in part_accounts if a != target_account]
        + [a for a in VERIFIED_COLAB_ACCOUNTS if a != target_account and a not in part_accounts]
    )
    seen_accounts: set[str] = set()
    accounts_to_try: List[str] = []
    for a in raw_accounts:
        if a and a != "account-02" and a not in seen_accounts:
            seen_accounts.add(a)
            accounts_to_try.append(a)

    account_used: Optional[str] = None
    client_used: Optional[Client] = None
    cache_base = job_dir / "cache/colab-tts"
    cache_base.mkdir(parents=True, exist_ok=True)

    tts_result_pre = audio_rev_dir / "tts-result.json"
    if not force_audio and tts_result_pre.is_file():
        try:
            pre_res = json.loads(tts_result_pre.read_text(encoding="utf-8"))
            pre_segs = pre_res.get("segments", [])
            if pre_segs and all((audio_rev_dir / s["path"]).is_file() for s in pre_segs):
                account_used = str(pre_res.get("account_used") or target_account)
                logger.info(f"  [✓] Tái sử dụng {len(pre_segs)} phân đoạn WAV đã tổng hợp sẵn từ Colab ({account_used})...")
        except Exception:
            account_used = None

    for acc in ([] if account_used else accounts_to_try):
        logger.info(f"Trying Colab OmniVoice synthesis on {acc} ({target_session})...")
        acc_cfg = copy.deepcopy(cfg)
        acc_cfg["colab_tts"]["account"] = acc
        acc_cfg["colab_tts"]["job_id"] = job_dir.name

        try:
            client = Client(sys_dir, acc_cfg)
            client.account = acc

            # Prefer reusing a channel-specific T4 session, otherwise fall back to any active T4 session on this account
            effective_session = target_session
            try:
                snap = client._budgets().snapshot("colab:" + acc)
                allocs = [
                    it["session"]
                    for it in snap.get("allocated_sessions", [])
                    if it.get("device") == "T4"
                    and (it.get("session") == target_session or str(it.get("session", "")).startswith(f"vp-{channel_slug}"))
                ]
                if not allocs:
                    allocs = [
                        it["session"]
                        for it in snap.get("allocated_sessions", [])
                        if it.get("device") == "T4" and it.get("session")
                    ]
                if allocs and effective_session not in allocs:
                    effective_session = allocs[0]
            except Exception:
                pass

            desired_session = effective_session
            client.session = effective_session
            acc_cfg["colab_tts"]["session"] = effective_session

            # Do NOT call destructive client.reconcile() before _ready() when session is already allocated
            client.session = desired_session

            # Or leave uncertain=True blocking start() if assignment_count is 0
            try:
                alias = f"colab:{acc}"
                snap = client._budgets().snapshot(alias)
                if snap.get("uncertain"):
                    cleanup_stale_colab_state(client, acc, desired_session)
                    client.session = desired_session
            except Exception:
                pass

            try:
                client._ready(auto_start=True)
            except (ColabBridgeError, Exception) as ex_ready:
                err_msg = str(ex_ready)
                if any(
                    marker in err_msg
                    for marker in (
                        "COLAB_VERIFIED_SETUP_REQUIRED",
                        "COLAB_UNCERTAIN_ALLOCATION",
                        "COLAB_SINGLE_ACTIVE_SESSION",
                        "already has allocated session",
                    )
                ):
                    logger.warning(
                        f"Account {acc} _ready failed with '{err_msg}'. Inspecting and clearing stale session/journal..."
                    )
                    cleanup_stale_colab_state(client, acc, desired_session)
                    client.session = desired_session
                    try:
                        client._ready(auto_start=True)
                        logger.info(
                            f"Account {acc} recovered and _ready succeeded on retry with session {desired_session}"
                        )
                    except Exception as ex_retry:
                        logger.warning(f"Account {acc} retry after stale cleanup failed: {ex_retry}")
                        raise ex_retry
                else:
                    logger.warning(f"Account {acc} _ready failed: {ex_ready}")
                    raise ex_ready

            client.synthesize(request, audio_rev_dir, cache_base / acc)
            account_used = acc
            client_used = client
            logger.info(f"Colab OmniVoice synthesis succeeded on {acc}")
            break
        except (ColabError, Exception) as ex:
            logger.warning(f"Synthesis on {acc} failed ({type(ex).__name__}): {ex}. Failing over...")
            continue

    if not account_used:
        raise RuntimeError(f"All candidate Colab accounts failed for job {job_dir.name}: {accounts_to_try}")

    # Process segments & word timestamps
    tts_result_file = audio_rev_dir / "tts-result.json"
    if not tts_result_file.is_file():
        raise FileNotFoundError(f"Missing {tts_result_file}")

    tts_res = json.loads(tts_result_file.read_text(encoding="utf-8"))
    synced_segments = tts_res.get("segments", [])

    segments: List[Dict[str, Any]] = []
    wav_parts: List[Path] = []
    current_time = 0.0

    for seg_info in synced_segments:
        sc_id = seg_info["scene_id"]
        text = restore_display_text(seg_info["text"])
        part_wav = audio_rev_dir / seg_info["path"]
        wav_parts.append(part_wav)

        with wave.open(str(part_wav), "rb") as w:
            total_dur = w.getnframes() / w.getframerate()

        content_dur = float(seg_info.get("content_duration", total_dur))
        words = text.split()

        existing_wts = seg_info.get("word_timestamps")
        valid_existing = False
        if isinstance(existing_wts, list) and len(existing_wts) == len(words):
            try:
                prev_e = 0.0
                all_good = True
                for wt in existing_wts:
                    s_rel = float(wt["start"])
                    e_rel = float(wt["end"])
                    if not (0.0 <= prev_e - 0.02 <= s_rel < e_rel <= content_dur + 0.05):
                        all_good = False
                        break
                    prev_e = s_rel
                valid_existing = all_good
            except Exception:
                valid_existing = False

        if valid_existing and existing_wts:
            word_timestamps = [
                {
                    "word": restore_display_text(wt.get("word", "")),
                    "start": wt["start"],
                    "end": wt["end"],
                }
                for wt in existing_wts
            ]
        else:
            word_dur = content_dur / max(1, len(words))
            word_timestamps = []
            for i, w in enumerate(words):
                w_start = round(i * word_dur, 3)
                w_end = round((i + 1) * word_dur, 3)
                if i == len(words) - 1:
                    w_end = min(w_end, round(content_dur, 3))
                    w_end = max(w_end, w_start + 0.01)
                word_timestamps.append({
                    "word": restore_display_text(w),
                    "start": w_start,
                    "end": w_end,
                })

        seg = {
            "scene_id": sc_id,
            "text": text,
            "path": f"revisions/audio/1/{part_wav.name}",
            "start": round(current_time, 3),
            "end": round(current_time + total_dur, 3),
            "content_end": round(current_time + content_dur, 3),
            "word_timestamps": word_timestamps,
        }
        segments.append(seg)
        current_time += total_dur

    # Detect if final visual beat is an endcard
    has_endcard_final_beat = False
    if scenes:
        last_scene = scenes[-1]
        last_beats = last_scene.get("beats", [])
        if last_beats:
            last_beat = last_beats[-1]
            if last_beat.get("is_endcard") or last_beat.get("spec") == "endcard" or last_beat.get("tempo") == "hold":
                has_endcard_final_beat = True
        elif last_scene.get("images"):
            last_img = last_scene["images"][-1]
            if last_img.get("is_endcard") or last_img.get("spec") == "endcard":
                has_endcard_final_beat = True

    # Concatenate & Master
    raw_narration = audio_rev_dir / "narration_raw.wav"
    concat_mono_pcm16_wavs(wav_parts, raw_narration)

    # Pad with ~1.2s trailing silence if endcard beat
    silence_added = 0.0
    if has_endcard_final_beat:
        silence_added = 1.2
        logger.info(f"  [+] Cuối video có endcard beat: đệm {silence_added}s yên lặng vào đuôi WAV...")
        append_silence_to_wav(raw_narration, silence_seconds=silence_added)
        if segments:
            segments[-1]["end"] = round(segments[-1]["end"] + silence_added, 3)
        current_time += silence_added

    shutil.copy2(raw_narration, narration_wav)
    raw_narration.unlink(missing_ok=True)

    temp_work = audio_rev_dir / "master_work_tmp.wav"
    ap.master(
        narration_wav,
        temp_work,
        {"audio_lufs": target_lufs, "audio_peak_db": target_peak, "audio_voice_chain": voice_chain},
    )

    total_duration = round(current_time, 3)
    cues = subtitle_cues(segments, aspect_ratio=aspect_ratio)

    if aspect_ratio == "9:16":
        cue_audit = audit_cues(cues, aspect_ratio="9:16")
        if cue_audit.get("errors"):
            logger.warning(f"Subtitle technical warnings: {cue_audit['errors']}")

    # Measure loudness
    r_measure = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(narration_wav), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m_json: Dict[str, Any] = {}
    try:
        s_idx = r_measure.stderr.rindex("{")
        e_idx = r_measure.stderr.rindex("}") + 1
        m_json = json.loads(r_measure.stderr[s_idx:e_idx])
    except Exception:
        pass

    measured_lufs = float(m_json.get("input_i", target_lufs))
    measured_tp = float(m_json.get("input_tp", target_peak))

    # Write subtitles.srt
    def fmt_time(seconds: float) -> str:
        ms = round(seconds * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    srt_lines = []
    for i, c in enumerate(cues, 1):
        srt_lines.append(f"{i}\n{fmt_time(c['start'])} --> {fmt_time(c['end'])}\n{c['text']}\n")
    subtitles_srt.write_text("\n".join(srt_lines), encoding="utf-8")

    # Build scene metadata
    scenes_meta = []
    for sc in content.get("scenes", []):
        sc_segs = [s for s in segments if s["scene_id"] == sc["id"]]
        if sc_segs:
            sc_start = sc_segs[0]["start"]
            sc_end = sc_segs[-1]["end"]
            scenes_meta.append({
                "id": sc["id"],
                "start": sc_start,
                "end": sc_end,
                "duration": round(sc_end - sc_start, 3),
            })

    audio_output = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "audio",
        "revision": 1,
        "files": [f"revisions/audio/1/{p.name}" for p in audio_rev_dir.glob("*.wav")] + ["revisions/audio/1/subtitles.srt"],
        "payload": {
            "wav": "revisions/audio/1/narration.wav",
            "srt": "revisions/audio/1/subtitles.srt",
            "duration": total_duration,
            "segments": segments,
            "scenes": scenes_meta,
            "cues": cues,
            "measured_lufs": measured_lufs,
            "measured_peak_dbtp": measured_tp,
            "account_used": account_used,
            "engine": "colab-omnivoice",
            "tracks": {
                "vi": {
                    "wav": "revisions/audio/1/narration.wav",
                    "srt": "revisions/audio/1/subtitles.srt",
                    "duration": total_duration,
                    "segments": segments,
                    "cues": cues,
                }
            },
        },
    }
    tmp_out_json = audio_out_json.with_suffix(".json.tmp")
    tmp_out_json.write_text(json.dumps(audio_output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_out_json.replace(audio_out_json)
    (audio_rev_dir / "audio-result.json").write_text(json.dumps(audio_output["payload"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(
        f"  [✓] Giai đoạn B hoàn tất: {len(segments)} phân đoạn, thời lượng: {total_duration:.2f}s "
        f"(kèm silence {silence_added:.1f}s), âm học: {measured_lufs:.2f} LUFS / {measured_tp:.2f} dBTP trên {account_used}"
    )
    return audio_output["payload"], client_used, account_used


def stage_c_render(
    sys_dir: Path,
    job_dir: Path,
    root_dir: Path,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    images_payload: Dict[str, Any],
    audio_payload: Dict[str, Any],
    format_profile: str = "short_9x16",
    colab_account: Optional[str] = None,
    session_name: Optional[str] = None,
    inspect_dir: Optional[Path] = None,
) -> Tuple[Path, Optional[Client], Optional[str], Dict[str, Any]]:
    """Execute Stage C: Remote Colab Tesla T4 Native FFmpeg h264_nvenc Render."""
    ch_raw = (
        brief.get("channel")
        or (brief.get("channel_profile", {}).get("id") if isinstance(brief.get("channel_profile"), dict) else brief.get("channel_profile"))
        or brief.get("channel_id")
        or (job_dir.name.split("-week1")[0].replace("-", "_") if "-week1" in job_dir.name else "nao_luoi")
    )
    channel_id, channel_slug = resolve_channel_ids(str(ch_raw))
    _, part_accounts, default_session = get_channel_slice(channel_id)
    target_account = colab_account or part_accounts[0]
    target_session = session_name or default_session

    is_long = (format_profile == "long_16x9")
    aspect_tag = "16x9" if is_long else "9x16"
    expected_width = 1920 if is_long else 1080
    expected_height = 1080 if is_long else 1920

    logger.info(f"[*] GIAI ĐOẠN C: Render video Native FFmpeg h264_nvenc từ xa trên Colab T4 cho {job_dir.name} ({format_profile})...")
    render_dir = job_dir / "revisions/render/1"
    cache_dir = job_dir / "cache/colab-render"
    video_deliv_dir = root_dir / "video" / job_dir.name

    render_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    video_deliv_dir.mkdir(parents=True, exist_ok=True)

    def resolve_path(rel_path: str) -> Path:
        p_raw = Path(rel_path)
        if p_raw.is_file():
            return p_raw
        p = job_dir / rel_path
        if p.is_file():
            return p
        p2 = job_dir / "revisions" / rel_path
        if p2.is_file():
            return p2
        p3 = sys_dir / rel_path
        if p3.is_file():
            return p3
        raise FileNotFoundError(f"Cannot resolve render asset path: {rel_path}")

    # Build render request with explicit output contract
    render_brief = copy.deepcopy(brief)
    render_brief["channel"] = channel_id
    render_brief["channel_profile"] = channel_id
    render_brief.setdefault("thumbnail_spec", {})
    if isinstance(render_brief["thumbnail_spec"], dict):
        render_brief["thumbnail_spec"]["channel_id"] = channel_id
        wm_file = sys_dir / "channels" / channel_id / "assets/watermark_150x150.png"
        if not wm_file.is_file():
            wm_candidates = [
                sys_dir / "channels" / channel_id / "assets/avatar_800x800.png",
                sys_dir / "channels" / channel_id / "assets/avatar.png",
                sys_dir / "channels" / channel_id / "assets/logo.png",
                sys_dir / "assets/channels" / channel_id / "watermark_150x150.png",
                sys_dir / "assets/channels" / channel_id / "avatar_800x800.png",
                sys_dir / "assets/channels" / channel_id / "avatar.png",
                sys_dir / "assets/channels" / channel_id / "logo.png",
                Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/channels/{channel_id}/assets/watermark_150x150.png"),
                Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/channels/{channel_id}/assets/avatar_800x800.png"),
                Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/channels/{channel_id}/assets/watermark_150x150.png"),
                Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/channels/{channel_id}/assets/avatar_800x800.png"),
            ]
            for cand in wm_candidates:
                if cand.is_file():
                    wm_file = cand
                    break
        if wm_file.is_file():
            try:
                import base64 as _b64
                import io as _io

                from PIL import Image as _PILImage

                _wm_img = _PILImage.open(wm_file).convert("RGBA").resize((108, 108), _PILImage.Resampling.LANCZOS)
                _wm_buf = _io.BytesIO()
                _wm_img.save(_wm_buf, format="WEBP", quality=88)
                render_brief["thumbnail_spec"]["brand_logo_data_uri"] = (
                    "data:image/webp;base64," + _b64.b64encode(_wm_buf.getvalue()).decode("ascii")
                )
            except Exception as ex_wm:
                logger.warning(f"Could not encode channel watermark for {channel_id}: {ex_wm}")
    render_brief["aspect_ratio"] = "16:9" if is_long else "9:16"
    render_brief["outputs"] = [
        {
            "aspect_ratio": "16:9" if is_long else "9:16",
            "language": "vi",
            "subtitles": not is_long,  # external SRT for long_16x9, burned-in for short_9x16
        }
    ]

    images_manifest = {"checkpoint": "final", "items": images_payload.get("items", [])}

    # G5 Long Explainer Pacing Gate (Narrative-Adaptive High Density 1.80-3.80s + legacy up to 8.05s)
    if is_long:
        non_endcard_items = [
            im for im in images_manifest.get("items", [])
            if not str(im.get("id", "")).endswith("_I3") and "endcard" not in str(im.get("path", "")).lower()
        ]
        is_full_chain_mp4 = bool(non_endcard_items) and all(
            str(im.get("path", "")).endswith(".mp4") for im in non_endcard_items
        )
        if is_full_chain_mp4:
            total_beats = sum(len(sc.get("beats", [])) or len(sc.get("images", [])) for sc in content.get("scenes", []))
            measured_dur = float(audio_payload.get("duration") or 180.0)
            avg_hold = round(measured_dur / max(1, total_beats), 2)
            logger.info(
                f"  [✓] Full-Chain 16:9 MP4 timeline preserved 1-to-1 ({total_beats} beats, avg_hold = {avg_hold}s) without _s sub-beat splitting."
            )
            if not (1.80 <= avg_hold <= 8.50):
                raise ValueError(
                    f"AVERAGE_HOLD_OUT_OF_TARGET: full-chain long_16x9 average hold is {avg_hold}s (allowed 1.80–8.50s)"
                )
        else:
            from visual_pacing import retime_long_beats_to_measured_audio
            content, pacing_meta = retime_long_beats_to_measured_audio(
                content=content,
                audio_payload=audio_payload,
                target_hold_sec=2.8,
            )
            logger.info(
                f"  [✓] G5 Long Pacing Re-timed to measured WAV: {pacing_meta['beats']} beats, "
                f"avg_hold = {pacing_meta['avg_hold']}s (allowed [1.80, 8.05]s, V3 Narrative-Adaptive target [2.0, 3.6]s), "
                f"tempos = {pacing_meta['tempos']}"
            )
            if not (1.80 <= pacing_meta['avg_hold'] <= 8.05):
                raise ValueError(
                    f"AVERAGE_HOLD_OUT_OF_TARGET: long_16x9 average hold is {pacing_meta['avg_hold']}s (allowed 1.80–8.05s)"
                )

    # Crop-Safety Pre-Render Gate & Safe Enforcement
    from crop_safety import enforce_scenes_crop_safety, validate_scenes_crop_safety

    scenes = content.get("scenes", [])
    violations = validate_scenes_crop_safety(scenes, images_dir=job_dir / "revisions/images/1", raise_on_error=False)
    if violations:
        logger.warning(f"  [!] Phát hiện {len(violations)} beat vi phạm Crop-Safety -> Tự động điều chỉnh an toàn...")
        repaired_scenes, count = enforce_scenes_crop_safety(scenes, images_dir=job_dir / "revisions/images/1")
        content["scenes"] = repaired_scenes
        logger.info(f"  [✓] Đã điều chỉnh {count} beat vi phạm Crop-Safety (tránh cắt chữ và chém mặt nhân vật).")
        try:
            content_file = job_dir / "content.json"
            if content_file.is_file():
                content_file.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as ex_save:
            logger.warning(f"Không thể ghi đè content.json sau sửa crop: {ex_save}")

    # Pre-render gate verification: guaranteed zero violations before submission
    validate_scenes_crop_safety(content.get("scenes", []), images_dir=job_dir / "revisions/images/1", raise_on_error=True)

    request = build_render_request(sys_dir, render_brief, content, images_manifest, audio_payload, resolve_path)
    (render_dir / "request-colab-render.json").write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    base_cfg_path = sys_dir / "config.json"
    cfg: Dict[str, Any] = json.loads(base_cfg_path.read_text(encoding="utf-8")) if base_cfg_path.is_file() else {}
    cfg.setdefault("colab_tts", {})
    cfg["colab_tts"]["session"] = target_session
    cfg["colab_tts"]["_session_explicit"] = True
    cfg["colab_tts"]["render_timeout_seconds"] = 7200 if is_long else 5400

    # Prioritize target channel slice accounts, then fail over across all healthy verified Colab accounts
    raw_accounts = (
        [target_account]
        + [a for a in part_accounts if a != target_account]
        + [a for a in VERIFIED_COLAB_ACCOUNTS if a != target_account and a not in part_accounts]
    )
    seen_accounts: set[str] = set()
    accounts_to_try: List[str] = []
    for a in raw_accounts:
        if a and a != "account-02" and a not in seen_accounts:
            seen_accounts.add(a)
            accounts_to_try.append(a)

    account_used: Optional[str] = None
    client_used: Optional[Client] = None
    consecutive_exec_failures = 0

    for acc in accounts_to_try:
        logger.info(f"Submitting render request to Colab {acc} ({target_session})...")
        acc_cfg = copy.deepcopy(cfg)
        acc_cfg["colab_tts"]["account"] = acc

        try:
            client = Client(sys_dir, acc_cfg)
            client.account = acc

            # Prefer reusing a channel-specific T4 session, otherwise fall back to any active T4 session on this account
            effective_session = target_session
            try:
                snap = client._budgets().snapshot("colab:" + acc)
                allocs = [
                    it["session"]
                    for it in snap.get("allocated_sessions", [])
                    if it.get("device") == "T4"
                    and (it.get("session") == target_session or str(it.get("session", "")).startswith(f"vp-{channel_slug}"))
                ]
                if not allocs:
                    allocs = [
                        it["session"]
                        for it in snap.get("allocated_sessions", [])
                        if it.get("device") == "T4" and it.get("session")
                    ]
                if allocs and effective_session not in allocs:
                    effective_session = allocs[0]
            except Exception:
                pass

            desired_session = effective_session
            client.session = effective_session
            acc_cfg["colab_tts"]["session"] = effective_session

            # Auto-reconcile any prior failed/aborted render state in cache_dir / acc before submitting
            acc_cache = cache_dir / acc
            if acc_cache.is_dir():
                for st_file in acc_cache.glob("*/state.json"):
                    try:
                        st_obj = json.loads(st_file.read_text(encoding="utf-8"))
                        if st_obj.get("phase") in ("submitted", "ambiguous"):
                            prev_req_id = st_obj.get("request_id")
                            if prev_req_id and prev_req_id != request["request_id"]:
                                client.reconcile_render_failure(
                                    {"operation": "render", "request_id": prev_req_id},
                                    acc_cache,
                                    source="channel_production_common_auto_reconcile",
                                )
                    except Exception:
                        pass

            try:
                client.reconcile()
            except Exception:
                pass

            # Do NOT let client.reconcile() overwrite client.session with an old dead session
            client.session = desired_session

            # Or leave uncertain=True blocking start() if assignment_count is 0
            try:
                alias = f"colab:{acc}"
                snap = client._budgets().snapshot(alias)
                if snap.get("uncertain"):
                    cleanup_stale_colab_state(client, acc, desired_session)
                    client.session = desired_session
            except Exception:
                pass

            try:
                client._ready(auto_start=True)
            except (ColabBridgeError, Exception) as ex_ready:
                err_msg = str(ex_ready)
                if any(
                    marker in err_msg
                    for marker in (
                        "COLAB_VERIFIED_SETUP_REQUIRED",
                        "COLAB_UNCERTAIN_ALLOCATION",
                        "COLAB_SINGLE_ACTIVE_SESSION",
                        "already has allocated session",
                    )
                ):
                    logger.warning(
                        f"Render account {acc} _ready failed with '{err_msg}'. Inspecting and clearing stale session/journal..."
                    )
                    cleanup_stale_colab_state(client, acc, desired_session)
                    client.session = desired_session
                    try:
                        client._ready(auto_start=True)
                        logger.info(
                            f"Render account {acc} recovered and _ready succeeded on retry with {desired_session}"
                        )
                    except Exception as ex_retry:
                        logger.warning(f"Render account {acc} retry after stale cleanup failed: {ex_retry}")
                        raise ex_retry
                else:
                    logger.warning(f"Render account {acc} _ready failed: {ex_ready}")
                    raise ex_ready

            client.render(request, render_dir, cache_dir / acc)
            account_used = acc
            client_used = client
            logger.info(f"Colab render succeeded on {acc}")
            break
        except (ColabError, Exception) as ex:
            try:
                client._settle(request["request_id"])
            except Exception:
                pass
            try:
                if hasattr(client, "management") and hasattr(client.management, "unpin"):
                    client.management.unpin(request["request_id"])
            except Exception:
                pass
            logger.warning(f"Render on {acc} failed ({type(ex).__name__}): {ex}. Failing over...")
            err_text = str(ex)
            if "COLAB_WORKER_CHANGED" in err_text:
                raise RuntimeError(f"Deterministic COLAB_WORKER_CHANGED on {acc}; aborting failover: {ex}") from ex
            if "COLAB_EXEC_UNCONFIRMED" in err_text:
                consecutive_exec_failures += 1
                if consecutive_exec_failures >= 2:
                    logger.error(
                        f"Fail-fast guard triggered: {consecutive_exec_failures} consecutive COLAB_EXEC_UNCONFIRMED "
                        f"failures (latest on {acc}). Aborting blind account rotation; inspect remote stderr via Client.exec."
                    )
                    raise RuntimeError(
                        f"FAIL_FAST_COLAB_EXEC_UNCONFIRMED ({job_dir.name}): {consecutive_exec_failures} consecutive "
                        f"accounts failed in remote execution (latest {acc}: {ex})"
                    ) from ex
            continue

    if not account_used:
        raise RuntimeError(f"All candidate Colab accounts failed for render {job_dir.name}: {accounts_to_try}")

    res_path = render_dir / "render-result.json"
    if not res_path.is_file():
        raise RuntimeError("render-result.json missing after extraction")

    # Locate rendered MP4
    candidates = [
        render_dir / f"video_{aspect_tag}.mp4",
        render_dir / "video.mp4",
        render_dir / "video_16x9.mp4",
        render_dir / "video_9x16.mp4",
    ]
    source_mp4 = next((c for c in candidates if c.is_file()), None)
    if not source_mp4:
        raise FileNotFoundError(f"No rendered video file found in {render_dir} (searched: {candidates})")

    # Copy deliverables
    final_mp4 = video_deliv_dir / f"{job_dir.name}.mp4"
    named_mp4 = video_deliv_dir / f"video_{aspect_tag}.mp4"
    shutil.copy2(source_mp4, final_mp4)
    shutil.copy2(source_mp4, named_mp4)

    # Subtitles
    srt_source = render_dir / "subtitles.srt"
    if not srt_source.is_file():
        srt_source = job_dir / "revisions/audio/1/subtitles.srt"
    if srt_source.is_file():
        shutil.copy2(srt_source, video_deliv_dir / f"{job_dir.name}.srt")
        shutil.copy2(srt_source, video_deliv_dir / "subtitles.srt")

    # Thumbnail
    thumb_source = job_dir / f"thumbnail_{aspect_tag}.jpg"
    if not thumb_source.is_file():
        thumb_source = job_dir / f"revisions/images/1/THUMBNAIL_{aspect_tag}.jpg"
    if thumb_source.is_file():
        shutil.copy2(thumb_source, video_deliv_dir / f"thumbnail_{aspect_tag}.jpg")
        shutil.copy2(thumb_source, video_deliv_dir / "cover.jpg")

    # Optional inspection copy
    if inspect_dir and inspect_dir.is_dir():
        try:
            shutil.copy2(final_mp4, inspect_dir / f"{job_dir.name}.mp4")
            if thumb_source.is_file():
                shutil.copy2(thumb_source, inspect_dir / f"{job_dir.name}_thumb.jpg")
            logger.info(f"Copied deliverables to inspection dir: {inspect_dir}")
        except Exception as ex_insp:
            logger.warning(f"Could not copy to inspect dir: {ex_insp}")

    # FFprobe validation
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json",
        str(final_mp4),
    ]
    probe_data = json.loads(subprocess.check_output(probe_cmd, text=True))
    video_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None)

    if not video_stream:
        raise ValueError("Rendered MP4 has no video stream")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    v_codec = video_stream["codec_name"]
    duration = float(probe_data.get("format", {}).get("duration", 0))
    a_codec = audio_stream["codec_name"] if audio_stream else "none"
    size_mb = round(final_mp4.stat().st_size / (1024 * 1024), 2)

    # Frame rate check
    fps_eval = 30.0
    r_frame_rate = video_stream.get("r_frame_rate", "30/1")
    if "/" in r_frame_rate:
        num, den = r_frame_rate.split("/")
        fps_eval = round(float(num) / float(den), 2)

    if (width, height) != (expected_width, expected_height):
        raise ValueError(f"Resolution mismatch: expected {expected_width}x{expected_height}, got {width}x{height}")

    # Audio/Video duration sync check (must be <= 0.12s)
    audio_dur = float(audio_payload.get("duration", duration))
    dur_diff = abs(duration - audio_dur)
    if dur_diff > 0.12:
        logger.warning(f"Audio/video sync difference {dur_diff:.3f}s exceeds nominal 0.12s target (|{duration:.2f} - {audio_dur:.2f}|)")

    render_report = {
        "file": str(final_mp4),
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps_eval,
        "video_codec": v_codec,
        "audio_codec": a_codec,
        "size_mb": size_mb,
        "account_used": account_used,
    }

    output_manifest = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "render",
        "revision": 1,
        "input_versions": {
            "content": hashlib.sha256((job_dir / "content.json").read_bytes()).hexdigest(),
            "images": hashlib.sha256((job_dir / "revisions/images/1/output.json").read_bytes()).hexdigest(),
            "audio": hashlib.sha256((job_dir / "revisions/audio/1/output.json").read_bytes()).hexdigest(),
        },
        "payload": {
            "video": f"video/{job_dir.name}/{job_dir.name}.mp4",
            "duration": duration,
            "resolution": f"{width}x{height}",
            "fps": fps_eval,
            "video_codec": v_codec,
            "audio_codec": a_codec,
            "size_mb": size_mb,
            "account_used": account_used,
        },
    }
    (render_dir / "output.json").write_text(json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    logger.info(f"  [✓] Giai đoạn C hoàn tất: Xuất bản video tại {video_deliv_dir} ({width}x{height}, {duration:.2f}s, {size_mb}MB)")
    return final_mp4, client_used, account_used, render_report


def stage_c_flow_video(
    sys_dir: Path,
    job_dir: Path,
    root_dir: Path,
    brief: Dict[str, Any],
    content: Dict[str, Any],
    images_payload: Dict[str, Any],
    audio_payload: Dict[str, Any],
    format_profile: str = "short_9x16",
    video_model: str = "omni_flash",
    chain_mode: str = "daisy_chain",
    max_workers: int = 6,
    inspect_dir: Optional[Path] = None,
    remote_colab: bool = False,
    colab_account: Optional[str] = None,
    colab_session: Optional[str] = None,
) -> Tuple[Path, Optional[Client], Optional[str], Dict[str, Any]]:
    """Execute Stage C via Flow Video Start -> End Frames Chain (Omni 1.1 Flash / Veo 3.1 + Zero-Credit Fallback)."""
    from flow_video.models import ChainMode, KeyframeSpec, ScenePairSpec, VideoChainSpec
    from flow_video.orchestrator import FlowVideoChainOrchestrator
    from tools.apply_watermark_logo import apply_logo, resolve_channel_logo

    ch_raw = (
        brief.get("channel")
        or (brief.get("channel_profile", {}).get("id") if isinstance(brief.get("channel_profile"), dict) else brief.get("channel_profile"))
        or brief.get("channel_id")
        or (job_dir.name.split("-week1")[0].replace("-", "_") if "-week1" in job_dir.name else "vu_tru_ti_hon")
    )
    channel_id, _ = resolve_channel_ids(str(ch_raw))
    try:
        ch_profile = get_channel(channel_id)
    except Exception:
        ch_profile = get_channel("nao_luoi")
    visual_style_id = getattr(getattr(ch_profile, "visual", None), "profile_id", "handdrawn_2d_explainer")
    visual_style_desc = getattr(getattr(ch_profile, "visual", None), "style_description", "2D hand-drawn explainer illustration")

    is_long = format_profile == "long_16x9"
    aspect_ratio = "16:9" if is_long else "9:16"
    aspect_tag = "16x9" if is_long else "9x16"
    expected_width = 1920 if is_long else 1080
    expected_height = 1080 if is_long else 1920

    flow_video_dir = job_dir / "revisions/flow_video/1"
    render_dir = job_dir / "revisions/render/1"
    video_deliv_dir = root_dir / "video" / job_dir.name

    flow_video_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    video_deliv_dir.mkdir(parents=True, exist_ok=True)

    is_remote = remote_colab or os.environ.get("VP_FLOW_VIDEO_REMOTE_COLAB", "0") in ("1", "true", "True")
    if is_remote:
        from tools.colab_multijob_flow_render_batch import run_multijob_flow_render
        _, part_accounts, default_session = get_channel_slice(channel_id)
        target_account = colab_account or (part_accounts[0] if part_accounts else "account-01")
        target_session = colab_session or default_session
        fmt = "16x9" if is_long else "9x16"
        logger.info(
            f"[*] GIAI ĐOẠN C (FLOW VIDEO REMOTE COLAB T4): Render qua Colab T4 ({target_account}/{target_session}) "
            f"cho {job_dir.name} ({format_profile})..."
        )
        run_multijob_flow_render(
            account=target_account,
            session=target_session,
            channels=[channel_id],
            formats=[fmt],
            force=True,
        )
        final_mp4 = video_deliv_dir / f"{job_dir.name}.mp4"
        render_result_json = render_dir / "render-result.json"
        render_report = (
            json.loads(render_result_json.read_text(encoding="utf-8"))
            if render_result_json.is_file()
            else {
                "file": str(final_mp4),
                "duration": 0.0,
                "width": expected_width,
                "height": expected_height,
                "fps": 30.0,
                "video_codec": "h264",
                "audio_codec": "aac",
                "size_mb": round(final_mp4.stat().st_size / (1024 * 1024), 2) if final_mp4.is_file() else 0,
                "account_used": target_account,
                "engine": "colab-nvenc:flow_video",
            }
        )
        return final_mp4, None, target_account, render_report

    logger.info(
        f"[*] GIAI ĐOẠN C (FLOW VIDEO START->END FRAMES): Tạo chuỗi video {video_model} ({chain_mode}) "
        f"cho {job_dir.name} ({format_profile})..."
    )

    # Map scene durations from measured audio
    scene_dur_map: Dict[str, float] = {}
    for sc_meta in audio_payload.get("scenes", []):
        if sc_meta.get("id") and sc_meta.get("duration"):
            scene_dur_map[str(sc_meta["id"])] = float(sc_meta["duration"])

    # Map image descriptions and beat durations from content.json
    img_desc_map: Dict[str, str] = {}
    img_dur_map: Dict[str, float] = {}
    for sc in content.get("scenes", []):
        sc_id = str(sc.get("id", ""))
        sc_imgs = sc.get("images", [])
        sc_dur = scene_dur_map.get(sc_id, float(sc.get("duration", 5.0)))
        per_img_dur = max(3.0, round(sc_dur / max(1, len(sc_imgs)), 2))
        for im in sc_imgs:
            im_id = str(im.get("id", ""))
            img_desc_map[im_id] = str(im.get("description") or im.get("motion_prompt") or "")
            img_dur_map[im_id] = float(im.get("duration") or per_img_dur)

    manifest_items = images_payload.get("items") or images_payload.get("payload", {}).get("items", [])
    keyframes: List[KeyframeSpec] = []
    for idx, item in enumerate(manifest_items):
        img_id = str(item.get("image_id") or f"KF_{idx:03d}")
        rel_path = str(item.get("path", ""))
        img_path = job_dir / rel_path
        if not img_path.is_file():
            img_path = job_dir / "revisions/images/1" / Path(rel_path).name
        raw_desc = img_desc_map.get(img_id, "the focal visual metaphor")
        clean_desc = _sanitize_non_stickman_text(raw_desc, ch_profile)
        style_tag = (
            "Smooth 2D hand-drawn doodle explainer animation"
            if visual_style_id in ("ch_stickman_doodle", "handdrawn_2d_explainer", "1.7.0")
            else f"Smooth 2D explainer animation ({visual_style_id}: {visual_style_desc[:90].strip().rstrip('.')})"
        )
        motion_prompt = (
            f"{style_tag}. {clean_desc[:180].strip().rstrip('.')} "
            "transitions smoothly into the next frame, silent visual storytelling, no talking, no lip movement"
        )
        target_dur = img_dur_map.get(img_id, 5.0)
        keyframes.append(
            KeyframeSpec(
                id=img_id,
                image_path=str(img_path.resolve()),
                motion_prompt=motion_prompt,
                target_duration=target_dur,
            )
        )

    if len(keyframes) < 2:
        raise ValueError(f"Flow Video Start->End chain requires at least 2 keyframes (found {len(keyframes)})")

    try:
        resolved_mode = ChainMode(chain_mode)
    except ValueError:
        resolved_mode = ChainMode.DAISY_CHAIN

    scene_pairs: List[ScenePairSpec] = []
    if resolved_mode == ChainMode.SCENE_PAIRS:
        for i in range(len(keyframes) - 1):
            kf_s = keyframes[i]
            kf_e = keyframes[i + 1]
            scene_pairs.append(
                ScenePairSpec(
                    id=f"pair_{i:03d}_{kf_s.id}_to_{kf_e.id}",
                    start_image_path=kf_s.image_path,
                    end_image_path=kf_e.image_path,
                    motion_prompt=kf_s.motion_prompt,
                    target_duration=kf_s.target_duration,
                )
            )

    narration_wav = job_dir / "revisions/audio/1/narration.wav"
    spec = VideoChainSpec(
        job_id=job_dir.name,
        mode=resolved_mode,
        aspect=aspect_ratio,
        video_model=video_model,
        duration_seconds=6,
        keyframes=keyframes,
        scene_pairs=scene_pairs,
        audio_path=str(narration_wav.resolve()) if narration_wav.is_file() else None,
        no_talking_prompt_guard=True,
        keep_veo_audio=False,
        target_fps=30,
        normalize_audio_lufs=True,
        auto_duration=True,
        auto_fallback_zero_credit=True,
        channel_id=channel_id,
    )

    raw_stitched_mp4 = flow_video_dir / f"video_{aspect_tag}_raw.mp4"

    # Cross-process 2-slot render semaphore to prevent CPU/RAM saturation when 16 subagents run concurrently
    slot_fh = None
    while slot_fh is None:
        for slot_idx in (0, 1):
            candidate_lock = Path(f"/tmp/vp_flow_video_slot_{slot_idx}.lock")
            fh = candidate_lock.open("a", encoding="utf-8")
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                slot_fh = fh
                break
            except BlockingIOError:
                fh.close()
        if slot_fh is None:
            time.sleep(2.0)

    try:
        try:
            os.nice(15)
        except Exception:
            pass
        orchestrator = FlowVideoChainOrchestrator(
            spec=spec,
            work_dir=flow_video_dir,
            output_mp4_path=raw_stitched_mp4,
            max_workers=min(2, max_workers),
            headless=True,
            resume=True,
        )
        chain_report = orchestrator.run()

        rendered_mp4 = render_dir / f"video_{aspect_tag}.mp4"
        shutil.copy2(raw_stitched_mp4, rendered_mp4)

        # Burn-in subtitles for short_9x16 if subtitles.srt exists
        srt_file = job_dir / "revisions/audio/1/subtitles.srt"
        if not is_long and srt_file.is_file():
            sub_tmp = render_dir / f"video_{aspect_tag}_subtitled.mp4"
            try:
                sub_cmd = [
                    "ffmpeg", "-y", "-threads", "2", "-i", str(rendered_mp4),
                    "-vf", f"subtitles={srt_file}:force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=0,MarginV=140,Alignment=2'",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
                    "-c:a", "copy",
                    str(sub_tmp),
                ]
                subprocess.check_call(sub_cmd)
                shutil.move(sub_tmp, rendered_mp4)
                logger.info(f"  [✓] Đã burn-in phụ đề cho {job_dir.name} ({aspect_tag})")
            except Exception as ex_sub:
                logger.warning(f"Không thể burn-in phụ đề: {ex_sub}")

        # Apply rounded channel watermark logo
        try:
            logo_file = resolve_channel_logo(channel_id)
            if logo_file.is_file():
                apply_logo(rendered_mp4, rendered_mp4, logo_path=logo_file)
        except Exception as ex_logo:
            logger.warning(f"Could not apply channel watermark logo: {ex_logo}")
    finally:
        if slot_fh is not None:
            try:
                fcntl.flock(slot_fh.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            slot_fh.close()

    # Copy deliverables to video/<job_id>/
    final_mp4 = video_deliv_dir / f"{job_dir.name}.mp4"
    named_mp4 = video_deliv_dir / f"video_{aspect_tag}.mp4"
    shutil.copy2(rendered_mp4, final_mp4)
    shutil.copy2(rendered_mp4, named_mp4)

    srt_source = job_dir / "revisions/audio/1/subtitles.srt"
    if srt_source.is_file():
        shutil.copy2(srt_source, video_deliv_dir / f"{job_dir.name}.srt")
        shutil.copy2(srt_source, video_deliv_dir / "subtitles.srt")

    thumb_source = job_dir / f"thumbnail_{aspect_tag}.jpg"
    if not thumb_source.is_file():
        thumb_source = job_dir / f"revisions/images/1/THUMBNAIL_{aspect_tag}.jpg"
    if thumb_source.is_file():
        shutil.copy2(thumb_source, video_deliv_dir / f"thumbnail_{aspect_tag}.jpg")
        shutil.copy2(thumb_source, video_deliv_dir / "cover.jpg")

    if inspect_dir and inspect_dir.is_dir():
        try:
            shutil.copy2(final_mp4, inspect_dir / f"{job_dir.name}.mp4")
            if thumb_source.is_file():
                shutil.copy2(thumb_source, inspect_dir / f"{job_dir.name}_thumb.jpg")
        except Exception as ex_insp:
            logger.warning(f"Could not copy to inspect dir: {ex_insp}")

    # FFprobe validation
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json",
        str(final_mp4),
    ]
    probe_data = json.loads(subprocess.check_output(probe_cmd, text=True))
    video_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not video_stream:
        raise ValueError("Rendered Flow Video MP4 has no video stream")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    v_codec = video_stream["codec_name"]
    duration = float(probe_data.get("format", {}).get("duration", 0))
    a_codec = audio_stream["codec_name"] if audio_stream else "none"
    size_mb = round(final_mp4.stat().st_size / (1024 * 1024), 2)

    if (width, height) != (expected_width, expected_height):
        raise ValueError(f"Resolution mismatch: expected {expected_width}x{expected_height}, got {width}x{height}")

    profiles_used_str = ",".join(chain_report.get("profiles_used", [])) or "flow_video_pool"
    render_report = {
        "file": str(final_mp4),
        "duration": duration,
        "width": width,
        "height": height,
        "fps": 30.0,
        "video_codec": v_codec,
        "audio_codec": a_codec,
        "size_mb": size_mb,
        "account_used": profiles_used_str,
        "engine": f"flow_video:{video_model}:{chain_report.get('mode', chain_mode)}",
        "total_credit_cost": chain_report.get("total_credit_cost", 0),
        "nb_clips": chain_report.get("nb_clips", 0),
    }
    (render_dir / "render-result.json").write_text(
        json.dumps(render_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    output_manifest = {
        "schema_version": "1.0",
        "job_id": job_dir.name,
        "module": "render",
        "revision": 1,
        "payload": {
            "video": f"video/{job_dir.name}/{job_dir.name}.mp4",
            "duration": duration,
            "resolution": f"{width}x{height}",
            "fps": 30.0,
            "video_codec": v_codec,
            "audio_codec": a_codec,
            "size_mb": size_mb,
            "account_used": profiles_used_str,
            "engine": render_report["engine"],
            "total_credit_cost": chain_report.get("total_credit_cost", 0),
        },
    }
    (render_dir / "output.json").write_text(
        json.dumps(output_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info(
        f"  [✓] Giai đoạn C (Flow Video) hoàn tất: {final_mp4} ({width}x{height}, {duration:.2f}s, "
        f"{size_mb}MB, credits={chain_report.get('total_credit_cost', 0)})"
    )
    return final_mp4, None, profiles_used_str, render_report
