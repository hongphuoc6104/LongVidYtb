#!/usr/bin/env python3
"""
Tool to overlay the official stickman brand logo over the video watermark.
Automatically calculates position and dimensions based on resolution,
ensuring 100% coverage without obstructing video content.
"""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOGO = ROOT / "renderer/brand_logo.png"


def get_video_dimensions(video_path: Path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        str(video_path)
    ]
    res = subprocess.check_output(cmd, text=True).strip().split("x")
    return int(res[0]), int(res[1])


def apply_logo(video_path: Path, output_path: Path, logo_path: Path = DEFAULT_LOGO):
    if not video_path.exists():
        raise FileNotFoundError(f"Input video not found: {video_path}")
    if not logo_path.exists():
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    w, h = get_video_dimensions(video_path)
    is_horizontal = w >= h

    if is_horizontal:
        logo_size = round(w * (108 / 1920))
        pad_x = round(w * (23 / 1920))
        pad_y = round(h * (38 / 1080))
    else:
        logo_size = round(w * (100 / 1080))
        pad_x = round(w * (24 / 1080))
        pad_y = round(h * (50 / 1920))

    overlay_expr = f"W-w-{pad_x}:H-h-{pad_y}"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output_path.with_name(f"_tmp_{output_path.name}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(logo_path),
        "-filter_complex",
        f"[1:v]scale={logo_size}:{logo_size}[logo];[0:v][logo]overlay={overlay_expr}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(temp_output)
    ]

    print(f"[Brand Logo] Applying logo ({logo_size}x{logo_size}) at {overlay_expr} on {w}x{h} video...")
    subprocess.run(cmd, check=True)
    temp_output.replace(output_path)
    print(f"[Brand Logo] Successfully saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Apply stickman brand logo over watermark in video.")
    parser.add_argument("video", type=Path, help="Input video path")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output video path (default: <name>_branded.mp4)")
    parser.add_argument("--logo", type=Path, default=DEFAULT_LOGO, help="Logo image path")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the original video")
    args = parser.parse_args()

    out = args.video if args.in_place else (args.output or args.video.with_name(f"{args.video.stem}_branded.mp4"))
    apply_logo(args.video, out, args.logo)


if __name__ == "__main__":
    main()
