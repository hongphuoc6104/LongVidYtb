"""38-Channel Lifecycle State SSOT, Rollout Waves, VN<->EN Twin Map & Alias Deduplicator.

Governs all 38 physical channels (20 Vietnamese + 18 English) via a 4-state valve:
- ACTIVE: Actively producing & publishing (currently `su_ke_lai` in wave_0)
- CANARY: Opened for 3-5 Short V4 validation runs before scaling
- STANDBY: Preserved intact with full config/profiles/videos, hidden from Focus Mode
- NEEDS_AUTH: Quarantined for Chrome profile / YouTube Studio tier check
"""

from __future__ import annotations

import fcntl
import json
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from channels.registry import CHANNEL_ALIASES
from channels.registry import channel_ids as get_registry_channel_ids

SYS_DIR = Path(__file__).resolve().parents[1]
DEFAULT_LIFECYCLE_PATH = SYS_DIR / "channels" / "fleet_lifecycle.json"
DEFAULT_CHANNEL_MAP_PATH = SYS_DIR / "channels" / "youtube_channel_map.json"

VALID_LIFECYCLE_STATES: tuple[str, ...] = ("ACTIVE", "CANARY", "STANDBY", "NEEDS_AUTH")

WAVE_ASSIGNMENTS: dict[str, list[str]] = {
    "wave_0": ["su_ke_lai"],
    "wave_1": ["ban_do_quyen_luc", "co_the_ke", "ho_so_ky_la", "chanh_niem_ke"],
    "wave_2": ["loi_sang_soi", "nghe_song_sot", "luat_ngam", "banh_rang", "ua_sao_vay"],
    "wave_3": [
        "ai_binh_dan",
        "nao_luoi",
        "tui_tien",
        "thuong_cho_kheo",
        "dia_com",
        "vu_tru_ti_hon",
        "la_ban_hoc_thuat",
        "luat_doi_thuong",
        "minh_triet_song",
        "tam_tinh_dem",
    ],
    "wave_4": [
        "en_choke_point",
        "en_cold_case_ink",
        "en_inside_vessel",
        "en_parable_lamp",
        "en_macro_gears",
        "en_second_arrow",
    ],
    "wave_5": [
        "en_crowd_strings",
        "en_career_leverage",
        "en_pocket_cosmos",
        "en_plain_sight_ai",
        "en_kitchen_molecules",
        "en_wait_how",
        "en_lazy_brain",
        "en_wallet_anatomy",
        "en_fine_print",
        "en_kindred_sketch",
        "en_first_principles",
        "en_bamboo_marble",
    ],
}

WAVE_LABELS: dict[str, str] = {
    "wave_0": "Sóng 0 — Chủ Lực (Sử Kể Lại)",
    "wave_1": "Sóng 1 — 4 Kênh VN 3D/GIS Mũi Nhọn",
    "wave_2": "Sóng 2 — 5 Kênh VN Tín Hiệu Cao",
    "wave_3": "Sóng 3 — 10 Kênh VN Mở Rộng",
    "wave_4": "Sóng 4 — 6 Kênh EN Song Sinh Mũi Nhọn",
    "wave_5": "Sóng 5 — 12 Kênh EN Song Sinh Còn Lại",
}

VN_TO_EN_TWIN_MAP: dict[str, str] = {
    "ban_do_quyen_luc": "en_choke_point",
    "ho_so_ky_la": "en_cold_case_ink",
    "co_the_ke": "en_inside_vessel",
    "su_ke_lai": "en_parable_lamp",
    "banh_rang": "en_macro_gears",
    "luat_ngam": "en_crowd_strings",
    "nghe_song_sot": "en_career_leverage",
    "vu_tru_ti_hon": "en_pocket_cosmos",
    "ai_binh_dan": "en_plain_sight_ai",
    "dia_com": "en_kitchen_molecules",
    "ua_sao_vay": "en_wait_how",
    "nao_luoi": "en_lazy_brain",
    "tui_tien": "en_wallet_anatomy",
    "luat_doi_thuong": "en_fine_print",
    "thuong_cho_kheo": "en_kindred_sketch",
    "la_ban_hoc_thuat": "en_first_principles",
    "loi_sang_soi": "en_second_arrow",
    "tam_tinh_dem": "en_bamboo_marble",
    "chanh_niem_ke": "en_parable_lamp",
    "minh_triet_song": "en_second_arrow",
}

