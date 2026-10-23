"""Standalone Video Renderer Engine CLI Wrapper.

Executes Remotion Chromium renderer with strict I/O contract:
Inputs: <work_dir>/props.json and <work_dir>/public/
Outputs: <work_dir>/video.mp4, <work_dir>/subtitles.srt, <work_dir>/layout.json, scene stills, thumbnails
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RENDER_MJS = ROOT / "renderer" / "render.mjs"


def check_node_runtime() -> str:
    """Verifies that Node.js executable is available in PATH."""
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js runtime not found. Ensure 'node' is installed and in PATH.")
    return node


def verify_inputs(work_dir: Path) -> dict:
    """Validates that work_dir contains valid props.json and public directory."""
    if not work_dir.is_dir():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    props_path = work_dir / "props.json"
    if not props_path.is_file():
        raise FileNotFoundError(f"Missing props.json in {work_dir}")
    try:
        props = json.loads(props_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to parse {props_path}: {e}") from e
    return props


def collect_outputs(work_dir: Path, props: dict | None = None) -> dict[str, Path | list[Path]]:
    """Collects all expected generated output artifacts from work_dir."""
    outputs: dict[str, Path | list[Path]] = {}

    video_mp4 = work_dir / "video.mp4"
    if video_mp4.is_file():
        outputs["video"] = video_mp4

    for extra_video in ("video_9x16.mp4", "video_16x9.mp4", "video_youtube_16x9.mp4", "video_facebook_16x9.mp4"):
        vp = work_dir / extra_video
        if vp.is_file():
            outputs[extra_video.removesuffix(".mp4")] = vp

    srt = work_dir / "subtitles.srt"
    if srt.is_file():
        outputs["subtitles"] = srt

    layout = work_dir / "layout.json"
    if layout.is_file():
        outputs["layout"] = layout

    # Thumbnails
    thumb_16x9 = work_dir / "thumbnail_youtube_16x9.png"
    if thumb_16x9.is_file():
        outputs["thumbnail_youtube_16x9"] = thumb_16x9

    cover_9x16 = work_dir / "cover_tiktok_reels_9x16.png"
    if cover_9x16.is_file():
        outputs["cover_tiktok_reels_9x16"] = cover_9x16

    # Scene stills
    stills: list[Path] = []
    scenes = (props or {}).get("scenes", [])
    for scene in scenes:
        scene_id = scene.get("id")
        if scene_id:
            still = work_dir / f"{scene_id}.png"
            if still.is_file():
                stills.append(still)
    if stills:
        outputs["stills"] = stills

    return outputs


def render_standalone(
    work_dir: str | Path,
    timeout: float = 3600.0,
    check_outputs: bool = True,
    concurrency: int | None = None,
    env: dict | None = None,
) -> dict[str, Path | list[Path]]:
    """Renders video package in standalone multi-threaded mode.

    Args:
        work_dir: Path to directory containing props.json and public/
        timeout: Maximum execution seconds
        check_outputs: If True, validates video.mp4 and layout.json were produced
        concurrency: Optional explicit worker thread count (defaults to automatic multi-threading)
        env: Optional custom environment dictionary

    Returns:
        Dictionary of produced output file paths.
    """
    work_path = Path(work_dir).resolve()
    props = verify_inputs(work_path)
    node = check_node_runtime()

    if not RENDER_MJS.is_file():
        raise FileNotFoundError(f"Renderer entrypoint missing: {RENDER_MJS}")

    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    if concurrency is not None:
        if int(concurrency) <= 0:
            raise ValueError("concurrency must be a positive integer")
        run_env["VP_RENDER_CONCURRENCY"] = str(int(concurrency))

    cmd = [node, str(RENDER_MJS), str(work_path)]
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=run_env,
        timeout=timeout,
        capture_output=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"render.mjs failed with return code {result.returncode}")

    outputs = collect_outputs(work_path, props)
    if check_outputs:
        if "video" not in outputs:
            raise RuntimeError(f"Render completed but video.mp4 was not found in {work_path}")
        if "layout" not in outputs:
            raise RuntimeError(f"Render completed but layout.json was not found in {work_path}")

    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Video Pilot Standalone Video Renderer Engine CLI (Node/Remotion)")
    parser.add_argument(
        "work_dir",
        type=str,
        help="Path to package directory containing props.json and public/",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Explicit render thread concurrency (default: auto multi-threaded for Colab T4 GPU / CPU cores)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3600.0,
        help="Max execution seconds (default: 3600)",
    )
    parser.add_argument(
        "--no-check",
        dest="check_outputs",
        action="store_false",
        default=True,
        help="Do not check output existence after render",
    )

    args = parser.parse_args(argv)

    try:
        outputs = render_standalone(
            work_dir=args.work_dir,
            timeout=args.timeout,
            check_outputs=args.check_outputs,
            concurrency=args.concurrency,
        )
        print(f"Render successful: {len(outputs)} artifact types generated in {args.work_dir}")
        for key, val in outputs.items():
            if isinstance(val, list):
                print(f"  - {key}: {[str(p.name) for p in val]}")
            else:
                print(f"  - {key}: {val.name}")
        return 0
    except Exception as e:
        print(f"Error during render: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
