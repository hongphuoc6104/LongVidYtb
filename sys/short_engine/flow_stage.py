"""Parallel Flow Stage A (BELUGA 9:16 images) & Stage B (selective tier-0 Omni video) for Short Engine V3."""
from __future__ import annotations

import copy
import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
from flow_cdp import stop_all_profiles
from flow_cdp.cdp_direct_client import get_all_configured_profiles
from flow_cdp.credit_ledger import CreditLedger
from flow_cdp.persistent_pool import PersistentWorkerPool
from flow_cdp.process_manager import get_process_manager
from flow_cdp.resource_locks import DEFAULT_MAX_GLOBAL_BROWSERS, GlobalFlowProductionLock
from flow_video.chain_planner import build_dual_model_chain_spec
from flow_video.models import ChainMode, ScenePairSpec, VideoChainSpec
from flow_video.orchestrator import FlowVideoChainOrchestrator
from flow_video.scene_map_planner import SceneMap, SceneMapEntry
from flow_video.sparkle_unblend import (
    _ALPHA_1X1_B64,
    _ALPHA_9X16_16X9_B64,
    _decode_alpha_68,
    clean_beluga_sparkle_pil,
)
from PIL import Image

logger = logging.getLogger("produce_serialized_short")

VALID_VISUAL_MODES = ("hybrid_2k", "full_video")
VALID_ASSET_MODES = ("flow_video", "2k_native_kenburns")
STORY_OVERSCAN = 1.045
THUMB_OVERSCAN = 1.015
YT_MAX_THUMB_BYTES = 1_950_000
MAX_THUMB_LIMIT_BYTES = 2_000_000


def resolve_worker_count(raw_value: str | int, *, stage: str = "image") -> int:
    """Resolve `auto` or numeric worker count cleanly within hardware limits."""
    if isinstance(raw_value, str) and raw_value.strip().lower() == "auto":
        max_slots = max(2, int(DEFAULT_MAX_GLOBAL_BROWSERS))
        if str(stage).strip().lower() == "video":
            return 2 if max_slots <= 4 else min(3, max_slots)
        return 3 if max_slots <= 4 else min(6, max(4, max_slots))
    return max(1, int(raw_value))


def classify_hybrid_beats(
    short_spec: dict[str, Any],
    visual_mode: str = "hybrid_2k",
) -> list[dict[str, Any]]:
    """Classify each beat as `flow_video` or `2k_native_kenburns`.

    In `hybrid_2k`:
    - Any beat participating in a `frame_link` pair (source or arrival target) is always `flow_video`.
    - Explicit per-beat `asset_mode_override` (`flow_video` | `2k_native_kenburns`) is honored otherwise.
    - Fallback without override keeps `tactical_sand_table` or calm `context`/`mechanism`/`payoff`
      breakdowns/reflections outside Act 4 on `2k_native_kenburns`, and live beats on `flow_video`.
    """
    if visual_mode not in VALID_VISUAL_MODES:
        raise ValueError(f"Unsupported visual_mode={visual_mode!r}; expected one of {VALID_VISUAL_MODES}")

    beats = list(short_spec.get("beats") or [])
    classified: list[dict[str, Any]] = []
    for idx, beat in enumerate(beats):
        entry = dict(beat)
        if visual_mode == "full_video":
            entry["asset_mode"] = "flow_video"
            classified.append(entry)
            continue

        prev_tmode = str(beats[idx - 1].get("transition_mode") or "") if idx > 0 else ""
        curr_tmode = str(beat.get("transition_mode") or "")
        is_frame_link_pair = curr_tmode == "frame_link" or prev_tmode == "frame_link"
        has_oner_group = bool(str(beat.get("oner_group_id") or "").strip())
        override = str(beat.get("asset_mode_override") or "").strip()

        if is_frame_link_pair:
            asset_mode = "flow_video"
        elif override in VALID_ASSET_MODES:
            asset_mode = override
        elif has_oner_group:
            asset_mode = "flow_video"
        else:
            beat_role = str(beat.get("beat_role") or beat.get("role") or "")
            scene_type = str(beat.get("scene_type") or "live_action")
            delivery_mode = str(beat.get("delivery_mode") or "")
            act_num = int(beat.get("act") or 0)
            if scene_type == "tactical_sand_table":
                asset_mode = "2k_native_kenburns"
            elif (
                beat_role in ("context", "mechanism", "payoff")
                and delivery_mode in ("tactical_breakdown", "reflective_lesson")
                and act_num != 4
            ):
                asset_mode = "2k_native_kenburns"
            else:
                asset_mode = "flow_video"

        entry["asset_mode"] = asset_mode
        classified.append(entry)
    return classified


def _valid_png(path: Path, expected_size: tuple[int, int], *, require_rgb: bool = True, min_bytes: int = 50_000) -> bool:
    if not path.is_file() or path.stat().st_size < min_bytes:
        return False
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            return im.size == expected_size and (not require_rgb or im.mode == "RGB")
    except Exception:
        return False


