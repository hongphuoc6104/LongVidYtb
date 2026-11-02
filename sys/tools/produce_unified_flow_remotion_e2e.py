#!/usr/bin/env python3
"""Video Pilot — Unified Flow Remotion E2E Runner (produce_unified_flow_remotion_e2e.py).

Combines:
- Stage A: Flow CDP Full-Frame Images + Native Thumbnail (0-credit Nano Banana Pro / GEM_PIX_2)
- Stage B: Wave 4 Studio-Clean Fast Audio TTS on Colab Tesla T4
- Stage B retiming: exact measured audio retiming for long_16x9
- Authentic Start -> End 2-frame video synthesis (nprQif via DirectCDP / FlowVideoChainOrchestrator):
    * full_chain for Short 9x16: daisy chain across all non-endcard consecutive keyframes
    * hybrid for Long 16x9: hero clips for flow_motion beats (SC01 hook, midpoint, pre-outro)
- Automatic Remotion beat metadata registration (trim_before, playback_rate clamped to [0.65, 1.45])
- Stage C: Remote Colab Tesla T4 Headless Remotion NVENC render (1-word yellow/red captions on 9:16, BGM ducking, endcard watermark)
- Review queue registration (sys/channels/video_review_queue.json with PENDING_REVIEW)
- Publication kit generation
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from colab_bridge.client import Client  # noqa: E402
from flow_cdp.cdp_direct_client import get_all_configured_profiles  # noqa: E402
from flow_cdp.credit_ledger import CreditLedger  # noqa: E402
from flow_cdp.resource_locks import JobExecutionLock  # noqa: E402
from flow_video.chain_planner import apply_prompt_guard  # noqa: E402
from flow_video.models import ChainMode, KeyframeSpec, ScenePairSpec, VideoChainSpec  # noqa: E402
from flow_video.orchestrator import FlowVideoChainOrchestrator  # noqa: E402
from flow_video.stitcher import probe_video_clip  # noqa: E402
from tools.build_publish_kit import build_publish_kit  # noqa: E402
from tools.channel_production_common import (  # noqa: E402
    _sanitize_non_stickman_text,
    get_channel,
    get_channel_slice,
    resolve_channel_ids,
    stage_a_images,
    stage_b_audio,
    stage_c_render,
)
from tools.review_queue_manager import register_video_for_review  # noqa: E402
from visual_pacing import retime_long_beats_to_measured_audio  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("produce_unified_flow_remotion_e2e")


def resolve_motion_mode(
    motion_mode: Optional[str] = None,
    flow_profiles_arg: Optional[str] = None,
    ledger: Optional[Any] = None,
    profiles: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Resolve production motion mode based on Flow pool credit balance.

    Invariant:
    - Priority 1 (Default while ANY Flow pool profile has remaining video credits > 0):
      'full_chain' (100% continuous Omni 1.1 Flash / Veo 3.1 Lite video clips across all keyframes).
    - Priority 2 (Automatic Fallback ONLY when 100% of Flow pool profiles have 0 video credits left):
      'images_only' (dense multi-image mode using all generated Flow keyframes: 10-14 for 9:16, 28-70+ for 16:9).
    """
    raw_mode = str(motion_mode).lower().strip() if motion_mode else "auto"
    if raw_mode == "images_only":
        return "images_only"

    try:
        if ledger is None:
            ledger = CreditLedger()

        if profiles is not None:
            all_profiles = profiles
        else:
            try:
                all_profiles = get_all_configured_profiles()
            except Exception:
                all_profiles = []

        if flow_profiles_arg and all_profiles:
            explicit_names = {x.strip() for x in flow_profiles_arg.split(",") if x.strip()}
            target_profiles = [
                p
                for p in all_profiles
                if (p.get("name") in explicit_names or p.get("id") in explicit_names)
            ]
        else:
            target_profiles = all_profiles

        summary = ledger.get_pool_summary(profiles=target_profiles if target_profiles else None)
        total_p = summary.get("total_profiles", 0)
        video_ready = summary.get("video_ready_count", 0)
        total_cred = summary.get("total_available_credits", 0)

        # Fallback to images_only ONLY when 100% of evaluated profiles have 0 video credits left
        if total_p > 0 and video_ready == 0 and total_cred <= 0:
            logger.warning(
                "[!] Flow pool completely exhausted (0/%d profiles with video credits). "
                "Automatically falling back to dense multi-image mode ('images_only').",
                total_p,
            )
            return "images_only"

    except Exception as exc:
        logger.warning(f"Could not check credit pool summary ({exc}); defaulting to full_chain video mode.")

    if raw_mode == "hybrid":
        return "hybrid"
    return "full_chain"


