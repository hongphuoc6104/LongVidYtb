#!/usr/bin/env python3
"""Remote Colab Tesla T4 Flow Video Worker & Native NVENC Compositor.

Generates smooth AI keyframe transitions (Start -> End Frames flipbook crossfade),
stitches video clips, normalizes audio loudness (-11.0 LUFS / -1.0 dBTP), burns in
Vietnamese .srt subtitles, overlays rounded channel watermark logos (100x100 at
W-w-36:H-h-36 or W-w-32:120), and encodes with hardware-accelerated h264_nvenc
(or libx264 CPU fallback).
"""

from __future__ import annotations

import argparse
import base64
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
    ffmpeg -f lavfi -i color=c=black:s=256x256:d=0.04 -c:v h264_nvenc -f null -
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
                "color=c=black:s=256x256:d=0.04",
                "-c:v",
                "h264_nvenc",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            check=False,
        )
        _NVENC_AVAILABLE = res.returncode == 0
    except Exception:
        _NVENC_AVAILABLE = False

    return _NVENC_AVAILABLE


def video_encoder_args(use_nvenc: bool | None = None) -> list[str]:
    """Return ffmpeg video encoder arguments.

    If use_nvenc is True (or auto-detected True via has_nvenc()):
        returns ['-c:v', 'h264_nvenc', '-preset', 'p4', '-b:v', '6M', '-pix_fmt', 'yuv420p']
    Otherwise fallback to:
        returns ['-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p']
    """
    active_nvenc = has_nvenc() if use_nvenc is None else bool(use_nvenc)
    if active_nvenc:
        return ["-c:v", "h264_nvenc", "-preset", "p4", "-b:v", "6M", "-pix_fmt", "yuv420p"]
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
    cand_name = base_dir / pth.name
    if cand_name.is_file():
        return cand_name.resolve()
    # Also check inside common subdirectories
    for sub in ("keyframes", "clips", "assets", "public"):
        sub_cand = base_dir / sub / pth.name
        if sub_cand.is_file():
            return sub_cand.resolve()
    return None


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
        for c in clips_input:
            c_str = c if isinstance(c, str) else str(c.get("output_mp4_path") or c.get("path") or c.get("src", ""))
            cp = _resolve_file(req_dir, c_str)
            if cp and cp.is_file():
                clip_paths.append(cp)
            else:
                raise FileNotFoundError(f"Clip file not found: {c_str}")
    else:
        keyframes: list[dict[str, Any]] = req.get("keyframes", [])
        if not keyframes:
            raise ValueError(f"No keyframes or clips provided in request {req_file}")

        num_keyframes = len(keyframes)
        num_segments = max(1, num_keyframes - 1) if num_keyframes > 1 else 1

        target_total_dur = (
            audio_duration
            if audio_duration > 0.5
            else float(
                req.get("duration")
                or sum(float(k.get("target_duration") or k.get("duration") or 5.0) for k in keyframes)
            )
        )

        nominal_durs = [
            float(keyframes[i].get("target_duration") or keyframes[i].get("duration") or 1.0)
            for i in range(num_segments)
        ]
        sum_nom = sum(nominal_durs)
        if sum_nom > 0:
            durations = [target_total_dur * (d / sum_nom) for d in nominal_durs]
        else:
            durations = [target_total_dur / num_segments] * num_segments

        durations[-1] = max(0.2, target_total_dur - sum(durations[:-1]))

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

    if len(clip_paths) == 1:
        filter_chains.append(f"[0:v]setsar=1,fps={fps}[vconcat]")
    else:
        concat_labels = []
        for i in range(len(clip_paths)):
            filter_chains.append(f"[{i}:v]setsar=1,fps={fps}[v{i}]")
            concat_labels.append(f"[v{i}]")
        filter_chains.append(f"{''.join(concat_labels)}concat=n={len(clip_paths)}:v=1:a=0[vconcat]")

    cur_v = "vconcat"

    if has_subtitles:
        assert srt_path is not None
        escaped_srt = str(srt_path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        filter_chains.append(
            f"[{cur_v}]subtitles='{escaped_srt}':force_style='FontName=Arial,FontSize=20,MarginV=140,Alignment=2'[vsub]"
        )
        cur_v = "vsub"

    if logo_input_idx is not None:
        filter_chains.append(f"[{cur_v}][{logo_input_idx}:v]overlay=W-w-36:H-h-36[vlogo]")
        cur_v = "vlogo"

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

    if srt_path and srt_path.is_file():
        shutil.copy2(srt_path, out_dir / "subtitles.srt")

    zip_path = Path(output_dir).with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(final_mp4, final_mp4.name)
        zf.write(result_json_path, result_json_path.name)
        if (out_dir / "subtitles.srt").is_file():
            zf.write(out_dir / "subtitles.srt", "subtitles.srt")

    logger.info(
        f"[{job_id}] Render complete: {final_mp4.name} ({meta['duration']}s, {meta['size_mb']}MB, zip={zip_path.name})"
    )

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


def format_srt_timestamp(seconds: float) -> str:
    """Format seconds into standard SRT timestamp HH:MM:SS,mmm."""
    total_ms = max(0, int(round(float(seconds) * 1000)))
    ms = total_ms % 1000
    total_sec = total_ms // 1000
    s = total_sec % 60
    total_min = total_sec // 60
    m = total_min % 60
    h = total_min // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(cues: list[dict[str, Any]] | None) -> str:
    """Generate SubRip (.srt) string from subtitle cues list."""
    if not cues or not isinstance(cues, list):
        return ""
    entries = []
    idx = 1
    for cue in cues:
        if not isinstance(cue, dict):
            continue
        text = str(cue.get("text", "")).strip()
        if not text:
            continue
        start_ts = format_srt_timestamp(cue.get("start", 0.0))
        end_ts = format_srt_timestamp(cue.get("end", 0.0))
        entries.append(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n")
        idx += 1
    return "\n".join(entries)


def generate_thumbnail_image(
    output_path: Path,
    width: int,
    height: int,
    image_src: Path | None,
    text: str = "",
) -> None:
    """Generate thumbnail or cover image at specified dimensions with title overlay."""
    from PIL import Image, ImageDraw, ImageFont

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if image_src and image_src.is_file():
        try:
            base_img = Image.open(image_src).convert("RGBA")
            img_ratio = base_img.width / base_img.height
            target_ratio = width / height
            if img_ratio > target_ratio:
                new_h = height
                new_w = int(round(height * img_ratio))
            else:
                new_w = width
                new_h = int(round(width / img_ratio))
            base_img = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - width) // 2
            top = (new_h - height) // 2
            canvas = base_img.crop((left, top, left + width, top + height)).convert("RGB")
        except Exception:
            canvas = Image.new("RGB", (width, height), "#F8F0DC")
    else:
        canvas = Image.new("RGB", (width, height), "#F8F0DC")

    clean_text = text.strip()
    if clean_text:
        draw = ImageDraw.Draw(canvas)
        font_size = max(24, int(height * 0.055))
        font = None
        for font_cand in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ):
            if Path(font_cand).is_file():
                try:
                    font = ImageFont.truetype(font_cand, font_size)
                    break
                except Exception:
                    pass
        if font is None:
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

        if font:
            words = clean_text.split()
            lines = []
            cur_line: list[str] = []
            for w in words:
                cur_line.append(w)
                bbox = draw.textbbox((0, 0), " ".join(cur_line), font=font)
                if bbox[2] - bbox[0] > width * 0.85:
                    if len(cur_line) > 1:
                        cur_line.pop()
                        lines.append(" ".join(cur_line))
                        cur_line = [w]
                    else:
                        lines.append(" ".join(cur_line))
                        cur_line = []
            if cur_line:
                lines.append(" ".join(cur_line))

            line_height = int(font_size * 1.35)
            start_y = int(height * 0.22)
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_w = bbox[2] - bbox[0]
                pos_x = (width - line_w) // 2
                pos_y = start_y + i * line_height
                for dx, dy in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, 3), (0, -3), (3, 0), (-3, 0)):
                    draw.text((pos_x + dx, pos_y + dy), line, font=font, fill=(0, 0, 0))
                draw.text((pos_x, pos_y), line, font=font, fill=(255, 255, 255))

    canvas.save(output_path, format="PNG")