def _clean_beluga_sparkle_adaptive(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    w, h = rgb.size
    if (w, h) in ((768, 1376), (1376, 768), (1024, 1024)):
        cleaned = clean_beluga_sparkle_pil(rgb)
        alpha = _decode_alpha_68(_ALPHA_1X1_B64 if (w, h) == (1024, 1024) else _ALPHA_9X16_16X9_B64)[..., 0]
        y0, x0, side = (h - 136, w - 136, 68) if (w, h) == (1024, 1024) else (h - 132, w - 132, 68)
        arr = np.array(cleaned, dtype=np.float64)
        patch_gray = arr[y0 : y0 + side, x0 : x0 + side].mean(axis=2)
        diff = float(patch_gray[alpha > 0.15].mean() - patch_gray[alpha < 0.01].mean())
        corr = float(np.corrcoef(patch_gray.ravel(), alpha.ravel())[0, 1])
        if diff >= 35.0 and corr >= 0.45:
            cleaned = clean_beluga_sparkle_pil(cleaned)
        return cleaned

    if (w, h) == (756, 1344):
        alpha_68 = _decode_alpha_68(_ALPHA_9X16_16X9_B64)[..., 0]
        a_70 = (
            np.array(
                Image.fromarray((alpha_68 * 255.0).astype(np.uint8)).resize((70, 70), Image.Resampling.BICUBIC),
                dtype=np.float64,
            )
            / 255.0
        )
        y0, x0, side = h - 162, w - 162, 70
        arr = np.array(rgb, dtype=np.float64)
        a_3 = a_70[..., None]
        for _ in range(2):
            patch = arr[y0 : y0 + side, x0 : x0 + side]
            patch_gray = patch.mean(axis=2)
            diff = float(patch_gray[a_70 > 0.15].mean() - patch_gray[a_70 < 0.01].mean())
            corr = float(np.corrcoef(patch_gray.ravel(), a_70.ravel())[0, 1])
            if diff < 35.0 or corr < 0.45:
                break
            arr[y0 : y0 + side, x0 : x0 + side] = np.round(
                np.clip((patch - 255.0 * a_3) / np.maximum(0.25, 1.0 - a_3), 0.0, 255.0)
            )
        return Image.fromarray(arr.astype(np.uint8), mode="RGB")

    return rgb


def _postprocess_frame(raw_path: Path, dst_path: Path, target_size: tuple[int, int], overscan: float) -> None:
    with Image.open(raw_path) as im:
        im.load()
        cleaned = _clean_beluga_sparkle_adaptive(im)
        w, h = cleaned.size
        crop_w = max(16, int(round(w / overscan)))
        crop_h = max(16, int(round(h / overscan)))
        tw, th = target_size
        target_ratio = tw / float(th)
        if crop_w / float(crop_h) > target_ratio:
            crop_w = int(round(crop_h * target_ratio))
        else:
            crop_h = int(round(crop_w / target_ratio))
        left = max(0, (w - crop_w) // 2)
        top = max(0, (h - crop_h) // 2)
        resized = (
            cleaned.crop((left, top, min(w, left + crop_w), min(h, top + crop_h)))
            .resize(target_size, Image.Resampling.LANCZOS)
            .convert("RGB")
        )
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst_path.with_suffix(".tmp.png")
    resized.save(tmp, format="PNG", compress_level=6, optimize=True)
    os.replace(tmp, dst_path)


def _export_yt_safe_thumbnail(master_png: Path, yt_png: Path) -> Path:
    with Image.open(master_png) as im:
        im.load()
        rgb = im.convert("RGB")
        tmp_png = yt_png.with_suffix(".tmp.png")
        rgb.save(tmp_png, format="PNG", optimize=True, compress_level=9)
        if tmp_png.stat().st_size <= YT_MAX_THUMB_BYTES:
            os.replace(tmp_png, yt_png)
            return yt_png
        rgb.resize((810, 1440), Image.Resampling.LANCZOS).save(tmp_png, format="PNG", optimize=True, compress_level=9)
        if tmp_png.stat().st_size <= YT_MAX_THUMB_BYTES:
            os.replace(tmp_png, yt_png)
            return yt_png
        rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(
            tmp_png, format="PNG", optimize=True
        )
        os.replace(tmp_png, yt_png)
        return yt_png


def _cleanup_all_chrome() -> None:
    """Clean up Chrome instances owned by this process + dead-owner orphans only."""
    for fn in (
        lambda: get_process_manager().terminate_all(include_foreign_live_owners=False),
        lambda: stop_all_profiles(force_all=False),
    ):
        try:
            fn()
        except Exception as exc:
            logger.warning("Chrome teardown warning: %s", exc)


def _try_rescue_staged_asset(
    raw_path: Path,
    final_path: Path,
    target_size: tuple[int, int],
    overscan: float,
) -> bool:
    """Post-process an interrupted staging asset if it is already valid on disk."""
    if not raw_path.is_file() or raw_path.stat().st_size <= 30_000:
        return False
    try:
        _postprocess_frame(raw_path, final_path, target_size, overscan)
        raw_sc = raw_path.with_suffix(".json")
        if raw_sc.is_file():
            shutil.copy2(raw_sc, final_path.with_suffix(".json"))
        if _valid_png(final_path, target_size, require_rgb=True):
            logger.info("Rescued staged raw asset %s -> %s", raw_path.name, final_path.name)
            return True
    except Exception as exc:
        logger.debug("Could not rescue staged raw asset %s: %s", raw_path.name, exc)
    return False


def _resolve_1hop_parent_map(beats: list[dict[str, Any]]) -> dict[str, str | None]:
    beats_by_id = {str(b["beat_id"]): b for b in beats}
    tid_by_id = {str(b["beat_id"]): f"short_beat_{int(b['beat_index']):02d}" for b in beats}
    parent_map: dict[str, str | None] = {}
    for b in beats:
        bid = str(b["beat_id"])
        refs = [str(r) for r in (b.get("reference_scene_ids") or []) if str(r) in beats_by_id and str(r) != bid]
        if not refs:
            parent_map[bid] = None
            continue
        chosen = next((r for r in refs if not (beats_by_id[r].get("reference_scene_ids") or [])), None)
        if chosen is None:
            cur = refs[0]
            seen = {bid, cur}
            while beats_by_id[cur].get("reference_scene_ids"):
                nxt = [str(x) for x in beats_by_id[cur]["reference_scene_ids"] if str(x) in beats_by_id and str(x) not in seen]
                if not nxt:
                    break
                cur = nxt[0]
                seen.add(cur)
            chosen = cur
        parent_map[bid] = tid_by_id[chosen]
    return parent_map


def _ordered_stage_a_profiles(
    profiles: list[dict[str, Any]] | None = None,
    credits_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Order Flow profiles, honoring VP_FLOW_PROFILES override and Ultra 25k priority first."""
    base = [dict(p) for p in (profiles if profiles is not None else get_all_configured_profiles())]
    env_raw = os.environ.get("VP_FLOW_PROFILES", "").strip()
    if env_raw:
        requested = [x.strip() for x in env_raw.split(",") if x.strip()]
        if requested:
            by_name = {str(p.get("name") or p.get("id") or ""): p for p in base}
            filtered = [by_name[name] for name in requested if name in by_name]
            if filtered:
                return filtered

    c_path = credits_path or (Path.home() / ".config" / "video-pilot" / "flow" / "credits.json")
    credits_map: dict[str, dict[str, Any]] = {}
    if c_path.is_file():
        try:
            credits_map = json.loads(c_path.read_text(encoding="utf-8")).get("profiles") or {}
        except Exception:
            credits_map = {}

    now = time.time()

    def _sort_key(item: tuple[int, dict[str, Any]]) -> tuple[int, int, int, int]:
        idx, prof = item
        pid = str(prof.get("name") or prof.get("id") or "")
        info = credits_map.get(pid) or {}
        last_used = float(info.get("last_used_at") or 0.0)
        cooldown_until = float(info.get("cooldown_until") or 0.0)
        credits_rem = int(info.get("credits_remaining") or 0)
        ptier = int(info.get("paygate_tier") or 0)
        age = max(0.0, now - last_used) if last_used > 0.0 else 0.0
        if (credits_rem >= 5000 or ptier >= 2) and credits_rem > 0 and cooldown_until <= now:
            # Tier -1: Google AI Ultra 25k+ pools prioritized first
            return (-1, 0, -credits_rem, idx)
        ready_funded = last_used > 0.0 and credits_rem > 0 and cooldown_until <= now
        if ready_funded and 2700.0 <= age <= 172800.0:
            # Tier 0 (Goldilocks): warm auth (<= 48h) + rested past rolling-hour (>= 45m).
            return (0, 0, -credits_rem, idx)
        if ready_funded and age < 2700.0:
            return (1, 0, -credits_rem, idx)
        if ready_funded:
            # Tier 2: older verified funded accounts, least-stale first.
            return (2, int(age), -credits_rem, idx)
        if last_used > 0.0:
            return (3, int(max(0.0, cooldown_until - now)), -credits_rem, idx)
        return (4, 0, -credits_rem, idx)

    return [p for _, p in sorted(enumerate(base), key=_sort_key)]


def _resolve_stage_a_beluga_profiles(
    profiles: list[dict[str, Any]] | None = None,
    credits_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Order Stage A 0c BELUGA profiles using zero-credit specialists first, leaving Ultra 25k fresh for Stage B."""
    base = [dict(p) for p in (profiles if profiles is not None else get_all_configured_profiles())]
    env_raw = os.environ.get("VP_FLOW_PROFILES", "").strip()
    if env_raw:
        requested = [x.strip() for x in env_raw.split(",") if x.strip()]
        if requested:
            by_name = {str(p.get("name") or p.get("id") or ""): p for p in base}
            filtered = [by_name[name] for name in requested if name in by_name]
            if filtered:
                return filtered

    try:
        ledger = CreditLedger(path=credits_path)
        selector = getattr(ledger, "select_beluga_zero_credit_specialists", None)
        if callable(selector):
            specialist_ids = selector(profiles=base)
            if specialist_ids:
                by_id = {str(p.get("id") or p.get("name") or ""): p for p in base}
                by_name = {str(p.get("name") or p.get("id") or ""): p for p in base}
                ordered: list[dict[str, Any]] = []
                seen: set[str] = set()
                for pid in specialist_ids:
                    pid_str = str(pid).strip()
                    if not pid_str or pid_str in seen:
                        continue
                    prof = by_id.get(pid_str) or by_name.get(pid_str)
                    if prof is not None:
                        ordered.append(prof)
                        seen.add(pid_str)
                if ordered:
                    return ordered
    except Exception as exc:
        logger.warning("BELUGA specialist routing unavailable, falling back to configured profiles: %s", exc)

    return _ordered_stage_a_profiles(profiles=base, credits_path=credits_path)


def run_flow_stage_a(
    short_spec: dict[str, Any],
    spec_dir: Path,
    work_root: Path,
    *,
    max_workers: int = 8,
) -> dict[str, Any]:
    """Generate missing BELUGA 9:16 keyframe PNGs and Flow-native thumbnail with adaptive sparkle cleanup."""
    t0 = time.monotonic()
    beats = short_spec["beats"]
    frames_dir = spec_dir / "frames"
    staging_dir = work_root / "flow_raw_staging"
    frames_dir.mkdir(parents=True, exist_ok=True)
    staging_dir.mkdir(parents=True, exist_ok=True)

    logger.info("[STUDIO_STAGE 1/3] Starting Flow Stage A BELUGA (%d beats, max_workers=%d)", len(beats), max_workers)
    parent_map = _resolve_1hop_parent_map(beats)
    pending_ids: set[str] = set()
    for b in beats:
        idx = int(b["beat_index"])
        tid = f"short_beat_{idx:02d}"
        final_png = frames_dir / f"beat_{idx:02d}.png"
        if _valid_png(final_png, (1080, 1920), require_rgb=True):
            continue
        if _try_rescue_staged_asset(staging_dir / f"{tid}.jpg", final_png, (1080, 1920), STORY_OVERSCAN):
            continue
        pending_ids.add(tid)

    jobs: list[dict[str, Any]] = []
    for b in beats:
        idx = int(b["beat_index"])
        bid = str(b["beat_id"])
        tid = f"short_beat_{idx:02d}"
        if tid not in pending_ids:
            continue
        parent_tid = parent_map.get(bid)
        active_parent = parent_tid if (parent_tid and parent_tid in pending_ids) else None
        pre_media_id = pre_prof = None
        if parent_tid and active_parent is None and (staging_dir / f"{parent_tid}.json").is_file():
            try:
                sc_data = json.loads((staging_dir / f"{parent_tid}.json").read_text(encoding="utf-8"))
                pre_media_id = sc_data.get("forgeId") or sc_data.get("media_id")
                pre_prof = sc_data.get("profile_id")
            except Exception:
                pass
        jobs.append({
            "id": tid,
            "prompt": b["prompt"],
            "raw_path": staging_dir / f"{tid}.jpg",
            "final_path": frames_dir / f"beat_{idx:02d}.png",
            "target_size": (1080, 1920),
            "overscan": STORY_OVERSCAN,
            "based_on": active_parent,
            "baseMediaId": pre_media_id,
            "pinned_profile": pre_prof,
            "priority": 5 if active_parent else 0,
        })

    thumb_master = spec_dir / "thumbnail_9x16_master.png"
    thumb_yt = spec_dir / "thumbnail_9x16.png"
    thumb_ok = _valid_png(thumb_yt, (1080, 1920), require_rgb=False) and thumb_yt.stat().st_size < MAX_THUMB_LIMIT_BYTES
    if not thumb_ok and not _valid_png(thumb_master, (1080, 1920), require_rgb=True):
        if not _try_rescue_staged_asset(
            staging_dir / "short_thumb_9x16.jpg", thumb_master, (1080, 1920), THUMB_OVERSCAN
        ):
            jobs.append({
                "id": "short_thumb_9x16",
                "prompt": short_spec["thumbnail_spec"]["prompt"],
                "raw_path": staging_dir / "short_thumb_9x16.jpg",
                "final_path": thumb_master,
                "target_size": (1080, 1920),
                "overscan": THUMB_OVERSCAN,
                "based_on": None,
                "baseMediaId": None,
                "pinned_profile": None,
                "priority": 0,
            })

    if jobs:
        job_id_str = str(short_spec.get("job_id") or spec_dir.name)
        flow_lock = GlobalFlowProductionLock(job_id=job_id_str, stage="stage_a")
        acquired = flow_lock.acquire_patiently(
            timeout=7200.0,
            poll_interval=0.75,
            on_wait=lambda holder, waited: logger.info(
                "[RESOURCE_GUARD] Waiting for active Flow job %s (pid=%s, stage=%s, waited=%.1fs)...",
                holder.get("job_id", "unknown"),
                holder.get("pid", "?"),
                holder.get("stage", "?"),
                waited,
            ),
        )
        if not acquired:
            raise TimeoutError("Timed out waiting for GlobalFlowProductionLock in Stage A")
        ordered_profiles = _resolve_stage_a_beluga_profiles()
        eff_workers = min(max_workers, len(jobs), max(1, len(ordered_profiles)))
        try:
            pool = PersistentWorkerPool(
                profiles=ordered_profiles,
                target_workers=eff_workers,
                headless=True,
                default_out_dir=staging_dir,
                enforce_os_locks=True,
                max_global_browsers=max(min(eff_workers + 2, 6), int(DEFAULT_MAX_GLOBAL_BROWSERS)),
                min_credits_required=0,
                cooldown_seconds=float(os.environ.get("VP_STAGE_A_COOLDOWN_SEC", "25.0")),
                pacing_seconds=2.0,
                stagger_seconds=3.2,
                enable_rpc_batching=True,
                max_rpc_batch_size=4,
            )
            try:
                pool.start()
                for j in jobs:
                    j["raw_path"].unlink(missing_ok=True)
                    payload: dict[str, Any] = {
                        "id": j["id"],
                        "type": "image",
                        "model": "BELUGA",
                        "credit_cost": 0,
                        "credit_reason": "image",
                        "prompt": j["prompt"],
                        "aspect": "9:16",
                        "ratio": "9:16",
                        "output_path": str(j["raw_path"]),
                    }
                    if j.get("based_on"):
                        payload["based_on"] = j["based_on"]
                    elif j.get("baseMediaId") and j.get("pinned_profile"):
                        payload["baseMediaId"] = j["baseMediaId"]
                        payload["pinned_profile"] = j["pinned_profile"]
                    pool.submit_task(payload, priority=j["priority"])
                if not pool.wait_completion(timeout=2400.0):
                    raise RuntimeError("Stage A PersistentWorkerPool timed out")
            finally:
                try:
                    pool.shutdown()
                finally:
                    _cleanup_all_chrome()
        finally:
            flow_lock.release()

        for j in jobs:
            _postprocess_frame(j["raw_path"], j["final_path"], j["target_size"], j["overscan"])
            raw_sc = j["raw_path"].with_suffix(".json")
            if raw_sc.is_file():
                shutil.copy2(raw_sc, j["final_path"].with_suffix(".json"))

    if thumb_master.is_file() and (not thumb_yt.is_file() or thumb_yt.stat().st_size >= MAX_THUMB_LIMIT_BYTES):
        _export_yt_safe_thumbnail(thumb_master, thumb_yt)

    return {
        "status": "completed",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "generated_count": len(jobs),
        "total_frames": len(beats),
    }


OMNI12_VALID_DURATIONS = (4, 6, 8, 10)


def _is_v12_omni12_spec(short_spec: dict[str, Any]) -> bool:
    """Return True when V12 Omni 1.2 Flash variable gearbox is enabled on `short_spec`."""
    if bool(short_spec.get("v12_omni12_gearbox")):
        return True
    schema_ver = str(short_spec.get("schema_version") or "").strip().lower()
    return schema_ver.startswith("v12") or schema_ver.startswith("12.")


def _is_omni12_model_name(model: str) -> bool:
    low = (model or "").strip().lower()
    return any(tok in low for tok in ("omni", "macaron")) and not any(tok in low for tok in ("1_1", "1.1", "abra"))


def _resolve_beat_duration_sec(beat: dict[str, Any]) -> float:
    raw = beat.get("duration_sec")
    if raw is None:
        raw = beat.get("duration")
    if raw is None:
        start = beat.get("start_sec")
        end = beat.get("end_sec")
        if start is not None and end is not None:
            raw = max(0.5, float(end) - float(start))
    return float(raw) if raw is not None else 5.0


def _select_omni12_gearbox_duration(duration_sec: float) -> int:
    """Map beat duration (sec) to Omni 1.2 Flash variable gearbox {4, 6, 8, 10}."""
    if duration_sec <= 4.2:
        return 4
    if duration_sec <= 6.2:
        return 6
    if duration_sec <= 8.2:
        return 8
    return 10


def _explicit_clip_duration_sec(beat: dict[str, Any]) -> int | None:
    """Read an explicit per-beat `clip_duration_sec` / `duration_seconds` override in {4, 6, 8, 10}."""
    raw = beat.get("clip_duration_sec")
    if raw is None:
        raw = beat.get("duration_seconds")
    if raw is None:
        return None
    try:
        val = int(round(float(raw)))
    except (TypeError, ValueError):
        return None
    return val if val in OMNI12_VALID_DURATIONS else None


def _resolve_stage_b_beat_model_and_duration(
    beat: dict[str, Any],
    *,
    is_v12_spec: bool,
) -> tuple[str, int | None]:
    """Resolve Stage B video model and optional explicit {4, 6, 8, 10}s clip duration for a beat."""
    raw_vm = str(beat.get("video_model") or "").strip()
    explicit_dur = _explicit_clip_duration_sec(beat)
    beat_dur = _resolve_beat_duration_sec(beat)

    if raw_vm:
        if _is_omni12_model_name(raw_vm):
            chosen_dur = explicit_dur if explicit_dur is not None else _select_omni12_gearbox_duration(beat_dur)
            return ("omni_flash", chosen_dur)
        return (raw_vm, explicit_dur)

    if is_v12_spec:
        chosen_dur = explicit_dur if explicit_dur is not None else _select_omni12_gearbox_duration(beat_dur)
        return ("omni_flash", chosen_dur)

    return ("veo_3_1_lite", explicit_dur)


def _probe_mp4_duration_sec(mp4_path: Path) -> float:
    """Probe MP4 container duration in seconds via ffprobe."""
    try:
        res = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                str(mp4_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return max(0.0, float((res.stdout or "").strip() or "0"))
    except Exception:
        return 0.0


def _split_oner_clip_mp4(
    src_mp4: Path,
    split_sec: float,
    dst_first: Path,
    dst_second: Path,
) -> None:
    """Split a generated 10s unbroken oner MP4 frame-accurately at `t = split_sec` into 2 beat clips."""
    if not src_mp4.is_file():
        raise FileNotFoundError(f"Missing 10s oner source clip to split: {src_mp4}")

    src_dur = _probe_mp4_duration_sec(src_mp4)
    raw_split = max(0.5, float(split_sec))
    safe_split = min(raw_split, max(0.5, src_dur - 0.5)) if src_dur > 1.0 else raw_split

    dst_first.parent.mkdir(parents=True, exist_ok=True)
    dst_second.parent.mkdir(parents=True, exist_ok=True)
    tmp_first = dst_first.with_suffix(".tmp.mp4")
    tmp_second = dst_second.with_suffix(".tmp.mp4")

    common_out = [
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
    ]
    cmds = [
        (
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src_mp4), "-t", f"{safe_split:.6f}", *common_out, str(tmp_first)],
            tmp_first,
            dst_first,
        ),
        (
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src_mp4), "-ss", f"{safe_split:.6f}", *common_out, str(tmp_second)],
            tmp_second,
            dst_second,
        ),
    ]
    try:
        for cmd, tmp_p, final_p in cmds:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg oner split failed for {src_mp4.name} -> {final_p.name}: {(proc.stderr or proc.stdout)[-400:]}"
                )
            os.replace(tmp_p, final_p)
    finally:
        tmp_first.unlink(missing_ok=True)
        tmp_second.unlink(missing_ok=True)


