"""FFmpeg-based seamless video stitcher for Flow Video daisy chains and scene pairs."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from sys.flow_video.models import ChainMode, VideoClipTask
from typing import Any

ASPECT_RESOLUTIONS: dict[str, tuple[int, int]] = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
}


def _get_ffmpeg_bin() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("ffmpeg executable not found in PATH")
    return path


def _get_ffprobe_bin() -> str:
    path = shutil.which("ffprobe")
    if not path:
        raise RuntimeError("ffprobe executable not found in PATH")
    return path


def probe_video_clip(path: str | Path) -> dict[str, Any]:
    """Probe video and audio streams of a media file via ffprobe.

    Raises ValueError if the file does not exist, is empty, has no video stream,
    or has invalid/0 duration.
    """
    file_p = Path(path)
    if not file_p.is_file():
        raise ValueError(f"Video file does not exist: {path}")

    if file_p.stat().st_size == 0:
        raise ValueError(f"Video file is empty (0 bytes): {path}")

    ffprobe = _get_ffprobe_bin()
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration,codec_name,codec_type,channels,sample_rate",
        "-show_entries",
        "format=duration,size,bit_rate",
        "-of",
        "json",
        str(file_p.resolve()),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise ValueError(f"ffprobe failed on {path}: {res.stderr.strip()}")

    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse ffprobe JSON for {path}: {err}") from err

    streams = data.get("streams", [])
    format_info = data.get("format", {})

    video_stream: dict[str, Any] | None = None
    audio_stream: dict[str, Any] | None = None

    for s in streams:
        c_type = s.get("codec_type")
        if c_type == "video" and video_stream is None:
            video_stream = s
        elif c_type == "audio" and audio_stream is None:
            audio_stream = s

    if not video_stream:
        raise ValueError(f"No video stream found in {path}")

    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    codec_name = str(video_stream.get("codec_name", ""))

    # Frame rate calculation
    fps = 30.0
    for r_key in ("r_frame_rate", "avg_frame_rate"):
        r_str = video_stream.get(r_key, "")
        if r_str and "/" in r_str:
            num, den = r_str.split("/", 1)
            try:
                n, d = float(num), float(den)
                if d > 0 and n > 0:
                    fps = n / d
                    break
            except ValueError:
                pass

    # Duration calculation
    duration = 0.0
    for dur_src in (video_stream.get("duration"), format_info.get("duration")):
        if dur_src:
            try:
                duration = float(dur_src)
                if duration > 0:
                    break
            except ValueError:
                pass

    nb_frames = 0
    if video_stream.get("nb_frames"):
        try:
            nb_frames = int(video_stream["nb_frames"])
        except ValueError:
            pass
    if nb_frames <= 0 and duration > 0 and fps > 0:
        nb_frames = int(round(duration * fps))

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid dimensions for {path}: {width}x{height}")

    if duration <= 0.0:
        raise ValueError(f"Invalid or zero duration for {path}: {duration}s")

    has_audio = audio_stream is not None
    audio_codec = str(audio_stream.get("codec_name")) if audio_stream else None
    audio_dur = None
    if audio_stream and audio_stream.get("duration"):
        try:
            audio_dur = float(audio_stream["duration"])
        except ValueError:
            pass

    return {
        "path": str(file_p.resolve()),
        "width": width,
        "height": height,
        "fps": round(fps, 3),
        "nb_frames": nb_frames,
        "duration": round(duration, 4),
        "codec_name": codec_name,
        "has_audio": has_audio,
        "audio_codec": audio_codec,
        "audio_duration": round(audio_dur, 4) if audio_dur is not None else None,
        "size_bytes": int(format_info.get("size", 0)),
    }


def probe_audio_duration(path: str | Path) -> float:
    """Probe duration of an audio file via ffprobe."""
    file_p = Path(path)
    if not file_p.is_file():
        raise ValueError(f"Audio file does not exist: {path}")
    ffprobe = _get_ffprobe_bin()
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=duration",
        "-of",
        "json",
        str(file_p.resolve()),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode == 0:
        try:
            data = json.loads(res.stdout)
            format_dur = data.get("format", {}).get("duration")
            if format_dur:
                d = float(format_dur)
                if d > 0:
                    return d
            for st in data.get("streams", []):
                s_dur = st.get("duration")
                if s_dur:
                    d = float(s_dur)
                    if d > 0:
                        return d
        except (ValueError, TypeError, json.JSONDecodeError):
            pass
    return 0.0


def _normalize_clip_input(
    clip: VideoClipTask | dict[str, Any] | str,
) -> tuple[str, bool, float | None]:
    """Extract (path, trim_first_frame, target_duration) from clip input."""
    if isinstance(clip, VideoClipTask):
        return clip.output_mp4_path, clip.trim_first_frame, clip.target_duration
    if isinstance(clip, dict):
        return (
            str(clip.get("output_mp4_path", clip.get("src", ""))),
            bool(clip.get("trim_first_frame", False)),
            float(clip["target_duration"]) if clip.get("target_duration") is not None else None,
        )
    return str(clip), False, None


def render_flipbook_segment(
    start_image: str | Path,
    end_image: str | Path | None,
    output_mp4: str | Path,
    duration_sec: float,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    crossfade_sec: float = 0.45,
) -> dict[str, Any]:
    """Render an animated flipbook video segment using local ffmpeg (0 credits).

    Applies a subtle 1.0 -> 1.04 slow zoom/pan over duration_sec and, if end_image is provided,
    smoothly crossfades (xfade) into end_image.
    """
    start_p = Path(start_image)
    if not start_p.is_file():
        raise FileNotFoundError(f"Start image file not found: {start_image}")

    dur = float(duration_sec)
    if dur <= 0:
        raise ValueError(f"duration_sec must be positive, got {dur}")

    out_p = Path(output_mp4)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    has_end = False
    if end_image:
        end_p = Path(end_image)
        if not end_p.is_file():
            raise FileNotFoundError(f"End image file not found: {end_image}")
        if end_p.resolve() != start_p.resolve():
            has_end = True

    ffmpeg_bin = _get_ffmpeg_bin()
    nb_frames = max(1, int(round(dur * fps)))
    step = 0.04 / nb_frames

    if has_end:
        end_p = Path(end_image)  # type: ignore
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
            ffmpeg_bin,
            "-y",
            "-loop", "1",
            "-t", str(dur),
            "-r", str(fps),
            "-i", str(start_p.resolve()),
            "-loop", "1",
            "-t", str(xfade_dur + 0.5),
            "-r", str(fps),
            "-i", str(end_p.resolve()),
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-t", str(dur),
            str(out_p.resolve()),
        ]
    else:
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"zoompan=z='min(zoom+{step:.6f},1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps={fps}"
        )
        cmd = [
            ffmpeg_bin,
            "-y",
            "-loop", "1",
            "-t", str(dur),
            "-r", str(fps),
            "-i", str(start_p.resolve()),
            "-vf", vf,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-t", str(dur),
            str(out_p.resolve()),
        ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"render_flipbook_segment failed:\n{res.stderr.strip()}")

    return probe_video_clip(out_p)


def stitch_video_chain(
    clips: list[VideoClipTask | dict[str, Any] | str],
    output_mp4_path: str | Path,
    mode: ChainMode = ChainMode.DAISY_CHAIN,
    aspect: str = "16:9",
    fps: int = 30,
    audio_path: str | Path | None = None,
    normalize_audio_lufs: bool = True,
    keep_veo_audio: bool = True,
    veo_audio_mix_weight: float = 0.45,
) -> dict[str, Any]:
    """Stitch multiple video clips into a single continuous seamless MP4.

    Features:
    - Target canvas scaling and centering to exact aspect ratio (16:9, 9:16, 1:1).
    - In DAISY_CHAIN: clip 0 keeps full clip; clips i >= 1 apply
      `trim=start_frame=1,setpts=PTS-STARTPTS` so boundary frame Fi is NEVER duplicated!
    - In SCENE_PAIRS:
      - 0.7 <= raw/target <= 1.35: smooth setpts time-stretch to land on beat.
      - target > raw * 1.35: plays at natural speed and applies tpad clone freeze on last frame.
      - target < raw * 0.7: speeds up 1.35x and trims cleanly.
    - Native Flow/Veo audio: kept by default (`keep_veo_audio=True`).
      - When an external voiceover is provided, native audio is mixed underneath the voiceover
        using `amix` with `veo_audio_mix_weight` (default 0.45).
      - If `keep_veo_audio=False`, only external voiceover is mapped.
    - Audio muxing: if `audio_path` is given, muxes external narration with optional
      LUFS normalization (-11 LUFS / -1 dBTP).
    """
    if not clips:
        raise ValueError("Cannot stitch empty clip list")

    out_p = Path(output_mp4_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    target_res = ASPECT_RESOLUTIONS.get(aspect, ASPECT_RESOLUTIONS["16:9"])
    tw, th = target_res

    # Probe all clips first
    parsed_clips: list[tuple[str, bool, float | None, dict[str, Any]]] = []
    for c in clips:
        p_str, trim_first, target_dur = _normalize_clip_input(c)
        meta = probe_video_clip(p_str)
        parsed_clips.append((p_str, trim_first, target_dur, meta))

    clip_probes = [m for _, _, _, m in parsed_clips]
    all_have_audio = all(p.get("has_audio", False) for p in clip_probes)
    has_native_audio = keep_veo_audio and all_have_audio

    k = len(parsed_clips)
    ffmpeg_bin = _get_ffmpeg_bin()

    cmd: list[str] = [ffmpeg_bin, "-y", "-threads", "2"]
    for path_str, _, _, _ in parsed_clips:
        cmd.extend(["-threads", "1", "-i", path_str])

    has_ext_audio = False
    ext_audio_idx = k
    if audio_path is not None:
        audio_p = Path(audio_path)
        if not audio_p.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        cmd.extend(["-i", str(audio_p.resolve())])
        has_ext_audio = True

    # Calculate video and audio durations to detect if video needs end-padding
    ext_audio_dur = 0.0
    if has_ext_audio:
        ext_audio_dur = probe_audio_duration(audio_p)

    total_video_dur = 0.0
    for i, (_, trim_first, target_dur, meta) in enumerate(parsed_clips):
        raw_dur = float(meta.get("duration", 0.0))
        if mode == ChainMode.DAISY_CHAIN:
            clip_dur = raw_dur - (1.0 / fps) if (trim_first or i > 0) else raw_dur
        elif mode == ChainMode.ZERO_CREDIT_FLIPBOOK or str(mode).lower() == "zero_credit_flipbook":
            clip_dur = target_dur if target_dur is not None and target_dur > 0 else raw_dur
        else:
            # SCENE_PAIRS pacing logic
            if target_dur is not None and target_dur > 0:
                clip_dur = target_dur
            else:
                clip_dur = raw_dur
        total_video_dur += max(0.0, clip_dur)

    pad_final_dur = 0.0
    if has_ext_audio and ext_audio_dur > total_video_dur + 0.01:
        pad_final_dur = ext_audio_dur - total_video_dur

    # Build filtergraph
    filter_chains: list[str] = []
    video_labels: list[str] = []
    audio_labels: list[str] = []

    base_scale = (
        f"scale={tw}:{th}:force_original_aspect_ratio=decrease,"
        f"pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    )

    for i, (_, trim_first, target_dur, meta) in enumerate(parsed_clips):
        raw_dur = meta["duration"]
        is_last_clip = (i == k - 1)
        tpad_str = f",tpad=stop_mode=clone:stop_duration={pad_final_dur:.3f}" if (is_last_clip and pad_final_dur > 0.001) else ""

        if mode == ChainMode.DAISY_CHAIN:
            if trim_first or i > 0:
                vfilter = f"[{i}:v]{base_scale},trim=start_frame=1{tpad_str},setpts=PTS-STARTPTS[v{i}]"
            else:
                vfilter = f"[{i}:v]{base_scale}{tpad_str},setpts=PTS-STARTPTS[v{i}]"
        elif mode == ChainMode.ZERO_CREDIT_FLIPBOOK or str(mode).lower() == "zero_credit_flipbook":
            vfilter = f"[{i}:v]{base_scale}{tpad_str},setpts=PTS-STARTPTS[v{i}]"
        else:
            # SCENE_PAIRS pacing logic
            if target_dur is not None and target_dur > 0:
                ratio = raw_dur / target_dur
                if 0.7 <= ratio <= 1.35:
                    # Smooth time-stretch so motion hits End Frame right on beat
                    pts_factor = target_dur / raw_dur
                    vfilter = (
                        f"[{i}:v]{base_scale}{tpad_str},setpts={pts_factor:.6f}*PTS[v{i}]"
                    )
                elif target_dur > raw_dur * 1.35:
                    # Target is longer: play at natural speed, freeze last frame with tpad
                    extra = target_dur - raw_dur + (pad_final_dur if is_last_clip else 0.0)
                    vfilter = (
                        f"[{i}:v]{base_scale},"
                        f"tpad=stop_mode=clone:stop_duration={extra:.3f},"
                        f"setpts=PTS-STARTPTS[v{i}]"
                    )
                else:
                    # Target is shorter: speed up up to 1.35x and trim remainder
                    speed_factor = 1.0 / 1.35
                    vfilter = (
                        f"[{i}:v]{base_scale},"
                        f"setpts={speed_factor:.6f}*PTS,"
                        f"trim=duration={target_dur:.3f}{tpad_str},"
                        f"setpts=PTS-STARTPTS[v{i}]"
                    )
            else:
                vfilter = f"[{i}:v]{base_scale}{tpad_str},setpts=PTS-STARTPTS[v{i}]"

        filter_chains.append(vfilter)
        video_labels.append(f"[v{i}]")

        if has_native_audio:
            afilter = (
                f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]"
            )
            filter_chains.append(afilter)
            audio_labels.append(f"[a{i}]")

    # Concat video and audio
    if has_native_audio:
        concat_inputs = "".join(f"{v}{a}" for v, a in zip(video_labels, audio_labels, strict=True))
        filter_chains.append(f"{concat_inputs}concat=n={k}:v=1:a=1[vconcat][aconcat]")
    else:
        concat_inputs = "".join(video_labels)
        filter_chains.append(f"{concat_inputs}concat=n={k}:v=1:a=0[vconcat]")

    # Audio filter when external audio is provided
    if has_ext_audio:
        loudnorm_str = "loudnorm=I=-11.0:TP=-1.0:LRA=7.0," if normalize_audio_lufs else ""
        if has_native_audio:
            # Case 2: external audio + native audio mix
            filter_chains.append(
                f"[{ext_audio_idx}:a]{loudnorm_str}aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[avoice]"
            )
            filter_chains.append(
                f"[aconcat]volume={veo_audio_mix_weight}[anative];"
                f"[avoice]volume=1.0[av];"
                f"[anative][av]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[afinal]"
            )
        else:
            # Case 3: external audio only
            filter_chains.append(
                f"[{ext_audio_idx}:a]{loudnorm_str}aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[afinal]"
            )

    cmd.extend(["-filter_complex", ";".join(filter_chains)])

    if has_ext_audio:
        cmd.extend([
            "-map", "[vconcat]",
            "-map", "[afinal]",
            "-c:v", "libx264",
            "-threads", "2",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
        ])
        if total_video_dur > ext_audio_dur + 0.05:
            cmd.append("-shortest")
        cmd.extend([
            "-movflags", "+faststart",
            str(out_p.resolve()),
        ])
    elif has_native_audio:
        # Case 1: native audio only
        cmd.extend([
            "-map", "[vconcat]",
            "-map", "[aconcat]",
            "-c:v", "libx264",
            "-threads", "2",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_p.resolve()),
        ])
    else:
        cmd.extend([
            "-map", "[vconcat]",
            "-an",
            "-c:v", "libx264",
            "-threads", "2",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "18",
            "-movflags", "+faststart",
            str(out_p.resolve()),
        ])

    run_res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if run_res.returncode != 0:
        raise RuntimeError(
            f"ffmpeg stitch failed (code {run_res.returncode}):\n{run_res.stderr.strip()}"
        )

    # Verify final output MP4
    final_meta = probe_video_clip(out_p)
    if final_meta["width"] != tw or final_meta["height"] != th:
        raise ValueError(
            f"Stitched video resolution mismatch: expected {tw}x{th}, got {final_meta['width']}x{final_meta['height']}"
        )

    return {
        "output_path": str(out_p.resolve()),
        "mode": mode.value if isinstance(mode, ChainMode) else str(mode),
        "aspect": aspect,
        "width": final_meta["width"],
        "height": final_meta["height"],
        "fps": final_meta["fps"],
        "duration": final_meta["duration"],
        "nb_frames": final_meta["nb_frames"],
        "nb_clips": k,
        "has_audio": final_meta["has_audio"],
        "size_bytes": final_meta["size_bytes"],
    }


__all__ = [
    "ASPECT_RESOLUTIONS",
    "probe_audio_duration",
    "probe_video_clip",
    "render_flipbook_segment",
    "stitch_video_chain",
]