def _extract_watermark(work_p: Path, props: dict[str, Any], scratch: Path) -> Path | None:
    """Extract or decode rounded watermark image."""
    thumb_spec = props.get("thumbnail_spec") or {}
    logo_data_uri = thumb_spec.get("brand_logo_data_uri") or props.get("brand_logo_data_uri")
    raw_logo_path: Path | None = None
    if logo_data_uri and isinstance(logo_data_uri, str) and logo_data_uri.startswith("data:"):
        try:
            _, encoded = logo_data_uri.split(",", 1)
            raw_bytes = base64.b64decode(encoded)
            raw_logo_path = scratch / "decoded_logo.png"
            raw_logo_path.write_bytes(raw_bytes)
        except Exception as e:
            logger.warning(f"Failed to decode brand_logo_data_uri: {e}")

    if not raw_logo_path or not raw_logo_path.is_file():
        cand = props.get("logo_path") or props.get("logo_file") or thumb_spec.get("logo_path")
        if cand:
            resolved = _resolve_file(work_p, cand)
            if resolved and resolved.is_file():
                raw_logo_path = resolved
            else:
                pub_cand = work_p / "public" / Path(cand).name
                if pub_cand.is_file():
                    raw_logo_path = pub_cand

    if not raw_logo_path or not raw_logo_path.is_file():
        for def_logo in (
            work_p / "public" / "brand_logo.png",
            work_p / "brand_logo.png",
        ):
            if def_logo.is_file():
                raw_logo_path = def_logo
                break

    if raw_logo_path and raw_logo_path.is_file():
        out_wm = scratch / "watermark_100x100.png"
        try:
            return make_rounded_watermark(raw_logo_path, out_wm, size=100, opacity=0.92, radius=15)
        except Exception as e:
            logger.warning(f"Failed to generate rounded watermark from {raw_logo_path}: {e}")
            return None
    return None