def _build_scene_map_from_spec(short_spec: dict[str, Any], spec_dir: Path) -> SceneMap:
    smap_path = spec_dir / "scene_map.json"
    if smap_path.is_file():
        return SceneMap.from_json_file(smap_path)
    default_model = "omni_flash" if _is_v12_omni12_spec(short_spec) else "veo_3_1_lite"
    entries = [
        SceneMapEntry(
            scene_id=str(b["beat_id"]),
            time_range=f"{float(b.get('start_sec', 0)):.1f}-{float(b.get('end_sec', 5)):.1f}s",
            vo_snippet=str(b.get("display_text", "")),
            location=str(b.get("location", "scene")),
            hero_subject=str(b.get("hero_subject", "subject")),
            cast_spec=str(b.get("cast_spec", "none")),
            reference_scene_ids=[str(x) for x in (b.get("reference_scene_ids") or [])],
            camera_move=str(b.get("camera_move", "push_in")),
            exit_seam=str(b.get("exit_seam", "dark_opening")),
            transition_mode=str(b.get("transition_mode", "seam")),
            video_model=str(b.get("video_model") or default_model),
            beat_role=str(b.get("beat_role") or b.get("role") or "context"),
            lighting_key=str(b.get("lighting_key", "daylight")),
            person_count=int(b.get("person_count", 0)),
            scene_type=str(b.get("scene_type", "live_action")),
            delivery_mode=str(b.get("delivery_mode", "narrative_cinema")),
        )
        for b in short_spec["beats"]
    ]
    return SceneMap(
        job_id=str(short_spec["job_id"]),
        channel_id=str(short_spec["channel_id"]),
        format_profile="short_9x16",
        scenes=entries,
    )


