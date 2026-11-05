#!/usr/bin/env python3
"""CLI tool for executing multi-account Flow Video daisy chains and scene pairs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SYS_DIR = _REPO_ROOT / "sys"
for _p in (str(_REPO_ROOT), str(_SYS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sys.flow_video import ChainMode, FlowVideoChainOrchestrator, VideoChainSpec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Flow Video daisy chain or scene pair synthesis with multi-account CDP orchestration."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--spec", type=str, help="Path to VideoChainSpec JSON file")
    input_group.add_argument(
        "--frames-dir", type=str, help="Path to directory containing sorted image frames"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default="smooth cinematic transition",
        help="Motion prompt for frames when using --frames-dir (default: 'smooth cinematic transition')",
    )
    parser.add_argument(
        "--mode",
        choices=["daisy_chain", "scene_pairs", "zero_credit_flipbook"],
        default="daisy_chain",
        help="Chain mode (default: daisy_chain; choices: daisy_chain, scene_pairs, zero_credit_flipbook)",
    )
    parser.add_argument(
        "--channel",
        type=str,
        default=None,
        help="Target channel ID (default: None for unassigned experimental mode)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path for final stitched MP4 output (default: video/flow_video/<job_id>_final.mp4)",
    )
    parser.add_argument(
        "--aspect",
        choices=["16:9", "9:16", "1:1"],
        default=None,
        help="Aspect ratio (default: 16:9)",
    )
    parser.add_argument(
        "--model",
        choices=["omni_flash", "abra", "veo_3_1_fast", "veo_3_1_quality", "veo_3_1_lite"],
        default="omni_flash",
        help="Video model on Google Flow (default: omni_flash; options: omni_flash, abra, veo_3_1_fast, veo_3_1_quality, veo_3_1_lite)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        choices=[4, 5, 6, 8, 10],
        default=6,
        help="Clip duration in seconds (Omni: 4s/6s/8s/10s; default: 6; used when --no-auto-duration is passed)",
    )
    parser.add_argument(
        "--auto-duration",
        dest="auto_duration",
        action="store_true",
        default=True,
        help="Automatically choose clip duration (4s/6s/8s/10s) and credits based on target duration (default: True)",
    )
    parser.add_argument(
        "--no-auto-duration",
        dest="auto_duration",
        action="store_false",
        help="Disable auto-duration selection and use fixed --duration for all clips",
    )
    parser.add_argument(
        "--auto-fallback-zero-credit",
        dest="auto_fallback_zero_credit",
        action="store_true",
        default=True,
        help="Automatically fallback to zero-credit flipbook if account pool has insufficient credits (default: True)",
    )
    parser.add_argument(
        "--no-auto-fallback-zero-credit",
        dest="auto_fallback_zero_credit",
        action="store_false",
        help="Disable automatic zero-credit fallback",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=6,
        help="Max parallel Chrome profiles / workers (default: 6)",
    )
    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="Optional path to external voiceover or narration audio WAV/MP3",
    )
    parser.add_argument(
        "--normalize-lufs",
        dest="normalize_lufs",
        action="store_true",
        default=True,
        help="Normalize audio to Video Pilot standard -11 LUFS / -1 dBTP (default: True)",
    )
    parser.add_argument(
        "--no-normalize-lufs",
        dest="normalize_lufs",
        action="store_false",
        help="Disable LUFS normalization on external audio",
    )
    parser.add_argument(
        "--keep-veo-audio",
        dest="keep_veo_audio",
        action="store_true",
        default=False,
        help="Keep Veo native generated audio tracks instead of muting video (default: False)",
    )
    parser.add_argument(
        "--veo-audio-weight",
        type=float,
        default=0.45,
        help="Volume weight for Veo native audio when mixed with external voiceover (default: 0.45)",
    )
    parser.add_argument(
        "--allow-talking",
        action="store_true",
        default=False,
        help="Disable automatic 'no talking, no lip movement' prompt guard",
    )
    parser.add_argument(
        "--resume",
        dest="resume",
        action="store_true",
        default=True,
        help="Resume from existing chain_manifest.json if available (default: True)",
    )
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="Force re-generation of all clips",
    )
    parser.add_argument(
        "--headless",
        dest="headless",
        action="store_true",
        default=True,
        help="Run Chrome in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Run Chrome with visible UI (for debugging)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simulate generation with synthetic clips to verify stitching and metadata without consuming credits",
    )
    parser.add_argument(
        "--work-dir",
        type=str,
        default=None,
        help="Custom working directory (default: sys/runs/flow_video_<job_id>)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "daisy_chain":
        mode_enum = ChainMode.DAISY_CHAIN
    elif args.mode == "scene_pairs":
        mode_enum = ChainMode.SCENE_PAIRS
    else:
        mode_enum = ChainMode.ZERO_CREDIT_FLIPBOOK

    if args.spec:
        spec_path = Path(args.spec)
        if not spec_path.is_file():
            print(f"Error: spec file not found: {args.spec}", file=sys.stderr)
            return 1
        spec = VideoChainSpec.from_json_file(spec_path)
    else:
        frames_dir = Path(args.frames_dir)
        if not frames_dir.is_dir():
            print(f"Error: frames directory not found: {args.frames_dir}", file=sys.stderr)
            return 1
        spec = VideoChainSpec.from_directory(
            dir_path=frames_dir,
            motion_prompt=args.prompt,
            mode=mode_enum,
            aspect=args.aspect or "16:9",
            video_model=args.model or ("zero_credit_flipbook" if mode_enum == ChainMode.ZERO_CREDIT_FLIPBOOK else "omni_flash"),
            duration_seconds=args.duration or 6,
            no_talking_prompt_guard=not args.allow_talking,
            audio_path=args.audio,
            auto_duration=args.auto_duration,
            auto_fallback_zero_credit=args.auto_fallback_zero_credit,
            channel_id=args.channel,
            keep_veo_audio=args.keep_veo_audio,
            veo_audio_mix_weight=args.veo_audio_weight,
        )

    if args.mode:
        spec.mode = mode_enum
    if args.aspect:
        spec.aspect = args.aspect
    if args.model:
        spec.video_model = args.model
    if mode_enum == ChainMode.ZERO_CREDIT_FLIPBOOK:
        spec.video_model = "zero_credit_flipbook"
    if args.audio:
        spec.audio_path = args.audio
    spec.auto_duration = args.auto_duration
    spec.auto_fallback_zero_credit = args.auto_fallback_zero_credit
    if args.channel:
        spec.channel_id = args.channel

    if args.output:
        resolved_output = Path(args.output)
    else:
        resolved_output = Path(f"video/flow_video/{spec.job_id}_final.mp4")

    work_dir = Path(args.work_dir) if args.work_dir else None

    orchestrator = FlowVideoChainOrchestrator(
        spec=spec,
        work_dir=work_dir,
        output_mp4_path=resolved_output,
        max_workers=args.max_workers,
        headless=args.headless,
        resume=args.resume,
        dry_run=args.dry_run,
    )

    try:
        report = orchestrator.run()
        print(f"\n[✓] Flow Video Chain finished successfully!")
        print(f"    Output MP4: {report.get('output_path')}")
        print(f"    Total clips: {len(report.get('clips', []))}")
        print(f"    Total credits: {report.get('total_credit_cost', 0)}")
        return 0
    except Exception as exc:
        print(f"\n[ERROR] Flow Video Chain failed: {exc}", file=sys.stderr)
        try:
            from sys.flow_cdp.multi_profile_manager import MultiProfileManager

            MultiProfileManager().stop_all_profiles()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
