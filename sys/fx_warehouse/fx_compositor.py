"""Real Audio Mixer, 30fps HUD Overlay Renderer & FFmpeg/CUDA FX Compositor.

Executes `fx_plan.json` specs across both `short_9x16` and `long_16x9` runs:
1. Mixes narration + voice-ducked Niche BGM + aligned 48kHz stereo SFX/bespoke WAVs
   into EBU R128 `-11.0 LUFS / -1.0 dBTP` mastered 48kHz audio.
2. Pre-renders crisp RGBA HUD PNG overlays (shared 14 widgets, dynamic bespoke HUDs,
   and `forensic_v2` 9 widgets) safely scaled/positioned for `16:9` and `9:16`.
3. Resolves per-beat sub-pixel 2.5D camera curves and safe FFmpeg VFX filters while
   enforcing each Niche Archetype's comfort guardrails (`disallowed_vfx`).
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from scipy.signal import butter, filtfilt

from .camera_vfx import get_camera_motion
from .hud_forensic_v2 import FORENSIC_HUD_V2_CATALOG, render_forensic_hud_v2
from .hud_widgets import build_bespoke_topic_hud_patch, render_hud_widget_patch

TARGET_SR = 48000

_FFMPEG_VFX_MAP: dict[str, str] = {
    "kodak_35mm_grain": "noise=alls=4:allf=t",
    "warm_dust_motes": "eq=saturation=1.05:gamma_r=1.02:gamma_b=0.98",
    "hypoxic_vignette": "vignette=PI/4.5",
    "crimson_strobe_alert": "eq=contrast=1.05:saturation=1.10",
    "chromatic_glitch_pulse": "rgbashift=rh=2:bh=-2",
}

_FORENSIC_V2_TOPIC_MAP: tuple[tuple[str, str], ...] = (
    ("radar", "calibrated_radar_overlay"),
    ("cvr", "hypoxia_tuc_meter"),
    ("countdown", "hypoxia_tuc_meter"),
    ("oscilloscope", "dual_horn_pulse"),
    ("stat", "alt_pressure_divergence"),
    ("xray", "swiss_cheese_align"),
    ("split", "classic_vs_ng_compare"),
    ("dossier", "lemmino_hairline_hud"),
)


def _decode_audio_stereo_f32(path: Path, sr: int = TARGET_SR) -> np.ndarray:
    """Decode any audio file via FFmpeg into contiguous stereo float32 PCM."""
    cmd = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(path.resolve()),
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "-ac",
        "2",
        "-ar",
        str(sr),
        "pipe:1",
    ]
    res = subprocess.run(cmd, check=True, capture_output=True)
    if not res.stdout:
        return np.zeros((sr, 2), dtype=np.float32)
    arr = np.frombuffer(res.stdout, dtype=np.float32)
    n_frames = len(arr) // 2
    return arr[: n_frames * 2].reshape(n_frames, 2).copy()


def _write_pcm16_wav(path: Path, stereo: np.ndarray, sr: int = TARGET_SR) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(stereo))) if len(stereo) else 0.0
    if peak > 0.92:
        stereo = stereo * (0.92 / peak)
    pcm = np.clip(np.round(stereo * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def _loop_bgm_to_length(bgm: np.ndarray, n_samples: int) -> np.ndarray:
    if len(bgm) == 0 or n_samples <= 0:
        return np.zeros((max(1, n_samples), 2), dtype=np.float32)
    if len(bgm) >= n_samples:
        return bgm[:n_samples].copy()
    reps = int(math.ceil(n_samples / float(len(bgm))))
    tiled = np.tile(bgm, (reps, 1))
    return tiled[:n_samples].copy()


def _compute_voice_duck_gain(voice: np.ndarray, sr: int, idle_gain: float, speech_gain: float) -> np.ndarray:
    mono = np.abs(voice.mean(axis=1))
    win = max(1, int(0.04 * sr))
    kernel = np.ones(win, dtype=np.float32) / float(win)
    rms = np.sqrt(np.convolve(mono * mono, kernel, mode="same"))
    active = np.clip((rms - 0.014) / 0.055, 0.0, 1.0).astype(np.float32)
    if len(active) > 32:
        b, a = butter(2, 3.0 / (sr * 0.5), btype="lowpass")
        duck_env = np.clip(filtfilt(b, a, active), 0.0, 1.0).astype(np.float32)
    else:
        duck_env = active
    return (idle_gain - (idle_gain - speech_gain) * duck_env).astype(np.float32)


def mix_fx_warehouse_audio(
    voice_wav: Path,
    fx_plan_path: Path | str,
    out_wav: Path,
    sr: int = TARGET_SR,
) -> dict[str, Any]:
    """Mix voice narration + ducked niche BGM + aligned 48kHz SFX stems -> `-11.0 LUFS` WAV."""
    plan = json.loads(Path(fx_plan_path).read_text(encoding="utf-8"))
    if not plan.get("enabled"):
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        if voice_wav.resolve() != out_wav.resolve():
            shutil.copy2(voice_wav, out_wav)
        return {"mixed": False, "bgm_used": "", "sfx_mixed": 0, "out_wav": str(out_wav.resolve())}

    voice = _decode_audio_stereo_f32(voice_wav, sr=sr)
    n_samples = len(voice)
    mixed = voice.copy()

    is_mindful = plan.get("archetype_id") == "archetype_5_mindful_healing"
    idle_gain = 0.065 if is_mindful else 0.115
    speech_gain = 0.022 if is_mindful else 0.038
    sfx_gain = 0.14 if is_mindful else 0.22

    bgm_used = ""
    bgm_raw_path = Path(str(plan.get("bgm_path") or ""))
    if bgm_raw_path.is_file():
        bgm_stem = _decode_audio_stereo_f32(bgm_raw_path, sr=sr)
        bgm_loop = _loop_bgm_to_length(bgm_stem, n_samples)
        duck = _compute_voice_duck_gain(voice, sr=sr, idle_gain=idle_gain, speech_gain=speech_gain)
        fade_n = min(n_samples // 6, int(0.40 * sr))
        if fade_n > 1:
            bgm_loop[:fade_n] *= np.linspace(0.0, 1.0, fade_n, dtype=np.float32)[:, None]
            bgm_loop[-fade_n:] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)[:, None]
        mixed += bgm_loop * duck[:, None]
        bgm_used = bgm_raw_path.name

    sfx_cache: dict[str, np.ndarray] = {}
    sfx_mixed = 0
    for b in plan.get("beats", []):
        sfx_str = str(b.get("sfx_path") or "")
        if not sfx_str:
            continue
        sfx_p = Path(sfx_str)
        if not sfx_p.is_file():
            continue
        if sfx_str not in sfx_cache:
            sfx_cache[sfx_str] = _decode_audio_stereo_f32(sfx_p, sr=sr)
        stem = sfx_cache[sfx_str]
        if len(stem) == 0:
            continue
        idx0 = max(0, int(round((float(b.get("t_start", 0.0)) + 0.04) * sr)))
        if idx0 >= n_samples:
            continue
        take = min(len(stem), n_samples - idx0)
        mixed[idx0 : idx0 + take] += stem[:take] * sfx_gain
        sfx_mixed += 1

    raw_mix_wav = out_wav.parent / f"._{out_wav.stem}_raw.wav"
    _write_pcm16_wav(raw_mix_wav, mixed, sr=sr)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw_mix_wav.resolve()),
            "-af",
            "loudnorm=I=-11.0:TP=-1.0:LRA=7.0,aresample=48000,aformat=sample_fmts=s16:channel_layouts=stereo",
            "-ar",
            str(sr),
            "-ac",
            "2",
            str(out_wav.resolve()),
        ],
        check=True,
        capture_output=True,
    )
    raw_mix_wav.unlink(missing_ok=True)
    return {
        "mixed": True,
        "bgm_used": bgm_used,
        "sfx_mixed": sfx_mixed,
        "duration_sec": round(n_samples / float(sr), 4),
        "out_wav": str(out_wav.resolve()),
    }


def build_ffmpeg_vfx_filter(vfx_name: str, disallowed_vfx: list[str] | tuple[str, ...]) -> str:
    """Return safe FFmpeg video filter snippet for `vfx_name`, obeying comfort guardrails."""
    if not vfx_name or vfx_name in set(disallowed_vfx):
        return ""
    return _FFMPEG_VFX_MAP.get(str(vfx_name), "")


def _render_single_hud_patch(
    beat_cue: dict[str, Any],
    beat_text: str,
    fx_mode: str,
    variant: str,
    target_w: int,
    target_h: int,
    is_short: bool,
) -> tuple[int, int, Image.Image] | None:
    dur = max(0.6, float(beat_cue.get("duration") or 2.5))
    t_sample = min(dur * 0.72, max(0.35, dur * 0.48))
    hud_id = beat_cue.get("hud")
    bespoke_spec = beat_cue.get("bespoke_hud_spec")

    base_w, base_h = 2560, 1440
    res: tuple[int, int, Image.Image] | None = None

    if isinstance(bespoke_spec, dict) and bespoke_spec:
        res = build_bespoke_topic_hud_patch(bespoke_spec, t_beat=t_sample, dur=dur, amp=0.32, width=base_w, height=base_h)
    elif hud_id:
        spec = {
            "kicker": "PHÂN TÍCH CHUYÊN SÂU",
            "headline": (beat_text.strip()[:42] or str(hud_id).replace("_", " ").upper()),
            "subline": f"T+{float(beat_cue.get('t_start', 0.0)):05.1f}s",
        }
        if fx_mode == "forensic_v2":
            v2_id = next((v2 for key, v2 in _FORENSIC_V2_TOPIC_MAP if key in str(hud_id).lower()), None)
            if v2_id and v2_id in FORENSIC_HUD_V2_CATALOG:
                full_im = render_forensic_hud_v2(v2_id, spec, t_beat=t_sample, dur=dur, width=target_w, height=target_h, variant=variant)
                return 0, 0, full_im
        res = render_hud_widget_patch(str(hud_id), spec, t_beat=t_sample, dur=dur, amp=0.32, width=base_w, height=base_h)

    if res is None:
        return None

    bx, by, patch = res
    if is_short:
        # Scale proportionally to portrait width and keep clear of bottom kinetic .ass subtitles & logo.
        max_pw = max(240, target_w - 84)
        scale_f = min(1.0, max_pw / float(max(1, patch.width)))
        nw = max(32, int(round(patch.width * scale_f)))
        nh = max(32, int(round(patch.height * scale_f)))
        if (nw, nh) != (patch.width, patch.height):
            patch = patch.resize((nw, nh), Image.Resampling.LANCZOS)
        px = max(24, (target_w - nw) // 2)
        py = max(120, min(int(target_h * 0.62), target_h - nh - 420))
        return px, py, patch

    sx = target_w / float(base_w)
    sy = target_h / float(base_h)
    nw = max(32, int(round(patch.width * sx)))
    nh = max(32, int(round(patch.height * sy)))
    if (nw, nh) != (patch.width, patch.height):
        patch = patch.resize((nw, nh), Image.Resampling.LANCZOS)
    px = max(0, min(target_w - nw, int(round(bx * sx))))
    py = max(0, min(target_h - nh, int(round(by * sy))))

    # Preserve bottom-right watermark exclusion zone unless widget is full-width header/overlay.
    wm_clear_x = target_w - int(round(240 * sx))
    wm_clear_y = target_h - int(round(240 * sy))
    if nw < int(target_w * 0.85) and (px + nw) > wm_clear_x and (py + nh) > wm_clear_y:
        px = max(24, wm_clear_x - nw - 16)
    return px, py, patch


def prepare_fx_hud_assets(
    fx_plan_path: Path | str,
    beats: list[dict[str, Any]],
    overlay_dir: Path,
    target_w: int,
    target_h: int,
    is_short: bool = False,
) -> list[dict[str, Any]]:
    """Pre-render beat HUD RGBA PNG overlays and enrich beat render specs for Colab/Local encoders."""
    plan = json.loads(Path(fx_plan_path).read_text(encoding="utf-8"))
    if not plan.get("enabled"):
        return []

    overlay_dir.mkdir(parents=True, exist_ok=True)
    fx_mode = str(plan.get("fx_mode") or "auto_niche")
    disallowed = list(plan.get("disallowed_vfx") or [])
    variant = str((plan.get("forensic_v2") or {}).get("suspense_variant") or "B")

    beat_specs: list[dict[str, Any]] = []
    for idx, cue in enumerate(plan.get("beats", [])):
        beat_text = ""
        if idx < len(beats):
            beat_text = str(beats[idx].get("narration") or beats[idx].get("text") or "")

        cam_name = str(cue.get("camera") or "parallax_push_in")
        cam_params = dict(get_camera_motion(cam_name))
        vfx_name = str(cue.get("vfx") or "clean_daylight_none")
        if vfx_name in disallowed:
            vfx_name = "clean_daylight_none"

        hud_entry: dict[str, Any] = {
            "beat_index": idx,
            "t_start": float(cue.get("t_start", 0.0)),
            "duration": float(cue.get("duration", 2.5)),
            "camera": cam_name,
            "camera_params": {
                "z0": float(cam_params.get("z0", 1.04)),
                "z1": float(cam_params.get("z1", 1.10)),
                "x0": float(cam_params.get("x0", 0.0)),
                "x1": float(cam_params.get("x1", 0.0)),
                "y0": float(cam_params.get("y0", 0.0)),
                "y1": float(cam_params.get("y1", 0.0)),
                "parallax_amp": float(cam_params.get("parallax_amp", 0.016)),
            },
            "vfx": vfx_name,
            "vfx_ffmpeg": build_ffmpeg_vfx_filter(vfx_name, disallowed),
            "hud_file": "",
            "hud_x": 0,
            "hud_y": 0,
            "hud_w": 0,
            "hud_h": 0,
        }

        rendered = _render_single_hud_patch(
            cue,
            beat_text=beat_text,
            fx_mode=fx_mode,
            variant=variant,
            target_w=target_w,
            target_h=target_h,
            is_short=is_short,
        )
        if rendered is not None:
            hx, hy, patch = rendered
            fname = f"hud_b{idx:04d}.png"
            out_png = overlay_dir / fname
            patch.save(out_png, format="PNG")
            hud_entry.update({
                "hud_file": f"hud_overlays/{fname}",
                "hud_local_path": str(out_png.resolve()),
                "hud_x": int(hx),
                "hud_y": int(hy),
                "hud_w": int(patch.width),
                "hud_h": int(patch.height),
            })

        beat_specs.append(hud_entry)
    return beat_specs