EN_TO_VN_TWIN_MAP: dict[str, str] = {
    "en_choke_point": "ban_do_quyen_luc",
    "en_cold_case_ink": "ho_so_ky_la",
    "en_inside_vessel": "co_the_ke",
    "en_parable_lamp": "su_ke_lai",
    "en_macro_gears": "banh_rang",
    "en_crowd_strings": "luat_ngam",
    "en_career_leverage": "nghe_song_sot",
    "en_pocket_cosmos": "vu_tru_ti_hon",
    "en_plain_sight_ai": "ai_binh_dan",
    "en_kitchen_molecules": "dia_com",
    "en_wait_how": "ua_sao_vay",
    "en_lazy_brain": "nao_luoi",
    "en_wallet_anatomy": "tui_tien",
    "en_fine_print": "luat_doi_thuong",
    "en_kindred_sketch": "thuong_cho_kheo",
    "en_first_principles": "la_ban_hoc_thuat",
    "en_second_arrow": "loi_sang_soi",
    "en_bamboo_marble": "tam_tinh_dem",
}

ALIAS_TO_CANONICAL: dict[str, str] = {
    **CHANNEL_ALIASES,
    "en_scale_and_bone": "en_plain_sight_ai",
    "en_root_and_canopy": "en_kitchen_molecules",
    "en_spawn_to_apex": "en_wait_how",
    "en_deep_time_strata": "en_parable_lamp",
}


def resolve_canonical_channel_id(raw_id: str) -> str:
    """Normalize hyphens/case and map EN aliases to their canonical 38-channel ID."""
    norm = (raw_id or "").strip().lower().replace("-", "_")
    return ALIAS_TO_CANONICAL.get(norm, norm)


def get_wave_for_channel(channel_id: str) -> str:
    """Return the rollout wave (`wave_0`..`wave_5`) for a canonical channel ID."""
    cid = resolve_canonical_channel_id(channel_id)
    for wave_id, members in WAVE_ASSIGNMENTS.items():
        if cid in members:
            return wave_id
    return "wave_3" if not cid.startswith("en_") else "wave_5"


def get_twin_channel_id(channel_id: str) -> str:
    """Return the paired VN <-> EN twin channel ID."""
    cid = resolve_canonical_channel_id(channel_id)
    if cid.startswith("en_"):
        return EN_TO_VN_TWIN_MAP.get(cid, "")
    return VN_TO_EN_TWIN_MAP.get(cid, "")


@contextmanager
def _file_lock(path: Path) -> Iterator[None]:
    lock_path = path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)


def build_default_fleet_lifecycle() -> dict[str, Any]:
    """Build deterministic initial 38-channel lifecycle payload."""
    now_iso = datetime.now(timezone.utc).isoformat()
    canon_ids = list(get_registry_channel_ids())
    channels_map: dict[str, dict[str, Any]] = {}
    for cid in canon_ids:
        wave_id = get_wave_for_channel(cid)
        state = "ACTIVE" if cid == "su_ke_lai" else "STANDBY"
        channels_map[cid] = {
            "channel_id": cid,
            "state": state,
            "rollout_wave": wave_id,
            "wave_label": WAVE_LABELS.get(wave_id, wave_id),
            "language": "en" if cid.startswith("en_") else "vi",
            "twin_channel_id": get_twin_channel_id(cid),
            "canary_ready": wave_id == "wave_1",
            "short_v4_enabled": True,
            "note": (
                "Kênh chủ lực đang chạy Short V4 + Long M1-Flex."
                if cid == "su_ke_lai"
                else ("Sẵn sàng bật Canary Sóng 1." if wave_id == "wave_1" else "Đang đóng chờ tới sóng.")
            ),
            "updated_at": now_iso,
        }
    return {
        "schema_version": "1.0",
        "updated_at": now_iso,
        "total_channels": len(channels_map),
        "waves": {k: list(v) for k, v in WAVE_ASSIGNMENTS.items()},
        "channels": channels_map,
    }


def _reconcile_lifecycle(data: dict[str, Any]) -> dict[str, Any]:
    defaults = build_default_fleet_lifecycle()
    raw_channels = data.get("channels") if isinstance(data.get("channels"), dict) else {}
    merged_channels: dict[str, dict[str, Any]] = {}
    for cid, default_entry in defaults["channels"].items():
        existing = raw_channels.get(cid)
        entry = dict(default_entry)
        if isinstance(existing, dict):
            st = str(existing.get("state") or entry["state"]).upper()
            if st in VALID_LIFECYCLE_STATES:
                entry["state"] = st
            if existing.get("note"):
                entry["note"] = str(existing["note"])
            if existing.get("updated_at"):
                entry["updated_at"] = str(existing["updated_at"])
            if "canary_ready" in existing:
                entry["canary_ready"] = bool(existing["canary_ready"])
        merged_channels[cid] = entry
    return {
        "schema_version": "1.0",
        "updated_at": str(data.get("updated_at") or defaults["updated_at"]),
        "total_channels": len(merged_channels),
        "waves": defaults["waves"],
        "channels": merged_channels,
    }