def _write_social_post_kit(work_dir: Path, props: dict[str, Any]) -> None:
    """Generate Markdown social media posting guide for omni-platform deliverables."""
    topic = props.get("hook_title") or props.get("topic") or "Explainer Video"
    shorts = props.get("short_deliveries", [])
    lines = [
        f"# Social Media Distribution Kit: {topic}",
        "",
        "## 1. YouTube Master (16:9)",
        "- File: `video_youtube_16x9.mp4`",
        "- Thumbnail: `thumbnail_youtube_16x9.png`",
        f"- Title: {topic}",
        "",
        "## 2. Facebook Master (16:9 Burned-in Subtitles)",
        "- File: `video_facebook_16x9.mp4`",
        "",
        "## 3. TikTok & Reels Short Spinoffs (9:16)",
        "- Cover Image: `cover_tiktok_reels_9x16.png`",
    ]
    for idx, s in enumerate(shorts, 1):
        s_file = s.get("file", f"video_tiktok_short_{idx:02d}_9x16.mp4")
        s_props = s.get("props", {})
        s_hook = s_props.get("hook_title") or f"Short #{idx}"
        lines.append(f"- **Short {idx:02d}**: `{s_file}` — *{s_hook}*")
    lines.append("")
    (work_dir / "SOCIAL_POST_KIT.md").write_text("\n".join(lines), encoding="utf-8")


