#!/usr/bin/env python3
"""Video Pilot — Universal E2E Short Production Runner for Channels (Wave 4 & V2).

Executes full end-to-end production for Short-Video (short_9x16):
- Stage A: Flow CDP Full-Frame Images + Native Thumbnail (revisions/images/1/)
- Stage B: Wave 4 Studio-Clean Fast Audio TTS with endcard silence padding (revisions/audio/1/)
- Stage C: Remote Colab T4 Headless Remotion Render (revisions/render/1/ -> video/<job_id>/)
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional

SYS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = SYS_DIR.parent
for _p in (str(SYS_DIR), str(SYS_DIR / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from colab_bridge.client import Client  # noqa: E402
from flow_cdp.resource_locks import JobExecutionLock  # noqa: E402
from tools.build_publish_kit import build_publish_kit  # noqa: E402
from tools.channel_production_common import (  # noqa: E402
    get_channel_slice,
    resolve_channel_ids,
    stage_a_images,
    stage_b_audio,
    stage_c_flow_video,
    stage_c_render,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("produce_channel_short_e2e")


def produce_channel_short(
    channel_arg: str,
    job_id_arg: Optional[str] = None,
    colab_account: Optional[str] = None,
    flow_profiles_arg: Optional[str] = None,
    force_audio: bool = False,
    session_name: Optional[str] = None,
    inspect_dir: Optional[Path] = None,
    use_flow_video: bool = False,
    video_model: str = "omni_flash",
    chain_mode: str = "daisy_chain",
) -> Dict[str, Any]:
    channel_id, channel_slug = resolve_channel_ids(channel_arg)
    job_id = job_id_arg or f"{channel_slug}-week1-9x16"

    job_lock = JobExecutionLock(job_id)
    if not job_lock.try_acquire():
        raise RuntimeError(f"Job '{job_id}' is already running in another process")

    last_active_client: Optional[Client] = None
    last_active_account: Optional[str] = None
    target_session: Optional[str] = None

    try:
        # Resolve job_dir and appropriate sys_dir
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
            raise FileNotFoundError(f"Could not locate job directory for job '{job_id}' (searched: {candidate_job_dirs})")

        active_sys_dir = job_dir.parents[1] if (job_dir.parents[1] / "config.json").is_file() else SYS_DIR
        active_root_dir = active_sys_dir.parent

        # Resource partition defaults from contract §1
        part_flow, part_colab, default_session = get_channel_slice(channel_id)
        target_account = colab_account or part_colab[0]
        target_session = session_name or default_session

        logger.info("=" * 72)
        logger.info(f"  STARTING E2E SHORT PRODUCTION: {job_id}")
        logger.info(f"  Channel: {channel_id} (slug: {channel_slug})")
        logger.info(f"  Job Dir: {job_dir}")
        logger.info(f"  Sys Dir: {active_sys_dir}")
        logger.info(f"  Colab Session: {target_session} (preferred account: {target_account})")
        logger.info("=" * 72)

        brief = json.loads((job_dir / "brief.json").read_text(encoding="utf-8"))
        content = json.loads((job_dir / "content.json").read_text(encoding="utf-8"))

        # Parallel Execution: Stage A (Local Flow Images) || Stage B (Remote Colab T4 Audio)
        logger.info("[*] Launching Stage A (Flow Images) and Stage B (Colab Audio) in parallel...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            fut_images = executor.submit(
                stage_a_images,
                sys_dir=active_sys_dir,
                job_dir=job_dir,
                channel_id=channel_id,
                brief=brief,
                content=content,
                format_profile="short_9x16",
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
                format_profile="short_9x16",
                colab_account=target_account,
                session_name=target_session,
                force_audio=force_audio,
            )

        # Both futures joined. Capture active client first for strict teardown safety.
        if fut_audio.exception() is None:
            audio_payload, audio_client, audio_account = fut_audio.result()
            if audio_client:
                last_active_client = audio_client
            if audio_account:
                last_active_account = audio_account
        else:
            fut_audio.result()

        images_output = fut_images.result()

        # Stage C: Render via Flow Video Start->End Frames or Remote Colab Remotion
        enable_flow_video = bool(use_flow_video or brief.get("video_engine") == "flow_video")
        if enable_flow_video:
            final_mp4, render_client, render_account, render_report = stage_c_flow_video(
                sys_dir=active_sys_dir,
                job_dir=job_dir,
                root_dir=active_root_dir,
                brief=brief,
                content=content,
                images_payload=images_output,
                audio_payload=audio_payload,
                format_profile="short_9x16",
                video_model=video_model,
                chain_mode=chain_mode,
                inspect_dir=inspect_dir,
            )
        else:
            final_mp4, render_client, render_account, render_report = stage_c_render(
                sys_dir=active_sys_dir,
                job_dir=job_dir,
                root_dir=active_root_dir,
                brief=brief,
                content=content,
                images_payload=images_output,
                audio_payload=audio_payload,
                format_profile="short_9x16",
                colab_account=colab_account or (audio_account if audio_account in part_colab else part_colab[0]),
                session_name=target_session,
                inspect_dir=inspect_dir,
            )
        if render_client:
            last_active_client = render_client
        if render_account:
            last_active_account = render_account

        # Generate Vietnamese publication kit (youtube_shorts.md)
        try:
            logger.info(f"Generating Vietnamese publication kit for {channel_id} / {job_id}...")
            build_publish_kit(channel_id=channel_id, job_id=job_id, root_dir=active_root_dir)
            logger.info("  [✓] Publication kit generated successfully.")
        except Exception as ex_pub:
            logger.warning(f"Could not generate publication kit: {ex_pub}")

        # Ensure deliverables exist in both vp-agent-core and vp-channels/channel-<slug>
        source_video_dir = active_root_dir / "video" / job_id
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

        summary = {
            "status": "SUCCESS",
            "job_id": job_id,
            "channel": channel_id,
            "format": "short_9x16",
            "deliverables": {
                "mp4": str(final_mp4),
                "srt": str(active_root_dir / "video" / job_id / f"{job_id}.srt"),
                "thumbnail": str(active_root_dir / "video" / job_id / "thumbnail_9x16.jpg"),
            },
            "render": render_report,
            "audio": {
                "duration": audio_payload["duration"],
                "measured_lufs": audio_payload.get("measured_lufs"),
                "measured_peak_dbtp": audio_payload.get("measured_peak_dbtp"),
                "account_used": audio_account,
            },
            "images": {
                "count": len(images_output.get("items", [])),
            },
        }

        print("\n" + "=" * 72)
        print("  E2E SHORT PRODUCTION COMPLETE:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        print("=" * 72 + "\n")
        return summary

    finally:
        # Strict teardown: stop session so zero idle T4 GPUs leak!
        if last_active_client and last_active_account and target_session:
            try:
                logger.info(f"Stopping Colab session '{target_session}' on {last_active_account}...")
                last_active_client.stop()
                logger.info(f"Cleanly released Colab session on {last_active_account}.")
            except Exception as ex_stop:
                logger.warning(f"Failed stopping Colab session on {last_active_account}: {ex_stop}")
        job_lock.release()


def main():
    parser = argparse.ArgumentParser(description="Video Pilot — Universal E2E Short Production Runner")
    parser.add_argument("--channel", required=False, help="Channel identifier or slug (e.g. nao_luoi, tui_tien)")
    parser.add_argument("--job", "--job-id", dest="job", required=False, help="Job identifier (defaults to <channel_slug>-week1-9x16 or v2 dir)")
    parser.add_argument("--colab-account", "--account", dest="colab_account", default=None, help="Target Colab account (with automatic slice failover)")
    parser.add_argument("--flow-profiles", default=None, help="Comma-separated slice of Chrome profiles (e.g. profile_1,profile_2)")
    parser.add_argument("--force-audio", action="store_true", help="Force re-synthesis of Stage B audio + Stage C render")
    parser.add_argument("--session", default=None, help="Colab session name")
    parser.add_argument("--inspect-dir", default=None, type=Path, help="Optional directory to copy deliverables for review")
    parser.add_argument("--use-flow-video", action="store_true", help="Render Stage C via Flow Video Start->End Frames chain (Omni 1.1 Flash)")
    parser.add_argument("--video-engine", choices=["remotion", "flow_video"], default="remotion", help="Video rendering engine (remotion or flow_video)")
    parser.add_argument("--video-model", default="omni_flash", help="Flow video model when --use-flow-video is enabled (default: omni_flash)")
    parser.add_argument("--chain-mode", default="daisy_chain", choices=["daisy_chain", "scene_pairs", "zero_credit_flipbook"], help="Flow video chain mode")
    args = parser.parse_args()

    channel = args.channel
    if not channel:
        if ROOT_DIR.name.startswith("channel-"):
            channel = ROOT_DIR.name[len("channel-"):]
        else:
            parser.error("--channel is required when running outside a channel directory")

    produce_channel_short(
        channel_arg=channel,
        job_id_arg=args.job,
        colab_account=args.colab_account,
        flow_profiles_arg=args.flow_profiles,
        force_audio=args.force_audio,
        session_name=args.session,
        inspect_dir=args.inspect_dir,
        use_flow_video=bool(args.use_flow_video or args.video_engine == "flow_video"),
        video_model=args.video_model,
        chain_mode=args.chain_mode,
    )


if __name__ == "__main__":
    main()