def load_fleet_lifecycle(path: Path = DEFAULT_LIFECYCLE_PATH) -> dict[str, Any]:
    """Load `fleet_lifecycle.json`, creating canonical 38-channel defaults if missing."""
    p = Path(path)
    with _file_lock(p):
        if not p.is_file():
            data = build_default_fleet_lifecycle()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return data
        loaded = json.loads(p.read_text(encoding="utf-8"))
        return _reconcile_lifecycle(loaded if isinstance(loaded, dict) else {})


def save_fleet_lifecycle(data: dict[str, Any], path: Path = DEFAULT_LIFECYCLE_PATH) -> dict[str, Any]:
    """Atomically validate and write `fleet_lifecycle.json`."""
    p = Path(path)
    with _file_lock(p):
        reconciled = _reconcile_lifecycle(data)
        reconciled["updated_at"] = datetime.now(timezone.utc).isoformat()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(reconciled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(p)
        return reconciled


def set_channel_lifecycle_state(
    channel_id: str,
    state: str,
    *,
    note: str = "",
    path: Path = DEFAULT_LIFECYCLE_PATH,
) -> dict[str, Any]:
    """Update one channel's 4-state valve (`ACTIVE`, `CANARY`, `STANDBY`, `NEEDS_AUTH`)."""
    cid = resolve_canonical_channel_id(channel_id)
    st = str(state or "").strip().upper()
    if st not in VALID_LIFECYCLE_STATES:
        raise ValueError(f"Invalid lifecycle state {state!r}; expected one of {VALID_LIFECYCLE_STATES}")
    data = load_fleet_lifecycle(path)
    if cid not in data["channels"]:
        raise KeyError(f"Unknown canonical channel_id: {channel_id!r}")
    now_iso = datetime.now(timezone.utc).isoformat()
    data["channels"][cid]["state"] = st
    data["channels"][cid]["updated_at"] = now_iso
    if note:
        data["channels"][cid]["note"] = note
    return save_fleet_lifecycle(data, path)


def set_wave_lifecycle_state(
    wave_id: str,
    state: str,
    *,
    note: str = "",
    path: Path = DEFAULT_LIFECYCLE_PATH,
) -> dict[str, Any]:
    """Update lifecycle state for every channel assigned to a rollout wave (`wave_0`..`wave_5`)."""
    wid = str(wave_id or "").strip().lower().replace("-", "_")
    if wid not in WAVE_ASSIGNMENTS:
        raise KeyError(f"Unknown rollout wave {wave_id!r}; expected one of {tuple(WAVE_ASSIGNMENTS)}")
    st = str(state or "").strip().upper()
    if st not in VALID_LIFECYCLE_STATES:
        raise ValueError(f"Invalid lifecycle state {state!r}; expected one of {VALID_LIFECYCLE_STATES}")
    data = load_fleet_lifecycle(path)
    now_iso = datetime.now(timezone.utc).isoformat()
    for cid in WAVE_ASSIGNMENTS[wid]:
        if cid in data["channels"]:
            data["channels"][cid]["state"] = st
            data["channels"][cid]["updated_at"] = now_iso
            if note:
                data["channels"][cid]["note"] = note
    return save_fleet_lifecycle(data, path)


def get_channels_by_state(
    states: tuple[str, ...] = ("ACTIVE", "CANARY"),
    *,
    path: Path = DEFAULT_LIFECYCLE_PATH,
) -> list[str]:
    """Return canonical channel IDs matching any requested lifecycle state."""
    allowed = {s.strip().upper() for s in states}
    data = load_fleet_lifecycle(path)
    return [cid for cid, entry in data["channels"].items() if entry.get("state") in allowed]


def lifecycle_counts(path: Path = DEFAULT_LIFECYCLE_PATH) -> dict[str, int]:
    """Return channel count summary across all 4 lifecycle states."""
    data = load_fleet_lifecycle(path)
    counts = {s: 0 for s in VALID_LIFECYCLE_STATES}
    for entry in data["channels"].values():
        st = str(entry.get("state") or "STANDBY")
        if st in counts:
            counts[st] += 1
    counts["total"] = len(data["channels"])
    return counts


def collect_system_health(lifecycle_path: Path = DEFAULT_LIFECYCLE_PATH) -> dict[str, Any]:
    """Read lifecycle valve summary, Flow credit ledger, and Colab T4 pool status without blocking."""
    flow_summary: dict[str, Any] = {
        "profiles_tracked": 0,
        "total_credits": 0,
        "eligible_profiles": 0,
        "image_only_profiles": 0,
    }
    try:
        from flow_cdp.credit_ledger import CreditLedger

        raw = CreditLedger()._read_data()
        profiles = raw.get("profiles") if isinstance(raw.get("profiles"), dict) else {}
        if isinstance(profiles, dict):
            credits = [int((v or {}).get("credits_remaining") or 0) for v in profiles.values() if isinstance(v, dict)]
            flow_summary = {
                "profiles_tracked": len(profiles),
                "total_credits": sum(credits),
                "eligible_profiles": sum(1 for c in credits if c >= 10),
                "image_only_profiles": sum(1 for c in credits if 0 <= c < 10),
            }
    except Exception:
        pass

    colab_summary: dict[str, Any] = {"healthy_idle": 0, "total_accounts": 0}
    try:
        from colab_bridge.pool_manager import ColabPoolManager

        st = ColabPoolManager().get_status(probe_server=False)
        workers = list(st.get("workers") or [])
        colab_summary = {
            "total_accounts": len(workers),
            "healthy_idle": sum(
                1
                for w in workers
                if w.get("state") == "healthy" and not w.get("external_lock_busy") and not w.get("local_sessions")
            ),
        }
    except Exception:
        pass

    host_memory: dict[str, int] = {"total_mb": 0, "available_mb": 0}
    try:
        from flow_cdp.resource_locks import get_host_ram_available_mb, get_host_ram_total_mb

        host_memory = {
            "total_mb": int(get_host_ram_total_mb() or 0),
            "available_mb": int(get_host_ram_available_mb() or 0),
        }
    except Exception:
        pass

    return {
        "status": "ok",
        "lifecycle_counts": lifecycle_counts(lifecycle_path),
        "flow_pool": flow_summary,
        "colab_pool": colab_summary,
        "host_memory": host_memory,
    }


def _extract_yt_vid(url: str) -> str:
    m = re.search(r"(?:v=|/shorts/|youtu\.be/)([a-zA-Z0-9_-]{11})", str(url or ""))
    return m.group(1) if m else ""


def deduplicate_channel_map_aliases(channel_map_path: Path = DEFAULT_CHANNEL_MAP_PATH) -> dict[str, Any]:
    """Merge the 4 duplicate EN alias entries into their canonical entries in `youtube_channel_map.json`."""
    p = Path(channel_map_path)
    if not p.is_file():
        return {"changed": False, "removed_aliases": [], "total_channels": 0}

    with _file_lock(p):
        raw = json.loads(p.read_text(encoding="utf-8"))
        channels_obj = raw.get("channels")
        if not isinstance(channels_obj, dict):
            return {"changed": False, "removed_aliases": [], "total_channels": 0}

        alias_pairs = (
            ("en_scale_and_bone", "en_plain_sight_ai"),
            ("en_root_and_canopy", "en_kitchen_molecules"),
            ("en_spawn_to_apex", "en_wait_how"),
            ("en_deep_time_strata", "en_parable_lamp"),
        )
        removed: list[str] = []
        changed = False

        for alias_id, canon_id in alias_pairs:
            if alias_id not in channels_obj:
                continue
            alias_entry = channels_obj[alias_id]
            canon_entry = channels_obj.setdefault(canon_id, {})
            if isinstance(alias_entry, dict) and isinstance(canon_entry, dict):
                for field in ("short_video_url", "long_video_url", "branding_v3_verified", "branding_verified_at"):
                    if not canon_entry.get(field) and alias_entry.get(field):
                        canon_entry[field] = alias_entry[field]

                existing_vids = list(canon_entry.get("published_videos") or [])
                seen_keys = {
                    _extract_yt_vid(v.get("video_url", "")) or str(v.get("video_url") or "")
                    for v in existing_vids
                    if isinstance(v, dict)
                }
                for av in alias_entry.get("published_videos") or []:
                    if not isinstance(av, dict):
                        continue
                    vkey = _extract_yt_vid(av.get("video_url", "")) or str(av.get("video_url") or "")
                    if vkey and vkey not in seen_keys:
                        existing_vids.append(av)
                        seen_keys.add(vkey)
                canon_entry["published_videos"] = existing_vids
                aliases = list(canon_entry.get("aliases") or [])
                if alias_id not in aliases:
                    aliases.append(alias_id)
                canon_entry["aliases"] = aliases

            del channels_obj[alias_id]
            removed.append(alias_id)
            changed = True

        if changed:
            raw["description"] = "SSOT 38-Channel (20 VN + 18 EN) to Chrome CDP Profile mapping for YouTube automation"
            tmp = p.with_suffix(".tmp")
            tmp.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            tmp.replace(p)

        return {
            "changed": changed,
            "removed_aliases": removed,
            "total_channels": len(channels_obj),
        }