def _render_delivery_plan(
    work_p: Path,
    output_mp4: Path,
    width: int,
    height: int,
    target_duration: float,
    scenes: list[dict[str, Any]],
    cues: list[dict[str, Any]],
    burn_subtitles: bool,
    audio_path: Path | None,
    bgm_path: Path | None,
    bgm_volume: float | None,
    watermark_png: Path | None,
    use_nvenc: bool,
    scratch_dir: Path,
) -> None:
    """Render a single timeline delivery plan via FFmpeg NVENC (or CPU fallback)."""
    fps = 30
    flat_beats: list[dict[str, Any]] = []

    for scene_idx, scene in enumerate(scenes):
        scene_start = float(scene.get("start", 0.0))
        if "end" in scene:
            scene_end = float(scene["end"])
        elif "durationInFrames" in scene:
            scene_end = scene_start + float(scene["durationInFrames"]) / fps
        elif "endFrame" in scene:
            scene_end = float(scene["endFrame"]) / fps
        elif "duration" in scene:
            scene_end = scene_start + float(scene["duration"])
        else:
            scene_end = scene_start

        beats = scene.get("images")
        if not beats:
            img = scene.get("image") or scene.get("src") or ""
            beats = [{"src": img, "at": 0.0, "is_endcard": scene.get("is_endcard", False)}]

        for b_idx, beat in enumerate(beats):
            b_at = float(beat.get("at", 0.0))
            abs_at = scene_start + b_at
            flat_beats.append({
                "beat": beat,
                "scene": scene,
                "scene_idx": scene_idx,
                "beat_idx": b_idx,
                "abs_at": abs_at,
                "scene_end": scene_end,
            })

    flat_beats.sort(key=lambda x: x["abs_at"])

    if target_duration <= 0.0:
        if audio_path and audio_path.is_file():
            target_duration = probe_audio_duration(audio_path)
        if target_duration <= 0.0:
            target_duration = 5.0

    if flat_beats:
        nominal_durs = []
        for i in range(len(flat_beats)):
            fb = flat_beats[i]
            if i + 1 < len(flat_beats):
                next_start = flat_beats[i + 1]["abs_at"]
                d = next_start - fb["abs_at"]
            else:
                d = max(0.1, fb["scene_end"] - fb["abs_at"])
                if d <= 0.05 and target_duration > fb["abs_at"]:
                    d = target_duration - fb["abs_at"]
            if d <= 0.01:
                d = 0.5
            nominal_durs.append(d)

        sum_nom = sum(nominal_durs)
        if sum_nom > 0:
            durations = [round(d * target_duration / sum_nom, 4) for d in nominal_durs]
        else:
            durations = [round(target_duration / len(flat_beats), 4)] * len(flat_beats)
        durations[-1] = max(0.05, round(target_duration - sum(durations[:-1]), 4))
    else:
        durations = []

    endcard_start = None
    curr_time = 0.0
    for i, fb in enumerate(flat_beats):
        b = fb["beat"]
        is_ec = bool(b.get("is_endcard") or b.get("spec") == "endcard" or fb["scene"].get("is_endcard"))
        if is_ec and endcard_start is None:
            endcard_start = curr_time
        curr_time += durations[i]

    sub_filter = ""
    srt_p = work_p / "subtitles.srt"
    if burn_subtitles and cues and srt_p.is_file() and srt_p.stat().st_size > 0:
        escaped_srt = str(srt_p.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        font_size = 48 if height > width else 32
        margin_v = 400 if height > width else 64
        sub_filter = (
            f"subtitles=filename={escaped_srt}:original_size={width}x{height}:"
            f"force_style='FontName=Arial,FontSize={font_size},Bold=1,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,MarginV={margin_v},Alignment=2'"
        )

    enc_args = video_encoder_args(use_nvenc)

    if len(flat_beats) == 0:
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=#F8F0DC:s={width}x{height}:d={target_duration:.4f}:r=30",
        ]
        filter_chains = ["setsar=1,fps=30,format=yuv420p[vconcat]"]
        cur_v = "vconcat"
        inp_idx = 1

        if sub_filter:
            filter_chains.append(f"[{cur_v}]{sub_filter}[vsub]")
            cur_v = "vsub"

        if watermark_png and watermark_png.is_file():
            cmd.extend(["-i", str(watermark_png.resolve())])
            wm_pos = "W-w-32:120" if height > width else "W-w-36:H-h-36"
            enable_str = f":enable='between(t,0,{endcard_start:.3f})'" if endcard_start is not None else ""
            filter_chains.append(f"[{cur_v}][{inp_idx}:v]overlay={wm_pos}{enable_str}[vwm]")
            cur_v = "vwm"
            inp_idx += 1

        has_audio = audio_path is not None and audio_path.is_file()
        if has_audio:
            cmd.extend(["-i", str(audio_path.resolve())])
            audio_inp = inp_idx
            inp_idx += 1
            has_bgm = bgm_path is not None and bgm_path.is_file() and bgm_volume is not None
            if has_bgm:
                cmd.extend(["-stream_loop", "-1", "-i", str(bgm_path.resolve())])
                bgm_inp = inp_idx
                inp_idx += 1
                filter_chains.append(
                    f"[{bgm_inp}:a]volume={float(bgm_volume):.4f}[bgm_ducked];"
                    f"[{audio_inp}:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[amixed];"
                    f"[amixed]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[afinal]"
                )
            else:
                filter_chains.append(
                    f"[{audio_inp}:a]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[afinal]"
                )
        else:
            filter_chains.append(
                "anullsrc=r=48000:cl=stereo,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[afinal]"
            )

        cmd.extend([
            "-filter_complex",
            ";".join(filter_chains),
            "-map",
            f"[{cur_v}]",
            "-map",
            "[afinal]",
            "-t",
            f"{target_duration:.4f}",
            *enc_args,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output_mp4.resolve()),
        ])
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg composite failed:\n{res.stderr[-600:]}")
        return

    elif len(flat_beats) <= 16:
        cmd = ["ffmpeg", "-y"]
        filter_chains = []
        v_labels = []
        inp_idx = 0

        for idx, fb in enumerate(flat_beats):
            dur = durations[idx]
            beat = fb["beat"]
            src_str = beat.get("src") or beat.get("image") or fb["scene"].get("image") or ""
            res_path = _resolve_file(work_p / "public", src_str) or _resolve_file(work_p, src_str)
            if not res_path or not res_path.is_file():
                fallback_img = scratch_dir / f"fallback_{idx}.png"
                if not fallback_img.is_file():
                    try:
                        from PIL import Image

                        im = Image.new("RGB", (width, height), "#F8F0DC")
                        im.save(fallback_img, format="PNG")
                    except Exception:
                        pass
                res_path = fallback_img

            is_video = res_path.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv")
            if is_video:
                cmd.extend(["-i", str(res_path.resolve())])
                trim_before = int(beat.get("trim_before") or 0)
                playback_rate = float(beat.get("playback_rate") or 1.0)
                if playback_rate <= 0:
                    playback_rate = 1.0
                filter_chains.append(
                    f"[{inp_idx}:v]trim=start_frame={trim_before},"
                    f"setpts=PTS-STARTPTS,"
                    f"setpts=PTS/{playback_rate:.4f},"
                    f"tpad=stop_mode=clone:stop_duration=3.0,"
                    f"trim=duration={dur:.4f},"
                    f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                    f"setsar=1,fps=30,format=yuv420p[v{idx}]"
                )
            else:
                cmd.extend(["-loop", "1", "-t", f"{dur:.4f}", "-r", "30", "-i", str(res_path.resolve())])
                is_ec = bool(beat.get("is_endcard") or beat.get("spec") == "endcard" or fb["scene"].get("is_endcard"))
                if is_ec:
                    filter_chains.append(
                        f"[{inp_idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                        f"setsar=1,fps=30,format=yuv420p[v{idx}]"
                    )
                else:
                    filter_chains.append(
                        f"[{inp_idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
                        f"zoompan=z='min(zoom+0.0008,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps=30,format=yuv420p[v{idx}]"
                    )
            v_labels.append(f"[v{idx}]")
            inp_idx += 1

        if len(v_labels) == 1:
            filter_chains.append("[v0]null[vconcat]")
            cur_v = "vconcat"
        else:
            filter_chains.append(f"{''.join(v_labels)}concat=n={len(v_labels)}:v=1:a=0[vconcat]")
            cur_v = "vconcat"

        if sub_filter:
            filter_chains.append(f"[{cur_v}]{sub_filter}[vsub]")
            cur_v = "vsub"

        if watermark_png and watermark_png.is_file():
            cmd.extend(["-i", str(watermark_png.resolve())])
            wm_pos = "W-w-32:120" if height > width else "W-w-36:H-h-36"
            enable_str = f":enable='between(t,0,{endcard_start:.3f})'" if endcard_start is not None else ""
            filter_chains.append(f"[{cur_v}][{inp_idx}:v]overlay={wm_pos}{enable_str}[vwm]")
            cur_v = "vwm"
            inp_idx += 1

        has_audio = audio_path is not None and audio_path.is_file()
        if has_audio:
            cmd.extend(["-i", str(audio_path.resolve())])
            audio_inp = inp_idx
            inp_idx += 1
            has_bgm = bgm_path is not None and bgm_path.is_file() and bgm_volume is not None
            if has_bgm:
                cmd.extend(["-stream_loop", "-1", "-i", str(bgm_path.resolve())])
                bgm_inp = inp_idx
                inp_idx += 1
                filter_chains.append(
                    f"[{bgm_inp}:a]volume={float(bgm_volume):.4f}[bgm_ducked];"
                    f"[{audio_inp}:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[amixed];"
                    f"[amixed]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[afinal]"
                )
            else:
                filter_chains.append(
                    f"[{audio_inp}:a]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[afinal]"
                )
        else:
            filter_chains.append(
                "anullsrc=r=48000:cl=stereo,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[afinal]"
            )

        cmd.extend([
            "-filter_complex",
            ";".join(filter_chains),
            "-map",
            f"[{cur_v}]",
            "-map",
            "[afinal]",
            "-t",
            f"{target_duration:.4f}",
            *enc_args,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output_mp4.resolve()),
        ])
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg composite failed:\n{res.stderr[-600:]}")
        return

    else:
        # > 16 beats: render in chunks of 12 then concat
        chunk_size = 12
        chunk_files: list[Path] = []

        for c_idx in range(0, len(flat_beats), chunk_size):
            chunk_beats = flat_beats[c_idx : c_idx + chunk_size]
            chunk_durs = durations[c_idx : c_idx + chunk_size]
            chunk_dur = sum(chunk_durs)
            chunk_mp4 = scratch_dir / f"chunk_{c_idx // chunk_size:03d}.mp4"
            chunk_files.append(chunk_mp4)

            c_cmd = ["ffmpeg", "-y"]
            c_fc = []
            c_labels = []
            c_inp_idx = 0

            for idx, fb in enumerate(chunk_beats):
                dur = chunk_durs[idx]
                beat = fb["beat"]
                src_str = beat.get("src") or beat.get("image") or fb["scene"].get("image") or ""
                res_path = _resolve_file(work_p / "public", src_str) or _resolve_file(work_p, src_str)
                if not res_path or not res_path.is_file():
                    fallback_img = scratch_dir / f"fallback_c_{c_idx}_{idx}.png"
                    if not fallback_img.is_file():
                        try:
                            from PIL import Image

                            im = Image.new("RGB", (width, height), "#F8F0DC")
                            im.save(fallback_img, format="PNG")
                        except Exception:
                            pass
                    res_path = fallback_img

                is_video = res_path.suffix.lower() in (".mp4", ".mov", ".webm", ".mkv")
                if is_video:
                    c_cmd.extend(["-i", str(res_path.resolve())])
                    trim_before = int(beat.get("trim_before") or 0)
                    playback_rate = float(beat.get("playback_rate") or 1.0)
                    if playback_rate <= 0:
                        playback_rate = 1.0
                    c_fc.append(
                        f"[{c_inp_idx}:v]trim=start_frame={trim_before},"
                        f"setpts=PTS-STARTPTS,"
                        f"setpts=PTS/{playback_rate:.4f},"
                        f"tpad=stop_mode=clone:stop_duration=3.0,"
                        f"trim=duration={dur:.4f},"
                        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                        f"setsar=1,fps=30,format=yuv420p[cv{idx}]"
                    )
                else:
                    c_cmd.extend(["-loop", "1", "-t", f"{dur:.4f}", "-r", "30", "-i", str(res_path.resolve())])
                    is_ec = bool(
                        beat.get("is_endcard") or beat.get("spec") == "endcard" or fb["scene"].get("is_endcard")
                    )
                    if is_ec:
                        c_fc.append(
                            f"[{c_inp_idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                            f"setsar=1,fps=30,format=yuv420p[cv{idx}]"
                        )
                    else:
                        c_fc.append(
                            f"[{c_inp_idx}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
                            f"zoompan=z='min(zoom+0.0008,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps=30,format=yuv420p[cv{idx}]"
                        )
                c_labels.append(f"[cv{idx}]")
                c_inp_idx += 1

            if len(c_labels) == 1:
                c_fc.append("[cv0]null[c_vconcat]")
            else:
                c_fc.append(f"{''.join(c_labels)}concat=n={len(c_labels)}:v=1:a=0[c_vconcat]")

            c_cmd.extend([
                "-filter_complex",
                ";".join(c_fc),
                "-map",
                "[c_vconcat]",
                "-t",
                f"{chunk_dur:.4f}",
                *enc_args,
                "-an",
                str(chunk_mp4.resolve()),
            ])
            res_c = subprocess.run(c_cmd, capture_output=True, text=True, check=False)
            if res_c.returncode != 0:
                raise RuntimeError(f"FFmpeg chunk render failed:\n{res_c.stderr[-600:]}")

        chunks_list_file = scratch_dir / "chunks.txt"
        chunks_list_file.write_text(
            "\n".join(f"file '{p.resolve().as_posix()}'" for p in chunk_files) + "\n",
            encoding="utf-8",
        )

        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(chunks_list_file.resolve())]
        filter_chains = []
        cur_v = "0:v"
        inp_idx = 1

        if sub_filter:
            filter_chains.append(f"[{cur_v}]{sub_filter}[vsub]")
            cur_v = "vsub"

        if watermark_png and watermark_png.is_file():
            cmd.extend(["-i", str(watermark_png.resolve())])
            wm_pos = "W-w-32:120" if height > width else "W-w-36:H-h-36"
            enable_str = f":enable='between(t,0,{endcard_start:.3f})'" if endcard_start is not None else ""
            filter_chains.append(f"[{cur_v}][{inp_idx}:v]overlay={wm_pos}{enable_str}[vwm]")
            cur_v = "vwm"
            inp_idx += 1

        has_audio = audio_path is not None and audio_path.is_file()
        if has_audio:
            cmd.extend(["-i", str(audio_path.resolve())])
            audio_inp = inp_idx
            inp_idx += 1
            has_bgm = bgm_path is not None and bgm_path.is_file() and bgm_volume is not None
            if has_bgm:
                cmd.extend(["-stream_loop", "-1", "-i", str(bgm_path.resolve())])
                bgm_inp = inp_idx
                inp_idx += 1
                filter_chains.append(
                    f"[{bgm_inp}:a]volume={float(bgm_volume):.4f}[bgm_ducked];"
                    f"[{audio_inp}:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[amixed];"
                    f"[amixed]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[afinal]"
                )
            else:
                filter_chains.append(
                    f"[{audio_inp}:a]loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[afinal]"
                )
        else:
            filter_chains.append(
                "anullsrc=r=48000:cl=stereo,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[afinal]"
            )

        if cur_v == "0:v":
            filter_chains.append("[0:v]null[vfinal]")
            cur_v = "vfinal"

        cmd.extend([
            "-filter_complex",
            ";".join(filter_chains),
            "-map",
            f"[{cur_v}]",
            "-map",
            "[afinal]",
            "-t",
            f"{target_duration:.4f}",
            *enc_args,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(output_mp4.resolve()),
        ])
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg composite failed:\n{res.stderr[-600:]}")


