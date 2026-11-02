#!/usr/bin/env python3
"""Remote Colab Tesla T4 Flow Video Worker.

Generates smooth AI keyframe transitions (Start -> End Frames flipbook crossfade),
stitches video clips, normalizes audio loudness (-11.0 LUFS / -1.0 dBTP), burns in
Vietnamese .srt subtitles, overlays rounded channel watermark logos (100x100 at
W-w-36:H-h-36), and encodes with hardware-accelerated h264_nvenc (or libx264 fallback).
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("flow_video_worker")

_NVENC_AVAILABLE: bool | None = None


def has_nvenc() -> bool:
    """Check if ffmpeg on the remote host supports h264_nvenc hardware acceleration.

    Tests a 1-frame null encode:
    ffmpeg -f lavfi -i color=c=black:s=64x64:d=0.04 -c:v h264_nvenc -f null -
    Returns True if exit code is 0, else False.
    """
    global _NVENC_AVAILABLE
    if _NVENC_AVAILABLE is not None:
        return _NVENC_AVAILABLE

    try:
        res = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=black:s=64x64:d=0.04",
                "-c:v",
                "h264_nvenc",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            check=False,
        )
        _NVENC_AVAILABLE = (res.returncode == 0)
    except Exception:
        _NVENC_AVAILABLE = False

    return _NVENC_AVAILABLE


def video_encoder_args(use_nvenc: bool | None = None) -> list[str]:
    """Return ffmpeg video encoder arguments.

    If use_nvenc is True (or auto-detected True via has_nvenc()):
        returns ['-c:v', 'h264_nvenc', '-preset', 'p4', '-cq', '19', '-pix_fmt', 'yuv420p']
    Otherwise fallback to:
        returns ['-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p']
    """
    active_nvenc = has_nvenc() if use_nvenc is None else bool(use_nvenc)
    if active_nvenc:
        return ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19", "-pix_fmt", "yuv420p"]
    return ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p"]


def make_rounded_watermark(
    logo_path: str | Path,
    output_path: str | Path,
    size: int = 100,
    opacity: float = 0.92,
    radius: int = 15,
) -> Path:
    """Create a rounded-corner 100x100 watermark PNG at 92% opacity."""
    from PIL import Image, ImageChops, ImageDraw

    logo_p = Path(logo_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(logo_p).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=int(round(255 * opacity)))

    _, _, _, a = img.split()
    combined_a = ImageChops.multiply(a, mask)
    img.putalpha(combined_a)
    img.save(out_p, format="PNG")
    return out_p


def probe_video(video_path: str | Path) -> dict[str, Any]:
    """Probe video file duration, dimensions, codecs, and size via ffprobe."""
    vp = Path(video_path)
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(vp.resolve()),
    ]
    data = json.loads(subprocess.check_output(cmd, text=True))
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    dur = float(data.get("format", {}).get("duration", 0.0))
    size_bytes = int(data.get("format", {}).get("size", vp.stat().st_size if vp.exists() else 0))

    return {
        "width": int(v.get("width", 0)),
        "height": int(v.get("height", 0)),
        "video_codec": v.get("codec_name", "unknown"),
        "audio_codec": a.get("codec_name", "none"),
        "duration": round(dur, 4),
        "size_bytes": size_bytes,
        "size_mb": round(size_bytes / (1024 * 1024), 2),
    }


def probe_audio_duration(audio_path: str | Path) -> float:
    """Return duration of audio file in seconds."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(Path(audio_path).resolve()),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out) if out else 0.0


def render_flipbook_segment(
    start_image: str | Path,
    end_image: str | Path | None,
    output_mp4: str | Path,
    duration_sec: float,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    crossfade_sec: float = 0.45,
    use_nvenc: bool | None = None,
) -> Path:
    """Render single flipbook transition segment from start_image to end_image."""
    start_p = Path(start_image)
    if not start_p.is_file():
        raise FileNotFoundError(f"Start image file not found: {start_image}")

    dur = max(0.2, float(duration_sec))
    out_p = Path(output_mp4)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    has_end = False
    if end_image is not None:
        end_p = Path(end_image)
        if end_p.is_file() and end_p.resolve() != start_p.resolve():
            has_end = True

    nb_frames = max(1, int(round(dur * fps)))
    step = 0.04 / nb_frames
    enc_args = video_encoder_args(use_nvenc)

    if has_end:
        assert end_image is not None
        end_p = Path(end_image)
        xfade_dur = min(crossfade_sec, max(0.1, dur * 0.4))
        if xfade_dur >= dur:
            xfade_dur = dur / 2.0
        offset = max(0.0, dur - xfade_dur)

        filter_complex = (
            f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"zoompan=z='min(zoom+{step:.6f},1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}[v0];"
            f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v1];"
            f"[v0][v1]xfade=transition=fade:duration={xfade_dur:.4f}:offset={offset:.4f}[outv]"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            str(dur),
            "-r",
            str(fps),
            "-i",
            str(start_p.resolve()),
            "-loop",
            "1",
            "-t",
            str(xfade_dur + 0.5),
            "-r",
            str(fps),
            "-i",
            str(end_p.resolve()),
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            *enc_args,
            "-t",
            str(dur),
            str(out_p.resolve()),
        ]
    else:
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"zoompan=z='min(zoom+{step:.6f},1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            str(dur),
            "-r",
            str(fps),
            "-i",
            str(start_p.resolve()),
            "-vf",
            vf,
            *enc_args,
            "-t",
            str(dur),
            str(out_p.resolve()),
        ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"render_flipbook_segment failed for {start_p.name}:\n{res.stderr.strip()[:400]}")

    return out_p


