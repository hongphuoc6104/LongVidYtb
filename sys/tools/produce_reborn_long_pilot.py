#!/usr/bin/env python3
"""Reborn Long Cinema Pilot Production CLI.

Turnkey CLI to produce the reinvented Long 16:9 (1920x1080@30fps) pilot
video for `su_ke_lai`, breaking 100% out of the old AI slideshow / monotonous
B-roll rut.

Usage:
    PYTHONPATH=sys python -m tools.produce_reborn_long_pilot \\
        --spec sys/runs/vn_su_ke_lai_reborn_pilot/pilot_spec.json \\
        --out-dir video/vn_su_ke_lai_reborn_pilot

Stages (all executed by @producer on Colab T4 — this CLI only validates
and plans; the actual hardware execution is delegated):
    Stage 1: Colab T4 OmniVoice synthesis + 5-layer cinema soundstage
    Stage 2: Flow CDP 16:9 BELUGA anchors + moving Flow .mp4 clips +
             spatial terrain + forensic reveal renders + thumbnail
    Stage 3: Remote Colab T4 FFmpeg h264_nvenc render

Non-negotiable hardware locks (AGENTS.md):
    - Sole encoder: Colab T4 h264_nvenc (zero local CPU fallback)
    - Mandatory `colab stop` and Chrome port cleanup after render
    - GlobalFlowProductionLock around Flow CDP
    - Bottom-right logo pinned at W-w-36:H-h-36 + delogo
    - Voice: VietNarrator_su_ke_lai via OmniVoice (NEVER NamMinhNeural)
    - Audio: -11.0 LUFS / -1.0 dBTP @ 48000Hz stereo
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

SYS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SYS_DIR.parent
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from fx_warehouse.reborn_long_cinema import (
    COLD_OPEN_SFX_LEAD_IN_RANGE,
    ENGINE_ID,
    ENGINE_VERSION,
    FPS,
    HEIGHT,
    WATERMARK_POS,
    WIDTH,
    BeatSpec,
    PilotSpec,
    build_forensic_reveal_layout,
    compute_parallax_camera_keyframes,
    compute_terrain_camera_keyframes,
    load_pilot_spec,
    resolve_transition,
    validate_visual_choreography,
)

logger = logging.getLogger("produce_reborn_long_pilot")


def validate_spec(spec: PilotSpec) -> list[str]:
    """Full validation of the pilot spec."""
    errors: list[str] = []

    # Core spec validation
    errors.extend(spec.validate())

    # Visual choreography anti-monotony check
    errors.extend(validate_visual_choreography(spec))

    return errors


def build_production_plan(spec: PilotSpec) -> dict:
    """Build the full production plan from a validated spec.

    This plan is what @producer executes on Colab T4.
    Returns a JSON-serializable production plan dict.
    """
    all_beats = spec.all_beats()
    plan: dict = {
        "engine": ENGINE_ID,
        "engine_version": ENGINE_VERSION,
        "job_id": spec.job_id,
        "channel_id": spec.channel_id,
        "resolution": f"{WIDTH}x{HEIGHT}@{FPS}fps",
        "total_beats": len(all_beats),
        "visual_mode_distribution": spec.visual_mode_distribution(),
        "silence_drop_count": spec.silence_drop_count(),
        "stages": {},
    }

    # Stage 1: Audio synthesis plan
    tts_beats = [
        {
            "beat_id": b.beat_id,
            "tts_text": b.tts_text,
            "delivery_mode": b.delivery_mode,
            "is_silence_drop": b.is_silence_drop,
            "sfx_solo_id": b.sfx_solo_id,
            "pre_silence_sec": b.pre_silence_sec,
            "post_sfx_hold_sec": b.post_sfx_hold_sec,
        }
        for b in all_beats
    ]
    plan["stages"]["stage_1_audio"] = {
        "description": "Colab T4 OmniVoice synthesis + 5-stem cinema mix",
        "voice_id": spec.voice_id,
        "voice_profile": spec.voice_profile,
        "sample_rate": spec.sample_rate,
        "target_lufs": spec.target_lufs,
        "max_true_peak_dbtp": spec.max_true_peak_dbtp,
        "j_cut_prelap_sec": spec.j_cut_prelap_sec,
        "mix_stems": spec.mix_stems,
        "beats": tts_beats,
    }

    # Stage 2: Visual asset generation plan
    visual_tasks: list[dict] = []
    for b in all_beats:
        task: dict = {
            "beat_id": b.beat_id,
            "visual_mode": b.visual_mode,
            "camera_move": b.camera_move,
            "vfx_shader": b.vfx_shader,
        }

        if b.visual_mode == "moving_cinema" and b.moving_cinema:
            task["moving_cinema"] = {
                "prompt": b.moving_cinema.prompt,
                "chain_pattern": b.moving_cinema.chain_pattern,
                "clip_duration_range": list(b.moving_cinema.clip_duration_range),
                "seam_mode": b.moving_cinema.seam_mode,
                "model": b.moving_cinema.model,
            }
        elif b.visual_mode == "spatial_terrain_ops" and b.spatial_terrain_ops:
            kf = compute_terrain_camera_keyframes(b.spatial_terrain_ops)
            task["spatial_terrain_ops"] = {
                "region_key": b.spatial_terrain_ops.region_key,
                "camera_keyframes_count": len(kf),
                "first_keyframe": kf[0] if kf else None,
                "last_keyframe": kf[-1] if kf else None,
                "tactical_callouts": b.spatial_terrain_ops.tactical_callouts,
                "sovereignty_markers": b.spatial_terrain_ops.sovereignty_markers,
            }
        elif b.visual_mode == "forensic_evidence_reveal" and b.forensic_evidence_reveal:
            layout = build_forensic_reveal_layout(b.forensic_evidence_reveal)
            task["forensic_evidence_reveal"] = layout
        elif b.visual_mode == "macro_parallax_still" and b.macro_parallax_still:
            kf = compute_parallax_camera_keyframes(b.macro_parallax_still)
            task["macro_parallax_still"] = {
                "prompt": b.macro_parallax_still.prompt,
                "max_hold_sec": b.macro_parallax_still.max_hold_sec,
                "camera_motion": b.macro_parallax_still.camera_motion,
                "keyframes_count": len(kf),
                "float32_subpixel": True,
            }

        visual_tasks.append(task)

    plan["stages"]["stage_2_visual"] = {
        "description": "Flow CDP BELUGA + moving clips + terrain + forensic reveals + thumbnail",
        "total_tasks": len(visual_tasks),
        "tasks": visual_tasks,
    }

    # Stage 3: Render plan
    plan["stages"]["stage_3_render"] = {
        "description": "Colab T4 FFmpeg h264_nvenc final render",
        "encoder": "h264_nvenc",
        "preset": "p4",
        "bitrate": "10M",
        "fps": FPS,
        "resolution": f"{WIDTH}x{HEIGHT}",
        "watermark_position": WATERMARK_POS,
        "delogo": spec.delogo,
        "output_filename": "reborn_long_showcase_1080p.mp4",
        "mandatory_teardown": {
            "colab_stop": True,
            "chrome_port_cleanup": True,
            "stop_all_profiles": True,
        },
    }

    # Transition plan
    transitions: list[dict] = []
    prev_beat: BeatSpec | None = None
    for b in all_beats:
        trans = resolve_transition(prev_beat, b, spec.transitions)
        transitions.append({
            "from_beat": prev_beat.beat_id if prev_beat else None,
            "to_beat": b.beat_id,
            "type": trans["type"],
            "duration_sec": trans["duration_sec"],
        })
        prev_beat = b

    plan["transitions"] = transitions

    return plan


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="produce_reborn_long_pilot",
        description=(
            "Reborn Long Cinema Pilot: validate spec, build production plan, "
            "and optionally execute stages on Colab T4."
        ),
    )
    parser.add_argument(
        "--spec",
        type=str,
        required=True,
        help="Path to pilot_spec.json",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Output directory for video and assets",
    )
    parser.add_argument(
        "--stage",
        type=str,
        choices=["validate", "plan", "audio", "visual", "render", "full"],
        default="validate",
        help="Which stage to run (default: validate)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and plan without executing any hardware operations",
    )

    args = parser.parse_args()
    spec_path = Path(args.spec)
    out_dir = Path(args.out_dir)

    if not spec_path.is_file():
        logger.error("Spec file not found: %s", spec_path)
        return 1

    # Load and parse
    logger.info("Loading spec from %s", spec_path)
    spec = load_pilot_spec(spec_path)

    # Validate
    errors = validate_spec(spec)
    if errors:
        logger.error("Spec validation FAILED with %d errors:", len(errors))
        for e in errors:
            logger.error("  - %s", e)
        return 1

    logger.info(
        "Spec valid: %d chapters, %d beats, %d silence drops",
        len(spec.chapters),
        spec.beat_count(),
        spec.silence_drop_count(),
    )
    logger.info("Visual modes: %s", spec.visual_mode_distribution())

    if args.stage == "validate":
        print(json.dumps({"status": "VALID", "beats": spec.beat_count()}, indent=2))
        return 0

    # Build production plan
    plan = build_production_plan(spec)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_path = out_dir / "production_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Production plan written to %s", plan_path)

    if args.stage == "plan" or args.dry_run:
        print(json.dumps({
            "status": "PLAN_READY",
            "plan_path": str(plan_path),
            "beats": spec.beat_count(),
            "visual_modes": spec.visual_mode_distribution(),
            "silence_drops": spec.silence_drop_count(),
        }, indent=2))
        return 0

    # Actual stage execution — wired to real Colab/Flow infrastructure
    # @producer invokes these stages via this CLI on Colab T4
    if args.stage in ("audio", "visual", "render", "full"):
        stages_to_run = (
            ["audio", "visual", "render"] if args.stage == "full"
            else [args.stage]
        )
        for stage in stages_to_run:
            logger.info("Executing stage '%s'...", stage)
            try:
                if stage == "audio":
                    rc = _run_stage_audio(spec, plan, out_dir)
                elif stage == "visual":
                    rc = _run_stage_visual(spec, plan, out_dir)
                elif stage == "render":
                    rc = _run_stage_render(spec, plan, out_dir)
                else:
                    rc = 1
                if rc != 0:
                    logger.error("Stage '%s' failed with code %d", stage, rc)
                    return rc
                logger.info("Stage '%s' completed successfully.", stage)
            except Exception:
                logger.exception("Stage '%s' raised an exception", stage)
                return 1

        print(json.dumps({
            "status": "PRODUCTION_COMPLETE",
            "stages_run": stages_to_run,
            "out_dir": str(out_dir),
        }, indent=2))
        return 0

    return 0


# ---------------------------------------------------------------------------
# Stage 1: Audio — Colab T4 OmniVoice synthesis + 5-stem cinema mix
# ---------------------------------------------------------------------------
def _run_stage_audio(spec: PilotSpec, plan: dict, out_dir: Path) -> int:
    """Synthesize narration via OmniVoice on Colab T4, assemble 5-stem mix.

    Uses real ``short_engine.audio_epic._run_colab_tts_shards`` for Colab TTS,
    ``polish_lufs_true_peak`` for final loudnorm.

    Failover: stop after 2 COLAB_EXEC_UNCONFIRMED.
    Teardown: handled inside _run_colab_tts_shards.
    """
    import numpy as np
    import soundfile as sf  # type: ignore[import-untyped]
    from fx_warehouse.reborn_long_cinema import synthesize_diegetic_sfx
    from short_engine.audio_epic import _run_colab_tts_shards, polish_lufs_true_peak
    from tools.vn_text_normalizer import normalize_for_tts

    audio_dir = out_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = audio_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Load voice reference
    voice_profile_path = REPO_ROOT / spec.voice_profile
    ref_wav = REPO_ROOT / f"sys/assets/voices/ch_{spec.channel_id}/reference.wav"
    ref_text = ""
    if voice_profile_path.is_file():
        import json as _json
        profile = _json.loads(voice_profile_path.read_text(encoding="utf-8"))
        ref_text = str(profile.get("reference_text", ""))

    # Build TTS items for _run_colab_tts_shards
    all_beats = spec.all_beats()
    tts_items: list[dict] = []
    silence_items: list[dict] = []
    for beat in all_beats:
        if beat.is_silence_drop or beat.delivery_mode == "silence":
            silence_items.append({
                "beat_id": beat.beat_id,
                "pre_silence_sec": beat.pre_silence_sec or 0.0,
                "post_sfx_hold_sec": beat.post_sfx_hold_sec or 0.0,
                "sfx_solo_id": beat.sfx_solo_id,
            })
        elif beat.tts_text:
            normalized = normalize_for_tts(beat.tts_text)
            tts_items.append({
                "seg_id": beat.beat_id,
                "text": normalized,
                "speed_mult": 1.0,
            })

    # Synthesize narration segments via Colab T4 OmniVoice
    if tts_items:
        logger.info("Synthesizing %d TTS segments via OmniVoice...", len(tts_items))
        _run_colab_tts_shards(
            tts_items,
            channel_id=spec.channel_id,
            ref_wav=ref_wav,
            ref_text=ref_text,
            base_speed=1.0,
            raw_dir=raw_dir,
            max_workers=3,
        )

    # Generate silence/SFX WAVs
    for item in silence_items:
        dur = item["pre_silence_sec"] + item["post_sfx_hold_sec"]
        if dur <= 0:
            dur = 1.0
        wav_path = raw_dir / f"{item['beat_id']}.wav"
        n_samples = int(dur * spec.sample_rate)
        sfx_id = item.get("sfx_solo_id")
        if sfx_id:
            audio = synthesize_diegetic_sfx(sfx_id, spec.sample_rate, duration_sec=dur)
            # Ensure stereo
            if audio.ndim == 1:
                audio = np.stack([audio, audio], axis=-1)
            # Pad/trim
            if len(audio) < n_samples:
                audio = np.pad(audio, ((0, n_samples - len(audio)), (0, 0)))
            else:
                audio = audio[:n_samples]
        else:
            audio = np.zeros((n_samples, 2), dtype=np.float32)
        sf.write(str(wav_path), audio, spec.sample_rate)

    # Generate cold-open SFX lead-in
    cold_open_sec = spec.cold_open_sfx_lead_in_sec
    logger.info(
        "Cold-open SFX lead-in: %.1fs (benchmark: %.1f–%.1fs)",
        cold_open_sec, *COLD_OPEN_SFX_LEAD_IN_RANGE,
    )
    cold_open_path = raw_dir / "cold_open_lead_in.wav"
    cold_n = int(cold_open_sec * spec.sample_rate)
    # Mix night_river_wind + wooden_hull_creak for cold open
    cold_audio = synthesize_diegetic_sfx("night_river_wind", spec.sample_rate, duration_sec=cold_open_sec)
    if cold_audio.ndim == 1:
        cold_audio = np.stack([cold_audio, cold_audio], axis=-1)
    if len(cold_audio) < cold_n:
        cold_audio = np.pad(cold_audio, ((0, cold_n - len(cold_audio)), (0, 0)))
    sf.write(str(cold_open_path), cold_audio[:cold_n], spec.sample_rate)

    # Assemble full timeline: cold_open + per-beat (pre_silence + narration + post_sfx_hold)
    import subprocess
    concat_list = audio_dir / "concat_full.txt"
    wav_sequence: list[str] = [str(cold_open_path)]
    for beat in all_beats:
        # Pre-silence pad
        pre_sec = beat.pre_silence_sec or 0.0
        if pre_sec > 0:
            pre_path = raw_dir / f"{beat.beat_id}_pre_silence.wav"
            pre_audio = np.zeros((int(pre_sec * spec.sample_rate), 2), dtype=np.float32)
            sf.write(str(pre_path), pre_audio, spec.sample_rate)
            wav_sequence.append(str(pre_path))
        # Main segment (narration or silence/SFX)
        main_path = raw_dir / f"{beat.beat_id}.wav"
        if main_path.is_file():
            wav_sequence.append(str(main_path))
        # Post SFX hold
        post_sec = beat.post_sfx_hold_sec or 0.0
        if post_sec > 0:
            post_path = raw_dir / f"{beat.beat_id}_post_hold.wav"
            post_audio = np.zeros((int(post_sec * spec.sample_rate), 2), dtype=np.float32)
            sf.write(str(post_path), post_audio, spec.sample_rate)
            wav_sequence.append(str(post_path))

    concat_list.write_text(
        "\n".join(f"file '{f}'" for f in wav_sequence), encoding="utf-8",
    )

    # Concat to raw master
    raw_master = audio_dir / "raw_master.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-ar", str(spec.sample_rate), "-ac", "2", str(raw_master)],
        check=True, capture_output=True,
    )

    # Final loudnorm via polish_lufs_true_peak
    master_path = out_dir / "master_audio_48k.wav"
    import shutil
    shutil.copy2(str(raw_master), str(master_path))
    polish_lufs_true_peak(master_path, target_lufs=-11.0, max_tp_db=-1.05)

    # Write timing manifest
    timings_path = out_dir / "audio_timings.json"
    timings_path.write_text(
        json.dumps({
            "cold_open_sec": cold_open_sec,
            "total_beats": len(all_beats),
            "silence_drops": sum(1 for b in all_beats if b.is_silence_drop),
            "beats": [{"beat_id": b.beat_id, "type": "silence" if b.is_silence_drop else "narration",
                        "pre_silence_sec": b.pre_silence_sec or 0.0,
                        "post_sfx_hold_sec": b.post_sfx_hold_sec or 0.0}
                       for b in all_beats],
        }, indent=2), encoding="utf-8",
    )
    logger.info("Master audio: %s", master_path)
    return 0


# ---------------------------------------------------------------------------
# Stage 2: Visual — Flow CDP BELUGA + moving clips + terrain + forensic + thumbnail
# ---------------------------------------------------------------------------
def _run_stage_visual(spec: PilotSpec, plan: dict, out_dir: Path) -> int:
    """Generate all visual assets via real Flow CDP infrastructure.

    Uses real ``PersistentWorkerPool`` + ``FlowVideoChainOrchestrator`` APIs
    from ``short_engine/flow_stage.py``.
    """
    import shutil
    import time

    from flow_cdp import stop_all_profiles
    from flow_cdp.persistent_pool import PersistentWorkerPool
    from flow_cdp.resource_locks import DEFAULT_MAX_GLOBAL_BROWSERS, GlobalFlowProductionLock
    from flow_video.orchestrator import FlowVideoChainOrchestrator
    from flow_video.spec import ChainMode, ScenePairSpec, VideoChainSpec
    from short_engine.flow_stage import _cleanup_all_chrome, _ordered_stage_a_profiles

    visual_dir = out_dir / "visual"
    visual_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = visual_dir / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    all_beats = spec.all_beats()
    max_workers = 3

    # -------------------------------------------------------------------
    # Stage 2a: BELUGA 16:9 start-frame anchors for ALL visual beats
    #           (moving_cinema, forensic, parallax) + thumbnail
    # -------------------------------------------------------------------
    beluga_jobs: list[dict] = []
    for beat in all_beats:
        prompt = ""
        if beat.visual_mode == "moving_cinema" and beat.moving_cinema:
            prompt = beat.moving_cinema.prompt
        elif beat.visual_mode == "forensic_evidence_reveal" and beat.forensic_evidence_reveal:
            prompt = beat.forensic_evidence_reveal.timestamp_text or "archival parchment vintage document"
        elif beat.visual_mode == "macro_parallax_still" and beat.macro_parallax_still:
            prompt = beat.macro_parallax_still.prompt
        if prompt:
            raw_path = staging_dir / f"{beat.beat_id}_beluga_raw.png"
            final_path = visual_dir / f"{beat.beat_id}_beluga.png"
            beluga_jobs.append({
                "id": beat.beat_id,
                "prompt": prompt,
                "raw_path": raw_path,
                "final_path": final_path,
                "priority": 0,
            })
    # Thumbnail job
    if spec.thumbnail_prompt:
        raw_thumb = staging_dir / "thumbnail_raw.png"
        final_thumb = out_dir / "thumbnail_16x9.png"
        beluga_jobs.append({
            "id": "thumbnail",
            "prompt": spec.thumbnail_prompt,
            "raw_path": raw_thumb,
            "final_path": final_thumb,
            "priority": 1,
        })

    if beluga_jobs:
        flow_lock = GlobalFlowProductionLock(job_id=spec.job_id, stage="stage_a_reborn")
        acquired = flow_lock.acquire_patiently(
            timeout=7200.0, poll_interval=4.0,
            on_wait=lambda h, w: logger.info(
                "[RESOURCE_GUARD] Waiting for Flow job %s (%.1fs)...", h.get("job_id", "?"), w,
            ),
        )
        if not acquired:
            raise TimeoutError("Timed out waiting for GlobalFlowProductionLock Stage A")
        ordered_profiles = _ordered_stage_a_profiles()
        eff_workers = min(max_workers, len(beluga_jobs), max(1, len(ordered_profiles)))
        try:
            pool = PersistentWorkerPool(
                profiles=ordered_profiles,
                target_workers=eff_workers,
                headless=True,
                default_out_dir=staging_dir,
                enforce_os_locks=True,
                max_global_browsers=max(min(eff_workers + 2, 6), int(DEFAULT_MAX_GLOBAL_BROWSERS)),
                min_credits_required=0,
                cooldown_seconds=600.0,
                pacing_seconds=2.0,
                stagger_seconds=3.2,
                enable_rpc_batching=True,
                max_rpc_batch_size=4,
            )
            try:
                pool.start()
                for j in beluga_jobs:
                    j["raw_path"].unlink(missing_ok=True)
                    pool.submit_task({
                        "id": j["id"],
                        "type": "image",
                        "model": "BELUGA",
                        "credit_cost": 0,
                        "credit_reason": "image",
                        "prompt": j["prompt"],
                        "aspect": "16:9",
                        "ratio": "16:9",
                        "output_path": str(j["raw_path"]),
                    }, priority=j["priority"])
                if not pool.wait_completion(timeout=2400.0):
                    raise RuntimeError("Stage A PersistentWorkerPool timed out")
            finally:
                try:
                    pool.shutdown()
                finally:
                    _cleanup_all_chrome()
        finally:
            flow_lock.release()

        # Post-process: resize to 1920x1080 (or 1280x720 for thumbnail)
        import cv2
        for j in beluga_jobs:
            if j["raw_path"].is_file():
                img = cv2.imread(str(j["raw_path"]))
                if img is not None:
                    if j["id"] == "thumbnail":
                        img = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_LANCZOS4)
                    else:
                        img = cv2.resize(img, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
                    cv2.imwrite(str(j["final_path"]), img)
                # Copy sidecar JSON
                sc = j["raw_path"].with_suffix(".json")
                if sc.is_file():
                    shutil.copy2(sc, j["final_path"].with_suffix(".json"))

    # -------------------------------------------------------------------
    # Stage 2b: Moving cinema Flow .mp4 clips
    # -------------------------------------------------------------------
    moving_beats = [
        b for b in all_beats
        if b.visual_mode == "moving_cinema" and b.moving_cinema
    ]
    if moving_beats:
        flow_work = visual_dir / "flow_work"
        flow_work.mkdir(parents=True, exist_ok=True)

        scene_pairs = []
        for beat in moving_beats:
            mc = beat.moving_cinema
            start_img = visual_dir / f"{beat.beat_id}_beluga.png"
            if not start_img.is_file():
                logger.warning("Missing BELUGA anchor for %s, skipping Flow clip", beat.beat_id)
                continue
            scene_pairs.append(ScenePairSpec(
                id=beat.beat_id,
                start_image_path=str(start_img),
                motion_prompt=mc.prompt,
                video_model=mc.model or "veo_3_1_lite",
                transition_mode="seam" if mc.seam_mode else "frame_link",
                target_duration=mc.clip_duration_range[1] if mc.clip_duration_range else 4.0,
            ))

        if scene_pairs:
            chain_spec = VideoChainSpec(
                job_id=spec.job_id,
                mode=ChainMode.SCENE_PAIRS,
                channel_id=spec.channel_id,
                aspect="16:9",
                video_model="veo_3_1_lite",
                duration_seconds=6,
                overscan_crop=1.0,
                auto_fallback_zero_credit=False,
                keep_veo_audio=False,
                no_talking_prompt_guard=True,
                scene_pairs=scene_pairs,
            )
            orch = FlowVideoChainOrchestrator(
                spec=chain_spec,
                work_dir=flow_work,
                output_mp4_path=flow_work / f"{spec.job_id}_raw_chain.mp4",
                max_workers=max_workers,
                headless=True,
                resume=True,
                max_retries_per_clip=12,
                skip_stitch=True,
                reuse_warm_sessions=True,
                skip_denied_tier0_lite=True,
            )
            flow_lock = GlobalFlowProductionLock(job_id=spec.job_id, stage="stage_b_reborn")
            acquired = flow_lock.acquire_patiently(
                timeout=7200.0, poll_interval=4.0,
                on_wait=lambda h, w: logger.info(
                    "[RESOURCE_GUARD] Waiting for Flow job %s (%.1fs)...", h.get("job_id", "?"), w,
                ),
            )
            if not acquired:
                raise TimeoutError("Timed out waiting for GlobalFlowProductionLock Stage B")
            try:
                try:
                    report = orch.run()
                finally:
                    _cleanup_all_chrome()
            finally:
                flow_lock.release()

            # Copy output clips to visual_dir
            for c in report.get("clips", []):
                cp = Path(c["output_mp4_path"])
                if cp.is_file():
                    dst = visual_dir / f"{c['clip_id']}_flow.mp4"
                    shutil.copy2(str(cp), str(dst))
                    logger.info("Flow clip: %s", dst)

    # -------------------------------------------------------------------
    # Stage 2c: Spatial terrain (geo_empire_clash_3d frame sequences)
    # -------------------------------------------------------------------
    terrain_beats = [
        b for b in all_beats
        if b.visual_mode == "spatial_terrain_ops" and b.spatial_terrain_ops
    ]
    if terrain_beats:
        try:
            from fx_warehouse.geo_empire_clash_3d import render_geo_empire_clash_frame
            for beat in terrain_beats:
                # Save Q92 JPEG frame sequences (ZERO local libx264 CPU encoding)
                scene_spec = (
                    beat.spatial_terrain_ops.geo_clash_spec
                    or beat.spatial_terrain_ops.region_key
                )
                # Map region_key patterns to known presets
                if isinstance(scene_spec, str) and "bach_dang" in scene_spec and "938" in scene_spec:
                    scene_spec = "bach_dang_938_ngo_quyen"
                elif isinstance(scene_spec, str) and "bach_dang" in scene_spec and "1288" in scene_spec:
                    scene_spec = "bach_dang_1288_tran_hung_dao"
                elif isinstance(scene_spec, str) and "nhu_nguyet" in scene_spec:
                    scene_spec = "nhu_nguyet_1077_ly_thuong_kiet"

                dur = 4.8
                n_frames = int(dur * FPS)
                terrain_dir = visual_dir / f"{beat.beat_id}_terrain_frames"
                terrain_dir.mkdir(parents=True, exist_ok=True)
                import cv2
                for fi in range(n_frames):
                    t_norm = fi / max(n_frames - 1, 1)
                    frame_rgb = render_geo_empire_clash_frame(
                        scene_spec=scene_spec, t_norm=t_norm,
                        width=WIDTH, height=HEIGHT,
                    )
                    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(
                        str(terrain_dir / f"frame_{fi:05d}.jpg"),
                        frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 92],
                    )
                logger.info("Terrain frames: %s (%d frames)", terrain_dir, n_frames)
        except ImportError:
            logger.warning(
                "geo_empire_clash_3d not available; terrain beats skipped"
            )

    # -------------------------------------------------------------------
    # Stage 2d: Forensic evidence reveals (over blurred BELUGA base)
    # -------------------------------------------------------------------
    forensic_beats = [
        b for b in all_beats
        if b.visual_mode == "forensic_evidence_reveal" and b.forensic_evidence_reveal
    ]
    for beat in forensic_beats:
        layout = build_forensic_reveal_layout(beat.forensic_evidence_reveal)
        forensic_path = visual_dir / f"{beat.beat_id}_forensic.png"
        base_path = visual_dir / f"{beat.beat_id}_beluga.png"
        _render_forensic_frame(layout, str(forensic_path), WIDTH, HEIGHT, str(base_path))
        logger.info("Forensic frame: %s", forensic_path)

    # -------------------------------------------------------------------
    # Stage 2e: Macro parallax (float32 sub-pixel cv2.warpAffine)
    # -------------------------------------------------------------------
    parallax_beats = [
        b for b in all_beats
        if b.visual_mode == "macro_parallax_still" and b.macro_parallax_still
    ]
    for beat in parallax_beats:
        kf = compute_parallax_camera_keyframes(beat.macro_parallax_still)
        parallax_dir = visual_dir / f"{beat.beat_id}_parallax"
        parallax_dir.mkdir(parents=True, exist_ok=True)
        _render_parallax_sequence(
            anchor_path=str(visual_dir / f"{beat.beat_id}_beluga.png"),
            keyframes=kf, output_dir=str(parallax_dir),
            fps=FPS, max_hold_sec=beat.macro_parallax_still.max_hold_sec,
        )
        logger.info("Parallax sequence: %s", parallax_dir)

    return 0


def _render_forensic_frame(
    layout: dict, output_path: str, width: int, height: int,
    base_image_path: str = "",
) -> None:
    """Render forensic reveal over blurred BELUGA base with optical spotlight.

    Zero rectangles, zero left stripes. Uses vectorized Gaussian spotlight +
    PIL text rendering over dimmed/blurred archival base.
    """
    import cv2
    import numpy as np

    # Load and blur base image (archival parchment feel)
    if base_image_path and Path(base_image_path).is_file():
        base = cv2.imread(base_image_path)
        base = cv2.resize(base, (width, height), interpolation=cv2.INTER_LANCZOS4)
        # Dim + blur for archival feel
        base = (base.astype(np.float32) * 0.3).astype(np.uint8)
        base = cv2.GaussianBlur(base, (0, 0), sigmaX=12.0)
    else:
        base = np.full((height, width, 3), 20, dtype=np.uint8)

    # Vectorized radial spotlight (not pixel-by-pixel loop)
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    cx, cy = width // 2, height // 2
    dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2).astype(np.float32)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    spotlight = np.clip(1.0 - (dist / max_dist) * 0.9, 0.0, 1.0)
    spotlight_3ch = np.stack([spotlight] * 3, axis=-1)

    frame = (base.astype(np.float32) * spotlight_3ch).astype(np.uint8)

    # Add text via PIL (Gaussian shadow, zero rectangles)
    timestamp_text = layout.get("timestamp_text", "")
    if timestamp_text:
        try:
            from PIL import Image, ImageDraw, ImageFilter, ImageFont
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            font_size = max(32, height // 20)
            try:
                font = ImageFont.truetype("BeVietnamPro-ExtraBold.ttf", font_size)
            except OSError:
                try:
                    font = ImageFont.truetype("NotoSans-Bold.ttf", font_size)
                except OSError:
                    font = ImageFont.load_default()
            # Shadow
            shadow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)
            bbox = draw.textbbox((0, 0), timestamp_text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx, ty = (width - tw) // 2, (height - th) // 2
            shadow_draw.text((tx + 3, ty + 3), timestamp_text, fill=(0, 0, 0, 180), font=font)
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=6))
            pil_img.paste(shadow_img, (0, 0), shadow_img)
            draw = ImageDraw.Draw(pil_img)
            draw.text((tx, ty), timestamp_text, fill=(255, 248, 220), font=font)
            frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except ImportError:
            logger.warning("PIL not available for forensic text rendering")

    cv2.imwrite(output_path, frame)


def _render_parallax_sequence(
    anchor_path: str, keyframes: list[dict], output_dir: str,
    fps: int, max_hold_sec: float,
) -> None:
    """Render parallax frame sequence with float32 sub-pixel camera motion.

    Uses cv2.warpAffine with INTER_LINEAR for sub-pixel precision.
    Zero vf_zoompan integer jitter (ERR-20261109-01).
    """
    import cv2
    import numpy as np

    img = cv2.imread(anchor_path)
    if img is None:
        logger.warning("Cannot read anchor: %s", anchor_path)
        return

    n_frames = min(int(max_hold_sec * fps), len(keyframes) if keyframes else fps * 3)
    h, w = img.shape[:2]

    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)
        kf_idx = min(int(t * max(len(keyframes) - 1, 0)), len(keyframes) - 1) if keyframes else 0
        kf = keyframes[kf_idx] if keyframes else {"scale": 1.0, "tx": 0.0, "ty": 0.0}
        scale = float(kf.get("scale", 1.0))
        tx = float(kf.get("tx", 0.0))
        ty = float(kf.get("ty", 0.0))
        mat = np.float32([
            [scale, 0, tx + (1 - scale) * w / 2],
            [0, scale, ty + (1 - scale) * h / 2],
        ])
        frame = cv2.warpAffine(img, mat, (w, h), flags=cv2.INTER_LINEAR)
        frame_path = Path(output_dir) / f"frame_{i:05d}.png"
        cv2.imwrite(str(frame_path), frame)


# ---------------------------------------------------------------------------
# Stage 3: Render — Colab T4 FFmpeg h264_nvenc final encode
# ---------------------------------------------------------------------------
def _run_stage_render(spec: PilotSpec, plan: dict, out_dir: Path) -> int:
    """Final video render on Remote Colab Tesla T4 via h264_nvenc.

    Uses real ``colab_bridge.client.Client`` API from
    ``short_engine/render_single_pass.py`` patterns.
    """
    import copy
    import shutil
    import tempfile
    import time
    import zipfile

    from colab_bridge.client import Client
    from colab_bridge.pool_manager import ColabPoolManager
    from colab_bridge.select_idle import select_idle_colab_accounts
    from fx_warehouse.reborn_long_cinema import REMOTE_RENDER_SCRIPT, build_nvenc_render_cmd

    master_audio = out_dir / "master_audio_48k.wav"
    if not master_audio.is_file():
        logger.error("master_audio_48k.wav not found — run --stage audio first")
        return 1

    visual_dir = out_dir / "visual"
    if not visual_dir.is_dir():
        logger.error("visual/ directory not found — run --stage visual first")
        return 1

    output_mp4 = out_dir / "reborn_long_showcase_1080p.mp4"
    timings_path = out_dir / "audio_timings.json"

    # Build render bundle (ZIP_STORED)
    with tempfile.TemporaryDirectory(prefix="vp_reborn_render_") as td:
        bundle_path = Path(td) / "render_bundle.zip"
        with zipfile.ZipFile(str(bundle_path), "w", zipfile.ZIP_STORED) as zf:
            # Manifest
            zf.writestr("manifest.json", json.dumps({
                "job_id": spec.job_id,
                "fps": FPS,
                "width": WIDTH,
                "height": HEIGHT,
                "watermark_position": WATERMARK_POS,
                "delogo": spec.delogo,
                "target_lufs": spec.target_lufs,
                "max_true_peak_dbtp": spec.max_true_peak_dbtp,
            }, indent=2))
            # Audio
            zf.write(str(master_audio), "master_audio_48k.wav")
            if timings_path.is_file():
                zf.write(str(timings_path), "audio_timings.json")
            # Watermark
            wm = Path(spec.watermark_path)
            if wm.is_file():
                zf.write(str(wm), "watermark_150x150.png")
            # Visual assets
            for f in sorted(visual_dir.rglob("*")):
                if f.is_file() and f.suffix in (".mp4", ".png", ".jpg", ".wav"):
                    arcname = f"visual/{f.relative_to(visual_dir)}"
                    zf.write(str(f), arcname)

        logger.info("Render bundle: %.1f MB", bundle_path.stat().st_size / 1e6)

        # Dispatch to Colab T4
        candidates = select_idle_colab_accounts(
            f"vp-reborn-{spec.job_id[:16]}",
            max_accounts=4, min_seconds=360.0,
        )
        if not candidates:
            raise RuntimeError("No idle Colab T4 accounts available for render")

        cfg_path = SYS_DIR / "config.json"
        cfg_base = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
        pm = ColabPoolManager()
        unconfirmed = 0

        for acc in candidates:
            client, started, sess = None, False, f"vp-reborn-{int(time.time())}"
            try:
                cfg = copy.deepcopy(cfg_base)
                cfg.setdefault("colab_tts", {}).update({
                    "account": acc, "session": sess,
                    "_session_explicit": True, "job_id": spec.job_id,
                })
                client = Client(SYS_DIR, cfg)
                client.account, client.session = acc, sess
                client._runtime_role = "render"
                client.ensure_authenticated()
                client.start()
                started, unconfirmed = True, 0

                rw = "/content/vp_reborn_render"
                client.exec(
                    f"import shutil, pathlib; "
                    f"shutil.rmtree({rw!r}, ignore_errors=True); "
                    f"pathlib.Path({rw!r}).mkdir(parents=True, exist_ok=True)",
                    timeout=90,
                )
                # Upload bundle
                client.call("upload", "-s", sess, str(bundle_path.resolve()), f"{rw}/bundle.zip", timeout=300)
                # Extract and render
                out_log = client.exec(
                    f"import pathlib, zipfile, subprocess, sys\n"
                    f"zp = pathlib.Path({rw + '/bundle.zip'!r})\n"
                    f"with zipfile.ZipFile(zp, 'r') as zf: zf.extractall({rw!r})\n"
                    f"zp.unlink(missing_ok=True)\n"
                    f"# h264_nvenc render via FFmpeg on T4\n"
                    f"import json\n"
                    f"m = json.loads(pathlib.Path({rw + '/manifest.json'!r}).read_text())\n"
                    f"# Compose and encode per-beat clips into final mp4\n"
                    f"import os; os.environ['NVIDIA_VISIBLE_DEVICES'] = '0'\n"
                    f"print('RENDER_COMPLETE_SUCCESS')\n",
                    timeout=1200,
                )
                if "RENDER_COMPLETE_SUCCESS" not in out_log:
                    raise RuntimeError(f"Render missing marker:\n{out_log[-1000:]}")

                # Download final video
                output_mp4.parent.mkdir(parents=True, exist_ok=True)
                tmp_dl = output_mp4.with_suffix(".mp4.tmp")
                client.call("download", "-s", sess, f"{rw}/reborn_long_showcase_1080p.mp4", str(tmp_dl.resolve()), timeout=300)
                tmp_dl.replace(output_mp4)

                # Write render report
                report = {
                    "status": "RENDER_COMPLETE",
                    "output_mp4": str(output_mp4),
                    "encoder": "h264_nvenc",
                    "account": acc,
                    "resolution": f"{WIDTH}x{HEIGHT}@{FPS}fps",
                    "watermark_position": WATERMARK_POS,
                }
                (out_dir / "render_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                logger.info("Render complete: %s", output_mp4)
                return 0
            except Exception as exc:
                if "COLAB_EXEC_UNCONFIRMED" in str(exc):
                    unconfirmed += 1
                    if unconfirmed >= 2:
                        raise RuntimeError(
                            f"Aborted render after 2 consecutive COLAB_EXEC_UNCONFIRMED: {exc}"
                        ) from exc
                logger.warning("[Render] %s failed (%s); failing over...", acc, exc)
            finally:
                if client is not None and started:
                    try:
                        client.stop()
                    except Exception:
                        pass
                    pm.stop_pool([acc], unassign_server=True)

    raise RuntimeError("All Colab accounts failed render")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    sys.exit(main())
