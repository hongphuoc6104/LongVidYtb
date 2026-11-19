#!/usr/bin/env python3
"""Turbo Serialized Short Production Engine (`<= 15 min/video` Single-Pass V3 architecture).

Modular engine facade backed by `sys/short_engine/`:
- `hybrid_2k` vs `full_video` beat routing (`asset_mode_override` + `frame_link` protection)
- Parallel Colab T4 OmniVoice Audio (5-Act `heroic_vietnam_epic` score + `132px` kinetic ASS)
  running concurrently with local Flow Stage A BELUGA images (`_clean_beluga_sparkle_adaptive`)
- Selective Flow Stage B video (`skip_denied_tier0_lite=True`)
- Single-Pass 4-GPU Colab T4 final render (`--render-mode single_pass`, `>= 132px` max-4-word
  heroic banners, chunk-local ASS slicing, `-bf 0 -g 30 -b:v 10M -preset p4`) + `<2s` lossless concat.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SYS_DIR = ROOT_DIR / "sys"
if not hasattr(sys, "__path__"):
    sys.__path__ = [str(SYS_DIR)]
if str(SYS_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_DIR))

from short_engine import select_idle_colab_accounts  # noqa: E402
from short_engine.audio_epic import (  # noqa: E402
    run_audio_stage,
    slice_ass_for_window,
    synthesize_heroic_epic_score,
)
from short_engine.flow_stage import (  # noqa: E402
    VALID_VISUAL_MODES,
    classify_hybrid_beats,
    resolve_worker_count,
    run_flow_stage_a,
    run_flow_stage_b,
)
from short_engine.render_single_pass import (  # noqa: E402
    VALID_NVENC_PRESETS,
    VALID_RENDER_MODES,
    build_hud_stamps,
    build_kenburns_filter,
    plan_chunked_render_timeline,
    render_heroic_banner_png,
    run_render_stage,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

__all__ = [
    "build_hud_stamps",
    "build_kenburns_filter",
    "classify_hybrid_beats",
    "main",
    "plan_chunked_render_timeline",
    "render_heroic_banner_png",
    "resolve_worker_count",
    "select_idle_colab_accounts",
    "slice_ass_for_window",
    "synthesize_heroic_epic_score",
]


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="High-speed Single-Pass Turbo Serialized Short Production Engine.")
    parser.add_argument("--spec", required=True, help="Path to short_spec.json")
    parser.add_argument("--stage", choices=["all", "audio", "flow", "render"], default="all")
    parser.add_argument("--visual-mode", choices=list(VALID_VISUAL_MODES), default="hybrid_2k")
    parser.add_argument("--render-mode", choices=list(VALID_RENDER_MODES), default="single_pass")
    parser.add_argument("--img-workers", default="auto", help="Stage A BELUGA Chrome workers (`auto` or int)")
    parser.add_argument("--vid-workers", default="auto", help="Stage B Flow video Chrome workers (`auto` or int)")
    parser.add_argument("--colab-tts-workers", type=int, default=3)
    parser.add_argument("--colab-render-workers", type=int, default=4)
    parser.add_argument("--nvenc-preset", choices=list(VALID_NVENC_PRESETS), default="p4")
    parser.add_argument("--delogo", choices=["on", "off"], default="on")
    parser.add_argument("--prep-only", action="store_true", help="Validate banners, beat routing & chunk math without Colab/Chrome.")
    parser.add_argument("--out-mp4", default=None, help="Optional destination MP4 path (writes benchmark_timings.json beside it).")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    spec_path = Path(args.spec).expanduser().resolve()
    spec_dir = spec_path.parent
    short_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    job_id = str(short_spec.get("job_id") or spec_dir.name)

    default_mp4 = (spec_dir / "final_short_2k.mp4").resolve()
    out_mp4 = Path(args.out_mp4).expanduser().resolve() if args.out_mp4 else default_mp4
    out_overridden = args.out_mp4 is not None and out_mp4 != default_mp4
    if out_overridden:
        work_root = out_mp4.parent / f"{job_id}_work"
    elif args.prep_only:
        work_root = SYS_DIR / "scratch" / f"{job_id}_prep_work"
    else:
        work_root = spec_dir / "_work_short"

    t_all = time.monotonic()
    results: dict[str, Any] = {
        "job_id": job_id,
        "stage": args.stage,
        "visual_mode": args.visual_mode,
        "render_mode": args.render_mode,
        "prep_only": bool(args.prep_only),
    }

    if args.prep_only:
        results["render"] = run_render_stage(
            short_spec,
            spec_dir,
            work_root,
            visual_mode=args.visual_mode,
            render_mode=args.render_mode,
            colab_render_workers=args.colab_render_workers,
            nvenc_preset=args.nvenc_preset,
            delogo=args.delogo,
            prep_only=True,
            out_mp4=out_mp4,
            out_overridden=out_overridden,
        )
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    img_workers = resolve_worker_count(args.img_workers)
    vid_workers = resolve_worker_count(args.vid_workers)
    stage_timings: dict[str, Any] = {}

    if args.stage == "all":
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            f_audio = pool.submit(run_audio_stage, short_spec, spec_dir, work_root, colab_tts_workers=args.colab_tts_workers)
            f_stage_a = pool.submit(run_flow_stage_a, short_spec, spec_dir, work_root, max_workers=img_workers)
            results["audio"] = f_audio.result()
            results["flow_stage_a"] = f_stage_a.result()
        stage_timings["audio_sec"] = results["audio"]["elapsed_sec"]
        stage_timings["flow_stage_a_sec"] = results["flow_stage_a"]["elapsed_sec"]

        results["flow_stage_b"] = run_flow_stage_b(short_spec, spec_dir, work_root, visual_mode=args.visual_mode, max_workers=vid_workers)
        stage_timings["flow_stage_b_sec"] = results["flow_stage_b"]["elapsed_sec"]

        results["render"] = run_render_stage(
            short_spec,
            spec_dir,
            work_root,
            visual_mode=args.visual_mode,
            render_mode=args.render_mode,
            colab_render_workers=args.colab_render_workers,
            nvenc_preset=args.nvenc_preset,
            delogo=args.delogo,
            prep_only=False,
            out_mp4=out_mp4,
            out_overridden=out_overridden,
            stage_timings=stage_timings,
        )
    elif args.stage == "audio":
        results["audio"] = run_audio_stage(short_spec, spec_dir, work_root, colab_tts_workers=args.colab_tts_workers)
    elif args.stage == "flow":
        results["flow_stage_a"] = run_flow_stage_a(short_spec, spec_dir, work_root, max_workers=img_workers)
        results["flow_stage_b"] = run_flow_stage_b(short_spec, spec_dir, work_root, visual_mode=args.visual_mode, max_workers=vid_workers)
    elif args.stage == "render":
        results["render"] = run_render_stage(
            short_spec,
            spec_dir,
            work_root,
            visual_mode=args.visual_mode,
            render_mode=args.render_mode,
            colab_render_workers=args.colab_render_workers,
            nvenc_preset=args.nvenc_preset,
            delogo=args.delogo,
            prep_only=False,
            out_mp4=out_mp4,
            out_overridden=out_overridden,
        )

    results["wall_elapsed_sec"] = round(time.monotonic() - t_all, 2)
    bench_json = out_mp4.parent / "benchmark_timings.json"
    if bench_json.is_file() and args.stage in ("all", "render"):
        bdata = json.loads(bench_json.read_text(encoding="utf-8"))
        bdata["wall_elapsed_sec"] = results["wall_elapsed_sec"]
        bench_json.write_text(json.dumps(bdata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