def run_flow_stage_b(
    short_spec: dict[str, Any],
    spec_dir: Path,
    work_root: Path,
    *,
    visual_mode: str = "hybrid_2k",
    max_workers: int = 8,
) -> dict[str, Any]:
    """Generate Flow video clips ONLY for beats classified as `flow_video`."""
    t0 = time.monotonic()
    is_v12_spec = _is_v12_omni12_spec(short_spec)
    classified = classify_hybrid_beats(short_spec, visual_mode=visual_mode)
    flow_beats = [b for b in classified if b["asset_mode"] == "flow_video"]
    clips_dir = spec_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    if not flow_beats:
        return {"status": "completed", "elapsed_sec": 0.0, "clips_count": 0, "total_credit_cost": 0}

    frames_dir = spec_dir / "frames"
    flow_work = work_root / "flow_video"
    flow_work.mkdir(parents=True, exist_ok=True)
    smap = _build_scene_map_from_spec(short_spec, spec_dir)

    img_map: dict[str, str] = {}
    for i, sc in enumerate(smap.scenes):
        kf = frames_dir / f"beat_{i:02d}.png"
        if not _valid_png(kf, (1080, 1920), require_rgb=True):
            raise FileNotFoundError(f"Missing valid Stage A keyframe: {kf}")
        img_map[sc.scene_id] = str(kf.resolve())

    full_chain = build_dual_model_chain_spec(
        smap,
        work_dir=flow_work,
        aspect="9:16",
        prefer_credit_saving=True,
        image_paths_by_scene=img_map,
    )
    pair_by_id = {sp.id: sp for sp in full_chain.scene_pairs}

    filtered_pairs: list[ScenePairSpec] = []
    target_by_pair_id: dict[str, dict[str, Any]] = {}
    target_by_cid: dict[str, dict[str, Any]] = {}
    oner_pairs_planned = 0

    pos = 0
    while pos < len(flow_beats):
        b1 = flow_beats[pos]
        g1 = str(b1.get("oner_group_id") or "").strip()
        is_oner_pair = (
            bool(g1)
            and (pos + 1 < len(flow_beats))
            and str(flow_beats[pos + 1].get("oner_group_id") or "").strip() == g1
        )

        if is_oner_pair:
            b2 = flow_beats[pos + 1]
            pos += 2
            bid1, bid2 = str(b1["beat_id"]), str(b2["beat_id"])
            idx1, idx2 = int(b1["beat_index"]), int(b2["beat_index"])
            clip1 = clips_dir / f"clip_{idx1:02d}.mp4"
            clip2 = clips_dir / f"clip_{idx2:02d}.mp4"
            if (
                clip1.is_file()
                and clip1.stat().st_size > 200_000
                and clip2.is_file()
                and clip2.stat().st_size > 200_000
            ):
                continue

            dur1 = _resolve_beat_duration_sec(b1)
            dur2 = _resolve_beat_duration_sec(b2)
            pair_id = f"{bid1}_{bid2}_oner"
            p1 = str(b1.get("motion_prompt") or (pair_by_id[bid1].motion_prompt if bid1 in pair_by_id else "")).strip()
            p2 = str(b2.get("motion_prompt") or (pair_by_id[bid2].motion_prompt if bid2 in pair_by_id else "")).strip()
            if p1 and p2 and p2 != p1:
                combined_prompt = f"{p1} Continuing unbroken into: {p2}"
            else:
                combined_prompt = p1 or p2 or "continuous unbroken 10s Steadicam shot"

            sp = copy.deepcopy(pair_by_id.get(bid1) or ScenePairSpec(id=pair_id, start_image_path=img_map[bid1]))
            sp.id = pair_id
            sp.start_image_path = img_map[bid1]
            sp.motion_prompt = combined_prompt
            sp.video_model = "omni_flash"
            sp.target_duration = round(dur1 + dur2, 4)
            sp.clip_duration_sec = 10  # type: ignore[attr-defined]

            explicit_end_bid = str(b2.get("end_beat_id") or b1.get("end_beat_id") or "").strip()
            lk1 = str(b1.get("lighting_key") or "").strip().lower()
            lk2 = str(b2.get("lighting_key") or "").strip().lower()
            both_frame_link_same_lighting = (
                str(b1.get("transition_mode") or "").strip().lower() == "frame_link"
                and str(b2.get("transition_mode") or "").strip().lower() == "frame_link"
                and lk1 == lk2
            )
            if explicit_end_bid and explicit_end_bid in img_map:
                sp.transition_mode = "frame_link"
                sp.end_image_path = img_map[explicit_end_bid]
            elif both_frame_link_same_lighting and bid2 in img_map:
                # Only link b1 -> img_map[bid2] inside a same-lighting oner pair; NEVER cross into nxt_bid (b3).
                sp.transition_mode = "frame_link"
                sp.end_image_path = img_map[bid2]
            else:
                sp.transition_mode = "seam"
                sp.end_image_path = None
                sp.end_image_prompt = None

            target_meta: dict[str, Any] = {
                "kind": "oner_pair",
                "beat_indices": (idx1, idx2),
                "split_sec": dur1,
                "oner_group_id": g1,
            }
            cid = f"clip_{len(filtered_pairs):03d}_{pair_id}"
            target_by_pair_id[pair_id] = target_meta
            target_by_cid[cid] = target_meta
            filtered_pairs.append(sp)
            oner_pairs_planned += 1
            continue

        pos += 1
        bid = str(b1["beat_id"])
        orig_i = int(b1["beat_index"])
        existing_clip = clips_dir / f"clip_{orig_i:02d}.mp4"
        if existing_clip.is_file() and existing_clip.stat().st_size > 200_000:
            continue

        resolved_model, resolved_dur = _resolve_stage_b_beat_model_and_duration(b1, is_v12_spec=is_v12_spec)
        beat_dur = _resolve_beat_duration_sec(b1)
        sp = copy.deepcopy(pair_by_id.get(bid) or ScenePairSpec(id=bid, start_image_path=img_map[bid]))
        sp.target_duration = beat_dur
        sp.motion_prompt = str(b1.get("motion_prompt") or sp.motion_prompt)
        sp.video_model = resolved_model
        raw_tmode = str(b1.get("transition_mode") or "seam").strip().lower()
        if resolved_dur is not None:
            sp.clip_duration_sec = resolved_dur  # type: ignore[attr-defined]
        end_bid = str(b1.get("end_beat_id") or "").strip()
        if (
            raw_tmode == "frame_link"
            and "lite" not in sp.video_model.lower()
            and end_bid
            and end_bid in img_map
        ):
            sp.transition_mode = "frame_link"
            sp.end_image_path = img_map[end_bid]
        else:
            # Never auto-link incompatible next beats across scene cuts via START_END_FRAMES.
            sp.transition_mode = "seam"
            sp.end_image_path = None
            sp.end_image_prompt = None

        target_meta = {"kind": "single", "beat_index": orig_i}
        cid = f"clip_{len(filtered_pairs):03d}_{bid}"
        target_by_pair_id[bid] = target_meta
        target_by_cid[cid] = target_meta
        filtered_pairs.append(sp)

    if not filtered_pairs:
        return {
            "status": "completed",
            "elapsed_sec": round(time.monotonic() - t0, 2),
            "clips_count": len(flow_beats),
            "total_credit_cost": 0,
            "credits_deducted": {},
        }

    chain_video_model = (
        "omni_flash"
        if (is_v12_spec or any(_is_omni12_model_name(sp.video_model or "") for sp in filtered_pairs))
        else full_chain.video_model
    )
    chain_spec = VideoChainSpec(
        job_id=str(short_spec["job_id"]),
        mode=ChainMode.SCENE_PAIRS,
        channel_id=str(short_spec["channel_id"]),
        aspect="9:16",
        video_model=chain_video_model,
        duration_seconds=6,
        overscan_crop=1.0,
        auto_fallback_zero_credit=False,
        keep_veo_audio=False,
        no_talking_prompt_guard=not bool(short_spec.get("veo_native_foley")),
        scene_pairs=filtered_pairs,
    )

    logger.info(
        "[STUDIO_STAGE 2/3] Starting Flow Stage B Video (%d tasks covering %d flow beats, %d 10s oners, max_workers=%d)",
        len(filtered_pairs),
        len(flow_beats),
        oner_pairs_planned,
        max_workers,
    )
    orch = FlowVideoChainOrchestrator(
        spec=chain_spec,
        work_dir=flow_work,
        output_mp4_path=flow_work / f"{short_spec['job_id']}_raw_chain.mp4",
        max_workers=max_workers,
        headless=True,
        resume=True,
        max_retries_per_clip=12,
        skip_stitch=True,
        reuse_warm_sessions=True,
        skip_denied_tier0_lite=True,
    )
    flow_lock = GlobalFlowProductionLock(job_id=str(short_spec.get("job_id") or spec_dir.name), stage="stage_b")
    acquired = flow_lock.acquire_patiently(
        timeout=7200.0,
        poll_interval=0.75,
        on_wait=lambda holder, waited: logger.info(
            "[RESOURCE_GUARD] Waiting for active Flow job %s (pid=%s, stage=%s, waited=%.1fs)...",
            holder.get("job_id", "unknown"),
            holder.get("pid", "?"),
            holder.get("stage", "?"),
            waited,
        ),
    )
    if not acquired:
        raise TimeoutError("Timed out waiting for GlobalFlowProductionLock in Stage B")
    try:
        try:
            report = orch.run()
        finally:
            _cleanup_all_chrome()
    finally:
        flow_lock.release()

    for c in report.get("clips", []):
        cid = str(c["clip_id"])
        target = target_by_cid.get(cid)
        if target is None:
            target = target_by_pair_id.get(cid)
        if target is None and cid.startswith("clip_") and len(cid.split("_", 2)) == 3:
            target = target_by_pair_id.get(cid.split("_", 2)[2])
        if target is None:
            target = target_by_pair_id.get(cid.rsplit("_", 1)[-1])
        if target is None:
            raise KeyError(f"Unable to map orchestrator clip_id {cid!r} back to beat index")
        cp = Path(c["output_mp4_path"])
        if target["kind"] == "oner_pair":
            idx1, idx2 = target["beat_indices"]
            _split_oner_clip_mp4(
                cp,
                float(target["split_sec"]),
                clips_dir / f"clip_{idx1:02d}.mp4",
                clips_dir / f"clip_{idx2:02d}.mp4",
            )
        else:
            orig_idx = int(target["beat_index"])
            dst = clips_dir / f"clip_{orig_idx:02d}.mp4"
            if cp.resolve() != dst.resolve():
                shutil.copy2(cp, dst)

    missing_or_invalid: list[str] = []
    for b in flow_beats:
        orig_i = int(b["beat_index"])
        clip_path = clips_dir / f"clip_{orig_i:02d}.mp4"
        if not clip_path.is_file() or clip_path.stat().st_size <= 200_000:
            size = clip_path.stat().st_size if clip_path.is_file() else 0
            missing_or_invalid.append(f"{clip_path.name} ({size}B)")
    if missing_or_invalid:
        raise RuntimeError(
            "Flow Stage B completed without valid >200KB clips for beats: "
            + ", ".join(missing_or_invalid)
        )

    return {
        "status": "completed",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "clips_count": len(filtered_pairs),
        "oner_pairs_split": oner_pairs_planned,
        "total_credit_cost": report.get("total_credit_cost", 0),
        "credits_deducted": report.get("credits_deducted", {}),
    }