def select_hybrid_hero_scenes(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Select scenes to animate via Flow Video Start -> End frames in hybrid mode.

    Prefers scenes, beats, or images explicitly flagged with flow_motion: true.
    If none are flagged, picks the opening Hook (SC01), early mechanism, midpoint peak,
    practical example, and closing pre-outro scene (up to 5 key hero clips).
    """
    flagged = [
        sc for sc in scenes
        if sc.get("flow_motion")
        or any(b.get("flow_motion") for b in sc.get("beats", []))
        or any(im.get("flow_motion") for im in sc.get("images", []))
    ]
    if flagged:
        return flagged

    non_endcards = [
        sc for sc in scenes
        if not (sc.get("is_endcard") or sc.get("spec") == "endcard")
    ]
    nb_scenes = len(non_endcards)
    if nb_scenes == 0:
        return []
    if nb_scenes <= 3:
        return non_endcards

    hero_indices = {
        0,
        max(1, nb_scenes // 4),
        nb_scenes // 2,
        max(1, (3 * nb_scenes) // 4),
        max(1, nb_scenes - 2),
    }
    return [non_endcards[i] for i in sorted(hero_indices) if i < nb_scenes]


def _clean_summary(text: str, max_chars: int = 140) -> str:
    """Clean and truncate string on word boundary without cutting words mid-stride."""
    cleaned = " ".join((text or "").split()).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    truncated = cleaned[:max_chars]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated.rstrip(",. ")


def collect_full_chain_keyframes(
    scenes: List[Dict[str, Any]],
    job_dir: Path,
    aspect_tag: str,
    ch_profile: Any,
    visual_style_id: str,
    audio_payload: Optional[Dict[str, Any]] = None,
) -> List[KeyframeSpec]:
    """Collect consecutive keyframes for continuous daisy chain animation (including terminal endcard target)."""
    seg_dur_by_scene: Dict[str, float] = {}
    if isinstance(audio_payload, dict):
        for sc_meta in audio_payload.get("scenes", []):
            if isinstance(sc_meta, dict) and sc_meta.get("id") and sc_meta.get("duration") is not None:
                seg_dur_by_scene[str(sc_meta["id"])] = float(sc_meta["duration"])
        if not seg_dur_by_scene:
            segments = []
            if isinstance(audio_payload.get("tracks"), dict):
                vi_track = audio_payload["tracks"].get("vi", {})
                if isinstance(vi_track, dict) and "segments" in vi_track:
                    segments = vi_track["segments"]
            if not segments:
                segments = audio_payload.get("segments", [])
            for seg in segments:
                s_id = seg.get("scene_id") or seg.get("scene")
                if s_id:
                    seg_dur_by_scene[str(s_id)] = seg_dur_by_scene.get(str(s_id), 0.0) + max(
                        0.0, float(seg.get("end", 0.0)) - float(seg.get("start", 0.0))
                    )

    avg_sc_dur = (
        float(audio_payload["duration"]) / max(1, len(scenes))
        if isinstance(audio_payload, dict) and audio_payload.get("duration")
        else 4.0
    )

    style_tag = (
        "Smooth 2D hand-drawn doodle explainer animation"
        if visual_style_id in ("ch_stickman_doodle", "handdrawn_2d_explainer", "1.7.0")
        else f"Smooth 2D explainer animation ({visual_style_id})"
    )

    seen_ids = set()
    raw_items: List[tuple[Dict[str, Any], Dict[str, Any], Path, float]] = []
    terminal_endcard_kf: Optional[KeyframeSpec] = None

    for sc in scenes:
        sc_id = str(sc.get("id", ""))
        sc_dur = seg_dur_by_scene.get(sc_id, float(sc.get("duration") or avg_sc_dur))
        sc_imgs = sc.get("images", [])

        non_endcard_imgs = [
            i
            for i in sc_imgs
            if not (sc.get("is_endcard") or sc.get("spec") == "endcard")
            and not (i.get("is_endcard") or i.get("spec") == "endcard")
        ]
        non_endcard_img_count = max(1, len(non_endcard_imgs))

        for im in sc_imgs:
            img_id = str(im.get("id", ""))
            if not img_id or img_id in seen_ids:
                continue

            img_candidates = [
                job_dir / f"revisions/images/1/{img_id}_{aspect_tag}.jpg",
                job_dir / f"revisions/images/1/{img_id}.jpg",
                job_dir / f"{img_id}_{aspect_tag}.jpg",
            ]
            img_path = next((c for c in img_candidates if c.is_file()), img_candidates[0])

            if sc.get("is_endcard") or sc.get("spec") == "endcard" or im.get("is_endcard") or im.get("spec") == "endcard":
                if terminal_endcard_kf is None and img_path.is_file():
                    terminal_endcard_kf = KeyframeSpec(
                        id=img_id,
                        image_path=str(img_path.resolve()),
                        motion_prompt="Clean static endcard hold, no talking, no lip movement",
                        target_duration=float(im.get("duration") or 2.5),
                    )
                seen_ids.add(img_id)
                continue

            matching_beats = [b for b in sc.get("beats", []) if isinstance(b, dict) and b.get("image_id") == img_id]
            beat_dur = 0.0
            if matching_beats:
                for b in matching_beats:
                    if b.get("duration") is not None:
                        beat_dur += float(b["duration"])
                    elif b.get("start") is not None and b.get("end") is not None:
                        beat_dur += max(0.0, float(b["end"]) - float(b["start"]))

            if beat_dur <= 0:
                beat_dur = float(im.get("duration") or max(1.5, sc_dur / non_endcard_img_count))

            seen_ids.add(img_id)
            raw_items.append((im, sc, img_path, beat_dur))

    keyframes: List[KeyframeSpec] = []
    total_items = len(raw_items)

    for i, (im, _sc, img_path, beat_dur) in enumerate(raw_items):
        img_id = str(im.get("id", ""))
        has_explicit_motion = bool(im.get("motion_prompt") and str(im["motion_prompt"]).strip())

        if has_explicit_motion:
            clean_mp = _sanitize_non_stickman_text(str(im["motion_prompt"]).strip(), ch_profile)
            if not clean_mp.startswith(style_tag):
                base_prompt = f"{style_tag}. {clean_mp.lstrip('. ')}"
            else:
                base_prompt = clean_mp
            motion_prompt = apply_prompt_guard(base_prompt, guard_enabled=True)
        else:
            start_desc = _sanitize_non_stickman_text(str(im.get("description") or "focal visual metaphor"), ch_profile)
            start_summary = _clean_summary(start_desc, 130)

            next_im = None
            if i + 1 < total_items:
                next_im = raw_items[i + 1][0]
            elif terminal_endcard_kf is not None:
                next_im = {"description": "channel outro endcard"}

            if next_im:
                next_desc = _sanitize_non_stickman_text(
                    str(next_im.get("motion_prompt") or next_im.get("description") or "next visual metaphor"),
                    ch_profile,
                )
                end_summary = _clean_summary(next_desc, 130)
                body = (
                    f"Seamless continuous 2D character animation evolving smoothly from "
                    f"{start_summary} into {end_summary}, dynamic hand-drawn motion"
                )
            else:
                body = f"Seamless continuous 2D character animation evolving smoothly from {start_summary}, dynamic hand-drawn motion"

            base_prompt = f"{style_tag}. {body}"
            if len(base_prompt) > 300:
                base_prompt = _clean_summary(base_prompt, 300)
            motion_prompt = apply_prompt_guard(base_prompt, guard_enabled=True)

        target_dur = round(beat_dur + 0.35, 2)
        keyframes.append(
            KeyframeSpec(
                id=img_id,
                image_path=str(img_path.resolve()) if img_path.is_file() else str(img_path),
                motion_prompt=motion_prompt,
                target_duration=target_dur,
            )
        )

    # Append terminal endcard keyframe as the final destination frame so the last story/bridge beat
    # also animates Start->End smoothly into the static endcard without overwriting the endcard beat itself.
    if terminal_endcard_kf is not None and len(keyframes) >= 1:
        keyframes.append(terminal_endcard_kf)

    return keyframes


def collect_hybrid_scene_pairs(
    scenes: List[Dict[str, Any]],
    hero_scenes: List[Dict[str, Any]],
    job_dir: Path,
    aspect_tag: str,
    ch_profile: Any,
    visual_style_id: str,
) -> List[ScenePairSpec]:
    """Collect Start -> End scene pairs for hero beats in Long 16x9 (1 pair per flagged beat or hero scene)."""
    scene_pairs: List[ScenePairSpec] = []
    all_scenes = scenes

    for sc in hero_scenes:
        sc_imgs = [
            im for im in sc.get("images", [])
            if not (im.get("is_endcard") or im.get("spec") == "endcard")
        ]
        if not sc_imgs:
            continue

        sc_id = str(sc.get("id", "SC"))
        style_tag = (
            "Smooth 2D hand-drawn doodle explainer animation"
            if visual_style_id in ("ch_stickman_doodle", "handdrawn_2d_explainer", "1.7.0")
            else f"Smooth 2D explainer animation ({visual_style_id})"
        )
        flagged_beat_img_ids = {
            b.get("image_id") for b in sc.get("beats", []) if b.get("flow_motion") and b.get("image_id")
        } | {
            im.get("id") for im in sc_imgs if im.get("flow_motion") and im.get("id")
        }

        if len(sc_imgs) >= 2:
            if flagged_beat_img_ids:
                candidate_indices = [
                    k for k in range(len(sc_imgs) - 1) if sc_imgs[k].get("id") in flagged_beat_img_ids
                ]
                if not candidate_indices:
                    candidate_indices = [0]
            else:
                # Default to 1 clean Start->End pair per hero scene (first 2 beats of the scene)
                candidate_indices = [0]

            for k in candidate_indices:
                im_s = sc_imgs[k]
                im_e = sc_imgs[k + 1]
                s_path = job_dir / f"revisions/images/1/{im_s['id']}_{aspect_tag}.jpg"
                e_path = job_dir / f"revisions/images/1/{im_e['id']}_{aspect_tag}.jpg"

                if im_s.get("motion_prompt") and str(im_s["motion_prompt"]).strip():
                    clean_mp = _sanitize_non_stickman_text(str(im_s["motion_prompt"]).strip(), ch_profile)
                    if not clean_mp.startswith(style_tag):
                        base_prompt = f"{style_tag}. {clean_mp.lstrip('. ')}"
                    else:
                        base_prompt = clean_mp
                    prompt = apply_prompt_guard(base_prompt, guard_enabled=True)
                else:
                    start_desc = _sanitize_non_stickman_text(
                        str(im_s.get("description") or "hero scene transition"), ch_profile
                    )
                    start_summary = _clean_summary(start_desc, 130)
                    end_desc = _sanitize_non_stickman_text(
                        str(im_e.get("motion_prompt") or im_e.get("description") or "next key visual"),
                        ch_profile,
                    )
                    end_summary = _clean_summary(end_desc, 130)
                    body = (
                        f"Seamless continuous 2D character animation evolving smoothly from "
                        f"{start_summary} into {end_summary}, dynamic hand-drawn motion"
                    )
                    base_prompt = f"{style_tag}. {body}"
                    if len(base_prompt) > 300:
                        base_prompt = _clean_summary(base_prompt, 300)
                    prompt = apply_prompt_guard(base_prompt, guard_enabled=True)

                dur = float(im_s.get("duration") or 4.0)
                scene_pairs.append(
                    ScenePairSpec(
                        id=f"pair_{sc_id}_{im_s['id']}_to_{im_e['id']}",
                        start_image_path=str(s_path.resolve()) if s_path.is_file() else str(s_path),
                        end_image_path=str(e_path.resolve()) if e_path.is_file() else str(e_path),
                        motion_prompt=prompt,
                        target_duration=dur,
                    )
                )
        else:
            im_s = sc_imgs[0]
            s_path = job_dir / f"revisions/images/1/{im_s['id']}_{aspect_tag}.jpg"
            curr_idx = next((i for i, s in enumerate(all_scenes) if s.get("id") == sc.get("id")), -1)
            next_img = None
            if 0 <= curr_idx < len(all_scenes) - 1:
                next_sc = all_scenes[curr_idx + 1]
                if not (next_sc.get("is_endcard") or next_sc.get("spec") == "endcard"):
                    next_imgs = [i for i in next_sc.get("images", []) if not (i.get("is_endcard") or i.get("spec") == "endcard")]
                    if next_imgs:
                        next_img = next_imgs[0]

            e_path = (job_dir / f"revisions/images/1/{next_img['id']}_{aspect_tag}.jpg") if next_img else None

            if im_s.get("motion_prompt") and str(im_s["motion_prompt"]).strip():
                clean_mp = _sanitize_non_stickman_text(str(im_s["motion_prompt"]).strip(), ch_profile)
                if not clean_mp.startswith(style_tag):
                    base_prompt = f"{style_tag}. {clean_mp.lstrip('. ')}"
                else:
                    base_prompt = clean_mp
                prompt = apply_prompt_guard(base_prompt, guard_enabled=True)
            else:
                start_desc = _sanitize_non_stickman_text(
                    str(im_s.get("description") or "hero scene transition"), ch_profile
                )
                start_summary = _clean_summary(start_desc, 130)
                if next_img:
                    end_desc = _sanitize_non_stickman_text(
                        str(next_img.get("motion_prompt") or next_img.get("description") or "next key visual"),
                        ch_profile,
                    )
                    end_summary = _clean_summary(end_desc, 130)
                    body = (
                        f"Seamless continuous 2D character animation evolving smoothly from "
                        f"{start_summary} into {end_summary}, dynamic hand-drawn motion"
                    )
                else:
                    body = f"Seamless continuous 2D character animation evolving smoothly from {start_summary}, dynamic hand-drawn motion"
                base_prompt = f"{style_tag}. {body}"
                if len(base_prompt) > 300:
                    base_prompt = _clean_summary(base_prompt, 300)
                prompt = apply_prompt_guard(base_prompt, guard_enabled=True)

            dur = float(im_s.get("duration") or 4.0)
            scene_pairs.append(
                ScenePairSpec(
                    id=f"pair_{sc_id}_{im_s['id']}",
                    start_image_path=str(s_path.resolve()) if s_path.is_file() else str(s_path),
                    end_image_path=str(e_path.resolve()) if e_path and e_path.is_file() else (str(e_path) if e_path else None),
                    motion_prompt=prompt,
                    target_duration=dur,
                )
            )

    return scene_pairs


def register_clips_to_timeline(
    tasks: List[Any],
    images_payload: Dict[str, Any],
    content: Dict[str, Any],
    mode: ChainMode,
    keyframes: List[KeyframeSpec],
    scene_pairs: List[ScenePairSpec],
    aspect_ratio: str,
    audio_payload: Optional[Dict[str, Any]] = None,
) -> int:
    """Register generated Flow Video MP4 clips into images_payload and content scenes.

    Sets:
    - trim_before: 1 on daisy-chained clips i >= 1 (0 on first clip or scene pairs)
    - playback_rate: round(clip_dur / beat_dur, 3) clamped to [0.65, 1.45]
    """
    items = images_payload.setdefault("items", [])
    items_by_id = {it.get("image_id"): it for it in items if isinstance(it, dict) and "image_id" in it}
    seg_dur_by_scene: Dict[str, float] = {}
    if isinstance(audio_payload, dict):
        for sc_meta in audio_payload.get("scenes", []):
            if isinstance(sc_meta, dict) and sc_meta.get("id") and sc_meta.get("duration") is not None:
                seg_dur_by_scene[str(sc_meta["id"])] = float(sc_meta["duration"])
        if not seg_dur_by_scene:
            for seg in audio_payload.get("segments", []):
                s_id = seg.get("scene_id") or seg.get("scene")
                if s_id:
                    seg_dur_by_scene[s_id] = seg_dur_by_scene.get(s_id, 0.0) + max(
                        0.0, float(seg.get("end", 0.0)) - float(seg.get("start", 0.0))
                    )

    registered_count = 0

    for task in tasks:
        t_dict = task.to_dict() if hasattr(task, "to_dict") else dict(task)
        if t_dict.get("status") != "completed":
            continue

        mp4_path = t_dict.get("output_mp4_path")
        if not mp4_path or not Path(mp4_path).is_file():
            continue

        idx = int(t_dict.get("index", 0))

        if mode == ChainMode.DAISY_CHAIN and idx < len(keyframes):
            assigned_img_id = keyframes[idx].id
            trim_before_val = 1 if idx > 0 else 0
        elif mode == ChainMode.SCENE_PAIRS and idx < len(scene_pairs):
            sp = scene_pairs[idx]
            start_stem = Path(sp.start_image_path).stem.replace("_16x9", "").replace("_9x16", "")
            assigned_img_id = start_stem
            trim_before_val = 0
        else:
            clip_id = str(t_dict.get("clip_id", ""))
            assigned_img_id = clip_id
            trim_before_val = 1 if t_dict.get("trim_first_frame") else 0

        try:
            meta = probe_video_clip(mp4_path)
            clip_dur = float(meta["duration"])
        except Exception:
            clip_dur = float(t_dict.get("duration_sec") or t_dict.get("duration_seconds") or 5.0)

        resolved_mp4 = str(Path(mp4_path).resolve())
        if assigned_img_id in items_by_id:
            items_by_id[assigned_img_id]["path"] = resolved_mp4
            items_by_id[assigned_img_id]["kind"] = "scene"
            items_by_id[assigned_img_id].setdefault("ratio", aspect_ratio)
        else:
            new_item = {
                "image_id": assigned_img_id,
                "path": resolved_mp4,
                "aspect_ratio": aspect_ratio,
                "ratio": aspect_ratio,
                "kind": "scene",
            }
            items.append(new_item)
            items_by_id[assigned_img_id] = new_item

        for sc in content.get("scenes", []):
            sc_dur = float(seg_dur_by_scene.get(sc.get("id")) or sc.get("duration") or 4.0)
            for b in sc.get("beats", []):
                b_img_id = b.get("image_id") or b.get("id")
                if b_img_id == assigned_img_id:
                    beat_dur = float(b.get("target_duration") or b.get("duration") or (sc_dur / max(1, len(sc.get("beats", [])))))
                    b["src"] = resolved_mp4
                    b["trim_before"] = trim_before_val
                    b["clip_duration"] = round(clip_dur, 3)
                    effective_raw_dur = max(0.3, clip_dur - (trim_before_val / 30.0) - 0.05)
                    if beat_dur > 0:
                        calc_rate = effective_raw_dur / (beat_dur + 0.15)
                        b["playback_rate"] = round(max(0.28, min(1.45, calc_rate)), 3)
                    else:
                        b["playback_rate"] = 1.0

        registered_count += 1

    return registered_count


def produce_unified_flow_remotion_e2e(
    channel_arg: str,
    job_id_arg: Optional[str] = None,
    format_profile: str = "short_9x16",
    motion_mode: Optional[str] = None,
    video_model: str = "omni_flash",
    colab_account: Optional[str] = None,
    session_name: Optional[str] = None,
    flow_profiles_arg: Optional[str] = None,
    max_flow_workers: Optional[int] = None,
    force_audio: bool = False,
    inspect_dir: Optional[Path] = None,
    dry_run: bool = False,
    credit_ledger: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute Unified Flow + Remotion E2E production runner."""
    channel_id, channel_slug = resolve_channel_ids(channel_arg)
    is_long = (format_profile == "long_16x9")
    aspect_ratio = "16:9" if is_long else "9:16"
    aspect_tag = "16x9" if is_long else "9x16"

    # Default motion mode: 100% continuous full_chain for both short and long while ANY Flow profile has credits;
    # automatically falls back to dense multi-image (images_only) ONLY when 100% of Flow pool profiles are exhausted.
    resolved_motion_mode = resolve_motion_mode(
        motion_mode=motion_mode,
        flow_profiles_arg=flow_profiles_arg,
        ledger=credit_ledger,
    )

    job_id = job_id_arg or f"{channel_slug}-week1-{aspect_tag}"

    job_lock = JobExecutionLock(job_id)
    if not job_lock.try_acquire():
        raise RuntimeError(f"Job '{job_id}' is already running in another process")

    last_active_client: Optional[Client] = None
    last_active_account: Optional[str] = None
    target_session: Optional[str] = None

    try:
        candidate_job_dirs = [
            SYS_DIR / "runs" / job_id,
            Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/sys/runs/{job_id}"),
            Path(f"/home/hongphuoc6104/Desktop/vp-agent-core/sys/runs/{job_id}"),
        ]
        if job_id_arg and Path(job_id_arg).is_dir():
            candidate_job_dirs.insert(0, Path(job_id_arg))

        job_dir = None
        for cd in candidate_job_dirs:
            if cd.is_dir() and (cd / "content.json").is_file():
                job_dir = cd
                break

        if not job_dir:
            raise FileNotFoundError(f"Could not locate job directory for '{job_id}' (searched: {candidate_job_dirs})")

        is_isolated_job = (
            not str(job_dir.resolve()).startswith(str(ROOT_DIR.resolve()))
            and not str(job_dir.resolve()).startswith("/home/hongphuoc6104/Desktop/vp-channels/")
        )
        if (job_dir.parents[1] / "config.json").is_file():
            active_sys_dir = job_dir.parents[1]
            active_root_dir = active_sys_dir.parent
        elif is_isolated_job and len(job_dir.parents) >= 2 and job_dir.parents[0].name == "runs":
            active_sys_dir = job_dir.parents[1]
            active_root_dir = active_sys_dir.parent
        elif is_isolated_job and len(job_dir.parents) >= 1:
            active_sys_dir = job_dir.parents[0]
            active_root_dir = active_sys_dir.parent
        else:
            active_sys_dir = SYS_DIR
            active_root_dir = ROOT_DIR

        part_flow, part_colab, default_session = get_channel_slice(channel_id)
        target_account = colab_account or (part_colab[0] if part_colab else "account-01")
        target_session = session_name or default_session

        try:
            ch_profile = get_channel(channel_id)
        except Exception:
            ch_profile = get_channel("nao_luoi")
        ch_name = getattr(ch_profile, "name", channel_id)
        visual_style_id = getattr(getattr(ch_profile, "visual", None), "profile_id", "handdrawn_2d_explainer")

        logger.info("=" * 76)
        logger.info(f"  STARTING UNIFIED FLOW + REMOTION E2E PRODUCTION: {job_id}")
        logger.info(f"  Channel: {channel_id} ({ch_name})")
        logger.info(f"  Format: {format_profile} ({aspect_ratio})")
        logger.info(f"  Motion Mode: {resolved_motion_mode} | Video Model: {video_model}")
        logger.info(f"  Colab Session: {target_session} (preferred account: {target_account})")
        logger.info(f"  Job Dir: {job_dir}")
        logger.info("=" * 76)

        brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
        content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))

        # ---------------------------------------------------------------------
        # Step a: Run Stage A (Flow Images) & Stage B (Colab Audio) in Parallel
        # ---------------------------------------------------------------------
        logger.info("[*] Bước A & B: Chạy song song sinh ảnh Flow CDP và tổng hợp giọng OmniVoice trên Colab T4...")
        if max_flow_workers is not None and int(max_flow_workers) > 0:
            import os
            os.environ["VP_FLOW_MAX_WORKERS"] = str(int(max_flow_workers))
            os.environ["VP_WORKERS_PER_JOB"] = str(int(max_flow_workers))
        if flow_profiles_arg:
            import os
            os.environ["VP_FLOW_PROFILES"] = str(flow_profiles_arg)

        with ThreadPoolExecutor(max_workers=2) as executor:
            fut_images = executor.submit(
                stage_a_images,
                sys_dir=active_sys_dir,
                job_dir=job_dir,
                channel_id=channel_id,
                brief=brief,
                content=content,
                format_profile=format_profile,
                flow_profiles_arg=flow_profiles_arg,
            )
            fut_audio = executor.submit(
                stage_b_audio,
                sys_dir=active_sys_dir,
                job_dir=job_dir,
                channel_id=channel_id,
                channel_slug=channel_slug,
                brief=brief,
                content=content,
                format_profile=format_profile,
                colab_account=target_account,
                session_name=target_session,
                force_audio=force_audio,
            )

        if fut_audio.exception() is None:
            audio_payload, audio_client, audio_account = fut_audio.result()
            if audio_client:
                last_active_client = audio_client
            if audio_account:
                last_active_account = audio_account
        else:
            fut_audio.result()

        images_output = fut_images.result()

        # ---------------------------------------------------------------------
        # Step b: Audio Retiming Gate for long_16x9
        # ---------------------------------------------------------------------
        if is_long:
            logger.info("[*] Bước B.2: Re-timing beats theo audio WAV thực tế cho long_16x9...")
            content, pacing_meta = retime_long_beats_to_measured_audio(
                content=content,
                audio_payload=audio_payload,
                target_hold_sec=2.8,
            )
            if resolved_motion_mode == "full_chain":
                # Protect 1-to-1 clip-to-beat mapping: deduplicate any split beats reusing an existing image_id
                for sc in content.get("scenes", []):
                    original_beats = sc.get("beats", [])
                    deduped_beats: list[dict] = []
                    seen_beat_images: dict[str, dict] = {}
                    for b in original_beats:
                        img_id = b.get("image_id")
                        if img_id and img_id in seen_beat_images:
                            seen_beat_images[img_id]["duration"] = round(
                                float(seen_beat_images[img_id].get("duration", 0.0)) + float(b.get("duration", 0.0)),
                                3,
                            )
                        else:
                            deduped_beats.append(b)
                            if img_id:
                                seen_beat_images[img_id] = b
                    sc["beats"] = deduped_beats

            logger.info(
                f"  [✓] Retimed {pacing_meta.get('beats')} beats, avg_hold = {pacing_meta.get('avg_hold')}s"
            )
            content_path = job_dir / "content.json"
            content_path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # ---------------------------------------------------------------------
        # Step c: Synthesize Start -> End 2-Frame Video Clips (Flow Video)
        # ---------------------------------------------------------------------
        flow_video_dir = job_dir / "revisions/flow_video/1"
        flow_video_dir.mkdir(parents=True, exist_ok=True)
        narration_wav = job_dir / "revisions/audio/1/narration.wav"
        from flow_cdp.lifecycle import calculate_optimal_workers

        keyframes: List[KeyframeSpec] = []
        scene_pairs: List[ScenePairSpec] = []
        chain_mode_resolved = ChainMode.DAISY_CHAIN

        if resolved_motion_mode == "full_chain":
            chain_mode_resolved = ChainMode.DAISY_CHAIN
            keyframes = collect_full_chain_keyframes(
                scenes=content.get("scenes", []),
                job_dir=job_dir,
                aspect_tag=aspect_tag,
                ch_profile=ch_profile,
                visual_style_id=visual_style_id,
                audio_payload=audio_payload,
            )
            logger.info(f"[*] Bước C (Full-Chain {aspect_tag}): Chuẩn bị {len(keyframes)} non-endcard keyframes...")

        elif resolved_motion_mode == "hybrid":
            chain_mode_resolved = ChainMode.SCENE_PAIRS
            hero_scenes = select_hybrid_hero_scenes(content.get("scenes", []))
            scene_pairs = collect_hybrid_scene_pairs(
                scenes=content.get("scenes", []),
                hero_scenes=hero_scenes,
                job_dir=job_dir,
                aspect_tag=aspect_tag,
                ch_profile=ch_profile,
                visual_style_id=visual_style_id,
            )
            logger.info(f"[*] Bước C (Hybrid 16x9): Chuẩn bị {len(scene_pairs)} hero scene pairs ({[sc['id'] for sc in hero_scenes]})...")

        render_content = copy.deepcopy(content)
        clips_generated_count = 0
        if resolved_motion_mode in ("full_chain", "hybrid") and (len(keyframes) >= 2 or len(scene_pairs) >= 1):
            planned_clips = max(1, (len(keyframes) - 1) if chain_mode_resolved == ChainMode.DAISY_CHAIN else len(scene_pairs))
            if max_flow_workers is not None and int(max_flow_workers) > 0:
                worker_limit = max(1, min(16, int(max_flow_workers)))
            else:
                worker_limit = min(planned_clips, calculate_optimal_workers(planned_clips * 3, max_cap=12, min_cap=2))
            spec = VideoChainSpec(
                job_id=job_id,
                mode=chain_mode_resolved,
                aspect=aspect_ratio,
                video_model=video_model,
                duration_seconds=6,
                keyframes=keyframes,
                scene_pairs=scene_pairs,
                audio_path=str(narration_wav.resolve()) if narration_wav.is_file() else None,
                no_talking_prompt_guard=True,
                target_fps=30,
                auto_duration=True,
                auto_fallback_zero_credit=False,  # Authentic high-credit Flow Video generation
                channel_id=channel_id,
            )
            orchestrator = FlowVideoChainOrchestrator(
                spec=spec,
                work_dir=flow_video_dir,
                max_workers=worker_limit,
                headless=True,
                resume=True,
                dry_run=dry_run,
                skip_stitch=True,
            )
            if credit_ledger is not None:
                orchestrator.credit_ledger = credit_ledger

            try:
                orchestrator_report = orchestrator.run()
            except Exception as exc_orch:
                err_str = str(exc_orch).lower()
                is_credit_exhausted = any(
                    term in err_str
                    for term in (
                        "exhausted",
                        "insufficient credits",
                        "no eligible chrome profiles",
                        "quota_exceeded",
                        "quota",
                        "captcha",
                    )
                )
                if is_credit_exhausted:
                    logger.warning(
                        f"[!] FlowVideoChainOrchestrator encountered pool-wide credit exhaustion: {exc_orch}. "
                        "Automatically falling back to dense multi-image mode ('images_only') using all generated Flow keyframes!"
                    )
                    orchestrator_report = {"clips": [], "tasks": [], "exhausted": True}
                    resolved_motion_mode = "images_only"
                else:
                    raise

            # -----------------------------------------------------------------
            # Step d: Register Generated MP4 Clips into Timeline & images_payload
            # -----------------------------------------------------------------
            clip_entries = orchestrator_report.get("clips") or orchestrator_report.get("tasks") or []
            if clip_entries and resolved_motion_mode != "images_only":
                logger.info("[*] Bước D: Đăng ký video clips vào timeline Remotion (trim_before & playback_rate)...")
                clips_generated_count = register_clips_to_timeline(
                    tasks=clip_entries,
                    images_payload=images_output,
                    content=render_content,
                    mode=chain_mode_resolved,
                    keyframes=keyframes,
                    scene_pairs=scene_pairs,
                    aspect_ratio=aspect_ratio,
                    audio_payload=audio_payload,
                )
                logger.info(f"  [✓] Đã đăng ký {clips_generated_count} video clip vào timeline Remotion.")

                timeline_content_path = flow_video_dir / "timeline_content.json"
                timeline_content_path.write_text(
                    json.dumps(render_content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )
            else:
                logger.warning(
                    "[*] Bước C/D: 0 video clip hoàn thành hoặc pool credit cạn kiệt. "
                    "Chuyển sang chế độ dense multi-image ('images_only') sử dụng toàn bộ keyframes đã tạo!"
                )
                resolved_motion_mode = "images_only"
                render_content = copy.deepcopy(content)
        else:
            logger.info("[*] Bước C/D: Chế độ images_only hoặc không đủ keyframes -> Giữ nguyên ảnh tĩnh Flow.")

        # ---------------------------------------------------------------------
        # Step e: Stage C Remotion NVENC Render on Colab Tesla T4
        # ---------------------------------------------------------------------
        logger.info("[*] Bước E: Tiến hành Remotion Render trên Colab Tesla T4 NVENC...")
        final_mp4, render_client, render_account, render_report = stage_c_render(
            sys_dir=active_sys_dir,
            job_dir=job_dir,
            root_dir=active_root_dir,
            brief=brief,
            content=render_content,
            images_payload=images_output,
            audio_payload=audio_payload,
            format_profile=format_profile,
            colab_account=colab_account or (audio_account if audio_account in part_colab else part_colab[0]),
            session_name=target_session,
            inspect_dir=inspect_dir,
        )
        if render_client:
            last_active_client = render_client
        if render_account:
            last_active_account = render_account

        # Generate publication kit
        try:
            logger.info(f"Generating Vietnamese publication kit for {channel_id} / {job_id}...")
            build_publish_kit(channel_id=channel_id, job_id=job_id, root_dir=active_root_dir)
            logger.info("  [✓] Publication kit generated successfully.")
        except Exception as ex_pub:
            logger.warning(f"Could not generate publication kit: {ex_pub}")

        # Synchronize deliverables across workspace trees (skip for isolated test roots)
        source_video_dir = active_root_dir / "video" / job_id
        is_isolated_root = (
            active_root_dir.resolve() != ROOT_DIR.resolve()
            and not str(active_root_dir.resolve()).startswith("/home/hongphuoc6104/Desktop/vp-channels/")
        )
        if not is_isolated_root:
            target_video_dirs = [
                ROOT_DIR / "video" / job_id,
                Path(f"/home/hongphuoc6104/Desktop/vp-channels/channel-{channel_slug}/video/{job_id}"),
            ]
            for tvd in target_video_dirs:
                if tvd.resolve() != source_video_dir.resolve() and tvd.parent.parent.is_dir():
                    try:
                        shutil.copytree(source_video_dir, tvd, dirs_exist_ok=True)
                        logger.info(f"  [✓] Synchronized deliverables to {tvd}")
                    except Exception as ex_sync:
                        logger.warning(f"Could not sync deliverables to {tvd}: {ex_sync}")

        # ---------------------------------------------------------------------
        # Step f: Register Video for Review in review queue
        # ---------------------------------------------------------------------
        logger.info("[*] Bước F: Đăng ký video vào hàng đợi phê duyệt (video_review_queue.json)...")
        title = brief.get("packaging", {}).get("youtube_title") or brief.get("title") or job_id
        thumb_file = source_video_dir / f"thumbnail_{aspect_tag}.jpg"
        if not thumb_file.is_file():
            thumb_file = job_dir / f"revisions/images/1/THUMBNAIL_{aspect_tag}.jpg"

        srt_file = source_video_dir / f"{job_id}.srt"
        if not srt_file.is_file():
            srt_file = job_dir / "revisions/audio/1/subtitles.srt"

        registered_item = register_video_for_review(
            job_id=job_id,
            channel_id=channel_id,
            channel_name=ch_name,
            format_profile=format_profile,
            title=title,
            mp4_path=str(final_mp4.resolve()) if final_mp4.is_file() else "",
            thumbnail_path=str(thumb_file.resolve()) if thumb_file.is_file() else "",
            srt_path=str(srt_file.resolve()) if srt_file.is_file() else "",
            duration_sec=float(render_report.get("duration", 0.0)),
            competitor_formula=brief.get("competitor_formula", ""),
            queue_path=(active_sys_dir / "channels" / "video_review_queue.json") if is_isolated_root else None,
            reset_status=True,
        )
        logger.info(f"  [✓] Đã cập nhật review queue trạng thái: {registered_item.get('status')}")

        summary = {
            "status": "SUCCESS",
            "job_id": job_id,
            "channel": channel_id,
            "format": format_profile,
            "motion_mode": resolved_motion_mode,
            "video_model": video_model,
            "clips_generated": clips_generated_count,
            "deliverables": {
                "mp4": str(final_mp4),
                "srt": str(srt_file),
                "thumbnail": str(thumb_file),
            },
            "render": render_report,
            "review_queue": {
                "status": registered_item.get("status"),
                "job_id": job_id,
            },
        }

        print("\n" + "=" * 76)
        print("  UNIFIED FLOW + REMOTION E2E COMPLETE:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print("=" * 76 + "\n")
        return summary

    finally:
        if last_active_client and last_active_account and target_session:
            try:
                logger.info(f"Stopping Colab session '{target_session}' on {last_active_account}...")
                last_active_client.stop()
                logger.info(f"Cleanly released Colab session on {last_active_account}.")
            except Exception as ex_stop:
                logger.warning(f"Failed stopping Colab session on {last_active_account}: {ex_stop}")
        job_lock.release()


def main():
    parser = argparse.ArgumentParser(description="Video Pilot — Unified Flow Remotion E2E Runner")
    parser.add_argument("--channel", required=False, help="Channel identifier or slug (e.g. nao_luoi, tui_tien)")
    parser.add_argument("--job", "--job-id", dest="job", required=False, help="Job identifier (defaults to <channel_slug>-week1-<format>)")
    parser.add_argument("--format", default="short_9x16", choices=["short_9x16", "long_16x9"], help="Video format profile")
    parser.add_argument("--motion-mode", default=None, choices=["full_chain", "hybrid", "images_only"], help="Motion mode")
    parser.add_argument("--video-model", default="omni_flash", help="Flow video model (default: omni_flash)")
    parser.add_argument("--colab-account", "--account", dest="colab_account", default=None, help="Target Colab account")
    parser.add_argument("--session", default=None, help="Colab session name")
    parser.add_argument("--flow-profiles", default=None, help="Comma-separated slice of Chrome profiles")
    parser.add_argument("--max-flow-workers", type=int, default=None, help="Max Flow Chrome workers (auto-scales 1-16 via GPU headless pool when omitted)")
    parser.add_argument("--force-audio", action="store_true", help="Force re-synthesis of Stage B audio")
    parser.add_argument("--inspect-dir", default=None, type=Path, help="Optional inspection directory")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode for mock execution")
    args = parser.parse_args()

    channel = args.channel
    if not channel:
        if ROOT_DIR.name.startswith("channel-"):
            channel = ROOT_DIR.name[len("channel-"):]
        else:
            parser.error("--channel is required when running outside a channel directory")

    produce_unified_flow_remotion_e2e(
        channel_arg=channel,
        job_id_arg=args.job,
        format_profile=args.format,
        motion_mode=args.motion_mode,
        video_model=args.video_model,
        colab_account=args.colab_account,
        session_name=args.session,
        flow_profiles_arg=args.flow_profiles,
        max_flow_workers=args.max_flow_workers,
        force_audio=args.force_audio,
        inspect_dir=args.inspect_dir,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
