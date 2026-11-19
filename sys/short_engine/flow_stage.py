"""Parallel Flow Stage A (BELUGA 9:16 images) & Stage B (selective tier-0 Omni video) for Short Engine V3."""
from __future__ import annotations

import copy
import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np
from flow_cdp import stop_all_profiles
from flow_cdp.multi_profile_manager import MultiProfileManager
from flow_cdp.persistent_pool import PersistentWorkerPool
from flow_cdp.process_manager import get_process_manager
from flow_cdp.resource_locks import DEFAULT_MAX_GLOBAL_BROWSERS
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


def resolve_worker_count(raw_value: str | int) -> int:
    """Resolve `auto` or numeric worker count cleanly within hardware limits."""
    if isinstance(raw_value, str) and raw_value.strip().lower() == "auto":
        return min(10, max(6, int(DEFAULT_MAX_GLOBAL_BROWSERS)))
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
        override = str(beat.get("asset_mode_override") or "").strip()

        if is_frame_link_pair:
            asset_mode = "flow_video"
        elif override in VALID_ASSET_MODES:
            asset_mode = override
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
    for fn in (
        lambda: MultiProfileManager().stop_all_profiles(),
        lambda: stop_all_profiles(force_all=True),
        lambda: get_process_manager().terminate_all(),
    ):
        try:
            fn()
        except Exception as exc:
            logger.warning("Chrome teardown warning: %s", exc)


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

    parent_map = _resolve_1hop_parent_map(beats)
    pending_ids = {
        f"short_beat_{int(b['beat_index']):02d}"
        for b in beats
        if not _valid_png(frames_dir / f"beat_{int(b['beat_index']):02d}.png", (1080, 1920), require_rgb=True)
    }
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
        pool = PersistentWorkerPool(
            target_workers=min(max_workers, len(jobs)),
            headless=True,
            default_out_dir=staging_dir,
            enforce_os_locks=True,
            max_global_browsers=max(max_workers, int(DEFAULT_MAX_GLOBAL_BROWSERS)),
            min_credits_required=0,
            cooldown_seconds=120.0,
            pacing_seconds=2.0,
            stagger_seconds=0.4,
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

        for j in jobs:
            _postprocess_frame(j["raw_path"], j["final_path"], j["target_size"], j["overscan"])

    if thumb_master.is_file() and (not thumb_yt.is_file() or thumb_yt.stat().st_size >= MAX_THUMB_LIMIT_BYTES):
        _export_yt_safe_thumbnail(thumb_master, thumb_yt)

    return {
        "status": "completed",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "generated_count": len(jobs),
        "total_frames": len(beats),
    }


def _build_scene_map_from_spec(short_spec: dict[str, Any], spec_dir: Path) -> SceneMap:
    smap_path = spec_dir / "scene_map.json"
    if smap_path.is_file():
        return SceneMap.from_json_file(smap_path)
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
            video_model=str(b.get("video_model", "veo_3_1_lite")),
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
    idx_by_bid: dict[str, int] = {}
    idx_by_cid: dict[str, int] = {}
    for seq_i, b in enumerate(flow_beats):
        bid = str(b["beat_id"])
        orig_i = int(b["beat_index"])
        idx_by_bid[bid] = orig_i
        idx_by_cid[f"clip_{seq_i:03d}_{bid}"] = orig_i
        sp = copy.deepcopy(pair_by_id.get(bid) or ScenePairSpec(id=bid, start_image_path=img_map[bid]))
        sp.target_duration = float(b.get("duration_sec") or b.get("duration") or 5.0)
        sp.motion_prompt = str(b.get("motion_prompt") or sp.motion_prompt)
        sp.video_model = str(b.get("video_model") or "veo_3_1_lite")
        sp.transition_mode = str(b.get("transition_mode") or "seam")
        if sp.transition_mode == "frame_link" and "lite" not in sp.video_model.lower():
            end_bid = b.get("end_beat_id")
            if end_bid and end_bid in img_map:
                sp.end_image_path = img_map[end_bid]
        else:
            sp.end_image_path = None
        filtered_pairs.append(sp)

    chain_spec = VideoChainSpec(
        job_id=str(short_spec["job_id"]),
        mode=ChainMode.SCENE_PAIRS,
        channel_id=str(short_spec["channel_id"]),
        aspect="9:16",
        video_model=full_chain.video_model,
        duration_seconds=6,
        overscan_crop=1.0,
        auto_fallback_zero_credit=False,
        keep_veo_audio=False,
        scene_pairs=filtered_pairs,
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
    try:
        report = orch.run()
    finally:
        _cleanup_all_chrome()

    for c in report.get("clips", []):
        cid = str(c["clip_id"])
        orig_idx = idx_by_cid.get(cid)
        if orig_idx is None:
            orig_idx = idx_by_bid.get(cid)
        if orig_idx is None:
            orig_idx = idx_by_bid.get(cid.rsplit("_", 1)[-1])
        if orig_idx is None:
            raise KeyError(f"Unable to map orchestrator clip_id {cid!r} back to beat index")
        cp = Path(c["output_mp4_path"])
        dst = clips_dir / f"clip_{orig_idx:02d}.mp4"
        if cp.resolve() != dst.resolve():
            shutil.copy2(cp, dst)

    return {
        "status": "completed",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "clips_count": len(filtered_pairs),
        "total_credit_cost": report.get("total_credit_cost", 0),
        "credits_deducted": report.get("credits_deducted", {}),
    }