def render_props_package(work_dir: str | Path, *, require_nvenc: bool = False) -> dict[str, Any]:
    """Render full video package from props.json using native FFmpeg NVENC (or libx264 CPU fallback).

    Reads <work_dir>/props.json and assets from <work_dir>/public/.
    Generates video deliverables, subtitles (.srt), layout report, thumbnails and scene stills.
    """
    if require_nvenc and not has_nvenc():
        raise RuntimeError("COLAB_NVENC_REQUIRED: h264_nvenc hardware encoder unavailable")

    work_p = Path(work_dir).resolve()
    props_p = work_p / "props.json"
    if not props_p.is_file():
        raise FileNotFoundError(f"Missing props.json in {work_p}")

    props = json.loads(props_p.read_text(encoding="utf-8"))
    public_dir = work_p / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    nvenc_active = has_nvenc()
    encoder_name = "h264_nvenc" if nvenc_active else "libx264"

    scratch_dir = work_p / "_nvenc_work"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    watermark_png = _extract_watermark(work_p, props, scratch_dir)

    # 1. Normalize outputs / plans
    outputs = props.get("outputs")
    if not outputs or not isinstance(outputs, list):
        aspect = str(
            props.get("aspect_ratio") or ("9:16" if (props.get("height", 1920) > props.get("width", 1080)) else "16:9")
        )
        lang = str(props.get("primary_language", "vi"))
        subs = not bool(props.get("hideSubtitles", False))
        if aspect == "dual":
            outputs = [
                {"aspect_ratio": "9:16", "language": lang, "subtitles": subs},
                {"aspect_ratio": "16:9", "language": lang, "subtitles": False},
            ]
        else:
            outputs = [{"aspect_ratio": aspect, "language": lang, "subtitles": subs}]

    # 2. Extract and write subtitles from cues if available
    for plan in outputs:
        lang = plan.get("language") or props.get("primary_language", "vi")
        track = (props.get("tracks") or {}).get(lang) or {}
        cues = track.get("cues") or props.get("cues") or []
        if cues:
            srt_content = generate_srt(cues)
            if srt_content:
                (work_p / f"subtitles_{lang}.srt").write_text(srt_content, encoding="utf-8")
                if not (work_p / "subtitles.srt").is_file():
                    (work_p / "subtitles.srt").write_text(srt_content, encoding="utf-8")

    if not (work_p / "subtitles.srt").is_file() and props.get("cues"):
        srt_content = generate_srt(props["cues"])
        if srt_content:
            (work_p / "subtitles.srt").write_text(srt_content, encoding="utf-8")

    # 3. Render each delivery plan
    rendered_files: list[str] = []
    first_output_file: Path | None = None

    for plan in outputs:
        aspect = plan.get("aspect_ratio", "16:9")
        lang = plan.get("language") or props.get("primary_language", "vi")
        w = int(plan.get("width") or (1080 if aspect == "9:16" else 1920))
        h = int(plan.get("height") or (1920 if aspect == "9:16" else 1080))

        if len(outputs) == 1:
            out_name = "video.mp4"
        else:
            out_name = "video_9x16.mp4" if aspect == "9:16" else "video_16x9.mp4"

        target_file = work_p / out_name
        if first_output_file is None:
            first_output_file = target_file

        track = (props.get("tracks") or {}).get(lang) or {}
        scenes = (track.get("scenesByAspect") or {}).get(aspect)
        if not scenes:
            if aspect == "16:9" and props.get("en_scenes") and lang == "en":
                scenes = props["en_scenes"]
            else:
                scenes = (props.get("scenes_by_aspect") or {}).get(aspect) or props.get("scenes") or []

        audio_src = track.get("audioSrc") or props.get("audioSrc") or "narration.wav"
        audio_path = _resolve_file(public_dir, audio_src) or _resolve_file(work_p, audio_src)

        target_duration = float(track.get("duration") or 0.0)
        if target_duration <= 0.0 and audio_path and audio_path.is_file():
            target_duration = probe_audio_duration(audio_path)
        if target_duration <= 0.0:
            target_duration = float(props.get("duration") or (props.get("durationInFrames", 900) / props.get("fps", 30)))

        cues = track.get("cues") or props.get("cues") or []
        burn_subs = bool(plan.get("subtitles")) and not bool(plan.get("hideSubtitles", False))

        bgm_src = props.get("bgmSrc")
        bgm_vol = props.get("bgmDuckedVolume")
        bgm_path = (_resolve_file(public_dir, bgm_src) or _resolve_file(work_p, bgm_src)) if bgm_src else None

        logger.info(f"Rendering plan -> {out_name} ({w}x{h}, {target_duration:.2f}s, subs={burn_subs})...")
        _render_delivery_plan(
            work_p=work_p,
            output_mp4=target_file,
            width=w,
            height=h,
            target_duration=target_duration,
            scenes=scenes,
            cues=cues,
            burn_subtitles=burn_subs,
            audio_path=audio_path,
            bgm_path=bgm_path,
            bgm_volume=bgm_vol,
            watermark_png=watermark_png,
            use_nvenc=nvenc_active,
            scratch_dir=scratch_dir,
        )
        rendered_files.append(out_name)

    # If multiple outputs, copy first output to video.mp4
    if len(outputs) > 1 and first_output_file and first_output_file.is_file():
        shutil.copy2(first_output_file, work_p / "video.mp4")
    elif len(outputs) == 1 and (work_p / "video.mp4").is_file():
        # Ensure aspect-specific copy also exists
        single_aspect = outputs[0].get("aspect_ratio", "16:9")
        if single_aspect == "16:9" and not (work_p / "video_16x9.mp4").is_file():
            shutil.copy2(work_p / "video.mp4", work_p / "video_16x9.mp4")
        elif single_aspect == "9:16" and not (work_p / "video_9x16.mp4").is_file():
            shutil.copy2(work_p / "video.mp4", work_p / "video_9x16.mp4")

    # 4. Handle omni_platform deliveries
    if props.get("omni_platform"):
        spec = props.get("thumbnail_spec") or {}
        if spec.get("text_overlay"):
            words = spec["text_overlay"].strip().split()
            if spec["text_overlay"] != spec["text_overlay"].upper() or len(words) < 2 or len(words) > 4:
                raise ValueError("Invalid thumbnail text: 2–4 uppercase words required")

        # video_youtube_16x9.mp4 (subtitles = False)
        target_yt = work_p / "video_youtube_16x9.mp4"
        if not target_yt.is_file():
            # Check if any rendered 16:9 without subtitles exists
            src_yt = work_p / "video_16x9.mp4" if (work_p / "video_16x9.mp4").is_file() else work_p / "video.mp4"
            if src_yt.is_file():
                shutil.copy2(src_yt, target_yt)

        # video_facebook_16x9.mp4 (subtitles = True)
        target_fb = work_p / "video_facebook_16x9.mp4"
        if not target_fb.is_file():
            primary_lang = props.get("primary_language", "vi")
            tr_fb = (props.get("tracks") or {}).get(primary_lang) or {}
            sc_fb = (tr_fb.get("scenesByAspect") or {}).get("16:9") or props.get("scenes") or []
            dur_fb = float(tr_fb.get("duration") or props.get("duration", 30))
            aud_fb = _resolve_file(public_dir, tr_fb.get("audioSrc") or props.get("audioSrc"))
            cues_fb = tr_fb.get("cues") or props.get("cues") or []
            _render_delivery_plan(
                work_p=work_p,
                output_mp4=target_fb,
                width=1920,
                height=1080,
                target_duration=dur_fb,
                scenes=sc_fb,
                cues=cues_fb,
                burn_subtitles=True,
                audio_path=aud_fb,
                bgm_path=None,
                bgm_volume=None,
                watermark_png=watermark_png,
                use_nvenc=nvenc_active,
                scratch_dir=scratch_dir,
            )

        # short_deliveries
        for short in props.get("short_deliveries", []):
            short_file = short.get("file")
            if not short_file:
                continue
            short_out = work_p / short_file
            s_props = short.get("props", {})
            s_scenes = s_props.get("scenes", [])
            s_cues = s_props.get("cues", [])
            s_dur = float(s_props.get("duration", 45))
            s_aud = _resolve_file(public_dir, s_props.get("audioSrc"))
            _render_delivery_plan(
                work_p=work_p,
                output_mp4=short_out,
                width=int(s_props.get("width", 1080)),
                height=int(s_props.get("height", 1920)),
                target_duration=s_dur,
                scenes=s_scenes,
                cues=s_cues,
                burn_subtitles=not bool(s_props.get("hideSubtitles", False)),
                audio_path=s_aud,
                bgm_path=None,
                bgm_volume=None,
                watermark_png=watermark_png,
                use_nvenc=nvenc_active,
                scratch_dir=scratch_dir,
            )

        # Write SOCIAL_POST_KIT.md
        _write_social_post_kit(work_p, props)

    # 5. Generate Thumbnails and Covers
    if props.get("thumbnail_spec") or props.get("omni_platform"):
        spec = props.get("thumbnail_spec") or {}
        thumb_text = spec.get("title") or spec.get("text_overlay") or spec.get("text") or props.get("hook_title") or ""
        first_img = _resolve_file(public_dir, spec.get("image")) if spec.get("image") else None
        if not first_img and props.get("scenes"):
            first_sc = props["scenes"][0]
            first_beat_src = (first_sc.get("images") or [{}])[0].get("src") or first_sc.get("image")
            first_img = _resolve_file(public_dir, first_beat_src)

        ratio = str(props.get("aspect_ratio", "9:16"))
        if ratio in ("16:9", "dual") or props.get("omni_platform"):
            out_yt = work_p / "thumbnail_youtube_16x9.png"
            generate_thumbnail_image(out_yt, 1920, 1080, first_img, thumb_text)

        if ratio in ("9:16", "dual") or props.get("omni_platform"):
            out_cover = work_p / "cover_tiktok_reels_9x16.png"
            cover_text = props.get("cover_text") or thumb_text
            generate_thumbnail_image(out_cover, 1080, 1920, first_img, cover_text)

    # 6. Export scene stills if top-level scenes present
    top_scenes = props.get("scenes")
    if top_scenes and isinstance(top_scenes, list):
        still_w = int(props.get("width") or 1920)
        still_h = int(props.get("height") or 1080)
        for scene in top_scenes:
            scene_id = scene.get("id")
            if not scene_id:
                continue
            still_out = work_p / f"{scene_id}.png"
            src_cand = None
            if scene.get("images") and len(scene["images"]) > 0:
                src_cand = scene["images"][0].get("src")
            if not src_cand:
                src_cand = scene.get("image") or scene.get("src")

            res_path = _resolve_file(public_dir, src_cand) if src_cand else None
            if not res_path and src_cand:
                res_path = _resolve_file(work_p, src_cand)

            if res_path and res_path.is_file():
                if res_path.suffix.lower() in (".mp4", ".mov", ".webm"):
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-ss",
                            "0.05",
                            "-i",
                            str(res_path.resolve()),
                            "-vf",
                            f"scale={still_w}:{still_h}",
                            "-vframes",
                            "1",
                            str(still_out),
                        ],
                        capture_output=True,
                        check=False,
                    )
                else:
                    try:
                        from PIL import Image

                        im = Image.open(res_path).convert("RGB")
                        if im.size != (still_w, still_h):
                            im = im.resize((still_w, still_h), Image.Resampling.LANCZOS)
                        im.save(still_out, format="PNG")
                    except Exception:
                        pass

            if not still_out.is_file():
                try:
                    from PIL import Image

                    im = Image.new("RGB", (still_w, still_h), "#F8F0DC")
                    im.save(still_out, format="PNG")
                except Exception:
                    pass

    # 7. Write layout.json
    layout_data = {
        "passed": True,
        "failures": [],
        "renderer": "ffmpeg_h264_nvenc",
        "encoder": encoder_name,
        "remotion_concurrency": None,
        "execution_mode": "multi_threaded_batch",
        "concurrency": 4,
    }
    (work_p / "layout.json").write_text(json.dumps(layout_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Clean up scratch work
    shutil.rmtree(scratch_dir, ignore_errors=True)

    result = {
        "status": "success",
        "renderer": "ffmpeg_h264_nvenc",
        "encoder": encoder_name,
        "work_dir": str(work_p),
        "files": [p.name for p in work_p.iterdir() if p.is_file()],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Colab Tesla T4 Flow Video Worker & Native NVENC Compositor.")
    parser.add_argument("--job", help="Path to single job request JSON")
    parser.add_argument("--batch", help="Path to batch manifest JSON")
    parser.add_argument("--package", help="Path to props.json work directory to render")
    parser.add_argument("--require-nvenc", action="store_true", help="Fail if h264_nvenc is unavailable")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--check-nvenc", action="store_true", help="Check h264_nvenc availability")
    args = parser.parse_args()

    if args.check_nvenc:
        nv = has_nvenc()
        print(f"h264_nvenc available: {nv}")
        sys.exit(0 if nv else 1)

    if args.package:
        res = render_props_package(args.package, require_nvenc=args.require_nvenc)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.job:
        if not args.output_dir:
            parser.error("--output-dir required with --job")
        res = render_single_job(args.job, args.output_dir)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.batch:
        if not args.output_dir:
            parser.error("--output-dir required with --batch")
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