def _resolve_file(base_dir: Path, p: str | Path | None) -> Path | None:
    if not p:
        return None
    pth = Path(p)
    if pth.is_file():
        return pth.resolve()
    cand = base_dir / pth
    if cand.is_file():
        return cand.resolve()
    # Also check inside common subdirectories
    for sub in ("keyframes", "clips", "assets"):
        sub_cand = base_dir / sub / pth.name
        if sub_cand.is_file():
            return sub_cand.resolve()
    return pth


def render_single_job(req_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Execute Flow Video clip generation, stitching, loudness normalization, subtitle burn-in, and logo overlay."""
    req_file = Path(req_path).resolve()
    if not req_file.is_file():
        raise FileNotFoundError(f"Job request file not found: {req_path}")

    req_dir = req_file.parent
    req = json.loads(req_file.read_text(encoding="utf-8"))

    job_id = str(req.get("job_id", req_file.stem))
    raw_aspect = str(req.get("aspect", req.get("aspect_tag", "16:9"))).lower().strip()
    is_long = raw_aspect in ("16:9", "16x9", "long_16x9")
    aspect_tag = "16x9" if is_long else "9x16"
    width = 1920 if is_long else 1080
    height = 1080 if is_long else 1920
    fps = int(req.get("fps", 30))

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = out_dir / "_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    use_nvenc_pref = req.get("use_nvenc")
    nvenc_active = has_nvenc() if use_nvenc_pref is None else bool(use_nvenc_pref)
    encoder_name = "h264_nvenc" if nvenc_active else "libx264"
    enc_args = video_encoder_args(nvenc_active)

    # 1. Resolve audio file and duration
    raw_audio = req.get("audio_path") or req.get("audio_file") or "narration.wav"
    audio_path = _resolve_file(req_dir, raw_audio)
    has_audio = audio_path is not None and audio_path.is_file()
    audio_duration = probe_audio_duration(audio_path) if has_audio else 0.0

    # 2. Determine clip sequence
    clips_input = req.get("clips")
    clip_paths: list[Path] = []

    if clips_input and isinstance(clips_input, list) and len(clips_input) > 0:
        # Pre-supplied video clips
        for c in clips_input:
            c_str = c if isinstance(c, str) else str(c.get("output_mp4_path") or c.get("path") or c.get("src", ""))
            cp = _resolve_file(req_dir, c_str)
            if cp and cp.is_file():
                clip_paths.append(cp)
            else:
                raise FileNotFoundError(f"Clip file not found: {c_str}")
    else:
        # Render clips from keyframe sequence
        keyframes: list[dict[str, Any]] = req.get("keyframes", [])
        if not keyframes:
            raise ValueError(f"No keyframes or clips provided in request {req_file}")

        num_keyframes = len(keyframes)
        num_segments = max(1, num_keyframes - 1) if num_keyframes > 1 else 1

        target_total_dur = (
            audio_duration
            if audio_duration > 0.5
            else float(req.get("duration") or sum(float(k.get("target_duration") or k.get("duration") or 5.0) for k in keyframes))
        )

        # Distribute segment durations
        nominal_durs = [
            float(keyframes[i].get("target_duration") or keyframes[i].get("duration") or 1.0)
            for i in range(num_segments)
        ]
        sum_nom = sum(nominal_durs)
        if sum_nom > 0:
            durations = [target_total_dur * (d / sum_nom) for d in nominal_durs]
        else:
            durations = [target_total_dur / num_segments] * num_segments

        # Exact duration alignment with audio
        durations[-1] = max(0.2, target_total_dur - sum(durations[:-1]))

        # Render each transition segment
        for i in range(num_segments):
            kf_start = keyframes[i]
            img_start_str = kf_start.get("image_path") or kf_start.get("filename") or kf_start.get("path") or ""
            start_img = _resolve_file(req_dir, img_start_str)
            if not start_img or not start_img.is_file():
                raise FileNotFoundError(f"Keyframe image not found: {img_start_str}")

            end_img: Path | None = None
            if num_keyframes > 1 and i < num_keyframes - 1:
                kf_end = keyframes[i + 1]
                img_end_str = kf_end.get("image_path") or kf_end.get("filename") or kf_end.get("path") or ""
                end_img = _resolve_file(req_dir, img_end_str)

            seg_out = work_dir / f"seg_{i:03d}.mp4"
            seg_dur = durations[i]
            logger.info(
                f"[{job_id}] Rendering segment {i + 1}/{num_segments} ({seg_dur:.2f}s): "
                f"{start_img.name} -> {end_img.name if end_img else 'HOLD'}"
            )
            render_flipbook_segment(
                start_image=start_img,
                end_image=end_img,
                output_mp4=seg_out,
                duration_sec=seg_dur,
                width=width,
                height=height,
                fps=fps,
                crossfade_sec=0.45,
                use_nvenc=nvenc_active,
            )
            clip_paths.append(seg_out)

    if not clip_paths:
        raise ValueError(f"No valid clips generated for {job_id}")

    # 3. Watermark logo preparation
    raw_logo = req.get("logo_path") or req.get("logo_file") or "logo.png"
    logo_path = _resolve_file(req_dir, raw_logo)
    watermark_png: Path | None = None
    if logo_path and logo_path.is_file():
        watermark_png = work_dir / "watermark_100x100.png"
        make_rounded_watermark(logo_path, watermark_png, size=100, opacity=0.92, radius=15)

    # 4. Subtitles preparation
    raw_srt = req.get("srt_path") or req.get("srt_file") or "subtitles.srt"
    srt_path = _resolve_file(req_dir, raw_srt)
    burn_subs_cfg = req.get("burn_subtitles")
    burn_subtitles = (aspect_tag == "9x16") if burn_subs_cfg is None else bool(burn_subs_cfg)
    has_subtitles = burn_subtitles and srt_path is not None and srt_path.is_file()

    # 5. Build unified ffmpeg compositing command
    cmd: list[str] = ["ffmpeg", "-y"]
    for cp in clip_paths:
        cmd.extend(["-i", str(cp.resolve())])

    logo_input_idx: int | None = None
    if watermark_png and watermark_png.is_file():
        logo_input_idx = len(clip_paths)
        cmd.extend(["-i", str(watermark_png.resolve())])

    audio_input_idx: int | None = None
    if has_audio:
        assert audio_path is not None
        audio_input_idx = (len(clip_paths) + 1) if logo_input_idx is not None else len(clip_paths)
        cmd.extend(["-i", str(audio_path.resolve())])

    filter_chains: list[str] = []

    # Concat clips
    if len(clip_paths) == 1:
        filter_chains.append(f"[0:v]setsar=1,fps={fps}[vconcat]")
    else:
        concat_labels = []
        for i in range(len(clip_paths)):
            filter_chains.append(f"[{i}:v]setsar=1,fps={fps}[v{i}]")
            concat_labels.append(f"[v{i}]")
        filter_chains.append(f"{''.join(concat_labels)}concat=n={len(clip_paths)}:v=1:a=0[vconcat]")

    cur_v = "vconcat"

    # Burn subtitles if enabled
    if has_subtitles:
        assert srt_path is not None
        escaped_srt = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        filter_chains.append(
            f"[{cur_v}]subtitles='{escaped_srt}':force_style='FontName=Arial,FontSize=20,MarginV=140,Alignment=2'[vsub]"
        )
        cur_v = "vsub"

    # Overlay watermark logo
    if logo_input_idx is not None:
        filter_chains.append(f"[{cur_v}][{logo_input_idx}:v]overlay=W-w-36:H-h-36[vlogo]")
        cur_v = "vlogo"

    # Loudness normalization for audio (-11.0 LUFS / -1.0 dBTP)
    if audio_input_idx is not None:
        filter_chains.append(
            f"[{audio_input_idx}:a]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[afinal]"
        )

    final_mp4 = out_dir / f"video_{aspect_tag}.mp4"
    cmd.extend(["-filter_complex", ";".join(filter_chains)])
    cmd.extend(["-map", f"[{cur_v}]"])

    if audio_input_idx is not None:
        cmd.extend(["-map", "[afinal]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"])
        if audio_duration > 0.1:
            cmd.extend(["-t", f"{audio_duration:.3f}"])
        else:
            cmd.append("-shortest")
    else:
        cmd.append("-an")

    cmd.extend(enc_args)
    cmd.extend(["-movflags", "+faststart", str(final_mp4.resolve())])

    logger.info(f"[{job_id}] Compositing final video -> {final_mp4.name} (encoder={encoder_name})...")
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        logger.error(f"FFmpeg composite failed:\n{res.stderr.strip()[:600]}")
        raise RuntimeError(f"Compositing video failed for {job_id}:\n{res.stderr.strip()[:400]}")

    # 6. Verify and output results
    meta = probe_video(final_mp4)
    result = {
        "job_id": job_id,
        "aspect": raw_aspect,
        "aspect_tag": aspect_tag,
        "width": meta["width"],
        "height": meta["height"],
        "duration": meta["duration"],
        "encoder": encoder_name,
        "size_bytes": meta["size_bytes"],
        "video_path": str(final_mp4.resolve()),
        "rendered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    result_json_path = out_dir / "render-result.json"
    result_json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Copy srt into output_dir if available for downstream consumers
    if srt_path and srt_path.is_file():
        shutil.copy2(srt_path, out_dir / "subtitles.srt")

    # 7. Pack single job zip archive
    zip_path = Path(output_dir).with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(final_mp4, final_mp4.name)
        zf.write(result_json_path, result_json_path.name)
        if (out_dir / "subtitles.srt").is_file():
            zf.write(out_dir / "subtitles.srt", "subtitles.srt")

    logger.info(f"[{job_id}] Render complete: {final_mp4.name} ({meta['duration']}s, {meta['size_mb']}MB, zip={zip_path.name})")

    # Clean up temp working files
    shutil.rmtree(work_dir, ignore_errors=True)

    return result


def run(request_path: str, output_base_dir: str) -> dict[str, Any]:
    """Compatibility wrapper calling render_single_job."""
    return render_single_job(request_path, output_base_dir)


def run_batch(batch_manifest_path: str | Path, out_base_dir: str | Path) -> dict[str, Any]:
    """Execute batch rendering over a manifest of job requests and pack into batch_results.zip."""
    manifest_p = Path(batch_manifest_path).resolve()
    if not manifest_p.is_file():
        raise FileNotFoundError(f"Batch manifest file not found: {batch_manifest_path}")

    out_base = Path(out_base_dir).resolve()
    out_base.mkdir(parents=True, exist_ok=True)

    manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
    if isinstance(manifest_data, list):
        items = manifest_data
    elif isinstance(manifest_data, dict):
        items = manifest_data.get("jobs", manifest_data.get("requests", manifest_data.get("items", [manifest_data])))
    else:
        items = [manifest_data]

    results: list[dict[str, Any]] = []
    job_zips: list[Path] = []

    for idx, item in enumerate(items):
        if isinstance(item, str):
            req_p = _resolve_file(manifest_p.parent, item)
            if not req_p or not req_p.is_file():
                raise FileNotFoundError(f"Job request file not found: {item}")
            req_dict = json.loads(req_p.read_text(encoding="utf-8"))
            job_id = str(req_dict.get("job_id", req_p.stem))
        elif isinstance(item, dict):
            req_dict = item
            job_id = str(req_dict.get("job_id", f"job_{idx:03d}"))
            req_p = out_base / f"req_{job_id}.json"
            req_p.write_text(json.dumps(req_dict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            continue

        job_out_dir = out_base / job_id
        logger.info(f"[BATCH] Processing job {idx + 1}/{len(items)}: {job_id}...")
        res = render_single_job(req_p, job_out_dir)
        results.append(res)

        jzip = Path(job_out_dir).with_suffix(".zip")
        if jzip.is_file():
            job_zips.append(jzip)

    # Pack all resulting zip files into batch_results.zip
    batch_zip = out_base / "batch_results.zip"
    with zipfile.ZipFile(batch_zip, "w", zipfile.ZIP_DEFLATED) as bz:
        for jz in job_zips:
            bz.write(jz, jz.name)
        batch_summary = {
            "completed": len(results),
            "jobs": results,
            "batch_zip": str(batch_zip.resolve()),
        }
        bz.writestr("batch-result.json", json.dumps(batch_summary, ensure_ascii=False, indent=2) + "\n")

    logger.info(f"[BATCH] Completed {len(results)} jobs. Packed into {batch_zip.name}.")
    return {
        "completed": len(results),
        "jobs": results,
        "batch_zip": str(batch_zip.resolve()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Colab Tesla T4 Flow Video Worker.")
    parser.add_argument("--job", help="Path to single job request JSON")
    parser.add_argument("--batch", help="Path to batch manifest JSON")
    parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    parser.add_argument("--check-nvenc", action="store_true", help="Check h264_nvenc availability")
    args = parser.parse_args()

    if args.check_nvenc:
        nv = has_nvenc()
        print(f"h264_nvenc available: {nv}")
        sys.exit(0 if nv else 1)

    if args.job:
        res = render_single_job(args.job, args.output_dir)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.batch:
        res = run_batch(args.batch, args.output_dir)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 3 and not sys.argv[1].startswith("-"):
        run(sys.argv[1], sys.argv[2])
    else:
        main()
